# rescan 2026-11-09 10:xx — pkn125 fresh(≥11-06) 扫描 → 6dvs5 reedchen@pkn002 CLEAN → PostSimUncommentFix-001 交付

## 触发
loop task card（09:56:08）派「1 case + WAITING:0」。前轮（09:2x）spice-dom 11-05 summary 62 全 in-ledger，pkn004 fresh 已尽（ddo96 交付，余 parked）。本轮 11-05 重扫令转向 **pkn001/002/005 fresh 时间窗（≥11-06）**。

## 扫描与候选发现
1. eda_flow open_session → run_commands ssh pkn004 `find -newermt 2026-11-06` → 67 fresh sessions，grep spice kw（head -c 8000）→ 排序：szdav(9)/pj4bf(8)/ojko8(6) 等。查台账：**全 67 中仅 3 un-ledgered 且 kw≤2**（gwgyd/mpmdp/ybagc），高 kw 候选全 in-ledger（多为 case 或 parked）。pkn004 fresh 已尽。
2. 转扫 pkn001/002/005 fresh（write scan_pkn125.sh → bash → 202 lines）。grep spice kw 排序：
   - 6dvs5 reedchen@pkn002 kw=7 size=219664 **un-ledgered** ← TOP
   - 6nte7 kaixuanx@pkn002 kw=7（ledger? 待查）
   - 3l3yx ynbai@pkn005 kw=6 → ledger parked（consulting/analysis 非 generative）
   - dhy10 e0046686@pkn001 kw=5 / i4kkz e0044979@pkn001 kw=5 / z3tqe reedchen@pkn002 kw=5 / ifj1a dandans@pkn002 kw=5（ledger parked, lsf 监控）— 多 un-ledgered 备选
3. 台账核对：6dvs5 ledger_count=0 → **scp 6dvs5.json(219KB) 到 .75 workdir** → python3 解析（dict{messages:[47]}）→ peek U#0

## peek 结果（6dvs5 CLEAN → 交付）
| sid | user | host | msgs | A-faithful | 选用 |
|---|---|---|---|---|---|
| 6dvs5 | reedchen | pkn002 | 47/28user | ✓ U#0 后仿网表没正确取消注释，定位修复 bug（提需求无根因）| **本案交付** |

（pkn004 3 un-ledgered kw≤2 弱候选未 peek；pkn125 其余 un-ledgered 高 kw 候选 dhy10/i4kkz/z3tqe/2bsgc/df52y/e3sf0/scut3 留作下轮备选）

## 深读：6dvs5（reedchen @ pkn002，FineSim 后仿网表取消注释 bug）
- U#0 逐字：`python gen_sp_write.py --pvt ../../PVT_HighVolt.csv --template ../template/template.sp --outdir ../sim_run_pre/ --sim post` 后仿网表没正确取消注释，定位修复 bug
- 金标准=assistant 修复 `_netlist_cat()`：硬编码块名 `DOutFIFOx1_Dmi_PN1p76_DbusMg` → 模式匹配（.inc 路径含 .spf 或 subckt → post；含 netlist → pre；以 XI_ 开头 → inst）
- 验证：post 模式 .inc spf/.inc subckt/XI_ 全解开、.inc netlist 保持注释；pre 模式（回归）.inc netlist 解开、其余注释 ✓

## 案例交付：EDA-Eval-DesignFlow-PostSimUncommentFix-001
- domain: spice_sim, track: faithful (A), level: L1, k=10
- A 资产: buggy gen_sp_write.py（硬编码 DOutFIFOx1）+ template_A.sp（latsqmuxPF 块名，trace 原文行）+ PVT_A.csv（9 corners，trace 原文）+ prompt.txt（U#0 逐字）+ task_brief.md
- hidden B: template_B.sp（异块名 wbufMuxPF_RdPath_length52_rev3）+ PVT_B.csv（5 corners）+ template_C.sp（再异块名 rdqMuxPF_DqPath_length38_rev5，验泛化）+ PVT_C.csv（2 corners）+ hidden_manifest.json
- check.py 10 断言(a-j): ①zip含py ②py_compile ③B post exit0+生成.sp ④B post spf解开 ⑤B post subckt解开 ⑥B post XI_解开 ⑦B post netlist注释 ⑧B pre netlist解开 ⑨B pre spf+subckt+XI_全注释 ⑩C post(全新块名) spf+XI_解开=泛化
- 3 negative(naive_uncomment_all/hardcoded_A/always_identity) + §4.9 三假(empty/print_expected/del_core)
- 自验: ref PASS 10/10 ✓ + 3 neg 全 FAIL ✓ + §4.9 三假全 FAIL ✓ + 闸门 10==10≥8 ✓ + jsonl test sha 50860ea422==disk ✓
- 追加 EDA-Eval-DesignFlow_B.jsonl(202→203) + mark ledger(204→205 covered, spice_sim)

## 证据链（11-05 重扫令履行）
1. 扫描命令：eda_flow run_commands ssh pkn004/pkn001/pkn002/pkn005 `find -newermt 2026-11-06` + 远端 grep spice kw（head -c 8000）
2. 时间窗：fresh ≥ 2026-11-06（11-05 summary.tsv 之后），6dvs5 mtime=2026-11-09 01:35
3. 遍历：pkn004 fresh 67（高 kw 全 in-ledger，3 un-ledgered kw≤2 弱）+ pkn001/002/005 fresh 202 → 6dvs5 un-ledgered kw=7 CLEAN
4. 命中：6dvs5 交付 / 0 reject parked（本轮未 park 弱候选，留备选）
5. diff vs 旧 summary：6dvs5 NOT in 11-05 summary.tsv（mtime 11-09，新写入）

## 11-05 重扫令状态
- spice-dom 池（11-05 summary.tsv mc≥30 spice≥10）62 全 in-ledger → 已尽
- pkn004 fresh(≥11-06)：67 sessions，高 kw 全 in-ledger，3 un-ledgered kw≤2（gwgyd/mpmdp/ybagc）→ 弱，未 peek
- pkn001/002/005 fresh(≥11-06)：202 sessions，6dvs5 交付，余 un-ledgered 高 kw 候选：dhy10(e0046686)/i4kkz(e0044979)/z3tqe(reedchen)/2bsgc(reedchen)/df52y(chunfang)/e3sf0(ronghu)/scut3(ronghu) → 下轮备选
- 下轮：peek pkn125 余下 un-ledgered 高 kw 候选（dhy10/i4kkz/z3tqe 等），或扩扫 hfhds201/plg 系列其他主机 fresh
- WAITING:0
