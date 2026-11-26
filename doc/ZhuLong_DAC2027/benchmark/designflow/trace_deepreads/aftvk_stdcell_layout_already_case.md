# aftvk 深读复核 · jieran@hfeg0plg70 · 1793963596117_aftvk (mc=1034)

## 元数据
- session: 1793963596117_aftvk (3.35MB messages.json, 741 msgs / 379 user / 362 assistant)
- user: jieran @ hfeg0plg70 (ledger 旧记录 host 标 hfeg0pkn004 / ip 10.129.2.13，session 实际在 hfeg0plg70)
- ledger 状态: **已为 case** `EDA-Eval-DesignFlow-StdcellLayoutPlanGen-001` (2026-11-09，layout_aether，k_check=18)
- summary.tsv mc=1034, kw: pyaether:1135;dbopencv:567;aether:526;lvs:510;.lef:488;drc:450;schematic:353;cellview:340

## r790 复核目的
本轮 fresh-trace 搜索（mc≥10, C-pure cscore≥5）top-13 候选全在 ledger。aftvk 是其中 mc 最高（1034）者，旧 ledger 有「parked 2026-11-06 netlist file path」记录，按 2026-11-15 复活令需复核是否为 weak-reason 误杀。

## 复核结论：非复活候选（已为 case，旧 parked 记录为早期入库遗留）
- ledger_C.tsv 有 3 条 aftvk 记录：line ~? parked 2026-11-06「netlist file path (jieran)」(空 user/host/mc) + line 495 case StdcellLayoutPlanGen-001 (host hfeg0pkn004, mc=14) + line 500 case StdcellLayoutPlanGen-001 (空字段)
- **已落 case** `EDA-Eval-DesignFlow-StdcellLayoutPlanGen-001` 在 EDA-Eval-DesignFlow_C.jsonl：reframe 为纯 stdlib `stdcell_layout_plan_gen.py`，读 netlist+rules → 输出 `layout_plan.json`（cell/ports/boundary/transistors/nets/pins/merge_groups/pcu_bridges/drc_lvs_checklist），k_check=18，B 档 nor3LVSx2 反硬编码
- 旧 parked 记录是 2026-11-06 早期入库遗留，2026-11-09 已被 reframe 为 case，**非 weak-reason 误杀**，复活令不适用

## 任务形态（真实用户意图，供参考）
 sprawling 多任务 stdcell layout 绘制教学/迭代：U#1「根据这个netlist帮我绘制版图」→ U#5 5 条 stdcell 绘制规则 → U#11 完整绘制流程 5 步 → U#16 画 nand2LVSx6 → U#19 画 nand2IOLVIOx1 → U#40（末轮）「重新绘制，严格根据stancellor的绘制规则」。助手 238 SandBox run_code (pyAether) + 33 editor + 0 write_file，gold 落 .oa 在 /proj/dscqa/... 生产服务器。前 agent 的 reframe 抽取了「netlist → layout_plan JSON 规划」离线可验子任务，跳过 GUI .oa 绘制本身。

## 池确证（r790）
- top-13 C-pure fresh（mc≥542, cscore≥5≥nlist）全在 ledger（13/13）
- aftvk 已为 case；其余 12 条：4kf4h/itvhk/9fg5t/mwoue(A)/t1xjg/bmhid/mku3e 已 case，4ybw1(wrong-shard B)/enh4y(内容重叠)/wyrs2(重叠)/ajqj4(重复主题)/f86ll(wrong-shard D) parked 有合理理由
- ⇒ 高 mc fresh 池确证趋薄（与 r786 一致），需扩扫 lower-mc 或跨域候选
