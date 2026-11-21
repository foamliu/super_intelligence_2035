# Deepread — 1795057180298_esbdu · FineSim si.inp ignore audit

- **session**: `1795057180298_esbdu.messages.json`
- **user / host**: kevin3d @ hfeahpc503
- **mc**: 71 (spice_sim; netlist:391 / analog:179 / hspice:22 / cmos:19 / lvs:16 / synopsys:10)
- **round**: r968 (shard B)
- **case_id**: `EDA-Eval-DesignFlow-FinesimIgnoreAudit-001`
- **形态**: A-faithful analysis-Q&A deck-audit (L1 离线 Python 解析) — 11-15 重审后合法

## Trace shape (real user wording, verbatim)

U[0] (用户粘贴 `grep -i ignore finesim .../si.inp` 输出 + `cat IGNORE_PROBE_INST.list` 输出, 然后):
> 把上面的ignore有效的，需要补进inst的name给我

U_idx9 (后续追问):
> 从si.inp的ignore来看，active的bank有哪些？

U_idx13: zpower filter check; U_idx41: low-freq 3200 run check; U_idx57: zpower trim + ignore analysis.
(本轮只取 U[0] + U_idx9 两条 core asks 造 case; 其余作为 trace 真实性佐证.)

## si.inp 结构 (A 档, 真实 trace 原文)

`.option finesim_ignore` 行分 3 类:
1. `*.option finesim_ignore = "..."` / `***.option ...` — SPICE 注释行 (行首 `*`), **不算**有效
2. `.option finesim_ignore = "Name"` — 有效 (单名)
3. `.option finesim_ignore = "xI_A_Top...XI_BankGap_Nicap" **B0` — 有效, 引号后 `**B0` 是 bank 号尾巴注释

decoy: `.option finesim_ignore_chkfunc_error=1` — 另一个 option, **不是** finesim_ignore (finesim_ignore 后跟 `_chkfunc_error` 而非 空白/`=`)

有效行结构 (A):
- 6 抽象单名: nan / Thin_FsAllTop_cap_new / thick_fsalltop / TS_Sref_Top / Thin_FsAllTop / spine_cap_top
- 16 BankGap_Nicap 行 (全 16 bank B0-BF, 每行 `xI_A_Top.xI_Ary8G_{W,E}.xI_Array1GBK<x>.XI_BankGap_Nicap`)
- 7 DLDO 行: DLDO_ChanRight/ChanLeft/ChanMid/ArrayCtrlx4/ArrayCtrlx4AC/ArrayCtrlx4B/ArrayCtrlx4A
- `* Ignore cell *` 块: 13 ignored bank × 2 行 (A_Top 行 + C_Top 行), 每行带 `**B<x>` 尾巴
- 共 55 有效行, 55 distinct names

IGNORE_PROBE_INST.list (A, 42 行):
- 16 BankGap 行 (全 16 bank, `XI_A_Top.XI_Ary8G_{W,E}.XI_Array1GBK<x>.XI_BankGap_Nicap`, 大写 XI_ 前缀)
- 26 bank-level 行 (13 ignored bank × 2: `XI_A_Top.XI_Ary8G_{side}.XI_Array1GBK<x>` + `XI_C_Top.XI_Array16GTop.XI_Array8G_{side}.XI_Array1GBK<x>.XI_m1G_TOP`)

## 答案 (A)

- effective_ignore_count = 55
- effective_ignore_names = 55 distinct
- missing_from_inst_list = 13 (6 抽象 + 7 DLDO; instance 路径全在 list 中大小写不敏感匹配)
- ignored_banks = {0,1,3,4,5,6,7,8,9,B,C,D,F} (13)
- active_banks = {2,A,E} (3)  ← 16 - 13
- active_banks_dec = [2,10,14]

## Case 设计

交付 `finesim_ignore_audit.py` 通用 si.inp 解析器 (读 spec.json → 解析 si.inp+inst list → 写 audit_result.json, 6 字段).

hidden B 由 A 经 `build_variant.py` 确定性派生:
- 10 instance token 重命名 (xI_A_Top→xInstA_Top, xI_Ary8G_W→xArr_West, xI_Array1GBK→xBank1G, XI_BankGap_Nicap→XIBankGapNicap, xI_m1G_TOP→xM1gTopInst, ...) 跨 si.inp + inst list 一致应用 → 重命名后 instance 路径仍大小写不敏感匹配 (故不进 missing)
- 13 ignored bank 换组: A {0,1,3,4,5,6,7,8,9,B,C,D,F}→active{2,A,E}; B {0,2,3,4,5,6,7,8,9,A,B,C,F}→active{1,D,E}
- 2 行多名有效 ignore 新增 (DecapTopA/B/C + VrefGenA/B) → B missing 18 ≠ A 13 (anti-hardcode-A)
- B 残留 A token = 0

## 答案 (B)

- effective_ignore_count = 57 (55 + 2 多名行)
- effective_ignore_names = 60 distinct (55 + 5 新名, 因多名行 5 name 在 2 行)
- missing_from_inst_list = 18 (13 A-shared + 5 B-only)
- ignored_banks = {0,2,3,4,5,6,7,8,9,A,B,C,F}
- active_banks = {1,D,E}
- active_banks_dec = [1,13,14]

## check.py (14 条 a-n, k_rationale==k_check==14)

a zip 含 3 文件 / b py_compile / c bash -n / d run.sh exit 0 产 JSON / e 顶层键齐全 /
f eff_count 独立 grep / g eff_names 集合独立 grep / h missing 集合独立复算 (大小写不敏感) /
i ignored_banks 独立 grep **Bx / j active_banks={0..F}-独立 grep / k active_dec=hex2int /
l anti-hardcode-A missing≠A / m anti-hardcode-A active≠A{2,A,E} / n 2 次确定性

## 自验

- ref PASS 14/14
- negative_selftest 4/4 FAIL: neg_empty→d, neg_print→d, neg_core_removed→f, neg_hardcode_a→j
  (neg_hardcode_a = 解析 B 正确但硬编码 A 的 active_banks {2,A,E}, fail at j)

## 落库

- cases/B 491→492, B.jsonl (build 产物) 489→490
- ledger_B case 650→651, spice_sim
- mc≥10 fresh 282→281 (本轮 claim esbdu mark case)
