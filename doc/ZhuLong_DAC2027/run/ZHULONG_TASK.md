# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区
### 🔨 执行令 · 2026-10-24 09:3x（**按精简报告改一版论文 → 编译 → 提交并推送，供用户审阅**）· 用户直令 · 最高优先

> 用户原话：「zhulong 精简论文的报告我看了，**安排他按此改一版，提交 & 推送我看看**。」

**① 依据**：`run/reports/report_zhulong_paper_trim_advice_zh.html`（28,389B，commit `c32342e4`）
按它的 **① 逐章诊断表 + ② 可删清单（16 条）+ ④ 6 页预算 + ⑤ 摘要/引言草稿** 执行。

**② 硬指标**
| 项 | 目标 |
|---|---|
| **正文页数** | **≤ 6.0 页**（当前 12.0 页）——编译后必须实测页数并贴出 |
| 行预算 | 按报告 §④：Abstract ~16 / Intro ~30 / Bg ~10 / Design ~26 / Grounding ~34 / Bench ~22 / **Exp ~95** / Disc ~5 / Concl ~6 ≈ **244 行** |
| 表/图 | 正文 **1 图 + 3 主表**（main-ablation + phi-bound 精简 + llm 4 模型）；其余移附录或合并 |

**③ 关键改动（按报告执行，不得走样）**
1. **实验章 6_exp.tex 从 248 非注释行 → ~95 行**（最硬一刀）：
   - `tab:cost` → 移附录；`tab:configurations` → 并入正文文字；`tab:error-categories` → 改一句文字
   - `tab:phi-bound` → 删 [TBD] 空列；`tab:llm-comparison` → 6 模型留 4
   - S1–S4 各压到 ~1 段；Error Analysis 4 case → 1 段
2. **摘要用 §⑤-A 草稿**（含末句落地佐证"hundreds of design engineers"）
3. **引言用 §⑤-B 草稿**（3 条 contribution 各一行）
4. **理论章 4_grounding 81 → ~34 行**：砍 "Two clarifications" 整段 + L99–105 设计原则展开
5. **discussion 6 条 limitations → 3 条**

**④ ⚠️ 必须同时并入 09:2x 令的价值主张（这条比报告更新）**
摘要与引言要体现：
> **coding agent 天生会做 design flow 编排**（写 Makefile/tcl 驱动/调度，串起现有 EDA 工具）
> **+ EDA scripting 能力补全工具断链**（现成工具覆盖不到、要手写胶水处，现场生成代码接上）
> **= 真实 DE 价值：flow 能完整跑通**

即：在报告的 "execution grounding" 主线之外，**把"编排 + 补断链"作为更高层的价值表现写进去**，形成「scripting → flow 编排」的递进。报告是 09:2x 之前生成的，摘要/引言草稿需按此再调整一遍。

**⑤ 交付与验证**
1. **改完后编译**（`pdflatex`/`latexmk`，与现有构建方式一致），**必须贴最终页数**（`pdfinfo` 或 pdf 页数）。
2. **若仍 > 6.0 页**：继续按报告 §② 清单再砍（每轮只砍最长的 2 条），**直到 ≤6.0 页**；每轮贴页数变化。
3. **不要破坏参考文献/图表编号**（`\ref`/`\cite` 编译无 undefined）。
4. **commit + push**：
   ```
   zhulong paper: 按精简报告改 6 页版（12p→6p）· Exp 248→95 行 / 摘要+引言重写(含编排+补断链 与 落地"数百") / 3 主表
   ```
5. **推送后回报**：页数 / 各章实际行数 / 砍掉的 16 条中执行了哪些 / 编译告警（undefined ref 等）

**⑥ 纪律**
- ✅ 原 12 页版本**先备份**（`git tag paper_12p_backup` 或复制到 `paper_12p_backup/`），不要覆盖丢失
- 🚫 不打断正在跑的评测（`dsv4pro-cline-full r1` 若仍在跑，评测不受影响，改稿是纯文件操作）
- 🚫 不改实验数据与结论数字（只精简表述，不删关键数字：75.7% / 18.3% / 62.5% / 57.4pp / 22.0pp 必须保留）


### 🎯 补正 · 2026-10-24 09:2x（**论文核心价值主张重定位：从 "EDA scripting" 升维到 "design flow 编排"**）· 用户直令 · 最高优先

