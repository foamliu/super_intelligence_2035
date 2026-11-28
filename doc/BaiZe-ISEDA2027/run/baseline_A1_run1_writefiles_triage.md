# A1 (Qwen3.5-2B) run1 — write_files / tool-rejection triage
> 数据源: codegen.log + completed_code_generation.jsonl + final_report.json + A0_base_ragfix_run1_pertask.json
## 1. 结论（首屏）
- **A1 run1 = 1.27% (2/158) 主因 = INFRA/协议回归，不是 Qwen3.5-2B 能力不行。**
- cline MCP 配置 `~/.cline/data/settings/cline_mcp_settings.json` 在 2026-11-28 HOME snapshot 回退(wake870)中被清空。`run_cli.sh:109` 用 `cp ... || true` 静默跳过 ⇒ A1 8 worker 均无 `pyAether_MCP_server` ⇒ `search_apis/get_api_details/run_code` 全判 unavailable。
- `no_sandbox.md` prompt 明文要求用 `search_apis/get_api_details`，Qwen3.5-2B 照做 → 共 199 次 unavailable-tool 拒绝(search_apis 131/get_api_details 0/search_apis_by_keyword 10/write_files 4) → 无码 → 1.27%。
- **公平性**: A0_base_ragfix(11-24,wipe 前)同 prompt/同 harness/同 hook 但 MCP 文件在位 → search_apis 1044/get_api_details 663/run_code 179 成功, rag_queried_rate=0.9937 → 45.06%。**两臂工具集不同 ⇒ 口径不一致 ⇒ 不可直接配对。**
- **裁决: 属「协议适配问题」→ 修**(用户令 22:3x 第3条)。恢复 cline_mcp_settings.json → 重跑 A1 run1 冒烟确认 MCP 可用 + 命中率回升 → A0 1-run 校准 → A1 run1-5。

## 2. 汇总统计
- 总任务 158；有码 68；无码 90；PASS 2；Pass@1 0.0127
- run_commands 被 hook 阻断: 1519；editor schema 错误: 56

### 2.1 工具调用 (aggregate exact)
| 工具 | 次数 |
|---|---:|
| `run_commands` | 299 |
| `read_files` | 150 |
| `editor` | 145 |
| `search_apis` | 124 |
| `submit_and_exit` | 61 |
| `abort` | 27 |
| `list` | 17 |
| `list_files` | 11 |
| `search_apis_by_keyword` | 10 |
| `status` | 6 |
| `complete_code_generation` | 6 |
| `fix_function_name` | 5 |
| `write_files` | 4 |
| `edit` | 2 |
| `list_dir` | 2 |
| `edit_files` | 2 |
| `format_raw_task` | 1 |
| `foundartive_prompt_interact` | 1 |
| `list_and_read` | 1 |
| `accept_run` | 1 |
| `think` | 1 |
| `educate` | 1 |
| `create_and_exit` | 1 |
| `search_codebase` | 1 |
| `search_files` | 1 |
| `print_statement` | 1 |
| `edit_all` | 1 |
| `urgy` | 1 |
| `list_dir_files` | 1 |
| `writer` | 1 |

### 2.2 被拒工具 (unavailable-tool exact)
| 工具 | 拒绝次数 |
|---|---:|
| `search_apis` | 131 |
| `list` | 19 |
| `list_files` | 12 |
| `search_apis_by_keyword` | 10 |
| `write_files` | 4 |
| `edit` | 2 |
| `list_dir` | 2 |
| `edit_files` | 2 |
| `foundartive_prompt_interact` | 1 |
| `list_and_read` | 1 |
| `create_files` | 1 |
| `accept_run` | 1 |
| `think` | 1 |
| `create_or_create_file` | 1 |
| `educate` | 1 |
| `$` | 1 |
| `edit\n\n格式` | 1 |
| `create_and_exit` | 1 |
| `search_codebase` | 1 |
| `search_files` | 1 |
| `print_statement` | 1 |
| `edit_all` | 1 |
| `urgy` | 1 |
| `list_dir_files` | 1 |
| `writer` | 1 |

## 3. 三堆分类 (per-task boundary 近似, aggregate 精确)
| 分类 | 计数 | 含义 |
|---|---:|---|
| c_capability | 66 | code emitted but failed (logic/API misuse) -- genuine gap |
| b_path_or_schema | 44 | editor used but no code landed (path/schema) |
| other | 24 | uncategorized |
| a_protocol_incompat_mcp | 16 | no code; MCP tools rejected as unavailable; never reached editor |
| d_submit_text_only | 6 | submit_and_exit text, no editor code |
| pass | 2 | passed |

