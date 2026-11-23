# trace_deepread: 5ew0s — wendy1w WL-hierarchy trace (DRAM tWR testbench)

- **session**: `1794894548787_5ew0s` @ `wendy1w` / `hfeg0plg100` (10.129.8.232)
- **scan**: ssh_eda_search_20261123_064315, mc=147, keywords: schematic:1159 / waveview:670 / netlist:596 / aether:107 / verilog:46 / hspice:39 / transistor:24 / lib.defs:20
- **size**: 89 msgs / 1.12 MB messages.json (agent=lead), accessible via ssh e0031982@10.129.8.232 (nested path `sessions/1794894548787_5ew0s/1794894548787_5ew0s.messages.json`)
- **shard/domain**: B / spice_sim ✓

## 用户真实意图（U0 / U11 / U25）

U0: 「读取 `/proj/drgqa/V3_test/workdir/wendy1w/simulation/WRTIME_V4_tWRTBV4SW_schematic_ALPS/WRTIME_V4_tWRTBV4SW_schematic.netlist` 这个网表，然后 *****PVT***** `.lib '.../V1_HK_Model_D5_v0d9_t01.sp' tt` + `.lib '.../V4_HK_Model_PF_v0d00_t03/model.sp' ss_array` + Add finesim option `.inc '.../SM/finesim_option'` + hspice option … Netlist …」— 给出网表+PVT .lib+finesim/hspice option，让 agent 读网表并理解整体 testbench 结构。

U11: 「你看一下开得哪一条 wl」— 问哪条 wordline 被打开（针对被测存储节点 cc13/cc10）。

U25: 「你能从仿真激励上看到吗我怎么给的wl的激励」— 问 WL 的激励是怎么给的（在哪个 stimulus 文件里）。

## assistant 工具链与关键产物

1. `read_files` 读 `WRTIME_V4_tWRTBV4SW_schematic.netlist`（分多段：636-1200 / 9487-10131 / 9460-9500）+ `.netlist.map` + `/rundata/.../netlist` + `netlistHeader`/`netlistFooter`/`form.rc`/`netlist.log`/`netlist.presim`/`force_power.inc` + `ideal_stimulus_write_v4.sp`(不存在/无权限) + `.simrc`/`.simrc.presim`。
2. `list_allowed_files` 大量目录枚举（/proj/drgqa/.../wendy1w, /rundata/.../finesim/workdir/wendy1w, simulation/WRTIME_..., v3bg_tWR, tWRtestbenchV4SW 等）。
3. `run_approved_command` (profile=shell-runner) 尝试 `find ... -name '*stim*'`（被 filePath 必须以 .sh 结尾的限制拒）。

## 关键分析结论（A[10] / A[16] / A[24] / A[88]）

**层级结构**（A[10]）：
```
tWRTBV4SW (顶层)
├── XI31 → ONEMV4SW  (Port A 偶数bit, blasec0/blbsec1)
├── XI26 → ONEMV4SW  (Port B 奇数bit)
├── XI30 → ONEMV4SW
├── xi5  → BLx16TGV4sw  (TG BL array, 含受测 bitcell)
│   └── xi1 → kcellx64targetV4SW
│       └── xi6 → kcellx16mdlV4sw
│           └── xi2 → VCT_kcellx2mdl_V4sw  (2-cell bitcell 叶子!)
│               ├── cc10, cc11, cc00, cc01  存储节点
│               ├── XMMN5.mn1 读管 (CC13侧)
│               └── XMMN4.mn1 读管 (CC10侧)
```

**WL 追踪**（A[16]/A[24]）：VCT_kcellx2mdl_V4sw 网表 line 24-28：
```
XMMN3 CC01  Wl0  net7  BG    ← CC01(= cc13) 接 Wl0
XMMN2 CC00  Wl0  net2  BG
XMMN5 CC11  Wl1  net1  BG
XMMN4 CC10  Wl1  net0  BG    ← CC10 接 Wl1
```
kcellx16mdlV4sw 的 XI2 实例化（line 98）：**Wl0(VCT pin 21)=WL<2>**, **Wl1(VCT pin 22)=WL<3>**。kcellx64targetV4SW 透传 WL<3:0>。BLx16TGV4sw XI6（line 296）透传 WL<3:0>。

