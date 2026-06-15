import sys
import struct
sys.path.insert(0, '.')
from src.protocol.registry import get_driver
from src.codec.checksum import sum_invert_low16
import time

HOST = '192.168.117.26'
PORT = 20004
TIMEOUT = 5

print('TCP 驱动连接测试')
print('=' * 50)
print('目标: ' + HOST + ':' + str(PORT))

driver = get_driver('tcp')
received = []
driver.set_receive_callback(lambda d: received.append(d))

ok = driver.open({'host': HOST, 'port': PORT, 'timeout': TIMEOUT})
if not ok:
   print('[失败] 无法连接到 ' + HOST + ':' + str(PORT))
   print('  请检查:')
   print('  - 设备是否已开机')
   print('  - IP 和端口是否正确')
   print('  - 防火墙是否允许连接')
   sys.exit(1)

print('[成功] 已连接到 ' + HOST + ':' + str(PORT))

# 发送遥测请求 (005A)
raw = bytes.fromhex('0520C0000001005A')
cs = sum_invert_low16(raw)
frame = bytes.fromhex('EB90') + raw + struct.pack('>H', cs)

print('发送: ' + frame.hex().upper())
driver.send(frame)
print('等待响应...')
time.sleep(3)

if received:
   print('收到 ' + str(len(received)) + ' 个包:')
   for i, d in enumerate(received):
       resp = d.hex().upper()
       if len(resp) > 80:
           resp = resp[:80] + '...'
       print('  [' + str(i+1) + '] ' + resp)
       # 检查是否是遥测响应帧
       if d[:2] == bytes.fromhex('1ACF'):
           print('      -> 遥测响应帧, APID=' + d[2:4].hex() + ', 数据长度=' + str((d[6] << 8 | d[7]) + 1) + 'B')
else:
   print('超时: 3秒内未收到响应')

driver.close()
print('连接已关闭')
