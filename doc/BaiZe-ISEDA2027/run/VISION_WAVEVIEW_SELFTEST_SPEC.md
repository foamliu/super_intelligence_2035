# VISION_WAVEVIEW_SELFTEST_SPEC.md — vision 自测 WaveView 10 题（±VQA MCP）规格

> 下发：运维 2026-11-14 19:4x（用户直令）。**引用处**：`BAIZE_VISION_TASK.md` 顶部令。
> **用户原话**：「请 vision 自己做一下 waveview 的题目看看通过率。然后给自己配置 Qwen3.5-2B 的 VQA 作为 MCP，再做一遍，看看通过率能否有提升。」

---

## 0. 这次测什么（一句话）

**vision 线要建立的是「MLLM 作为 agent 系统的一部分」带来的增益**——不是让 2B VLM 单打独斗。

> 用户原话（2026-11-14 21:5x）：「vision 补 agent 臂：我们看的是 MLLM 作为 agent 系统一部分带来的增益，而不是让它单打独斗。」

因此正式测法必须是 **agent 当 SUT**：vision 自己的 cline（`glm-5.2` 文本底座）+ 把 `Qwen3.5-2B` 封成 **VQA MCP** 供它调用。**agent 的价值在于**：能把没读准的量**再问一次 / 换问法 / 交叉验证**，从而把「每量 55.5%」补成「整题全过」——这是单模型臂结构上做不到的事。

### 0.1 已交付的「单模型臂」结果（保留，但只作**工具天花板**参考）

| 臂 | 设置 | 整题 | 每量 |
|:--|:--|:--|:--|
| V0 | Qwen3.5-2B 不看图 | 0/10 | 30.9%（34/110） |
| V1 | + VQA 基模 | 0/10 | 38.2%（+7.3pp） |
| V2 | + rft2_adapter | 0/10 | 55.5%（+17.3pp） |

这三臂**没有 agent 环节**（V1/V2 是模型经 HTTP 调自己的 VQA），所以它们只回答「这个 VQA 工具本身能读多准」，**不能**作为本线的能力结论。报告里必须标「单模型臂（工具天花板）」。

### 0.2 本轮必须补的「agent 臂」（正式测法）

| 臂 | SUT | 工具 | 预期 |
|:--|:--|:--|:--|
| **G0** | vision cline（glm-5.2） | **无 VQA MCP** | 应 fail（正确基线） |
| **G1** | 同上 | VQA MCP（Qwen3.5-2B 基模） | 看增益 |
| **G2** | 同上 | VQA MCP（rft2_adapter） | 看增益 |

同一 10 题、同 `check.py`、同参数、顺序随机化；**唯一变量 = 有没有/用哪个 VQA MCP**。

**agent 臂额外必须记录的指标**（这是本轮的核心证据）：
- `vqa_calls_per_task`（每题问了几次）
- `reask_count`（同一量重复提问/换问法次数）
- `agent_selfcheck`（是否有「先问一遍 → 发现不一致 → 再问」的轨迹，给 1–2 条原文片段）
- 若仍 0/10：**必须指出卡在哪几个量**，并给出「agent 也没救」的具体证据（例如反复问同一量仍不稳定）

> ⚠️ **线职责边界（2026-11-14 用户订正，勿混）**：
> - **designflow = 做 benchmark**（造题 / 恢复原形态 / 写 `check.py`）。它此前用 `minicpm5-2b-sft` 跑出的「10/10 FAIL」是**题库自检**（确认题在无多模态下确实不可解），**不是模型能力结论**。
> - **posttrain = 文本/脚本能力线**（基模 minicpm5-2b → EDA-Eval-PyAether 158 → SFT/RL 提升）。
> - **vision = 多模态能力线**（agent glm-5.2 + VQA MCP → WaveView 看图题 → SFT/RL 提升）。
> - 所以本次**不是**要复刻 designflow 那份结果，也不是要和它比表；我们测的是「vision 这条能力线在 MLLM 接入 agent 前后的差」。

## 1. 测试集与判分（只读引用，不许改）

