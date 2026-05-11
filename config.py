ROI = {
    "x1": 100,
    "y1": 100,
    "x2": 600,
    "y2": 500
}

# ─── Activity Classification Thresholds ───────────────────────
MOVEMENT_THRESHOLD = 10        # pixels moved between frames to count as "moving"
IDLE_TIME_SECONDS = 15         # seconds without movement = Idle
BREAK_ABSENCE_SECONDS = 2     # seconds outside ROI = Break Time
WORKING_MIN_SECONDS = 5        # seconds in ROI with low movement = Working

# ─── Video Settings ───────────────────────────────────────────
VIDEO_SOURCE = 0               # 0 = webcam, or path to video file e.g. "video.mp4"
OUTPUT_VIDEO = "output/videos/output.mp4"
LOG_FILE = "output/logs/activity_log.csv"