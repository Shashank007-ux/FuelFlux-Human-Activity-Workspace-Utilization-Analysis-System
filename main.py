# main.py
import cv2
import threading
import time
from detector import PersonDetector
from tracker import PersonTracker
from pose_analyzer import PoseAnalyzer
from activity_classifier import ActivityClassifier
from roi_manager import ROIManager
from logger import ActivityLogger
from config import VIDEO_SOURCE, OUTPUT_VIDEO, LOG_FILE

ACTIVITY_COLORS = {
    "Working":    (0, 255, 0),
    "Idle":       (0, 165, 255),
    "Break Time": (0, 0, 255),
    "Unknown":    (200, 200, 200)
}

# ── Threaded Camera Reader (prevents lag) ──────────────────────
class CameraReader:
    def __init__(self, source):
        self.cap     = cv2.VideoCapture(source)
        self.ret     = False
        self.frame   = None
        self.lock    = threading.Lock()
        self.running = True
        self.thread  = threading.Thread(target=self._read, daemon=True)
        self.thread.start()

    def _read(self):
        while self.running:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret  = ret
                self.frame = frame

    def get(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def release(self):
        self.running = False
        self.cap.release()

    def get_props(self):
        w   = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h   = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
        return w, h, fps


def draw_label(frame, text, x, y, color):
    """Draw a filled background behind the label text for readability."""
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 2)
    cv2.rectangle(frame, (x, y - th - 10), (x + tw + 4, y), color, -1)
    cv2.putText(frame, text, (x + 2, y - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 2)


def main():
    # ── Initialize Camera ──────────────────────────────────────
    print("[INFO] Starting camera...")
    cam = CameraReader(VIDEO_SOURCE)
    width, height, fps = cam.get_props()

    # ── Wait for first valid frame ─────────────────────────────
    print("[INFO] Waiting for first frame...")
    first_frame = None
    for _ in range(30):
        ret, frame = cam.get()
        if ret and frame is not None:
            first_frame = frame
            break
        time.sleep(0.1)

    if first_frame is None:
        print("[ERROR] Cannot open camera. Check VIDEO_SOURCE in config.py")
        return

    # ── ROI Selection ──────────────────────────────────────────
    roi = ROIManager()
    roi.select_roi(first_frame)

    # ── Video Writer ───────────────────────────────────────────
    out = cv2.VideoWriter(
        OUTPUT_VIDEO,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps, (width, height)
    )

    # ── Initialize All Modules ─────────────────────────────────
    detector   = PersonDetector()
    tracker    = PersonTracker()
    pose       = PoseAnalyzer()
    classifier = ActivityClassifier()
    logger     = ActivityLogger(LOG_FILE)

    # ── Processing Settings ────────────────────────────────────
    SCALE        = 0.5   # process at 50% size for speed
    DETECT_EVERY = 2     # run YOLO every N frames
    POSE_EVERY   = 4     # run pose every N frames

    # ── Cache last results (used on skipped frames) ────────────
    last_tracks    = []
    last_pose_data = {}   # pid -> pose_data dict
    last_labels    = {}   # pid -> (posture, activity, eye_direction)

    frame_count = 0
    prev_time   = time.time()

    print("[INFO] System running. Press Q to quit.")

    while True:
        ret, frame = cam.get()
        if not ret or frame is None:
            break

        frame_count += 1

        # ── Flip frame (mirror effect) ─────────────────────────
        frame = cv2.flip(frame, 1)

        # ── Resize for faster detection ────────────────────────
        small = cv2.resize(frame, (int(width * SCALE), int(height * SCALE)))

        # ── Detection every N frames ───────────────────────────
        if frame_count % DETECT_EVERY == 0:
            detections_small = detector.detect(small)

            # Scale detections back to original resolution
            detections = []
            for d in detections_small:
                x1, y1, x2, y2, conf = d
                detections.append([
                    int(x1 / SCALE), int(y1 / SCALE),
                    int(x2 / SCALE), int(y2 / SCALE),
                    conf
                ])

            last_tracks = tracker.update(detections, frame)

        # ── Process Each Tracked Person ────────────────────────
        for (pid, x1, y1, x2, y2) in last_tracks:
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            in_roi = roi.is_inside(cx, cy)

            # ── Pose + Classification every N frames ───────────
            if frame_count % POSE_EVERY == 0:
                pose_data = pose.analyze(frame, x1, y1, x2, y2)
                activity  = classifier.classify(pid, cx, cy, in_roi, pose_data)

                posture       = pose_data.get("posture", "unknown")
                eye_direction = pose_data.get("eye_direction", "unknown")

                last_pose_data[pid] = pose_data
                last_labels[pid]    = (posture, activity, eye_direction)
            else:
                # Use cached values on skipped frames
                pose_data = last_pose_data.get(pid, {})
                posture, activity, eye_direction = last_labels.get(
                    pid, ("unknown", "Unknown", "unknown")
                )

            # ── Log every 30 frames (~1 second) ───────────────
            if frame_count % 30 == 0:
                logger.log(pid, posture, activity, in_roi)

            # ── Draw Bounding Box ──────────────────────────────
            color = ACTIVITY_COLORS.get(activity, (200, 200, 200))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # ── Draw Labels (stacked) ──────────────────────────
            label1 = f"ID:{pid} | {posture.title()}"
            label2 = f"Status: {activity}"

            draw_label(frame, label1, x1, y1 - 35, color)
            draw_label(frame, label2, x1, y1 - 10, color)

            # ── ROI indicator dot ──────────────────────────────
            roi_color = (0, 255, 0) if in_roi else (0, 0, 255)
            cv2.circle(frame, (cx, cy), 5, roi_color, -1)

        # ── FPS Counter ────────────────────────────────────────
        curr_time = time.time()
        fps_val   = 1 / (curr_time - prev_time + 1e-6)
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps_val)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # ── Person count ───────────────────────────────────────
        cv2.putText(frame, f"Persons: {len(last_tracks)}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # ── Write & Display ────────────────────────────────────
        out.write(frame)
        cv2.imshow("FuelFlux Activity Analysis", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("[INFO] Releasing resources...")
    cam.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Done! Log saved to {LOG_FILE}")
    print(f"[INFO] Output video saved to {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()