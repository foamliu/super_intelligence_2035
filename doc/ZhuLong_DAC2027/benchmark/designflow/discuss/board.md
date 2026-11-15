# 讨论看板 · board.md

> **只由 shard A（召集人）维护**。其他 shard 🚫 **只读**。
> 协议见同目录 `README.md`。

---

## 当前状态（每次开/闭议题时更新这一行）

`OPEN: 1 · CLOSED: 5 · 最近更新: 2026-11-15 (r589 A 召集人落地 IrunSimDiagnose-001-v2 (C-A debug-Q&A 模板, v2 队列第 2 条) — P-006 B/C/D 仍无直接表态但 D grounded-extraction-tool (6 source-type + 判分牙齿五件套 + 7/15 prototype-proven + v2 6/8) 实质 = (C)/(A) 操作化, de facto 共识成立; v2 还原 debug-Q&A 形态交付 diagnosis_report.json only, check() 用 content-correctness(15) + evidence-verification(error.evidence.token 真实存在于 A sim.log) + listing cross-verif(stale=file/live=symlink) + B judge-self-check + 3-seed 给牙; k=19; 复用 v1 trace-faithful A/B 资产; v2 队列 2/28; 据 r588 模板继续推进, 除非 B/C/D 提反对+替代)`

---

## OPEN 议题

### P-006 v2 redo 的 check()-contract：pure-Q&A off_intent 案的「§4.2 subprocess-on-B / §4.9 anti-hardcode」根本张力 · 状态：**OPEN** · r586 (2026-11-15) · 召集人 A 开题
- **问题**：11-15 最高优先令要求把 28 条 off_intent 案「重做(v2)：还原为原始 Q&A/分析任务形态，check() 刭结构化答案/报告，满足 §4.2/4.3 牙齿」。但 v2 还原成 Q&A 形态后，**§4.1「check() 只跑 B」+ §4.2「subprocess 在 B 上执行候选脚本」+ §4.9「只 print 期望串必须 FAIL」三条同时不可满足**——这是本议题要各 shard 定夺的设计决策，定夺前不应批量产 28 条 v2（否则可能全需返工）。
- **张力根因**（逐条）：
  1. off_intent 案的用户意图 = **one-shot Q&A answer 关于固定输入 A**（如 LibPVT「列出这个 folder 的 PVT 表」、AsyncResetSyncRelease「异步复位同步释放电路是什么样的」、FloorplanTclAudit「解释一下这个脚本」）。用户要的是**答案/结论**，不是可复用工具。
  2. v2 还原 Q&A 形态 ⇒ 交付物 = 一份结构化答案/报告（JSON 或 md），**不是脚本**。
  3. 但 §4.1 要求 check()「只跑 B」（B 不进 SUT 沙箱）；§4.2 要求「subprocess 在 B 上执行候选**脚本**」——而 Q&A 交付物是静态报告，agent 从未见 B，无法对 B 产出答案 ⇒ **§4.2 字面不可满足**。
  4. §4.9 要求「只 print 期望串」假提交 FAIL。对固定输入 A 的 Q&A，一个硬编 A 金答案的 stub 与真分析 A 的正确答案**不可区分** ⇒ 若 check() 只判 A，§4.9 字面不可满足（这正是 §4.1「只跑 B」存在的理由：用 agent 没见过的 B 击败硬编 A）。
  5. 顶部令排除标准只剩两条（①无真实 trace ②写不出有牙 check）；「Q&A 合法」与「§4.2/4.9 全满足」对固定输入 A 的 Q&A **互相矛盾**。
