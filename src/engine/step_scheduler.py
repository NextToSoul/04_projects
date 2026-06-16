class StepScheduler:
    def __init__(self, steps, config=None):
        self.steps = steps
        self._index = 0
        self._config = config or {}
        self._done = False

    def next(self):
        if self._done or self._index >= len(self.steps):
            self._done = True
            return None
        return self.steps[self._index]

    def handle_result(self, result):
        step = self.steps[self._index]
        on_fail = step.get("on_failure", self._config.get("on_step_failure", "continue"))
        if result == "pass" or (result == "fail" and on_fail != "abort"):
            self._index += 1
        elif result == "fail" and on_fail == "abort":
            self._done = True
        elif result == "error":
            self._done = True

    def is_done(self):
        return self._done