**结论**：cc13(CC01)→Wl0→WL<2>，cc10(CC10)→Wl1→WL<3>，**两条 WL 都被打开**（2-cell 结构同时对两存储节点写）。

**WL 激励来源**（A[88]）：`ideal_stimulus_write_v4.sp` 不在 finesim 运行目录也不在 wendy1w 工作目录（无权限/本地）。从 testbench 头部 .param 提取：`tstart=30n trise=300p t1=300p tcom=0 tsel=2n / toc=1.18n tsdt=15n tseldly=0 tsadly=0 / tt=300p tcs=0n / Sanadj1/2/3=1 Sapadj1/2/3=1 / .inc './ideal_stimulus_write_v4.sp'`。引导用户在 stimulus 文件里搜 `VWl0 c_m0wler<0> 0 PWL(...)` 关键字。

## reframe（合成 case = EDA-Eval-DesignFlow-WlHierarchyTraceProduce-001）

**核心可程序化部分** = SPICE 层次化网表 WL-gate 追踪：给一个层次化网表 + 目标实例路径 + 存储节点列表，输出每个存储节点的 gate 信号沿实例化链自底向上到顶层 net 的 trace 链。

**为何这是合法真实意图**：用户 U11「开得哪一条 wl」本质是「存储节点→access MOS gate→层次 WL bus」的端口映射追踪——这是纯分析/查询意图，11-15 令明确 analysis-Q&A 合法。reframe 把 Q&A 的「答案」固化成可执行交付物（Python 分析器），check() 用独立 oracle 在隐藏 B 上校验 trace 链。

**A netlist**（faithful）：2-cell VCT_kcellx2mdl_V4sw 叶子（M3 cc01 wla / M4 cc10 wlb）→ kcellx16mdlV4sw xi2(wla→wl2,wlb→wl3) → kcellx64targetV4SW xi6(透传) → BLx16TGV4sw xi1(透传) → top xtop(wl2→wl_top2,wl3→wl_top3)。instance_path=`xtop.xi1.xi6.xi2`，storage=[cc01,cc10]，4 层（5 entry）。

**hidden B**（8 维 anti-hardcode）：4-cell Bitcell2xV5sw 叶子（M0 s0 g0 / M1 s1 g1 / M2 s2 g2 / M3 s3 g3）→ RowMod8V5sw xi3(**scrambled**: g1→w6,g2→w7) → ColGrpV5sw xi5(透传) → top xbank(w6→gw6,w7→gw7)。instance_path=`xbank.xi5.xi3`，storage=[s1,s2]，3 层（4 entry）。差异维度：①leaf subckt 名(Bitcell2xV5sw vs VCT_kcellx2mdl_V4sw) ②cell 数(4 vs 2) ③WL 数(8 vs 4) ④层级深度(3 vs 4) ⑤port 顺序(scrambled vs sequential) ⑥storage 节点名(s1/s2 vs cc01/cc10) ⑦顶层 net 名(gw0..7 vs wl_top0..3) ⑧实例路径(xbank.xi5.xi3 vs xtop.xi1.xi6.xi2)。

**check.py 13 条**（a-m）：①zip+leak+size+compile ②B exit0+非空 JSON ③顶层键 ④traces 覆盖 spec nodes ⑤entry 结构 ⑥叶子 gate==oracle(g1/g2) ⑦顶层 net==oracle(gw6/gw7) ⑧链长==oracle(4) ⑨subckt 序列==oracle ⑩端口映射一致性(核心齿-真层级遍历) ⑪anti-hardcode A 缺席/B 在场 ⑫instance_path==spec ⑬3-seed sha256 一致。

**3 negs**：empty_shell(→a) / print_only(硬编 A→l/k/d) / core_removed(读 spec 但叶子硬编 wla→f/g/i/k)。§4.9 三假全 FAIL ✓。

**自验**：REF 13/13 PASS ✓；negative_selftest 3/3 FAIL ✓；3-seed 确定性 ✓；build_jsonl.py --shard B 收录（B.jsonl 535→536）。