- **与 7 borderline（r586 全 keep）的判据对照**（佐证张力仅限 pure-Q&A）：borderline 7 案用户动词=找出/对比/修改/交叉引用，交付物=**经 process 产出的结构化结果**（diff 树 / dep 路径 / xref 映射 / audit 清单 / patched 文件 / diag 检测），交付物**自然 B-可执行**（脚本跑在隐藏 B 的另一棵树/另一份 runcmd 上）⇒ §4.2/4.9 全满足，keep 成立。off_intent 28 案用户动词=列出/解释/分析/诊断/讲解，交付物=**关于固定 A 的答案**，无 process 可在 B 上重跑 ⇒ 张力成立。**判据一句话**：交付物是否「可在 agent 未见过的 B 上重跑/重用」？是 → keep produce-task；否 → 落入本议题。
- **三选项**（请各 shard 表态选一，或提替代）：
  - **(A) 放宽 §4.2/4.9 对 pure-Q&A 的字面要求，改用「evidence-citation verification」给牙**：check() 解析提交的 JSON 报告，断言①结论字段正确（≥8 条独立内容断言）②**证据定位可核验**（报告须引用 A 输入文件的具体 file:line/token，check() 重解析 A 输入独立验证引用为真，fabricated evidence FAIL）③ anti-stub negatives（empty / print-gold-without-evidence / wrong-conclusion 各自 FAIL 于 ①或②）。放弃 §4.1「只跑 B」与 §4.9「print 期望串」对 Q&A 的字面适用——以「证据可核验」替代「B-重跑」给牙。**弱点**：一个同时硬编金答案 + 真实证据引用的强 stub 能 PASS（但构造它 = 已做真分析，且 negative 库不构造这种 stub）。**优点**：任务形态最忠实用户 Q&A 意图。
  - **(B) v2 仍交付「答案报告 + 轻量抽取脚本」双件，check() 跑脚本于 B**：prompt 以 Q&A 口吻问答案（还原意图），但交付格式要求 submit.zip 含「答案 JSON + 产生该答案的 analysis 脚本」，check() 跑脚本于隐藏 B 验证泛化。**优点**：§4.2/4.9 全字面满足，牙最硬。**弱点**：交付物仍含脚本 ⇒ 与 v1 off_intent「合成成代码生成任务」**形态无实质差别**，v2 重做失去意义（等于 v1 换个 prompt 措辞）。
  - **(C) 按可牙性分流：能 evidence-verify 的走 (A)，不能的 retired**：对 28 案逐条判「答案是否含可独立核验的证据定位」。能（如 LibPVT 的 PVT 表可回溯 folder/file 名 token、IrunSimDiagnose 的根因可回溯 log 行号）→ (A) v2；不能（如 AsyncResetSyncRelease 纯概念问答、WaveviewModuleUpdate env-config 主观建议）→ 标 `retired`（jsonl 行保留，从通过率分母剔除），归入排除标准②「写不出有牙 check」。**优点**：既忠实 Q&A 意图又不降低判分门禁；与顶部令「唯一排除标准=无 trace / 无牙 check」一致。**弱点**：部分案下线，28 → 实际 v2 数 < 28。
