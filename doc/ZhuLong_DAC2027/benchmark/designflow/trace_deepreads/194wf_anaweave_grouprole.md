# 深读笔记 · 194wf · AnaWeave VwlpRefAmpIP 电路结构分析与对称群推断

## trace_source
- session_file: `1790149493569_194wf.messages.json`
- user: ziyuny · host: 10.129.32.190 (hfeg0pkn190) · match_count: 128
- domain: schematic_netlist (D-shard)
- n_msgs: 229 · n_user: 21 · n_assist: 101
- tools: editor:51 / run_approved_command:35 / read_files:15 / ask_question:3
- ledger: claimed 2026-11-07 (#346 选料轮, DEBT:1 → #347 合成)

## 用户真实意图（逐字原文，A 档候选轮）
- U#0 (context summary, 续接笔记): AnaWeave VwlpRefAmpIP 版图生成 + 手工 placement，CP0 重摆位
- U#22/31: 「不要考虑pin,根据电路的摆放位置，将版图做对应的摆放」
- U#125: 「你能通过电路图，识别有哪些对称结构吗」 ← **核心 produce 意图**
- U#131: 「这个电路的结构，包含所有的device分别是什么作用，你能分析给我吗？」 ← **核心 produce 意图**
- U#133: 「MPDUM<3:0>的作用你知道是什么吗？」
- U#135: 「CP0是不是cascode?」
- U#137: 「那你按照你对电路图的分析与理解，把对应版图的位置进行重新调整到和电路图逻辑一致」
- U#161: 「能按照电路图例的，把版图修改成一致的样子吗？」(识别 text 标注的 match&dummy / common centroid)
- U#210: 「前面请你帮忙检查电路的图例和版图的一致性，请你把检查的经验输出给我」 ← **report produce**

## A-faithful 判定
- **不可行**：真实 produce = 版图 placement（live cellview `AnaWeave_demo/VwlpRefAmpIP/layout`，需 pyAether dbMoveFig 操作 76 instances / 15 figGroups），不可附加 + 不可离线复刻。
- **可移植 facet** = assistant 在 [132]/[134]/[136] 产出的**电路结构分析**（device-by-device role classification + symmetry group identification），这是 placement 的「电路依据」中间产物，纯文本/JSON 可验。
- **B 档 synthesized**：取 portable facet = 「SPICE 网表 → 模拟单元对称群角色推断器」(parse netlist + group annotations → classify each device role + identify symmetry groups → emit JSON report)。

## 真实电路（从 trace assistant [132]/[134]/[136] 完整提取）

**VwlpRefAmpIP = 带使能门控的单端输出差分 OTA**：可开关尾电流 + 双管串联（同栅驱动）输入对 + PMOS 电流镜负载 + 禁用态复位开关。

### 器件清单（真实 device name + 连接 + 角色）

| group | device | model | 连接 (G/S/D/B) | 角色 |
|---|---|---|---|---|
| **CP0** (尾电流, vss 侧) | MN0<1:0> | ntk | G=BiasN, S/B=vss!, D=net0 | 尾电流源管 |
| CP0 | MN1<1:0> | ntk | G=BiasN, S/B=vss!, D=net1 | 尾电流源管(第二阵列) |
| CP0 | MNSW1<1:0> | ntk | G=RegEnVdd1, S=net0, D=ntail | 尾电流串联开关(ON=共栅=cascode) |
| CP0 | MNSW3<1:0> | ntk | G=RegEnVdd1, S=net1, D=ntail | 尾电流串联开关 |
| **DP0** (输入核心, ntk_lv) | MN2<3:0> | ntk_lv | G=Pos, S=ntail, D=net2 | 输入对下管(跨导) |
| DP0 | MN3<3:0> | ntk_lv | G=Neg, S=ntail, D=net3 | 输入对下管(Neg侧) |
| DP0 | MNPAIR1<3:0> | ntk_lv | G=Pos, S=net2, D=pmirror | 输入驱动串联上管(cascode/跟随) |
| DP0 | MNPAIR2<3:0> | ntk_lv | G=Neg, S=net3, D=Out | 输入驱动串联上管(Neg侧,漏=Out) |
| **CM0** (PMOS镜像负载, ptk_lv, vdd1 侧) | MPCUR3<3:0> | ptk_lv | D=G=pmirror, S/B=vdd1! | 二极管接法镜像基准 |
| CM0 | MPCUR4<3:0> | ptk_lv | G=pmirror, S/B=vdd1!, D=Out | 镜像输出管(电流求差→Out) |
| **dummy** | MPDUM<3:0> | ptk_lv | G/S/D/B 全=vdd1! | CM0 镜像排匹配 dummy |
| dummy | MNDUM1<3:0> | ntk_lv | G/S/D/B 全=vss! | DP0 输入排 dummy |
| dummy | MNDUM2<3:0> | ntn_m | G/S/D/B 全=vss! | 独立 dummy(无同类型阵列) |
| **enable** | MPSW1 | ptk_lv | G=¬RegEnVdd1, D=pmirror, S/B=vdd1! | pmirror 复位开关(禁用态把 pmirror 拉到 vdd1) |

### 信号网
- 偏置: BiasN, RegEnVdd1
- 尾节点: ntail
- 内部: net0, net1, net2, net3
- 镜像/输出: pmirror, Out
- 输入: Pos, Neg
- 电源/地: vdd1!, vss!

### 对称群（trace 已识别）
- **CM0** = PMOS current mirror (MPCUR3 diode ‖ MPCUR4 mirror, `<3:0>` interdigitate+ABAB, 4 dummy MPDUM)
- **DP0** = differential pair (MN2/MN3 下管 + MNPAIR1/MNPAIR2 上管, 共 ntail 尾, 同栅串联 cascode, `<3:0>` 四列交错 Group0~7, 4 dummy MNDUM1)
- **CP0** = switchable tail current (MN0/MN1 电流源 + MNSW1/MNSW3 开关, ON 态= cascode 尾电流源, 2×2 排布 Group8~11)
- **dummy 群**: MPDUM(CM0), MNDUM1(DP0), MNDUM2(独立)
- **enable**: MPSW1 (pmirror 复位)

## 合成 plan（#347 执行）

### case id: `EDA-Eval-DesignFlow-AnalogGroupRoleInfer-001`
- domain: schematic_netlist · L1 (offline Python parse) · B-grade synthesized
- trace: 194wf (ziyuny/AnaWeave VwlpRefAmpIP)

### 接口
```
gen_group_role_infer.py --netlist <sp> --outdir <dir>
→ group_roles.json + report.md
```
读 SPICE netlist（含 `* @group <name> @type <mirror|diff_pair|cascode|tail_switch|dummy|enable_switch>` 注释 + `.SUBCKT` + MOS device lines），解析 device 连接 + group 注释 + 连接推断，emit JSON。

### A 输入网表 (si_A.sp 风格, trace-faithful)
- 顶层 `.SUBCKT VwlpRefAmpIP Pos Neg Out vdd1! vss! BiasN RegEnVdd1`
- 4 group 注释: CP0(tail_switch) / DP0(diff_pair) / CM0(current_mirror) + dummy 群
- 14 device lines (真实名 MN0/MN1/MNSW1/MNSW3/MN2/MN3/MNPAIR1/MNPAIR2/MPCUR3/MPCUR4/MPDUM/MNDUM1/MNDUM2/MPSW1)
- 真实 net 连接（上表）
- n_groups=4 (CP0/DP0/CM0/dummy), n_devices=14, match_groups=[CM0,DP0], dummy_groups=[dummy], enable=[MPSW1]

### hidden B 输入 (si_B.sp, 不同结构)
- 2-stage Miller opamp: `.SUBCKT MILLER_B in inn out vdd vss pbias`
- group: BIAS(current_mirror, pbias 镜像) / DP(diff_pair, PMOS 输入对) / GAIN2(common_source, NMOS 第二级) / MILLER(coupling, Miller cap C1+Rz) / DUM(dummy)
- 不同 device 名 (MB1/MB2/MP1/MP2/MN3/MN4/MC1/Rz/MDUMx), 不同 net (pbias/netb/in1/in2/out)
- n_groups=5, n_devices~12, 不同 match/dummy 计数

### hidden B2 输入 (si_B2.sp, 更简)
- 单级 folded cascode: `.SUBCKT FCASCODE_B2 in out vdd vss pbias`
- 3 group: BIAS(mirror) / DP(diff_pair) / CASCODE(folded cascode load)
- 无 dummy 群, n_groups=3, n_devices~8

### 反硬编码轴
- A/B/B2 顶层 cell 名全不同 (VwlpRefAmpIP/MILLER_B/FCASCODE_B2)
- device 名全不相交 (MN0/CM0/DP0/ntail/RegEnVdd1 vs MB1/DP/GAIN2 vs ...)
- group 数 4/5/3 → n_groups 不同 (硬编 4 者 B/B2 上 FAIL)
- match/dummy 计数不同 (B2 无 dummy)
- 源码禁 A 字面量 (VwlpRefAmpIP/CM0/DP0/CP0/MN0/MNSW1/ntail/RegEnVdd1/MPDUM/MPCUR3/Pos/Neg/pmirror)

### check.py 16 条件 (a-p)
- a. zip 防泄漏 (无 check.py/reference/negative/jsonl/_tmp_/__chk) + py_compile gen_group_role_infer.py
- b. B 真跑 subprocess exit 0 + 产出 2 文件 (group_roles.json + report.md)
- c. JSON 必需顶层键 {groups, devices, n_groups, n_devices, n_match_groups, n_dummy_groups, annotation_count, cell_name}
- d. cell_name == B 的 .SUBCKT 名 (MILLER_B)
- e. n_groups == B 注释 group 数 (5)
- f. n_devices == B device 行数
- g. 每个 group dict 含 {name, type, role, members, key_nets, match_flag, dummy_flag}
- h. group.type ∈ {current_mirror, diff_pair, cascode, tail_switch, common_source, dummy, enable_switch, coupling}
- i. match_flag=True 的 group (current_mirror/diff_pair) members ≥ 2
- j. dummy_flag=True 的 group 全部 members 4 端子接同一电源/地网 (dummy 电学特征)
- k. current_mirror group 的 key_nets 含共享 gate net (镜像基准)
- l. diff_pair group 的 key_nets 含共享 source net (尾节点)
- m. report.md 含每个 group 一节 (## <name>) + device role 表
- n. 反硬编码: 源码无 A 字面量 (VwlpRefAmpIP/CM0/DP0/CP0/MN0/MNSW1/MPCUR3/MPDUM/ntail/RegEnVdd1/Pos/Neg/pmirror) + A-run cell_name==VwlpRefAmpIP
- o. 跨输入 B2: n_groups==3 + n_dummy_groups==0 + cell_name==FCASCODE_B2
- p. 3x 确定性 sha256 (3 seed 同 B 输入 → 同输出)

### negatives (≥2)
- empty_shell (gen 只 print, 不产文件) → b FAIL
- hardcode_a (源码硬编 A 的 group 名/计数) → n/o FAIL
- print_expected (直接 cat 预期 JSON) → b/d/e/f FAIL (B 不同)
- ref_core_deleted (删除推断逻辑) → g/h/k/l FAIL
- naive_stub (只数 `* @group` 行不解析 device) → f/g/h FAIL

### k 条断言（与 check 16 条件 a-p 一一对账, k=16）
`16 条断言：①(a) zip 无泄漏+脚本可编译 ②(b) B 运行 exit0+产 2 文件 ③(c) JSON 含 8 必需顶层键 ④(d) cell_name==B 的 SUBCKT 名 ⑤(e) n_groups==B 注释 group 数 5 ⑥(f) n_devices==B device 行数 ⑦(g) 每 group 含 7 必需字段 ⑧(h) group.type ∈ 8 种合法枚举 ⑨(i) match group members≥2 ⑩(j) dummy group 全端子接同一网 ⑪(k) mirror group key_nets 含共享 gate ⑫(l) diff_pair group key_nets 含共享 source ⑬(m) report.md 每 group 一节+device 表 ⑭(n) 源码无 A 字面量+A-run cell_name==VwlpRefAmpIP ⑮(o) 跨输入 B2 n_groups==3+n_dummy==0 ⑯(p) 3x sha256 确定性`

## #346 结论
- **本轮 #346 = 选料/深读轮** (DEBT:1)。fresh 池 mc≥30 顶部 ~25 候选已全部 peek：clean L2 produce 稀缺（多数 skill-opt/Q&A/wrong-domain/dup/non-portable）。
- **9 条 weak/dup 候选已 parked**：t2hnp(=dup NetHighlightProbe-001) / sr426(=dup NetlistFightX-001) / iz828(weak Q&A) / 7kyrv(wrong domain synopsys build) / vpj8o(AnaWeave dup cfg) / 5vmvu(skill-edit multi-turn) / vbxlf(skill-opt run-regression) / kxqt7(shard C DRC) / mrlo9(VAMAgent 1turn)。
- **194wf claimed** 留 #347 合成 AnalogGroupRoleInfer-001 (B-grade L1, 16 条件 a-p, 真实 VwlpRefAmpIP 网表已完整提取于本笔记)。
- **#347 第一件事**：复用本深读笔记 → 合成 gen_group_role_infer.py + A/B/B2 网表 + check.py + negatives → 自验 → 追加 D.jsonl → mark 194wf case → 还 DEBT。
- L1/L2 比例债仍存（本 case 亦 L1）；#347 后继续优先 L2 produce。
