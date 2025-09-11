import cv2
import json
import argparse

def displayBoundingBoxes(image_path, json_path):
    """
    Display bounding boxes from JSON on the given image.
    
    Args:
        image_path: Path to the input PNG image
        json_path: Path to the detection JSON file

        Example: python displayBoundingBox.py --image testing_data/image.png --json cache/playerDetection.json
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Load detections
    with open(json_path, "r") as f:
        data = json.load(f)

    # Assume we want the first (or only) frame in JSON
    if "frames" not in data or len(data["frames"]) == 0:
        print("No frames found in JSON")
        return

    detections = data["frames"][0].get("detections", [])

    # Draw bounding boxes
    for det in detections:
        bbox = det["bbox"]
        x1, y1, x2, y2 = int(bbox["x1"]), int(bbox["y1"]), int(bbox["x2"]), int(bbox["y2"])
        label = det["class"]
        conf = det["confidence"]

        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Put label
        text = f"{label} {conf:.2f}"
        cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

    # Show image
    cv2.imshow("Detections", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Display bounding boxes from JSON on image")
    parser.add_argument("--image", type=str, required=True, help="Path to input PNG image")
    parser.add_argument("--json", type=str, required=True, help="Path to detection JSON file")
    args = parser.parse_args()

    displayBoundingBoxes(args.image, args.json)


if __name__ == "__main__":
    main()