- **召集人推荐：**(C) 分流。理由：(A) 单独用会系统性弱化 §4.9 对 Q&A 的适用，影响全 benchmark 判分门禁口径（不只 28 案）；(B) 使 v2 失去意义；(C) 既守住「有牙 check 才入库」红线，又对能 evidence-verify 的案忠实还原 Q&A 形态，对纯概念/env 主观建议案诚实下线（它们本就落在排除标准②）。预计 28 案中 (A)-类 v2 ≈ 15-20（debug-Q&A / 列表-Q&A 有可核验证据）、retired ≈ 8-13（concept-Q&A / env-config / 主观推荐）。
- **LibPVT 走 (C)-(A) 示例**（若 (C) 采纳，作为首条 v2 模板）：保留 v1 资产 folders.txt/filelist.txt/sample_lib_tt_header.txt（真实输入不变）；v2 prompt 仍 trace-faithful「请帮我列出一个表格，逻辑出这个folder中包含哪些PVT」+「以 pvt_report.json 提交结构化分析」；交付物 = pvt_report.json（**删 v1 的 pvt_parse.py 要求**）；check() ≥8 断言：①folder_count==12 ②widths=={25,30,35,40} ③vt_classes=={LVT,SVT,ULVT} ④lib_count==36 ⑤corners=={ff,tt,ss} ⑥ff V/T==0.825/0 ⑦tt V/T==0.75/85 ⑧ss V/T==0.675/125 ⑨每条 entry 含 filename + 可核验 evidence(folder/file token 真实存在于 A 输入) ⑩header nom_voltage/nom_temperature 印证 tt ⑪无 A 外其他硬编串泄漏 ⑫-⑮ B 变体……（B 变体如何用见下）。**B 变体处理**（(A) 下 B 不再「重跑」）：B = 同结构不同取值的另一份 folders/filelist（不同宽度/Vt/V-T），check() 对 B 的金答案独立重算；但 agent 只见 A ⇒ check() 不要求 agent 出 B 答案，而是把 B 用作**判分器自检**（确认判分逻辑非硬编 A）+ **determinism seed**。anti-hardcode 主要靠 ⑨ evidence-verification（硬编 A 金答案但 evidence 指错位的 stub FAIL）。
- **期望产出**：(1) 各 shard 表态选 (A)/(B)/(C)/替代；(2) 若 (C) 采纳，各 shard 对本域 off_intent 案逐条标 (A)-v2 / retired 并报数；(3) 定稿后 A 出 v2 模板（LibPVT）供各 shard 复用。
- **点名**：@A @B @C @D（本议题决定 28 条 A 域 v2 + 各 shard 若有同类 off_intent 的统一口径，影响全 benchmark Q&A 判分门禁）
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（task contract / judging stdlib-only）· `sections/5_analysis.tex`（Threats: task-form fidelity）· `sections/9_reproducibility.tex`（check contract）
- **A 域初报**（r586）：28 off_intent 全量已审（r584 13 + r585 15）；7 borderline r586 复审全 keep（retrieval/process B-可执行）；推荐 (C) 分流；LibPVT 拟作 (C)-(A) 首条 v2 模板（待共识后落地）。详见 `discuss/A.md` r586。

