# Deepread — sid 1790042012585_5e6p2 (xinqiaoz / hfeg0plg76, mc=359)
**Case**: EDA-Eval-DesignFlow-DRCDeckSyncPlan-001 · domain=physical_verify · track=B-档 synthesized · difficulty=L1-boundary
**Session**: 281 msgs / 1.36MB / 2026-09-22..24 · model=deepseek-v4-flash (cxmt-deepseek-flash) · agent=lead · status=failed (external process exit) · forked from 1793102773959_okq91

## 真实任务（一句话）
PDK QA DRC deck (Python) 的 local (`/home/xinqiaoz/PDK_QA/pdkQaSystem`, master) ↔ stable (`/apps/imctf/develop/PDK_QA/pdkQaSystem`, hbpeng sos workspace) 同步规划：从头 diff `common/` + `DRC/` 两目录，把本地待同步修改按功能拆成多个独立、风险可控的提交分步同步给 hbpeng，并设计长期 local↔stable 标准同步流程机制。

## 用户意图轮（A-档 seed 候选）
- **USER#1** (ts=1789973244505): 读 sync_to_stable/README.md 了解背景（文件已过时）→ 背景了解，非任务
- **USER#2** (ts=1789973522901) **★ A-档 seed**: 「我们需要重新 diff 本地版本的 common，DRC 两个目录和 stable 版本的 common，DRC 两个目录的差异：1.发现 stable 版本已经被他人修改，但是本地没有更新的地方 2.发现本地已修改但没同步到 stable 的 fix or feature 3.sync_to_stable 的文件只可以做参考，不能作为比对来源」= 提出目标，未给根因/修复 ✓ 合规
- **USER#3** (ts=1789974434796): 「分步提交，拆成几个具体的功能提交」= 提出目标
- USER#4: 「按功能说，这一系列的修改包含了哪些功能？」
- USER#5: 「3,7 这两个修改是否不需要再同步了」→ 用户给出方向性判断（接近根因）→ hint
- USER#6: 「重新设计同步方案」
- USER#7-8: 「天线过滤收尾是什么意思？」(澄清)
- USER#9-11: 给出合并/排序建议（用户给修复方向）→ hint
- USER#12: 「使用快照而不是 patch」+ 粘贴上次给 hbpeng 的真实 handoff 文本（含 3 个真实 feature 示例：DrcPatternCheck fnmatch / DrcValueCheck lockedDrc / DrcQaReport statusDetail）
- USER#13: 提出两个流程问题（队列插队 / review 打回破坏快照）→ 给方向
- USER#14 (ts=1790037901467): 「规划一整套 local↔stable 同步流程机制，写方案文档到 .tmp」+ 「sync_to_stable 目录清空，作为以后主战场」
- USER#15-17: 细化机制 + git commit 规范
- USER#18: 「use handoff skill to write handover document」

## assistant 工具链（关键）
list_allowed_files / approved command profiles (SHELL_CMD_AGENT.txt) / python diff 脚本 / git log / git show / grep stable 文件 → 产出 .tmp/diff_analysis_report.md + diff_stable_local_output.txt (2266 行)。

## Gold 结构（真实产物，人工复核）
### G1. 差异分类（ASST#20）— 68 .py + 10 non-py 全量对比
- 60 .py identical, 10 non-py identical, **8 .py 有差异**：
  - **stable_only** (1): `common/PdkQaMain.py` (+2/-3, hbpeng 加 `self.onlyOneCheckItem = None`)
  - **local_only** (6): `DRC/DrcQa.py` (+6/-1 thkUnit), `DRC/pattern/DrcPatternCheck.py` (+575/-234 **未提交** Good/Bad cell), `DRC/text/AntMetalThkCheck.py` (+182/-107 thkUnit), `DRC/text/DrcValueCheck.py` (+328/-30 9 commits), `common/deckInfo/DrcInfo.py` (+3/-1 defineLine 去重), `common/designManual/EdrInfo.py` (+18/-13 thk_spec +/-)
  - **bidirectional** (1): `common/designManual/LdrInfo.py` (+9/-23, stable: DDR non_dram_value + jsonRow + ruleType; local: 空 childId 过滤；互不冲突可合并)
