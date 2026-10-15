# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `wo_sandbox` / `wo_selfexpl`（tab:main-ablation 这两行暂缓）· `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑） |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 🆕 运维指令 · 2026-10-15（二十二）— 🔁 S1 重测调整：跳过 omega_low，改重测 readback_binary【用户直令 · 最高优先】

> **用户令（2026-10-15）**：「为什么要跑 S1.omega_low，这个试验在 zhulong_results 不是已经测好填好了吗？反倒是 S1.readback_binary 标准差过大，需要重测。」

**① 停止 omega_low 重跑（跳过）**：
- omega_low legacy **82.8±1.0%（std=1.0，5-run 高度一致）** 已可信，**不必 fresh 重跑**。
- 当前 omega_low r1（PID 2616015）若已跑完则收该结果即可；若仍在跑则 kill，**取消后续 r2–r5 计划**。
- 采用 legacy **82.8±1.0%** 作为 omega_low 最终值（`zhulong_results.md` 标注来源＝legacy、std 可信）。

**② 重测 readback_binary**：
- legacy **66.2±16.1%** 的 std 过大（含 43.0% 离群 run），**需 fresh 5-run 重测**得到可靠 std。
- 切配置 `readback_binary`（READBACK=binary + 核心 4 工具 + full 锚点 phi=BUDGET0/LAGGED0），`stop.sh && start.sh` 重启后跑满 5 轮。

**③ readback_none**：legacy 73.3±2.2%（std=2.2）同样可信，**暂不重跑**（与 omega_low 同理）。

**④ 纪律**：判据(十三)不变（消融臂 Pass@1 任何值有效、timeout≤10 且无 infra 故障）；重测 binary 后把 fresh 结果替换 `zhulong_results.md` 旧 legacy 值并注明；commit 前缀 `zhulong S1:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（二十一）— 🧪 结合进展提「15 天窗口消融建议」· 中文 HTML· 用户直令 · 最高优先

> **用户令（2026-10-15）**：「安排 zhulong 结合试验进展，提出进一步消融试验的建议，写成 html 中文报告。现在到论文提交 deadline 还有 15 天。」

**① 背景**：距投稿 deadline **15 天**。当前进展：B 4/4、C1 4/4、C2 4/4 已 5/5 收口（12 臂），**S1 三臂为剩余主线**（`omega_low` r1 跑中，`readback_binary` / `readback_none` 未跑）。

**② 任务**：结合**当前试验进展 + 15 天时间约束**，提出「进一步消融试验」建议，写成中文 HTML 报告。每条建议给四要素：
- **动机**：回答论文哪个开放问题 / 审稿人或读者最可能质疑什么
- **做法 + 成本**：GPU/沙盒时延 + 墙钟估算
- **优先级**：15 天窗口内「必做 / 建议 / 可选」三档
- **编排**：与 S1 主线三臂的时间线如何错开（🚫 不与 S1 冲突）

**③ 候选方向（自己 judge、不限于此，结合论文审视报告 §8「仍缺数据」清单）**：
- 可回填但未做的消融（如 `wo_selfexpl` 自探索增益 82.1 vs 79.8、配对显著性检验 McNemar/paired bootstrap、gen-fail 机制深挖、错误分析基于 5-run 代表性 run 重做）
- 其它你认为 15 天内价值最大的补充实验

**④ 交付**：`doc/ZhuLong_DAC2027/reports/report_zhulong_next_ablation_plan_zh.html`（中文自包含），文末附「**15 天排期表**」（按天列出 S1 收尾 + 各项消融）。

**⑤ 纪律**：纯写作零 GPU，在 S1 评测空窗期做，🚫 不打断 S1 主线；数字与 `MEMORY_ZHULONG.md` 执行看板一致；commit 前缀 `zhulong plan:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-15（二十）— 📝 把最新评测结果填入 zhulong_results.md【用户直令 · 最高优先】

> **用户令（2026-10-15）**：「让 zhulong 把最新评测结果填入 zhulong_results.md。」

