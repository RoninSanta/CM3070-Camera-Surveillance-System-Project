import cv2
import numpy as np
import time
import sys
import os
import unittest
from ultralytics import YOLO

CONFIDENCE = 0.5
font_scale = 1
thickness = 1
labels = open("data/coco.names").read().strip().split("\n")
colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)
_, image = cap.read()
h, w = image.shape[:2]

# Define the desired video resolution
new_width = 1080  # Change to desired width
new_height = 720  # Change to desired height

# Determine the output filename with a unique number
output_dir = 'output_videos'
os.makedirs(output_dir, exist_ok=True)
output_num = 1
output_filename = os.path.join(output_dir, f'webCamVid{output_num}.mp4')
while os.path.exists(output_filename):
    output_num += 1
    output_filename = os.path.join(output_dir, f'webCamVid{output_num}.mp4')

fourcc = cv2.VideoWriter_fourcc(*"XVID")
# Specify the new resolution here
out = cv2.VideoWriter(output_filename, fourcc, 20.0, (new_width, new_height))

while True:
    _, image = cap.read()
    # Resize the captured frame to the new resolution
    image = cv2.resize(image, (new_width, new_height))

    start = time.perf_counter()
    results = model.predict(image, conf=CONFIDENCE)[0]
    time_took = time.perf_counter() - start
    print("Time took:", time_took)

    # loop over the detections
    for data in results.boxes.data.tolist():
        # get the bounding box coordinates, confidence, and class id
        xmin, ymin, xmax, ymax, confidence, class_id = data
        # converting the coordinates and the class id to integers
        xmin = int(xmin)
        ymin = int(ymin)
        xmax = int(xmax)
        ymax = int(ymax)
        class_id = int(class_id)

        # draw a bounding box rectangle and label on the image
        color = [int(c) for c in colors[class_id]]
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax),
                      color=color, thickness=thickness)
        text = f"{labels[class_id]}: {confidence:.2f}"
        # calculate text width & height to draw the transparent boxes as background of the text
        (text_width, text_height) = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)[0]
        text_offset_x = xmin
        text_offset_y = ymin - 5
        box_coords = ((text_offset_x, text_offset_y),
                      (text_offset_x + text_width + 2, text_offset_y - text_height))
        overlay = image.copy()
        cv2.rectangle(
            overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)
        # add opacity (transparency to the box)
        image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
        # now put the text (label: confidence %)
        cv2.putText(image, text, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=font_scale, color=(0, 0, 0), thickness=thickness)

    # end time to compute the fps
    end = time.perf_counter()
    # calculate the frame per second and draw it on the frame
    fps = f"FPS: {1 / (end - start):.2f}"
    cv2.putText(image, fps, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 6)
    out.write(image)
    cv2.imshow("image", image)

    if ord("q") == cv2.waitKey(1):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

'''
    5 UNIT TESTING PROCESS BELOW
    
    Tests for :
    1)Real-time Object Tracking |	Accurate real-time tracking	
    2)Object Recognition |	Correct object identification
    3)Video Capture Start Correctly |	Video capture starts 
    4)Video Capture Ends Correctly |	Video capture ends 
    5) YOLO Object Detection Accuracy|	Accurate object detection
'''


class TestVideoCapture(unittest.TestCase):
    def setUp(self):
        self.video_capture = cv2.VideoCapture(0)
        self.model = YOLO("yolov8n.pt")
        self.output_dir = 'test_the_output_videos'
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_num = 1

    def test_real_time_object_tracking(self):
        ret, frame = self.video_capture.read()
        self.assertTrue(ret)

    def test_object_recognition(self):
        ret, frame = self.video_capture.read()
        results = self.model.predict(frame, conf=0.5)[0]
        self.assertGreater(len(results.boxes.data.tolist()), 0)

    def test_video_capture_functionality(self):
        self.assertTrue(self.video_capture.isOpened())

    def test_object_counting(self):
        ret, frame = self.video_capture.read()
        results = self.model.predict(frame, conf=0.5)[0]
        object_count = len(results.boxes.data.tolist())
        self.assertGreater(object_count, 0)

    def test_yolo_object_detection_accuracy(self):
        ret, frame = self.video_capture.read()
        results = self.model.predict(frame, conf=0.5)[0]
        detected_objects = [labels[int(data[5])]
                            for data in results.boxes.data.tolist()]
        # The Expected objects to be identified
        expected_objects = ["person"]
        for obj in expected_objects:
            self.assertIn(obj, detected_objects)

    def tearDown(self):
        self.video_capture.release()
        cv2.destroyAllWindows()
        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))


if __name__ == "__main__":
    unittest.main()
