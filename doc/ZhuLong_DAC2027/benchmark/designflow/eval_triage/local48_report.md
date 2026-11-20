# Cline 轨迹解剖报告（local48，pilot 子集）

> 本文件的 §1–§7 由 `trace_anatomy.py` **机器生成**，所有数字均可在同一命令下复现。
> 生成命令：`python trace_anatomy.py --glob "<cline_eval>/*/cline_session.jsonl" --out local48_metrics.json --md <report>.md`
> argv: `trace_anatomy.py --glob ../cline_eval/*/cline_session.jsonl --out local48_metrics.json --md local48_report_auto.md --quiet`
> 生成时间(UTC)：2026-11-10T11:40:13Z ｜ python 3.10.11 ｜ 本机总耗时 **9.25 s**
> 解析器：trace_anatomy.py v1.0.0（stdlib only）

## 1. 覆盖率与规模

| 项目 | 值 |
| --- | --- |
| 匹配到的 case 目录数 | 48 |
| 有非空 `cline_session.jsonl` | 47 |
| 有 session 文件但 0 字节 | 1 |
| 无 session 文件 | 0 |
| session 总字节 | 217309001 (207.2 MB) |
| session 总行数(事件数) | 1210060 |
| 解析失败行数 | 0 |
| 时间跨度(首 ts ~ 末 ts) | 2026-11-03T00:05:43.813Z ~ 2026-11-06T14:31:45.329Z |
| outputs/ 非空文件总数 | 175 |
| assets/ 文件总数 | 255 |

## 2. 分布统计（全部 case，None 值已剔除）

| 指标 | n | median | p25 | p75 | mean | min | max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wall_seconds (秒) | 47 | 1047.4 | 551.6 | 1494.7 | 1043.7 | 54.2 | 2564.5 |
| n_iterations | 48 | 20.5 | 9.0 | 32.5 | 22.5 | 0.0 | 69.0 |
| n_tool_calls | 48 | 26.5 | 13.8 | 38.0 | 28.6 | 0.0 | 97.0 |
| n_output_files | 48 | 3.0 | 2.0 | 3.2 | 3.6 | 0.0 | 17.0 |
| session_lines | 48 | 22520.0 | 11484.8 | 39323.2 | 25209.6 | 0.0 | 65903.0 |
| n_reasoning_chunks | 48 | 21939.0 | 10887.0 | 38381.0 | 24694.2 | 0.0 | 65379.0 |
| n_text_chunks | 48 | 404.5 | 25.2 | 470.5 | 302.9 | 0.0 | 789.0 |
| n_asset_files | 48 | 3.5 | 3.0 | 6.2 | 5.3 | 0.0 | 23.0 |

说明：分位数用线性插值（与 numpy 默认 `linear` 口径一致），实现见 `percentile()`。`n_reasoning_chunks` / `n_text_chunks` 计的是**流式增量 chunk 数**，不是语义段落数——模型按 token 流式吐字，一个句子会被拆成几十个 chunk，故量级很大。

## 3. 工具使用（top 15）

| # | toolName | 调用次数 | 调用占比 | 出现的 trace 数 (共47) | 类型 |
| --- | --- | --- | --- | --- | --- |
| 1 | `read_files` | 395 | 28.8% | 47 | 内置 |
| 2 | `eda_flow__run_commands` | 247 | 18.0% | 34 | MCP |
| 3 | `editor` | 210 | 15.3% | 38 | 内置 |
| 4 | `run_commands` | 103 | 7.5% | 47 | 内置 |
| 5 | `eda_flow__write_file` | 101 | 7.4% | 30 | MCP |
| 6 | `search_codebase` | 84 | 6.1% | 33 | 内置 |
| 7 | `pyAether_MCP_server__run_code` | 77 | 5.6% | 5 | MCP |
| 8 | `eda_flow__open_session` | 43 | 3.1% | 38 | MCP |
| 9 | `eda_flow__read_file` | 36 | 2.6% | 9 | MCP |
| 10 | `pyAether_MCP_server__search_apis_by_keyword` | 16 | 1.2% | 2 | MCP |
| 11 | `eda_flow__list_files` | 13 | 0.9% | 8 | MCP |
| 12 | `pyAether_MCP_server__search_apis` | 13 | 0.9% | 2 | MCP |
| 13 | `fetch_web_content` | 11 | 0.8% | 5 | 内置 |
| 14 | `pyAether_MCP_server__get_api_details` | 11 | 0.8% | 2 | MCP |
| 15 | `eda_flow__declare_done` | 5 | 0.4% | 5 | MCP |

