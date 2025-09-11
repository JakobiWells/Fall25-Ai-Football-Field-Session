import cv2
import json

# Load image
img = cv2.imread("testing_data/image.png")
if img is None:
    raise FileNotFoundError("Could not load image. Check path!")

clone = img.copy()
points = []

def redraw_image():
    """Redraws the image with all points and labels"""
    global img, clone, points
    img = clone.copy()
    for p in points:
        cv2.circle(img, (p["x"], p["y"]), 5, (0, 0, 255), -1)
        label = f"{p['yard']}-{p['hash']}"
        cv2.putText(img, label, (p["x"]+5, p["y"]-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.imshow("Image", img)

def click_event(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        # Place red dot first
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Image", img)

        # Now ask for labels
        yard = input("Enter yard line (e.g., 20, 30, 40): ")
        hash_side = input("Enter hash side (close/far): ")

        # Save info
        points.append({"x": x, "y": y, "yard": yard, "hash": hash_side})
        redraw_image()

# Show image
cv2.imshow("Image", img)
cv2.setMouseCallback("Image", click_event)

print("Instructions:")
print("- Left click to add a point (dot shows immediately, then terminal prompt).")
print("- Press 'u' in the image window to undo the last point.")
print("- Press 'q' to quit and save.")

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("u"):  # Undo last point
        if points:
            points.pop()
            print("Undid last point.")
            redraw_image()
    elif key == ord("q"):  # Quit
        break

cv2.destroyAllWindows()

# Save points
with open("points.json", "w") as f:
    json.dump(points, f, indent=2)

print("Saved points:", points)