### P-005 私有资产逼出的保真度降级（private-asset-forced fidelity degradation）· 状态：**CLOSED** · r519 (2026-11-14)
- **r519 召集人闭合更新**（2026-11-14）：**P-005 正式 CLOSED**——论文 §2/§5/§9 落盘全部完成。§5 Threats 新增第八型「Asset-forced fidelity degradation」（8a-only-threat 采 C r556：intent-substitute ONLY，D WAVEVIEW 11 题实证 text-only baseline FAIL 证难度差；8b tool-mock 归 P-003 r392 mock-behavioral check mode 不重复列 threat）+ 分档报（A 档恢复版 vs B 档替身版）+ Lite set 按域区分（waveform 仅可恢复替身版 / layout mock fixture 可释放 / spice sanitized .lib copy）。§9 line 27 资产枚举扩 4 类（waveforms (FSDB) + eye-diagram plots + WaveView project environments / foundry model libraries .lib/.inc + sel_cond / project-private PDK paths /proj / live-license tool bridges Aether/Virtuoso/Calibre/WaveView）+ 降级披露句 + `asset_fidelity` 三值（original/synth_deck/text_sub）。§9 line 30 mitigations 增 (iv) 沙盒重生真图恢复路径（matplotlib / WaveView sx_dump_png，恢复 image-required 形态，no-VQA vs with-VQA 多模态通过率差可度量）。§2 Lite set releaseability 按域区分披露句。pdflatex 两遍 exit=0 / 0 undefined / 14p / main.pdf 重生成。**B r542 问责成立并本轮执行**：P-005 自 r515 收敛至 r542 跨 27 轮 0 落盘 stalled，根因 A 召集人未执行落盘（非讨论条件未满足），本轮 A 执行闭合。**asset_fidelity jsonl 侧回标是各 shard 渐进任务非 P-005 前置**（论文侧机制已就位）：A 280 条无降级可批量 original / B 76 / C 149 / D 11 分批回标（B r542 已承诺 B 本轮起做）。**r518 verilog-dominant gem 附带方法论修正**（P-002 CLOSED 后实证）：r482-r517「A 质量枯竭」是 strict-A-STRONG 过滤口径的属性非池属性，broad-filter（含 verilog/synopsys）仍挖出真 gem Lpddr5CovTermitFix-001（A.jsonl 279→280）；A 线选料默认切换 broad-filter。详见 `discuss/A.md` r519。
- **召集人裁决（A r511）**：**开 P-005**，第八型 selection-bias = 造题保真度偏差（trace 选对但私有波形/FSDB/WaveView 环境不可复刻逼出文本替身降级），层级异于前七型（选料/落库期）。裁决四点：(a) **分档报**——A 档（原意图恢复版 image-required）vs B 档（文本替身版）分开报通过率不混算（与 2026-10-31 A/B 双档令一致；WAVEVIEW α1/β9 基线 2B text-only FAIL 证难度差实质）；(b) **Lite set** 含可恢复题（图可沙盒重生，D r650 证 matplotlib/sx_dump_png 可行），仅排除不可恢复题，§2 line 86 releaseability 须披露 Lite set 域偏移；(c) §9 line 27 补「waveforms (FSDB), eye-diagram plots, WaveView project environments」+ 降级披露句 + 恢复路径（沙盒重生真图）；(d) §5 Threats 加第八型与第七型（D r646 cross-shard evaluated-set collision）并列；(e) **@各 shard 核查本域降级题占比**（grep `metadata.grade=="B"` + deepread「B-grade/synthesized」段）。**同步召集人裁决**：裁决 1「一 trace→一 case」lenient+cap 2 口径（distinct check + same_trace_group 标注 + ≤2/trace，pure-dup 必删）/ 裁决 2 key schema `id` 为新 case 规范主键存量 alias 保留冻结期不回溯迁移 / 裁决 3 keyword 域边界软优先级（spice→B/layout→C/waveform→D/verilog→A first-peek）+ D filter 收窄去 spice。详见 `discuss/A.md` r511。
- **问题**：当 trace 原意图依赖私有波形/FSDB/WaveView 环境/项目目录时，造题 agent 降级成文本/脚本替身（B-grade synthesized），稀释难度、绕过多模态/真跑能力考查。这是 selection-bias 第八型，与第五型 cross-domain-tool inflation / 第六型 sub-domain leak / 第七型 cross-shard evaluated-set collision 并列但层级不同（造题保真度 vs 选料/落库）。
- **背景**：D r650 WAVEVIEW α1 EyeApertureSelect-001 恢复实证——降级版=解析 .rep 写脚本可过，恢复版=看 PNG 读数，cline v3.0.51+2B text-only → FAIL（50s loop-abort）。D r651 β9 WaveMaxFind-001 同构→FAIL（22s）。11 题（α4+β7）全降级为 B-grade，根因统一=私有资产不可复刻。A r504 handoff 核对=11 题全 D/B 域（0 题 A 域）。
- **期望产出**：(1) 各 shard 降级题占比表（grade=B / 同源 deepread B-grade 标注）；(2) §5 Threats 第八型 + §9 资产类型补漏 + 降级披露 + 恢复路径；(3) §2 Lite set 域偏移披露 + 分档报通过率（A 档恢复版 vs B 档替身版）；(4) 裁决 1-3 落 §2/§9（same_trace_group+cap 2 / key alias 注 / keyword 软优先级）。
- **点名**：@A @B @C @D（各 shard 核查本域降级占比 + 表态分档报/Lite set）
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（line 21 unified contract / line 86 Lite set releaseability / line 88-89 domain balance / task-schema）/ `sections/5_analysis.tex`（Threats selection-bias 七+八型）/ `sections/9_reproducibility.tex`（line 27 资产类型 / line 30 roadmap iii 恢复路径）

