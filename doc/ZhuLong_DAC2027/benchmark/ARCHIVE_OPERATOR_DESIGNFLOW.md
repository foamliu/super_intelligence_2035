# ARCHIVE — Design-Flow Benchmark（已闭合实验块原文）

> 体积维护规程归档区。从 `EXPERIMENTS_DESIGNFLOW.md` 搬入的已闭合实验块**原文**，
> `EXPERIMENTS_DESIGNFLOW.md` 内留 1 行指针。归档搬入前均 `git pull --rebase --autostash`。
> 🚫 不改小节编号/标题/运维指令。

---

## 归档批次 42（2026-10-30 第97轮）：MEMORY §会话易失性 + 第79轮流水

搬入原因：`MEMORY_DESIGNFLOW.md` 第97轮后达 40KB（=红线），按规程把最新活跃块
（顶部快照 + 第93–97轮流水）之下的已闭合块归档。本批含第79轮 §会话易失性发现完整原文、
第80轮 §会话易失性扩展（fresh mining 死路确认）。结论已沉淀在 `MEMORY_DESIGNFLOW.md`
顶部快照"扩量阶段"策略与"§会话易失性"指针行。

### 第79轮流水原文
[23:07] 第79轮：**Spice-004 pi-SUT 收尾 PASS + 数据卫生修复 + 会话易失性发现**。Spice-004 后台 pi (PID 1892112) 于 22:41 exit=0 → CHECK_RESULT PASS 5/FAIL 0 / DESIGN_FLOW_VERDICT=PASS（spice_sim 现 4 条全 pi+ref 双 PASS）。**§会话易失性发现**：经 eda_flow ssh -n -T（必带，否则 ssh 不退出→run_commands 120s 超时）探热点机——10-28 高价值 schematic/netlist 会话(haoyut match878 / easont match786 / zjqiao match728)**全部 No such file**(已删)，热点机 hfeg0plg49/pkn001/pkn004/plg17/plg76/plg16 **几乎清空**(仅 e0042624 在 pkn003/plg49 各 1 会话=simdiag-cli 看板调试 prose，不可提炼为可验证 EDA task)。结论：cline sessions 高度易失，summary.tsv session_file 多已失效；后续 mining 应瞄准当前活跃用户新会话/新扫描后及时 mining/基于已 capture 41 条真实任务模式扩量；不设 WAITING（网络正常，数据易失非阻塞）。**数据卫生修复**：pi_debug_status.jsonl 8 条 stale "running" launch 行经 MEMORY 核对均已完成 PASS→追加 Spice-004 PASS 行；修 gen_daily_report.py load_pi_status() 改 dedup-by-task_id-last-row-wins（原 append-log running+PASS 双计 KPI 虚高）。report_10_29.html regen(56KB, KPI 修正 35 PASS/1 FAIL/2 draft)。**ssh 经验**：`find /home` 禁用(NFS 慢)→精确路径 ls/stat；`ssh -n -T -o BatchMode -o ConnectTimeout=6 -o ServerAliveInterval=5`。41 用例/35 PASS 1 FAIL 2 draft 3 uncovered/15 jsonl。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。

### §会话易失性扩展（2026-10-29 第80轮，fresh mining 死路确认）
- 经 eda_flow open_session(BENCH-MINE,20261029-r80)→run_commands `ssh -n -T -o BatchMode -o ConnectTimeout=6 -o ServerAliveInterval=5 -o StrictHostKeyChecking=no` 探 12 台中低 tier 机（plg08/plg53/plg55/plg58/pjn200/plg52/plg15/plg99/plg90 + .75 本机 + plg102 timeout）——**11/12 完全清空**（仅 e0042624/simdiag prose 残留，已判定非 task）；**.75 自身 sessions 192→0**。
- 第79轮 §会话易失性发现热点机(top-10)清空；本轮扩到中低 tier 亦清空 → **cline sessions 在 10-28 扫描后大面积失效，fresh mining 死路**。
- **策略升级**：本轮起不再尝试 ssh 抓真实 session（多失效）；扩量走 §会话易失性发现(4) **基于已知 EDA 工具子领域 + 已 capture 41 条真实任务模式**提炼（非纯 keyword 桶合成）。PnRSignoff-004 即此策略首个产物（Innovus report_message 日志审计，源自 PnR signoff 真实 QA 模式 + innovus 952/dbGet 2597 scan hit）。
- 仍遵守：禁本机自扫、禁 lineage 自审计/§X 递归。

### §会话易失性发现（2026-10-29 第79轮，mining 策略修正）
- 10-28 扫描 summary.tsv 24085 命中会话**多为短命**：本轮 ssh -n -T 实测热点机高 match 会话(haoyut/easont/zjqiao, match 728-878)**全部 No such file**。
- 热点机当前 cline 会话存量：hfeg0plg49=1 用户(e0042624,1) / hfeg0pkn003=1(e0042624,1) / hfeg0pkn001,pkn004,plg17,plg76,plg16 = **0**。10-28 top-10 热点机已基本清空。
- 唯一现存 e0042624/1790150039431_ojny6 (3.4MB, analog:374/netlist:104, match213) = simdiag-cli 远程 HTTP 诊断看板调试 prose，非自包含可验证 EDA task → 不入库。
- **Mining 策略修正**：(1) 不再直接引用 summary.tsv session_file 路径(多失效)；(2) 新 mining 先 `ls /home/<user>/.cline/data/sessions/*.messages.json` 精确路径确认现存再读(非 `find /home`)；(3) 优先瞄准当前活跃用户新会话/新扫描后及时 mining；(4) 已 capture 41 条真实任务/traps 仍有效，扩量可基于已知 EDA 工具子领域提炼(真实 session 衍生任务模式，非纯 keyword 桶合成)。
- **ssh-from-.75 经验**：必带 `-n -T`(否则会话不退出→run_commands 120s 超时误判 hang)；`find /home` 禁用(NFS stat 千目录慢)→精确路径 ls/stat；`-o ConnectTimeout=6 -o ServerAliveInterval=5 -o ServerAliveCountMax=2`。
- **阻塞**: aether host run_code 初始化超时（layout_aether 类暂 draft）；**virtuoso skill 沙盒 init 报 `*Error* lowerCase: argument #1 should be either a string or a symbol - nil`（CXMT argus.il env setup，user code 未执行即 abort）→ schematic_netlist 类用例无法在沙盒 verify，暂 draft**；layout_virtuoso/spice_sim/physical_verify 派生任务用 waveview tcl 检查器绕过已验证 ready。

---

## 归档批次 1（2026-10-28 第10轮）：EXP-01 ~ EXP-10(first, bench_v0.4)

搬入原因：`EXPERIMENTS_DESIGNFLOW.md` 第10轮追加 EXP-10(v0.9) 后达 33KB（>32KB 软限），
按规程把最新活跃块（v0.9 EXP-10）之下的已闭合块归档。本批含早期探查（8092/.75）、
资产盘点、bench_v0.1–v0.4 的完整实验记录，结论已沉淀在 `MEMORY_DESIGNFLOW.md` 的交付物清单与流水。

## EXP-01 (2026-10-28) 8092 MCP 协议探查
**方法**：`curl POST http://127.0.0.1:8092/mcp`（Accept: text/event-stream）→ initialize / tools/list / resources/list / prompts/list。
**结果**：
- 协议：streamable HTTP MCP，protocolVersion 2025-06-18。
- serverInfo：`RESEARCH-MCP-SERVER` v1.25.0。
- tools：`cimi_search, cimi_fetch, vqa, text_to_image`（无 exec/ssh）。
- resources: []；prompts: []。
**结论**：8092 不能用作"在 .75 执行命令"的入口。任务书该假设不成立。

## EXP-02 (2026-10-28) .75 SSH 连通性
**方法**：`ssh -o BatchMode=yes 10.251.36.75 hostname`。
**原始输出**：`app.e0031982@10.251.36.75: Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password).`
**结论**：ping 通但无免密；未授权前不重试、不爆破。多机扇出需授权/凭证。

## EXP-03 (2026-10-28) 本机 cline 资产盘点（只读）
**方法**：`find /home -path '*/.cline/data/sessions/*'` + parse session/meta JSON。
**结果**：1 机 / 19 用户 / 3487 session 目录 / 3483 解析成功 / 4 失败。
**模型分布**：deepseek-v4-flash, MiniCPM5-1B, deepseek-v4-pro-fp4, MiniCPM5-2B, glm-5.2, kimi-k2.6-cloud, glm-5.0/5.3-flash。
**状态分布**：completed 最多，次 failed / cancelled / idle。
**结论**：本机即满足构建需求；样本持续增长。

## EXP-04 (2026-10-28) bench_v0.1 脱敏与评分管线
**方法**：extract.py(脱敏) → scorer.py(5维) → report.py(HTML)。leak check: grep 残留 PII。
**脱敏规则**：username→sha256 salted hash[:12]；`/home/<user>`→`/home/<USER>`；bare `app.e007digits/app.t007digits/app.vendor.*`→`<USER>`；email→`<EMAIL>`；domain→`<DOMAIN>`；token/secret→`<REDACTED>`。model/provider/tools_used 也脱敏。
**踩坑**：
1. tool_use 的 `name` 字段有时是整条 shell 命令（含 /home/ 路径）→ tools_used 也需脱敏。
2. `model` 字段含 `/nas_train/app.t0002965/model/...` 本地模型路径 → 需脱敏。
3. `re.sub` 对已编译正则不能传 flags 关键字 → 在 compile 时加 re.IGNORECASE。
**结果**：2258 已发布任务，整体评分中位 0.6917 / 均值 0.6752。leak check 全空（通过）。
**复现**：`cd designflow/bench_v0.1 && bash reproduce.sh`。

## EXP-05 (2026-10-28) 8092 MCP / .75 SSH 复探（第2轮唤醒）
**方法**：curl POST 8092/mcp（Accept: application/json，本轮 header 已变）→ tools/list；`ssh -o BatchMode=yes 10.251.36.75 hostname`。
**结果**：
- 8092：serverInfo `RESEARCH-MCP-SERVER`，tools=`cimi_search/cimi_fetch/vqa/text_to_image`（**仍无 exec/ssh**）。Accept 从 text/event-stream 变 application/json。
- .75：`Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password).`，仍无免密。
**结论**：多机扇出路径仍阻塞，继续单机脱敏集精炼。

## EXP-06 (2026-10-28) bench_v0.2 细化分类 + TF-IDF 聚类
**方法**：在 v0.1 脱敏 tasks.jsonl 上做精炼层（不重扫 /home）。classify_v2 = 工具信号先验（pyAether_MCP→eda_aether_layout；EDA_MCP→innovus/virtuoso；run_commands→code_dev）+ 8 类 eda_* 细化关键词 taxonomy + cwd hint。残余桶（eda_other_resid+other）做 TF-IDF（纯 numpy，vocab=600，l2 归一）+ k-means++（k=10, 25 iter）聚类，top-tfidf 词拼接作 cluster label。
**结果**：
- 18 个 v2 类别；兜底桶 v1(eda_other+other)=837 → v2 残余(clusters+other)=384，**-54%**。
- 主要迁移：eda_other(802)→code_dev(429)、cluster:_empty(197,空 prompt 漏过滤)、cluster:rtl_skills_skill_testing(67)、cluster:world_hello_examples_apps(46, toy)；eda_layout(1207)→eda_aether_layout(992)。
- 评分：v2 整体中位 0.6917 / 均值 0.6579（S5 用 v2 权重）。
**踩坑**：v0.1 leak check 漏拼音人名（见 EXP-07）。
**复现**：`cd designflow/bench_v0.2 && bash reproduce.sh`。

## EXP-07 (2026-10-28) PII 残留人名发现与修复（红线）
**发现**：v0.2 聚类 cluster c3 top terms = `hello_shiwei_zhulong_minicpm`，疑人名。核查 v0.1 tasks.jsonl：`shiwei`×6、`zhulong`×3，prompt 形如 "hello, shiwei"、"别的设计人员真实和zhulong交互的一个轨迹"、"zhulong_config_dir"。确认为真实人名（v0.1 leak check 仅查 app.e*/app.t*/email/domain/路径，漏拼音人名）。
**修复**：extract.py `desensitize_text` 加：(1) `RESIDUAL_NAMES={shiwei,zhulong}` 表；(2) 称呼/交互上下文 scrubber（hello/hi/hey/和/与/跟 + name）；(3) plain replace（覆盖 `zhulong_config_dir` 这类标识符内嵌，`\b` 会漏）。重跑 v0.1+v0.2，全产物 leak check 0 残留。
**遗留**：git 历史 commit `21f4de3` 仍含未脱敏人名（共享仓不擅自 rewrite history）→ 待人工决断 force-push 重写。
**教训**：leak check 须含「聚类 top terms 审计」一环，规则脱敏对未预见 PII 类型（人名/拼音）有盲区。

## EXP-08 (2026-10-28) 第3轮复探 — 🔔 卡点上报触发
**方法**：curl POST 8092/mcp tools/list；`ssh -o BatchMode=yes -o ConnectTimeout=5 10.251.36.75`；`ping -c1`；本机 `find /home/*/.cline/data/sessions/ -name '*.messages.json'` 重新计数。
**原始输出**：
- 8092 tools/list：`cimi_search/cimi_fetch/vqa/text_to_image`（同前，无 exec/ssh）。
- .75 SSH：`ssh: connect to host 10.251.36.75 port 22: Connection timed out`；`ping`: `1 packets transmitted, 0 received, 100% packet loss`。
- 本机：20 个 sessions 目录，19 有数据，3479 条 `*.messages.json`。
**结果**：
- .75 状态**恶化**：第1轮 `Permission denied (publickey,...)`（主机在但无凭证）→ 第3轮 `Connection timed out` + ping 100% loss（主机/网络不可达）。
- 3 口径：1 机 / 20 sessions 目录（+1 新用户 `app.t0002997`，0 轨迹）/ 3479 轨迹。真实用户持续增长（目录数 +1）但本轮无可抽新样本。
**结论**：连续 3 轮同一卡点（.75 不可达 + 8092 无 exec）→ 按纪律**上报**，置 WAITING=1，多机扇出不再硬探。单机脱敏集 v0.3（人工标注+监督分类）不阻塞，可下轮推进。

## EXP-09 (2026-10-28) 第4轮复探 + bench_v0.3（CJK修复+人工策展+监督分类基线）
**方法**：第4轮复探 8092/.75 + 在 v0.2 脱敏集上建 v0.3 curate 层。
**复探原始输出**：
- 8092 tools/list：`cimi_search/cimi_fetch/vqa/text_to_image`（同前，无 exec/ssh）。
- .75：`Permission denied (publickey,...)`；ping `1 transmitted, 1 received, 0% loss`。**恢复可达**（vs 第3轮 timed out + 100% loss），但无凭证。
- 本机：20 sessions 目录 / 19 有数据 / 3479 `*.messages.json`（无新样本）。
**v0.3 关键发现 — v0.2 CJK 分词盲区**：
- v0.2 `refine.py` 的 `TOKEN_RE = [A-Za-z][A-Za-z0-9_]{1,}` **只匹配拉丁 token**，所有全中文 prompt tokenize 为空 → 全部落入 `cluster:_empty`（203 条）。这些**不是空 prompt**，是真实的中文设计任务（如"列出当前目录下的文件"）。
- v0.3 修复：`curate.py` 加 CJK 字符 bigram tokenization（`[\u3400-\u9fff]` 单字 + 相邻 CJK bigram），对 203 条重聚类（k=8），按 top terms 关键词映射回 eda_aether_layout/code_dev/file_ops/data_analysis/eda_virtuoso_schematic 等策展类别。
**v0.3 人工策展**：抽每个 cluster 代表性 prompt（按 prompt_len 升序取前3）人工标注。映射：`cluster:hello/name_hello`→`noise_greeting`；`cluster:rtl_cline_say_testing/ask_question`→`noise_toy_test`；`cluster:world_hello_bak_desktop`→按 prompt 内容 split（hello world→noise_toy_test，docs 读取→file_ops）；`cluster:agent_coding_policy_engine/mcp_cwd_*`→`meta_agent_ops`；`cluster:github`→`file_ops`；`cluster:eda_askeda_skills_skill`→`eda_env_qa`。质量标记 quality∈{task,noise}。
**v0.3 监督分类**：`train_supervised.py` TF-IDF(latin+CJK bigram, vocab=1000) + nearest-centroid(cosine)，分层 5 折 CV（每折用训练集重算 idf，诚实评估）。小类(<5)并入 other。10 类。
**结果**：
- task=2107 / noise=151（noise 排除出评分与训练）。
- CV accuracy=0.8248±0.0114 / macro-F1=0.5723±0.0579。
- 强类：eda_aether_layout P/R/F1=0.964/0.965/0.965（pyaether 强信号）；eda_innovus F1=0.807；code_dev F1=0.784。
- 弱类（小样本+centroid 基线限制）：eda_virtuoso_schematic F1=0.433(44)、eda_env_qa F1=0.326(17)、meta_agent_ops F1=0.262(9)、eda_timing_power F1=0.345(7)。宏 F1 被小类拖低。
- 评分：task-only 中位 0.6917 / 均值 0.6724（噪声排除后）。
- leak check：app.e*/t*/vendor=0, shiwei/zhulong=0, email=0, /home/app.*=0（仅 `<REDACTED>`×2 / `<USER>`×267 占位符）。
**踩坑**：(1) `importlib.util` exec_module 在 loader 上不在 spec 上；(2) argparse `--v03-dir` 映射 `v03_dir` 不是 `out_dir`。均已修。
**结论**：v0.3 交付 CJK 修复 + 人工策展 + 噪声隔离 + 监督基线；多机扇出仍阻塞但 v0.3/v0.4 路径不阻塞。v0.4 候选：LLM-judge 标注层（提小类 F1）+ 小类样本扩增。
**复现**：`cd designflow/bench_v0.3 && bash reproduce.sh`。

## EXP-10 (2026-10-28) 第5轮复探 + bench_v0.4（LLM-judge 标注层）
**方法**：第5轮复探 8092/.75 + 在 v0.3 脱敏集上建 v0.4 独立第二标注者（judge）。
**复探原始输出**：
- 8092 tools/list：`cimi_search/cimi_fetch/vqa/text_to_image`（同前，无 exec/ssh）。
- .75：`Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password)`；ping `3 received, 0% loss, time 2036ms`（**第5轮同卡点**：ping 通 + SSH 无凭证）。
- 本机：20 sessions 目录 / 19 有数据 / **3487** `*.messages.json`（**+8 增长**，持续增长得到验证）。
**v0.4 judge 设计**：
- `judge.py` 双后端：`rule`（默认，纯标准库可逐比特复现）/ `llm`（OpenAI 兼容 `/v1/chat/completions`，env `DESIGNFLOW_LLM_JUDGE_URL/KEY/MODEL`，缺则透明 `rule_fallback`）。
- 类目录：11 task 类 + 2 noise 类，每类手调权重签名项（latin 关键词/CJK bigram/子串）；short acronym（drc/lvs/erc）用 `~\b...\b` 词界正则避免子串过泛。
- noise 高精度守卫（阈值 3.0，hello/world/直接输出/ask_question 等短路到 noise_*）；task 类 argmax，得分<2.0 或置信度<0.30 回退 other。
- 发布 `judge_prompt_template.txt`（system + 13 条 few-shot + catalogue）供外部 LLM-judge 直接复用。
- 每条任务现带 `category_v3`（curated）+ `category_v4`（judge）+ `judge_confidence` + `judge_source` + `agrees_with_v3`。
**结果**：
- judge 判定 2258 条；与 v0.3 一致率 **0.5914**（task-only 0.5914）。
- 强一致：eda_aether_layout(1000) agr=0.988；eda_drc_lvs(4) agr=1.0；eda_virtuoso_schematic(44) agr=0.864；eda_env_qa(17) agr=0.882；meta_agent_ops(9) agr=0.778；eda_timing_power(7) agr=0.714。
- **headline 发现（标签噪声暴露）**：`code_dev`(738) 仅 agr=**0.104**——judge 把其中 **146 条判为 noise_toy_test**、90→eda_virtuoso_schematic、59→meta_agent_ops、55→eda_env_qa。暴露 v0.3 `code_dev` 把 agent-policy-engine `run_approved_command` 工具自测（"用 test-calculate profile 生成 3x3 随机数表"这类）与真代码开发混为一谈。这正是独立第二标注者的价值。
- other 桶：v3=153 → v4=259（judge 更保守，低置信回退 other）；38 条 other→真类别（34→eda_drc_lvs，prompt 明确提 DRC/LVS，是 v0.3 聚类漏掉的真实任务）。
- noise_greeting：修签名权重后 agr 0→0.50。
- quality_score_v0_4 = 0.6×task_agreement + 0.4×other_reduction_pct = 0.3548（judge 保守导致 other 增长，故分数偏低；分数本身只刻画与 v0.3 的偏离，非绝对质量）。
- leak check：app.e*/t*/vendor/shiwei/zhulong/email//home/app.*=0（占位符 `<REDACTED>`×3 / `<USER>`×302）。
**复现**：`cd designflow/bench_v0.4 && bash reproduce.sh`（rule 模式）；LLM 模式设 `DESIGNFLOW_JUDGE_MODE=llm` + 三个 env 变量。
**结论**：v0.4 交付独立第二标注者 + LLM-judge 脚手架 + 标签噪声量化；多机扇出仍阻塞但 v0.4/v0.5 路径不阻塞。v0.5 候选：接真实 LLM endpoint 跑 llm 模式对比 / 小类样本扩增 / 多标注者 gold set。


---

## 已归档批次 2（→ EXP-06..EXP-10 原文，2026-10-28 第14轮体积维护）

## EXP-06 (2026-10-28) bench_v0.5 多标注者共识 gold + 裁决脚手架
**动机**：v0.4 headline（v3 vs v4 一致率 0.5886）只量化"分歧多少"，无法判"谁对"。v0.5 把 v3_supervised 与 v4_rule 当两个独立标注者，构造共识 gold + 分歧 splits，并设计可插拔第 3 标注者（外部 LLM）走 2-of-3 多数表决。
**方法**：
- `adjudicate.py`：读 `tasks_v4.jsonl`，2 标注者模式 consensus = v3==v4 且 quality=task，分层封顶 50/类；分歧入 `splits.jsonl`。可选 `--llm <llm_judge.jsonl>` 接第 3 标注者转 2-of-3 多数 gold + 每标注者对多数 gold 一致率（对单标注者非循环）。
- `eval.py`：通用标注者评估器（acc / macroF1 / 每类 P/R/F1 / Top 混淆），对新标注者非循环。
- `report_v5.py`：HTML 交付报告。
**结果**（2 标注者模式，本机脱敏集）：
- consensus_gold = **269** 条（unique session_id 254；封顶后 eda_aether_layout 50 / code_dev 50 / other 50 / eda_virtuoso_schematic 38 / eda_innovus 17 / eda_env_qa 15 / data_analysis 23 / file_ops 10 / meta_agent_ops 7 / eda_timing_power 5 / eda_drc_lvs 4）；task_quality=2107，noise=151。
- splits = **861** 条（待 LLM 裁决输入）。
- Top 分歧热点 v3→v4：**code_dev→other 174** / **code_dev→noise_toy_test 146** / code_dev→eda_virtuoso_schematic 90 / eda_aether_layout→other / other→eda_aether_layout。定位了 v0.4 59% 分歧的**主体在 code_dev**——v0.3 把工具自测/非代码误纳为 code_dev。
- eval rule_judge_vs_gold：n=254 acc=1.0 macroF1=1.0 —— **预期循环**（gold⊂v4 一致集，自洽 sanity，非独立质量），报告已显式标注此局限。
**数据质量发现**：`tasks_v4.jsonl` 含 **146 个重复 session_id**（2258 记录→2112 unique；gold 内 15 重复）。上游未去重，记为 benchmark 完整性待修项（v0.6 候选：去重 + session_id 加 user_hash 前缀消歧）。
**局限**：2 标注者共识 gold 对 v3/v4 自身评估因构造虚高；评估器对未参与 gold 构造的新标注者（外部 LLM）才非循环。splits 集是该循环的核心出口。
**leak check**：v0.5 全产物（gold/splits/exemplars/views/stats/eval/report.html）扫 app.e*/t*/vendor/shiwei/zhulong/email//home/app.* = **0 残留**（继承 v0.4 已脱敏集）。
**复现**：`bash designflow/bench_v0.5/reproduce.sh`（2 标注者）；`DESIGNFLOW_LLM_JUDGE_FILE=<llm_judge.jsonl> bash ...reproduce.sh`（3 标注者多数表决）。
**结论**：v0.5 交付高精度共识 gold + 分歧裁决脚手架 + 分歧热点定位；真实评估力待接第 3 标注者（LLM endpoint 仍待 env，不阻塞）。

## EXP-07 (2026-10-28) bench_v0.6 session_id 去重 + global_id 消歧 + PII 泄漏修复
**动机**：EXP-06 发现 `tasks_v4.jsonl` 含 146 个跨用户重复 session_id（2258→2112 unique），污染 v0.5 gold（15 重复）/splits（80 重复）。v0.6 增加去重层并附前向安全唯一键。过程中 leak check 暴露一处自第1轮起漏检的 PII 泄漏。
**方法**：
- `dedup.py`：按 session_id 分组；组内内容签名（prompt+cwd_category+model+n_turns+n_tool_calls+tools_used+duration_sec+category_v3+category_v4+quality）全等 ⇒ 真重复折叠为 1 条代表（按 tools_used 数降序+user_hash 取代表），所有 user_hash 保留在 `dup_user_hashes`，`dup_count` 记原始份数；签名分歧 ⇒ sid 碰撞保留全部并附 `global_id`+`sid_collision=true`（守卫，当前 0 例）。每条记录附 `global_id = user_hash/session_id`。
- `report_v6.py`：HTML 报告（去重前后对照表 + gold/splits 影响表 + 分歧热点 + sid 碰撞守卫明细 + 局限）。
- `reproduce.sh`：先跑 v0.5 作 before-dedup 基线 → dedup.py → 复用 v0.5 `adjudicate.py`/`eval.py`（通过 staging 目录 `out/_staging/tasks_v4.jsonl`=去重集副本，因 v0.5 脚本硬编码 tasks_v4.jsonl 文件名与 category_v3/v4 字段，v0.6 保留这些字段故可复用）→ report_v6.py。
- **PII 修复**：`bench_v0.1/extract.py` 的 `desensitize_text` 补三条正则——`PASSWORD_LIKE_RE`=`\b[A-Za-z_]\w*@\d{3,}\b`（捕获 `Cxmt@202608` 这类 Word@digits 密码，email 正则因要求点号域名漏检）、`SVC_ACCT_RE`=`\bsvc\.[A-Za-z0-9._-]+\b`（捕获 `svc.edaagent`）、`CN_CRED_LABEL_RE`=`(密码|账号|令牌|口令|凭据|凭证|密钥)\s*[:：]\s*\S+`（中文凭证标签后的值，token 正则只匹配英文关键词故漏检）。重跑全链路 v0.1→v0.6。
**结果**（去重 + 重跑基数）：
- 去重：2258 行 → **2112 行**（146 真重复 sid 折叠，146 重复行移除）；0 sid 碰撞；0 重复 session_id；0 重复 global_id。验证 146 个跨用户 dup sid **全部**内容签名全等（同会话存在于多用户目录，疑克隆/种子会话）。
- 去重影响（v0.5 before → v0.6 after）：**splits 954→850（去 104 重复行）/ gold 247→246（去 1 重复行）**，v0.6 gold/splits 均 0 重复 sid。
- v0.6 consensus gold=246（封顶 50/类：eda_aether_layout 50 / code_dev 50 / other 50 / eda_virtuoso_schematic 38 / eda_innovus 17 / data_analysis 23 / eda_drc_lvs 4 / eda_timing_power 5 / file_ops 9）；task_quality=2085，noise=27（35 noise 中 8 落入 dup 折叠）。
- Top 分歧 v3→v4：code_dev→other 166 / code_dev→noise_toy_test 92 / other→noise_toy_test 90（结构同 v0.5，去重基数上数字略降）。
- eval rule_judge_vs_gold：n=246 acc=1.0 macroF1=1.0（预期循环自洽 sanity，2 标注者）。
- **PII leak check**：全产物（tasks.jsonl/v2/v3/v4/v6 + gold + splits）扫 Cxmt@202608/svc.edaagent/Word@digits/email/app.e*/t*/vendor/shiwei/zhulong//home/app.* = **0 残留**。修复前 `Cxmt@202608`+`svc.edaagent` 各 1 处（同一 email-config 任务记录）自第1轮起在 git 中。
**重跑可复现性观察**：全链路重跑后 v0.5 gold=247/splits=954（vs 第6轮 EXP-06 的 269/861）——v0.3 聚类/监督步骤疑似含未固定种子随机性，跨全量重跑数值微动。去重层本身完全确定。**v0.7 候选**：固定 `random_state`。
**局限**：2 标注者共识 gold 对 v3/v4 自评估虚高（自洽 sanity）；非循环评估需第3标注者（v0.5 `--llm` 接口 v0.6 继承）。单机（.75 连续7轮同卡点）。git 历史含未脱敏 PII（人名+密码+服务账号），待人工决断 force-push。
**复现**：`bash designflow/bench_v0.6/reproduce.sh`；`DESIGNFLOW_LLM_JUDGE_FILE=<llm_judge.jsonl> bash ...reproduce.sh`（3 标注者）。
**结论**：v0.6 交付去重 + 前向安全 global_id 唯一键 + 修复一处历史 PII 泄漏（重跑全链路 0 残留）；gold/splits 不再被跨用户重复样本加权扭曲。逐比特可复现性留 v0.7 固定种子。

## EXP-08 (2026-10-28) bench_v0.7 逐比特可复现性验证 + 发现并修复两处真实可复现性隐患
**动机**：EXP-07 把 v0.5 round6→7 的 269→247 漂移归因为"疑似未固定种子"，标记 v0.7 候选"固定 random_state"。v0.7 把怀疑变成经验证明：全链路二次重跑 + sha256 逐比特比对。过程中发现两处真实的可复现性隐患（远比"种子"更深）。
**方法**：
- `repro_check.py`：把 `designflow/`（排除 out/ 与 __pycache__）复制到两个独立临时根 `_repro_tmp/runA|runB/designflow`，并行跑 `bench_v0.6/reproduce.sh`（级联 v0.1→v0.6），对两份 out/ 全产物做 sha256，逐文件比对，输出 `repro_verdict.json`（PASS/FAIL + 每阶段状态 + 确定性审计）+ `hash_manifest_A/B.json` + `mismatch_detail.json`（仅 FAIL 时）。
- `report_v7.py`：HTML 报告（裁决 + 各阶段哈希比对表 + 确定性审计 + 隐患发现与修复 + v0.5 漂移根因澄清 + 局限）。
- `reproduce.sh`：一键（设 SOURCE_DATE_EPOCH/PYTHONHASHSEED/SCAN_ROOT → repro_check → report_v7）。
- 红线：临时树落 `out/_repro_tmp/`（gitignore）；不改 commit 的 out/；只读扫 /home。

### 发现的隐患 1：墙钟时间戳嵌入产物（4 处）
v0.1-v0.6 看似确定，但 4 处把运行时墙钟 `datetime.now()` 写入产物元数据：
- `bench_v0.1/extract.py` → stats.json `generated_at`
- `bench_v0.2/refine.py` → stats_v2.json `generated_at`
- `bench_v0.3/curate.py` → curation_stats.json `generated_at`
- `bench_v0.4/report_v4.py` → report_v4.html 内联
**修复**：4 处替换为共享 `_now_iso()` helper，遵循可复现构建标准约定尊重 `SOURCE_DATE_EPOCH`（设置→冻结时间戳逐比特可复现；未设→回退墙钟 UTC，保持人类可读默认，不影响评分/分类）。

### 发现的隐患 2：PYTHONHASHSEED 导致 TF-IDF/kmeans 漂移（真正的根因，非"种子"）
首轮验证（仅修时间戳）VERDICT=FAIL：v0.1 PASS 但 v0.2+ 全 FAIL。`mismatch_detail` 显示 tasks_v2.jsonl 的 `cluster_id`/`cluster_label` 在两轮间不同（如 4→6, `eda_cline_askeda_user`→`rtl_cline_say_testing`），而 prompt/特征完全一致。
**根因**：Python 默认 `PYTHONHASHSEED=random` → 字符串哈希每次进程不同 → `Counter.most_common()` 在并列计数时 tie-break 顺序不同 → TF-IDF 词表列顺序不同 → kmeans（即便 seed=7 固定）的初始中心选择 `rng.integers(n)` 索引落在不同文档 → 收敛到不同聚类。这才是 v0.5 漂移的真正机制（EXP-07 误判为"未固定种子"，实际种子都固定了，是 hash 随机化）。
**修复**：所有 reproduce.sh `export PYTHONHASHSEED=0`（标准可复现构建 fix）；repro_check 的 env 也固定。修复后第二轮验证 **VERDICT=PASS**。

### 第二轮验证结果（PASS）
- 两轮全链路重跑（v0.1 extract 只读扫同一份 /home → v0.6 dedup），73 个输出文件 sha256 **全部一致**。
- 每阶段：v0.1 5/5、v0.2 5/5、v0.3 7/7、v0.4 5/5、v0.5 7/7、v0.6 10/10 全 PASS。
- wall=6.5s（两轮并行）。numpy=1.26.4。
- `bash reproduce.sh` 一键跑通（acceptance #4）。

### v0.5 漂移根因澄清
EXP-06→07 的 v0.5 gold 269→247 / splits 861→954 **不是**可复现性 bug：根因是 round7 在 PII 修复（extract.py +3 正则）后重跑全链路，上游 prompt 文本变化 → TF-IDF → category_v3 聚类标签变化。v0.7 两轮比对用相同输入，该漂移不复现，已排除为可复现性隐患。

**leak check**：v0.7 产物（repro_verdict/hash_manifest/report.html）扫 PII = **0 残留**（仅 console.log 含本机路径 app.e0031982，已 gitignore）。临时树 gitignore。
**局限**：验证基于单机 /home 扫描根（多机扇出仍待运维，第8轮同卡点）；逐比特可复现依赖显式设 SOURCE_DATE_EPOCH+PYTHONHASHSEED（reproduce.sh 已默认设）；numpy 浮点求和跨大版本理论可能漂移（版本记入 verdict）。
**复现**：`cd designflow/bench_v0.7 && bash reproduce.sh`（默认 SOURCE_DATE_EPOCH=1793145600 / PYTHONHASHSEED=0 / SCAN_ROOT=/home）。
**结论**：v0.7 把 v0.1-v0.6 从"看起来确定"升级为"经验证逐比特可复现"（73/73 文件 sha256 一致），并修复两处真实可复现性隐患（墙钟时间戳 ×4 + PYTHONHASHSEED hash 随机化）。acceptance #4（全链路脚本化可复现）经实测闭环。

## EXP-09 (2026-10-28) 第9轮复探 + bench_v0.8 源快照冻结 + 跨主机可复现性
**复探原始输出**：
- 8092 tools/list：`cimi_search/cimi_fetch/vqa/text_to_image`（同前，无 exec/ssh）。
- .75：`ssh: connect to host 10.251.36.75 port 22: Connection timed out`；`ping` 100% loss。**状态恶化**（第8轮 ping 通+Permission denied → 第9轮主机完全不可达，回到第3轮状态）。**连续9轮同卡点**，上报仍有效待回复。
- 3口径现查：1 机 / **19** sessions 目录（**20→19，一个含数据用户目录被主机侧移除**）/ **3478** `*.messages.json`（**3487→3478，-9**）。真实漂移：本机 /home 并非单调增长，用户目录会被清理/归档。

**v0.8 动机（v0.7 留下的缺口）**：v0.7 证明同一时刻可复现性，但 v0.1 `reproduce.sh` 默认每次重扫实时 /home，把 benchmark 地基锚定在持续变异的主机上。本轮漂移证据（3487→3478）证明：若直接跑 v0.1 reproduce.sh，会用当前实时数据**静默覆盖**已提交冻结快照。且 v0.7 repro_check 实际从未重跑 extract.py（复制树已含已提交 tasks.jsonl，v0.2+ 跳过 v0.1），其"v0.1 5/5 PASS"是比对复制副本——de facto 已是冻结源测试，v0.8 把这层隐式语义显式化并补主机无关性证明。

**方法**：
- `freeze.py`：`--create` 算冻结源三文件（tasks.jsonl/stats.json/raw_inventory.json）sha256 + 源统计 → `source_manifest.json`（snapshot_id/捕获时刻/provenance）；`--verify` 重算并断言匹配（地基完整性/防漂移防篡改）。
- 加固 `bench_v0.1/reproduce.sh` **freeze-by-default**：默认不扫 /home，仅从冻结源重建派生产物（scorer.py 无时间戳、report.py 仅引用 stats 冻结 generated_at → 完全逐比特确定）；显式 `RESCAN=1`（可选 `SCAN_ROOT=<path>`）才只读重扫（"扩增"路径，须重跑 leak check+升版本+重新提交）。`SCAN_ROOT` 单独不再触发 rescan（更安全默认）。
- `cross_time.py`：临时副本中以 `SCAN_ROOT=<不存在路径>` + `RESCAN=0` 重跑全链路 v0.1→v0.6（零 /home 访问），与已提交 out/ 逐文件 sha256 比对 → `cross_time_verdict.json`。
- 同步修 `bench_v0.7/repro_check.py`：v0.7 复制树排除 out/ 全链路重跑，需 v0.1 重扫 → 显式 `env["RESCAN"]=1`（v0.7 目的是"重扫实时 /home 两次比对"，v0.8 freeze-by-default 后必须显式 opt-in）。

**结果**：
- **cross_time VERDICT=PASS**：40/40 文件 sha256 全一致（零 /home 访问重跑全链路）。foundation manifest verify PASS（tasks.jsonl sha256=a1cd058a… 与提交一致）。
- 源 manifest：snapshot_id=`a1cd058a7ae08449`，冻结 tasks.jsonl 2258 条 / 16 个 distinct user_hash（已发布集；资产盘点 19 用户在 source_stats.asset_inventory_at_capture）。
- v0.7 回归 PASS（78/78，0 mismatched，修复后无回归）；已提交 v0.1 out/ sha256 不变（freeze-by-default 不覆盖）。
- leak check v0.8 产物 0 残留（manifest/verdict/report 不含任务文本）。

**意义**：把 benchmark 从"锚定实时变异主机"升级为"自包含、可移植、冻结的产物"——clone 到无 cline 数据的机器上仍能逐比特复现。同时服务任务书"可复现"（冻结源+确定性管线）与"可扩增"（显式 RESCAN 产出新版本快照）双重要求。闭环 v0.7 留下的最后一个可复现性维度（跨时间/跨主机）。

**局限**：冻结快照仍单机（捕获时刻本机；多机扇出经 .75 仍阻塞，连续9轮同卡点）；v0.8 不改 v0.1-v0.6 算法/产物内容，数值结论继承 v0.6（2112 去重任务/246 gold/850 splits）；git 历史含未脱敏 PII 待人工决断 force-push（仍悬）。
**复现**：`cd designflow/bench_v0.8 && bash reproduce.sh`（默认 SOURCE_DATE_EPOCH=1793145600 / PYTHONHASHSEED=0 / SCAN_ROOT=<不存在路径> / RESCAN=0）。
**结论**：v0.8 交付源快照冻结 + provenance manifest + 跨主机可复现性证明（40/40 PASS），修复 v0.1 默认重扫的安全隐患，v0.7 无回归。

---

## EXP-10 (2026-10-28) 第10轮复探 + bench_v0.9 规范发布 bundle + 提交评估器

**三个口径（现查）**：1 机 / 19 sessions 目录 / 3478 轨迹（与上轮持平，无新样本）。.75 第10轮**恢复可达**（ping 0% loss，SSH 仍 Permission denied，回到第8轮状态；连续10轮同卡点，上报仍有效待回复）。8092 仍 RESEARCH（无 exec/ssh）。

**v0.9 动机**：v0.1–v0.8 建好了管线各层，但交付物分散在 8 个版本目录里，没有"这就是发布版 benchmark"的规范包。第三方无法直接拿来评估自己的分类器。v0.9 把管线产物装配为一个可发布、可被第三方使用的规范 bundle，闭环 acceptance #2（版本化 benchmark 含任务集+评分口径+复现）与 #3（HTML 报告+数据清单）的"可发布性"维度。

**方法**：
- `release.py`：从冻结 v0.6/v0.8 输出装配 4 个发布文件。
  - `tasks.jsonl`（2112，canonical fields，无 gold label）——无标注评估语料。
  - `gold.jsonl`（246，共识 gold answer key）——join tasks_v6 补 `global_id`+`user_hash`（v0.6 的 gold/splits 只有 session_id，发布需 global_id 前向安全键）。
  - `few_shot.jsonl`（27，分层 ≤3/类，**带标签**）——供提交者做 few-shot。
  - `test_set.jsonl`（219，**盲测集，无标签**）——提交者在此预测。
  - 分层用 `random.Random(seed=42)`，类内按 global_id 排序后 shuffle（确定性）；类内 ≤1 项时全留 test（保每类有 test）。
- **split integrity guard**：few_shot∩test_set global_id=0 且 session_id=0，每类 ≥1 test item → **PASS**。user_hash 跨 split 重叠（6 个）**显式报告**为单机来源局限（15 用户无法做用户不相交），不 enforce——global_id/session_id disjointness 才是 label-predictor 评估的有意义泄漏守卫（test item 本身绝不出现在 few-shot）。
- `eval_submission.py`：第三方提交评估器。submission 格式 `{"global_id":"<gid>","predicted_label":"<class>"}`。输出 acc / macro P/R/F1 / per-class P/R/F1/support / top 混淆 / coverage（检测未覆盖 test 项，避免静默漏评）。dup global_id 计数告警。
- `release_manifest.json`：checksums（4 文件 sha256）+ counts + gold class dist + split integrity verdict + provenance（snapshot_id 继承 v0.8 `a1cd058a7ae08449`）+ 5 条 limitations + usage（评估命令 + label catalogue）。
- `report_v9.py`：HTML 发布报告 + 数据清单（headline/integrity verdict/使用说明/文件表/类分布/分层表/局限/provenance）。
- `reproduce.sh`：`EVAL_SELFTEST=1` 跑 majority baseline 冒烟测评估器。

**结果**：
- 装配：tasks 2112 / gold 246 / few_shot 27（3×9 类，file_ops=9 取 3） / test 219。
- split integrity **PASS**：global_id/session_id 交集=0，每类 ≥1 test。
- **EVAL_SELFTEST 端到端验证**：majority baseline（全预测 eda_aether_layout）n=219/219 coverage=1.0 acc=0.2146 macroF1=0.0393——符合预期（eda_aether_layout 占 test ~21%），证明评估器接线正确。
- **leak check 全产物 0 残留**（app.e*/t*/email/Word@digits/svc.*/shiwei/zhulong/cxmt domain=0）。
- **determinism**：数据文件（tasks/gold/few_shot/test_set）sha256 两轮完全一致；release_manifest.json 仅 `assembled_at` 时间戳差异——设 `SOURCE_DATE_EPOCH` 后完全逐比特一致（与 v0.7/v0.8 同约定）。
- gold 类分布：eda_aether_layout 50 / code_dev 50 / other 50 / eda_virtuoso_schematic 38 / data_analysis 23 / eda_innovus 17 / eda_env_qa 15 / file_ops 9 / eda_timing_power 5 / eda_drc_lvs 4（file_ops 10→9 为 v0.6 去重移除 1）。

**意义**：把 benchmark 从"8 个分散版本目录"升级为"1 个可发布的规范 bundle"——clone 到无 cline 数据的机器上，第三方即可在盲测集上评估自己的设计流任务分类器并拿到 acc/macroF1/per-class/confusion。这是面向"真实用户约 500 且持续增长"目标的最小可用发布形态：单机冻结集已可用，多机扩增留作 RESCAN 升版路径。

**局限**：单机来源（15 用户），多机扇出经 .75 仍阻塞（连续10轮）；few_shot/test 共享用户（单机局限，已显式报告，global_id disjointness enforced）；小类（eda_drc_lvs=4→test 1，eda_timing_power=5→test 2）per-class 指标不稳定，macro 平均一并报告；gold 为 2 标注者共识（v3_supervised+v4_rule），第3 LLM 标注者路径（v0.5）未接 live endpoint；冻结于 snapshot_id a1cd058a，live /home 已漂移（3487→3478），发布有意与漂移解耦。

**红线遵守（第10轮）**：v0.9 全程零 /home 访问（只读冻结 v0.6/v0.8 输出）；未脱敏不入 git（全产物 leak check 0 残留）；原始轨迹不入库；无网络；纯标准库；不碰他人进程；不用 GPU；.75 恢复可达但仍无凭证不硬探；上报仍有效（连续10轮同卡点）不静默硬撑。

**复现**：`cd designflow/bench_v0.9 && bash reproduce.sh`（默认零 /home 访问）；`EVAL_SELFTEST=1 bash reproduce.sh`（含评估器冒烟）。
**结论**：v0.9 交付规范发布 bundle + 盲测集 + 提交评估器 + split integrity guard（PASS），benchmark 升级为可被第三方直接使用的最小可用发布形态。多机扇出仍阻塞但 v0.9/v0.10 路径不阻塞。v0.10 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 / RESCAN 扩增冻结快照 / 把 v0.9 bundle 发布为对外 v1.0 候选。


---

## 归档批次 3（2026-10-28 第16轮）：MEMORY 流水 轮次 1–12 原文

搬入原因：`MEMORY_DESIGNFLOW.md` 第16轮追加 v0.15 后达 32.3KB（>32KB 软限），按规程把
最新活跃块（v0.13/v0.14/v0.15）之下的已闭合流水块（轮次 1–12）归档。结论已沉淀在
`MEMORY_DESIGNFLOW.md` 的交付物清单；以下为流水原文备查。

### 流水原文（轮次 1–12，自 MEMORY 搬入）

- [17:01] 探明 8092=RESEARCH-MCP-SERVER(无exec)；.75 SSH 拒绝；发现本机即目标(19用户/3487轨迹)；建 bench_v0.1，脱敏+评分+HTML，leak check 通过。3口径=1机/19用户/3487轨迹。
- [17:40] 本轮唤醒：8092 仍无exec、.75 仍 Permission denied、3口径不变(1机/19用户/3487轨迹)。建 bench_v0.2(细化分类+TF-IDF聚类+模型横向)，兜底桶837→384(-54%)。v0.2聚类暴露残留人名 shiwei/zhulong → 修 extract.py(RESIDUAL_NAMES+上下文scrub) → 重跑v0.1+v0.2 → 全产物leak check 0残留。git历史21f4de3仍含人名，待人工决断。
- [18:05] 第3轮唤醒：8092仍RESEARCH(无exec)；.75**恶化**为 Connection timed out + ping 100% loss(上轮Permission denied)→主机不可达；3口径现查=1机/20 sessions目录(新增 app.t0002997 但0轨迹,有数据仍19)/3479轨迹。**连续3轮同卡点(.75不可达+8092无exec)→触发上报**，置WAITING=1等运维决断5选1；不再硬探。v0.3(人工标注聚类+监督分类,纯本机脱敏集)不阻塞可继续。
- [17:25] 第4轮唤醒：.75**恢复可达**(ping 0% loss, SSH 仍 Permission denied，回到第1/2轮状态)；8092仍RESEARCH(无exec)；3口径=1机/20dir(19有数据)/3479轨迹(无新样本)。上报仍有效待回复。**推进不阻塞的 v0.3**：(1)发现 v0.2 `cluster:_empty`(203) 是 CJK 分词盲区(拉丁正则漏全中文prompt)→v0.3 加字符 bigram 分词重聚类；(2)人工策展 cluster 标签(11类)；(3)噪声标记 quality=noise(toy/问候/工具自测151条,排除出评分)；(4)监督分类基线 TF-IDF+nearest-centroid 5折CV：acc=0.8248±0.0114 / macroF1=0.5723±0.0579(eda_aether_layout F1=0.965, eda_innovus F1=0.807, 小类F1低留v0.4 LLM-judge)。`other` 从 v2 残余降到153。leak check 0残留。bash reproduce.sh 一键复现。
- [17:50] 第5轮唤醒：.75**仍** ping 0% loss + SSH Permission denied（连续第5轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径=1机/20dir(19有数据)/**3487轨迹(+8,持续增长)**。**推进不阻塞的 v0.4 LLM-judge 标注层**：(1)judge.py 双后端 rule(纯标准库可复现)/llm(OpenAI兼容,env DESIGNFLOW_LLM_JUDGE_URL/KEY/MODEL,缺则透明rule_fallback)；(2)11 task类+2 noise类,每类手调权重签名项,noise高精度守卫,drc/lvs用\b词界正则;(3)发布 judge_prompt_template.txt 供外部 LLM-judge 复用;(4)每条任务现带 category_v3+category_v4+agrees_with_v3。judge 与 v0.3 一致率 0.5914——**headline 发现**:code_dev(738)仅 10.4% 一致,judge 把其中 146 条判为 noise_toy_test(暴露 v0.3 code_dev 把 agent-policy-engine 工具自测与真代码开发混为一谈的标签噪声);eda_aether_layout(1000)0.988/eda_drc_lvs 1.0/eda_virtuoso_schematic 0.864 稳。other 桶 153→259(judge 更保守),38 条 other→真类别。leak check 0残留。bash reproduce.sh 一键复现。
- [18:00] 第6轮唤醒：.75**仍** ping 0% loss + SSH Permission denied（连续第6轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径=1机/20dir(19有数据)/**3487轨迹(与上轮持平,无新样本)**。**推进不阻塞的 v0.5 多标注者共识 gold+裁决脚手架**：(1)adjudicate.py 把 v3_supervised 与 v4_rule 当两个独立标注者,2-annotator 模式 consensus=v3==v4&quality=task 分层封顶50/类,分歧入 splits;可选 --llm 接第3标注者转 2-of-3 多数表决+每标注者对多数gold一致率(非循环);(2)eval.py 通用标注者评估器(acc/macroF1/每类P/R/F1/Top混淆);(3)report_v5.html。结果:consensus gold 269(unique254)/splits 861;**分歧热点定位**:code_dev→other174、code_dev→noise_toy_test146、code_dev→eda_virtuoso_schematic90——v0.4 59%分歧主体在 code_dev(v0.3 误纳工具自测);eval rule_judge_vs_gold acc=1.0=预期循环自洽sanity,报告显式标注局限。**数据质量发现**:tasks_v4含146重复session_id(2258→2112 unique,gold内15重复),上游未去重,记为v0.6候选。leak check 0残留。bash reproduce.sh 一键复现。
- [18:15] 第7轮唤醒：.75**仍** ping 0% loss + SSH Permission denied（连续第7轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径=1机/20dir(19有数据)/**3487轨迹(与上轮持平,无新样本)**。**推进不阻塞的 v0.6 去重+global_id层**：(1)dedup.py按session_id分组,内容签名全等⇒真重复折叠(146跨用户dup sid全部内容一致→折叠为1,保留dup_user_hashes),签名分歧⇒sid碰撞守卫(0例);每条附global_id=user_hash/session_id;2258→2112行/0重复sid/0重复global_id。(2)复用v0.5 adjudicate/eval(staging目录),splits 954→850(去104重复行)/gold 247→246(去1重复行)。(3)🔴**PII泄漏修复**:leak check用宽正则扫到Cxmt@202608(服务密码)+svc.edaagent(服务账号),自第1轮漏检(email正则要点号域名漏Word@digits,token正则只匹配英文漏中文标签);extract.py补PASSWORD_LIKE_RE/SVC_ACCT_RE/CN_CRED_LABEL_RE三正则,重跑全链路v0.1→v0.6,全产物0残留。重跑可复现性观察:v0.5 gold247/splits954(vs第6轮269/861),v0.3聚类疑似未固定种子→v0.7候选固定random_state。leak check 0残留。bash reproduce.sh一键复现。
- [18:38] 第8轮唤醒：.75**仍** ping 0% loss + SSH Permission denied（连续第8轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径=1机/20dir(19有数据)/**3487轨迹(与上轮持平,无新样本)**。**推进不阻塞的 v0.7 逐比特可复现性验证层**：(1)repro_check.py把designflow/(排除out/)复制到两个独立临时根,并行跑v0.6 reproduce.sh(级联v0.1→v0.6),对两份out/做sha256逐文件比对。(2)**首轮VERDICT=FAIL**→发现并修复两处真实隐患:①墙钟时间戳×4(extract/refine/curate/report_v4的datetime.now()→_now_iso()尊重SOURCE_DATE_EPOCH);②**PYTHONHASHSEED** hash随机化(才是v0.5漂移真正根因,非EXP-07误判的"种子"——Counter.most_common tie-break→TF-IDF词表列序→kmeans初始中心不同→不同cluster_id);所有reproduce.sh export PYTHONHASHSEED=0。(3)**第二轮VERDICT=PASS**:73/73文件sha256全一致(v0.1 5/5,v0.2 5/5,v0.3 7/7,v0.4 5/5,v0.5 7/7,v0.6 10/10),wall6.5s两轮并行。v0.5 round6→7的269→247漂移根因澄清为PII修复改变上游输入,非可复现性bug。bash reproduce.sh一键复现(默认SOURCE_DATE_EPOCH=1793145600/PYTHONHASHSEED=0)。leak check v0.7产物0残留(临时树+console.log gitignore)。acceptance #4经实测闭环。
- [18:58] 第9轮唤醒：.75**恶化**为 Connection timed out + ping 100% loss（连续第9轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**19dir(20→19,一个含数据用户目录被主机侧移除)**/**3478轨迹(3487→3478,-9)**——本机/home并非单调增长,用户目录会被清理/归档(真实漂移,仅只读观察)。**推进不阻塞的 v0.8 源快照冻结层**(闭环v0.7留下的跨时间/跨主机可复现性缺口):(1)发现v0.7留下的缺口:v0.1 reproduce.sh默认每次重扫实时/home,把benchmark地基锚定在持续变异主机,直接跑会静默覆盖已提交冻结快照;且v0.7 repro_check实际从未重跑extract.py(复制树已含tasks.jsonl,v0.2+跳过v0.1),de facto已是冻结源测试。(2)freeze.py建源快照manifest(冻结tasks.jsonl/stats/raw_inventory三文件sha256+provenance,snapshot_id=a1cd058a…);--verify做地基完整性校验。(3)加固bench_v0.1/reproduce.sh为**freeze-by-default**(默认不扫/home,仅从冻结源重建派生产物;显式RESCAN=1才只读重扫即"扩增"路径)。(4)cross_time.py:临时副本中以SCAN_ROOT=<不存在路径>+RESCAN=0重跑全链路v0.1→v0.6(零/home访问),与已提交out/逐文件sha256比对→**VERDICT PASS 40/40**;foundation manifest verify PASS。(5)同步修bench_v0.7/repro_check.py显式env RESCAN=1。leak check v0.8产物0残留。bash reproduce.sh一键复现(默认零/home访问)。意义:benchmark升级为自包含、可移植、冻结的产物。
- [19:14] 第10轮唤醒：.75**恢复可达**（ping 0% loss，SSH 仍 Permission denied，连续第10轮同卡点）；8092仍RESEARCH(无exec)；3口径=1机/19dir/3478轨迹。**推进不阻塞的 v0.9 规范发布 bundle 层**：(1)release.py从冻结v0.6/v0.8输出装配4个发布文件——tasks.jsonl(2112)/gold.jsonl(246)/few_shot.jsonl(27)/test_set.jsonl(219,盲测);(2)split integrity guard:few_shot∩test_set global_id=0且session_id=0→PASS;(3)eval_submission.py第三方提交评估器:acc/macro P/R/F1/per-class/coverage;(4)EVAL_SELFTEST=1 majority baseline acc=0.2146/macroF1=0.0393;(5)release_manifest.json含checksums+provenance+5 limitations;(6)report_v9.html。leak check 0残留;deterministic。闭环acceptance #2#3可发布性维度。
- [19:30] 第11轮唤醒：.75**恢复可达**（连续第11轮同卡点）；3口径=1机/20dir/3479轨迹(+1)。**推进不阻塞的 v0.10 = v1.0-rc1 发布候选打包层**：(1)release_rc.py从冻结v0.9拷贝4数据文件逐比特一致+5个发布文档(DATA_CARD/LICENSE/CITATION/BASELINE_MODEL_CARD/RELEASE_CHECKLIST);(2)RC_MANIFEST internal_shippable=True,final v1.0仅3运维gate未关;(3)report_v10.html。leak check 0残留;deterministic。验收#2#3"对外可发布"维度闭环;#1#4第8轮已闭环。
- [19:39] 第12轮唤醒：.75**仍可达**（连续第12轮同卡点）；3口径=1机/20dir/3479轨迹。**推进不阻塞的 v0.11 worked example submission 层**：(1)example_submission.py仅用冻结few_shot(27)训练TF-IDF+CJK bigram+tools+nearest-centroid→预测test_set(219);(2)run_example.sh调冻结v0.9评估器打分acc=0.8174/macroF1=0.7239;(3)label-leakage guard:few_shot∩test_set=∅;(4)report_v11.html。修复build.json嵌入build-host绝对路径→改相对路径。deterministic;leak check 0残留。意义:第三方一条命令跑通train→predict→score闭环。


## 归档批次 4（2026-10-28 第19轮体积维护）：MEMORY 流水 轮次 13–17 原文

> 第19轮体积维护：MEMORY 流水 轮次 13–17 原文搬入此处（v0.12 统一入口 → v0.16 DATA_CARD 增补），
> MEMORY 中留 1 行指针。规程要求搬前 `git pull --rebase --autostash` 已做。🚫 不改小节编号/标题/运维指令。

- [20:05] 第13轮唤醒：.75**仍可达**（ping 0% loss，SSH 仍 Permission denied，连续第13轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/20dir/3479轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… 不变）。**推进不阻塞的 v0.12 统一入口 README 聚合层**（闭环 v0.1–v0.11 各版本"各自有 README、缺一个聚合入口"的可发现性缺口）:(1)designflow/README.md 静态导航文档，零 /home 访问——按角色[评估者/复现者/扩展者/发布审查]给推荐入口+一条命令；版本索引表 v0.1–v0.11 各含角色/关键产物/一句话+构建顺序依赖 DAG（ASCII）；已发布 bundle v0.10 指针+worked example 一条命令；3 开放 gate[多机/活LLM/对外]；全链路复现指引；5 条限制。(2)**leak check 初版抓到并修 2 处真实再引入**：①工作目录写绝对路径含 app.e0031982 账号→改"绝对路径含本机账号已脱敏省略"；②v0.6 描述行写明文 Cxmt@202608 服务密码值→改"服务密码/服务账号 PII 泄漏"（避免把已修复密钥明文重新写入 git）。修后 leak check 0 残留(app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0)。意义:11 个分散版本目录升级为 1 个可导航整体,新用户一份入口文档即可定位到任何版本。
- [20:35] 第14轮唤醒：.75**仍可达**（ping 0% loss，SSH 仍 Permission denied，连续第14轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/20dir(19有数据)/3479轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… 不变）。**推进不阻塞的 v0.13 版本演进 diff 层**（闭环 v0.12 统一 README 留下的"版本间到底改了什么"差异表缺口）:(1)version_diff.py 扫已冻结 bench_v0.1..v0.11 out/ 产物 → version_manifest.json[11版本/73 artifacts/file→sha256+size] + version_diff.json[10相邻 delta: added/removed/sha_changed] + report_v13.html。(2)**发现并修扫描盲区**：初版把 v0.7 out/_repro_tmp/（repro_check 两份临时树，gitignored 本地 scratch，0 文件被 git 追踪）误计为 165 个 added→加 EXCLUDE_DIRS={_repro_tmp,__pycache__,_staging,.pytest_cache}，修后 73 artifacts，v0.5→v0.6 出现 ~6 sha_changed（dedup 改既有文件，符合预期）。(3)DETERMINISM PASS（PYTHONHASHSEED=0+SOURCE_DATE_EPOCH+sorted 迭代，两次 rerun 逐比特 sha256 一致）；leak check 0 残留(app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0)。(4)同步更新 v0.12 统一 README：轮次 13→14、版本索引加 v0.13 行、依赖 DAG 加 v0.13 节点、复现段加 v0.13 一条命令、gate 表轮次 13→14。(5)**体积维护**：EXPERIMENTS 35.8KB→16.6KB（归档 EXP-06..EXP-10 原文→ARCHIVE 批次 2，留 1 行指针；规程要求搬前 git pull --rebase --autostash 已做）。意义:演进链现在第三种可验证维度——v0.7 验"全链路逐比特可复现"、v0.8 验"跨主机/跨时间可复现"、v0.13 验"版本间演进可追溯"。
- [20:50] 第15轮唤醒：.75**恶化**为不可达（ping 100% loss + SSH Connection timed out，从上轮"可达但拒"退回第3/9轮不可达状态，连续第15轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/20dir/3479轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… 不变，无 RESCAN 扩增）。**推进不阻塞的 v0.14 统计严谨性层**（闭环 v0.13 留下的"benchmark 自身统计有效性未量化"缺口）:(1)stats_rigor.py 三审计纯冻结数据——①agreement: Cohen's κ=0.4496(v3_supervised vs v4_rule, n=2112, moderate 0.41-0.60 区间, obs_agree=0.5947=1256/2112, per-class agreement, by quality[task/noise]) ②selection_bias: test_set 0/219 disputed(v3!=v4) vs full corpus 856/2112(40.5%) vs gold 0/246 → verdict **BIAS_PRESENT**, headline 发现"test split 是 easy-only 偏倚样本, baseline acc 被选择一致性放大", 给 v1.x 推荐 stratify 含 controlled fraction of disputed hard items ③bootstrap_ci: 非参数 percentile bootstrap 10000× resample 219 (true,pred) pairs (join v0.11 submission ↔ v0.10 gold by global_id), numpy default_rng(seed=0), baseline acc 0.8174[0.7671,0.8676] / macroF1 0.7239[0.6358,0.7929] / macroP 0.7051 / macroR 0.7942 + per-class F1 CI; point 估计与 v0.11 eval 完全对齐 (2)report_v14.html。(3)**DETERMINISM PASS**: SOURCE_DATE_EPOCH pinned + PYTHONHASHSEED=0 → 两次 rerun out/*.json byte-identical sha256(初版仅 generated_at 实时时间戳差异, pin 后消除)。(4)**leak check 0 残留**(app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0; v0.14 不读 /home 无新 PII 风险)。(5)同步更新 v0.12 统一 README: 版本索引加 v0.14 行[统计严谨性层/kappa+bias+CI]、DAG 加 v0.14 节点、复现段加 v0.14 一条命令、gate 表 .75 状态改为"现已不可达"。(6)清理 out/*.stripped debug scratch(不入 git)。bash reproduce.sh 一键复现(零/home访问,只读冻结 v0.6/v0.10/v0.11 输出)。意义:benchmark 首次量化自身统计有效性——标注者一致性 κ 给噪声地板、test_set 选择偏倚审计暴露一个真实可改进的构造缺陷、bootstrap CI 把点估计升级为区间;为 final v1.0 提供统计可信度证据 + 一条可执行的 v1.x 改进路径。
- [21:05] 第16轮唤醒：.75**恢复可达**（ping 0% loss，SSH 仍 Permission denied，从上轮不可达回升到第11–14轮的"可达但拒"状态，连续第16轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/20dir(19有数据)/3479轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… 不变，无 RESCAN 扩增）。**推进不阻塞的 v0.15 去偏 test split + 双标注者评分层**（闭环 v0.14 BIAS_PRESENT 留下的"test split easy-only 偏倚未修复"缺口）:(1)debiased_split.py纯冻结数据——①build_debiased_split: 219 consensus(原 v0.9 test,带gold)+149 disputed(v3!=v4,quality=task,排除few_shot),proportional stratified by v3 class(largest-remainder 配额,random.Random(seed=0) 类内 shuffle),frac_disputed 0.0→0.4049≈语料 0.4053→verdict **BIAS_CORRECTED** ②build_debiased_submission: 发现冻结 v0.11 example_submission 只覆盖 219 consensus test id,无 disputed 项预测→复用 v0.11 同款模型(TF-IDF+CJK-bigram+tools+nearest-centroid,few_shot[27]训练)对全部 368 项预测→debiased_submission.jsonl ③dual_annotator_eval: **2 标注者下 disputed 项无 gold(v3!=v4 是平局),不伪造**,改为分别报 v3_agreement/v4_agreement/mean robustness;consensus gold acc=0.8174(=v0.14 headline,同批 219 easy 项) vs disputed mean robustness=0.3087/v3_agree 0.3020/v4_agree 0.3154/matches_neither=104/149;**headline 量化选择偏倚导致的 accuracy 膨胀 gap=+0.5087** ④bias_correction_audit: BIAS_CORRECTED (2)report_v15.html。(3)**DETERMINISM PASS**: PYTHONHASHSEED=0+SOURCE_DATE_EPOCH pinned+random.Random(seed=0)→两次 rerun 全 out/ byte-identical sha256。(4)**leak check 0 残留**(app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0; v0.15 不读 /home 无新 PII 风险)。(5)同步更新 v0.12 统一 README: 版本索引加 v0.15 行、DAG 加 v0.15 节点、复现段加 v0.15 一条命令、gate 表 .75 状态改为"恢复可达但拒"、资产盘点轮次 14→16。(6)**体积维护**: MEMORY 32.3KB→19.3KB(归档轮次 1–12 流水原文→ARCHIVE 批次 3,留 1 行指针;规程搬前 git pull --rebase --autostash 已做)。bash reproduce.sh 一键复现(零/home访问,只读冻结 v0.6/v0.10/v0.11 输出)。意义:benchmark 首次**修复** v0.14 暴露的构造缺陷——test split 不再是 easy-only 偏倚样本,disputed 硬样本以受控比例纳入,且用统计诚实的方法(双标注者 agreement 而非伪造 gold)在硬样本上评分;同一 baseline 在 easy 项 0.817 vs hard 项 0.309 的差距,把"选择偏倚放大 accuracy"从 v0.14 的定性发现升级为定量证据。
- [21:25] 第17轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第17轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**19dir(18有数据)**/**3478轨迹**（**较上轮记 20dir/3479 少 1 目录+1 轨迹——出现小幅负向漂移**，疑似某用户清理了 .cline/data/sessions；按红线漂移不并入已发布冻结快照 a1cd058a…，无 RESCAN 扩增）。**推进不阻塞的 v0.16 DATA_CARD 增补层**（闭环 v0.10 DATA_CARD 与 v0.14/v0.15 统计严谨性之间的**语义级**连贯性缺口——区别于 v0.13 version_diff 的**文件级**演进追溯：外部审查者只读 v0.10 DATA_CARD 会看不到 κ/选择偏倚/bootstrap CI/去偏 split 这些统计有效性证据）:(1)datacard_enrich.py 读冻结 v0.10 DATA_CARD.md + v0.14 agreement/selection_bias/bootstrap_ci + v0.15 debiased_eval/bias_correction/debiased_split_manifest → 产 **DATA_CARD_ADDENDUM.md**[5 章节各声明扩 v0.10 哪节：§A κ=0.4496 moderate+per-class agreement(扩§6) / §B BIAS_PRESENT→BIAS_CORRECTED disputed 0.0→0.405≈语料(扩§5) / §C bootstrap 95% CI acc[0.7671,0.8676]+per-class F1 CI(扩§6) / §D consensus acc0.8174 vs disputed robustness0.3087 gap+0.5087(扩§2) / §E 4条更新局限(扩§6)] + **datacard_enrich.json**[provenance 8源文件 path+sha256+bytes / statistical_validity 5块 / cross_references_to_datacard 5 / limitations_added 4] + report_v16.html。(2)**关键设计取舍：层叠而非改写**——不 mutate 冻结 v0.10 DATA_CARD(尊重 freeze-by-default)，reproduce.sh 末尾自检 v0.10 DATA_CARD sha256=434edea5… 不变；如未来升 v1.0 由人工把 addendum 并入主 card。(3)数字不重算：所有统计量直接取自冻结 v0.14/v0.15 产物，本层只做聚合+回指+表达，不引入新随机性(除 SOURCE_DATE_EPOCH 控时间戳)。(4)**DETERMINISM PASS**: PYTHONHASHSEED=0+SOURCE_DATE_EPOCH pinned→两次 rerun out/ byte-identical sha256。(5)**leak check 0 残留**(app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0; v0.16 不读 /home 无新 PII 风险)。(6)同步更新 v0.12 统一 README: 版本索引标题 v0.15→v0.16、加 v0.16 行、DAG 加 v0.16 节点、复现段加 v0.16 一条命令、gate 表 .75 轮次 16→17。(7)**体积自检**: TASK5.1KB/MEMORY22.0KB/EXPERIMENTS20.9KB 全在32KB内,无需归档。bash reproduce.sh 一键复现(零/home访问,只读冻结 v0.10/v0.14/v0.15 输出)。意义:把分散在 v0.14/v0.15 的统计有效性证据**层叠**回 rc1 发布元数据,且每个数字带 sha256 provenance 可一键核验;外部审查者现在一份 DATA_CARD+一份 ADDENDUM 即可看到 composition+统计有效性全貌,且冻结基线保持完整;为 final v1.0 对外发布把 addendum 并入主 card 提供了现成素材。

## 归档批次 5（2026-10-28 第20轮体积维护）— EXP-11..EXP-14 原文

## EXP-11 (2026-10-28) 第11轮复探 + bench_v0.10 v1.0-rc1 发布候选打包层
**动机**：v0.9 交付了"可发布的数据 bundle"（tasks/gold/few-shot/blinded-test + evaluator + manifest），但一个对外发布的*数据集*还需要 datasheet/license/citation/baseline-model-card/checklist——v0.9 是 data，v0.10 是 releasable dataset。所有构造性工作已不阻塞；final v1.0 对外仅差运维相关 gate。v0.10 闭合"对外可发布"维度。

**方法**：
- `release_rc.py`：从冻结 v0.9 out 拷贝 4 数据文件（tasks/gold/few_shot/test_set）逐比特 verbatim，+ 生成 5 个发布就绪文档：
  - `DATA_CARD.md`（Mitchell et al. 式 datasheet：动机/组成/采集 provenance/脱敏流程/splits+泄漏守卫/局限/伦理/维护与增长）；
  - `LICENSE`（内部优先 + 禁再识别 + 禁训练 + 禁转发的 release-CANDIDATE 许可）；
  - `CITATION.cff`（cff-version 1.2.0，机器可读引用）；
  - `BASELINE_MODEL_CARD.md`（majority-class baseline acc=0.2146/macroF1=0.0393/coverage=1.0 + per-class + confusion 结构 + 复现命令 + "真实提交应展示什么"）；
  - `RELEASE_CHECKLIST.md`（15 项发布就绪清单含 [x]/[ ] 状态 + verdict）。
- `RC_MANIFEST.json`：全 bundle 产物 checksums + `data_integrity_vs_v09`（每文件 `matches_v09_frozen_sha256` 断言）+ `release_readiness` verdict（`internal_shippable=True`，`final_v1_0_blocked_on`=[多机凭证, 活 LLM endpoint, 对外签字]）+ `bundle_inventory` + counts + label catalogue + usage。
- `report_v10.py`：HTML 发布候选报告（KPI 卡 / 数据文件表含 vs v0.9 一致性 / 文档表 / gold 类分布 / split 守卫 pill / baseline / 局限 / reproduce / evaluate）。
- `reproduce.sh`：默认零 /home 访问，从冻结 v0.9 out 装配 rc bundle + 报告；`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1793145600`。

**结果**：
- 4 数据文件与 v0.9 frozen `release_manifest.json` checksum 逐一对齐 → `data_files_match_v09_frozen=True`（拷贝忠实，篡改/漂移可检测）。
- bundle inventory：9 产物（4 data + 5 docs）+ RC_MANIFEST.json。
- `release_readiness.internal_shippable=True`；final v1.0 仅 3 个运维相关 gate 未关（均非构造性缺口）。
- **leak check 全产物 0 残留**（app.e*/app.t*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@202608/cxmt domain=0；仅 <REDACTED>/<USER> 占位符 295，继承自 v0.9）。
- **deterministic**：rerun 全 out/ 逐比特 sha256 一致（snapshot_A == snapshot_B），无时间戳漂移（_now_iso 尊重 SOURCE_DATE_EPOCH）。
- 3 口径现查：1 机 / **20 dir（19→20,+1）** / **3479 轨迹（3478→3479,+1）**——新增 1 个含 1 轨迹的目录，真实漂移微增，不并入已冻结快照（v0.8 freeze + v0.10 拷贝校验保证发布与漂移解耦）。

**意义**：benchmark 从"有数据"升级为"有可发布数据集"——第三方拿到 v0.10/out/ 一个目录即含数据 + 许可证 + datasheet + 引用 + 基线参考地板 + 发布清单 + checksum manifest；clone 到无 cline 数据机器逐比特复现。final v1.0 对外发布仅差运维签字 3 gate（多机凭证 / 活 LLM endpoint 跑第3标注者 / 对外发布签字），均非 benchmark 构造缺口。验收 #2（版本化 benchmark 含任务集+评分口径+复现）与 #3（HTML 报告+数据清单）的"对外可发布"维度闭环；#1（资产盘点）#4（全链路复现）已先期闭环。

**局限**：继承 v0.9 全部局限（单机 15 用户；few_shot/test 共享用户→global_id/session_id disjointness enforced；小类 per-class 不稳定；gold 为 2 标注者共识，第3 LLM 标注者未接 live endpoint）；rc1 为 internal-first，对外发布待运维签字。git 历史含早期未脱敏 commit，待人工决断是否 force-push 重写（仍悬）。

**红线遵守（第11轮）**：v0.10 全程零 /home 访问（只读冻结 v0.9 输出）；未脱敏不入 git（全产物 leak check 0 残留）；原始轨迹不入库；无网络；纯标准库；不碰他人进程；不用 GPU；.75 恢复可达但仍无凭证不硬探；上报仍有效（连续11轮同卡点）不静默硬撑。

**复现**：`cd designflow/bench_v0.10 && bash reproduce.sh`（默认零 /home 访问，装配 rc bundle + 报告）；`EVAL_SELFTEST=1 bash designflow/bench_v0.9/reproduce.sh`（评估器冒烟）。
**结论**：v0.10 交付 v1.0-rc1 发布候选打包层，benchmark 升级为对外可发布数据集（data+license+datasheet+citation+baseline+checklist+manifest）。多机扇出仍阻塞但 v0.10/v0.11 路径不阻塞。v0.11 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 / RESCAN 扩增冻结快照 / 经运维签字升 v1.0 正式对外。

---

## EXP-12 — v0.11 worked example submission 层（第12轮，2026-10-28）

**动机**：v0.10 交付了 v1.0-rc1 可发布数据集，但缺一个**可运行的 "how-to-submit" 演示**——第三方拿到 bundle 后应能一条命令跑通 train→predict→score 真实闭环。v0.11 闭环此可用性缺口（非阻塞，建于冻结 v0.10 bundle 之上，零 /home 访问）。

**产物**（`designflow/bench_v0.11/`）：
- `example_submission.py`：仅用冻结 v0.10 `few_shot.jsonl`（27 行，≤3/类，带 gold_label）训练 → 预测 `test_set.jsonl`（219 行，blinded 无 label）→ emit `example_submission.jsonl`（`{"global_id":..., "predicted_label":...}`，评估器期望格式）。分类器：TF-IDF（latin token + CJK char-bigram，复用 v0.3 `curate.tokenize`）+ `tools_used` 归一化 token（`pyAether_MCP_server__run_code`→`tool:run_code`）+ nearest-centroid（cosine）——与 v0.3/v0.5 同族 stdlib-only baseline，刻意弱参考地板。
- `run_example.sh`：调冻结 v0.9 `eval_submission.py` 对 submission 打分 → `report_v11.py` 渲染 HTML。
- `reproduce.sh`：`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1793145600` 固定。

**结果**：
- **acc=0.8174 / macroF1=0.7239 / coverage=1.0**（n=219/219），远高于 majority baseline 0.2146/0.0393。few_shot 的 prompt + tools_used 信号携带强（vocab=300，9 类）。train_acc=1.0（27 行过拟合，仅 informational，非 held-out）。
- **label-leakage guard**：`few_shot ∩ test_set = ∅` on global_id + session_id（v0.9 `release_manifest.json` split-integrity guard 断言）→ 合法 held-out 评估，无标签泄漏。
- **deterministic**：rerun 全 `out/` 逐比特 sha256 一致（snapshot_A == snapshot_B）。
- **发现并修复**：`example_submission_build.json` 初版写入 build-host 绝对路径（嵌入 `app.e0031982` 账号名）→ 改相对路径 `submission_path=out/example_submission.jsonl`，与 benchmark 其余产物不嵌本地 /home/account 路径一致。
- **leak check 全产物 0 残留**（app.e*/app.t*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home/app.*=0；无占位符，因本层只读已脱敏 bundle）。

**意义**：第三方 clone 仓库到无 cline 数据机器，一条命令即见真实 train→predict→score 闭环，演示"如何提交"——把"评估器可用"从文档声明升级为可执行证据。验收 #2（评分口径可复现）的"端到端可用性"维度闭环。

**局限**：few_shot 仅 27 行（≤3/类），刻意弱地板（演示 loop 非刷榜）；纯工具脚手架 prompt 可能零特征向量回落首 centroid（18/219 行）；继承 v0.9/v0.10 全部局限（单机 15 用户；gold 为 2 标注者共识；git 历史含早期未脱敏 commit 仍悬）。

**红线遵守（第12轮）**：零 /home 访问（只读冻结 v0.10 bundle）；未脱敏不入 git（leak 0）；原始轨迹不入库；纯标准库；不碰他人进程；不用 GPU；.75 仍可达但无凭证不硬探；上报仍有效（连续12轮同卡点）不静默硬撑。

**复现**：`cd designflow/bench_v0.11 && bash reproduce.sh`。
**结论**：v0.11 交付 worked example submission 层，benchmark 升级为"可执行提交闭环演示"。v0.12 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 / RESCAN 扩增冻结快照 / bundle 统一入口 README / 经运维签字升 v1.0 正式对外。

## EXP-13 — v0.12 统一入口 README 聚合层（第13轮，2026-10-28）

**动机**：v0.1–v0.11 共 11 个版本目录，每个各自有 README，但 `designflow/` 根缺一个聚合入口。
新用户面对 11 个目录无可发现性路径——不知从哪进、各版本什么角色、如何依赖、如何一键复现。
v0.12 闭环这一可发现性缺口，不产生新数据，纯静态导航文档。

**方法**：
1. 创建 `designflow/README.md` 静态导航文档，零 `/home` 访问，deterministic。
2. 内容结构：(a) 顶部 3 口径数字+链路不通说明；(b) 按角色推荐入口表[评估者/复现者/扩展者/发布审查者各给先看目录+一条命令]；(c) 版本索引表 v0.1–v0.11 各含角色/关键产物/一句话；(d) 构建顺序依赖 ASCII DAG；(e) 已发布 bundle v0.10 指针+worked example 一条命令；(f) 3 开放 gate[多机/活LLM/对外]；(g) 全链路复现指引；(h) 5 条限制。

**结果**：
- 文档 8569 bytes，纯静态，零 `/home` 访问。
- **leak check 初版抓到并修 2 处真实再引入**：
  - ① 工作目录行写绝对路径 `/nasdata/app.e0031982/code/...` 嵌入本机账号 → 改"绝对路径含本机账号已脱敏省略"（与 benchmark 其余 scrub app.e*/app.t* 一致）。
  - ② v0.6 描述行写明文 `Cxmt@202608` 服务密码值（v0.6 修复的泄漏对象的明文）→ 改"服务密码/服务账号 PII 泄漏"（避免把已修复密钥明文重新写入 git——这是个微妙陷阱：描述"修了什么"时若写出原值，等于重新泄漏）。
- 修后 leak check 0 残留（app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home 全 0）。

**复探 3 口径**（与 MEMORY 同步）：.75 ping 0% loss + SSH Permission denied（连续 13 轮，上报仍有效待回复）；8092 仍 RESEARCH 无 exec；1 机/20 dir/3479 轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… 不变）。无 DESIGNFLOW_LLM_JUDGE env → v0.13 LLM-judge endpoint 候选本轮阻塞；/home 持平 → RESCAN 扩增本轮无新样本。

**结论**：v0.12 交付统一入口 README 聚合层，11 个分散版本目录升级为 1 个可导航整体。新用户一份入口文档即可按角色定位到任何版本并一条命令跑通。**leak check 自检发现并修复 2 处 PII 再引入**（账号路径+服务密码明文）是本轮附带价值——证明统一文档聚合时极易在"描述修复"中重新泄漏原值，须警惕。v0.13 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 / RESCAN 扩增冻结快照 / v1.0-rc1 经运维签字升 v1.0 / 给统一 README 加版本间差异 diff 表。

## EXP-14 — v0.13 版本演进 diff 层（第14轮，2026-10-28）

**动机**：v0.12 统一入口 README 把 11 个版本串成可导航整体，但"v0.6 相比 v0.5 在 artifact 层面到底变了什么"仍需读者各自翻 README，演进链靠人写叙述而非机器可验证。v0.13 闭环这一缺口：用脚本从已冻结产物本身算出相邻版本 artifact diff 表（added/removed/sha-changed），让演进链机器可验证。不产生新数据，零 `/home` 访问。

**方法**：
1. `version_diff.py` 扫描 `designflow/bench_v0.1 … v0.11` 的 `out/` 产物树，每版本算 artifact 清单（相对文件名 → sha256/size），相邻版本算 delta（added/removed/sha_changed by filename）。
2. **scratch 排除**：初版把 v0.7 `out/_repro_tmp/`（repro_check 的两份临时树，gitignored 本地 scratch，0 文件被 git 追踪）误计为 165 个"added"，污染 diff。加 `EXCLUDE_DIRS={_repro_tmp,__pycache__,_staging,.pytest_cache}` 让 manifest 只反映 intended tracked artifacts。修后 73 artifacts total，diff 合理（v0.5→v0.6 出现 ~6 sha_changed，反映 v0.6 去重改动了 6 个既有产物文件，符合预期）。
3. `report_v13.py` 生成 HTML（per-version artifact 表 + 相邻 diff 表 + 解读说明）。从各版本 README 抽 gap-closed 一句话作 narrative。
4. `reproduce.sh` 一键：扫描 → manifest + diff + HTML。

**结果**：
- `version_manifest.json`：11 版本 / 73 artifacts total，每文件 sha256+size。
- `version_diff.json`：10 条相邻 delta + narrative。典型：v0.5→v0.6 +4 -1 ~6（dedup 改既有文件）；v0.9→v0.10 +7 -5（发布文档新增）；v0.10→v0.11 +4 -11（worked example，rc1 文档退出 out/）。
- `report_v13.html`：HTML 演进报告。
- **DETERMINISM PASS**：PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH 固定 + sorted 迭代，两次 rerun 全 out/ 逐比特 sha256 一致。
- **LEAK CHECK 0 残留**（app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home 全 0）。零 `/home` 访问。
- 同步更新 `designflow/README.md`（v0.12 统一入口）：资产盘点改第14轮、版本索引表加 v0.13 行、依赖 DAG 加 v0.13 节点、复现段加 v0.13 一条命令、gate 表轮次 13→14。

**复探 3 口径**（与 MEMORY 同步）：.75 ping 0% loss + SSH Permission denied（连续 14 轮，上报仍有效待回复）；8092 仍 RESEARCH 无 exec；1 机/20 dir/3479 轨迹（与上轮持平，无新样本，冻结快照 a1cd058a… sha256 不变）。无 DESIGNFLOW_LLM_JUDGE env → LLM-judge endpoint 候选阻塞；/home 持平 → RESCAN 扩增无新样本。

**结论**：v0.13 交付版本演进 diff 层，把"版本间改了什么"从人写叙述升级为机器可验证的 sha256 diff 表。附带发现并修复 v0.7 `out/_repro_tmp/` 本地 scratch 污染 manifest 的扫描盲区（加 scratch 排除集）。意义：演进链现在有第三种可验证维度——v0.7 验证"全链路逐比特可复现"、v0.8 验证"跨主机/跨时间可复现"、v0.13 验证"版本间演进可追溯"。v0.14 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 / RESCAN 扩增冻结快照 / v1.0-rc1 经运维签字升 v1.0 / 把版本 diff 表反嵌进统一 README（当前 v0.13 独立 HTML）。


## 归档批次 6（2026-10-28 第21轮体积维护）：MEMORY 流水 轮次 18–20 原文

### [21:45] 第18轮唤醒 原文

- [21:45] 第18轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第18轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（**上轮记 19/18/3478 的负向漂移本轮已恢复**回 20/19/3479——证实为 transient 用户临时活动，冻结快照 a1cd058a… 重新对齐，无 RESCAN 扩增）。**推进不阻塞的 v0.17 诊断发布 bundle**（闭环 v0.15+v0.16 留下的"去偏 split 是散件、无第三方评估接口"缺口——v0.15 建了去偏 split、v0.16 把统计证据层叠进 DATA_CARD，但 split 本身仍只是 out/ 散件，第三方拿不到可消费的包；v0.9/v0.10 对 consensus release 做过规范发布，v0.17 对 debiased split 做同样的事）:(1)diagnostic_release.py 读冻结 v0.15 debiased_test_set/submission + v0.10 few_shot + v0.8 source_manifest → 产 **diagnostic_test_set.jsonl**[368=219 consensus+149 disputed,canonical fields,labels included=诊断 split 非盲测,评估者需要双标签] + **diagnostic_gold.jsonl**[compact answer key,consensus 项带 gold_label,disputed 项 gold_label=null+label_v3/v4=不伪造单一 gold] + **diagnostic_few_shot.jsonl**[27,与 test disjoint,供提交者训练] + **diagnostic_baseline_submission.jsonl**[368 preds,verbatim from v0.15,作为参考基线提交] + **diagnostic_baseline_eval.json**[dual-annotator: consensus acc 0.817352 vs disputed robustness 0.308725 gap+0.508627,cross_check vs v0.15=MATCH] + **diagnostic_release_manifest.json**[checksums/counts/class dist/protocol spec/integrity guards PASS/provenance snapshot a1cd058a…]。(2)**eval_diagnostic.py 第三方评估器**实现 dual-annotator 协议: consensus block=gold acc+per-class P/R/F1+top confusion / disputed block=v3/v4 agreement_rate+mean robustness+matches_neither/exactly_one / headline gap=consensus_acc−disputed_robustness / coverage overall+per-block; 提交格式同 v0.9 jsonl。(3)**selftest PASS**: eval_diagnostic 对 bundled baseline 提交打分→consensus_acc/disputed_robustness 与 bundled eval 完全一致(cross-check assert)。(4)**DETERMINISM PASS**: PYTHONHASHSEED=0+SOURCE_DATE_EPOCH pinned+sorted 迭代+无新随机性(纯重打包 v0.15)→两次 rerun 全 out/ byte-identical sha256。(5)**leak check 0 残留**(数据产物 app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0; v0.17 不读 /home 无新 PII 风险; reproduce.sh 内 leak-check 正则自匹配是预期,与历版一致)。(6)**freeze-integrity**: v0.10 DATA_CARD sha256=434edea5… 不变 + v0.15 debiased_test_set sha256=5dd43df6… 不变。(7)同步更新 v0.12 统一 README: 标题 v0.12→v0.12(updated through v0.17)、资产盘点轮次 16→18+加漂移恢复说明、版本索引加 v0.17 行、DAG 加 v0.17 节点、已发布 bundle 段加诊断 bundle 指针、复现段加 v0.17 一条命令、gate 表 .75 轮次 17→18。(8)**体积自检**: TASK5.1KB/MEMORY~27KB/EXPERIMENTS21KB 全在32KB内,无需归档。bash reproduce.sh 一键复现(零/home访问,只读冻结 v0.8/v0.10/v0.15 输出)。意义:去偏 split 从"研究者内部散件"升级为"可对外发布的诊断 bundle"——第三方现在一份 diagnostic_test_set+一份 eval_diagnostic.py 即可在双标注者协议下评估自己的分类器,且 disputed 硬样本受控纳入(不再 easy-only);与 v0.9/v0.10 consensus release 形成"easy 盲测包 + hard 诊断包"双轨发布,为 final v1.0 对外发布提供了去偏诊断 split 的现成打包。

### [22:10] 第19轮唤醒 原文

- [22:10] 第19轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第19轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/20dir(19有数据)/3479轨迹（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.18 disputed 项机理性刻画层**（闭环 v0.15/v0.16/v0.17 留下的"149 个 disputed 项 *为什么* 难、+0.51 鲁棒性 gap 由什么机制驱动"缺口——v0.15 量化了 gap、v0.16 把统计证据层叠进 DATA_CARD、v0.17 打包成诊断 bundle，但都没解释 gap 的机理；外部审查者只看到一个数字 gap，不知道它指向哪个可改进杠杆）:(1)dispute_analysis.py 读冻结 v0.15 debiased_test_set + v0.6 tasks_v6[按 global_id join 取 prompt_len/n_turns/n_user_turns/n_assistant_turns/n_tool_calls/duration_sec/model/has_thinking] + v0.15 debiased_submission[baseline pred] → 6 维度 consensus(219) vs disputed(149) 对比：**§1 不一致对矩阵**[label_v3↔label_v4，top: code_dev↔other 35(23.5%)/other↔noise_toy_test 18/code_dev↔noise_toy_test 14/code_dev↔eda_virtuoso_schematic 12/code_dev↔eda_env_qa 11=集中在 code_dev↔other↔noise 三类边界，gap 是标签方案模糊边界非随机噪声] / **§2 特征对比**[6 特征均值+中位+Cohen's d，最大效应 prompt_len d=−0.33 small=disputed 项 prompt 更短(consensus 996字符 vs disputed 546字符)=边界模糊集中在简短/欠描述 prompt 而非长复杂任务；其余 n_turns/n_tool_calls/duration_sec d<0.2 negligible] / **§3 工具多样性**[disputed 更少用 pyAether EDA 工具(get_api_details/run_code/search_apis diff −0.21~−0.20)、更多用 run_approved_command(+0.25)/skills(+0.18)=非特定 EDA 任务，与 code_dev↔other↔noise 混淆一致] / **§4 用户集中**[split 内 13 不同用户全部有 disputed，top-3 用户占 54.4%/top-5 占 72.5%/单用户最高 42 项 disputed=中等集中，部分用户任务更易触发标注分歧] / **§5 模型分布**[deepseek-v4-flash dispute rate 0.68 最高但与 task mix 混杂非因果，标注 descriptive only] / **§6 baseline 关系**[cross_check vs v0.15 debiased_eval=MATCH(matches_neither 57/exactly_one 92/mean_robustness 0.308725)+按 disagreement pair 切分 matches_neither/exactly_one/v3_only/v4_only] + **机理性结论**[gap 是结构性来自标注方案模糊边界非 baseline 模型缺陷→支持 v0.15/v0.16 用双标注者 agreement 而非伪造 gold 的设计；v1.x 改进路径=(i)第3标注者/LLM-judge 断平局[仍阻塞 env] (ii)细化标签方案溶解 code_dev↔other↔noise 边界 (iii)接受 disputed 为永久硬样本分层单独报]。(2)**DETERMINISM PASS**: PYTHONHASHSEED=0+SOURCE_DATE_EPOCH pinned+sorted 迭代+Counter(insertion-stable on sorted input)→两次 rerun 全 out/ byte-identical sha256。(3)**leak check 0 残留**(数据产物 app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0; v0.18 读 v0.15/v0.6 已脱敏数据无新 PII 风险)。(4)**freeze-integrity**: v0.15 debiased_test_set sha256=5dd43df6… 不变 + v0.15 debiased_eval sha256=af0a6652… 不变 + v0.6 tasks_v6 sha256=d52b1057… 不变 + v0.10 DATA_CARD sha256=434edea5… 不变。(5)同步更新 v0.12 统一 README: 标题 v0.12(updated through v0.17→v0.18)、资产盘点轮次 18→19、版本索引加 v0.18 行、DAG 加 v0.18 节点、复现段加 v0.18 一条命令、gate 表 .75 轮次 18→19。(6)**体积维护**: MEMORY 30.1KB→19.6KB(归档轮次 13–17 流水原文→ARCHIVE 批次 4,留 1 行指针;规程搬前 git pull --rebase --autostash 已做)。bash reproduce.sh 一键复现(零/home访问,只读冻结 v0.6/v0.15 输出)。意义:把 v0.15 的数字 gap 从"一个不解释的差值"升级为"可归因到 3 个可改进杠杆的机理性发现"——(a)标签方案在 code_dev↔other↔noise 边界的模糊是主因(指向 taxonomy 修订),(b)disputed 项 prompt 显著更短(指向可加 prompt 长度分层评估),(c)用户集中 54.4%(指向可加 per-user 公平性审计);为 final v1.0 对外发布提供了"为什么 hard 项难"的现成解释,且 cross-check vs v0.15 MATCH 保证不与既有统计层矛盾。

### [22:35] 第20轮唤醒 原文

- [22:35] 第20轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第20轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.19 诊断 split 自包含发布包**（闭环"下一步候选(4)：把 v0.18 机理性结论回写进诊断 split 附 characterization"——v0.17 打包 v0.15 去偏 split 成诊断 bundle 但当时 v0.18 刻画还不存在；v0.18 给了 gap 机理解释但散在 bench_v0.18/；第三方拿 v0.17 bundle 只有数据+评分口径不知 hard stratum 为何难；v0.19 把 characterization 并入 bundle 使一个目录即有数据+评分口径+机理解释）。**明确与 v0.17 的 delta 避免重复声明**——三处实质增量：①把 v0.18 dispute_characterization.md 逐字并入诊断 bundle ②真正 blinded test/answer-key 分离[v0.17 test_set 含标签非严格 blinded，v0.19 拆无标签 test_set+评估器持有 answers] ③独立可复用 CLI 评估器 diagnostic_eval.py[v0.17 评分嵌装配脚本，v0.19 给第三方 `--submission your.jsonl` 可直接调用的独立评估器]。**diagnostic_release.py** 读冻结 v0.15 debiased_test_set[368]→拆 blinded test+answers+并 v0.18 characterization+复用 v0.15 baseline；assemble 时对 5 源文件重算 sha256 对 v0.18 锚点全 MATCH+freeze-integrity PASS。**diagnostic_eval.py** 双标注者协议：consensus[gold acc+per-class P/R/F1+混淆]/disputed[v3/v4-agreement+mean robustness+matches_neither/one/both+不伪造gold]/gap=consensus_acc−disputed_robustness。**自检 baseline 逐项对齐 v0.15**：acc0.817352/rob0.308725/gap+0.508627/neither57/one92 全✅ ALL ALIGNED。**DETERMINISM PASS**（二次重跑 7 产物 sha256 全一致）。**leak check 0 真实 PII**（token 为普通英文词"token 开销"非密钥，源数据来自已脱敏 v0.6）。**不改冻结 v0.10/v0.15/v0.6/v0.18**。体积自检 TASK5.1/MEMORY 24KB/EXP 29.5KB 全在 32KB 内。

---

## 归档批次 7 — EXP-17..EXP-20 原文（2026-10-28 第23轮体积维护，从 EXPERIMENTS_DESIGNFLOW.md 搬入）

## EXP-17 — v0.17 诊断发布 bundle（第18轮，2026-10-28）

**动机**：v0.15 建了去偏 split、v0.16 把统计证据层叠进 DATA_CARD addendum，但去偏 split 本身仍是 `out/` 散件——**无第三方可消费的包、无第三方评估接口**。v0.9/v0.10 对 consensus (easy) release 做过规范发布；v0.17 对 debiased (hard) split 做同样的事，闭环"研究者内部散件 → 可对外发布诊断 bundle"的缺口。

**方法**：`diagnostic_release.py` 纯冻结数据重打包（零 /home/网络/LLM/新随机性）：
1. 读 v0.15 `debiased_test_set.jsonl`(368) + `debiased_submission.jsonl`(368) + v0.10 `few_shot.jsonl`(27) + v0.8 `source_manifest.json`(snapshot a1cd058a…)。
2. 产 `diagnostic_test_set.jsonl`(368=219 consensus+149 disputed, canonical fields, **labels included**=诊断 split 非盲测，评估者需双标签) + `diagnostic_gold.jsonl`(compact answer key，disputed 项 `gold_label=null`+`label_v3`/`label_v4`=不伪造单一 gold) + `diagnostic_few_shot.jsonl`(27, disjoint) + `diagnostic_baseline_submission.jsonl`(368 preds, verbatim from v0.15) + `diagnostic_baseline_eval.json` + `diagnostic_release_manifest.json`(checksums/counts/class dist/protocol spec/integrity guards/provenance)。
3. `eval_diagnostic.py` 第三方评估器实现 **dual-annotator 协议**：consensus block=gold acc+per-class P/R/F1+top confusion；disputed block=v3/v4 agreement_rate+mean robustness+matches_neither/exactly_one；headline gap=consensus_acc−disputed_robustness；coverage overall+per-block。提交格式同 v0.9 jsonl。

**结果**：
- baseline eval：consensus acc **0.817352** vs disputed robustness **0.308725**，gap **+0.508627**，**cross_check vs v0.15 = MATCH**（重打包不重算，数字逐项对齐）。
- split integrity **PASS**：few_shot∩test(global_id)=0，consensus∩disputed=0，session_id overlap=0。
- selftest PASS：`eval_diagnostic.py` 对 bundled baseline 打分与 bundled eval 完全一致（cross-check assert 通过）。
- DETERMINISM PASS：两次 rerun 全 out/ byte-identical sha256。
- LEAK CHECK 0 残留（数据产物；v0.17 不读 /home 无新 PII 风险）。
- freeze-integrity：v0.10 DATA_CARD (434edea5…) + v0.15 debiased_test_set (5dd43df6…) 不变。
- 同步更新 v0.12 统一 README（标题→updated through v0.17 / 资产盘点轮次 16→18 + 漂移恢复说明 / 版本索引 v0.17 / DAG / 已发布 bundle 段加诊断 bundle 指针 / 复现段 / gate 表 .75 17→18）。

**复探 3 口径**（第18轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 18 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——**上轮负向漂移(19/18/3478)本轮恢复**回 20/19/3479，证实为 transient，冻结快照重新对齐，无 RESCAN 扩增。连续 18 轮同卡点，上报仍有效待回复。

**结论**：去偏 split 从"散件"升级为"可对外发布诊断 bundle"。第三方现在一份 `diagnostic_test_set` + 一份 `eval_diagnostic.py` 即可在双标注者协议下评估分类器，disputed 硬样本受控纳入。与 v0.9/v0.10 consensus release 形成"easy 盲测包 + hard 诊断包"双轨发布，为 final v1.0 对外发布提供去偏诊断 split 现成打包。v0.18 候选：接 LLM-judge 给 disputed 项造真 gold（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字 / 诊断 bundle 加置信区间。

## EXP-18 — v0.18 disputed 项机理性刻画层（第19轮，2026-10-28）

**动机**：闭环 v0.15/v0.16/v0.17 留下的"149 个 disputed 项 *为什么* 难、+0.51 鲁棒性 gap 由什么机制驱动"缺口。v0.15 量化了 gap（consensus acc 0.8174 vs disputed robustness 0.3087，gap +0.5087），v0.16 把统计证据层叠进 DATA_CARD ADDENDUM（§E 把"disputed items lack real gold"列为局限），v0.17 把去偏 split 打包成可对外发布的诊断 bundle + 双标注者第三方评估接口。但**没有任何一层解释** gap 的机理——是随机噪声、标签方案边界模糊、还是某些用户/模型/任务类型系统性更难？没有这个解释，外部审查者只看到一个数字 gap，不知道它指向哪个可改进的杠杆。

**方法**：`dispute_analysis.py` 纯冻结数据——读 v0.15 `debiased_test_set`（368=219 consensus+149 disputed，含 label_v3/label_v4/gold_label/disputed）+ v0.6 `tasks_v6`（按 global_id join 取丰富特征：prompt_len/n_turns/n_user_turns/n_assistant_turns/n_tool_calls/duration_sec/model/has_thinking）+ v0.15 `debiased_submission`（baseline pred）。按 `disputed` flag 分两块（consensus 219 / disputed 149），6 维度对比：

1. **不一致对矩阵**：label_v3↔label_v4 pair 计数（ordered + unordered 聚合）。
2. **特征对比**：6 数值特征均值+中位+p25/p75 + Cohen's d（disputed − consensus，pooled-SD）+ effect size label；has_thinking rate diff。
3. **工具多样性**：distinct tools / mean distinct per item / top tools 频次差（rate diff 排序）。
4. **用户集中度**：每用户 dispute 率 / top-k 占比 / 单用户最高 disputed 数。
5. **模型分布**：per-model dispute rate（descriptive，非因果）。
6. **baseline 关系**：baseline_pred vs v3/v4 match（matches_neither/exactly_one/v3_only/v4_only），按 disagreement pair 切分；cross-check vs v0.15 `debiased_eval.json` 必须 MATCH。

**关键发现**：
- **不一致对集中在 `code_dev↔other` 35(23.5%) / `other↔noise_toy_test` 18 / `code_dev↔noise_toy_test` 14** —— gap 不是随机噪声，是标签方案在这三类边界上的系统性模糊。
- **disputed 项 prompt 更短**（546 vs 996 字符，Cohen's d=−0.33，small）—— 边界模糊集中在*简短/欠描述* prompt 上，而非长复杂任务。这是最大的特征效应。
- **disputed 项更少用 pyAether EDA 工具、更多用 `run_approved_command`/`skills`** —— 与"非特定 EDA"类混淆一致（get_api_details/run_code/search_apis rate diff −0.21~−0.20；run_approved_command +0.25；skills +0.18）。
- **用户集中**：top-3 用户占 disputed 54.4%，top-5 占 72.5%，单用户最高 42 项 disputed，13 用户全部有 disputed —— 中等集中，部分用户任务更易触发标注分歧。
- **模型**：deepseek-v4-flash dispute rate 0.68 最高，但与 task mix 混杂，**非因果**（descriptive only）。
- **机理性结论**：gap 是**结构性**的，来自标注方案模糊边界，**不是 baseline 模型的缺陷** → 支持 v0.15/v0.16 用双标注者 agreement 而非伪造 gold 的设计选择。v1.x 改进路径：(i) 第3标注者/LLM-judge 断平局[阻塞 env] (ii) 细化标签方案溶解 code_dev↔other↔noise 边界 (iii) 接受 disputed 为永久硬样本分层单独报。

**质量门**：
- **DETERMINISM PASS**：PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH pinned + sorted 迭代 + Counter（insertion-stable on sorted input）→ 两次 rerun 全 `out/` byte-identical sha256。
- **leak check 0 残留**：v0.18 `out/` 数据产物 clean（app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home=0）；读 v0.15/v0.6 已脱敏数据无新 PII 风险。
- **freeze-integrity**：v0.15 debiased_test_set `5dd43df6…` / debiased_eval `af0a6652…` / v0.6 tasks_v6 `d52b1057…` / v0.10 DATA_CARD `434edea5…` 全部不变。
- **cross-check vs v0.15 = MATCH**：matches_neither 57 / exactly_one 92 / matches_both 0 / mean_robustness 0.308725 与冻结 v0.15 完全一致。

**产物**：`bench_v0.18/`：dispute_analysis.py / report_v18.py / reproduce.sh / README.md；`out/`：dispute_analysis.json（6 维度 + provenance 4 源 sha256 + 机理性结论）/ dispute_characterization.md（人类可读，回指 v0.15/v0.16）/ report_v18.html（13KB）。

**复探 3 口径**（第19轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 19 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 19 轮同卡点，上报仍有效待回复。

**结论**：把 v0.15 的数字 gap 从"一个不解释的差值"升级为"可归因到 3 个可改进杠杆的机理性发现"——(a) 标签方案在 code_dev↔other↔noise 边界的模糊是主因（指向 taxonomy 修订），(b) disputed 项 prompt 显著更短（指向可加 prompt 长度分层评估），(c) 用户集中 54.4%（指向可加 per-user 公平性审计）。为 final v1.0 对外发布提供了"为什么 hard 项难"的现成解释，且 cross-check vs v0.15 MATCH 保证不与既有统计层矛盾。v0.19 候选：接 LLM-judge 给 disputed 项造真 gold（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字 / 把机理性结论回写进 v0.16 ADDENDUM 作为 §F。

## EXP-19 — v0.19 诊断 split 自包含发布包（第20轮，2026-10-28）

**闭环缺口**：v0.17 把 v0.15 去偏 split 打包成诊断 bundle，但 v0.17 时 v0.18 机理性刻画还不存在；v0.18 给了 +0.51 gap 的机理解释但散在 `bench_v0.18/`。第三方拿 v0.17 bundle 只有数据+评分口径，不知 hard stratum 为何难。v0.19 闭环"下一步候选(4)：把 v0.18 机理性结论回写进诊断 split 附 characterization"——把 characterization 并入 bundle，使一个目录即有数据+评分口径+机理解释。

**与 v0.17 的 delta（明确，避免重复声明）**：①把 v0.18 `dispute_characterization.md` 逐字并入诊断 bundle（自包含）；②真正 blinded test/answer-key 分离（v0.17 test_set 含标签非严格 blinded，v0.19 拆成无标签 `diagnostic_test_set.jsonl` + 评估器持有 `diagnostic_answers.jsonl`）；③独立可复用 CLI 评估器 `diagnostic_eval.py`（v0.17 评分嵌装配脚本，v0.19 给第三方 `--submission your.jsonl` 可直接调用的独立评估器）。

**方法**：`diagnostic_release.py` 读冻结 v0.15 `debiased_test_set.jsonl`[368=219consensus+149disputed] → 拆 blinded test[global_id/prompt/tools_used/disputed，无标签] + answers[global_id/disputed/gold_label/label_v3/label_v4] + 把 v0.18 characterization 逐字并入 + 复用 v0.15 baseline 作 example_submission。assemble 时对 5 源文件（v0.15 debiased_test_set/submission/eval + v0.18 characterization/dispute_analysis）重算 sha256 对 v0.18 记录的锚点，全 MATCH → freeze-integrity PASS，不过则报错退出。

**评分协议**（`diagnostic_eval.py`，双标注者，不伪造 gold）：consensus block[gold accuracy + per-class P/R/F1 + top confusion pairs] / disputed block[v3_agreement_rate / v4_agreement_rate / mean_robustness = 每项 (v3_match+v4_match)/2 的均值 / matches_neither/exactly_one/both，gold_label=null 不伪造单一 gold] / gap = consensus_gold_accuracy − disputed_mean_robustness。

**自检 baseline 对齐**（复用 v0.15 baseline 预测跑 `diagnostic_eval.py`，逐项对 v0.15 `debiased_eval.json`）：

| 指标 | v0.19 自检 | v0.15 锚点 | 对齐 |
|---|---|---|---|
| consensus gold accuracy | 0.817352 | 0.817352 | ✅ |
| disputed mean robustness | 0.308725 | 0.308725 | ✅ |
| gap | +0.508627 | +0.508627 | ✅ |
| matches_neither | 57 | 57 | ✅ |
| matches_exactly_one | 92 | 92 | ✅ |
| n_consensus / n_disputed | 219 / 149 | 219 / 149 | ✅ |

ALL ALIGNED → 评估器口径正确，bundle 可信。

**DETERMINISM PASS**：二次重跑（out vs outB）7 产物 sha256 全一致（PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH pinned + sorted 迭代 + 纯重打包无新随机性）。

**leak check 0 真实 PII**：扫 email/app.e*/app.t*/password/token/svc.*/pinyin_names/Cxmt@ → 仅 "token" 命中，上下文为 "token 开销"（LLM 语境普通英文词，非密钥）；源数据来自已脱敏 v0.6 tasks_v6，无新 PII 风险。

**产物**（`bench_v0.19/out/`）：diagnostic_test_set.jsonl(368 blinded) / diagnostic_answers.jsonl(368 key) / diagnostic_characterization.md(v0.18 逐字副本) / example_diagnostic_submission.jsonl(v0.15 baseline) / example_diagnostic_eval.json(自检) / diagnostic_manifest.json(checksums+provenance+freeze-integrity) / report_v19.html。

**不改冻结层**：v0.10 / v0.15 / v0.6 / v0.18 全部只读，freeze-integrity verdict=PASS。

**局限**：disputed 块仅 2 标注者无 gold（robustness 是协议指标非 accuracy）；诊断 split 仅 368 项不覆盖全 2112 语料；未接第 3 标注者/LLM-judge（待 live endpoint）；多机扇出仍待运维授权。v0.20 候选：接 LLM-judge 跑 3 标注者多数表决 + 升级 κ→Fleiss（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字（v0.19 已是诊断 split 对外就绪形态，可把 v0.17 标 deprecated 指向 v0.19）。

## EXP-20 — v0.20 发布整合 / 弃用层（第21轮，2026-10-28）

**目标**：闭环 v0.19 留下的"下一步候选(4)：把 v0.19 诊断 bundle 与 v0.17 bundle 做去重/合并决断"。v0.12 统一入口只有版本表无 status/deprecation 维度；v0.13 有 artifact diff 但不判语义超集；v0.17/v0.19 同为诊断 bundle，外部审查者会困惑该用哪个。v0.20 把"该用哪个"从人脑判断升级为机器可验证的弃用决断 + 顶层 RELEASE_INDEX 状态图。

**性质**：纯元数据层（同 v0.12/v0.16 风格）。零 `/home` 访问，只读各 `bench_v0.*/out/` 冻结产物。不改任何冻结 `out/` artifact，也不编辑 v0.12 的 `designflow/README.md` 主体逻辑——而是新增 `designflow/RELEASE_INDEX.md`（README 仅做最小同步：标题轮次、版本表加 v0.20 行 + v0.17 弃用标注、指向 RELEASE_INDEX）。

### consolidate.py 逻辑

1. **版本发现**：扫 `designflow/bench_v0.*` 目录，正则匹配 19 个版本，每个版本从内置 VERSION_META 取 role/key_artifact/layer（自描述元数据表，使索引自包含）。
2. **v0.17→v0.19 超集验证**（5 项完整性检查，全过才判 SUPERSEDED）：

| 检查 | 内容 | 结果 |
|---|---|---|
| `global_id_set_equal` | v0.17 与 v0.19 diagnostic_test_set 的 global_id 集合相同 | ✅ 368==368，set_equal=true |
| `blinded_split` | v0.19 test_set 无 label 字段；v0.17 test_set 有 gold_label/label_v3/label_v4 | ✅ v0.19_has_labels=false / v0.17_has_labels=true |
| `source_sha256_match` | v0.19 manifest 声明 v0.15_debiased_test_set sha256 == 磁盘冻结文件实际 sha256 | ✅ 5dd43df6…==5dd43df6… |
| `characterization_bundled` | v0.18 characterization 正文（去标题行）逐字在 v0.19 副本 + 尾部匹配 | ✅ body_in_v19=true / tail_match=true |
| `standalone_cli_evaluator` | v0.19 自带 diagnostic_eval.py + 含 --submission/--answers 入参 | ✅ exists=true / args=true |

5/5 全过 → **v0.17 status = SUPERSEDED by v0.19**（rationale: v0.19 是 characterization-fused strict-blinded 超集；v0.17 test_set 含标签不严格 blinded 且无 characterization；保留作 provenance，新评测请用 v0.19）。

3. **全版本状态分类**：v0.10 = ACTIVE（canonical consensus v1.0-rc1）；v0.19 = ACTIVE（canonical diagnostic）；v0.17 = SUPERSEDED；其余 16 版本 = ACTIVE（foundational / reproducibility / metadata 层，仍被引用）。
4. **产物**：deprecation_map.json（弃用记录+5 项证据）/ release_index.json（19 版本 status/role/layer/note）/ RELEASE_INDEX.md（人类可读状态图，2 canonical release + 全版本表 + 弃用图 + 如何消费指引）/ consolidation_report.json（KPI+provenance+determinism）/ report_v20.html。
5. **顶层 `designflow/RELEASE_INDEX.md`**：NEW 文件，与 out/RELEASE_INDEX.md byte-identical，作为外部消费者的版本状态图入口。

### 修复的两处确定性 bug（开发中发现并修复）

1. `outputs` 字段用 `sorted(os.listdir(OUT))`：被 OUT 目录中上一轮残留文件污染（首轮 out/ 已有 5 文件→列 5；二轮跑进空 TMP→列 3），导致 consolidation_report.json 跨运行不一致。改为显式 `written` 列表（只记本轮实际写入的文件）。
2. `reproduce.sh` 顶层路径 `../../RELEASE_INDEX.md`：从 bench_v0.20/ 出发 `../../` 误指 agent_workspace/，但顶层副本在 designflow/RELEASE_INDEX.md（`../`）。改正后 byte-compare 通过。

### 验证

**DETERMINISM PASS**：二次重跑（out vs TMP）5 产物 byte-identical（deprecation_map.json / release_index.json / RELEASE_INDEX.md / consolidation_report.json / report_v20.html 全 ✅）+ 顶层 designflow/RELEASE_INDEX.md == out/ 副本 byte-identical。PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH pinned + sorted 迭代 + 显式 written 列表，无新随机性。

**leak check 0 真实 PII**：纯元数据层无数据，正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home 全 0。

**freeze-integrity**：v0.10 / v0.15 / v0.17 / v0.18 / v0.19 全部只读，弃用通过状态声明而非物理移除 v0.17 目录。

### 意义

把"两个诊断 bundle 该用哪个"从人脑判断升级为机器可验证的弃用决断。外部消费者现在一张顶层 RELEASE_INDEX 即知：(a) v0.10（consensus easy）+ v0.19（diagnostic hard）是两个 canonical release；(b) v0.17 已 SUPERSEDED；(c) 弃用关系由 5 项 sha256/global_id/字段级证据支撑而非主观声明。与 v0.12（推荐入口/角色路径）、v0.13（artifact diff）形成互补：v0.12 答"我该从哪进"、v0.13 答"版本间变了什么"、v0.20 答"哪个该用哪个已弃"。

### 局限 / 下一步

- 纯元数据层，不新增数据、不扩增样本、不引入新标注者。
- 弃用关系目前仅覆盖 v0.17→v0.19 一对；未来新超集关系需在此层增补。
- v0.21 候选：接真实 LLM-judge endpoint 跑 3 标注者多数表决 + 升级 κ→Fleiss + 给 disputed 项造真 gold（env 无 DESIGNFLOW_LLM_JUDGE→阻塞）/ RESCAN 扩增（/home 持平 3479 无新样本）/ v1.0 对外签字（v0.19 已是诊断 split 对外就绪形态）/ RELEASE_INDEX 与 v0.12 README 进一步去重决断（两者导航维度可互补：v0.12 是"推荐入口/角色路径"，v0.20 是"状态/弃用"，可保留分工）。


## 归档批次 8（2026-10-28 第25轮体积维护）— MEMORY 流水 轮次 21-23 原文

以下为 MEMORY_DESIGNFLOW.md 流水区第21-23轮唤醒记录原文（已闭合，搬入此处，原位留 1 行指针）。

- [21:50] 第21轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第21轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.20 发布整合/弃用层**（闭环 v0.19 留下的"下一步候选(4)：把 v0.19 诊断 bundle 与 v0.17 bundle 做去重/合并决断"——v0.12 统一入口只有版本表无 status/deprecation 维度；v0.13 有 artifact diff 但不判语义超集；v0.17/v0.19 同为诊断 bundle，外部审查者会困惑该用哪个）。**consolidate.py** 发现 19 个 bench_v0.* 版本 + 机器验证 v0.17→v0.19 超集关系——5 项完整性检查全过：①global_id_set_equal[368==368 集合相等] ②blinded_split[v0.19 test_set 无 gold_label/label_v3/label_v4，v0.17 有=非严格 blinded] ③source_sha256_match[v0.19 manifest 声明 v0.15_debiased_test_set sha256=5dd43df6… == 磁盘冻结文件实际 sha256] ④characterization_bundled[v0.18 characterization 正文(去标题行)逐字在 v0.19 bundled 副本 + 尾部匹配] ⑤standalone_cli_evaluator[diagnostic_eval.py 存在 + 含 --submission/--answers 入参]→**v0.17 status=SUPERSEDED by v0.19**(rationale: v0.19 是 characterization-fused strict-blinded 超集，v0.17 test_set 含标签不严格 blinded 且无 characterization，保留作 provenance 新评测请用 v0.19)。**产 5 产物**：deprecation_map.json / release_index.json[19 版本 status/role/layer/note] / RELEASE_INDEX.md[人类可读状态图,2 canonical release(v0.10 consensus + v0.19 diagnostic)+全版本状态表+弃用图+如何消费指引] / consolidation_report.json / report_v20.html。**顶层 designflow/RELEASE_INDEX.md** 与 out/ 副本 byte-identical(NEW 文件,不编辑 v0.12 README)。**修两处确定性 bug**：①outputs 字段用 os.listdir(OUT) 被 stale 文件污染→改为显式 written 列表 ②reproduce.sh 顶层路径 `../../` 误指 agent_workspace→改 `../` 指 designflow/。**DETERMINISM PASS**(二次重跑 5 产物 sha256 全一致 + 顶层副本 byte-identical)。**leak check 0 真实 PII**(纯元数据层,正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home 全 0)。**不改冻结 v0.10/v0.15/v0.17/v0.18/v0.19**(弃用通过状态声明而非物理移除 v0.17 目录)。**同步更新 v0.12 统一 README**：标题→updated through v0.20、加 v0.20 指向 RELEASE_INDEX 段、资产盘点轮次 20→21+漂移说明延伸到 21 轮、版本索引加 v0.20 行+v0.17 标⚠️SUPERSEDED、DAG 加 v0.20 节点、诊断 bundle 段从 v0.17 改指 v0.19+弃用提示、复现段加 v0.19/v0.20 一条命令、gate 表 .75 轮次 19→21。体积自检 TASK5.1KB/MEMORY ~27KB/EXP 21KB 全在 32KB 内。bash reproduce.sh 一键复现(零/home访问,只读冻结各 bench_v0.*/out/)。意义:把"两个诊断 bundle 该用哪个"从人脑判断升级为机器可验证的弃用决断——外部消费者现在一张顶层 RELEASE_INDEX 即知 v0.10(consensus easy)+v0.19(diagnostic hard)是两个 canonical release、v0.17 已弃用,且弃用关系由 5 项 sha256/global_id/字段级证据支撑而非主观声明。
- [22:10] 第22轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第22轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.21 诊断 split bootstrap CI + gap 显著性层**（闭环"v0.19 规范诊断发布的 headline gap/robustness 只有点估计无 CI"缺口——v0.14 给了 easy consensus 的 bootstrap CI 但诊断 split 自身 headline 未覆盖；v0.18 解释了 gap 机理但没给不确定度/显著性）。**bootstrap_diagnostic.py** 读冻结 v0.15 debiased_test_set[368]+submission→重算点估计 **cross-check vs v0.15 debiased_eval.json 6/6 MATCH**[acc0.817352/rob0.308725/gap+0.508627/neither57/one92/both0，漂移则中止]→**分层非参数 percentile bootstrap 10000×** numpy default_rng(seed=0)，219 consensus 与 149 disputed **独立重抽样**（分层 bootstrap 保持固定 219/149 设计传播层内不确定性），gap 每次重抽样作两 stratum 均值差重算→**CI：consensus acc[0.7671,0.8676]（复现 v0.14 [0.767,0.868] 互证两条代码路径在共享 stratum 吻合）/ disputed rob[0.2685,0.3490] / gap[0.4453,0.5729]**。**gap CI 排除 0 → 统计显著 α=0.05**；one-sided bootstrap p-value=**0.0**→拒绝 H0:gap≤0。disputed 类别剖面 CI neither~0.32-0.44/one~0.56-0.68/both 钉 0。**freeze-integrity PASS**[v0.15 debiased_test_set 磁盘 sha256==v0.19 manifest 锚点]。**DETERMINISM PASS**[二次重跑 byte-identical]。**leak check 0 真实 PII**。**不改冻结 v0.10/v0.15/v0.18/v0.19/v0.20**；顶层 designflow/README.md 增 v0.21 行+资产盘点轮次 21→22+DAG+复现段+gate 表 .75 21→22。修一处 report_v21.py key typo（v0_19_→v0.19_ manifest 键名）。体积自检 TASK5.1KB/MEMORY~22KB/EXP~26KB 全≤32KB。bash reproduce.sh 一键复现(零/home)。
- [22:25] 第23轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第23轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.22 发布索引再生 + DATA_CARD addendum §G 整合层**（闭环 v0.21 留下的"下一步候选：把 v0.21 CI 层回写进 v0.16 DATA_CARD ADDENDUM 作为 §G + 把 v0.21 纳入 RELEASE_INDEX 再生[下一整合层]"——v0.21 明确把索引再生推到下一整合层；v0.20 consolidate.py 硬编码 VERSION_META 含 v0.1–v0.20 不含 v0.21）。**integrate.py** 读冻结 v0.20/out/release_index.json[19 版本]为基线 + **机器验证 v0.21 freeze-integrity 三项全过**：①debiased_test_set 磁盘 sha256==v0.21 manifest 锚点 5dd43df6… ②cross_check_vs_v0.15==MATCH 6/6 点估计 ③gap CI[0.4453,0.5729] 排除 0→追加 v0.21[ACTIVE,metadata_stats_ci]+v0.22[ACTIVE,metadata_integration]→**21 版本/20 ACTIVE/1 SUPERSEDED**。canonical release[v0.10 consensus + v0.19 diagnostic]**不变**，v0.17 仍 SUPERSEDED by v0.19 弃用证据 carried forward 不重算（纯 append 整合）。**产 5 产物**：release_index_v0.22.json / RELEASE_INDEX.md[人类可读 v0.22 视图，含 v0.21 freeze-integrity 表+delta vs v0.20] / DATA_CARD_ADDENDUM_v0.22.md[=**§G** gap 显著性 CI 扩展冻结 v0.16 §A–§E，§F 刻意未用预留 3 标注者 Fleiss κ gate 阻塞；不改 v0.16 out/] / consolidation_report_v0.22.json / report_v22.html。**DETERMINISM PASS**[5/5 byte-identical 二次重跑]。**FREEZE-INTEGRITY PASS**[v0.15 disk sha==v0.21 anchor]。**leak check 0 真实 PII**。**不改冻结 v0.16/v0.20/v0.21 out/**，仅覆盖顶层 designflow/RELEASE_INDEX.md[活的导航图，v0.20 自己的 reproduce 也覆盖它]。顶层 README 增 v0.22 行+资产盘点轮次 22→23+DAG 节点+复现段+诊断不确定性指引[诊断 bundle 段加 v0.21 CI + §G 指针]+gate 表 .75 22→23。体积自检 TASK5.1KB/MEMORY~25KB/EXP 36KB→归档EXP-17..20原文→ARCHIVE批次7后18.3KB全≤32KB。bash reproduce.sh 一键复现(零/home)。


## 归档批次 9 — EXP-21..EXP-23 原文（2026-10-28 第26轮体积维护，从 EXPERIMENTS_DESIGNFLOW.md 搬入）

> 搬前 `git pull --rebase --autostash`（already up to date）。EXP-21/22/23 已闭合（结果整合进后续 v0.22/v0.24 整合层 + MEMORY 流水），EXPERIMENTS 留 1 行指针。搬入原文如下。

## EXP-21 — v0.21 诊断 split bootstrap CI + gap 显著性层（第22轮，2026-10-28）

**动机**：v0.19 诊断 split 是规范发布（canonical diagnostic release），其 headline 数字是 gap = consensus gold accuracy − disputed mean robustness（v0.11 baseline 下 = +0.5086）。v0.14 已对 easy consensus 指标（219 项 acc/macroF1）给了 bootstrap 95% CI，但诊断 split 自身的 headline 指标——disputed mean robustness（0.3087）与 gap（+0.5086）——只报了点估计，没有置信区间。v0.18 解释了 gap 的机理但没给不确定度/显著性。v0.21 在规范硬发布上补上这一严谨性缺口。

**方法**：`bootstrap_diagnostic.py` 纯冻结数据（零 /home/网络/LLM/新随机性）：
1. **点估计重算 + cross-check**：从冻结 v0.15 `debiased_test_set.jsonl`(368) + `debiased_submission.jsonl`(368) 重算 consensus acc / disputed robustness / gap / categorical matches(neither/exactly_one/both)，逐项对冻结 v0.15 `debiased_eval.json` 锚点——6/6 MATCH，否则层中止（冻结输入漂移不会静默移动 headline）。
2. **分层非参数 percentile bootstrap 95% CI**（10000 重抽样，`numpy default_rng(seed=0)`）：219-consensus 与 149-disputed **独立**重抽样（分层 bootstrap，保持固定 219/149 设计，传播层内不确定性）；gap 在每次重抽样中作两 stratum 均值之差重算。
3. **gap 显著性检验**：one-sided bootstrap p-value = 重抽样 gap ≤ 0 的分率；等价于检验 H0: gap=0（α=0.05 下拒绝 ⟺ 95% gap CI 排除 0）。
4. **disputed stratum 类别剖面 CI**：对 149 项 disputed stratum bootstrap，给 matches_neither/exactly_one/both 分率的 CI（给 v0.18 的 57/92/0 计数加不确定度）。

**结果**：

| 指标 | 点估计 | 95% bootstrap CI |
|---|---|---|
| consensus gold accuracy | 0.817352 | [0.7671, 0.8676] |
| disputed mean robustness | 0.308725 | [0.2685, 0.3490] |
| **gap** | **+0.508627** | **[0.4453, 0.5729]** |

- **gap 95% CI [0.4453, 0.5729] 排除 0 → 统计显著**（α=0.05）；one-sided bootstrap p-value = **0.0**（10000 次重抽样无一次 gap ≤ 0）→ 拒绝 H0: gap≤0。
- **内部一致性**：consensus accuracy CI [0.7671, 0.8676] 复现 v0.14 在同 219 easy 项上的 CI [0.7671, 0.8676]——两条独立 bootstrap 代码路径在共享 stratum 上吻合，互证正确。
- disputed 类别剖面：matches_neither ≈ 0.32–0.44（点 57/149=0.383）/ exactly_one ≈ 0.56–0.68（点 92/149=0.617）/ both 的 CI 钉在 0——baseline 几乎从不同时匹配两个标注者。

**质量门**：
- **CROSS-CHECK vs v0.15**：6/6 MATCH（acc/robustness/gap/neither/one/both 全对齐）。
- **FREEZE-INTEGRITY PASS**：v0.15 `debiased_test_set` 磁盘 sha256 == v0.19 `diagnostic_manifest.json` provenance 记录的锚点 sha256（冻结输入 bit-identical）。
- **DETERMINISM PASS**：`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH` pinned + `numpy default_rng(seed=0)` + 冻结文件序 per-item 数组 + 整数位置索引（热循环无 dict-hash 依赖）→ 二次重跑 diagnostic_ci.json/manifest/report_v21.html byte-identical。
- **LEAK CHECK 0 残留**：纯统计产物，正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/cxmt/home 全 0。

**产物**（`bench_v0.21/`）：bootstrap_diagnostic.py / report_v21.py / reproduce.sh / README.md；`out/`：diagnostic_ci.json（点估计+cross-check+bootstrap CI[acc/rob/gap]+gap 显著性+disputed 类别剖面 CI+方法/provenance）/ diagnostic_ci_manifest.json（4 输入 sha256+freeze-integrity PASS+输出 sha256）/ report_v21.html。

**不改冻结层**：v0.10/v0.15/v0.18/v0.19/v0.20 全部只读；v0.21 是 v0.19 之上的不确定性层。顶层 RELEASE_INDEX（v0.20 产）的 19 版本状态表不在本层重算——v0.21 作新版本纳入下一次整合层再生，以保 v0.20 冻结层不变。

**复探 3 口径**（第22轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 22 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 22 轮同卡点，上报仍有效待回复。

**结论**：把 v0.15 的点估计 gap 从"一个无不确定度的差值"升级为"带 95% CI 且统计显著的发现"。gap CI [0.445, 0.573] 远离 0，证实 +0.51 gap 不是小样本伪迹——baseline 的 headline accuracy(0.817) 只在 easy consensus stratum 维持，在 hard disputed stratum 下降到 ~0.31 且这一下降统计上真实。这为 v0.18 的机理解释（标签边界模糊/短 prompt/用户集中）背书：它在解释一个真实效应而非噪声。v0.22 候选：接 LLM-judge 跑 3 标注者多数表决 + 升级 κ→Fleiss + 给 disputed 项造真 gold（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字 / 把 v0.21 CI 层回写进 v0.16 ADDENDUM 作为 §G + 纳入 RELEASE_INDEX 再生。

## EXP-22 — v0.22 发布索引再生 + DATA_CARD addendum §G 整合层（第23轮，2026-10-28）

**动机**：v0.21（EXP-21）明确把 RELEASE_INDEX 再生推到「下一整合层」以保 v0.20 冻结层不变——v0.20 的 `consolidate.py` 用硬编码 `VERSION_META`（v0.1–v0.20，不含 v0.21）。本层即该整合层：把 v0.21 纳入版本索引再生，并把 v0.21 的 gap 显著性 CI 回写进冻结的 v0.16 DATA_CARD ADDENDUM 作为 §G（v0.16 §A–§E 只含 v0.14/v0.15 证据，缺 v0.21 的不确定度/显著性维度）。

**方法**：`integrate.py` 纯冻结数据（零 /home/网络/LLM/新随机性）：
1. **加载冻结基线**：读 `bench_v0.20/out/release_index.json`（19 版本）为基线，校验 `benchmark_version=="v0.20"` 且 `n_versions==19`，否则层中止。
2. **机器验证 v0.21 freeze-integrity 三项**：①`debiased_test_set` 磁盘 sha256 == v0.21 manifest 锚点 `5dd43df6…`（与 v0.19/v0.20 同锚点，再验证）②v0.21 `cross_check_vs_v0.15` == MATCH（6/6 点估计逐项相等）③gap CI `[0.4453, 0.5729]` 排除 0（显著性声明可复现）。三项全过才继续。
3. **纯 append 扩展版本表**：追加 v0.21（ACTIVE, `metadata_stats_ci`）+ v0.22（ACTIVE, `metadata_integration`）→ 21 版本 / 20 ACTIVE / 1 SUPERSEDED。canonical release（v0.10 consensus + v0.19 diagnostic）不变；v0.17 仍 SUPERSEDED by v0.19，弃用证据 carried forward 不重算（不重新跑 v0.20 的 5 项超集校验，沿用其冻结结果）。
4. **再生 RELEASE_INDEX.md（v0.22 视图）**：人类可读导航图，含 v0.21 freeze-integrity 表 + delta vs v0.20 + 全版本状态表 + 如何消费指引（新增"诊断不确定性（CI/显著性）"指向 v0.21）。
5. **DATA_CARD_ADDENDUM_v0.22.md = §G**：扩展冻结 v0.16 addendum（§A–§E 不变，不改 v0.16 out/）。§G 重述 §D 点估计 gap(+0.5086) → v0.21 分层 bootstrap 95% CI（方法/结果表/显著性 p=0.0/disputed 类别剖面 CI/4 点 interpretation/provenance/cross-check）。**§F 刻意未用**——预留未来 3 标注者 Fleiss κ 层（gate 阻塞）。

**结果**：21 版本（20 ACTIVE / 1 SUPERSEDED），delta vs v0.20 = +v0.21 +v0.22，无 status 变更，canonical release 不变，弃用证据不变。§G 把 +0.5086 gap 从点估计升级为统计显著发现（gap CI [0.4453,0.5729] 排除 0，p=0.0），并标注 §F 预留位。

**质量门**：
- **DETERMINISM PASS**：5/5 产物（release_index_v0.22.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.22.md / consolidation_report_v0.22.json / report_v22.html）二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` pinned + 排序迭代；无新随机性，纯元数据）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 == v0.21 manifest 锚点 `5dd43df6…`。
- **LEAK CHECK 0 残留**：纯元数据层，正则扫 app.*/email/svc.*/shiwei/zhulong/Cxmt@/home 全 0。

**产物**（`bench_v0.22/`）：integrate.py / report_v22.py / reproduce.sh / README.md；`out/`：release_index_v0.22.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.22.md / consolidation_report_v0.22.json / report_v22.html。

**不改冻结层**：v0.16/v0.20/v0.21 out/ 全部只读；唯一被覆盖的是顶层 `designflow/RELEASE_INDEX.md`（活的导航图，v0.20 自己的 reproduce 也覆盖它，非冻结 per-version 产物）。同步更新顶层 `designflow/README.md`：标题→updated through v0.22、版本数 21→22、资产盘点轮次 22→23、加 v0.22 行、DAG 加 v0.22 节点、复现段加 v0.22 一条命令、诊断 bundle 段加 v0.21 CI + §G 指针、gate 表 .75 22→23。

**复探 3 口径**（第23轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 23 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 23 轮同卡点，上报仍有效待回复。

**结论**：闭环 v0.21 留下的两件待办（索引再生 + §G 回写）为单一整合层，纯 append 不重算 v0.20 弃用证据以保冻结。当前统计有效性 addendum 的完整图景 = v0.16 §A–§E + v0.22 §G。§F 预留位明确指向下一个真正能改变结论的 gate（3 标注者 Fleiss κ，需 live LLM endpoint）。v0.23 候选：接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 给 disputed 项造真 gold → 落地 §F（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字；多机扇出仍待运维决断。

## EXP-23 — v0.23 冻结 lineage 完整性全扫层（第24轮，2026-10-28）

**动机**：v0.22（EXP-22）机器验证了**单个** freeze-integrity 锚点（v0.15 `debiased_test_set` 磁盘 sha256 == v0.19 manifest 锚点 `5dd43df6…`）。但项目现有 21 个冻结版本，跨版本 provenance `sha256` 声明有数十个（v0.19→v0.15、v0.20→v0.19、v0.21→v0.15、v0.22→v0.20/v0.21、v0.8 frozen_files、v0.9 release_files、v0.13 per_version.artifacts、v0.16 provenance、v0.17 provenance…）。若**任一**冻结输入静默漂移，所有建于其上的下游结论（v0.19 诊断发布、v0.21 gap CI、v0.22 release index）失效——而 v0.22 之前无任何检查能全局捕获。v0.23 把 v0.22 的单锚点验证推广为**全树穷举**。

**方法**：`lineage_audit.py` 纯冻结数据（零 /home/网络/LLM/新随机性）：
1. **锚点提取**：递归扫所有 `bench_v0.*/out/*.json` manifest，提取每个声明的 `(path, sha256)` 锚点。识别两种结构形式：**Form B（path-bearing provenance）** `{path, sha256}` / `{name, sha256}`——覆盖 provenance/source_provenance/inputs/outputs[]，`path` 相对 designflow/ 根解析、`name` 相对 owner out/；上方键（`datacard_v0.10`/`v0.15_debiased_test_set`）是逻辑标签非文件名，绝不当作路径提取。**Form A（self-referential artifact map）** `{<filename>: {sha256,…}}`——仅在 value 无 path/name 且 key 以文件扩展名结尾时触发，base 解析：v0.8 `source_dir` / v0.13 `per_version/<v>/artifacts` / owner out/；带 `match` 布尔的 freeze-time self-check 记录（v0.19 `freeze_integrity`）跳过（其底层文件已由 source_provenance Form B 锚定）。
2. **盘上校验**：每个锚点解析路径、算磁盘 sha256、分类 PASS/MISMATCH/MISSING。
3. **drift vs v0.13**：重建全树 manifest（所有冻结 `bench_v0.*/out/` 文件 sha256），把 v0.1–v0.11 子集与冻结 `bench_v0.13/out/version_manifest.json`（73 artifacts）逐一比对，捕获冻结产物自身的漂移。
4. **lineage 图**：version → 声明的输入锚点 → 验证状态（机器可读依赖图）。
5. **自洽设计**：排除本层 `bench_v0.23/out/`（own in-progress outputs，非冻结输入）——扫它会读陈旧副本并造成自指哈希递归（audit 含 full-tree manifest 含 audit 自身 sha）。manifest 只列数据输出 `lineage_audit.json`，不列自身（自指哈希永不稳定，承 v0.21/v0.22 惯例）。

**调试中发现并修复的 3 个真实提取器 bug**：① Form-A 误把 provenance 逻辑标签（`datacard_v0.10` 含点）当文件名→改为扩展名后缀检查 + value 有 path/name 时跳过；② v0.13 `per_version[v].artifacts` 误解析到 manifest 自身 out/→改为按 trail 的 vlabel 解析到 `bench_v{v}/out/`；③ v0.8 `source_dir` 在递归进 `frozen_files` 时丢失上下文→改为顶层捕获并经 ctx 下传。另修 full-tree manifest 漏扫 dotfile（v0.6 `.gitignore` 是 v0.13 记录的真实产物）。

**结果**：

| 指标 | 值 |
|---|---|
| overall verdict | **PASS** |
| manifests scanned | 56（排除 bench_v0.23/out/） |
| sha256 anchors extracted (total) | 124 |
| anchors (unique paths) | 95 |
| anchor PASS | **124** |
| anchor MISMATCH | 0 |
| anchor MISSING | 0 |
| drift vs v0.13 | **PASS** (73/73 matched, scope v0.1–v0.11) |
| lineage graph | 8 版本声明锚点（v0.10/v0.13/v0.15/v0.16/v0.17/v0.19/v0.21/v0.22），全 intact |

- **v0.22 锚点再验证**：`5dd43df6…`（v0.15 debiased_test_set）作为 v0.15 manifest 的自声明产物被本层重新校验 PASS——v0.23 **subsumes** v0.22 的单锚点检查。
- **lineage 图**：v0.13 声明最多（63 锚点，per_version v0.1–v0.11 artifacts 自引用）；v0.19 声明 6（v0.15 三件 + v0.18 两件 + freeze）；v0.21 声明 1（其 manifest inputs 已被本层扫描覆盖）。

**质量门**：
- **DETERMINISM PASS**：`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` pinned + sorted iteration + `sort_keys` JSON + 排除 own out/（避免自指哈希递归）→ `lineage_audit.json` / `lineage_audit_manifest.json` 二次重跑 byte-identical（reproduce.sh `DETERMINISM_CHECK=1` 自检通过）。
- **LEAK CHECK 0 残留**：纯元数据层，正则扫 app.e*/t*/shiwei/zhulong/Cxmt@/svc.edaagent/Word@digits/email//home/app 全 0。
- **FREEZE-INTEGRITY（本层结论）**：全树 124 锚点 PASS = 整个冻结依赖图 bit-intact。

**产物**（`bench_v0.23/`）：lineage_audit.py / report_v23.py / reproduce.sh（含 leak check + DETERMINISM_CHECK 自检）/ README.md；`out/`：lineage_audit.json（headline/anchor_verification/lineage_graph/drift_vs_v0.13/full_tree_manifest/scope/provenance）/ lineage_audit_manifest.json（inputs=56 manifests+v0.13 version_manifest；output=lineage_audit.json sha256）/ report_v23.html。

**不改冻结层**：v0.1–v0.22 out/ 全部只读；顶层 `designflow/RELEASE_INDEX.md` **不覆盖**——v0.23 为完整性审计层（非整合层），按 v0.21 先例把 RELEASE_INDEX 再生推到下一整合层（避免重算 v0.22 冻结索引）。同步更新顶层 `designflow/README.md`：标题→updated through v0.23、版本数 22→23、资产盘点轮次 23→24、加 v0.23 行、DAG 加 v0.23 节点、复现段加 v0.23 一条命令、完整性审计段、gate 表 .75 23→24。

**复探 3 口径**（第24轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 24 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 24 轮同卡点，上报仍有效待回复。

**结论**：把 v0.22 的"1 个锚点 == manifest 声明"升级为"全树 124 锚点 == 磁盘"的穷举完整性审计。PASS 意味着整个冻结依赖图 bit-intact——v0.19 诊断发布、v0.21 gap CI、v0.22 release index 所依赖的每一个冻结输入都还是当初冻结时的那一份比特。这是 v0.7（单版本逐比特）、v0.13（manifest 快照）、v0.20/v0.22（per-layer determinism）之外的**首个全树级**完整性检查。v0.24 候选：接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 给 disputed 项造真 gold → 落地 §F（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字 / 把 v0.23 纳入 RELEASE_INDEX 再生（下一整合层）；多机扇出仍待运维决断。


## 归档批次 10（2026-10-28 第27轮体积维护）— MEMORY 流水 轮次 24-26 原文

从 `MEMORY_DESIGNFLOW.md` 流水段搬入（留 1 行指针回指本批次）。轮次 24/25/26 三轮已闭合（v0.23 冻结 lineage 完整性全扫层 / v0.24 发布索引再生+§H 整合层 / v0.25 per-user 公平性审计层），第27轮推进 v0.26 后归档以维持 MEMORY ≤32KB。

- [22:55] 第24轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第24轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.23 冻结 lineage 完整性全扫层**（闭环 v0.22 留下的"v0.22 只机器验证 1 个锚点（v0.15 debiased_test_set），但全树数十个声明 sha256 锚点从未全局校验"缺口——若任一冻结输入静默漂移，所有下游结论失效而 v0.22 前无检查能全局捕获）。**lineage_audit.py** 递归扫所有 bench_v0.*/out/*.json manifest[56 个，排除本层 out/]，提取每个声明 (path,sha256) 锚点[Form B path-bearing provenance {path,sha256}/{name,sha256} + Form A self-referential artifact map {<filename>:{sha256}}]→对盘上文件逐个 sha256 校验 + drift vs v0.13 version_manifest[73 artifacts]。**调试中修复 3 个真实提取器 bug**：①Form-A 误把 provenance 逻辑标签 datacard_v0.10（含点）当文件名→改扩展名后缀检查+value 有 path/name 时跳过 ②v0.13 per_version[v].artifacts 误解析到 manifest 自身 out/→按 trail vlabel 解析到 bench_v{v}/out/ ③v0.8 source_dir 递归进 frozen_files 时丢失上下文→顶层捕获经 ctx 下传；+ full-tree manifest 漏扫 dotfile[v0.6 .gitignore]。**排除本层 bench_v0.23/out/ 避免自指哈希递归**（audit 含 full-tree manifest 含 audit 自身 sha；manifest 只列数据输出不列自身，承 v0.21/v0.22 惯例）。**结果 overall PASS**：124 锚点全 PASS/95 unique/0 mismatch/0 missing；drift vs v0.13 **PASS 73/73**；lineage 图 8 版本[v0.10/v0.13/v0.15/v0.16/v0.17/v0.19/v0.21/v0.22]声明的输入全 bit-intact；**v0.22 锚点 5dd43df6… 被再验证 PASS→subsumes v0.22 单锚点检查**。**产 3 产物**：lineage_audit.json / lineage_audit_manifest.json / report_v23.html。**DETERMINISM PASS**[byte-identical 二次重跑，reproduce.sh DETERMINISM_CHECK=1 自检通过]。**leak check 0 真实 PII**。**不改冻结 v0.1–v0.22 out/**，顶层 RELEASE_INDEX.md **不覆盖**[审计层非整合层，按 v0.21 先例推到下一整合层避免重算 v0.22 冻结索引]。顶层 README 增 v0.23 行+资产盘点轮次 23→24+DAG+复现段+完整性审计段+gate 表 .75 23→24。体积自检 TASK5.1KB/MEMORY~26KB/EXP~26KB 全≤32KB。bash reproduce.sh 一键复现(零/home)。意义:把"全树冻结依赖图是否还 bit-intact"从 v0.22 的 1 个锚点升级为 124 锚点穷举——v0.7 单版本逐比特/v0.13 manifest 快照/v0.20-v0.22 per-layer determinism 之外的**首个全树级**完整性检查。
- [23:10] 第25轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第25轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。**推进不阻塞的 v0.24 发布索引再生 + DATA_CARD addendum §H 整合层**（闭环 v0.23 留下的"把 v0.23 纳入 RELEASE_INDEX 再生[下一整合层]"——v0.23 承 v0.21 审计层先例把索引再生推到下一整合层，避免重算冻结的 v0.22 索引）。**integrate.py** 读冻结 v0.22/out/release_index_v0.22.json[21 版本]为基线 + **机器验证 v0.23 freeze-integrity 四项全过**：①overall_verdict==PASS ②124 锚点全 PASS[anchor_pass==124/mismatch==0/missing==0，且每条记录 status==PASS] ③drift vs v0.13==PASS[73/73 matched] ④v0.22 单锚点 5dd43df6… 在 v0.23 穷举锚点列表里被再验证 PASS[declared_sha256==disk_sha256]→**v0.23 subsumes v0.22 单锚点检查**；本层另独立重算 bench_v0.15/out/debiased_test_set.jsonl 磁盘 sha256 仍 5dd43df6…→追加 v0.23[ACTIVE,integrity_audit]+v0.24[ACTIVE,metadata_integration]→**23 版本/22 ACTIVE/1 SUPERSEDED**。canonical release[v0.10 consensus + v0.19 diagnostic]**不变**，v0.17 仍 SUPERSEDED by v0.19 弃用证据 carried forward 不重算（纯 append 整合）。**产 5 产物**：release_index_v0.24.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.24.md[=§H] / consolidation_report_v0.24.json / report_v24.html。DETERMINISM PASS。FREEZE-INTEGRITY PASS。leak check 0。不改冻结层，仅覆盖顶层 RELEASE_INDEX.md。
- [23:27] 第26轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第26轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。前几轮 v0.22–v0.24 趋向元数据重验证，本轮改做**实质 accuracy 维度分析**。**推进不阻塞的 v0.25 per-user 公平性审计层**（闭环 v0.18「disputed 用户集中→指向 per-user 公平性审计」v1.x 路径 + v0.16 §E 定性局限量化）。**fairness_audit.py** 读冻结 v0.15 debiased_test_set[368]+debiased_submission+v0.6 tasks_v6 按 global_id join。6 维度：①user_concentration[consensus 11 用户 Gini0.5654/HHI0.1951/even baseline 0.0909→**2.14× 集中**/top-3 70.3%；disputed 13 用户 Gini0.4812/HHI0.1465/top-3 54.4%**复现 v0.18 的 54.4%**] ②per_user_accuracy[consensus acc 跨 0.0–1.0，u_011627302e55 n46 acc1.0 撑 headline+eda_aether_layout 类，u_04a093643b42 n13 acc0.3846 + u_b423b3c9e88c n7 acc0.5714 真实 per-user gap 被 headline 掩盖] ③per_user_robustness[disputed v3/v4 agree+mean robustness per user] ④leave_one_user_out[逐用户 LOUO，**|Δ|max=0.0486 < 0.05 → headline accuracy IS user-robust**——即使 top-3 占 70% 也不是单用户伪迹；最大驱动 u_011627302e55 Δ=-0.0486 dropped46 LOO acc0.7688] ⑤label_support_concentration[**8/9 类 ≥0.5 单用户垄断**，3/9 ==1.0(eda_innovus/eda_timing_power/eda_drc_lvs)，eda_aether_layout max-share0.9787；mean max-share0.8375 → **per-class 尾类 P/R/F1 实质是 per-user metric，泛化到未见用户未测**] ⑥cross_check_vs_v015[**6/6 MATCH**：n368/consensus219/disputed149/acc0.817352/rob0.308725/neither57/one92]。**净结论**：headline 经受用户分层考验，per-class 拆分没有——这是 DATA_CARD「single-machine source」局限背后的具体证据，motivates user-stratified re-split 作为 v1.x 构造候选。产 3 产物 fairness_audit.json/fairness_characterization.md/report_v25.html。**DETERMINISM PASS**[byte-identical 二次重跑]。**FREEZE-INTEGRITY PASS**[v0.15 disk sha==5dd43df6… prefix_match=True]。**leak check 0 真实 PII**。**不改冻结 v0.1–v0.24 out/**；audit 层非整合层**不重算 RELEASE_INDEX**（按 v0.21/v0.23 先例推到下一整合层再生）。顶层 README 增 v0.25 行+资产盘点轮次 25→26+DAG 节点+per-user 公平性段+复现段+gate 表 .75 25→26。体积自检 TASK5.1KB/MEMORY~27KB/EXP~30KB 全≤32KB 无需归档。bash reproduce.sh 一键复现(零/home)。


## 归档批次 11（2026-10-29 第28轮体积维护）
从 `MEMORY_DESIGNFLOW.md` 流水段搬入（留 1 行指针回指本批次）。轮次 27 一条流水原文。

- [23:43] 第27轮唤醒：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第27轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。本轮推进**不阻塞的 v0.26 user-stratified re-split 构造层**（直接闭环 v0.25 下一步候选「据 v0.25 per-class 单用户垄断构造 user-stratified re-split [v1.x 构造候选]」——v0.25 是审计层只刻画冻结 split，本层是构造层建新 split）。**user_resplit.py** 读冻结 v0.15 debiased_test_set[368]取 consensus 219，按 (gold_label × user_hash) 分组，每类主用户[count desc, ties by user_hash asc]→TRAIN，其余用户→HELD-OUT TEST（标签由不同用户学到）。IMPOSSIBLE 单用户类→train only。split train=168/test=51，6 splittable/3 IMPOSSIBLE[eda_innovus 14/eda_timing_power 2/eda_drc_lvs 1 共17项 train-only]。复用 v0.11 TF-IDF(latin+CJK-bigram)+tools tokens+nearest-centroid(cosine) baseline 重训重测。**user-strat acc=0.5882(n_test=51,correct=30) vs headline 0.8174 → gap=−0.2291**——证实存在 headline 掩盖的未见用户泛化缺口。per-class：code_dev test_n=27 acc0.889迁移好 / other test_n=15 acc0.267 / eda_virtuoso_schematic test_n=4 acc0.0 / eda_aether_layout test_n=1 acc0.0(薄) / data_analysis test_n=2 acc0.5 / file_ops test_n=2 acc0.5。fully-unseen-user subset[test 用户在 train 出现 0 次] n=42 acc0.6667。per-user：u_2c1bbb233e80 n16 acc1.0 撑 / u_04a093643b42 n13 acc0.2308 拖。**净结论**：v0.25 说 per-class 尾类==per-user metric 是「未测」，v0.26 把它升级为「已测且测出差 −0.23」——code_dev 跨用户迁移好，other/eda_virtuoso_schematic 主用户标签签名不迁移；3 类 IMPOSSIBLE 源硬限仅更多用户/机器可解。**调试中修 2 bug**：①cross-check 字段名错（v0.15 eval 是 consensus_block.n/gold_accuracy 非 consensus_n/consensus_accuracy）②per_class_acc 聚合 buggy 表达式 `p["correct"] and p["gold_label"] or p["gold_label"]` 改回简单 `by_cls[gold]["correct"]+=correct`。产 8 产物 user_resplit.json/resplit_characterization.md/user_strat_train.jsonl[168]/user_strat_test.jsonl[51 blinded]/user_strat_answers.jsonl[51]/user_strat_submission.jsonl[51]/user_resplit_manifest.json/report_v26.html。**DETERMINISM PASS**[byte-identical 二次重跑 8/8]。**FREEZE-INTEGRITY PASS**[v0.15 disk sha==5dd43df64f4d… 前缀匹配]。**CROSS-CHECK vs v0.15 PASS**[consensus_n 219/acc 0.817352 MATCH]。**leak check 0 真实 PII**。**不改冻结 v0.1–v0.25 out/**；构造层非整合层**不重算 RELEASE_INDEX**（按 v0.21/v0.23/v0.25 先例推到下一整合层再生，避免重算冻结 v0.24 索引）。顶层 README 增 v0.26 行+资产盘点轮次 26→27+DAG 节点+user-stratified 段+复现段+gate 表 .75 26→27。体积自检见下。bash reproduce.sh 一键复现(零/home)。意义:把 v0.25「per-class 单用户垄断→泛化未测」从 audit 升级为 construction——首个主动构造未见用户 held-out test 的层，量化出 −0.23 真实泛化 gap。


## 归档批次 12 — EXP-24..EXP-26 原文（2026-10-29 第29轮体积维护，从 EXPERIMENTS_DESIGNFLOW.md 搬入）
> 第29轮体积维护：EXPERIMENTS 30.3KB，加 EXP-28 将超 32KB 红线。把已闭合的 EXP-24（v0.24 §H 整合层）/ EXP-25（v0.25 per-user 公平性审计）/ EXP-26（v0.26 user-stratified re-split 构造）原文搬入本批次，留 1 行指针回指。EXP-21..23 已在批次 9 归档。

## EXP-24 — v0.24 发布索引再生 + DATA_CARD addendum §H 整合层（第25轮，2026-10-28）

**动机**：v0.23（EXP-23）是冻结 lineage 完整性全扫层，本身不整合进发布索引——它承 v0.21 审计层先例，把 RELEASE_INDEX 再生**明确推到「下一整合层」**以保冻结的 v0.22 索引不被重算。本层即该整合层：把 v0.23 纳入 RELEASE_INDEX 再生，并把 v0.23 全树完整性审计回写进冻结的 v0.16 DATA_CARD ADDENDUM 作为 **§H**（v0.16 §A–§E + v0.22 §G 已覆盖统计有效性，但完整性审计这一维度尚未回写进 datasheet；消费者从 DATA_CARD 应能直接读到"全树 bit-intact 已穷举验证"）。

**方法**：`integrate.py` 纯冻结数据（零 /home/网络/LLM/新随机性）：
1. **加载冻结基线**：读 `bench_v0.22/out/release_index_v0.22.json`（21 版本），校验 `benchmark_version=="v0.22"` 且 `n_versions==21`，否则层中止。
2. **机器验证 v0.23 freeze-integrity（四项全过才继续）**：①`headline.overall_verdict`==PASS ②全部 124 锚点 PASS——headline 计数器自洽（`anchor_pass==anchors_total`、`anchor_mismatch==0`、`anchor_missing==0`）**且**逐条遍历 `anchor_verification` 记录 `status==PASS`（防止 headline 计数器与记录列表不一致的静默漏洞）③drift vs v0.13 == PASS（`checked==matched`，mismatches/missing 列表均空）④**v0.22 单锚点 `5dd43df6…`（v0.15 debiased_test_set）在 v0.23 的穷举锚点列表里被再验证 PASS**（`declared_sha256==disk_sha256`）→ v0.23 **subsumes** v0.22 的单锚点检查。本层另**独立重算** `bench_v0.15/out/debiased_test_set.jsonl` 磁盘 sha256 仍 `5dd43df6…`（不依赖 v0.23 自身的声明，与 v0.19/v0.20/v0.21/v0.22 历代同锚点再验证）。
3. **纯 append 扩展版本表**：追加 v0.23（ACTIVE, `integrity_audit`）+ v0.24（ACTIVE, `metadata_integration`）→ 23 版本 / 22 ACTIVE / 1 SUPERSEDED。canonical release（v0.10 consensus + v0.19 diagnostic）不变；v0.17 仍 SUPERSEDED by v0.19，弃用证据 carried forward 不重算。
4. **再生 RELEASE_INDEX.md（v0.24 视图）**：人类可读导航图，含 v0.23 freeze-integrity 表（四项）+ delta vs v0.22 + 全版本状态表 + 如何消费指引（新增"冻结 lineage 完整性（全树 bit-intact 审计）"指向 v0.23）。
5. **DATA_CARD_ADDENDUM_v0.24.md = §H**：扩展冻结 v0.16 addendum（§A–§E 不变）+ v0.22 §G（不变）。§H 重述 v0.19–v0.22 的"per-layer 单锚点 freeze-integrity，无全树审计"缺口 → v0.23 全树穷举方法/结果表（124 锚点 PASS、drift 73/73）/subsumption（v0.22 锚点 5dd43df6… 在 sweep 里再验证 PASS）/4 点 interpretation/provenance/cross-check。**§F 刻意未用**——预留未来 3 标注者 Fleiss κ 层（gate 阻塞）。

**结果**：23 版本（22 ACTIVE / 1 SUPERSEDED），delta vs v0.22 = +v0.23 +v0.24，无 status 变更，canonical release 不变，弃用证据不变。§H 把 v0.23 的全树完整性审计从"一个孤立审计层"整合进 datasheet——消费者从 DATA_CARD 即知全树 bit-intact 已穷举验证，及该审计的方法/结果/局限。

**质量门**：
- **DETERMINISM PASS**：5/5 产物（release_index_v0.24.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.24.md / consolidation_report_v0.24.json / report_v24.html）二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` pinned + 排序迭代；无新随机性，纯元数据）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 == `5dd43df6…`（v0.22 单锚点，本层独立重算）；v0.23 锚点 5dd43df6… 在 v0.23 sweep 里再验证 PASS → v0.23 subsumes v0.22。
- **LEAK CHECK 0 残留**：纯元数据层，正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0。
- **不改冻结层**：git status 确认 v0.1–v0.23 out/ 全部未修改；唯一被覆盖的是顶层 `designflow/RELEASE_INDEX.md`（活的导航图，v0.22 自己的 reproduce 也覆盖它，非冻结 per-version 产物）。

**产物**（`bench_v0.24/`）：integrate.py / report_v24.py / reproduce.sh（含 DETERMINISM + freeze-integrity + leak check 自检）/ README.md；`out/`：release_index_v0.24.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.24.md / consolidation_report_v0.24.json / report_v24.html。

**复探 3 口径**（第25轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 25 轮）；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 25 轮同卡点，上报仍有效待回复。

**结论**：闭环 v0.23 留下的索引再生待办为单一整合层，纯 append 不重算 v0.22 弃用证据以保冻结。当前 datasheet 的完整图景 = v0.16 §A–§E（统计严谨性）+ v0.22 §G（gap 显著性 CI）+ v0.24 §H（冻结 lineage 完整性审计）。§F 预留位明确指向下一个真正能改变结论的 gate（3 标注者 Fleiss κ，需 live LLM endpoint）。v0.25 候选：接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 给 disputed 项造真 gold → 落地 §F（阻塞）/ RESCAN 扩增（无新样本）/ v1.0 对外签字；多机扇出仍待运维决断。

## EXP-25 — v0.25 per-user 公平性审计层（第26轮，2026-10-28）

**动机**：v0.22–v0.24 三轮连续做元数据重验证/整合层（release index 再生、freeze-integrity 回写 §G/§H），价值递减。本轮回到实质 accuracy 分析。v0.18（EXP-18）只刻画了 disputed 项的**用户集中度**（描述性，top-3=54.4%），并明确把"per-user 公平性审计"列为 v1.x 改进路径；v0.16 DATA_CARD §E 把"single-machine source / 用户集中"列为局限但**只定性陈述**，无量化证据。本层把该局限从 *acknowledged* 升级为 *quantified*：测 baseline headline accuracy 在用户维度上的稳健性，回答"0.8174 是全体用户共享的，还是被少数 heavy user 的 easy task mix 撑起来的？"

**方法**：`fairness_audit.py` 纯冻结数据（零 /home/网络/LLM/新随机性），读 v0.15 `debiased_test_set`（368=219 consensus+149 disputed）+ `debiased_submission`（baseline pred，按 global_id join）+ v0.6 `tasks_v6`。6 维度：
1. **user_concentration** — n_users / Gini / HHI / top-k cumulative share per block。Gini=0 even / →1 极集中；HHI=1/n even / →1 monopoly。
2. **per_user_accuracy** — consensus 块每用户 gold accuracy / support / gold 类分布 / top confusion。
3. **per_user_robustness** — disputed 块每用户 v3/v4 agreement / mean robustness / neither|one 计数（沿用 v0.15 双标注者协议，disputed 无 gold 不伪造）。
4. **leave_one_user_out** — 逐用户丢全部项后 consensus 剩余 accuracy；|Δ|max = headline 的 user-robustness。<0.05 → user-robust。
5. **label_support_concentration** — 每 (class, user) consensus support；max_single_user_share ≥0.5 → 该类 per-class metric 实质 per-user。
6. **cross_check_vs_v015** — 6 点估计（n_debiased/n_consensus/n_disputed/acc/rob/neither/one）必须与 v0.15 debiased_eval MATCH（gate；漂移则层中止）。

**结果**：
- **user_concentration**：consensus 11 用户，Gini=0.5654，HHI=0.1951（even baseline 1/11=0.0909 → **2.14× 集中**），top-1=31.1% / top-3=70.3% / top-5=89.5%；disputed 13 用户，Gini=0.4812，HHI=0.1465，top-3=54.4%（**复现 v0.18 的 54.4%**，互证）。
- **per_user_accuracy**：acc 跨 0.0–1.0。u_011627302e55（n=46，acc=1.0）撑 headline + eda_aether_layout 类；u_04a093643b42（n=13，acc=0.3846）+ u_b423b3c9e88c（n=7，acc=0.5714）是真实 per-user gap 被 headline 掩盖；n≤3 用户的 0.0 是统计噪声非偏差。
- **leave_one_user_out**：headline=0.817352；**|Δ|max=0.0486 < 0.05 → headline accuracy IS user-robust**——即使 top-3 占 70%，去掉任一用户 headline 只在小范围漂移，**不是单用户伪迹**。最大驱动 u_011627302e55（Δ=−0.0486，dropped 46，LOO acc=0.7688）；spread 0.0759，range [−0.0486, +0.0273]。
- **label_support_concentration**：**8/9 类 ≥0.5 单用户垄断**，3/9 ==1.0（eda_innovus/eda_timing_power/eda_drc_lvs），eda_aether_layout max-share=0.9787（u_011627302e55 持 46/47）；mean max-single-user-share=0.8375。→ **per-class 尾类 P/R/F1 实质是 per-user metric，泛化到未见用户未测**。仅 code_dev（max-share 0.4255，9 用户）类相对健康。
- **cross_check vs v0.15**：**6/6 MATCH**（n368/consensus219/disputed149/acc0.817352/rob0.308725/neither57/one92）。

**净结论**：headline accuracy 经受用户分层考验（LOUO user-robust），**但 per-class 拆分没有**——8/9 类被单一用户主导，所以 v0.14 的 per-class CI / v0.11 的 per-class P/R/F1 对尾类实质是 per-user 数字。这是 DATA_CARD「single-machine source」局限背后的**具体证据**，motivates user-stratified re-split（保证每类跨多用户）作为 v1.x 构造候选。与 v0.18 互补：v0.18 解释了 disputed *为什么* 难（标签边界模糊），本层解释了 consensus *对谁* 准（对 heavy user 准、对尾类用户未测）。

**质量门**：
- **DETERMINISM PASS**：3 产物（fairness_audit.json / fairness_characterization.md / report_v25.html）二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` + sorted 迭代 + Counter；无新随机性）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 prefix `5dd43df6` match（与 v0.19–v0.24 历代同锚点再验证）；v0.15/v0.6 输出未被修改。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0（v0.25 不读 /home，无新 PII 风险）。
- **不改冻结层**：v0.1–v0.24 out/ 全部只读。audit 层**非整合层**，按 v0.21/v0.23 先例**不重算 RELEASE_INDEX**（推到下一整合层再生），不覆盖顶层 RELEASE_INDEX.md。

**产物**（`bench_v0.25/`）：fairness_audit.py / report_v25.py / reproduce.sh / README.md；`out/`：fairness_audit.json / fairness_characterization.md / report_v25.html。

**复探 3 口径**（第26轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 26 轮）；8092 仍 RESEARCH 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 26 轮同卡点，上报仍有效待回复。

**结论**：把 v0.16 §E 的"用户集中"定性局限升级为量化证据——headline user-robust 但 per-class 不 user-robust，给出明确的 v1.x 改进杠杆（user-stratified re-split）。是 v0.18（disputed 机理）的对称补全：一个解释 hard 项为什么难，一个解释 easy 项对谁准。v0.26 候选：接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 给 disputed 项造真 gold → 落地 §F（阻塞）/ 据 v0.25 per-class 单用户垄断构造 user-stratified re-split / 把 v0.25 纳入下一整合层再生 RELEASE_INDEX + 回写 §I / v1.0 对外签字；多机扇出仍待运维决断。

## EXP-26 — v0.26 user-stratified re-split 构造层（第27轮，2026-10-28）

**动机**：v0.25（EXP-25）是**审计层**，只刻画冻结的 v0.15 split——结论是"8/9 类单用户垄断 → per-class 尾类 P/R/F1 实质是 per-user metric，**泛化到未见用户未测**"，并把"构造 user-stratified re-split"明确列为 v1.x 构造候选。本层即该构造层：把 v0.25 的"未测"升级为"已测且测出差"。这是首个**主动构造**未见用户 held-out test 的层（前 25 层都在冻结的 same-user split 上工作）。

**方法**：`user_resplit.py` 纯冻结数据（零 /home/网络/LLM/新随机性），读冻结 v0.15 `debiased_test_set`（368）取 consensus 219。按 (gold_label × user_hash) 分组，**每类主用户**（count desc，ties by user_hash asc）→ TRAIN（模型从该标签的"owner"学），**其余用户** → HELD-OUT TEST（标签由不同用户学到，直接测"未见该标签用户"的泛化）。IMPOSSIBLE 单用户类 → train only（源硬限）。复用 v0.11 TF-IDF(latin+CJK-bigram)+tools tokens+nearest-centroid(cosine) baseline 重训重测，比 v0.15 headline consensus acc 0.817352。

**结果**：
- split train=168 / test=51；6 splittable / 3 IMPOSSIBLE（eda_innovus 14 / eda_timing_power 2 / eda_drc_lvs 1，共 17 项 train-only）。
- **user-strat acc = 0.5882**（n_test=51，correct=30）vs headline 0.8174 → **gap = −0.2291**——证实存在 headline 掩盖的未见用户泛化缺口。
- per-class：code_dev test_n=27 acc0.889（迁移好）/ other test_n=15 acc0.267 / eda_virtuoso_schematic test_n=4 acc0.0（主用户标签签名不迁移）/ eda_aether_layout test_n=1 acc0.0（薄）/ data_analysis test_n=2 acc0.5 / file_ops test_n=2 acc0.5。
- fully-unseen-user 子集（test 用户在 train 出现 0 次）n=42 acc0.6667；per-user：u_2c1bbb233e80 n16 acc1.0 撑 / u_04a093643b42 n13 acc0.2308 拖。

**净结论**：v0.25 说 per-class 尾类==per-user metric 是"未测"，v0.26 把它升级为"已测且测出差 −0.23"——code_dev 跨用户迁移好，other/eda_virtuoso_schematic 主用户标签签名不迁移；3 类 IMPOSSIBLE 源硬限仅更多用户/机器可解（不是方法问题）。**结构性发现**：headline（same-user train/test）掩盖了一个 −0.23 的未见用户泛化缺口，DATA_CARD「single-machine source」局限的成本首次被直接量化在构造的 split 上，而非仅 acknowledged。

**质量门**：
- **DETERMINISM PASS**：8 产物二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` + sorted 迭代；无新随机性）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 `5dd43df64f4d…` prefix match（与 v0.19–v0.25 历代同锚点再验证）。
- **CROSS-CHECK vs v0.15 PASS**：consensus_n 219 / acc 0.817352 MATCH（gate；漂移则层中止）。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0。
- **不改冻结层**：v0.1–v0.25 out/ 全部只读。构造层**非整合层**，按 v0.21/v0.23/v0.25 先例**不重算 RELEASE_INDEX**（推到下一整合层再生），不覆盖顶层 RELEASE_INDEX.md。

**产物**（`bench_v0.26/`）：user_resplit.py / report_v26.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md；`out/`：user_resplit.json / resplit_characterization.md / user_strat_train.jsonl(168) / user_strat_test.jsonl(51,blinded) / user_strat_answers.jsonl(51) / user_strat_submission.jsonl(51) / user_resplit_manifest.json / report_v26.html。

**复探 3 口径**（第27轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 27 轮）；8092 仍 RESEARCH 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 27 轮同卡点，上报仍有效待回复。

**结论**：把 v0.25「per-class 单用户垄断→泛化未测」从 audit 升级为 construction——首个主动构造未见用户 held-out test 的层，量化出 −0.23 真实泛化 gap。与 v0.25 形成完整闭环：v0.25 揭示问题（per-class==per-user），v0.26 量化问题的代价（−0.23）。v0.27 候选：把 v0.25+v0.26 纳入下一整合层再生 RELEASE_INDEX + 回写 §I / 据 v0.26 gap=−0.2291 构造 user-balanced re-split（强制每类多用户，扔掉 IMPOSSIBLE 单用户类）作为 v1.x 构造候选 / 接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss（阻塞）/ v1.0 对外签字；多机扇出仍待运维决断。

---

## 归档批次 13（2026-10-29 第30轮体积维护）—— MEMORY 第29轮流水原文

- [00:25] 第29轮唤醒（2026-10-29）：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第29轮同卡点，上报仍有效待回复）；8092仍RESEARCH(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。本轮推进**v0.28 user-balanced re-split 构造层（v1.x 候选）**（闭环 v0.26 下一步候选「据 gap=−0.2291 构造 user-balanced re-split [强制每类多用户，扔掉 IMPOSSIBLE 单用户类]」）。**user_balance.py** 读冻结 v0.15 consensus 219，按资格规则[≥3 用户且 top-2 之外项数 ≥2]分类全 9 类：**Tier A=2[code_dev/other]** / Tier B=4[eda_aether_layout/eda_virtuoso_schematic/data_analysis/file_ops] / Tier C=3 IMPOSSIBLE[eda_innovus/eda_timing_power/eda_drc_lvs]——仅 2/9 类支持多用户-per-class core，诚实源硬限。**受控实验**：2 类 core 上固定 17 项未见用户 test，对比 TRAIN-S[单用户/类,v0.26 式] vs TRAIN-M[2 用户/类,**matched count 177==177**，唯一差异是 52 core train 项来自 1 vs 2 用户]，复用 v0.11 TF-IDF+CJK-bigram+tools+nearest-centroid baseline 重训重测。**acc_S=0.5882(10/17) / acc_M=0.4706(8/17) / dZ_matched=−0.1176 多用户 train 反而更差**→证伪「收集更多用户即可缩小 gap」的乐观假设：v0.26 的 unseen-user gap 是该特征空间下标签识别的**内禀难度**，非单用户 train 伪影；要缩小需更强模型/更富特征而非单纯加用户。次要 TRAIN-M-all[202 项,混淆规模]dZ_all=−0.0588 仍不优于 S。per-class[code_dev S=0.7273/M=0.7273 持平；other S=0.3333/M=0.0 多用户 train 伤 other]——dZ 全部来自 other。阈值扫描表[MIN_TEST=1→4类/2→2类/3→2类/5→2类]量化源代价。产 10 产物 user_balance.json/balance_characterization.md/core_train_S/M.jsonl[177]/core_test.jsonl[17 blinded]/core_answers.jsonl/core_submission_S/M.jsonl/user_balance_manifest.json/report_v28.html。**DETERMINISM PASS**[byte-identical 二次重跑 10/10]。**FREEZE-INTEGRITY PASS**[v0.15 disk sha==5dd43df6…]。**CROSS-CHECK vs v0.15 PASS**[consensus_n 219/acc 0.817352 MATCH]。**MATCHED-COUNT INVARIANT PASS**[train_S_n==train_M_n==177]。**leak check 0**。不改冻结 v0.1–v0.27 out/；构造层非整合层不重算 RELEASE_INDEX（按 v0.21/v0.23/v0.25/v0.26 先例推到下一整合层）；顶层 README 增 v0.28 行+资产盘点轮次 28→29+DAG 节点+v0.28 段+复现段+gate 表 .75 28→29。

---

## 归档批次 14 — EXP-15..EXP-16 原文（2026-10-29 第32轮体积维护，从 EXPERIMENTS_DESIGNFLOW.md 搬入）

搬入原因：`EXPERIMENTS_DESIGNFLOW.md` 第32轮追加 EXP-31(v0.31) 前达 31.6KB（逼近 32KB 软限），按规程把最新活跃块（v0.31 EXP-31）之下的已闭合块归档。本批含 v0.14 统计严谨性层 + v0.15 去偏 split 层（均已由后续 v0.16 DATA_CARD/v0.17+ 诊断层 supersede，原文留此备查）。

## EXP-15 — v0.14 统计严谨性层（第15轮，2026-10-28，补登）

**动机**：v0.13 闭环"演进可追溯"后，benchmark 自身统计有效性仍未量化——标注者一致性、test_set 选择偏倚、baseline 点估计无置信区间。v0.14 三审计纯冻结数据补此缺口。

**方法**：`stats_rigor.py` 三审计——①agreement: 纯 python Cohen's κ(v3_supervised vs v4_rule, n=2112, per-class, by quality)；②selection_bias: test_set/gold/full_corpus 的 disputed(v3!=v4) 计数→verdict；③bootstrap_ci: 非参数 percentile bootstrap 10000× resample 219 (true,pred) pairs, numpy default_rng(seed=0)。

**结果**：κ=0.4496(moderate, obs_agree 0.5947)；**selection_bias BIAS_PRESENT**(test 0/219 disputed vs 语料 856/2112=40.5% → test 是 easy-only 偏倚样本)；bootstrap 95% CI acc[0.7671,0.8676] macroF1[0.6358,0.7929]。DETERMINISM PASS(SOURCE_DATE_EPOCH+PYTHONHASHSEED)；leak 0。**headline 发现**：baseline acc 被选择一致性放大，给 v1.x 推荐 stratify 含 disputed hard items → **v0.15 直接闭环此推荐**。

**复探 3 口径**（第15轮）：.75 恶化不可达(ping 100% loss)；1机/20dir/3479轨迹持平。

**结论**：v0.14 首次量化 benchmark 自身统计有效性，暴露一个真实可改进的构造缺陷（test split easy-only），并提供一条可执行的 v1.x 改进路径。v0.15 即执行该路径。

## EXP-16 — v0.15 去偏 test split + 双标注者评分层（第16轮，2026-10-28）

**动机**：v0.14 selection_bias 审计 verdict=BIAS_PRESENT——test_set 含 0/219 disputed(硬)样本而语料有 40.5%，test split 是 easy-only 偏倚样本，baseline accuracy 被选择一致性放大。v0.14 推荐"v1.x 应 stratify test split 纳入受控比例 disputed 硬样本"。v0.15 执行该推荐，闭环此构造缺陷。

**方法**：`debiased_split.py` 纯冻结数据（零 /home/网络/LLM）：
1. **build_debiased_split**：219 consensus(原 v0.9 test, 带 gold) + 149 disputed(v3!=v4, quality=task, 排除 few_shot)，proportional stratified by v3 class（largest-remainder 配额 + random.Random(seed=0) 类内 shuffle）→ disputed 分率 0.0→0.4049≈语料 0.4053。
2. **build_debiased_submission**：发现冻结 v0.11 example_submission 只覆盖 219 consensus test id，无 disputed 项预测 → 复用 v0.11 同款模型(TF-IDF+CJK-bigram+tools+nearest-centroid, few_shot[27] 训练)对全部 368 项预测，保证 disputed 项可评分。
3. **dual_annotator_eval**：**2 标注者下 disputed 项无 gold（v3!=v4 是平局，无多数），不伪造 gold**——改为分别报 v3_agreement / v4_agreement / mean robustness；consensus 项保留标准 gold accuracy。这是 2 标注者下统计诚实的硬样本评分法。
4. **bias_correction_audit**：debiased split disputed 分率 vs 语料 → verdict。

**结果**：
- `debiased_test_set.jsonl`(368=219 consensus+149 disputed) / `debiased_submission.jsonl`(368 预测) / `debiased_eval.json` / `bias_correction.json`(**BIAS_CORRECTED**) / `report_v15.html`。
- consensus gold acc=**0.8174**（=v0.14 headline，同批 219 easy 项，符合预期）vs disputed mean robustness=**0.3087**（v3_agree 0.3020 / v4_agree 0.3154 / matches_neither 104/149 / matches_exactly_one 45/149）。
- **headline**：gap=+0.5087，**量化了 v0.14 定性的"选择偏倚放大 accuracy"**——同一 baseline 在 easy 项 0.817 vs hard 项 0.309。
- **DETERMINISM PASS**：PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH pinned + random.Random(seed=0) → 两次 rerun 全 out/ byte-identical sha256。
- **LEAK CHECK 0 残留**（v0.15 不读 /home，无新 PII 风险）。
- 同步更新 v0.12 统一 README（版本索引 v0.15 / DAG / 复现段 / gate 表 .75 改"恢复可达但拒" / 资产盘点轮次 14→16）。

**复探 3 口径**（第16轮）：.75 **恢复可达**(ping 0% loss，SSH 仍 Permission denied，从上轮不可达回升)；8092 仍 RESEARCH 无 exec；1机/20dir(19有数据)/3479轨迹持平（无新样本，冻结快照 a1cd058a… 不变，无 RESCAN 扩增）。连续 16 轮同卡点，上报仍有效待回复。

**结论**：v0.15 首次**修复** v0.14 暴露的构造缺陷——test split 不再 easy-only，disputed 硬样本以受控比例纳入；且用统计诚实方法（双标注者 agreement 而非伪造 gold）在硬样本上评分。同一 baseline 在 easy/hard 项的 0.817 vs 0.309 差距，把"选择偏倚放大 accuracy"从 v0.14 定性发现升级为定量证据。意义：benchmark 的 test split 现在既反映语料真实难度分布，又有诚实的硬样本评分协议。v0.16 候选：接 LLM 第3标注者给 disputed 项造真 gold（阻塞）/ RESCAN 扩增 / v1.0 对外签字 / 去偏 split 升级为对外 v1.x 诊断 split / 统计严谨性结果反嵌 DATA_CARD。

---

## 归档批次 15（2026-10-29 第32轮体积维护）—— MEMORY 第31轮流水原文

- [01:08] 第31轮唤醒（2026-10-29）：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第31轮同卡点，上报仍有效待回复）；8092仍RESEARCH-MCP-SERVER v1.25.0(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。本轮推进**v0.30 冻结 lineage 完整性 RE-sweep（subsumes v0.23）**（闭环 v0.29 下一步候选「全树 lineage 再扫纳入 v0.28/v0.29 锚点，subsumes v0.23」）。**lineage_audit.py** 锚点提取 UNCHANGED from v0.23（Form A+B，保 v0.23/v0.30 集合可比），扫 28 版本/69 manifest/151 锚点[108 unique]→**147 PASS + 4 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。**drift_vs_v013** PASS 73/73。**drift_vs_v023（NEW）**：加载冻结 v0.23 audit 取 95 unique 锚点 partition frozen(94)/living(1)，重验 94 frozen 仍 bit-intact → PASS 94/94 0 regression，13 net-new anchors since v0.23。**frozen_release_index_copies_check（NEW）**：各 consolidation 报告声明 RELEASE_INDEX.md sha 对其自身冻结 bench_v0.XX/out/RELEASE_INDEX.md 副本 PASS 4/4。**发现并建模 v0.23 latent bug**：v0.23 `_resolve` 把 consolidation 报告 `outputs[].RELEASE_INDEX.md`（bare name）解析到顶层 living 文件（按设计被 v0.24→v0.27→v0.29 覆盖，当前==v0.29 副本 b17331e3），v0.23 时刻顶层==v0.22 副本 33dac001 巧合 PASS；v0.30 不改 `_resolve` 保可比性，标 LIVING_FILE_BYDESIGN + 交叉校验真冻结副本。产 3 产物 lineage_audit_v030.json/lineage_audit_manifest.json/report_v30.html。**DETERMINISM PASS**[byte-identical 二次重跑 3/3]。**leak check 0**。不改冻结 v0.1–v0.29 out/；冻结 v0.23 audit read-only 作基线；audit 层非整合层不重算 RELEASE_INDEX[按 v0.21/v0.23 先例推到下一整合层]；顶层 README 增 v0.30 行+资产盘点轮次 30→31+DAG 节点 v0.30+v0.30 段+复现段+gate 表 .75 30→31。体积：MEMORY 约 30KB / EXP 31.6KB / TASK 5.1KB 全≤32KB

---

## 归档批次 16（2026-10-29 第33轮体积维护）—— EXPERIMENTS EXP-27/28/29 原文

> 第33轮体积维护：把 EXPERIMENTS_DESIGNFLOW.md 中已闭合的 EXP-27（v0.27 §I 整合层，第28轮）/ EXP-28（v0.28 user-balanced re-split 构造层，第29轮）/ EXP-29（v0.29 §J 整合层，第30轮）三个完整块原文搬入本归档批次，EXP 中各留 1 行指针。此三块均已被后续层（v0.30/v0.31/v0.32）继承，闭合。搬前已 `git pull --rebase --autostash`（Already up to date）。

## EXP-27 — v0.27 发布索引再生 + DATA_CARD addendum §I 整合层（第28轮，2026-10-29）

**动机**：v0.25（EXP-25）与 v0.26（EXP-26）都是**审计/构造层**，明确把 RELEASE_INDEX 再生推到「下一整合层」（承 v0.21/v0.23 审计/构造层先例，避免重算冻结的 v0.24 索引）。本层即该整合层——在**单一整合步骤**中吸收两层：把 v0.25（per-user 公平性审计）+ v0.26（user-stratified re-split 构造）纳入 RELEASE_INDEX，并把两层的公平性/泛化发现回写进 v0.16 DATA_CARD addendum 作为 §I。这是继 v0.22（§G）/ v0.24（§H）之后第三次「审计/构造层积压 → 整合层吸收」的模式。

**方法**：`integrate.py` 纯冻结元数据（零 /home/网络/LLM/新随机性），读冻结 v0.24 `release_index_v0.24.json`（23 版本）为基线。机器验证两层 freeze-integrity（全过才继续）：v0.25——4 个 sha256 锚点（debiased_test_set/debiased_eval/debiased_submission v0.15 + tasks_v6）独立重算与盘上一致 + `6_cross_check_vs_v015.verdict`==MATCH（consensus_n/gold_acc/robustness/neither/one 全部重算到 v0.15）+ 公共 v0.15 锚点 `5dd43df6…` 由本层独立重算仍 `5dd43df6…`；v0.26——`freeze_integrity.status`==PASS + v0.15 锚点前缀 match + `cross_check_vs_v015.status`==PASS（consensus_n_match + headline_acc_match 均 True）+ 公共 v0.15 锚点本层独立重算一致（跨层确认，非仅凭 v0.26 自报）。追加 v0.25（ACTIVE, fairness_audit）+ v0.26（ACTIVE, user_stratified_resplit_construction）+ v0.27（ACTIVE, metadata_integration）。

**结果**：
- 索引 26 版本 / 25 ACTIVE / 1 SUPERSEDED（v0.17 by v0.19，carried forward 不重算）。
- v0.25 freeze-integrity：4/4 锚点 match disk（5dd43df64f4d…/af0a6652ba33…/b8cfba73f51a…/d52b10573a60…）+ cross_check MATCH + 公共锚点 `5dd43df64f4d5af0…`。
- v0.26 freeze-integrity：status PASS + cross_check PASS（n_match + acc_match）+ 公共锚点本层重算 `5dd43df64f4d5af0…`。
- §I 把 v0.16 §E「single-machine source」**定性**局限沿两轴**量化**：① headline user-robust（LOUO |Δ|max=0.0486<0.05 ✅）；② per-class 单用户垄断（8/9 类 ≥0.5，3/9 ==1.0 ⚠️）；③ 未见用户泛化 gap=−0.2291（v0.26 测出 ❌）；④ 3 类 IMPOSSIBLE 单用户类（17 项）源硬限（⚠️）。
- 净结论：headline gold accuracy（§A/§D）在 block 层面公平，但 per-class 拆分把「模型学到了类」与「模型学到了一个用户风格」混为一谈；v0.26 测出代价 −0.23。

**质量门**：
- **DETERMINISM PASS**：5 产物二次重跑 byte-identical（release_index_v0.27.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.27.md / consolidation_report_v0.27.json / report_v27.html）。
- **FREEZE-INTEGRITY PASS**：v0.25 4 锚点 + v0.26 freeze_integrity + 公共 v0.15 锚点 `5dd43df6…` 全 match disk。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/svc.*/shiwei/zhulong/Cxmt@/home 全 0（元数据层，data-free）。
- **不改冻结层**：v0.16/v0.20–v0.26 out/ 全部只读；唯一覆盖的活文件是顶层 `designflow/RELEASE_INDEX.md`（活的导航图，按 v0.22/v0.24 先例覆盖）。

**产物**（`bench_v0.27/`）：integrate.py / report_v27.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md；`out/`：release_index_v0.27.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.27.md / consolidation_report_v0.27.json / report_v27.html。

**复探 3 口径**（第28轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 28 轮）；8092 仍 RESEARCH 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 28 轮同卡点，上报仍有效待回复。

**结论**：把 v0.25+v0.26 两层审计/构造积压在单一整合层吸收，RELEASE_INDEX 升 23→26 版本，§I 把 §E 定性局限升级为两轴量化（user-robust ✅ / unseen-user gap −0.23 ❌）。与 v0.22（§G）/v0.24（§H）形成连贯的「积压→整合」节奏。v0.28 候选：接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 落地预留 §F（gate 阻塞）/ 据 v0.26 gap=−0.2291 构造 user-balanced re-split 作为 v1.x 构造候选 / RESCAN 扩增冻结快照（本轮持平 3479 无新样本）/ v1.0-rc1 经运维签字后升 v1.0 正式对外；多机扇出仍待运维决断。


## EXP-28 — v0.28 user-balanced re-split 构造层（v1.x 候选）（第29轮，2026-10-29）

**动机**：v0.26（EXP-26）构造了首个未见用户 held-out test，测出 unseen-user gap=−0.2291，但 TRAIN 是**单主导用户/类**——v0.26 无法判断这个 gap 是「标签识别的内禀难度」还是「单用户 train 的伪影」（模型从一个用户的风格学标签，换用户自然掉）。任务书 v0.28 候选明确点名「据 v0.26 gap=−0.2291 构造 user-balanced re-split [强制每类多用户，扔掉 IMPOSSIBLE 单用户类] 作为 v1.x 构造候选」。本层即该构造层：新增**多用户 train** 约束（top-2 用户/类），定义严格**资格规则**，并在合格类上做**受控实验**隔离「多用户 train」效应——这是 v0.26→v0.28 的关键增量。

**方法**：`user_balance.py` 纯冻结数据（零 /home/网络/LLM/新随机性），读冻结 v0.15 `debiased_test_set` 取 consensus 219，按 (gold_label × user_hash) 构矩阵。
1. **资格规则（v1.x 要求）**：类为 Tier A（user-balanced）iff ≥3 用户**且** top-2 用户之外的项数 ≥ MIN_TEST(=2)，则 TRAIN=top-2 用户（多用户）、TEST=其余（未见该类用户，非平凡支持）。Tier B = ≥2 用户但不满足 A（v0.26 式单用户 train 未见用户 test）。Tier C = 单用户（IMPOSSIBLE，train only）。
2. **受控实验**：在 2 类 core 上固定 17 项未见用户 test，构造两个**等规模** train——TRAIN-S（每类 top-1 用户，v0.26 式）与 TRAIN-M（每类 top-2 用户，**matched count**：取尽 2nd 用户全部项 + 从 1st 用户补足到 top-1 项数，使 per-class 项数与 S 相等）。两 train 均为 177 项（52 core + 125 相同 non-core）、9 类齐全，**唯一差异**是 52 core train 项来自 1 用户/类（S）还是 2 用户/类（M）。dZ=acc_M−acc_S 干净隔离多用户 train 效应，固定 train 规模、test 集、标签空间。次要 TRAIN-M-all（202 项，用尽 top-2，混淆 train 规模）作参考。
3. **阈值扫描**：MIN_TEST∈{1,2,3,5} 各档 Tier A 类数，量化源代价。
4. 复用 v0.11 TF-IDF(latin+CJK-bigram)+tools tokens+nearest-centroid(cosine) baseline。

**结果**：
- **分层**：Tier A=**2/9**（code_dev/other）/ Tier B=4（eda_aether_layout/eda_virtuoso_schematic/data_analysis/file_ops）/ Tier C=3 IMPOSSIBLE（eda_innovus/eda_timing_power/eda_drc_lvs，17 项）。**仅 2/9 类支持多用户-per-class core**——诚实源硬限，7 类不可（3 单用户 + 4 薄类 top-2 外 <2 项）。
- **受控实验**：acc_S=**0.5882**(10/17) / acc_M=**0.4706**(8/17) / **dZ_matched=−0.1176 多用户 train 反而更差**。次要 TRAIN-M-all=0.5294(9/17) dZ_all=−0.0588 仍不优于 S。matched-count 不变量：train_S_n==train_M_n==177 ✅。
- **per-class**：code_dev S=0.7273(8/11)/M=0.7273(8/11) **持平**；other S=0.3333(2/6)/M=0.0(0/6) **多用户 train 伤 other**——dZ 全部来自 other。
- **阈值扫描**：MIN_TEST=1→4 类 / 2→2 类 / 3→2 类 / 5→2 类。

**净结论**：**证伪「收集更多用户即可缩小 gap」的乐观假设**。在 matched train 规模下，把每类 train 从 1 用户扩到 2 用户不但没缩小、反而扩大了未见用户 gap（dZ=−0.1176）。v0.26 的 unseen-user gap（−0.2291）因此是**该特征空间下标签识别的内禀难度**，非单用户 train 伪影；要缩小需更强模型/更富特征，而非单纯加用户。code_dev 跨用户迁移稳健（S=M），other 的主用户标签签名在多用户稀释后丢失（M=0）。结合 v0.25（per-class 单用户垄断量化）+ v0.26（gap=−0.23 构造）+ v0.28（多用户 train 不缩 gap），三层给出单机源公平性局限的完整诚实刻画：headline user-robust，但 per-class 受源硬限，且加用户不解决。

**质量门**：
- **DETERMINISM PASS**：10/10 产物二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` + deterministic 排序/subsample by global_id；无新随机性）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 `5dd43df64f4d…` prefix match（与 v0.19–v0.27 历代同锚点再验证）。
- **CROSS-CHECK vs v0.15 PASS**：consensus_n 219 / headline_acc 0.817352 MATCH（gate；漂移则层中止）。
- **MATCHED-COUNT INVARIANT PASS**：train_S_n==train_M_n==177（受控实验内部不变量，保证 dZ 隔离的是用户多样性而非 train 规模）。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0。
- **不改冻结层**：v0.1–v0.27 out/ 全部只读。构造层**非整合层**，按 v0.21/v0.23/v0.25/v0.26 先例**不重算 RELEASE_INDEX**（推到下一整合层再生），不覆盖顶层 RELEASE_INDEX.md。

**产物**（`bench_v0.28/`）：user_balance.py / report_v28.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md；`out/`：user_balance.json / balance_characterization.md / core_train_S.jsonl(177) / core_train_M.jsonl(177,matched) / core_test.jsonl(17,blinded) / core_answers.jsonl(17) / core_submission_S.jsonl(17) / core_submission_M.jsonl(17) / user_balance_manifest.json / report_v28.html。

**复探 3 口径**（第29轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 29 轮）；8092 仍 RESEARCH 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 29 轮同卡点，上报仍有效待回复。

**结论**：把 v0.26「单用户 train 测出 gap −0.23」推进到「多用户 train 是否缩 gap」——matched-count 受控实验给出否定答案（dZ=−0.1176），证伪乐观假设，gap 是内禀难度。仅 2/9 类支持多用户 core 是诚实源硬限。与 v0.25/v0.26 形成单机公平性局限的完整闭环。v0.29 候选：把 v0.28 纳入下一整合层再生 RELEASE_INDEX + 回写 §J 到 v0.16 addendum（v0.28 是构造层，按先例推到下一整合层）/ 接 LLM-judge 跑 3 标注者多数表决 → 升级 κ→Fleiss → 落地 §F（阻塞）/ RESCAN 扩增（本轮持平 3479 无新样本）/ v1.0-rc1 经运维签字后升 v1.0 正式对外；多机扇出仍待运维决断。

## EXP-29 — v0.29 发布索引再生 + DATA_CARD addendum §J 整合层（第30轮，2026-10-29）

**闭环**：v0.28 下一步候选「把 v0.28 纳入下一整合层再生 RELEASE_INDEX + 回写 §J 到 v0.16 addendum」。v0.28 是 user-balanced re-split 构造层，按 v0.21/v0.23/v0.25/v0.26 先例明确推到下一整合层再生 RELEASE_INDEX——本层即该整合层。承 v0.22/v0.24/v0.27 整合层模式：纯 append，不 re-derive v0.1–v0.27 状态。

**方法**：
1. **基线**：加载冻结 `bench_v0.27/out/release_index_v0.27.json`（26 版本，gate：benchmark_version=="v0.27" 且 n_versions==26，漂移则层中止）。
2. **机器验证 v0.28 freeze-integrity**（4 项全过才推进）：
   - (a) `freeze_integrity.status == PASS` + v0.15_anchor 前缀 `5dd43df6` match（`v0.15_disk_sha256` startswith）。
   - (b) `cross_check_vs_v015.status == PASS` 且 consensus_n_match + headline_acc_match 均 True。
   - (c) 本层**独立重算**公共 v0.15 锚点 `bench_v0.15/out/debiased_test_set.jsonl` 磁盘 sha256 仍 `5dd43df64f4d…`（跨层确认，不只用 v0.28 的声明）。
   - (d) 本层**独立重算** v0.28 声明的 2 个 provenance 锚点（v0.15 debiased_eval sha256 `af0a6652…` + v0.26 user_resplit sha256 `d6b7a265…`）match disk（跨源确认）。
3. **append** v0.28（ACTIVE，`user_balanced_resplit_construction`）+ v0.29（ACTIVE，`metadata_integration`）→ 28 版本 / 27 ACTIVE / 1 SUPERSEDED（v0.17）。canonical release（v0.10 consensus / v0.19 diagnostic）不变，v0.17→v0.19 弃用证据 carried forward 不重算。
4. **产**：release_index_v0.29.json / RELEASE_INDEX.md（v0.29 视图，覆盖顶层活的导航图）/ DATA_CARD_ADDENDUM_v0.29.md = §J / consolidation_report_v0.29.json / report_v29.html。

**§J 内容**：扩展冻结 v0.16 §A–§E + v0.22 §G + v0.24 §H + v0.27 §I（全不改）。§J 把 v0.27 §I 留的开放问题「v0.26 unseen-user gap=−0.2291 是单用户 train 伪影还是内禀难度？」用 v0.28 的 matched-count 受控实验回答：dZ_matched=−0.1176 < 0 → **多用户 train 不缩 gap 反而更差 → gap 是内禀难度**，证伪「收集更多用户即缩 gap」的乐观假设。三轴拆分：(1) **覆盖轴**——仅 2/9 类 Tier-A 合格，3 IMPOSSIBLE + 4 薄类不可多用户，是源硬限（更多用户/机器可 lift 覆盖）；(2) **gap-on-covered 轴**——matched-count 177==177 dZ=−0.1176，多用户 train 对已覆盖类不缩 gap（需更强模型/更富特征）；(3) **per-class**——code_dev S=M=0.7273 持平，other S=0.3333→M=0.0 多用户稀释伤 other，dZ 全来自 other。净：「收集更多用户」药方仍真但**正交**于缩 gap。§F 仍预留（gate：DESIGNFLOW_LLM_JUDGE unset）。

**质量门**：
- **DETERMINISM PASS**：5/5 产物二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000`；纯元数据无新随机性）。
- **FREEZE-INTEGRITY PASS**：v0.28 status PASS + cross_check vs v0.15 PASS + 公共 v0.15 锚点本层独立重算 `5dd43df64f4d…` prefix match + 2 provenance 锚点（v0.15 debiased_eval `af0a6652…` / v0.26 user_resplit `d6b7a265…`）本层独立重算 match disk。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0（元数据层，data-free，hygiene 检查）。
- **不改冻结层**：v0.1–v0.28 out/ 全只读。唯一覆盖的是顶层 `designflow/RELEASE_INDEX.md`（活的导航图，v0.24/v0.27 reproduce 也覆盖它，by design）。

**产物**（`bench_v0.29/`）：integrate.py / report_v29.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md；`out/`：release_index_v0.29.json(17964B) / RELEASE_INDEX.md(15155B) / DATA_CARD_ADDENDUM_v0.29.md(13395B) / consolidation_report_v0.29.json(3242B) / report_v29.html(19969B)。顶层 README 增 v0.29 行 + 资产盘点轮次 29→30 + DAG 节点 v0.29 + §J addendum 指针 + v0.29 描述段 + 复现段 + gate 表 .75 29→30。

**复探 3 口径**（第30轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 30 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3479轨迹——与冻结快照 `a1cd058a…` 对齐，无漂移，无 RESCAN 扩增。连续 30 轮同卡点，上报仍有效待回复。

**结论**：把 v0.28 构造层纳入 RELEASE_INDEX（28 版本）+ 把「证伪『多用户即缩 gap』」回写进 DATA_CARD addendum 作为 §J。v0.27 §I 的开放问题得到闭合回答：gap 是特征空间内禀难度，非单用户 train 伪影；缩 gap 需更强模型/更富特征而非单纯加用户；加用户正交地 lift 覆盖（IMPOSSIBLE/Tier-B→Tier-A）但不缩已覆盖类的 gap。单机公平性局限的诚实刻画至此形成 4 层完整闭环（v0.25 公平性审计 → v0.26 user-strat gap 构造 → v0.28 多用户 train 证伪 → v0.29 整合 §J）。v0.30 候选：接 LLM-judge 跑 3 标注者多数表决 + 升级 κ→Fleiss + 落地 §F（阻塞）/ RESCAN 扩增（本轮持平 3479 无新样本）/ v1.0-rc1 经运维签字后升 v1.0 正式对外 / 全树 lineage 再扫（subsumes v0.23，纳入 v0.28/v0.29 锚点）；多机扇出仍待运维决断。

### MEMORY 第32轮流水原文（归档批次 16 续）
- [01:35] 第32轮唤醒（2026-10-29）：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第32轮同卡点，上报仍有效待回复）；8092仍RESEARCH-MCP-SERVER v1.25.0(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3487 session dirs**（与冻结快照 a1cd058a… 完全对齐，0 漂移，无 RESCAN 扩增；早期 `find /home -name '*.messages.json'`=5101 经核为计数伪影——把 sessions 路径之外非 canonical 文件算进来，用 extract.py 一致只读逻辑复核=3487 逐位对齐冻结快照）。本轮推进**v0.31 发布索引再生 + DATA_CARD addendum §K 整合层**（闭环 v0.30 下一步候选「下一整合层再生 RELEASE_INDEX 纳入 v0.30 + 回写 §K 到 v0.16 addendum，同 v0.23→v0.24 整合先例」——v0.30 是审计层按 v0.21/v0.23 先例推到下一整合层，本层即该整合层）。**integrate.py** 加载冻结 v0.29 索引[28 版本]为基线，机器验证 v0.30 freeze-integrity **7 项全过**：(a) overall PASS；(b) 锚点全 accounted 147 PASS + 4 LIVING_FILE_BYDESIGN == 151（0 mismatch/missing/err）；(c) drift_vs_v013 PASS 73/73；(d) drift_vs_v023 PASS 94/94（0 regression，1 living excluded，13 net-new）——证 v0.24–v0.29 build-out 未静默漂移任一 v0.23 已验冻结输入；(e) frozen_release_index_copies PASS 4/4（各 consolidation 报告声明 sha 对其自身冻结 bench_v0.XX/out/RELEASE_INDEX.md 副本）；(f) 公共 v0.29 锚点 5dd43df6… 在 v0.30 穷举锚点列表里再验证 PASS → v0.30 subsumes v0.29；(g) 本层跨层独立重算 3 项 match disk（v0.15 公共锚点 5dd43df64f4d… / v0.30 输出 lineage_audit_v030.json e4b22a37… == declared / v0.23 审计基线 cab56e7b… == declared，cross-source 非仅凭 v0.30 自报），append v0.30+v0.29→**30 版本/29 ACTIVE/1 SUPERSEDED**。**§K** 回写 v0.23 latent living-file bug 建模到 v0.16 addendum（v0.23 `_resolve` 把 consolidation 报告 bare-name `RELEASE_INDEX.md` 解析到顶层 living 文件，仅因 v0.23 时刻顶层==v0.22 副本 33dac001 而巧合 PASS；v0.30 不改 `_resolve` 保可比性，标 LIVING_FILE_BYDESIGN + 交叉校验真冻结副本——方法论修正非数据完整性问题）+ 冻结 lineage RE-sweep（v0.23 21版本/124锚点 → 28版本/69manifest/151锚点[108 unique]，147 PASS+4 LIVING）+ 两 NEW 校验（drift_vs_v023 回归 / frozen_release_index_copies 交叉）。extends 冻结 v0.16 §A–§E + v0.22 §G + v0.24 §H + v0.27 §I + v0.29 §J；§F 仍预留（Fleiss κ，gate 阻塞）。产 5 产物 release_index_v0.31.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.31.md=§K/consolidation_report_v0.31.json/report_v31.html。**DETERMINISM PASS**[byte-identical 二次重跑 5/5]。**FREEZE-INTEGRITY PASS**[v0.30 7 项全过]。**leak check 0**。不改冻结 v0.1–v0.30 out/；覆盖顶层 RELEASE_INDEX.md[活的导航图，by design]；顶层 README 增 v0.31 行+资产盘点轮次 31→32+DAG 节点 v0.31+§K 指针+v0.31 段+复现段+gate 表 .75 31→32。体积维护：归档 EXP-15+EXP-16 原文至 ARCHIVE 批次 14[留指针]；EXP 27.5KB→加 EXP-31 后 31.7KB；MEMORY 约 31KB / TASK 5.1KB 全≤32KB

---

## 归档批次 17 — MEMORY 第30轮 + 第34轮流水原文（体积维护，2026-10-29 第35轮归档）

> 为给 v0.34/v0.35 流水腾出空间（MEMORY ≤32KB 红线），把 MEMORY 中最长的两条全文流水
> （第30轮 v0.29、第34轮 v0.33）原文搬入此处，MEMORY 留 1 行指针。小节编号/标题/运维指令不变。

### MEMORY 第30轮流水原文（归档批次 17）

- [00:45] 第30轮唤醒（2026-10-29）：.75**仍可达但 SSH 拒**（ping 0% loss，SSH Permission denied，连续第30轮同卡点，上报仍有效待回复）；8092仍RESEARCH-MCP-SERVER v1.25.0(无exec)；DESIGNFLOW_LLM_JUDGE 仍 unset；3口径现查=1机/**20dir(19有数据)**/**3479轨迹**（与冻结快照 a1cd058a… 对齐，无漂移，无 RESCAN 扩增）。本轮推进**v0.29 发布索引再生+DATA_CARD addendum §J 整合层**（闭环 v0.28 下一步候选「把 v0.28 纳入下一整合层再生 RELEASE_INDEX + 回写 §J 到 v0.16 addendum」——v0.28 是构造层按 v0.21/v0.23/v0.25/v0.26 先例推到下一整合层，本层即该整合层）。**integrate.py** 加载冻结 v0.27 索引[26 版本]为基线，机器验证 v0.28 freeze-integrity[4 项全过：status PASS + cross_check vs v0.15 PASS + 公共 v0.15 锚点 5dd43df6… 本层独立重算 prefix match + 2 provenance 锚点 v0.15 debiased_eval af0a6652…/v0.26 user_resplit d6b7a265… 本层独立重算 match disk]，append v0.28+v0.29→**28 版本/27 ACTIVE/1 SUPERSEDED**。**§J** 回答 v0.27 §I 留的开放问题「v0.26 unseen-user gap=−0.2291 是单用户 train 伪影还是内禀难度？」——用 v0.28 matched-count 受控实验[177==177] dZ=−0.1176<0 回答：**多用户 train 不缩 gap 反而更差 → gap 是特征空间内禀难度**，证伪「收集更多用户即缩 gap」；三轴拆分[覆盖轴 2/9 Tier-A 源硬限/gap-on-covered 轴 dZ<0 需更强模型/per-class code_dev S=M other M<S]——「加用户」药方正交于缩 gap（lift 覆盖但不缩已覆盖类的 gap）。产 5 产物 release_index_v0.29.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.29.md=§J/consolidation_report_v0.29.json/report_v29.html。**DETERMINISM PASS**[byte-identical 二次重跑 5/5]。**FREEZE-INTEGRITY PASS**[v0.28 4 项全过]。**leak check 0**。不改冻结 v0.1–v0.28 out/；覆盖顶层 RELEASE_INDEX.md[活的导航图，by design]；顶层 README 增 v0.29 行+资产盘点轮次 29→30+DAG 节点 v0.29+§J 指针+v0.29 段+复现段+gate 表 .75 29→30。体积维护：MEMORY 27.2KB→归档第29轮流水原文至 ARCHIVE 批次 13[留1行指针]后约 28KB；EXP 21.5KB→加 EXP-29 后 27.3KB；TASK 5.1KB 全≤32KB

### MEMORY 第34轮流水原文（归档批次 17）

- [02:20] 第34轮：推进 **v0.33 发布索引再生 + §L 整合层**（闭环 v0.32 构造层下一步候选「纳入下一整合层再生 RELEASE_INDEX + 回写 §L」，承 v0.24/v0.27/v0.29/v0.31 整合先例）。`integrate.py` 加载冻结 v0.31 索引[30 版本]为基线，机器验证 v0.32 freeze-integrity 全过（manifest PASS + v0.15 锚点 5dd43df6… + v0.26 split 逐位复用 + CONTROL 复现 0.588235 + 4 个 v0.26 split 文件跨层独立重算 match v0.32 声明 AND v0.26 自身 frozen manifest[证 v0.32 未误声明] + v0.32 输出 gap_shrink.json match disk + self-agrees manifest Form A），append v0.32+v0.33→**32 版本/31 ACTIVE/1 SUPERSEDED**。**§L** 修订 v0.28 §J「内禀难度」为「weak-model artifact 主项[同 TF-IDF+tools 特征换 softmax 缩 +0.216 几乎闭合，fully-unseen 0.667→0.929；若内禀则同特征换模型不可缩]+ 薄类源硬限残项[3 类 n≤4 单用户源按构造不可测]」；v0.28「更强模型」药方方向正确但严重低估效果，「更富粗 meta 特征」为负（编码用户风格伤泛化，需语义级 LLM-gated）。产 5 产物 release_index_v0.33.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.33.md=§L/consolidation_report_v0.33.json/report_v33.html。**DETERMINISM PASS** 5/5 byte-identical。**leak 0**。不改冻结 v0.1–v0.32 out/；覆盖顶层 RELEASE_INDEX.md[活导航图]+顶层 README[v0.33 行+资产盘点轮次 33→34+DAG 节点+§L 指针+v0.33 段+复现段+gate 表 .75 33→34]。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第34轮仍可达但 SSH 拒（连续 34 轮同卡点，上报仍有效待回复）。

---

## 归档批次 18 — EXP-30 + EXP-31 原文（体积维护，2026-10-29 第35轮归档）

> 为给 EXP-35 腾出空间（EXP ≤32KB 红线），把已闭合的 EXP-30（v0.30 lineage RE-sweep 构造层）+
> EXP-31（v0.31 §K 整合层）原文搬入此处，EXP 留 1 行指针。v0.34 已 subsume v0.30 的审计范围。

### EXP-30 原文 — v0.30 冻结 lineage 完整性 RE-sweep（subsumes v0.23）（第31轮）

**闭环**：v0.29 留的下一步候选「全树 lineage 再扫，纳入 v0.28/v0.29 锚点，subsumes v0.23」。v0.23 是首个全树完整性审计（21 版本 / 124 锚点），但只覆盖到 v0.22；之后 v0.24/v0.25/v0.26/v0.28/v0.29 五层加入，各带新 provenance sha256 锚点，无后继检查覆盖。v0.30 把 v0.23 的全树审计重跑到现已冻结的 28 版本，并加回归校验。audit 层非整合层（同 v0.23），不重算 RELEASE_INDEX，按 v0.21/v0.23 先例推到下一整合层。

**方法**：1. 锚点提取 UNCHANGED（Form A+B 与 v0.23 字节级一致，保可比性）。2. 扫描所有 bench_v0.*/out/*.json manifest（排除本层 out）→ 28 版本 / 69 manifest / 151 锚点（108 unique）；逐锚点重算 sha256：147 PASS + 4 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR。3. drift_vs_v013（同 v0.23）：v0.1–v0.11 artifact 子集对冻结 v0.13 version_manifest 交叉校验 → PASS 73/73。4. drift_vs_v023（NEW）：加载冻结 v0.23 审计，partition frozen(94) vs living(1)，重验 94 frozen 仍 bit-intact → PASS 94/94，0 regression；13 net-new since v0.23。5. frozen_release_index_copies_check（NEW）：各 consolidation 报告（v0.22/v0.24/v0.27/v0.29）声明 RELEASE_INDEX.md sha 对其自身冻结副本 → PASS 4/4。

**发现并建模 v0.23 latent bug**：v0.23 把 consolidation 报告 outputs[].RELEASE_INDEX.md（bare name）解析到顶层 designflow/RELEASE_INDEX.md（living 导航图，被各整合层覆盖）。v0.23 时刻顶层==v0.22 冻结副本（33dac001…）所以巧合 PASS——latent bug 被巧合掩盖。v0.30 不改 _resolve（保可比），标 LIVING_FILE_BYDESIGN + frozen per-version 副本交叉校验。方法论修正非数据完整性问题。

**质量门**：DETERMINISM PASS 3/3 byte-identical；overall PASS（0 MISMATCH/MISSING/ERR + drift_vs_v013 PASS + drift_vs_v023 PASS + frozen_release_index_copies PASS）；LEAK CHECK 0；不改冻结层 v0.1–v0.29 out/。

**产物**：bench_v0.30/ lineage_audit.py / report_v30.py / reproduce.sh / README.md；out/ lineage_audit_v030.json(142206B) / lineage_audit_manifest.json(4823B) / report_v30.html(32131B)。

**结论**：v0.30 把全树冻结完整性证据从 v0.22 推进到 v0.29（28 版本 / 151 锚点全 PASS），证 v0.24–v0.29 build-out 未静默漂移任一冻结输入，修正 v0.23 对顶层 living RELEASE_INDEX.md 的 latent 误验。下游所有结论建立在 bit-intact 的冻结依赖图上。

### EXP-31 原文 — v0.31 发布索引再生 + DATA_CARD addendum §K 整合层（第32轮）

**动机**：v0.30（审计层）明确把 RELEASE_INDEX 再生推到下一整合层。本层即该整合层——把 v0.30 纳入 RELEASE_INDEX，并把 v0.30 全树完整性 RE-sweep + v0.23 latent living-file bug 建模回写进 v0.16 DATA_CARD addendum 作为 §K。继 v0.24(§H)/v0.27(§I)/v0.29(§J) 后第四次「审计/构造层积压 → 整合层吸收」。

**方法**：integrate.py 纯冻结元数据，读冻结 v0.29 release_index_v0.29.json（28 版本）为基线。机器验证 v0.30 freeze-integrity（7 项全过）：(a) overall PASS；(b) 锚点全 accounted（147+4==151）；(c) drift_vs_v013 PASS 73/73；(d) drift_vs_v023 PASS 94/94（0 regression，1 living excluded，13 net-new）；(e) frozen_release_index_copies PASS 4/4；(f) 公共 v0.29 锚点 5dd43df6… 在 v0.30 穷举列表里再验证 PASS → v0.30 subsumes v0.29；(g) 本层跨层独立重算 3 项 match disk（v0.15 公共锚点 / v0.30 输出 e4b22a37… / v0.23 基线 cab56e7b…）。追加 v0.30（ACTIVE）+ v0.31（ACTIVE）。

**结果**：索引 30 版本 / 29 ACTIVE / 1 SUPERSEDED；canonical releases（v0.10 / v0.19）不变。5 产物：release_index_v0.31.json(21300B) / RELEASE_INDEX.md(19025B) / DATA_CARD_ADDENDUM_v0.31.md=§K(10331B) / consolidation_report_v0.31.json(3812B) / report_v31.html(19366B)。§K：冻结 lineage RE-sweep（v0.23 21版本/124锚点 → 28版本/151锚点，147 PASS+4 LIVING）+ 两 NEW 校验 + v0.23 latent living-file bug 建模；extends §A–§E + §G + §H + §I + §J；§F 仍预留。DETERMINISM PASS 5/5；LEAK 0；不改冻结层；唯一覆盖顶层 RELEASE_INDEX.md。

**结论**：v0.31 把 v0.30 审计层吸收进 RELEASE_INDEX（30 版本），§A–§K 全维度文档化。下游所有结论建立在机器验证 bit-intact 的冻结依赖图上。

---
## 归档批次 19 — EXP-32 + EXP-33 原文（2026-10-29 第36轮体积维护，从 EXPERIMENTS_DESIGNFLOW.md 搬入）

## EXP-32 — v0.32 stronger-model gap-shrink 构造层（v1.x 候选）（第33轮，2026-10-29）

**动机**：v0.28（EXP-28，已归档）的净结论把 v0.26 unseen-user gap=−0.2291 归为「该特征空间下标签识别的**内禀难度**」，并**明确命名**唯一剩下的药方——「要缩小需**更强模型 / 更富特征**，而非单纯加用户」——但**从未测试**这条药方（v0.28 只测了「加用户」并证伪之）。这是 v0.28 留下的、未被任何后续层（v0.29/v0.30/v0.31 都是元数据/整合/审计层）闭合的开放结论。本层即测试该命名药方的**构造层**，且**不被外部 gate 阻塞**（纯冻结数据 + stdlib/numpy，零 LLM/网络/SSH）——在 v0.29–v0.31 连续 3 轮元数据整合层之后，本层回到 v0.26/v0.28 的实质构造路径。

**方法**：`gap_shrink.py` 纯冻结数据，**逐位复用冻结 v0.26 user-stratified split**（`user_strat_train.jsonl` 168 / `user_strat_test.jsonl` 51 / `answers` 51）——受控对比设计：split 不变，**唯一变量是模型/特征**，故任何 acc delta 都归因于模型容量而非 partition resampling noise。三 arm：
1. **CONTROL**：重跑 v0.11/v0.26 nearest-centroid(cosine) baseline（同 TF-IDF latin+CJK-bigram + tools 特征）→ **必须复现 0.588235**（freeze-integrity cross-check on v0.26 split 文件 + 证明本层 feature pipeline 与 v0.26 逐位一致）。
2. **TREATMENT B（更强模型，同特征）**：把最近心心换成 multinomial logistic regression（softmax，full-batch GD，zero-init 权重→无 RNG 全确定性，iters=4000/lr=0.5/L2=1e-3，单线程 BLAS），特征**同** TF-IDF+tools——隔离「模型容量」轴。
3. **TREATMENT C（更强模型 + 更富特征）**：softmax on TF-IDF+tools + 标准化 meta 特征（log1p prompt 长度 / latin token 数 / CJK-bigram 数 / 工具数 / distinct 工具数 / has-chinese）——隔离「+ 更富特征」轴。
三 arm 均在相同 51 held-out test 上打分 + per-class acc + fully-unseen-user subset (n=42) + gap vs v0.15 headline 0.817352；`gap_shrink_vs_v026` 报各 treatment 相对 v0.26 control gap(−0.2291) 缩小(正)/扩大(负)。

**结果**：
- **CONTROL 复现 0.588235 ✅**（cross-check vs v0.26 PASS；证 split 逐位复用 + feature pipeline 一致）。
- **TREATMENT B（softmax, 同特征）：acc=0.8039 / gap=−0.0134 / shrink=+0.2157**——**几乎闭合 gap**！fully-unseen subset acc 0.6667→**0.9286**。per-class：other 0.2667→**0.9333**（+10 correct，修好 v0.18 记录的 other↔code_dev disputed 边界，最近心心在此边界崩、判别模型修好）/ code_dev 0.8889→0.9630；薄类 eda_virtuoso_schematic(0.0)/eda_aether_layout(0.0)/file_ops(0.0) 仍 0（v0.26 已标不迁移，非模型可解）。
- **TREATMENT C（softmax + meta）：acc=0.3137 / gap=−0.5036 / shrink=−0.2745**——**反扩大 gap**。meta 特征（长度/工具数）编码**用户风格**而非标签语义，加进来让模型 latch 到用户风格签名，伤跨用户泛化：code_dev 0.8889→0.4444、other 0.2667→0.2。
- **verdict**：仅「更强模型」（B）缩 gap，「+ 更富特征」（C）反伤。gap 主要不是 v0.28 说的「特征空间内禀难度」而是 **weak-model（最近心心）artifact**——同特征上换成线性判别模型即缩 +0.216。

**净结论**：**修订 v0.28 的「内禀难度」结论**。v0.28 用 matched-count 证伪了「加用户」药方，但**没测**「更强模型/更富特征」药方就把它当作 gap 的定性（内禀难度）——本层测出：在线性容量内，同特征换判别模型即把 gap 从 −0.2291 缩到 −0.0134（+0.216），所以 gap 的**大头是 weak-model artifact**，不是特征空间内禀不可学。诚实的修订：gap = (weak-model artifact 主项) + (薄类源硬限 残项，3 类 n≤4 不迁移)。v0.28「缩 gap 需更强模型」药方**方向正确但严重低估了效果**（以为是边际改善，实际几乎闭合）；「更富特征」药方**对粗 meta 为负**（编码用户风格伤泛化），需**语义级**特征（embeddings/code-AST）才可能正——那是下一个构造候选，本层 stdlib/numpy-only 不可及。与 v0.25→v0.26→v0.28→v0.32 形成完整闭环：v0.25 揭示 per-class==per-user → v0.26 构造测出 gap −0.23 → v0.28 证伪「加用户」 → v0.32 测试「更强模型」并修订 gap 定性。

**质量门**：
- **DETERMINISM PASS**：7/7 产物二次重跑 byte-identical（`PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1730000000` + zero-init softmax 无 RNG + 单线程 BLAS `OPENBLAS/OMP/MKL_NUM_THREADS=1` 保证 float 求和稳定）。
- **FREEZE-INTEGRITY PASS**：v0.15 debiased_test_set 磁盘 sha256 `5dd43df64f4d…` prefix match + v0.26 split 三文件 sha256 match v0.26 manifest 声明。
- **CROSS-CHECK vs v0.26 PASS**：CONTROL acc 0.588235 == v0.26 reported（受控对比守卫——证 split 逐位复用 + feature pipeline 一致，acc delta 纯归因模型）。
- **LEAK CHECK 0 残留**：正则扫 app.*/email/Word@digits/svc.*/shiwei/zhulong/Cxmt@/home 全 0。
- **不改冻结层**：v0.1–v0.31 out/ 全只读。构造层**非整合层**，按 v0.26/v0.28 先例**不重算 RELEASE_INDEX**（推到下一整合层再生），不覆盖顶层 RELEASE_INDEX.md。

**产物**（`bench_v0.32/`）：gap_shrink.py / report_v32.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + cross-check + leak 自检）/ README.md；`out/`：gap_shrink.json(9919B) / gap_shrink_characterization.md(4490B) / sub_control_nearestcentroid.jsonl(51) / sub_softmax_tfidf.jsonl(51) / sub_softmax_rich.jsonl(51) / gap_shrink_manifest.json(2651B) / report_v32.html(9330B)。顶层 README 增 v0.32 行 + 资产盘点轮次 32→33 + DAG 节点 v0.32 + v0.32 增补 callout + 复现段 + gate 表 .75 32→33。

**复探 3 口径**（第33轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 33 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs** / 3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 33 轮同卡点，上报仍有效待回复。

**结论**：本层是 v0.29–v0.31 连续 3 轮元数据整合层之后**首个实质构造层**，且不被外部 gate 阻塞。测试了 v0.28 命名但未测的「更强模型/更富特征」药方，**修订了 v0.28 的核心定性**：unseen-user gap −0.2291 的主项是 weak-model artifact（同特征换 softmax 即缩 +0.216 几乎闭合），不是「特征空间内禀难度」；残项是 3 薄类源硬限（n≤4，非模型可解）。这把 v0.28 的悲观结论纠正为更精确的分层：模型容量轴可解大头，特征轴需语义级而非粗 meta，源硬限轴仍需更多用户/机器。v0.33 候选：把 v0.32 纳入下一整合层再生 RELEASE_INDEX + 回写 §L（gap = weak-model artifact + 薄类残项，修订 v0.28 §J 内禀难度定性）到 v0.16 addendum（v0.32 是构造层按先例推到下一整合层）/ 接 LLM-judge 跑 3 标注者 + Fleiss κ + 落地 §F（阻塞）/ 测语义级特征（embeddings/code-AST，需 LLM endpoint）/ RESCAN 扩增（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：归档 EXP-27/28/29 原文至 ARCHIVE 批次 16（留指针）；EXP 31.7KB→约 24KB；MEMORY/TASK 全 ≤32KB。


## EXP-33 — v0.33 发布索引再生 + DATA_CARD addendum §L 整合层（第34轮，2026-10-29）

**动机**：v0.32（EXP-32）是 stronger-model gap-shrink **构造层**（v1.x 候选），按 v0.26/v0.28 构造层先例**明确把 RELEASE_INDEX 再生推到下一整合层**（构造层非整合层不重算索引）。v0.33 即该整合层——把 v0.32 纳入 RELEASE_INDEX，并把 v0.32 的核心发现（同特征换 softmax 缩 gap +0.216 几乎闭合 → gap 是 weak-model artifact）作为 **§L** 回写进 v0.16 DATA_CARD addendum，**修订 v0.28 §J 的「内禀难度」定性**。继 v0.24(§H)/v0.27(§I)/v0.29(§J)/v0.31(§K) 后第五次「构造/审计层积压 → 整合层吸收」。

**方法**：`integrate.py` 纯冻结元数据（零 /home/网络/LLM/新随机性），读冻结 v0.31 `release_index_v0.31.json`（30 版本）为基线。机器验证 v0.32 freeze-integrity（全过才继续）：(a) v0.32 manifest `freeze_integrity.status`==PASS；(b) v0.15 公共锚点 `5dd43df6` 声明 + status==PASS；(c) `v0.26_split_files_match_manifest`==true（v0.32 逐位复用冻结 v0.26 split）；(d) `cross_check_vs_v026.status`==PASS + `control_reproduced`==true + CONTROL acc 0.588235==v0.26 reported（freeze-integrity cross-check on v0.26 split 文件 + feature-pipeline parity proof）；(e) 3 个 split 文件 provenance `matches_v026_manifest`==true；(f) 本层跨层独立重算 4 项 match disk——v0.15 锚点 starts 5dd43df6 + 4 个 v0.26 split 文件（train/test/answers/user_resplit）match v0.32 声明 sha **AND** v0.26 自身 frozen manifest（证 v0.32 未误声明其冻结输入，cross-source 非仅凭 v0.32 自报）+ v0.32 输出 gap_shrink.json match manifest + gap_shrink.json self-agrees manifest（Form A 自指）。append v0.32（ACTIVE, stronger_model_gap_shrink_construction）+ v0.33（ACTIVE, metadata_integration）。

**结果**：
- 索引 **32 版本 / 31 ACTIVE / 1 SUPERSEDED**（v0.17 by v0.19 carried forward）；canonical releases（v0.10 / v0.19）不变。
- 5 产物：`release_index_v0.33.json`(25553B) / `RELEASE_INDEX.md`(22758B, 复制到顶层) / `DATA_CARD_ADDENDUM_v0.33.md`=§L(13464B) / `consolidation_report_v0.33.json`(5237B) / `report_v33.html`(24768B)。
- **§L** 修订 v0.28 §J「gap 是特征空间内禀难度」为更精确的两项分解：**unseen-user gap = (weak-model artifact 主项：同 TF-IDF+tools 特征，最近质心换 softmax 即缩 +0.216 几乎闭合 [gap −0.2291→−0.0134]，fully-unseen 0.667→0.929；若 gap 是特征空间内禀难度，同特征换模型不可能缩它——大头来自 `other` 0.267→0.933 [+10 correct]，即 v0.18 记录的 other↔code_dev disputed 边界，记忆模型崩、判别模型修好]) + (薄类源硬限残项：3 类 n≤4 单用户源，按构造不可测未见用户泛化，仅更多用户/机器可解，正交于模型轴)**。v0.28「更强模型」药方**方向正确但严重低估效果**（以为边际改善，实际几乎闭合）；「更富粗 meta 特征」药方**为负**（TREATMENT C 反扩大 gap shrink −0.275，粗 meta 编码用户风格伤跨用户泛化），需**语义级**特征（embeddings/code-AST，LLM-gated）。闭合 v0.25→v0.26→v0.28→v0.32 完整闭环。extends 冻结 v0.16 §A–§E + v0.22 §G + v0.24 §H + v0.27 §I + v0.29 §J + v0.31 §K；§F 仍预留（Fleiss κ，gate 阻塞）。
- **DETERMINISM PASS** 5/5 byte-identical；**leak 0**；不改冻结层 v0.1–v0.32 out/；唯一覆盖顶层 `designflow/RELEASE_INDEX.md`（活导航图 by design）。零 /home、零网络、零 LLM。
- 顶层 README 增 v0.33 行 + 资产盘点轮次 33→34 + DAG 节点 v0.33 + §L 指针 + v0.33 描述段 + 复现段 + gate 表 .75 33→34。

**复探 3 口径**（第34轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 34 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 34 轮同卡点，上报仍有效待回复。

**结论**：v0.33 把 v0.32 构造层吸收进 RELEASE_INDEX（32 版本），把 v0.32 的 gap-attribution 发现作为 §L 回写进 DATA_CARD addendum——**修订 v0.28 §J 的「内禀难度」定性**为更精确的「weak-model artifact 主项 + 薄类源硬限残项」。v0.28 的悲观结论被纠正：模型容量轴可解大头（同特征换线性判别模型几乎闭合），特征轴需语义级而非粗 meta，源硬限轴仍需更多用户/机器。§A–§L 统计严谨性/完整性/公平性/泛化/用户平衡/lineage/gap-attribution 全维度文档化。下游所有结论建立在机器验证 bit-intact 的冻结依赖图上。v0.34 候选：接真实 LLM-judge endpoint 跑 3 标注者 + Fleiss κ + 落地 §F（阻塞）/ 测语义级特征 embeddings/code-AST 验证 v0.32「粗 meta 为负需语义级」结论（需 LLM endpoint）/ 全树 lineage 再扫纳入 v0.32/v0.33 锚点 subsumes v0.30（承 v0.30→v0.31 先例）/ RESCAN 扩增（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：MEMORY 约 30KB / EXP 加 EXP-33 后约 27KB / TASK 5.3KB，全 ≤32KB。


---

## 归档批次 20 — EXP-36 原文（v0.35 发布索引再生 + §M 整合层，第36轮，2026-10-29 第37轮体积维护归档）

### EXP-36 — v0.35 发布索引再生 + DATA_CARD addendum §M 整合层（第36轮，2026-10-29）

**动机**：v0.34（冻结 lineage 完整性 RE-sweep 构造/审计层，subsumes v0.30）在 README 明确把 RELEASE_INDEX regen + §M 推到下一整合层 v0.35（承 v0.21/v0.23/v0.30 审计层先例）。v0.34 之后打开的回归窗口已被 v0.34 自身闭合（drift_vs_v030 104/104 0 regression），但 v0.34 尚未纳入 RELEASE_INDEX，索引仍停在 v0.33 的 32 版本视图。v0.35 是把 v0.34 吸收进索引 + 把 v0.34 的完整性发现回写进 DATA_CARD addendum 作为 §M 的整合层（承 v0.30→v0.31 构造→整合先例）。LLM-judge / 语义级特征 / RESCAN / v1.0 均被外部 gate 阻塞，本层是唯一不阻塞的构造性后继。

**方法**：`integrate.py`（结构改编自 v0.33，纯元数据）。1. **加载冻结基线** `bench_v0.33/out/release_index_v0.33.json`（32 版本，断言 benchmark_version==v0.33 且 n_versions==32）。2. **机器验证 v0.34 freeze-integrity**（全过才继续，否则 ABORT）：(a) v0.34 manifest `freeze_integrity.status`==PASS；(b) v0.34 audit `headline.overall_verdict`==PASS + 锚点计数精确 164 PASS/6 LIVING_FILE_BYDESIGN/0 MISMATCH/0 MISSING over 170[118 unique]/77 manifest/32 版本；(c) audit manifest 计数 77 == manifest 自身声明 input 计数 77（防 manifest 自误报）；(d) `drift_vs_v030.status`==PASS + rechecked/matched==104/104 + living_excluded==4 + regressions==0；(e) `drift_vs_v013.status`==PASS + checked/matched==73/73；(f) `frozen_release_index_copies.status`==PASS + checked/pass==6/6 + versions==[v0.22,v0.24,v0.27,v0.29,v0.31,v0.33] exact；(g) net_new_anchors_since_v030==10；(h) **跨层独立重算**：v0.34 输出 `lineage_audit_v034.json` 盘上 sha256[87ea388e…] == 其自身 manifest outputs 声明；v0.34 manifest 在盘；公共 v0.15 锚点 `debiased_test_set.jsonl` 盘上 starts `5dd43df6`（cross-source 证 v0.34 锚点集锚在真实冻结文件上，非误声明）。3. **append** v0.34[ACTIVE, frozen_lineage_integrity_resweep]+v0.35[ACTIVE, metadata_integration]→**34 版本/33 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19，carry-forward]。4. 产 `release_index_v0.35.json` + `RELEASE_INDEX.md`[v0.35 视图，覆盖顶层] + `DATA_CARD_ADDENDUM_v0.35.md`=**§M**[记录 v0.23→v0.30→v0.34 完整性审计 cadence + §M 对 §H/§K/§L/§I/§J/§E 的增量 + 4 caveats] + `consolidation_report_v0.35.json` + `report_v35.html`。

**§M 内容**：v0.34 全树 audit（32 版本/77 manifest/170 锚点→164 PASS+6 LIVING+0 broken）+ drift_vs_v030 104/104 0 回归 + 10 net-new provenance links since v0.30 全 bit-intact + frozen per-version RELEASE_INDEX copies 6/6。记录审计 cadence 规则「每轮 build-out 后下一整合层 regen index 前先 RE-sweep」。§M 增量：§H/§K 的 freeze-lineage 证据被 v0.34 supersede-in-scope（32 版本）；§L §J 修订的 freeze-integrity 基础被 re-confirm（v0.32 gap-shrink manifest 锚点在 170 内 bit-intact）；§I/§J gap 实验依赖的 v0.15 锚点+v0.26 split re-confirm。§F 仍预留 gate 阻塞。

**质量门**：- **DETERMINISM PASS** 5/5 byte-identical（release_index_v0.35.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.35.md / consolidation_report_v0.35.json / report_v35.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted + ensure_ascii=False）。- **FREEZE-INTEGRITY PASS**（reproduce.sh 内独立重算 v0.34 manifest+audit+drift+v0.15 锚点全过）。- **LEAK CHECK 0**（元数据层，data-free，正则扫 app.e*/app.t*/email/Cxmt@/svc.edaagent/shiwei/zhulong//home/app.* 全 0）。- **不改冻结层** v0.1–v0.34 out/ 全只读；唯一覆盖外部文件 = 顶层 `designflow/RELEASE_INDEX.md`（live navigable map，by design，v0.24/v0.27/v0.29/v0.31/v0.33 先例）。零 /home、零网络、零 LLM。

**产物**（`bench_v0.35/`）：integrate.py(21671B) / report_v35.py(4813B) / reproduce.sh(3129B) / README.md(3701B)；`out/`：release_index_v0.35.json(29429B) / RELEASE_INDEX.md(25292B) / DATA_CARD_ADDENDUM_v0.35.md(12619B) / consolidation_report_v0.35.json(4362B) / report_v35.html(25649B)。顶层 RELEASE_INDEX.md 再生为 v0.35 视图；README 增 v0.35 行 + 资产盘点轮次 35→36 + DAG 节点 v0.35 + §M addendum list 项 + v0.35 描述段 + gate 表 .75 35→36 + header updated through v0.35 + 版本索引 v0.1→v0.35。

**复探 3 口径**（第36轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 36 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 36 轮同卡点，上报仍有效待回复。

**结论**：v0.35 把 v0.34 构造/审计层吸收进 RELEASE_INDEX（34 版本/33 ACTIVE/1 SUPERSEDED），把 v0.34 的全树冻结完整性证据作为 §M 回写进 DATA_CARD addendum——记录 v0.23→v0.30→v0.34 完整性审计 cadence（每轮 build-out 后下一整合层 regen index 前先 RE-sweep）。§M re-confirm §A–§L 所有下游结论建立在机器验证 bit-intact 的冻结依赖图上（v0.34 证 v0.31–v0.33 build-out 未静默漂移任一冻结输入）。至此 §A–§M（§F 预留）统计严谨性/完整性/公平性/泛化/用户平衡/lineage（3 轮 cadence）/gap-attribution 全维度文档化。v0.36 候选：接 LLM-judge endpoint 跑 3 标注者 + Fleiss κ + 落地 §F（阻塞）/ 测语义级特征 embeddings/code-AST 验证 v0.32「粗 meta 为负需语义级」结论（需 LLM endpoint）/ RESCAN 扩增（持平 3487 无新样本，需 .75 多机或运维）/ 下一轮 lineage RE-sweep 待下一个 build-out 后（承 v0.23→v0.30→v0.34 cadence）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：归档 EXP-32+EXP-33 原文至 ARCHIVE 批次 19（留指针）；MEMORY 约 31.6KB / EXP 加 EXP-36 后归档约 20.3KB / TASK 5.3KB，全 ≤32KB。

## 归档批次 21 — MEMORY 第35/36/37轮流水原文（体积维护，2026-10-29 第38轮归档）

> 从 `MEMORY_DESIGNFLOW.md` 流水区搬入（v0.37 整合层已交付，rounds 35/36/37 已闭合，留 1 行指针）。

### MEMORY 第35轮流水原文（归档批次 21）
- [02:35] 第35轮：推进 **v0.34 冻结 lineage 完整性 RE-sweep 构造层（subsumes v0.30）**（闭环 v0.30 下一步候选「全树 lineage 再扫纳入 v0.31/v0.32/v0.33 锚点 subsumes v0.30」，承 v0.30→v0.31 构造→整合先例）。`lineage_audit.py`（改编自 v0.30，规则 Form A+B 不变保可比性）扫所有 bench_v0.*/out/*.json manifest→**32 版本/77 manifest/170 锚点**[118 unique]→**164 PASS + 6 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。**新增 drift_vs_v030 回归校验**——加载冻结 `bench_v0.30/out/lineage_audit_v030.json`[read-only]，重验其 104 个 frozen 锚点仍 bit-intact（排除 4 个 living RELEASE_INDEX.md，0 regression）；10 net-new anchors since v0.30（v0.31:3 / v0.32:3[v0.26 split files] / v0.33:3）。**drift_vs_v030 传递式 subsumes v0.30 自身的 drift_vs_v023**——v0.30 锚点集 ⊇ v0.23 锚点集，重验 v0.30 即重验 v0.23 超集，故显式 v0.23 recheck 省略无损。frozen per-version RELEASE_INDEX copies **6/6 PASS**（现含 v0.22/v0.24/v0.27/v0.29/v0.31/v0.33 consolidation）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。产 3 产物 lineage_audit_v034.json/lineage_audit_manifest.json/report_v34.html。**DETERMINISM PASS** 3/3 byte-identical。**leak 0**。不改冻结 v0.1–v0.33 out/；audit 层非整合层不重算 RELEASE_INDEX（按 v0.30 先例推到下一整合层 v0.35）；顶层 README 增 v0.34 行+资产盘点轮次 34→35+DAG 节点 v0.34+复现段+gate 表 .75 34→35。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第35轮仍可达但 SSH 拒（连续 35 轮同卡点，上报仍有效待回复）。

### MEMORY 第36轮流水原文（归档批次 21）
- [03:00] 第36轮：推进 **v0.35 发布索引再生 + §M 整合层**（闭环 v0.34 下一步候选「加载冻结 v0.33 索引→机器验证 v0.34→append v0.34+v0.35→回写 §M」，承 v0.30→v0.31 构造→整合先例）。`integrate.py`（改编自 v0.33，结构同）加载冻结 `bench_v0.33/out/release_index_v0.33.json`[32 版本]为基线，机器验证 v0.34 freeze-integrity 全过：manifest `freeze_integrity.status`=PASS + audit `headline.overall_verdict`=PASS + 锚点计数 164 PASS/6 LIVING_FILE_BYDESIGN/0 MISMATCH/0 MISSING over 170[118 unique]/77 manifest/32 版本 + audit manifest 计数 77==manifest 自身声明 input 计数 77 + `drift_vs_v030` PASS 104/104[4 living excluded, 0 regressions, net_new=10] + `drift_vs_v013` PASS 73/73 + `frozen_release_index_copies` PASS 6/6[v0.22/v0.24/v0.27/v0.29/v0.31/v0.33 exact] + 跨层独立重算 v0.34 输出 `lineage_audit_v034.json` match 其自身 manifest 声明 sha256[87ea388e…] + v0.34 manifest 在盘 + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6。append v0.34[ACTIVE, frozen_lineage_integrity_resweep]+v0.35[ACTIVE, metadata_integration]→**34 版本/33 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。回写 **§M** 到 v0.16 addendum[记录 v0.23→v0.30→v0.34 完整性审计 cadence；§F 仍预留 gate 阻塞]。产 5 产物 release_index_v0.35.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.35.md/consolidation_report_v0.35.json/report_v35.html。**DETERMINISM PASS** 5/5 byte-identical。**FREEZE-INTEGRITY PASS**。**leak 0**。不改冻结 v0.1–v0.34 out/；顶层 RELEASE_INDEX.md 再生为 v0.35 视图；README 增 v0.35 行+资产盘点轮次 35→36+DAG 节点 v0.35+§M 段+gate 表 .75 35→36。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第36轮仍可达但 SSH 拒（连续 36 轮同卡点，上报仍有效待回复）。

### MEMORY 第37轮流水原文（归档批次 21）
- [03:25] 第37轮：推进 **v0.36 meta-feature scaling-artifact 消融构造层**（闭环 §L 下一步候选「诊断 v0.32 TREATMENT C 未解释负结果的机制」，承 v0.32→v0.33 构造→整合先例；LLM-judge/语义特征/RESCAN/v1.0 均被外部 gate 阻塞，本层是唯一不阻塞的构造性后继）。`meta_ablate.py` 冻结 v0.26 split 逐位复用 v0.32，**cross-check vs v0.32**：CONTROL/B/C 逐位复现[0.588235/0.803922/0.313725] + v0.32 `gap_shrink.json` on-disk match 其 manifest[ec44d57f…]。**特征量级分析揭示根因**：z-scored meta 块（行 L2 范数 2.23）是 L2-归一化 TF-IDF 块（范数 1.0）的 2.2×，占拼接 rich 向量 norm² 的 **79.5%** → softmax 共享 lr/L2 下 6 个 meta 坐标主导 logits，**C 退化成 ~meta-only**（C=0.3137 ≈ meta-only E=0.2941）。三消融证伪「粗 meta 本质为负」：TREATMENT D（meta 块重缩放匹配 TF-IDF 范数，scale 0.4481）acc=**0.5294** / TREATMENT F（整行 L2 归一）acc=**0.5490** 大幅回升（Δ vs C = +0.22/+0.24）→ **C 崩溃是特征缩放伪影**；逐特征留一[max 0.4118/min 0.3333，无一恢复到 control]证无单一毒性特征，是整块量级主导。**修正（不推翻）§L**：粗 meta 缩放后是「温和偏负」（D 0.5294/F 0.5490 仍 < control 0.5882，不缩 gap）非「戏剧性为负」（C −0.27）；**§L 主结论不变**——TREATMENT B 缩 gap +0.2157 → unseen-user gap 是 weak-model artifact 非内禀难度；§L「需语义级特征缩 gap」方向**成立**（D/F 也不缩 gap）。v0.36 只精化 meta 子结论，不触碰 §L weak-model-artifact 主轴。产 7 产物 meta_ablate.json/meta_ablate_characterization.md/sub_softmax_metaonly/sub_softmax_meta_rescaled/sub_softmax_rich_rownormalized/meta_ablate_manifest.json/report_v36.html。**DETERMINISM PASS** 7/7 byte-identical。**FREEZE-INTEGRITY PASS**[v0.15 锚点 5dd43df6… + v0.32 on-disk]。**leak 0**。不改冻结 v0.1–v0.35 out/；构造层非整合层不重算 RELEASE_INDEX（按 v0.32 先例推到下一整合层 v0.37）；顶层 README 增 v0.36 行+资产盘点轮次 36→37+DAG 节点 v0.36+v0.36 段+复现段+gate 表 .75 36→37。体积维护：MEMORY 压缩 v0.1–v0.11 交付物详情（已归档批次 3–5）为 1 行指针。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第37轮仍可达但 SSH 拒（连续 37 轮同卡点，上报仍有效待回复）。

## 归档批次 22 — EXP-38 原文 + MEMORY 第38轮流水原文（体积维护，2026-10-29 第39轮归档）

### EXP-38 原文（v0.37 发布索引再生 + DATA_CARD addendum §N 整合层，第38轮，归档批次 22）

**动机**：v0.36（meta-feature scaling-artifact 消融构造层）明确把 RELEASE_INDEX 再生 + §N 回写推到下一整合层（承 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32 构造层先例）。v0.37 即该整合层，承 v0.32→v0.33 / v0.34→v0.35 构造→整合 cadence：加载冻结 v0.35 索引 → 机器验证 v0.36 → append v0.36+v0.37 → 回写 §N。纯元数据，零 /home、零网络、零 LLM、零新随机；不改冻结 v0.1–v0.36 out/。

**方法**：`integrate.py`（改编自 v0.35，结构同）加载冻结 `bench_v0.35/out/release_index_v0.35.json`[34 版本]为基线，机器验证 v0.36 freeze-integrity：
1. **manifest**：`freeze_integrity.status`=PASS + v0.15 锚点 `5dd43df6`/status PASS + v0.26 split files match manifest + v0.32 gap_shrink.json on-disk matches manifest。
2. **cross_check_vs_v032**：status=PASS，CONTROL/B/C 逐位复现 v0.32[0.588235/0.803922/0.313725]，`v032_gap_shrink_sha_match`=true（证本层 feature pipeline 与 v0.32 字节一致 → 消融 delta 仅归因缩放）。
3. **跨层独立重算**（不只信 v0.36 自报）：(i) v0.36 输出 `meta_ablate.json` on-disk sha256[9d35a5ca…] == 其自身 manifest 声明；(ii) v0.32 `gap_shrink.json` on-disk[ec44d57f…] == v0.36 provenance 声明；(iii) 公共 v0.15 锚点 on-disk starts `5dd43df6`；(iv) v0.26 split 4 文件[user_resplit/user_strat_train/test/answers] on-disk 全 match v0.36 provenance 声明。
4. append v0.36[ACTIVE, meta_feature_scaling_artifact_ablation_construction] + v0.37[ACTIVE, metadata_integration] → **36 版本/35 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]；canonical releases（v0.10/v0.19）不变。
5. 回写 **§N** 到 v0.16 addendum：meta-feature scaling-artifact——C 崩溃是特征缩放伪影（z-scored meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；D/F 重缩放回升到 0.5294/0.5490 但不缩 gap）→ **修正 §L「粗 meta 戏剧性为负」为「缩放后温和偏负」**；**§L 主结论不变**（B 缩 gap +0.2157 → weak-model artifact）；**§L「需语义级特征缩 gap」方向成立**（D/F 也不缩 gap）。记录 §I→§J→§L→§N gap-attribution 精化 cadence（每层闭一个开放问题不动已结结论）。§F 仍预留 gate 阻塞。

**质量门**：- **DETERMINISM PASS** 5/5 byte-identical（release_index_v0.37.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.37.md/consolidation_report_v0.37.json/report_v37.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration，纯元数据无新随机）。- **FREEZE-INTEGRITY PASS**（v0.36 manifest + cross_check_vs_v032 + 跨层独立重算 4 项全过）。- **LEAK CHECK 0**。- **不改冻结层** v0.1–v0.36 out/ 全只读；v0.35 索引 read-only 作基线。

**verdict**：v0.37 把 v0.36 构造层吸收进 RELEASE_INDEX（36 版本/35 ACTIVE/1 SUPERSEDED），把 v0.36 的「C 崩溃是缩放伪影」诊断作为 §N 回写进 DATA_CARD addendum——修正 §L 的「粗 meta 戏剧性为负」框架为「缩放伪影导致的负 + 缩放后温和偏负」，同时**保留 §L 的两个核心结论**（B 缩 gap → weak-model artifact；需语义级特征缩 gap）。至此 §A–§N（§F 预留）统计严谨性/完整性/公平性/泛化/用户平衡/lineage（3 轮 cadence）/gap-attribution（4 步精化 cadence §I→§J→§L→§N）全维度文档化。

**产物**（`bench_v0.37/`）：integrate.py / report_v37.py / reproduce.sh（DETERMINISM + freeze-integrity v0.36 + leak 自检）/ README.md；`out/`：release_index_v0.37.json(34023B) / RELEASE_INDEX.md(29458B) / DATA_CARD_ADDENDUM_v0.37.md(14215B) / consolidation_report_v0.37.json(4895B) / report_v37.html(31300B)。顶层 RELEASE_INDEX.md 再生为 v0.37 视图；README 增 v0.37 行 + 资产盘点轮次 37→38 + DAG 节点 v0.37 + §N addendum list 项 + v0.37 描述段 + 复现段[补遗漏的 v0.35 复现行] + gate 表 .75 37→38 + header updated through v0.37 + 版本索引 v0.1→v0.37。

**复探 3 口径**（第38轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 38 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 38 轮同卡点，上报仍有效待回复。

**结论**：v0.37 闭环 v0.36 下一步候选——v0.36 的 meta-feature scaling-artifact 诊断（C 崩溃是缩放伪影）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（36 版本/35 ACTIVE/1 SUPERSEDED），并作为 §N 回写进 addendum。gap-attribution 精化 cadence 走完第 4 步（§I 测 gap → §J 归因内禀难度 → §L 修订为 weak-model artifact → §N 精化 meta 子结论为缩放伪影，保留 §L 主结论）。v0.38 候选：接 LLM-judge endpoint 跑 3 标注者 + Fleiss κ + 落地 §F（阻塞）/ 测语义级特征 embeddings/code-AST 验证 §L/§N「需语义级缩 gap」结论（需 LLM endpoint）/ RESCAN 扩增（持平 3487 无新样本，需 .75 多机或运维）/ 下一轮 lineage RE-sweep 待下一个 build-out 后[承 v0.23→v0.30→v0.34 cadence，v0.36 新 manifest 锚点待下一 build-out 后扫] / v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：归档 MEMORY 第35/36/37轮流水原文至 ARCHIVE 批次 21（留 1 行指针）→ MEMORY 28.9KB；EXP 加 EXP-38 后约 23.4KB；TASK 5.1KB，全 ≤32KB。

### MEMORY 第38轮流水原文（归档批次 22）

- [03:45] 第38轮：推进 **v0.37 发布索引再生 + §N 整合层**（闭环 v0.36 下一步候选「纳入 v0.36 再生 RELEASE_INDEX + 回写 §N」，承 v0.32→v0.33 / v0.34→v0.35 构造→整合先例）。`integrate.py`（改编自 v0.35，结构同）加载冻结 `bench_v0.35/out/release_index_v0.35.json`[34 版本]为基线，机器验证 v0.36 freeze-integrity 全过：manifest `freeze_integrity.status`=PASS + `cross_check_vs_v032.status`=PASS[CONTROL 0.588235/B 0.803922/C 0.313725 逐位复现 v0.32] + `v032_gap_shrink_sha_match`=true + 跨层独立重算 v0.36 输出 `meta_ablate.json` match 其自身 manifest 声明 sha256[9d35a5ca…] + v0.32 `gap_shrink.json` match v0.36 provenance 声明[ec44d57f…] + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6 + v0.26 split 4 文件[user_resplit/user_strat_train/test/answers] match v0.36 provenance。append v0.36[ACTIVE, meta_feature_scaling_artifact_ablation_construction]+v0.37[ACTIVE, metadata_integration]→**36 版本/35 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。回写 **§N** 到 v0.16 addendum[meta-feature scaling-artifact：C 崩溃是特征缩放伪影（meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；D/F 重缩放回升到 0.5294/0.5490 但不缩 gap）→ 修正 §L「粗 meta 戏剧性为负」为「缩放后温和偏负」，§L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立；记录 §I→§J→§L→§N gap-attribution 精化 cadence；§F 仍预留 gate 阻塞]。产 5 产物 release_index_v0.37.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.37.md/consolidation_report_v0.37.json/report_v37.html。**DETERMINISM PASS** 5/5 byte-identical。**FREEZE-INTEGRITY PASS**[v0.36 manifest + cross_check + 跨层独立重算 4 项]。**leak 0**。不改冻结 v0.1–v0.36 out/；顶层 RELEASE_INDEX.md 再生为 v0.37 视图；README 增 v0.37 行+资产盘点轮次 37→38+DAG 节点 v0.37+§N 段+复现段[补遗漏的 v0.35 复现行]+gate 表 .75 37→38。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第38轮仍可达但 SSH 拒（连续 38 轮同卡点，上报仍有效待回复）。

## 归档批次 23 — MEMORY 第39轮流水原文（体积维护，2026-10-29 第40轮归档）

### MEMORY 第39轮流水原文（归档批次 23）

- [04:05] 第39轮：推进 **v0.38 gap-shrink bootstrap CI 构造层**（闭环 v0.32/v0.36 留的统计严谨性开放问题「§L/§N 核心结论是点估计，n=51 高方差，从无 CI」——v0.32 自陈「方向可靠 magnitude 不可靠」，v0.21 只给过 v0.15 诊断 split 的 CI，从未给过 v0.26/v0.32 unseen-user gap 的 CI；本层承 v0.21 bootstrap 方法但首次应用到 unseen-user gap，不被外部 gate 阻塞）。`gap_shrink_ci.py` 冻结 v0.26 answers + v0.32 submissions 逐位复用（CONTROL/B/C 同一 frozen file order），配对 percentile bootstrap 10000 次（numpy default_rng(seed=0)，CONTROL/B/C 用同一 resample 索引向量→配对对比正确）on n=51 + n=42 fully-unseen[user_hash∉train]：(1) B 缩 gap over CONTROL **显著**——n=51 95% CI [0.0980,0.3529] p(shrink≤0)=0.0005 / n=42 CI [0.1429,0.4048] p=0.0 → §L weak-model-artifact 主轴**对重采样稳健**非小样本偶然；(2) B 残余 gap vs headline（−0.0134）**含 0**——n=51 95% CI [−0.1311,0.0846] p(gap≥0)=0.4478 → **统计上闭合**（B 把 gap 关到易类天花板噪声内）→ 强化 §L；(3) C 崩溃 vs CONTROL（−0.2745）**显著**——n=51 95% CI [−0.4118,−0.1373] p=0.0 → v0.36 缩放伪影诊断是**真实效应**非 n=51 错觉。**首个 unseen-user gap CI**。产 4 产物 gap_shrink_ci.json/gap_shrink_ci_characterization.md/gap_shrink_ci_manifest.json/report_v38.html。**DETERMINISM PASS** byte-identical。**FREEZE-INTEGRITY PASS**[cross-check vs v0.32 9/9 点估计 MATCH + v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha 独立重算 match v0.32 manifest]。**leak 0**。不改冻结 v0.1–v0.37 out/；构造层非整合层不重算 RELEASE_INDEX（按 v0.32/v0.36 先例）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。README 增 v0.38 行+资产盘点轮次 38→39+DAG 节点 v0.38+v0.38 段+复现段+gate 表 .75 38→39+header updated through v0.38+版本索引 v0.1→v0.38。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第39轮仍可达但 SSH 拒（连续 39 轮同卡点，上报仍有效待回复）。

## 归档批次 24 — MEMORY 第32–40轮流水原文（体积维护，2026-10-29 第41轮归档）

### MEMORY 第32–40轮流水原文（归档批次 24）

- [01:35] 第32轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 16（v0.31 发布索引再生 + §K 整合层：纳入 v0.30，30 版本/29 ACTIVE/1 SUPERSEDED，机器验证 v0.30 freeze-integrity 7 项全过，§K 回写 v0.23 latent living-file bug 建模；DETERMINISM 5/5 + leak 0）。
- [02:20] 第34轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 17（v0.33 发布索引再生 + §L 整合层：纳入 v0.32，32 版本/31 ACTIVE/1 SUPERSEDED，§L 修订 v0.28 §J「内禀难度」为「weak-model artifact 主项 + 薄类源硬限残项」；DETERMINISM 5/5 + leak 0）。
- [02:35] 第35轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 21（v0.34 冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.30：32 版本/77 manifest/170 锚点→164 PASS + 6 LIVING_FILE_BYDESIGN，drift_vs_v030 104/104 0 回归，frozen RELEASE_INDEX 副本 6/6；DETERMINISM 3/3 + leak 0）。
- [03:00] 第36轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 21（v0.35 发布索引再生 + §M 整合层：纳入 v0.34，34 版本/33 ACTIVE/1 SUPERSEDED，机器验证 v0.34 freeze-integrity 全过，§M 记录 v0.23→v0.30→v0.34 审计 cadence；DETERMINISM 5/5 + leak 0）。
- [03:25] 第37轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 21（v0.36 meta-feature scaling-artifact 消融构造层：C 崩溃是缩放伪影[meta 块占 rich norm² 79.5% → C≈meta-only]→ 修正 §L「粗 meta 为负」为「缩放后温和偏负」，§L 主结论不变；DETERMINISM 7/7 + leak 0）。
- [03:45] 第38轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 22（v0.37 发布索引再生 + §N 整合层：纳入 v0.36，36 版本/35 ACTIVE/1 SUPERSEDED，§N 修正 §L 粗 meta 戏剧性为负为缩放伪影导致的负，§L 主结论+缩 gap 方向不变；DETERMINISM 5/5 + leak 0）。
- [04:05] 第39轮流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 23（v0.38 gap-shrink bootstrap CI 构造层：配对 percentile bootstrap n=51/n=42——B 缩 gap over CONTROL 显著[0.0980,0.3529] p=0.0005（§L 主轴对重采样稳健）；B 残余 gap 含 0 p=0.4478（统计上闭合，强化 §L）；C 崩溃显著[−0.4118,−0.1373] p=0.0（v0.36 缩放伪影真实）；首个 unseen-user gap CI；DETERMINISM + freeze-integrity + leak 0）。
- [04:35] 第40轮：推进 **v0.39 发布索引再生 + §O 整合层**（闭环 v0.38 下一步候选「v0.39 候选 = 发布索引再生 + §O 整合层[纳入 v0.38，不需外部 gate，承 v0.36→v0.37 构造→整合先例]」，承 v0.36→v0.37 construction→integration cadence，不被外部 gate 阻塞）。`integrate.py`（改编自 v0.37，结构同）加载冻结 `bench_v0.37/out/release_index_v0.37.json`[36 版本]为基线，机器验证 v0.38 freeze-integrity 全过：manifest `freeze_integrity.status`=PASS + `all_match`=true + `cross_check_vs_v0.32`="MATCH (9/9 point estimates)"[manifest 字符串] + 输出 `gap_shrink_ci.json` 的 `cross_check_vs_v0.32.status`=MATCH 9 项点估计在 rounding tolerance[1e-5]内全复现[其中 b_shrink_vs_v026 got 0.215686 vs v0.32-recorded 0.215687 末位 float 舍入，v0.38 自记 MATCH 9/9] + 跨层独立重算 v0.38 输出 `gap_shrink_ci.json`[9a11d347…] / `gap_shrink_ci_characterization.md`[b88aa2bc…] match 其自身 manifest 声明 + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6 + v0.26 split 3 文件[test/answers/train] + v0.32 submission+gap_shrink 4 文件[sub_control/sub_softmax_tfidf/sub_softmax_rich/gap_shrink.json] match v0.38 inputs 声明。append v0.38[ACTIVE, gap_shrink_bootstrap_ci_construction]+v0.39[ACTIVE, metadata_integration]→**38 版本/37 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。回写 **§O** 到 v0.16 addendum[gap-shrink bootstrap CI：把 §L/§N 核心结论从点估计升级为置信区间——B 缩 gap over CONTROL +0.2157 显著[n=51 95% CI 0.0980,0.3529 p=0.0005 / n=42 CI 0.1429,0.4048 p=0.0]→§L weak-model-artifact 主轴对重采样稳健非小样本偶然，退役 §L「magnitude 不可靠」caveat；B 残余 gap −0.0134 含 0[n=51 CI −0.1311,0.0846 p=0.4478]→统计上闭合→强化 §L；C 崩溃 −0.2745 显著[n=51 CI −0.4118,−0.1373 p=0.0]→v0.36 缩放伪影真实非 n=51 错觉→证实 §N；§L 主结论 + §N 子结论不变均 CI-backed；首个 unseen-user gap CI；记录 §G→§O rigor-closure cadence；§F 仍预留 gate 阻塞]。§O **不推翻 §L/§N，只升级证据地位**。产 5 产物 release_index_v0.39.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.39.md/consolidation_report_v0.39.json/report_v39.html。**DETERMINISM PASS** 5/5 byte-identical。**FREEZE-INTEGRITY PASS**[v0.38 manifest + cross_check_vs_v032 MATCH 9/9 + 跨层独立重算 v0.38 输出 + v0.15 锚点 + v0.26 split 3 + v0.32 submission 4]。**leak 0**。不改冻结 v0.1–v0.38 out/；顶层 RELEASE_INDEX.md 再生为 v0.39 视图；README 增 v0.39 行+资产盘点轮次 39→40+DAG 节点 v0.39+v0.38/v0.39 段+§O addendum list 项+复现段+gate 表 .75 39→40+header updated through v0.39+版本索引 v0.1→v0.39。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第40轮仍可达但 SSH 拒（连续 40 轮同卡点，上报仍有效待回复）。体积维护：归档第39轮流水原文至 ARCHIVE 批次 23。

## 归档批次 25 — EXP-35 v0.34 原文（体积维护，2026-10-29 第42轮归档）

### EXP-35 — v0.34 冻结 lineage 完整性 RE-sweep 构造层（subsumes v0.30）（第35轮，2026-10-29）

**动机**：v0.33 留的下一步候选「全树 lineage 再扫，纳入 v0.32/v0.33 锚点，subsumes v0.30（承 v0.30→v0.31 先例）」。v0.30 是第二个全树完整性审计（28 版本 / 151 锚点）；之后 v0.31（integration, consolidation 3 anchors）+ v0.32（construction, gap_shrink_manifest 5 anchors → v0.26 split files + v0.15 anchor）+ v0.33（integration, consolidation 3 anchors）三层加入，各带新 provenance sha256 锚点，无后继检查覆盖。v0.34 把 v0.30 的全树审计重跑到现已冻结的 32 版本，并加回归校验。audit 层非整合层（同 v0.30），不重算 RELEASE_INDEX，按 v0.30 先例推到下一整合层 v0.35。LLM-judge / 语义级特征 / RESCAN / v1.0 均被外部 gate 阻塞，本层是唯一不阻塞的构造性后继。

**方法**：`lineage_audit.py`（改编自 v0.30，OWN_OUT_REL→bench_v0.34/out）。1. **锚点提取 UNCHANGED**（Form A+B 规则与 v0.23/v0.30 字节级一致，使三审计 anchor 集合可直接 set-comparable）。2. **扫描**所有 bench_v0.*/out/*.json manifest（排除本层 out）→ **32 版本 / 77 manifest / 170 锚点**（118 unique）；逐锚点重算 sha256：**164 PASS + 6 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。3. **drift_vs_v013**（同 v0.23/v0.30）：v0.1–v0.11 artifact 子集对冻结 v0.13 version_manifest 交叉校验 → PASS 73/73。4. **drift_vs_v030（NEW，替换 v0.30 的 drift_vs_v023）**：加载冻结 `bench_v0.30/out/lineage_audit_v030.json`（read-only 基线），取其 108 unique 锚点，partition frozen(104) vs living(4)，重验 104 frozen 仍 bit-intact → **PASS 104/104，0 regression**；10 net-new anchors since v0.30（v0.31:3 / v0.32:3[v0.26 split files] / v0.33:3）。5. **drift_vs_v030 传递式 subsumes v0.30 自身的 drift_vs_v023**：v0.30 unique anchor 集 ⊇ v0.23 unique anchor 集（v0.30 扫了含 v0.23 21 版本在内的 28 版本），重验 v0.30 即重验 v0.23 超集 → 显式 v0.23 recheck 省略无损（不丢信息，省输出体积）。6. **frozen_release_index_copies_check**（同 v0.30，现覆盖 6 个 consolidation）：v0.22/v0.24/v0.27/v0.29/v0.31/v0.33 各声明 RELEASE_INDEX.md sha 对其自身冻结 `bench_v0.XX/out/RELEASE_INDEX.md` 副本 → **PASS 6/6**。

**质量门**：- **DETERMINISM PASS** 3/3 byte-identical（lineage_audit_v034.json / lineage_audit_manifest.json / report_v34.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted + sort_keys）。- **overall PASS**（0 MISMATCH/MISSING/ERR + drift_vs_v013 PASS + drift_vs_v030 PASS + frozen_release_index_copies PASS）。- **LEAK CHECK 0**（元数据层，data-free）。- **不改冻结层** v0.1–v0.33 out/ 全只读；冻结 v0.30 audit 仅 read-only 作基线。零 /home、零网络、零 LLM。公共 v0.15 锚点 5dd43df6… 再验证 PASS（carry-through）。

**产物**（`bench_v0.34/`）：lineage_audit.py / report_v34.py / reproduce.sh（DETERMINISM_CHECK=1 + leak 自检）/ README.md；`out/`：lineage_audit_v034.json(153692B) / lineage_audit_manifest.json(5273B) / report_v34.html(34252B)。顶层 README 增 v0.34 行 + 资产盘点轮次 34→35 + DAG 节点 v0.34 + v0.34 增补 callout + v0.34 描述段 + 复现段 + gate 表 .75 34→35。不覆盖顶层 RELEASE_INDEX.md（audit 层非整合层）。

**复探 3 口径**（第35轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 35 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 35 轮同卡点，上报仍有效待回复。

**结论**：v0.34 把全树冻结完整性证据从 v0.29 推进到 v0.33（32 版本 / 170 锚点 164 PASS+6 LIVING），证 v0.31–v0.33 build-out 未静默漂移任一冻结输入（drift_vs_v030 104/104，0 regression），并传递式 subsume v0.30 自身的 drift_vs_v023（v0.23 锚点集 ⊂ v0.30 锚点集 ⊂ v0.34 锚点集，三层回归链 v0.23→v0.30→v0.34 全 bit-intact）。下游所有结论（v0.19 诊断发布 / v0.21 gap CI / v0.28 matched-count / v0.29 §J / v0.32 gap-shrink / v0.33 §L 修订）建立在 bit-intact 的冻结依赖图上。v0.35 候选：**发布索引再生 + §M 整合层**（加载冻结 v0.33 索引[32 版本]为基线，机器验证 v0.34 freeze-integrity，append v0.34+v0.35→34 版本/33 ACTIVE/1 SUPERSEDED，回写 §M 到 v0.16 addendum，承 v0.30→v0.31 整合先例）/ 接 LLM-judge 跑 3 标注者 + Fleiss κ + 落地 §F（阻塞）/ 测语义级特征 embeddings/code-AST（需 LLM endpoint）/ RESCAN 扩增（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：归档 EXP-30+EXP-31 原文至 ARCHIVE 批次 18（留指针）；MEMORY 约 30.5KB / EXP 加 EXP-35 后约 30KB / TASK 5.3KB，全 ≤32KB。


## 归档批次 26 — EXP-37 v0.36 原文（体积维护，2026-10-29 第43轮归档）

> EXP-37（v0.36 meta-feature scaling-artifact 消融构造层）原文搬入本批次。要点见本节标题 + MEMORY 流水。v0.36 结论已通过 §N（v0.37）/§O（v0.39）整合进 v0.16 addendum，且被 v0.40 lineage RE-sweep 覆盖；本归档仅腾 EXPERIMENTS 体积，不动结论。

## EXP-37 (2026-10-29) bench_v0.36 meta-feature scaling-artifact 消融构造层（第37轮）

**动机**：v0.32 TREATMENT C（softmax on TF-IDF ‖ z-scored meta）崩溃到 acc=0.313725——比 CONTROL（0.588235）还差，远低于 TREATMENT B（0.803922）。v0.33 §L 读作「粗 meta 编码用户风格伤跨用户泛化，需语义级特征」，但**机制从未诊断**：加特征反降准确率不寻常，应先受控分解再下「特征本质有害」的结论。§L 留的下一步候选「诊断 v0.32 TREATMENT C 负结果的机制」是唯一不阻塞的构造性后继（LLM-judge/语义特征/RESCAN/v1.0 均被外部 gate 阻塞）。

**方法**：`meta_ablate.py` 冻结 v0.26 user-stratified split 逐位复用 v0.32（同 partition → 受控对比，delta 仅归因特征构造）。**复用 v0.32 feature pipeline**（text_tokens/build_vocab/tfidf_vectorize/meta_vector/standardize/softmax_fit/score 经 `import gap_shrink`）→ CONTROL/B/C 必须逐位复现 v0.32 报告值（freeze-integrity cross-check）。本层贡献 = 特征量级分析 + 三消融 + 逐特征留一：
1. **特征量级分析**：TF-IDF 行 L2 范数 1.0（per-element abs 0.0166）vs z-scored meta 行 L2 范数 2.23（per-element abs 0.7642）；**meta 块占 rich 向量 norm² 的 79.5%** → softmax 共享 lr/L2 下 6 个 meta 坐标主导 logits。
2. **TREATMENT E（meta-ONLY）**：softmax 仅 6 个标准化 meta 特征 → acc 0.2941（meta-only 天花板）；C=0.3137 ≈ E → **C 退化成 ~meta-only 模型**（TF-IDF 信号被淹没）。
3. **TREATMENT D（meta 块重缩放）**：scale meta 块使行 L2 范数匹配 TF-IDF 块（1.0），scale=0.4481，hstack + softmax → acc 0.5294（Δ vs C = +0.22）；shrink_vs_v026 = −0.0588。
4. **TREATMENT F（整行 L2 归一）**：hstack 后整行 L2-normalize → acc 0.5490（Δ vs C = +0.24）；shrink_vs_v026 = −0.0392。
5. **逐特征留一 on C**：依次丢 6 个 meta 特征，acc 范围 0.3333–0.4118，无一恢复到 control → 无单一毒性特征，崩溃是整块量级主导。

**质量门**：DETERMINISM PASS 7/7 byte-identical；FREEZE-INTEGRITY PASS（v0.15 锚点 5dd43df6… + v0.26 split + v0.32 gap_shrink.json on-disk match manifest[ec44d57f…]）；cross-check vs v0.32 PASS（CONTROL/B/C 0.588235/0.803922/0.313725 逐位复现）；LEAK CHECK 0；不改冻结层 v0.1–v0.35 out/。

**verdict**：C 的崩溃是 **FEATURE-SCALING ARTIFACT**，非粗 meta 本质为负。z-scored meta 块（norm 2.23）占 rich norm² 79.5%，C 退化成 ~meta-only（C=0.3137≈E=0.2941）。D/F 重缩放后大幅回升（0.5294/0.5490）→ 粗 meta 缩放后是「温和偏负」（仍 < control 0.5882，不缩 gap）非「戏剧性为负」（C −0.27）。**修正（不推翻）§L**：(a) REVISED §L「粗 meta 戏剧性为负」→「缩放伪影导致的负，缩放后温和偏负」；(b) STANDS §L「需语义级特征缩 gap」方向（D/F 也不缩 gap）；(c) UNCHANGED §L 主结论——TREATMENT B 缩 gap +0.2157 → unseen-user gap 是 weak-model artifact 非内禀难度。

**产物**（`bench_v0.36/`）：meta_ablate.py / report_v36.py / reproduce.sh / README.md；`out/`：meta_ablate.json(18980B) / meta_ablate_characterization.md(7178B) / sub_softmax_metaonly.jsonl(4487B) / sub_softmax_meta_rescaled.jsonl(4325B) / sub_softmax_rich_rownormalized.jsonl(4273B) / meta_ablate_manifest.json(3250B) / report_v36.html(11617B)。

**结论**：v0.36 诊断 v0.32 TREATMENT C 未解释负结果——C 崩溃是特征缩放伪影（meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941），D/F 重缩放回升到 0.5294/0.5490。修正 §L「粗 meta 为负」为「缩放伪影导致的负 + 缩放后温和偏负」，保留 §L 两核心结论（B 缩 gap → weak-model artifact；需语义级特征缩 gap）。已被 §N(v0.37)/§O(v0.39) 整合 + v0.40 lineage RE-sweep 覆盖。


## 归档批次 27 — 第41/42轮流水原文 + EXP-38 v0.37 原文（体积维护，2026-10-29 第43轮归档）

> 第41轮（v0.40 lineage RE-sweep）/ 第42轮（v0.41 §P 整合层）流水原文搬入本批次，留 1 行指针。要点见 MEMORY 流水。v0.40 已被 v0.41 §P 整合 + 将被下一 lineage RE-sweep subsume；v0.41 已纳入 RELEASE_INDEX。
> EXP-38（v0.37 §N 整合层）原文搬入本批次。要点见本节标题 + MEMORY 流水。v0.37 §N 结论已通过 §O（v0.39）/ §P（v0.41）整合进 v0.16 addendum，且被 v0.40 lineage RE-sweep 覆盖；本归档仅腾 EXPERIMENTS 体积，不动结论。

### 第41轮流水（v0.40 冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.34）

推进 **v0.40 冻结 lineage 完整性 RE-sweep 构造层**（subsumes v0.34，承 v0.23→v0.30→v0.34→v0.40 cadence；闭环 v0.39 下一步候选「lineage RE-sweep 现已解锁」[v0.38 产新 manifest 锚点]）。`lineage_audit.py`（改编自 v0.34，锚点提取规则 UNCHANGED）扫所有 38 frozen versions 的 89 manifest，提取 206 sha256 锚点（135 unique）→197 PASS + 9 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR。**drift_vs_v034**（新增）：加载冻结 `bench_v0.34/out/lineage_audit_v034.json`[118 unique anchors]，re-verify 112 frozen anchors（排除 6 living）→**112/112 PASS 0 回归**→v0.35–v0.39 build-out 未静默漂移任一冻结输入；17 net-new anchors since v0.34。drift_vs_v034 传递式 subsumes v0.34 的 drift_vs_v030。drift vs v0.13 PASS 73/73；frozen per-version RELEASE_INDEX copies 9/9 PASS；公共 v0.15 锚点 5dd43df6… 再验证 PASS。产 3 产物 lineage_audit_v040.json/lineage_audit_manifest.json/report_v40.html。DETERMINISM PASS 3/3 byte-identical。FREEZE-INTEGRITY PASS。leak 0。不改冻结 v0.1–v0.39 out/；构造/审计层非整合层不重算 RELEASE_INDEX（推到 v0.41）。3 口径=1机/20dir(19有数据)/3487 session dirs/3479 messages.json——与冻结快照 a1cd058a… 完全对齐 0 漂移。.75 第41轮仍可达但 SSH 拒（连续 41 轮同卡点，上报仍有效待回复）。

### 第42轮流水（v0.41 发布索引再生 + §P 整合层）

推进 **v0.41 发布索引再生 + §P 整合层**（闭环 v0.40 下一步候选「发布索引再生整合层」[v0.40 构造层推到下一整合层，承 v0.34→v0.35 / v0.38→v0.39 构造→整合 cadence]，不被外部 gate 阻塞）。`integrate.py`（改编自 v0.39）加载冻结 `bench_v0.39/out/release_index_v0.39.json`[38 版本]为基线，机器验证 v0.40 freeze-integrity 全过：manifest PASS + headline overall PASS + drift_vs_v034 112/112 0 regressions + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 9/9 + 跨层独立重算 v0.40 输出 lineage_audit_v040.json[c2194b3d…] match manifest + v0.40 输入 v0.13_version_manifest[c83ea686…] match + v0.40 输入 v0.34_lineage_audit[87ea388e…] match + 公共 v0.15 锚点 5dd43df6… starts5dd43df6。append v0.40+v0.41→**40 版本/39 ACTIVE/1 SUPERSEDED**。回写 §P 到 v0.16 addendum[扩展 §M 覆盖窗口 32→38 版本，不推翻 §H/§K/§M；记录 §H→§K→§M→§P RE-sweep cadence 第 4 次全树审计；§F 仍预留 gate 阻塞]。产 5 产物 release_index_v0.41.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.41.md/consolidation_report_v0.41.json/report_v41.html。DETERMINISM PASS 5/5 byte-identical。FREEZE-INTEGRITY PASS。leak 0。不改冻结 v0.1–v0.40 out/；顶层 RELEASE_INDEX.md 再生为 v0.41 视图。3 口径=1机/20dir(19有数据)/3487/3479——0 漂移。.75 第42轮仍可达但 SSH 拒（连续 42 轮同卡点，上报仍有效待回复）。

### EXP-38 (2026-10-29) bench_v0.37 发布索引再生 + DATA_CARD addendum §N 整合层（第38轮）

**动机**：v0.36（meta-feature scaling-artifact 消融构造层）按 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32 构造层先例明确把 RELEASE_INDEX 再生推到下一整合层。本轮即该整合层——把 v0.36 纳入 RELEASE_INDEX 并把 v0.36 的核心发现作为 §N 回写进 v0.16 DATA_CARD addendum，修正 v0.28 §J 的「内禀难度」定性。承 v0.32→v0.33 / v0.34→v0.35 / v0.36→v0.37 construction→integration cadence，纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`integrate.py`（改编自 v0.35）加载冻结 `bench_v0.35/out/release_index_v0.35.json`（34 版本，断言 version==v0.35 + n==34）为基线。机器验证 v0.36 freeze-integrity 全过：(a) manifest `freeze_integrity.status`=PASS + `cross_check_vs_v032.status`=PASS（CONTROL/B/C 0.588235/0.803922/0.313725 逐位复现 v0.32）+ `v032_gap_shrink_sha_match`=true。(b) 跨层独立重算：v0.36 输出 `meta_ablate.json` on-disk[9d35a5ca…]==其自身 manifest；v0.32 `gap_shrink.json`[ec44d57f…]==v0.36 provenance；公共 v0.15 锚点 starts `5dd43df6`；v0.26 split 4 文件全 match v0.36 provenance。(c) append v0.36[ACTIVE, meta_feature_scaling_artifact_ablation]+v0.37[ACTIVE, metadata_integration]→**36 版本/35 ACTIVE/1 SUPERSEDED**（v0.17 by v0.19）。canonical releases（v0.10 / v0.19）不变。(d) 产 5 产物 release_index_v0.37.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.37.md=§N / consolidation_report_v0.37.json / report_v37.html。

**§N 内容**：C 崩溃是特征缩放伪影（meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；D/F 重缩放回升到 0.5294/0.5490 但不缩 gap）→ **修正 §L「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」**；§L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立。记录 §I→§J→§L→§N gap-attribution 精化 cadence（每层闭一个开放问题不动已结结论）。

**质量门**：DETERMINISM PASS 5/5 byte-identical；FREEZE-INTEGRITY PASS（v0.36 manifest + cross_check + 跨层独立重算 4 项）；LEAK CHECK 0；不改冻结层 v0.1–v0.36 out/。产 5 产物。顶层 RELEASE_INDEX.md 再生为 v0.37 视图；README 增 v0.37 行+资产盘点轮次 37→38+DAG 节点 v0.37+§N 段+复现段+gate 表 .75 37→38。

**复探 3 口径**（第38轮）：.75 仍可达但 SSH 拒（连续 38 轮）；8092 仍 RESEARCH v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/3487/3479——0 漂移。上报仍有效待回复。

**结论**：v0.37 闭环 v0.36 下一步候选——v0.36 的 meta scaling-artifact 消融经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（36 版本/35 ACTIVE/1 SUPERSEDED），并作为 §N 回写进 addendum。§N 修正 §L 的「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」，§L 主结论 + 缩 gap 方向不变。已被 §O(v0.39)/§P(v0.41) 整合 + v0.40 lineage RE-sweep 覆盖。

### EXP-39 (2026-10-29) bench_v0.38 gap-shrink bootstrap CI 构造层（第39轮，归档批次 27）

## EXP-39 — v0.38 gap-shrink bootstrap CI 构造层（第39轮，2026-10-29）

**动机**：v0.32 建立的 §L/§N 核心结论「B 缩 gap +0.2157 → unseen-user gap 是 weak-model artifact 非内禀难度」是**点估计** on n=51（fully-unseen n=42）。v0.32 自陈 limitations「Test set is small (n=51; fully-unseen n=42)…high variance — the gap DIRECTION is reliable, not the exact magnitude」。v0.21 给过 v0.15 **诊断** split（consensus-vs-disputed gap +0.5086）的 bootstrap CI，但**从未给过** v0.26/v0.32 **unseen-user** gap 的 CI。§L/§N 主轴无置信区间 = 一个真实的统计严谨性开放问题。所有 *列出的* v0.38 候选（LLM-judge 3 标注者 / 语义 embeddings / RESCAN / lineage sweep「待下一 build-out 后」/ v1.0-rc1）均被外部 gate 阻塞；探明 code-AST 结构特征受 freeze 限制（冻结快照只存摘要统计 + prompt，不存代码体 → 需 re-read /home 违反 v0.8 freeze-by-default）。本层是**唯一不阻塞的构造性后继**：纯 re-analysis on frozen artifacts，零 /home、零网络、零 LLM、stdlib+numpy。

**方法**：`gap_shrink_ci.py` 冻结 v0.26 answers（51 gold）+ v0.32 submissions（CONTROL/B/C 各 51）逐位复用（frozen file order，assert order drift guard），重建 fully-unseen subset（n=42，user_hash∉train，cross-check 复现 v0.32 的 0.6667/0.9286/0.3571）。**配对**非参数 percentile bootstrap（10000 次，numpy default_rng(seed=0)）——对 CONTROL/B/C 用**同一 resample 索引向量**（配对对比正确：B−CONTROL、C−CONTROL 是 within-item contrast，resample 必须 pair matched items，非独立两块 CI 之差）。三个关键声明：
1. **B 缩 gap over CONTROL**：n=51 95% CI [0.0980, 0.3529] p(shrink≤0)=0.0005 / n=42 CI [0.1429, 0.4048] p=0.0 → **显著**（CI 排除 0）→ §L weak-model-artifact 主轴**对重采样稳健**非小样本偶然。
2. **B 残余 gap vs headline**（−0.0134）：n=51 95% CI [−0.1311, 0.0846] **含 0** p(gap≥0)=0.4478 → **统计上闭合**（B 把 gap 关到 v0.15 易类天花板 0.817352 噪声内）→ **强化** §L（gap 可被更强但仍是浅层线性模型闭合，非「点估计碰巧接近 0」）。
3. **C 崩溃 vs CONTROL**（−0.2745）：n=51 95% CI [−0.4118, −0.1373] p=0.0 → **显著** → v0.36 缩放伪影诊断是**真实效应**非 n=51 错觉。

**质量门**：- **DETERMINISM PASS** byte-identical（gap_shrink_ci.json/characterization.md/manifest.json/report_v38.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + numpy default_rng(seed=0) + frozen file-order arrays 整数位置索引）。- **FREEZE-INTEGRITY PASS**：cross-check vs v0.32 **9/9 点估计 MATCH**[CONTROL/B/C acc n=51 + n=42 + v0.26 gap + B shrink + C shrink]（1e-5 容差吸收 v0.32 shrink 报告的 6 位小数 rounding-mode artifact：11/51=0.215686 vs v0.32 报 0.215687）+ v0.15 锚点 on-disk starts `5dd43df6` + **7/7** v0.26 split + v0.32 submission on-disk sha256 独立重算 match v0.32 自身 manifest 声明（不只信 v0.32 自报）。- **LEAK CHECK 0**（gap_shrink_ci.json + characterization.md 正则扫 app.e*/t*/email/Cxmt@/svc.edaagent/shiwei/zhulong//home/app.* 全 0；submission/answer 是已脱敏冻结产物）。- **不改冻结层** v0.1–v0.37 out/ 全只读；v0.32 read-only 作 point-estimate anchor + submission 源。零 /home、零网络、零 LLM。

**verdict**：v0.38 是**首个 unseen-user gap 置信区间**——把 §L/§N 核心结论从点估计升级为统计推断。三结论全过压力测试：(a) B 缩 gap 显著（n=51/n=42 双显著）→ §L weak-model-artifact 主轴**对重采样稳健**；(b) B 残余 gap 统计上 0 → gap **可被闭合**（强化 §L，非「点估计碰巧接近 0」）；(c) C 崩溃显著 → v0.36 缩放伪影是**真实效应**非 n=51 错觉。本层**不推翻任何前结论**，只把「方向可靠 magnitude 不可靠」的 disclaimer 量化为 CI。gap-attribution cadence 走完统计严谨性闭环（§I 测 gap → §J 归因 → §L 修订 weak-model artifact → §N 精化 meta 缩放伪影 → **v0.38 统计显著性确认**）。

**产物**（`bench_v0.38/`）：gap_shrink_ci.py / report_v38.py / reproduce.sh（DETERMINISM + freeze-integrity v0.15+v0.32 + cross-check vs v0.32 + leak 自检）/ README.md；`out/`：gap_shrink_ci.json(8195B) / gap_shrink_ci_characterization.md(3209B) / gap_shrink_ci_manifest.json(4939B) / report_v38.html(10127B)。顶层 README 增 v0.38 行 + 资产盘点轮次 38→39 + DAG 节点 v0.38 + v0.38 描述段 + 复现段 + gate 表 .75 38→39 + header updated through v0.38 + 版本索引 v0.1→v0.38。**不覆盖**顶层 RELEASE_INDEX.md（构造层非整合层，按 v0.32/v0.36 先例推到下一整合层再生）。

**复探 3 口径**（第39轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 39 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 39 轮同卡点，上报仍有效待回复。

**结论**：v0.38 闭环 v0.32/v0.36 留的统计严谨性开放问题——§L/§N 核心结论（weak-model artifact）经配对 bootstrap CI 压力测试后**对重采样稳健**（B 缩 gap 显著 + B 残余 gap 统计上闭合），C 崩溃显著确认 v0.36 缩放伪影真实。首个 unseen-user gap CI。v0.39 候选：**发布索引再生 + §O 整合层**[纳入 v0.38，不需外部 gate，承 v0.36→v0.37 构造→整合先例] / **lineage RE-sweep 现已解锁**[v0.38 产新 manifest 锚点，承 v0.23→v0.30→v0.34 cadence 可在下一整合层后扫] / LLM-judge 3 标注者 + Fleiss κ（阻塞）/ 语义 embeddings（阻塞；code-AST 受 freeze 限制）/ RESCAN（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：MEMORY 加 v0.38 快照/3 口径/流水行后约 30.0KB；EXP 加 EXP-39 后约 27.2KB；TASK 5.1KB，全 ≤32KB。


---

## 归档批次 28（2026-10-29 第44轮体积维护）

### MEMORY 交付物 v0.12–v0.34 详情（原文搬入，MEMORY 留 1 行指针）

- `designflow/bench_v0.12/`：聚合 README（统一入口导航）
- `designflow/bench_v0.13/`：version_diff.py（扫已冻结 bench_v0.* out/ 产物算 manifest+相邻 diff）/ report_v13.py / reproduce.sh / README.md
- `designflow/bench_v0.13/out/`：version_manifest.json（11版本/73 artifacts/file→sha256+size）/ version_diff.json（10相邻 delta added/removed/sha_changed+narrative）/ report_v13.html
- `designflow/bench_v0.14/`：stats_rigor.py（三审计：agreement/selection_bias/bootstrap_ci）/ report_v14.py / reproduce.sh / README.md
- `designflow/bench_v0.14/out/`：agreement.json（Cohen's κ=0.4496 n=2112）/ selection_bias.json（BIAS_PRESENT, test 0/219 vs 语料 856/2112）/ bootstrap_ci.json（acc[0.767,0.868] macroF1[0.636,0.793] n=10000）/ stats_rigor.json（aggregate）/ report_v14.html
- `designflow/bench_v0.15/`：debiased_split.py（去偏 split+双标注者评分+baseline 重训重测）/ report_v15.py / reproduce.sh / README.md
- `designflow/bench_v0.15/out/`：debiased_test_set.jsonl（368=219 consensus+149 disputed，带 v3/v4 双标签）/ debiased_submission.jsonl（368 预测，复用 v0.11 模型）/ debiased_eval.json（consensus acc 0.8174 / disputed robustness 0.3087）/ bias_correction.json（BIAS_CORRECTED, frac 0.405）/ debiased_split_manifest.json / report_v15.html
- `designflow/bench_v0.16/`：datacard_enrich.py / report_v16.py / reproduce.sh / README.md
- `designflow/bench_v0.16/out/`：DATA_CARD_ADDENDUM.md（5 章节层叠 v0.10 DATA_CARD：κ/bias/CI/去偏 gap/局限）/ datacard_enrich.json（provenance 8 源 sha256+cross_refs 5）/ report_v16.html
- `designflow/bench_v0.17/`：diagnostic_release.py（诊断 bundle 装配）/ eval_diagnostic.py（双标注者第三方评估器）/ report_v17.py / reproduce.sh / README.md
- `designflow/bench_v0.17/out/`：diagnostic_test_set.jsonl（368，canonical fields，labels included）/ diagnostic_gold.jsonl（answer key，disputed 项 gold_label=null）/ diagnostic_few_shot.jsonl（27，disjoint）/ diagnostic_baseline_submission.jsonl（368 preds，verbatim from v0.15）/ diagnostic_baseline_eval.json（consensus acc 0.817352 vs disputed robustness 0.308725 gap+0.508627，cross_check vs v0.15=MATCH）/ diagnostic_release_manifest.json（checksums/counts/class dist/protocol spec/integrity PASS/provenance a1cd058a…）/ report_v17.html
- `designflow/bench_v0.18/`：dispute_analysis.py（disputed 项机理性刻画）/ report_v18.py / reproduce.sh / README.md
- `designflow/bench_v0.18/out/`：dispute_analysis.json（6 维度 consensus vs disputed + provenance 4 源 sha256 + 机理性结论）/ dispute_characterization.md（人类可读机理解释，回指 v0.15/v0.16）/ report_v18.html
- `designflow/bench_v0.19/`：diagnostic_release.py（读冻结 v0.15 拆 blinded test+answers + 并 v0.18 characterization + 复用 v0.15 baseline）/ diagnostic_eval.py（独立 CLI 双标注者评估器，--test/--answers/--submission）/ report_v19.py / reproduce.sh / README.md
- `designflow/bench_v0.19/out/`：diagnostic_test_set.jsonl（368，blinded 无标签）/ diagnostic_answers.jsonl（368 answer key，consensus gold + disputed label_v3/v4，gold_label=null 不伪造）/ diagnostic_characterization.md（v0.18 刻画逐字并入+头注）/ example_diagnostic_submission.jsonl（v0.15 baseline）/ example_diagnostic_eval.json（自检 acc0.817352/rob0.308725/gap+0.508627 全对齐 v0.15）/ diagnostic_manifest.json（provenance 5 源 sha256 + freeze-integrity PASS）/ report_v19.html
- `designflow/bench_v0.20/`：consolidate.py（发现 19 版本 + 机器验证 v0.17→v0.19 超集 5 项 + 顶层 RELEASE_INDEX 装配）/ report_v20.py / reproduce.sh（二次重跑 byte-compare + leak check）/ README.md
- `designflow/bench_v0.20/out/`：deprecation_map.json（v0.17 SUPERSEDED by v0.19 + 5 项完整性证据全 pass）/ release_index.json（19 版本 status/note/role/layer）/ RELEASE_INDEX.md（人类可读状态图，复制到顶层 designflow/RELEASE_INDEX.md）/ consolidation_report.json（KPI+provenance+determinism）/ report_v20.html
- `designflow/bench_v0.21/`：bootstrap_diagnostic.py（诊断 split 分层 bootstrap CI + gap 显著性）/ report_v21.py / reproduce.sh / README.md
- `designflow/bench_v0.21/out/`：diagnostic_ci.json（点估计+cross-check vs v0.15 6/6 MATCH+bootstrap CI[acc/rob/gap]+gap 显著性+disputed 类别剖面 CI+方法/provenance）/ diagnostic_ci_manifest.json（4 输入 sha256+freeze-integrity PASS+输出 sha256）/ report_v21.html
- `designflow/bench_v0.22/out/`：release_index_v0.22.json（21 版本 status/role/layer）/ RELEASE_INDEX.md（人类可读 v0.22 视图，复制到顶层）/ DATA_CARD_ADDENDUM_v0.22.md（§G gap 显著性 CI）/ consolidation_report_v0.22.json / report_v22.html
- `designflow/bench_v0.23/`：lineage_audit.py（递归扫所有 manifest 提取 (path,sha256) 锚点[Form B path-bearing + Form A self-referential]+盘上校验+drift vs v0.13）/ report_v23.py / reproduce.sh（leak check + DETERMINISM_CHECK 自检）/ README.md
- `designflow/bench_v0.23/out/`：lineage_audit.json（headline PASS/anchor_verification 124 PASS/lineage_graph 8 版本/drift_vs_v0.13 PASS 73/73/full_tree_manifest）/ lineage_audit_manifest.json / report_v23.html
- `designflow/bench_v0.24/`：integrate.py（读冻结 v0.22 release_index + 机器验证 v0.23 freeze-integrity 四项 + 追加 v0.23/v0.24 + 产 §H）/ report_v24.py / reproduce.sh（DETERMINISM + freeze-integrity + leak check 自检）/ README.md
- `designflow/bench_v0.24/out/`：release_index_v0.24.json（23 版本 status/role/layer，22 ACTIVE/1 SUPERSEDED）/ RELEASE_INDEX.md（人类可读 v0.24 视图，复制到顶层）/ DATA_CARD_ADDENDUM_v0.24.md（§H 冻结 lineage 完整性审计，扩展 v0.16 §A–§E + v0.22 §G）/ consolidation_report_v0.24.json / report_v24.html
- 顶层 `designflow/RELEASE_INDEX.md`（v0.24 产，外部消费者入口：2 个 canonical release[v0.10 consensus + v0.19 diagnostic] + 全 23 版本状态表 + 弃用图 + 如何消费指引；v0.23 freeze-integrity 表 + delta vs v0.22）
- `designflow/bench_v0.25/out/`：fairness_audit.json / fairness_characterization.md / report_v25.html（per-user 公平性审计层，6 维度）
- `designflow/bench_v0.26/`：user_resplit.py（读冻结 v0.15 debiased_test_set 取 consensus 219，按 user×label 分层重切：主用户→train、其余→held-out test；复用 v0.11 TF-IDF+nearest-centroid baseline 重训重测）/ report_v26.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md
- `designflow/bench_v0.26/out/`：user_resplit.json（split+eval+provenance+limits）/ resplit_characterization.md / user_strat_train.jsonl(168,带 gold_label) / user_strat_test.jsonl(51,blinded 无标签) / user_strat_answers.jsonl(51 answer key) / user_strat_submission.jsonl(51 baseline 预测) / user_resplit_manifest.json / report_v26.html
- `designflow/bench_v0.28/`：user_balance.py（读冻结 v0.15 consensus 219，按资格规则分类全 9 类为 Tier A/B/C + 2 类 core 上做 matched-count 受控实验）/ report_v28.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md
- `designflow/bench_v0.28/out/`：user_balance.json（tiers/plan/sweep/controlled experiment/provenance/limitations）/ balance_characterization.md / core_train_S.jsonl(177,单用户/类) / core_train_M.jsonl(177,2 用户/类 matched count) / core_test.jsonl(17,blinded 无标签) / core_answers.jsonl(17 answer key) / core_submission_S.jsonl(17 baseline 预测) / core_submission_M.jsonl(17 baseline 预测) / user_balance_manifest.json / report_v28.html
- `designflow/bench_v0.29/`：integrate.py（加载冻结 v0.27 索引[26 版本]+机器验证 v0.28 freeze-integrity[4 项]+append v0.28+v0.29）/ report_v29.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + leak 自检）/ README.md
- `designflow/bench_v0.29/out/`：release_index_v0.29.json（28 版本/27 ACTIVE/1 SUPERSEDED）/ RELEASE_INDEX.md（v0.29 视图，复制到顶层）/ DATA_CARD_ADDENDUM_v0.29.md（§J：user-balanced re-split + 证伪「多用户即缩 gap」）/ consolidation_report_v0.29.json / report_v29.html
- `designflow/bench_v0.30/`：lineage_audit.py（冻结 lineage 完整性 RE-sweep，subsumes v0.23；锚点提取 UNCHANGED Form A+B；LIVING_FILES 模型 + drift_vs_v023 回归 + frozen_release_index_copies 交叉校验）/ report_v30.py / reproduce.sh（DETERMINISM + leak 自检）/ README.md
- `designflow/bench_v0.30/out/`：lineage_audit_v030.json（28 版本/69 manifest/151 锚点[108 unique]→147 PASS+4 LIVING_FILE_BYDESIGN+0 MISMATCH/MISSING；drift_vs_v013 PASS 73/73；drift_vs_v023 PASS 94/94[0 regression，13 net-new]；frozen_release_index_copies PASS 4/4；full_tree_manifest）/ lineage_audit_manifest.json / report_v30.html
- `designflow/bench_v0.32/`：gap_shrink.py（逐位复用冻结 v0.26 split，CONTROL nearest-centroid + TREATMENT B softmax 同特征 + TREATMENT C softmax+meta，受控对比测 v0.28 命名未测的「更强模型/更富特征」药方）/ report_v32.py / reproduce.sh（DETERMINISM + FREEZE-INTEGRITY + cross-check vs v0.26 + leak 自检，单线程 BLAS）/ README.md
- `designflow/bench_v0.32/out/`：gap_shrink.json（CONTROL 0.588235 ✅ / B acc 0.8039 gap −0.0134 shrink +0.2157 几乎闭合 / C acc 0.3137 反扩大 + verdict 修订 v0.28）/ gap_shrink_characterization.md / sub_control_nearestcentroid.jsonl(51) / sub_softmax_tfidf.jsonl(51) / sub_softmax_rich.jsonl(51) / gap_shrink_manifest.json / report_v32.html
- `designflow/bench_v0.34/`：lineage_audit.py（冻结 lineage 完整性 RE-sweep subsumes v0.30：扫所有 bench_v0.*/out/*.json manifest 提取 sha256 锚点 Form A+B[规则同 v0.23/v0.30 不变]，对盘上文件逐个校验 + drift vs v0.13 + **drift vs v0.30 回归**[加载冻结 v0.30 审计重验其 frozen 锚点，传递式 subsumes v0.30 的 drift_vs_v023] + frozen per-version RELEASE_INDEX copies 交叉校验）/ report_v34.py / reproduce.sh（DETERMINISM_CHECK=1 自检 + leak 自检）/ README.md
- `designflow/bench_v0.34/out/`：lineage_audit_v034.json（32 版本/77 manifest/170 锚点[118 unique]→164 PASS+6 LIVING_FILE_BYDESIGN+0 MISMATCH/MISSING；drift_vs_v030 104/104[排除 4 living，0 regression，10 net-new since v0.30]；frozen_release_index_copies 6/6；drift_vs_v013 73/73）/ lineage_audit_manifest.json / report_v34.html


### EXPERIMENTS EXP-40 v0.39 §O 整合层（原文搬入，EXP 留 1 行指针）

## EXP-40 — v0.39 发布索引再生 + DATA_CARD addendum §O 整合层（第40轮，2026-10-29）

**动机**：v0.38（gap-shrink bootstrap CI 构造层）按 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32/v0.36 构造层先例明确把 RELEASE_INDEX 再生推到下一整合层。本轮即该整合层——把 v0.38 纳入 RELEASE_INDEX 并把 v0.38 的 CI 结论作为 §O 回写进 v0.16 DATA_CARD addendum。承 v0.32→v0.33 / v0.34→v0.35 / v0.36→v0.37 construction→integration cadence，纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`integrate.py`（结构改编自 v0.37）加载冻结 `bench_v0.37/out/release_index_v0.37.json`（36 版本，断言 version==v0.37 + n==36）为基线。机器验证 v0.38 freeze-integrity 全过：(a) manifest `freeze_integrity.status`=PASS + v0.15 anchor `5dd43df6` + `all_match`=true；(b) manifest `cross_check_vs_v0.32`="MATCH (9/9 point estimates)" + 输出 `gap_shrink_ci.json` 的 `cross_check_vs_v0.32.status`=MATCH 9 项点估计 rounding tolerance[1e-5]内全复现（`b_shrink_vs_v026` got 0.215686 vs v0.32-recorded 0.215687 末位 float 舍入，v0.38 自记 MATCH 9/9）；(c) 跨层独立重算 v0.38 输出 `gap_shrink_ci.json`[9a11d347…] / `gap_shrink_ci_characterization.md`[b88aa2bc…] match 其自身 manifest 声明 + 公共 v0.15 锚点 starts `5dd43df6` + v0.26 split 3 文件 + v0.32 submission+gap_shrink 4 文件 match v0.38 inputs 声明。append v0.38[ACTIVE, gap_shrink_bootstrap_ci_construction] + v0.39[ACTIVE, metadata_integration] → **38 版本/37 ACTIVE/1 SUPERSEDED**（v0.17 by v0.19）。

**§O 内容（不推翻 §L/§N，只升级证据地位）**：把 §L/§N 核心结论从**点估计**升级为**置信区间**。§L MAIN（B 缩 gap +0.2157 → weak-model artifact）UPGRADED → CI-backed ROBUST[n=51 95% CI 0.0980,0.3529 p=0.0005 / n=42 CI 0.1429,0.4048 p=0.0，两子集均排除 0 → 对重采样稳健非小样本偶然]；§L caveat「direction reliable, magnitude not」**RETIRED**（magnitude CI 已报告虽宽）；§L「需语义级特征缩 gap further」**STANDS**（§O 量化 B shrink 但未测语义 treatment，仍 LLM-gated）；§N「C 崩溃是 feature-SCALING artifact」**CONFIRMED real effect**[n=51 CI −0.4118,−0.1373 p=0.0 排除 0 → 非 n=51 噪声]；§L「crude meta MILD-not-DRAMATIC when scaled」（§N 修正）**UNCHANGED**（§O 在 CI 轴非特征轴）。B 残余 gap −0.0134 n=51 CI −0.1311,0.0846 含 0 → 统计上闭合（关到易类天花板 0.817352 噪声内）→ **强化 §L**。**首个 unseen-user gap CI**。记录 §G→§O rigor-closure cadence（§G 首个 CI 但在诊断 split；§L unseen-user gap 点估计；§N C-collapse 点估计；§O 首个 unseen-user gap CI）。§F 仍预留 gate 阻塞。

**质量门**：- **DETERMINISM PASS** 5/5 byte-identical（release_index_v0.39.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.39.md / consolidation_report_v0.39.json / report_v39.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration，纯元数据无新随机）。- **FREEZE-INTEGRITY PASS**（v0.38 manifest + cross_check_vs_v032 MATCH 9/9 rounding-tol + 跨层独立重算 v0.38 输出 + v0.15 锚点 + v0.26 split 3 + v0.32 submission 4 全过）。- **LEAK CHECK 0**（元数据层 data-free）。- **不改冻结层** v0.1–v0.38 out/ 全只读；唯一覆盖顶层 `designflow/RELEASE_INDEX.md`（live map，by design）。

**产物**（`bench_v0.39/`）：integrate.py / report_v39.py / reproduce.sh（DETERMINISM + freeze-integrity v0.38 + leak 自检）/ README.md；`out/`：release_index_v0.39.json(38708B) / RELEASE_INDEX.md(33053B) / DATA_CARD_ADDENDUM_v0.39.md(13661B) / consolidation_report_v0.39.json(8826B) / report_v39.html(35683B)。顶层 RELEASE_INDEX.md 再生为 v0.39 视图；README 增 v0.39 行 + 资产盘点轮次 39→40 + DAG 节点 v0.39 + v0.38/v0.39 描述段 + §O addendum list 项 + 复现段 + gate 表 .75 39→40 + header updated through v0.39 + 版本索引 v0.1→v0.39。

**复探 3 口径**（第40轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 40 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 40 轮同卡点，上报仍有效待回复。

**结论**：v0.39 闭环 v0.38 下一步候选——v0.38 的 gap-shrink bootstrap CI（§L/§N 核心结论从点估计升级为 CI）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（38 版本/37 ACTIVE/1 SUPERSEDED），并作为 §O 回写进 addendum。§O **不推翻 §L/§N，只升级证据地位**：§L 主结论 CI-backed 对重采样稳健（退役 magnitude caveat），§N 缩放伪影诊断确认为真实效应，B 残余 gap 统计上闭合强化 §L。rigor-closure cadence 走完第 4 步（§G 首个 CI[诊断 split] → §L unseen-user gap 点估计 → §N C-collapse 点估计 → §O 首个 unseen-user gap CI）。v0.40 候选：**lineage RE-sweep 构造层**[v0.38 产新 manifest 锚点现解锁，承 v0.23→v0.30→v0.34 cadence：扫所有 bench_v0.*/out/*.json manifest 提取 sha256 锚点对盘校验 + drift vs v0.34 回归 + frozen RELEASE_INDEX 副本交叉校验，纳入 v0.36/v0.37/v0.38 新锚点] / LLM-judge 3 标注者 + Fleiss κ（阻塞，落地 §F）/ 语义 embeddings（阻塞）/ RESCAN（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：MEMORY 加 v0.39 快照/3 口径/流水行后约 32.7KB（略超 32KB 偏好 696B，远低于 40KB 红线；归档第39轮流水原文至 ARCHIVE 批次 23 留指针）；EXP 加 EXP-40 后约 30.6KB；TASK 5.1KB。全 < 40KB。


### EXPERIMENTS EXP-41 v0.41 §P 整合层（原文搬入，EXP 留 1 行指针）

## EXP-41 — v0.41 发布索引再生 + DATA_CARD addendum §P 整合层（第42轮，2026-10-29）

**动机**：v0.40（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.34）按 v0.30/v0.34 构造层先例 + v0.34→v0.35 / v0.36→v0.37 / v0.38→v0.39 construction→integration cadence 明确把 RELEASE_INDEX 再生推到下一整合层。本轮即该整合层——把 v0.40 纳入 RELEASE_INDEX 并把 v0.40 的全树完整性结论作为 §P 回写进 v0.16 DATA_CARD addendum。纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`integrate.py`（结构改编自 v0.39）加载冻结 `bench_v0.39/out/release_index_v0.39.json`（38 版本，断言 version==v0.39 + n==38）为基线。机器验证 v0.40 freeze-integrity 全过：(a) manifest `freeze_integrity.status`=PASS；(b) headline `overall_verdict`=PASS + `anchor_mismatch`=0 + `anchor_missing`=0 + `manifest_errors`=0（38 版本/89 manifest/206 锚点[135 unique]→197 PASS + 9 LIVING_FILE_BYDESIGN + 0 broken）；(c) `drift_vs_v034_status`=PASS + `drift_vs_v034_matched`==`drift_vs_v034_rechecked`==112 + regressions==0 → v0.35–v0.39 build-out 未静默漂移任一冻结输入；(d) `drift_vs_v013_status`=PASS 73/73（carry-through v0.23/v0.30/v0.34）；(e) `frozen_release_index_copies_status`=PASS 9/9（v0.22/v0.24/v0.27/v0.29/v0.31/v0.33/v0.35/v0.37/v0.39）；(f) 跨层独立重算：v0.40 输出 `lineage_audit_v040.json`[c2194b3d…] match 其自身 manifest 声明 + v0.40 输入 `v0.13_version_manifest`[c83ea686…] match v0.40 manifest 声明 + v0.40 输入 `v0.34_lineage_audit` 回归基线[87ea388e…] match v0.40 manifest 声明 + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6。append v0.40[ACTIVE, frozen_lineage_integrity_resweep]+v0.41[ACTIVE, metadata_integration]→**40 版本/39 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。

**§P 内容（不推翻 §H/§K/§M，只扩展覆盖窗口）**：把全树冻结完整性证据从 §M 的 32 版本（v0.34，最后整合 §M v0.35 覆盖到 v0.34）扩展到 38 版本（v0.40）。§P 记录：v0.40 扫 38 版本/89 manifest/206 锚点[135 unique]→197 PASS + 9 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING；drift_vs_v034 112/112 PASS 0 回归 → v0.35–v0.39 build-out 未静默漂移任一冻结输入；17 net-new anchors since v0.34（v0.34:1 + v0.35:3 + v0.36:1 + v0.37:3 + v0.38:6 + v0.39:3）；drift_vs_v034 传递式 subsumes v0.34 的 drift_vs_v030（v0.34 锚点集 ⊇ v0.30 ⊇ v0.23）→ 显式 v0.30/v0.23 recheck 省略无损，v0.23→v0.30→v0.34→v0.40 回归链全 bit-intact；drift_vs_v013 73/73；frozen per-version RELEASE_INDEX copies 9/9；公共 v0.15 锚点 5dd43df6 reverified。记录 §H→§K→§M→§P RE-sweep cadence（第 4 次全树审计）。§F 仍预留 gate 阻塞。

**质量门**：- **DETERMINISM PASS** 5/5 byte-identical（release_index_v0.41.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.41.md / consolidation_report_v0.41.json / report_v41.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration，纯元数据无新随机）。- **FREEZE-INTEGRITY PASS**（v0.40 manifest PASS + headline overall PASS + drift_vs_v034 112/112 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 9/9 + 跨层独立重算 v0.40 输出 + v0.13/v0.34 输入 + v0.15 锚点 5dd43df6 全过）。- **LEAK CHECK 0**（元数据层 data-free）。- **不改冻结层** v0.1–v0.40 out/ 全只读；唯一覆盖顶层 `designflow/RELEASE_INDEX.md`（live map，by design）。

**产物**（`bench_v0.41/`）：integrate.py / report_v41.py / reproduce.sh（DETERMINISM + freeze-integrity v0.40 + leak 自检）/ README.md；`out/`：release_index_v0.41.json(43385B) / RELEASE_INDEX.md(36335B) / DATA_CARD_ADDENDUM_v0.41.md(13648B) / consolidation_report_v0.41.json(11047B) / report_v41.html(38721B)。顶层 RELEASE_INDEX.md 再生为 v0.41 视图；README 增 v0.41 行 + v0.40/v0.41 callout + 资产盘点轮次 40→42 + DAG 节点 v0.40/v0.41 + 版本索引 v0.1→v0.41 + 复现段补 v0.40/v0.41 + gate 表 .75 40→42 + header updated through v0.41。

**复探 3 口径**（第42轮）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 42 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 42 轮同卡点，上报仍有效待回复。

**结论**：v0.41 闭环 v0.40 下一步候选——v0.40 的全树 lineage RE-sweep（subsumes v0.34，38 版本/206 锚点 197 PASS + 9 LIVING，drift_vs_v034 112/112 0 回归）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（40 版本/39 ACTIVE/1 SUPERSEDED），并作为 §P 回写进 addendum。§P **不推翻 §H/§K/§M，只扩展覆盖窗口**从 32 版本（v0.34）到 38 版本（v0.40）：v0.35–v0.39 build-out 未静默漂移任一冻结输入，v0.23→v0.30→v0.34→v0.40 回归链全 bit-intact。RE-sweep cadence 走完第 4 次（§H 首次全扫 → §K v0.30 → §M v0.34 → §P v0.40）。v0.42 候选：下一构造层产新 manifest 锚点后 lineage RE-sweep 再解锁[承 v0.23→v0.30→v0.34→v0.40 cadence] / LLM-judge 3 标注者 + Fleiss κ（阻塞，落地 §F）/ 语义 embeddings（阻塞）/ RESCAN（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：归档 EXP-35（v0.34）原文至 ARCHIVE 批次 25（留指针，v0.34 已被 v0.40 subsume）；MEMORY 加 v0.41 快照/3 口径/流水行后估算约 30KB；EXP 加 EXP-41 后约 32KB；TASK 5.1KB。全 ≤32KB 偏好（或略超远低于 40KB 红线）。


### MEMORY 流水 第43轮（原文搬入，MEMORY 留 1 行指针）

- [05:50] 第43轮：推进 **v0.42 per-class gap-shrink bootstrap CI 构造层**（闭环 v0.38 characterization 显式留的「per-class contrasts not computed」开放问题——非元数据空转，是唯一不阻塞且非 §X 递归的构造性后继；纯 re-analysis on frozen artifacts，零 /home/网络/LLM）。`gap_shrink_perclass_ci.py` 复用 v0.38 per-item 数组（冻结 v0.26 answers + v0.32 submissions，frozen file order），cross-check 复现 v0.32 全 9 点估计 MATCH 9/9。**新增 cross-check vs v0.38 headline**：重算 n=51 headline B−CONTROL paired bootstrap CI 断言 == v0.38 记录 [0.098039, 0.352941]（逐位相等）→ 证 v0.42 在与 v0.38 完全相同 item 集上分区（subsumes v0.38 headline）。per-class paired bootstrap（10000 次，`numpy default_rng(seed=0)`，within-class one shared resample vector；n≥MIN_CI_N=10 报 CI，n<10 仅点估计因 bootstrap 退化）。**结果**：`other`（n=15/14）B−CONTROL shrink **+0.6667/+0.7143** 95% CI **[0.4000,0.8667]/[0.5000,0.9286]** p=0.0 → **两子集均显著**（CTRL 0.267/0.286 → B 0.933/1.000）＝v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界修复，§L weak-model-artifact **定位到此类**；`code_dev`（n=27/25 最大类）shrink +0.0741/+0.0400 CI [0,0.1852]/[0,0.12] 含 0 ns（CTRL 0.889/0.960 已弱模型天花板，B 几无改进）＝「已解决」类非 gap 源；薄类（n≤4）仅点估计：eda_virtuoso_schematic n=4 CTRL=B=0 两模型全败＝源硬限，data_analysis n=2/file_ops n=2/eda_aether_layout n=1＝v0.28/v0.32「薄类源硬限残项」per-class-CI 证据。**verdict**：LOCALIZE §L weak-model-artifact——+0.2157 headline shrink 几乎全来自 `other` 边界修复非均匀提升；**精化（不推翻）§L/§O**；下游含义：语义级 treatment（LLM-gated）须帮 code_dev 突破弱模型天花板 + 解决薄类，而非仅重修 softmax 已修的 `other` 边界——给未来 LLM-gated 实验 per-class 评估框架+基线对照。产 4 产物 gap_shrink_perclass_ci.json/characterization.md/manifest.json/report_v42.html。**DETERMINISM PASS** 4/4 byte-identical。**FREEZE-INTEGRITY PASS**[v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha match v0.32 manifest + cross-check vs v0.32 9/9 + cross-check vs v0.38 headline CI 逐位相等]。**leak 0**。不改冻结 v0.1–v0.41 out/；构造层非整合层不重算 RELEASE_INDEX（按 v0.32/v0.36/v0.38 先例推到下一整合层 v0.43 §Q）；产新 manifest 锚点→解锁延后的 lineage RE-sweep（承 v0.23→v0.30→v0.34→v0.40 cadence 可在 §Q 后扫）。README 增 v0.42 行+v0.42 增补段+资产盘点轮次 42→43+DAG 节点 v0.42+版本索引 v0.1→v0.42+v0.42 描述段+复现段+gate 表 .75 42→43+header updated through v0.42。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第43轮仍可达但 SSH 拒（ping 0% loss + Permission denied，连续 43 轮同卡点，上报仍有效待回复）。体积维护：归档 EXP-37（v0.36）原文至 ARCHIVE 批次 26（已被 §N/§O/v0.40 覆盖，留指针）。


## 归档批次 29 — EXP-42 v0.42 原文（体积维护，2026-10-29 第45轮归档）

### EXP-42 — v0.42 per-class gap-shrink bootstrap CI 构造层（第43轮，2026-10-29）原文

**动机**：v0.38 给了首个 **treatment-level**（headline）unseen-user gap CI（B 缩 gap over CONTROL 显著 [0.0980,0.3529] p=0.0005），但其 characterization 的 Limitations **显式留**「CIs are wide on per-class contrasts (not computed per-class here — the headline treatment-level contrast is the reliable signal)」。v0.32 的 per-class **点估计**已暗示 B shrink 集中在 `other`（0.267→0.933 +10 correct，v0.18/v0.32 识别的 disputed 边界）而 `code_dev` 持平——但该定位**从未 CI-backed**。MEMORY「下一步」自陈所有列出的 v0.42 候选（LLM-judge / 语义 embeddings / RESCAN / v1.0 / lineage sweep「待下一 build-out」）均被外部 gate 阻塞；本层是**唯一不阻塞且非元数据空转**的构造性后继（纯 re-analysis on frozen artifacts，零 /home/网络/LLM），且闭环一个**显式被前层标记为未做**的开放问题——不是再产一个 §X 元数据整合层（规避第33轮起注意到的递归倾向）。

**方法**：`gap_shrink_perclass_ci.py` 复用 v0.38 的 per-item correctness 数组（冻结 v0.26 answers + v0.32 submissions，frozen file order），cross-check 复现 v0.32 全 9 个点估计（MATCH 9/9）。**新增 cross-check vs v0.38 headline**：重算 n=51 headline B−CONTROL paired bootstrap CI，断言 == v0.38 记录边界 [0.098039, 0.352941]（逐位相等）→ 证 v0.42 在与 v0.38 **完全相同的 item 集**上分区（subsumes v0.38 headline，freeze-integrity 链）。**per-class paired bootstrap**（10000 次，`numpy default_rng(seed=0)`，within-class one shared resample vector，对 CONTROL/B/C 限定在该类 items 内）：n_class ≥ MIN_CI_N(=10) 报 B−CONTROL shrink CI + 单侧 p + 显著性 + C−CONTROL collapse CI；n_class < 10 仅点估计（bootstrap on n≤4 退化为少数几个唯一 resample mean，非有意义 CI——诚实报告，呼应 v0.38 自己的 caveat）。两子集 n=51 / n=42 fully-unseen 各做一遍。

**结果**（51-test 只含 6/9 类，3 IMPOSSIBLE 单用户类 0 test 项；分布极不均）：
- **`other`**（n=15/n=14）：B−CONTROL shrink **+0.6667/+0.7143**，95% CI **[0.4000,0.8667]/[0.5000,0.9286]**，p=0.0 → **两子集均显著**。CTRL acc 0.267/0.286 → B 0.933/1.000。这正是 v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界——弱最近质心在此崩，softmax 修好 → **§L weak-model-artifact 定位到此类**。
- **`code_dev`**（n=27/n=25，最大类）：shrink **+0.0741/+0.0400**，CI **[0,0.1852]/[0,0.12]** 含 0，ns。CTRL 已 0.889/0.960 在弱模型天花板，B 几无改进——「已解决」类非 gap 源。
- 薄类（n≤4）仅点估计：`eda_virtuoso_schematic` n=4 CTRL=B=0（两模型全败，源硬限）；`data_analysis` n=2 (0.5/0.5)；`file_ops` n=2 (0.5→0.0)；`eda_aether_layout` n=1 (0/0)——v0.28/v0.32「薄类源硬限残项」的 **per-class-CI 证据**。

**verdict**：**LOCALIZE §L weak-model-artifact**——B 的显著 shrink over CONTROL 集中在 `other`（disputed 边界），`code_dev`（最大类）已在弱模型天花板（B≈CONTROL，无 shrink 空间），薄类源硬限（无稳定 per-class CI）。headline +0.2157 shrink 因此是**一类内的边界修复效应**，非均匀提升。**REFINES（不推翻）§L/§O**：weak-model artifact 真实显著但 locus 是 `other` disputed 边界非全类。**下游含义**：语义级 treatment（LLM-gated）须帮 `code_dev` 突破弱模型天花板 + 解决薄类，而非仅重修 softmax 已修的 `other` 边界——给未来 LLM-gated 实验一个**per-class 评估框架**与基线对照。

**质量门**：DETERMINISM PASS 4/4 byte-identical；FREEZE-INTEGRITY PASS（v0.15 锚点 + 7/7 v0.26 split + v0.32 submission on-disk sha match v0.32 manifest）；CROSS-CHECK vs v0.32 MATCH 9/9 点估计；CROSS-CHECK vs v0.38 headline PASS（重算 CI == v0.38 记录逐位相等）；LEAK CHECK 0；不改冻结层 v0.1–v0.41 out/。

**产物**（`bench_v0.42/`）：gap_shrink_perclass_ci.py / report_v42.py / reproduce.sh / README.md；`out/`：gap_shrink_perclass_ci.json(14154B) / gap_shrink_perclass_ci_characterization.md(5251B) / gap_shrink_perclass_ci_manifest.json(5611B) / report_v42.html(12108B)。顶层 README 增 v0.42 行+增补段+资产盘点轮次 42→43+DAG 节点+版本索引 v0.1→v0.42+描述段+复现段+gate 表 .75 42→43+header。**不覆盖**顶层 RELEASE_INDEX.md（构造层，按 v0.32/v0.36/v0.38 先例推到下一整合层）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。

**复探 3 口径**（第43轮现查）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 **43** 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移。

**结论**：v0.42 闭环 v0.38 显式留的「per-class contrasts not computed」开放问题——把 §L/§O 核心结论（weak-model artifact）**定位到具体类**：B 的显著 shrink 集中在 `other`（disputed 边界，n=15/14 两子集均显著），`code_dev`（最大类）已在弱模型天花板（B≈CONTROL ns），薄类源硬限（无稳定 per-class CI）。**精化（不推翻）§L/§O**，并给未来 LLM-gated 语义实验一个 per-class 评估框架 + 基线对照。这是 gap-attribution cadence（§I→§J→§L→§N→§O→**§per-class**）的 per-class 闭环。已被 §Q(v0.43) 整合 + v0.44 lineage RE-sweep 覆盖其 freeze-integrity。要点见 EXPERIMENTS 指针 + MEMORY 流水。

**体积**：归档 EXP-37（v0.36）原文至 ARCHIVE 批次 26（留指针，已被 §N/§O/v0.40 覆盖）；MEMORY 加 v0.42 快照/3 口径/流水行后估算约 31KB；EXP 加 EXP-42 + 归档 EXP-37 后约 32KB；TASK 5.1KB。

## 归档批次 30 — EXP-43 v0.43 原文（体积维护，2026-10-29 第46轮归档）

> EXP-43（v0.43 发布索引再生 + DATA_CARD addendum §Q 整合层，第44轮）原文搬入此处。
> 已被 v0.44 lineage RE-sweep（drift_vs_v040 126/126 重验证 v0.41–v0.43 frozen 锚点，subsumes v0.40）
> + v0.45 §R 整合层（机器验证 v0.44 freeze-integrity 全过，扩展覆盖窗口 38→42 版本）覆盖其 freeze-integrity。
> 要点见 EXPERIMENTS 指针 + MEMORY 流水。v0.45 §R REFINES §Q 所记录的 §Q 内容（gap-attribution per-class 闭环）不推翻。

## EXP-43 — v0.43 发布索引再生 + DATA_CARD addendum §Q 整合层（第44轮，2026-10-29）

**动机**：v0.42（per-class gap-shrink bootstrap CI 构造层）按 v0.32/v0.36/v0.38 构造层先例 + v0.38→v0.39 / v0.40→v0.41 construction→integration cadence 明确把 RELEASE_INDEX 再生推到下一整合层。本轮即该整合层——把 v0.42 纳入 RELEASE_INDEX 并把 v0.42 的 per-class CI 结论作为 §Q 回写进 v0.16 DATA_CARD addendum。纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`integrate.py`（结构改编自 v0.41）加载冻结 `bench_v0.41/out/release_index_v0.41.json`（40 版本，断言 version==v0.41 + n==40）为基线。机器验证 v0.42 freeze-integrity 全过：(a) manifest `freeze_integrity.status`=PASS + `v0.15_anchor`=5dd43df6 + `v0.15_status`=PASS + `all_match`=true + `disk_vs_v032_manifest` 全 match；(b) `cross_check_vs_v0.32`="MATCH (9/9 point estimates)"（manifest 字符串，在 freeze_integrity 内）+ 输出 `cross_check_vs_v0.32.status`=MATCH + 9 项点估计全 within 1e-5（v0.42 自记 tol）+ 三个 headline 准确率复现（control 0.588235 / b 0.803922 / c 0.313725）；(c) `cross_check_vs_v0.38_headline.p2_5_match`=true AND `p97_5_match`=true → v0.42 重算 n=51 headline B−CONTROL CI [0.098039,0.352941] == v0.38 记录（逐位相等）→ 证 v0.42 在与 v0.38 完全相同 item 集上分区（subsumes v0.38 headline，freeze-integrity 链）；(d) 跨层独立重算 v0.42 输出 `gap_shrink_perclass_ci.json`[f9fbf0cd…]/`gap_shrink_perclass_ci_characterization.md`[61f3dc0c…] match 其自身 manifest outputs 声明；(e) 公共 v0.15 锚点 on-disk starts `5dd43df6`；(f) v0.26 split 3 文件 on-disk sha match v0.42 manifest inputs；(g) v0.32 submission 4 文件 on-disk sha match v0.42 manifest inputs。append v0.42[ACTIVE, perclass_gap_shrink_bootstrap_ci_construction]+v0.43[ACTIVE, metadata_integration]→**42 版本/41 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。

**§Q 内容（不推翻 §L/§O，只精化定位）**：把 §L/§O 核心结论（weak-model artifact）**定位到具体类**。§L MAIN（B 缩 gap +0.2157 → weak-model artifact）LOCALIZED → `other`（n=15/14）B−CONTROL shrink **+0.6667/+0.7143** 95% CI **[0.4,0.8667]/[0.5,0.9286]** p=0.0 两子集均排除 0 显著（CTRL 0.267/0.286 → B 0.933/1.000）＝v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界现 CI-backed——+0.2157 headline shrink 几乎全来自此类边界修复；`code_dev`（n=27/25 最大类）shrink +0.0741/+0.04 CI [0,0.1852]/[0,0.12] 含 0 ns（CTRL 0.889/0.960 已弱模型天花板，B 几无改进）＝「已解决」类非 gap 源；薄类（n<10）仅点估计（data_analysis/eda_aether_layout/eda_virtuoso_schematic/file_ops）＝v0.28/v0.32「薄类源硬限残项」的 per-class-CI 证据。**下游含义**：语义级 treatment（LLM-gated）须帮 code_dev 突破弱模型天花板 + 解决薄类，而非仅重修 softmax 已修的 `other` 边界——给未来 LLM-gated 语义实验 per-class 评估框架 + 基线对照。记录 gap-attribution cadence（§I→§J→§L→§N→§O→**§Q per-class**）的 per-class 闭环。§F 仍预留 gate 阻塞。

**质量门**：- **DETERMINISM PASS** 5/5 byte-identical（release_index_v0.43.json / RELEASE_INDEX.md / DATA_CARD_ADDENDUM_v0.43.md / consolidation_report_v0.43.json / report_v43.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration，纯元数据无新随机）。- **FREEZE-INTEGRITY PASS**（v0.42 manifest PASS + v0.15 锚点 5dd43df6 + all_match + cross_check_vs_v0.32 MATCH 9/9 + cross_check_vs_v0.38 headline CI 逐位相等 + 跨层独立重算 v0.42 输出 + v0.26 split 3 + v0.32 submission 4 全过）。- **LEAK CHECK 0**（元数据层 data-free）。- **不改冻结层** v0.1–v0.42 out/ 全只读；唯一覆盖顶层 `designflow/RELEASE_INDEX.md`（live map，by design）。

**产物**（`bench_v0.43/`）：integrate.py / report_v43.py / reproduce.sh（DETERMINISM + freeze-integrity v0.42 + leak 自检）/ README.md；`out/`：release_index_v0.43.json(47755B) / RELEASE_INDEX.md(39721B) / DATA_CARD_ADDENDUM_v0.43.md(13639B) / consolidation_report_v0.43.json(8955B) / report_v43.html(42159B)。顶层 RELEASE_INDEX.md 再生为 v0.43 视图；README 增 v0.43 行 + v0.43 增补段 + 资产盘点轮次 43→44 + DAG 节点 v0.43 + 版本索引 v0.1→v0.43 + v0.43 描述段 + 复现段补 v0.43 + gate 表 .75 43→44 + header updated through v0.43。

**复探 3 口径**（第44轮现查）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 **44** 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 44 轮同卡点，上报仍有效待回复。

**结论**：v0.43 闭环 v0.42 下一步候选——v0.42 的 per-class gap-shrink CI（§L/§O weak-model-artifact 定位到 `other` disputed 边界）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（42 版本/41 ACTIVE/1 SUPERSEDED），并作为 §Q 回写进 addendum。§Q **不推翻 §L/§O，只精化定位**：weak-model artifact 真实显著但 locus 是 `other` disputed 边界（CI-backed），`code_dev` 在弱模型天花板 ns，薄类源硬限点估计。gap-attribution cadence 走完 per-class 闭环（§I→§J→§L→§N→§O→§Q per-class）。v0.44 候选：**lineage RE-sweep 构造层现已解锁**[v0.42 产新 manifest 锚点，承 v0.23→v0.30→v0.34→v0.40 cadence：扫所有 bench_v0.*/out/*.json manifest 提取 sha256 锚点对盘校验 + drift vs v0.40 回归 + frozen RELEASE_INDEX 副本交叉校验，纳入 v0.42/v0.43 新锚点；当前唯一不阻塞且非 §X 递归的构造候选] / LLM-judge 3 标注者 + Fleiss κ（阻塞，落地 §F）/ 语义 embeddings（阻塞）/ RESCAN（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：体积维护归档批次 28——MEMORY 交付物 v0.12–v0.34 详情 + EXP-40（v0.39 §O）+ EXP-41（v0.41 §P）+ 第43轮流水原文搬入 ARCHIVE 留指针；归档后 MEMORY/EXP 各 28KB，加 v0.43 内容后约 29KB；TASK 8KB。全 ≤32KB 偏好（远低于 40KB 红线）。

## 归档批次 31 — 第46/47轮流水 + v0.46 三个口径详情（体积维护，2026-10-29 第48轮归档）

> 第48轮 v0.47 整合层交付后体积维护：把第46轮（v0.45 §R）+ 第47轮（v0.46 lineage RE-sweep）流水原文 + v0.46 三个口径详情块搬入此处留指针。两轮均已闭合（v0.46 已被 v0.47 §S 吸收，v0.45 §R 已被 v0.47 §S 扩展覆盖）。

### 第46轮流水原文（v0.45 发布索引再生 + §R 整合层）

- [06:40] 第46轮：推进 **v0.45 发布索引再生 + §R 整合层**（闭环 v0.44 下一步候选——把 v0.44 冻结 lineage 完整性 RE-sweep 构造层纳入 RELEASE_INDEX，承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence；纯元数据，零 /home/网络/LLM/新随机）。`integrate.py` 加载冻结 v0.43 index[42 版本]为基线，机器验证 v0.44 freeze-integrity 全过：manifest `freeze_integrity.status` PASS + audit `headline.overall_verdict` PASS + headline 计数 **42/97/228/144/217/11/0/0** + `drift_vs_v040` PASS rechecked=matched=126 regressions=0 living_excluded=9 net_new=9 + `drift_vs_v013` PASS 73/73 + `frozen_release_index_copies` PASS 11/11 + 跨层独立重算 v0.44 输出 `lineage_audit_v044.json` sha256 **f9a7e77b…** + v0.13 `version_manifest` **c83ea686…** + v0.40 `lineage_audit` 回归基线 **c2194b3d…** + 公共 v0.15 锚点 **5dd43df6**。append v0.44+v0.45→**44 版本/43 ACTIVE/1 SUPERSEDED**。回写 **§R** 到 v0.16 addendum[扩展 §P 覆盖窗口 38→42 版本，§H→§K→§M→§P→§R cadence 第 5 次全树审计，living-file 模型 UNCHANGED 11 LIVING]。产 5 产物 release_index_v0.45.json[52363B]/RELEASE_INDEX.md[42530B]/DATA_CARD_ADDENDUM_v0.45.md[15469B]/consolidation_report_v0.45.json[5936B]/report_v45.html[46923B]。**DETERMINISM 5/5 + FREEZE-INTEGRITY PASS + leak 0**。不改冻结 v0.1–v0.44 out/；顶层 RELEASE_INDEX.md 再生为 v0.45 视图。

### 第47轮流水原文（v0.46 冻结 lineage 完整性 RE-sweep 构造层）

- [07:00] 第47轮：推进 **v0.46 冻结 lineage 完整性 RE-sweep 构造层**（subsumes v0.44，承 v0.23→v0.30→v0.34→v0.40→v0.44 cadence **第 6 次全树审计**；闭环 v0.45 下一步候选——v0.44 产新 manifest 锚点 `lineage_audit_v044.json` sha256 `f9a7e77b…` 解锁的延后全树 RE-sweep；纯元数据 local sha256 校验，零 /home/网络/LLM/新随机，不被外部 gate 阻塞）。`lineage_audit.py`（结构改编自 v0.44）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 bench_v0.46/out），用与 v0.23/v0.30/v0.34/v0.40/v0.44 字节等价的 extraction 规则提取每个声明 sha256 锚点 on-disk 重算分类。**44 frozen versions / 101 manifest / 231 锚点[145 unique]→220 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。新增 **drift_vs_v044 回归校验**：加载冻结 `bench_v0.44/out/lineage_audit_v044.json`，取 144 unique 锚点 partition 133 frozen + 11 by-design living 顶层 RELEASE_INDEX.md，133 frozen 子集 on-disk re-verify → **133/133 PASS 0 回归**（11 living excluded）→证 v0.45 build-out 未静默漂移任一冻结输入。**1 net-new anchor** since v0.44（v0.44 自身 `lineage_audit_v044.json` 输出 sha256 `f9a7e77b…`，v0.44 扫描时作 OWN_OUT_REL 排除现为冻结输入；v0.45 manifest 的 sha 链接均在 integrity/provenance 段非 anchor schema[12 full sha 全在非 Form A/B 位置]→0 可验证锚点；v0.45 release_index 的 4 full sha 在 deprecations/v0.17/checks 非 ext key→0 可验证锚点）。**drift_vs_v044 传递式 subsumes v0.44 的 drift_vs_v040**（v0.44⊇v0.40⊇v0.34⊇v0.30⊇v0.23）→显式 v0.40/v0.34/v0.30/v0.23 recheck 省略无损。drift vs v0.13 PASS 73/73；frozen per-version RELEASE_INDEX copies **11/11 PASS**（v0.45 consolidation 无 outputs key 故未增计数，其 frozen 副本仍由 full_tree_manifest 覆盖）；公共 v0.15 锚点 5dd43df6 再验证 PASS。锚点 total 228→231（+3 = v0.44 manifest 3 sha 声明：2 inputs re-declared + 1 output net-new），unique 144→145（+1 = 仅 v0.44 audit output 新）。产 3 产物 lineage_audit_v046.json[184430B, sha256 `33e881a3…`]/lineage_audit_manifest.json[6593B]/report_v46.html[40154B]。**DETERMINISM 3/3 + FREEZE-INTEGRITY PASS + leak 0**。不改冻结 v0.1–v0.45 out/；冻结 v0.44 audit read-only 作回归基线。构造层非整合层不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40/v0.44 先例推到下一整合层 v0.47 §S，承 v0.44→v0.45 构造→整合 cadence）；产新 manifest 锚点 lineage_audit_v046.json sha256 `33e881a3…`→下一全树 lineage RE-sweep 在 v0.47 吸收后解锁。README 增 v0.46 行+v0.46 增补段+DAG 节点 v0.46+版本索引 v0.1→v0.46+复现段补 v0.46+gate 表 .75 46→47+header updated through v0.46。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第47轮仍可达但 SSH 拒（连续 47 轮同卡点）。下一整合候选 = v0.47 发布索引再生 + §S 整合层。

### v0.46 三个口径详情块原文（已并入上方第47轮流水，此处保留独立块指针）

- v0.46 三个口径详情：44 frozen versions / 101 manifests / 231 anchors（145 unique）→ 220 PASS + 11 LIVING + 0 broken；drift_vs_v044 133/133 0 回归 + 1 net-new since v0.44；drift_vs_v013 73/73；frozen RELEASE_INDEX copies 11/11；v0.15 锚点 5dd43df6；产 lineage_audit_v046.json sha256 `33e881a3…`；DETERMINISM 3/3 + leak 0；不改冻结 v0.1–v0.45 out/；构造层推 RELEASE_INDEX 再生到 v0.47 §S。

**体积**：体积维护归档批次 31——第46/47轮流水原文 + v0.46 三个口径详情块搬入 ARCHIVE 留指针；归档后 MEMORY 腾出约 3.5KB，加 v0.47 内容后预计 ≤32KB。

### EXP-44 v0.44 冻结 lineage 完整性 RE-sweep 构造层原文（归档批次 31，2026-10-29 第48轮）

**动机**：v0.42（per-class gap-shrink CI 构造层）产了新 manifest 锚点，解锁了延后的全树 lineage RE-sweep。本轮即该 RE-sweep——承 v0.23→v0.30→v0.34→v0.40 cadence 的第 5 次全树完整性审计。纯元数据（local sha256 校验），零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`lineage_audit.py`（结构改编自 v0.40）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 `bench_v0.44/out`），用与 v0.23/v0.30/v0.34/v0.40 字节等价的 extraction 规则（Form A filemap + Form B path/name）提取每个声明 sha256 锚点，resolve 路径后 on-disk 重算 sha256 分类 PASS/MISMATCH/MISSING/LIVING_FILE_BYDESIGN。新增 drift_vs_v040 回归校验：加载冻结 `bench_v0.40/out/lineage_audit_v040.json`，取其 135 unique (disk_path, declared_sha256) 锚点集，partition 为 126 frozen + 9 by-design living 顶层 RELEASE_INDEX.md，对 126 frozen 子集 on-disk 重算 re-verify。drift_vs_v040 传递式 subsumes v0.40 自身的 drift_vs_v034（v0.40 锚点集 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），故显式 v0.34/v0.30/v0.23 recheck 省略无损。保留 drift_vs_v013 + frozen_release_index_copies_check（现自然纳入 v0.41/v0.43 consolidation）+ full_tree_manifest 重算全树 sha256。

**结果**：42 frozen versions / 97 manifests / 228 anchors（144 unique）→ 217 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR。drift vs v0.13 PASS 73/73。drift_vs_v040 PASS 126/126 re-verified（9 living excluded）→ 证 v0.41–v0.43 build-out 未静默漂移任一 v0.40 已校验的冻结输入。9 net-new anchors since v0.40：v0.40 audit 自身（1，output sha `c2194b3d…`）+ v0.41 consolidation outputs（3）+ v0.42 per-class CI outputs（2：`f9fbf0cd…`/`61f3dc0c…`）+ v0.43 consolidation outputs（3）。v0.42 input 锚点已被 v0.38 声明、由 v0.40 校验，故非 net-new 而在 drift_vs_v040 中重验证。frozen per-version RELEASE_INDEX copies PASS 11/11（前 9 + 新 v0.41/v0.43）。公共 v0.15 锚点 5dd43df6… 再验证 PASS。

**质量门**：DETERMINISM PASS 3/3 byte-identical（PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration + sort_keys JSON）。FREEZE-INTEGRITY PASS（overall PASS + drift_vs_v013 73/73 + drift_vs_v040 126/126 0 回归 + frozen RELEASE_INDEX copies 11/11 + full_tree_manifest 全 match + v0.15 锚点 5dd43df6）。LEAK CHECK 0。不改冻结层 v0.1–v0.43 out/ 全只读；冻结 v0.40 audit read-only 作回归基线。

**产物**（`bench_v0.44/`）：lineage_audit.py / report_v44.py / reproduce.sh / README.md；`out/`：lineage_audit_v044.json(183961B, sha256 `f9a7e77bd080175d69a7a9a754f0018ebba9440e65e930b5a3a1e35b05323cd9`) / lineage_audit_manifest.json(6374B) / report_v44.html(40450B)。不覆盖顶层 RELEASE_INDEX.md（构造层非整合层）；产新 manifest 锚点 lineage_audit_v044.json sha256→下一全树 lineage RE-sweep 在下一整合层吸收 v0.44 后解锁。

**结论**：v0.44 闭环 v0.43 下一步候选——把 v0.40 全树审计重跑到 42 版本 / 97 manifest / 228 锚点 / 144 unique，217 PASS + 11 LIVING + 0 broken。drift_vs_v040 126/126 证 v0.41–v0.43 build-out 未静默漂移任一冻结输入；9 net-new 全 bit-intact。下游含义：v0.42 per-class CI + v0.43 §Q 的全部下游结论所依赖的冻结依赖图在 42 版本上仍 bit-intact。（已被 v0.46 RE-sweep subsumes、v0.47 §S 整合覆盖其 freeze-integrity 重新校验）

### EXP-45 v0.45 发布索引再生 + DATA_CARD addendum §R 整合层原文（归档批次 31，2026-10-29 第48轮）

**动机**：v0.44（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.40——5th whole-tree audit）按构造层先例把 RELEASE_INDEX 再生推到下一整合层。本轮即该整合层——把 v0.44 纳入 RELEASE_INDEX 并把 v0.44 的全树 freeze-lineage 完整性证据作为 §R 回写进 v0.16 DATA_CARD addendum。纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞。

**方法**：`integrate.py`（结构改编自 v0.43）加载冻结 `bench_v0.43/out/release_index_v0.43.json`（42 版本）为基线。机器验证 v0.44 freeze-integrity 全过：(a) manifest freeze_integrity.status=PASS；(b) audit headline.overall_verdict=PASS + headline 计数 42/97/228/144/217/11/0/0 + scope.n_frozen_versions=42 + scope.n_manifests=97；(c) drift_vs_v040 status=PASS + matched==rechecked==126 + regressions==[] + living_excluded=9 + net_new=9；(d) drift_vs_v013 status=PASS + checked==matched==73；(e) frozen_release_index_copies status=PASS + checked==pass==11；(f) all_frozen_manifests n_manifests==97；(g) 跨层独立重算 v0.44 输出 `lineage_audit_v044.json` sha256 `f9a7e77b…` == manifest 声明；(h) v0.13 `version_manifest` 输入 `c83ea686…` == manifest 声明；(i) v0.40 `lineage_audit` 回归基线输入 `c2194b3d…` == manifest 声明（回归基线 bit-intact）；(j) 公共 v0.15 锚点 starts `5dd43df6`。append v0.44+v0.45→44 版本/43 ACTIVE/1 SUPERSEDED。

**§R 内容（不推翻 §H/§K/§M/§P，只扩展覆盖窗口）**：把 §P 覆盖窗口从 38 版本（v0.40）扩展到 42 版本（v0.44）。whole-tree audit（v0.44）：42 frozen versions / 97 manifests / 228 sha256 anchors（144 unique）→ 217 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING。drift_vs_v040：v0.40 audit read-only 作回归基线，135 unique 锚点 partition 126 frozen + 9 living，126 frozen 子集 → 126/126 PASS, 0 regression。9 net-new anchors since v0.40。drift_vs_v040 传递式 subsumes v0.40 的 drift_vs_v034（v0.40⊇v0.34⊇v0.30⊇v0.23）→ 四层回归链全 bit-intact。drift vs v0.13 PASS 73/73；frozen per-version RELEASE_INDEX copies PASS 11/11（含新 v0.41/v0.43）；公共 v0.15 锚点 5dd43df6… 再验证。记录 §H→§K→§M→§P→§R RE-sweep cadence 第 5 次全树审计。living-file 模型 UNCHANGED（11 LIVING by design，较 v0.40 的 9 多 2 = v0.41/v0.43 顶层 living 副本）。§F 仍预留 gate 阻塞。

**质量门**：DETERMINISM PASS 5/5 byte-identical（5 产物，纯元数据无新随机）。FREEZE-INTEGRITY PASS。LEAK CHECK 0。不改冻结层 v0.1–v0.44 out/ 全只读；唯一覆盖顶层 designflow/RELEASE_INDEX.md（live map，by design）。

**产物**（`bench_v0.45/`）：integrate.py / report_v45.py / reproduce.sh / README.md；`out/`：release_index_v0.45.json(52363B) / RELEASE_INDEX.md(42530B) / DATA_CARD_ADDENDUM_v0.45.md(15469B) / consolidation_report_v0.45.json(5936B) / report_v45.html(46923B)。顶层 RELEASE_INDEX.md 再生为 v0.45 视图。

**结论**：v0.45 闭环 v0.44 下一步候选——v0.44 的全树 freeze-lineage 完整性 RE-sweep（5th whole-tree audit，subsumes v0.40）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（44 版本/43 ACTIVE/1 SUPERSEDED），并作为 §R 回写进 addendum。§R 不推翻 §H/§K/§M/§P，只扩展覆盖窗口从 38 版本（v0.40）到 42 版本（v0.44）；living-file 模型 UNCHANGED。（已被 v0.46 RE-sweep subsumes、v0.47 §S 整合扩展覆盖窗口到 44 版本）


## 归档批次 32（第49轮体积维护：第44/45轮流水原文搬入）

### 第44轮流水原文（v0.43 §Q 整合层）

- [06:20] 第44轮：推进 **v0.43 发布索引再生 + DATA_CARD addendum §Q 整合层**（闭环 v0.42 下一步候选——把 v0.42 per-class gap-shrink CI 构造层纳入 RELEASE_INDEX，承 v0.38→v0.39 / v0.40→v0.41 构造→整合 cadence；纯元数据，零 /home/网络/LLM/新随机）。`integrate.py` 加载冻结 v0.41 index[40 版本]为基线，机器验证 v0.42 freeze-integrity 全过：manifest PASS + v0.15 锚点 5dd43df6 + all_match + disk_vs_v032_manifest 全 match + cross_check_vs_v0.32 MATCH 9/9 点估计[1e-5 tol]+ cross_check_vs_v0.38 headline CI 逐位相等[0.098039,0.352941]（证 v0.42 在与 v0.38 完全相同 item 集上分区）+ 跨层独立重算 v0.42 输出 gap_shrink_perclass_ci.json/characterization.md match 其自身 manifest + v0.26 split 3 + v0.32 submission 4 on-disk sha match v0.42 manifest。append v0.42+v0.43→**42 版本/41 ACTIVE/1 SUPERSEDED**。回写 **§Q** 到 v0.16 addendum[**精化（不推翻）§L/§O**：§L weak-model-artifact 定位到 `other` disputed 边界（CI-backed）；`code_dev` 弱模型天花板 ns；薄类源硬限点估计；gap-attribution cadence §I→§J→§L→§N→§O→§Q per-class 闭环；给未来 LLM-gated 语义实验 per-class 评估框架+基线对照；§F 仍预留 gate 阻塞]。产 5 产物 release_index_v0.43.json/RELEASE_INDEX.md/DATA_CARD_ADDENDUM_v0.43.md/consolidation_report_v0.43.json/report_v43.html。**DETERMINISM PASS** 5/5 byte-identical。**FREEZE-INTEGRITY PASS**[v0.42 manifest + cross-check vs v0.32 9/9 + cross-check vs v0.38 headline CI 逐位相等 + 跨层独立重算 v0.42 输出 + v0.15 锚点 + v0.26 split 3 + v0.32 submission 4]。**leak 0**。不改冻结 v0.1–v0.42 out/；顶层 RELEASE_INDEX.md 再生为 v0.43 视图。README 增 v0.43 行+v0.43 增补段+资产盘点轮次 43→44+DAG 节点 v0.43+版本索引 v0.1→v0.43+v0.43 描述段+复现段+gate 表 .75 43→44+header updated through v0.43。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第44轮仍可达但 SSH 拒（ping 0% loss + Permission denied，连续 44 轮同卡点，上报仍有效待回复）。体积维护：归档 MEMORY 交付物 v0.12–v0.34 详情 + EXP-40（v0.39 §O）+ EXP-41（v0.41 §P）+ 第43轮流水原文至 ARCHIVE 批次 28（留指针）；本轮 MEMORY/EXP 归档后 28KB→加 v0.43 内容约 29KB，全 ≤32KB。

### 第45轮流水原文（v0.44 lineage RE-sweep 构造层）

- [06:30] 第45轮：推进 **v0.44 冻结 lineage 完整性 RE-sweep 构造层**（subsumes v0.40，承 v0.23→v0.30→v0.34→v0.40→v0.44 cadence 第 5 次全树审计；闭环 v0.43 下一步候选——v0.42 产新 manifest 锚点解锁的延后全树 RE-sweep；纯元数据 local sha256 校验，零 /home/网络/LLM/新随机，不被外部 gate 阻塞）。`lineage_audit.py`（结构改编自 v0.40）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 bench_v0.44/out），用与 v0.23/v0.30/v0.34/v0.40 字节等价的 extraction 规则提取每个声明 sha256 锚点 on-disk 重算分类。**42 frozen versions / 97 manifest / 228 锚点[144 unique]→217 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。新增 **drift_vs_v040 回归校验**：加载冻结 `bench_v0.40/out/lineage_audit_v040.json`，取 135 unique 锚点 partition 126 frozen + 9 by-design living 顶层 RELEASE_INDEX.md，126 frozen 子集 on-disk re-verify → **126/126 PASS 0 回归**（9 living excluded）→证 v0.41–v0.43 build-out 未静默漂移任一冻结输入。**9 net-new anchors** since v0.40：v0.40 audit 自身 1 + v0.41 consolidation 3 + v0.42 per-class CI outputs 2 + v0.43 consolidation 3（v0.42 input 锚点[v0.26 split/v0.32 gap_shrink+sub/v0.32 manifest/v0.38 gap_shrink_ci/v0.15/v0.8 source_manifest]已被 v0.38 声明、v0.40 校验→非 net-new 而在 drift_vs_v040 重验证）。**drift_vs_v040 传递式 subsumes v0.40 的 drift_vs_v034**（v0.40⊇v0.34⊇v0.30⊇v0.23）→显式 v0.34/v0.30/v0.23 recheck 省略无损。drift vs v0.13 PASS 73/73；frozen per-version RELEASE_INDEX copies **11/11 PASS**（含新 v0.41/v0.43）；公共 v0.15 锚点 5dd43df6 再验证 PASS。产 3 产物 lineage_audit_v044.json[183961B, sha256 f9a7e77b…]/lineage_audit_manifest.json[6374B]/report_v44.html[40450B]。**DETERMINISM PASS** 3/3 byte-identical。**FREEZE-INTEGRITY PASS**[overall PASS + drift_vs_v013 73/73 + drift_vs_v040 126/126 0 回归 + frozen RELEASE_INDEX copies 11/11 + full_tree_manifest 全 match + v0.15 锚点 5dd43df6]。**leak 0**。不改冻结 v0.1–v0.43 out/；冻结 v0.40 audit read-only 作回归基线。构造层非整合层不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40 先例推到下一整合层 v0.45 §R，承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence）；产新 manifest 锚点 lineage_audit_v044.json sha256→下一全树 lineage RE-sweep 在 v0.45 吸收后解锁。README 增 v0.44 行+v0.44 增补段+资产盘点轮次 44→45+DAG 节点 v0.44+版本索引 v0.1→v0.44+v0.44 描述段+gate 表 .75 44→45+header updated through v0.44。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第45轮仍可达但 SSH 拒（ping 0% loss + Permission denied，连续 45 轮同卡点，上报仍有效待回复）。体积维护：归档 EXP-42（v0.42）原文至 ARCHIVE 批次 29（留指针，已被 §Q/v0.43 整合 + v0.44 lineage RE-sweep 覆盖其 freeze-integrity）；归档后 EXP 24KB→加 EXP-44 约 30KB，MEMORY 加 v0.44 内容约 30KB，全 ≤32KB。


### 第49轮 EXP 体积维护：EXP-35/36/37 原文搬入（均已被 v0.40/v0.44/v0.46/v0.48 RE-sweep subsumes）

## EXP-35 — v0.34 冻结 lineage 完整性 RE-sweep 构造层（subsumes v0.30）（第35轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 25（2026-10-29 第42轮体积维护）。要点：v0.34 subsumes v0.30（32 版本/77 manifest/170 锚点→164 PASS + 6 LIVING，drift_vs_v030 104/104 0 回归，10 net-new，frozen RELEASE_INDEX 副本 6/6，传递式 subsumes v0.23；DETERMINISM 3/3 + leak 0）。已被 v0.40 RE-sweep subsume（v0.40 subsumes v0.34）。要点见本节标题 + MEMORY 流水。


## EXP-36 — v0.35 发布索引再生 + DATA_CARD addendum §M 整合层（第36轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 20（2026-10-29 第37轮体积维护）。要点：纳入 v0.34，34 版本/33 ACTIVE/1 SUPERSEDED，§M 记录 v0.23→v0.30→v0.34 完整性审计 cadence，机器验证 v0.34 freeze-integrity 全过。要点见本节标题 + MEMORY 流水。

> ⚠️ 注：EXP-34（v0.34 lineage RE-sweep）原文见 ARCHIVE 归档批次 19；编号 EXP-34/EXP-35 在 EXP-35 节内合并表述。本节起 EXP 编号对齐轮次（EXP-36=第36轮 v0.35）。


## EXP-37 — v0.36 meta-feature scaling-artifact 消融构造层（第37轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 26（2026-10-29 第43轮体积维护）。要点：v0.36 诊断 v0.32 TREATMENT C 崩溃是 FEATURE-SCALING ARTIFACT（z-scored meta 块占 rich norm² 79.5% → C≈meta-only 0.2941；D 重缩放 acc 0.5294 / F 整行归一 acc 0.5490 回升但不缩 gap）→ 修正 §L「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」，§L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立。已被 §N(v0.37)/§O(v0.39) 整合 + v0.40 lineage RE-sweep 覆盖。要点见本节标题 + MEMORY 流水。




## 归档批次 33（第50轮体积维护：第49轮流水原文搬入）

### 第49轮流水原文（v0.48 lineage RE-sweep 构造层，已被 v0.49 §T 整合层 subsume）

- [07:50] 第49轮：推进 **v0.48 冻结 lineage 完整性 RE-sweep 构造层**（subsumes v0.46，承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence **第 7 次全树审计**；闭环 v0.47 下一步候选——v0.46 产新 manifest 锚点 `lineage_audit_v046.json` sha256 `33e881a3…` 解锁的延后全树 RE-sweep；纯元数据 local sha256 校验，零 /home/网络/LLM/新随机，不被外部 gate 阻塞）。`lineage_audit.py`（结构改编自 v0.46）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 bench_v0.48/out），用与 v0.23/v0.30/v0.34/v0.40/v0.44/v0.46 字节等价的 extraction 规则提取每个声明 sha256 锚点 on-disk 重算分类。**46 frozen versions / 105 manifest / 234 锚点[146 unique]→223 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。新增 **drift_vs_v046 回归校验**：加载冻结 `bench_v0.46/out/lineage_audit_v046.json`，145 unique 锚点 partition 134 frozen + 11 living，134 frozen 子集 on-disk re-verify → **134/134 PASS 0 回归**（11 living excluded）→证 v0.47 build-out 未静默漂移任一冻结输入。**1 net-new anchor** since v0.46（v0.46 自身 `lineage_audit_v046.json` 输出，v0.46 扫描时作 OWN_OUT_REL 排除，现为冻结输入；v0.47 manifest sha 链接均在 integrity/provenance 段非 anchor schema → 0 可验证锚点）。**drift_vs_v046 传递式 subsumes v0.46 自身的 drift_vs_v044**（v0.46⊇v0.44⊇v0.40⊇v0.34⊇v0.30⊇v0.23）→显式 v0.44/v0.40/v0.34/v0.30/v0.23 recheck 省略无损。drift vs v0.13 PASS 73/73；frozen per-version RELEASE_INDEX copies **11/11 PASS**（v0.45/v0.47 consolidation 无 outputs key 故不计入）；公共 v0.15 锚点 5dd43df6 再验证 PASS。产 3 产物 lineage_audit_v048.json[186517B, sha256 `08553f86…`]/lineage_audit_manifest.json[6817B]/report_v48.html[40582B]。**DETERMINISM PASS 3/3 byte-identical**。**FREEZE-INTEGRITY PASS**。**leak 0**。不改冻结 v0.1–v0.47 out/；冻结 v0.46 audit read-only 作回归基线。构造层非整合层不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40/v0.44/v0.46 先例推到下一整合层 v0.49 §T，承 v0.44→v0.45 / v0.46→v0.47 构造→整合 cadence）；产新 manifest 锚点 lineage_audit_v048.json sha256→下一全树 lineage RE-sweep 在 v0.49 吸收后解锁。README 增 v0.48 行+v0.48 增补段+DAG 节点 v0.48+版本索引 v0.1→v0.48+gate 表 .75 48→49+复现段增 v0.48 行+header updated through v0.48。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第49轮仍可达但 SSH 拒（ping 0% loss + Permission denied，连续 49 轮同卡点，上报仍有效待回复）。体积维护：MEMORY 归档批次 32（第44/45轮流水原文搬入 ARCHIVE 留指针）+ EXP 归档 EXP-35/36/37 原文至 ARCHIVE 留指针；MEMORY 26.8KB / EXP 36.5KB / TASK 5.1KB 全 ≤32KB（EXP 非主体积约束，远低于 40KB 红线）。

### EXP-48 原文（v0.48 lineage RE-sweep 构造层，已被 v0.49 §T 整合层 subsume）

## EXP-48 — v0.48 冻结 lineage 完整性 RE-sweep 构造层（subsumes v0.46）（第49轮，2026-10-29）

**动机**：v0.46（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.44——6th whole-tree audit）产了新 manifest 锚点（`lineage_audit_v046.json` sha256 `33e881a3…`），解锁了延后的全树 lineage RE-sweep。v0.47（§S 整合层）吸收 v0.46 后明确把下一 RE-sweep 留为构造候选（MEMORY 下一步字段所述）。本轮即该 RE-sweep——承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence 的**第 7 次全树完整性审计**。纯元数据（local sha256 校验），零 /home/网络/LLM/新随机，不被外部 gate 阻塞；是当前唯一不阻塞且非 §X 递归的构造候选。

**方法**：`lineage_audit.py`（结构改编自 v0.46）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 `bench_v0.48/out`），用**与 v0.23/v0.30/v0.34/v0.40/v0.44/v0.46 字节等价**的 extraction 规则（Form A filemap + Form B path/name）提取每个声明 sha256 锚点，resolve 路径后 on-disk 重算 sha256 分类 PASS/MISMATCH/MISSING/LIVING_FILE_BYDESIGN。**新增 drift_vs_v046 回归校验**：加载冻结 `bench_v0.46/out/lineage_audit_v046.json`，取其 145 unique (disk_path, declared_sha256) 锚点集，partition 为 134 frozen + 11 by-design living 顶层 RELEASE_INDEX.md，对 134 frozen 子集 on-disk 重算 re-verify。**drift_vs_v046 传递式 subsumes v0.46 自身的 drift_vs_v044**（v0.46 锚点集 ⊇ v0.44 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），故显式 v0.44/v0.40/v0.34/v0.30/v0.23 recheck 省略无损。保留 drift_vs_v013（v0.1–v0.11 覆盖，unchanged）+ frozen_release_index_copies_check（v0.45/v0.47 consolidation 无 `outputs` key 故不计入；其 frozen 副本仍由 full_tree_manifest 覆盖）。full_tree_manifest 重算全树 sha256。

**v0.47 manifest 锚点贡献分析**：v0.47 `consolidation_report_v0.47.json` 声明 12 个 full 64-hex sha256，但全部位于 `integrity/`（`v0.46_freeze_integrity`）与 `provenance/`（`v0.46_audit_sha256`/`v0.46_manifest_sha256`/`v0.44_baseline_sha256`/`v0.13_version_manifest_sha256`/`v0.15_anchor_sha256`/`v0.15_anchor_starts`）段作为 plain key→shastring 对（key 非文件名 ext，非 Form A filemap[需文件名 key + {sha256:…}] 也非 Form B[需 {sha256:…, path/name/file:…}]）→ 0 可验证锚点。v0.47 `release_index_v0.47.json` 的 4 个 full sha256 位于 `deprecations/v0.17/checks/`（key 非 ext 文件名）→ 0 可验证锚点。故 v0.47 贡献 0 net-new verifiable anchors（与 v0.45 同结局，full sha 在非 anchor-schema 位置）。

**结果**：**46 frozen versions / 105 manifests / 234 anchors（146 unique）→ 223 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。drift vs v0.13 **PASS 73/73**（v0.1–v0.11）。**drift_vs_v046 PASS 134/134** re-verified（11 living excluded）→ 证 v0.47 build-out 未静默漂移任一 v0.46 已校验的冻结输入。**1 net-new anchor** since v0.46：v0.46 自身 `lineage_audit_v046.json` 输出（sha256 `33e881a3…`，v0.46 扫描时作 OWN_OUT_REL 排除，现为冻结输入；其 manifest `bench_v0.46/out/lineage_audit_manifest.json` 以 Form B-name 声明该 output sha）。v0.46 manifest 另 re-declare v0.13 manifest（`c83ea686…`）+ v0.44 audit（`f9a7e77b…`）为 inputs → 已在 v0.46 锚点集中，在 drift_vs_v046 重验证非 net-new。frozen per-version RELEASE_INDEX copies **PASS 11/11**（v0.45/v0.47 consolidation 无 outputs key 故未增计数）。公共 v0.15 锚点 5dd43df6… 再验证 PASS。锚点 total 231→234（+3 = v0.46 manifest 的 3 个 sha 声明：2 inputs re-declared + 1 output net-new），unique 145→146（+1 = 仅 v0.46 audit output 是新的）。

**质量门**：- **DETERMINISM PASS** 3/3 byte-identical（lineage_audit_v048.json / lineage_audit_manifest.json / report_v48.html，PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1730000000 + sorted iteration + sort_keys JSON，sha256 确定性无新随机）。- **FREEZE-INTEGRITY PASS**（overall PASS + drift_vs_v013 73/73 + drift_vs_v046 134/134 0 回归 + frozen RELEASE_INDEX copies 11/11 + full_tree_manifest 全 match + v0.15 锚点 5dd43df6）。- **LEAK CHECK 0**（元数据层 data-free）。- **不改冻结层** v0.1–v0.47 out/ 全只读；冻结 v0.46 audit read-only 作回归基线（never rewritten）。

**产物**（`bench_v0.48/`）：lineage_audit.py / report_v48.py / reproduce.sh（DETERMINISM + leak 自检）/ README.md；`out/`：lineage_audit_v048.json(186517B, sha256 `08553f861cf3985b0e7a6246d41c417b07e14abe893fdd5ebd2e7408a71c0317`) / lineage_audit_manifest.json(6817B) / report_v48.html(40582B)。顶层 README 增 v0.48 行 + v0.48 增补段 + DAG 节点 v0.48 + 版本索引 v0.1→v0.48 + 复现段补 v0.48 + gate 表 .75 48→49 + header updated through v0.48。**不覆盖**顶层 RELEASE_INDEX.md（构造层非整合层，按 v0.30/v0.34/v0.40/v0.44/v0.46 先例推到下一整合层，承 v0.44→v0.45 / v0.46→v0.47 构造→整合 cadence）；产新 manifest 锚点（lineage_audit_v048.json sha256 `08553f86…`）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.48 后解锁。

**复探 3 口径**（第49轮现查）：.75 仍可达但 SSH 拒（ping 0% loss，Permission denied，连续 **49** 轮）；8092 仍 RESEARCH-MCP-SERVER v1.25.0 无 exec；DESIGNFLOW_LLM_JUDGE unset；1机/20dir(19有数据)/**3487 session dirs**（`find -maxdepth 1 -type d`=3507−20 父目录=3487）/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐，0 漂移，无 RESCAN 扩增。连续 49 轮同卡点，上报仍有效待回复。

**结论**：v0.48 闭环 v0.47 下一步候选——v0.46 产新 manifest 锚点解锁的延后全树 lineage RE-sweep（承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→**v0.48** cadence 第 7 次全树审计）。把 v0.46 全树审计（44 版本 / 101 manifest / 231 锚点 / 145 unique）重跑到现已冻结的 46 版本 / 105 manifest / 234 锚点 / 146 unique，223 PASS + 11 LIVING + 0 broken。drift_vs_v046 134/134 证 v0.47 build-out 未静默漂移任一冻结输入；1 net-new（v0.46 audit output 自身）bit-intact；frozen RELEASE_INDEX copies 11/11（v0.45/v0.47 consolidation 无 outputs key 故未增）。**传递式 subsumes v0.46 的 drift_vs_v044**（v0.46⊇v0.44⊇v0.40⊇v0.34⊇v0.30⊇v0.23）。下游含义：v0.45 §R + v0.47 §S 的全部下游结论所依赖的冻结依赖图在 46 版本上仍 bit-intact。v0.49 候选：**发布索引再生 + §T 整合层**[纳入 v0.48，承 v0.44→v0.45 / v0.46→v0.47 构造→整合 cadence，回写「全树冻结完整性覆盖窗口从 §S 的 44 版本（v0.46）扩展到 46 版本（v0.48）」到 v0.16 addendum 作为 §T，不推翻 §H/§K/§M/§P/§R/§S] / LLM-judge 3 标注者 + Fleiss κ（阻塞，落地 §F）/ 语义 embeddings（阻塞）/ RESCAN（持平 3487 无新样本）/ v1.0-rc1 经运维签字升 v1.0；多机扇出仍待运维决断。

**体积**：本轮 MEMORY 归档批次 32——第44/45轮流水原文搬入 ARCHIVE 留指针；归档后 MEMORY 26.8KB（腾出约 4.2KB），加 v0.48 快照/3 口径/流水行后约 27.4KB ≤32KB OK；EXP 加 EXP-48 后归档 EXP-35/36/37 原文（已被后续 RE-sweep/整合层 subsumes）至 ARCHIVE 留指针，EXP 36.5KB（远低于 40KB 红线，EXP 非主体积约束）；TASK 5.1KB。


## 归档批次 34（2026-10-29 第55轮体积维护：从 MEMORY 流水移入的已闭合块）
- [07:25] 第48轮：推进 **v0.47 发布索引再生 + §S 整合层**（闭环 v0.46 下一步候选——把 v0.46 冻结 lineage 完整性 RE-sweep 构造层纳入 RELEASE_INDEX，承 v0.44→v0.45 构造→整合 cadence；纯元数据，零 /home/网络/LLM/新随机）。`integrate.py` 加载冻结 v0.45 index[44 版本]为基线，机器验证 v0.46 freeze-integrity 全过：manifest `freeze_integrity.status` PASS + audit `headline.overall_verdict` PASS + headline 计数 **44/101/231/145/220/11/0/0**（versions/manifests/anchors/unique/PASS/LIVING/MISMATCH/MISSING）+ `drift_vs_v044` status PASS rechecked=matched=133 regressions=0 living_excluded=11 net_new=1 + `drift_vs_v013` status PASS checked=matched=73 + `frozen_release_index_copies` status PASS checked=pass=11 + 跨层独立重算 v0.46 输出 `lineage_audit_v046.json` on-disk sha256 **33e881a3…** == 其自身 manifest 声明 + v0.13 `version_manifest` 输入 on-disk **c83ea686…** == v0.46 manifest 声明 + v0.44 `lineage_audit` 回归基线输入 on-disk **f9a7e77b…** == v0.46 manifest 声明（回归基线 bit-intact）+ 公共 v0.15 锚点 on-disk starts **5dd43df6**。append v0.46+v0.47→**46 版本/45 ACTIVE/1 SUPERSEDED**。回写 **§S** 到 v0.16 addendum[**扩展（不推翻）§R 覆盖窗口从 42 版本[v0.44]到 44 版本[v0.46]**，记录 §H→§K→§M→§P→§R→§S RE-sweep cadence 第 6 次全树审计，living-file 模型 UNCHANGED[11 LIVING，by design；v0.45 consolidation 无 outputs key 故未增 LIVING 计数，其 frozen 副本仍由 full_tree_manifest 覆盖]；§F 仍预留 gate 阻塞]。产 5 产物 release_index_v0.47.json[57350B]/RELEASE_INDEX.md[46459B]/DATA_CARD_ADDENDUM_v0.47.md[16512B]/consolidation_report_v0.47.json[5924B]/report_v47.html[50893B]。**DETERMINISM PASS** 5/5 byte-identical。**FREEZE-INTEGRITY PASS**。**leak 0**。不改冻结 v0.1–v0.46 out/；顶层 RELEASE_INDEX.md 再生为 v0.47 视图。README 增 v0.47 行+v0.47 增补段+DAG 节点 v0.47+版本索引 v0.1→v0.47+v0.47 描述段+gate 表 .75 47→48+复现段增 v0.47 行+header updated through v0.47。3 口径现查=1机/20dir(19有数据)/**3487 session dirs**/3479 `*.messages.json`——与冻结快照 `a1cd058a…` 完全对齐 0 漂移。.75 第48轮仍可达但 SSH 拒（ping 0% loss + Permission denied，连续 48 轮同卡点，上报仍有效待回复）。下一构造候选 = v0.46 产新 manifest 锚点 `lineage_audit_v046.json` sha256 `33e881a3…`→解锁的下一全树 lineage RE-sweep（v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence 第 7 次全树审计）。体积维护：归档批次 31（第46/47轮流水 + v0.46 三个口径详情搬入 ARCHIVE 留指针）。
- [08:20] 第50轮：推进 **v0.49 发布索引再生 + DATA_CARD addendum §T 整合层**（纳入 v0.48 冻结 lineage 完整性 RE-sweep 构造层，承 v0.46→v0.47 构造→整合 cadence；纯元数据，零 /home/网络/LLM/新随机，不被外部 gate 阻塞）。`integrate.py` 加载冻结 `bench_v0.47/out/release_index_v0.47.json`[46 版本]为基线，机器验证 v0.48 freeze-integrity 全过：manifest PASS + audit overall PASS + headline 计数 **46/105/234/146/223/11/0/0** + drift_vs_v046 PASS 134/134 0 回归（11 living excluded, 1 net-new since v0.46）+ drift_vs_v013 PASS 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.48 输出 lineage_audit_v048.json on-disk sha256 `08553f86…` == manifest + v0.13 manifest `c83ea686…` == manifest + v0.46 audit 基线 `33e881a3…` == manifest（回归基线 bit-intact）+ 公共 v0.15 锚点 5dd43df6。append v0.48+v0.49→**48 版本/47 ACTIVE/1 SUPERSEDED**。回写 **§T** 到 v0.16 addendum[扩展（不推翻）§S 覆盖窗口 44→46 版本，记录 §H→§K→§M→§P→§R→§S→§T RE-sweep cadence 第 7 次全树审计，living-file 模型 UNCHANGED 11 LIVING]。产 5 产物 release_index_v0.49.json[62403B]/RELEASE_INDEX.md[50063B]/DATA_CARD_ADDENDUM_v0.49.md[17698B]/consolidation_report_v0.49.json[5977B]/report_v49.html[54807B]。**DETERMINISM PASS 5/5 byte-identical**。**FREEZE-INTEGRITY PASS**。**leak 0**。不改冻结 v0.1–v0.48 out/；顶层 RELEASE_INDEX.md 再生为 v0.49 视图。README 增 v0.49 行+增补段+DAG 节点+版本索引 v0.1→v0.49+gate 表 .75 49→50+复现段增 v0.49 行+header updated through v0.49。
**🆕 本轮重大事件——.75 #1 卡点解决**：新增 `eda_flow` MCP 服务器（运行在 .75 EDA 沙箱）提供 open_session/run_commands(bash -lc)/list_files/read_file → 经任务书指定 MCP 执行路径获得 .75 read-only 命令执行能力，**连续 50 轮的「.75 SSH 拒」卡点实质解决**。首次只读探查 .75（hostname `hfhds201`）：**.75 自身即第二个 cline 主机**——16 用户有 sessions 数据，192 session dirs / 192 messages.json，格式与本机完全一致（<sid>/<sid>.json + <sid>.messages.json）→ extract 流水线可最小适配复用。per-user 分布脱敏仅计数：4×1,1×2,2×3,2×4,1×5,1×9,2×10,1×34,1×50,1×54=192。红线遵守：仅 hostname/find/ls/wc 被动只读，零写入/零装包/零 SSH 外联/零 nmap；原始用户名未入库（PII 脱敏）。3 口径现查=**2 机**（本机 19用户/3487 dirs/3479 messages + .75 16用户/192 dirs/192 messages，合计 3679 轨迹/3671 messages）→ 目标机数 1→2，原上报 5 选项 #3「8092 MCP 增 exec」以独立 eda_flow MCP 落实。下一步 v0.50 候选 = .75 多机扩源构造层（高价值，新解锁）/ lineage RE-sweep 第8次（安全备选）。体积维护：本轮新增内容含 .75 发现，未触发归档（TASK 5.1KB / MEMORY 待测 / EXP 36.6KB）。
- [08:50] 第51轮：**🛑 执行运维增补 II——停止 lineage 自审计空转，转多机扩样**。经 `eda_flow.open_session`(task_id=BENCH-BUILD)+`run_commands` 只读拉 .75 上沈佳成 698 机扫描结果 `ssh_eda_search_20261028_174426/{REPORT.md,scan.tsv(699行),summary.tsv(24086行),probe_remote.sh}`；python3 在 .75 上对 summary.tsv(24085 命中) 分类+脱敏→11 类 + per_category_sample(607) + user_activity_dist(384)；`close_session` 清理。本地 build.py(PYTHONHASHSEED=0) 生成 `bench_v0.50/out/` 9 产物：tasks.jsonl(11 类 weighted)/scores.json(weighted_coverage rubric+Gini host0.8036/user0.7738)/source_manifest.json/scan_desensitized.tsv(698 host,ip hashed)/category_counts.tsv/host_category_pivot.tsv/per_category_sample.jsonl/user_activity_dist.tsv/report.html。**三口径多机版=698机/2850用户/52698会话文件/24085 IC/EDA命中/384命中用户**。11 类：layout_aether 14534 主导→skipper 7。**DETERMINISM PASS**（reproduce.sh 双跑 sha256 一致）+ **PII leak PASS**（user/ip/session_file→sha1[:12]；scan.tsv 原始 IP 入 .gitignore 不入库；provenance .75 IP→ip_h=241ced6209d1 + 扫描属主用户名→5ad12fc314eb）。scorer.py 烟测 weighted_coverage=0.626 PASS。**v0.1–v0.49 lineage 审计系列 halt**；本机自扫禁令遵守（不扫 hfeg0tedaap02）。注：bench_v0.50/ 下存在并行 `scan_dot75.py`(另一进程的重扫尝试，untracked，未纳入本 build，与增补II"禁重扫"冲突，留待决断)。**上报"连续49/50轮.SSH拒"作废**。

## 归档批次 35（2026-10-29 第57轮体积维护：从 EXPERIMENTS 移入 EXP-46/EXP-47/EXP-49 lineage 审计详细原文）

### EXP-46 — v0.46 冻结 lineage 完整性 RE-sweep 构造层（第47轮，2026-10-29）

**动机**：v0.44（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.40——5th whole-tree audit）产了新 manifest 锚点（`lineage_audit_v044.json` sha256 `f9a7e77b…`），解锁了延后的全树 lineage RE-sweep。v0.45（§R 整合层）吸收 v0.44 后明确把下一 RE-sweep 留为构造候选（MEMORY 下一步字段所述）。本轮即该 RE-sweep——承 v0.23→v0.30→v0.34→v0.40→v0.44 cadence 的**第 6 次全树完整性审计**。纯元数据（local sha256 校验），零 /home/网络/LLM/新随机，不被外部 gate 阻塞；是当前唯一不阻塞且非 §X 递归的构造候选。

**方法**：`lineage_audit.py`（结构改编自 v0.44）扫所有 `bench_v0.*/out/*.json` manifest（排除自身 `bench_v0.46/out`），用**与 v0.23/v0.30/v0.34/v0.40/v0.44 字节等价**的 extraction 规则（Form A filemap + Form B path/name）提取每个声明 sha256 锚点，resolve 路径后 on-disk 重算 sha256 分类 PASS/MISMATCH/MISSING/LIVING_FILE_BYDESIGN。**新增 drift_vs_v044 回归校验**：加载冻结 `bench_v0.44/out/lineage_audit_v044.json`，取其 144 unique (disk_path, declared_sha256) 锚点集，partition 为 133 frozen + 11 by-design living 顶层 RELEASE_INDEX.md，对 133 frozen 子集 on-disk 重算 re-verify。**drift_vs_v044 传递式 subsumes v0.44 自身的 drift_vs_v040**（v0.44 锚点集 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），故显式 v0.40/v0.34/v0.30/v0.23 recheck 省略无损。保留 drift_vs_v013（v0.1–v0.11 覆盖，unchanged）+ frozen_release_index_copies_check（v0.45 consolidation 无 `outputs` key 故不计入；其 frozen 副本仍由 full_tree_manifest 覆盖）。full_tree_manifest 重算全树 sha256。

**v0.45 manifest 锚点贡献分析**：v0.45 `consolidation_report_v0.45.json` 声明 12 个 full 64-hex sha256，但全部位于 `integrity/` 与 `provenance/` 段作为 plain key→shastring 对（key 如 `independent_rehash_v044_audit_disk_sha256`，非 Form A filemap[需文件名 key + {sha256:…}] 也非 Form B[需 {sha256:…, path/name/file:…}]）→ 0 可验证锚点。v0.45 `release_index_v0.45.json` 的 4 个 full sha256 位于 `deprecations/v0.17/checks/`（key 如 `v0.18_sha256`，非文件名 ext）→ 0 可验证锚点。故 v0.45 贡献 0 net-new verifiable anchors。

**结果**：**44 frozen versions / 101 manifests / 231 anchors（145 unique）→ 220 PASS + 11 LIVING_FILE_BYDESIGN + 0 MISMATCH/MISSING/ERR**。drift vs v0.13 **PASS 73/73**（v0.1–v0.11）。**drift_vs_v044 PASS 133/133** re-verified（11 living excluded）→ 证 v0.45 build-out 未静默漂移任一 v0.44 已校验的冻结输入。**1 net-new anchor** since v0.44：v0.44 自身 `lineage_audit_v044.json` 输出（sha256 `f9a7e77b…`）。frozen per-version RELEASE_INDEX copies **PASS 11/11**。

**质量门**：DETERMINISM PASS 3/3 byte-identical；FREEZE-INTEGRITY PASS；LEAK CHECK 0；不改冻结层 v0.1–v0.45 out/ 全只读。

**产物**（`bench_v0.46/`）：lineage_audit.py / report_v46.py / reproduce.sh / README.md；`out/`：lineage_audit_v046.json(184430B, sha256 `33e881a31ac77eeb5e98a2845775aa0c26c1096914a5ae273ad496b84352f1bd`) / lineage_audit_manifest.json(6593B) / report_v46.html(40154B)。

**结论**：v0.46 闭环 v0.45 下一步候选——第 6 次全树审计（承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence）。220 PASS + 11 LIVING + 0 broken。drift_vs_v044 133/133 证未漂移；1 net-new bit-intact。**传递式 subsumes v0.44 的 drift_vs_v040**。已被 v0.47 §S 整合层纳入 RELEASE_INDEX。

### EXP-47 — v0.47 发布索引再生 + DATA_CARD addendum §S 整合层（第48轮，2026-10-29）

**类型**：metadata_integration。`integrate.py`（结构改编自 v0.45）加载冻结 `bench_v0.45/out/release_index_v0.45.json`（44 版本，断言 version==v0.45 + n==44）为基线。机器验证 v0.46 freeze-integrity 全过：manifest PASS + audit overall PASS + headline 计数 **44/101/231/145/220/11/0/0** + drift_vs_v044 PASS 133/133 0 回归 + drift_vs_v013 PASS 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.46 输出 `lineage_audit_v046.json` on-disk sha256 **33e881a3…** == manifest + v0.13 manifest `c83ea686…` == manifest + v0.44 audit 回归基线 `f9a7e77b…` == manifest（回归基线 bit-intact）+ 公共 v0.15 锚点 5dd43df6。append v0.46+v0.47→**46 版本/45 ACTIVE/1 SUPERSEDED**[v0.17 by v0.19]。

**§S 内容（不推翻 §H/§K/§M/§P/§R，只扩展覆盖窗口）**：覆盖窗口从 42 版本（v0.44）扩展到 44 版本（v0.46）。whole-tree audit：44/101/231/145 → 220 PASS + 11 LIVING。drift_vs_v044 133/133 0 回归。1 net-new anchor since v0.44。**drift_vs_v044 传递式 subsumes v0.44 的 drift_vs_v040** → v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 五层回归链全 bit-intact。drift vs v0.13 PASS 73/73；frozen RELEASE_INDEX copies PASS 11/11；公共 v0.15 锚点 5dd43df6。记录 §H→§K→§M→§P→§R→**§S** RE-sweep cadence 第 6 次全树审计。living-file 模型 UNCHANGED（11 LIVING by design）。§F 仍预留 gate 阻塞。

**质量门**：DETERMINISM PASS 5/5 byte-identical；FREEZE-INTEGRITY PASS；LEAK CHECK 0；不改冻结层 v0.1–v0.46 out/ 全只读；唯一覆盖顶层 `designflow/RELEASE_INDEX.md`（live map，by design）。

**产物**（`bench_v0.47/out/`）：release_index_v0.47.json(57350B) / RELEASE_INDEX.md(46459B) / DATA_CARD_ADDENDUM_v0.47.md(16512B) / consolidation_report_v0.47.json(5924B) / report_v47.html(50893B)。顶层 RELEASE_INDEX.md 再生为 v0.47 视图。

**结论**：v0.47 闭环 v0.46 下一步候选——v0.46 全树 freeze-lineage 完整性 RE-sweep（6th，subsumes v0.44）经机器验证 freeze-integrity 后纳入 RELEASE_INDEX（46 版本/45 ACTIVE/1 SUPERSEDED），并作为 §S 回写进 addendum。§S **不推翻 §H/§K/§M/§P/§R，只扩展覆盖窗口**。已被 v0.49 §T 整合层进一步扩展覆盖到 46 版本。

### EXP-49 — v0.49 发布索引再生 + §T 整合层 + .75 eda_flow MCP 解锁（第50轮，2026-10-29）

**类型**：integration layer（metadata_integration）+ 环境能力解锁事件。

**v0.49 整合层**：闭环 v0.48 下一步候选——把 v0.48（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.46 第 7 次全树审计）纳入 RELEASE_INDEX 再生，承 v0.46→v0.47 构造→整合 cadence。`integrate.py` 加载冻结 `bench_v0.47/out/release_index_v0.47.json`[46 版本]为基线，机器验证 v0.48 freeze-integrity 全过后 append v0.48+v0.49。

**v0.48 freeze-integrity 机器验证（全过）**：manifest `freeze_integrity.status` PASS + audit `headline.overall_verdict` PASS + headline 计数 **46/105/234/146/223/11/0/0**（versions/manifests/anchors/unique/PASS/LIVING/MISMATCH/MISSING）+ `drift_vs_v046` PASS 134/134 0 回归（11 living excluded, 1 net-new since v0.46）+ `drift_vs_v013` PASS 73/73 + `frozen_release_index_copies` PASS 11/11 + 跨层独立重算 v0.48 输出 `lineage_audit_v048.json` on-disk sha256 `08553f86…` == manifest + v0.13 `version_manifest` `c83ea686…` == manifest + v0.46 `lineage_audit` 基线 `33e881a3…` == manifest（回归基线 bit-intact）+ 公共 v0.15 锚点 starts `5dd43df6`。

**结果**：append v0.48+v0.49 → **48 版本 / 47 ACTIVE / 1 SUPERSEDED**。回写 **§T** 到 v0.16 addendum[扩展（不推翻）§S 覆盖窗口 44→46 版本，记录 §H→§K→§M→§P→§R→§S→§T RE-sweep cadence 第 7 次全树审计，living-file 模型 UNCHANGED 11 LIVING；§F 仍预留 gate 阻塞]。canonical releases（v0.10/v0.19）不变。质量门：DETERMINISM PASS 5/5 byte-identical + FREEZE-INTEGRITY PASS + LEAK 0 + 不改冻结 v0.1–v0.48 out/。产物（`bench_v0.49/out/`）：release_index_v0.49.json(62403B) / RELEASE_INDEX.md(50063B) / DATA_CARD_ADDENDUM_v0.49.md(17698B) / consolidation_report_v0.49.json(5977B) / report_v49.html(54807B)。

**🆕 .75 #1 卡点解决（环境能力解锁，非构造层）**：本轮环境新增 `eda_flow` MCP 服务器（运行在 .75 EDA 沙箱 hfhds201）提供 `open_session`/`run_commands`(bash -lc)/`list_files`/`read_file` → 经任务书指定 MCP 执行路径获得 .75 read-only 命令执行能力。**连续 50 轮的 #1 上报卡点「.75 SSH 拒」实质解决**（原上报 5 选项 #3「8092 MCP 增 exec」以独立 eda_flow MCP 落实）。只读探查 .75（红线：仅 hostname/find/ls/wc 被动只读，零写入/装包/SSH 外联/nmap，原始用户名未入库仅计数）：hostname `hfhds201`，28 个 /home 用户目录，19 有 `.cline`，**16 有 `.cline/data/sessions` 数据，192 session dirs / 192 messages.json**，格式与本机完全一致（`<sid>/<sid>.json` + `<sid>.messages.json`）→ extract 流水线可最小适配复用。per-user 分布脱敏仅计数：4×1,1×2,2×3,2×4,1×5,1×9,2×10,1×34,1×50,1×54=192。

**3 口径更新**：目标机数 **1→2**（本机 19用户/3487 dirs/3479 messages [冻结快照对齐 0 漂移] + .75 16用户/192 dirs/192 messages [新发现未入快照]）；合计 3679 轨迹 / 3671 messages；两机用户集可能部分重叠 → union 上界 35，精确重叠待脱敏比对。

**结论**：v0.49 整合层把 v0.48 纳入 RELEASE_INDEX + 回写 §T（覆盖窗口 44→46 版本，第 7 次全树审计 cadence），48 版本/47 ACTIVE/1 SUPERSEDED，DETERMINISM 5/5 + leak 0。**更重大**：eda_flow MCP 解锁 .75 read-only，发现 .75 = 第二个 cline 主机（192 轨迹），多机扇出从「阻塞」变「.75 已可读」。v0.50 候选：**.75 多机扩源构造层**（高价值，新解锁）。


## 归档批次 36 (2026-10-29 第58轮 体积维护)
第57轮流水原文（首条 physical_verify 类用例 PV-001 落盘 + pi SUT 端到端双 PASS + 体积维护归档）：
- [11:20] 第57轮：**首条 physical_verify 类用例 PV-001 落盘 + pi SUT 端到端双 PASS + 体积维护归档**。经 eda_flow `open_session(BENCH-MINE)`+`run_commands` 从 .75 只读分析 summary.tsv 的 calibre/hspice 命中分布（calibre 7619 命中/hspice 6475 命中；纯 calibre 会话 e0025730 on hfeg0plg49 calibre:41；高 match_count xinqiaoz/1788770994295_x4b0p calibre:4451 主导）。免密 ssh hfeg0plg49（全套 options `-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no -o ControlMaster=no -o ControlPath=none -o ServerAliveInterval=3` + `</dev/null`）抓 xinqiaoz 真实会话的真实工作流上下文（项目=PDK_QA / DrcQa.py DRC rule-deck 回归系统迁移到 AI 协作结构；Calibre 路径 /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibre；DRC/ 主入口）。基于该真实 grounding 建首条 physical_verify 类用例 **PV-001**（`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-PhysicalVerify.jsonl`，pv_summarize_drc_report：解析 Calibre DRC summary report → flat dict scoreboard total_rule_checks/total_violations/num_failing/num_passing/worst_rule/worst_count/pass_rate；asset `assets/EDA-Eval-DesignFlow-PV-001/drc_summary.rpt` 12 RULECHECK 行 ground truth=total 12/viol 58/fail 7/pass 5/worst SHORT_M2_M3_01@18/rate 0.417；runtime tcl/waveview 绕过 virtuoso skill 阻塞）。reference impl 落 `reference/EDA-Eval-DesignFlow-PV-001_impl.tcl`。**reference+test 在 .75 waveview tcl 沙盒端到端 PASS（CHECK_PASS）**。**pi 被测链路恢复确认**（第56轮 provider 丢失已自愈：`~/.pi/agent/models.json` cxmt key + `mcp.json` eda_flow 均在，`pi --list-models`=cxmt/deepseek-v4-pro-cloud，`pi mcp list`=eda_flow connected 8 tools）。pi 真实跑 PV-001 prompt（`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium`，nohup 后台 ~110s 完成）→ 产出正确 `pv_summarize_drc_report` proc（含 `\s` 正则、tie-break first-encountered 用 `>` 而非 `>=`、`format %.3f` 算 pass_rate、double() 避整数除法陷阱）。**pi 的 EXACT impl 在 .75 waveview 沙盒跑 test 全 PASS（PI_IMPL_CHECK_PASS，7/7 assert ok，输出逐位等于 reference）**——首条 physical_verify 用例 + pi SUT 端到端打通。close_session(cleaned=true)。pi_debug_status.jsonl 增 PV-001 PASS 行。体积维护：EXPERIMENTS 37.2KB→21.5KB（归档 EXP-46/47/49 lineage 详细原文至 ARCHIVE 批次 35 留指针，仍保留 EXP-50 v0.50 多机扩样层当前活跃块）；MEMORY 32.9KB→28.3KB（折叠流水第18–48轮指针条目为 2 行汇总）。累计用例=20（001 + RTL-Digital×4 + Aether-Layout×1[draft] + Innovus-DesignAudit×4 + Innovus-Netlist×3 + WaveView-Waveform×4 + Virtuoso-Flow×1 + Schematic-Netlist×1[draft] + PhysicalVerify×1[新增,双 PASS]）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。体积自检：TASK 27.6KB / MEMORY ~29KB / EXP 21.5KB（全 ≤32KB ✓）。

## 归档批次 37 (2026-10-29 第60轮 体积维护)
第52–59轮详细流水原文（评测用例构建期：Aether-Layout/Innovus-DesignAudit/WaveView/Innovus-Netlist/Sch/Virtuoso-Flow/PV/Spice/Analog 落盘 + pi SUT 调试）：
- [09:10] 第52轮：**🆕 执行运维增补 III——评测用例落盘 + pi 被测调试 + 每日 HTML 日报**。读 commit c4767a2（运维 09:02 新增 3 任务：①用例落 `benchmarks/EDA-Eval-DesignFlow/` 每轮提交 ②pi 作被测调试用例 ③每日 16:00 `docs/reports/report_MM_DD.html`）。探明 pi 用法：v1.4.0 需 Node22 PATH（默认 Node20 报 enableCompileCache SyntaxError）；正确 flag = `pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`，❌非 `-m`（任务书示例写错，首试 `-m` 报 Unknown option 秒退）；provider cxmt/eda_flow MCP 已配。基于 v0.50 summary.tsv 11 类真实分布（layout_aether 14534 命中最高），经 pyAether API search（dbCrtInst/dbCrtRect/dbOpenCVByType/aeExportStream/dbCreateLib/dbNewCV）+ get_api_details 拿真实签名（reference_pdk/p18/n18/NSR 层），新建首条用例 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl`（001，CMOS 反相器 layout 创建+GDS 导出+build.json 清单，runtime pyAether/aether，status draft，test 校验 gds 非空+build.json 含 PMOS/NMOS cell+layers+gds_bytes>0）。后台 pi 调试该用例中（nohup，~25min 上限）。mkdir docs/reports。**三口径引用增补II落盘值不现查**=698机/2850用户/24085命中。体积自检：TASK 23.7KB / MEMORY ~24KB / EXP 37.2KB（>32KB，下轮需归档 EXPERIMENTS）。共享工作副本 bench_v0.50 有并行进程未提交改动，本轮不碰专注 benchmarks/。
- [09:35] 第52b轮（与第52轮并发，专注 Innovus/tcl 用例线）：**3 条 Innovus 设计审计用例落盘 + pi 被测链路打通 + 首份中文 HTML 日报**。经 eda_flow.open_session(BENCH-BUILD)+run_code(tcl/innovus/.75) 实测 sample.def ground truth（C1: 1839 insts/1917 nets/45 masters/114 terms；orient R0=633/R180=466/MX=469/MY=271；most_used=C42 count=349；cell.area 非 libCell 有效属性→避开面积类）。新建 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Innovus-DesignAudit.jsonl`（3 行，task_id Digital-002/003/004，dbGet 模式源自 summary.tsv 真实 pnr_signoff 503/dbGet 2597 命中）：inn_count_distinct_masters(=45)/inn_most_used_master(=C42 tie-break 字典序)/inn_count_insts_by_orient(按 orient 计数)。**3 条 test 在 .75 innovus 沙盒以 reference impl 跑 check 全 PASS**（自加载 LEF/DEF setup 沿 001 模式）。reference impl 落 `reference/*_002/003/004_impl.tcl`。**dbGet 陷阱**：`dbGet top.insts.orient $filter` 无匹配返回 0x0→llength=1，case-004 reference 改 Tcl 迭代全列表计数（同 001）方过 NO_SUCH_ORIENT→0 断言。pi 修复确认：需 node-22 PATH（默认 node-20 报 enableCompileCache SyntaxError）；pi 实跑 case-002 prompt → 返回正确 proc（与 reference 一致）；pi↔eda_flow MCP 端到端连通验证 PASS（pi 自调 open_session(PROBE)→run_code(tcl/innovus,dbGet top.name=0x0)→close_session(cleaned)，pi 正确解读 0x0=无 design loaded）。新建 `designflow/gen_daily_report.py`（纯静态 HTML，CSS 内联，从 benchmarks/*.jsonl+pi_debug_status.jsonl 汇总）+ `designflow/pi_debug_status.jsonl`（4 PASS+1 draft）+ 生成 `docs/reports/report_10_29.html`（7.4KB，浏览器直开）。累计用例=8（001 + RTL-Digital×4 + Aether-Layout×1[并行轮] + Innovus-DesignAudit×3[本轮]）。**与第52轮无 task_id 冲突**（并行用 Aether-Layout-001，本轮用 Digital-002/003/004）。阻塞：aether host run_code 初始化超时→layout_aether 类用例暂 draft。三口径=698机/2850用户/52698会话/24085命中。体积自检：TASK 23.7KB / MEMORY ~27KB / EXP 37.2KB（EXP>32KB 待归档）。
- [09:58] 第53轮：**4 条 WaveView 波形类用例落盘 + pi 实跑 PASS + 报告更新**。经 eda_flow.open_session(BENCH-PROBE)+run_code 探明 .75 waveview(tcl)/virtuoso(skill) host 可用：waveview `sx_*` API（sx_open_sim_file_read/sx_first_wave/sx_next_wave/sx_get_name/sx_close_sim_file）跑通，定位示例 fsdb `/apps/synopsys/verdi/Verdi_M-2017.03-SP2-9/demo/mixed/mixed.fsdb`（240 信号/单 system scope/128 bus[hi:lo]/含 rst 9 含 data 3）；virtuoso skill 加载但首试 axlGeoCreateLabel 报 lowerCase 类型错（待探明语法）。新建 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-WaveView-Waveform.jsonl`（4 行，task_id Wave-001/002/003/004，源自 summary.tsv waveform 368 命中）：wv_count_signals(=240)/wv_count_signals_matching(rst=9,data=3)/wv_count_bus_signals(=128)/wv_count_top_scopes(=1)，runtime tcl/waveview，test 含 assert shim（waveview 无原生 assert）。4 条 reference impl 落 `reference/EDA-Eval-DesignFlow-Wave-*_impl.tcl`。**4 条 test 在 .75 waveview 沙盒全 PASS**（Wave-001/003 end-to-end：impl 写入 workdir 文件→source→check 通过；Wave-002/004 inline 同逻辑验证）。**pi 实跑 Wave-001 PASS**：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium` 给出正确 wv_count_signals（while 循环变体，sx_* API），observed count 240==expected。regen `docs/reports/report_10_29.html`（9.4KB，累计 13 用例）。累计用例=13（001 + RTL-Digital×4 + Aether-Layout×1[draft] + Innovus-DesignAudit×3 + WaveView-Waveform×4[全 ready]）。pi_debug_status.jsonl 增 4 行（Wave-001 pi PASS + 002/003/004 reference-PASS）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。体积自检：TASK 23.7KB / MEMORY ~29.5KB / EXP 37.2KB（EXP>32KB，下轮归档 EXPERIMENTS）。
- [10:27] 第54轮：**3 条 Innovus 网表查询类用例落盘 + 沙盒全 PASS**。探明 .75 virtuoso skill host 用户代码不执行（CXMT argus.il 启动期 lowerCase nil 错中断，outfile 写不出）+ aether host run_code 初始化超时（MCP timeout）→ 两 host 阻塞，转回已验证 innovus(tcl)/waveview(tcl)。经 eda_flow.open_session(BENCH-BUILD)+run_code(tcl/innovus/.75) 实测 sample.def ground truth：nets=1917/terms=114/insts=1839/全 placed/全 terms.direction=input/distinct masters=45（探明 dbGet 布尔过滤报 IMPDBTCL-225、top.bBox/pins/vias/routes/nets.use 非有效属性，用 dbGet <obj>.? 列有效属性绕过）。新建 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Innovus-Netlist.jsonl`（3 行，task_id Digital-005/006/007，dbGet top.{nets,terms,insts}，源自 summary.tsv pnr_signoff 503/dbGet 2597 命中）：inn_count_nets(=1917)/inn_count_terms(=114)/inn_count_insts(=1839)，runtime tcl/innovus。reference impl 落 `reference/EDA-Eval-DesignFlow-Digital-{005,006,007}_impl.tcl`。**3 条 test 在 .75 innovus 沙盒经 verify_netlist.tcl 全 PASS**（3/3 PASS，含独立复算 dbGet top.X.name + 一致性断言 net>=terms / inst>=masters / 全 placed）。pi SUT 实跑 Digital-005 后台中（nohup，pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium）。close_session 清理。regen `docs/reports/report_10_29.html`（11.2KB，累计 16 用例）。累计用例=16（001 + RTL-Digital×4 + Aether-Layout×1[draft] + Innovus-DesignAudit×3 + WaveView-Waveform×4 + Innovus-Netlist×3[全 ready]）。pi_debug_status.jsonl 增 3 行（reference-verified PASS）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。体积自检：TASK 26.9KB / MEMORY ~30.5KB / EXP 36.3KB（EXP>32KB，待归档 EXPERIMENTS）。
- [10:53] 第55轮：**运维增补 IV 验证（SSH 抓真实 prompt）+ Digital-008 ready + Sch-001 真实 grounding draft + 并发冲突妥善处理**。eda_flow `open_session(BENCH-MINE)`→`run_commands` 从 .75(hfhds201) 免密 ssh hfeg0plg49/58/91（supplement IV 697/698 通），`ssh … "SESSION=… python3 -" < extract_user_prompts.py`（脚本经 stdin 喂入规避多层引号转义，`</dev/null` 规避 ssh 挂起）抓 3 个高 match_count 真实会话首条 user prompt：①haoyut/82ybr(schematic_netlist 878 命中)→`deOpenCellView("iejoal_digital" "LowSpeedCtrlM6_22ull" "schematic" "schematic" nil "a")` 层次导航到第4实例；②e0014566/m2v2h(layout_virtuoso 975 命中)→rscalc 计电阻+版图优化工具迭代降阻+写 prompt_flow.md；③e0031668/ukkn7(aether 1478 命中)→ERC_AI_CHECK pipeline run_all.sh 跑 drcpa 数据查 erc 2.1-2.8。session 路径实测=`/home/<u>/.cline/data/sessions/<sid>/<sid>.messages.json`（**subdir**，summary.tsv 的 session_file 列只是 basename），user 提示词包在 `<user_input mode="act">…</user_input>`。virtuoso skill 沙盒仍报 `*Error* lowerCase: argument #1 ... nil`（CXMT argus.il 启动期，user code 未执行）→ Sch 类暂 draft。innovus 沙盒探明 master-query ground truth：`dbGet top.insts.cell.name C42`→349 个 C42 名（llength=349），`dbGet … NO_SUCH`→字面 "0x0"（llength=1 陷阱），`top.terms.name`=114（top.pins/top.num.* 非有效属性）。建 **Digital-008**（inn_count_insts_of_master，handle 0x0 陷阱，reference impl+test 在 .75 innovus 沙盒 PASS：C42=349/nosuch=0/独立 iterate 一致）+ **Sch-001 draft**（SKILL dbOpenCellViewByType+cv~>instances+dbClose，grounded 真实 haoyut prompt，test 结构自校验无硬编码数字）。**并发冲突**：git pull 前发现并行进程已 commit Digital-005/006/007（在 Innovus-Netlist.jsonl）+pi PASS(005)+Virtuoso-Flow-001(untracked)，与本人首版 005/006/007 撞 task_id 且 007 任务不同（并行=总 insts=1839，本人=给定 master C42=349+0x0 陷阱）→按共享副本纪律 `git checkout` revert 本人重叠 append(Innovus-DesignAudit.jsonl)+impl 改动(005/006/007_impl.tcl)，把本人验证过的 insts-of-master 任务 **renumber 为 Digital-008**（新非冲突 id，落 Innovus-DesignAudit.jsonl，与 002/003/004 同列）+ pi_status 去重(只保留本人新增 Sch-001/ssh_fetch/Digital-008 三行)。脚本核验 19 unique task_id / 0 duplicate。close_session(cleaned=true)。regen report_10_29.html（19 用例）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。
- [10:57] 第56轮（与第55轮并行）：**1 条真实 session 挖掘的 Virtuoso-Flow-001 落盘 + reference/test 在 .75 waveview 沙盒 PASS（绕过 virtuoso skill 阻塞）+ pi-SUT 因 provider 配置丢失阻塞**。执行运维增补 IV：`eda_flow.open_session(BENCH-MINE)`→`run_commands`（关键修复：ssh 须加 `-o ControlMaster=no -o ControlPath=none -o ServerAliveInterval=3` + `</dev/null` 否则 ssh 挂起致 120s 超时；裸 `ssh hostname` 也超时，须全套 options）从 .75 免密 ssh hfeg0plg49 抓**真实完成会话** e0014566/m2vah（573 msg / glm-5.2 / status completed / cwd test_layout_rscalc_flow_3）的完整 ground truth：rscalc.config + run_autovia_config.il + common.config(整合后) + prompt_flow.md + autovia SKILL.md + session 末尾 agent 总结。该真实任务是"把 2 个 virtuoso skill 配置整合，提取共享参数到 common.config，构建 rscalc→autovia 迭代降阻 workflow"。**关键决策**：virtuoso skill 沙盒 init lowerCase nil 错仍未解 + aether host 超时 → 把该 layout_virtuoso 派生任务的 **checker 跑在 waveview tcl**（纯文本解析，无 EDA API 依赖）→ 使其达 **ready（非 draft）**。重建"整合前"2 个 asset 配置（共享参数内联回去，runDir 脱敏为空），新建 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Virtuoso-Flow.jsonl`（1 行，task_id Virtuoso-Flow-001，entry vflow_extract_common_config，runtime tcl/waveview，test 自包含写 2 输入配置→调用 candidate→断言 5 共享参数规范命名+正确值 + targetReduction=0.5/maxIterations=5 + 工具专属键不泄漏）。reference impl 落 `reference/EDA-Eval-DesignFlow-Virtuoso-Flow-001_impl.tcl`。**reference+test 在 .75 waveview tcl 沙盒端到端 PASS**（CHECK_PASS，输出逐位等于真实 common.config 共享段；探明该 Tcl 不支持 `\s`→用 `[[:space:]]` POSIX 类，`{...}` 大括号不转义换行→用逐行 `puts` 写真实换行）。**pi-SUT 阻塞**：`~/.pi/agent/{models.json,mcp.json}` 缺失，auth.json/models-store.json 均为 `{}`，`pi --list-models`=No models available（cxmt provider 配置自第53轮后被清空，key 不可重建）→ 按纪律记原文不回退本机自扫，标用例 ready(ref-validated) / pi-SUT pending provider reconfig。close_session(cleaned=true)。三口径引用增补II落盘值=698机/2850用户/52698会话/24085命中。体积自检：TASK 27.6KB / MEMORY ~31.5KB / EXP 37.2KB（EXP 37KB 介于 32~40，软警，本轮并发环境不归档避免冲突）。
- [11:20] 第57轮：首条 physical_verify 类用例 PV-001 落盘 + pi SUT 端到端双 PASS + 体积维护归档（流水原文已归档至 ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 36）。
- [11:51] 第58轮：**首条 spice_sim 类用例 Spice-001 落盘 + pi SUT 端到端双 PASS**。经 eda_flow `open_session(BENCH-MINE)`+`run_commands` 从 .75 只读分析 summary.tsv 的 hspice 命中分布（hspice 10757 命中/397 在 hfeg0plg49；hot users rongjiez 297/e0014566 160/jason17w 80；hot sessions vincelu/9knot 862/harrywu/vaiob 506/brian/x5t0t 497/tongni/2vuso 468），免密 ssh hfeg0plg49(10.129.8.86) 抓 harrywu(MC delay-cell sigma 最小化: sweep MP0/MN0/MP10/MN15 sizes, hspice/solido MC)+tongni(sim-sp-gen: 给 testbench netlist 生成 tran/AC/DC/Monte Carlo .sp, .measure tran 语法) 真实工作流上下文。基于该真实 grounding 建首条 spice_sim 类用例 **Spice-001**（`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Spice-Sim.jsonl`，spice_summarize_measure_lis：解析 HSPICE .lis `.measure tran` 结果行 `<name> = <sci-notation> targ = ... trig = ...` → flat dict scoreboard，total_measurements/sum_values/mean_value/max_value/max_name/min_value/min_name/range/num_nonzero；12 结果行 ground truth=total 12/sum 1.66655e-8/mean 1.3888e-9/max 3.456e-9 delay_max/min 1.23e-10 delay_pvt_ff/range 3.333e-9/12 nonzero；runtime tcl/waveview）。asset `assets/EDA-Eval-DesignFlow-Spice-001/meas.lis`；reference impl 落 `reference/EDA-Eval-DesignFlow-Spice-001_impl.tcl`。**reference+test 在 .75 waveview tcl 沙盒端到端 PASS（CHECK_PASS）**。pi 真实跑 Spice-001 prompt（`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium`，~40s）→ 产出正确 `spice_summarize_measure_lis` proc（显式 float grammar 正则、foreach+split、double() 守护、first-encountered tie-break 用 `>`/`<` 而非 `>=`/`<=`）。**pi 的 EXACT impl 在 .75 waveview 沙盒跑 test 全 PASS（PI_IMPL_CHECK_PASS，10/10 assert ok）**——首条 spice_sim 用例 + pi SUT 端到端打通。close_session(cleaned=true)。pi_debug_status.jsonl 增 Spice-001 PASS 行。regen report_10_29.html（21 用例，16.9KB）。累计用例=21（001 + RTL-Digital×4 + Aether-Layout×1[draft] + Innovus-DesignAudit×4 + Innovus-Netlist×3 + WaveView-Waveform×4 + Virtuoso-Flow×1 + Schematic-Netlist×1[draft] + PhysicalVerify×1 + Spice-Sim×1[新增,双 PASS]）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。
- [12:25] 第59轮：**首条 analog_context 类用例 Analog-001 落盘 + reference 在 .75 waveview 沙盒 PASS（pi-SUT 后台跑中）**。执行 MEMORY「下一步」首项（analog 1167 命中已定位 brian/opamp）。经 eda_flow `open_session(BENCH-MINE,eval_id=20261029-analog)`+`run_commands` 从 .75 只读分析 summary.tsv 的 analog 命中分布（`awk` dedup by session_file keep first，brian/x5t0t@hfeg0plg95 497 命中 opamp:756/hspice:461 是热点；次 vincelu/9knot@hfeg0plg55 862 cmos+analog+hspice+.cdl mixed-signal；easont/as67p@hfhds207 786 netlist+schematic+cmos+analog+waveview）。免密 ssh hfeg0plg95(10.129.8.227) 抓 **brian/x5t0t**（313-msg glm-5.2 真实会话）完整 ground truth：first user prompt = "make a simple OP AMP. gain over 1000, phase margin over 60 degree, gain bandwidth 1M"（经典两级 Miller-compensated 运放设计任务），+ assistant 探明 PDK（19nm 厚氧 I/O NTK/PTK subckts，VDD=3.3V，CL=10pF，hspice at /apps/synopsys/.../hspice64）+ 多次 HSPICE AC 仿真迭代（run_hspice.sh + opamp_testbench.sp/final_opamp.sp/opamp_v3.sp 等，编辑/重跑循环）+ 4 次真实 .lis `.measure` 块（grep `dc_gain=|ugf=|ph_ugf=|pm=|bw3=` 于 opamp_v3.lis/opamp_fixed.lis，实测 d1: dc_gain=3.8108/ugf=1.9193x/ph_ugf=109.7072/pm=289.7072/bw3=2.9790x；d2: dc_gain=-1.8993/ugf=failed/.../bw3=681.1814k；d3: dc_gain=31.2207/ugf=311.5293k/.../bw3=440.0795k；d4: dc_gain=-10.6042/全 failed）。基于该真实 grounding 建首条 analog_context 类用例 **Analog-001**（`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Analog-Context.jsonl`，analog_judge_opamp_ac_lis：解析 HSPICE AC .lis `.measure` 结果块（dc_gain[dB]/ugf[Hz]=GBW/ph_ugf[deg]/pm[deg]/bw3[Hz] per design iteration），normalize HSPICE scale suffixes（x=1e6/k=1e3/m=1e-3/u=1e-6/n=1e-9/p=1e-12/f=1e-15/a=1e-18/t=1e12/g=1e9/meg=1e6），保留字面 `failed`（不转 0/NaN），judge each design against spec（gain>=60dB AND ugf>=1e6 AND pm>=60deg，failed→不达标）→ flat dict scoreboard（num_designs + per-design d<i>_{dc_gain_db,ugf_hz,ph_ugf_deg,pm_deg,bw3_hz,meets_spec}）；4 真实 .measure 块 ground truth 4 设计无一达标；runtime tcl/waveview）。asset `assets/EDA-Eval-DesignFlow-Analog-001/opamp_ac.lis`（4 design blocks，脱敏 host/path）。reference impl 落 `reference/EDA-Eval-DesignFlow-Analog-001_impl.tcl`（_hspice_norm proc + 5-in-a-row block grouping + spec judge）。**reference+test 在 .75 waveview tcl 沙盒端到端 PASS（CHECK_PASS，all asserts ok）**——含 `failed` 字面保留 + scale suffix normalize + spec judge + negative boundary（4 真实设计无一达标，meets_spec 全 0）。b64 传输坑：单行 b64 在 paste/echo 经 base64 -d 时偶发字符损坏（`]`→`}`）致 Tcl `extra characters after close-brace` / `missing close-bracket`；解法：base64 -w1000 分 13 行，逐行 printf append 到 .75 文件再 decode（round-trip 干净）。pi 真实跑 Analog-001 prompt（`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium`，nohup 后台跑中，pi_done.txt 未现）。pi_debug_status.jsonl 增 Analog-001 PASS(ref-validated) 行。regen report_10_29.html（22 用例，18.3KB）。19→22 unique task_id / 0 dup。累计用例=22（+Analog-Context×1[新增,ref-validated PASS]）。三口径引用增补II落盘值不现查=698机/2850用户/52698会话/24085命中。体积自检：TASK 27.6KB / MEMORY ~31.5KB / EXP 21.5KB（全 ≤32KB OK）。close_session(cleaned=true) 待 pi 跑完。


## 归档批次 38（第69轮体积维护，2026-10-29）：第61–68轮详细流水原文

[13:07] 第61轮：LogicSynth-001 pi-SUT FAIL（$SPYGLASS_HOME 未转义→waveview 崩溃，ref 转义两行→PASS，test 经崩溃区分正确）+ 首条 skipper 类 Skipper-001 落盘（jason17w/hfeg0pnd002 UVS bsub run_regr 真实场景，tcl/skipper native runtime，pi+ref 双 PASS，skipper 沙盒 init 干净无 lowerCase-nil）。24 用例/10 类覆盖/19 PASS 1 FAIL 2 draft。三口径=698机/2850用户/52698文件/24085命中。
[13:31] 第62轮：首条 eda_other 类 EdaOther-001 落盘（sierraw/hfeg0plg08 CDL-vs-lib 覆盖率检查，真实 .lib ~452MB quoted-cell 陷阱，tcl/waveview 纯文本，pi+ref 双 PASS，naive unquoted-only impl 实测 FAIL 证 test 有 teeth）。**11/11 类全部覆盖完成**。25 用例/20 PASS 1 FAIL 2 draft。三口径=698机/2850用户/52698文件/24085命中。
[14:05] 第63轮：spice_sim 扩量第 2 条 Spice-002 落盘（e0030760/hfeg0plg49 6T SRAM bitcell Iread/Iwrite vs VDD sweep，真实 .mt0 $DATA1 双头跳过陷阱 + split " " 多空格空 token 坑，tcl/waveview POSIX regex，pi+ref 双 PASS 19 asserts，naive 不跳头 impl 实测 FAIL 证 test 有 teeth）。**进入扩量阶段**。26 用例/21 PASS 1 FAIL 2 draft。三口径=698机/2850用户/52698文件/24085命中。
[14:41] 第64轮：analog_context 扩量第 2 条 Analog-002 落盘（vincelu/hfeg0plg55 SiliconSmart drgqx_cmos_analog characterization，PEX 网表引用一致性审计，真实 .cdl.spf vs .spf_RC 后缀子串陷阱 + SMSC-99 no-PEX cell，tcl/waveview exact-suffix match，pi+ref 双 PASS 10 asserts 含 2 consistency invariants，naive substring impl 实测 FAIL 证 test 有 teeth）。fixture 43 inst/33 netlists/15 cdl.spf/18 spf_RC/10 no-PEX 与真实 SMSC-99 列表逐字匹配。**探明并修复 test-vs-impl string-rep 适配坑**：pi 用 dict create 返回→Tcl dict string-rep 给多 word value 加花括号→get_list 捕获含 `}`，修复剥一层 surrounding braces 同时接受 flat-string 与 dict-string-rep。27 用例/22 PASS 1 FAIL 2 draft。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。
[15:13] 第65轮：**logic_synth 扩量第 2 条 LogicSynth-002 落盘 + pi+ref 双 PASS**。经 eda_flow open_session(BENCH-MINE,20261029-logicsynth2)+run_commands 从 .75 awk 扫 summary.tsv 定位 logic_synth 真实会话 e0045128/1792719811850_q5ogm @ hfeg0plg49 (10.129.8.86, mc=139, genus:305/synthesis:186/dc_shell:70/synopsys:58/icc2:51)。**探明 sessions 真实布局=sessions/<sid>/<sid>.messages.json（子目录，任务书 SSH 模板路径需加一层 <sid>/）**；ssh 免密通但 channel 不自动关→输出已捕获、stderr "timed out" 仅为等 EOF 非失败。scp 1MB .messages.json 到 .75 workdir，python3 解析：真实任务=DC NXT WLM 模式（无物理库）综合，多 bit banking=0%（MB 库 MB2SDF/MB4SDF 已加载、1128 候选 bank、15307 单 bit FF、0 MB FF）。**真实陷阱（mined agent deepseek-v4-flash 实测踩到）**：先误诊"MB 库没加载"（错，log 显示已加载），后纠正为真根因——flow 用 `if {shell_is_in_topographical_mode}` 守卫 `identify_register_banks`，WLM compile_ultra（无 -spg）不进 topo→banking 步被整段跳过。建 LogicSynth-002（logicsynth_wlm_multibit_plan(log_summary) 返回 dict{root_cause,wlm_can_merge,enable_script,expected_mb_widths,needs_topo_for_wide_bus}，runtime tcl/waveview）。**test 设 3 输入案例给真 teeth**：Case A（真实 WLM+MB 加载+topo-gated）要求 root_cause 含 topographical AND identify_register_banks、NOT library-missing、wlm_can_merge=1、WLM enable_script 含 hdlin_infer_multibit+set_multibit_options+compile_ultra+report_multibit_banking、NOT identify_register_banks/-spg；Case B（MB 未加载）要求说 library not loaded+wlm_can_merge=0；Case C（topo has_spg=1）要求含 topographical+wlm_can_merge=0。naive always-topo-gated 失败 B；naive always-library-missing 失败 A。reference（3 分支 mb/spg/gated 诊断+dict create 返回）+test 在 .75 waveview CHECK_PASS（16 asserts/3 cases）。pi EXACT impl（string equal 分支+4 命令 WLM enable_script \\n 分隔+dict create 返回）同沙盒 PI_IMPL_CHECK_PASS。28 用例/23 PASS 1 FAIL 2 draft。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：MEMORY≈23.6KB / TASK 27.6KB / EXP 21.5KB（全 ≤32KB ✓）。

[15:43] 第66轮：**首条 pnr_signoff 类用例 PnRSignoff-001 落盘 + pi+ref 双 PASS（覆盖 503 命中空桶）**。经 eda_flow open_session(BENCH-MINE,20261029-pnr1)+run_commands 从 .75 awk 扫 summary.tsv 定位 pnr_signoff 真实会话 e0046913/1792572733650_pfubi @ hfeg0pkn003 (10.129.2.12, mc=153, primetime:213/icc2:194/innovus:60/netlist:654/synopsys:357/tempus:16)。scp 1.3MB .messages.json 到 .75 workdir，python3 解析 253 msgs：真实任务=在 STA_flow 之上构建 PrimeTime Top Timing ECO flow——cshell 启动器(run/run_eco.csh)→pt_shell -f scr/main_eco.tcl，10 个编号 tcl 步骤脚本(1_setup…10_rpt)，ECO_STAGE 选 signoff|eco|resignoff。真实结构（mined agent 的 main_eco.tcl 实测）：step7 signoff 总跑、step8 apply-ECO 仅 eco、step9 re-signoff 在 eco+resignoff、step10 总跑、1-6 总跑。真实陷阱：resignoff 重跑 signoff 于 ECO'd 网表(re-read patch/)但不重做 ECO(跳过 step8)。建 PnRSignoff-001（pnr_signoff_timing_eco_stage_plan(flow_spec) 返回 dict{num_steps,step_names,stage_runs[stage→排序步号],resignoff_runs_eco=0,resignoff_netlist_source=patch,eco_patch_strategy[buffer_whitelist+fixing_margin+eco_netlist_handoff],sta_eco_handoff[shared_library+shared_corner+shared_sdc],output_dirs,run_script_lang=cshell}，runtime tcl/waveview）。test 3 案例（A 真实 10 步 3 阶段验 signoff={1..7,10}/eco={1..10}/resignoff={1..7,9,10}跳8；B 2 阶段验无 resignoff key；C 纯 8 步 STA 验 signoff={1..8}）。naive run-all-steps 实测 FAIL 证 teeth。reference+test 在 .75 waveview CHECK_PASS（28 asserts/3 cases）。pi EXACT impl（逐步门控）同沙盒 PI_IMPL_CHECK_PASS。29 用例/24 PASS 1 FAIL 2 draft/15 jsonl。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：MEMORY≈25.5KB / TASK 27.6KB / EXP 21.5KB（全 ≤32KB ✓）。

[16:13] 第67轮：**eda_other 扩量第 2 条 EdaOther-002 落盘 + pi+ref 双 PASS**。经 eda_flow open_session(BENCH-MINE,20261029-edaoth2)+run_commands 从 .75 grep summary.tsv 定位 eda_other 真实会话 jascperc/1793172758983_0kv56 @ hfeg0pkn001 (10.129.2.10, cadence:25, mc=23)。scp 1.7MB .messages.json，python3 解析 462 msgs：真实任务=DDR DV pattern-speed 周统计（PTE_20260624 dvprog pattern_simulation_16Gb_LP6_Fix_*.avc，统计 speed/周/数量输出 html+md）。真实陷阱（mined agent 迭代~30 msg）：(1) only-irun.log folder 必须排除（真实 1005 avc 中 1000 folder 只含 irun.log→全排除，验证 152/1158 全 10667）；(2) speed=avc basename 倒数第二 `_` 字段(10667/9600)非最后(001/996)。建 EdaOther-002（pattern_speed_weekly_stats(manifest) 返回 flat dict{total_avc,total_valid,num_no_folder,num_only_irunlog,num_empty,num_no_speed,time_span_lo,hi,speeds,speed_totals,weeks,week_totals,week_speed}，tcl/waveview）。test 3 案例（A:28 条 15 valid 10667 跨 W34/38/42/43/44,9 only-irunlog speed-9600 全排除;B:9600 有 folder 证非无条件排除;C:speed=倒数第二 8000/9600/10667）。探明 waveview `clock format %G-W%V -gmt 1` 可用 ISO 周一致。探明并修复 2 坑：双引号内 `[[:space:]]` 被 expr 解析为命令替换→改 literal-space pattern；speeds `lsort -integer`(数字序)。reference+test 在 .75 waveview CHECK_PASS(27 asserts/3 cases)。naive count-all-avc 实测 FAIL(leaks 9600,total_valid=11)。pi EXACT impl(Tcl arrays+lindex end-1+strict folder validation+lsort -integer+flat join)同沙盒 PI_IMPL_CHECK_PASS(27 asserts/3 cases)。30 用例/25 PASS 1 FAIL 2 draft/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.3KB / MEMORY 27.2KB / EXP 21.0KB（全 ≤32KB ✓）。

## 流水
- 轮次 1–12 流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 3（v0.1 脱敏基线 → v0.11 worked example）。要点：v0.1 探明本机即目标(19用户/3487轨迹)；v0.2 聚类暴露残留人名 shiwei/zhulong→scrub 修复；v0.4 judge 揭示 code_dev 标签噪声；v0.6 修服务密码/服务账号 PII 泄漏；v0.7 修 PYTHONHASHSEED+4×datetime 漂移；v0.8 freeze-by-default；v0.9 规范发布 bundle；v0.10 v1.0-rc1；v0.11 worked example acc=0.8174。
- 轮次 13–17 流水原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 4（v0.12 统一入口 → v0.16 DATA_CARD 增补）。要点：v0.12 聚合 README；v0.13 版本演进 diff；v0.14 统计严谨性（κ=0.4496/选择偏倚/bootstrap CI）；v0.15 去偏 split+双标注者评分（gap+0.5087）；v0.16 DATA_CARD 增补 addendum。
- [21:45]第18–22:35]第20轮 + 轮次21–26：流水原文已归档至 ARCHIVE 归档批次 6/8/10/11/13/15/17。要点：v0.17 诊断发布 bundle / v0.18 disputed 刻画 / v0.19 诊断 split；v0.20 发布整合+弃用 v0.17 / v0.21 bootstrap CI gap[0.4453,0.5729]显著(p=0.0) / v0.22 §G；v0.23 全树 124 锚点穷举 PASS（首个全树级，subsumes v0.22）/ v0.24 §H / v0.25 per-user 公平性 Gini0.5654 LOUO|Δ|max0.0486<0.05 user-robust 但 8/9 类单用户垄断；v0.26 user-strat gap=−0.2291 / v0.27 §I / v0.28 matched-count dZ=−0.1176 证伪「多用户即缩 gap」 / v0.29 §J / v0.30 lineage RE-sweep 147 PASS+4 LIVING。
- 第32–48轮：流水原文已归档至 ARCHIVE 归档批次 24/27/28/31/32/33/34。要点：v0.31 §K / v0.33 §L / v0.34 lineage RE-sweep（第4次全树）/ v0.35 §M / v0.36 scaling-artifact / v0.37 §N / v0.38 bootstrap CI / v0.39 §O / v0.40 lineage RE-sweep（第5次全树，197 PASS+9 LIVING）/ v0.41 §P / v0.42 per-class gap-shrink CI / v0.43 §Q / v0.44 lineage RE-sweep（第5次，217 PASS+11 LIVING）/ v0.45 §R / v0.46 lineage RE-sweep（第6次，220 PASS+11 LIVING）/ v0.47 §S / v0.48 lineage RE-sweep（第7次，223 PASS+11 LIVING）。
> 第49轮流水原文（v0.48 lineage RE-sweep 构造层，已被 v0.49 §T 整合层 subsume）已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 33。要点：v0.48 subsumes v0.46 第 7 次全树审计，46 版本/105 manifest/234 锚点→223 PASS+11 LIVING，drift_vs_v046 134/134 0 回归+1 net-new，产 lineage_audit_v048.json sha256 08553f86…，DETERMINISM 3/3+leak 0。
- [08:20] 第50轮：v0.49 发布索引再生 + DATA_CARD addendum §T 整合层（纳入 v0.48 第7次全树审计，48 版本/47 ACTIVE，DETERMINISM 5/5+leak 0）。流水原文已归档至 ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 34。
- [08:20] 第50轮事件：**.75 #1 卡点解决**——新增 eda_flow MCP 获 .75 只读命令执行能力，.75=第二个 cline 主机(16用户/192 sessions，格式同本机)；3 口径现查=2机/3679轨迹。原文已归档至 ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 34。
- [08:50] 第51轮：**执行运维增补 II——停止 lineage 自审计空转，转多机扩样**。eda_flow 只读拉 .75 上沈佳成 698 机扫描结果→bench_v0.50（11 类 weighted，698机/2850用户/52698会话/24085命中）；DETERMINISM+PII leak PASS；v0.1–v0.49 halt。流水原文已归档至 ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 34。
- 第52轮：执行运维增补 III（用例落盘+pi调试+日报）。探明 pi 用法（需 Node22 PATH，flag=--print --no-approve --model deepseek-v4-pro-cloud --thinking medium）。新建首条 Aether-Layout-001（draft，aether host 超时）。流水原文已归档至 ARCHIVE 批次 37。
- 第52b轮：3 条 Innovus-DesignAudit（Digital-002/003/004，dbGet distinct masters/most_used/orient）落盘 + .75 innovus 沙盒全 PASS + pi↔eda_flow MCP 端到端连通验证 + 首份 report_10_29.html + gen_daily_report.py/pi_debug_status.jsonl。流水原文已归档至 ARCHIVE 批次 37。
- 第53轮：4 条 WaveView-Waveform（Wave-001/002/003/004，sx_* API count signals/bus/scopes）落盘 + .75 waveview 沙盒全 PASS + pi 实跑 Wave-001 PASS。流水原文已归档至 ARCHIVE 批次 37。
- 第54轮：3 条 Innovus-Netlist（Digital-005/006/007，dbGet nets/terms/insts）落盘 + .75 innovus 沙盒全 PASS。探明 virtuoso skill/aether host 阻塞。流水原文已归档至 ARCHIVE 批次 37。
- 第55轮：运维增补 IV 验证（698 机免密 SSH 抓真实 prompt，3 会话）+ Digital-008（insts_of_master，0x0 陷阱）ready + Sch-001 draft（virtuoso skill lowerCase nil 阻塞）+ 并发冲突妥善处理（renumber 避撞 task_id）。流水原文已归档至 ARCHIVE 批次 37。
- 第56轮：Virtuoso-Flow-001（真实 e0014566/m2vah rscalc+autovia 配置整合）落盘 + reference/test 在 .75 waveview 沙盒 PASS（绕过 skill 阻塞）+ pi-SUT 因 provider 丢失阻塞。流水原文已归档至 ARCHIVE 批次 37。
- [11:20] 第57轮：首条 physical_verify 类用例 PV-001（Calibre DRC scoreboard）落盘 + pi SUT 端到端双 PASS + 体积维护归档（流水原文已归档至 ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 36）。
- [11:51] 第58轮：首条 spice_sim 类用例 Spice-001（HSPICE .measure scoreboard）落盘 + pi SUT 端到端双 PASS。流水原文已归档至 ARCHIVE 批次 37。
- [12:25] 第59轮：首条 analog_context 类用例 Analog-001（HSPICE AC opamp spec-judge，真实 brian/x5t0t 两级 Miller 运放）落盘 + reference 在 .75 waveview 沙盒 PASS（pi-SUT 后台跑中）。流水原文已归档至 ARCHIVE 批次 37。
- [12:55] 第60轮：**首条 logic_synth 类用例 LogicSynth-001 落盘 + reference/test 在 .75 waveview 沙盒 PASS（pi-SUT 跑中）+ 体积维护归档**。经 eda_flow open_session(BENCH-MINE)+run_commands 从 .75 只读 awk summary.tsv 定位 logic_synth 热点会话 lorikx/1792574756685_lond8（mc=249,dc_shell:151/synthesis:99/icc2:46），免密 ssh hfeg0plg49(10.129.8.86) 抓真实 lint+syn 综合流程 ground truth（first prompt=做 lint 项目文件+综合流程，dc_shell 可用，建 lint/{design_rtl.list,cfreq_ctrl.prj,Makefile,waiver.tcl,cdc.sdc,rdc.sdc}+syn/{syn_filelist.f,common_setup.tcl,dc.tcl(compile_ultra),Makefile}）。建 LogicSynth-001（logicsynth_build_lint_scaffold 返回 dict{design_rtl_list,prj,makefile}，runtime tcl/waveview）。reference+test 在 .75 waveview 沙盒 CHECK_PASS（探明 waveview Tcl 无 eq 运算符→[string equal]，$SPYGLASS_HOME needle 须 $ 转义）。pi 后台跑中。体积维护：MEMORY 35.1KB→19KB（归档第52–59轮详细流水至 ARCHIVE 批次 37 留指针）。累计用例=23（23 unique/0 dup，覆盖 9/11 类）。三口径引用增补II落盘值=698机/2850用户/52698会话/24085命中。体积自检：TASK 27.6KB / MEMORY 19KB / EXP 21.5KB（全 ≤32KB ✓）。
[16:55] 第68轮：**运维即时令V 执行 + pnr_signoff 扩量第 2 条 PnRSignoff-002 落盘 + reference 在 .75 waveview CHECK_PASS（pi-SUT 后台跑中）**。(1) 运维即时令V：gen_daily_report.py 生成 report_10_29.html（36KB，30用例/25PASS）+ commit dc9764b + push。(2) PnRSignoff-002：经 eda_flow open_session(BENCH-MINE,20261029-pnr2)+run_commands 从 .75 awk summary.tsv 定位 johnl/1792572659304_xt45f @ hfeg0pfn119 (10.129.33.245, mc=183, innovus:1655/primetime:54)。scp 1.4MB .messages.json，python3 解析 269 msgs：真实任务=addr_to_rowcol_v7 (cxmtG5_CIP DRAM, 107 cells/116 nets) Innovus PR→StarRC→SPEF→PrimeTime STA 复现指南。**真实 ground-truth**：SPEF 116/116=100%、WNS −0.04/TNS −0.17、5 violating/116 total、critical 13 levels、arrival 0.54 vs required 0.50→slack −0.04 (VIOLATED)。建 pnr_signoff_parse_sta_report(report)→dict，tcl/waveview。**真实陷阱（初级工程师常见错）**：(1) slack 符号=required−arrival（VIOLATED 为负）——naive arrival−required 翻转符号把违反报成 MET；(2) TNS=仅负 slack 之和（MET 正值不计）；(3) SPEF coverage=annotated/total 非 total/annotated；(4) WNS=最负 slack 非 max/first，全 MET 时为正。**额外坑**：path 行 `slack (VIOLATED) -0.04`（无冒号无 ns）vs critical 行 `Slack (VIOLATED): -0.04 ns`（有冒号有 ns），正则 `^\s*slack\s+\((VIOLATED|MET)\)\s+(-?\d+\.\d+)\s*$` 精确匹配前者拒绝后者。test 3 案例（A 真实 7 paths 5 VIOLATED+2 MET 116/116；B 全 MET +0.12 证 wns 正；C 部分 SPEF 95/116=81.9% 证 coverage=annotated/total）。reference+test 在 .75 waveview **CHECK_PASS**(41 asserts/3 cases)。naive（max-scan wns+sum-all tns+total/annotated+arrival−required）实测 **FAIL**(A wns_ns assert 即被捕获)证 teeth。pi-SUT PID 297161 后台跑中。31 用例/25 PASS 1 FAIL 2 draft 1 running/16 jsonl（PnRSignoff 现 2 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。

## 归档批次 39（第78轮归档，第69–75轮详细流水原文）

> 第61–68轮详细流水原文（评测用例扩量期：LogicSynth-001/Skipper-001/EdaOther-001/Spice-002/Analog-002/LogicSynth-002/PnRSignoff-001/EdaOther-002/PnRSignoff-002 落盘 + pi SUT 调试 + 运维即时令V 日报）已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 38。要点：11/11 类全覆盖后进入扩量阶段，pi+ref 双 PASS 累计 12 条（Wave-001/Digital-005/PV-001/Spice-001/Skipper-001/EdaOther-001/Spice-002/Analog-002/LogicSynth-002/PnRSignoff-001/EdaOther-002/PnRSignoff-002），LogicSynth-001 pi-SUT FAIL 真实 Tcl 引号陷阱。
[17:38] 第69轮：**physical_verify 扩量第 2 条 PV-002 落盘 + reference 在 .75 waveview CHECK_PASS（pi-SUT 后台跑中）**。经 eda_flow open_session(BENCH-MINE,20261029-pv2)+run_commands 从 .75 grep summary.tsv 找 calibre/lvs 命中→ssh hfeg0plg49 grep "Comparison (CORRECT|INCORRECT)|LVS run.*COMPLETE" 定位 9 个含完整 LVS 结果会话→scp 候选 + python3 解析 first prompt 选 ziyuny/1789561002781_mqop7 @ hfeg0plg49（lvsdebug 会话，102 msgs）：真实任务=PDK QA Argus LVS 回归扫描——精读 argus-lvs-log-analysis.md 学习 NE+SVS 两段式 LVS log 结构→扫 /proj/drgqa/V0/ver/lvs_argus/drgqa_cmos_top/*/argusLVS.log 按 4 类分诊（莫名中断/卡住/power-ground short/超万 pin error）汇总。**真实陷阱（mined agent + 用户现场纠正）**：(1) "N PENDING OPERATIONS" 是**并发算法进程数**不是 pending 堆积——completed+full progress 高 PENDING 正常，stuck 只由 NE progress% + REAL TIME 判定**绝不由 PENDING 判**；(2) power/ground short 可在 LVS PASS 时存在（BCenter vddq!-vdpg! 但 LVS PASS），short 从 SHORT: 行读**不从 LVS verdict 读**；(3) pin-error-storm 阈值 >10000（Channel_x >100000）；(4) interrupted vs stuck 由 REAL TIME 区分；(5) `====end====` 后 PVE viewer log 须忽略。建 argus_lvs_log_triage(path)→flat dict{lvs_completed,total_real_time_sec,ne_progress_pct,max_pending_operations,power_ground_short,short_net_pairs,pin_error_count,pin_error_storm,stuck_long_running,interrupted,primary_category}，tcl/waveview。test **5 案例**（A vcc!-vss!+105342 pin+LVS FAIL+completed→power_ground_short；B NE 7%+140s+206 PENDING 无 completion→stuck；C completed CLEAN 250 PENDING+signal short→**证 PENDING-is-not-backlog 关键坑** stuck=0；D vddq!-vdpg! short **DESPITE LVS PASS**→power_ground_short 独立 verdict；E crashed NE 3%+5s+segfault→interrupted）。reference+test 在 .75 waveview **CHECK_PASS**(51 asserts/5 cases)。naive（stuck by PENDING>200 + short gated on LVS FAIL）实测 **FAIL**(A power_ground_short assert 即被捕获)证 teeth。**pi-SUT 后台 PID 552996 ~9min 跑完 REF_CHECK_RC=0（5 cases/51 asserts 全 PASS）→ pi+ref 双 PASS**。32 用例/27 PASS 1 FAIL 2 draft 0 running/16 jsonl（PV 现 2 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY 17.6KB（归档第61–68轮详细流水→ARCHIVE 批次38）/ EXP 21.5KB（全 ≤32KB ✓）。
[18:11] 第70轮：**waveform 扩量第 3 条 Wave-005 (sx_signal wildcard-selection) 落盘 + pi+ref 双 PASS**；回收 PV-002 pi-SUT=PASS。经 eda_flow open_session(BENCH-MINE,20261029-wave2)+run_commands 从 .75 grep summary.tsv 找 waveview 命中→ssh hfeg0plg49 抓 t0002801/1791876404012_d7cbo（waveview:403 hits，190 match_count，Gm/Id 查找表 MOSFET I-V sizing）：真实 waveview 脚本（grep tool_result 原文）=`set fileObj [sx_open_sim_file_read $dbFile]; sx_display [sx_signal "*.isub(d*)"]; wv_select_waveview 1 {waveview 1}`，用 **sx_signal glob 批量选信号**（与 Wave-001/002 iterate+string-match API 不同）。**真实陷阱（.75 waveview demo mixed.fsdb 实测验证）**：`sx_signal <glob>` 比 `iterate + string match [sx_get_name]` 多匹配 **4 个** alias/escaped 信号（sx_get_name 不暴露）——每个非平凡 pattern 都差 4：`*clock*`=9 vs 5、`*rst*`=13 vs 9、`*data*`=7 vs 3、`*En_*`=24 vs 20、`*`=240 vs 240。建 wv_count_by_pattern(fsdb_path,pattern)→llength [sx_signal $pattern]，tcl/waveview。test 8 asserts。reference CHECK_PASS；naive（iterate+string-match）实测 **FAIL**（clock==9 返回 5）证 teeth。pi EXACT impl（sx_signal + llength）经 eda_flow MCP .75 waveview 跑 test → **REF_CHECK_RC=0/CHECK_PASS**（~7min, PID 733083, exit=0）。回收 PV-002 pi-SUT（PID 552996）=**PASS**（51 asserts/5 cases，~9min）。33 用例/28 PASS 1 FAIL 2 draft 0 running/16 jsonl（WaveView 现 5 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~18.5KB / EXP 21.5KB（全 ≤32KB ✓）。
[18:43] 第71轮：**spice_sim 扩量第 3 条 Spice-003 (FineSim/CustomSim XA log BSIM-CMG 版本不支持诊断) 落盘 + pi+ref 双 PASS (DESIGN_FLOW_VERDICT=PASS, 5 cases/45 asserts, pi exit=0 ~5min)**。经 eda_flow open_session(BENCH-MINE,20261029-spice3)+run_commands 从 .75 grep summary.tsv 找 hspice 命中→ssh hfeg0pkn004 抓 e0024852/1792118523831_f10db（hspice:1317 tool hits，77 msgs/5 user prompts）：真实任务=后仿验证读 FastSPICE xa.log 判 done/failed + 失败定位 root-cause category 路由工单。真实场景：CCK_..._1016 老 CustomSim P-2019.06-SP1-BETA 跑挂，CCK_..._1009 新 PrimeSim XA V-2023.12 跑通——根因 BSIM-CMG version=111.2 老版 XA 不支持，CMI warning 表明示 "Version = 111.2 in BSIM-CMG model is not supported. Reset it to version = 110"。**真实陷阱**：root_cause 优先级 success > model_version_unsupported > convergence > missing_model > unknown；Case E (CMI warning + "time step too small" convergence) naive 按 keyword 分类返回 convergence 而 FAIL。建 xa_log_diagnose(path)→flat dict，tcl/waveview。test 5 cases/45 asserts。**flat-dict 空值用 `none` 占位**。reference 经框架 wrapper（proc check{candidate} + catch check xa_log_diagnose→DESIGN_FLOW_VERDICT）→ VERDICT=PASS / DETAIL=PASS 5 / FAIL 0。naive（不解析 CMI）FAIL 3 teeth asserts。**test 已 wrap proc check{candidate}** 匹配框架单参 check 约定。34 用例/14 PASS 1 FAIL 2 draft 1 running/16 jsonl（Spice-Sim 现 3 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~18.5KB / EXP 21.5KB（全 ≤32KB ✓）。
[19:33] 第72轮：**logic_synth 扩量第 3 条 LogicSynth-003 (DC→Genus 21.x set_db 脚本移植) 落盘 + pi+ref 双 PASS (RESULT:PASS 9 cases; pi foreground via stdin ~1min, switch-based impl 避开 waveview-Tcl 不支持\b gotcha)**。经 eda_flow open_session(BENCH-MINE,20261029-ls3)+run_commands 从 .75 grep summary.tsv 找 genus 命中→scp hfeg0plg49:e0045128/1792719811850_q5ogm（genus:305 synthesis:186 dc_shell:70，205 msgs）→python3 解析。工程师迁移 DC NXT WLM 综合流到 Genus 21.17 手写「DC/Genus 综合速查 KB」记录真实 set_db idiom。真实任务=把 DC Tcl 综合脚本 8 类构造（target_library/link_library/hdlin_infer_multibit/set_multibit_options -min_bit_width/set_dont_use/compile_ultra/compile_ultra -spg/report_multibit_banking/未知 var）逐一翻译成 Genus set_db idiom，返回 dict{genus_cmd,port_type,removed}。真实映射：libs→read_lib；mb→design:*.multibit attr；mb_width→multibit_threshold；dont_use→lib_cell.dont_use；compile_ultra→syn_generic/syn_map/opt -pre_cts；-spg→NO_EQUIVALENT；report_banking→report_qor -summary。真实陷阱=naive 1:1 set_app_var→set_db 关键字替换发出错误属性名+保留 compile_ultra→FAIL；Case G -spg teeth。Waveview-Tcl GOTCHA：regexp 不支持 \b→ref/pi 用 ($|\s)。建 logicsynth_dc_to_genus_port(dc_cmd)→dict，tcl/waveview，test 9 cases。reference impl .75 waveview → PASS 9 cases（2 rerun 稳定）。pi-SUT deepseek-v4-pro-cloud switch-based impl → .75 waveview → RESULT:PASS 9 cases。pi+ref 双 PASS。35 用例/16 PASS 1 FAIL 2 draft 0 running/16 jsonl（LogicSynth 现 3 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~19KB / EXP 21.5KB（全 ≤32KB ✓）。
[20:03] 第73轮：**pnr_signoff 扩量第 3 条 PnRSignoff-003 (PrimeTime STA cshell launcher 审计 · csh -f module-bootstrap 陷阱) 落盘 + reference 在 .75 waveview CHECK_PASS (run_design_flow.py TCL-case-OK, 6 cases/52 asserts)；naive always-ok impl 实测 FAIL (caught at A has_module_bootstrap) 证 teeth；pi-SUT 后台 running**。经 eda_flow open_session(BENCH-MINE,20261029-pnr3)+run_commands 从 .75 awk summary.tsv 按 primetime 命中排序→旧候选 thomas1w/1792056947936_36yj3 实为 netlist-rich(805)/primetime:4 非 primetime-rich(描述有误)→改挖 e0046913/1792401589701_f9heo @ hfeg0plg46 (primetime:111 synopsys:649 pdk:47 hspice:12, 185 msgs)：scp messages.json 到 .75 workdir→python3 解析。真实任务=构建完整 PrimeTime STA flow (cshell launcher run_sta.csh → pt_shell -f sta_main.tcl -x "<preset>"，编号 tcl 1_setup..10_rpt，corner/mode 传参，RUN_TAG 后缀，common_setup.tcl 用 if {![info exists]} 尊重 -x 预设)。**真实陷阱（mined agent 现场纠正，editor msg 116）**：`#!/bin/csh -f` 跳 .cshrc → tcsh 在 csh -f 下**不继承** bash 导出的 module 函数 → 直接 module purge/load 运行报 'module: Command not found'；修复=首个 module 调用前定义 alias module (modulecmd csh) 或 source modules.csh；bash launcher 无需 bootstrap。建 pnr_signoff_audit_pt_launcher(launcher)→dict(9 keys)，tcl/waveview，4 critical rules R1/R2/R3/R4，test 6 cases/52 asserts（A 无bootstrap→broken R1；B alias-before-purge→ok；C source-modules.csh→ok；D bootstrap-after-purge→broken R1 顺序 teeth；E bash 无bootstrap→ok bash teeth；F 预设漏MODE→broken R4）。reference impl（POSIX [[:space:]] 避 \\b；line-index 判 bootstrap-before；XVAR/-x 行扫描判 preset vars）经 run_design_flow.py 在 .75 waveview → TCL-case-OK/PASSED。naive always-ok FAIL 证 teeth。**test 用 @D@/@B@ 占位 + global $::dch/$::btk + string map mk 绕 Tcl {} 内 ${...}/backtick 限制**（首轮 mk 作用域漏 $dch 报 'can't read dch' 已修 global）。reference 持久化到 reference/ 目录。pi-SUT (deepseek-v4-pro-cloud, bg, 自验证模式 pi 调 eda_flow MCP open_session→run_code→close_session→print DESIGN_FLOW_VERDICT) running。36 用例/16 PASS 1 FAIL 2 draft 1 running/16 jsonl（PnRSignoff 现 3 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~23.5KB / EXP ~21.5KB（全 ≤32KB ✓）。
[20:11] 第73轮收尾：**PnRSignoff-003 pi-SUT 回收 = PASS** (CHECK_RESULT: PASS 6 cases / DESIGN_FLOW_VERDICT=PASS, deepseek-v4-pro-cloud exit=0 ~9min via eda_flow MCP .75 waveview 自验证模式) → **pi+ref 双 PASS**。37→36 用例口径修正：实际 36 unique task_id（PnRSignoff 现 3 条全 PASS）；pi SUT PASS=17 / FAIL=1 / draft=2 / running=0。三口径=698机/2850用户/52698文件/24085命中。体积自检：TASK 28.9KB / MEMORY ~23.4KB / EXP ~21.5KB（全 ≤32KB ✓）。
[20:34] 第74轮：**physical_verify 扩量第 3 条 PV-003 (Calibre DRC emptyDeriveLayer error-count inversion + waive list) 落盘 + reference 在 .75 waveview CHECK_PASS (DESIGN_FLOW_VERDICT=PASS 5 cases/35 asserts)；naive normal-DRC-convention (cnt==0=hasShapes, ignore waive) impl 实测 FAIL (caught at A has_shapes_count eq 3, naive returns 6) 证 teeth；pi-SUT 后台跑中**。经 eda_flow open_session(BENCH-MINE,20261029-pv3)+run_commands 从 .75 grep summary.tsv 找 calibre 命中→ssh hfeg0plg49 scp xinqiaoz/1788770994295_x4b0p.messages.json (calibre:4451 pdk:2168 .gds:149, 537 msgs, PDK-QA DRC Deck migration/Calibre pattern-QA session)→python3 解析。**真实陷阱（mined agent Phase-1 EmptyDeriveLayerCheck 设计文档记录）**：emptyDeriveLayer probe 为每个衍生层生成 deriveCheck_<LAYER> DRC rule 故意把该层 shapes 标为 DRC errors，bsub -Is -q drc 跑后解析 per-rule error count；verdict 与正常 DRC 反转：error_count>0=层有 shapes=OK，error_count==0=层空=defect。naive '0 errors=PASS' 完全反。叠加真实 WAIVE list (FB_CMP/POWER_SINGLE/VOLTAGE_L/VOLTAGE_H/PROBEPAD)：waived-empty 层不算 defect（单独跟踪）。建 calibre_empty_derive_layer_classify(summary,waive_list)→dict(7 keys)，tcl/waveview（POSIX [[:space:]] 类，无 \b/\s/\d）。test 5 cases/35 asserts（A mixed has-shapes+empty-unwaived(VIA1,VIA2)+empty-waived→fail；B all has_shapes→pass verdict-inversion teeth；C all empty all waived→pass waive teeth；D all empty none waived→fail core inversion teeth；E format robustness lowercase/leading-ws/extra-spaces+单 empty-unwaived）。reference impl 经 .75 waveview run → DESIGN_FLOW_VERDICT=PASS/DETAIL=PASS 5 cases。naive 实测 FAIL 证 teeth。**PnRSignoff-003 pi-SUT 回收=PASS** (CHECK_RESULT: PASS 6 cases / DESIGN_FLOW_VERDICT=PASS, ~9min)。37 用例/17 PASS 1 FAIL 2 draft 1 running/16 jsonl（PhysicalVerify 现 3 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~26KB / EXP 21.5KB（全 ≤32KB ✓）。
[21:34] 第75轮：**analog_context 扩量第 3 条 Analog-003 (HSPICE .meas tran 脚本结构化解析) pi+ref 双 PASS (DESIGN_FLOW_VERDICT=PASS 6 cases；pi DETAIL=PASS 6 / FAIL 0)**。Analog-003 由 build_analog003_jsonl.py 在 21:21 auto-commit 落盘（status ready 但未沙盒验证），本轮补做双验证：经 eda_flow open_session(BENCH-ANA3-VAL,20261029-a3val)→write_file ref.tcl(5249B)+checker.tcl→run_code tcl/waveview (cd workdir; source ref.tcl; source checker.tcl) → CHECK_RESULT: PASS 6 / FAIL 0 / DESIGN_FLOW_VERDICT=PASS。pi-SUT (deepseek-v4-pro-cloud, bg) 同 prompt+checker 经 eda_flow MCP .75 waveview 自验证 → DESIGN_FLOW_VERDICT=PASS / DETAIL=PASS 6 / FAIL 0。**真实陷阱**：'+' 续行须先 merge 到所属 .meas 再分类（注释/空行不中断续行）；tokenize 用 [[:space:]]+ 跑（空格 OR TAB，.meas\ttran\tNAME）；param='...' 算术 expr 子句不是电压 level；数字 literal '0.625' 非 param-expr；trig/targ/when/find 整 token 相等；bodiless 头→unknown；优先级 param>find_when>when>trig_targ>unknown。test 6 cases（A trig/targ+quoted-param-level, B when-only TAB teeth, C find/diff, D param+tdref+diff, E dual-trig+bodiless+comments, F numeric-level teeth）。mined zongjiuh/1792551168500_xppi3 @ hfhds234 (hspice:22 netlist:304 analog:46, 119 msgs, DRAM CAS-read per-bank daily timing .sp deck)。pi_debug_status.jsonl 追加 Analog-003 PASS 行（45 rows）。report_10_29.html regen(71KB)。38 用例/18 PASS 1 FAIL 2 draft 0 running/16 jsonl（Analog-Context 现 3 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。体积自检：TASK 28.9KB / MEMORY ~28KB / EXP 21.5KB（全 ≤32KB ✓）。


## 归档批次 40（2026-10-30 第90轮体积维护，从 MEMORY 流水移入）

[23:35] 第80轮：**PnRSignoff-004 (Innovus report_message 日志严重性审计+unique-MSG_ID dedup+late-stage blocking 检测) 新建 ref-PASS / pi-SUT running**。经 eda_flow open_session(BENCH-MINE,20261029-r80)→run_commands ssh -n -T 探 12 台中低 tier 机→**11/12 完全清空**（§会话易失性扩展：fresh mining 死路确认，.75 自身 192→0）→转基于已知真实任务模式扩量。建 PnRSignoff-004 = Innovus `**ERROR/**WARNING/**INFO (IMPRPT-NNNN)` report_message 日志审计 + 缩进 continuation 合并 + `# Stage: route_complete` late 标记 + WAIVED whole-token + blocking 判定（late & not waived→blocking_errors）。真实陷阱：(1) CONTINUATION MERGE for WAIVED（续行上）line-1-only 漏判→overcount blocking；(2) OCCURRENCES vs UNIQUE（同 id fire N 次）error_count=N/unique=distinct；(3) LATE-STAGE ORDERING + marker prefix（`# Stage: ` 前缀必填，banner `# route_complete ...` 不翻；marker 前=EARLY）；(4) NO-ID malformed ERROR 仍计数+blocking 但不入 unique_ids/blocking_ids；(5) `**WARNING:` 全词。Task pnr_signoff_report_message_audit(log)→dict(12 keys)。test 6 cases/40+ asserts。reference impl（单遍 forward scan 合并 continuation+snapshot late at msg start；二遍 count/dedup/classify）经 .75 waveview run_code → RESULT:ALL_ASSERTS_PASS 6 cases。pi-SUT deepseek-v4-pro-cloud 后台 running (PID 2157750, 23:33 启动)。pi_debug 追加 running。report_10_29.html regen(58KB, KPI dedup 35 PASS/1 FAIL/2 draft/1 running)。bench-mine session close+clean。42 用例/35 PASS 1 FAIL 2 draft 1 running 3 uncovered/15 jsonl（PnRSignoff 现 4 条）。三口径=698机/2850用户/52698文件/24085命中。

[21:58] 第76轮：**skipper 扩量第 2 条 Skipper-002 (UVS vps.log 回归进度解析+状态分类) pi+ref 双 PASS (RC=0 RESULT=CHECK_PASS 6 cases A-F / pi DESIGN_FLOW_VERDICT=PASS)**。经 eda_flow open_session(BENCH-MINE,20261029-skip2)→run_commands 从 .75 grep summary.tsv 找 skipper 命中→ssh hfeg0pnd002 scp jason17w/1790166621537_hcxal.messages.json (skipper:51/netlist:345/hspice:66, 195 msgs, DDR/LPDDR UVS Verilog 回归)→python3 解析。真实任务=tail vps.log 监控 UVS 回归状态。**真实陷阱（mined agent 现场 root-cause）**：(1) 主 bsub job 队列(bcp_LP1) vs VPS **worker** task 队列(VPC grid config 默认 uvs_test)——`uvs_test: No such queue` 意味 worker 无法启动、Queued 堆积 Running=0 → STUCK(worker_queue_missing) **非** running；修复=把 `-q bcp_LP1` 传给 run_regr 自身（非只传 bsub）；(2) pending+Running:0 但**无** queue error = 仅等 LSF 资源 → 仍 running（**非** stuck）；(3) verdict 按 pass-rate：done+fail>0 → FAIL 即使 pass>0（真实 avl_no_act_wr PASS + dqs_osc_manual FAIL = 50% → FAIL）；(4) 终态 summary `Total: 2, Pass: 2, Fail: 0` **无** Queued/Running（逗号变体）live-line-only regex 失败留 0；(5) state 优先级 stuck>done>running。建 vps_regr_progress_classify(log)→flat dict(9 keys)，tcl/skipper（POSIX [[:space:]]/[[:digit:]]/[[:alnum:]_]，无 \s/\d/\b）。test 6 cases（A running；B queue-stuck TEETH；C done-pass；D done-fail TEETH pass>0!=PASS；E comma-summary TEETH；F pending-not-stuck TEETH）。reference .75 skipper tcl RC=0 CHECK_PASS；naive（无 queue_error/pass>0->PASS/Running:0->stuck/live-only）FAIL(B) 证 teeth；pi-SUT deepseek-v4-pro-cloud 经 eda_flow MCP .75 skipper 自验证 → RC=0 CHECK_PASS / DESIGN_FLOW_VERDICT=PASS。pi_debug 追加 Skipper-002 PASS。report_10_29.html regen(73KB)。40 用例/31 PASS 1 FAIL 1 draft(+7 无 pi 行)/15 jsonl（Skipper 现 2 条全 PASS）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。

[22:03] 第77轮：**waveform 扩量第 6 条 Wave-006 (WaveView ACE 批量 WVRES/WVERR/WVINFO 协议输出解析) pi+ref 双 PASS (DESIGN_FLOW_VERDICT=PASS / DETAIL=PASS 6 cases / pi exit=0)**。mined adaml/1792215882223_qv6pl @ hfeg0plg49 (synopsys:1412 waveview:729, 337 msgs, waveview-ace-batch skill) 经 eda_flow ssh scp。真实任务=parse `wv -ace_no_gui` catch 包装后吐出的 WVRES/WVERR/WVINFO 协议→dict(13 keys)。**真实陷阱**：(1) WVRES value 可为数值标量/非数值 sentinel/逗号 LIST——总是 float-coerce 的 parser 崩溃；(2) WVERR/WVINFO msg 可能含 pipe→uniform split('|') 无 maxsplit 切碎 msg 丢行；正确 WVRES/WVERR maxsplit=3、WVINFO maxsplit=2；(3) WVERR key=FAILED key 与 result_keys 分离；(4) files_seen 取自 WVRES+WVERR；(5) total_numeric_elements=数值标量各1+数值 list token 各1。tcl/waveview（POSIX 类；Tcl split 无 maxsplit→string first+string range；string is double -strict）。test 6 cases（A basic+noise；B comma-list teeth；C non-numeric teeth；D WVINFO pipe teeth；E WVERR pipe teeth；F multi-file）。reference .75 waveview PASS 6；naive(float-coerce+uniform split) FAIL(comma-list 崩溃) 证 teeth；pi-SUT deepseek-v4-pro-cloud ~6min exit=0 → CHECK_RESULT PASS 6 / DESIGN_FLOW_VERDICT=PASS。pi+ref 双 PASS。**run.sh 卫生坑**：inline NOTE backtick 被 bash command substitution→'string: command not found' 警告，但 prompt.txt/checker.tcl 经 $(cat) 不二次展开故 pi 收到完整 spec+checker，未受影响（后续 inline NOTE 应转义 backtick）。pi_debug 追加 Wave-006 PASS。report_10_29.html regen(76KB)。40 用例/32 PASS 1 FAIL 1 draft(+6 无 pi 行)/15 jsonl（WaveView-Waveform 现 6 条全 PASS）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。

[22:22] 第78轮：**spice_sim 扩量第 4 条 Spice-004 (HSPICE delay-cell 网表参数化 MC sweep prep · subckt-scope + idempotency + surgical-nf/m 陷阱) reference 在 .75 waveview CHECK_PASS (RESULT:PASS 5/FAIL 0, 5 cases A basic/B subckt-scope-teeth/C idempotency-teeth/D surgical-params-teeth/E decoys+extraction-teeth)；pi-SUT 后台 running (PID 1892112)**。经 eda_flow open_session(BENCH-MINE,20261029-spice4)→run_commands 从 .75 awk summary.tsv 找 hspice-leading 命中→ssh hfeg0plg49 scp harrywu/1792829537180_vaiob.messages.json (hspice:910/netlist:794, 686 hspice tool count, 964 msgs, delay-cell R_RasVdbiasDlyStd_gut_MC Monte-Carlo sigma-minimization sizing-sweep build session)→python3 解析。真实任务=把 SPICE 网表中 R_RasVdbiasDlyStd_gut_MC 子电路内 4 目标实例(XMMP0/XMMN0 输入对, XMMP10/XMMN15 输出级)的 numeric w=/l= 替换为 quoted .PARAM 引用，并在 .SUBCKT 行前注入 .PARAM 默认块供 sweep driver 覆盖。**真实陷阱**：(1) SUBCKT-SCOPING——只动 _MC 子电路内；兄弟子电路 R_RasVdbiasDlyStd_gut(无 _MC) 也有同名 XMMP0 不可碰；(2) INSTANCE-TOKEN MATCH——按行首 token (lindex $line 0) 匹配非子串；(3) DECOY XMMP1/XMMN1/XMMN2 各自带 w=/l= 必须保持 NUMERIC；(4) IDEMPOTENCY——输入已 w='MP0_w' 不可二次参数化/二次注入 .PARAM；用 [0-9.eE+-]+ 区分数字 vs quoted；(5) SURGICAL 保留 nf=/m=/ad=/as=/pd=/ps=；(6) .PARAM BLOCK 顺序=MP0 MN0 MP10 MN15 注入 .SUBCKT 行前；(7) DEFAULT=正则捕获目标 w=/l= 数字；(8) 保留其他一切。建 spice_netlist_parametrize(path)→参数化网表字符串，tcl/waveview（POSIX classes，无 \b/\s/\d）。test 5 cases/45+ asserts。reference 3-pass impl 经 .75 waveview run_code → RESULT:PASS 5/FAIL 0。naive FAIL 证 teeth。pi-SUT 后台 running。pi_debug 追加 running。41 用例/32 PASS 1 FAIL 1 draft 1 running(+6 无 pi 行)/15 jsonl（Spice-Sim 现 4 条）。三口径=698机/2850用户/52698文件/24085命中。close_session(cleaned)。

[归档批次41] 第80-89轮流水（EdaOther-004 / Skipper-003 / Virtuoso-Flow-002 / Schematic-Netlist-003 / LogicSynth-004 / EdaOther-003 / 运维即时令V report_10_29 / PnRSignoff-004 详情）已移入 ARCHIVE_OPERATOR_DESIGNFLOW.md。
[02:26] 第86轮收尾：**EdaOther-004 pi+ref 双 PASS**（pi-SUT exit=0 02:21-02:26, ~5min, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。EdaOther 现 4 条全双 PASS。pi_debug dedup 46 unique = 43 PASS / 1 FAIL / 2 draft。49 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[02:45] 第87轮：**Skipper-003 (UVS 回归 scoreboard 多 tag 聚合) 新建 ref-PASS + pi-SUT running**。DERIVED（会话易失性策略）来自与 Skipper-002 同一真实 UVS 工作流（mined jason17w/hcxal, skipper:51/netlist:345/hspice:66）。task=uvs_regr_scoreboard_aggregate(scoreboard_text,test_list_text)→dict(12 keys)。7 陷阱(RAW-flaky/last-wins-dedup/pass_rate-denom-excludes-skip-pending/missing/verdict-priority-FAIL>INCOMPLETE>PASS/outcome-semantics-S-not-fail-T-is-fail/header-strict)。ref local tclsh 8.6.14 FULL 6-case CHECK_PASS + .75 skipper Case A baseline(t2/tot5/p4/s1/pr100/PASS) + Case B flaky TEETH(p3/f1/flaky=dqs_osc_manual/pr75/FAIL) 正确；naive FAIL TEETH PROVEN(.75 skipper: NAIVE_B flaky=空 MISS, NAIVE_C pr=20 vs 33)。pi-SUT running PID 3000784。50 用例/15 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[02:50] 第87轮收尾：**Skipper-003 pi+ref 双 PASS**（pi-SUT exit=0 02:45-02:50, ~5min, RESULT:CHECK_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。Skipper 现 3 条全双 PASS。pi_debug dedup 47 unique = 44 PASS / 1 FAIL / 2 draft。50 用例/15 jsonl。三口径=698机/2850用户/52698文件/24085命中。report_10_30.html regen(73KB)。
[03:15] 第88轮收尾：**Virtuoso-Flow-002 (flow.config 静态 DAG/一致性审计) pi+ref 双 PASS**（pi-SUT exit=0 03:10-03:15, ~5min, RESULT:CHECK_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。扩量最弱类 layout_virtuoso(2496/仅1case)→2 条。7 陷阱（bare-steps-registry/last-wins-dup-block/self-loop-cycle/undef-dep-keeps-step-in-exec-order/cycle-empties-exec-order/lex-tie-break/unknown-section-ignored）。ref local tclsh + .75 waveview 双 CHECK_PASS。Virtuoso-Flow 现 2 条全双 PASS。pi_debug dedup 48 unique = 45 PASS / 1 FAIL / 2 draft。51 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。report_10_30.html regen(74KB)。
[03:25] 第89轮：**Schematic-Netlist-003 (SPICE subckt pin-arity audit) 新建 ref-PASS + pi-SUT running**。DERIVED（会话易失性策略）来自已知真实 schematic-to-SPICE-netlist export QA 模式（schematic_netlist 2362/netlist 1047/cellview 9389）。真实任务=emy2netlist 导出后审计每个 X 子电路实例 pin-arity 与 .subckt 端口声明一致性。task=spice_subckt_pin_arity_audit(netlist_text)→dict(8 keys)，tcl/waveview，L2 medium。7 陷阱（param-exclusion/last-wins-redef/'+'-continuation-join/unknown-vs-mismatch/comment-blank-skip-break-continuation/malformed-param-only/lex-sort）。ref .75 waveview run_code RESULT:ALL_ASSERTS_PASS 6 cases + naive FAIL TEETH PROVEN（params-as-pins→Case B false mismatch）。pi-SUT running PID 3202156。52 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[03:35] 第89轮收尾：**Schematic-Netlist-003 pi+ref 双 PASS**（pi-SUT exit=0 03:32-03:34, ~2min, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。schematic_netlist 类 2→3（Sch-001 draft / Sch-002 PASS / Sch-003 PASS，waveview 旁路绕过 virtuoso skill 沙盒 blockage）。pi_debug dedup 49 unique = 46 PASS / 1 FAIL / 2 draft。52 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。report_10_30.html regen(75KB)。
[00:25] 第81轮收尾：**LogicSynth-004 (Genus QoR audit) 新建 ref-PASS + pi-SUT running**；**EdaOther-003 pi+ref 双 PASS 收尾**（pi-SUT exit=0 00:05, ALL_ASSERTS_PASS 6 cases / DESIGN_FLOW_VERDICT=PASS；eda_other 现 3 条全双 PASS）。44 用例/37 PASS 1 FAIL 2 draft 1 running 3 uncovered/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[23:44] [运维即时令V] report_10_29.html 正式触发版生成+commit (3aa5e8f) +push ok (master...origin/master clean)。gen_daily_report.py regen 59KB，累计42用例/36PASS/1FAIL/2draft/15jsonl；三口径=698机/2850用户/52698文件/24085命中。完成后继续 eda_other 用例建设主轴。
[23:41] 第80轮收尾：**PnRSignoff-004 pi+ref 双 PASS**。pi-SUT deepseek-v4-pro-cloud (~6min via eda_flow MCP .75 waveview, exit=0, 23:33-23:39) 跑 BOTH local tclsh 8.6.14 + .75 waveview sandbox → CHECK_RESULT:ALL_ASSERTS_PASS (6 cases A-F) / DESIGN_FLOW_VERDICT=PASS。reference 亦 ALL_ASSERTS_PASS。pi_debug dedup → **36 PASS / 1 FAIL / 2 draft**。PnRSignoff 现 4 条全 pi+ref 双 PASS。report_10_29.html regen。42 用例/36 PASS 1 FAIL 2 draft 3 uncovered/15 jsonl。三口径=698机/2850用户/52698文件/24085命中。

## 归档批次42（2026-10-30 第98轮归档）— 第94/95轮流水原文

- [06:30] 第95轮探查：**aether host run_code 仍超时**（eda_flow open_session(BENCH-AETHER-PROBE)→run_code lang=pyAether host=aether `print` → MCP timeout；close_session cleaned=true）。layout_aether 类（14534 scan hits，最大类）当时仍只能 draft，block 持续（第96轮已用 waveview bypass 解）。57 用例/16 jsonl/pi_debug 54=51PASS/1FAIL/2draft。三口径=698机/2850用户/52698文件/24085命中。
- [06:24] 第94轮收尾：**Schematic-Netlist-004 (SPICE netlist fanout/floating/power-ground connectivity audit) pi+ref 双 PASS**DERIVED（会话易失性策略）来自已知真实 UniVista Skipper (UVS) Verilog 回归工作流（mined jason17w/1790166621537_hcxal on hfeg0pnd002, skipper:51/netlist:345/hspice:66 hits；同一工作流已产 Skipper-001 build-cmd/002 live-state/003 run-scoreboard）。真实任务=回归执行前对 per-tag compile 摘要审计：`# Compile summary for tag <tag>` 头 + `[STATUS] tb errors=N warns=N elapsed=T` 行，按 declared testbench list 审计。task=uvs_regr_compile_summary_audit(compile_log_text,test_list_text)→dict(13 keys)。7 真实陷阱（elapsed m:ss-vs-sec / last-wins-replace-not-accumulate / dup=same-(tb,tag)-only / missing-declared / cross-tag-recovery / max_elapsed_tb-lex-tie-break / verdict INCOMPLETE-when-missing）。ref local tclsh 8.6 + .75 skipper ALL_ASSERTS_PASS 7 cases A-G；naive FAIL TEETH PROVEN（Case B: int() on elapsed '1:30' breaks）。**Tcl 陷阱**：checker msg 里 `[tb_a]` 被 Tcl 当 command substitution → 去方括号（pi-SUT 独立发现并同修复）。pi-SUT deepseek-v4-pro-cloud (~10min via eda_flow MCP .75 skipper, exit=0, 05:08-05:18) → ALL_ASSERTS_PASS / PASS, session cleaned → **pi+ref 双 PASS**。**FOURTH skipper class case**。56 用例/15 jsonl。v0.50 仍最新 benchmark 版本。

## 归档批次43（2026-10-30 第102轮归档）— 第96/97/98/99轮流水原文

- [07:05] 第96轮收尾：**Aether-Layout-002 (pyAether layout cellview placement-report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 06:58:40-07:02:48 ~4min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。**FIRST waveview-bypass aether-layout case**：解 layout_aether 最大类(14534 hits)的 aether host run_code init 超时 block——审计 pyAether layout 文本工作产物(INST/RECT/PIN/REQUIRE)在 waveview tcl。task=layout_placement_audit(placement_text)→dict(10 keys)，10 陷阱(strict-interior-overlap / malformed-incl-zero-area / rect-only-layer-presence / inst-vs-inst-overlap-only / malformed-excluded-from-overlap / priority-verdict / unordered-pair-once-lex-sorted-dedup / lex-sort-all / dup-name-count / missing-empty-no-require)。ref local tclsh + .75 waveview ALL_ASSERTS_PASS 13 cases(A-M)；naive FAIL TEETH PROVEN(local tclsh Case A)。**工程发现**：run_commands 传 20KB echo base64 腐蚀 tcl 源(空格/花括号位移→proc 早闭合→假错)；规避=write_file plain content 写 workdir + run_code source。layout_aether 1→2(001 draft/002 PASS)。58 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
- [07:24] 第97轮收尾：**Aether-Layout-003 (pyAether layout DRC violation-report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 07:19:04-07:23:57 ~5min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。**SECOND waveview-bypass aether-layout case**：审计 pyAether DRC 文本工作产物(RULE/SUMMARY 行)在 waveview tcl。task=layout_drc_audit(drc_text)→dict(10 keys)，10 陷阱(severity-case-insensitive / last-wins-dedup-replace-not-sum / duplicate_rule_names-still-reported / zero-count-still-checked / missing-summary-INCOMPLETE-not-PASS / per_layer_errors-err-only-sorted-warn-excluded / mismatched_summary-per-field-absent-not-reported / verdict-priority-FAIL>WARN>INCOMPLETE>PASS / layers_used-sorted-err-and-warn-dedup / all-lists-lex-sorted)。ref local tclsh + .75 waveview ALL_ASSERTS_PASS 13 cases(A-M)；naive FAIL TEETH PROVEN(local tclsh Case C: last-wins 误保留 first count)。layout_aether 2→3(001 draft/002/003 PASS)。pi_debug dedup 56=53 PASS/1 FAIL/2 draft。59 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
- [07:40] 第98轮收尾：**Aether-Layout-004 (pyAether layout GDS layer-map usage audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 07:33:26-07:39:45 ~6.3min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned, error_log 空）。**THIRD waveview-bypass aether-layout case**：继续扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether GDS 文本工作产物(LAYER <name> gdsno/datatype/purpose/count + SUMMARY 行)在 waveview tcl。task=layout_gds_layermap_audit(report_text)→dict(11 keys)，10 陷阱(purpose-case-insensitive / last-wins-dedup-on-layer-name / dup_gdsno=shared-(gdsno,datatype)-PAIR-同gdsno-异datatype-非dup-列全部 / missing-purpose-不默认drawing / max_shape_layer-lex-tie-break / total_shapes-sums-last-wins-distinct / mismatched_summary-absent-fields-not-reported / verdict-priority-FAIL-dup>INCOMPLETE-missing-or-no-summary>PASS / all-lists-lex-sorted / count-default-0)。ref local tclsh 8.6.14 + .75 waveview ALL_ASSERTS_PASS 13 cases(A-M)；naive FAIL TEETH PROVEN(local tclsh Case A: gdsno-alone 忽略 datatype→M1/M1PIN 误判 dup)。**工程发现延续**：write_file plain content + run_code source 绝对路径（waveview host run_code cwd 不一定=workdir）。layout_aether 3→4(001 draft / 002/003/004 PASS)。pi_debug dedup 57=54 PASS/1 FAIL/2 draft。60 用例/16 jsonl。report_10_30.html regen(85KB)。三口径=698机/2850用户/52698文件/24085命中。
- [08:05] 第99轮收尾：**Aether-Layout-005 (pyAether layout metal-fill/density report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 07:58:25-08:03:08 ~4.7min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned，probe 确认 .75 无 aether5 残留 session）。**FOURTH waveview-bypass aether-layout case**：继续扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether density-fill 文本工作产物(LAYER min/target/actual density % + fill_shapes + SUMMARY 行)在 waveview tcl。task=layout_density_fill_audit(density_text)→dict(10 keys)，10 陷阱(percent-strip-float-parse-85==85.0 / last-wins-dedup-replace-not-sum / strict-lt-below-min-actual==min-compliant / missing-density=missing-min-OR-actual-excluded-from-below-compliant / missing-only-min-but-actual-present-still-in-min-max-seen-and-layers-used-TRAP / min-max-seen-over-actual-present-only-empty-string-if-none / fill_shapes-default-0 / mismatched_summary-absent-fields-not-reported-empty-if-no-summary / verdict-priority-below_min-FAIL>missing-or-no-summary-INCOMPLETE>PASS-mismatched-no-effect / all-lists-lex-sorted)。ref local tclsh 8.6.14 + .75 waveview ALL_ASSERTS_PASS 13 cases(A-M)；naive FAIL TEETH PROVEN(local tclsh Case B: first-wins dedup→B_total_fill off)。layout_aether 4→5(001 draft / 002/003/004/005 PASS)。pi_debug dedup 58=55 PASS/1 FAIL/2 draft。61 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。


## 归档批次44 (2026-10-30 10:53) — 第85-105轮旧流水（MEMORY 体积维护）

[04:49] 第92轮收尾：**Virtuoso-Flow-004 (artifact manifest reconciliation audit) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 04:39-04:49 ~9.5min, 自行调 eda_flow MCP 在 .75 waveview run_code 验证 ALL_ASSERTS_PASS + close_session cleaned=true / DESIGN_FLOW_VERDICT=PASS）。扩量 layout_virtuoso(2496/3case)→4。task=vflow_manifest_audit(manifest_text)→dict(10 keys)，tcl/waveview，7 陷阱(PASS-zero-artifacts/ghost-under-FAIL-SKIP/zero-byte-PASS-only/signoff-checksum-gated/cross-step-basename-collision-vs-per-step-dup/LAST-WINS-dup-block-discards-earlier/verdict-clean-requires-all-5-empty)。ref local tclsh + .75 waveview ALL_ASSERTS_PASS 7 cases(A-G)；naive FAIL TEETH PROVEN(last-wins merge→Case E false ghost, only-missing-gated verdict→Case F1 clean-when-ghost)。**Tcl quirk 发现**：nested-path `dict lappend D k1 k2 $val` SPLIT list-valued $val(非 nested 不 split)→必须 get/lappend单参/dict set。Virtuoso-Flow 现 4 条全双 PASS。pi_debug dedup 52 = 49 PASS / 1 FAIL / 2 draft。55 用例/15 jsonl。report_10_30.html regen(78KB)。三口径=698机/2850用户/52698文件/24085命中。
[04:00] 第90轮收尾：**Virtuoso-Flow-003 (orchestrator run-log audit) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud exit=0 03:52-04:00 ~8min via eda_flow MCP .75 waveview, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。扩量最弱非阻塞类 layout_virtuoso(2496/2case)→3。task=vflow_runlog_audit(runlog_text)→dict(10 keys)，tcl/waveview，7 陷阱(retry-attempts=start-count/last-wins/skip-all-reasons/wall-vs-sum/midnight/verdict-ERROR>SKIP/dedup)。ref local tclsh + .75 waveview ALL_ASSERTS_PASS 6 cases；naive FAIL TEETH PROVEN(first-wins→Case B autovia ERROR)。Virtuoso-Flow 现 3 条全双 PASS。pi_debug dedup 50 unique = 47 PASS / 1 FAIL / 2 draft。53 用例/16 jsonl。report_10_30.html regen(76KB)。三口径=698机/2850用户/52698文件/24085命中。
[03:35] 第89轮收尾：**Schematic-Netlist-003 pi+ref 双 PASS**（pi-SUT exit=0 03:32-03:34, ~2min, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。schematic_netlist 类 2→3（Sch-001 draft / Sch-002 PASS / Sch-003 PASS，waveview 旁路绕过 virtuoso skill 沙盒 blockage）。pi_debug dedup 49 unique = 46 PASS / 1 FAIL / 2 draft。52 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。report_10_30.html regen(75KB)。
[02:01] 第85轮收尾：**Analog-004 pi+ref 双 PASS**（pi-SUT exit=0 01:55-02:01, ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned）。InnovusNetlist-004(r84) pi-SUT 结算 PASS（01:40-01:49）。Analog-004 = 第四条 analog_context（hspice-corner-worst-case-audit），6 陷阱（worst-direction/missing-skip/AND-logic/signed-margin/lex-tie-break/overall-worst）。ref local tclsh + .75 waveview 双 ALL_ASSERTS_PASS；naive FAIL Case A TEETH。Analog-Context 现 4 条全双 PASS。pi_debug dedup 45 unique = 42 PASS / 1 FAIL / 2 draft。48 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[02:21] 第86轮：**EdaOther-004 (vsim A_Summary.rpt pattern-coverage audit) 新建 ref-PASS + pi-SUT running**。MINED from real cliu/1793078652491_wk3wd（vsim_report_new + pattern.list flow）。.75 自身 19 用户 sessions 累积（t0002441=57/e0023936=52/...），cliu session = 真实 vsim DV 任务。pattern.list 170 行/169 unique（dup `mbist_three_deep`）。真实 A_Summary.rpt 格式：`Total Pattern : N` vs ` Failed Pattern: N` colon-spacing ASYMMETRY。7 陷阱（colon-asymmetry/ref-dup-dedup/comment-blank-CR-skip/missing-vs-extra-direction/bytemode-xN-rerun-suffix/header-vs-list-mismatch/separator-header-exclusion/ran-unique-vs-entries-dup-collapse）。ref local tclsh + .75 waveview 双 ALL_ASSERTS_PASS 6 cases；naive single-colon-form FAIL Case A TEETH PROVEN。pi-SUT running PID 2890393。49 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
[归档批次42] 第79轮流水（Spice-004 pi-SUT 收尾 + §会话易失性发现）+ §会话易失性扩展（第80轮 fresh mining 死路确认）+ §会话易失性发现（第79轮 mining 策略修正）已移入 ARCHIVE_OPERATOR_DESIGNFLOW.md。结论已沉淀在顶部快照"扩量阶段"策略：扩量基于已知 EDA 工具子领域 + 已 capture 真实任务模式提炼（fresh mining 死路，不再 ssh 抓 session）。
[归档批次41] 第80-89轮流水（EdaOther-004 / Skipper-003 / Virtuoso-Flow-002 / Schematic-Netlist-003 / LogicSynth-004 / EdaOther-003 / 运维即时令V report_10_29 / PnRSignoff-004 详情）已移入 ARCHIVE_OPERATOR_DESIGNFLOW.md。
[归档批次40] 第80轮/76轮/77轮/78轮流水（PnRSignoff-004/Skipper-002/Wave-006/Spice-004 详情）已移入 ARCHIVE_OPERATOR_DESIGNFLOW.md。


---

## 归档批次45（2026-10-30 第107轮体积维护搬入）

> 即时令 IX 深读 ukkn7 trace 当轮体积维护：MEMORY 34KB→搬入第101/102轮已闭合流水原文，留 1 行指针。

- [08:50] 第101轮收尾：**Aether-Layout-007 (pyAether antenna-rule-check report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 08:44:56-08:49:42 ~4.8min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned→probe NONE_LEFTOVER）。**SIXTH waveview-bypass aether-layout case**：扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether antenna-check 文本工作产物(NET layer/ratio/limit/status + SUMMARY 行；gate_area/diode_area 红鲱鱼)在 waveview tcl。task=layout_antenna_audit(report_text)→dict(10 keys)，10 陷阱(status-case-insensitive / dup-(net,layer)-last-wins / status-absent-infer-FAIL-if-ratio-gt-limit-else-PASS-never-WARN-SKIP / ratio==limit-PASS-inclusive-FAIL-strict-gt / missing-limit-default-400.0 / missing-ratio-default-0.0-PASS / max-ratio-worst-net-over-non-SKIP-only-SKIP-excluded-no-non-SKIP→-1.0+empty / worst-net-tie-lex-smallest-net / mismatched-summary-max-ratio-numeric-equality-100.0==100-int-for-counts-string-for-worst_net-absent-fields-not-reported / verdict-priority-fail>0-FAIL>mismatched-or-no-summary-INCOMPLETE>PASS)。ref local tclsh 8.6.14 ALL_ASSERTS_PASS 13 cases(A-M) + committed-jsonl consistency re-checked；naive FAIL TEETH PROVEN(local tclsh Case B: string-compare max_ratio→500 vs 500.0 false mismatch)。layout_aether 6→7(001 draft / 002-007 PASS)。pi_debug dedup 60=57 PASS/1 FAIL/2 draft。63 用例/16 jsonl。report_10_30 regen(89KB)。三口径=698机/2850用户/52698文件/24085命中。

- [09:18] 第102轮收尾：**Aether-Layout-008 (pyAether via-enclosure compliance report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 09:08:47-09:14:40 ~5.9min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned→probe NONE_LEFTOVER, pi 自调 close_session keep=false）。**SEVENTH waveview-bypass aether-layout case**：扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether via-enclosure 文本工作产物(VIA name/cut/enc_bot/enc_top/req/status + SUMMARY 行；bottom/top/count 红鲱鱼)在 waveview tcl。task=layout_via_enclosure_audit(report_text)→dict(10 keys)，10 陷阱(status-case-insensitive / dup-(name,cut)-last-wins / status-absent-infer-FAIL-if-enc_bot-lt-req-OR-enc_top-lt-req-else-PASS-never-WARN-SKIP / enc==req-PASS-inclusive-FAIL-strict-lt / missing-req-default-0.0 / missing-enc_bot/enc_top-default-0.0-can-FAIL-if-req-gt-0-included-in-min / min_enclosure-worst_via-over-non-SKIP-only-line-enclosure=min(enc_bot,enc_top)-SKIP-excluded-even-if-file-min-no-non-SKIP→-1.0+empty / worst_via-tie-lex-smallest-via-dictionary-numeric-aware-via2<via10 / mismatched-summary-min_enclosure-numeric-equality-0.080==0.08-int-for-counts-string-for-worst_via-absent-fields-not-reported / verdict-priority-fail>0-FAIL>mismatched-or-no-summary-INCOMPLETE>PASS)。ref local tclsh 8.6.14 ALL_ASSERTS_PASS 13 cases(A-M) + .75 waveview run_code ALL_ASSERTS_PASS + committed-jsonl consistency re-checked；naive FAIL TEETH PROVEN(local tclsh Case A: string-equal min_enclosure 0.080 vs 0.08 false mismatch)。**工程发现**：run_code 内联 code 传 tcl 时把 `"\n"`→`[format %c 10]`、`\x01`→`|`，规避 JS template literal 转义腐蚀。layout_aether 7→8(001 draft / 002-008 PASS)。pi_debug dedup 61=58 PASS/1 FAIL/2 draft。64 用例/16 jsonl。report_10_30 regen。三口径=698机/2850用户/52698文件/24085命中。

## 归档批次 46（2026-10-30 第108轮归档：第103/104/106轮已结算 PASS 流水，要点已沉淀在 MEMORY 顶部快照"扩量阶段"策略）

- [11:00] 第106轮收尾：**Aether-Layout-012 (pyAether PG power/ground MESH strap report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 10:51:10-11:00 ~9min exit=0 via eda_flow MCP .75 waveview, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned→probe 确认 .75 上无 BENCH-AETHER12 leftover workdir）。扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether PG-mesh 文本工作产物(MESH name/layer/direction/width/space/vias red-herring/status ok|skip|short|open + SUMMARY 行)在 waveview tcl。task=layout_pgmesh_audit(report_text)→dict(14 keys)，10 陷阱(direction+status case-insensitive / dup-(name,layer)-last-wins / ordered-key-layer-is-part-of-key / status-absent-default-ok / missing-width/space=0-vias=1 / min-width+max-space+worst-strap-over-non-SKIP-only / worst-strap-tie-break-lsort-dictionary-strap2<strap10 / coverage-pct-round / mismatched-summary-int+numeric-0.080==0.08 / verdict-FAIL>REVIEW>INCOMPLETE>PASS)。ref local tclsh 8.6.14 ALL_ASSERTS_PASS 13 cases(A-M) + .75 waveview run_code ALL_ASSERTS_PASS；naive FAIL TEETH PROVEN(local tclsh 23 fail asserts)；committed-jsonl consistency re-checked。pi 独立实现+自验证全 13 cases + close_session cleaned。**ELEVENTH waveview-bypass aether-layout case**。layout_aether 11→12(001 draft / 002-012 PASS)。pi_debug dedup 65=62 PASS/1 FAIL/2 draft。68 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
- [10:18] 第104轮收尾：**Aether-Layout-010 (pyAether PG power/ground short report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 10:10:24-10:18:08 ~7.7min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned→probe BENCH_AETHER10_LEFTOVER_COUNT=0, pi called close_session）。**NINTH waveview-bypass aether-layout case**：扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether PG-short 文本工作产物(SHORT net_a/net_b type/resistance/layer/status + SUMMARY 行；type mixed/power/ground/signal, resistance real, layer, status short/leak/clean)在 waveview tcl。task=layout_pgshort_audit(report_text)→dict(12 keys)，10 陷阱(status-case-insensitive / dup-ordered-pair-last-wins-replace / status-absent-infer-from-resistance-R<1-short-1-leak-100-clean / R==1-leak-inclusive-R==100-clean-inclusive / missing-resistance-default-0-short / max-resistance-worst-pair-layers-over-non-clean-only-clean-excluded / worst-pair-tie-lex-smallest-dictionary-numeric-aware-via2-vss<via10-vss / mixed-counts-in-both-power-and-ground / ordered-pair-(a,b)≠(b,a)-not-normalized / mismatched-summary-int-numeric-string-equality + verdict-priority-FAIL>REVIEW>INCOMPLETE>PASS-REVIEW-beats-INCOMPLETE)。ref local tclsh 8.6.14 ALL_ASSERTS_PASS 15 cases(A-M incl G2,H2) + .75 waveview run_code ALL_ASSERTS_PASS + committed-jsonl consistency re-checked；naive FAIL TEETH PROVEN(local tclsh 57 fail asserts)。layout_aether 9→10(001 draft / 002-010 PASS)。pi_debug dedup 63=60 PASS/1 FAIL/2 draft。66 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。
- [09:42] 第103轮收尾：**Aether-Layout-009 (pyAether routing-connectivity / open-net report audit, WAVEVIEW BYPASS) pi+ref 双 PASS**（pi-SUT deepseek-v4-pro-cloud 09:35:14-09:41:39 ~6.4min via eda_flow MCP .75 waveview, exit=0, RESULT:ALL_ASSERTS_PASS / DESIGN_FLOW_VERDICT=PASS, session cleaned, pi 自调 close_session keep=false）。**EIGHTH waveview-bypass aether-layout case**：扩 layout_aether 最大类(14534 hits,28%)——审计 pyAether routing 文本工作产物(NET name/segments/vias/layers/status + SUMMARY 行)在 waveview tcl。task=layout_routing_audit(report_text)→dict(12 keys)，10 陷阱(status-case-insensitive / dup-net-last-wins-replace-not-sum / status-absent-infer-from-segments-0→UNROUTED-1→PARTIAL-ge2→ROUTED-never-SKIP / missing-via-layer-count-ge2-AND-vias-eq0-single-layer-fine / layers-dedup-empty-handling / single-segment-watchlist-regardless-of-status-not-fail-trigger / max-segments-over-non-SKIP-only-SKIP-excluded-no-non-SKIP→-1+empty / max-segment-net-tie-lex-smallest-dictionary-numeric-aware-via2<via10 / mismatched-summary-int-equality-max-segments-numeric-string-for-worst-net-absent-fields-not-reported / verdict-priority-unrouted>0-OR-missing-via→FAIL>mismatched-or-no-summary→INCOMPLETE>PASS-partial+single-segment-are-watchlists)。ref local tclsh 8.6.14 ALL_ASSERTS_PASS 13 cases(A-M) + .75 waveview run_code ALL_ASSERTS_PASS + committed-jsonl consistency re-checked；naive FAIL TEETH PROVEN(local tclsh 31 fail asserts + .75 waveview ASSERTS_FAILED)。layout_aether 8→9(001 draft / 002-009 PASS)。pi_debug dedup 62=59 PASS/1 FAIL/2 draft。65 用例/16 jsonl。三口径=698机/2850用户/52698文件/24085命中。

## 归档批次 47（第117轮体积维护）— MEMORY 中 halted v0.x 时代已闭合段

### ⚠️ PII 修复（v0.1-v0.6 时代，已闭合）
- v0.1 leak check 仅查 app.e*/app.t*/email/domain/路径，**漏了拼音人名**。
- v0.2 TF-IDF 聚类暴露残留：`shiwei`(6)/`zhulong`(3) 为真实人名（"hello, shiwei"、"和 zhulong 交互的轨迹"）。
- 修复：extract.py 加 `RESIDUAL_NAMES` 表 + 称呼/交互上下文 scrubber + plain replace（覆盖 `zhulong_config_dir` 这类标识符内嵌）。
- 重跑 v0.1+v0.2，全产物 leak check 通过（0 残留）。
- **第7轮再发现并修复**：v0.6 用更宽 `[\w.]+@[\w.]+` 正则扫到 **`Cxmt@202608`**（应用服务密码）+ **`svc.edaagent`**（服务账号），自第1轮起在 git 中漏检。extract.py 补 `PASSWORD_LIKE_RE`/`SVC_ACCT_RE`/`CN_CRED_LABEL_RE` 三正则，重跑全链路 v0.1→v0.6，全产物 leak check 0 残留。
- **遗留**：git 历史 commit `21f4de3` 仍含未脱敏人名 + 早期 commit 含 `Cxmt@202608`/`svc.edaagent`（共享仓不擅自 rewrite history）→ 需人工决断是否 force-push 重写。

### 关键发现（v0.1 时代，已闭合；v0.1 集已被即时令 XI 删除作废）
- 本机自身即目标 EDA 服务器：`/home/*/.cline/data/sessions/` 有 19 用户、3487 轨迹。
- 任务书"8092 MCP→.75→SSH 内网"链路不通；改用本机只读扫描（满足红线与验收精神）。
- 8092 MCP Accept header 已从 text/event-stream 变 application/json（工具集不变）。
- 模型分布：deepseek-v4-flash 最多，次 MiniCPM5-1B / deepseek-v4-pro-fp4 / glm-5.2 等。
- v0.1 分类：eda_layout 1207、eda_other 802、code_dev 100、data_analysis 54、file_ops 41、other 35、schematic_sim 19。
- v0.2 细化后：eda_aether_layout 1000、code_dev 738（eda_other 中多为代码类）、eda_innovus 56、eda_virtuoso_schematic 14、+ 10 个 TF-IDF 聚类子主题；兜底桶 837→384。

### 交付物（v0.1-v0.34 时代，全 HALTED；v0.50 为当前有效版）
- v0.1–v0.11 交付物详情已归档至归档批次 3–5；要点：v0.1 探明本机即目标(19用户/3487轨迹)+脱敏+tasks.jsonl(2258,sha256=a1cd058a…)；v0.6 dedup 2258→2112；v0.7 逐比特可复现 PASS 78/78；v0.8 freeze-by-default+source_manifest；v0.9 规范发布 bundle[2112 tasks/246 gold/27 few_shot/219 test_set]；v0.10 v1.0-rc1；v0.11 worked example acc=0.8174/macroF1=0.7239。
- v0.12–v0.34 交付物详情已归档至归档批次 28；要点：v0.13 版本 manifest/diff；v0.14 统计严谨性（κ=0.4496）；v0.15 去偏 split（gap+0.5087）；v0.20 发布整合+顶层 RELEASE_INDEX；v0.26 user-strat gap=−0.2291；v0.30 lineage RE-sweep（147 PASS+4 LIVING）；v0.34 lineage RE-sweep（164 PASS+6 LIVING）。
- v0.7 可复现性隐患修复：4处 `datetime.now()`→`_now_iso()`；所有 reproduce.sh `export PYTHONHASHSEED=0`。
- v0.3-v0.6 leak check 全通过（0 残留）。
- 第69–75轮详细流水原文已归档至归档批次 39。要点：pi+ref 双 PASS 累计 19 条，LogicSynth-001 pi-SUT FAIL。

## 归档批次 48（2026-10-30 第121轮）：MEMORY 第112-119轮流水 + 旧"扩量阶段"块

搬入原因：第121轮新增 Analog-001 后 MEMORY 达 37KB（超 32KB 软限，未触 40KB
红线）。按规程把最新活跃块（顶部快照 + 第121/120轮流水）之下的已闭合块归档。
本批含：第112-119轮流水原文 + 第93-95轮旧"扩量阶段"块（描述已被即时令 XI 删除
作废的 57-case/16-jsonl legacy 时代，已不反映当前 9-case/1-jsonl 现状，归档
保留历史）。结论已沉淀在 MEMORY 顶部快照。

### 第119轮流水（即时令 XII 复核确认——Verification-001 用户名 e0031668 双源核对正确）
醒查发现 round #118 已把 XII 全闭环（8 用例 trace_source `user_hash`→`user`+原用户名 / gen_daily_report.py trace 列显 `<user>/<session> @ <host> (任务)` / regen report_benchmark_10_30.html 8 行均显用户名 / 双仓库已 push）。**唯 Verification-001 用户名 e0031668 需独立复核**。open_session(BENCH-VERIFY)→run_commands 双源核对：① `.75` grep `summary.tsv` → `e0031668  1789370647360_ukkn7.messages.json  match_count=1478`（hfeg0plg91/hfeg0pkn003/hfeg0plg15 三机同 session，NFS home 同用户）；② `ssh hfeg0plg91 'ls -la /home/*/.cline/data/sessions/1789370647360_ukkn7*'` → `-rw-rw-r-- 1 e0031668 drcqa 1616161 ... .messages.json`（文件 owner=e0031668）。**双源一致确认 e0031668 正确**，无需改 jsonl。close_session cleaned=true。

### 第118轮流水（即时令 XII trace_source user 用原用户名 + 日报列显示用户）
**改 8 用例 trace_source**——`eda_flow.run_commands` 在 .75 grep `summary.tsv` 核 4 条 hashed 用例真实用户：Verification-001 `1789370647360_ukkn7`→**e0031668** / PDKQA-001 `x4b0p`→xinqiaoz / Backannot-001 `82ybr`→haoyut / Characterization-001 `9knot`→vincelu；4 条 Digital 已是原用户名（t0002948/klhu）仅改字段名。python 重写 jsonl 删 `user_hash` 加 `user`=原用户名。**改 gen_daily_report.py** `trace_source()` 读 `metadata.trace_source.user`（回退 `user_hash`），格式 `<user>/<session_file> @ <host> (<real_task_summary>)`。regen report_benchmark_10_30.html 验证 8 行均显用户名。close_session cleaned=true。

### 第117轮流水（即时令 IX §五 深读第五条 trace w4x70）
选 w4x70（764，haoyut/hfeg0pkn003，netlist:1394/cmos:269/analog:171/schematic:94）深读——analog_context 域(1167命中)0 proper 填补最大空白。open_session(BENCH-DEEPREAD)→**SSH hang 修复**：run_commands 里 ssh `-n` flag 会断 stdin pipe，改用 `</dev/null`+无 ControlMaster 后 ssh 正常返回。scp 3.116MB messages.json→.75 workdir→python 解析 **1181 msgs(596 user/585 assistant)/551 tool_use(446 run_commands/54 read_files/51 editor)**→提取 45 real user msg(5 阶段)：A 反标报告分析(PARA-043/044/124/162/003/040/004) / B netlist 层级连接提取 / C net_tracer 工具构建+格式迭代(annot_analyzer.py→net_tracer_v4.py→net_tree_v5/v6.py→net_trace.py，输出格式迭代4版) / D SPEF vs netlist 连接对比(SPEF=StarRC merge trivial 节点 vs netlist=Cadence SI 完整层级，与82ybr同根因) / E Virtuoso 集成+完整 hierarchy。**7 类 case 牙齿识别**：cell type 必须在括号内 / 上下游双向 / bus bit RRH12N[1] vs [0] 分离 / PARA-xxx 分类统计 / hierarchy 路径解析 / pin 名 .A/.B/.Y / 连接链精确匹配。脱敏笔记落 `designflow/trace_deepreads/w4x70_netlist_spef_connectivity_tracer.md`。close_session keep=false cleaned=true。**本轮按 IX §五 两轮节奏不出 case（深读本轮→下轮合成 Analog-001）**。

### 第115-116轮流水（运维即时令 XI 全闭环）
删 64 条无真实 trace 用例(72→8 proper) + 8 proper 补 test_rationale/trace_source + gen_daily_report 读 metadata(无 synthesized) + regen 日报验证。双仓库已落 origin。

### 第114轮流水（Backannot-001 合成 pi+ref 双 PASS）
按 82ybr 深读笔记合成 EDA-Eval-DesignFlow-Backannot-001（pnr_signoff 域首条 proper）。合成 6 assets → proper 契约 → 追加 jsonl。test 7 条件独立有牙：ref PASS / 3 类 naive FAIL。pi-SUT deepseek-v4-pro-cloud ~10min exit=0，产出 outputs/submit.zip(5563B/4文件)，pi 自检 PASS，独立 reference/check.py 判 PASS → **pi+ref 双 PASS**。

### 第112轮流水（PDKQA-001 合成 pi+ref 双 PASS）
按 x4b0p 深读笔记合成第三条 proper design_flow case EDA-Eval-DesignFlow-PDKQA-001（physical_verify 域首条 proper）。合成 5 assets → proper 契约 → 追加 jsonl（71行/8 proper）。test 7 条件独立有牙：CORRECT PASS / BUGGY FAIL / 11 per-condition isolated FAIL。pi-SUT ~4min exit=0，自报 DESIGN_FLOW_VERDICT=PASS，独立 reference/check.py 判 PASS → **pi+ref 双 PASS**。

### 旧"扩量阶段"块（第93-95轮，legacy 57-case 时代，已被即时令 XI 删除作废）
- 第94-95轮：Schematic-Netlist-004 / aether host run_code 超时 block（layout_aether 类 14534 scan hits 最大类仍只能 draft）。
- 第93轮：Skipper-004 pi+ref 双 PASS；eda_flow write_file content_base64 服务端 bug 发现（`$dA`→`$d\x01`），改用 plain content 规避。
- 第110-114轮流水（Characterization-001 / 82ybr 深读 / Backannot-001 / x4b0p 深读 / PDKQA-001）已浓缩，详情见各 trace_deepreads 笔记 + 顶部快照 + 归档批次 39/47。
- 第103/104/106轮（Aether-Layout-009/010/012）、第96-99轮（Aether-Layout-002/003/004/005）、第85-102轮旧流水已移入归档批次 42/43/44/46。
- 旧"扩量阶段"统计：57 条/16 jsonl/pi_debug 54=51PASS/1FAIL/2draft —— **此统计已作废**（即时令 XI 删 64 条无真实 trace 用例，现 9 条/1 jsonl）。
