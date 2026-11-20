# 深读笔记 — qe1n4 (Qualib STD char TCL template)

- **trace**: `1792478336435_qe1n4` · user `t0002801` · host `hfeg0plg99` · mc=212 · 947KB · keywords sim_count=88 (hspice/finesim/spectre 偶发，主体为 Qualib/library-char TCL)
- **session path**: `/home/t0002801/.cline/data/sessions/1792478336435_qe1n4/1792478336435_qe1n4.messages.json`
- **ledger**: claimed 2026-11-05 (shard B, characterization)

## 真实对话流（逐轮）

- **U0（需求轮，A 档选轮合规）** 逐字原文：
  > 帮我在本地路径下生成一份检查STD 的tcl文件，检查TT corner下 电压1.8V 温度25度。我要一个模板
  - 未给根因、未给修复方案 → A 档选轮规则合规。
  - "STD" = Standard Cells（标准单元库）；"检查STD 的tcl" = Qualib 标准单元库表征/检查 TCL 模板；"TT corner 1.8V 25度" = 工艺角 TT / 电压 1.8V / 温度 25°C；"我要一个模板" = 交付形态是可复用模板（参数化），非一次性脚本。
- **assistant 行为**：全程 **未真跑任何仿真/表征工具**。仅 `list_allowed_files` / `search_codebase` / `read_files` / `RAG_MCP_Server__search_apis` 检索上下文 + `editor`（28 次）逐段写入 TCL，`run_approved_command`/`run_commands` 偶发（用于查目录/文件，非跑 Qualib）。
- **交付物**：一份 Qualib TCL 模板文件，核心命令片段（从 mid 段取证）：
  ```tcl
  ## --- Liberty (.lib) Corner ---
  create_corner tt18_25 \
      -voltage 1.8 \
      -process tt \
      -temperature 25
  ## --- SPICE / CDL Corner ---
  create_corner tt \
      -voltage 1.8 \
      -process tt \
      -temperature 25
  ```
  - thinking 原文：「The user wants me to generate a Qualib TCL file for checking STD (Standard Cells) at TT corner, 1.8V, 25°C ... qualib tcl which is likely related to the Qualib tool (a standard cell library characterization tool)」。
  - 关键词计数（tail 200KB）：corner×240 / TT×511 / 1.8V×65 / power×70 / timing×44 / delay×15 / setup×2 / hold×3 / leakage×0。→ 模板覆盖 PVT corner 定义 + Liberty/SPICE 双 corner + timing/power arc 框架。
- **过程痛点（真实）**：assistant 用 editor 多次部分写入 → 文件结构错乱（"文件结构有些错乱" / "之前的文件结构混乱" / "文件经过太多次部分替换已经变得非常混乱了"）→ 最终改用 Python 沙箱直接生成全新文件重写。**这是 trace 的真实技术痛点：长模板的逐段 editor 写入易错，需整文件生成策略。**
- **用户接受状态**：trace 末尾未见用户明确接受/拒绝（agent 仍在重写文件）→ A 档金标准不可用 → **B 档 synthesized**（子技能忠实，金标准 .75 标定）。

## 子技能（faithful 重述）

**Corner-parameterized standard-cell library characterization TCL template generator**：给定 corner（process/voltage/temperature）+ 单元列表 + 指标集，生成一份可复用的表征检查模板（定义 corner、导入 library/model、为每个 cell 定义 timer/arc、配置 timing/power/leakage 表征任务），输出结构化模板文件 + 配置清单。

## distinct vs 已有 B characterization case

- GmidLut/NmosAgeChar/CTLEtranChar/VihTripTune/ButterflyCurve/DffSetupHoldChar/ThoxVthExtract/OtaAutoTune/TxRonSize/PVTvarSpecJudge/RcurrDirClassify/SizingSensDiag/NocalOffsetDeck/WvFmFreqExtract… 全为**单 cell/单电路的指标测量或 spec 合规判定**（一次性脚本，跑 sim 得数）。
- 本条 = **库级表征模板生成器**：(a) 多 cell 覆盖（inv/nand/nor/buf 同模板）、(b) corner 参数化（TT/SS/FF × V × T 可切换）、(c) 多指标框架（tpd/tr/tf/Icc_avg/Ileak）、(d) 交付是**可复用模板**而非一次性行数值。
- 与 PVTvarSpecJudge/InvPVTchar 的区别：那些是**在给定 PVT corner 上跑测得数值再判 variation 合规**；本条是**生成表征模板本身**（模板是产物，corner 是输入参数），且面向**库（多 cell）**而非单 cell。
- distinct ✓（shard B 首个「library-char template generator」case）。

## 便携 reframe（关键）

