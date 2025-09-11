import cv2
from ultralytics import YOLO
import os
import json
from datetime import datetime

# Load a pretrained YOLO model
# Choose from: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
#model = YOLO("bestsecondtryX.pt")  # Extra Large model - best accuracy
model = YOLO("bestX.pt")
# Input video path
input_video = "football_film/Wide - Clip 005.mp4"
#input_video = "nfl.mp4"
output_video = "output_detection.mp4"
output_text = "detection_results.txt"
output_json = "detection_results.json"

# Open the input video
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    print(f"Error: Could not open video {input_video}")
    exit()

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Processing video: {input_video}")
print(f"Output video: {output_video}")
print(f"Output text: {output_text}")
print(f"Output JSON: {output_json}")
print(f"FPS: {fps}, Resolution: {width}x{height}, Total frames: {total_frames}")

# Try different codecs for better compatibility
codecs_to_try = [
    ('avc1', '.mp4'),  # H.264 codec - most compatible
    ('mp4v', '.mp4'),  # MPEG-4 codec
    ('XVID', '.avi'),  # XVID codec - very compatible
    ('MJPG', '.avi')   # Motion JPEG - universal compatibility
]

output_video_path = None
out = None

for codec, extension in codecs_to_try:
    try:
        test_output = f"output_detection{extension}"
        fourcc = cv2.VideoWriter_fourcc(*codec)
        test_writer = cv2.VideoWriter(test_output, fourcc, fps, (width, height))
        
        if test_writer.isOpened():
            print(f"Successfully created video writer with codec: {codec}")
            output_video_path = test_output
            out = test_writer
            break
        else:
            test_writer.release()
            print(f"Failed to create video writer with codec: {codec}")
    except Exception as e:
        print(f"Error with codec {codec}: {e}")
        continue

if out is None:
    print("Error: Could not create video writer with any codec")
    cap.release()
    exit()

print(f"Using output format: {output_video_path}")

# Initialize output files
with open(output_text, 'w') as f:
    f.write(f"Detection Results for {input_video}\n")
    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Video Info: {width}x{height}, {fps} FPS, {total_frames} frames\n")
    f.write("="*80 + "\n\n")


