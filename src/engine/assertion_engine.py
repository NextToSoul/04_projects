class AssertionEngine:
    def evaluate(self, check_node, decoded, prev=None):
        if "logic" in check_node:
            results = [self.evaluate(c, decoded, prev) for c in check_node["conditions"]]
            if check_node["logic"] == "and":
                return all(results)
            if check_node["logic"] == "or":
                return any(results)
            return True
        actual = decoded.get(check_node["param"])
        if actual is None:
            return False
        expected = check_node["value"]
        op = check_node["operator"]
        tol = check_node.get("tolerance", 0)
        return self._compare(op, actual, expected, tol, prev, check_node["param"])

    def _compare(self, op, actual, expected, tol, prev=None, param=None):
        if op == "eq":
            return abs(actual - expected) <= tol
        if op == "not_eq":
            return abs(actual - expected) > tol
        if op == "gt":
            return actual > expected
        if op == "ge":
            return actual >= expected
        if op == "lt":
            return actual < expected
        if op == "le":
            return actual <= expected
        if op == "between":
            return expected[0] <= actual <= expected[1]
        if op == "in":
            return str(actual) in [str(x) for x in expected]
        if op == "changed_to":
            if prev is None:
                return False
            prev_val = prev.get(param)
            return prev_val is not None and prev_val != expected and actual == expected
        if op == "rising_to":
            return abs(actual - expected) <= tol
        return False
