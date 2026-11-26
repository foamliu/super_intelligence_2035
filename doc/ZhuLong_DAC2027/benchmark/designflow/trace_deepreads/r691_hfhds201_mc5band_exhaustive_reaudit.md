# r691 — hfhds201 mc 5-9 band A-domain 候选池穷尽重审（11-15 新标准）

**轮次**: r691 (0-case, 候选池重审 — 2026-11-15 最高优先令 §II 候选池重审 + r690 下轮建议)
**日期**: 2026-11-17
**动机**: r690 已深读 2 复活线索均落空（l0x4z 不可造无 evidence anchor + ai203 实为 shard B 已造 case 全回退），并在 MEMORY 留下「本轮未 exhaustive 重审 r689 列出的余 16 条 mc 5-9 band，暂不触发 auto-stop，留下轮 exhaustive 重审后再判」。本轮执行该穷尽重审，以 11-15 新标准（analysis-Q&A/doc-search/debug-Q&A/env-config/flow-driving/setup/retrieval/explain 全部恢复为可造；**唯一排除 = 无真实 trace + 写不出有牙 check()**；**域归属不因新标准改变**——C/B/D 域任务仍属 C/B/D shard）判定 r689 表中 18 条 mc 5-9 band 候选每一条。

**扫描源**: `.75:/home/t0002965/log/ssh_eda_search_20261116_072610/summary.tsv`（37113 行；承 r689 口径）
**方法**: eda_flow open_session → .75 本机 `awk` 取 hfhds201 + 5≤mc<10 + A 关键词 → 18 条；逐条 `python3` 解析 `<user>/.cline/data/sessions/<sid>/<sid>.messages.json`，抽 **全部 user 消息文本**（非仅首条，修正 r689 只 peek 首条的偏差）+ assistant tool_use 名；按「真实用户意图 + 域归属 + evidence anchor 可判分性」三轴判定。

## 一、穷尽重审结果（18 条 mc 5-9 band）

| slug | mc | user | 真实用户意图（user msg verbatim） | 域归属 | evidence anchor | 判定 |
|---|---|---|---|---|---|---|
| l0x4z | 8 | yuankong | "AddressParameter.v中的COLA赋值给了谁" | digital(code-search) | ❌ 文件不在 .75 本机也不在 trace（r690 实测 find 空） | **不可造**（r690 已定：无 anchor）|
| ai203 | 5 | yuankong | "写个python脚本...解析 bmatrix -f Fail 行" | eda_other(produce) | ✅ 但 **已为 shard B case `BmatrixRerunGen-001`**（r690 实测台账双行） | **不可造**（r690 已定：跨 shard dup）|
| 9a7jm | 8 | t0002441 | "Finesim仿真报DC不收敛的错误, 可能的原因及解决方案有哪些?" | **B (spice_sim)** | ❌ 纯概念 Q&A，无 log/网表可验 | 不可造（wrong-shard B + 无 anchor）|
| 6sh4c | 7 | t0002441 | 同上（**与 9a7jm 逐字相同**） | B | ❌ | 不可造（dup 概念 Q&A + wrong-shard）|
| qnm9e | 5 | t0002441 | 同上 | B | ❌ | 不可造（dup + wrong-shard）|
| shssw | 5 | t0002441 | 同上 | B | ❌ | 不可造（dup + wrong-shard）|
| y2mlp | 8 | t0002441 | 同上 | B | ❌ | 不可造（dup + wrong-shard）|
| ck74p | 5 | t0002987 | "分析你自己构建任务的完整流程" + "为什么从阶段2开始输出？检查 sessions 和 hooks logs" | **off-domain**（zhulong agent harness 自检） | n/a | 不可造（off-domain：调试 agent 自身非 EDA 用户任务）|
| b2zwp | 6 | t0002987 | "检查一下你自己的harness架构" | off-domain | n/a | 不可造（off-domain）|
| ogyui | 5 | t0002987 | "检查一下你自己的harness架构" | off-domain | n/a | 不可造（off-domain）|
| qhg0k | 6 | t0002987 | "完整检索你自己的代码结构" | off-domain | n/a | 不可造（off-domain）|
| 7cdxg | 5 | t0002987 | "检查一下你自己的harness架构" | off-domain | n/a | 不可造（off-domain）|
| 7f29h | 7 | t0002987 | "盘点烛龙出现这个问题可能的原因" + "回答结束后仍输出重复不完整内容...日志未记录" + "你自己可以进行代码排查吗" | off-domain（zhulong agent 重复输出 bug 诊断） | n/a | 不可造（off-domain）|
| m273z | 7 | t0002987 | "怎么增加点log信息，当agent慢或卡的时候...指的是当前zl agent" | off-domain（zl agent 卡慢 log） | n/a | 不可造（off-domain）|
| lxajs | 7 | mike | "/home/SIM/finesim/drjqa/Matrixrun/Cosim/SystemC/DDR6+Cosim/d6 这个目录下看下 makefile 咋干啥" | **B (spice cosim)** | 弱（makefile 阅览 Q&A） | 不可造（wrong-shard B）|
| 0mx9i | 7 | mike | "logic_cosim 这个路径下可以执行 shell 命令吗" | env-config + B | n/a | 不可造（env-config + wrong-shard）|
| nlwn9 | 5 | t0002441 | "who are you" / "nishishei" | **trivial（无任务）** | n/a | 不可造（无真实任务，仅问候）|
| uhrnk | 5 | t0002441 | "hello/who are you"（首 3 turn 问候，后续 28 turn；keyword virtuoso:aether:hspice） | **C/B (layout/spice)** | 未深挖 | 不可造（wrong-shard C/B，keyword 已明示）|

## 二、关键发现（修正 r689 偏差）

