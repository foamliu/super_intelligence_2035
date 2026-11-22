# neh60 — dVOHdV2 ZQ-bias-reference fix (clarawu @ hfeg0pkn005)

## trace 溯源
- **session**: `1795163422684_neh60.messages.json`（55 msgs，1 user request）
- **user**: clarawu @ hfeg0pkn005 (10.129.32.75-side)
- **match_count**: 106（keywords: hspice:106）
- **domain**: spice_sim
- **case_id**: `EDA-Eval-DesignFlow-Dvohdv2ZqRefFix-001` (shard B, L1, k=12)

## 用户真实意图
clarawu 在做 DDR4 ZQ 校准电路的 dVOH/dV2 HSPICE 仿真。msg 0 附上 3 个 buggy dVOHdV2 激励文件（V2=0.82/0.85/0.88）+ 2 类参考激励（dRONdV2 测 dRON/dV2、dVOHdVQ 测 dVOH/dVQ），原话大意「dVOHdV2 仿真结果不对，参考 dRONdV2 和 dVOHdVQ 的接法帮我看看哪里写错了」。

## bug 定位（对照参考文件即得）
3 个 dVOHdV2 文件里 **12 个 ZQ 偏置电压源**（`vZqPu0-5` + `vZqPd0-5`）的 DC 表达式写成：
```
DC='zqpuX*VVDD2CS'   /   DC='zqpdX*VVDD2CS'
```
但 `VVDD2CS` 是被 `.dc VVDD2CS POI 3 'V2-0.001' 'V2' 'V2+0.001'` **扫描的节点**（`.param VVDD2CS='V2'`）。ZQ 偏置应当参考**固定的 corner 电源 VVDD**，参考文件 dRONdV2 / dVOHdVQ 里 ZQ 源接的都是：
```
DC='zqpuX*VVDD'   /   DC='zqpdX*VVDD'
```
用 `VVDD2CS` 会让 ZQ 偏置在每个扫描点上漂移，污染 dVOH/dV2 测量。

## 修复
把 3 个文件里 12 个 ZQ 源行的 `VVDD2CS` 换成 `VVDD`，**其余行逐字保留**：
- `.param V2=0.82/0.85/0.88` — 保留（V2 是扫描中心）
- `.param VVDD2CS='V2'` — 保留（扫描变量定义）
- `.dc VVDD2CS POI 3 ...` — 保留（扫描语句）
- `.meas dc VOH_V2_minus1/0/plus1` — 保留
- `.lib '../zqcode_75pvt.sp' ZQCODE_FF/TT/SS_25C_0P8xV_0P5V` — 保留（3 corner）
- `.inc '../../netlist_delvto'` — 保留（netlist）

agent 在后续 msgs 里逐个 editor call 修正了 3 个文件（16 个 editor call 全是改 ZQ 源行）。

## reframe（L1 produce 工具）
把「手工修 3 个固定文件」reframe 成参数化 `fix_zqref.py`：
```
python3 fix_zqref.py --in-dir <buggy_dir> --out-dir <fixed_dir>
```
逐文件扫 `vZqPu*` / `vZqPd*` 行，把 DC 表达式里的 `VVDD2CS` 换成 `VVDD`，其余行逐字保留。

## hidden B（anti-hardcode-A）
3 个合成 buggy 文件，V2=0.90/0.95/1.00、corner `_0P90V_`/`_0P95V_`/`_1P00V_`、`.inc '../../netlist_dvoh_b'`、`.lib '../zqcode_b_pvt.sp'`，同 ZQ=VVDD2CS bug。A 专属 marker（`0P82V/0P85V/0P88V/netlist_delvto/zqcode_75pvt.sp`）不得出现在 B 输出或源码。

## check.py 12 齿（k=12）
(a) zip+py_compile  (b) run B exit0+3 文件  (c) 12 ZQ 源全用 *VVDD  (d) vZq 行无 VVDD2CS 残留  (e) ZQ 计数==12  (f) `.param VVDD2CS='V2'` 保留（击败全局替换）  (g) `.dc VVDD2CS POI 3` 保留（击败全局替换）  (h) `.param V2=<val>` 保留  (i) 3 `.meas` 保留  (j) 3 corner tag 保留  (k) anti-hardcode-A  (l) 3-seed determinism

§4.9 三假（empty/print-only/core-removed）全 FAIL；naive-global-replace 假提交 FAIL (f)(g)。

## 自验
- ref `fix_zqref_ref.py` PASS 12/12
- 3 negs（empty/print-only/core-removed）全 FAIL，distinct teeth (a,b / b / c,d)
- 3-seed deterministic（sha256 一致）

## distinct 说明
neh60 与 e0039786(e692a) DBC varactor deck-gen（shard B r1001 已落库）主题完全不同：neh60 是「定位 ZQ 偏置参考点 bug 并批量修复既有 deck」，e692a 是「据参考 deck 生成一系列不同电性测试的新 deck」。neh60 的 16 个 editor call 全是改 ZQ 源行（fix），e692a 是产出新文件（produce）。fix vs produce 主题 distinct。