| 汇总 | 值 |
| --- | --- |
| 不同工具种类数 | 19 |
| 工具调用总数 | 1371 |
| MCP 类调用数（名字含 `__`） | 565 |
| 非 MCP 内置调用数 | 806 |
| **MCP 调用占比** | **41.2%** |
| 字面 `mcp__` 前缀调用数 | 0 |

MCP 判定口径：Cline 采用 `<server>__<tool>` 命名，故 `"__" in toolName` 即视为 MCP server 工具。本批实际出现的前缀只有 `eda_flow__` 与 `pyAether_MCP_server__`，**没有任何工具以字面 `mcp__` 开头**（见上表最后一行）。此外 `tool_call` hook 事件不含工具名，工具名只能从 `agent_event.content_start.contentType=="tool"` 取。

## 4. produced_output 分组对比

分组定义：produced_output = outputs/ 下存在至少 1 个字节数>0 的文件（仅代表产物存在，不代表正确）

| 组 | n | median 工具调用数 | median wall_seconds | median n_output_files |
| --- | --- | --- | --- | --- |
| produced_output = true | 42 | 26.5 | 1046.5 | 3.0 |
| produced_output = false | 6 | 28.0 | 1629.4 | 0.0 |

⚠️ **样本极小（false 组仅 6 个），且两组按定义互为补集（n_output_files=0 必然落在 false 组），因此该对比只能当作“行为差异线索”，不能做显著性推断，也不能外推到全量任务集。**
## 5. 终止形态分布（ended_with_tag）

| ended_with_tag | trace 数 | 含义 |
| --- | --- | --- |
| `aborted` | 3 | 有 `run_aborted`（外部/本地中断）或 finishReason=aborted |
| `completed` | 27 | 有 `run_result` 且 `finishReason=completed`（正常收尾） |
| `empty_session` | 1 | `cline_session.jsonl` 为 0 字节 |
| `error` | 6 | 无 run_result，末条为 `error` 事件（报错收尾） |
| `no_terminator` | 11 | 无任何终止记录（采集被截断，最后一行停在 streaming 中途） |

注意：`no_terminator` 不等于“失败”。它只说明**归档被截断**（harness 侧未落 run_result），因此这批 trace 的 wall_seconds 是**观测下界**，真实运行时长可能更长。

## 6. token 可得性

| 项目 | 值 |
| --- | --- |
| 有 `run_result.aggregateUsage` 的 trace | 30 / 48 |
| 有任意 token 数字的 trace | 47 / 48 |
| 可得 trace 的 outputTokens 之和 | 2755824 |
| 可得 trace 的 inputTokens 之和（aggregate 口径） | 45714922 |

**usage 事件实测字段结构**（本节最需要写清的一点）：

```json
{"ts":"2026-11-03T05:38:27.285Z","type":"agent_event","event":{"type":"usage",
  "inputTokens":10797,"outputTokens":110,
  "totalInputTokens":10797,"totalOutputTokens":110,"totalCost":0}}
```

```json
{"ts":"2026-11-04T23:54:25.712Z","type":"run_result","finishReason":"completed","iterations":11,
  "usage":{"inputTokens":602283,"outputTokens":57143,"cacheReadTokens":0,"cacheWriteTokens":0,"totalCost":0},
  "aggregateUsage":{"inputTokens":602283,"outputTokens":57143,"cacheReadTokens":0,"cacheWriteTokens":0,"totalCost":0},
  "durationMs":608125,"model":{"id":"deepseek-v4-pro-cloud","provider":"openai-compatible"}}
```

