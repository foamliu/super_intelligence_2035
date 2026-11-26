# trace_deepread — 1790576052982_qc0nn (chengk / hfeg0pgn022, mc=26)

- session: `/home/chengk/.cline/data/sessions/1790576052982_qc0nn/1790576052982_qc0nn.messages.json` (1.6 MB, 410 msgs, 209 user turns; 12 user text turns)
- summary.tsv: `10.129.35.121 hfeg0pgn022 chengk 1790576052982_qc0nn 26 hspice:45;analog:20;cmos:8`
- domain kw: hspice:45 / analog:20 / cmos:8 → spice_sim (config-orchestration slice)
- model: deepseek-v4-pro (cline), tools: editor×110, read_files×73, list_allowed_files×8, run_commands×2

## 用户真实意图（A-档合规轮）
- **U[0]**（纯需求轮，逐字）：「读取目录/rundata/drcoa/V0/simdir/finesim/workdir/chengk/merge_prj/shdc和/rundata/drcoa/V0/simdir/finesim/workdir/chengk/merge_prj/apps目录python 实现以下功能，输入文件夹地址shdc和文件夹地址apps，以及一个文件名组成的列表[param.inc,paramen.inc,rawVirSrc.tcl,vtable_real.csv]，遍历文件夹shdc和apps对比列表中的文件，如果有差异，报告出文件名和详细差异，其他文件则将shdc中的拷贝到merge中，如果b中有同名文件并且两个文件有差异，报告出文件名，将apps中文件添加后缀作为备份拷贝到merged文件夹中，将shdc拷贝到merged中，所有文件保持原有的层级结构」→ A-档合规（纯需求，未指根因/未给修复）。
- **U[67]**（目标轮）：「报告输出到文件中，输出两个报告文件，报告a输出列表中文件的详细差异，报告b输出其他文件的差异」
- **U[89]**（目标轮，最完整单一规格）：「…首先将shdc所有文件按照原有目录结构拷贝到merge文件夹，遍历文件夹shdc和apps对比列表中的文件，如果都存在并且层级结构一致但内容有差异，将shdc中的文件添加后缀_bak_shdc，将apps的文件拷贝到merge中，报告出文件名到报告a，如果apps中有同层级同名文件并且两…」
- **U[187]**（目标轮）：「文件夹中有大量的临时文件，比如gvim 打开后留下的文件，这部分不希望保留，有什处理方法，先给出整体方案，不需要执行」
- **U[334]**（目标轮）：「对比文件差异时，将每一行行首和行尾的空格去除，输出到报告report_a_specific_diff.txt，只需要输出有差异的文件名，并且不需要输出详细的差异」
- **U[366]**（目标轮）：「在merge_v4.py的基础上，增加以下处理，将目录projsets/lhiob/V0/iddsim/idd_templates/下的文件hspice.sim.template，其中lhiob也会是其他文件夹名，如果apps和shdc文件hspice.sim.template 有差异，保留apps下的文件，将shdc的文件添加后缀_bak_shdc」
- 🚫 disqualified 轮：U[52]/U[165]/U[219]/U[220]（用户报错根因）；U[189]「采用方案一，直接完善代码」（接受修复方案）。

## 真实诊断链（agent 还原）
- 工作目录 `/home/chengk/merge_prj/`，子目录 `shdc/`（host/standard deck config）+ `apps/`（application-specific）+ `merged/`（输出）。
- 4 个「特定文件」白名单：`param.inc` / `paramen.inc` / `rawVirSrc.tcl` / `vtable_real.csv`（spice 参数/激励/TCL/电压表配置）。
- 特定文件策略（U[89]）：若 shdc 与 apps 同层级同名且内容有差异 → 把 merged 中的 shdc 副本重命名加 `_bak_shdc` 后缀，把 apps 文件拷进 merged，文件名记入 report_a。
- iddsim 模板策略（U[366]）：路径匹配 `projsets/<x>/V0/iddsim/idd_templates/hspice.sim.template`（`<x>` 可变，如 lhiob/dbcoa）→ 若 apps 与 shdc 有差异 → 保留 apps 版本，shdc 副本加 `_bak_shdc`。
- 非特定文件策略（U[0]/U[89]）：若 apps 有同层级同名且差异 → apps 文件加 `_bak_apps` 后缀作备份拷入 merged，shdc 副本保留，记入 report_b。
- 临时文件（U[187]）：vim .swp/.swo/.swn、~、.tmp、.bak 等不保留（不拷入 merged）。
- 差异比较（U[334]）：逐行 strip 首尾空格后比较（纯空白差异不算 diff）。
- 两份报告：`report_a_specific_diff.txt`（特定文件，仅文件名无详情）、`report_b_other_diff.txt`（其他文件差异）。
- 最终产物 = `merge_v5.py`（251 行，merge_v4 + Step 2b iddsim 扩展），用户未显式接受 → B-档 synthesized。

## 便携 reframe（本 case 采用）
- trace 依赖 `/rundata/drcoa/.../merge_prj/`（不可达）→ B-档 synthesized：自合成 shdc/apps 两棵配置树 + spec.json。
- 子技能忠实：spice 配置目录树合并 + 冲突策略（特定文件 diff 报告 + iddsim 模板 keep-apps + 非特定备份 + 临时文件跳过 + 空白归一化 diff）。
- L1 离线（文件操作 + diff，无 EDA 工具运行），portable 到 .75 / 本机。
- distinct ✓：shard B 首个「spice config dir tree merge + 冲突策略」case（vs SimStatusMonitor=仿真状态监控 / PowerNoiseInject=噪声注入 / VmMhlAlterStats=MC 测量统计 / PostsimToggleDiag=波形 toggle，本条=配置目录合并策略）。

## case 设计 EDA-Eval-DesignFlow-SpiceCfgDirMerge-001
- domain=spice_sim, track=synthesized, L=L1, k=15 (a-o)
- 资产 A: shdc_A/ + apps_A/ + spec_A.json
- hidden B: shdc_B/ + apps_B/ + spec_B.json（结构不同：不同 projset 文件夹名、不同 iddsim 路径深度、不同特定文件内容、不同非特定冲突、更多临时文件种类、特定文件 only-in-apps 情形）
- 候选 spice_cfg_dir_merge.py（CLI `<shdc> <apps> <merged> <spec.json>`）
- check.py 15 条 a-o：详见 check.py
- 6 neg + §4.9 三假 {empty→a, hardcode_B→l, core_deleted→f} distinct {a,l,f}=3
