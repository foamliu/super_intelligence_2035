# Deep-read: 1793328999007_61zln — DRAM CSL-BL 耦合电容抽取与校验

- **session**: `1793328999007_61zln` (rongtaoy @ hfeg0pkn001 / 10.129.2.10)
- **mc**: 76 (keywords: pex:137; netlist:8; schematic:2; rtl:2; aether:2; ...)
- **shard**: D (analog_context — DRAM 模拟域 CSL↔BL 耦合电容分析)
- **claim round**: r545 (2026-11-12)
- **case id**: `EDA-Eval-DesignFlow-CslBlCouplingExtract-001`

## 真实任务摘要

用户（rongtaoy/"zl"）负责 DRAM csl2bl coupling 的抓取，工作区
`/home/rongtaoy/Documents/workspace/csl2bl_coupling`。数据来源是
`sacap_0922.pl`（StarRC PEX 提参后处理脚本）输出的 detail CSV
（如 `0930BK_PCSnearLSA.csv`、`0921BK.csv`、`drgqa_REVC.csv`）。
用户的核心请求链：

1. 交接稿：sacap detail CSV → CSL-BL coupling 后处理脚本（解析稀疏边表 +
   每 block 汇总 + 5 张分布图），`parse_net1()` 是"靠猜"的识别函数。
2. **校验 `0921BK.csv` 里每个 `Cslin<*>` 以及 total 值是否正确**（逐条对账 SPF 原始 C 线）。
3. **检查 `extract_csl_edges.py` 抽出来的 `csl_edges.csv` 是否准确**。
4. 审核 drgqa 方法的 `drgqa_REVC.csv`，重点看 **BL2000-2500 / csl500-700 突降**原因。

## 关键技术事实（从会话与金标脚本 `sacap_csl_postproc.py` / `final_dir/extract_csl_edges.py` 提取）

### detail CSV 格式（宽表）
- 整份文件**只有 1 个** detail 表头 `Net1,Net2,Cap(fF),,,...`（约第 28 行）；
  4416 个 block 靠**每块末尾的 `total_BL2BL` 行**分隔（不是每 block 一个表头 ——
  交接稿按"每 block 一个表头"分割会把全部当成一个 block，这是 B1 必修 bug）。
- 每个 data row 是**宽表**：6 组 × 5 列 = 30 列 + 尾部 noise 列。
  每组 = `(Net1, Net2, Cap(fF), G, blank)`。
  6 个槽位顺序固定：`Bl_b, Bl_a, SaBl_b, SaBl_a, Bl_local_b, Bl_local_a`。
  **Net1（BL 侧网名）在一个 block 内 carry-forward**：只在每组首行打印，后续行留空。
- Net2 = `Cslin<m>`（绝对编号；组0 用 0–3，组15 用 1100–1103）。

### parse_net1(net1) → (net_type, polarity, group_guess) 或 (None,None,None)
- `Bl_local`：`Bl[ab]_local<\d+>$`
- `SaBl`：`SaBl[ab]<\d+>$`
- `Bl(cn)`：`(?:^|\.)cn(\d+)bl([ab])<(\d+)>$` → group_guess = cn*256+n+(320 if cn>=8 else 0)
- `Bl(cec)`：`(?:^|\.)cec(\d+)bl([ab])<(\d+)>$` → group_guess = cec*256+n+2048
- 其余 → unrecognized（--verify 必须为 0）

### drgqa 突降根因（关键工程洞察）
`drgqa_REVC.csv` 的 BL2000-2500 / csl500-700 "突降"**不是物理现象**，而是
`extract_csl_edges.py` 的 `parse_net1()` 只认 `cn\d+bl[ab]` 和 `cec\d+bl[ab]`，
**不认** drgqa 阵列的 `ce00blb` / `cc00bla` / `cn07pblb` / `ce00pblb` 等变体顶层 BL 网，
把整片中区的边（3402 条）当 unrecognized 丢弃 → 看起来"突降"。
**修复**：在 parse_net1 增加通用分支
`(?:cn|ce|cc|cec)[a-z0-9]*bl([ab])<(\d+)>$`，修复后 51578 条边、unrecognized=0。

### 输出 csl_edges.csv schema（11 列）
`block_idx, net_type, polarity, net1, cslin_id, cap_fF, local_anchor, offset, rank_in_net, sum_in_net, share_in_net`
- `local_anchor` = 该 (block, net_type, polarity) 内 min(cslin_id)
- `offset` = cslin_id - local_anchor
- `rank_in_net` = 按 cap_fF 降序的 rank（method='min'）
- `sum_in_net` = 该 (block,net_type,polarity) 内 cap_fF 之和
- `share_in_net` = cap_fF / sum_in_net

### verify() 输出
`[VERIFY] blocks=N`、`total CSL edges=N`、`unrecognized net1 unique=N`、
group_guess 单调性、每 (net_type,polarity) 边数/block 覆盖/offset 分位、dump 前 N block。
无边时 `print("[ERROR] ..."); sys.exit(2)`。

### CLI
`python3 sacap_csl_postproc.py <csv> -o <outdir> [--verify] [--dump N]`
`--verify` 只校验不画图/不写 CSV；非 verify 模式写 csl_edges.csv / csl_summary.csv + 图。

## 合成设计（L1）

- **A（prompt）**：描述宽表格式、单表头+total_BL2BL 分块、6 组×5 列、Net1 carry-forward、
  parse_net1 规则（**要求识别 cn/ce/cc/cec 多前缀 + 中间字母变体**，即包含 drgqa 修复）、
  11 列输出 schema、--verify 模式、错误处理。不给具体数值。
- **B（hidden mock_B.csv，不在 SUT 沙盒）**：6 个 block，cn 前缀 BL 网，已知 fF 值。
- **C（check.py 内嵌 mock_C）**：4 个 block，**ce/cc/cn07p 变体** BL 网，已知 fF 值 ——
  测 parse_net1 泛化（naive cn-only 正则会漏抽 → unrecognized>0 / 边数不足）。
- **check.py**：~15 条断言（静态 4 + 动态 B 8 + 动态 C 2 + 负面/§4.9/3-seed）。
