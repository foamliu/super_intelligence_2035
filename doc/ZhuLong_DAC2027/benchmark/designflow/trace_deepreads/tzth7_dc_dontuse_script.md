# 深读笔记：1793324309763_tzth7 — DC dont_use 脚本生成（Liberty .lib + 允许单元白名单）

- **trace**: `1793324309763_tzth7` · user `e0045144` @ `hfeg0pkn004` (10.129.2.13) · mc=23 (17 synthesis + 6 pyAether) · 377 msgs · 1.06MB · clide `lead` agent · 11/04 fresh
- **台账**: shard A，claim→deepread（轮 53），下一轮必合成
- **域**: digital（DC synthesis dont_use 策略）

## 用户轮（A档②判定）

- **USER#1 (msg0)**: 「如何synthesis时设置dont used cell」— 概念 Q&A，非任务说明。
- **USER#2 (msg2)** 逐字（A档任务说明）: 「这个lib : `/proj/lacaa/TV1_digital/workdir/Data_Transfer/to_HF/e0037828_20261025/LIB/DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs.lib` 只允许用 `xorX1,nandx1,nandx2,norx1,norx2,invx1,invx2,invx16,bufx1,bufx3,bufx8,bufx128,tiehx1,tielx1,icgx1,dffx1,latx1,muxx1,delayx1` 这些类型cell，帮我产生个DC脚本」
  - = **clean 提需求**（给定 lib 路径 + 允许 cell 白名单，生成 DC 脚本），未给根因/修复 → **A档规则②合格 → A档 faithful**。
  - **注意命名不一致**：用户白名单用 `xorX1/invx1/bufx1` 小写 `x<drive>` 风格；真实 lib 单元用 `XOR2D1/INVD1/BUFFD1...DBCP51H180L6W25T5LVT` 大写 `D<drive>`+PDK 后缀风格。任务隐含「白名单 base 名 → lib 单元名」的映射。
- **USER#3 (msg88)**: 「如何看这些cell的功能」— Q&A。
- **USER#4 (msg108)** 逐字: 「`set_dont_use [get_lib_cells */CK*]` ... `set_dont_use [get_lib_cells */*D32*]` 帮我按照这个格式写下」— refine：要求按 `set_dont_use [get_lib_cells */<pattern>]` 通配格式输出。

## 金标准（助手真实交付，用户接受）

助手最终交付 `dont_use_dc.tcl`（msg 67/69，editor 写盘），策略 = **disable-all-then-enable-allowed**：

```tcl
# 1. 从 .lib 提取 library name
set LIB_NAME "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"
# 2. 全禁
set_dont_use [get_lib_cells "${LIB_NAME}/*"] true
# 3. 仅允许单元 re-enable（enable_cells proc，wildcard pattern ${LIB_NAME}/${short}*）
proc enable_cells {lib_name cell_short_names {allow_partial_wildcard 0}} {...}
#   allowed_xor/nand/nor/inv/buf/tie/mux/icg/dff lists（short name 如 XOR2D1/INVD1/BUFFD1...）
# 4. 对每个 allowed short name：set_dont_use [get_lib_cells "${LIB_NAME}/${short}*"] false
```

助手把用户白名单（xorX1→XOR2D1, invx1→INVD1, bufx1→BUFFD1, icgx1→CKLNQD1, dffx1→DFKRPQD1, latx1→..., muxx1→MUX2D1, delayx1→..., tiehx1→TIEH, tielx1→TIEL, nandx1→ND2D1, norx1→NR2D1）映射到 lib 命名后逐类 re-enable。

## 真实 lib 单元（从 trace grep 输出提取，92 条，PDK 后缀 `DBCP51H180L6W25T5LVT`）

BOUNDARY{N,P}{,IN}CORNER、BUFFD{1,2,3,4,5,6,8,10,12}、CKMUX2D{1,2,4,8}、CKOR2D{3,4,6,8}、CKXOR2D{1,2,4,6,8}、INVD{1,2,3,4,5,6,8,10,12}、MUX2D{1,2,3,4,6,8}、MUX2ND{1,2,3,4,6,8}、MUX3D{1,2,4}、MUX3ND{1,2,4}、MUX4D{1,2,4}、MUX4ND{1,2,4}、OR2D{1,2,3,4,6,8,12}、OR3D{1,2,3,4,6,8}、OR4D{1,2,3,4,6,8}、TIEH、TIEL、XOR2D{1,2,3,4,6,8}、XOR3D{1,2,4}、XOR4D{1,2,4}。

