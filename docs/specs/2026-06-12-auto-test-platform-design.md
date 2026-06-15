 # 通用自动化测试平台 — 设计规格说明书
 
 **文档编号**: SPEC-20260612-001
 **版本**: 1.1
 **日期**: 2026-06-15
 **状态**: 定稿
 
 ---
 
 ## 1. 概述
 
 ### 1.1 项目目标
 
 开发一款通用的自动化测试软件，支持通过配置（而非硬编码）适配不同的通信协议和数据格式，允许用户灵活编排测试序列，适用于航天器推进系统等领域的自动化测试场景。
 
 ### 1.2 核心设计原则
 
 - **零硬编码**: 所有协议定义、指令码表、遥测参数表均由外部配置文件驱动
 - **协议无关引擎**: 测试执行引擎不感知协议细节，仅通过统一接口与驱动交互
 - **配置驱动**: 系统的"业务知识"全部存储在配置文件中，代码只提供框架和流程
 - **直接读Excel**: 运行时直接读取 Excel 配置文件（openpyxl, data_only=True），无需中间转换环节
- **可扩展性**: 新增协议只需新增驱动插件 + 配置文件，无需修改核心引擎
 
 ### 1.3 适用范围
 
 本规格涵盖系统的架构设计、组件划分、配置文件体系、接口定义、GUI 设计和错误处理策略，用于指导后续的实现计划。
 
 ---
 
 ## 2. 整体架构
 
 ### 2.1 分层结构
 
 系统分为四层，自底向上：
 
 ```
 ┌─────────────────────────────────────────────────────────────┐
 │                      GUI 应用层 (PySide6)                     │
 │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
 │  │测试序列    │  │实时遥测    │  │测试报告    │  │系统设置    │  │
 │  │编辑器     │  │监视器     │  │生成器     │  │(连接/配置) │  │
 │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
 ├───────┼─────────────┼─────────────┼───────────────┼────────┤
 │       ▼             ▼             ▼               ▼        │
 │  ┌─────────────────────────────────────────────────────────┐ │
 │  │                  测试执行引擎                             │ │
 │  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────────┐ │ │
 │  │  │步骤    │ │超时    │ │异步    │ │判据    │ │日志/状态    │ │
 │  │  │调度器  │ │管理器  │ │收发器  │ │评估器  │ │管理器      │ │
 │  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────────────┘ │ │
 │  │  ┌──────────────────────────────────────────────────┐  │ │
 │  │  │            协议配置模块 (Configurator)             │  │ │
 │  │  │  帧编码 / 帧解码 / 校验计算 / 遥测参数解析          │  │ │
 │  │  └──────────────────────────────────────────────────┘  │ │
 │  └────────────────────────┬──────────────────────────────┘ │
 ├───────────────────────────┼────────────────────────────────┤
 │                           ▼                                │
 │  ┌─────────────────────────────────────────────────────────┐ │
 │  │                  协议驱动层 (插件)                        │ │
 │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
 │  │  │ RS-422 驱动   │  │ CAN 驱动      │  │ TCP 驱动      │  │ │
 │  │  │(pyserial)    │  │(python-can)  │  │(socket)      │  │ │
 │  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
 │  │  ┌──────────────────────────────────────────────────┐  │ │
 │  │  │  未来可扩展: 1553B / SPI / I2C / UDP 等          │  │ │
 │  │  └──────────────────────────────────────────────────┘  │ │
 │  └─────────────────────────────────────────────────────────┘ │
 ├─────────────────────────────────────────────────────────────┤
 │  ┌─────────────────────────────────────────────────────────┐ │
 │  │                  配置文件体系                             │ │
 │  │                                                          │ │
 │  │  protocols/  ─ 协议定义（帧头/校验/字节序/波特率等）       │ │
 │  │  commands/   ─ 指令码表（命令名→hex指令+参数定义）         │ │
 │  │  telemetry/  ─ 遥测参数表（参数ID→偏移/类型/转换公式）     │ │
 │  │  sequences/  ─ 测试序列（步骤编排+时序判据）               │ │
 │  │  devices/    ─ 设备实例（串口号/CAN ID/IP地址等）         │ │
 │  └─────────────────────────────────────────────────────────┘ │
 └─────────────────────────────────────────────────────────────┘
 ```
 
 ### 2.2 组件依赖关系
 
 ```
 GUI 层 ────→ 引擎层 ────→ 驱动层
   │              │            │
   │              │            └── 协议配置加载配置文件
   │              └── 加载配置文件
   └── 加载配置文件（序列编辑时预览）
 ```
 
 从上到下单向依赖，下层不依赖上层。
 
 ---
 
 ## 3. 配置文件体系
 
 ### 3.1 总体策略
 
 **直接读 Excel**: 运行时直接读取 Excel 配置文件（openpyxl, data_only=True），Excel 是唯一的编辑入口和数据源。
 
 - Excel 是唯一的 source of truth，只在 Excel 中手工编辑
 - 运行时通过 openpyxl（data_only=True）直接读取，Excel 公式（如 =E2+F2）自动计算为数值
 - 列名到字段的映射集中在 loader.py 中，格式变化只改一处
 
 ### 3.2 文件目录结构
 
 ```
 project_root/
 ├── src/                     # 源码目录
│   └── ...
├── tests/                   # 测试目录
│   └── ...
├── 项目文档/
│   ├── 优化后excel配置表/    # 运行时直接读取的 Excel 配置文件
│   │   ├── 立即遥控指令配置表_优化后.xlsx   (92 条指令)
│   │   ├── 遥测配置表_优化后.xlsx           (253 个遥测参数)
│   │   ├── 固定地址参数注入表1_优化后.xlsx  (57 个注入参数)
│   │   └── 固定地址参数注入表2_优化后.xlsx  (39 个注入参数)
│   ├── excel版遥测大表草稿/   # 原始草稿
│   └── 星云RS422通讯协议A04_20250423二院.docx
├── scripts/
 │   ├── protocols/          # 协议定义 (YAML, 自动生成)
 │   │   ├── rs422_ppcu.yaml
 │   │   └── can_default.yaml
 │   ├── commands/           # 指令码表 (YAML, 自动生成)
 │   │   ├── ppcu_immediate.yaml
 │   │   └── ppcu_inject.yaml
 │   ├── telemetry/          # 遥测参数表 (YAML, 自动生成)
 │   │   ├── ppcu_slow.yaml
 │   │   └── ppcu_fast.yaml
 │   ├── sequences/          # 测试序列 (YAML, 手工编写或GUI生成)
 │   │   ├── normal_ignition_test.yaml
 │   │   └── cathode_activation_test.yaml
 │   └── devices/            # 设备实例 (YAML)
 │       └── lab_device.yaml
 ├── config_templates/       # Excel 模板和 YAML 模板参考
 │   ├── protocol_template.xlsx
 │   ├── commands_template.xlsx
 │   ├── telemetry_template.xlsx
 │   └── yaml_examples/
 │       ├── protocol_example.yaml
 │       ├── commands_example.yaml
 │       └── telemetry_example.yaml
 ├── scripts/
 │   └── convert_xlsx_to_yaml.py   # Excel → YAML 转换脚本
 └── docs/
     └── specs/
         └── 2026-06-12-auto-test-platform-design.md
 ```
 
 ### 3.3 三种指令/遥测数据类型