**① 填写对象**（`doc/ZhuLong_DAC2027/zhulong_results.md`，以下均为**已 5/5 收口的实测**，与 `MEMORY_ZHULONG.md` 执行看板逐字一致）：
1. **S2.phi_k1**：5/5 = **63.8 ± 3.2%**（r1 65.2 · r2 66.5 · r3 58.2 · r4 64.6 · r5 =? 从台账/日报取准确值），并补各轮 gen-fail（k=1 预算效应：35/30/39/34/?）。
2. **S2.phi_lagged**：5/5 = **73.0 ± 3.2%** [74.7, 76.6, 69.6, 69.6, 74.7]。
3. **更正 B.deepseek-v4-flash**：当前标 `⬜ 0/5` 系漏填 → 应 **✅ 5/5 = 16.7 ± 12.3%** [9.5, 10.1, 19.0, 7.6, 37.3]。

**② 填写规范**：
- 每个臂填 **mean ± std + 5 轮明细 + gen-fail 数**（与论文 `tab:phi-bound` 口径一致）。
- 把「S2 各臂仅有 1-shot 探路值」的旧注**删除/更新**（现在 k10/k3/k1/lagged 均已 5/5）。
- 同步把 `[ ]`（未完成复选框）改成 `[x]`（已完成）。

**③ 纪律**：数字从 `MEMORY_ZHULONG.md` 执行看板 / 当日 daily-memories 抄，🚫 凭印象；S1.omega_low 本论仍在跑、**不填**（只填已 5/5 的）；commit 前缀 `zhulong results:` · 任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-14（十九）— 🖨️ pdflatex 已装好，编译验证论文【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「zhulong 环境刚刚装好 pdflatex 了。」

**① 现在编译验证论文**（衔接十七的 P0+P1+P2 改稿）：进论文树 → `pdflatex` + `bibtex` + `pdflatex×2`，验证改稿后 `main.pdf` 编译成功。

**② 检查项（逐项报）**：
- **0 error** · **0 undefined reference / citation**；有 warning 也要记录（尤其 bib 缺 page/volume 类）。
- **页数变化**：改稿前 10 页 → 改稿后 ? 页。
- **overfull hbox**：新增与否；>20pt 的必须是 0（README 自检阈值）。

**③ 若编译报错**：先判断是**改稿引入**（如 label/引用、表格语法、`\cite` 错名）还是**环境**（缺 `.sty`/`.cls`/字体/`bibtex` 命令）。改稿引入的能修就修；环境缺件如实报并给等价替代（如缺 `texlive-latex-extra` 包名）。

**④ 纪律**：纯 CPU 编译，不占 GPU；`main.pdf` 编译产物按仓库惯例提交（`.tex`+`.bib` 必交，`.aux/.log` 不入库）；commit 前缀 `zhulong compile:`；任务书 >32KB 自滚归档。主线 `phi_k1 r3 regrade` 照常推进，编译在空窗期做。

### 🆕 运维指令 · 2026-10-14（十八）— 🧩 评测集全貌 + SKILL/Tcl 结果并入论文【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「告知 zhulong agent：它自己在测 PyAether，其它 agent 在同时测 SKILL 和 TCL，结果汇总到 `doc/ZhuLong_DAC2027/zhulong_results.md`。请 zhulong agent 在回填结果、刷新论文时，把 zhulong_results.md 中 SKILL/TCL 的结果带上。补充信息：EDA-Scripting-Bench 评测集中各语言 case 数，pyaether=158，skill=158，tcl=133，共计 449。」

**① 评测集全貌（EDA-Scripting-Bench，三语言）**：
| 语言 | case 数 |
|:--|:--|
| PyAether | 158 |
| SKILL | 158 |
| Tcl | 133 |
| **合计** | **449** |

**② 分工**：你（zhulong）测 **PyAether（158）**；**其它 agent 并行测 SKILL（158）+ Tcl（133）**。三路结果统一汇总到 `doc/ZhuLong_DAC2027/zhulong_results.md`。

