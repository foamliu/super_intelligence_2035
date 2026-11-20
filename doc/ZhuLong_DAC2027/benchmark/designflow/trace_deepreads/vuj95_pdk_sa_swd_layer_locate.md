# 深读笔记 — vuj95 (marryma @ hfeg0pkn005, mc1126) — PDK SA/SWD 版图层定位

**trace 源**：`.75` scp `10.129.2.14:/home/marryma/.cline/data/sessions/1794227337092_vuj95/1794227337092_vuj95.messages.json`（1.4MB, 105 msgs, 1 真实用户轮）。
**真实用户原话**：「可以帮我找一下SA 和 SWD 的版图吗？」（U#1, mode=act）。

## 真实意图
PDK/characterization 工程师 marryma 维护 Cadence OA smic14ff 工艺库，要找 SA 和 SWD 两个"版图层"。助手遍历 `/home/marryma` 下多版本 PDK 快照（`0.0.8_toquanhao` / `0.0.9_toquanhao` 等，以及 `/proj/lxcaf/V0/workdir/marryma/0.0.8~0.1.1`），用 `list_allowed_files`/`read_files`/`grep` 翻 `techfile.tf`、`layermap.layermap`、`readme.txt`。

## 真实结论（ground truth, 实测于 .75）
- **SA（Self-Aligned mark）**：在 `0.0.8_toquanhao` 有定义。
  - `layermap.layermap` 实测 line 1345/1346：`RLDEV  mark1  302  51`（SA mark, GDS 302:51）与 `RLDEV  mark67  302  517`（SA split mark, GDS 302:517）。
  - `techfile.tf` 实测 line 295/296：`( mark1  600  mark1 )` / `( mark67  601  mark67 )`（purpose 600/601）。
  - `readme.txt` 实测 line 125/126（v0.0.8 段）：`c.Add 302;51 SA mark follow CXMT` / `d.Add 302;517 SA split mark`。
  - readme v0.0.8 changelog owner=marryma date=20261012，"KLS Layer definition v0.01_Rev08_S5 (20261010).csv specification"。
- **SWD**：在 `0.0.8_toquanhao` 全目录 `grep -i SWD` 实测 0 命中 ⇒ 所有版本均未找到任何名为 SWD 的 layer/cell/mark 定义（**负结果**）。

## 助手工具链
全程无 EDA 仿真工具执行；仅 `list_allowed_files`（≈30 次）、`read_files`（≈20 次）、`run_approved_command grep`（1 次）。属 L1 离线文本检索/解析。

## 旧判 vs 新判
- 旧判（2026-11-10）：`REJECT file-search consulting (SA/SWD 版图查找), no produce deliverable, wrong-type`。
- 新判（11-15 reaudit）：可造 —— "查文档/找文件"是真实用户意图，新标准恢复；造「PDK 层定位结构化报告」check 验跨文件关联/负结果/跨输入泛化，stub 必 FAIL。

## 合成形态
case_id `EDA-Eval-DesignFlow-PdkLayerLocate-001`，domain=characterization，layer=L1，A 档 trace-faithful。
- A（可见 PDK）：合成 `pdk/{0.0.8_toquanhao,0.0.9_toquanhao}/{techfile.tf,layermap.layermap,readme.txt}` + `cds.lib`。0.0.8 含 SA 真值（302:51/302:517, mark1/mark67, RLDEV, purpose 600/601, readme v0.0.8）；0.0.9 为 decoy（无 SA/SWD）。SWD 负结果。
- hidden B：0.0.8 用**全异**数值 —— SA=305:88/305:891（mark44/mark45, purpose 612/613），**SWD=304:77（mark77, purpose 614, found=True）**。0.0.9 decoy 同构无 SA/SWD。
- 任务：写 `locate_layers.py(pdk_root, out_json, [names...])` 解析三文件并关联（readme Add L;D NAME role → layermap (L,D)→purpose → techfile purpose num），产出 schema 化 `layer_report.json`，打包 submit.zip。
- 判分 k=12，含 cross-input guard（A/B 在 SA layer_number、SA datatype、SWD found 三项全异）+ 负结果断言（SWD found=false）+ decoy 版本排除。

## 自验
ref 12/12 PASS + 4 negs（naive_hardcode_a/always_not_found/print_only/core_deleted）全 FAIL + §4.9 degenerate 三假全 FAIL + negative_selftest ALL GREEN。k_rationale==k_check==12 ✓。

## 复活池进度
191 可造 → 已造 3（r619 am99r / r620 hwbr5 / **r621 vuj95**），余 188。