> 用户原话：「zhulong 设计初衷是 EDA scripting，但 DE 用户使用最多的场景还是 **design flow 的编排**。这是 coding agent **天生具备的能力**，而 EDA scripting 能力可以支持 design flow 编排是**补全断链**（有些现成工具无法覆盖的断链，可以被 EDA scripting 轻易接上）。」
> **⚠️ 这是论文的叙事主干，必须体现在摘要/引言/结论**，不只是"落地一句话"。

**① 重新定义的价值链条（写入报告，作为论文立论）**

```
coding agent 的通用能力  →  直接可做 design flow 编排（写 Makefile/tcl 驱动/调度脚本，
                             串起现有 EDA 工具）—— 这是"天生具备"，不需要特殊训练
        +
EDA scripting 专业能力  →  补全断链（现有工具覆盖不到、或需要手写胶水的地方，
                             agent 用 pyAether/SKILL/Tcl 现场写代码接上）
        ↓
    真正的用户价值 = design flow 能被完整跑通
    （断链是 flow 跑不通的头号原因，而接断链正是 LLM 最擅长的事：写一小段新代码）
```

**② 为什么这个论点对 DAC 有说服力（报告里要论证清楚）**
- **DE 的真实工作分布**：不是天天写全新脚本，而是**编排 + 补洞**（flow 串不起来时现场补一段）。这一点决定"通用 coding 能力 > 纯 EDA 专用模型"。
- **"补全断链"是本工作的独特切入点**：现成商用工具是**闭合的**（不给你改），断链只能靠**现场生成胶水代码**；而 LLM 恰好能把"自然语言意图 → 可执行脚本"这段补上。
- **解释了为什么 benchmark 要这样设计**：我们的 benchmark 不只是"写脚本题"，而是**模拟真实 flow 中的断链场景**（如果现有 benchmark 是这样设计的，请明确指出并引用 RQ；如果不是，在报告里建议补一节说明）。
- **与落地规模自洽**：数百名工程师的价值不在于"人人写脚本"，而在于**每个人的 flow 都有跑不通的时刻**，agent 在那里补位。

**③ 报告里必须给出（中英各一）**
1. **一句话价值主张（paper pitch，≤30 词）**：
   - 中文草稿方向："ZhuLong 让通用 coding agent 直接承担 design flow 编排，并用 EDA scripting 能力补全工具间的断链——这正是 DE 日常工作中最耗时、最被忽视的一环。"
   - 英文草稿方向："ZhuLong lets a general coding agent orchestrate design flows and, where existing tools leave gaps, synthesizes the missing glue in domain scripts — precisely where DEs lose the most time."
2. **摘要重写草稿（6 页版，150-180 词）**：按「问题（flow 编排 + 断链）→ 洞察（coding agent 天生会编排，EDA 能力补断链）→ 方法 → 结果（benchmark + 落地）→ 意义」组织。
3. **引言动机段（3-4 句）**：把"DE 天天补断链"的痛点写实，再引出"为什么通用 coding agent 是正确选择"。
4. **结论段**：回扣"编排 + 补断链"这个定位，而不是只谈脚本准确率。

**④ 与既有内容的衔接（不要冲突）**
- 现有论文若以 "EDA scripting" 为标题/主线，**不必改标题**（`ZhuLong: An Execution-Grounded LLM Agent for EDA Scripting` 可保留），但在摘要与引言里**把"编排 + 补断链"作为 scripting 的更高价值表现**写出来，形成"从 scripting 到 flow"的递进。
- 6 页预算紧张，**优先保摘要 + 引言的这个叙事**，实验章可以更精简。


### 🟢 补正 · 2026-10-24 09:0x（**"长鑫落地"融入口径修正：轻描淡写提分量、留余地，不写具体 500**）· 用户直令

> 用户原话：「领导已经在跟外部厂商沟通时介绍了 ZhuLong 落地的情况，但在论文需要轻描淡写留有余地，比如不说 500（因为一直变化），而写成**数百**（就算全量 2000 人都使用数百也说得过去）」。
> **⚠️ 修正 08:3x 令 §③ 的方向**：不是去评估"能不能用/有什么风险"，而是——**这个信息有价值，要自然地融进论文，提高成果分量与录用概率，同时措辞留有余地**。

