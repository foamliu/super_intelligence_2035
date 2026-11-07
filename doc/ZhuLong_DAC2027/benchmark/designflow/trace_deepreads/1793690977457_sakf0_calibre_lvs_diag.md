# Deepread — 1793690977457_sakf0 (e0024852 @ hfeg0pkn005, mc=633, physical_verify)

## trace source
- session: 1793690977457_sakf0 (197 msgs, 956645 B)
- user: e0024852 (NEW — shard C ledger 0 prior coverage)
- host: hfeg0pkn005
- mc=633, calibre:633 + schematic:305 + netlist:29 + spectre:12 + hspice:9
- timestamp: 2026-11-05 (last update 2026-10-29T06:18Z per header, but msgs run 2026-11-05)

## 用户意图主线（user turns，逐字原文片段）

- msg#0/1: "when I run /rundata/.../SPF_378/case3_6t8_run_tailor.sh the error is TOOL_DIR wrong: /mnt/hgfs/shared_dir/Python/schematic_gen/dspf-tool (no backend/dspf under it) how to fix it"  → dspf-tool 路径修复
- msg#29: "tell me what is .../35H_1P18M_..._Test08.lvs where is M0 pitch space width" → 找 LVS rule 文件 + M0 pitch
- msg#45: "我如果想改这个文件要怎么办 我要改M0 的pitch width length 值 然后写到lvs 然后我布局布线的版图看是否满足DRC lvs" → **A 档候选意图**：改 M0 pitch/width/length → 写 lvs → 看 layout 是否过 DRC/LVS（提出需求/表达目标轮，未给根因）
- msg#51/55: "gds he cdl path is where" / "where is gds and cdl" → 找 GDS/CDL
- msg#65/67: "我的问题是我只在外部定义一些M0 M1 是合理的吗" / "lvs 与 design rule 没有关系是吗" → 概念问答
- msg#69: "when i run calibre -lvs -hier 35H_1P18M_..._Test08.lvs ... the error is CALIBRE_ATOMIC_LVHEAP=0 ... CALIBRE_HOME=/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18 ..." → **真跑 calibre -lvs -hier，DECRYPT2 报错**（user 已贴报错但未给根因 → 仍可作 A 档）
- msg#111: "LVS_Cal_V0d1_Rev06_Test08.lvs - You are recommended to run with calibre 2023.3_14 or a higher version ... HDB FOR LAYOUT PRIMARY: \"CH231_HDT_Bitcell_FS_WiPin\" WAS RESTORED FROM SVDB: svdb ... CALIBRE::HDB QUERY SERVER COMPLETED - Thu Nov 5 14:24:23 2026" → 切到 2023.3_14.8 后 query server 跑通
- msg#113/115: calibre -version 输出 `//  Calibre v2023.3_14.8    Mon Jul 3 16:56:42 PDT 2023` + WARNING discontinuation
- msg#117: "grep -i clean lvs.rep ... tail -n 40 lvs.rep" → **真实 lvs.rep 摘要**：
  ```
  Ports:              7         7
  Nets:               7         7
  Instances:          6         6         M (4 pins)
  Total Inst:         6         6
  Matched Layout/Source | Unmatched Layout/Source | Component
  Ports:    7  7  0  0
  Nets:     7  7  0  0
  Instances: 2  2  0  0  M(hdt_pd_fs)
             2  2  0  0  M(hdt_pg_fs)
             2  2  0  0  M(hdt_pu_fs)
  Total Inst: 6  6  0  0
  o Initial Correspondence Points:
     Ports:        VDD VSS WL BLB BL SB S
  ```
  → **LVS CLEAN**（全 matched, 0 unmatched）
- msg#119/121: 重跑 calibre -query_input query_cmd -query svdb CH231_HDT_Bitcell_FS_WiPin，输出含 CALIBRE_HOME=/apps/mentor/calibre/2023.3_14/aoi_cal_2023.3_14.8
- msg#130/143: 切到 GloryEX RC (gxrc -c gxrc_cci_cmd_V0d1_Rev07)，报错 `-E- (TRIO-0212) {EXT_SUBSTRATE} : the command or value is invalid.` + `-E- (TRIO-0214) Failed to parse command file`
- msg#149: sed -i 's#^EXT_SUBSTRATE.*#EXT_SUBSTRATE\tNO#' 修复后重跑
- msg#167/171: 切到 GloryEX 2026.06_P004，.lock file warning
- msg#177/187: "帮我找最新的glory 版本" / "我昨天记得有P006 的版本" → 找 GloryEX 版本（结尾主线）

