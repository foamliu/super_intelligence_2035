# Deepread — 1792204811067_m61nd (xinqiaoz @ hfeg0pkn004, mc=314)

trace: `/home/xinqiaoz/.cline/data/sessions/1792204811067_m61nd/1792204811067_m61nd.messages.json`
151 msgs / 771 KB / 7 user turns. keywords: 746 calibre + netlist/schematic (PDK_QA dummy deck QA).

## 真实意图（USER 逐字）

- **USER#0 (A-档 seed, 提出目标, 未给根因/修复)**：「我会给你数据，让你来完整的执行一个 qa 的全部流程。1. 把每一个检查项遇到的问题/经验/步骤/踩坑记录到一个文档；2. 当前仓库 DUMMY 目录我在做 dummy 的部分 qa 的 python 脚本，本次不要使用这个脚本，但你要记录每一个 qa 项是否可以扩展到我的脚本里。先创建一份空白的 dummy qa 目录。」
- USER#1: 数据在 `/home/pdk/peiyaoz/00_Dummy/deck/DYT4E_WHCFP_LHCRP_DHCFP/`（只读），复制到工作区，脱敏（删除已有中间文件，后续 qa 过程自己产生）。
- USER#2: 指出漏删 3 文件（skipper_server, QA_chip/frame.gds, calibreDummy_chip/frame.rule）= 给根因/修复 → hint, 不进 A-档 prompt。
- USER#3: 正式开始 QA-T-01 GDS_TYPE 确认。
- USER#4: 改为只 review rev02，删 rev01；开始 QA-T-02 suffix 版本确认。
- USER#5: 改回保留 rev01、删 rev02；从源目录恢复 rev01；新开会话重做 → 让助手写一个 prompt 给新会话；清空已有记录。
- USER#6: QA_LOG 只要空白文件，不要模板，让下个 AI 自己探索。

## assistant 工具链
read_files(rules/index, DUMMY/index, dummy_qa_process, task-preflight, doc-and-index-sync) + list_allowed_files(DUMMY, 源 deck depth 4) + editor(创建 qa_workspace/README+QA_LOG+SCRIPTING_FEASIBILITY+scripts/index 4 文件, 同步 DUMMY/index.md) + run_approved_command(profile shell_generic_pdkqa: cp -r 源→副本, rm -rf 中间产物, find 验证) + search_codebase(验证 26 模板). 共 ~20 次 editor + ~8 次 run_approved_command + 多次 list_allowed_files 验证.

## 关键发现（gold 事实）

1. **脱敏口径（用户/助手共同确立）**：「能重新产生 = 可删」。
2. **保留 (keep) = 源输入，每 rev 目录 6 个文件**：
   - `calibreDummy.rule` (TVF 配置, 源)
   - `chipGen` (chip 侧) / `frameGen` (frame 侧) — 展开工具
   - `config.ini` (测试 GDS 生成配置)
   - `releasenotes.dummy` (版本历史)
   - `CheckLayerDuplicates.py` (参考脚本, 留档)
   - `DummyPatternGenerator_v5.py` (参考脚本, 留档)
3. **删除 (delete) = 中间产物**：
   - vim 交换文件 `.sw[k-p]` / `.swp` / `.swo`
   - 查看器缓存 `.skipper/` / `skipper_server/` (含空目录树)
   - QA 运行输出 `QA/` / `QA_new/` / `QA_xinqiaoz/` (dummy GDS / 分 mask GDS / calibre.db / drc.results)
   - DRC overlay 输出 `DRC/` (den_* 密度文件 / overlay.calibre.db / 运行临时副本)
   - 测试 GDS `QA_chip.gds` (由 DummyPatternGenerator_v5.py 重新生成)
   - 展开 SVRF `calibreDummy_chip.rule` / `calibreDummy_chip.rule0` / `calibreDummy_frame.rule` / `calibreDummy_frame.rule0` (由 chipGen/frameGen 从 calibreDummy.rule 重新展开)