**① 写法口径（硬约束）**
- ✅ 用 **"数百"（hundreds of）** 表述用户规模，**🚫 不写具体数字 500**（用户数持续变化，写死会被质疑）。
- ✅ 用 **"已在量产级 EDA 设计流程中部署"（deployed in production EDA flows）** 这类表述，强调**工业环境 + 真实设计流**，不强调人数。
- ✅ 强调**质量维度**而非数量：覆盖 Tcl / waveview / SKILL 等多种脚本接口、真实设计数据流、长时间稳定运行。
- ✅ **轻描淡写、克制**：一句话带过即可，不单开小节炫耀；放在摘要末句 / 引言动机段 / 结论任一处（择一，不必都写）。
- 🚫 不吹"领先""首个""大规模"这类易被审稿人挑战的绝对化表述。
- 🚫 不写具体公司名吗？——**按投稿匿名要求处理**（DAC 双盲则写 "a leading memory-chip manufacturer / a production memory design house"；非双盲可直接写 CXMT）。

**② 报告里给 3 版可直接插入的句子（中英各一）**
- **版本 A（摘要末句，最克制）**：一句话点出"已在工业 EDA 流程部署，服务数百名设计工程师"。
- **版本 B（引言动机，强调痛点真实）**：从"真实设计流中的脚本编写痛点"引出，落地作为佐证。
- **版本 C（结论/实验章，强调可信度）**：作为"结果不仅在 benchmark 上成立，也在生产环境中被使用"的背书。
每版给出中英文，并标注字数占用（6 页预算下建议 **≤ 25 词**）。

**③ 一句话回答（不要再展开风险论述）**：这个信息对录用有帮助，理由 1-2 条即可（工业落地 = DAC 重视的实用性；真实部署 = 方法可信度背书）。


### 📄 运维指令 · 2026-10-24 08:3x（**审视 ZhuLong 论文 → 出中文 HTML 精简意见（DAC 正文 6 页）+ "长鑫落地"如何轻描淡写融入**）· 用户直令 · 最高优先

> 用户原话：「zhulong：安排它审视 zhulong 论文，提出精简意见（DAC 要求正文 6 页）。另外 ZhuLong 已经在长鑫落地，当前用户 500 左右。这个信息对论文是否有价值，如何融入，也写在精简意见中文 HTML 报告中。」

**① 背景**
- 论文当前 **12 页**（`cccc49c2` 从 13p 压到 12p），**DAC 正文限 6 页** → **还需砍掉约 50%**。
- 现状：`6_exp.tex` 319 行（占全文 53%）、`4_grounding.tex` 105 行，其余章节合计 ~184 行。

**② 交付物（一份中文 HTML，自包含单文件）**
`reports/report_zhulong_paper_trim_advice_zh.html`，必须包含：
1. **逐章诊断表**：`文件 | 当前行数/占比 | 建议目标 | 拟删/合并的具体段落（标行号或小节名）| 理由`
2. **可直接砍的清单**（按"性价比"排序：先砍低信息密度的过程性描述、重复叙述、legacy 对比；保留主表 + 核心结论）
3. **挪到附录/补充材料的建议**（若 DAC 允许）
4. **6 页预算分配建议**（摘要/引言/方法/实验/结论各占多少行）
5. **⚠️ 重写的摘要与引言草稿**（6 页版本，需体现"执行落地"卖点而不是压缩后的残篇）

**③ 关于「长鑫已落地」—— 按 09:0x 补正令执行（见上方最新一块）**
> ⚠️ **本节已被 09:0x 补正令取代**，请以补正令的写法口径为准：**轻描淡写融入论文、提高分量与录用概率、措辞留有余地**（用"数百"而非 500），**不要**写成"风险评估 / 审稿人会不会质疑"的论述。

**④ 纪律**
- 🚫 不改论文 .tex 源文件（本轮**只出建议报告**，改稿等用户确认）。
- ✅ 报告里的"建议删除"必须能对上具体小节名/行号，不许泛泛说"精简实验部分"。
- ⏭ 不打断正在跑的评测（`dsv4pro-cline-full r1` 仍在收尾，别 kill）。



### 🆕 运维指令 · 2026-10-23 22:1x（**本 5-run 收口后 → 起 `cline × deepseek-v4-pro × full` 5-run**）· 用户直令 · 最高优先

> 用户原话：「Zhulong：zl+glm-5.3-flash+full 5-run结束后，跑cline+deepseek-v4-pro 5-run+full」

