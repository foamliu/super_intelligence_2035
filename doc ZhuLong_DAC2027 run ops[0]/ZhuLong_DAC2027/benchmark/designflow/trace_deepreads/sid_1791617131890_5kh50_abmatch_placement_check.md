# Deepread — sid 1791617131890_5kh50 (ziyuny @ hfeg0pkn002, layout_aether)

- **trace**: `1791617131890_5kh50.messages.json` (542KB, 143 msgs); markers: 2776 dbShape, 755 pyAether, 528 schematic, 228 dbGet, 86 cellview, 53 netlist, 28 "lang":pyAether, 15 calibre, 2 "lang":skill. mc=3890.
- **真实意图**:
  - USER#0 (idx0) = "Context summary" 续接笔记：VwlpRefAmpIP 原理图标注 vs 版图 AB 匹配检查；phase5.json(schematic 42 inst+75 text+39 annotation boxes; layout 58 inst+44 text+47 boxes)；比对脚本只吃 phase5.json 不需 pyAether。
  - USER#2 (idx7, **A-档 seed 逐字**)：`再添加以下几个检查项 1 是否share AA 2 采用哪种匹配方式 3 mos管是step还是mirror的方式 4 source/drain的metal width,以及CT孔个数` —— 提出目标，未给根因/修复 → 合格 A-档 seed。
  - USER#3-8：continue / 续接 / 总结请求 → hint 不进 prompt。
- **assistant 工具链**: editor(写脚本) + run_approved_command(跑 pythone/pyAether) + read_files + SandBox_MCP_Server__run_code。
  - `final_check2.py`：读 phase5.json layout，按 master 后缀分组(ptk_lv/ntk_lv/ntn_m)，按行 y 排序 unit，用 letter_map 映射成字母序列，与草图 top/bot 比对 + text label 中心对位 → **PASS**（三组两行草图/实例/版图字母三方一致 OABABO/OBABAO 等）。
  - 4 新增检查需深入 pcell master 图形层(AA/PG.NCH/PCH/PC=CT/M1)：`probe6.py` 解层名 + `device_match_phase6.py` 提 per-unit AA 范围/每节点 CT 数/M1 宽度 + 顶层 M1 连通性追踪判 step/mirror。
- **gold 可达性**: 4 新增检查 gold 依赖 live pyAether + live OA layout `/proj/train/ddgoa_test/workdir/ziyuny/device_match_check`（在 10.129.2.11，.75 沙盒不可达）→ **A-档 disqualified (tooling/data unreachable)** → **B-档 synthesized L1-boundary**。
- **合成方案**: 把 phase5.json 结构固化为 `match_manifest.json`(groups: sketch top/bot + letter_map + rows y + units[name/xy/ort/bbox/aa_bbox/w/l/nf/sd_m1_width/ct_count] + text_labels)。候选 `ab_match_check.py` 跑 8 per-group 检查(seq_match top/bot + label_align + share_aa + match_method common_centroid/simple_pair + step_vs_mirror + sd_ct_present + unit_count_parity + dummy_endpoints) → match_check_report.json + verdict OK/HAS_ISSUES。
- **资产**: A 忠实复刻真实(pmirror 镜像对 OABABO/OBABAO + inp 输入对 OCDCDO/ODCDCO，全 OK)；hidden B 5 处植入错(pmirror bot 行 A/B 互换→seq_bot 错 + label 错位 + 匹配 unit ct_count=0；inp 非共享 AA + 破坏行间 mirror)→HAS_ISSUES；B2 全 OK 不同 device 前缀(QP/QN)/cell(VrefAmpIP_C) 击穿 hardcoded-A/always-FAIL。
- **正交性**: 与 DdgoaDeviceAudit-001(device audit) 正交 —— 本案是 AB 匹配摆放校验；与 r88 DrcPatCheckAudit / r84 FillImplantFlowAudit / r80 DRCSpecGen / r81 MVValueCmp 等 physical_verify 审计类不同域(layout_aether placement-match)。
- **check.py**: 15 条断言 a-o (k=15=k_check≥8 GATE PASS)；自验 ref PASS 15/15；5 negative(空壳/print-expected/core-deleted/always-ok/no-stepmirror) 全 FAIL @ distinct labels (a/m/f/c/h)；§4.9 三假提交(空壳+print-expected+core-deleted)全 FAIL；跨输入 B2 OK guard ✓。
