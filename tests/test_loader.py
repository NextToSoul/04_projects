import pytest
from src.config.loader import load_excel_config, normalize_hex

def test_load_excel_with_data_only():
    rows = load_excel_config('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx', '立即遥控指令')
    names = [r.get('指令代号', '') for r in rows]
    assert len(rows) == 92
    assert 'TCHEDTTA106' in names

def test_normalize_hex():
    assert normalize_hex('EB 90') == 'EB90'
    assert normalize_hex('01 01') == '0101'
    assert normalize_hex(None) == ''
    assert normalize_hex('') == ''

def test_normalize_hex_int():
    assert normalize_hex(11) == '11'
    assert normalize_hex(255) == '255'
