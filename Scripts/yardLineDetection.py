#MAY NOT BE NEEDED

# script to detect yard lines in a video file
#input: video file
#output: json file with frame by frame yard line detection data
#saved as yardLineDetection.json in the cache folder

#sample json output:
# Example of the expected JSON output format for yard line detections:
# {
#     "frames": [
#         {
#             "frame_number": 0,
#             "timestamp": 0.0,
#             "detections": [
#                 {
#                     "class": "yard_line",
#                     "class_id": 0,
#                     "confidence": 0.852,
#                     "bbox": {
#                         "x1": 592.7,
#                         "y1": 381.6,
#                         "x2": 617.7,
#                         "y2": 444.4,
#                         "width": 25.0,
#                         "height": 62.7,
#                         "center_x": 605.2,
#                         "center_y": 413.0
#                     }
#                 }
#             ]
#         }
#     ]
# }