- 题集：`designflow/waveview_baseline_results.D.json`（8 题）+ `.B.json`（2 题）里 `track=synthesized-image-restored` 的 case，共 **10 题**（α4 + β7）。
- 判分：**直接调用 designflow 已交付的 `check.py`**（每题自带，k≥12 断言），逐题跑；🚫 不改 check、不改题面、不改 assets、不挑题。
- 资产若在沙盒内不可达 ⇒ **如实标 `asset_unavailable`**，不计入分母，🚫 不许用文本替身（`.rep`/CSV）凑数。
- 提交物：按每题 check 要求产出（通常 `submit.zip` 或指定文件），落 `vision/vqa_tool/waveview_selftest/<arm>/<case_id>/`。

## 2. 两臂（唯一变量 = 有没有 VQA MCP）

| 臂 | 配置 | 说明 |
|:--|:--|:--|
| **V0** | vision cline 现有配置，**MCP 里不含 VQA** | 文本底座，理论上「看不到图」 |
| **V1** | V0 **逐字节一致** + MCP 增加 `qwen35_vqa_mcp_server.py`（工具：问图） | 唯一差异 |

其余必须保持一致：同一批 10 题、同一 `temperature`、同一超时、同一 harness、同一提交路径。**跑的顺序随机化**（V0/V1 交替，防止顺序效应），种子/时间戳记录在案。

## 3. 🚫 作弊防线（本案最关键）

本题的答案就藏在 PNG 里，所以「怎么读图」必须钉死：

- **V0 臂**：只允许看题面文本。🚫 禁止任何形式的读图绕行 —— 不许用 `python/PIL/opencv/tesseract/OCR`、不许 `base64` 解码图片、不许调 `localhost:30001`、不许按 case_id 去 grep 源码/参考实现/答案、不许读 `.rep/.vec/.csv` 原始数据。
- **V1 臂**：读图**只准**走 VQA MCP 工具；同样禁止上述绕行。
- **审计**：逐题扫 trace 的 bash 命令与 tool 调用，命中任一条禁用路径 ⇒ 该题判 **cheat** 并作废（在报告里单列，不计入 pass）。审计脚本落 `vision/vqa_tool/waveview_selftest/audit_*.py`。
- 反作弊结论必须写进报告：**cheat 数 = 0 才允许引用通过率**。

## 4. 指标与统计力（先说清局限）

- 主指标：**通过率（pass/10）**，逐题 PASS/FAIL 表 + `asset_unavailable` 单列。
- 副指标：**翻转数**（V0 fail → V1 pass）、VQA 调用次数、单题耗时、cheat 数。
- ⚠️ **n=10 统计力极弱**：McNemar 要 ≥6 个不一致对才可能 p<0.05。所以**预注册**：主结论用「翻转表 + 逐题 verdict」，p 值只作参考并注明样本量不足。
- 若要统计结论 ⇒ 另开扩样（γ 中可恢复题、或合成集 150 题做机制验证），但**不得**用合成集数字冒充 WaveView 结果。

## 5. 预注册判据

- **V1 通过率 > V0** 且 **cheat=0** ⇒ 记「VQA 通道在自测 SUT 上有效」，给出翻转题清单与每题一句话归因。
- **V1 = V0** ⇒ 记「工具可用但未被有效使用或不足以解题」，必须从 trace 给出原因（没调用 / 调了但问题问错 / 读对了但代码写错 / 超时）。
- **V1 < V0** ⇒ 记负结果，并检查是否 VQA 引入错误读数（幻觉读数）。

## 6. 产物

1. `vision/vqa_tool/waveview_selftest/V0/<case>.json`、`V1/<case>.json`（verdict / 耗时 / tool 调用 / 提交物路径）
2. `reports/report_vision_waveview_selftest_zh.html`（中文 HTML，含两臂并列表、翻转表、cheat 审计结果、诚实声明）
3. `EXPERIMENTS_VISION.md` 新节 + MEMORY 一行心跳

## 7. 与 designflow 的边界

- 只**读** designflow 的 case/check/assets；🚫 不改其文件、不写其 MEMORY；需要 designflow 配合（如资产不可达）⇒ 写进 `WAVEVIEW_COLLAB.md` 的交付记录，不直接改。
- commit 前缀 `vision waveview-selftest:`；`git add` 只加本线文件。
