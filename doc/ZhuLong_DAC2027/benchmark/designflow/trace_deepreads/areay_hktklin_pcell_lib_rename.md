# Deepread: areay — Virtuoso SKILL PCell batch library rename

**Session**: `1795400314824_areay.messages.json` (dict json, 255KB / 83 msgs)
**User**: hktklin @ hfeg0pkn004 (10.129.40.214)
**mc**: 179
**Keywords**: virtuoso:234;cellview:228;ddgetobj:144;dbcreaterect:140;dbget:99;dbcreatelabel:48;...
**Domain**: layout_virtuoso (C-dominant)
**Format**: cline dict messages.json (subdir path sessions/<sid>/<sid>.messages.json)

## User intent (real task)

hktklin 在做 Virtuoso PCell 库迁移。目录
`/proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/L54/AMN3P/` 下有一批
`common_tap_*_pcell_SKILL.il` 文件，每个首行：
```
pcDefinePCell(list(ddGetObj("tap_p") "common_tap_L54_coner_pcell_SKILL" "layout") ...)
```

用户指令（同一句重复 6 次，目录文件逐步新增）：
> 文件中内容为 tap_p 的改为 lacaa_common，内容 _SKILL 删除

即：① `ddGetObj("tap_p")` → `ddGetObj("lacaa_common")`（库名重命名）；
② pcDefinePCell 里 cell 名字符串末尾的 `_SKILL` 去掉（`"foo_SKILL"` → `"foo"`）。
**文件名不变**（仍 `*_SKILL.il`），只改内容。

## Iteration history

- 最初目录 3 个 .il + readme。agent 先试 editor（被 policy.writableRoots 拒绝 /proj 路径），
  再试 run_approved_command shell-runner（需要 .sh filePath），最后用 python-runner 跑
  `fix_AMN3P_tap.py`：sed 式 replace `ddGetObj("tap_p")`→`lacaa_common` + 去掉 cell 名 `_SKILL`。
- 第 3 个文件首次未生效，agent 重跑修复。
- 后续用户重复同一指令时目录新增文件（L20_edge_V、L54_edge_lr_fin2、L54_edge_coner 等），
  agent 把脚本改成 glob 通配 `*_SKILL.il`，一次性覆盖所有新增文件。
- 最终 6 个 .il 文件全部改完，readme 不含目标内容跳过。
- 真实交付：`/ai_sandbox/.../fix_AMN3P_tap.py`（glob + replace + idempotent NO CHANGE）。

## Why good offline-synth candidate

- 纯文本/文件处理，不需要 live Virtuoso（L1 离线 Python）。
- 判分有牙：glob 通用性（B 用不同 cell 名）、幂等性、注释保留（反 naive 全局 replace）、
  文件名不重命名、预改文件不变。
- 真实 trace 溯源完整：user/host/session_file/mc/real_task_summary 齐全。

## Case produced

`EDA-Eval-DesignFlow-SkillPcellLibRename-001` (shard C, layout_virtuoso, L1).
k_rationale = k_check = 16 (≥8). ref PASS 16/16; 5 negatives 全 FAIL distinctly
(empty_shell→cond4 / print_only→cond4 / delete_core→cond8 注释腐蚀 / rename_files→cond10 /
hardcode_a→cond6 B 名不同); §4.9 (a)(b)(c) 三假全 FAIL; 3-seed 子集确定性 cond14;
hidden B 与 A 在 cell 名/文件数/预改文件/注释陷阱上全不同。
cases/C 612 → 613. ledger areay → case.
