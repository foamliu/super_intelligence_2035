# 深读笔记 — sid 1792998659148_31lou (claire1l @ hfeg0plg49/10.129.x)

- **trace**: `1792998659148_31lou.messages.json`（claire1l，117 msgs/1.0MB，agent=lead，model=deepseek-v4-flash）
- **mc=90**：keywords 278 innovus, 25 netlist, 2 synthesis, 1 pyAether（Innovus-dominant → pg_layout）
- **真实意图（USER 逐字）**：
  - USER#1 逐字「/home/pdk/chengleiy/e_innovus/QA/tsi/tech_thk2d0_m5.lef，读取这份techlef文件，汇总每一层走线层和通孔层的布线规则」
  - USER#2 逐字「再读取这份techlef:tech_thk2d0_m5_20260917.lef,与刚才那份对比走线规则，以表格形式呈现」
  - **USER#3 逐字（A-档 seed，提出目标未给根因/修复）**「用的是这份lef：/proj/lacaa/V0_Virtuoso/workdir/claire/TSI/innovus/tsi/tech_thk2d0_m5_20260917.lef，命令文件为run.tcl，分析为啥innovus宽线上不能自动打孔，只能打出单个孔」
  - USER#5/6/7/9 给 log 路径+「分析为啥打孔有问题/为1cut或2cut没有4cut」=迭代细化（hint 性质，不进 prompt）
  - USER#10 逐字「读取/apps/cdsmgr/CRB/INNOVUS231/doc/子目录下所有文档，给一个总结文档，概括每一个工具的应用场景」=独立子任务（Innovus 23.12 文档集概览，67 分册）

## assistant 工具链
list_allowed_files(/home/pdk/chengleiy/e_innovus/QA/tsi) → read_files(tech_thk2d0_m5.lef 全 452 行) → read_files(tech_thk2d0_m5_20260917.lef) → 对比表格 → list_allowed_files(/proj/lacaa/.../tsi) → read_files(run.tcl + innovus.cmd + innovus.logv5/v6/v7) → editor(/home/claire1l/fixed_viagen_20260917.lef + run_fixed.tcl) → list_allowed_files(/apps/cdsmgr/CRB/INNOVUS231/doc 67 分册) → read_files(preface.html 抽样) → editor(/home/claire1l/innovus231_doc_overview.md)

## 关键技术发现（USER#3-9 的 via-cut 诊断）
**tech LEF 事实**（tech_thk2d0_m5_20260917.lef）：
- 走线层 M1(H,pitch1.76,width0.88) M2(V,1.76,0.88) M3(H,1.76,0.88) M4(V,1.76,0.88) M5(H,1.76,0.88) RDL(V,12,6)
- cut 层 V1-V4, RDV, TSV
- VIA 定义：VIA1_1cut(cuts1,enc0.72×0.72) VIA1_2cut(cuts2,enc1.6×0.72) VIA1_4cut(cuts4,enc2.45×2.45) … 每 via 层都有 1/2/4cut 三档
- VIARULE GENERATE：GENV1(rows1,cols1) GENV2 GENV3 GENV4 GENRDV
- 与旧 lef 差异：旧 M1/M2 pitch9.76/width8.88（厚线），新 pitch1.76/width0.88（细线）

**run.tcl 事实**（logv7 用的）：
```
setViaGenMode -viarule_preference VIA2_2cut       ;# 偏好 2cut（VIA 名非 VIARULE，用法存疑）
add_ndr -name width_wide -width {M1:M3 5}         ;# 线宽 5，无 -generate_via
routeDesign -globalDetail -viaOpt -wireOpt
routeDesign -viaOpt
globalDetailRoute
# 全程没有 setNanoRouteMode -drouteUseMultiCutViaEffort / -drouteMaxMultiCutViaLevel
```

**logv7 布线统计**（L727-735）：100 net，total 522 via，cut 分布 1cut≈510 / 2cut≈12 / 4cut=0。

