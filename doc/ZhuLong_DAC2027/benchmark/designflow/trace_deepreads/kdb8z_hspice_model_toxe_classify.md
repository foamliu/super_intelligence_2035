# trace_deepread: kdb8z — HSPICE 模型包薄氧/厚氧分类

- **session**: `1793704886522_kdb8z.messages.json` · user `owench` · host `pkn002` (10.129.2.11)
- **mc**: 12 (spice-cnt 14 / tot 82, ratio 0.171) · 65 msgs / 31 tool_use
- **domain**: spice_sim (parse-bound produce-task)
- **trace_source**: 真实 cline v3 session，单 trace 闭环（3 条 user prompt，其后 62 条全 tool_use/result）

## 用户原话（逐字）
1. `/apps/imctf/models/V1/model_local/V1_HK_Model_L5_v0d9_Rev02_t02/V1_HK_Model_L5_v0d9_Rev02_t02.sp 分析一下这个model`
2. `mos器件有哪些 怎么分类`
3. `按照薄氧/厚氧分一下`

## agent 工具链
`run_commands ls` 模型目录 → `list_allowed_files` → `read_files` 读 .sp + incFile_V1_HKMG (35 万行 / 23MB) + incFile_lp → `run_approved_command grep .lib/.endl/.param/.model` → `editor` 写 analyze_model.py 多轮迭代（scan_lib_top / scan_models / blocklines / dump_model / per-device toxe/vth0/u0/k1 提取）→ `run_approved_command(python-runner)` 跑出结果。

## 关键产物（agent 实测）
- 入口 `.sp` (331 行) = corner 包装：`.lib pre_sim` + 9 工艺角 (tt/ft/st/tf/ts/ff/ss/fs/sf) + 9 全局角，每个 corner 块通过 `.lib 'incFile_V1_HKMG' mos` 等把模型正文按分区组装。
- `incFile_V1_HKMG` (352515 行 / 23MB)：`.LIB mos` (line 18755) ... `.ENDL mos` (line 351608) 巨块 + bjt/diode/res/nicap/flag 小块。
- mos 块含 1370 个 `.MODEL`，折叠为 **42 个基础器件**（NMOS 28 / PMOS 14），均 BSIM6 (Level=77, Version=107, tnom=98°C)。
- 按 `toxe` 分两档：**薄氧** ntn/ptn 系 + SA（toxe ~1.5-1.65nm），**厚氧** ntk/ptk 系 + WL 阵列（toxe ~4.3-4.8nm）。
- 边缘：`ntk_wl` (Level=72) **无 toxe**，只有 `toxp=6.8E-10`，按族 (ntk_) 归厚氧（阵列/字线）。

## 真实器件 toxe（自 incFile_V1_HKMG mos 块 grep 提取 leading numeric）
薄氧：ntn=1.55E-9, ntn_lv/lvio/m/esd=1.55E-9, ntnlv_lsa=1.5E-9, ntnlvio_*=1.55E-9, ptn=1.65E-9, ptn_lv/lvio=1.65E-9, ptnlvio_sa=1.65E-9
厚氧：ntk=4.5E-9, ntk_lv/hv/esd=4.5E-9, ntk_s=4.5E-9, ntk_sv1/sv2=4.15E-9, ntk_esd_hv=4.2E-9, ntk_wl=(无toxe,toxp=6.8E-10), ptk=4.8E-9, ptk_lv=4.36E-9, ptk_esd=4.8E-9, ptk_s=4.36E-9, ptk_sv=4.35E-9, ptk_lvl=4.8E-9

## case 合成方案（已交付 EDA-Eval-DesignFlow-MosToxeClassify-001）
- **track = synthesized**：A-faithful 不可行因真实 incFile 23MB 超 sandbox 资产 + SUT parse 超时风险。用真实器件名 + 真实 toxe 值（leading numeric）合成紧凑 deck（~120 行），保留真实 HSPICE 结构（.lib corner 包装 + .LIB mos/.ENDL mos + 带 single-quote 的 toxe 表达式 + 无 toxe 的 ntk_wl 边缘器件）。
- **deliverable**: `mos_toxe_classify.py` (CLI `<model.sp> <output.json>`, stdlib only) — 解析入口 .sp 找 `.lib '<inc>' <block>` → 解析 incFile 的 mos 块 → 提取 .MODEL name/type/toxe（leading numeric of quoted expr）→ 折叠基础器件（strip .N）→ 分类 (toxe<2.5e-9=thin, else thick; 缺 toxe 按 ntk/ptk→thick 族回退) → 出 JSON。
- **A (可见)**: 22 基础器件 / 25 section (薄氧 1.5-1.65nm, 厚氧 4.15-4.8nm, ntk_wl 无 toxe)。
- **hidden B**: 26 基础器件 / 29 section，**不同** toxe (薄氧 1.7-2.0nm, 厚氧 5.0-6.5nm)，保留无 toxe 边缘器件 `ntk_wl2`。
- **check.py**: 16 断言 (a-p)，跑 B + A 交叉核对（击败硬编码 B 的 stub）。ref 16/16 PASS + 4 neg (empty/print/hardcoded_a/core_deleted) 全 FAIL + §4.9 三假全 FAIL。

## 价值
印证 B r389 讨论发言「spice_sim hard part 在 parse 不在工具链深度」——kdb8z spice-ratio=0.171 因 model-deck-parse session 的 hspice keyword 计数低（parse-bound 特性），实为 CLEAN spice_sim produce-task，与前轮 lcbck (ratio 0.341) 同类。说明 spice-ratio≥0.35 启发式对 parse-bound spice 域系统性低估，mc≥10 下仍需逐条核验 cross-shard fresh。
