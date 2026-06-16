from src.engine.step_scheduler import StepScheduler

def test_next():
    s = StepScheduler([{"id": "S1"}, {"id": "S2"}])
    assert s.next()["id"] == "S1"

def test_pass_to_next():
    s = StepScheduler([{"id": "S1"}, {"id": "S2"}])
    s.next()
    s.handle_result("pass")
    assert s.next()["id"] == "S2"

def test_abort():
    s = StepScheduler([{"id": "S1"}], {"on_step_failure": "abort"})
    s.next()
    s.handle_result("fail")
    assert s.is_done()

def test_skip():
    s = StepScheduler([{"id": "S1"}, {"id": "S2"}], {"on_step_failure": "skip"})
    s.next()
    s.handle_result("fail")
    assert not s.is_done()
    assert s.next()["id"] == "S2"

def test_end():
    s = StepScheduler([{"id": "S1"}])
    s.next()
    s.handle_result("pass")
    assert s.next() is None
    assert s.is_done()