**诊断结论（msg[90]）—— 打孔数被卡在 ≤2，永远不到 4cut 的 4 个根因**：
1. **主因**：`drouteMaxMultiCutViaLevel` 默认=2，未设置 → 路由器最多放 2cut，绝不放 4cut（不管线多宽/LEF 有无 4cut）
2. **次因**：`setViaGenMode -viarule_preference VIA2_2cut` 主动偏向 2cut，进一步锁死
3. **没开高多孔努力**：无 `setNanoRouteMode -drouteUseMultiCutViaEffort high`，detail 路由按默认/低努力，不主动升级单孔→4 孔
4. **NDR 无 -generate_via**：`add_ndr ... 5` 只加宽线，不生成多孔 via 阵；4cut 只能靠既有 VIA*_4cut 单元 + swap，swap 又受 maxlevel=2 限制

**修复建议**（msg[90]）：
```
setNanoRouteMode -drouteUseMultiCutViaEffort high
setNanoRouteMode -drouteMaxMultiCutViaLevel 4
setNanoRouteMode -droutePostRouteSwapVia multiCut
setNanoRouteMode -routeReserveSpaceForMultiCut true
# 去掉 setViaGenMode -viarule_preference VIA2_2cut
# add_ndr 加回 -generate_via
```
几何验证：VIA1_4cut 包络 2.45×2.45，NDR 线宽 5 够放；M1 TSV pad 12 够放 → 提 level 到 4 + 高努力即可出 4cut。仅 net_wire[0]（宽5）能 4cut，其余 99 net 默认宽 0.88 仅容 1cut（0.72 切孔+0.08×2 包络≈0.88）。

## USER#10 子任务（Innovus 23.12 文档概览）
/apps/cdsmgr/CRB/INNOVUS231/doc/ 含 67 分册（Doc Assistant/Stylus Common UI），按工具族归纳：Innovus(UG/TCR/MR/WN/errmsg/KPNS/DBAref) / Stylus Common UI / Integrity / Voltus(IR/EM) / LEF-DEF / CPF-UPF / 混合信号(dmsflow) / 基础设施。产 `innovus231_doc_overview.md`。

## A-档资格判定
USER#3 逐字提出目标（「分析为啥innovus宽线上不能自动打孔，只能打出单个孔」），未给根因/修复 → 合格 A-档 seed。但 gold 依赖 live Innovus + live PDK LEF(/home/pdk/chengleiy/...内网) + live /proj/lacaa 工作区 → **.75 沙盒不可达 → A-档 disqualified(data/tooling)** → **B-档 synthesized L1-boundary**（纯离线 manifest → via-cut 诊断器生成，无 EDA 工具依赖）。

## 合成方向（B-档）
case_id: `EDA-Eval-DesignFlow-InnovusViaCutDiag-001`（pg_layout）
candidate `via_cut_diag.py`（标准库，确定性无随机）：读 `via_diag_manifest.json`（tech_lef layers/vias/viarules + run_tcl viaGenMode/nanoRouteMode/ndrs + ndr_nets + log_stats cut_distribution）→ 推导 max_cut_allowed（默认2）/ via_pref_bias / multi_cut_effort / per-NDR generate_via / fits_4cut（几何：NDR width ≥ 4cut enclosure）/ effective_max_cut / can_achieve_4cut / root_causes（4 因子）/ recommendations（tcl 修复）/ log_consistency → 产 `via_diag_report.json`。
资产 A 忠实（tsi_top，M1-M5 pitch1.76/width0.88，VIA1_1/2/4cut enc0.72/1.6/2.45，run.tcl VIA2_2cut pref + NDR width5 无 generate_via + 无 nanoRouteMode，log 1cut510/2cut12/4cut0）。
hidden B（pcm_top，M1-M5 pitch2.4/width1.2，VIA3_2cut pref，NDR pwr_wide width8 无 generate_via，log 1cut480/2cut20/4cut0）/ B2（B 修复后：level4+effort high+无 pref+generate_via true → can_4cut=True，击穿 always-capped）/ B3（NDR width2.0 < 4cut enc2.45 + level4 + effort high → can_4cut=False 几何限制，击穿 always-true）。

## 与现有 case 正交
InnovusDbAudit-001(r98) 是 read-only 数字后端能力审计分类（每阶段 must/conditional/non_must + PVT/覆盖/缺口 + final_verdict），不涉及 via 生成。本案是 Innovus multi-cut via 生成诊断（max_cut_level/via_pref/effort/generate_via/几何 fits 4 因子 + 修复建议），是 via-generation 诊断类，正交。
