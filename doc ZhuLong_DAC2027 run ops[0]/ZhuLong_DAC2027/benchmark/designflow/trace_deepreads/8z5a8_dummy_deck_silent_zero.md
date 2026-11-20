# Deepread: 1792715254915_8z5a8 — Calibre Dummy deck silent-zero-output diagnosis

- **session**: `1792715254915_8z5a8.messages.json`
- **user/host**: xinqiaoz / hfeg0pkn004
- **match_count**: 611 (mc>=300, safe 1.43 MB)
- **domain**: physical_verify (calibre -drc dummy)
- **status**: → case `EDA-Eval-DesignFlow-DummyDeck-001` (L2, calibredrv)

## 真实任务
PDK QA 项目跑 `calibre -drc -hier calibreDummy.rule` 做 Dummy 生成。部分 mask 的 dummy GDS 没生成，
`drc.sum` 报 `No output is produced. File XXX.gds will not be generated.`，进程 exit 0、无 ERROR（静默零输出）。
用户用 handoff 技能恢复上下文后继续诊断。364 msgs / 163 tool_use / 7 substantive user msgs。

## 根因（双重实验验证）
Dummy 的生成范围被 deck 中的"允许填充区"层严格限定：
- **MP / MPstack 型** mask：`FILLZONE BORD`（填整个 board extent）→ 不依赖任何 derived 层 → 正常生成。
- **CMP / 2ND / CMP_LINE / SOH 型** mask：`FILLZONE BORD NOT <derived_layer>`（只在 `<derived_layer>` 为空的区域填 dummy）。
  `<derived_layer>` 经 `DERIVED <name> = LAYER <l> DATATYPE <dt>` 解析到 GDS 的 `(l, dt)`。
  当该 `(l, dt)` 在测试 GDS 里**完全为空**时，`BORD NOT <空层>` = 整个 BORD 进入避让块 → 填充区塌缩为空
  → DFM FILL 无处可填 → **静默零输出**（exit 0，no ERROR）。

`ORIGINAL LAYER STATISTICS` 里失败 mask 的 `ori_defMainBLK_XXX = 0` 且 `dum_defMainBLK_XXX = 0` 印证填充区为空。

## 诊断方法论（trace 里 agent 做的交叉关联）
1. **drc.sum** → 每 mask 生成/失败状态 + ori/dum 统计
2. **SVRF deck** → 每 mask 的 TYPE + FILLZONE 子句 + DERIVED 名 → (l,dt)
3. **测试 GDS** → calibredrv `peek -layers` 取实际 (l,dt) 清单
4. 三者交叉：失败 mask 的 BORD NOT <derived> 的 (l,dt) 是否在 GDS 里 → 缺层 = missing_allowed_fill_zone_layer；在层但仍败 = other

## case 设计（DummyDeck-001）
- **A（可见）**：自然规律 deck — 4 层 GDS (10/0,11/0,12/0,20/0)，3 个 fill-zone derived (301/11, 301/0, 15/7) 全缺席
  → 6 MP 型成功 / 6 CMP·2ND·SOH 型失败（全缺层）→ verdict=MISSING_FILL_ZONE_LAYERS。
- **B（隐藏）**：故意反转 TYPE↔成败 + 干扰 datatype + other 失败
  - 7 层 GDS (40/0,41/0,42/0,50/0,55/5,60/3,70/0)，干扰：55/5 在但 CORE:TEG=55/8 不在；70/0 在但 SOH:ARR=70/9 不在
  - MP 型 MET3 失败（缺 55/8）；CMP 型 VIA0/VIA1 成功（REV:peri=60/3 在）；ETCH=other 失败（60/3 在但仍败）
  → generated=[TOPV,MET2,VIA0,VIA1], failed=[MET3,ETCH,COAT,SOH1,SOH2,NCU], verdict=MIXED_FAILURES
- **14 条断言** a-n：含 L2 真工具校验 (k: gds_layers==calibredrv peek)、跨输入 guard (m: A 上跑报 A 非 B)、确定性 (l)、
  精确 (l,dt) 匹配 (i, 击败只比 layer 号)、root_cause 分类 (j, 击败按 TYPE 猜)。
- **2 naive 负样本** + 3 §4.9 fakes 全 FAIL；NEGATIVE_SELFTEST ALL-OK（.75 calibredrv 2020.1_36 真跑 14/14 PASS）。

## 关键技术细节
- calibredrv `-a layout peek <gds> -layers` 实际输出格式：`{10 0} {11 0} {12 0} {20 0}`（裸 pair 序列，**无** `layers {...}` 外壳）。
  最初假设的 `layers {{L DT}...}` 格式错误，导致 gds_layers 解析为空 → 条件 k 空洞通过。修正后正则 `\{(\d+)\s+(\d+)\}` 直接搜裸 pair。
- SVRF deck 的 MASK 行格式：`MASK <name> TYPE <type> FILLZONE <expr>`（TYPE 后有空格，type 无 `TYPE_` 前缀）。
  最初 deck 写成 `TYPE_CMP_MPstack`（无空格）→ 正则 `TYPE\s+(\w+)` 不匹配 → masks 全漏 → g/h/i/j 空洞通过。修正后 deck 改 `TYPE CMP_MPstack`。
- write_file(content=plain) 对 .py 文件可靠（py_compile + md5 校验通过）；base64 经 run_commands 传输会损坏 `+`/`)` 字符（check.py 被毁），不可用于 .py。