# Store all results for JSON export
all_results = {
    "video_info": {
        "input_file": input_video,
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": total_frames,
        "generated": datetime.now().isoformat()
    },
    "frames": []
}

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Perform YOLO detection on the frame
    results = model(frame)
    
    # Draw the results on the frame
    annotated_frame = results[0].plot()
    
    # Write the annotated frame to output video
    out.write(annotated_frame)
    
    # Extract and save detection data
    frame_data = {
        "frame_number": frame_count,
        "timestamp": frame_count / fps,
        "detections": []
    }
    
    # Write to text file
    with open(output_text, 'a') as f:
        f.write(f"Frame {frame_count:04d} (Time: {frame_count/fps:.2f}s):\n")
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:

                for i, box in enumerate(boxes):
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = result.names[cls]
                    
                    # Get keypoints if available (these are the points you see on the lines)
                    keypoints = None
                    keypoint_names = None
                    
                    # Check for keypoints in the result
                    if hasattr(result, 'keypoints') and result.keypoints is not None:
                        try:
                            # Get keypoints for this specific detection (i-th detection)
                            # The keypoints tensor has shape [num_detections, num_keypoints, 3]
                            kp_data = result.keypoints[i]  # Shape: [num_keypoints, 3]
                            
                            if hasattr(kp_data, 'xy'):
                                # Get xy coordinates (first 2 values)
                                xy_data = kp_data.xy.cpu().numpy()
                                keypoints = []
                                for point in xy_data:
                                    # Convert numpy arrays to Python floats
                                    x = float(point[0]) if isinstance(point[0], (int, float)) else float(point[0].item())
                                    y = float(point[1]) if isinstance(point[1], (int, float)) else float(point[1].item())
                                    keypoints.append([x, y])
                            elif hasattr(kp_data, 'data'):
                                # Get raw data and extract x,y coordinates
                                raw_data = kp_data.data.cpu().numpy()
                                keypoints = []
                                for point in raw_data:
                                    x = float(point[0]) if isinstance(point[0], (int, float)) else float(point[0].item())
                                    y = float(point[1]) if isinstance(point[1], (int, float)) else float(point[1].item())
                                    keypoints.append([x, y])
                            else:
                                # Try numpy method and extract x,y coordinates
                                raw_data = kp_data.cpu().numpy()
                                keypoints = []
                                for point in raw_data:
                                    x = float(point[0]) if isinstance(point[0], (int, float)) else float(point[0].item())
                                    y = float(point[1]) if isinstance(point[1], (int, float)) else float(point[1].item())
                                    keypoints.append([x, y])
                            
                            # For lines, we expect 2 keypoints (start and end)
                            if keypoints and len(keypoints) == 2:
                                keypoint_names = ["start_point", "end_point"]
                            elif keypoints:
                                keypoint_names = [f"point_{j+1}" for j in range(len(keypoints))]
                            
                        except Exception as e:
                            print(f"Error extracting keypoints for detection {i}: {e}")
                            # Debug: Let's see what the data actually looks like
                            if i == 0:  # Only for first detection to avoid spam
                                print(f"Debug - kp_data type: {type(kp_data)}")
                                if hasattr(kp_data, 'xy'):
                                    print(f"Debug - xy shape: {kp_data.xy.shape}")
                                    print(f"Debug - xy type: {type(kp_data.xy)}")
                                    print(f"Debug - xy[0] type: {type(kp_data.xy[0])}")
                                    print(f"Debug - xy[0][0] type: {type(kp_data.xy[0][0])}")
                            keypoints = None
                    
                    # Alternative: check if keypoints are in the box object
                    elif hasattr(box, 'keypoints') and box.keypoints is not None:
                        try:
                            kp_data = box.keypoints[0]
                            if hasattr(kp_data, 'xy'):
                                keypoints = kp_data.xy.cpu().numpy().tolist()
                            elif hasattr(kp_data, 'data'):
                                keypoints = kp_data.data.cpu().numpy().tolist()
                            else:
                                keypoints = kp_data.cpu().numpy().tolist()
                            
                            if keypoints and len(keypoints) == 2:
                                keypoint_names = ["start_point", "end_point"]
                        except Exception as e:
                            print(f"Error extracting box keypoints: {e}")
                            keypoints = None
                    
                    # Write to text file
                    f.write(f"  Detection {i+1}: {class_name} (conf: {conf:.3f})\n")
                    f.write(f"    Bounding Box: ({x1:.1f}, {y1:.1f}) to ({x2:.1f}, {y2:.1f})\n")
                    f.write(f"    Width: {x2-x1:.1f}, Height: {y2-y1:.1f}\n")
                    
                    if keypoints:
                        f.write(f"    Keypoints ({len(keypoints)} points):\n")
                        for j, kp in enumerate(keypoints):
                            point_name = keypoint_names[j] if keypoint_names and j < len(keypoint_names) else f"point_{j+1}"
                            # Each kp should be [x, y] list
                            if isinstance(kp, (list, tuple)) and len(kp) >= 2:
                                x, y = kp[0], kp[1]
                                f.write(f"      {point_name}: ({x:.1f}, {y:.1f})\n")
                            else:
                                f.write(f"      {point_name}: Invalid format - {kp}\n")
                    else:
                        f.write(f"    No keypoints detected\n")
                    
                    # Store for JSON
                    detection_data = {
                        "class": class_name,
                        "class_id": cls,
                        "confidence": conf,
                        "bbox": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2),
                            "width": float(x2 - x1),
                            "height": float(y2 - y1),
                            "center_x": float((x1 + x2) / 2),
                            "center_y": float((y1 + y2) / 2)
                        }
                    }
                    
                    if keypoints:
                        detection_data["keypoints"] = {
                            "points": keypoints,
                            "names": keypoint_names
                        }
                    
                    frame_data["detections"].append(detection_data)
                    
                f.write(f"  Total detections: {len(boxes)}\n")
            else:
                f.write("  No detections\n")
        
        f.write("\n")
    
    # Add frame data to all results
    all_results["frames"].append(frame_data)
    
    frame_count += 1
    if frame_count % 30 == 0:  # Print progress every 30 frames
        progress = (frame_count / total_frames) * 100
        print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

# Save JSON results
with open(output_json, 'w') as f:
    json.dump(all_results, f, indent=2)

# Write summary to text file
with open(output_text, 'a') as f:
    f.write("="*80 + "\n")
    f.write("SUMMARY\n")
    f.write("="*80 + "\n")
    
    total_detections = sum(len(frame["detections"]) for frame in all_results["frames"])
    frames_with_detections = sum(1 for frame in all_results["frames"] if frame["detections"])
    total_keypoints = sum(
        len(detection.get("keypoints", {}).get("points", [])) 
        for frame in all_results["frames"] 
        for detection in frame["detections"]
    )
    
    f.write(f"Total frames processed: {frame_count}\n")
    f.write(f"Frames with detections: {frames_with_detections}\n")
    f.write(f"Total detections: {total_detections}\n")
    f.write(f"Total keypoints detected: {total_keypoints}\n")
    f.write(f"Average detections per frame: {total_detections/frame_count:.2f}\n")
    
    # Count by class
    class_counts = {}
    for frame in all_results["frames"]:
        for detection in frame["detections"]:
            class_name = detection["class"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    f.write("\nDetections by class:\n")
    for class_name, count in sorted(class_counts.items()):
        f.write(f"  {class_name}: {count}\n")

print(f"Video processing complete! Output saved to: {output_video_path}")
print(f"Text results saved to: {output_text}")
print(f"JSON results saved to: {output_json}")
print(f"Video file size: {os.path.getsize(output_video_path) / (1024*1024):.2f} MB")

# Try to open the video to verify it was created successfully
if os.path.exists(output_video_path):
    print(f"Output file exists and is accessible")
    # Try to open it with cv2 to verify it's readable
    test_cap = cv2.VideoCapture(output_video_path)
    if test_cap.isOpened():
        test_frames = int(test_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        test_cap.release()
        print(f"Output video is readable and contains {test_frames} frames")
    else:
        print("Warning: Output video was created but cannot be read back")
else:
    print("Error: Output file was not created")