4. **rev 选择**：最终保留 rev01，删除 rev02（USER#5 改回）。源目录 `/home/pdk/peiyaoz/...` 全程只读未动（多次验证 .swp/.skipper 原样保留）。
5. **最终工作区状态**：`data/DYT4E_WHCFP_LHCRP_DHCFP/{chip,frame}/v0d5_rev01/` 各 6 文件共 12；QA_LOG.md = 4 行极简空白（标题 + "记录结构由执行 AI 自行探索组织" + 指向 README）；SCRIPTING_FEASIBILITY.md 极简空白；README.md 重写只留事实与硬要求；scripts/index.md 空表。
6. **handoff prompt**：助手写出新会话 prompt（含 deck 名/rev/6 文件清单/源目录只读/脱敏口径/工作方式/继承的判定规则）。
7. **踩坑**：`find -type f` 验证会漏掉空目录树（skipper_server 残留根因）；按"像不像输入"判断删留是错的，正确口径是"能重新产生 = 可删"。

## gold 依赖
live PDK_QA 代码库 `/home/xinqiaoz/PDK_QA` + live 源 deck `/home/pdk/peiyaoz/00_Dummy/deck/DYT4E_WHCFP_LHCRP_DHCFP/` (内网) → .75 沙盒不可达 → **A-档 disqualified (tooling/data)** → **B-档 synthesized L1-boundary**：把 deck 文件树固化为 `deck_manifest.json`，候选写 `dummy_qa_data_prep.py` (标准库, 确定性) 读 manifest → 按"能重新产生 = 可删"+ name pattern 分类 keep/delete → 产 `cleaned_workspace.json` (kept/deleted/per-rev-count/source-untouched/summary) + `QA_LOG.md` (空白极简) + `handoff_prompt.md`。

## 候选筛选记录
候选池 (mc≥30, shard C strict filter, excl ledger 193): top = m61nd(xinqiaoz,746 calibre,mc314)/ vdqlw(ypzheng,skill-spec,skip)/ 17cgk(xinqiaoz,handoff-resume,overlap)/ qv6pl(adaml,fsdb-sim,skip)。选 m61nd：physical_verify 域, 746 calibre 强信号, USER#0 干净 A-档 seed, 多轮交互有清晰最终接受态。与现有 PDKQA-001(env setup)/DummyQA-001 正交——本案是 **deck 数据准备 + 脱敏分类 + 空白交接**（不是 env 检查也不是单点 QA）。

## 16 条断言 spec (k=16, 对应 check.py a-p)
- a: zip 4 文件 + .py py_compile
- b: 候选跑 B exit0 + 3 产物 (cleaned_workspace.json + QA_LOG.md + handoff_prompt.md) + stdout==cleaned_workspace.json
- c: cleaned_workspace.json 顶层键齐 (deck_name/target_rev/kept/deleted/per_rev_kept_count/source_dir_untouched/summary) + summary total==len(entries_B)
- d: source_dir_untouched==True (源只读)
- e: vim swap (.swp/.swk/.swo/.swn) → delete
- f: viewer cache (.skipper/skipper_server) → delete (含空目录)
- g: QA 运行输出 (QA/QA_new/QA_xinqiaoz/DRC/lvs_run/drc_run/LVS_DB) → delete
- h: 测试 GDS (QA_*.gds) → delete
- i: 展开 SVRF (calibreDummy_(chip|frame).rule*) → delete
- j: 源输入 keep (calibreDummy.rule/chipGen/frameGen/config.ini/releasenotes.dummy/CheckLayerDuplicates.py/DummyPatternGenerator_v5.py)
- k: 非 target_rev 整 rev 目录 → delete
- l: per_rev_kept_count 对 target rev == 6 (B) + 独立重计数对账
- m: QA_LOG.md 空白极简 (≤6 行 + 含 "QA_LOG" + 无 "PASS"/"FAIL"/"QA-T-01" 结论)
- n: handoff_prompt.md 含关键事实 (deck 名 + target rev + "能重新产生 = 可删"/"脱敏" + 源只读 + kept 文件清单)
- o: cross-input guard B2 (单 rev chip-only, 7 源文件含 layer_map.map): exit0 + kept==7 (额外 layer_map.map keep) + 无 frame → 击穿 hardcoded-6/hardcoded-12
- p: cross-input guard B3 (rev05 chip+frame, 5 源文件无 CheckLayerDuplicates.py): exit0 + kept per rev==5 → 击穿 hardcoded-6

## 自验计划
ref dummy_qa_data_prep.py 跑 A/B/B2/B3 → cleaned_workspace.json; check.py 跑 B/B2/B3 + 3 §4.9 假提交 + 2 naive; negative_selftest NEG_RC=0 全 FAIL.