- `usage` 事件：`inputTokens` / `outputTokens` / `totalInputTokens` / `totalOutputTokens` / `totalCost`，**没有 cacheReadTokens / cacheWriteTokens**；它是**每次请求**的用量，直接求和会重复计入上下文。
- `run_result.aggregateUsage`：`inputTokens` / `outputTokens` / `cacheReadTokens` / `cacheWriteTokens` / `totalCost`，是**整个 run 的权威总量**。
- `tokens` 字段口径：优先 `run_result.aggregateUsage`；缺失时退回 usage 事件求和，并在 `tokens_source` 标注 `sum(usage events) PER_REQUEST_SUM_NOT_TOTAL`。48 份里只有 30 份有可信总量，故本报告**不给 token 分布统计**，避免跨口径混算。

## 7. 逐 case 明细

| case_id | bytes | lines | wall_s | iters | tools | out_files | submit_zip | ended | err_sig | tokens_out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AprLogAudit-001 | 3605987 | 20088 | 608.2 | 11 | 14 | 3 | 0 | completed | 7 | 57143 |
| AprStampFix-001 | 5595383 | 31508 | 1170.7 | 25 | 35 | 5 | 0 | completed | 0 | 78262 |
| AutoCellTclFlow-001 | 4265699 | 23073 | 1489.4 | 45 | 64 | 2 | 0 | error | 0 | 66999 |
| CalibreOpen1Fix-001 | 1055722 | 4526 | 181.9 | 10 | 13 | 3 | 0 | completed | 1 | 12267 |
| CalibrePdf2md-001 | 7123328 | 42303 | 1490.5 | 37 | 40 | 0 | 0 | error | 0 | 106726 |
| CdlBodyMapFix-001 | 7061403 | 40384 | 1201.5 | 25 | 28 | 4 | 0 | completed | 1 | 89728 |
| CdlVbnBulkRemap-001 | 3907672 | 21967 | 619.0 | 14 | 17 | 4 | 0 | completed | 0 | 53061 |
| CombSdcGen-001 | 4409098 | 24228 | 1318.3 | 27 | 35 | 3 | 0 | completed | 0 | 60898 |
| CombSynthClean-001 | 7003698 | 39948 | 1677.7 | 31 | 40 | 3 | 0 | completed | 0 | 86614 |
| CovFMFlow-001 | 9773095 | 57635 | 1793.9 | 44 | 71 | 17 | 0 | no_terminator | 0 | 135031 |
| DCDirSwitch-001 | 3444134 | 18320 | 616.7 | 20 | 26 | 3 | 0 | completed | 0 | 42353 |
| DCSynth-001 | 2092621 | 10503 | 366.0 | 10 | 16 | 3 | 0 | completed | 0 | 23977 |
| DRCDeckOpt-001 | 7187730 | 40601 | 1479.0 | 25 | 27 | 2 | 0 | completed | 0 | 88632 |
| DcDontuseGen-001 | 1265450 | 7528 | 222.7 | 6 | 7 | 3 | 0 | no_terminator | 0 | 14829 |
| DcUpfDiag-001 | 3935467 | 21103 | 965.7 | 20 | 29 | 3 | 0 | completed | 2 | 62515 |
| DeadLoopScan-001 | 8810085 | 49363 | 1761.3 | 48 | 60 | 2 | 0 | error | 0 | 112343 |
| DelPgLib-001 | 1331458 | 6705 | 297.6 | 6 | 7 | 2 | 0 | completed | 0 | 14481 |
| Digital-021 | 5152105 | 30053 | 1046.5 | 15 | 19 | 3 | 0 | completed | 0 | 65794 |
| Digital-022 | 1054226 | 3986 | 202.7 | 16 | 15 | 3 | 0 | completed | 0 | 15238 |
| DrcDocConvert-001 | 7696554 | 46770 | 1798.8 | 27 | 29 | 3 | 0 | no_terminator | 0 | 101286 |
| FindPcells-001 | 7437375 | 39264 | 2564.5 | 69 | 97 | 2 | 2 | completed | 1 | 96754 |
| FlatNet-001 | 6377986 | 37025 | 1162.9 | 23 | 26 | 3 | 0 | completed | 0 | 90893 |
| FlowGuide-001 | 4972113 | 26835 | 1046.0 | 38 | 38 | 3 | 0 | completed | 1 | 71966 |
| IMPSR1253VddPmFix-001 | 3446111 | 19008 | 713.2 | 9 | 15 | 3 | 0 | no_terminator | 0 | 37187 |
| ItfCompare-001 | 6648521 | 39501 | 1799.0 | 37 | 42 | 2 | 0 | no_terminator | 0 | 85232 |
| LibPVT-001 | 493187 | 3092 | 112.4 | 4 | 6 | 4 | 0 | no_terminator | 0 | 2820 |
| OstrichSpefRCFactor-001 | 455026 | 2733 | 131.5 | 6 | 9 | 0 | 0 | aborted | 0 | 6209 |
| PTSignoff-001 | 1889686 | 7198 | 276.1 | 7 | 11 | 5 | 0 | completed | 2 | 16890 |
| PTStaFlowBuild-001 | 4584081 | 26774 | 1498.9 | 38 | 61 | 13 | 0 | error | 0 | 72610 |
| PTVersionRecon-001 | 3204570 | 16194 | 591.0 | 19 | 20 | 2 | 0 | completed | 0 | 36755 |
| PdkDirSizeScan-001 | 0 | 0 | — | 0 | 0 | 2 | 0 | empty_session | 0 | — |
| PortCatch-001 | 3662586 | 19535 | 788.5 | 17 | 20 | 3 | 0 | completed | 0 | 48556 |
| PyShebangFix-001 | 2402799 | 11812 | 512.2 | 9 | 13 | 3 | 0 | completed | 1 | 28726 |
| QualibTimingFix-001 | 9172445 | 54869 | 2281.5 | 50 | 52 | 0 | 0 | error | 0 | 88633 |
| RcmaxTreeCompare-001 | 4094999 | 21963 | 1039.2 | 32 | 34 | 2 | 0 | completed | 2 | 58483 |
| RedhawkGenInputs-001 | 1120874 | 6896 | 231.0 | 5 | 6 | 0 | 0 | aborted | 0 | 13906 |
| RunsetVer-001 | 8141734 | 49907 | 1797.5 | 22 | 22 | 0 | 0 | no_terminator | 0 | 81208 |
| SPFCoupling-001 | 10855748 | 65903 | 1799.0 | 21 | 27 | 2 | 0 | no_terminator | 0 | 133069 |
| STAFlow-001 | 6988050 | 34001 | 1386.7 | 37 | 59 | 16 | 0 | completed | 0 | 82743 |
| SiOutWarnDiag-001 | 5091939 | 28609 | 1743.2 | 25 | 29 | 2 | 0 | completed | 2 | 70710 |
| SubcktExtract-001 | 3382482 | 18030 | 629.3 | 8 | 13 | 3 | 0 | aborted | 0 | 41639 |
| SweepMeasFix-001 | 4879573 | 26808 | 1058.0 | 17 | 27 | 4 | 0 | completed | 0 | 61355 |
| SweepParallel-001 | 9087075 | 42548 | 1398.9 | 42 | 49 | 3 | 1 | no_terminator | 0 | 96626 |
| SynLintFlow-001 | 4824628 | 24937 | 1047.4 | 9 | 20 | 15 | 0 | completed | 0 | 53978 |
| TLEFRules-001 | 1284593 | 8165 | 236.5 | 5 | 6 | 4 | 0 | no_terminator | 0 | 3133 |
| TimingECO-001 | 3044008 | 18088 | 1768.4 | 34 | 34 | 0 | 0 | error | 0 | 39734 |
| Verification-001 | 113426 | 586 | 54.2 | 6 | 5 | 5 | 0 | no_terminator | 0 | 2016 |
| WLMMultibit-001 | 3882471 | 19187 | 1080.4 | 30 | 38 | 3 | 1 | completed | 0 | 45816 |


