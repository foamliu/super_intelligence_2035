# BAIZE_DESIGNFLOW_BENCH_TASK.md — 设计流 Benchmark 任务书（2026-10-30 重构版）

> **本文件由运维维护（agent 只读）**。运行时状态写 `MEMORY_DESIGNFLOW.md`、`EXPERIMENTS_DESIGNFLOW.md`、`daily-memories-designflow/`。
> 旧版全文（即时令 VII/VIII/IX/X/XI/XII、运维增补 I–IV、收尾铁律、体积规程）已**原文归档** → `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档批次 48」。本版把上述指令**按主题融合**，不再按时间堆叠。

## 0. 目标（一句话）

用 `.75` 内网 **698 台机 / 2,850 用户 / 52,698 会话（24,085 条 IC-EDA 命中）** 的真实 cline 轨迹，构建「设计流编排」评测集；**难度必须校准到 pi-SUT 通过率 20–30%**——不是"能跑通就算过"。

## 1. 红线（不可协商）

1. **真实 trace 才有资格**：每条 case 必带 `metadata.trace_source{user, host, session_file, match_count, real_task_summary}`。没有真实 trace 的 case 一律删除，🚫 不许改个名字保留。
2. **不脱敏（全产物）**：`user` / `host` / `session_file` / `/home/<user>` 路径 / `prompt` / `attachments` / 深读笔记 / 日报 / MEMORY **一律保留原值**；只有 **key / token / 密码** 需掩码。🚫 prompt 里出现"脱敏""不要出现真实用户名"字样视为违规。
3. **单一 jsonl**：只往 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl` 追加；🚫 新建 jsonl（>500 条才按 `metadata.domain` 拆 4 个）。
4. **只读纪律**：对 698 机只 `find`/`ls`/`cat`/`head -c`/`awk`/`python3` 只读；🚫 写目标机、🚫 `rm`/`tee`/`>`；🚫 本机自扫；🚫 lineage 自审计 / §X 递归。
5. **git 双仓**：workspace + 日报 → `super_intelligence_2035` **main**；用例产物 → `EDA-Flow-Bench` **master**；🚫 `git add -A`。
6. **体积**：本 TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限按 §8 归档（原文搬 ARCHIVE，留 1 行指针）。

## 2. 环境速查

| 项 | 值 |
|:--|:--|
| workspace | `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/` |
| 用例仓库 | `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（jsonl / assets / reference） |
| 历史快照 | `EDA-Flow-Bench/agent_workspace/designflow/`（bench_v0.1~v0.50，只读，不迁） |
| 运行时 cwd | `/nasdata/app.e0031982/code/EDA-Flow-Bench/` |
| 沙盒入口 | `eda_flow` MCP `http://127.0.0.1:18891/mcp` → `.75`（`hfhds201` / `10.129.32.75`）`run_commands`·`run_code`·`read_file`·`write_file` |
| 扫描结果 | `.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`（列：`ip host user session_file match_count keywords tools`） |
| 评测框架 | `./RUN_EVAL.sh --design-flow` / `--design-flow-agent`；`scripts/run_design_flow_batch.py`；`config.yaml`；`docs/design_flow_session_backend.md`（§3 接口 / §9 判分两步）；`docs/设计流Benchmark-{测试用例编写指南,框架改进设计文档}.html` |
| pi（被测） | `pi` 1.4.0，provider `cxmt` / `deepseek-v4-pro-cloud`，已配 `eda_flow` MCP。调用：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`（Node 22 需在 PATH：`export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH`） |
| 日报 | `cd <benchmark>/designflow && python3 gen_daily_report.py` → `doc/ZhuLong_DAC2027/reports/report_benchmark_MM_DD.html`（运维已加独立「用户」列，**别再重复改**） |

**命令模板（只读抓 trace）**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "ls /home/*/.cline/data/sessions/*.messages.json | head -20"
```
> `.75` 已对 **697/698** 台免密（`e0031982` 身份）。**分批 5–10 台/次**，别一次扫 698 台（会超时）。

**三个已知坑（别再踩）**
1. **GitHub 假阴性**：`curl https://github.com` 在剥掉 proxy 的环境里返回 `000`，但 `git push` 走 `git config --global http.proxy` 仍可通。**判据用 `git ls-remote origin HEAD`，不要用 curl**。（确需代理：`git config --global http.proxy http://172.19.92.23:13128`）
2. **`write_file(content_base64=...)` 会腐蚀内容**（`$dA` → `$d\x01`）：一律用 plain `content` 字符串，或 `run_commands` 里 `base64 -d` 在本机解码。
3. **`ssh` 在 eda_flow 里会 hang**：命令前加 `</dev/null`（`-n` 反而会断 stdin pipe）。

## 3. 用例契约（proper `design_flow`）

```text
mode:        "design_flow"
entry_point: "outputs/submit.zip"
test:        "def check(deliverable, workdir): ..."   # 双参，返回通过 / 抛异常失败
prompt:      自然语言，写真实场景（真实用户名/路径/工具/指标），不是函数签名题
attachments: [assets/<task_id>/...]                    # 真实输入文件
metadata:    { trace_source{...}, domain, test_rationale }
```
🚫 不带 `lang` / `host` / `runtime`；🚫 不写"实现 `xxx(args)->dict`"这类抽象题。

