#!/usr/bin/env python3
"""
Automated Correspondence Points Detection Script
Uses YOLO to detect yard markers and automatically generate correspondence points
based on NCAA football field standards.

Yard marker format: (near/far)(left/right)(yardNumber)
Possible values: fl1,fl2,fl3,fl4,f5,nl1,nl2,nl3,nl4,n5,nr1,nr2,nr3,nr4,nr5

NCAA Standards:
- Yard-line numbers: max 6 feet height, 4 feet width
- Tops of numbers: 9 yards from sidelines
- Field width: 160 feet (53.33 yards)
- Field length: 120 yards (100 + 2 endzones of 10 yards each)
"""

import cv2
import json
import os
import numpy as np
from ultralytics import YOLO

# NCAA Field dimensions (in feet)
FIELD_LENGTH_FT = 360  # 120 yards * 3 feet/yard
FIELD_WIDTH_FT = 160   # 160 feet
HASH_DISTANCE_FT = 40  # Hash marks 40 feet from sidelines
YARD_MARKER_HEIGHT_FT = 6  # Max height per NCAA rules
YARD_MARKER_WIDTH_FT = 4   # Max width per NCAA rules
YARD_MARKER_TOP_DIST_FT = 27  # 9 yards * 3 feet/yard from sidelines

def load_yard_marker_model(model_path="yolo_models/bestYardMarkerDetector.pt"):
    """Load the YOLO model for yard marker detection"""
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        print(f"Error loading yard marker model: {e}")
        print("Please ensure you have a trained YOLO model for yard marker detection")
        return None

