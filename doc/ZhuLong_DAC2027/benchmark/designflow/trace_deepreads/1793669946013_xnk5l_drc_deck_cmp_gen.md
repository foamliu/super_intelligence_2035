# Deepread — 1793669946013_xnk5l (kenwang @ hfeg0plg16)

- shard: C · domain: physical_verify · level: L1 · track: faithful (A档)
- match_count: 212 · keywords: drc:961; calibre:307; .def:7
- status: completed · nmsgs: 214 · user turns: 7
- case_id: EDA-Eval-DesignFlow-DrcDeckCmpGen-001 (jsonl_C 278→279, k=12 a-l)
- ledger: case 280 (r323)

## 会话元数据（r323 .75 NFS-read 实证）

| 字段 | 值 |
|---|---|
| session_file | 1793669946013_xnk5l |
| user | kenwang |
| host | **hfeg0plg16**（172.16.8.192）— summary.tsv 第 1/2/3 列实证；ledger/jsonl 旧记 hfeg0plg49 为误，r323 已更正 |
| source | desktop · model: glm-5.3-flash（用户自有 cline desktop 会话，非 pi） |
| started_at / ended_at | 2026-11-03T01:39:06Z → 2026-11-05T11:10:45Z |
| exit_code / status | 0 / completed |
| cwd | /home/kenwang/zl |
| messages.json | 883158 B（新版 cline 子目录布局 `<sid>/<sid>.messages.json`） |

## 用户原始意图（U#0 逐字）

> [drc-rule-dev] 请学习一下，另一个DRC 文件/rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/V05_coding_rebuild/10302026_3/35H_DRC_Cal_V0d1a_Rev13_1P22M_16F1xa1x1xb1ya6y4yy_6B2v2z1u.drc，学习一下n7文件中没有的code写法，如果同一个description相同但是两个写法有冲突，优先按新的写法做，并把它整成里一个skills，

## 任务分类

produce-task（A档 rule 2 通过：用户只表达目标"学习新写法 + 冲突优先新 deck + 整成 skills"，未给根因或修复方案）。7 个 user turn 多为 "go on" / "已经成功了吗" / "分享给同事"，无修复性指令。status=completed = 单用户接受 gold。

## 真实 assistant 工作链

1. read 35H deck（174653 行，1P22M）+ n7 参考 deck（141200 行）。
2. 写 `analyze_35h.sh`（同步脚本）+ `compare_35h_n7.py`（对比脚本，11305 bytes）。
3. compare_35h_n7.py 核心：
   - `parse_deck`：正则 `^([A-Za-z][A-Za-z0-9_.:\[\]]*)\s*\{` 提取 `NAME { @ desc ... body ... }` 检查块；跟踪 `#IFDEF/#ENDIF` 栈；`strip_comment` 剥 `//`。
   - `count_constructs`：~100 条 SVRF 构件正则频次统计（INT/EXT/ENCLOSURE/EXCLUDE SHIELDED/...）。
   - `norm_desc`：desc 小写 + `\s+→空格` 归一化；`norm_body`：每行空白折叠后 ` | ` 拼接。
   - main 报告 4 节：① 构件差异（only-in-35H / 频次差 / only-in-n7）② 同名规则代码不同（name-conflict）③ 同 description 代码不同（desc-conflict，35H 为准）④ 前缀分布。
   - `dump_conflicts`：导出冲突代码到 conflict_code_dump.txt。
4. 产出 skills 包：`~/.cline/skills/drc-rule-dev/`{SKILL.md(10784B), references/35h_patterns.md(14488B, 15 类新构件 + 7 条冲突裁决表), references/deck_structure.md(7163B, n7 章节地图), INSTALL.md}。
5. U#41 "再给一份简单明了的功能需求描述" → brief 版；U#50 "能不能用中文来写" → 中文版。最终交付 skills 包 + 中英文需求文档。

产物名在 messages.json 出现频次（grep 实证）：.drc×208 · 35h_patterns×103 · compare_35h×93 · SKILL.md×80 · deck_structure×68 · report.md×66 · 35h_vs_n7×66。