**单轮闭环 + 交付定义（DoD）**

一轮 = 一条 case 从选料到落库，**不要拆成两轮**：
`选料 → 深读 → 合成 → 自验(ref PASS + §4.9 三假提交 FAIL) → 追加 jsonl → 日报一行`

- **深读是硬闸门，但不是独立的一轮**：必须先解析完整对话流（`scp` `messages.json` → user 意图 / assistant 工具链 / 关键产物 → `designflow/trace_deepreads/<sid>_<主题>.md`）才允许合成；已有笔记可直接复用，不重复深读。
- **DoD（交付定义）**：1 条 case 通过自验并写进 `EDA-Eval-DesignFlow.jsonl` 才算交付；**深读笔记是中间产物，不算交付**。
- **每轮至少交付 1 条 case**；预算（`AGENT_TIMEOUT` 45 min，单条约 35–45 min）内有剩余就继续下一条，**不设上限**。
- **唯一例外**：单条 trace 过大（>2MB 或 >600 msgs）允许本轮只深读，但**下一轮必须先交付 case**，心跳记 `DEBT: 1 deepread 未合成`；🚫 禁止连续两轮只深读。
- 选 trace：`summary.tsv` 按 `match_count` 降序，排除已用 / 已清理 session，优先**命中最多且尚无 case 的 domain**。

## 4. 判分质量（"有牙"，缺一不可）

1. **隐藏输入 B**：A 给 SUT 看，B 放 `assets/<id>/hidden/` + `hidden_manifest.json`，**不进 SUT 沙箱**；`check()` **只跑 B**，B 与 A 在规模/取值/结构上必须不同（不是换文件名）。
2. **真跑候选**：≥1 个条件用 `subprocess` 在 B 上执行候选脚本，断言**输出结构**（解析成字段/拓扑/计数再比较），不是文本相似。
3. **≥8 个独立条件**，每个单独可 FAIL；🚫 "仅成员名 / 仅子串出现"式断言。
4. **负样本入库**：`reference/<id>/negative/` ≥2 个错解（naive / always-XXX stub）+ `negative_selftest.py`，一次跑完必须**全 FAIL**；每轮抽查 1 条重跑。
5. **随机化**：在 B 上随机抽子集（net / signal / 行），3 个随机种子跑 3 次结论一致；🚫 把期望值硬编码成固定串。
6. **`metadata.test_rationale` = 逐条断言清单（不是摘要）**：格式固定 `k 条断言：①<验什么> ②<验什么> …`，**一条对应 `check()` 里一个可独立失败的条件**，写清"对象 + 判定"。
   - ✅ `7 条断言：① zip 内 5 个文件齐全 ② mac4.v 有 module mac4 且端口 clk/rst_n/acc0 齐全 ③ 累加为 32-bit 有符号饱和（边界 0x7fffffff/0x80000000） ④ sim_mac4.log 含 MAC4_SIM_PASS 且无 MAC4_SIM_FAIL ⑤ …`
   - 🚫 废话：`解 zip 校验 3 文件`、`校验交付件完整性`、`断言内容达标`
   - 🚫 实现细节：`raise AssertionError(...)`、`zipfile.ZipFile(...)`、`z.read(...).decode(...)`
   - 自检：`k` 必须等于 §4.3 要求的独立条件数（≥8）；两者对不上 = 未完成。
7. `check()` 在**独立临时目录**解 zip；🚫 在 SUT workdir 留 `__chk`。
8. **泄漏隔离**：SUT 沙箱不得包含 `benchmarks/EDA-Eval-DesignFlow/`（`reference/`、jsonl、`test` 字段）；结论写 MEMORY 一行。
9. **退化提交回归**：每条 case 必须让 (a) 空壳 (b) 只 print 期望串 (c) 参考解删核心 三种假提交**全部 FAIL**；任一 PASS ⇒ 该 case 判分不合格，限期整改或下线。

## 5. 难度校准（立即生效）

| 层 | 定义 | 配额 |
|:--|:--|--:|
| L1 | 离线 Python 复刻（读附件写脚本） | **≤30%** |
| L2 | 真跑沙盒工具（calibre LVS/DRC、Virtuoso、PrimeTime、VCS，经 eda_flow / .75） | **≥50%** |
| L3 | 多工具链路 + 修复 + 回归（DRC 179→0、LVS 干净 CORRECT、ERC 全清） | **≥20%** |

- 新建 case **只做 L2 / L3**；L1 仅用于补牙维护。
- 总样本 **<30 条前不报通过率**，只写"已跑 n 条中 x PASS"（6 条算百分比没有统计意义）。
- 滚动窗口（最近 20 条已跑）目标 **20–30%**：
  - **>50% ⇒ 自动判"太简单"**：上隐藏输入 B / 加条件 / 换更难 trace，下轮重跑；
  - **<10% ⇒ 先查 `check()` 误判**（ref 是否真能 PASS），再考虑降难；
  - 20–30% ⇒ 保持。