系统目前支持 4 个配置表，对应 3 种数据类型。

#### 3.3.1 立即遥控指令 (Immediate Commands)

- 来源：立即遥控指令配置表_优化后.xlsx (92 条)

#### 3.5.2 遥测参数 (Telemetry)

- 来源：遥测配置表_优化后.xlsx (253 参数)

#### 3.5.3 固定参数注入 (Fixed Parameter Injection)

- 来源：固定地址参数注入表1/2_优化后.xlsx (57+39 参数)
- 模式：整表打包发送

### 3.4 帧结构

Byte 0-1:标识符(EB90) Byte 2-3:APID(0520) Byte 4-5:分组标志(2bit)+序列号(14bit) Byte 6-7:数据域长度 Byte 8-9:指令码 Byte 10+:参数 Last 2B:校验和

固定参数注入帧：同上，Byte 8-9:指令码(03FF/03FE)

### 3.5 配置格式说明（YAML 参考）

> 以下 YAML 示例仅为格式参考。

#### 3.5.1 协议定义 (protocols/*.yaml)
 
 ```yaml
 name: rs422_ppcu
 type: rs422
 baudrate: 115200
 databits: 8
 parity: odd
 stopbits: 1
 frame:
   header: [0xEB, 0x90]
   response_header: [0x1A, 0xCF]
   byte_order: big_endian
   checksum:
     algorithm: sum_invert_low16
     range: [2, -2]
   fields:
     - name: header
       offset: 0
       length: 2
     - name: version_type_apid
       offset: 2
       length: 2
     - name: sequence_count
       offset: 4
       length: 2
     - name: data_length
       offset: 6
       length: 2
     - name: data
       offset: 8
       length: dynamic
     - name: checksum
       offset: end
       length: 2
 ```
 
 #### 3.5.2 指令码表 (commands/*.yaml)
 
 ```yaml
 protocol: rs422_ppcu
 apid: 0x520
 type: immediate
 
 commands:
   - name: TCHEDTTA106
     description: 正常点火时间设置
     code: 0x03D8
     params:
       - name: 保留参数1
         length: 2
         default: 0x0000
       - name: 点火时长
         length: 2
         unit: s
         scale: 1
         default: 120
         range: [0, 65535]
   
   - name: TCHEDTTA016_1
     description: 流量控制方式
     code: 0x0307
     params:
       - name: 流量控制方式
         length: 1
         type: enum
         default: 压传闭环
         values:
           - value: 0x00
             label: 压传闭环
           - value: 0x11
             label: 阳极电流闭环
           - value: 0x22
             label: 双级减压
 
   - name: TCHEDTTA003_2
     description: 工作模式切换
     code: 0x0030
     params:
       - name: 工作模式
         length: 1
         type: enum
         default: 待机模式
         values:
           - value: 0x00
             label: 待机模式
           - value: 0x11
             label: 推进模式
           - value: 0x44
             label: 阴极激活模式
           - value: 0xFF
             label: 维护模式
 ```
 
 #### 3.5.3 遥测参数表 (telemetry/*.yaml)
 
 ```yaml
 protocol: rs422_ppcu
 frame_type: response
 apid: 0x520
 response_header: [0x1A, 0xCF]
 
 parameters:
   - id: TMHEDTT2079
     name: 本次阳极点火设置时长
     frame: slow
     offset: 12
     length: 2
     type: uint16
     unit: s
     scale: 1
 
   - id: TMHEDT2023
     name: 流量控制模式
     frame: slow
     offset: 28
     length: 1
     type: enum
     enum_map:
       0x00: 压传闭环
       0x11: 阳极电流闭环
       0x22: 双级减压
 
   - id: TMHEDTT1005
     name: 工作模式字
     frame: fast
     offset: 14
     length: 1
     type: enum
     enum_map:
       0x0: 待机模式
       0x1: 推进模式
       0x3: 管路预处理模式
       0x4: 阴极激活模式
       0xF: 维护模式
 
   - id: TMHEDT1022
     name: 电磁阀SV2状态检测
     frame: fast
     offset: 46
     length: 2bit
     type: status
     status_map:
       0: 关
       3: 开
 ```
 
 #### 3.5.4 测试序列 (sequences/*.yaml)
 
 ```yaml
 name: 正常点火测试
 description: 验证正常点火流程各参数正确性
 version: 1.0
 
 steps:
   - id: S01
     name: 设置点火时间120s
     command: TCHEDTTA106
     params:
       点火时长: 120
     expect:
       - type: slow_frame
         timeout: 5s
         checks:
           logic: and
           conditions:
             - param: TMHEDTT2079
               operator: eq
               value: 120
 
   - id: S02
     name: 切换流量控制为压传闭环
     command: TCHEDTTA016_1
     params:
       流量控制方式: 压传闭环
     expect:
       - type: slow_frame
         timeout: 5s
         checks:
           logic: and
           conditions:
             - param: TMHEDT2023
               operator: eq
               value: 压传闭环
             - param: TMHEDT2024
               operator: eq
               value: PID
 
   - id: S03
     name: 切换正常点火模式
     command: TCHEDTTA003_2
     params:
       工作模式: 推进模式
     anchors:
       - name: t0
         type: command_sent
       - name: t_enter_propulsion
         type: condition_met
         wait: 60s
         on:
           param: TMHEDTT1005
           operator: changed_to
           value: 推进模式
     timeline:
       - at: +0s
         from: t0
         checks:
           - param: TMHEDTT1005
             operator: eq
             value: 推进模式
       - at: +10s
         from: t_enter_propulsion
         checks:
           - param: TMHEDTT1006
             operator: eq
             value: 下游供气管路放气
       - at: +50s
         from: t0
         checks:
           - param: TMHEDT1022
             operator: eq
             value: 开
 
 config:
   retry:
     max_retries: 3
     retry_delay: 1s
   on_step_failure: continue
 ```
 
 ### 3.6 判据条件系统
 
 #### 3.6.1 逻辑组合
 
 ```yaml
 checks:
   logic: or
   conditions:
     - logic: and
       conditions:
         - param: A
           operator: eq
           value: X
         - param: B
           operator: eq
           value: Y
     - logic: and
       conditions:
         - param: C
           operator: not_eq
           value: 异常
         - param: D
           operator: between
           value: [10, 20]
 ```
 
 #### 3.6.2 支持的运算符
 
 | 运算符 | 含义 | 适用值类型 |
 |--------|------|-----------|
 | eq | 等于 | 所有 |
 | not_eq | 不等于 | 所有 |
 | gt / ge | 大于 / 大于等于 | 数值 |
 | lt / le | 小于 / 小于等于 | 数值 |
 | between | 在闭区间内 [a, b] | 数值 |
 | in | 属于枚举值集合 | 枚举 |
 | not_in | 不属于枚举值集合 | 枚举 |
 | changed_to | 从其他值变为目标值 | 所有 |
 | changed_from_to | 从特定值变为特定值 | 所有 |
 | stable_for | 稳定在某个条件下保持T秒 | 所有（叠加） |
 
 #### 3.6.3 时序模式
 
 | 模式 | 说明 |
 |------|------|
 | at: +Xs (固定偏移) | 以锚点为基准，延迟X秒后执行检查 |
 | mode: poll (持续监测) | 按 poll_interval 持续检查，条件满足或超时即止 |
 | mode: sequence (状态序列) | 定义一组按时间顺序的检查点 |
 | at: +a..+b (时间窗口) | 在[a, b]秒窗口内任意时刻满足即通过 |
 
 #### 3.6.4 锚点体系
 
 | 锚点类型 | 含义 | 触发条件 |
 |----------|------|---------|
 | command_sent | 命令发出瞬间 | 步骤开始执行时自动触发 |
 | condition_met | 某条件首次满足 | 持续监测遥测直到条件成立 |
 | frame_received | 收到指定类型帧 | 帧解析器匹配到指定APID |
 | step_pass | 上一步通过 | 上一步骤状态变为Pass |
 | manual | 用户手动打标 | GUI中点击标记按钮 |
 
 ---
 
 ## 4. 协议驱动层
 
 ### 4.1 驱动接口定义
 
 ```python
 class ProtocolDriver(ABC):
     @abstractmethod
     def open(self, config: dict) -> bool: ...
     @abstractmethod
     def close(self): ...
     @abstractmethod
     def send(self, data: bytes): ...
     @abstractmethod
     def set_receive_callback(self, callback): ...
     @abstractmethod
     def is_open(self) -> bool: ...
     @property
     def name(self) -> str: ...
 ```
 
 ### 4.2 内置驱动
 
 | 驱动 | Python 依赖 | 说明 |
 |------|------------|------|
 | RS422Driver | pyserial | 标准串口通信 |
 | CANDriver | python-can | CAN总线通信 |
 | TcpDriver | socket（内置） | TCP客户端模式 |
 
 ### 4.3 驱动注册机制
 
 ```python
 DRIVER_REGISTRY = {
     "rs422": RS422Driver,
     "can": CANDriver,
     "tcp": TcpDriver,
 }
 ```
 
 ---
 
 ## 5. 测试执行引擎
 
 ### 5.1 核心工作流
 
 ```
 启动序列
    │
    ▼
 加载配置文件
    │
    ▼
 [循环每个步骤]
    │
    ├─ 1. 查找命令名 → 获取指令码 + 参数格式
    ├─ 2. 协议配置模块编码帧
    ├─ 3. 通过协议驱动发送
    ├─ 4. 注册预期监听器
    │      ├─ 启动锚点监听
    │      ├─ 启动 timeline 定时器
    │      └─ 启动超时定时器
    ├─ 5. 等待 → 条件满足 / 超时 / 异常
    ├─ 6. 判据评估器评估 → Pass / Fail / Error
    ├─ 7. 记录结果
    └─ 8. 根据 on_failure 策略决定继续/跳过/中止
    │
    ▼
 序列结束 → 生成测试报告
 ```
 
 ### 5.2 核心模块
 
 | 模块 | 职责 |
 |------|------|
 | StepScheduler | 按序调度步骤，管理流程控制 |
 | TimeoutManager | 管理步骤级和全局超时 |
 | AsyncTransceiver | 后台线程持续收发，带时间戳的帧队列 |
 | AssertionEngine | 解析 logic 树，判断时序条件 |
 | ProtocolConfigurator | 帧编码/解码、校验计算、遥测参数解析 |
 | LogManager | 记录收发字节、中间值、判定结果 |
 
 ---
 
 ## 6. GUI 应用层 (PySide6)
 
 ### 6.1 主窗口布局
 
 使用 QTabWidget 组织多标签页：
 
 - **测试方案 (TestSuite)**: 树形方案列表，管理多个测试序列
 - **序列编辑 (SequenceEditor)**: 步骤列表 + 右侧属性面板，支持拖拽排序
 - **实时监控 (LiveMonitor)**: 遥测参数树 + 数值/波形显示 + 日志窗口
 - **报告查看 (ReportView)**: 测试结果概览 + 详细日志
 - **系统设置 (Settings)**: 连接管理（串口/CAN/TCP）、配置文件路径
 
 ### 6.2 关键交互设计
 
 - 序列编辑器中选中指令后，右侧自动加载参数定义和预期判据编辑器
 - 实时监控与测试执行独立
 - 运行中可暂停/继续/中止/手动发指令
 
 ---
 
 ## 7. 错误处理策略
 
 ### 7.1 异常分级
 
 | 级别 | 含义 | 处理 |
 |------|------|------|
 | Warn | 遥测偏离预期 | 记录告警，继续执行 |
 | Fail | 判据不通过 | 标记失败，按策略继续/跳过/中止 |
 | Error | 通信中断/无响应 | 中止当前步骤，尝试重连 |
 | Critical | 校验错误/帧损坏 | 丢弃帧，重试N次后上报Error |
 
 ### 7.2 重试策略
 
 - 全局默认：最多重试3次，间隔1s
 - 步骤级可覆盖 retry.max_retries 和 retry.retry_delay
 - 步骤失败行为：continue/skip/abort
 
 ---
 
 ## 8. 测试报告
 
 ### 8.1 报告内容
 
 - 概要信息（项目名称、日期、耗时、通过率）
 - 步骤列表（ID、名称、判定、耗时）
 - 详细时序（每个时间点的检查结果）
 - 原始收发字节记录
 
 ### 8.2 导出格式
 
 - HTML
 - PDF
 - Excel
 - 二进制追踪文件 (.bin)
 
 ---
 
 ## 9. 软件测试策略
 
 | 测试层 | 范围 | 工具 |
 |--------|------|------|
 | 单元测试 | 帧编码/解码、校验计算、判据评估 | pytest |
 | 集成测试 | 全链路：配置→帧编码→帧解码→判据 | pytest + mock |
 | 通信测试 | 模拟串口回环/虚拟CAN | pytest + 虚拟串口 |
 | GUI测试 | 主窗口加载、序列编辑、运行更新 | pytest-qt |
 
 ---
 
 ## 10. 配置文件格式建议
 
 ### 10.1 推荐方案

