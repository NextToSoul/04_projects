import json
import pytest
from src.engine.sequence_loader import SequenceLoader

def test_load_valid(tmp_path):
   f = tmp_path / "test.json"
   f.write_text('{"name": "ignition_test", "steps": [{"id": "S01", "command": "TCHEDTTA106"}]}')
   loader = SequenceLoader()
   seq = loader.load(str(f))
   assert seq["name"] == "ignition_test"
   assert len(seq["steps"]) == 1

def test_missing_name(tmp_path):
   f = tmp_path / "test.json"
   f.write_text('{"steps": []}')
   loader = SequenceLoader()
   with pytest.raises(ValueError, match="name"):
       loader.load(str(f))

def test_missing_steps(tmp_path):
   f = tmp_path / "test.json"
   f.write_text('{"name": "t"}')
   loader = SequenceLoader()
   with pytest.raises(ValueError, match="steps"):
       loader.load(str(f))

def test_missing_step_cmd(tmp_path):
   f = tmp_path / "test.json"
   f.write_text('{"name": "t", "steps": [{"id": "S1"}]}')
   loader = SequenceLoader()
   with pytest.raises(ValueError, match="command"):
       loader.load(str(f))
