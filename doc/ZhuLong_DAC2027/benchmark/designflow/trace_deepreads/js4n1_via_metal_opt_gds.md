# js4n1 — SRAM bitcell DTCO 过孔/金属宽度 GDS 优化变体生成器

## trace_source
- session_file: `1795075084116_js4n1.messages.json`
- user: e0024852 · host: hfhds201 · match_count: 545
- domain: physical_verify (SRAM bitcell DTCO / GDS via+metal width sweep)
- ledger: claimed r1475 (covered 570→571) → marked `case` (EDA-Eval-DesignFlow-ViaMetalOptGdsGen-001)

## 真实用户意图
SRAM bitcell 的 design-rule + layout 联合 DTCO 优化：读一个 bitcell 的 GDS
（`CH252_HD_Bitcell_FS_pin.gds`），对过孔层（V0D/V0G/V1）扫描候选尺寸、对 M1 金属
扫描候选宽度，每跑一个候选就做 design-rule 检查（enclosure / space / pitch），通过
的就导出一个变体 GDS，最后汇总成一份 report 供下游 PEX/仿真用。

真实流程踩过的坑（agent 在 trace 里反复 debug 出来的，本案 prompt 直接提示，避免被测
重新踩坑）：
- `dbGdsOut(fromMemory=False)` 只导出 delta 不导整版 → 必须用 `fromMemory=True`；
- 同一个库里反复 `dbGdsIn(Overwrite)` 会让过孔逐变体累积 → 每个变体要用独立库名；
- 层名要用 tech 映射后的 `V0D/V0G/M1` 而不是裸 `L1225/L90/L88`。

## 本 case 的抽象（关键决策）
真实流程依赖 pyAether + Aether license + GDS 二进制，无法离线判分。本 case 把它抽成
一个**纯 Python、shape-spec 驱动**的变体生成器，便于 L0/L1 静态判分（LIVE-NA，不需
.75 真工具）：

- layout = 一个 JSON：一组按 layer 分组的轴对齐矩形（`bbox:[x1,y1,x2,y2]`，单位 nm）
- 候选 optimizer 读 spec JSON，扫 `(via_layer, size_nm)` 与 `(metal_layer, width_nm)`
  候选，对每个候选做几何 DRC（enclosure / via-via space / pitch / metal space），
  `OK` 的写一个变体 layout JSON，最后写 `report.json` 汇总
- 坐标单位 nm；金属线是水平长矩形（x 长 y 窄），过孔是小正方形；resize 按「中心缩放」/
  「中心加宽」保持线长不变

这层抽象保留了真实流程的**核心 DRC 语义与变体生成逻辑**（过孔 enclosure、via-via
space、metal pitch/space、每变体独立输出 + report 汇总），但把 GDS 二进制读写换成
JSON，使判分可在任意 Python 环境跑。

## case 设计
- **task_id**: `EDA-Eval-DesignFlow-ViaMetalOptGdsGen-001`
- **domain**: physical_verify · **mode**: design_flow · entry_point: `outputs/submit.zip`
- **judge_layers**: `[L0,L1]`（纯 Python shape-spec，无 EDA binary ⇒ LIVE-NA）
- **visible A**: `spec_A.json`（via_layers=[V0D,V0G]，via_size 7 候选，metal_width 8
  候选，DRC 阈值）+ `base_A.json`（19 形状：4 M1 + 12 V0D + 3 V0G）+ `gen_base.py`
  （生成脚本，仅供参考）+ `prompt.txt`
- **hidden B**（判分用，assets/hidden/）: `spec_B.json`（不同候选列表 + 不同 DRC 阈值）
  + `base_B.json`（23 形状：5 M1 + 15 V0D + 3 V0G，不同 pitch 70 vs 60 / width 36 vs 30
  / 过孔数量位置）—— A 的 hardcoder 在 B 上 FAIL
- **reference 解**: `via_metal_optimizer.py`（7157 B，扫候选 → 几何 DRC → 写变体 JSON +
  report.json；malformed spec raise；无 A 专属字面量）
- **A vs B verdict 差异**（防 hardcode 实证）: A → 15 OK / 7 SKIP；B → 15 OK / 4 SKIP
  —— verdict 分布不同，hardcode A 结果必在 B 上 c8(c8_verdict_correctness) FAIL

