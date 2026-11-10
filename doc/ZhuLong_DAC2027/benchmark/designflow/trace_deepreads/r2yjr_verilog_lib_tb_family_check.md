# r2yjr — verilog_lib_trans tb_family check (deepread · r318)

**session**: 1794201552569_r2yjr · user e0039602 · host hfeg0pkn002 (10.129.2.11) · mc=287
**size**: 194 msgs / 91 asst / 103 user / 1.04 MB messages.json (scp'd to workdir)
**scan**: ssh_eda_search_20261109_224902, keywords verilog:1058;lvs:227;netlist:156;rtl:48;drc:19
**domain**: digital (verilog library translation validation)
**status**: r318 claimed → DEBT:1 build → r319

## USER 原话（A-faithful，提出目标未给根因 ✓）

U#0 逐字：
> 请用这个目录下的tb-family 对/home/e0039602/Documents/verilog_lib_trans_skill/verilog_lib_trans_skill_aifree/result_map_20261109_095523_d55b.txt这里面的所有进行检查，把检查通过的放入一个sv文件，sv文件只需要保存转换之后的就行了，不许要用resultmap的格式，final_merged_netlist_stdcells_ac_converted.sv用这种格式的保存，检查不通过的你也先不用改写，在对话框里返回给我所有错误的，并告诉我错误的原因

U#101 逐字：`继续`（= 修复 192 个失败 cell，属 fix-loop，L3-too-complex，不纳入本轮 case）

## 任务本质（L2 — 真跑 Xcelium xrun 功能对拍）

- **tb_family** = 一组 testbench 模板，用 Xcelium `xrun` 对每个转换后的 cell 做功能对拍（converted netlist vs reference behavior），判定 PASS / MISMATCH / NO_CONVERT。
- **result_map_*.txt** = verilog_lib_trans_skill 的转换产物，含 883 个 cell 的转换后 netlist。
- agent 写了一串 python 脚本（_probe/_analyze/_run_single/_run_all/_summary/_inspect2）逐 cell 跑 xrun 对拍，产出：
  - `_xcheck/_results.json`：每 cell `{verdict, miss, fam, reason}`
  - `tb_family_check_report_*.md`：人类可读错误分类报告
  - `final_merged_netlist_stdcells_ac_converted.sv`：仅 PASS cell 的合并 SV（691 个 module）

## 真实结果（金标，from A#89 最终报告）

- **883 cells 全检**
- **PASS 691** → 写入 `final_merged_netlist_stdcells_ac_converted.sv`（含 691 个 `module`，与 PASS 数一致，未通过者不入）
- **FAIL 192**（不改写），分类：
  - **A. MISMATCH (51)** — 有转换、能编译、功能对拍不一致
    1. 电源/阱脚连接不全，输出悬空 z/x（Vx/Wx/Yx 强弱驱动变体、B 型）：inv `invBx2 invBx4 invVx2 invVx4 invVx6 invVx8 invWx2 invWx4 invYx2 invYx4 invYx6 invYx8 invYx16 invYx24`；nand2 ... 等
    2. AOI/OAI 逻辑错误（布尔方程错）
    3. FF/latch 时钟极性（Ck/CkN 建模错）
    4. ...（更多类别见报告）
  - **B. NO_CONVERT (141)** — 占位、未转换

## 交付契约（design_flow）

```
mode: design_flow
entry_point: outputs/submit.zip
prompt: U#0 逐字原文（A-faithful）
attachments: assets/<id>/result_map_spec_a.txt + tb_family_defs_a/ + simlib_base.sv
```

## reframe：spec-driven generator + static-verification（匹配 r297 CkmuxXlsxExport / r310 SignalXrefBuilder 模式）

**为何 reframe**：grading env 无 Xcelium xrun，无法动态对拍。采用 spec-driven-generator + static-verification：spec 编码 ground-truth verdict 表（来自真实 xrun 结果），生成器 emit 一个 checker，check.py 静态验证 emitted checker 的输出结构与 verdict 复现。

**deliverable**：
- `gen_tb_family_check.py`（stdlib 生成器）+ `spec_a.json`
- 生成器读 spec → emit `tb_family_check.py`（读 result_map + tb_family defs + spec 的 verdict ground-truth 表）→ 产出：
  - `_results.json`：每 cell `{verdict: PASS|MISMATCH|NO_CONVERT, miss:int, fam:str, reason:str, reason_category:str}`
  - `final_merged_netlist_stdcells_ac_converted.sv`：仅 PASS cell 的合并 SV（每 cell 一个 `module`，按 final_merged 格式）
  - `tb_family_check_report.md`：错误分类报告（MISMATCH 按 reason_category 分组，NO_CONVERT 列表）

**spec 参数化**（A→B 异构）：
- `result_map_file`, `tb_family_defs_dir`, `output_sv_file`, `results_json_file`, `report_file`
- `cells`: list of `{name, fam, expected_verdict, miss, reason, reason_category, converted_netlist_block}`
- `family_rules`: name→family 派生正则（inv→inv, nand2→nand2, aoi21→aoi, ...）
- `merged_sv_format`: 模板

**A = spec_a faithful**（e0039602 / result_map_20261109_095523_d55b / 883 cells / 691 PASS / 192 FAIL / final_merged_netlist_stdcells_ac_converted.sv）
**hidden B = spec_b isomorphic**（不同 cell 名/不同 fam 分布/不同 PASS-FAIL 划分/不同 merged sv 名）

## check.py 预想（≥8 conds，独立 recompute 比对）

a) zip 内含 gen + spec_a + emitted checker + outputs
b) gen py_compile OK
c) gen on spec_b → emit `tb_family_check.py`
d) emitted checker py_compile OK
e) emitted checker on spec_b → `_results_b.json` + `merged_b.sv` + `report_b.md`
f) _results_b.json 合法 + 每 cell 必需字段齐（verdict/miss/fam/reason/reason_category）
g) family 派生正确（cell name → fam，按 family_rules）
h) verdict 复现 spec_b ground-truth（PASS/MISMATCH/NO_CONVERT 一一对应）
i) miss 计数正确
j) reason_category 分组正确（MISMATCH 按 category，NO_CONVERT 单列）
k) merged_b.sv 仅含 PASS cell，每 PASS cell 一个 `module`，module 数 == PASS 数
l) merged_b.sv 不含任何 FAIL cell
m) report_b.md 含 MISMATCH 分组 + NO_CONVERT 列表 + 各组 cell 计数
n) 反硬编码 A：B 特异 cell 名/fam/sv 文件名/PASS-FAIL 划分 present，A 特异 absent（整词比对）
o) 反硬编码 A 源码 + 反平凡 + 3-seed 确定性
p) 退化提交回归（空壳/print-only/core-deleted 全 FAIL）

预计 k_check ≈ 16，k_rationale = 16。

## 自验计划

- gold `gen_tb_family_check.py` 复现真实 trace 的 checker 逻辑（family 派生 + verdict 查表 + merged sv 生成 + report 分类）
- ref PASS 16/16
- negatives（noop/stub/hardcode_a/fake_print/keep_all_pass/flip_verdict）全 FAIL
- §4.9 (a)(b)(c) 全 FAIL

## 备注

- e0039602 在池中有多个 session（r2yjr/rv1g2/fyknj/dlrpg/ikg9e/2b5i8/pzo6g/k7668...），diversity 关注：r2yjr 任务=tb_family check ≠ 其他 LVS/diagnosis 任务，非重复。
- "继续" fix-loop（192 cell 修复 + 重检）L3-too-complex，不纳入本轮 case；如需可另建 follow-up case（fix-generator），但优先级低。
- 真 clean A-faithful produce 第 12 次评估：r2yjr 是 clean produce（U#0 提出目标未给根因 ✓），L2（xrun 对拍）→ reframe 为 spec-driven+static 后降为 L1-static+subprocess，符合 §5 L1≤30% 配额需注意（已有多个 L1，本 case 若建应归 L1-static，需确保 L2/L3 占比不破线）。