### P-004 候选池 per-shard 排除口径 → 4-shard fresh 系统性高估 77-93% · 状态：**CLOSED** · r462 (2026-11-13)
- **r462 召集人闭合更新**（2026-11-13）：**P-004 正式 CLOSED**——两条 track 均闭环：(a) fresh-pool track CLOSED r444（论文披露 + §9 roadmap code-fix）；(b) evaluated-set near-dup 清理本轮 grep 实测全量完成：B-4（FinesimIgnoreGen-001/NetlistViewSpiceldSwap-001/LatchFFNetlistMatch-001/VsimEnvFileKeep-001 B.jsonl hits=0，B r473 执行属实）/ C-1（NetPathHL-001 C.jsonl exact hits=0）/ D-10（RegrCaseFilter/ABMatchPlacementCheck/SRAM6TSweep/CtleTranGen/SaSweepOpt/RasTbFinesimGen/VsimCleanupDisable D.jsonl hits=0，叠加 r566 的 3）/ A-0（r438 已闭环）。board r444「B-4 pending」标注 stale（写于 02:3x，B r473 05:2x 执行后未同步）。回 B r483 状态对齐请求：B r473 正确。candidates_mc10.tsv 腐蚀事故经 D r610（recount target=2882≈HEAD 2883）/ C r515（mc-matrix 从 summary.tsv 重生）/ A r462（本地 summary_1109.tsv 重算）三 shard 佐证降级为流程卫生（@ops 提醒各 agent 勿 git add candidates_mc10.tsv manual workaround 产物）。剩余 code-fix（`trace_ledger.py next` 4-shard 联合排除 + suffix-normalize）是 §9 roadmap(iii) 工程任务非讨论条件。详见 `discuss/A.md` r462。
- **r444 召集人闭合更新**（2026-11-13）：**fresh-pool track CLOSED by paper disclosure**——接受 C r475 方案 (a)，三 shard 实测（A 77.4% / B 83.7% / C 93.2% 跨 1105/1109 快照稳定）已充分支撑论文 §2/§5/§9 诚实披露，code-fix 是工程任务移交 §9 roadmap(iii) 落地（非讨论条件）。采纳 D r574「code-fix 正交必要」（解分母污染 + robustness，反对 B r465 绝对化），§9 roadmap 拆「dedup code-fix」与「质量枯竭」两条正交。采纳 B r467 characterization 根因分型（scan vocabulary blind spot + 交互式覆盖盲区，非 mined-out），§5 Threats 补覆盖边界。采纳 D r574 visible-input round-trip cond 为可选判分模式（非强制）。**新事故**：candidates_mc10.tsv 工作树 778 行 vs HEAD 2883 行（未提交删除 2105 行），manual 4-shard workaround fragile 的实证，支撑 code-fix robustness 论证；@ops 排查 02:11 regen 来源。**evaluated-set near-dup 清理仍 pending**：累计下线 D-10（已执行 3 + 待执行 7）/ C-1 / B-4 / A-0，\Ntasks 1191→1176（pending 各 shard 执行 + merge）。B-4 四连未执行（ops lag，@B 本轮即做）。详见 `discuss/A.md` r444。
- **r440 召集人续裁更新**（2026-11-12）：evaluated-set near-dup 清理近闭环——C-D 3 pair 已执行（D r566，D.jsonl 362→359）；task_id collision 续裁：RegrCaseFilter A 保留 D 下线 / **NetPathHL D 保留 C 下线（接受 C r471 自纠，反转 D r566）** / ABMatch C 保留 D 下线；B-D 11 pair 采信 B r461+D r566（B 下线 4 / D 下线 5 含 VsimCleanupDisable provisional）。**碰撞分型修正**：B-D 双向非 single-direction（B r461+C r471 证伪 r448），§5 Threats 须写「mislabel 双向/多向」非「D universal sink」。**累计下线 pending**：D-10（已执行 3 + 待执行 7）/ C-1 / B-4 / A-0，\Ntasks 1191→1176（pending 各 shard 执行 + merge）。**fresh-pool track 仍 OPEN**：`trace_ledger.py next` 4-shard 联合排除 code-fix 未落地（各 shard 手动 workaround），是 P-004 剩余闭合条件。详见 `discuss/A.md` r440。
- **问题**：各 shard 的 `trace_ledger.py --shard X next` 在排除时只用**自己 shard 的台账**（excl X-ledger），导致报的「fresh」对 4-shard 全局而言系统性高估——同一个 session 被 multiple shard 当 fresh 入池，引发选料撞车（dup-case 风险，污染通过率分母）+ deepread 预算浪费（peek 他 shard 已 reject 的 session）。三 shard top-N 交叉实测：A refined-A fresh 77.4% 实已在 BCD 台账（A r426）/ B top-245 83.7% 在 ACD 台账（B r448）/ C top-250 93.2% 在 ABD 台账（C r451+r459）——均落 77-93% 高位区间，跨三 shard 同构坐实。D 侧 top-N 未补，但 B/C 实测均证 D 是 universal sink（B overcount 72.2% 由 D 独占 / C overcount D-in-any 83.3%）。
- **背景**：A r426 提议（refined-A 337 fresh，∈BCD 261=77.4%，truly-4shard-fresh 76=22.6%）+ B r448 表态（top-245 covered 205=83.7%，D 独占 72.2%，B→D single-direction）+ C r451/r459 表态（top-250 covered 233=93.2%，D-in-any 83.3% 但 D 独占仅 36.1%，C→D 是 D 主导 + B-D 共享簇，非 B 的 single-direction）。碰撞结构分型：B→D single-direction / C→D D 主导+B-D 共享簇 / A→多向（gracew/jkxu/e0014566 跨域）。修法不应 one-size-fits-all：B 可用 B-D 双联优先（消 86.3%），C 需 4-shard 全联（碰撞跨 A/B/D 三方），A 需 4-shard 全联（多向交叉）。B r448 另拆出两层：dup-case risk（case-only cross，B 29.0% 自 r434 停滞）+ ledger-clutter（all-status cross，B 54.7%，他 shard 已 reject 仍被当 fresh）。
- **期望产出**：(1) `trace_ledger.py --shard X next` 的 USED_PATH 从「仅 X-ledger」改为「A+B+C+D 4-shard anchor 并集」的修法落地；(2) 论文 §2/appendix A 披露 fresh pool 须分两层——「dup-case risk（case-only cross）= X%」+「ledger-clutter（all-status cross）= Y%」；(3) 论文 §9 roadmap(iii) candidate pipeline 补「4-shard 联合 anchor 排除」修法。
- **点名**：@A @B @C @D（D 待补 top-N 同法交叉实测——D 是 universal sink，D 侧 overcount 分布会揭示 B-D/C-D 碰撞是否对称）
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（candidate selection / fresh pool 口径）· `sections/5_analysis.tex`（Threats frozen snapshot / selection bias）· `sections/9_reproducibility.tex`（roadmap iii candidate pipeline）· 附录 A（fresh pool 披露）
- **A 域初报**（r426）：refined-A fresh 337，∈BCD ledger 261（77.4%），truly-4shard-fresh 76（22.6%）。详情见 `discuss/A.md` r426 + r434。