**③ 要求（衔接指令十七「放行刷新论文」）**：
- 回填论文结果时，**以 `doc/ZhuLong_DAC2027/zhulong_results.md` 为汇总源**，把 **SKILL/Tcl 的结果一并带上**——论文评测口径从「PyAether 158」扩展为「**EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）**」。
- 具体落地：
  - 回填 **RQ3「SKILL/Tcl 切片」**（此前标 pending）——`zhulong_results.md` 中 SKILL/Tcl 已有结果即填，未齐则如实标 `partial`/`pending`。
  - 回填 intro/abstract 的 **「unified benchmark [X%]」**——按三语言 449 合并 Pass@1 重算（或显式标注口径）。
  - 全文凡涉及「PyAether-only」的主表/轴向，须改口径说明，🚫 避免「158」与「449」混用、避免读者误以为全榜只有 PyAether。
- 🚫 不得只报 PyAether 而继续忽略 SKILL/Tcl；🚫 不得凭印象编 SKILL/Tcl 数字——**只认 `zhulong_results.md` 现存数字**，未齐标 pending。

**④ 纪律**：每次唤醒刷新论文前先 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；数字与之逐字一致；缺数据标 pending 不编造；commit 前缀沿用 `zhulong paper-fix:`；评测主线不变（finish phi_k1 → phi_lagged → S1，改稿仍在空窗期做）。

### 🆕 运维指令 · 2026-10-14（十七）— ✍️ 放行改进论文（执行审视报告修改）【用户直令 · 最高优先】

> **用户令（2026-10-14）**：「zhulong agent 论文改进报告已审视/批准，请 zhulong agent 按此改进论文。」

**性质**：纯写作、零 GPU。**主线仍是评测**（当前 `phi_k1 r3` 跑中）——改稿只在空窗期做，🚫 绝不为改稿延迟/打断评测收割与切臂。

**① 撤销「只报不改」红线**：放行你修改论文 `.tex`，执行审视报告 `reports/report_zhulong_paper_review_zh.html` 的修改（按 §8 优先级 P0→P1→P2→P3）。

**② 🔴 P0 硬伤必须修（先改锚点、再批量同步，避免表文矛盾）**：
- **锚点全局替换** `84.8% → 82.1±3.0%`（`0_abstract` / `1_intro` / `8_conclusion` + 4 表锚点行：main-ablation Full、ablation-harness F、phi-bound unbounded、llm-comparison DeepSeek-V4-Pro）。
- **重算所有 Δ**：main-ablation（Full **+10.3pp**、wo_retrieval **−1.1pp**）· llm-comparison 4 个 Δ（**+1.2 / −65.4 / −5.1 / −18.3**）· §S2 正文（**+10.3pp**）。
- **Error Analysis 重做/重声明**：改用 5-run 代表性 run（建议 full_v3 r3=81.6%、129/158）重计失败数；或显式标注「基于单次代表性 trace」。🚫 不得仍绑 84.8% 那次 134/158。
- **硬伤#3**：`tab:omega` (L)=82.8、`tab:ablation-harness` (N)=73.3、(B)=66.2 无 5-run 支撑 → 一律标 `[provisional, n=1]` 或回退 `[TBD]`，🚫 不得再以 `±` 呈现（尤其 (B) ±16.1 的 std 无 n≥2 支撑）。
- **硬伤#5**：`tab:phi-bound` 增加「Mean gen-fail」列（k10/k3/k1），§S2 正文补「k↓ → gen-fail↑ → Pass@1↓」1–2 句。
- **硬伤#6**：§2（Background/Prior work）或 §3 加 1–2 句 BaiZe 边界，措辞中性如「本工作的 harness（三 MCP 工具 + 评测协议）属 ZhuLong；agent backbone 的底层能力另由互补工作 BaiZe[ref] 详述，二者互引不重报」。

