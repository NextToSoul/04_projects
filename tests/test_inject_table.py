from src.config.inject_table import InjectTable

def test_inject1_count():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    assert len(t.get_params()) == 57

def test_TCT4001():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    p = t.lookup('TCT4001')
    assert p['参数值(十进制)'] == 240
    assert p['数据类型'] == 'float'
    assert p['位偏移' + chr(10) + 'bit_offset'] == 80

def test_inject1_inst_code():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    assert t.instruction_code == '03FF'

def test_inject2_count():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表2_优化后.xlsx')
    assert len(t.get_params()) == 39

def test_TCT4058():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表2_优化后.xlsx')
    p = t.lookup('TCT4058')
    assert abs(float(p['参数值']) - 0.20159376) < 0.0001

def test_inject2_inst_code():
    t = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表2_优化后.xlsx')
    assert t.instruction_code == '03FE'
