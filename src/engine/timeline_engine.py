import time
from src.engine.assertion_engine import AssertionEngine

class TimelineEngine:
    def __init__(self):
        self.anchors = {}
        self._anchor_times = {}
        self._done_checks = set()
        self.timeline = []

    def register_anchors(self, anchors):
        for a in anchors:
            self.anchors[a["name"]] = a
            if a["type"] == "command_sent":
                self._anchor_times[a["name"]] = time.time()

    def set_timeline(self, timeline):
        self.timeline = timeline
        self._done_checks = set()

    def process_frame(self, frame, ae=None):
        for name, a in self.anchors.items():
            if a["type"] == "condition_met" and name not in self._anchor_times:
                on = a["on"]
                if ae is None:
                    ae = AssertionEngine()
                if ae.evaluate({"operator": on["operator"], "param": on["param"], "value": on["value"]}, frame):
                    self._anchor_times[name] = time.time()

    def get_due_checks(self):
        now = time.time()
        checks = []
        for i, tl in enumerate(self.timeline):
            if i in self._done_checks:
                continue
            anchor_name = tl.get("from")
            if anchor_name not in self._anchor_times:
                continue
            base = self._anchor_times[anchor_name]
            at_str = tl["at"]
            if ".." in at_str:
                parts = at_str.split("..")
                start_delay = float(parts[0].replace("s", ""))
                end_delay = float(parts[1].replace("s", ""))
            else:
                start_delay = float(at_str.replace("s", ""))
                end_delay = start_delay
            elapsed = now - base
            if elapsed >= start_delay and elapsed <= end_delay + 0.5:
                if tl not in checks:
                    checks.append(tl)
            if elapsed > end_delay + 0.5:
                self._done_checks.add(i)
        return checks

    def get_anchor_time(self, name):
        return self._anchor_times.get(name)
