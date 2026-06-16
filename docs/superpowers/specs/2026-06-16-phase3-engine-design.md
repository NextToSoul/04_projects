# Phase 3 测试执行引擎 — 设计规格说明书

**文档编号**: SPEC-20260616-001
**版本**: 0.1
**日期**: 2026-06-16

## 1. 概述

实现测试执行引擎，将 Phase 1（配置解析/帧编解码）和 Phase 2（TCP 驱动）串联为完整的测试执行流程。

设计原则:
- YAML 驱动: 测试序列定义在 YAML 文件中，不写代码
- 模块单向依赖: Loader > Scheduler > AssertionEngine > TestRunner
- 与 GUI 解耦: 引擎不依赖任何 GUI 组件

## 2. 整体架构

<pre>
sequences/*.yaml
       |
       v
  sequence_loader.py     YAML 加载 + schema 校验
       |
       v
  step_scheduler.py     步骤调度 (顺序/条件跳转/循环)
       |
       v
  assertion_engine.py   判据评估 (AND/OR/NOT 逻辑树)
       |
       v
  timeline_engine.py    锚点 + 时序队列管理
       |
       v
  test_runner.py        总编排器 (加载 > 调度 > 评估 > 报告)
       |
       +-- config/   (CommandTable, TelemetryTable, InjectTable)
       +-- codec/    (checksum, frame_encoder, frame_decoder)
       +-- protocol/ (TcpDriver, ProtocolDriver)
</pre>

## 3. YAML 序列格式

### 3.1 顶层结构

<pre>
name: 正常点火测试
description: 验证正常点火流程
version: 1.0

steps:
  - id: S01
    name: 设置点火时间
    command: TCHEDTTA106
    params: "00000078"

  - id: S02
    command: TCHEDTTA016_1
    params: 压传闭环
    expect:
      - type: slow_frame
        timeout: 5s
        checks:
          logic: and
          conditions:
            - param: TMHEDT2023
              operator: eq
              value: 压传闭环

config:
  retry:
    max_retries: 3
    retry_delay: 1s
  on_step_failure: continue
</pre>

### 3.2 参数填写规则

- 枚举标签名: 如 推进模式, 引擎查枚举映射表反向映射为 hex
- 开关标签名: 如 使能, 引擎查枚举映射表反向映射为 hex
- hex 字符串: 如 00000078, 直接编码
- 纯数字: 如 120, 按十进制处理
- 0x 前缀: 如 0x78, 按十六进制处理
- 浮点数: 如 0.5, 按浮点处理
- 省略: 使用配置表默认值
- 无参数: 指令无参时不编码参数域

### 3.3 判据检查

<pre>
checks:
  logic: and
  conditions:
    - param: TMHEDT2023
      operator: eq
      value: 压传闭环
    - logic: or
      conditions:
        - param: TMHEDT2024
          operator: eq
          value: PID
</pre>

### 3.4 支持的运算符

eq: == 等于, 可带 tolerance 字段支持容差
not_eq: != 不等于
gt / ge: > / >=
lt / le: < / <=
between: 在区间内 [a,b]
in: 在集合中
changed_to: 从其他值变为目标值
rising_to: 从 start 单调上升到 end, 需 start_value/end_value/tolerance/within

### 3.5 时序检查

<pre>
anchors:
  - name: t0
    type: command_sent
  - name: t_p
    type: condition_met
    wait: 30s
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
    from: t_p
    checks:
      - param: TMHEDTT1006
        operator: eq
        value: 下游供气管路放气
</pre>

## 4. 核心模块

### 4.1 SequenceLoader
加载并校验 YAML 序列文件.

### 4.2 StepScheduler
按序调度步骤, 支持条件跳转.

### 4.3 AssertionEngine
递归评估 AND/OR/NOT 逻辑树.

### 4.4 TimelineEngine
管理锚点和时序队列.

### 4.5 TestRunner
总编排器, 加载 > 调度 > 评估 > 报告.

## 5. 判据评估器

递归逻辑树:
<pre>
def evaluate(node, decoded, prev=None):
    if "logic" in node:
        results = [evaluate(c, decoded, prev) for c in node["conditions"]]
        if node["logic"] == "and":  return all(results)
        if node["logic"] == "or":   return any(results)
    else:
        return _compare(node["operator"], decoded.get(node["param"]), node["value"], node.get("tolerance", 0))
</pre>

比较器实现:
- eq: abs(actual - expected) <= tolerance
- not_eq: abs(actual - expected) > tolerance
- gt: actual > expected
- ge: actual >= expected
- lt: actual < expected
- le: actual <= expected
- between: expected[0] <= actual <= expected[1]
- in: str(actual) in [str(x) for x in expected]
- changed_to: 检查上一帧到当前帧的跳变
- rising_to: 检查单调上升趋势和终值

## 6. 测试策略

- 单元测试 assertion_engine 各比较器
- 单元测试 sequence_loader YAML 解析
- 集成测试 全链路 YAML > 执行 > 报告
- 场景测试 用户 3 步骤示例完整验证

## 附录: 用户示例 YAML

<pre>
name: 正常点火测试
steps:
  - id: S01
    name: 设置点火时间120s
    command: TCHEDTTA106
    params: "00000078"
    expect:
      - type: slow_frame
        timeout: 5s
        checks:
          - param: TMHEDTT2079
            operator: eq
            value: 120

  - id: S02
    name: 切换流量控制
    command: TCHEDTTA016_1
    params: 压传闭环
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
            - param: TMHEDT2057
              operator: eq
              value: 自锁阀1

  - id: S03
    name: 切换正常点火
    command: TCHEDTTA003_2
    params: 推进模式
    anchors:
      - name: t0
        type: command_sent
    timeline:
      - at: +0s
        from: t0
        checks:
          logic: and
          conditions:
            - param: TMHEDTT1005
              operator: eq
              value: 推进模式
            - param: TMHEDTT1006
              operator: eq
              value: 下游供气管路放气/阴极0.8A加热
            - param: TMHEDTT2017
              operator: eq
              value: "0"
            - param: TMHEDT1022
              operator: eq
              value: 开
            - param: TMHEDT1023
              operator: eq
              value: 开
            - param: TMHEDTT2006
              operator: rising_to
              start_value: 0
              end_value: 40
              tolerance: 5
              within: 60s
      - at: +5s
        from: t0
        checks:
          - param: TMHEDT1020
            operator: eq
            value: 开
      - at: +60s
        from: t0
        checks:
          logic: and
          conditions:
            - param: TMHEDT1026
              operator: eq
              value: 开
            - param: TMHEDTT1006
              operator: eq
              value: 贮供流量调节阶段/阴极1.5A加热
</pre>