### P-003 grounding depth 标注粒度：域级标签系统性错配 case 级真实 grounding demand · 状态：**CLOSED** · r392 (2026-11-11)
- **问题**：§5.2 的 grounding-depth bin 按 **domain** 分配（line 46「annotation we assign per domain」），但同一 domain 内 case 的真实 grounding demand（是否真 drive EDA 工具）方差极大。域级标签是否系统性错配 case 级真实 demand？若错配，§5.2 的 depth→Pass% 斜率与 §4 line 77「7.1× 域差距 → grounding depth 是因」headline 是否仍成立？
- **背景**：D r514 提议——waveform 域 IddMeasPostProcess（纯 stdlib CSV 后处理，实为 depth 1-2）被域标签拔到 depth 6；check.py 用 stdlib 判分（§2 line 104）构造上不验工具驱动 ⇒ depth 标签是 design-intent 非 verified behavior。A r390 独立坐实——A.jsonl 末 12 条全 L1-static（0 drive VCS/dc_shell/verdi），但 5/12 被域标签 verification 拔到 depth 5、4/12 被域标签 digital 拔到 depth 4，共 9/12 被上调 2-4 档。跨两域（A verification+digital、D waveform）同构。C r397 补充 third check mode (c) mock-pyAether behavioral——layout_aether gold 真 drive pyAether 但 check 用 mock，是「不依赖 live license 仍验工具驱动序列」的可行路径。
- **期望产出**：一份「按 shard 分域的 actual_tool_demand 分布表」（drive_eda_tool / parse_tool_output / pure_text_no_tool 占比 + 被域级 depth 标签上调档数分布），+ 论文 §5.2 改 case 级或 sub-bin 标注的可行性评估 + 重算后 depth→Pass% 是否仍单调。
- **点名**：@A @B @C @D
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（line 104 stdlib-only judging）· `sections/5_analysis.tex`（line 46 per-domain annotation, line 52-58 depth bin 分配, line 64 caption design choice）· `sections/4_experiments.tex`（line 77 7.1× 域差距 headline）
- **A 域初报**（r390）：12/12 近期 case actual_tool_demand = pure_text_no_tool / parse_tool_output，0/12 drive_eda_tool；9/12 被域级 depth 标签上调 2-4 档；A 域 12/12 L1 违反 TASK §5 L1≤30% 配额（根因 P-002 质量枯竭）。详情见 `discuss/A.md` r390。

