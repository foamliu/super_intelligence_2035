# Deepread: 1795480920609_s21dt — FzCPSelX16 fn.sp 批量激励生成

- **trace_source**: user=krisluo, host=hfeg0pkn002, session=1795480920609_s21dt.messages.json, mc=151, domain=schematic_netlist
- **scan**: ssh_eda_search_20261128_164430/summary.tsv, D-dominant (schematic:1965;cmos:1962;verilog:20;netlist:18;pex:4), FRESH, NEW-ish user (krisluo 在 B/D 台账有别的 session 但本 session 未 claim)
- **trace size**: 1.54MB, 363 msgs (190 user / 173 assistant), agent=lead
- **真实上下文**: krisluo 在 FineSim/ALPS 后仿 DRAM digital cell `FzCPSelX16` (schematic) 的冗余列编程(redundant-column programming)激励。`fn.sp` 是 16 个 8-bit 信号 `Fn_0..Fn_15` 的 SPICE 电压源激励文件, 每位 `1=pvdd2h / 0=0`, 行格式 `vFn_{N}<{bit}> Fn_{N}<{bit}> 0 {val}` (bit 7..0)。

## 用户真实意图（可合成核心）

用户要**批量生成 fn.sp 激励文件**, 两套规则:

### 规则 A: 384 组合（gen_fzcp384.py, msg13, 核心）
每个 fnN 是 8-bit = `<7:5>` 高3位 + `<4:0>` 低5位:
- **<7:5> 分组 + 加一回卷**: fn0-3=B, fn4-7=(B+1)%8, fn8-11=A, fn12-15=(A+1)%8。A,B 各 0..7 → 8×8=64
- **<4:0> 互补规则**: 偶数下标 fn = x, 奇数下标 fn = ~x (5-bit 按位取反); fn8-15 与 fn0-7 共用同一个 x → 6 种 x
- **6 个基值**: BASE4_0 = ["00110","00101","01001","01010","01101","01110"], 互不相同 且 任一基值 ≠ 另一基值的互补 (assert 校验)
- **总计**: 8(A) × 8(B) × 6(x) = **384**, 输出 run_0000..run_0383/fn.sp + combos.txt(参数对应表)
- 编码: bit=1→`pvdd2h`, bit=0→`0`; value=(hi<<5)|lo

### 规则 B: 1000 组随机（gen_fn_random.py, msg221, 较简）
每个 fn.sp 16 组, 每组 8-bit 三段独立均匀随机:
- `<7:5>` 0..7, `<4:2>` 1..6 (001..110), `<1:0>` 1..3 (01..11)
- SEED 可复现, FILENUM 可调, 输出 random_seed.txt

## 后段（不合成）
- 新测量方法: 上升沿→上升沿 + 上升沿→下降沿 delay, 5ns 窗口找最大, 64 窗口找"最大值中的最小值", 阈值 350ps waive (msg44/200/326/357) — 涉及真实 FineSim 跑 + .mt0 解析, 强依赖仿真器产物, 不合成 produce 题
- check_fn540.py / parse_min_delay.py / report_train384.py 是结果分析脚本, 非激励生成核心

