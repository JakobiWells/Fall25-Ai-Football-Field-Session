import cv2
from ultralytics import YOLO
import os

# Load a pretrained YOLO model
# Choose from: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
#model = YOLO("yolov8n.pt")  # Extra Large model - best accuracy
model = YOLO("Football Player Detection.v2i.yolov8/train/weights/best.pt")
# Input video path
input_video = "testing_data/soccer.mp4"
output_video = "output_detection.mp4"

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
    
    frame_count += 1
    if frame_count % 30 == 0:  # Print progress every 30 frames
        progress = (frame_count / total_frames) * 100
        print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Video processing complete! Output saved to: {output_video_path}")
print(f"File size: {os.path.getsize(output_video_path) / (1024*1024):.2f} MB")

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