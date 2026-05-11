# detector.py
from ultralytics import YOLO

class PersonDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []

        frame_h, frame_w = frame.shape[:2]
        min_height = frame_h * 0.15   # person must be at least 15% of frame height
        min_width  = frame_w * 0.05   # person must be at least 5% of frame width

        for box in results.boxes:
            class_id   = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == 0 and confidence > 0.55:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w = x2 - x1
                h = y2 - y1

                # ── Filter out small detections (hands, arms) ──
                if w < min_width or h < min_height:
                    continue

                detections.append([x1, y1, x2, y2, confidence])

        return detections