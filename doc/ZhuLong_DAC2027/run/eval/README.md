# 评测流水线与当前结果参考（EDA-Eval-PyAether → EDA-Scripting-Bench）

并发跑量手册在仓库根 `benchmark_parallel_guide.md`。本文件是「真实流水线 +
当前结果 + 沙盒作者笔记」的备忘，替代早先的玩具 harness（已删除）。

## 真实流水线（已存在，勿另起炉灶）

| 组件 | 位置 |
|------|------|
| 代码生成 driver | `/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh` |
| 评分 | `/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py` |
| 评测框架 | `/nasdata/app.e0031982/code/EDA-Eval-Framework` |
| 158-case 数据集 | `eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl` |

一键运行（在 `eda_fastmcp` 下）：

```bash
# 代码生成 + 评测一体（8 并发、禁用 Memory Bank 注入），约 3 小时/轮
bash scripts/run_cline_script.sh -p 8 -n
# 仅评分（给已生成代码打分）
python scripts/run_eval.py -g ~/eda_code_eval/completed_code_generation_<ts>.jsonl
```

## 数据集任务 schema（jsonl，每行一个 task）

```json
{
  "task_id": "EDA-Eval-PyAether-001",
  "prompt": "import pyAether as pyScript\n...  def <entry_point>(...): ...docstring...",
  "entry_point": "count_unique_bus_bits",
  "canonical_solution": "  ...body...",
  "test": "import pyAether as pyScript\ndef check(candidate):\n    ...asserts...",
  "metadata": {"scenario": "Schematic", "source": "pyAether.emyStringGetNumUniqueBits", ...}
}
```

要点：任务是**函数级**（agent 实现 `entry_point`），由 `check(candidate)` 断言
评分；不是「建库建图改设计」的 `run()` 风格。

## 当前主配置结果（cline + zhulong_deepseek_v32, -p 8 -n）

5 次独立运行 Pass@1（Sep 14–15，`~/eda_code_eval/`）：

| batch | pass | Pass@1 |
|-------|------|--------|
| 152253 | 148/157 | 94.3% |
| 180729 | 145/152 | 95.4% |
| 204303 | 146/157 | 93.0% |
| 233152 | 148/158 | 93.7% |
| 020828 | 147/157 | 93.6% |

- 均值 ≈ **94.0%**，run-to-run spread **93.0–95.4%**（±~1.2 pp）。
- 最新批 `020828`：`metrics.pass_rate = 0.9363`，生成成功 157/157（0 fail /
  0 timeout）；`final_report.json` 含 per-task `details_per_task`。
- 论文旧值（78.5% 全系统 / 23.6% 裸 LLM / +43.0 沙盒 / +3.2 自探索）已失效，
  将在 EDA-Scripting-Bench 上全量重测。

## pyAether 沙盒作者笔记（写 EDA-Scripting-Bench 任务用）

无头沙盒无默认 techlib/design：`aeOpenDesign("test",...)` 返回 False，需先
`aeNewLib → aeNewCell → aeOpenDesign`。已验证的最小序列：

```python
import pyAether as py
py.emyInitAether("-adv")                              # None（headless 正常）
py.aeNewLib(lib="bp")                                 # True
py.aeNewCell(lib="bp", cell="c1", view="layout", viewType="Layout")  # True
py.aeOpenDesign("bp", "c1", "layout", "edit")        # True
cv = py.dbOpenCV(lib="bp", cell="c1")                # db handle
box = py.emyBoxF(10, 20, 100, 200)
fig = py.aeCreateRect(box)                            # emyRect
fig = py.dbCrtRect(cv=cv, bbox=box, layer="text")     # 指定命名层
b = py.getBBox([fig], toUU=True)
b.left(), b.bottom(), b.right(), b.top()             # 10.0, 20.0, 100.0, 200.0
```