**③ 🟠/🟢 按 §8 清单继续**：
- **P1**：补配对检验（paired bootstrap/McNemar）或在 Limitations 明示「未做配对检验」；§5.3/§6 补 gen-fail 计入分母 + infra 故障 run 剔除规则 + 75% 锚点健康下限；§6.1.4 声明 backbone 量化 `deepseek-v4-pro-fp4`；消歧 (N)→(N′)。
- **P2**：删 ICML 中文注释（`6_exp.tex:132-133`）；加结果可视化图至少 2 张（消融条形 + Φ 折线）；Limitations 独立成节并补「未配对检验」「量化未消融」两条；附录加 75 轮原始值表。
- **P3**：回填后重编译处理 overfull hbox（13.6pt/13.1pt 两处）；核对 DAC 2027 页数上限。

**④ 🟢 可回填（§7.1 第 1–10 项）**：能填即填（k10→`77.7±2.2`、k3→`69.1±2.5`、锚点 `82.1±3.0` 等）。🚫 **仍缺数据项一律保留 `[TBD]`/provisional，不得编造**：phi_k1 r3–r5、phi_lagged、S1 三臂（omega_low/readback_binary/_none）、wo_sandbox、SKILL/Tcl、全部 Converged(%)。

**⑤ 改稿纪律**：改后编译 `main.pdf` 验证 **0 error** + 报页数变化；每个数字与 `MEMORY_ZHULONG.md` 执行看板/成绩一致、🚫 凭印象；完成把「改了哪几处 + 编译结果」写进心跳；commit 前缀 `zhulong paper-fix:`（区别于 paper-review）· 任务书 >32KB 自滚归档。

**红线**：🚫 评测优先于改稿，不得为此 kill/延迟评测；🚫 数字编造；✅ 锚点与全部 Δ 必须同步改，避免表文矛盾。

### 🆕 运维指令 · 2026-10-14（十六）— 📝 实验空窗期审视论文，出改进意见 HTML（中文）【已完成·2026-10-14 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-14）。HTML 报告 `reports/report_zhulong_paper_review_zh.html` 已交付（运维令十七据此放行改稿）。

### 🆕 运维指令 · 2026-10-13（十五）— ✅ 沙盒已重启完成，恢复试验（撤销 (十四) 暂停令）【已完成·2026-10-14 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-14）。沙盒已重启，phi_k3→phi_k1→phi_lagged 已依次推进，撤销 (十四) 暂停令生效。

### 🆕 运维指令 · 2026-10-13（十四）— 🛑 立即暂停所有试验（沙盒重启中）【已被(十五)撤销·2026-10-13 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。暂停令已被 (十五) 撤销，phi_k3 已恢复试验。

### 🆕 运维指令 · 2026-10-13（十三）— 🔴 紧急修正：75% 下限只适用于 `full` 锚点，消融臂不得用它作废成绩【最高优先 · 用户直令】

> **用户令（2026-10-13）**：「谁说 phi k3 一定要大于 75% 了，限制沙盒执行三次必然影响 Pass@1，72% 在正常范围。75% 是 full 的下限，不要混淆。」

**背景**：任务书 `(十二)`④ 和更早的 `(九)`④ 写了「判据 timeout ≤10 且 Pass@1 ≥75% ⇒ 该轮有效」。该判据**最初是针对 `full` 锚点写的**（目的是验证 infra 健康——如果 full 都跑不到 75%，说明沙盒/模型服务有问题，而非 agent 能力问题）。但 agent **错误地将它推广到了所有消融臂**（C2.phi_k10 / phi_k3 / phi_k1 / phi_lagged 以及 S1），导致消融臂的低分被误判为「无效」而重跑。

**🔴 立即生效的修正（逐字遵守）**：

1. **`Pass@1 ≥ 75%` 下限只适用于 `C1.full`（锚点）**。锚点跑不到 75% = infra 不健康（沙盒/模型/license/端口故障），该轮作废、重跑。
2. **消融臂（C2 的 phi_k10/k3/k1/lagged、S1 的 omega_low/readback_binary/readback_none、C1 的 pure_llm/rag/wo_retrieval/wo_selfexp）的判据 = 仅 `timeout ≤ 10` 且无 infra 故障**（license 耗尽 / 端口宕 / 磁盘 <8G）。**Pass@1 任何值都有效**——低分是消融效应的真实体现，不是 infra 问题。
3. **phi_k3 r1 att1 = 72.8%（115/158, timeout=0）应判为有效**。立即：
   - 如果 att2 仍在跑 → **等 att2 跑完后取 att2 的成绩**（不浪费已投入的算力），记 r1 = att2 成绩；
   - 如果 att2 已跑完 → 取 att2 成绩记 r1；
   - 如果 att2 尚未开始 → **取消 att2，直接记 r1 = 72.8%**，推进 r2。
   - 无论哪种情况，**ERROR_COUNT 重置为 0**，不因 72.8% 计错误。
