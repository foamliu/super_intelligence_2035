# Trace deepread — o8ivt (StdcellListXtract)

- **session**: `1792552823708_o8ivt.messages.json` (yutongy / hfeg0plg53, mc28)
- **size**: 281 KB / 35 msgs / 9 user turns
- **domain**: schematic_netlist (SPICE/CDL netlist parsing)
- **source path** (trace-time, now cleaned): `/home/yutongy/vcap_commit/ddgoa/netlist` (179 MB) + `spf_std_path`
- **A-faithful 提需求轮**: MSG 0 (U#0) 逐字原文 → prompt.txt
  > @netlist 抓取这个网表中的所有stdcells_am的cell名字道义个单独的文件中，每个cell名字单独占一行，名字前面写上stdcells_am，中间用空格隔开

## 对话流（agent 行为）
- U#0 提需求（提取 stdcells_am cell 名字到单独文件，每行 `stdcells_am <名字>`）。
- agent: get_agent_policy_status + list_allowed_files `/home/yutongy/vcap_commit/ddgoa` → 发现 `netlist`(179MB) + `spf_std_path`。
- read_files netlist 头 80 行 → run_commands 被 policy 禁用（"Raw shell tool run_commands is disabled; use run_approved_command"）。
- read agent-policy.json → 发现 `python-runner` profile 可跑 `/home/yutongy/*.py`。
- editor 写 `extract_cells_inspect.py`（只读检查：file size + 前 40 行 + stdcells_am 行数 + 样本）→ run_approved_command → 输出：file size 178969596，`*WOWTOP` / `* Tool : AETHER-SE` / `.subckt switch_close` ... 头部；`stdcells_am` 行数 756。
- 进一步检查：`* Library : stdcells_am` header count=756；上下文显示 `* Library : stdcells_am` + `* Cell : invx1` + `.SUBCKT invx1 A Y inh_vbn inh_vbp inh_vcc inh_vss` + `.ENDS invx1`；无 `stdcells_am/` 实例引用（`stdcells_am/` 行数 0）。
- editor 写 `extract_stdcells_am.py`（lib_re/cell_re 正则；pending_lib 跟踪；命中 `* Library :` 设 pending，下一个 `* Cell :` 若 pending==stdcells_am 则抓取；dedup 用 seen set；保序；写 `stdcells_am <name>` 每行）→ run_approved_command → **756 cell headers, 756 unique (无重复)**，输出 `stdcells_am_cells.txt`，前 10: invx1/nor2x1/dlyg2s2_gut2/dlyg2s2_gut1/dlyg0of8s2_ut/dlyg8of8s2/dlyg6of8s2/pulsehi15gx1/invLx1/bufLx24，末 5: invBx8/or3GFx1/invLx3/invMx8/nand4PFx3_gut。
- read_files 验证输出文件 → 756 行格式正确。**用户隐含接受**（直接进入第二个任务）。

## 第二个任务（不取作 A 档 prompt，但记录）
- U#24（MSG 24）"筛选 spf_std_path 这个文件里面的路径，删掉不包含在 std_list 这个里面的 cell 路径" + attachments (spf_std_path, std_list=stdcells_am_cells.txt)。
- agent 写 `filter_spf_std_path.py`：load std_list cell 名（每行第二字段）→ 解析 spf 路径 `/cell/<名字>/<名字>.spf_RCC`（文件名去 `.spf_RCC`）→ 保留在 std_list 中的路径，原地写回 + `.orig` 备份。1794→754 保留/1040 删除。2 个 cell（invBx8, nand4PFx3_gut）在 spf 路径中无对应。验证通过，用户接受。

## 金标
- 取 U#0 提需求轮 + agent 的 `extract_stdcells_am.py` 逻辑结构（lib_re/cell_re/pending_lib/dedup/保序）。
- 真实脚本路径硬编码 → 复刻为 config-driven（读 config.json{netlist_path,output_path,stats_path,library_name}）。
- 真实 756-cell 网表已清空，按 trace 暴露的结构（AETHER-SE header / `* Library :`/`* Cell :`/`.SUBCKT`/`.ENDS`）合成 faithful netlist_A（含真实 cell 名词表 + dups + 其他库 decoy + orphan Cell 行）。

## 隐藏 B 设计
- 不同 top design（ddgoa_top_alt/ROMTOP）、不同 user、不同其他库（ddgoa_cmos_digital / io_cmos_b）。
- stdcells_am cell 名空间与 A **完全不相交**（B 用 bufx/nandx/dlyg3-9/pulselo/invS/bufS/invC/and3GF/nor4PF 模式）→ cross-guard A-only 不泄。
- 30 headers / 3 dups（bufx1 x3, nandx1 x2）→ 27 unique。
- decoy：在其他库下放同名 cell（bufx1/nandx1/invSx1）+ orphan `* Cell :` 行（decoy_orphan_b, bufx1）→ 测 pending_lib 重置 / 库作用域。
