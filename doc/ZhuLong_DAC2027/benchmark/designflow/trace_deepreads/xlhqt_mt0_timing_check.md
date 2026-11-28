# xlhqt deepread — NanoSpice .mt0 timing-window check (RDQS pair check)

- **trace**: 1795658202485_xlhqt · alexli @ hfeg0plg101 · mc65 (netlist:254/cmos:38/waveview:8/aether:8/schematic:2)
- **session**: 644KB / 196 msgs (102 user / 94 asst) · agent=lead · 2 `<user_input mode=act>` blocks
- **date**: 2026-11-29 r1677

## 用户真实意图

P2S (parallel-to-serial) DDGOA 适配项目的 timing-check skill 续作。用户在 RDQS pad 侧要验证 5 个数据/时钟信号对（DOE/net11/DNNER_0/DatLat/DNNOR_0）的边沿是否落在参考时钟的高电平窗口内（setup/hold）。用户明确规则：**信号按发送顺序每 2 个一组**（data, clock），奇数个直接报错不要猜配对。

trace 核心是助手交付 `rdqs_pair_check.py`（14870 字节）—— 一个 NanoSpice `.mt0` 解析 + 边沿-窗口判分器。助手在过程中踩了 6 个真实 bug，全部编码为断言。

## 助手工具链（produce 方向）

1. `_rdqs_audit.py` / `_rdqs_probe*.py` — 审计污染脚本 + fsdb 节点可读性探测
2. `_rdqs_resolve*.py` / `_rdqs_hier*.sh` — netlist 层级解析（`XI_DQByteHi`→`DQByte`→`XI_DqPad_0`/`XI_RDqsPadX2`）
3. `_seed*.sh` — 受控小实验确认 `.mt0` 双位置写入 + `failed` token
4. **`rdqs_pair_check.py`** — 最终交付：`.mt0` 解析 + per-node 50% swing threshold + crossing 提取 + high-window 构建 + setup/hold/inside 判分 + direction 反转

## 可移植核心算法（叙事高潮）

**NanoSpice .mt0 timing-window analyzer**：

1. `make_pairs(signals)`：按顺序 2 个一组拆 (data, clock)；**奇数个直接 raise PairsError**（不按名字相似度猜配对——上次猜配对结论全错）
2. `read_mt0(workdir, label)`：`.mt0` 同时写在 `<label>.mt0` 和 `<label>.output/finesim.mt0` 两处，**两处都要找**（只读一处→所有节点"absent"）
3. `as_num(v, key)`：`failed`/absent → None（**不 float('failed') 崩，不当 0**）
4. `swing_and_threshold`：per-node 50% own swing（**非固定 0.45V**——低摆幅节点 0.45 抓不到边沿）
5. `crossings`：`.meas tran x_u_<tag><k> when v(node)=thr rise=<k>`，时间转 ps：`(t - T0)*1e12`（T0=1us，4 sig digit → 0.1ps 绝对精度）
6. `high_windows(rises, falls, max_width=600)`：**rise → 之后第一个 fall**（NOT rise_k/fall_k 索引配对），窗口宽 >max_width 丢弃（burst 间隙非捕获窗口）
7. `judge(data_edges, windows)`：per edge 最近窗口（min|edge-start|,|edge-end|），setup=|edge-start|, hold=|end-edge|, inside=(start≤edge≤end)
8. **direction 反转**：data/DOE 侧 inside=PASS（outside=violation）；NAND 侧 inside=FAIL（outside=PASS）—— 两侧判据相反，搞反会让所有结论反转

## 关键 gotcha（可移植核心，造题显性化）

- **G1 `.mt0` 双位置**：NanoSpice 把结果同时写 `<label>.mt0` 和 `<label>.output/finesim.mt0`；只读一处→节点全 absent
- **G2 `failed` token**：不可解析节点打印字面 `failed`；`float('failed')` raise → 误判"节点不存在"；必须 None 化
- **G3 per-node 50% threshold**：固定 0.45V 抓不到低摆幅节点（mx=0.6/mn=0.2 → thr=0.4 非 0.45）
- **G4 rise→first-fall-after**：rises=[100,300,500] falls=[200,600] → windows=[(100,200),(300,600),(500,600)] 3 个；索引配对 rise_k/fall_k → [(100,200),(300,600)] 2 个（漏 rise500）。不同！
- **G5 max_width 丢弃跨间隙**：窗口宽 >600ps 是 burst 间隙非捕获窗口，必须丢
- **G6 make_pairs 奇数拒绝**：5 信号直接 PairsError，不按名字猜配对（上次猜配对→结论错）
- **G7 direction 反转**：data 侧 inside=PASS / NAND 侧 inside=FAIL，搞反结论全反
- **G8 T0 ps 转换**：x_u/x_d 在秒（~1e-6），转 ps 用 (x-T0)*1e12；不转→~1e6 ps 错值
- **G9 non-toggling 检测**：mx-mn<1e-3 → 节点不翻转，报错（不输出假 setup/hold）
- **G10 PRIMER**：第一条 .meas 被丢，须加 primer（deck 生成细节，reframe 不测）

## 可移植判定

原 deliverable 依赖 NanoSpice 二进制 + fsdb + 项目私有 netlist → 不可直接移植。

**可移植抽象** = 纯 Python `.mt0` 文本解析 + timing-window 判分器：输入 spec-JSON（含 `mt0_text` 原始 .mt0 文本 + `signals` 顺序列表 + `direction` + `t0_s`/`max_window_ps`/`n_cross`）→ 输出 report.json（per-pair windows/rows/summary + direction 判分 + 确定性 md5）。无 NanoSpice/fsdb/EDA 二进制依赖。

## 与既有 case 区分（避免 dup）

- **FsdbHierFaninTrace-001**: FSDB 层级 fallback + fanin trace（波形读取，非 .mt0 解析）
- **PwlTimingExtractProduce-001**: PWL 波形 50% crossing 提取（波形解析，非 .mt0 列解析）
- **MeasDeckHierGenProduce-001**: .MEAS deck 生成（生成 deck，非解析 .mt0 结果）
- 无既有「NanoSpice .mt0 列解析 + edge-vs-window setup/hold 判分 + direction 反转」类 case。

## 造题计划

**case EDA-Eval-DesignFlow-Mt0TimingWindowCheckProduce-001** (schematic_netlist, LIVE-NA, judge=[L0,L1])。

- candidate `mt0_timing_check.py(spec_path, out_path)`：parse mt0_text → dict{col:raw} (keep `failed`) → make_pairs (reject odd) → per-pair swing/toggle-check → crossing ps 转换 (T0) → high_windows (rise→first-fall-after, max_width) → judge (nearest window, setup/hold/inside) → direction 反转 → summary → report.json
- A/B 双输入：A (data_side, DOE/net11/DNNER_0/DatLat, 2 pairs) vs B (nand_side, Qout/ClkA/Qbar/ClkB, 2 pairs, token-structurally 不相交)；额外 hidden spec_B_odd (5 signals odd→reject) + spec_B_nontoggle (mx-mn<1e-3→error)
- check.py ≥16 断言 (a,b 静态 + c..p L1 judge-run on hidden B + odd-spec + nontoggle-spec)
- 7 个 captured bug 编码：B1 failed→None / B3 first-fall-after / B4 max_width drop / B5 odd reject / B6 direction / B7 T0 ps / B2' non-toggling
- §4.9 negatives 6 个 first-fail distinct
- LIVE-NA: 纯 Python 无 EDA 二进制，不入 live_eval_changes.tsv
