# trace deepread — 1789558497514_ogbej (ellawu @ hfeg0pkn002, mc=296, physical_verify)

## 概要
- **用户**：ellawu（Aether implant-fill DRC flow 重度用户，已有 SvrfTvfLayerMapGen/DrcQaWidthTypeGeom 等 case）
- **工具画像**：88 calibre + 62 dbGet + 32 pyAether + 37 schematic + 13 virtuoso + 12 cellview（summary.tsv 计数含文档提及）
- **真实 trace 主题**：`IMCleFillImplantDrc.py`（174KB Python，Aether 上跑 implant fill + calibre DRC）反复跑同一 cell 出现「后面的脚本使用之前生成的 dummy 的问题」

## 对话流（209 msgs，2 轮 attach）
1. **msg[0]** 用户：「看一下这个脚本」+ attach `IMCleFillImplantDrc.py`（174KB）
2. **msg[6]** 用户：「会出现后面的脚本使用之前生成的 dummy 的问题」← **核心需求（A 档任务说明候选，未给根因/修复）**
3. **msg[11]** 用户：「需要」
4. assistant 读附件（分片 read_files 918-1400 等）→ 读 workdir `/proj/decqa/V0/workdir/ellawu/` 下 `IMCutGenPGDummy_for_Logic.py` 等 → 创建 `IMCleFillImplantDrc_fixed.py`（编辑器 insert 分片，反复超 6000 字符限制）
5. assistant 创建 `IMCleFillImplantDrc_patch.py` v1.2.0（monkey-patch，6 FIX）→ **msg[133]** 给「修复了 6 个关键问题」总结表
6. **msg[134]** 用户：「这样改 flow 有问题吗」+ 重 attach（174.1KB）→ assistant 指出只 `rm -rf workDir/*` 不够（没删 layout 上 dummy shapes）
7. **msg[150]** 用户问 `os.system("rm -rf "+workDir+"/*")` 作用
8. **msg[160]** 用户报真实运行错误：`cxmtG5_CIP dscqa ella AG_VdivActAmp / STEP1: stream out gds done! / [Errno 2] No such file or directory: '.../runFillImplant.rule'`
9. **msg[200]** 用户：「不要重叠的，只要如果存在旧的文件就删掉目录下的内容」
10. **msg[208]** 用户：「这个脚本有什么问题吗」+ 重 attach（174.3KB）→ assistant 最终改写 `fix_implant.py`

## 6 个「dummy 残留」问题族（gold patch `IMCleFillImplantDrc_patch.py`）
1. **stale_fill_shapes**：上次 fill 的 shapes（`implantFlag=fill_implant_by_drc`）未删 → Stream Out 导出旧 dummy → DRC 报 0 gap → flow 跳过 fill。**FIX1** `_patch_cleanup_previous_fill(cv, extra_layers)`：遍历 cv.lpps，删 `implantFlag==fill_implant_by_drc` 的 shape
2. **stale_gds**：`implantFill_flatten.gds` / `runFillImplant.rule` 上次产物未删。**FIX2** `_patch_remove_stale_gds(work_dir)`：`os.remove`
3. **unbound_projname**：`workDir` 不匹配 `^/proj/<proj>/<ver>/` 时 `projName`/`ver` 未绑定 → UnboundLocalError。**FIX5** 默认 `projName='ddcpa'` `ver='V0'`
4. **hardcoded_layer_list**：remove 函数写死 layer 列表，漏清 form 新启用层。**FIX3** `_patch_build_layer_dict(form)` 从 form 字段动态构建；`KNOWN_IMPLANT_LAYERS` 32 层
5. **length_not_len**：`IMCleRemoveImplantFill` 用 SKILL `length()`（非 Python `len()`）→ NameError。**FIX4** `_patched_IMCleRemoveImplantFill` 用 `len(lpp_list)`
6. **inst_name_collision**：instance 基名 `Inst_autofillbydrc` 重跑复用 → 名字碰撞

