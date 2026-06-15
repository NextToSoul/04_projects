from src.config.command_table import CommandTable
from src.config.telemetry_table import TelemetryTable
from src.config.inject_table import InjectTable
from src.codec.frame_encoder import encode_immediate_command
from src.codec.frame_decoder import decode_telemetry_frame
from src.codec.checksum import sum_invert_low16

CMD_PATH = '项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx'
TM_PATH = '项目文档/优化后excel配置表/遥测配置表_优化后.xlsx'
INJ1_PATH = '项目文档/优化后excel配置表/固定地址参数注入表1_优化后.xlsx'

def test_all_configs_load():
   cmd = CommandTable(CMD_PATH)
   tm = TelemetryTable(TM_PATH)
   inj1 = InjectTable(INJ1_PATH)
   assert len(cmd.all()) == 92
   assert len(tm.get_package('常规包1(SlowFrame)')) == 52
   assert len(inj1.get_params()) == 57

def test_immediate_frame_checksum():
   cmd = CommandTable(CMD_PATH)
   frame = encode_immediate_command(cmd, 'TCHEDTTA001', seq=0)
   cs = int.from_bytes(frame[-2:], 'big')
   calc = sum_invert_low16(frame[2:-2])
   assert cs == calc

def test_telemetry_decode_pkg1():
   tm = TelemetryTable(TM_PATH)
   frame = bytes.fromhex('1ACF0525C9760023ED000000000F0001CF000000E1026D026001F5017B01F80B500000088600000000000001F7A0')
   result = decode_telemetry_frame(tm, frame, '常规包1(SlowFrame)')
   assert len(result) > 10
   assert 'TM1005' in result
   assert 'TM1008' in result
   assert 'TM1001' in result
