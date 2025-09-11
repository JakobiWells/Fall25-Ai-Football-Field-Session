import cv2
import easyocr
import os

# make output folder for debug crops
os.makedirs("ocr_debug", exist_ok=True)

# load image
image_path = "testing_data/image.png"
img = cv2.imread(image_path)

# grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# adaptive threshold (better for uneven lighting)
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV, 11, 2
)

# morphology (thickens digits)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# init EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

# restrict to digits only
results = reader.readtext(morph, allowlist='0123456789')

# draw detections + save cropped attempts
for i, (bbox, text, conf) in enumerate(results):
    print(f"Detected: {text} (conf {conf:.2f})")

    # draw on original image
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(img, text, (top_left[0], top_left[1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    # crop and save debug image
    x_min = min(int(p[0]) for p in bbox)
    y_min = min(int(p[1]) for p in bbox)
    x_max = max(int(p[0]) for p in bbox)
    y_max = max(int(p[1]) for p in bbox)
    crop = img[y_min:y_max, x_min:x_max]
    cv2.imwrite(f"ocr_debug/crop_{i}_{text}.png", crop)

# save annotated result
cv2.imwrite("image_detected.png", img)