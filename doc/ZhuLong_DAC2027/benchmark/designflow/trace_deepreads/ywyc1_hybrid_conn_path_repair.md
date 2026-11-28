# 深读笔记 · ywyc1 (e05598@hfeg0pkn003, mc=195, schematic_netlist/verilog hierarchy)

## trace 溯源
- session: `1795518777122_ywyc1.messages.json` (scan summary 记 `1794376149232_ywyc1`，磁盘实际 ts=1795518777122，slug=ywyc1 一致)
- 732KB / 146 msgs (82 user / 64 assistant)，agent=cline
- 用户: e05598，DRAM PTE verilog 仿真方向
- 真实任务两段: ①"分析 .../LP5_Basic_tRFC_ABR_DDJOC.log fail 原因" ②"可以帮我 fix 这个问题吗"

## 用户真实在做什么
调试 LP5 DDR5 verilog 仿真 (irun/Xcelium) log 失败 + 修复。这是一条 **netlist hierarchy mismatch 诊断 + connect 路径修补** 的真实工程任务。

## 失败链 (agent 诊断结论)
1. log 共 327,103 行，最终 `irun: *E,ELBERR: Error during elaboration (status 1), exiting.` (line 327100)
2. 核心报错 ~77,280 次 (line 17982~327098) 全同一句:
   `ncelab: *E,CUVUNF (...): Hierarchical name component lookup failed at 'I_Array16GTop_Nicap_DDGOA'.`
3. 来源: connect 绑定文件 `/proj/.../wow_hybrid_connect.v` (由生成器 `wow_hybrid_connect_vlog.pl` 生成) 在 A 侧硬编码路径多了一层 `I_Array16GTop_Nicap_DDGOA`。

## netlist 真实结构 vs connect 引用 (逐层核实)
| 通道 | connect 引用路径 | netlist 实际路径 |
|---|---|---|
| A 侧 | `I_A_Top.`**`I_Array16GTop_Nicap_DDGOA`**`.I_Ary8G_W.I_Array1GBK0.I_Ary_m512Meg_U...` | `I_A_Top`(=Ary16G)→`I_Ary8G_W/E`→`I_Array1GBKx`→`I_Ary_m512Meg_U/V` (无中间层) |
| C 侧 | `I_C_Top.I_Array16GTop.I_Array8G_W.I_Array1GBK0.I_m1G_TOP.I_m512Meg_U...` | 与 netlist 完全一致 ✓ |

- agent 扫描所有 netlist 变体 (netlist / netlist_org / netlist_bak / bak1022/1026/1027/1028/1102 / 1029bypassDly): `I_Array16GTop_Nicap_DDGOA` 从未作为实例存在过。
- 结论: 修复方向 = 改生成器/connect 的 A 侧路径 (去掉多余层)，不是改 netlist。

