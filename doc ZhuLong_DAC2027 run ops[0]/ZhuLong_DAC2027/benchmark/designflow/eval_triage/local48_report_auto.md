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

