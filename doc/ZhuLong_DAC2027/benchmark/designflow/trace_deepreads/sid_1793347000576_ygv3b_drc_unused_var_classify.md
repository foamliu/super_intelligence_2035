# Deepread: sid_1793347000576_ygv3b — PDK_QA DRC variableUnusedDrc 根因分析

- **trace**: 1793347000576_ygv3b (xinqiaoz @ hfeg0pkn002, mc=389, physical_verify)
- **session**: 续跑 (msg0 = Context summary); nmsg=236; model deepseek-v4-flash
- **issue (yuxi 反馈)**: report 第 453~454 行 `V1A_Size_001_00`/`V2A_Size_001_00` 被判 `variableUnusedDrc`，但 derive layer 定义里明明用了变量 → 代码 bug 还是 deck 写法问题?
- **关键指标 (s1 report 第 233-237 行, 与原始 report 完全吻合)**:
  - `variableUnusedDrcCount=4`: `ESDPN_N_008_00`, `PG_L_006_01`, `V1A_Size_001_00`, `V2A_Size_001_00`
  - `derivedLayerExemptedCount=5`: `V4_Size_002_00`, `V5_Size_002_00`, `V6_Size_002_00`, `ESDCDM_S_006_00`, `ESD_S_009_00` (derive layer 含变量名 → 正确豁免)
  - `ldrValueWithMultiDataCount=12`; V1A/V2A_Size_001_00 LDR 值 = `0.045 × 0.045` (多值格式)
- **真实 derive layer 定义**:
  - `V1Asize1 = RECTANGLE V1A_NO_SL == _V1A_size_001_00_ BY == _V1A_size_001_00_` (含变量 `_V1A_size_001_00_`，但未豁免 = 误报)
  - `V2Asize1 = RECTANGLE V2A_NO_SL == _V2A_size_001_00_ BY == _V2A_size_001_00_` (同上)
  - `V4size1 = RECTANGLE V4_NO_SL == _V4_Size_001_00_ BY == _V4_Size_002_00_` (含 `_V4_Size_002_00_` → 正确豁免)
  - `variables=['_V4_Size_001_00_', '_V4_Size_002_00_', ...]` (DrcValueCheck 从 derive layer 抽 variables)
- **根因链 (assistant 最终汇报 msg235)**:
  - 两个预处理器行为不一致: `DrcInfo.preProcess`(不带 prepOptions, 旧豁免用) vs `CalibreSvrfPreprocessor`(带 prepOptions, 主检查用)
  - 真正元凶不是 `#IFDEF CHECK_PRODUCT DDR`，而是 deck 第 5886 行 `#IFNDEF CHECK_RANGE RDL_TECH` 大块 (V1A 在其中):
    1. deck 第 17 行 `#DEFINE CHECK_RANGE RDL_TECH` (激活) → by-value 判 `#IFNDEF CHECK_RANGE RDL_TECH` 为假 → 真实 Calibre 运行时 V1A 根本不存在
    2. 主检查 (CalibreSvrfPreprocessor): CHECK_RANGE 不在 workdOptions → 整块跳过保留 → V1A 存在 (QA 全量视角) → 报 unused variable
    3. 旧豁免 (DrcInfo by-value): 判假 → 大块注释 → V1A 不存在 → 豁免失败 → 误报
  - 修复 (已 commit DrcValueCheck): 豁免改用 `self.drcInfo` 让两者同源 → V1A 场景正确
  - 用户进一步担心 (msg162): 互斥 `#IFDEF CHECK_PRODUCT DDR`/`LPDDR` 两分支 derive layer 用不同变量时, 带 prepOptions 会同时保留两分支 → rule.variables 混入未生效分支变量 → 过度豁免
  - 二次修复建议: 修 `CalibreSvrfPreprocessor.getConditionCodes` 无 `#ELSE` 分支 bug (去掉 line 322 `if elseLocation != -1:` 外层守卫); 本 deck 77 个 CHECK_PRODUCT 块全匹配 `#IFDEF CHECK_PRODUCT DDR` → 修复后零变化
- **trace 末尾**: assistant 给完整根因 + 修复建议 (msg235), 无用户明确接受最终落盘报告 → 不适用 A-档
- **合成 (B-synthesized)**: 取 "DRC variableUnusedDrc 报告规则分类器" — 读 report + rule→derive-layer 映射, 按变量是否在 derive layer 定义里出现, 把 variableUnused 分到 exempted_missing(应豁免未豁免)/truly_unused, 把 derivedLayerExempted 分到 exempted_correctly/exempted_suspicious(过度豁免). 4 桶 + verdict.
- **grounded on**: 真实 rule 名 (V1A/V2A/V4-V6/ESDCDM/ESD/ESDPN/PG_L) + 真实 derive layer 定义 (RECTANGLE ... == _var_ BY == _var_) + 真实计数 (4 unused / 5 exempted) + 真实根因 (derive layer 含变量却未豁免)
- **DISTINCT** from r172b DrcRuleCellMatch (rule->cell 5 策略匹配) + r171 DummyHeaderQaResolver (deck 头部开关 QA) — 本 case 测 **derive-layer 变量间接使用判定 + 豁免漏判/过度豁免四桶分类**, 与 rule-cell 匹配 / header QA 互补不重叠
- **case**: EDA-Eval-DesignFlow-DrcUnusedVarClassify-001 (physical_verify, B-synthesized, L1-boundary, k=16/16 a-p)
