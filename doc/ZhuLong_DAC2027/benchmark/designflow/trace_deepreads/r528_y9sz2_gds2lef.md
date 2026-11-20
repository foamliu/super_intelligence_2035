# r528 deepread — 1794299476374_y9sz2 (michael1l @ hfeg0pkn004, mc=421, layout_aether)

## 选料路径
- r528 fresh-pool peek（scan ssh_eda_search_20261113_131349，mc≥10，shard C keywords 过滤，C-dominant 筛选 pv+lay > analog）。
- 跨 mc 段采样 4 候选 peek USER#0：
  - **l4tre**（xinqiaoz mc575 pdk/drc/calibre/lvs）USER#0="确定 genReleaseNote 脚本的最终权威版本..." = release-note 脚本 code-review → **REJECT**（review/maintain 非 produce）
  - **qvnvw**（xxchen mc427 drc/.gds）USER#0="阅读AGENTS.md 阅读PROJECT.md" = 仅 orientation → 跳过
  - **zyqoe**（gabrielh mc413 drc/pdk/lvs）USER#0="不要对文件做任何改动只读取...给出详细分析与介绍" = read-only analysis → **REJECT**
  - **bih9j**（thomasz mc99 drc/analog）USER#0="跑出来的IR结果里没有vcc和vblh...是怎么回事" = EM/IR diagnosis Q&A → **REJECT**
  - **y9sz2**（michael1l mc421 aether:3187;pyaether:1767）USER#0="能帮我抽lef吗 我给你gds" = **LEF 抽取 produce-task** ✓ → 选定

## trace 实情（8781 lines / 1.2MB / 358 msgs / 6 user turns）
- USER#0「能帮我抽lef吗 我给你gds」→ USER#2/3「继续」→ USER#4「skipper里的genlef在哪打开」→ USER#5 给 techfile.tf + gds.map 路径 → USER#6 报错 Subcircuit "HDTIP CXN4S1P1024..." not found 问原因。
- assistant 工具链：editor×70 / run_approved_command×67 / read_files×18 / RAG_search_apis×11 / list_allowed_files×8 / SandBox_run_code×1。
- 主产物 gds2lef.py（pyAether）：ae.emyInitAether("-ADV") → ae.dbCreateLib → ae.aeImportStream(file/lib/topCell/renameMode=Overwrite/logFile) → (导出 LEF)。
- 大量 turn 在配 pyAether 运行环境（LD_LIBRARY_PATH / PYTHONPATH / PYTHONHOME / AETHER_ROOT 冲突，python-runner profile），多版 run_gds2lef_v2/v3.sh。
- **结局**：pyAether license expired + segfault；ski-genlef 报 "not a TCL script"；最后 USER#6 报 ski-genlef 找不到 subcircuit HDTIP，assistant 诊断为 GDS 缺下层子单元（memory top cell 引用的 bitcell/decoder/sense amp 未包含/未 flatten）。
- 真实 LEF 产物**未成功生成**（trace 是 env-debug + 诊断，非 clean produce 闭环）；但任务本身是 genuine LEF 抽取 produce-task。

## 合成决策（B档 synthesized）
- trace gold 依赖 pyAether（live license），SUT 沙箱不可靠（与 r526 JsonGdsDrcPipe-001 同判断：Calibre/Aether binary 不可靠 → 纯 Python 实现）。
- 沿 r526 proven 模式：合成 GDSII（纯 Python writer）+ 纯 Python GDS→LEF converter + 结构化 LEF 校验。
- 方向互补：r526 = JSON→GDS→DRC（写 GDS + 几何 DRC）；本案 = GDS→LEF（**读** GDSII 二进制 + 写 LEF abstract），测试 GDSII 解析 + LEF 格式知识。

## case 设计（EDA-Eval-DesignFlow-Gds2Lef-001, layout_aether L2-boundary, k=14 a-n）
- **A（可见）**：cells.gds 2 cell（NAND2X1/INVX1）+ gds.map（88:0 M1 metal / 88:2 M1 pin）。GDSII 含 BOUNDARY（金属矩形，闭合 5 点）+ TEXT（pin 标签 + 1 XY 点）。
- **B（隐藏）**：cells_B.gds 3 cell（Buf8x/MUX2x/FLOP4x，不同名不同几何）+ 同 gds.map。check() 只跑 B。
- candidate `gds2lef.py <gds> <map> <out.lef>`：解析 GDSII 记录 → 按 gds.map 分 metal/pin → 每 cell 输出 MACRO（CLASS CORE / SIZE 包围盒 / PIN DIRECTION-by-name + PORT RECT / OBS metal RECT / FOREIGN / ORIGIN）。
- **14 条件 a-n**：a zip 含 gds2lef.py / b 无参退出非0 / c B 运行产非空 .lef / d VERSION / e UNITS+DATABASE MICRONS / f 三 B cell 名全到 / g SIZE 匹配包围盒(容差0.01) / h PIN 集合 / i DIRECTION∈{INPUT,OUTPUT,INOUT} / j PORT LAYER+RECT / k OBS M1+RECT / l 确定性两次 sha256 / m 防硬编码 A 名不漏入 B / n CLASS CORE。
- **自验**：GOLD PASS 14/14✓；negative_selftest 5 fakes NEG_RC=0 ALL-FAIL（empty→b / print_expected→f / core_deleted→g / naive_hardcode→g / always_pass→d）✓；§4.9 (a)empty→b (b)print_expected→f (c)core_deleted→g 全 FAIL✓；k_rationale==k_check==14≥8✓。
- **防硬编码**：A cell 名 NAND2X1/INVX1，B cell 名 Buf8x/MUX2x/FLOP4x，几何/sizes 全不同；cond m 断言 A 名在 B 输出中不出现。

## 资产
- assets/EDA-Eval-DesignFlow-Gds2Lef-001/patterns/{cells.gds, gds.map} + task_brief.md
- assets/.../hidden/{cells_B.gds, gds.map, hidden_manifest.json}
- reference/.../{check.py, gds2lef.py(gold), negative/×5, negative_selftest.py}

## trace_source
michael1l / hfeg0pkn004 / 1794299476374_y9sz2 / mc=421 / real_task_summary = GDS→LEF 抽取（pyAether/ski-genlef 路径失败 → 诊断 missing subcircuit；合成纯 Python GDSII parser+LEF writer 保真抽取意图）。
