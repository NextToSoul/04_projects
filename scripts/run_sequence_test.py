
import sys, time
sys.path.insert(0, '.')

from src.config.command_table import CommandTable
from src.config.telemetry_table import TelemetryTable
from src.engine.test_runner import TestRunner
from src.protocol.registry import get_driver

HOST = '192.168.117.26'
PORT = 20004
SEQUENCE = 'sequences/normal_ignition_test.yaml'

print('=== TCP 真实设备三步骤测试 ===')
print()
print('序列: ' + SEQUENCE)
print('设备: ' + HOST + ':' + str(PORT))

# 1. 加载配置
print()
print('[1/4] 加载配置表...')
cmd = CommandTable('项目文档/优化后excel配置表/立即遥控指令配置表_优化后.xlsx')
tm = TelemetryTable('项目文档/优化后excel配置表/遥测配置表_优化后.xlsx')
print('  指令码表: ' + str(len(cmd.all())) + ' 条')
print('  遥测参数: ' + str(len(tm.get_package('常规包1(SlowFrame)'))) + ' 条')

# 2. 连接设备
print()
print('[2/4] 连接设备...')
driver = get_driver('tcp')
received = []
driver.set_receive_callback(lambda d: received.append(d))
ok = driver.open({'host': HOST, 'port': PORT, 'timeout': 5})
if not ok:
   print('  连接失败: ' + HOST + ':' + str(PORT))
   print('  请检查设备是否开机、网络是否可达')
   sys.exit(1)
print('  连接成功: ' + driver.name)

# 3. 执行测试
print()
print('[3/4] 执行测试...')
runner = TestRunner(cmd, tm)
report = runner.run(SEQUENCE, driver)

# 4. 报告
print()
print('[4/4] 测试报告')
print()
print('序列名称: ' + report['name'])
print('通过: ' + str(report['passed']) + ' / 失败: ' + str(report['failed']))
print()
for s in report['steps']:
   status_mark = 'PASS' if s['status'] == 'pass' else 'FAIL'
   print('  [' + status_mark + '] ' + s['id'] + ' ' + s.get('name', ''))
   for c in s.get('checks', []):
       print('       ' + str(c))

driver.close()
print()
print('测试完成')
