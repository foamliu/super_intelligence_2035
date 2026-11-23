# r1122 (shard B) — 1-case 产出轮: ounw7 → MosCharMultiCornerDeckGenProduce-001

**日期**: 2026-11-24 04:4x
**轮次**: r1122 (loop shard B)
**trace**: `1795418883724_ounw7` (pirinliu@hfeg0plg77, mc55, hspice:403/schematic:198/netlist:120)
**case**: `EDA-Eval-DesignFlow-MosCharMultiCornerDeckGenProduce-001` (k=14 a-n, L1 纯 Python)

## 1. 候选发现

r1121 复查 1124 scan (`ssh_eda_search_20261124_023802/summary.tsv`) top-80 去重 21 sids，
cross-check 台账发现 3 真未 ledger：7pvru(r1121 已 case)/ounw7/nakpz。本轮选 **ounw7**
(pirinliu@plg77, mc55, hspice:403, 强 B-spice)；nakpz waveview-dominant 偏 D 拒。

claim → 台账 1727→1728。

## 2. 深读 ounw7 (217 msgs / 1.39MB)

**真实意图**: pirinliu 有一份 MOS DC 特性仿真 GUI 脚本 `mos_dc_gui.py` (132KB tkinter +
HSPICE bsub 提交，跑 VTSAT/Id-Vgs/Id-Vds/gm-Id 等 MOS 特性测试)。要求：
1. 复制到 `/proj/m2701/V0_DDR4/workdir/pirinliu/device_change` 并做一系列修改
2. **多 corner 多选**：对 model.sp 同时跑 top_tt/ff/ss/fs/sf 五个 corner
3. **多温度多选**：temp1 必选 + temp2/temp3 可选勾选（除 TEMP 扫描模式外）
4. **只输出 `data_overall.csv`**：合并所有 corner×temp，列含 `0_corner,0_temp`（0 前缀保证
   排序最前，数字 0 < 字母 A）；不再输出每 corner/temp 细分 CSV
5. **多 corner/temp 画同一张图**（叠加 PNG + GUI 画布），VTSAT x 轴对数坐标
6. **VTSAT 的 L/W-scan 输入不除 shrink**：模板 `w1='w/shrink' l1='l/shrink'` → `w1='w' l1='l'`
   （后更正为 drawing size；real size = drawing/shrink 只读显示）
7. **默认值**：vcc=0.875, w_min=100n, l_min=30n, temp2=-40, temp3=140,
   model=/proj/m2701/V0_DDR4/model/current/model.sp, NMOS=nulvt_ckt, PMOS=pulvt_ckt,
   instance=main
8. 标题改「MOS特性仿真工具 多corner多temp版」，存为 V2.0 不覆盖原版

**assistant 工具链** (msg 130-216): list_allowed_files + read_files (读 132KB 脚本关键函数)
+ editor (批量 patch V2.0: 标题/corner 默认/选中高亮/VTSAT 去 shrink/VTSAT 对数轴/
多 temp + overall CSV + 叠加绘图/_worker 重写/_poll 适配) + run_approved_command
(py_compile + importlib 加载冒烟测试) + ask_question。最终交付
`/home/pirinliu/Desktop/device_change_v2/mos_dc_gui_v2.0.py` + `run_mos_gui_v2.0.sh`。

**关键产物**:
- `mos_dc_gui_v2.0.py`: 全部 8 项落地，py_compile 通过
- `data_overall.csv` 列: `0_corner,0_temp,<metrics...>`（`_metric_label_prefix` 返回 `"0_"+prefix`）
- VTSAT 模板: `.param w1='w' l1='l' nf1='nf'`（不除 shrink）
- 多 temp: `effective_temps(cfg)` → temp1 + (勾选的 temp2/3)；TEMP 扫描模式跳过多 temp
- deck 生成: 每个 (corner, temp, test) 一个 `.sp`，`.lib '<model>' <CORNER_UPPER>` +
  `.temp <T>` + `.param vvdd=<vcc>`

