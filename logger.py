import csv
import os
from datetime import datetime

class ActivityLogger:
    def __init__(self, filepath):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write CSV header
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Person_ID", "Posture", "Activity", "In_ROI"])

    def log(self, person_id, posture, activity, in_roi):
        with open(self.filepath, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                person_id,
                posture,
                activity,
                in_roi
            ])