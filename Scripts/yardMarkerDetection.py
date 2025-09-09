#MAY NOT BE NEEDED

# script to detect yard markers in a video file
#input: video file
#output: json file with frame by frame yard marker detection data,
#saved as yardMarkerDetection.json in the cache folder

#sample json output:
# Example of the expected JSON output format for yard marker detections:
# {
#     "frames": [
#         {
#             "frame_number": 0,
#             "timestamp": 0.0,
#             "detections": [
#                 {
#                     "class": "yard_marker",
#                     "class_id": 0,
#                     "confidence": 0.852,
#                     "bbox": {
#                         "x1": 592.7,
#                         "y1": 381.6,
#                         "x2": 617.7,
#                         "y2": 444.4,