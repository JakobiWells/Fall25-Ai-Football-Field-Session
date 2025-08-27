import cv2
import numpy as np

# Load the image
image = cv2.imread("testing_data/image.png")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Threshold to keep only bright/white areas
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# Edge detection
edges = cv2.Canny(thresh, 255/3, 255, apertureSize=5) 

cv2.imshow("Edges", edges)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Hough Line Transform
lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    threshold=100,       # lower to detect more lines
    minLineLength=200,  # longer min length so sidelines are caught
    maxLineGap=100       # allow gaps to connect broken lines
)

# Draw detected lines
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2) # Red color for lines

# Save and show results
cv2.imwrite("detected_lines.jpg", image)
cv2.imshow("Detected Lines", image)
print("Press any key to close the window...")
cv2.waitKey(0)
cv2.destroyAllWindows()