## assistant 工具链（关键节点）
- msg#70: 诊断 DECRYPT2 → "Unsupported encryption version, please use a more recent version of Calibre"，规则文件 SVRFencrypt v2023.3_14.8，当前 calibre 2020.1_36 太旧
- msg#72-100: shell-runner 写 find_calibre.sh / check_calibre2023.sh / check_calibre2023_vco.sh / find_calibre_setup.sh / inspect_calibre_wrapper.sh / check_vco_env.sh / test_vco_fix.sh → 发现 /apps/mentor/calibre/2023.3_14/aoi_cal_2023.3_14.8，但 VCO=aok vs aoi 环境不匹配（沙箱里），用户自己 shell 里 module load calibre 已配好
- msg#104-110: read .bashrc → /apps/bin/.bashrc.common → module load calibre → 发现 module calibre/2023.3_14 存在 → 解决方案 `module load calibre/2023.3_14`
- msg#118: 解读 lvs.rep SUMMARY → LVS CLEAN
- msg#124: read CH252_FS/query_cmd → 解释 query_cmd 是 HDB 查询脚本（导 GDS_MAP/devtab/nl/net xref/instance xref/port table 到 CCI_DB/）
- msg#127-129: ask_question → 用户要给 CH231 生成 CCI_DB（仿 CH252）→ 给步骤 mkdir CCI_DB + cp query_cmd + run
- msg#131-133: 读 gxrc_cci_cmd_V0d1_Rev07 → 诊断 3 个错误（./output/ 不存在 + EXT_SUBSTRATE 值非法 + captab 路径）
- msg#143-171: gxrc 反复跑 + 修 + 切版本 2024.06_SP1_F001 → 2026.06_P004
- msg#177-196: 找最新 GloryEX，确认机器上无 P006，最高 2026.06_P004

## 干净 accepted artifact？
- **无单一干净 accepted artifact**：session 在反复切 GloryEX 版本中结束，用户最后问"我昨天记得有P006"被否（机器上无 P006）。
- 但中段 msg#69-118 的 **Calibre LVS 流程是完整闭环**：DECRYPT2 报错 → 切 calibre 2023.3_14.8 → 跑通 LVS → lvs.rep CLEAN。这段是真实工具产物（lvs.rep 字段、calibre -version 输出、CALIBRE_HOME 环境变量、SUMMARY 摘要、correspondence ports）。

## 合成方向（B-synthesized，grounded on real lvs.rep format）

trace 无干净 accepted artifact + 用户主线从 dspf-tool → calibre LVS → query_cmd → GloryEX RC 多次切换 → **不适用 A 档**。取 **B-synthesized grounded on 真实 Calibre LVS 报告格式**：

合成"**Calibre LVS run-log + report 解析器 → 结构化 JSON 诊断**"任务（SUT 写 `calibre_lvs_diag.py`，CLI 1 参 <lvs_run.log>，解析后输出 JSON）：
- `calibre_version`：从 `// Calibre v(\d+\.\d+_\d+\.\d+)` 抽
- `calibre_home`：从 `CALIBRE_HOME=(\S+)` 抽
- `encryption_version`：从 `Calibre SVRFencrypt v(\d+\.\d+_\d+\.\d+)` 抽
- `version_compatible`：calibre_version >= encryption_version（语义版本比较，split [._] 转 tuple int）
- `errors`：list[{code, message}]，从 `ERROR: (?:Error )?([A-Z]+\d*)\s*-?\s*([^\n]+)` 抽（DECRYPT2 等）
- `warnings`：list[str]，从 `// WARNING: ...` + `SVRF MESSAGE ...` 抽
- `layout_primary` / `source_primary`：从 `LAYOUT PRIMARY: "..."` / `SOURCE PRIMARY: "..."` 抽
- `summary`：{ports, nets, instances[], total_inst}，从 INFORMATION AND WARNINGS 块的 Matched/Unmatched 表抽
  - ports/nets/total_inst: {matched_layout, matched_source, unmatched_layout, unmatched_source}
  - instances: list[{component_type, matched_layout, matched_source, unmatched_layout, unmatched_source}]
- `correspondence_ports`：从 `Initial Correspondence Points:` 后的 `Ports: VDD VSS WL BLB BL SB S` 抽
- `query_server_completed`：bool，含 `CALIBRE::HDB QUERY SERVER COMPLETED`
- `verdict`：`error`（有 errors）> `mismatch`（summary 存在 + unmatched > 0）> `clean`（summary 存在 + unmatched == 0）> `incomplete`（无 summary 无 error）