- trace 原走 **Empyrean Qualib TCL**（Aether/Alps 库表征工具），`.75` 无 Qualib、无 Aether-Tcl headless 链路 → **不可直接移植**。
- 保留「corner-parameterized std-cell library char template」子技能，介质从 Qualib TCL 改为 **HSPICE .sp deck**（`.75` HSPICE V-2023.12-SP1-1 已验证可用，level-1 Shichman-Hodges，见 InvTripDelay/NocalOffsetDeck/RcurrDirClassify 等先例）：
  - 候选 `std_char_tmpl_gen_ref.py`（CLI `<lib_def.json> <corner.json> <out_dir>`）：
    1. 从 `lib_def.json` 读 cell 列表（inv/nand2/nor2/buf）+ 每-cell sizing + 负载/翻转点；
    2. 从 `corner.json` 读 process(Vto/kp 缩放)/voltage/temperature（name-agnostic）；
    3. **生成**参数化 .sp 模板（.model + 每-cell testbench + .tran + .measure tpd/tr/tf/icc_avg/ileak）→ `char_template.sp`；
    4. **subprocess 真跑** HSPICE → 解析 .lis/.mt0 → 每-cell 多指标数值；
    5. 落 `library_char_report.json`（per-cell × per-metric 矩阵 + corner 标签 + template_path + sim_log）。
  - 关键：交付物含 (1) 可复用模板文件 `char_template.sp`（反 hardcode-one-cell）+ (2) 真跑 sim 得库级报告（L2 牙）。

## A/B 设计（便携，.75 HSPICE 标定）

- **A**（visible）：corner TT / vdd=1.8 / T=25 / cells = {inv_a, nand2_a} / sizing(Wn=1u,Wp=2u,L=180n) / cl=5f / 指标 tpd/tr/tf/icc_avg。→ 得 inv_a tpd≈? nand2_a tpd≈?
- **B**（hidden）：corner SS / vdd=1.5 / T=85 / cells = {inv_b, nor2_b, buf_b} / sizing(Wn=1.5u,Wp=3u,L=150n, 不同模型名 nchb/pchb) / cl=8f / 指标同 + ileak。→ 数值/命名/结构/corner 全不同。
- 跨输入守卫：cell 名、corner 名、vdd、模型名、指标数值全不同 → 防 hardcode_a；B 多一个 cell + ileak → 防忽略输入。

## check.py ≥14 条 a-n 蓝图（next round 落地）

(a) zip 含 `std_char_tmpl_gen.py` + `char_template.sp` + `library_char_report.json`
(b) py_compile
(c) subprocess 真跑 HSPICE（sim_log 含 `job concluded` + .mt0 存在，反 naive_no_rerun/naive_print_expected）
(d) `char_template.sp` 含 ≥2 cell testbench（反 naive_single_cell/one-off）
(e) 模板含 corner 参数化（`create_corner` 等价：.param vdd/process/T 从 corner.json 注入，非硬编字面量 1.8/25）
(f) 模板含 ≥4 类 .measure（tpd/tr/tf/icc_avg，反 naive_grep_only）
(g) B report 每-cell × per-metric 矩阵齐全（≥2 cell × ≥4 metric）
(h) B inv_b tpd 匹配 GT ±15%
(i) B nor2_b tpd 匹配 GT ±15%
(j) B icc_avg 数值合理（>0，反 naive_zero_output）
(k) corner 标签从 spec_B 读（SS/1.5/85）非硬编 A 的 TT/1.8/25（反 naive_hardcode_a）
(l) 跨输入守卫：rerun A → cells={inv_a,nand2_a} + A corner 标签 + A tpd 匹配 GT_A
(m) name-agnostic：B 名{inv_b,nor2_b,buf_b,nchb,pchb} 出现 + A 名{inv_a,nand2_a} 不泄
(n) 确定性：rerun B inv_b tpd 2% 内一致

## negatives 蓝图（6 个，§4.9 三假齐备）

- `naive_empty`（空壳）→ (a)/(c)
- `naive_print_expected`（打印期望串不跑 sim）→ (c)/(h)/(i)
- `naive_no_rerun`（不调 HSPICE subprocess）→ (c)
- `naive_hardcode_a`（硬编 A corner/cell 名与数值）→ (k)/(m)
- `naive_single_cell`（只生成单 cell testbench）→ (d)/(g)
- `naive_zero_output`（icc_avg=0 stub）→ (j)
- §4.9 三假 = naive_empty / naive_print_expected / naive_no_rerun 全 FAIL。

## 风险与下轮第一件事

- **风险**：库级多 cell char 在 level-1 下 nand2/nor2/buf 的 tpd 可解性已由 InvTripDelay/CmdEdgeMeasGen 先例验证（level-1 反相器链/门 tpd 稳定）→ 低风险。
- **下轮第一件事**：.75 HSPICE 标定 A/B GT（inv/nand2/nor2/buf 在 TT1.8V25 / SS1.5V85 的 tpd/tr/tf/icc_avg/ileak）→ 合成 `EDA-Eval-DesignFlow-StdLibCharTmpl-001`（check.py 14 + 6 neg + selftest + reference_submit.zip）→ 追加 `EDA-Eval-DesignFlow_B.jsonl` → mark case → 清 DEBT:1。

## 教训

1. qe1n4 主体是 **Qualib TCL 模板生成**（L1 文件生成，无 sim 真跑）→ 便携 reframe 必须把「模板生成 + 真跑 sim 得库级报告」一起做才够 L2 牙，不能只交付 tcl 文件（否则沦为 L1）。
2. trace 真实痛点 = 长模板逐段 editor 写入易错 → 候选须**整文件生成** char_template.sp（一次写入，非逐段拼），check.py 可加「模板行数/结构完整」断言。
3. A 档选轮合规（U0 纯需求），但末尾无用户接受 → B 档 synthesized。
