# trace_deepread: rrx5s — FineSim .probe coverage / Vtlin recoverability Q&A

- **sid**: 1795152550043_rrx5s
- **user/host**: leo1ye @ hfeg0plg58 (10.129.x)
- **mc**: 9 (hspice:19; aether:6; mosfet:5; waveview:4; netlist:4; pyaether:2; virtuoso:1)
- **scan**: ssh_eda_search_20261122_172249
- **size**: 44279 B / 10 msgs (6 user+assistant turns)
- **fetched via**: `scp hfeg0plg58:/home/leo1ye/.cline/data/sessions/1795152550043_rrx5s/1795152550043_rrx5s.messages.json` (nested path)

## User intent (real task)
leo1ye 在 fullchip FineSim 仿真后想从 FSDB 中提取一个深层级器件的 **Vtlin（线性阈值电压，OP 参数）**：
1. U0: "how to get device vtlin in fullchip sim" — 问 AskEDA 知识库。
2. assistant 给出 Tcl API `get_device_param` / `.measure` 两套方案。
3. U6: 给出真实 FSDB 路径 + 目标器件层级 `xi_ddr6top_r.xi_array32gtop_0.....xim512meg_b02.ximsaq_47.xi_msax456_9.xi_cxsa_1x4_4.xmmn1r_iso.mn1`。
4. U8: 贴出仿真实际用的 `.probe` 语句清单：
   ```
   *.probe v(*)
   *.probe i(*)
   .probe v(*) except="*:*"
   .probe regexp=v(m\w+:gate)
   .probe regexp=v(m\w+:drn)
   .probe regexp=v(m\w+:src)
   .probe regexp=v(m\w+:bulk)
   .probe regexp=v(\w+:1$)
   ```
5. assistant 结论：这些 .probe 只存**节点电压**和**MOSFET 四端电压**（gate/drn/src/bulk）+ `:1` 端口电压，**不存 Vth/Vtlin 等 OP 参数** → Vtlin 不可恢复；要恢复需补 `.probe vth(...)` 或开 OP save。

## 关键产物
- 无脚本产物（纯 Q&A）。用户的核心信息需求 = "我这组 .probe 语句能不能拿到 Vtlin"。

## Reframe（L1 Python 复刻，符合"任务形态=用户意图"）
把用户的信息需求程序化：**FineSim `.probe` 语句覆盖分析器** `probe_cov_analyzer.py <spec.json> <out.json>`
- 输入 spec：{simulator, target, fsdb, device, probes:[<.probe 行>]}
- 逐行解析 .probe 语句：
  - 跳过注释行（`*` 开头，含 `*.probe`）
  - 抽 `except="..."` 子句、`regexp=` 前缀
  - 按 `func(arg)` 分类：`v(*)`→all_node_voltage；`i(*)`→all_current；`v(<pat>:<term>)`→device_terminal_voltage；`vth/vtlin/...`→op_param（param=func 名）
- 判定 target OP 参数可恢复性：∃ active op_param 探针且 param==target → recoverable；否则 not_recoverable
- 输出 JSON：{simulator, target, probes:[{line,active,category,func,arg,param,is_regexp,pattern,except}], n_active, n_commented, verdict, reason}

## A（可见，忠实 leo1ye 真实 .probe 清单）
- target=vtlin, 8 行 .probe（2 注释 + 6 active），verdict=not_recoverable（无 op_param 探针）— 与 trace assistant 结论一致。

## hidden B（五重 anti-hardcode）
- target=vth（≠ vtlin）
- 探针器件字母 x\w+（≠ m\w+），端名 g/d/s/b（≠ gate/drn/src/bulk）
- except="X*"（≠ "*:*"）
- 端口模式 `\w+:p2$`（≠ `\w+:1$`）
- **B 含显式 op_param 探针 `regexp=vth(m\w+)`** → verdict=**recoverable**（≠ A 的 not_recoverable）— 核心齿，反 "永远 not_recoverable" naive

## check.py 13 条独立断言（a-m）
a zip+py_compile+size; b B exit0+非空 report; c 顶层键集合精确; d n_active==8; e n_commented==1; f len(probes)==9; g 逐 active 探针 category==oracle; h op_param 探针 param==vth; i regexp 字段（regexp 探针 pattern 非空 / 非 regexp 为 None）; j except 字段（idx2=="X*" 余 None）; k verdict==recoverable（核心齿）; l anti-hardcode（B target 在场 / A 的 vtlin+`m\w+:gate`+`*:*` 全缺席）; m 3-seed sha256 一致。

## 3 negs（§4.9 三假）
- neg_empty → a/b FAIL
- neg_print_only（硬编 A 的 report）→ d/e/f/g/h/j/k/l FAIL（8 齿）
- neg_core_removed（真解析 B 但 op_param param 置 None + 永远 not_recoverable）→ h/k FAIL

## 自验
REF 13/13 PASS ✓；3 negs 全 FAIL ✓；3-seed 确定性 ✓。

## distinct
vs 现有 B cases（TieJitterIncGen/DualRatePwlClockGen/TrimSkewIncrement/DelvtoNetlistModifier/C2cCornerAmplifierAudit/PvtMt0ThreeLevelAggregate/LatchResetFomSweep/ResCornerTempSweep/DutyMidvalMeasRewrite/LatchFomSweepFineSim/JitterDutyBlockPwlGen/SigmaDcSweepAudit/StrongarmBaselineAnalyze/PVTalterChar/PvtConfigDeckGen/CharRemovalAbort/SharedLibDeployFix/DutyOffsetAlertMax/QuadClkSkewMeasDeckGen/PigzResolverProduce/OcsaTr0/MissingRef/Pumpcore/CompressNetlist/NetlistStructDiff/MeasTranSamplerGen/Mt0MetastabAudit/MosToxeClassify 等）— 无 .probe 语句覆盖分析类，机制完全不同 ✓。