## 8. 字段口径定义

| 字段 | 定义 |
| --- | --- |
| `session_bytes` | `cline_session.jsonl` 文件字节数 |
| `session_lines` | 非空行数（= 解析到的事件对象数）；`session_bad_lines` 为 JSON 解析失败数（本批 0） |
| `wall_seconds` | 最后一条事件 `ts` − 第一条事件 `ts`（ISO8601 UTC） |
| `n_iterations` | `agent_event.iteration_start` 计数；`n_iterations_run_result` 为 harness 自报值，用于交叉校验 |
| `n_tool_calls` | `agent_event.content_start.contentType=="tool"` 计数；`n_tool_calls_hook_xcheck` 为 `hook_event.tool_call` 计数，二者应接近 |
| `tool_histogram` | toolName → 调用次数（来自 content_start(tool)） |
| `n_reasoning_chunks` / `n_text_chunks` | `content_start` 中 contentType 为 reasoning / text 的**流式 chunk** 计数 |
| `tokens` | 见 §6 口径 |
| `submit_attempts` | 工具 `input` 序列化后匹配 `submit\.zip` 的工具调用次数 |
| `zip_mention_tool_calls` | 工具 `input` 中出现任意 `*.zip` 路径的工具调用次数 |
| `n_output_files` | `outputs/` 下文件总数（递归）；`n_output_files_nonempty` 为非空文件数 |
| `n_asset_files` | `assets/` 下文件总数（递归） |
| `produced_output` | `n_output_files_nonempty > 0`（产物存在 ≠ 产物正确） |
| `ended_with_tag` | 见 §5 |
| `error_signals` | 对 `cline_stderr.log` 全文与“最终文本语料”分别做**不区分大小写** `findall` 计数，pattern = `error` / `traceback` / `timeout` / `mcp` / `exception` / `failed` / `permission denied`；`stderr`、`text` 两组分别计数，`total` = 两组之和，`error_signal_total` = 各 pattern 的 total 之和。最终文本语料取 `run_result.text` → `done.text` → 最后一条 `text.accumulated`（**只取一份**，避免增量重复计数） |

