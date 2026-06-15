from src.config.command_table import CommandTable
from src.codec.frame_encoder import encode_immediate_command
from src.codec.checksum import sum_invert_low16

def test_encode_TCHEDTTA001():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    frame = encode_immediate_command(t, 'TCHEDTTA001', seq=0)
    assert len(frame) >= 10
    assert frame[:2] == bytes.fromhex('EB90')
    assert frame[8:10] == bytes.fromhex('001A')

def test_encode_TCHEDTTA106():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    frame = encode_immediate_command(t, 'TCHEDTTA106', params_bytes=bytes.fromhex('00000078'), seq=1)
    assert frame[8:10] == bytes.fromhex('03D8')
    assert frame[10:14] == bytes.fromhex('00000078')

def test_checksum_valid():
    t = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
    frame = encode_immediate_command(t, 'TCHEDTTA001', seq=0)
    cs = int.from_bytes(frame[-2:], 'big')
    calc = sum_invert_low16(frame[2:-2])
    assert cs == calc
