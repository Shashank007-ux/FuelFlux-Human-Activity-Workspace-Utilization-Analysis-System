# FuelFlux-Human-Activity-Workspace-Utilization-Analysis-System
A real-time computer vision system that detects, tracks, and classifies human activity in a workspace environment using pose estimation, hand tracking, and movement analysis.
📽️ Demo

Run python main.py to start the live system, then streamlit run dashboard.py to open the analytics dashboard.


🎯 Features

Real-time Person Detection — YOLOv8 detects persons in each frame
Multi-Person Tracking — DeepSORT assigns persistent IDs across frames
Posture Detection — Sitting vs Standing based on body landmark visibility
Activity Classification — Working / Idle / Break Time
6-Signal Activity Engine — body movement, head movement, wrist movement, upper body posture, hand activity, and finger detection
Interactive ROI Selection — Draw your workspace zone on startup by clicking and dragging
CSV Activity Logging — Timestamped logs saved automatically
Streamlit Dashboard — Live analytics with charts, per-person breakdown, and export


🧠 How It Works
Video Input (Webcam / File)
        │
        ▼
Person Detection (YOLOv8)
        │
        ▼
Person Tracking (DeepSORT) — assigns persistent Person IDs
        │
        ▼
Pose & Hand Analysis (MediaPipe)
  ├── Posture       → sitting / standing (via landmark visibility)
  ├── Head movement → nose Y position change
  ├── Wrist movement→ wrist Y position change
  ├── Hand activity → finger tip detection
  └── Upper body    → wrists above hip level
        │
        ▼
ROI Check — is person inside workspace zone?
        │
        ▼
Activity Classification
  ├── Working    → inside ROI + any active signal
  ├── Idle       → inside ROI + no signal for 15s
  └── Break Time → outside ROI for 20s+
        │
        ▼
Overlay labels on video + Write to CSV log

🏗️ Project Structure
fuelflux-activity-analysis/
│
├── main.py                 # Entry point — live video pipeline
├── detector.py             # YOLOv8 person detection
├── tracker.py              # DeepSORT multi-person tracking
├── pose_analyzer.py        # MediaPipe pose + hand analysis
├── activity_classifier.py  # Activity state classification engine
├── roi_manager.py          # Interactive ROI drawing & checking
├── logger.py               # CSV activity logging
├── dashboard.py            # Streamlit analytics dashboard
├── config.py               # All settings and thresholds
├── requirements.txt        # Python dependencies
└── output/
    ├── logs/               # activity_log.csv saved here
    └── videos/             # Processed output video saved here

⚙️ Tech Stack
PurposeLibraryPerson DetectionYOLOv8 (Ultralytics)Person TrackingDeepSORT RealtimePose EstimationMediaPipe PoseHand TrackingMediaPipe HandsVideo ProcessingOpenCVDashboardStreamlit + PlotlyLoggingCSV (Pandas)

🚀 Setup & Installation
1. Clone the Repository
bashgit clone https://github.com/your-username/fuelflux-activity-analysis.git
cd fuelflux-activity-analysis
2. Create Virtual Environment
bashpython -m venv venv
Activate it:

Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

3. Install Dependencies
bashpip install -r requirements.txt
4. Create Output Folders
bashmkdir -p output/logs output/videos

▶️ Running the System
Step 1 — Configure Video Source
Open config.py and set:
pythonVIDEO_SOURCE = 0          # 0 = webcam, or "path/to/video.mp4"
Step 2 — Run the Live System
bashpython main.py
On startup:

A window opens showing the camera feed
Click and drag to draw your workspace ROI
Press ENTER to confirm
System starts analyzing immediately
Press Q to quit

Step 3 — Run the Dashboard (separate terminal)
bashstreamlit run dashboard.py
Opens at http://localhost:8501

📊 Activity Classification Rules
StateConditionWorkingInside ROI + any active signal detectedWorkingInside ROI + was active within last 15 secondsIdleInside ROI + no signal for more than 15 secondsBreak TimeOutside ROI for more than 20 seconds
6 Active Signals Detected
SignalDetectsBody MovementPerson shifts, leans, or moves positionHead MovementNodding, looking up or downWrist MovementTyping, writing, using mouseUpper Body ActiveArms raised to working positionHand ActivityFingers raised or in useFinger DetectionFine hand movements

🛠️ Configuration
All thresholds are in config.py:
pythonMOVEMENT_THRESHOLD    = 10   # pixels moved to count as body movement
IDLE_TIME_SECONDS     = 15   # seconds with no signal before marking Idle
BREAK_ABSENCE_SECONDS = 20   # seconds outside ROI before marking Break Time
VIDEO_SOURCE          = 0    # 0 = webcam, or video file path
OUTPUT_VIDEO          = "output/videos/output.mp4"
LOG_FILE              = "output/logs/activity_log.csv"

📋 Output
1. Processed Video (output/videos/output.mp4)

Bounding boxes around detected persons
Labels showing Person ID, posture, and activity state
Color coded — 🟢 Working, 🟠 Idle, 🔴 Break Time

2. Activity Log (output/logs/activity_log.csv)
Timestamp            | Person_ID | Posture  | Activity | In_ROI
2024-01-15 10:30:01  | 1         | sitting  | Working  | True
2024-01-15 10:30:02  | 1         | sitting  | Working  | True
2024-01-15 10:30:31  | 1         | sitting  | Idle     | True
3. Streamlit Dashboard

Live KPI cards (Working %, Idle %, Break %)
Activity over time chart
Per-person breakdown with progress bars
Scrollable activity log table
CSV export


📦 Requirements
ultralytics
mediapipe==0.10.9
opencv-python
deep-sort-realtime
streamlit
pandas
plotly
Install all:
bashpip install -r requirements.txt

📁 requirements.txt
ultralytics
mediapipe==0.10.9
opencv-python
deep-sort-realtime
streamlit
pandas
plotly

🤝 Submission
Built for the FuelFlux Technical Assignment — Human Activity & Workspace Utilization Analysis System.

✅ Real-time person detection and tracking
✅ Posture and activity classification
✅ ROI-based workspace monitoring
✅ Timestamped activity logs
✅ Analytics dashboard
✅ Processed video output