4. **phi_k10 已完成的 5/5 = [78.5, 76.6, 77.2, 81.0, 75.3] → 77.7±2.2% 保留不变**（已跑完，不追溯重跑）。但须在成绩记录中标注：r3/r4/r5 经历了不必要的重试（att1 低分被误判为无效），最终取的是重试后的值；原始 att1 值（r3=74.1%, r4=63.3%/74.1%）应**保留在 daily-memories 中作为证据**，不删除。
5. **后续所有消融臂**：只要 `timeout ≤ 10` 且无 infra 故障（license_error / Connection_error / 端口 CLOSED 全 0 条），**一律记为有效，不重跑**。低分 = 真实消融效应。

**红线**：
- 🚫 不得以 `Pass@1 < 75%` 为由作废任何非 full 臂的成绩。
- 🚫 不得以 `Pass@1 < 75%` 为由重跑任何非 full 臂的任何轮次。
- ✅ 唯一的作废理由 = infra 故障（timeout > 10 / license_error / 端口宕 / 磁盘不足）或 auto-grade bug（PASS_RATE=1.3% 等明显异常值）。
- ✅ `ERROR_COUNT` 只计 infra 故障和 grade bug，**不计消融臂的正常低分**。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_ZHULONG.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ZHULONG_TASK_ARCHIVE.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `zhulong 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**29KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动。


### 🧭 运维规程 · 2026-10-06（**【每轮唤醒必须自己 commit+push】** —— 不许依赖 loop 兜底）· 常驻

> **用户指令（2026-10-06）**：与 BaiZe 四线同口径 —— **每条线每次唤醒都要推送**。本线此前明文写「靠外层 loop 每 ~5h 兜底」⇒ **自本轮起作废该口径**（§11 已同步修改）。
> **为什么**：运维**只能靠 git 判断你是死是活** —— 2026-10-06 data 线心跳文件近 2h 未更新，被**误判成卡死并上机排查**。🚫「loop 每 N 小时兜底」**不再作为交付保障**，只是保险丝。
> **每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡**：
> 1. **写心跳**：更新 `run/MEMORY_ZHULONG.md` 顶部状态头 / 执行看板 / 成绩表 + 追加 1 行操作流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮（**当天文件必须建**）。
> 3. **自己提交 + 推送**（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong <阶段/轮次>: <一句话>"` → `git push origin main`。🚫 **绝不用 `git add -A`**（多项目共用工作副本，会卷入别线在途文件）。
> 4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind。**push 失败**（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下轮第一件事补推**。
> ⏱️ **判死判据（硬）**：**心跳文件 >60min 无新提交 ⇒ 按卡死处理**（不再等你）。**你干得再多，心跳不动 = 仍会被判死。**


### 🧭 本轮（2026-10-11 上午）执行顺序 —— 换回旧 4 端口 + 修 RAG + 删 hook → 推进 r2–r5【已完成·2026-10-13 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。r2–r5 已完成，当前已推进至 C2.phi_k3。

### 🆕 运维指令 · 2026-10-11（十二）— r5 收割后补跑 5 轮「真正的 full」（自探索开启）【full_v3 5/5✅ 82.1±3.0% 已交付·2026-10-13 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。full_v3 5/5 = 82.1±3.0% 已交付（三组对照表见 `MEMORY_ZHULONG.md`），未复现 r1=88.0%。

---

### 🆕 运维指令 · 2026-10-11（十一）— 📊 Deep dive：为什么 `full` r1=88.0%【⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`·报告已交 `reports/R1_ANOMALY_ANALYSIS_2026-10-11.html` @commit 25b27adb】