**直接读 Excel**
 
 - 领域工程师使用 Excel 编辑
 - 
 - git 同时提交 Excel 和 YAML
 
 ### 10.2 工作流
 
 ```
 领域工程师编辑 Excel → git commit → 引擎直接加载 Excel (openpyxl data_only=True)
 ```
 
 ### 10.3 当前 Excel 配置表结构

当前所有配置表位于 项目文档/优化后excel配置表/，运行时直接读取。

**立即遥控指令配置表_优化后.xlsx**

| Sheet | 内容 | 行数 |
|-------|------|------|
| 立即遥控指令 | 每条指令一行：指令代号、指令码、参数字节数、值类型、枚举说明 | 92 |
| 枚举值映射表 | 指令码→参数值→枚举标签 映射（软件自动解析） | 84 |
| 帧格式参考(CCSDS) | 帧头/APID/序列号/指令码/校验和的位结构 | 7 |

**遥测配置表_优化后.xlsx**

| Sheet | 内容 | 行数 |
|-------|------|------|
| 常规包1(SlowFrame) | 慢帧1遥测参数：代号、位偏移、位长度、数据类型、当量 | 52 |
| 常规包2(SlowFrame2) | 慢帧2遥测参数 | 91 |
| 查询包1(QueryFrame) | 查询帧遥测参数 | 110 |
| 枚举值映射表 | 参数ID→Hex值→标签（自动解析） | 192 |
| 帧格式参考(CCSDS) | 应答帧头/数据域/校验和结构 | 7 |

