import pytest
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "项目文档" / "优化后excel配置表"

@pytest.fixture
def cmd_table_path():
    return str(CONFIG_DIR / "立即遥控指令配置表_优化后.xlsx")

@pytest.fixture
def tm_table_path():
    return str(CONFIG_DIR / "遥测配置表_优化后.xlsx")
