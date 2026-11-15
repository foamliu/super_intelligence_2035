# 深读笔记 · sjaal (1794549248472_sjaal) — CH336_FS 后仿网表「换 bitcell 结果不变」根因诊断

- **trace_source**: user=`e0024852`, host=`hfeg0pkn005`, session_file=`1794549248472_sjaal.messages.json`, match_count=971, mc=971（B 域复活池最高 mc 之一）
- **agent**: zhulong (lead), 198 msgs，1 个真实用户对话段（多轮迭代）
- **旧判定（作废）**: `Q&A inspection 'look at CH336_FS post-pe netlist', not produce-task` → reject
- **新判定（r618 reaudit）**: 可造（debug-Q&A / 根因诊断报告，spice_sim 真实用户意图）

## 真实用户意图（逐轮原文）

- **U#0**: 「你看一下 `/proj/lacaa/V0/workdir/e0012583/simulation` 这里 那个是仿真 CH336_FS 的后仿网表」——找 CH336_FS 后仿网表所在
- **U#65**: 「FS 不是工艺角 FS 对应 DBC」——澄清 FS 是一种 bitcell/工艺变体（对应 DBC 结构），不是 PVT 工艺角
- **U#80（核心意图）**: 「运行 `…/CH336_FS_guojing/stimulus_pex_rev06_model_rev04.sp` 的时候 我从原来的 CH252 换成 336 网表的 width 换成了 40 但是我现在仿真出来的结果跟 252 一样 你分析一下我那里错了」——**根因诊断：换 bitcell + 改 width 后仿真结果不变，定位错在哪**
- **U#134**: 粘贴 HSPICE 报错 `**error** (././CH336_bitcell_FS.netlist:26) Definition of model/subckt "hc_pu_fs" is not found for the element "xi_bitcell_fs_ileak^xpu1"`
- **U#166**: 「`/proj/lacaa/V0_Virtuoso/model/current_PF_v0d01_Rev06/hspice` use this model」——用户尝试改用 PF 模型库（错误尝试）

## 助手工具链 + 关键发现（ground truth）

1. `list_allowed_files` / `read_files` 定位 `CH336_FS_guojing/` 目录，读 `stimulus_pex_rev06_model_rev04.sp`、`CH336_bitcell_FS.netlist`、`CH336_HC_Bitcell_FS_PIN.dspf`
2. `run_approved_command` grep DSPF 实例 → `XMPU2 … hc_pu_fs l=6e-09 wgaa=4e-08 nfin=1 w=4e-08`（**width=4e-08=40nm 与用户「width 换成 40」一致**），`XMPG2 … hc_pg_fs`，`XMPD2 … hc_pd_fs`——器件模型为 `hc_*_fs` 系列
3. grep SRAM 模型库 `current_SRAM_v0d1_Rev06/35H_DBCFS_Model_SRAM_v0d1_Rev06.lib` 的 top-level corner：`tt_sram_dbc` / `tt_sram_fs` / `ff_sram_dbc` / `ff_sram_fs` / `pre_sim_dbc` 等
4. `tt_sram_dbc` corner 定义 `hd_pu_dbc`/`hd_pg_dbc`/`hd_pd_dbc`（**hd_*_dbc**，非 hc_*_fs）；`tt_sram_fs` corner 定义 `hc_pu_fs`/`hc_pg_fs`/`hc_pd_fs`
5. HSPICE 报错 `hc_pu_fs` not found ⇒ stimulus 的 `.LIB` 加载了 `*_sram_dbc` corner（只给 `hd_*_dbc`），DSPF 器件却要 `hc_*_fs` ⇒ 模型未定义 ⇒ 仿真 abort ⇒ **新网表没真正跑，结果与 CH252 一样**
6. 用户改用 PF 模型库 `current_PF_v0d01_Rev06`：grep 整个 PF 库树 **0 个 `hc_*` 模型** ⇒ 改用 PF 库是错误修复
7. 助手结论（U#184 ask_question + U#186 read_files）：**保持 SRAM 库 + 切到 `tt_sram_fs` corner（提供 hc_*_fs，与 DSPF 匹配）** = 正确修复

## 根因链（操作化）

DSPF 器件引用 `hc_*_fs` 模型（width=40nm，HC bitcell FS 变体） → stimulus `.LIB` 却加载 `tt_sram_dbc` corner（仅定义 `hd_*_dbc`） → `hc_pu_fs` 未定义 → HSPICE model-not-found abort → CH336 新网表未执行 → 结果与 CH252 相同 → 用户误以为「换了没用」 → 错误尝试改用 PF 库（PF 库无 hc_* 模型，同样失败） → 正确修复 = SRAM 库 + `tt_sram_fs` corner。

## 拟造任务形态（r622 复活池变现 #4）

`EDA-Eval-DesignFlow-SimModelMismatchDiag-001` · spice_sim L1 便携 · debug-Q&A / 根因诊断报告
- A 档 trace-faithful：保留真实 bitcell 名 CH336、真实模型族 `hc_*_fs`、真实 corner 命名 `tt_sram_dbc`/`tt_sram_fs`、真实 width=40nm、真实 HSPICE 报错原文
- SUT 任务：写 `diagnose_model_mismatch.py(sim_dir, out_json)` 解析 stimulus.sp / DSPF / sram_model.lib / pf_model.lib / run.log，产出结构化诊断 JSON（错误、器件模型、loaded corner、缺失模型、候选修复 corner、dbc/fs 类型失配、PF 库无 hc_*、推荐 corner、根因）
- hidden B：CH420 bitcell、width=60nm、加载 `ff_sram_dbc`、报错 `hc_pg_fs`、推荐 `ff_sram_fs`（全异输入，cross-input guard）
- k≈13，含 cross-input guard（重跑 B==oracle_B / A vs B 全异证非硬编）+ 负结果断言（PF 库无 hc_*）
