import cv2
import numpy as np
import easyocr
import os

def detect_yard_lines(image):
    """Detect horizontal yard lines using Hough line detection"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect lines
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    yard_lines = []
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            # Filter for nearly horizontal lines (yard lines)
            if abs(theta - np.pi/2) < 0.1 or abs(theta) < 0.1:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                yard_lines.append(((x1, y1), (x2, y2)))
    
    return yard_lines

def extract_yard_marker_regions(image, yard_lines):
    """Extract regions around yard lines where numbers should be"""
    regions = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    for line in yard_lines:
        (x1, y1), (x2, y2) = line
        
        # Create a region around the yard line
        # Yard markers are typically 2-3 feet wide and centered on the line
        line_y = (y1 + y2) // 2
        
        # Extract a horizontal strip around the line
        margin = 30  # pixels above and below the line
        x_start = max(0, min(x1, x2) - 50)
        x_end = min(image.shape[1], max(x1, x2) + 50)
        y_start = max(0, line_y - margin)
        y_end = min(image.shape[0], line_y + margin)
        
        region = image[y_start:y_end, x_start:x_end]
        if region.size > 0:
            regions.append({
                'region': region,
                'line_y': line_y,
                'x_start': x_start,
                'y_start': y_start
            })
    
    return regions

def enhance_for_ocr(region):
    """Enhance image region specifically for number detection"""
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def main():
    # Load image
    image_path = "testing_data/image.png"
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Could not load image: {image_path}")
        return
    
    print("Detecting yard lines...")
    yard_lines = detect_yard_lines(image)
    print(f"Found {len(yard_lines)} yard lines")
    
    # Draw yard lines on image
    line_image = image.copy()
    for line in yard_lines:
        cv2.line(line_image, line[0], line[1], (0, 255, 0), 2)
    
    # Extract regions around yard lines
    print("Extracting yard marker regions...")
    regions = extract_yard_marker_regions(image, yard_lines)
    print(f"Extracted {len(regions)} regions")
    
    # Create output directory
    os.makedirs("yard_marker_debug", exist_ok=True)
    
    # Initialize OCR
    reader = easyocr.Reader(['en'], gpu=False)
    
    # Process each region
    all_detections = []
    for i, region_data in enumerate(regions):
        region = region_data['region']
        
        # Enhance the region for OCR
        enhanced = enhance_for_ocr(region)
        
        # Save debug images
        cv2.imwrite(f"yard_marker_debug/region_{i}_original.png", region)
        cv2.imwrite(f"yard_marker_debug/region_{i}_enhanced.png", enhanced)
        
        # Run OCR on enhanced region
        results = reader.readtext(enhanced, allowlist='0123456789', width_ths=0.7, height_ths=0.7)
        
        for (bbox, text, conf) in results:
            if conf > 0.5 and text.isdigit():  # Higher confidence threshold
                print(f"Region {i}: Detected '{text}' with confidence {conf:.2f}")
                
                # Convert bbox to original image coordinates
                (top_left, top_right, bottom_right, bottom_left) = bbox
                top_left = tuple(map(int, top_left))
                bottom_right = tuple(map(int, bottom_right))
                
                # Adjust coordinates to original image
                abs_top_left = (top_left[0] + region_data['x_start'], 
                               top_left[1] + region_data['y_start'])
                abs_bottom_right = (bottom_right[0] + region_data['x_start'], 
                                   bottom_right[1] + region_data['y_start'])
                
                all_detections.append({
                    'text': text,
                    'confidence': conf,
                    'bbox': (abs_top_left, abs_bottom_right)
                })
    
    # Draw all detections on original image
    result_image = image.copy()
    for detection in all_detections:
        bbox = detection['bbox']
        text = detection['text']
        conf = detection['confidence']
        
        cv2.rectangle(result_image, bbox[0], bbox[1], (0, 255, 0), 2)
        cv2.putText(result_image, f"{text} ({conf:.2f})", 
                   (bbox[0][0], bbox[0][1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Save results
    cv2.imwrite("yard_lines_detected.png", line_image)
    cv2.imwrite("yard_markers_detected.png", result_image)
    
    print(f"\nFinal results: Found {len(all_detections)} yard markers")
    for detection in all_detections:
        print(f"  - {detection['text']} (confidence: {detection['confidence']:.2f})")

if __name__ == "__main__":
    main()
