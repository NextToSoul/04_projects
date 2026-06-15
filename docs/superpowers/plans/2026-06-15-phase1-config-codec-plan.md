 # Phase 1 实现计划：配置解析与帧编解码
 
 > 面向 AI 代理的工作者：必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（- [ ]）语法来跟踪进度。
 
 **目标：** 实现配置解析层和帧编解码层，使系统能直接读取 Excel 配置文件，将指令名+参数编码为 hex 帧，并将接收到的字节解码为结构化遥测值。
 
 **架构：** 四层分层架构中优先实现最底层两层。配置解析层(src/config/)从 Excel 读取指令码表和遥测参数表，以 Python dict 形式提供给上层。帧编解码层(src/codec/)使用配置信息进行帧的编码和解码。协议驱动层(src/protocol/)在本阶段只实现接口骨架。
 
 **技术栈：** Python 3.10+, openpyxl, pytest, struct
 
 ---
 
 ## 文件结构
 
 ```
 project_root/
 ├── pyproject.toml
 ├── src/
 │   ├── __init__.py
 │   ├── config/
 │   │   ├── __init__.py
 │   │   ├── loader.py
 │   │   ├── command_table.py
 │   │   ├── telemetry_table.py
 │   │   └── inject_table.py
 │   ├── codec/
 │   │   ├── __init__.py
 │   │   ├── checksum.py
 │   │   ├── frame_encoder.py
 │   │   └── frame_decoder.py
 │   └── protocol/
 │       ├── __init__.py
 │       ├── base.py
 │       └── registry.py
 ├── tests/
 │   ├── __init__.py
 │   ├── conftest.py
 │   ├── test_loader.py
 │   ├── test_command_table.py
 │   ├── test_telemetry_table.py
 │   ├── test_inject_table.py
 │   ├── test_checksum.py
 │   ├── test_frame_encoder.py
 │   ├── test_frame_encoder_inject.py
 │   ├── test_frame_decoder.py
 │   └── test_integration.py
 └── 项目文档/优化后excel配置表/
     ├── 立即遥控指令配置表_优化后.xlsx
     ├── 遥测配置表_优化后.xlsx
     ├── 固定地址参数注入表1_优化后.xlsx
     └── 固定地址参数注入表2_优化后.xlsx
 ```
 
 ---
 
 ### 任务 1：项目骨架搭建
 
 文件：pyproject.toml, src/__init__.py, src/config/__init__.py, src/codec/__init__.py, src/protocol/__init__.py, tests/__init__.py, tests/conftest.py, .gitignore
 
 - [ ] 步骤 1：创建 pyproject.toml
 
 内容如下：
 
 [build-system]
 requires = ["setuptools>=68.0"]
 build-backend = "setuptools.backends._legacy:_Backend"
 
 [project]
 name = "auto-test-platform"
 version = "0.1.0"
 requires-python = ">=3.10"
 dependencies = [
     "openpyxl>=3.1.0",
     "pyserial>=3.5",
 ]
 
 [tool.pytest.ini_options]
 testpaths = ["tests"]
 pythonpath = ["src"]
 
 - [ ] 步骤 2：创建 __init__.py 文件（全部为空文件），目录：
   - mkdir -p src/config src/codec src/protocol tests
   - touch src/__init__.py src/config/__init__.py src/codec/__init__.py src/protocol/__init__.py tests/__init__.py
 
 - [ ] 步骤 3：创建 conftest.py
 
 ```python
 import pytest
 from pathlib import Path
 
 CONFIG_DIR = Path(__file__).parent.parent / "项目文档" / "优化后excel配置表"
 
 @pytest.fixture
 def cmd_table_path():
     return str(CONFIG_DIR / "立即遥控指令配置表_优化后.xlsx")
 
 @pytest.fixture
 def tm_table_path():
     return str(CONFIG_DIR / "遥测配置表_优化后.xlsx")
 ```
 
 - [ ] 步骤 4：创建 .gitignore（__pycache__/ *.pyc *.egg-info dist/ build/ .eggs）
 
 - [ ] 步骤 5：运行 pip install -e . && pytest --collect-only，验证无报错
 
 - [ ] 步骤 6：git commit
 
 ---
 
 ### 任务 2：Excel 配置加载器 (loader.py)
 
 文件：src/config/loader.py, tests/test_loader.py
 
 - [ ] 步骤 1：编写测试 test_loader.py，验证：
   1. load_excel_config 读取 92 行
   2. normalize_hex("EB 90") == "EB90"
   3. normalize_hex(None) == ""
 
 - [ ] 步骤 2：运行确认失败 → 步骤 3：实现 loader.py
 
 ```python
 import openpyxl
 
 def load_excel_config(filepath, sheet_name):
     wb = openpyxl.load_workbook(filepath, data_only=True)
     ws = wb[sheet_name]
     headers = [cell.value for cell in ws[1]]
     rows = []
     for row in ws.iter_rows(min_row=2, values_only=True):
         if all(v is None for v in row):
             continue
         rows.append({headers[i]: row[i] for i in range(len(headers))})
     return rows
 
 def normalize_hex(val):
     if val is None:
         return ""
     if isinstance(val, str):
         v = val.replace(" ", "").strip()
         return v.upper() if v else ""
     if isinstance(val, (int, float)):
         return str(int(val))
     return str(val)
 ```
 
 - [ ] 步骤 4：pytest tests/test_loader.py -v 验证通过 → 步骤 5：commit
 
 ---
 
 ### 任务 3：指令码表模块 (command_table.py)
 
 文件：src/config/command_table.py, tests/test_command_table.py
 
 - [ ] 步骤 1：编写测试，验证：
   1. lookup("TCHEDTTA106") -> 指令码 03D8，参数字节数 4
   2. lookup("TCHEDTTA003_2") -> 指令码 0030，参数值 11
   3. get_enum_map("0030") -> 9 个枚举值
   4. all() 返回 92 条
 
 - [ ] 步骤 2：实现 CommandTable 类
 
 ```python
 from src.config.loader import load_excel_config, normalize_hex
 import openpyxl
 
 class CommandTable:
     def __init__(self, filepath):
         self.filepath = filepath
         self.rows = load_excel_config(filepath, "立即遥控指令")
         self._by_name = {}
         self._enum = {}
         for row in self.rows:
             name = str(row.get("指令代号") or "").strip()
             if name:
                 self._by_name[name] = row
         self._load_enum()
 
     def _load_enum(self):
         try:
             wb = openpyxl.load_workbook(self.filepath, data_only=True)
             ws = wb["枚举值映射表"]
             for row in ws.iter_rows(min_row=2, values_only=True):
                 if row[0] is None: continue
                 code = normalize_hex(str(row[0]))
                 val = normalize_hex(str(row[3]))
                 label = str(row[4] or "").strip()
                 if code not in self._enum:
                     self._enum[code] = {}
                 if val:
                     self._enum[code][val] = label
         except Exception:
             pass
 
     def lookup(self, name):
         if name not in self._by_name:
             raise KeyError(f"指令'{name}'未找到")
         return self._by_name[name]
 
     def get_enum_map(self, inst_code):
         return dict(self._enum.get(inst_code, {}))
 
     def all(self):
         return list(self.rows)
 ```
 
 - [ ] 步骤 3：pytest tests/test_command_table.py -v 通过 → commit
 
 ---
 
 ### 任务 4：遥测参数表模块 (telemetry_table.py)
 
 文件：src/config/telemetry_table.py, tests/test_telemetry_table.py
 
 - [ ] 步骤 1：测试验证：
   1. 常规包1 大于 47 行
   2. TM1005 数据类型=enum, 位偏移=104
   3. TM1008 当量约 0.0055556, 单位=V
   4. 枚举映射 TM1005 的 0=待机模式, 1=推进模式
 
 - [ ] 步骤 2：实现 TelemetryTable 类（含 get_package / get_enum_map）
 
 - [ ] 步骤 3：pytest 通过 → commit
 
 ---
 
 ### 任务 5：固定参数注入表模块 (inject_table.py)
 
 文件：src/config/inject_table.py, tests/test_inject_table.py
 
 - [ ] 步骤 1：测试验证：
   1. 注入1 有 57 个参数
   2. TCT4001 参数值=240, 数据类型=float, 位偏移=80
   3. 注入2 有 39 个参数
   4. 所有参数都有位偏移和位长度
 
 - [ ] 步骤 2：实现 InjectTable 类
 
 ```python
 from src.config.loader import load_excel_config
 import openpyxl
 
 class InjectTable:
     def __init__(self, filepath):
         self.filepath = filepath
         wb = openpyxl.load_workbook(filepath, data_only=True)
         for sname in wb.sheetnames:
             if "固定地址参数注入" in sname and "帧格式" not in sname:
                 self.sheet_name = sname
                 break
         self.params = load_excel_config(filepath, self.sheet_name)
 
     def get_params(self):
         return self.params
 ```
 
 - [ ] 步骤 3：pytest 通过 → commit
 
 ---
 
 ### 任务 6：校验和计算器 (checksum.py)
 
 文件：src/codec/checksum.py, tests/test_checksum.py
 
 - [ ] 步骤 1：测试：
   1. sum 已知帧数据得到期望值 0xFCE3
   2. calculate_checksum 用算法名调用
   3. 空数据返回 0xFFFF
 
 - [ ] 步骤 2：实现
 
 ```python
 def sum_invert_low16(data):
     s = sum(data)
     return (~s) & 0xFFFF
 
 def calculate_checksum(data, algorithm="sum_invert_low16"):
     if algorithm == "sum_invert_low16":
         return sum_invert_low16(data)
     raise ValueError(f"不支持的校验算法: {algorithm}")
 ```
 
 - [ ] 步骤 3：pytest 通过 → commit
 
 ---
 
 ### 任务 7：帧编码器 - 立即令模式
 
 文件：src/codec/frame_encoder.py, tests/test_frame_encoder.py
 
 - [ ] 步骤 1：测试验证：
   1. TCHEDTTA001 复位帧帧头正确，指令码=001A
   2. TCHEDTTA106 点火时间含参数 00000078
   3. 校验和计算正确
 
 - [ ] 步骤 2：实现 encode_immediate_command
 
 ```python
 import struct
 from src.codec.checksum import calculate_checksum
 
 def encode_immediate_command(table, cmd_name, params_bytes=b"", seq=0, apid=None):
     if apid is None:
         apid = bytes.fromhex("0520")
     cmd = table.lookup(cmd_name)
     inst_code = bytes.fromhex(cmd["指令码"])
     data = inst_code + params_bytes
     data_len = len(data) - 1
     header = bytes.fromhex("EB90") + apid
     header += struct.pack(">H", (0b11 << 14) | (seq & 0x3FFF))
     header += struct.pack(">H", data_len & 0xFFFF)
     payload = header + data
     checksum = calculate_checksum(payload[2:])
     return payload + struct.pack(">H", checksum)
 ```
 
 - [ ] 步骤 3：pytest 通过 → commit
 
 ---
 
 ### 任务 8：帧编码器 - 注入包模式
 
 文件：src/codec/frame_encoder.py（追加）, tests/test_frame_encoder_inject.py
 
 - [ ] 步骤 1：测试验证：
   1. 注入1 帧长度 = 240 字节
   2. TCT4001(240) 在字节10-13, TCT4002(120) 在字节14-17
   3. 校验和正确
 
 - [ ] 步骤 2：在 frame_encoder.py 追加
 
 ```python
 def encode_inject_package(inj_table, inst_code, seq=0, apid=None):
     if apid is None:
         apid = bytes.fromhex("0520")
     import struct
     params = inj_table.get_params()
     params_sorted = sorted(params, key=lambda p: int(p.get("位偏移bit_offset") or 0))
     data = inst_code
     for p in params_sorted:
         dt = str(p.get("数据类型") or "").lower().strip()
         val = float(p.get("参数值(十进制)") or 0)
         if dt in ("float", "float32"):
             data += struct.pack(">f", val)
         elif dt == "uint32":
             data += struct.pack(">I", int(val))
         else:
             data += struct.pack(">f", val)
     data_len = len(data) - 1
     header = bytes.fromhex("EB90") + apid
     header += struct.pack(">H", (0b11 << 14) | (seq & 0x3FFF))
     header += struct.pack(">H", data_len & 0xFFFF)
     payload = header + data
     checksum = calculate_checksum(payload[2:])
     return payload + struct.pack(">H", checksum)
 ```
 
 - [ ] 步骤 3：pytest 通过 → commit
 
 ---
 
 ### 任务 9：帧解码器 (frame_decoder.py)
 
 文件：src/codec/frame_decoder.py, tests/test_frame_decoder.py
 
 - [ ] 步骤 1：实现 decode_telemetry_frame，按位偏移提取参数
 
 ```python
 import struct
 
 def decode_telemetry_frame(tm, frame, package_name, resolve_enum=False):
     params = tm.get_package(package_name)
     result = {}
     for p in params:
         pid = str(p.get("遥测代号") or "").strip()
         if not pid:
             continue
         bo = int(p.get("位偏移bit_offset") or 0)
         bl = int(p.get("位长度bit_length") or 0)
         dt = str(p.get("数据类型") or "").lower().strip()
         scale = float(p.get("当量") or 1)
         if bl == 0:
             continue
         start_byte = bo // 8
         end_byte = (bo + bl + 7) // 8
         chunk = frame[start_byte:end_byte]
         if len(chunk) == 0:
             continue
         val = int.from_bytes(chunk, "big")
         shift = (end_byte * 8 - bo - bl)
         val = (val >> shift) & ((1 << bl) - 1)
         if dt in ("uint8", "uint16", "uint32", "uint"):
             result[pid] = val * scale
         elif dt in ("int16", "int32"):
             if val >= (1 << (bl - 1)):
                 val -= (1 << bl)
             result[pid] = val * scale
         elif dt in ("float32", "float"):
             result[pid] = struct.unpack(">f", chunk)[0] if len(chunk) == 4 else val
         elif dt in ("enum", "status", "bitfield"):
             sv = str(val)
             if resolve_enum:
                 em = tm.get_enum_map(pid)
                 result[pid] = em.get(sv, sv)
             else:
                 result[pid] = sv
         else:
             result[pid] = val * scale
     return result
 ```
 
 - [ ] 步骤 2：测试 → 通过 → commit
 
 ---
 
 ### 任务 10：端到端集成测试
 
 文件：tests/test_integration.py
 
 - [ ] 步骤 1：编写集成测试验证全套流程
   1. 发送 TCHEDTTA003_2(推进模式) → 帧结构正确 → 校验和正确
   2. 注入1 包长度240 → 首末参数正确
   3. 加载所有4个配置表 → 行数正确
 
 - [ ] 步骤 2：pytest tests/ -v 全部通过 → commit
 
 ---
 
 ## 自检
 
 - 规格覆盖：3.1(任务2), 3.3.1(任务3+7), 3.3.2(任务4+9), 3.3.3(任务5+8) 均已覆盖
 - 占位符：无 TODO/待定，每个任务有完整代码
 - 类型一致：函数签名在各任务间一致
 - 后续 Phase（判据系统、协议驱动、GUI）标记为下一阶段