**注意**：这是 grep 过滤 `(XOR|NAND|NOR|INV|BUF|TIE|ICG|DFF|LAT|MUX|DELAY|AND|OR)` + `head -300` 的子集；真实 lib 还有 NAND/AND/DFF/LAT/ICG/DELAY/AOI/OAI 等未在 trace 中完整捕获。合成时需按同一命名约定 `<BASE>DBCP51H180L6W25T5LVT` 补全典型单元（ND2/ND3/AN2/AN3/DFKRPQD1/CKLNQD1/DELAD1/AOI21/OAI21 等），使 disallowed 集非平凡。

## 真实 lib 不可直接访问

`/proj/lacaa/.../DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs.lib` 从 .75 与 10.129.2.13（e0031982 身份）均 **permission denied**（归 e0037828/e0045144 组）。trace 中 `read_files` tool_result 全空（权限/过大），仅 `run_approved_command` 的 `grep 'cell ('` 输出捕获了上述 92 单元名。→ **无法用真实 .lib 作 A 档附件**；须合成 faithful .lib（含真实单元名子集 + 同命名约定补全）→ **B 档 synthesized**（A 档⑥「真实 attachments」不可达）。

## 合成计划（下一轮第一件事落地，DEBT 清零）

- **case_id**: `EDA-Eval-DesignFlow-DcDontuseGen-001`
- **档位**: B 档 synthesized（真实 lib 不可达；A 档 faithful 任务说明照用 USER#2 逐字）
- **verb**: `lib-allowlist-to-dc-dontuse-script`（读 Liberty .lib + 允许白名单 → 生成 DC disable-all-then-enable-allowed 脚本）
- **verb 互斥**: 与已有 shard-A verb 全互斥（sta-flow-scaffold / rtl-derived-sdc-gen / netlist-port-connectivity-extract / lib-to-parm / synth-upf-diagnose / apr-stamp-fix / flat-net / apr-setup-audit / apr-log-audit / vcs-equiv / vcs-makefile / itf-compare / calibre-pdf2md / autocell-tcl-flow-gen）—— 本 verb 是「读 lib 生成 dont_use 策略脚本」，与 lib-to-parm（lib→反标 parm 抽取）和 rtl-derived-sdc-gen（RTL→SDC）均不同对象。
- **交付**: `submit.zip{gen_dontuse.py(通用 Liberty .lib + 白名单 → DC dont_use tcl 生成器, CLI `--lib <path> --allow <allow.txt> [-o out.tcl]`, 纯 stdlib re 解析 `library(...)`+`cell(...)`→提取 LIB_NAME 与全部 cell 名→白名单 short-name 映射→disable-all + enable-allowed tcl)+dont_use_A.tcl}`
- **A 可见 bundle**: `lib_A.lib`(合成 faithful Liberty, library name=`DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs`, ~60 cells 含真实 92 子集 + 补全 ND/AN/DFF/ICG/DELAY/AOI/OAI, 命名 `<BASE>DBCP51H180L6W25T5LVT`) + `allow_A.txt`(USER#2 逐字 19 行：xorX1/nandx1/.../delayx1)
- **B 隐藏 bundle**（异构 cross-input guard 击破硬编 A）: `lib_B.lib`(library name=`XXYN40H120L4W20T4_BASE_SVT_ff_typical_v0p55_125c_ccs`, 不同 PDK 后缀 `XXYN40H120L4W20T4SVT`, 不同 cell 集 ~50 cells, 不同 base 名如 `XOR2Y1/INVY1/BUFFY1/ND2Y1...`) + `allow_B.txt`(不同白名单 15 行) → 5 维全异（LIB_NAME / PDK 后缀 / cell base 命名 / drive 风格 / 白名单成员）击破硬编 A。
- **判分纯 stdlib python3**（无 DC license 依赖）：check.py **≥12 条 a-?** 独立断言：
  - a) zip 含 2 件
  - b) py_compile
  - c) 候选跑 A exit0 + 产 dont_use_A.tcl
  - d) A tcl 含 `set_dont_use [get_lib_cells "${LIB_NAME}/*"] true`（disable-all，LIB_NAME 从 lib_A.lib 提取 == `DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs`）
  - e) A tcl 含 `set_dont_use ... false` 对每个 allow_A.txt 白名单 short-name 映射后的 lib cell（≥19 条 enable 行）
  - f) A tcl 不含对 disallowed cell 的 enable（随机抽 3 个 disallowed cell，断言无对应 enable 行）
  - g) A tcl `LIB_NAME` 字符串与 lib_A.lib 的 `library(...)` 名一致（候选必须从 lib 解析，非硬编）
  - h) A tcl 含 `get_lib_cells` 通配 `${LIB_NAME}/<short>*` 形式
  - i) A tcl `tclsh info complete` == 1（语法完整）
  - j) 候选跑 B exit0 + 产 dont_use_B.tcl
  - k) 跨输入守卫 B tcl LIB_NAME == `XXYN40H120L4W20T4_BASE_SVT_ff_typical_v0p55_125c_ccs` ≠ A
  - l) 跨输入守卫 B tcl enable 行数 == |allow_B.txt| ≠ A 的 |allow_A.txt|=19
  - m) 跨输入守卫 B tcl 不含 A 的 PDK 后缀 `DBCP51H180L6W25T5LVT`
  - n) 反硬编 候选脚本不含 `DBCP51H180L6W25T5` 字面量（必须从 lib 读）
  - o) 随机化：3 个随机种子在 allow_A.txt 随机抽 10 行子集跑候选，enable 行集合 == 抽中子集（非硬编全 19）
  - k_check ≥ 12，k_rationale == k_check
