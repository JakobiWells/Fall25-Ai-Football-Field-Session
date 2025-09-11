import cv2
import numpy as np
import json

# Load clicked points
with open("points.json", "r") as f:
    data = json.load(f)

src_points = np.array([[p["x"], p["y"]] for p in data], dtype=np.float32)

# Destination points in field coordinates (yards across and length)
dst_points = np.array([
    [50, 20.0],   # 50 close
    [50, 33.3],   # 50 far
    [40, 20.0],   # 40 close
    [40, 33.3]    # 40 far
], dtype=np.float32)

# Homography
H, status = cv2.findHomography(src_points, dst_points)
print("Homography matrix:\n", H)

# Example: warp the frame into field coordinates
img = cv2.imread("frame.jpg")
height, width = 600, 1200  # size in pixels for visualization
warped = cv2.warpPerspective(img, H, (width, height))

cv2.imshow("Warped", warped)
cv2.waitKey(0)
cv2.destroyAllWindows()