**解析陷阱（实测发现，写下来供后续复用）**：

1. `hook_event.tool_call` / `tool_result` **没有**工具名与内容，只有 ts/agentId/taskId；工具统计必须走 `agent_event.content_start(contentType=tool)`。
2. 顶层 `type` 不止 `agent_event` / `hook_event` 两种，还有 `run_result` 与 `run_aborted`；把它们当 hook_event 处理会把 `hookEventName` 读成 None（本脚本初版就踩过）。
3. `content_start(text)` 的 `text` 是**增量**，`accumulated` 才是累计；把 `text` 逐条拼起来等价于 `accumulated`，但两者同时拼就会重复计数。
4. `content_start(reasoning)` 同理是增量，本报告只用于计数，不用来做文本统计。
5. `content_end(tool)` 才带 `output` / `durationMs`，偶尔带 `error`（工具执行失败），已单列为 `n_tool_content_end_errors`。

## 9. 局限（必须与数字一起引用）

1. **没有 judge verdict。** 本批 48 份是 11-05~11-07 pilot 归档，PASS/FAIL 判定不在本地（不在 session、不在 outputs、不在任何 sidecar 文件里）。因此本报告**只能给行为学指标**（工具调用、时长、产物是否存在），**不能给通过率、不能做“为什么 PASS/FAIL”的归因**。下文凡出现“成功/失败”含义的地方，指的都是 `produced_output`（产物文件是否存在），不是判定结果。
2. **produced_output 是极弱的代理指标**：只要模型写了任意非空文件就为 true——写错、写一半、写垃圾都算 true；反之 false 只说明 `outputs/` 为空。
3. **样本小、非随机**：48 份是 pilot 子集，任务类型（EDA 设计流程）与 harness 配置单一，不可外推到全量集或其它模型。
4. **archive 截断**：12 份 trace 无终止记录（`no_terminator` / `empty_session` / `no_session`），对应 trace 的 `wall_seconds` 是观测下界。
5. **token 覆盖不全**：只有 30 份有 `run_result.aggregateUsage`，故未给 token 分布。
6. **`error_signals` 是关键词计数**，会把日志里正常的 `**ERROR: (CODE):` 运行输出也算进去，只适合做量级对比，不宜当失败判据。
7. **时间戳口径**：本批实测首末 ts 为 2026-11-03 ~ 2026-11-06（UTC），任务书里写的 11-05~11-07 是批次标签，二者相差 1~2 天；以本文件 §1 的实测区间为准。


---