- 心跳每轮写一行：`🎯 通过率: 最近20条 x/20 = y%（目标20–30%）`。

## 6. 每轮流程

1. 选 trace → 深读（有笔记就复用）→ 合成（`assets/` `reference/` `hidden/` `negative/`）。
2. 自验：`reference/` 参考解跑 `check()` 必 PASS；§4.9 (a)(b)(c) 三假提交必 FAIL；`negative_selftest.py` 全 FAIL。
3. pi 实跑：`designflow/pi_debug_status.jsonl` 追加一行，记 `pi_model / pi_thinking / pi_dur_sec / pi_verdict / ref_check`。
4. 追加 jsonl → 日报：`python3 designflow/gen_daily_report.py`，中文单文件 HTML，含「用户」列与 `k 条断言` 清单。
5. 难度回路：按 §5 判定"加难 / 保持 / 查判分"，结论写进当日日报的"阻塞/下一步"。
6. **有余量 → 回到第 1 步做下一条**（一轮交付 ≥1 条，上不封顶）。

## 7. 当前基线（每轮只更新这一行，不堆历史）

`11 条 proper（10 域）· 已跑 6 条 = 6 PASS · 6 trace_deepreads · test_rationale 断言清单 0/11 · 目标通过率 20–30%`
明细看日报 `reports/report_benchmark_MM_DD.html`；历史结论看 `EXPERIMENTS_DESIGNFLOW.md`。
> 现存 11 条的 `test_rationale` 本轮内全部改写成 `k 条断言：①…`（k = 该 case `check()` 的独立条件数）。

## 8. 收尾（轻量结账，不是每轮做全套）

> 收尾是"结账"，**不是产出单位**：一轮可以交付多条 case，时间将尽时结账一次即可。

0. **体积自检**：TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限先把已闭合块**原文**搬 `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针），搬前 `git pull --rebase --autostash`，🚫 不改小节编号/标题。数字抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB`。
1. **心跳（轻）**：`MEMORY_DESIGNFLOW.md` 顶部快照**只改变化的几行** + **追加 1 行流水**（三口径 + `🎯 通过率` + `DEBT`）；🚫 每轮重写整份快照。
2. **日记忆**：`daily-memories-designflow/<YYYY-MM-DD>.md` **当天首轮创建，之后只追加**。
3. **提交**：**每 30 分钟或每 3 条 case 提交一次**（loop 本身每 30 分钟兜底）；本轮结束前必须提交，🚫 把工作留在工作树过夜。双仓命令：
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/designflow \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
           doc/ZhuLong_DAC2027/reports
git commit -m "designflow #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow
git commit -m "designflow #<轮次>: <一句话>" && git push origin master
```
4. **闭环自检**：`git status -sb` 无 ahead/behind；push 失败重试 1 次并记报错原文。

> ⏱ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

## 9. 待确认（未确认前按默认走）

- Benchmark 是否对外（默认：先内部）
- 是否允许主动扫描 698 机（默认：否，只被动只读发现）

## 10. 并发协作（多进程时的唯一契约）

多进程共用**一份工作树**，靠"文件所有权"消除冲突，不靠事后修 jsonl：

| 角色 | 只写（独占） | 禁止 |
|:--|:--|:--|
| `scout` | `designflow/claims/` `designflow/candidates/` | 不建 case、不改 jsonl、不 commit |
| `deepread` | `designflow/trace_deepreads/` | 不建 case、不改 jsonl、不 commit |
| `synth` | `designflow/cases_staging/<task_id>/` | 不改主 jsonl、不 commit |
| `teeth` | `designflow/governance/teeth/` | 不改 case 内容、不 commit |
| `integrator` | 主 jsonl / `reports/` / MEMORY / git commit+push | 不替 producer 写产物 |

- **领取协议**：出题前先 `mkdir designflow/claims/<sid>.claim`（原子操作，失败 = 已被抢）；claim 内写 `owner / 时间 / task_id`；**>2h 无产出自动回收**（integrator 负责删）。
- **只有 `integrator` 能 commit/push**；producer 的产物以 `cases_staging/<task_id>/` 交付，由 integrator 跑完 §4 自验（ref + 三假提交 + negative）后才合并进主 jsonl。
- **同一角色只能起一份**（脚本用 `/tmp/designflow_loop_<ROLE>.lock` 自锁），启动：
```bash
export ROLE=synth      # solo | scout | deepread | synth | teeth | integrator
setsid bash <benchmark>/designflow_bench_loop.sh > /tmp/df_$ROLE.log 2>&1 < /dev/null &
```
- 建议起步配比：`1 deepread + 2 synth + 1 integrator`（teeth 先由 integrator 兼）；观察 12h 后若 evaluator 排队 >5 条再单独起 `teeth`。

---

> ⚠️ 本文件为**只读指令文件**，agent 禁止修改；有异议写进 MEMORY 并存疑执行。

