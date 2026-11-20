# trace_deepread: 1795055245563_97z71 (shanliny @ hfeg0pkn003, mc137)

**session**: 1795055245563_97z71  
**user/host**: shanliny / hfeg0pkn003 (10.129.2.12)  
**scan**: ssh_eda_search_20261119_172105, B keywords (hspice:434; aether:212; .def:80; waveview:56; mosfet:46; synopsys:36; netlist:12)  
**msg_count**: 116 (1.3MB), uncompacted (原始 user prompt 完整保留)  

## 用户真实意图（多主题 session，B-shard 取 spice_sim 主题）

### 主题 1（B-shard 采纳）: SRAM racing-check WM 测量失败诊断
- msg[0] 用户: "帮我看 /proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/racing_check/9_autosim/racing_hd1p" — 看 SRAM racing-check autosim 目录
- msg[7] agent 给出目录全景分析：实例 CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS（cm=4,bk=2,nw=64,nb=8,re=1），WM/RM/Racing Check/Logic Racing 四类表征
- **msg[8] 用户核心诉求**: "sim_results/.../finesim_out 下你会看到 mt0 文件有测量失败的地方，结合 fsdb 文件告诉我发生了什么事情"
- msg[11-15] agent 读 mt0 + timing.meas + racing.pdef + racing.vec + 仿真日志，诊断：
  - 1060 个 measure 定义，约 260 条成功，其余 error
  - **WM（Write Margin）**: `_a`（WL↑→bitcell 翻转延时）只在 `ll`（xic0 左正常列）成功 ~69ps；`lr`→lcrc（冗余列）、`rl`→rcrc（冗余列）、`rr`（xic3 右正常列）全部 error
  - **WM `_b`**（WL 脉宽）全部成功 ~186ps；**RM** 全部成功 ~200-227mV
  - 根因：写操作只对最左正常列 `xic0` 生效，冗余列 lcrc/rcrc 与右正常列都写不进去（write-driver/column-select 路径问题）
- measure 命名（来自 config_rule.txt SETUP 宏）：
  - `wm_dm_<bk>_<edge>_y<N>_wl<N>_w0_a` = step a（bitcell 翻转延时）
  - `wm_dm_<bk>_<edge>_y<N>_wl<N>_w0_b` = step b（WL 脉宽）
  - `wm_dm_<bk>_<edge>_y<N>_wl<N>_w0` = WM = b - a
  - `rm_dm_<bk>_<edge>_y<N>_wl<N>_r0` = RM (mV)
  - `<bk>` = bk0d/bk0u/bk1d/bk1u；`<edge>` = ll/lr/rl/rr
- 边沿规则：`_ll -> _lr,_rl,_rr,_lcrc`（re=1 时 lr→lcrc/rl→rcrc 冗余列）；`_ll -> _lr,_rl,_rr`（re=0 无冗余）

### 主题 2（非 B-shard，跳过）: smart_ls.py 改进 list_allowed_files 工具
- msg[16-25+] 用户问 list_allowed_files 消耗上下文太快，要求改进；agent 写了 smart_ls.py 上下文友好目录浏览工具
- 属 generic Python utility，非 spice_sim 域，不在本 case 范围

## reframe 决策（portability-reframe + harness-for-teeth 第三十四实证）
- 原意图 = Q&A/diagnosis（诊断 mt0 失败），reframe 成 produce 型参数化诊断器 `wm_mt0_diag.py`
- 对任意 FineSim .mt0 + SRAM instance.cfg 输出结构化 JSON 诊断（分类/统计/边沿矩阵/根因）
- **隐藏 B 防背题**: 不同 instance（CXN2HC1PS32X16M2B1C1R1W1BW1RE0_FS, re=0 无冗余）+ **反转的成功边沿**（rr 成功 vs A 的 ll 成功）+ 不同 PVT（ss/0.6V/-40C）+ 更小测量集
- 判分器在 B 上断言：正确分类、反转模式、冗余标签随 $re 切换、rm 范围、防硬编码 A

## case 产出
- **case_id**: EDA-Eval-DesignFlow-WmMt0Diag-001
- **domain**: spice_sim, layer L1
- **k_check = k_rationale = 15**（a-o，≥8 ✓）
- **asset A**（SUT 可见）: sim.mt0（faithful 复刻 trace 真实 wm_a/wm_b/wm/rm 值与 error 模式，1024 measures/384 errors，ll-ok/lr-rl-rr-error，re=1）+ instance.cfg + pvt.txt
- **hidden B**（判分器用）: sim.mt0（256 measures/96 errors，rr-ok/ll-lr-rl-error，re=0）+ instance.cfg + pvt.txt
- **reference**: wm_mt0_diag.py（标准库，解析+分类+统计+边沿矩阵+冗余标签+根因 JSON）
- **check.py**: 15 条件 a-o，在 hidden B 上跑候选脚本断言结构+反转模式+防硬编码
- **negatives**: 5 个（empty/print-only/hardcode-A/no-failures/crash）全 FAIL ✓
- **自验**: ref 15/15 PASS ✓，NEG 5/5 FAIL ✓，§4.9 (a)(b)(c) 三假提交全 FAIL ✓
- **B.jsonl**: 438 → 439
