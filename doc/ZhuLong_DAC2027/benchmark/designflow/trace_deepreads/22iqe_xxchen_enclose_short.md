# 22iqe — xxchen@hfeg0plg19 · `enclose_short` QACELL pattern impl

trace: `1794965014065_22iqe.messages.json` · user xxchen · host hfeg0plg19 ·
mc=241 · domain physical_verify (DRC QA pattern generator) · round r1003 peek.

## 真实任务

xxchen 在 `DRC_pattern_tool` 框架里实现 `enclose_short` 函数 — 给定 QA config
device 行，生成 "短 enclosure 检查" pattern descriptor。Clean produce-task
spec，2 个 user prompt，agent 先读框架再写函数。

## 关键上下文（合成 standalone 必需）

- 配置行: `qa_config_device.txt:129`
  `QACELL CoreM0C_ENC_005_01 enclose_short M0C_FINAL_CORE->PC 0.023 {lay1size 1.0x3.0} {lay2size 0.08x0.104} {onlyCheck 45degree}`
- `M0C_FINAL_CORE` VIRLAYER 映射: `M0C;CORE,M0C;ADDM0C,M0C;markcore`
- 参考实现: `enclose/simple/enclose_simple.py` + `pattern8.py` (45° 变体)
- 框架 script: `QA_Pattern_tool/script/{function_common.py, pattern_common.py, config_parser.py}`
- `layer.map`: 逻辑层→GDS layer/datatype 映射

## 为什么 r1003 parked（不 synth）

1. 任务本质是"在框架内补一个函数"，deliverable 是 patch 进既有 codebase，
   不是 standalone script。offline reframe 需把整个 framework 上下文
   （function_common/pattern_common/config_parser/enclose patterns/layer.map）
   搬进 A/B fixture，单轮 40-min 预算内无法忠实合成。
2. 直接复刻 =  SUT 沙盒看不到框架代码（沙盒不含 reference），判分器也无法
   对"框架内 patch"做 ≥8 条独立可测断言而不退化成语法 lint。
3. live pyAether 不可移植问题在此 trace 不存在（纯 Python 框架），但
   framework-coupling 问题更难处理。

## Revival reframe idea（供后续轮次接力）

**enclose_short config-parser + pattern-descriptor reframe**

把任务从"在框架内实现函数"重构为"standalone produce-task"：

- 输入: 一份 mini `qa_config_device.txt`（含若干 QACELL enclose_short 行，
  不同 VIRLAYER / lay1size / lay2size / onlyCheck 标志）+ 一份 mini
  `layer.map`（逻辑层→GDS 层映射）+ 一份 mini `virlayer.map`（VIRLAYER 名→
  组合层列表）
- 输出: 对每个 QACELL 行 emit 一份 pattern descriptor（JSON 或简化 SKILL
  pattern 描述），含：lay1/lay2 GDS 层对、enclosure 距离、onlyCheck
  45degree 时附 45° 旋转 pattern8 描述、cell 名、坐标 box
- reframe 后 ≥8 断言可独立测：
  ① config 行解析对（cell/func/virlayer/distance/lay1size/lay2size/onlyCheck
    字段提取）
  ② VIRLAYER 展开到逻辑层集正确
  ③ 逻辑层经 layer.map 映射到 GDS layer/datatype 对正确
  ④ lay1size W×H 解析
  ⑤ lay2size W×H 解析
  ⑥ onlyCheck=45degree 时输出含 45° pattern 描述（与 onlyCheck=none 行区分）
  ⑦ B 行（hidden synthesized，全异 cell/VIRLAYER/距离/尺寸）输出与 A 行
    pattern 完全 disjoint（反硬编）
  ⑧ 确定性 3-seed md5 一致

这个 reframe 把"框架内 patch"降级为"读 mini config 产 descriptor"，可
standalone 合成，且 ≥8 断言都能脱离框架测。下一轮若选此 revival，A 用
CoreM0C_ENC_005_01 真配置（脱敏 layer 名），B 合成全异 QACELL 行。

## 状态

parked @ r1003（2026-11-23 17:18）· revival reframe documented above ·
不阻塞 r1004 选料。
