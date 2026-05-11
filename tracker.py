from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        # max_age: how many frames to keep a track alive without detection
        self.tracker = DeepSort(max_age=30)

    def update(self, detections, frame):
        """
        Takes detections → returns tracks with stable IDs.
        Each track: [x1, y1, x2, y2, track_id]
        """
        # DeepSORT expects format: ([x1,y1,w,h], confidence, class)
        ds_input = []
        for det in detections:
            x1, y1, x2, y2, conf = det
            w, h = x2 - x1, y2 - y1
            ds_input.append(([x1, y1, w, h], conf, 'person'))

        tracks = self.tracker.update_tracks(ds_input, frame=frame)

        results = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            tid = track.track_id
            ltrb = track.to_ltrb()  # left, top, right, bottom
            x1, y1, x2, y2 = map(int, ltrb)
            results.append((tid, x1, y1, x2, y2))

        return results