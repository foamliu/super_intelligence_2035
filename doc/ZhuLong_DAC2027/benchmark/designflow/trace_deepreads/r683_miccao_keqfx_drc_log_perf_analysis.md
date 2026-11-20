# Deepread: miccao / 1788743635326_keqfx — DRC Log Performance Analysis

## Trace Source
- **session**: 1788743635326_keqfx
- **user**: miccao
- **host**: 10.129.32.47
- **match_count**: 623 (drc:1208; calibre:392; netlist:239; transistor:92; aether:87; schematic:46; cellview:38; .gds:34)
- **domain**: physical_verify (DRC/calibre log analysis)

## User Intent (real task summary)

用户 miccao 要求分析 Calibre DRC-H 运行日志（rundrc.log），找出耗时最长的步骤，并溯源到具体 rule。核心方法论（U#16）：

1. **整体模块时间分布**：DRC 各大模块（LICENSING、RULE COMPILATION、LAYOUT DB、DATA INPUT、DRC-H EXECUTIVE）的 REAL TIME 占比
2. **连接关系建立时间**：CONNECT 操作的累积耗时（容易被忽略的隐性大模块）
3. **图形计算时间**：提取最耗时的图形计算操作（Top-N by REAL TIME）
4. **溯源到 rule**：从最耗时操作定位到所属 DRC RuleCheck
5. **FGC/HGC 比分析**：判断是否因层次化失效导致计算量爆炸
6. **VHC/VPC 标志**：VHC=F = 放弃层次压缩（硬证据）

用户进一步要求（U#62/U#65）：
- 输出格式 = 图形操作 + 耗时 + 图形数量
- 连接关系 = 总结冗余可优化的语句
- **层次化破坏步骤单独列出**：step_name, time, HGC/FGC 前后变化

最终（U#148）：封装成 skill，结果 = log 拆解报告。

## Assistant 行为

助手 read_files 读取 rundrc.log（33 万行），用 grep/awk/sed 定向提取：
- `ELAPSED TIME =` 序列 + ΔELAPSED 差值
- `MODULE COMPLETED` 行 → 模块时间分布
- `(HIER ... HGC=.. FGC=.. VHC=.. VPC=..)` → 图形计数
- `DRC RuleCheck COMPLETED` → rule 归属
- `Cumulative CONNECT Time` → 连接关系耗时

最终创建 SKILL.md `/home/miccao/.cline/skills/calibre-drc-log-analysis/SKILL.md`（184 行），定义了完整的 log 字段参考 + 5 阶段分析方法论 + 验收标准。

## Build 决策

**mock-behavioral reframe**（承 r645-r682 家族）：
- 真实 log 33 万行不可放入 SUT 沙盒，且判分需确定性期望值
- 新子型 `drc-log-perf-analysis`，distinct vs r681=CalibreDfmCmdExtract(deck regex)/r682=DrcEnclosureRuleExtract(3-signal classify)/r678=SpfCouplingSort(DSPF sort)
- 核心差异：输入 = DRC run log（非 deck/netlist/config），操作 = time parsing + step extraction + FGC/HGC ratio + VHC/F hierarchy-loss detection + redundant connect identification
- deliverable = 纯 stdlib `drc_log_perf_analysis.py`，读 mock log → 结构化 JSON 报告

**asset A** = rundrc_A.log（4 modules, 8 ops, 3 rules, 2 hierarchy-breaking, 1 redundant connect）
**hidden B** = rundrc_B.log（3 modules, 7 ops, 3 rules, 2 hierarchy-breaking, 1 redundant connect — 全异值全异 rule）
**hidden B2** = rundrc_B2.log（degenerate: 1 module, 1 op, 1 rule, 0 hierarchy-breaking, 0 redundant）

**check() 16 条件 a-p**：见 check.py
**4 negatives**: empty_shell(a)/print_expected_A(c)/core_deleted_silent_error(b)/always_pass_stub(d) — 4 distinct first_fail ≥3 ✓
