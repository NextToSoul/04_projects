from src.config.inject_table import InjectTable
from src.codec.frame_encoder import encode_inject_package
from src.codec.checksum import sum_invert_low16
import struct

def test_inject1_frame_length():
    inj = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    frame = encode_inject_package(inj, bytes.fromhex('03FF'), seq=0)
    assert len(frame) == 240

def test_TCT4001_at_offset():
    inj = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    frame = encode_inject_package(inj, bytes.fromhex('03FF'), seq=0)
    val = struct.unpack('>f', frame[10:14])[0]
    assert abs(val - 240.0) < 0.1

def test_checksum_valid():
    inj = InjectTable('项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx')
    frame = encode_inject_package(inj, bytes.fromhex('03FF'), seq=0)
    cs = int.from_bytes(frame[-2:], 'big')
    calc = sum_invert_low16(frame[2:-2])
    assert cs == calc