### P-002 源池饱和与 benchmark 增长轨迹 · 状态：**CLOSED** · r380 (2026-11-11)
- **结论**：三模式框架（非二分）——① 数量枯竭(B spice_sim, fresh=0, 普查物理封顶) ② 质量枯竭(A digital/verification, fresh=302 但 r374-r380 32/32 fresh strict-clean weak, 强闸门筛掉 Q&A/env-dependent) ③ 资产可达性枯竭(D netlist/waveform, fresh=237 但 synthesized 37%↑, /proj 私有路径沙盒不可达)。**模式可跨域共存**（A 域同时含质量+资产两种）。论文 §5 line 140「Frozen snapshot, adding cases changes the mix」须分模式重写；§9 roadmap(iii) 拆「需新 trace 源」(B) / 「需放宽 produce-task 定义」(A) / 「需 NFS mount 或 sanitized asset copy」(D) 三条。3-shard 表态达标（A r377+r380 / B r393 / D r514），C 未出席。存档见 `rounds/r380_P-002.md`。
- **问题**：benchmark 的「代表性 / 可扩展性」受源池封顶的方式是统一的还是分域不同的？论文 §5 line 140「Frozen snapshot, adding cases changes the domain mix」是否需要按「数量枯竭 vs 质量枯竭」分模式重写？
- **背景**：B r393 实测 spice_sim 源池饱和（mc≥10 + spice-dominant 95 条全 ledgered, 0 fresh），指出 §2 line 86「SPICE dominates」是相对表述、第二大 evaluated 域已撞普查天花板。A r377 补充：A 域 mc≥10 fresh=302（数量未枯竭）但 r374-r376 三连轮 17/17 fresh strict-clean 候选全 weak（env-config/analysis-Q&A/doc-search/debug-Q&A/flow-driving），是「质量枯竭」非「数量枯竭」。两种模式对 §9 reproducibility roadmap(iii) 含义相反。
- **期望产出**：一份「按 shard 分域的源池状态表」（fresh 数 / fresh 中 clean-produce-task 占比 / 封顶模式分类），+ 论文 §5 Threats 与 §9 roadmap 的分模式改写建议。
- **点名**：@A @B @C @D
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/2_benchmark.tex`（line 86 SPICE dominates）· `sections/5_analysis.tex`（line 127-128, 134, 140 domain imbalance + frozen snapshot）· `sections/9_reproducibility.tex`（roadmap iii）· 附录 A（line 18, 42 census + threshold）

---

## CLOSED 议题

### P-003 grounding depth 标注粒度 · 状态：**CLOSED** · r392 (2026-11-11)
- **结论**：域级 depth 标签系统性错配 case 级真实 grounding demand，跨 3 域同构——A r390（12/12 近期 case actual_tool_demand = pure_text/parse，9/12 被域级标签上调 2-4 档）/ C r399（depth 7+ bin 内 physical_verify 9/9 gold 不 drive vs layout_aether 3/3 gold 真 drive，同 bin 取均值 2.9% 抹平对立）/ D r522（近 5 轮 5/5 pure_text + 5/5 synthesized，错配 +2.6 档均值）。**修法**：§5.2 改按 `actual_tool_demand(3) × asset_fidelity(2)` 双轴 sub-bin，depth 7+ 须拆 (a) drive-and-iterate / (b) parse-multi-MB-output 两个 sub-bin 分别报 Pass@1（C r399）；abstract/§4 的「7.1× 域差距 → grounding depth 是因」headline 须加限定「按 case 级 actual_tool_demand，非域级标签」。A r392 补 post-scan 增量新证（11/10+11/11 daily log 13 genuinely-new session，0/13 A-domain dominant）⇒ A 域 depth 4/5 bin 修复只能靠改标注，无法靠补 case。3-shard 门槛达（A+C+D），B 未出席（同 P-002）。存档见 `rounds/r392_P-003.md`。

### P-001 论文最大薄弱点 + 两周行动优先级 · 状态：**CLOSED** · r371 (2026-11-11)
- **问题**：`EDA-LiveFlow-Bench_ICML2027` 现在最容易被 ICML 审稿人打穿的一个环节是什么？只有两周的话，四个 shard 该按什么顺序补？
- **背景**：论文当前事实源 —— `\Ntasks`=1032（A203+B242+C289+D298）；冻结评测 696 runs（2026-11-09）；**Pass@1 = 10.0%（62/620 已判定，ERROR 70 不计分母）**。B 线已在 r<待填> 提交了一份研究组视角的建议（`reports/report_designflow_paper_next_steps_zh.html`），本议题要求其余 shard 就其结论表态或提出替代方案。
- **期望产出**：形成一份「按 shard 分工的两周行动清单」，每条含 负责人 / 工时 / 依赖。
- **点名**：@A @B @C @D
- **截止**：开启后 2 轮内表态（未表态记「未出席」）
- **论文参考节**：`sections/0_abstract.tex`（10.0% 论断）· `sections/4_experiments.tex`（696-run 主表）· `sections/5_analysis.tex`（失败归因）

---

## CLOSED 议题

### P-001 论文最大薄弱点 + 两周行动优先级 · 状态：**CLOSED** · r371 (2026-11-11)
- **结论**：四周收敛——§5.2 grounding-depth 因果叙事是最易被打穿环节（depth 手工标签 + 多域与实际交付件类型不符 + §5.3 tool-mix 自相矛盾 + pnr 支柱机制被自身 case falsify）。两周行动清单 5 项已分派（洗 ERROR ∥ depth-label 审计 ∥ §5.3 交叉表 → headline 诚实化 → 重画曲线）。存档见 `rounds/r371_P-001.md`。

---

## 出席记录

| 议题 | A | B | C | D |
|:--|:--|:--|:--|:--|
| P-001 | ✅ r371 | ✅ r389 | ✅ r388 | ✅ r510 |
| P-002 | ✅ r377+r380 | ✅ r393 | ❌ 未出席 | ✅ r514 |
| P-003 | ✅ r390+r392 | ⏳ 未出席 | ✅ r399 | ✅ r522+r518 |
| P-004 | ✅ r434+r438+r440 | ✅ r448+r461 | ✅ r451+r459+r467+r471 | ✅ r562+r566 |
| P-005 | ✅ r511+r515+r519 | ✅ r538+r542 | ✅ r556 | ✅ r650 |
| P-006 | ✅ r586 (开题) + r588 (落地模板) | ⏳ | ⏳ | ⏳ |

> ⏳ 未发言 · ✅ 已发言 · ➖ 被点名但该轮有 case 造题（不计缺席）

---

## 给召集人（A）的操作提示

1. **开题**：按 README §4 模板在本文件追加 `### P-00N`。
2. **汇总**：每轮结束扫一遍 `A/B/C/D.md` 的新增段落，更新上面的「出席记录」。
3. **关闭**：≥3 个 shard 表态 → 写 `rounds/r<轮次>_<topic>.md` 存档 → 在 CLOSED 区记一行结论。
4. **⚠️ 自身也要发言**：A 既召集也参与，别只维护看板不表态。
