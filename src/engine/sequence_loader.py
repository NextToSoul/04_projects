try:
    import yaml
    yaml_available = True
except ImportError:
    yaml_available = False

import json

class SequenceLoader:
    def load(self, filepath: str) -> dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.endswith(('.yaml', '.yml')) and yaml_available:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        errors = self.validate(data)
        if errors:
            raise ValueError("; ".join(errors))
        return data

    def validate(self, data: dict) -> list:
        errors = []
        if "name" not in data:
            errors.append("Missing 'name'")
        if "steps" not in data:
            errors.append("Missing 'steps'")
        else:
            for i, step in enumerate(data["steps"]):
                if "id" not in step:
                    errors.append("Step " + str(i) + ": missing 'id'")
                if "command" not in step:
                    errors.append("Step " + str(i) + ": missing 'command'")
        return errors
