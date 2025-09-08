# install first if you don't have it:
# pip install easyocr opencv-python

import cv2
import easyocr

# Initialize EasyOCR reader (English digits are included in 'en')
reader = easyocr.Reader(['en'])

# Load an image (replace with your own frame or test photo)
image_path = "testing_data/image.png"
image = cv2.imread(image_path)

# Run OCR
results = reader.readtext(image)

# Draw results on the image
for (bbox, text, prob) in results:
    # Only keep numeric detections
    if text.isdigit():
        # Bounding box is a list of 4 points
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

        # Draw rectangle and put text
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, f"{text} ({prob:.2f})", (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# Show the result
cv2.imshow("Detected Numbers", image)
cv2.waitKey(0)
cv2.destroyAllWindows()