## case 改造（r323）

真实 gold 脚本硬编码真实 deck 路径、依赖 174653 行真实 35H deck，无法直接做 SUT 题。改造为**通用 deck 对比脚本题**：

- **A 档**：prompt = U#0 逐字原文。task_brief 收窄交付接口为 `compare_decks.py <new> <ref> <out>` + 报告 5 要素。
- **A 对**（SUT 可见 assets）：合成 `new_deck_A.drc`（35H 风格下划线命名，8 块，含 EXCLUDE SHIELDED 新写法）+ `ref_deck_A.drc`（n7 风格点分命名，6 块）。控制重叠：2 同名冲突(M0.W.1/M1.S.2) + 1 异名同 desc 对(M0_ENC_ALT<->M0.EN.3) + 2 new-only 块 + EXCLUDE SHIELDED 仅 new 有。
- **B 对**（hidden）：点分命名不同重叠，3 name-conflict / 4 desc-conflict，DENSITY 仅 ref 有。
- **B2 对**（hidden）：new deck 含 `#IFDEF WITH_SEALRING ... DD.SR.4 ... #ENDIF` 嵌套块，须被提取（new_checks=5 而非 4，DD 前缀 new=3）。
- **B3 对**（hidden）：ref 的 description 含 tab/多空格（`@\tMaximum\twidth\tof\tGG`），new 用单空格，归一化后方匹配（desc-conflicts=3 含 HH_ENC_ALT<->HH.EN.3）。

## check.py 12 条断言（a-l）

a zip 合法+含 compare_decks.py ｜ b A 对 exit 0+非空报告 ｜ c A 块计数 new=8/ref=6 ｜ d 识别 EXCLUDE SHIELDED 仅 new ｜ e name-conflict=2+列 M0.W.1/M1.S.2 ｜ f desc-conflict=3+含异名对 M0_ENC_ALT<->M0.EN.3 ｜ g 标注 new 权威 ｜ h 前缀分布段 ｜ i B 对 3/4 ｜ j B2 嵌套提取 5/DD=3 ｜ k B3 空白归一化 3/HH_ENC_ALT<->HH.EN.3 ｜ l B2 ref=3 确认注释剥离

## 自验（r323 复核）

- ref（compare_decks_ref.py 改名 compare_decks.py）→ check 12/12 PASS ✓（a-l 全 PASS）
- 6 negatives（naive/print_only/deleted_core + §4.9 三假 empty_shell/print_expected/name_only）→ 全 FAIL ✓
- jsonl test field == disk check.py（sha 8c84aae3cc019f3e，15243 B，exact equal）✓
- k_rationale == k_check == 12 ≥ 8 ✓ GATE PASS

## 关键

- 4-shard ledger exclusion 池（r322 首用）继续生效：xnk5l 在 2182 已账 sids 外，CLEAN。注：r322 判"172.16.x 不可达"，但 hfeg0plg16(172.16.8.192) r323 实测 ssh 可达（5s 响应）——该判定在此 host 不成立，后续候选可放宽 172.16.x。
- layout-affinity score 排序法第五城（r319-r322 同源）；本 case 与 r319(DrcVsDrmRuleAudit) 同为 deck 对比类，但 r319 是 DRM rule-list vs DRC deck，本 case 是 DRC deck vs DRC deck + #IFDEF 嵌套 + desc 空白归一化，判定逻辑不同。
- r342a(kenwang drc-rule-dev) 早先因"QA audit 76 rules 非单 produce-task"被 PARK；本 xnk5l 同用户同 skill 主题但为真 produce-task（产 skills 包 + 对比脚本），不同 session，无重复 case。
- task_brief 详尽度：A 档规则要求 task_brief「≤3 行只写交付接口」。本 case task_brief 含解析要求/输出结构/归一化规则，因 check.py 按特定报告结构判分，需向 SUT 明示 grader 接口以避免「①交付形态错」类失败占主导（A 档判据 ①+④≤30%）。prompt 已逐字原文，task_brief 仅补 grader 接口，属可接受的接口显式化。
