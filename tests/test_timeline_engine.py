from src.engine.timeline_engine import TimelineEngine

def test_cmd_anchor():
    te = TimelineEngine()
    te.register_anchors([{"name": "t0", "type": "command_sent"}])
    assert te.get_anchor_time("t0") is not None

def test_due_zero():
    te = TimelineEngine()
    te.register_anchors([{"name": "t0", "type": "command_sent"}])
    te.set_timeline([{"at": "+0s", "from": "t0", "checks": []}])
    due = te.get_due_checks()
    assert len(due) == 1

def test_cond_met():
    te = TimelineEngine()
    te.register_anchors([{"name": "tp", "type": "condition_met",
        "wait": 10, "on": {"param": "X", "operator": "eq", "value": 5}}])
    assert te.get_anchor_time("tp") is None
    te.process_frame({"X": 5})
    assert te.get_anchor_time("tp") is not None

def test_time_window():
    te = TimelineEngine()
    te.register_anchors([{"name": "t0", "type": "command_sent"}])
    te.set_timeline([{"at": "+4s..+6s", "from": "t0", "checks": []}])
    due = te.get_due_checks()
    assert len(due) == 0
