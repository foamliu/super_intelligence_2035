# ADP Subset Plan — `neulab/agent-data-collection`

> 生成时间：2026-11-15  
> 生成者：data agent (HfApi 实测)  
> 总量：130 files / 498.66 GB / 22 个子集  
> License：未在 cardData 标注（各子集来源各异，需逐子集核实）

## 判定规则

- **不许下**（与 P0 重复 / 可从 P0 派生）：`toucan_1_5m`、`orca_agentinstruct`、`nemotron_terminal_corpus`、`swe-smith`、`swe-gym_*`、`nebius_SWE-agent-trajectories`
- **要下**（AgentTrove/Toucan 里没有、且对"工具调用能力"有新信息）
- **自行裁定**（用户未列入两表，自行判断）

## 逐子集决策

| 子集 | 文件数 | GB | 决策 | 理由 |
|:--|--:|--:|:--|:--|
| `toucan_1_5m` | 4 | 222.27 | 🚫 **不下** | 与 P0 `Agent-Ark/Toucan-1.5M` 完全重复（ADP 把 Toucan 转成统一 SFT 格式，但 Toucan 原始已下载） |
| `orca_agentinstruct` | 6 | 42.15 | 🚫 **不下** | 与 P2 `microsoft/orca-agentinstruct-1M-v1` 重复（且 P2 判低优先未下） |
| `nemotron_terminal_corpus` | 4 | 7.77 | 🚫 **不下** | 与 P0 `open-thoughts/AgentTrove` 同格式同源（AgentTrove 规模是其 4 倍，已覆盖） |
| `swe-smith` | 6 | 8.36 | 🚫 **不下** | AgentTrove 含 `swesmith` 来源，已覆盖 |
| `swe-gym_openhands_sampled_trajectories` | 6 | 1.76 | 🚫 **不下** | SWE-gym 轨迹被 AgentTrove 的 SWE 来源覆盖 |
| `nebius_SWE-agent-trajectories` | 6 | 8.09 | 🚫 **不下** | AgentTrove 已覆盖 SWE-agent 轨迹 |
| `coderforge_preview` | 4 | 123.73 | 🟡 **暂不下** | 标注 "preview"，非正式版；体积大（124GB）；内容未确认是否与 AgentTrove/code_feedback 重复。若后续需要可补下 |
| `code_feedback` | 6 | 2.94 | ✅ **下** | 代码执行反馈数据，对"工具调用+代码执行"能力有新信息 |
| `codeactinstruct` | 6 | 0.33 | ✅ **下** | 代码交互指令数据，小体积 |
| `mind2web` | 6 | 9.97 | ✅ **下** | 真实 Web 交互轨迹，AgentTrove/Toucan 无此源 |
| `nnetnav-live` | 6 | 6.76 | ✅ **下** | 导航类 agent 轨迹 |
| `nnetnav-wa` | 6 | 3.78 | ✅ **下** | 导航类 agent 轨迹（WA 变体） |
| `go-browse-wa` | 6 | 36.99 | ✅ **下** | 浏览器交互 agent 轨迹 |
| `synatra` | 6 | 4.82 | ✅ **下** | 合成 agent 轨迹 |
| `mini-coder` | 4 | 17.86 | ✅ **下** | 代码 agent 轨迹 |
| `openhands` | 6 | 0.42 | ✅ **下** | OpenHands 框架轨迹（与 harness 线同源） |
| `swe-play-trajectories` | 4 | 0.59 | ✅ **下** | SWE 游走轨迹，小体积 |
| `agenttuning_alfworld` | 6 | 0.02 | ✅ **下** | AlfWorld 环境 agent 数据 |
| `agenttuning_db` | 6 | 0.02 | ✅ **下** | 数据库交互 agent 数据 |
| `agenttuning_kg` | 6 | 0.02 | ✅ **下** | 知识图谱 agent 数据 |
| `agenttuning_mind2web` | 6 | 0.00 | ✅ **下** | Mind2Web 子集 |
| `agenttuning_os` | 6 | 0.01 | ✅ **下** | 操作系统交互 agent 数据 |
| `agenttuning_webshop` | 6 | 0.02 | ✅ **下** | 网购交互 agent 数据 |

## 汇总

| 类别 | 子集数 | GB |
|:--|--:|--:|
| 🚫 不下（重复） | 6 | 290.40 |
| 🟡 暂不下（待评估） | 1 | 123.73 |
| ✅ 要下 | 15 | 84.53 |
| **合计** | 22 | 498.66 |

**实际下载量**：~84.53 GB（15 个子集）

## 执行方式

```bash
# 逐子集下载，每下完一个报体积 + df -h /nas_user
for subset in code_feedback codeactinstruct mind2web nnetnav-live nnetnav-wa go-browse-wa synatra mini-coder openhands swe-play-trajectories agenttuning_alfworld agenttuning_db agenttuning_kg agenttuning_mind2web agenttuning_os agenttuning_webshop; do
  hf download neulab/agent-data-collection --repo-type dataset \
    --include "${subset}/*" \
    --local-dir /nas_user/app.e0031982/datasets/neulab/agent-data-collection/
done
```

## 污染检查备忘

- `swe-smith` / `nebius_SWE-agent-trajectories` / `swe-gym_*` 可能含 SWE-bench 任务 → 已决定不下
- `mind2web` 可能含 Mind2Web 测试集 → 下载后需做 contamination check
- `code_feedback` 可能含 HumanEval/MBPP 题目 → 下载后需做 contamination check
