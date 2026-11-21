# 修复计划 — EDA-Eval-DesignFlow-SaNPTrannoiseFix-001 (anti-hardcode 修复轮 #10 候选)

> 本文件为 **fix-prep 产物**（r1076 修复准备轮）。r1076 只做 runtime GAP 确认 + A' fixture 设计 + A'-gold 计算 + 计划撰写，**未改 check.py / D.jsonl / audit TSV**（守红线：未过闸门不改 jsonl）。下一轮按本计划执行 check.py 重写 + 自验 + jsonl sync。

## 0. 案况

- **case**: EDA-Eval-DesignFlow-SaNPTrannoiseFix-001 (schematic_netlist, audit Top10 之外, k=11)
- **任务形态**: script-deliverable — 候选提交 `fix_spice.py`，判分器只在 hidden B testbench 上跑候选 + spice_lint.py 真跑，修 5 类缺陷 (1: MOSFET W/L 越界 clamp; 2: mode=promd→spicemd; 3: .option list 注释; 4: .trannoise 内联参数+删 orphan; 5: .option ARTIST post=2 删除)
- **现有 anti-hardcode**: 仅 (j) visible-A guard — 跑候选 on visible A (Check_SaNP_tb_A.sp 在 SUT 沙箱内)，要求 A clamp 值 ≠ B clamp 值 + A 输出 lint PASS。这正是 r1069 印证的 **visible-A guard 无效** 范式（A 可见即可被 stub 读取特判）。

## 1. Runtime GAP 确认（r1076 实测，附可复现命令）

**可复现命令**（在 EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/ 下）：
```bash
REF=reference/EDA-Eval-DesignFlow-SaNPTrannoiseFix-001
AST=assets/EDA-Eval-DesignFlow-SaNPTrannoiseFix-001
SCR=/tmp/sanp_prep
# 1) build reference_submit.zip (golden → fix_spice.py)
cp $REF/golden_fix_spice.py $SCR/fix_spice.py && (cd $SCR && zip -q reference_submit.zip fix_spice.py)
# 2) ref self-verify → PASS
python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('c','$REF/check.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.check('$SCR/reference_submit.zip','$PWD'); print('REF PASS')"
# 3) smart §4.9(b) B-hardcode stub (见 fix_prep_SaNPTrannoiseFix-001/neg_fake_hardcode_b.py)
#    keyed by input md5: A→A-gold, B→B-gold, unknown→B-gold fallback
cp $SCR/neg_fake_hardcode_b.py $SCR/fix_spice.py && (cd $SCR && zip -q -X fake_stub.zip fix_spice.py)
python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('c','$REF/check.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.check('$SCR/fake_stub.zip','$PWD'); print('STUB PASS = GAP')"
```

**实测结果**：

| 假提交 | 结果 | 失败条件 |
|---|---|---|
| §4.9(a) empty_shell | FAIL | (b) B 输出空 |
| §4.9(b) print_only | FAIL | (c) lint FAIL (输入未改) |
| §4.9(c) core_deleted | FAIL | (c) lint FAIL (输入未改) |
| **smart B-hardcode stub** | **PASS (GAP!)** | — 通过全 11 (a-k)，含 (j) visible-A guard |

**结论**: audit TSV 静态标的 `print_only=PASS, core_deleted=PASS` 是 **误报**（运行时实测均 FAIL，与 r1069/InvSpiceSim 同结论）。真 GAP = smart §4.9(b) B-hardcode stub 通过全 11 — 印证 r1069「visible-A guard 无效」病灶泛化到 SPICE-fix 类 case。

## 2. 病灶根因（同 r1069/r1074）

visible-A guard (j) 跑候选 on A，但 **A 在 SUT 沙箱内**，smart stub 读输入 md5/特征串特判：A→吐 A-gold，B→吐 B-gold，unknown→B-gold fallback。stub 不做任何真实计算，仅查表吐预烘焙 golden，故 (j) A clamps≠B clamps 被绕过，全 B-side (b-i) + (k) 确定性也被绕过（同输入→同输出）。

## 3. 修复范式（沿用 r1074 hidden-A' 文件式，适用于 script-deliverable）

新增 **隐藏 A' testbench**（SUT 不可见，judge 经 `HERE=dirname(__file__)` 读取 `reference/<id>/hidden_a/`，无 base64 腐蚀风险）。A' 与 A、B **token 结构性不相交**：

| 维度 | A | B | A' (新) |
|---|---|---|---|
| corner | TT 1.166V 25C | SS 0.95V -40C | **FF 1.35V 125C** |
| model | ntnlv_hlsa | ntnlv_hlsa | **sns_hv_nmos** |
| subckt | pcs_loading | pcs_loading | **sns_chain** |
| 实例 | xmmn13 | xmmn0/xmmn1/xmmn13 | **xmson0/xmson1** |
| 级数 | 1-stage | 3-stage | **2-stage** |
| 电阻 | 1k | 2.2k | **1.5k** |
| .tran | 1n 100n 0 1n | 2n 200n 0 2n | **0.5n 50n 0 0.5n** |
| DCON | 1 | 2 | **3** |
| noise | fmin=10 fmax=10G seed=1 | fmin=100 fmax=5G seed=7 | **fmin=50 fmax=20G seed=42** |
| W clamp | xmmn13 W 0.620736u→0.9u | xmmn0 W 0.45u→0.6u | **xmson0 W 0.75u→1.0u** |
| wmin/wmax | 0.9/1.6u | 0.6/1.2u | **1.0/2.0u** |
| lmin/lmax | 0.048/0.050u | 0.040/0.060u | **0.050/0.070u** |

