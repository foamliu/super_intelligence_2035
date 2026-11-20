# 深读笔记 — sid 1788162599553_9fg5t (e0014566 / hfeg0plg58, mc=570)

- **session**: `/home/e0014566/.cline/data/sessions/1788162599553_9fg5t.messages.json` (3.7MB, 824 msgs, 14 real `<user_input mode="act">` 轮)
- **tools 主导** (从 summary.tsv): calibre(494) / virtuoso(334) / dbGet(71) / cellview(66) / pyAether(36) / dbCreateInst(30) / netlist(23) / SKILL(18) / schematic(14) → 域 = layout_virtuoso（真跑 Virtuoso SKILL `dbOpenCellViewByType` 打开 OA cellview 查询 instances）
- **库/cell**: `auto_austin_case1 / Array16G_T_rscalc / layout` (layout.oa 4.5MB)，源 cell `Array16G_T`

## A-档 seed（UI#0, idx=0，逐字原文）
> 先帮忙看下Array16G_T_rscalc 上的autovia instance 和 powerfill instance 删除干净了吗？是不是还有留存

- **纯需求**：用户只提目标（验证删除干净与否、有无残留），未给根因或修复方案 → 合格 A-档 seed（§A ②）。
- 后续 UI#33 "OK" = 接受验证报告（idx=32 的分类结论）；idx=34-40 agent 主动删除残留 I9，超出原 ask（删除非用户首轮要求）。
- **gold = idx=32 的分类报告**（用户接受点）：32 个顶层 instance，按 master 命名分类
  - AUTOVIA via-cell（master 含大写 `_VIA`）: **0** ✅ 删干净
  - POWERFILL（master 含 `_auto_pgfill`）: **1** ⚠️ 残留 `I9` → `zlib/Array16G_T_auto_pgfill`
  - Merged-via（`_via<N>`）: 0；Merged-opt（`_opt<N>`）: 0
  - 与原始 `Array16G_T` 对比：原始有 4 个 `_VIA` instance（`Array16G_T_V4V3V2V1_20250716_vss_VIA` / `_vcc_VIA` / `Array16G_T_20250711_VIA_TOP` / `Array16G_T_20250728_VIA_TOP`），rscalc 中全部已删；powerfill `Array16G_T_auto_pgfill` 原始也有，rscalc 中残留 1 个（I9）。

## 关键分类规则（从 trace idx=29/31 + autovia/powerfill SKILL.md 提炼）
1. **autovia via-cell**：master cell 含**大写** `_VIA` token（`<top>_V4V3V2V1_<date>_<net>_VIA`、`<top>_VIA_TOP`）。case-sensitive：小写 `_via` 不算。
2. **powerfill**：master cell 含 `_auto_pgfill`（PowerFill marker cell `<top>_auto_pgfill`，由 `run_powerfill_nogui.il` `dbCreateInst(dstCV fillMasterCV strmInTopCell ...)` 创建，instName = `<top>_auto_pgfill`）。
3. **merged_via**：master cell 以 `_via<N>` 结尾（AutoVia merged output cell `<top>_via1`）。
4. **merged_opt**：master cell 以 `_opt<N>` 结尾（PowerFill merged output cell `<top>_opt1`）。
5. **normal**：其余。**关键精度陷阱**：`Array2GRTop_Core_power_via` / `Array2GLTop_Core_power_via` 含**小写** `_via` 且**无尾随数字** → 是原始设计 power-via cell，**非** autovia 残留。同理 `_opt` 无数字、`pgfill` 无 `_auto_` 前缀 → normal。

## 真实 instance 列表（idx=31 完整 32 条，A 输入）
见 `assets/EDA-Eval-DesignFlow-AutoViaPFAudit-001/instances_A.json`（逐条 instName | masterLib/masterCell，从 trace print_log 抄录）。残留：仅 `I9 → zlib/Array16G_T_auto_pgfill`（powerfill）。

## 合成（A-档 faithful + L1-boundary）
- 真 L2（打开 OA + Virtuoso）不可在沙盒复现（4.5MB OA + Virtuoso license）。取 L1-boundary：把 trace 的「dbGet instance 列表」作为输入 JSON，gold = Python 分类器 `autovia_pf_auditor.py` 复刻上述 5 类规则 + 报告。
- **A 输入** = 上述真实 32 条（SUT 可见）；**hidden B** = `BCenterCA_rscalc`（17 insts，2 autovia `_VIA` + 1 merged_via `_via1` + 0 powerfill + 干扰项：lowercase `_via` 无数字 / `_opt` 无数字 / `pgfill` 无 `_auto_` 前缀）。B 与 A 规模/取值/结构全不同（§4.1 ✓）。
- **判分**：check.py 只跑 B，subprocess 真跑候选脚本，17 条独立断言（k=17），负样本 4 个 + §4.9 三假提交全 FAIL。

## 与既有 case 区别
- `AutoViaGen-001`（layout_virtuoso）= **生成** autovia config 生成器；本案 = **审计删除残留**（验证 / 分类 / flag），主题独立。
- `PowerFill-001`（physical_verify）= GDS 审计（top cell / 层表 / bbox / power net 发现）；本案 = instance 列表按 master 命名分类找残留，对象/粒度不同。
- `ListInstCV-001`（layout_aether）= 通用 instance 列出工具；本案 = 针对性残留分类 + 精度规则（case-sensitive `_VIA` vs `_via`、尾随数字），判分断言完全不同。

## 踩坑
- trace 文件 3.7MB > 2MB，但 824 msgs 可逐段读；首轮（UI#0→idx=32）即闭环，无需全读。
- 分类必须 case-sensitive：lowercase `_via` 是原始设计 cell，只有大写 `_VIA` 或 `_via<digit>+$` 才是残留。