def detect_yard_markers(image_path, model):
    """
    Detect yard markers in the image using YOLO
    
    Args:
        image_path: Path to input image
        model: YOLO model for yard marker detection
    
    Returns:
        List of detected yard markers with bounding boxes and labels
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    
    # Run YOLO detection
    results = model(image, verbose=False, conf=0.3)
    
    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls.cpu().item())
            conf = float(box.conf.cpu().item())
            label = model.names[cls_id]
            
            # Parse yard marker label (e.g., "fl1", "nr5", etc.)
            if len(label) >= 3:  # Minimum length for valid yard marker
                x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                width = x2 - x1
                height = y2 - y1
                
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": {
                        "x1": float(x1),
                        "y1": float(y1),
                        "x2": float(x2),
                        "y2": float(y2),
                        "center_x": float(center_x),
                        "center_y": float(center_y),
                        "width": float(width),
                        "height": float(height)
                    }
                })
    
    return detections

def parse_yard_marker_label(label):
    """
    Parse yard marker label to extract position and yard information
    
    Args:
        label: Yard marker label (e.g., "fl1", "nr5")
    
    Returns:
        Dictionary with parsed information
    """
    if len(label) < 3:
        return None
    
    # Extract components
    near_far = label[0]  # 'f' for far, 'n' for near
    left_right = label[1]  # 'l' for left, 'r' for right
    yard_str = label[2:]  # Yard number as string
    
    try:
        yard_number = int(yard_str)
    except ValueError:
        return None
    
    return {
        "near_far": near_far,
        "left_right": left_right,
        "yard_number": yard_number,
        "original_label": label
    }

def calculate_field_coordinates(parsed_label, bbox, image_width, image_height):
    """
    Calculate field coordinates based on NCAA standards
    
    Args:
        parsed_label: Parsed yard marker information
        bbox: Bounding box of the detection
        image_width: Width of the input image
        image_height: Height of the input image
    
    Returns:
        Dictionary with field coordinates in feet
    """
    if not parsed_label:
        return None
    
    # Get image center and dimensions
    image_center_x = image_width / 2
    image_center_y = image_height / 2
    
    # Calculate relative position from image center
    rel_x = (bbox["center_x"] - image_center_x) / image_width
    rel_y = (bbox["center_y"] - image_center_y) / image_height
    
    # Convert to field coordinates (in feet)
    # Assuming the field spans most of the image width
    field_x = rel_x * FIELD_LENGTH_FT + FIELD_LENGTH_FT / 2  # Center at 50-yard line
    field_y = rel_y * FIELD_WIDTH_FT + FIELD_WIDTH_FT / 2   # Center at field middle
    
    # Adjust based on yard marker position
    yard_number = parsed_label["yard_number"]
    near_far = parsed_label["near_far"]
    left_right = parsed_label["left_right"]
    
    # Calculate expected yard line position
    if yard_number == 5:  # Special case for 5-yard markers
        expected_yard_line = 5 if near_far == 'n' else 115  # Near 5 or far 5
    else:
        # Regular yard markers (1-4)
        if near_far == 'n':  # Near side
            expected_yard_line = 10 + yard_number * 10  # 20, 30, 40, 50
        else:  # Far side
            expected_yard_line = 70 + yard_number * 10  # 80, 90, 100, 110
    
    # Calculate expected hash mark position
    if left_right == 'l':  # Left hash
        expected_hash_y = HASH_DISTANCE_FT
    else:  # Right hash
        expected_hash_y = FIELD_WIDTH_FT - HASH_DISTANCE_FT
    
    # Refine coordinates based on expected positions
    field_x = expected_yard_line * 3  # Convert yards to feet
    field_y = expected_hash_y
    
    return {
        "x": field_x,
        "y": field_y,
        "yard_line": expected_yard_line,
        "hash_side": left_right,
        "near_far": near_far,
        "yard_number": yard_number
    }

def findCorrespondancePoints(image_path, model_path="yolo_models/yardMarkerDetector.pt"):
    """
    Find correspondence points using automated yard marker detection
    
    Args:
        image_path: Path to reference image
        model_path: Path to YOLO model for yard marker detection
    
    Returns:
        List of correspondence points
    """
    # Load model
    model = load_yard_marker_model(model_path)
    if model is None:
        return []
    
    # Detect yard markers
    detections = detect_yard_markers(image_path, model)
    print(f"Detected {len(detections)} yard markers")
    
    # Load image to get dimensions
    image = cv2.imread(image_path)
    image_height, image_width = image.shape[:2]
    
    correspondence_points = []
    
    for detection in detections:
        # Parse the yard marker label
        parsed = parse_yard_marker_label(detection["label"])
        if not parsed:
            continue
        
        # Calculate field coordinates
        field_coords = calculate_field_coordinates(
            parsed, detection["bbox"], image_width, image_height
        )
        
        if field_coords:
            correspondence_points.append({
                "image_point": {
                    "x": detection["bbox"]["center_x"],
                    "y": detection["bbox"]["center_y"]
                },
                "field_point": {
                    "x": field_coords["x"],
                    "y": field_coords["y"]
                },
                "yard_marker_info": {
                    "label": detection["label"],
                    "yard_line": field_coords["yard_line"],
                    "hash_side": field_coords["hash_side"],
                    "near_far": field_coords["near_far"],
                    "yard_number": field_coords["yard_number"],
                    "confidence": detection["confidence"]
                }
            })
    
    print(f"Generated {len(correspondence_points)} correspondence points")
    return correspondence_points

def save_correspondence_points(points, output_path):
    """
    Save correspondence points to JSON file
    
    Args:
        points: List of correspondence points
        output_path: Path to output JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create the output structure
    output_data = {
        "correspondences": points,
        "metadata": {
            "total_points": len(points),
            "field_dimensions": {
                "length_ft": FIELD_LENGTH_FT,
                "width_ft": FIELD_WIDTH_FT,
                "hash_distance_ft": HASH_DISTANCE_FT
            },
            "ncaa_standards": {
                "yard_marker_height_ft": YARD_MARKER_HEIGHT_FT,
                "yard_marker_width_ft": YARD_MARKER_WIDTH_FT,
                "yard_marker_top_distance_ft": YARD_MARKER_TOP_DIST_FT
            }
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Correspondence points saved to: {output_path}")

def validate_correspondence_points(points):
    """
    Validate that we have enough correspondence points for homography
    
    Args:
        points: List of correspondence points
    
    Returns:
        Boolean indicating if we have sufficient points
    """
    if len(points) < 4:
        print(f"Warning: Only {len(points)} correspondence points found. Need at least 4 for homography.")
        return False
    
    # Check for diversity in yard lines
    yard_lines = set()
    for point in points:
        yard_lines.add(point["yard_marker_info"]["yard_line"])
    
    if len(yard_lines) < 2:
        print(f"Warning: Only {len(yard_lines)} unique yard lines found. Need at least 2 for good homography.")
        return False
    
    print(f"✓ Found {len(points)} correspondence points across {len(yard_lines)} yard lines")
    return True

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Correspondence Points Detection')
    parser.add_argument('--image', type=str, required=True, help='Path to reference image')
    parser.add_argument('--output', type=str, default='cache/correspondence/correspondences.json', 
                       help='Path to output JSON file')
    parser.add_argument('--model', type=str, default='yolo_models/yardMarkerDetector.pt',
                       help='Path to YOLO model for yard marker detection')
    parser.add_argument('--min-points', type=int, default=4,
                       help='Minimum number of correspondence points required (default: 4)')
    
    args = parser.parse_args()
    
    try:
        # Find correspondence points
        points = findCorrespondancePoints(args.image, args.model)
        
        # Validate points
        if not validate_correspondence_points(points):
            print("Insufficient correspondence points found. Please check your image and model.")
            return 1
        
        # Save points
        save_correspondence_points(points, args.output)
        
        # Print summary
        print("\n=== CORRESPONDENCE POINTS SUMMARY ===")
        for i, point in enumerate(points):
            info = point["yard_marker_info"]
            print(f"{i+1}. {info['label']} -> Yard {info['yard_line']}, {info['hash_side']} hash, {info['near_far']} side")
            print(f"   Image: ({point['image_point']['x']:.1f}, {point['image_point']['y']:.1f})")
            print(f"   Field: ({point['field_point']['x']:.1f}, {point['field_point']['y']:.1f}) ft")
            print(f"   Confidence: {info['confidence']:.3f}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())