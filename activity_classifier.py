# activity_classifier.py
import time
from config import MOVEMENT_THRESHOLD, IDLE_TIME_SECONDS, BREAK_ABSENCE_SECONDS

class ActivityClassifier:
    def __init__(self):
        self.person_states = {}

    def _init_person(self, pid):
        self.person_states[pid] = {
            "last_center":       None,
            "last_head_y":       None,
            "last_wrist_avg_y":  None,
            "last_active_time":  time.time(),
            "last_roi_time":     time.time(),
            "activity":          "Unknown",
            "activity_history":  []
        }

    def _smooth_activity(self, pid, new_activity):
        history = self.person_states[pid]["activity_history"]
        history.append(new_activity)
        if len(history) > 5:
            history.pop(0)
        counts = {}
        for a in history:
            counts[a] = counts.get(a, 0) + 1
        return max(counts, key=counts.get)

    def classify(self, pid, cx, cy, in_roi, pose_data):
        if pid not in self.person_states:
            self._init_person(pid)

        state = self.person_states[pid]
        now   = time.time()

        posture           = pose_data.get("posture",            "unknown")
        head_y            = pose_data.get("head_y",             None)
        left_wrist_y      = pose_data.get("left_wrist_y",       None)
        right_wrist_y     = pose_data.get("right_wrist_y",      None)
        upper_body_active = pose_data.get("upper_body_active",  False)
        hands_active      = pose_data.get("hands_active",       False)

        # ── Signal 1: Body movement ────────────────────────────
        body_moved = False
        if state["last_center"] is not None:
            prev_cx, prev_cy = state["last_center"]
            dist = ((cx - prev_cx)**2 + (cy - prev_cy)**2) ** 0.5
            if dist > MOVEMENT_THRESHOLD:
                body_moved = True
        state["last_center"] = (cx, cy)

        # ── Signal 2: Head movement (lowered threshold) ────────
        head_moved = False
        if head_y is not None and state["last_head_y"] is not None:
            if abs(head_y - state["last_head_y"]) > 2:   # was 3, now 2
                head_moved = True
        state["last_head_y"] = head_y

        # ── Signal 3: Wrist movement (lowered threshold) ───────
        wrist_moved = False
        wrist_val = None
        if left_wrist_y is not None and right_wrist_y is not None:
            wrist_val = (left_wrist_y + right_wrist_y) / 2
        elif left_wrist_y is not None:
            wrist_val = left_wrist_y
        elif right_wrist_y is not None:
            wrist_val = right_wrist_y

        if wrist_val is not None and state["last_wrist_avg_y"] is not None:
            if abs(wrist_val - state["last_wrist_avg_y"]) > 3:  # was 5, now 3
                wrist_moved = True
        state["last_wrist_avg_y"] = wrist_val

        # ── All signals ────────────────────────────────────────
        any_signal = (
            body_moved        or
            head_moved        or
            wrist_moved       or
            upper_body_active or
            hands_active
        )

        # ── Update timers ──────────────────────────────────────
        if in_roi:
            state["last_roi_time"] = now

        if any_signal:
            state["last_active_time"] = now

        time_since_active = now - state["last_active_time"]
        time_outside_roi  = now - state["last_roi_time"]

        # ── Debug print (remove after testing) ────────────────
        print(f"[ID:{pid}] body={body_moved} head={head_moved} "
              f"wrist={wrist_moved} hands={hands_active} "
              f"upper={upper_body_active} | "
              f"in_roi={in_roi} idle_for={round(time_since_active,1)}s")

        # ── Classification ─────────────────────────────────────
        if time_outside_roi > BREAK_ABSENCE_SECONDS:
            raw_activity = "Break Time"

        elif not in_roi:
            raw_activity = "Idle"

        elif in_roi and any_signal:
            raw_activity = "Working"

        elif in_roi and time_since_active < IDLE_TIME_SECONDS:
            raw_activity = "Working"

        else:
            raw_activity = "Idle"

        activity = self._smooth_activity(pid, raw_activity)
        state["activity"] = activity
        return activity

    def get_summary(self):
        summary = {}
        for pid, state in self.person_states.items():
            summary[pid] = {
                "activity":        state["activity"],
                "last_active_ago": round(time.time() - state["last_active_time"], 1),
                "last_roi_ago":    round(time.time() - state["last_roi_time"], 1),
            }
        return summary