## check.py（17 条独立断言，sha256=547da6ec…, 11824 B）
check 故意**独立重新实现**几何 DRC 复算（不 import reference），逐变体重算期望 verdict
并比对候选 report。17 条断言每条可独立 FAIL：

1. c1_zip_has_optimizer — zip 含 via_metal_optimizer.py
2. c2_py_compile — py_compile 通过
3. c3_runs_clean — hidden spec_B 运行 rc=0
4. c4_report_exists — report.json 存在
5. c4b_report_has_variants — report 含 variants 列表
6. c5_total_count — total == 候选总数
7. c6_variant_count — len(variants) == 候选总数
8. c7_record_fields — 每条记录字段齐全 {tag,mode,layer,size_nm,verdict,reason}
9. c8_verdict_correctness — 每条 verdict == check 独立几何复算（防猜）
10. c9_skip_reasons_descriptive — SKIP reason 含数值（nm/margin/gap/pitch/size/width）
11. c10_ok_variant_geometry — OK 变体的 variant_file 存在且几何真的被 resize
12. c10b_ok_skip_counts — report.ok/skip 统计 == 独立复算计数
13. c11_malformed_raises — malformed spec（缺 base_layout）→ 候选非零退出
14. c12_no_hardcode_a_base — 源码无 base_A.json 硬编码
15. c13_via_has_mix — via 候选既有 OK 又有 SKIP（真扫描）
16. c14_top_cell_matches_b — report.top_cell == base_B.top_cell
17. c15_both_via_layers — report 覆盖 spec_B 所有 via_layers

> 注：summary 早期草稿记为 15 条，实际 check.py 含 c4b / c10b 两条拆分（report 结构 +
> ok/skip 统计独立可 FAIL，提升负样本 first-fail 区分度），最终 k_check == k_rationale
> == 17。test_rationale 已按 17 条同步。

## negatives（5 个 + negative_selftest.py，4 distinct first-fail，§4.9 trio 3-distinct）
| negative | first-fail | 说明 |
|---|---|---|
| empty_stub | c4_report_exists | 空文件，跑不出 report |
| print_only | c5_total_count | 只 print 不写 report 字段 |
| naive_no_drc | c8_verdict_correctness | 全 OK 不做 DRC |
| hardcode_a | c8_verdict_correctness | hardcode A 的 verdict（B 上错） |
| no_variant_files | c10_ok_variant_geometry | report 说 OK 但不写 variant_file |

DISTINCT first-fails: c4 / c5 / c8 / c10 (4 distinct, ≥3 要求 ✓)
§4.9 trio: empty→c4, print→c5, naive→c8 (3 distinct ✓)
negative_selftest.py OVERALL_RC=0 ✓

## 自验
- reference `via_metal_optimizer.py` on A: 15 OK / 7 SKIP ✓
- reference on B: 15 OK / 4 SKIP ✓（与 A 不同，防 hardcode）
- `python3 check.py` self-test: OVERALL PASS 17/17 ✓
- `python3 negative_selftest.py`: 5 negatives all FAIL, 4 distinct first-fail, RC=0 ✓
- `SKIP_RUN=1 eval/run_one.sh ... --shard C`: 框架接受 case JSON，workdir 建
  + attachments 复制 + leak 自检通过（FAIL 仅因 SKIP_RUN 未产出 submit.zip，预期）✓
- `scripts/build_jsonl.py --shard C`: C.jsonl 重建 639 active case，本 case 入列 ✓

## 注意
- 与 SchematicStripeFix-001（r1472，4iv57，DRC pattern tool schematic 修图）完全不同
  域/不同意图：本 case 是 **变体生成器**（扫候选 + 几何 DRC + 汇总 report），那个是
  **示意图修复 + renderer stripe_deg 增强**
- 与 DrcEnclosure 类 case 不同：本 case 是 sweep + 变体导出 + report，不是单条 DRC
  rule 文本/几何校验
- 纯 Python shape-spec ⇒ 不需 .75 真工具，L0/L1 静态即可判，LIVE-NA 合规
- 已落地 r1475