- **oracle**: 独立 line-based Liberty 解析器（不同代码路径）重算 A/B 的 LIB_NAME + 全 cell 集 + 白名单映射期望 enable 行集。
- **5 negatives** + §4.9(a)(b)(c) 三假全 FAIL：
  - fake_empty → a
  - fake_print_expected（硬编 A 的 19 行 enable）→ k 跨输入守卫（B LIB_NAME 不匹配）
  - fake_core_deleted（删 disable-all 行）→ d
  - naive_hardcode_a（LIB_NAME 硬编 DBCP...）→ k 跨输入守卫（B LIB_NAME 错）
  - naive_enable_all_no_lib_parse（不读 lib，直接 echo 白名单）→ g（LIB_NAME 与 lib 不一致）
- **L2 判据**: subprocess 真跑候选于 A+B + tclsh info complete（无 DC license，本地 PASS == 判分环境等价）。
- **关键设计点**:
  1. 白名单 short-name → lib cell 映射规则要明确（xorX1→`XOR2*D1*`? 还是 XOR2D1 精确？）—— 取「short-name base 大写 + 通配 `${LIB_NAME}/${BASE}*`」让候选用通配匹配，避免精确映射歧义；allow 文件每行一个 short-name，候选转大写后拼通配。
  2. disable-all-then-enable-allowed 是金策略；候选若用「enumerate-disallowed」也对，但须覆盖全部 disallowed（随机抽验证）—— 判分 e/f 用「enable 行覆盖全部 allowed + 不覆盖任何 disallowed」双向断言，兼容两策略。
  3. 反硬编 n：候选脚本源码不得含 PDK 后缀字面量（必须 `re.search(r'library\s*\(\s*(\S+?)\s*\)', lib_text)` 从 lib 读 LIB_NAME）。
- **DEBT**: 1（本轮 deepread 未合成；§3 禁连续两轮只深读 → 下一轮第一件事合成 DcDontuseGen-001）。

## 本轮为何未合成

- 候选扫描耗 ~10 min（summary.tsv 10/28 stale；改扫 daily eda_trace_2026110{1-4}.log 4 文件 45125 行 → shard-A 数字工具评分筛出 18 候选；逐条 scp + 解析 user 轮判 A 档②）。
- 6 条设计_flow 候选中 4 条是 Q&A/代码解读（0yyhj/4efo6/kvv66 + 7qn0b DFT-env 梳理但真实文件不可达），仅 tzth7 是真 design_flow（生成 DC 脚本）。
- tzth7 完整合成（lib bundle + reference + ≥12 断言 + B 异构 + 5 negatives + 自验）超本轮剩余预算 ~10 min；强写易过不了断言闸门 → rewrite_queue（更差）。
- 故 deepread + park 其余，下一轮第一件事合成 DcDontuseGen-001，DEBT 清零。