### 🆕 运维指令 · 2026-10-11（十）— 🔎 RAG(9006) 排查【⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`·已收口·报告 `reports/RAG_AUDIT_2026-10-11.md` @commit 84e66335】

---

### 🆕 运维指令 · 2026-10-11（九）— 换回旧 4 端口 + RAG→9006 + 删 hook + .env 回退 + 重跑 r2–r5【已完成·2026-10-13 归档】

> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-13）。换回 4 端口 8650/8651/8652/8654 + RAG→9006 + 删 hook + .env 回退均已完成，r2–r5 已交付。

### （八）10-10 — 保留 4 端口 + `"timeout": 180` + 重跑 r2–r5【已被 (九) 取代·已归档】

### （七）10-10 — 剔除 8667 + 补 8650–8654 + 调高 MCP timeout【已被 (八) 取代·已归档】

### （六）10-10 — 若 9 端口健康先判别「端口数是否真因」【已被 (七) 取代·已归档】

### （四）10-10 — 根因排查：连续多日 timeout【已完成·已归档】

### （三）10-10 — 先停 zhulong + 实测沙盒端口【已完成·已归档】

### （二）10-10 — 专属沙盒就绪：保 r1 → 重跑 r2–r5【已被 (三)/(四) 取代·已归档】


### （一）10-10 — 切专属沙盒 + C1.full 作废重测【已被 (二) 取代·历史】


### 🆕 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【已被 2026-10-10(一) 取代·已归档】


### 🆕 运维指令 · 2026-10-09（四）— 🛑 沙盒坏了，r4 已被运维 kill，待命不要重跑【已被(五)取代·历史】

### 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测（模型服务不稳定致大量 timeout）【已归档·被(四)取代】

### 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【已完成·已归档】

### 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）【已完成·已归档】


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**：
   ```bash
   cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
   git pull --rebase --autostash origin main          # 先同步（这次用你当前 shell 的代理）
   pkill -f zhulong_loop.sh; sleep 3
   export https_proxy=http://172.19.92.23:13128
   export http_proxy=http://172.19.92.23:13128
   setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
   sleep 4
   # 复核：新 loop 进程应带代理
   _NPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   tr '\0' '\n' < /proc/$_NPID/environ | grep -iE 'https_proxy'
   ```

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 🆕 运维指令 · 2026-10-08（一）— 📝 HTML 报告【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-08）。产物 `reports/report_2026-10-08_holiday.html`（21870B，8 节齐全，已 commit a4dc5c3c）。

### 🆕 运维指令 · 2026-10-05（八）— ops 中继恢复【已解决·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。ops relay alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-05（七）— 评测侧隔离 config dir【已落地·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。合并线 eval 用 `CLINE_CONFIG_DIR=.cline_eval_zhulong`；编排用 `--config .cline_zhulong`。

### 🆕 运维指令 · 2026-10-05（六）— 试验次序调换 B→C1→C2→S1【已生效·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前顺序 B→C1→C2→S1（§4 已同步）。

### 🆕 运维指令 · 2026-10-04（五）— legacy 组件 loop 保活【常驻·已稳定·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。legacy loop alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-04（四）— 正式起始点 C1.wo_retrieval R2【已越过·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前已推进至 C1.full r1。

### 🆕 运维指令 · 2026-10-04（三）— 中继已恢复 / loop RUN_ID 6 重启【已解决·已归档】

### 🚨 运维指令 · 2026-10-04（二）— 抢救 ops 中继【已解决·勿再执行·已归档】
### 🆕 运维指令 · 2026-10-04：环境迁移 + 合并执行方式 + ops 中继独立

> 本次把 4 个 phase（S1 保真度 / 组件 / S2 Φ / 模型）**合并进本单一任务书 + 单一 loop**，不再按 `ablation_run_conductor_serial.sh` 拆 3 个 task book + 4 个 loop。**执行顺序不变**（README §8）：S1 → 组件 → S2 Φ → 模型。

