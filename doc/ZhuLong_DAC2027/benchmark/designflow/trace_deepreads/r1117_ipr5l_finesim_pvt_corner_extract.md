# trace_deepread: ipr5l — junyin FineSim PVT corner summary (DQIB_DFE tbt IP)

- **session**: `1794967361667_ipr5l` @ `junyin` / `hfeg0plg74`
- **scan**: ssh_eda_search_20261123_064315, mc=5, keywords: hspice:6 / schematic:4 / cmos:4 / netlist:3 / pex:1 / analog:1
- **size**: 4 msgs / 19 KB messages.json (agent=lead)
- **shard/domain**: B / spice_sim ✓

## 用户真实意图（U0）

U0: 「`/proj/ddgoa/V0/simdir/finesim/workdir/cokwang/simulation/ddgoa_cmos_work_cokwang_RxDfe_feedback_schematic_ALPS/01_DQIB_DFE_tbt_IP.sp` 总结一下这里面所跑的corner 温度+电压+corner」

— 给一个 FineSim SPICE deck，要 agent 总结里面跑的 PVT corner（温度+电压+工艺角）。

## assistant 工具链与关键产物

1. `read_files` 读 `.sp` 文件（178 行 / 8.2KB）。
2. 直接分析 deck 结构，产出 markdown 表总结。

## 关键分析结论（A[3]）

deck 结构（`01_DQIB_DFE_tbt_IP.sp`）：
- 顶部全局 `.param pvcc=0.9 pvdd1=1.8 pvddq=0.5 ...`（pvcc 默认 0.9V）
- `.tran 10p 45n sweep dq POI 10 80m 85m 90m 100m 105m 170m 165m 160m 150m 145m`
- 默认段：`.temp 45c` + `.lib model.sp tt` + bjt_tt/res_tt/nicap_tt/diode_tt
- 8 个 `.alter` 段：
  | # | MOS | BJT/Res/Nicap/Diode | temp | pvcc |
  |---|-----|---------------------|------|------|
  | 1 | ss | ss | -40 | 0.92 |
  | 2 | ss | ss | 130 | 0.92 |
  | 3 | ff | ff | -40 | 0.82 |
  | 4 | ff | ff | 130 | 0.82 |
  | 5 | sf | **tt** | -40 | 0.92 |
  | 6 | sf | **tt** | 130 | 0.92 |
  | 7 | fs | **tt** | -40 | 0.82 |
  | 8 | fs | **tt** | 130 | 0.82 |
- **核心齿**：sf/fs 段无源器件用 tt（不跟随 MOS corner），必须逐行读 `.lib incFile_lp bjt_tt` 才能得出。
- 共 9 条件（1 默认 + 8 .alter），每条 `.tran` 还嵌套 10 个 DQ sweep 点 = 90 子仿真。

## reframe（合成 case = EDA-Eval-DesignFlow-FinesimPvtCornerExtractProduce-001）

**核心可程序化部分** = FineSim PVT corner 提取器：给一个 deck + spec，解析出每个仿真条件（默认段 + .alter 段）的 MOS/BJT/Res/Nicap/Diode corner、温度、pvcc（全局默认 + alter 覆盖），以及 .tran sweep 信息，输出 summary.json + report.md。

**为何合法真实意图**：用户 U0「总结 corner 温度+电压+corner」本质是 PVT 条件结构化提取——这是 spice_sim 域真实分析/查询意图，11-15 令明确合法。reframe 把「总结」固化成可执行交付物（Python 提取器），check() 用独立 oracle 在隐藏 B 上校验。

**A deck**（faithful）：真实 01_DQIB_DFE_tbt_IP.sp，9 条件，tt/ss/ff/sf/fs，无源 sf/fs→tt，45c/-40/130，pvcc 0.9/0.92/0.82，.tran 10p 45n POI 10。

**hidden B**（7 维 anti-hardcode）：
1. 条件数 7（1 默认+6 .alter）vs A 9
2. MOS [tt,ff,ff,ss,ss,sf,fs] vs A [tt,ss,ss,ff,ff,sf,sf,fs,fs]
3. 温度 25/-55/110 vs A 45/-40/130
4. pvcc 0.88/0.81/0.95 vs A 0.9/0.92/0.82
5. **无源映射 sf→ff、fs→ss** vs A sf/fs→tt（核心齿——硬编"sf/fs→tt"必败）
6. .tran 5p/20n POI 8 vs A 10p/45n POI 10
7. 模型路径 /proj/auriga/V2/model/rel2.0/primitive vs A /proj/ddgoa/V0/model/current

**check.py 14 条**（a-n）：①zip+compile+size ②B exit0+summary.json+report.md ③顶层键 ④n_conditions==7 ⑤条件字段齐 ⑥MOS 序列 ⑦temp 序列 ⑧pvcc 序列 ⑨bjt 序列(核心齿-sf→ff/fs→ss) ⑩tran sweep var/type/n ⑪tran tstep/tstop ⑫anti-hardcode A token 缺席 ⑬report markdown 表行数 ⑭3-seed sha256 确定性。

**3 negs**：empty(→③缺键) / print_only(硬编 A 9 条件→④n=9/⑥⑦⑧⑨全错/⑫泄漏) / core_removed(真解析但无源跟 MOS→⑨ bjt sf/fs≠ff/ss)。

**自验**：REF 14/14 PASS ✓；negative_selftest 3/3 FAIL ✓（§4.9 三假齐）；REF on A 正确得 9 条件 ✓。

**台账**：ipr5l claim→mark case ✓。