**① 前置（顺序不可跳）**
1. 先把在跑的 `zl × glm-5.3-flash × full` **r5** 收口：手动 regrade → 记 `full-r5 = x/158` → 出 **5/5 mean±std**（现有 r1=69.0 / r2=77.2 / r3=76.6 / r4=81.0）→ 更新 `zhulong_results.md` 本轮实验块。
2. 收口后 **确认 4 端口与 8090 都空**（上一轮 worker 全退、`pgrep -af run_zhulong_script` 为空），再起新线；🚫 两条线并行（会互相抢端口/污染 batch）。

**② 新线配置（与上一条线只换 agent + 模型，其余保持 full 口径）**
- `CLI_AGENT = cline`、**模型 = `deepseek-v4-pro`**、**`READBACK=full`** / `OMEGA=high` / `BUDGET=0` / `LAGGED=0`。
- 端口 = **8650/8651/8652/8654**（沿用，保持口径一致）；`-p 4`；`unset http_proxy https_proxy`；`NO_PROXY=10.129.32.75,localhost,127.0.0.1`；`PYTHON=$PWD/venv/bin/python`。
- 数据目录用 cline 线自己的 `CLI_DATA_DIR`（`~/.cline`；**🚫 不要复用 `~/.zhulong`**，否则等于换汤不换药）。
- **起跑前先做 1 次「模型可用性冒烟」**：单次 `run_code` 走通（拿到四字段 readback）+ 记录模型 id / base / key 来源；**403 / 404 / 额度不足 ⇒ 立即停手报 blocker（附原文）**，🚫 不静默换模型、不换 provider 凑数。
- batch 命名沿用 `2026_MMDD_HHMMSS`；每轮 **r1→regrade→r2→…→r5**，每轮都跑判据十三（`timeout ≤10` / `0 infra` / `0 exec_err`）。

**③ 回报（每轮 + 收口各一次）**
- 每轮：batch / Pass@1(N/158) / literal-pass 数 / 耗时 / 端口状态 / 5-run 累计。
- 收口：`5/5 mean±std` + 与两条对照线的对比（`zl × glm-5.3-flash × full` 本轮 5/5、`zl × glm-5.3-flash` 旧 N′ 线 86.8±1.6%）。
- 口径：**新线不纳入论文**（独立探索），论文锚点不动；commit 前缀 `zhulong`。

### 🟢 运维指令 · 2026-10-23 09:4x（**作废 r1-r3 → 改 full 配置 → 重跑 5 轮**）· 用户直令 · 最高优先

> 用户原话：「作废 r1-r3，改 full 重跑 5 轮」+ 之前「新线不纳入论文。启动 r4 时尝试使用端口 8663/8666/8667/8670」
> **背景**：r1-r3 跑的是 **N′ 配置**（READBACK=none），用户要的是 **full 配置**（READBACK=full）。这是运维疏忽——00:3x 令只写了换模型/agent/端口，没写改配置，agent 沿用了 .env 当时的 N′ 值。现纠正。

**① 已由运维完成（勿重复）**
1. **停 r3 regrade**（已 kill）。
2. **改 .env**：`EDA_RUNCODE_READBACK` 从 `none` → **`full`**（其余不变：OMEGA=high/BUDGET=0/LAGGED=0/CLI_AGENT=zhulong/PROXY_PORTS=8650,8651,8652,8654）。
3. **重启 8090 MCP 服务**（PID 2535923，已 pick up full readback）。
4. **冒烟验证**：8650 run_code 返回四字段（response/error_log/print_log/result）→ **full readback 生效 ✅**。

**② 你要做的（按序）**
1. **确认 .env 是 full 配置**：grep `EDA_RUNCODE_READBACK` 应为 `full`；8090 `/health` OK。
2. **确认 8663 组状态**：RUN_ID 111 已探 = 4/4 不可用（breaker cooling）→ **用 8650 组**（4/4 OK·12-14ms）。
3. **起 r1**（full 配置 × glm-5.3-flash × zhulong × 8650 组 × `-p 4`）：
   - `run_zhulong_script.sh -p 4 -n`（CLI_AGENT=zhulong 自动·CLI_DATA_DIR=~/.zhulong 自动）
   - `export PYTHON=$PWD/venv/bin/python`；`unset http_proxy https_proxy`；`NO_PROXY=10.129.32.75,localhost,127.0.0.1`
   - 模型 = glm-5.3-flash（~/.zhulong/settings/providers.json 不变）
