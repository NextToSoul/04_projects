from src.config.telemetry_table import TelemetryTable
from src.codec.frame_decoder import decode_telemetry_frame

FRAME_HEX = '1ACF0525C9760023ED000000000F0001CF000000E1026D026001F5017B01F80B500000088600000000000001F7A0'

def test_decode_returns_dict():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    frame = bytes.fromhex(FRAME_HEX)
    result = decode_telemetry_frame(t, frame, '常规包1(SlowFrame)')
    assert isinstance(result, dict)
    assert len(result) > 10

def test_decode_TM1005():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    frame = bytes.fromhex(FRAME_HEX)
    result = decode_telemetry_frame(t, frame, '常规包1(SlowFrame)')
    assert 'TM1005' in result

def test_decode_with_enum():
    t = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
    frame = bytes.fromhex(FRAME_HEX)
    result = decode_telemetry_frame(t, frame, '常规包1(SlowFrame)', resolve_enum=True)
    assert isinstance(result.get('TM1005', ''), str)
