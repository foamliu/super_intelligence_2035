# Deepread: tvc27 — yongk1li IDD→IPF flow script modification

- **session**: 1789718624102_tvc27 (90 msgs, 315KB, 2026-09-18, agent=lead/zhulong-deepseek)
- **user**: yongk1li @ hfeg0plg77 (10.129.8.121)
- **domain**: physical_verify (Totem-SC Signal EM analysis flow tooling; drc:98/lvs:77 kw from ~/bin siblings)
- **mc**: 88 (summary_20261121)
- **cross-shard revival**: shard B parked 2026-11-13 as misfiled spice_sim (B note acknowledges "C physical_verify drc:98/lvs:77 dominant"); C r956 revived per 11-15 rule

## Real user task flow

1. U#0: "你是什么模型" (greeting)
2. U#2: 问 `/home/yongk1li/bin/totem_sc_signal_em/` 是干嘛的 → agent 解释是 Totem-SC Signal EM Launcher (Tkinter GUI, LPE/SignalEM/Rpt 三段流程)
3. U#10: 读 `/proj/drcoa/V0/workdir/yongk1li/simulation/DDR5TOP_4_channel_gds_only/white_box_cell/idd_to_ipf_flow.py` 看是干嘛的 → agent 完整解读：IDD CSV → IPF 功耗文件生成脚本（解析层级化 IDD CSV → 按 OUTPUT_SPECS 规则筛选实例 → 从 GDS 提取 cell 名纠正大小写 → 输出 Totem-SC IPF 格式 `cell_name total_power power_pin`）
4. U#24: **核心修改需求（两条）**：
   - ① 不许兼容老功能：删除 `TARGET_LEVEL`/`TARGET_CELLS`/`TARGET_FATHER_CELLS` 旧配置变量 + `main()` 里的 `if OUTPUT_SPECS is not None ... else ...` fallback 分支
   - ② `apply_spec` 大小写不敏感比较：CSV 里 cellName 都是小写（如 `bcenterca`），但 `OUTPUT_SPECS` 规则里写的是混合大小写（如 `BCenterCA`），直接 `in` 比较匹配不上 → 需要在 `apply_spec` 里把 father/include/exclude 都先 `.lower()` 再比
5. agent 因目标文件 read-only，把新版本（含两处修改）写入 `~/bin/idd_to_ipf_flow.py`（可写目录），分块 editor 替换：
   - 新增 `_to_lower_set()` 替代 `_to_set()`，把 father/include/exclude 统一转全小写集合
   - `apply_spec` 所有比较先转小写
   - 删除注释掉的旧 `TARGET_LEVEL` 等 + `main()` fallback 分支，直接 `for spec in OUTPUT_SPECS`
   - 保留 `extract_gds_cell_names(gds_path, needed_lower=None)` 流式读 GDSII STRNAME record
6. U#65-82: 改 `INPUT_DIR`/`OUTPUT_IPF` 为绝对路径（`/proj/drcoa/V0/workdir/yongk1li/simulation/DDR5TOP_4_channel_gds_only/white_box_cell/IDD` 和 `.../output.ipf`），用户多次纠正（相对→/IDD→完整绝对路径）
7. U#83-89: **最终任务** — 读 `output.ipf`，把所有涉及到的 cell 提取出来，去掉 `_0`/`_1` 实例编号后缀，按 `WHITE_BOX_CELLS { ... }` 格式打印供用户做替换。agent 提取了 50+ unique cell（BCenterL/array1G_Bot/.../R_AryBnkRptNear/BnkGTopX4_Bot/BnkGTopX4_Top/...）

## Key intent (reframe basis)

真实用户意图 = **修改一个 EDA 功耗流脚本（IDD→IPF）**，核心两处修改：
1. **死代码清理**：删旧配置兼容（TARGET_LEVEL 等 + fallback 分支）
2. **Bug 修复**：`apply_spec` 大小写不敏感匹配（CSV 小写 vs 规则混合大小写）+ GDS cell 名大小写纠正 + WHITE_BOX_CELLS 提取

## C-domain 归属

是。Totem-SC Signal EM = 信号电迁移可靠性验证；IPF = 功耗输入文件；GDS cell 提取 = 版图相关。属 physical_verify（EM/功耗完整性验证流工具）。本 shard 4 domain（layout_aether/layout_virtuoso/pg_layout/physical_verify）中 physical_verify 最贴切。

## 跨 shard 串台检查

- 4-shard ledger: tvc27 仅 B parked（misfiled，B 自认 C 域）
- 4-shard jsonl trace_source: 无 tvc27
- 同 domain 已落库 case 全正交（无 IDD→IPF / case-insensitive cell matching / WHITE_BOX_CELLS 提取 子型）