A' 含全部 5 类缺陷（mode=promd / .option list / .trannoise 无内联+orphan / .option ARTIST post=2 / xmson0 W 越界）。

## 4. A'-gold（golden_fix_spice.py 在 A' 上实测，见 fix_prep/rep_Ap_gold.json）

```
defect1: instance=xmson0, subckt=sns_hv_nmos, param=W, old=7.5e-7, new=1.0e-6
defect2: mode promd→spicemd
defect3: .option list 注释
defect4: fmin=50, fmax=20g, noiseseed=42
defect5: ARTIST post=2 删除
n_defects=5, spice_lint overall=PASS
```

**stub on A' 实测**（fix_prep/rep_Ap_stub.json 未存，运行时验证）：stub 不认 A' md5 → fallback 吐 B-gold → A' 上 clamp=(xmmn0, W, 4.5e-7, 6e-7)、d4=(100, 5g, 7)。与 A'-gold **三处不同**（instance/old/new + d4 三参数），即隐藏 A' 交叉击穿 stub。

## 5. check.py 重写规格（k=11→16，新增 5 条 l-p §4.9 A'-gold 交叉）

保留原 11 条 (a-k) B-side + visible-A guard (j)（向后兼容）。新增：

- **HERE** 路径常量：`AP_SP = os.path.join(HERE, "hidden_a", "Check_SaNP_tb_Ap.sp")`；`AP_MR = os.path.join(HERE, "hidden_a", "model_ranges_Ap.json")`（A' fixture 放 `reference/<id>/hidden_a/`，SUT 不可见）
- **(l)** 候选跑隐藏 A' exit 0 + 产 out_Ap.sp 非空 + rep_Ap.json 合法 JSON 含 defects_found/n_defects
- **(m)** A' class-1 clamp == A'-gold oracle `(instance=xmson0, param=W, old≈7.5e-7, new≈1.0e-6)`（核心交叉，击穿 stub 吐 B-gold 的 xmmn0/0.6）— judge 直接断言候选 rep_Ap 的 class-1 tuple
- **(n)** A' clamps ≠ B clamps（显式输入相关性，击穿对任意输入吐恒定 B-gold 的硬编码 stub）
- **(o)** A' rep defect classes == {1,2,3,4,5}（击穿只修部分缺陷的 stub）
- **(p)** A' rep class-4 params == A'-gold `(fmin=50, fmax=20g, noiseseed=42)`（击穿 stub 在 A' 上吐 B-gold 的 100/5g/7）

A'-gold 值**硬编码于 check.py**（A' 是固定 fixture，gold 确定性，无需运行时重算 — 同 r1074 范式）。judge 不导入 ref/golden_fix_spice.py。

**预期 stub 行为**（已运行时验证）：stub on A' → fallback B-gold → (m) FAIL [instance=xmmn0≠xmson0] + (n) FAIL [A' clamps==B clamps] + (p) FAIL [fmin=100≠50]。n_distinct=3。

## 6. 负样本入库规格

`negative/` 扩为 4 neg + 3 §4.9 deg（沿用现有 neg_noop.py / neg_only_defect1.py + 新增）：
- `neg_fake_hardcode_b.py`（smart §4.9(b) B-hardcode stub，已建，见 fix_prep/）→ post-fix FAIL [(m)/(n)/(p)]
- `_deg_empty` → FAIL [(b)]
- `_deg_print_only` → FAIL [(c)]
- `_deg_core_deleted` → FAIL [(c)]

`negative_selftest.py` 跑全 7，要求 ALL FAIL，n_distinct≥3（(b)(c)(m)）。

## 7. D.jsonl sync 清单（下一轮自验通过后执行）

1. 重写 `reference/EDA-Eval-DesignFlow-SaNPTrannoiseFix-001/check.py`（k=16，加 l-p）
2. 新建 `reference/EDA-Eval-DesignFlow-SaNPTrannoiseFix-001/hidden_a/Check_SaNP_tb_Ap.sp` + `model_ranges_Ap.json`（从 fix_prep/ 复制）
3. 入库 `reference/.../negative/neg_fake_hardcode_b.py` + 更新 `negative_selftest.py`
4. 自验：ref 16/16 PASS on (B)+(A) + (隐藏 A')；7 neg/deg 全 FAIL
5. D.jsonl 该行：`test` 字段替换为新 check.py 全文（byte-sync sha256+size）；`metadata` 更新 `check_sha256`/`check_size`/`byte_sync_sha`/`byte_sync_size`/`k_check=16`/`k_rationale=16`/`test_rationale`（⑫-⑯ 标注 §4.9 A'-gold 交叉）/`negatives[4]`/`negative_selftest`/`self_verify`
6. audit TSV 该行：`12→16` / `有anti_hardcode n→y` / `只在B跑 y→n` / `三假 PASS→FAIL(runtime)` / `判定 GAP→PASS`；report Top10 进度 9→10
7. MEMORY_D：r1077 指针（修复轮 #10），DEBT 496→495

## 8. 修复范式沉淀（r1076 增益）

- 印证 r1069「visible-A guard 无效」病灶**泛化到 SPICE-fix 类**（script-deliverable + 多缺陷 lint）：任何 A 可见的 script-deliverable case，visible-A guard 都可被 md5/特征串查表 stub 绕过
- A' fixture 范式适用于 SPICE-fix：A' testbench 与 A/B 在 model/subckt/实例/角点/参数全维异，5 缺陷类齐全，A'-gold 三字段（clamp instance+new、d4 fmin/fmax/seed）独立可断言 → n_distinct=3 击穿 stub
- 与 r1074 (netlist 解析类) 互补：本范式 = SPICE-fix 类的 hidden A' 同构 testbench
