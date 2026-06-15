from src.config.command_table import CommandTable

def test_lookup_TCHEDTTA106():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    cmd = t.lookup('TCHEDTTA106')
    assert cmd['指令码(Hex)'] == '03D8'
    assert cmd['参数字节数'] == 4

def test_lookup_TCHEDTTA003():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    cmd = t.lookup('TCHEDTTA003')
    assert cmd['指令码(Hex)'] == '0030'
    assert cmd['参数值(Hex)'] == '00'

def test_enum_map():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    em = t.get_enum_map('0030')
    assert len(em) == 9
    assert em['00'] == '待机模式'
    assert em['11'] == '正常点火模式'

def test_known_count():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    assert len(t.all()) == 92
