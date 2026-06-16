# Phase 3: 测试执行引擎 — 实现计划

目标: 实现 YAML 驱动的测试执行引擎, 包含 5 个核心模块

文件结构:
  src/engine/
    __init__.py
    sequence_loader.py      YAML 加载 + schema 校验
    assertion_engine.py     判据评估 (AND/OR/NOT + 所有运算符)
    timeline_engine.py      锚点 + 时序队列管理
    step_scheduler.py       步骤调度 (顺序/条件跳转/循环)
    test_runner.py          总编排器
  tests/
    test_sequence_loader.py   3 tests
    test_assertion_engine.py  6 tests (每种运算符)
    test_timeline_engine.py   3 tests
    test_step_scheduler.py    3 tests
    test_integration.py       2 tests (全链路)
  sequences/
    normal_ignition_test.yaml 用户3步骤示例

任务列表:

Task 1: SequenceLoader
  文件: src/engine/sequence_loader.py, tests/test_sequence_loader.py
  实现 load() 和 validate(), 加载 YAML 转 dict, 校验必需字段
  测试: 加载成功, 缺失字段报错, 错误步骤号提示

Task 2: AssertionEngine
  文件: src/engine/assertion_engine.py, tests/test_assertion_engine.py
  实现 evaluate() 递归逻辑树, 支持所有运算符和容差
  包含 changed_to 的跨帧状态比较和 rising_to 的趋势检查
  测试: 每个运算符单独测试, AND/OR 嵌套, 容差, rising_to

Task 3: TimelineEngine
  文件: src/engine/timeline_engine.py, tests/test_timeline_engine.py
  实现锚点注册/触发和时序队列管理
  测试: command_sent 锚点, condition_met 锚点, 时间窗口 +at:5s..+6s

Task 4: StepScheduler
  文件: src/engine/step_scheduler.py, tests/test_step_scheduler.py
  实现步骤顺序调度和 handle_result 流程控制
  测试: 正常执行, abort 中止, skip 跳过

Task 5: TestRunner
  文件: src/engine/test_runner.py
  编排器: 加载 YAML > 连接驱动 > 逐步骤执行 > 返回报告

Task 6: YAML 示例
  sequences/normal_ignition_test.yaml
  用户 3 步骤示例, 含枚举参数/数值参数/timeline/anchors

Task 7: 集成测试
  tests/test_integration.py
  全链路: 加载 YAML + mock 驱动执行 + 判据评估 + 报告
