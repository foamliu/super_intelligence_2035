# Deepread — sid 1789610335747_f7hpy (kenwang / hfeg0pkn005 / 10.129.2.14)

- session: 1787625078133? NO → 1789610335747_f7hpy.messages.json
- user: kenwang ; host: hfeg0pkn005 (10.129.2.14) ; mc=284 ; tools=calibre(75 calls) ; 235 msgs ; 2.07MB
- snapshot path: /home/kenwang/.snapshot/hourly-new.2026-11-02_1100/.cline/data/sessions/1789610335747_f7hpy/
- agent: 'lead' (zhulong) ; 31 user msgs (most are "[vps-cli]...", here only 3 real intent turns)

## 真实意图（逐字）
- USER#0 (act): `/rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/updateCode/Rev13_S9/35H_DBC_DRC_Cal_V0d1_Rev13_T8.drc 学习这个 DRC deck ，并 生成一份 开发 DRC 的 agent`
- USER#7 (act): `如果有design rule 更新，你可以根据更新内容和学习内容，可以开发出DRC code`
- USER#189 (act): `你可以根据design rule 的内容开发出来 svrf 的 DRC code 吗`

→ A-档 seed = USER#0：提出目标（学习 deck + 生成开发 agent），未给根因/修复 → 合规 A-档。USER#7/189 给方向（=hint，不进 prompt）。

## assistant 工具链
read_files×45, editor×60, run_commands×5, list_allowed_files×3, search_codebase×2, run_approved_command×1。
run_commands 全是只读 grep/wc/head 解析 deck：
- `wc -l 35H_DBC_DRC_Cal_V0d1_Rev13_T8.drc`
- `grep -n 'VARIABLE' ...` → 抽 VARIABLE 声明
- `grep -n '^[A-Z].*{' ... | grep -v LAYER|LAYOUT|CONNECT|#IFDEF|#DEFINE|VARIABLE` → 抽规则块
- `grep -n '#IFDEF DBC YES'` / `grep -n 'DBC_H180_'` / `grep -n 'FS_H204_'` → 平台条件 + 规则命名前缀
deck 摘要：`424 layers / 2853 rules / 27 switches / 3 variables`，平台 DBC(H180, Full_BS_5) + FS(H204, Full_FS_1)。

## 产物（editor 写 7 个文件，最终保留 2 个核心）
1. `/home/kenwang/calibre_agent.py` (18KB) — DRC deck 解析/分析 agent：解析 LAYER MAP/#DEFINE/VARIABLE/规则块，按平台 + check_type 统计，导出 JSON。
2. `/home/kenwang/drc2svrf.py` — **Design Rule spec → SVRF 代码生成器（核心 gold）**：
   - `RuleType` enum: W=Width(INT), S=Space(EXT), EN=Enclosure(ENC), L=Length(LENGTH), O=Overlap(AND), R=Restriction(ANGLE), A=Area(AREA), DN=Density(DENSITY), G=Offgrid(OFFGRID), NC=Notch, H=Hole, NB=Neighbor
   - `ABUT_OPS` map: SINGULAR→`ABUT<90 SINGULAR REGION`, OPPOSITE→`ABUT<90 OPPOSITE REGION`, ...
   - `RuleSpec` dataclass: name, rule_type, layer, min_value, max_value, condition, platform, layer2, via_layer, metal_layer, opposite_sides, width_list, tolerance, window_size, step_size, density_min/max, neighbor_count/space, exclude_condition, inside_condition, measured_layer, extra_statements
   - `SVRFGenerator.generate()`:
     - 平台自动检测：name 前缀 `DBC_H180`→platform=DBC, `FS_H204`→FS
     - 默认 condition：DBC→`DBC YES`, FS→`DBC NO`（若未显式给 condition）
     - 分派 `_gen_<type>`：`_gen_w`→`INT layer < v ABUT<90 SINGULAR REGION`（width_list→多区间 `INT layer_H_Edge > prev < w ABUT<90 OPPOSITE REGION`）；`_gen_s`→`EXT layer [layer2|measured_layer] < v`，neighbor→`WITH NEIGHBOR layer >= n SPACE < s`
     - `_assemble()`：`#IFDEF <condition>` → derived layers → `name { @desc <svrf lines> }` → `#ENDIF`
   - 支持高级：exclude_condition（`NOT SEALRING`）、inside_condition（`INSIDE Full_BS_5`）、opposite_sides（`RECTANGLE ENCLOSURE`）、measured_layer（差分间距）、width_list（MINP 多宽度）、extra_statements

