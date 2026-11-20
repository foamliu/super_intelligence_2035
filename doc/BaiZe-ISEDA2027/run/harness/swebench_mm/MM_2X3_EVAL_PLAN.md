# SWE-bench Multimodal 2×3 评测计划（用户令 2026-11-19）

> 用户原话：「SWE-bench Multimodal 下载完后，起如下的 2x3 评测。2 个 harness：cline+opencode。3 个 LLM：DeepSeek-V4-flash、Kimi-K2.6 和 Doubao」

## 1. 评测矩阵（2 harness × 3 LLM = 6 路）

| Harness | LLM | Base URL | Model |
|:--|:--|:--|:--|
| cline | DeepSeek-V4-flash | `http://agi-gateway.cxmt.com/v1` | `deepseek-v4-flash` |
| cline | Kimi-K2.6 | `http://agi-gateway.cxmt.com/cloud/v1` | `kimi-k2.6-cloud` |
| cline | Doubao | `http://agi-gateway.cxmt.com/cloud/v1` | `doubao-seed-2.0-pro-cloud` |
| opencode | DeepSeek-V4-flash | 同上 | 同上 |
| opencode | Kimi-K2.6 | 同上 | 同上 |
| opencode | Doubao | 同上 | 同上 |

API key 见 `mm_2x3_config.json`（gitignored，与任务书一致）。

## 2. 数据集

- `test.parquet`（480 题）+ `dev.parquet`：SWE-bench Multimodal。
- 每题字段：`instance_id, repo, base_commit, image(评测容器), problem_statement, image_assets{problem_statement:[图片URL…], patch:[], test_patch:[]}, patch(gold), test_patch, eval_script, log_parser, FAIL_TO_PASS, PASS_TO_PASS, eval_type, version`。
- 评测容器 580 个，`pull_all_images.sh` 顺序下载（nice19/ionice3，不抢 pretrain）。

## 3. 可行性核查（R2757 · 2026-11-19 11:0x，已实测）

| 项 | 结论 | 证据 |
|:--|:--|:--|
| 网关 `/v1/models` | ✅ 200 | `{"object":"list","data":[...]}` |
| Kimi-K2.6 文本 | ✅ | chat.completion 返回（reasoning_content） |
| Kimi-K2.6 多模态 | ✅ | base64 1px png → `usage.prompt_tokens_details.image_tokens=3`（已处理图片） |
| Doubao 文本 | ✅ | 返回 "OK" |
| Doubao 多模态 | ✅ | 接受 image_url；1px 被拒（min 14px，真实截图 OK） |
| DeepSeek-V4-flash | 🟠 额度耗尽 | 11:02 返回「Token额度已用完，请等待2小时3分钟」→ ~13:00 重置；V4 为已知 VLM，重置后复测多模态 |
| 评测容器下载 | 🟠 87.4% | 507/580 pulled，0 FAILED，ETA ~3-4h |
| swebench 版本 | ✅ 5.0.2 | `run_evaluation` 可用；MM 用同机制 + 实例级 `eval_script`/`log_parser` |

**结论**：3 个 LLM 均多模态可用（Kimi/Doubao 已证，DeepSeek 待额度重置后复测）。下载为启动硬约束（~3-4h）。

## 4. 关键工程缺口：harness 多模态适配

现状（`run_harness.py` / `run_single.py`）：
- `ClineDriver` / `OpencodeDriver` 把 `instance["problem_statement"]` 作为**纯文本**传给 CLI（cline 用位置参数，opencode 用 prompt）。
- **不处理** `image_assets.problem_statement` 里的图片 URL → 多模态题的图片信息丢失。

需做的适配（predict 阶段）：
1. 从 `image_assets.problem_statement` 取图片 URL（GitHub user-images 等）。
2. 下载图片（经 proxy `http://172.19.92.25:13128`，因外网需代理）→ 转 base64 data-url 或本地路径。
3. 把图片以 OpenAI 多模态 `content: [{type:text,…},{type:image_url,image_url:{url:…}}]` 格式喂给 LLM。
   - cline：cline CLI 的初始 task 是文本位置参数 → 需确认 cline 是否支持在 prompt 里嵌图片，或改用 cline 的 API 直接发多模态 messages（可能需改 cline 调用方式）。
   - opencode：opencode serve 的 prompt 机制 → 同上需确认多模态支持。
4. 兜底：若 harness CLI 不支持多模态，可把图片 URL 以 markdown `![](url)` 嵌入 problem_statement 文本，让 VLM 自行理解（部分 VLM 经网关可拉图）——但 GitHub URL 需代理，网关未必拉得到，**优先 base64 内嵌**。

## 5. 评测流程（eval 阶段，与 Verified 同机制）

```
swebench.harness.run_evaluation \
  --predictions_path <merged_predictions_2x3.json> \
  --dataset_name <mm_dataset_json> \      # 需把 test.parquet 转成 swebench 可读的本地 JSON
  --split test --instance_ids <...> \
  --max_workers 1 --run_id <route_id> --timeout 1800
```
- 容器内跑实例级 `eval_script`（bash：cd /testbed → git → 跑测试），`log_parser`（如 `parse_log_lighthouse`）解析结果。
- CPU 限制照旧（taskset 0-15 + OMP=1），避免 sklearn 类螺旋。
- 每路独立 run_id，结果落 `reports_2x3/`（gitignored），汇总后出中文 HTML 报告（落 `reports/`）。

## 6. 启动条件（gate）

1. 评测容器下载 100%（580/580，0 FAILED）—— **当前 87.4%**。
2. DeepSeek-V4-flash 额度恢复（~13:00）。
3. cline/opencode 多模态适配完成（§4）+ 1 题冒烟通过。
4. 不抢 pretrain CPU（nice19/ionice3 + CPU 限制）。

## 7. 进度

- R2757（本轮）：可行性核查 ✅ + 6 路配置落盘 ✅ + 本计划 ✅。incr_eval Verified（pi 2 real + cline/codex empties）并行跑。
- TODO 下轮：① 复测 DeepSeek 多模态（额度恢复后）② 开始 cline/opencode 多模态适配 ③ parquet→swebench JSON 转换器 ④ 下载完成后冒烟 1 题×6 路。
