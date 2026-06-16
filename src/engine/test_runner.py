import time
from src.engine.sequence_loader import SequenceLoader
from src.engine.step_scheduler import StepScheduler
from src.engine.assertion_engine import AssertionEngine
from src.engine.timeline_engine import TimelineEngine
from src.codec.frame_encoder import encode_immediate_command

class TestRunner:
    def __init__(self, cmd_table, tm_table):
        self.cmd_table = cmd_table
        self.tm_table = tm_table
        self.loader = SequenceLoader()
        self.ae = AssertionEngine()

    def run(self, sequence_file, driver):
        seq = self.loader.load(sequence_file)
        scheduler = StepScheduler(seq["steps"], seq.get("config", {}))
        report = {"name": seq["name"], "steps": [], "passed": 0, "failed": 0}
        while not scheduler.is_done():
            step = scheduler.next()
            if step is None:
                break
            result = self._exec(step, driver)
            scheduler.handle_result(result["status"])
            report["steps"].append(result)
            if result["status"] == "pass":
                report["passed"] += 1
            else:
                report["failed"] += 1
        return report

    def _exec(self, step, driver):
        result = {"id": step["id"], "name": step.get("name", ""), "status": "pass", "checks": []}
        pb = self._params(step)
        try:
            frame = encode_immediate_command(self.cmd_table, step["command"], pb)
            driver.send(frame)
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            return result
        te = TimelineEngine()
        te.register_anchors(step.get("anchors", []))
        te.set_timeline(step.get("timeline", []))
        timeout = 5
        ex = step.get("expect", [])
        if ex and isinstance(ex[0], dict):
            timeout = ex[0].get("timeout", 5)
        start = time.time()
        prev = None
        while time.time() - start < timeout:
            for tl in te.get_due_checks():
                cs = tl.get("checks", {})
                if isinstance(cs, list):
                    cs = {"logic": "and", "conditions": cs}
                if cs:
                    ok = self.ae.evaluate(cs, {}, prev)
                    result["checks"].append({"at": tl["at"], "ok": ok})
                    if not ok:
                        result["status"] = "fail"
            time.sleep(0.05)
            prev = {}
        if not result["checks"]:
            result["checks"].append({"at": "default", "ok": True})
        return result

    def _params(self, step):
        p = step.get("params")
        if p is None:
            return b""
        if isinstance(p, str):
            if not p:
                return b""
            cmd = self.cmd_table.lookup(step["command"])
            vt = str(cmd.get("值类型", ""))
            if vt in ("枚举", "开关/切换"):
                em = self.cmd_table.get_enum_map(cmd["指令码(Hex)"])
                for h, l in em.items():
                    if l == p:
                        return bytes.fromhex(h)
            else:
                if len(p) % 2 == 0:
                    return bytes.fromhex(p)
        return b""
