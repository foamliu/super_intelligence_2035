# w7spy — chapinc@hfeg0pkn002 (10.129.2.10) — layout_aether MOSFET inventory

**session_file**: `1794485797930_w7spy` (219 msgs, mc=381)
**user**: chapinc
**host**: 10.129.2.10 (= hfeg0pkn001 per r897 INFRA 纠偏)
**keywords**: cmos:6831; pyaether:507; aether:335; schematic:186; dbopencv:179; cellview:131; .lef:120; netlist:52
**domain**: layout_aether
**case_id**: EDA-Eval-DesignFlow-MosfetCellInventory-001 (shard C, r901)

## 用户原话 (U#0, verbatim)

> Count the type and name of the MOSFET used in the RWCbusGap_channelMid
> block, its size (W and L), and the voltage range it is in, as well as
> which lib library it comes from

## trace 流程摘要

chapinc 在 CXMT V0 DDR2 PHY 项目 (`/proj/m2701/V0_DDR2/`) 工作。block
实名为 `RWCbusGap_ChanMid`（非 `channelMid`），lib `degnt_cmos_digital`，
PDK `hlmc22ull`（22nm ULL）。assistant 经多条路径尝试：

1. 文件系统扫描（被 kill — 太重）
2. Virtuoso SKILL 桥（10.129.8.121:44527 已挂）
3. pyAether 桥（最终打通）—— 递归展平层级
   `RWCbusGap_ChanMid → SCmosRWCbusSC0Top → 大驱动 cell
   (SCmosDrvN1000u_RWABus / SCmosEnBufP2120N1060_H) → 实际 MOSFET`

提取到的 MOSFET 类型：
- `hlmc22ull.nuhvt_ckt` (NMOS UHVT) / `hlmc22ull.puhvt_ckt` (PMOS UHVT)
  — core 域，UHVT 器件
- `TECHLIB.NCH` / `TECHLIB.PCH` pcells — 巨 W 驱动（3200u–44096u）
- 层级很深，顶层无直接 MOSFET，全在 sub-block

assistant 最终产出一个 markdown 表格汇总（block 位置 / PDK / variant 副本 /
逐 MOSFET type+name+W/L+voltage+lib）。

## 为何 r538 判 REJECT，为何 r901 revive

- **r538 parked 理由**：`Q&A: count MOSFET in block` —— 旧规则把 Q&A /
  analysis / explain 类判为 weak 不可造。
- **2026-11-15 用户令**（候选池重审）：analysis-Q&A / doc-search /
  explain / retrieval 类**全部恢复为可造**——真实用户意图即合法任务。
- chapinc 的诉求是结构化的（type/name/W/L/voltage/lib per MOSFET），
  完全可以 reframe 成有牙的 `check()`：parse cellview JSON → filter
  mosfet → emit 结构化 report，断言 per-instance 字段 + by-type/by-lib/
  by-voltage 分桶 + anomaly flags。
- **唯一保留的排除标准只有两条**（11-15 令）：① 没有真实 trace ② 写不出
  能区分真假交付的 check()。w7spy 两条都过 → 可造。

## reframe 方案（档 B，fixture-driven judge）

**交付物** `mosfet_inventory.py <cellview_json> <out_json>`：解析扁平
cellview JSON → filter `type=="mosfet"` → 产出 `mosfet_report.json`
（顶层键 `cell_name/total_mosfets/by_type/by_lib/by_voltage/instances/
anomalies`）。

**A fixture**（SUT 可见，`RWCbusGap_ChanMid`）：8 MOSFETs
(nch_core×3, pch_core×2, nch_io×1, pch_io×1, native_nch×1) + 3 非 MOSFET
(2 res + 1 cap)；含 `degnt_cmos_digital/analog` lib；1 anomaly (missing L)。

**B fixture**（隐藏，base64 嵌 check.py，`RWCbusGap_ChanTop`）：11 MOSFETs
(nch_core×5, pch_core×4, nch_io×1, pch_io×1) + 2 非 MOSFET (1 res + 1 cap)；
**无 native_nch、无 analog lib**；2 anomalies (missing W + duplicate name)。
B 与 A 在 cell 名 / 数量 / 类型组合 / lib 组合 / anomaly 上全不同 → 硬编码
A 必败。

**k_check = 15 (a-o)**：①zip 含 mosfet_inventory.py>200B ②B 上 subprocess
exit0 产出 JSON ③7 顶层键 ④cell_name==B（非 A）⑤total==11（非 A 的 8）
⑥by_type 精确 B ⑦by_lib 精确 B ⑧by_voltage 精确 B ⑨instances 数+8 字段
⑩5 spot-check W/L 容差 0.001 ⑪missing_W=={M_b6} ⑫non_mosfet_excluded==2
⑬duplicate_names=={M_b7} ⑭anti-degenerate: native_nch 出现则 FAIL（A 指纹）
⑮非 mosfet master (rnpoly/cmim) 不得泄漏进 instances。

## 自验

- ref solve.py 打包 submit.zip → check PASS 15/15
- 4 负样本全 FAIL distinct：
  - neg_empty_stub → (a) trivially small
  - neg_print_fixed → (d) cell_name=RWCbusGap_ChanMid != B RWCbusGap_ChanTop
  - neg_no_filter → (o) 非 mosfet master 泄漏
  - neg_skip_anomaly → (k) missing_W=[] != B {M_b6}
- §4.9 (a)(b)(c) 三假提交全 FAIL：
  - empty shell → (a)
  - print-only B-fingerprint → (i) instances count=0 != 11
  - core-deleted ref → (f) by_type={} != B
- 3-seed 确定性：连跑 3 次全 PASS（ref 解确定性无随机）
- roundtrip：cases/C JSON.test == disk check.py sha256 1f49ff09 ✓；
  build_jsonl.py --shard C 重建 C.jsonl 563→564，含本 case
- JUDGE-tree 独立 /tmp/judge_mi dir PASS

## 11-15 审计状态

intent_audit_C.tsv：本 case 为 revival 新增，**符合任务初衷**
（真实 trace + 真实用户意图 + 有牙 check），标 `keep`。pool_reaudit_C.tsv：
w7spy 旧判 `parked-Q&A-不可造` → 新判 `可造-revived`。