## 4. 公平性对照 (A0 vs A1)
| 项 | A0_base_ragfix(11-24) | A1_qwen35_2b(11-28) | 同? |
|---|---|---|---|
| 模型 | MiniCPM5-2B | Qwen3.5-2B | **唯一应变量** |
| endpoint | :8098 | :8097 | - |
| prompt | no_sandbox.md | no_sandbox.md | 同 |
| harness | run_cline_script -p8 -n | run_cline_script -p8 -n | 同 |
| hook | PreToolUse sandbox | PreToolUse sandbox | 同 |
| benchmark | 158 题 | 158 题 | 同 |
| MCP 配置文件 | 在位 | **被 wipe(缺失)** | 不同 |
| 可用工具集 | core+MCP | 仅 core(4) | 不同 |
| search_apis 成功 | 1044 | 0 | 不同 |
| get_api_details 成功 | 663 | 0 | 不同 |
| run_code 成功 | 179 | 0 | 不同 |
| rag_queried_rate | 0.9937 | 0.0 | 不同 |
| Pass@1 | 45.06%(5-run) | 1.27%(run1) | 不可比 |

**裁决**: CALIBER MISMATCH (infra regression, not model): A1 lost MCP tools because ~/.cline/data/settings/cline_mcp_settings.json was wiped by 2026-11-28 HOME snapshot rollback (wake870). A0 (Nov 24) had the file -> MCP callable -> 45.06%. Single-variable design broken by missing MCP config, NOT by base-model capability.

## 5. 原始 trace 片段
### search_apis rejected (codegen.log L159+)
```
[search_apis] {"description":"Search for pyAether emyBoxF and emyPointF...
   â¿ error: {"error":"Tool call search_apis was rejected before execution: AI_NoSuchToolError: Model tried to call unavailable tool 'search_apis'. Available tools: read_files, run_commands, editor, submit_and_exit."}
[search_apis] {"description":"Search for pyAether SWIG type constructio...
   â¿ error: {"error":"Tool call search_apis was rejected before execution: AI_NoSuchToolError: Model tried to call unavailable tool 'search_apis'. Available tools: read_files, run_commands, editor, submit_and_exit."}
[run_commands] echo "ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only read and write inside the provide...
   â¿ ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only...
[run_commands] echo "ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only read and write inside the provide...
```
### write_files rejected (codegen.log L11684+)
```
[write_files] {"files":"[{\"path\": \"/home/app.e0031982/eda_code_eval/...
   â¿ error: {"error":"Tool call write_files was rejected before execution: AI_NoSuchToolError: Model tried to call unavailable tool 'write_files'. Available tools: read_files, run_commands, editor, submit_and_exit."}
:
 List   让我直接[T """uple
通过[INFO] [worker-3] 任务 EDA-Eval-PyAether-082 处理完毕，准备下一个
[float   终端, import命令 float py创建]])文件A ->ether： List

```
### run_commands hook-blocked (codegen.log L68+)
```

[run_commands] echo "ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only read and write inside the provide...
   â¿ ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only...
[read_files] {"files":[{"path":"/home/app.e0031982/eda_code_eval/2026_...
   â¿ ok
[run_commands] echo "ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only read and write inside the provide...
   â¿ ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only...
```
### editor schema error (codegen.log L187+)
```
[editor] {"file_path":"/home/app.e0031982/eda_code_eval/2026_1128_...
   â¿ error: {"error":"â Invalid input: expected string, received undefined\n  â at path\nâ Invalid input: expected string, received undefined\n  â at new_text"}
遇到审计权限无法访问外部目录。让我考虑使用已知的工具来查看技能文档：

[run_commands] echo "ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only read and write inside the provide...
   â¿ ACCESS RESTRICTED: outside the sandbox workspace or not allowed. You may only...

```
### model gives up -> submit (codegen.log L57+)
```
[submit_and_exit] {"summary":"根据任务要求，创建函数 get_date_from_timestamp 实现 Unix 时...
   â¿ Submission recorded (verified): 根据任务要求，创建函数 get_date_from_timestamp 实现 Unix 时间戳到年月日的转换。该函数会验证 inp...
[INFO] [worker-3] 任务 EDA-Eval-PyAether-002 成功完成

[INFO] [worker-3] 任务耗时: 13 秒
[read_files] {"files":[{"path":"/home/app.e0031982/eda_code_eval/2026_...
   â¿ ok
```

## 6. 修法(最小)
1. 恢复 `~/.cline/data/settings/cline_mcp_settings.json`(见下)指向在跑 eda-mcp :18888 SSE。
2. 重跑 A1 run1 冒烟(-p8 -n)，确认 search_apis/get_api_details 不再被拒、命中率回升。
3. A0 1-run 校准(重启 base:8098+重装 minicpm5 parser)，确认 45.06% 量级不掉。
4. A1 run1-5 → 5-run summary → A0_vs_A1 配对(McNemar/bootstrap)。

```json
{
  "mcpServers": {
    "pyAether_MCP_server": {
      "url": "http://127.0.0.1:18888/sse",
      "type": "sse",
      "disabled": false,
      "autoApprove": [
        "search_apis",
        "get_api_details",
        "search_apis_by_keyword",
        "run_code"
      ]
    }
  }
}
```

## 7. 证据索引
- A1 run1 codegen.log: `/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1/codegen.log`
- A1 run1 final_report.json: `/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1/final_report.json`
- A0 pertask: `/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baseline_A0_base_ragfix_run1_pertask.json`
- run_cli.sh:109 (MCP cp): /nas_data/app.e0031982/code/eda_fastmcp/scripts/run_cli.sh
- 本 triage: `/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1/write_files_triage.json` / `/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1/write_files_triage.md`
