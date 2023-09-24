import cv2
import numpy as np
import time
import sys
import os

from ultralytics import YOLO

# Define some parameters
CONFIDENCE = 0.5
font_scale = 1
thickness = 1
labels = open("data/coco.names").read().strip().split("\n")
colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

# Load the YOLOv8 model with the default weight file
model = YOLO("yolov8n.pt")

# Read the file from the folder
video_file = 'DemoVideos/lowLightStreet.mp4'
cap = cv2.VideoCapture(video_file)

# Get original frame width, height, and frame rate
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_rate = int(cap.get(5))

# Generate an output filename with a unique number
output_dir = 'output_videos'
os.makedirs(output_dir, exist_ok=True)
output_num = 1
output_filename = os.path.join(output_dir, f'surveillanceVid{output_num}.mp4')
while os.path.exists(output_filename):
    output_num += 1
    output_filename = os.path.join(
        output_dir, f'surveillanceVid{output_num}.mp4')

# Create the VideoWriter with the same frame rate as the input video
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter(output_filename, fourcc, frame_rate,
                      (frame_width, frame_height))

# Variables to track detected persons
person_detected = 0

while True:
    _, image = cap.read()

    if image is None:
        break

    start = time.perf_counter()
    results = model.predict(image, conf=CONFIDENCE)[0]
    time_took = time.perf_counter() - start

    # Loop over the detections
    for data in results.boxes.data.tolist():
        # Get the bounding box coordinates, confidence, and class id
        xmin, ymin, xmax, ymax, confidence, class_id = data
        # Converting the coordinates and the class id to integers
        xmin = int(xmin)
        ymin = int(ymin)
        xmax = int(xmax)
        ymax = int(ymax)
        class_id = int(class_id)

        if labels[class_id] == "person":
            person_detected += 1
            if person_detected == 2:  # Capture screenshot for the detected person
                text = f"{labels[class_id]}"
                color = [int(c) for c in colors[class_id]]
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax),
                              color=color, thickness=thickness)
                cv2.putText(image, text, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=font_scale, color=color, thickness=thickness)
                screenshot = image.copy()
                cv2.imwrite('screenshot.jpg', screenshot)
                break  # Stop processing after capturing the screenshot if person is captured

        # Draw a bounding box rectangle and label on the image
        color = [int(c) for c in colors[class_id]]
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax),
                      color=color, thickness=thickness)
        text = f"{labels[class_id]}: {confidence:.2f}"

        # Calculate text width & height to draw the transparent boxes as background of the text
        (text_width, text_height) = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)[0]
        text_offset_x = xmin
        text_offset_y = ymin - 5
        box_coords = ((text_offset_x, text_offset_y),
                      (text_offset_x + text_width + 2, text_offset_y - text_height))

        overlay = image.copy()
        cv2.rectangle(
            overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)

        # Add opacity (transparency to the box)
        image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)

        # Now put the text (label: confidence %)
        cv2.putText(image, text, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale, color=(0, 0, 0), thickness=thickness)

    # Calculate the frame per second and draw it on the frame
    fps = f"FPS: {frame_rate:.2f}"
    cv2.putText(image, fps, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
    out.write(image)
    cv2.imshow("image", image)

    # PRESS 'Q' TO END THE recording
    if ord("q") == cv2.waitKey(1):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
