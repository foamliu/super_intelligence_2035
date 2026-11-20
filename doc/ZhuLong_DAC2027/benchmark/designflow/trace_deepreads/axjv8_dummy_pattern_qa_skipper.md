# axjv8 — Dummy Pattern QA via Skipper (deepread note)

- **trace**: `1792149907675_axjv8.messages.json`, user `xinqiaoz`, host `hfeg0pkn004` (10.129.2.10), match_count 520, cwd `/home/xinqiaoz/PDK_QA/pdkQaSystem`, model glm-5.3-flash, status completed exit 0, 2026-10-16..10-19.
- **规模**: 262 msgs (143 user / 119 assistant), 140 tool_use = 68 editor + 49 run_approved_command + 16 read_files + 4 search_codebase + 2 list_allowed_files + 1 get_agent_policy_status。3 substantive user msgs（其余 continue）。
- **真实任务（user 原话）**:
  1. "做 dummy qa，给你一个 gds，让你测量某一层 dummy 生成的情况。量测长宽，间距，和 target layer 的距离。拿 /home/pdk/xinqiaoz/01_dummy/DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/QA/ 中的 gds 测试。"
  2. "把所有经验总结成一份文档，怎么通过一份跑完 dummy 的 gds 测量 gds 是否符合 guideline 需求？"
  3. "经验应单独增加一个文件总结，git 回退重写。"
- **agent 流程**:
  1. 读项目规则 / ssh profile / testing-sop / Dummy QA 背景 / skipper 集成代码（`ski-flashlvl`/`getGdsInfo`，可取 topcell/layers/bbox，支持 XOR diff+merge）。
  2. 探测目标目录：`/home/pdk/xinqiaoz/01_dummy/DYT4E_WHCFP_LHCRP_DHCFP/v0d5_rev01/frame/QA/` 存在，含每层独立 dummy GDS（D1B/D2P/D4P/D8P/DLP/HLP/HSP/LHP/**LM1**/**LTM**）+ 汇总 `QA_chip_dummy.gds`(40MB) + 原始 `QA_chip.gds` + `QA_chip.calibre.db` + `QA_chip.drc.summary`(25KB) + `_calibreDummy_frame.rule_`。
  3. **skipper GUI 崩**（缺 xterm + libfontconfig 符号错误）→ 改用 `skipper <tcl> -noterm` 批处理（IMCP 标准用法 `dbImport`/`dbLibExport`/`dbIPMerge`）。
  4. 写 `probe_info.tcl`：`dbImport QA_chip.gds` → `dbLibTopCell` → `dbLibSummary -lpps`，提出 topcell + layer/purpose。在 hfeg0pfn108 上 xvfb-run 跑通。
  5. 读 frame `config.ini`（7 组 layers/minSpace + bordSize 1500×500 + precision 10000 + outGds=QA_chip.gds + topcell=QA_chip + bordLayer 312_0）。
  6. QA_chip.gds 含主图形/target 层；QA_chip_dummy.gds 含 dummy 层（datatype 8）。
  7. U[1] 要求把经验总结成文档（ guideline 合规自检方法）。
- **.75 Skipper 沙盒实测**（经 eda_flow run_code host=skipper / run_commands）：
  - 二进制 `/apps/empyrean/tools/skipper/bin/skipper`，批处理 `skipper <tcl> <gds_abs> -noterm` 退出 0，license SKI_EDITOR。
  - **可用 API**：`dbImport <abs_path>`（必须绝对路径，相对路径 file open failed）、`dbLibTopCell $h`、`dbLibSummary -lib $h`（返回完整摘要串：Skipper Version / File Size / Format GDSII / Precision / MaxLevel / CellNum / Lpp Statistics 层表 / `ID Cells BBox without Text` 行含 `(xl, yl, xh, yh)` 单位 um）、`dbLibSummary -lib $h -lpps`（只层表）。
  - **不存在 API**：`dbLibBBox`/`dbLibCells`/`dbLayerCount`/`dbLibObjs`/`dbLibDump`（均 invalid command name）。
  - 加载时自动往 stdout 打 SUMMARY（total rect/polygon/path/text/inst/obj），但**不在** dbLibSummary 返回值里。
- **真实 GDS ground truth**（从 hfeg0pkn004 scp 到 .75 实测）：
  - `LM1.gds`（138776B）：topcell `QA_chip_CMP_LM1`，单层 `352_8`，bbox `(2, 1.75, 1498.25, 498.25)` → W×H 1496.25×496.5，14 rect/99 poly/113 obj。
  - `LTM.gds`（142328B）：topcell `QA_chip_CMP_LTM`，单层 `372_8`，bbox `(1.75, 1.75, 1498, 498.25)` → W×H 1496.25×496.5，14 rect/105 poly/119 obj。
  - A/B 同 W×H 但 topcell/层/filesize/bbox 原点不同 → 跨输入判别可用。
- **config.ini**：layers1..7（88/570/352+372/412+173/854/394/415+417+421+427+171），minSpace 0.254/0.9/1.5/3/6/1/3，bordSize 1500 500，precision 10000，bordLayer 312_0。
- **calibreDummy.rule**（150 行）+ `_calibreDummy_frame.rule_`（27 行，Calibre DRC rule header，INCLUDE calibreDummy.rule）。
- **case 抽取**：`EDA-Eval-DesignFlow-DummyMeas-001`（physical_verify 扩量#3，L2 真跑 Skipper）。deliverable=dummy_audit.tcl（dbImport+dbLibSummary 解析 14 字段 AUDIT 行）。A=LM1.gds+guideline_A，隐藏 B=LTM.gds+guideline_B（层/bbox/filesize 全不同）。check.py 13 条件 a-m（subprocess 真跑 skipper + 跨输入 guard + 3-seed）。ref 13/13 PASS + §4.9 三假 FAIL + 2 naive FAIL + negative_selftest ALL-OK（均在 .75 实跑验证）。
- **关键坑**：run_approved_command 工具只接 `profile` 字段，真实命令写进 `.tmp/SHELL_CMD_AGENT.txt`（editor）再由 profile 执行；summary.tsv 里 $4 带 `.messages.json` 后缀，台账 awk 排除正则必须先 `sub` 剥后缀。
