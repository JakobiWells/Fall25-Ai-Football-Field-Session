import cv2
import json
import os
from ultralytics import YOLO

def playerDetection(image_path, model_path="yolov8n.pt"):
    """
    Detect players in a single image
    
    Args:
        image_path: Path to input image file
        model_path: Path to YOLO model weights
    
    Returns:
        Dictionary with detection results


        Usage: python playerDetection.py --image path/to/image.jpg --output path/to/output.json --model path/to/model.pt

        Example: python playerDetection.py --image testing_data/image.png --output cache/playerDetection.json --model yolov8n.pt
    """
    # Load model
    model = YOLO(model_path)

    # Load image
    frame = cv2.imread(image_path)
    if frame is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    detections = []
    results = model(frame, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls.cpu().item())
            conf = float(box.conf.cpu().item())
            label = model.names[cls_id]

            if label.lower() != "player":  # only keep players
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()
            width = x2 - x1
            height = y2 - y1
            center_x = x1 + width / 2
            center_y = y1 + height / 2

            detections.append({
                "class": label,
                "class_id": cls_id,
                "confidence": conf,
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "width": width,
                    "height": height,
                    "center_x": center_x,
                    "center_y": center_y
                }
            })

    return {
        "frames": [
            {
                "frame_number": 0,
                "timestamp": 0.0,
                "detections": detections
            }
        ]
    }


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Player Detection Module (Image)')
    parser.add_argument('--image', type=str, required=True, help='Path to input image file')
    parser.add_argument('--output', type=str, default='cache/playerDetection.json', 
                       help='Path to output JSON file')
    parser.add_argument('--model', type=str, default='yolov8n.pt', 
                       help='Path to YOLO model weights')
    
    args = parser.parse_args()

    results = playerDetection(args.image, args.model)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Detections saved to {args.output}")


if __name__ == "__main__":
    main()