## 3. reframe (case 设计)

132KB 专有 GUI 脚本无法入沙箱；抽出**核心可验引擎**：spec 驱动的多 corner×多 temp
HSPICE MOS 特性 deck 批量生成器 + overall CSV 聚合器（即 V2.0 GUI 包裹的真用户意图）。

**case = `EDA-Eval-DesignFlow-MosCharMultiCornerDeckGenProduce-001`** (L1 纯 Python)

**工具**: `moschar_deckgen.py <mode> <args>`
- `gen <spec.json> <out_dir>`: 读 spec → 为每个 (corner, temp, test) 生成 `.sp` deck +
  `manifest.json`
- `aggregate <results_dir> <out_csv>`: 解析 `.mt0` 结果文件 → 写 `data_overall.csv`
  （列 `0_corner,0_temp,<metrics>`，0 前缀排序最前）

**spec 字段** (faithful to 真实默认值):
- model/device_n/device_p/instance/vcc/shrink
- corners: [tt/ff/ss/fs/sf]
- temp_config: {temp1, temp2, temp2_enabled, temp3, temp3_enabled} → effective_temps
- tests: [{name, type(l_scan/w_scan), mos, w/l, l_values/w_values}]
- TEMP 扫描模式 test.type=temp_scan → 只跑 temp1，不多 temp

**deck 内容** (每 (corner,temp,test)):
- `* MOS char <test> <mos> corner=<corner> temp=<temp>`
- `.lib '<model>' <CORNER_UPPER>`
- `.temp <temp>`
- `.param vvdd=<vcc>`
- `.param w1='w' l1='l' nf1='nf'`  ← V2.0 关键: 不除 shrink
- `X<instance> d g b s <device> w='w1' l='l1'`
- DC 扫描 + `.meas` VTSAT

**check 14 条** (a-n):
- a: gen exit0 + out_dir 非空 + zip compile
- b: deck 数 == corners×effective_temps×tests (temp_scan 只 temp1)
- c: 每 deck `.lib '<B_model>' <CORNER_UPPER>` 匹配其 corner
- d: 每 deck `.temp <T>` 匹配其 temp
- e: 每 deck `.param vvdd=<B_vcc>` 正确
- f: 每 deck `.param w1='w' l1='l'`（不除 shrink，anti 回归）
- g: 每 deck 实例行 `X<B_instance> d g b s <B_device> w='w1' l='l1'`
- h: manifest.json 条目数与 deck 数一致 + 每条 (corner,temp,mos,test,file) 正确
- i: effective_temps 逻辑：temp1 必选 + enabled temp2/3；temp_scan test 只 temp1
- j: aggregate exit0 + data_overall.csv 存在非空
- k: data_overall.csv 前两列 == `0_corner,0_temp`
- l: data_overall.csv 行数 == corners×effective_temps×tests
- m: anti-hardcode-A: B decks 无 A token (device/model/instance 词边界)，B token 存在
- n: 3-seed gen sha256 一致

**A** (faithful: 真实默认值 nulvt_ckt/main/vcc=0.875/model=/proj/m2701/.../model.sp/
corners tt_ff_ss_fs_sf/temps 25,-40,140/shrink 0.85)
**hidden B** (五重 anti-hardcode: ①device=nrvt_ckt/prvt_ckt ②instance=m0 ③vcc=1.2
④model=/proj/chip_t28/rel2.1/models/primitive.sp ⑤corners typ/fst/slw 4 个 + temps
27/125/-55 + temp3_enabled=false + 一个 temp_scan test 验 i 分支齿)

**3 negs**: empty(gen 空)/print_only(打印期望 deck 名不生成)/core_removed(gen deck 但
w1='w/shrink' 回归 + overall 无 0_ 前缀 → f/k FAIL)

## 4. 自验
- REF 14/14 PASS
- §4.9 三假 (empty/print_only/core_removed) 全 FAIL
- 3-seed sha256 一致
- 台账 ounw7 claim→mark case ✓
