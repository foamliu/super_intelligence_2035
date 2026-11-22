# r985 trace deepread: ezj8z — LEF BM2 OBS 缺失诊断

## trace meta
- session: 1794461048623_ezj8z (michael1l@hfeg0pkn003, mc38)
- keywords: .lef:26;verilog:19;.gds:17;skipper:12;rtl:6
- 49 msgs / 26 user msgs / 23 assistant msgs
- scp via ssh e0031982@hfeg0pkn003, subdirectory 1794461048623_ezj8z/

## 用户意图 (U#0 逐字)
「/proj/lacaa/TV1_DBC/workdir/michael1l/py/genlef_test/ 分析这个文件夹下的脚本 分析抽出来lef没有BM2的obs的原因」

## trace gold (A#22 最终诊断)
### 1. LEF OBS 现状
OBS 段(5211-5710行)含: BM1/M1/M2/M3/M4, **BM2 缺失**。
lefSummary.log 顶部: `OBS Layers: M4 M1_MASK_1 M1_MASK_2 M2_MASK_1 M2_MASK_2 M3_MASK_1 M3_MASK_2 BM1` (无BM2)

### 2. 根因: lefDefBoolean 减法零面积
- BM1 OBS(有效): `lefDefBoolean { 1005.0 "301.540 OR 301.540 "}` → 边界层 OR 自身 = 整单元矩形
- BM2 OBS(缺失): `lefDefBoolean { 1006.0 "167.355 NOT 167.251 "}` → BM2金属(167 dt355) 减去 BM2文字(167 dt251)
- VDD有118个BM2端口, VSS有119个, 每个引脚都带BM2文字标签 → 减法移除全部金属 → 零面积 → 无OBS

### 3. 其他层对比(均有效, 用边界层301.540)
M1(1001)/M2(1003)/M3(1004)/BM1(1005) 全用 `"301.540 OR 301.540"`

### 4. 加剧因素
- option.conf: `#lefExtOption -extractType "Block" -value {"ExtractBlockage" "M1"}` 被注释
- layer.conf: `#lefDefLayerStack "BM1.metal BV1.via BM2.metal"` 被注释

### 5. 修复
BM2 改用边界表达式: `lefDefBoolean { 1006.0 "301.540 OR 301.540 "}`

## case 提炼
通用 diagnose_lef_obs.py: LEF+rule.tcl+summary.log → JSON{obs_present/obs_missing/primary_missing_layer/primary_boolean_expr/primary_root_cause/fix_action}
- A: BM2缺失, 层167, MACRO HD1P_CXN4S1P128X144M1B1C1R1W1BW1RE1
- B: BM3缺失, 层168, MACRO SRAM8Kx32_B3 (反硬编码)

## 选料决策
- iehz0(e0039102 mc20): intent-dup r976 RegAllListMergeProduce(95b6o同用户同ALL.list merge任务) → parked
- p9nly(e0046913 mc46): intent-dup r984 StaRunEvalProduce(c1gcs同用户同STA评估任务) → parked
- 1fzxa(thqu mc18): weak trace(Simvision Q&A + shell disabled失败) → parked
- ezj8z(michael1l mc38): clean pnr_signoff LEF诊断, 不同用户无dup → 选中
