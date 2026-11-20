# Trace Deepread — r681 / miccao / 1794363187550_713t3

**Session**: `1794363187550_713t3` · **User**: `miccao` · **Host**: `10.129.32.47` · **mc**: 40
**Keywords**: `drc:263; calibre:162; lvs:48; rtl:26; aether:16; netlist:14; .gds:13; innovus:10`
**Domain**: physical_verify (calibre DRC/DFM rule deck analysis)

## User intent (原话)

- **U#0**: `/proj/shdc/cad/script` 这个路径下所有的用到的 calibre deck 里，把 DFM 命令汇总给我，我要看我们用了哪些 DFM 命令
- **U#1**: 输出成文本汇总格式，只要用了哪些命令，放到我桌面

## 对话流 (34 msgs, 2 user turns, 16 tool_uses)

| step | tool | what |
|---|---|---|
| 1 | list_allowed_files | `/proj/shdc/cad/script` → 136 疑似 calibre deck |
| 4 | read_files + search_codebase | 读 agent-policy.json；搜 `DFM`/`DFM FILL`/`DFM RULE` |
| 7 | editor → scan_calibre_decks.py | 扫描脚本：walk dir, 找 deck 文件 |
| 9 | run_approved_command | 跑扫描 → 136 个 deck |
| 11 | read_files | 抽查 3 个真实 deck (POWER_FILL/PG_DUMMY/AUTO_PC) |
| 13-25 | editor ×4 + run ×4 | find_dfm_commands.py / sample_dfm_cmds.py / group_dfm_by_cat.py，提取 DFM 前缀命令 |
| 29 | editor → Calibre_DFM_commands_汇总.txt | 最终汇总：14 个 DFM 命令 (DFM PROPERTY/COPY/SPEC/FILL/RDB/SHIFT/OR/EXPAND/JOGCLEAN/PARTITION/FUNCTION/TEXT/DP/BALANCE) |
| 31 | list_allowed_files | 确认文件落到桌面 |

## 用户接受的结果

`/home/miccao/Desktop/Calibre_DFM_commands_汇总.txt` —— 列出 14 个 DFM 命令（SVRF `DFM` 前缀）+ 各命令简要用途。

## 判分可行性 (teeth)

真实 deliverable = 文本汇总文件（在 miccao 桌面），依赖 `/proj/shdc/cad/script` 的 136 个真实 deck（SUT 不可访问）。→ **mock-behavioral reframe**：fixture = 合成 mock calibre deck 目录；candidate = 纯 stdlib `dfm_cmd_extract.py`，递归扫目录 + 剥注释 + 大小写不敏感提 DFM 命令 + 去重计数 + 结构化输出。隐藏 B 用与 A 完全不相交的 12 命令集防硬编码。②档 source-semantic-parse（deck 文本可 regex parse，但需实现剥注释 + 大小写 + 非 deck 过滤 + 递归 walk 的 rule logic，非纯 regex 模式匹配）。

## Build 产物

- `assets/EDA-Eval-DesignFlow-CalibreDfmCmdExtract-001/decks_A/` (8 deck + 3 非 deck 干扰)
- `reference/.../hidden/decks_B/` (6 deck, 12 DFM 命令, 与 A 不相交) + `decks_B2/` (退化)
- `reference/.../gold_ref.py` + `check.py` (16 条件 a-p) + 4 negatives + negative_selftest.py
- 自验: gold 16/16 PASS ✓; 4 neg 全 FAIL (first_fail a/c/b/b, 3 distinct ✓); §4.9 三假 (empty/print-A/core-del) 全 FAIL ✓; k_rationale=k_check=16≥8 GATE PASS ✓
- jsonl_C 421→422
