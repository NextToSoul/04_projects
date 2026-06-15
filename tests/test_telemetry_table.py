from src.config.telemetry_table import TelemetryTable

def test_pkg1_count():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    p1 = t.get_package('常规包1(SlowFrame)')
    assert len(p1) == 52

def test_TM1005_work_mode():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    p = t.get_package('常规包1(SlowFrame)')
    tm1005 = [r for r in p if str(r.get('遥测代号') or '') == 'TM1005']
    assert len(tm1005) == 1
    assert tm1005[0]['数据类型'] == 'enum'
    assert tm1005[0]['位偏移bit_offset'] == 104

def test_TM1008_scale():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    p = t.get_package('常规包1(SlowFrame)')
    tm1008 = [r for r in p if str(r.get('遥测代号') or '') == 'TM1008'][0]
    assert float(tm1008['当量']) == 180.0
    assert tm1008['单位'] == 'V'

def test_enum_resolve():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    em = t.get_enum_map('TM1005')
    assert len(em) >= 5
    assert em['0'] == '待机模式'
    assert em['1'] == '推进模式'
    assert em['15'] == '维护模式'
