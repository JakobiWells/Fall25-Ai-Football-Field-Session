import cv2
import pytesseract

# Load image
img = cv2.imread("testing_data/image.png")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Threshold to highlight white numbers
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

# Use pytesseract to detect digits with bounding boxes
detection_data = pytesseract.image_to_data(
    thresh,
    config="--psm 6 outputbase digits",  # look only for digits
    output_type=pytesseract.Output.DICT
)

# Loop over detected text
for i, text in enumerate(detection_data["text"]):
    if text.strip().isdigit():  # keep only numbers
        x, y, w, h = (detection_data["left"][i],
                      detection_data["top"][i],
                      detection_data["width"][i],
                      detection_data["height"][i])

        # Draw rectangle around detected number
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        print(f"Detected yard number: {text} at location (x={x}, y={y})")

# Save and show results
cv2.imwrite("yard_numbers_detected.jpg", img)
cv2.imshow("Detected Yard Numbers", img)
cv2.waitKey(0)
cv2.destroyAllWindows()