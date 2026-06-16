from src.engine.test_runner import TestRunner
import json

class _CT:
    def lookup(self, name):
        return {"指令码(Hex)": "001A", "值类型": "无参数"}
    def get_enum_map(self, code):
        return {}

class _TT:
    def get_package(self, n):
        return []
    def get_enum_map(self, p):
        return {}

def test_report_structure(tmp_path):
    s = {"name": "test_seq", "steps": [{"id": "S1", "command": "T1"}]}
    f = tmp_path / "s.json"
    json.dump(s, f.open("w"))
    class D:
        def send(self, d): pass
    r = TestRunner(_CT(), _TT()).run(str(f), D())
    assert r["name"] == "test_seq"
    assert len(r["steps"]) == 1
    assert r["passed"] == 1

def test_multiple_steps(tmp_path):
    s = {"name": "m", "steps": [{"id": "S1", "command": "T1"}, {"id": "S2", "command": "T2"}]}
    f = tmp_path / "m.json"
    json.dump(s, f.open("w"))
    class D:
        def send(self, d): pass
    r = TestRunner(_CT(), _TT()).run(str(f), D())
    assert len(r["steps"]) == 2
    assert r["passed"] == 2

def test_step_error_handling(tmp_path):
    s = {"name": "e", "steps": [{"id": "S1", "command": "BAD_CMD"}]}
    f = tmp_path / "e.json"
    json.dump(s, f.open("w"))
    class CT_err:
        def lookup(self, n):
            raise KeyError(n)
        def get_enum_map(self, c):
            return {}
    class D:
        def send(self, d): pass
    r = TestRunner(CT_err(), _TT()).run(str(f), D())
    assert r["steps"][0]["status"] == "error"
