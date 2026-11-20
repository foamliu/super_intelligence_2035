# r547 deepread: z6z4t — Nicap Pcell parameter extraction (layout_aether)

**trace**: 1794480004581_z6z4t · yu23z@hfeg0plg89 (10.129.x) · mc=158
**keywords**: pyaether:345;drc:212;aether:166;cellview:156;dbget:62;netlist:36;dbopencv:23;virtuoso:22
**size**: 327 msgs, 1.18MB
**date**: 2026-11-12 → 2026-11-13

## USER conversation flow (r527 verb法)

| # | text (verbatim, ≤600 char) | verb 分类 | A档? |
|---|---|---|---|
| U#0 | `11` | test garbage | ✗ |
| U#2 | `你可以编辑版图么` | capability Q&A | ✗ |
| U#6 | `我需要抓取出Aether layout中所有Nicap Pcell的parameter（nc/nr/c）` | **produce-task author-new-script** | **✓ A档合格** (提需求未给根因/方案) |
| U#90 | `如何抓取Aether layout中选中的所有Pcell的parameter` | howto rephrase (selection-based) | ✗ |
| U#123 | `让该脚本可以自定义设置想要抓取的parameter` | modify-existing (add config) | ✗ (给方案) |
| U#189/190 | `把这个txt文件中抓取的nc/nr/c参数整理成ncXnr=c的格式...重复项合并...输出成excel` [attach: selected_pcell_params_20261112_190042.txt] | produce-task post-process | ✗ (B档: 给详细spec) |
| U#281 | 同上 + `按照nc从大到小排序，如果nc相同再以nr从大到小排序` | modify-existing (add sort) | ✗ |
| U#289 | `c的值四舍五入了，不可以四舍五入，重新输出` | debug-fix (根因=rounding, 方案=no round) | ✗ |
| U#315 | `...整理成ncXnr=c...重复项合并...按照c从大到小排序...输出成excel` [attach: selected_pcell_params_20261113_092931.txt] | produce-task post-process (fresh sort spec) | ✗ (B档) |

## Assistant flow

1. **A#7-A#41 RAG 检索** (23× search_apis + 5× get_api_details): 查 Nicap Pcell API → `aeGetCurDesign()` / `cv.instances` / `dbCheckIsPCell(inst)` / `aeEmyInstGetParameter(paramName, inst, bEval=True, bRawType=True)` / `cdfGetInstCDF(inst)`
2. **A#43-A#87 SandBox run_code** (3×): probe pyAether (Sandbox 服务没启动 → 失败)
3. **A#51-A#89 editor** (8×): 写 `extract_nicap_params.py` — 在 Aether Python Console 内运行的 Nicap Pcell 参数提取脚本
4. **A#98-A#176 editor** (12×): 写 `get_selected_pcell_params.py` — 选中 Pcell 参数提取 (U#90/U#123 可配置参数)
5. **A#193-A#251 editor** (12×): 写 `process_nicap_to_excel.py` — txt→excel 后处理 (U#189/U#315: ncXnr=c 格式 + 去重 + 排序 + 不四舍五入)
6. 实际提取产物 = 两个 txt 附件 (用户在 Aether 内运行脚本后上传结果)

## 真实数据 (用户上传的提取产物)

### selected_pcell_params_20261113_092931.txt (35 PCells, 全 Nicap_1S)
- Design: `drcpa_array/m768Meg_Ys_TOP_TOP_t_base_cap/layout`
- 格式: 每个 PCell block: Instance / Master / # Params / Params: nc=INT / nr=INT / c=FLOAT\npF
- Master 全 = `drcpa_MAT/Nicap_1S/layout`
- 含重复 (nc,nr,c) 三元组: (175,311,272.125)×5, (367,263,482.605)×2, (295,311,458.725)×3, (271,311,421.405)×2, (415,311,645.325)×2, (199,71,70.645)×2, (151,311,234.805)×3, (175,71,62.125)×2
- c 值精度 3 位小数 (70.645, 122.845, 421.405...)

### selected_pcell_params_20261112_190042.txt (41 PCells, Nicap_1S + Nicap_2S)
- Design: `drcpa_array/m768Meg_Ys_TOP_nor_t_base_cap/layout`
- Master 含 Nicap_1S 与 Nicap_2S 两种
- Nicap_2S 参数: (391,152,148.58), (199,152,75.62), (127,272,86.36), (223,152,84.74), (751,128,240.32)
- c 值含 2 位小数 (148.58, 75.62, 86.36, 84.74, 240.32) — 比 1S 的 3 位少一位

## Case 合成决策

- **task**: U#6 (A档合格 produce-task) → **B档 mock-behavioral** 重构 (承 r539/r541/r542/r544/r545/r546 族)
- **核心算法不变**: 遍历 instances → 过滤 Nicap Pcell (master 含 "Nicap" + is_pcell) → 提取 nc/nr/c → 格式化 "ncXnr=c" → 去重 → 按 c 降序 → 输出 report.json
- **mock fixture**: layout.json (instances[] with name/master/is_pcell/params) 忠实编码真实 nc/nr/c 值 (from 092931/190042 txt) + 非 Nicap distractor (MOS/RES Pcell, 非 Pcell cell)
- **anti-hardcode dual-hidden**: B (13 Nicap_1S, 11 unique) / B2 (8 Nicap_1S+2S, 7 unique)
- **判分**: code-execution-validation (run script on hidden B → parse report.json → assert structure+values+dedup+sort+no-round+filtering)
- **domain**: layout_aether (78→79)
- **谱系**: produce-task 第十一子型 pcell-param-extract (前: deck/GDS图案/几何工具/track/label/rscalc/PG-rail/DRC-checker/QA-config)