1. **r689 只 peek 首条 user msg 造成两类误判**：
   - **9a7jm 类**：r689 peek 首 msg "Finesim DC 不收敛" 判 "concept-Q&A 不可造"，结论方向对但**口径错**——真实域归属是 **B (spice_sim)**，应判 wrong-shard，非"concept-Q&A 无 anchor"。且此问被 t0002441 **跨 5 个 session 重复问**（9a7jm/6sh4c/qnm9e/shssw/y2mlp 逐字同），r689 表里只列了 9a7jm 一条，漏另外 4 条同源 dup。
   - **pyaether:aether:rtl cluster（6 条）**：r689 凭 keyword `pyaether:aether:rtl` 判"C-domain 倾向，非 A-pure"，方向部分对但**根因错**——真实意图是 user **t0002987（烛龙开发员）让 agent 检查它自己的 harness 架构/构建流程/重复输出 bug**，属 **off-domain**（agent infra 自检），不是 C-domain layout 工作。`rtl/pyaether/aether` keyword 是 agent 读自身代码产生的噪声，非用户 EDA 任务。m273z 同类（zl agent 卡慢 log）。

2. **r689 表中"18 条 mc 5-9 band"的真实构成**：
   - 5 条 Finesim DC 概念 Q&A（B 域 dup）
   - 7 条 zhulong agent harness 自检/调试（off-domain，全 t0002987）
   - 2 条 Finesim/cosim Makefile+shell 能力 Q&A（B 域/env）
   - 1 条 trivial 问候（nlwn9）
   - 1 条 C/B 域 layout/spice（uhrnk）
   - 2 条 r690 已结案（l0x4z 不可造 + ai203 已 B）
   - **= 0 条真 A-domain (digital/verification/pnr_signoff/eda_other) 用户任务**

3. **r689 的 awk A-domain 关键词过滤过捕**：因 t0002987 的 agent 自检 session 让 agent read 自身 pyaether/aether/rtl 代码，产生 `rtl/pyaether/aether` keyword 假阳性命中 A-domain 过滤词。真实意图与 EDA design-flow 无关。

## 三、mc≥5 11-15 令止损判据复核

11-15 令止损唯一判据 = "mc≥5 候选里，有无能忠实还原用户意图、且能写出可判分 check() 的任务"。

**hfhds201（.75 本机唯一可达主机）mc≥5 A-domain**：
- mc≥10：0 fresh（全 ledgered，r689 已用 11-16 快照确证）
- mc 5-9 band：18 条，本轮穷尽重审 **0 条真 A-domain 可造**（5 B-dup + 7 off-domain + 2 B/env + 1 trivial + 1 C/B + 2 r690 已结案）
- ⇒ **hfhds201 本机 mc≥5 A-domain 可达池在「能忠实还原意图且可判分」口径下确证耗尽**（用 11-16 最新快照 + 逐条 user-msg 重审举证，非拿 mc≥10 旧证据）

**⚠️ 但 auto-stop（回退 shard_mc.A=10）本轮不触发，理由**：
- 2026-11-15 令 §II auto-stop 纪律要求「换 mc≥5 口径重新举证，不能拿旧证据说 mc≥5 也枯竭」。本轮已对 **hfhds201 本机** 完成 mc≥5 举证（0 viable）。
- 但 **r679 已解除远程 SSH infra-block**（hfeg0pkn005/002/pgn145/plg95/pkn001 全 OK），而 **r678 列出的 18 条 fresh truly-A 候选全在远程主机**（hfeg0pkn*/pfn*/pgn*/pjn*）。r685-r691 全部只审 hfhds201 本机，**远程 A-domain fresh 候选在 mc≥5 口径下尚未重审**。
- 故「mc≥5 全可达池耗尽」**尚未举证**。触发 auto-stop 须先穷尽远程 A-domain fresh 候选。shard_mc.A **维持 5**。
- 连续 0-case（mc≥5 口径）= 承 r690 状态 + 本轮 +1 = r685/r688/r689/r690/r691（5 轮，超 3 轮触发线），但其中 r685-r691 均只审本机/infra，未触远程，故「3 轮 0-case」计数不构成有效 auto-stop 证据（判据要求候选确证无牙，非仅计数）。

## 四、下轮建议（r692）

1. **优先**：经 eda_flow SSH 审远程 A-domain fresh 候选（r678 的 18 条，现已可达）。`trace_ledger.py --shard A next` 取 fresh 远程 top-5 → 逐条抓 messages.json + peek 真实意图 → 凡 digital/verification/pnr/eda_other 且有 evidence anchor 者 claim+深读+合成。
2. 若远程 A-domain fresh 在 mc≥5 口径下亦 0 viable，**方**在 MEMORY 记「mc≥5 扩池实测无效 + 远程/本机双举证数据依据」并触发 auto-stop 回退 shard_mc.A=10，转向 waveview 协作收尾 / 论文 Ntasks 追平 / 跨 shard 卫生。
3. 本轮 0-case 理由：候选池重审（2026-11-15 最高优先令 §II「候选池重审优先于继续造题」）+ fresh-agent 40min 预算不足保单条 case 质量闸门（§4.3 ≥8 + §4.9 + negative）。🚫 未推 incomplete 入 jsonl。

## 五、纪律

- 🚫 未推 incomplete case 入 jsonl（A.jsonl 350 不变）。
- 🚫 不动 summary_stats.json / shard_mc 配置（本轮非配置变更轮，仅可达性穷尽重审）。
- 🚫 不改别 shard 文件。
- ✅ 台账无新增 claim（18 条均不可造或已结案，无 claim 必要；off-domain/B-domain 不入 A 台账）。
- ✅ eda_flow session 已 close（keep=false）。
- ✅ 审计结论逐条可溯 trace 原文（user / session_file / user msg verbatim 见上表）。
