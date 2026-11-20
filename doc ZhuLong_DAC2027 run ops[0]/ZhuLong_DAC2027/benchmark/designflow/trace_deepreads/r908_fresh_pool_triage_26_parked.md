# r908 fresh-pool triage — 26 D-pure candidates peeked + parked (2026-11-19)

**背景**：r905-r907 三轮维护轮已确认 revival-pool 枯竭；r908 plan ②「必须 fresh fetch」。
本轮从 candidates_mc10.tsv (mc≥10 D-keyword 过滤) 取 fresh 候选（不在任何 4-shard ledger），
两轮筛选：(a) D-keyword 命中 (b) netlist/schematic/waveview/analog 为 top-2 keyword。
对 ~27 候选 ssh-fetch 首条 user message 判意图，全 marginal，逐条 claim+park。

**结论**：fresh mc≥10 D-domain 池（88→65 未动过）的「干净 produce-task」子集已枯竭。
剩余 65 未动过多为低 mc(10-20) + kw-from-agent-tool-reads false-positive + 同分型 marginal。
2026-11-15 reaudit 谓 Q&A/skill-trigger/doc-search「可造」，但「可造 ≠ 可判分」——
无干净 gold deliverable 的 skill-trigger(GUI 产物)/open-ended QA(无单一 gold)/NOFILE 无法写
k≥8 有牙 check()，强造 → incomplete → 不计通过率（违硬闸门）。

**26 候选 triage 明细**（全 parked, ledger note=r908 triage: <分型>）：

| sid | user@host | mc | 首条 user 意图 | 分型 | 判定 |
|---|---|---|---|---|---|
| hp4wb | jcgu@10.129.32.236 | 24 | [group-gen-sdl] 生成 group | skill-trigger GUI-layout | not-checkable (GUI 产物) |
| p5k61 | lizwen@10.129.2.11 | 38 | aether 里连续 copy 怎么做 | keybind Q&A | 无 gold |
| 5ersu | lizwen@10.129.2.11 | 38 | aether 里 smash 快捷键是什么 | keybind Q&A | 无 gold |
| sgvz4 | ziyuny@10.129.8.236 | 24 | 你有什么 rag 知识库?/什么是 DRC? | explanation Q&A | 无 gold |
| qvdrc | e0039122@10.129.2.13 | 25 | 先了解长鑫 G5 的工艺 | process-exploration | weak |
| 2d741 | e0041123@10.129.32.46 | 42 | load(...)后出现 license/traceback 错误 | debug Q&A pasted-error | 无单一 gold |
| jdjbi | sagequan@10.129.32.190 | 33 | [simdiag-cli] vps regression 诊断 demo | skill-trigger browser-demo | GUI not-checkable |
| ptr9i | e0047722@10.129.8.125 | 33 | 生成 70k tokens 长篇剧本《芯声》 | NON-EDA creative-writing | wrong-domain |
| u2kcz | minjiex@10.129.8.222 | 29 | — | NOFILE session-rotated | 不可造 |
| iv9vy | yanxvwei@10.129.2.11 | 28 | CAD Workstation(Qt+MySQL) 首页开发 | NON-EDA app-dev | wrong-domain |
| 2rwrr | miccao@10.129.32.47 | 23 | 批量 LVL 比较两目录版图(flashlvl) | produce-task 但 C-domain physical_verify | not-D |
| uegln | katief@10.129.2.13 | 24 | 解释 PAT (pvcc pvss 6.3n 40p...) 一行 | explanation Q&A thin-1-line | k≥8 不足 |
| nwthf | kevin1d@10.129.8.104 | 23 | layout 快捷键怎么修改 | keybind Q&A | 无 gold |
| n4bp8 | e0023936@10.129.32.75 | 11 | — | NOFILE session-rotated | 不可造 |
| cd5dj | steveny@10.129.32.189 | 12 | SKILL.md 格式不对无法加载 | skill-file debug Q&A | 无 gold |
| 49kxc | yutongy@10.129.2.11 | 10 | 推荐一个 stdcell 电路(3 TECHLIB 元件 1→2 并列) | circuit-rec Q&A open-ended | 无单一 gold |
| 4oru1 | yzwang@10.129.2.10 | 19 | TECHLIB 库有哪些文件/组件? | listing Q&A | 无 gold |
| n7mei | johnl@10.129.2.10 | 18 | 为什么到 zl 老是进入链接中状态 | debug Q&A | 无 gold |
| alyc0 | hao15z@10.129.2.14 | 12 | nihao | hello-world | weak |
| u9tql | e0014566@10.129.35.82 | 12 | 返回当前 top cell 名称(用 virtuoso skill API) | thin single-call | k≥8 不足 |
| 285vt | colinxu@10.129.35.74 | 12 | 帮我写个 hello world 脚本 | hello-world (r904 亦 triage) | weak |
| u0ng5 | e0041392@10.129.2.12 | 12 | Virtuoso 如何对当前电路做 Ignore Instance? | how-to Q&A | 无 gold |
| 8uwb4 | e0041392@10.129.2.12 | 10 | /anasimpro-gui-start | skill-trigger | not-checkable |
| 8c3y9 | e0041392@10.129.2.12 | 13 | askeda 查询 Ignore Instance | doc-search Q&A | 无 gold |
| znwrq | e0029495@10.129.2.10 | 17 | /anasimpro-gui-start | skill-trigger | not-checkable |
| jlx61 | e0025730@10.129.8.86 | 17 | /sense-margin-test | skill-trigger | not-checkable |

**分型统计**：skill-trigger(not-checkable GUI)=6 · Q&A(无 gold)=11 · NON-EDA=2 · NOFILE=2 ·
hello-world=2 · produce-task-but-wrong-shard=1 (2rwrr C-domain) · thin(k≥8 不足)=2 · weak-exploration=1

**对下轮的启示**：
- fresh mc≥10 D-domain「干净 produce-task」子集枯竭得到**第二轮验证**（r907 系统性 triage + r908 fresh-fetch 26 peek）。
- 剩余 65 未动过 mc≥10 中，低 mc(10-20) 占多数，分型与本次一致（keybind/Q&A/skill-trigger/NOFILE）。
- 真正可造的 D-domain case 需 (a)用户提供文件 → agent 产结构化 report/JSON/script，或 (b)真跑沙盒工具产可验证产物。
  这类 trace 在 mc≥10 D-domain 已被 r895-r904 消耗；新料需等下次 698 机 rescan（A 线 orchestrator.sh）带来新 session。
- r908+ 建议：待 A 线换池（summary_1118_230537 tsv 落地本地）后重跑 mc-matrix，可能带入新 D-domain produce-task 候选；
  在此之前 D 线维持维护态（triage/park marginal 候选 + discuss mandatory + MEMORY 体积治理）。
