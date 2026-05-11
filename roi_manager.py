# roi_manager.py
import cv2

class ROIManager:
    def __init__(self):
        self.roi        = None   # (x1, y1, x2, y2)
        self.drawing    = False
        self.start_pt   = None
        self.end_pt     = None
        self.confirmed  = False

    # ── Mouse callback ─────────────────────────────────────────
    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing  = True
            self.start_pt = (x, y)
            self.end_pt   = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end_pt = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing  = False
            self.end_pt   = (x, y)
            x1 = min(self.start_pt[0], self.end_pt[0])
            y1 = min(self.start_pt[1], self.end_pt[1])
            x2 = max(self.start_pt[0], self.end_pt[0])
            y2 = max(self.start_pt[1], self.end_pt[1])
            self.roi = (x1, y1, x2, y2)

    def select_roi(self, first_frame):
        """
        Opens a window on the first frame.
        User clicks and drags to draw the workspace ROI.
        Press ENTER to confirm, R to redraw.
        """
        window = "Draw ROI - Click & Drag | ENTER = confirm | R = redraw"
        cv2.namedWindow(window)
        cv2.setMouseCallback(window, self._mouse_callback)

        while True:
            display = first_frame.copy()

            # Draw instruction text
            cv2.putText(display,
                        "Draw your workspace area. Press ENTER to confirm, R to redraw.",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Draw ROI rectangle while dragging or after drawn
            if self.start_pt and self.end_pt:
                cv2.rectangle(display, self.start_pt, self.end_pt,
                              (0, 255, 255), 2)

                # Show ROI size info
                if self.roi:
                    x1, y1, x2, y2 = self.roi
                    info = f"ROI: ({x1},{y1}) to ({x2},{y2})"
                    cv2.putText(display, info, (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                                (0, 255, 255), 2)

            cv2.imshow(window, display)
            key = cv2.waitKey(1) & 0xFF

            if key == 13 and self.roi:     # ENTER key
                cv2.destroyWindow(window)
                self.confirmed = True
                print(f"ROI set to: {self.roi}")
                break

            elif key == ord('r'):          # R key = redraw
                self.roi      = None
                self.start_pt = None
                self.end_pt   = None

    def is_inside(self, x, y):
        """Check if a point is inside the ROI."""
        if not self.roi:
            return True    # if no ROI drawn, treat whole frame as ROI
        x1, y1, x2, y2 = self.roi
        return x1 < x < x2 and y1 < y < y2

    def draw_roi(self, frame):
        """Draw the ROI on every video frame."""
        if not self.roi:
            return frame
        x1, y1, x2, y2 = self.roi
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, "WORKSPACE ROI",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        return frame