坑（务必注意）：
1. `emyInitAether("-adv")` 返回 `None`，不要据此判失败。
2. `emyBoxF` **不支持下标**；`tuple(box)` 是两点元组 `((l,b),(r,t))`。取坐标用
   `.left()/.bottom()/.right()/.top()`。
3. `getBBox` 默认 **DB unit（×1000）**，要用户单位传 `toUU=True`。
4. 断言/test 代码必须**自包含**（每个任务独立新命名空间，看不到 harness helper）。

## MCP 消融：开关工具 + 重启服务（速查）

工具开关在 `eda_fastmcp/main.py` 的 `_TOOL_DEFAULTS` + `.env` 的
`EDA_MCP_TOOLS_ENABLED` 里；改完要重启两个服务才生效（详见仓库根
`benchmark_parallel_guide.md` §2.4）：

```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
source venv/bin/activate
bash scripts/stop_recall_api.sh && bash scripts/start_recall_api.sh  # ① 召回(端口会变→必须同步 .env RAG_RECALL_URL)
bash scripts/stop.sh           && bash scripts/start.sh              # ② 主 MCP(EDA_MCP_PORT=8090)
```

- 核心 4 工具恒开：`get_api_details / search_apis / search_apis_by_keyword / run_code`
- 扩展 3 工具（消融对象）：`cimi_search / cimi_fetch / vqa`
- 关闭这 3 个：`_TOOL_DEFAULTS` 设 False（当前默认）或 `EDA_MCP_TOOLS_ENABLED` 留空
- 开启这 3 个：`EDA_MCP_TOOLS_ENABLED=all` 或 `=cimi_search,cimi_fetch,vqa`

## 待复测清单（新版 Cline + 不 retry + V4-Pro）

| # | 配置 | 改什么 | 对应论文表 |
|---|---|---|---|
| 1 | Full system（主结果） | 默认关闭 3 扩展 MCP，5 轮 | 5_exp 主结果 |
| 2 | 组件消融：Pure LLM / RAG / w/o Sandbox / w/o Retrieval / w/o Self-Expl | 逐项禁用工具/阶段，各 5 轮 | `tab:main-ablation` |
| 3 | MCP 消融其余 4 模型（glm-5.2 / flash / kimi / doubao）关闭 MCP | `EDA_MCP_TOOLS_ENABLED=all` 关闭 | MCP 消融 |
| 4 | 多模型对比（pro-fp4 / glm-5.2 / flash / kimi / doubao） | `cline auth` 切基座（见 `benchmark_parallel_guide.md` §2.5），各 5 轮 | `tab:llm-comparison` |
| 5 | RQ3 检索（vector vs grep） | 切 `search_apis` 后端 | RQ3 |
| 6 | RQ4 index 构建（name+desc / desc-only / name-only） | 重建 kb，各 5 轮 | RQ4 |
| 7 | self-exploration 效率（tool-call 削减） | 对比 w/ vs w/o 自探索 | `tab:selfdoc-efficiency` |
| 8 | interactive 20 任务（PyAether/SKILL） | `CLI_AGENT` / lang 切片 | interactive |
| 9 | RQ5 harness 保真度 / RQ6 multi-agent / RQ7 MLLM-vs-tool | 设计后首测 | 架构消融 |

> 每组 5 次独立执行（reshuffled order + fresh context），报
> `mean Pass@1 ± run-to-run std` + `Pass^5`（task 级 5/5 全过）。
> 跑法：`bash scripts/run_cline_script.sh -p 8 -n`，打分 `python scripts/run_eval.py -g <jsonl>`
> （`-p 8` = 8 并发；`-n` = 禁用 Memory Bank 注入）。

## 下一步

1. 把「5 次运行」主配置统计可靠性（mean ± std + Pass^5）落进 `5_exp.tex`。
2. 按上表逐行复测填数（先 #2 组件消融，是 grounding 理论的实证支柱）。
3. EDA-Scripting-Bench 就绪后：加 `lang:"skill"` / `lang:"tcl"` 切片，全量重测。