# 附：人工撰写部分（§10–§13）

> 以下 §10–§13 由人工撰写并逐条核对过原始文件，与 §1–§9 的机器生成内容拼接成 `local48_report.md`。
> 拼接方式见 §10 命令 #6。

## 10. 复现命令与耗时（本机实测）

工作目录：`doc\ZhuLong_DAC2027\benchmark\designflow\eval_triage\`，
数据目录：`doc\ZhuLong_DAC2027\benchmark\designflow\cline_eval\`，
python 3.10.11（Windows），全部 stdlib，无 pandas/numpy。

| # | 命令 | 实测输出 / 耗时 |
| --- | --- | --- |
| 1 | `python trace_anatomy.py --selftest` | `Ran 13 tests in 0.005s` → `OK`（13/13 通过） |
| 2 | `python trace_anatomy.py --glob "../cline_eval/*/cline_session.jsonl" --out local48_metrics.json --md local48_report_auto.md` | `DONE 48 cases (47 with non-empty session) \| 217309001 bytes \| 1210060 lines \| 9.25 s`（三次运行内部计时 8.90 / 9.36 / 9.25 s，外部 Stopwatch 9.33 s） |
| 3 | 交叉校验 `sum(n_tool_calls)` vs `sum(n_tool_calls_hook_xcheck)` | **1371 vs 1371，diff = 0**（两条独立计数路径完全一致） |
| 4 | 交叉校验 `sum(n_iterations)=1081` vs `sum(n_iterations_run_result)=606` | 不等值属正常：后者只有 30 份有 run_result；单例校验见 §11 Case A |
| 5 | 统计 wall 落在 1780–1810 s 的 trace | **5 份**，见 §12 |
| 6 | `python -c "open('local48_report.md','w',encoding='utf-8').write(open('local48_report_auto.md',encoding='utf-8').read()+open('local48_report_manual_sections.md',encoding='utf-8').read())"` | 生成本文件 |
| 7 | 确定性校验：再跑一次到 `_rerun_check.json` 并逐字段比较 | `cases identical: True` / `coverage identical: True` / `tool_table identical: True`（除 `generated_at`、`runtime_seconds` 外完全可复现） |

解析吞吐：2.17 亿字节 / 121 万事件 / 8.9 s ≈ **13.6 万事件每秒**（含每行 `json.loads`）。
所有输出文件均 UTF-8 **无 BOM**（`raw[:3]==b'\xef\xbb\xbf'` → False，已校验）。

## 11. 人工抽查记录（4 例，附行号与片段）

### Case A — `EDA-Eval-DesignFlow-AprLogAudit-001`（completed；tokens 最大的一份）

解析结果：`session_lines=20088`，`n_iterations=11`，`n_tool_calls=14`，
`tool_histogram={read_files:6, eda_flow__write_file:3, editor:2, eda_flow__open_session:1, eda_flow__run_commands:1, run_commands:1}`，
`wall_seconds=608.191`，`n_output_files_nonempty=3`，`ended_with_tag=completed`。

证据 1（文件尾部 L20086–L20088，三条终止记录齐全）：
```
L20086 {"ts":"2026-11-04T23:54:25.641Z","type":"hook_event","hookEventName":"agent_end","agentId":"agent_1793835857464_9vv2ng",...}
L20087 {"ts":"2026-11-04T23:54:25.641Z","type":"agent_event","event":{"type":"done","reason":"completed","text":"Both deliverables are now written under `outputs/` ...
L20088 {"ts":"2026-11-04T23:54:25.712Z","type":"run_result","finishReason":"completed","iterations":11,"usage":{"inputTokens":602283,"outputTokens":57143,"cacheReadTokens":0,"cacheWriteTokens":0,"totalCost":...
```
对齐：`run_result.iterations=11 == n_iterations=11`；`run_result.durationMs=608125 ms` vs
`wall_seconds=608.191 s`，只差 0.066 s → wall 口径可靠。

证据 2（L33，第一条工具调用；证明 toolName/input 只存在于 content_start）：
```
L33 {"ts":"2026-11-04T23:44:23.239Z","type":"agent_event","event":{"type":"content_start","contentType":"tool","toolName":"read_files","toolCallId":"call_61b1bc7a6e3140e398c8b6d4","input":{"files":[{"path":"/nasdata/app.e0031982/.../prompt.txt"}]}}}
```

证据 3（**独立方法**交叉校验：子串计数，不走 JSON 解析）：
```
lines 20088
contentType=tool 28      # 14 content_start + 14 content_end → 14 次工具调用 ✓
read_files 12            # 6 start + 6 end                  → histogram read_files=6 ✓
run_result 1             # 1 条终止记录                      ✓
iteration_start 11       # 11 轮                             ✓
usage 11                 # 11 次 API 调用
reasoning chunks 19581   # 19570 content_start + 11 content_end → 解析器取 19570 ✓
text chunks 414          # 404 content_start + 10 content_end   → 解析器取 404  ✓
```
最后两行暴露一个**口径要点**：子串计数会把 `content_end` 里重复出现的 `contentType` 也算进去，
解析器只数 `content_start` 才是 chunk 数；差值恰好等于该 trace 的 `content_end` 条数（可自证）。


### Case B — `EDA-Eval-DesignFlow-Verification-001`（no_terminator；token 走 fallback 分支）

解析结果：`session_lines=586`，`n_iterations=6`，`n_tool_calls=5`，`wall_seconds=54.158`，
`n_output_files_nonempty=5`，`ended_with_tag=no_terminator`，
`tokens={input:63500, output:2016, cost:0.0}`，`tokens_source="sum(usage events) PER_REQUEST_SUM_NOT_TOTAL"`。

证据 1（L586 即最后一行，停在 streaming 中途，无 done/run_result）：
```
L586 {"ts":"2026-11-03T05:39:11.125Z","type":"agent_event","event":{"type":"content_start","contentType":"reasoning","reasoning":"s","redacted":false}}
```
证据 2（5 对 tool_call/tool_result hook → 5 次工具调用，与 `n_tool_calls=5` 一致）：
```
HOOK 1 agent_start
HOOK 12 tool_call    HOOK 14  tool_result
HOOK 28 tool_call    HOOK 30  tool_result
HOOK 335 tool_call   HOOK 337 tool_result
HOOK 415 tool_call   HOOK 417 tool_result
HOOK 474 tool_call   HOOK 476 tool_result
```
证据 3（usage 事件逐条，验证 fallback 求和口径）：
```
L10  inputTokens=10797 outputTokens=110
L26  inputTokens=11799 outputTokens=150
L333 inputTokens=12187 outputTokens=656
L413 inputTokens=12890 outputTokens=510
L472 inputTokens=15827 outputTokens=590
```
手算：10797+11799+12187+12890+15827 = **63500** ✓（= `tokens.input`）；
110+150+656+510+590 = **2016** ✓（= `tokens.output`）。
同时注意 `totalInputTokens` 由 10797 一路涨到 63500 —— 这就是“per-request 求和会重复计入上下文”的直接证据，
所以本报告不把它当 token 总量使用。

### Case C — `EDA-Eval-DesignFlow-PdkDirSizeScan-001`（empty_session，但 outputs 有文件）

解析结果：`session_bytes=0`、`session_lines=0`、`wall_seconds=None`、`n_tool_calls=0`、
`n_output_files_nonempty=2`、`produced_output=true`、`ended_with_tag=empty_session`。

证据 1（目录实况）：
```
cline_session.jsonl            0 B
cline_stderr.log              52 B
outputs/pdk_dir_size_check.py 9329 B
outputs/submit.zip            3584 B
```
证据 2（stderr 全文，**全批唯一**一条非 SDK 警告的 stderr，解释了 session 为何为空）：
```
run_one.sh: line 185: o-approve: command not found
```
→ agent 根本没起来（wrapper 脚本参数错误），但 `outputs/` 里有文件。
这条同时证明 **`produced_output` 与“是否真的跑过”无关**，因此绝不能把 `produced_output=true` 读成“成功”。

### Case D — `EDA-Eval-DesignFlow-SubcktExtract-001`（aborted）

解析结果：`session_lines=18030`，`n_iterations=8`，`n_tool_calls=13`，`wall_seconds=629.349`，
`n_output_files_nonempty=3`，`ended_with_tag=aborted`，`ending_detail="local_abort | aborted"`。

证据（L18030，最后一行）：
```
L18030 {"ts":"2026-11-05T11:15:06.221Z","type":"run_aborted","reason":"local_abort","message":"aborted"}
```
另两份 aborted 的 reason 是 `external_abort` + `"aborted by another client"`：
OstrichSpefRCFactor-001 L2733、RedhawkGenInputs-001 L6896。
这 3 份都是**人为中断**，不应计入“模型失败”。

## 12. 两个补充观察（均由上表数字直接推出）

### 12.1 wall≈1798 s 的 5 份 no_terminator —— 疑似采集侧 30 min 上限

| case | wall_seconds | ended_with_tag |
| --- | --- | --- |
| ItfCompare-001 | 1798.989 | no_terminator |
| SPFCoupling-001 | 1798.951 | no_terminator |
| DrcDocConvert-001 | 1798.779 | no_terminator |
| RunsetVer-001 | 1797.545 | no_terminator |
| CovFMFlow-001 | 1793.897 | no_terminator |

5 份 trace 的 wall 全部落在 1793.9–1799.0 s（彼此相差 < 6 s），且**全部**是 `no_terminator`。
这与“归档在固定 1800 s（30 min）处被截断”高度一致。但注意这是**相关性**：
11 份 no_terminator 里只有这 5 份贴边，另 6 份（如 Verification-001 仅 54 s）是别的原因被截断；
而 wall 最大的一份 `FindPcells-001` 是 2564.523 s 且 `completed`（超 30 min 仍正常收尾）。
**因此不能断言“30 min 超时 = 失败”，只能说这批 trace 的 wall_seconds 分布在上界附近被截断污染。**

### 12.2 `error_signals` 在本批数据上几乎是空指标（必须写明）

| 组 | error | traceback | timeout | mcp | exception | failed | permission_denied |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stderr | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| text | 15 | 0 | 0 | 1 | 2 | 2 | 0 |

`cline_stderr.log` 合计 778579 字节，但 **`Error` 出现 0 次**：47 份的 stderr 第一行都是
`Warning: AI SDK Warning System: To turn off warning logging, ...`，其余全是
`DeprecationWarning: AI SDK Warning (openai-compatible.chat / deepseek-v4-pro-cloud)` + bun 栈帧。
即 **stderr 只记录 SDK 警告，不记录 agent/工具失败**。真正的失败信息在 session 内部：
`agent_event.error` 出现在 11 份 trace（合计 20 条），`content_end(tool)` 带 `error` 字段的共 27 次。
因此若要研究失败模式，应看 `n_error_events` / `n_tool_content_end_errors`，
`error_signals` 只能当“文本里有没有提到 error 这个词”的弱信号。

## 13. 红线：这份报告不能支撑的结论

1. **不能给通过率。** 48 份 trace 里没有任何 judge verdict（PASS/FAIL 不在本地），
   §1–§12 全部是行为学指标。任何“这模型在 EDA-DesignFlow 上成功率 X%”的写法都是无源之数。
2. **不能做归因。** 例如“工具调用多 → 失败”不成立：`FindPcells-001` 工具调用 97 次（全批最多）却是 `completed`；
   `produced_output=false` 的 6 份里工具调用中位数 28.0，反而略高于 true 组的 26.5 —— 样本 6 vs 42，无意义。
3. **不能外推。** 48 份 pilot 子集、单一模型（全部 `deepseek-v4-pro-cloud`）、单一 harness 配置。
4. **不能把 `no_terminator` 当失败、也不能把 `completed` 当成功**：前者是归档截断（§5、§12.1），
   后者只表示模型自己结束了 run（`finishReason=completed`），不代表产物正确。
5. **`produced_output` 只能当“有没有写文件”**：§11 Case C 里 agent 没启动、产物却存在。

（§1–§9 机器生成 + §10–§13 人工撰写；总样本 n=48，其中可分析 session n=47。）

证据 4（`outputs/` 实际内容）：`audit_A.json 1805B`、`audit_apr.py 4189B`、`submit.zip 2285B` → 非空 3 个 ✓