## gold patch 结构（`patch_full.py` 9317 字节，已落 .75 workdir）
- `KNOWN_IMPLANT_LAYERS` = 32 层（y0/GX/DNW/PW/PCH1-3/AVT/NCH1-4/DGX/NGA/PGA/PL1-3/NL1-4/NSD/PSD/PCN/PCP/NAF/PDR/NMR/PMR/KGX/SGD/SAB）
- `_patch_cleanup_previous_fill` / `_patch_remove_stale_gds` / `_patch_build_layer_dict` / `_patched_IMCleRemoveImplantFill` / `_patched_fill_implant_flow`
- 末尾 `_orig.IMCleRemoveImplantFill = _patched_...` / `_orig.fill_implant_flow = _patched_...` 应用补丁

## 原始 buggy `fill_implant_flow`（orig_script_part.py 41638 字节）
- 31 个 `if hasattr(form,'fillXX') and form.fillXX.value: args=tconc(args,[...])` 硬编码逐层
- `workDir=getWorkingDir(); if rexMatchp(...): projName=rexSubstitute(...); ver=...` ← 不匹配则未绑定
- 无 pre-cleanup，直接 `IMCle_generate_implant_fill(args, cores_num, processName, projName, ver)`
- `IMCle_generate_implant_fill`：workDir2=`/proj/<proj>/<ver>/ver/drc/<user>/auto_implant/<lib>/<cell>`，写 `runFillImplant.rule`(211行)、`implantFill_flatten.gds`(241行)、`dbCrtInst(cv,...,inst="Inst_autofillbydrc")`(280行)

## case 设计（B-synthesized, L1-boundary, k=14 a-n）
- **SUT 写 `implant_dummy_diag.py`**（CLI 2 参 `<flow_state.json> <form_config.json>`，stdlib），读流程状态快照 + form 配置，检测 6 类 dummy 残留问题，输出结构化诊断 + 修复计划 JSON
- **A 输入**（trace grounded）：cell `ella/AG_VdivActAmp`，workDir 匹配 /proj/dscqa/V0/，5 个 tagged stale shapes（GX/DNW/PW/PL1），stale gds+rule，remove 源用 `length()` 无硬编码列表 → A 检测 4 类问题（stale_fill_shapes/stale_gds/length_not_len/inst_name_collision）
- **隐藏 B**（结构不同）：cell `AG_XtopBuf`，workDir `/home/ellawu/...` 不匹配 → unbound_projname；新层 XXY 启用 + remove 源含 `in ['GX','DNW','PW']` → hardcoded_layer_list；6 个 tagged shapes（GX/XXY/AVT）→ B 检测全 6 类问题
- **B2 干净守卫**：cell `AG_CleanRef`，无 tagged shapes、无 stale 文件、workDir 匹配、remove 用 `len()`、inst_name 带时间戳、fill 源含 cleanup → 0 问题、rerun_safe=True（杀 always-detect）
- **B3 重载守卫**：14 个 tagged shapes（6 层）、2 stale 文件、workDir 不匹配、length()、硬编码列表 → 6 问题 14 stale_shapes（杀 always-clean）
- **14 条 a-n**：见 check.py 与 jsonl test_rationale
- self-verify：golden CHECK PASS 14/14；5 negative 全 FAIL；3-seed sha256 STABLE；E2E jsonl PASS

## 选料判定
- 4vv1y（lizwen mc138）深读为 aether copy Q&A 文档推荐，无交付物，parked
- ogbej（ellawu mc296）真实 implant-fill DRC dummy 残留修复，6 问题族完整闭环，gold patch 真实可部署 → physical_verify 域（78→79）
- DISTINCT from r220 SvrfTvfLayerMapGen（ellawu, SVRF/TVF layer map 生成）/ r218b DrcQaWidthTypeGeom（kenwang, DRC QA width pattern 几何生成）—— 本案首次 ground on **implant-fill DRC flow dummy 残留诊断**（多问题族检测 + 修复计划，非单一生成器/单一规则映射）