### G2. 功能清单（ASST#24/#28）— 9 功能，核对 stable 后 7 需同步
- F1 antMetalThk thkUnit 配置化 (DrcQa.py + AntMetalThkCheck.py + EdrInfo.py) — 需同步
- F2 _THK 后缀变量匹配改进 (AntMetalThkCheck.py) — 需同步
- F3 DrcValueCheck lockedDrc 锁机制 — **不需同步**(被 F7a 取代)
- F4 衍生层间接变量豁免 (DrcValueCheck.py + DrcInfo.py) — 需同步
- F5 天线规则 ldrRow.location 过滤 — **不需同步**(stable 已有)
- F6 per-rule waive [DRC_VALUE_WAIVE] (DrcValueCheck.py) — 需同步
- F7a drcOwnerMap 重构 — **不需同步**(stable 已有)
- F7b 多值变量命名标准 (DrcValueCheck.py, depends_on F7a) — 需同步
- F8 LdrInfo 空 childId 过滤 (LdrInfo.py, **bidirectional**) — 需同步(人工合并)
- F9 DrcPatternCheck Good/Bad cell 分离 (575 行 **未提交**) — 需同步(先 commit)
- 需同步: F1,F2,F4,F6,F7b,F8,F9 = 7；不需: F3,F5,F7a = 3
### G3. 分步同步方案（ASST#23）— 8 步→6 提交
- 前提: 先 commit F9 (575 行未提交)
- Step1 DrcInfo defineLine 去重 (F4 一部分, low)
- Step2 EdrInfo thk_spec +/- (F1 一部分, low)
- Step3 antMetalThk thkUnit 配置化 (F1+F2, 3 文件强耦合, medium, **需 config.ini thkUnit=A**)
- Step4 DrcValueCheck 核心匹配修复 (用中间快照, medium)
- ... 按「小且安全→大且风险高」排序

## 为什么 A-disqualified → B-档
gold (G1/G2/G3) 依赖 live PDK QA 树真实文件内容（`/home/xinqiaoz/PDK_QA/pdkQaSystem` + `/apps/imctf/develop/PDK_QA/pdkQaSystem`，hfeg0plg76 内网，xinqiaoz 权限）→ `.75` 判分沙盒不可达 → A-档无法在沙盒复现 → B-档 synthesized L1-boundary：把 G1 diff 证据固化为 `deck_state_manifest.json`、G2 功能清单固化为 `feature_catalog.json`，候选纯标准库读 manifest 产 `sync_plan.json`，判分在隐藏 B/B2/B3 上独立重派对账。

## B-档合成要点（与 trace 主题一致，结构可判）
- **文件分类**: 按 stable_extras/local_extras 非空 → identical/stable_only/local_only/bidirectional
- **feature 取代链覆盖（核心区分点，fixpoint）**: sync_needed=false iff stable_already_has OR 任一 superseded_by 后继 will_be_present(后继 stable_already_has OR 后继 sync_needed)。两级链: F3→F7a(在 stable)、F4→F5(将被同步)。
- **文件耦合分批**: 共享文件→同批(连通分量)
- **依赖拓扑排序**: depends_on + (risk, id) tiebreak
- **uncommitted precondition**: 未提交 feature → B0 commit_first
- **bidirectional manual_merge**: 含双向 feature 的批 → manual_merge=True
- **verdict**: PLAN_READY / PRECONDITION_ONLY / NO_SYNC

## check.py 14 条断言 (a)-(n)
①[a]zip+compile+logic ②[b]B exit0+JSON+5键 ③[c]B file_classification+counts ④[d]B feature_status+两级取代链(F2→F3,F4→F5) ⑤[e]B batches count+feature_ids(文件耦合) ⑥[f]B depends_on+F12→F7→F5/6 链 ⑦[g]B manual_merge(F9/F10) ⑧[h]B config_note(F5) ⑨[i]B2 NO_SYNC(击穿 always-plan) ⑩[j]B3 PLAN_READY 全需同步(击穿 always-skip) ⑪[k]A↔B 结构差异 guard(击穿 fake_print_expected) ⑫[l]3×md5 确定性 ⑬[m]F8 precondition B0(击穿忽略 uncommitted) ⑭[n]三输入 verdict 自洽

## 自验
- ref PASS 14/14 ✓ (check.py self-test on reference_submit.zip)
- 5 neg (fake_empty→a / fake_print_expected→c / fake_core_deleted→e / naive_no_supersede→d / naive_ignore_dependency→e) 全 FAIL NEG_RC=0，4 distinct labels ✓
- §4.9 (a)(b)(c) 全 FAIL ✓
- test==disk roundtrip 29545B ✓
- jsonl_C 78→79，physical_verify 28→29

## 候选筛选记录
- shard C next ( stricter tool regex `calibre|lvs|drc|pexivirtuoso|layout|ipcustom`, mc≥50 ) → top: 1790042012585_5e6p2 (xinqiaoz, mc=359, calibre 47 + schematic 1) = physical_verify ✓
- 次选: 1793005343621_45gjq (xinqiaoz, mc=354, calibre 13) / 1792570431387_vdqlw (ypzheng, mc=335, schematic/netlist heavy — schematic 域，非 shard C)
- 顶部 mc≥100 候选 (1793147699495_as67p easont mc=786 pyAether/netlist/schematic) 实为 FSDB waveform 读取→simulation 域（shard B），已跳过