## 真实用户捕获的约束（编码为断言牙）
1. **<7:5> 4-组分配 + +1 回卷**: fn0-3=B / fn4-7=B+1 / fn8-11=A / fn12-15=A+1, 满 111 回卷 000 (用户 U#2 "前者fn<7:5>是000，那后者就001...总共8种")
2. **<4:0> 偶=x 奇=~x 互补**: 5-bit 按位取反 (用户 U#2 "间隔的fn<4:0>要是反码")
3. **fn8-15 与 fn0-7 共用 x**: 上下半 x 相同 (用户 U#3 "fn8-15的<4:0>和fn0-7的<4:0>完全一样")
4. **6 基值集**: 固定 6 个, 互异 + 无互补重叠 (助手 assert; 用户 U#2 列举 12 个其实是 6 互补对)
5. **pvdd2h/0 编码 + bit 7..0 行序 + 16 fnN 块 + 空行分隔**
6. **combos.txt 参数对应表**: run, A, B, k, x

## case 合成 plan（下轮交付，DEBT: 1）

- **task_id**: `FzcpFnDeckGenProduce-001`
- **domain**: schematic_netlist
- **reframe**: spec-JSON 驱动纯 Python FzCPSelX16 fn.sp 激励 deck 批量生成器 `gen_fzcp_fn_deck.py(spec.json, out_dir)` → `run_XXXX/fn.sp` + `combos.txt` + `report.json`。无真实 EDA 二进制依赖(纯文本生成)。**LIVE-NA**, `judge_layers=[L0,L1]`
- **A (visible)** spec_A.json: cell=FzCPSelX16, pvdd2h_token=pvdd2h, base_values=BASE4_0 6 个, hi_groups 4 组(B/B+1/A/A+1), hi_wrap=8, lo_rule even=x/odd=complement_x/shared, A_range=[0,7], B_range=[0,7], num_bits=8, num_fn=16
- **hidden B (token-structurally 不同)** spec_B.json: cell=RedColProgX8, pvdd2h_token=vddh, **不同** 6 基值(满足互异+无互补重叠, e.g. ["00011","00100","01000","01011","01100","01111"]), hi_groups 重新分组(e.g. fn0-1=A / fn2-3=A+1 / fn4-5=B / fn6-7=B+1 / fn8-9=C / fn10-11=C+1 / fn12-13=D / fn14-15=D+1 四参数 A/B/C/D 各 0..3 → 4×4×6=96 组), num_fn=16, lo_bits=5 → A 硬编码器在 B 全错
- **reference** `gen_fzcp_fn_deck.py` spec 驱动通用实现(validate 必填→malformed raise; 迭代 A_range×B_range×base_values; hi=(param+offset)%hi_wrap; lo=x if N%2==0 else complement; value=(hi<<lo_bits)|lo; 行 `vFn_{N}<{bit}> Fn_{N}<{bit}> 0 {tok}` bit 7..0; combos.txt + report.json{total_runs,cell,pvdd2h_token,A_range,B_range,num_base})
- **check.py ~16 conds**: 独立 gold 复算(不同代码路径: 显式 for 枚举 + 位运算) →
  - a zip 含 gen_fzcp_fn_deck.py ② b py_compile ③ c A 运行产 384 run 目录+combos.txt+report.json ④ d A run 数==8*8*6==384 ⑤ e A 每 fn.sp 16 块×8 vFn 行 bit 7..0 ⑥ f A gold 复算 <7:5> 4-组+回卷 (抽验若干 run) ⑦ g A gold 复算 <4:0> 偶=x 奇=~x 互补 ⑧ h A pvdd2h/0 编码正确 ⑨ i A combos.txt 映射 == gold ⑩ j A report.json schema 键全 ⑪ k anti-hardcode tokenize 剥注释/字符串/docstring 源码扫描无 A-only 字面 token (cell/base_values/pvdd2h 必须从 spec 读) ⑫ l 确定性: 重跑 A2 fn.sp md5 一致 ⑬ m hidden-B 运行产 B 特定 cell/token 输出 ⑭ n hidden-B gold 复算 (不同基值/分组/token, A 硬编码器失败) ⑮ o B run 数 == B_spec 的 gold (e.g. 96) ⑯ p B pvdd2h_token=vddh 非 pvdd2h (跨输入守卫)
- **negatives (≥4, §4.9 trio distinct)**: empty→c / print_only→c / core_deleted→f 或 g / hardcode_a→n 或 p
- **自验**: SKIP_RUN=1 eval/run_one.sh FzcpFnDeckGenProduce-001 --shard D → PASS; ref solve.py 跑 check PASS; negative_selftest 全 FAIL distinct; sha 3-way sync
- **风险**: 无 (纯 Python 文本生成, 无 EDA 二进制依赖, 规则清晰可独立 gold 复算)

## 候选开采记录
scan=ssh_eda_search_20261128_164430 (58417 行, 最新完整), D-dominant 过滤(D-set netlist/schematic/waveview/waveform/analog/cmos/verilog/aether/pyaether/cellview/spectre/skill/spiros/spectrum/cosmos; bad-set 排除 drc/gds/calibre/lvs/pex/innovus/floorplan/layout/vcs/siliconsmart/ngspice/custom_sim; hspice<5/finesim<5; dom≥total*0.4 且 bad≤dom*0.5), mc≥5 去重 → 2444 候选。mc≥200 全 claimed 或碎片化用户(junxu/e0031668/jason17w/e0039602/wellesc 等)。转 mc 15-200 mid-range 1575 候选, 对 4-shard 台账(4696 unique bare slug)验 fresh → 390 fresh。剔除碎片化用户, 按 DSTRONG(netlist/schematic/cmos/aether/pyaether/waveview) 占比排序 → 选定 s21dt(krisluo, mc=151, schematic:1965+cmos:1962 主导, bad=4 仅 pex, FRESH, 本 session 新任务)。.75 eda_flow open_session 秒级 + ssh→hfeg0pkn002 per-session subdir scp 取回 1.54MB/363msgs 直读成功。
