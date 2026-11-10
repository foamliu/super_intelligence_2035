
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