## agent 交付的修复
1. 生成 `wow_hybrid_connect.v.fixed` (79984 行，`_Nicap_DDGOA` 残留 0): 77280 处多余 `I_Array16GTop_Nicap_DDGOA` 全部消除；A 侧 `I_Ary8G_W` 38640 + `I_Ary8G_E` 38640；C 侧 `I_C_Top.I_Array16GTop` 77280 不变。
2. 生成 `wow_hybrid_connect_vlog.pl.fixed` (生成器修正版，硬编码 A 侧路径改为 `I_A_Top.`)。
3. 验证: perl 重跑修正生成器 → 产出 79984 行、`_Nicap_DDGOA`=0、首行样例 `.a0(TOP.Chip.I_A_Top.I_Ary8G_W.I_Array1GBK0.I_Ary_m512Meg_U.s00m0wle)` 与 netlist 完全吻合。
4. 本地绕过 (不碰 /proj SOS 共享区): 备份 `top.sv`→`top.sv_woohyb_back`，把修正 connect 复制到 run 目录 `wow_hybrid_connect_woofix.v`，改 `top.sv` line 44 的 `include 指向本地修正文件。
5. 环境就绪核查: SDF (pt_dir/WOWTOP.sdf.gz) 在位、netlist/libs/top.sv 齐全；唯一需用户提供 `period` 参数 (avc2csv.sh 依赖 WCKps)。

## 关键观察 (判分要点 / 可编码的"牙")
- **fail_stage 分类**: log final_error=ELBERR + error_sig=CUVUNF → "elaboration" (非 simulation/test fail)。这是真实分类，需基于 log 字段判定。
- **root_cause 识别**: 通过对比 connect binding path segments 与 netlist 实例树，找出"在 path 中出现但 netlist 任意层级都不存在"的 segment = stray hierarchy level。算法发现而非硬编码。
- **side 判定**: 哪一侧 binding 含 stray (A 侧受影响, C 侧正确)。
- **corrected path 生成**: 从 path 中删除 stray segment，剩余按序拼接。
- **repaired/unchanged 计数**: 含 stray 的 binding 数 vs 不含的。
- **fixed_connect.v 生成**: 每行 `.name(TOP.Chip.<corrected path>);`，repaired 行修正路径，unchanged 行原样。

## case 合成 plan (task_id=HybridConnPathRepairProduce-001)
**reframe**: spec-JSON 驱动纯 Python `diagnose_hybrid_connect.py(spec) -> {report.json, fixed_connect.v}`，netlist 层次树 + connect bindings + log summary → 诊断报告 (fail_stage/root_cause/failing_instance/side/stray_segment/cuvunf_count/bindings_repaired/unchanged/corrected_path_sample/verdict) + 修正版 connect 文件。LIVE-NA judge [L0,L1]，纯文本/结构判分无真实 EDA 二进制依赖 (irun/ncelab 不在 eval 沙盒)。

**spec schema**:
- `netlist_tree`: dict inst -> {module, children:[...]} (真实实例树，A/C 两侧)
- `connect_bindings`: list of {name(".a0"/".b0"), side("A"/"C"), path:[segments from TOP]}
- `log_summary`: {total_lines, error_sig, failing_name, error_count, final_error}

**A visible spec_A.json** (镜像真实 trace):
- netlist_tree: A 侧 I_A_Top(Ary16G)→I_Ary8G_W/I_Ary8G_E→I_Array1GBKx→I_Ary_m512Meg_U/V; C 侧 I_C_Top→I_Array16GTop→I_Array8G_W→I_Array1GBK0→I_m1G_TOP→I_m512Meg_U
- connect_bindings: 8 个 (4 A-side path 含 stray `I_Array16GTop_Nicap_DDGOA`, 4 C-side 正确)
- log_summary: {error_sig:"CUVUNF", failing_name:"I_Array16GTop_Nicap_DDGOA", error_count:77280, final_error:"ELBERR"}

**hidden-B spec_B.json** (token-structurally 不相交):
- 不同 netlist_tree (B 侧顶层 I_X_Top/X_8G_W，C 侧 I_Y_Top→I_Array16GTop...)
- stray segment 名不同 (`I_FooBar_Bridge`) 且在 **C 侧** (不同 side)
- 不同 binding 数 (12) + 不同 path 深度
- A 硬编码器 (只去 A 侧 `I_Array16GTop_Nicap_DDGOA`) 在 B 全错

**check.py ~16 conds a-p** (k_check=k_rationale=16):
- a: zip 含 diagnose_hybrid_connect.py
- b: py_compile
- c: A 运行 valid=True errors 空
- d: report.fail_stage=="elaboration" (gold: log_summary.final_error 含 ELBERR → elaboration，独立复算)
- e: report.root_cause=="stray_hierarchy_level"
- f: report.failing_instance==gold (来自 log_summary.failing_name)
- g: report.side_affected==gold (扫 bindings 哪侧含 stray)
- h: report.stray_segment==gold (算法发现的 stray)
- i: report.cuvunf_count==gold (log_summary.error_count)
- j: report.bindings_repaired==gold (含 stray binding 数)
- k: report.bindings_unchanged==gold (不含 stray binding 数)
- l: report.corrected_path_sample==gold (首个 repaired binding 修正路径)
- m: fixed_connect.v 行数==len(bindings)
- n: fixed_connect.v 每行格式 `.name(TOP.Chip.<path>);` 且 stray 残留 0
- o: fixed_connect.v unchanged 行原样 (C 侧 path 未变)
- p: anti-hardcode tokenize 源码扫描无 A-only 字面 token (I_Array16GTop_Nicap_DDGOA/Ary16G 等) + 确定性 md5 + hidden-B 守卫 (跑 B 候选 report 字段须匹配 B gold 非 A)

**6 neg**: empty→c / print_only→d / core_deleted→e / hardcode_a→p(hidden-B 守卫) / wrong_stage(报 simulation)→d / no_repair(stray 残留)→n。§4.9 trio {c,d,e} 3-distinct。

**check() 返回 {'pass':bool,'detail':str} 严格契约** (非 tuple, 避 r1661 隐患)。

## 状态
- ✅ r1672 合成收口: HybridConnPathRepairProduce-001 落库 (cases/D/ + assets/ + reference/ + hidden/spec_B.json + hidden_manifest.json)
- 自验: REF self-test PASS 16/16 (a-p 全 Y); negative_selftest 6 neg 全 FAIL, §4.9 trio {empty:c, print_only:d, core_deleted:e} 3-distinct; SKIP_RUN=1 eval/run_one.sh 框架接受 (workdir clean no-leak, infra_fail=0, hook_blocks=0, FAIL only from no submit.zip); test sha 31469b04 disk==JSON sync
- .75 eda_flow MCP open_session(r1671_D) 秒级 + ssh→hfeg0pkn003 scp 取回 732KB/146msgs 直读成功
- ledger: ywyc1 → case EDA-Eval-DesignFlow-HybridConnPathRepairProduce-001 (covered 683→684)
- live_eval_review_nonlite_D.tsv 追加 LIVE-NA 行 (505→506)
