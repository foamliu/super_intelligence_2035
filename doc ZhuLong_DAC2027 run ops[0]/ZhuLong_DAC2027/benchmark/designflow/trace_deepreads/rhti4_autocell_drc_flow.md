# 深读笔记 · rhti4 · AutoCell 标准 cell DRC 流（calibre VCO 旁路 + per-cell TCL 生成 + DRC 结果解析）

- **trace_source**: user=miccao, host=hfeg0pkn003, session_file=1789958710444_rhti4.messages.json, match_count=266, domain=schematic_netlist
- **真实任务（用户原话）**：U#0（经 autocell-tcl-flow-generator skill 调用）"Generate GDS from netlist /home/miccao/autocell/ddcpc/netlist/.../blcnand2PF47x1.cdl using cell constraints ... iterate DRC ... per-cell log"；U#1「继续」；U#2「检查当前环境的calibre是否可以正常调用」；U#3「hello」。
- **对话流**：177 msgs / 4 user turns。assistant 工具链：list_allowed_files×多 / read_files×多 / editor×多（写脚本到策略可写区 /home/miccao/.cline/scripts/data/）/ run_approved_command×多（shell-runner / python-runner）。
- **关键技术发现（真实产物）**：
  1. 现有 flow `/home/miccao/autocell/black/blcnand2PF47x1_flow/run.tcl` 的外部 DRC 引擎是 `nano_verify + nanov.drc`，在本机段错误（缺 GLIBCXX_3.4.26..3.4.31）→ compaction 6 次外部 DRC 迭代无效。
  2. **修复 1**：`prep_gds_drc.sh` 用 sed 把 `set_external_engine -drc_bin nano_verify -drc_deck .../nanov.drc` 换成 `set_external_engine -drc_bin calibre -drc_deck /apps/imctf/cad/runset/decqa/v0/current/calibreDRC.rule`（按 cell_constraints_template 的 drc_engine 指定）。
  3. **修复 2（核心）**：calibre 在 RHEL8 上 `MGC_VCO=aok`，但安装树是 `aoi`（RHEL6/7 build）→ calibre 报 VCO 不匹配。`calibre_vco` 脚本头部注释明确 `USE_CALIBRE_VCO` 环境变量可强制指定 VCO → `export USE_CALIBRE_VCO=aoi` 成功旁路，calibre v2020.1_36.18 正常运行。
  4. **per-cell DRC/LVS 任务框架**：镜像 g5_ddcpc task framework，`mk_cell_tasks.py` 为每个 cell 生成 `drc.tcl`（`run_drc -gds_files ... -top_cells ... -drc_bin calibre -drc_deck ... -work_dir <result>`）和 `lvs.tcl`（`set env(MGC_HOME) ...; run_lvs -cell_name ... -gds_file ... -lvs_bin calibre -lvs_deck ... -work_dir ... -spice .../flat.cdl -no_wait -timeout 60 -flatten`）。
  5. **runner** `run_cell_drc.sh`：导出 `USE_CALIBRE_VCO=aoi` + license + MGC_HOME，调 `<autocell> <drc.tcl> --output <task_dir> --log_file <task_dir>/drc.tcl.log --msg_level 3`，再调 `parse_drc.py <result_dir> <cell>`。
  6. **DRC 结果解析** `parse_drc.py`：从 work_dir 读 `drc.log`（`TOTAL RESULTS GENERATED = N` 取总数）+ `<cell>.SUM`（`RULECHECKS` 段下 `<rule> TOTAL Result Count = N` 取每规则计数）+ `<cell>.OUT`（ASCII results db 兜底规则名），产 JSON `{cell, total, rules:{name:count}}`，exit 2=有违规 / 0=干净。
- **金标准**：trace 末态——calibre 真实跑通（VCO 旁路生效）、per-cell drc.tcl/lvs.tcl 已生成、GDS 输出到 gds_drc、parse_drc.py 解析 DRC 结果为结构化 JSON（目录后被外部清空，但生成机制完整确立）。
- **合成方向（B 档 synthesized L1）**：把「per-cell TCL 生成 + runner（含 VCO 旁路）+ DRC 结果解析」抽成 spec 驱动的 `autocell_drc_flow.py`：读 spec{cell,gds,drc_deck,lvs_deck,mgc_home,kit,spice,autocell_bin,license,drc_task_dir,drc_result_dir,lvs_task_dir,lvs_result_dir} + fixture（drc.log/<cell>.SUM/<cell>.OUT），产 `drc.tcl`/`lvs.tcl`/`run_cell_drc.sh`/`drc_report.json`。check.py 在隐藏 B/B2 上 subprocess 跑候选脚本，验 16 条件（TCL 结构 + 各 flag 对齐 spec_B + USE_CALIBRE_VCO=aoi + autocell 调用 + parse 调用 + drc_report 重解析对账 + B2 抗硬编码）。
- **断言清单对账**：16 条断言（a-p），与 check.py 16 个独立可 FAIL 条件一一对应。