## 资产设计（A/B/B_broken 三档击穿硬编码）

- **A（SUT 可见）**：真实 trace grounded，calibre v2023.3_14.8，cell CH231_HDT_Bitcell_FS_WiPin / source hdt_CH231_bitcell，CLEAN LVS（7/7 ports, 7/7 nets, 6/6 inst: hdt_pd_fs/hdt_pg_fs/hdt_pu_fs 各 2，correspondence VDD VSS WL BLB BL SB S），query_server_completed=true，1 SVRF MESSAGE warning
- **B（隐藏，judge 跑候选 + 反读 JSON）**：全重参数化 — calibre v2024.1_22.5，cell CH252_HDT_Bitcell_X / source hdt_CH252_bitcell，**MISMATCH** LVS（ports 7/7/1/0, nets 8/8/2/0, instances hdt_pd_x:3/hdt_pg_x:2/hdt_pu_x:2, total_inst 7/6/2/0, correspondence VCC GND WL BLB BL SB S），query_server_completed=true，1 SVRF MESSAGE warning
- **B_broken（隐藏哨兵）**：DECRYPT2 错误路径 — calibre v2020.1_36.18（太旧），encryption v2023.3_14.8，version_compatible=false，verdict=error，errors 含 DECRYPT2，无 summary，query_server_completed=false（测 A/B 都不覆盖的错误路径，杀漏判 + 杀硬编码 A/B）

## 判分设计（k=16 条 a-p，对 B 跑候选 + A 跨输入守卫 + B_broken 哨兵）

a. submit.zip 合法 zip 含 >=1 .py 生成器
b. py_compile + 仅标准库
c. B exit0 + stdout 是 JSON dict
d. JSON 12 顶层键齐全
e. B calibre_version == "2024.1_22.5"（反硬编码 A 的 2023.3_14.8）
f. B encryption_version == "2024.1_22.5" + version_compatible == true
g. B layout_primary == "CH252_HDT_Bitcell_X"（反硬编码 A 的 CH231_HDT_Bitcell_FS_WiPin）
h. B source_primary == "hdt_CH252_bitcell"（反硬编码 A）
i. B verdict == "mismatch"（反硬编码 A 的 "clean"）
j. B summary.ports == {matched_layout:7, matched_source:7, unmatched_layout:1, unmatched_source:0}（反 A 的 7/7/0/0）
k. B summary.nets == {matched_layout:8, matched_source:8, unmatched_layout:2, unmatched_source:0}（反 A 的 7/7/0/0）
l. B summary.instances == 3 条 + component_types 集合 == {hdt_pd_x, hdt_pg_x, hdt_pu_x} + matched 各 3/2/2（反 A 的 hdt_*_fs 各 2）
m. B summary.total_inst == {matched_layout:7, matched_source:6, unmatched_layout:2, unmatched_source:0}（反 A 的 6/6/0/0）
n. B correspondence_ports == ["VCC","GND","WL","BLB","BL","SB","S"]（反 A 的 VDD VSS...）
o. 跨输入守卫 A：A verdict == "clean" + A layout_primary == "CH231_HDT_Bitcell_FS_WiPin" + A summary.ports unmatched_layout == 0 + A correspondence_ports[0] == "VDD"（杀硬编码 B）
p. B_broken 哨兵：verdict == "error" + version_compatible == false + calibre_version == "2020.1_36.18" + encryption_version == "2023.3_14.8" + errors 含 DECRYPT2 + query_server_completed == false（杀漏判错误路径 + 杀硬编码 A/B）

## DISTINCT from 既有 physical_verify case

- r208 DrcUnusedVarClassify：derive-layer 变量间接使用 4 桶分类（calibre DRC report variableUnusedDrc 段）
- r172b DrcRuleCellMatch：rule→cell 5 策略匹配
- r171 DummyHeaderQaResolver：deck 头部开关 QA
- 本案首次 ground on **Calibre LVS run-log + lvs.rep SUMMARY 表结构化解析 + 版本兼容性判定（calibre vs SVRFencrypt）+ DECRYPT2/VCO 错误识别 + verdict 五档（error/mismatch/clean/incomplete）+ correspondence ports**，与 DRC variableUnused / rule-cell / header QA 互补不重叠（LVS ≠ DRC，报告格式完全不同：Matched/Unmatched 4 列表 + Initial Correspondence Points）。

## DEBT: 0