4. **r1 → regrade → r2 → ... → r5 → 5/5 mean±std**。
5. **每轮回报**：batch / Pass@1(N/158) / literal-pass 数 / 耗时 / 端口状态 / 5-run 累计。

**③ 判据（05:0x 令不变）**：`literal-pass >10 → 只记录+标退化+继续跑`；停手仅 = MCP 率 ≥5/min **且** 4 端口全不可用。

**④ 口径备注**：
- **本轮配置 = full**（READBACK=full/OMEGA=high/BUDGET=0/LAGGED=0），即 C1.full 档。
- 新线（glm-5.3-flash × zhulong）**不纳入论文**，是独立探索线。论文锚点仍用旧线 (N′) fp4×cline 4 轮 mean=76.7% provisional。
- r1-r3 的 N′ 数据**作废**，不进 5-run。

**⑤ r1-r3 作废标记**（留证不删）：
- r1: batch `2026_1023_002456`·N′·67.1%(106/158)·16 literal-pass → ❌ 作废（配置错误）
- r2: batch `2026_1023_052506`·N′·68.4%(108/158)·17 literal-pass → ❌ 作废（配置错误）
- r3: batch `2026_1023_072528`·N′·regrade 未完成 → ❌ 作废（配置错误）


### 📦 已归档 batch 10 · 2026-10-23（09:4x 活跃块之下的已闭合运维块·原文搬入 `run/ZHULONG_TASK_ARCHIVE.md` §归档 batch 10）

> 以下均为已闭合/已被取代的历史运维块，1-line 指针，需要时读 archive。**当前唯一活跃块 = 上方 🟢 2026-10-23 09:4x**。

- 🟡 2026-10-23 09:1x（r4 起跑·尝试 8663 组）·【已被 09:4x 取代·历史·r1-r3 作废·配置从 N′ 改 full】→ archive §归档 batch 10
- 🟡 2026-10-23 05:0x（用户决策 B·放弃 8663 组·用 8650 组跑满 5 轮）·【已被 09:1x 取代·历史】→ archive §归档 batch 10
- 🔴 2026-10-23 00:3x（停 r5e3 → agent 换 zl/zhulong → glm-5.3-flash 重跑 → 端口 8663/8666/8667/8670）·【① 已由运维完成·② 已被 09:4x 配置纠正取代】→ archive §归档 batch 10
- 🔴 2026-10-20 21:4x（杀 r4/r5/regrade → 端口换 8650-8654 → 重启 r4⁗）·【已归档·r4⁗ 收口 INVALID·被 10:4x 取代】→ archive §归档 batch 9
- 🔴 2026-10-20 21:2x（r4 疑似停滞·只读取证）·【已归档·被 21:4x 取代】→ archive §归档 batch 8
- 🔄 2026-10-22 10:2x（r5e3 回到 -p 4 + 8650-8654）·【被 00:3x 取代·历史·r5e3 已停】→ archive §归档 batch 10
- 🔄 2026-10-22 09:0x（r5e3 回到 -p 4 + 8650-8654）·【被 10:2x 取代·历史】→ archive §归档 batch 10
- 🔄 2026-10-21 15:3x（r5e 改 8 并发）·【r5e2 -p8 实测退化·作废】→ archive §归档 batch 10
- 🔄 2026-10-21 14:0x（r5e 换端口 8663/8666/8667/8670）·【r5e -p 4 部分被 15:3x 取代】→ archive §归档 batch 10
- 🔄 2026-10-21 10:4x（参考 t0002147 修复 cline settings timeout=600 + .env 对齐 → 重跑 r4⁗）·【r4e 已收口·历史·timeout=600 修复保持】→ archive §归档 batch 10
- 🔄 2026-10-20 15:4x（licence fix → 重跑 r4‴）·【已归档·被 10:4x 取代·未根治】→ archive §归档 batch 9
- 🔄 2026-10-20 10:1x / 09:0x / 08:2x / 06:3x / 06:0x（r4 家族排查系列）·【已归档·历史·已闭合】→ archive §归档 batch 8
- 🔒 2026-10-19 23:2x（模型口径锁定：r4/r5 用 fp4；full 用 pro-cloud）·【full 臂已被 09:4x 改为 glm-5.3-flash×zhulong×full·历史口径参考】→ archive §归档 batch 10
### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

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


### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


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

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

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