1. **环境（agent 最终跑在 36.15 服务器，必须用下表 `/nasdata/` 路径）**：
   - `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
   - `PAPER=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/ZhuLong_DAC2027`（唯一可改 LaTeX 树）
   - `GIT_ROOT=/nasdata/app.e0031982/code/super_intelligence_2035`
   - **注意**：当前 2.12 开发机路径前缀为 `/nas_train/`（与 36.15 的 `/nasdata/` 独立挂载，互不关联）。旧 task book 中的 `/nasdata/` 路径在 36.15 上仍然有效，并非迁移关系。
2. **infra 前置校验（PHASE=init 首次启动前必做，不满足则 `WAITING=1` 原地等）**：
   - `df -h /home` 可用 **≥ ~8G**；四 shard 端口 **8664/8665/8653/8669 全 OPEN**；`run_code` 可正常执行（license 可用）。
   - 旧停摆根因即此三项，**没恢复就别开跑，跑出来也作废**。
3. **起始状态（运维在此填实）**：默认 `PHASE=init`，从 `STAGE=S1, CONFIG=omega_low, ROUND=1` 开始；若要延续旧 S1 进度，改填 `CONFIG=omega_low, ROUND=3`，并把 r1=81.6 / r2=82.3 写进 MEMORY 成绩表，r1/r2 不重跑。
4. **ops 中继通道已就绪**：`run/zhulong_ops_relay.sh` + `run/ops/{inbox,outbox,README}.md`。运维通过 git 下发 shell 命令（~20s 轮询），与 BaiZe ops 相互独立。启动命令见 `run/ops/README.md` 或本报告 §6。
   - ⚠️ 只有本区（运维指令区）的 ops 提及是写给人看的。**agent 不要碰 ops/ 目录**（中继专供运维下发命令，agent 写 MEMORY 和日常记录即可）。

### 🆕 运维指令（后续按需追加）

> （预留：运维批准模型消融、调整起始点、或追加 RQ3 SKILL/Tcl 切片时写在这里。）

---

## 1. 🎯 你是谁 · 任务总目标

你是推进 ZhuLong（DAC2027）EDA 消融评测的自动化 agent。每次被唤醒**只做一步**：

> 读 `MEMORY_ZHULONG.md` 恢复状态 → 读 `daily-memories/$(date +%F).md` 恢复上下文 → 判断下一步 → 执行 → 更新 `MEMORY_ZHULONG.md` 与当日流水 → 立刻退出。

不要 sleep/等待（外层循环负责间隔）。shell 命令直接调用工具，**不要调用任何 MCP 工具**。

**总目标**：把论文 6 张表里所有 `[TBD]` 换成实测 `mean ± std`（口径 README §4.1），共 **56 个 `[TBD]` / 30 行**。本任务书覆盖需要跑量的 4 个消融轴（见 §4）；`tab:selfdoc-cost`（离线自探索日志，1 次无重复）不在本循环内。

## 2. 🔒 冻结项（所有臂共用，不得变动）

- 数据集 `EDA-Eval-PyAether` **158 任务**；通过判据 = 生成代码在 sandbox 无错执行且全断言通过；`Pass@1 = 通过/158×100%`。
- 每配置 **5 次独立运行** → `mean ± std`；每次**重排任务顺序** + **全新 agent context**。
- 单任务单 trace、超时 **2500s**、`-p 8 -n`（8 并发 + 禁 Memory Bank 注入）。
- 主 backbone `deepseek-v4-pro-fp4`（**只有 STAGE=B 模型消融才换**）。
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**。
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰。
- 检索默认 = name+description 索引向量检索（只有 S1 显式改变该索引保真度）。

## 3. ⛔ 红线（不得违反）

1. 不复活被否决表述；不自造符号/定律；不把「轮次」当 Φ 的操作轴。
2. 不改 `tab:llm-comparison` 结构（列/行口径已锁定）。
3. 不承诺开放任务用例（开源只覆盖 harness/schema/protocol，不含 benchmark 任务本体）。
4. 不填未测数字（未测留 `[TBD]` 或显式 provisional）。
5. `tab:omega` 口径：`(N)`=Pure LLM（核心 4 全关）；不采用 ICML 的 `(N)=0.0`。
6. 各 hook `errorMessage` 用唯一前缀区分（反作弊 vs `[PHI-BUDGET-EXHAUSTED]`）。
7. 反作弊内部数据不入论文正文（只定性，不带数字）。

## 4. 🗺️ 合并消融总计划（4 阶段 · 15 臂 · 75 轮 · 单循环串行）

执行顺序（**已调换**：因 pro-fp4 额度 403 阻塞 C1，现将 Phase B 提到最前）：**B → C1 → C2 → S1**。

| 阶段 STAGE | 流 | 臂（顺序）| 轮 | 回填表 |
|:--|:--|:--|:-:|:--|
| `B` 模型 | B | `glm-5.2` → `deepseek-v4-flash` → `kimi-k2.6-cloud` → `doubao-seed-2.0-pro-cloud` | 20 | `tab:llm-comparison`(4 行) |
| `C1` 组件 | C | `pure_llm` → `rag` → `wo_retrieval` → `full`(锚点) | 20 | `tab:main-ablation`(4 行) + 锚点行 |
| `C2` S2 Φ | C | `phi_k10` → `phi_k3` → `phi_k1` → `phi_lagged` | 20 | `tab:phi-bound`(k1/3/10/lagged) |
| `S1` 保真度 | A | `omega_low` → `readback_binary` → `readback_none` | 15 | `tab:omega`(L) · `tab:ablation-harness`(B,N) |

**锚点复用（跑一次、多处引用，禁止重复跑）**：
- `C1.full` ×5 = `tab:main-ablation`(full) + `tab:omega`(H) + `tab:ablation-harness`(F) + `tab:phi-bound`(unbounded) + `tab:llm-comparison`(DeepSeek-V4-Pro 主基座)。
- ∴ S1 的 (H)/(F)、C2 的 `phi_unbounded`、B 的主基座臂**全部跳过，不重跑**。

## 5. ⚙️ 统一状态机（字段写 `MEMORY_ZHULONG.md` 顶部）

| 字段 | 取值与含义 |
|:--|:--|
| `STAGE` | `S1` → `C1` → `C2` → `B`（顺序，交叉衔接）|
| `CONFIG` | 当前臂名（见 §4 表）|
| `ROUND` | 1..5 |
| `PHASE` | `init` / `running` / `just_finished` / `done_all` |
| `WAITING` | 0=无异步阻塞（下轮 ~1min 续跑）；1=一轮 eval 正在跑，或 infra 不就绪（下轮 ~30min）|
| `ERROR_COUNT` | 连续失败计数（≥3 强制推进）|

**臂轮转矩阵（PHASE=just_finished 时查下表切下一臂——已调换为 B→C1→C2→S1）**：

```
B:  glm-5.2 → deepseek-v4-flash → kimi-k2.6-cloud → doubao-seed-2.0-pro-cloud → C1.pure_llm
C1: pure_llm → rag → wo_retrieval → full → C2.phi_k10
C2: phi_k10 → phi_k3 → phi_k1 → phi_lagged → S1.omega_low
S1: omega_low → readback_binary → readback_none → done_all
```

> ⚠️ **Phase B→C1 衔接**：Phase B 使用 full 配置（不切 set_ablation），切到 C1.pure_llm 前**必须先执行** `scripts/set_ablation.py pure_llm` + `stop.sh && start.sh` 将 .env 切为 pure_llm 配置。
> ⚠️ **C1→C2 衔接**：切 C2 前执行 `scripts/set_s2_phi.py <ARM>` + `stop.sh && start.sh`。
> ⚠️ **C2→S1 衔接**：切 S1 前执行 `scripts/set_s1_fidelity.py <ARM>` + `stop.sh && start.sh`。

## 6. 🔧 固定命令（所有 `cd` 用 `BASE_DIR` 展开；`<TAG>`=CONFIG 名，`<N>`=轮次 1..5）

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