## gold 依赖
- live deck `/rundata/lacaa/.../35H_DBC_DRC_Cal_V0d1_Rev13_T8.drc` 在 lacaa 内网 → .75 沙盒不可达
- live calibre 二进制不可达
→ **A-disqualified → B-档 synthesized L1-boundary**

## B-档合成方案（与既有 case 正交）
- r71 DRCPatGenAudit = DRC pattern manifest 分类审计
- r76 SVRFDepAudit = SETLAYER 依赖 DAG / 前向引用 / $var 审计
- r79 DRCDeckSyncPlan = local↔stable 同步规划（取代链+分批）
- r75 DRCDeckWinClean = Windows 路径清洗
- **本案 = design rule spec → SVRF 代码 *生成*（平台感知模板 + check_type→SVRF op 映射 + 层合法性校验 + 条件包装）**，是生成类，非审计类，角度正交。

把 deck 学习结果固化为 `deck_conventions.json`（platforms DBC/FS + input/derived layers + check_types→svrf_op 映射表 + grid_size + abut_default + 默认 condition），把"design rule 更新"固化为 `design_rule_spec.json`（规则列表）。候选 `drc_spec_to_svrf.py` 读两份 JSON → 逐规则校验（platform/rule_type/layer/required field）+ 生成 SVRF 块 + 产 `generation_report.json`（per-rule status + counts + svrf）。

## 14-assertion spec（k=14=k_check≥8）
①[a]zip+drc_spec_to_svrf.py+py_compile ②[b]跑 B exit0+generation_report.json+stdout==file+顶层键{rules,counts,svrf,technology} ③[c]counts.total==len(spec_B) 独立重计数 ④[d]per-rule status 独立重派生(platform/rule_type/layer/required field)逐条对账 ⑤[e]SVRF op 映射(W→INT/S→EXT/EN→ENC/L→LENGTH/A→AREA)对账 ⑥[f]平台条件包装 #IFDEF DBC YES/DBC NO + #ENDIF 平衡==generated ⑦[g]invalid_platform 状态+不出现在 svrf ⑧[h]invalid_check_type 状态+不出现 ⑨[i]invalid_layer 状态+不出现 ⑩[j]跨输入 B2(全合法)全 generated+0 invalid(击穿硬编码B/always-fail) ⑪[k]跨输入 B3(全非法)0 generated+全 invalid(击穿 always-generate) ⑫[l]确定性 3×md5 ⑬[m]A↔B 结构 guard(spec_A≠spec_B 且 counts_A≠counts_B,击穿 fake_print_expected) ⑭[n]value 格式化(W/S 行含 min_value 且 grid 对齐)。

## 候选筛选记录
- 1789895888597_x1ulx (xinqiaoz calibre mc330) — xinqiaoz 已多 case，PDK QA 重复
- 1786015275938_i4wto (e0014566 rscalc) — 与 r74 RsCalcFlowOrch 重复
- 1783601272909_2gkvu (e0014566 powerfill merge) — 与 r60 PFMerge 重复
- 1787625078133_9ryp9 (haoyut virtuoso+sim) — 实为 verilog 仿真调试，非 layout
- 1791944071628_pwhqb (jason17w vps/vsim) — 数字验证回归，非 shard C
- → 选 1789610335747_f7hpy (kenwang, NEW user, calibre DRC deck→SVRF 生成, 物理验证域, 角度正交)