**固定地址参数注入表1_优化后.xlsx**

| Sheet | 内容 | 行数 |
|-------|------|------|
| 固定地址参数注入1 | 57个float32参数，打包发送 | 57 |
| 帧格式参考(CCSDS) | 含指令码 03FF 的完整帧结构 | 9 |

**固定地址参数注入表2_优化后.xlsx**

| Sheet | 内容 | 行数 |
|-------|------|------|
| 固定地址参数注入2 | 39个float32参数，打包发送 | 39 |
| 帧格式参考(CCSDS) | 含指令码 03FE 的完整帧结构 | 9 |
 
 ---
 
 ### 11.3 当前配置表清单

| 文件名 | 数据行 | 用途 |
|--------|--------|------|
| 立即遥控指令配置表_优化后.xlsx | 92 | 指令编码 |
| 遥测配置表_优化后.xlsx | 253 | 遥测解析 |
| 固定地址参数注入表1_优化后.xlsx | 57 | 注入参数 |
| 固定地址参数注入表2_优化后.xlsx | 39 | 注入参数 |

---

## 11. 附录
 
 ### 11.1 术语表
 
 | 术语 | 含义 |
 |------|------|
 | SUT | 被测系统 (System Under Test) |
 | APID | 应用过程标识 (Application Process ID) |
 | Slow Frame | 慢帧，低频率遥测数据包 |
 | Fast Frame | 快帧，高频率遥测数据包 |
 | Anchor | 时间锚点，时序判断的参照物 |
 | Timeline | 时序线，基于锚点的检查序列 |
 
 ### 11.2 参考文档
 
 - 星云RS422通讯协议A04\_20250423二院.docx
