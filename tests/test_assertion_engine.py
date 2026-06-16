from src.engine.assertion_engine import AssertionEngine
import pytest

AE = AssertionEngine()

def test_eq():
    assert AE.evaluate({"operator": "eq", "param": "A", "value": 100}, {"A": 100})

def test_eq_tolerance():
    assert AE.evaluate({"operator": "eq", "param": "A", "value": 100, "tolerance": 5}, {"A": 102})

def test_eq_fail():
    assert not AE.evaluate({"operator": "eq", "param": "A", "value": 100}, {"A": 200})

def test_gt():
    assert AE.evaluate({"operator": "gt", "param": "A", "value": 50}, {"A": 100})

def test_ge():
    assert AE.evaluate({"operator": "ge", "param": "A", "value": 50}, {"A": 50})

def test_lt():
    assert AE.evaluate({"operator": "lt", "param": "A", "value": 50}, {"A": 30})

def test_between():
    assert AE.evaluate({"operator": "between", "param": "A", "value": [10, 20]}, {"A": 15})
    assert not AE.evaluate({"operator": "between", "param": "A", "value": [10, 20]}, {"A": 25})

def test_and():
    assert AE.evaluate({"logic": "and", "conditions": [
        {"operator": "eq", "param": "A", "value": 1},
        {"operator": "eq", "param": "B", "value": 2}
    ]}, {"A": 1, "B": 2})
    assert not AE.evaluate({"logic": "and", "conditions": [
        {"operator": "eq", "param": "A", "value": 1},
        {"operator": "eq", "param": "B", "value": 99}
    ]}, {"A": 1, "B": 2})

def test_or():
    assert AE.evaluate({"logic": "or", "conditions": [
        {"operator": "eq", "param": "A", "value": 1},
        {"operator": "eq", "param": "B", "value": 99}
    ]}, {"A": 1})
    assert not AE.evaluate({"logic": "or", "conditions": [
        {"operator": "eq", "param": "A", "value": 99},
        {"operator": "eq", "param": "B", "value": 98}
    ]}, {"A": 1, "B": 2})

def test_changed_to():
    assert AE.evaluate({"operator": "changed_to", "param": "X", "value": 5}, {"X": 5}, {"X": 0})
    assert not AE.evaluate({"operator": "changed_to", "param": "X", "value": 5}, {"X": 5}, {"X": 5})

def test_in():
    assert AE.evaluate({"operator": "in", "param": "A", "value": ["x", "y", "z"]}, {"A": "y"})
    assert not AE.evaluate({"operator": "in", "param": "A", "value": ["x", "y", "z"]}, {"A": "w"})

def test_nested_logic():
    assert AE.evaluate({"logic": "and", "conditions": [
        {"operator": "eq", "param": "A", "value": 1},
        {"logic": "or", "conditions": [
            {"operator": "eq", "param": "B", "value": 2},
            {"operator": "eq", "param": "C", "value": 3}
        ]}
    ]}, {"A": 1, "B": 2, "C": 0})
