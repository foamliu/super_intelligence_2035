# trace_deepread — 1795004623740_8n2mv (spf_RCC 贯穿线 RC 查看)

- **sid**: 1795004623740_8n2mv
- **user**: laijiang  · **host**: hfeg0pkn002 (10.129.2.11)  · **mc**: 196
- **model**: deepseek-v4-flash (cxmt-deepseek-flash)
- **cwd**: /ai_sandbox/drvqa/V0/agentdir/laijiang (permission denied to e0031982)
- **provider scene**: aether assistant (engine=aether)
- **size**: 470043 B / 123 msgs / 62 assistant turns
- **inputTokens**: 1,851,237 / outputTokens 20,568 (大量 token 来自 119 轮 RAG search_apis 返回)

## 真实任务（用户原话，trace msg 0）
> 「已经有了spf_RCC文件，怎么查看某一根贯穿线的RC」

（user_input mode="act"；session title 同句；单轮提问，无后续追问）

## 对话流（agent 行为）
- msg 0：用户单句提问。
- msg 1–119：agent 连续 119 个 assistant turn，全部仅调 `RAG_MCP_Server__search_apis` /
  `RAG_MCP_Server__get_api_details` / 首个 `search_apis`（共 ~120 次 API 检索），
  **无任何文件读 / 编辑 / 命令执行**。每个 assistant turn 后跟 2–3 个 tool_result（~4KB
  API 检索返回片段）。msg 36 / 48 出现 28–31KB 的大 tool_result（一次 get_api_details 全量返回）。
- msg 122（最终答复）：纯文本 how-to，**无脚本产出**。给出 4 种方法：
  1. **方法一 直接 grep**：`grep -A 50 "*NET VDD" your.spf`；并 verbatim 描述 SPF net 结构：
     ```
     *NET VDD 1.234e-15
     *R 1 2 5.6e+01
     *R 2 3 3.2e+01
     *C 1 0 2.1e-15
     *C 2 0 1.5e-15
     *C 3 0 0.8e-15
     ```
     注释：`*NET <name> <total_cap>` / `*R <n1> <n2> <R(Ω)>` / `*C <node> <gnd> <C(F)>`。
  2. **方法二 Aether GUI**：extracted view → Parasitic Network Browser。
  3. **方法三 pyAether**：`emyParasiticNetwork.load(net, ap)` + `getDevices()` 遍历 R/C。
  4. **建议**：快速看 → grep；正式 → GUI；批量 → 写 pyAether 脚本（offer 未兑现）。

## 关键判定
- **任务形态 = Q&A / how-to**（用户问"怎么查看"，非"帮我跑"）。按 2026-11-15 用户令，
  Q&A/explain/how-to 一律恢复为**可造**（旧规则判 weak/analysis-only 误杀）。
- **agent 无交付物**：仅文本答复，未读真实 spf 文件、未产脚本。真实 spf_RCC 文件在
  /ai_sandbox/drvqa/V0/agentdir/laijiang/ 下，e0031982 权限拒访（已 ssh 验证）⇒ 无 trace-verbatim
  真实文件可取。
- **reframe driver = harness-for-teeth**（MEMORY r740-r747 三分法：Q&A-analysis 类）：
  把"怎么查看贯穿线 RC"reframe 为 **produce 一个可复用 SPF RC 提取脚本**——
  参数化 `--spf --net`，解析 SPF 文本，输出指定 net 的 total_R / total_C / 各段 R /
  各节点 C / 节点数 / 段数（结构化 JSON）。判分真跑脚本在 hidden B（结构性差异的 SPF 文件）上。
  - asset_fidelity：A 文件 **format-faithful**——按 agent msg 122 verbatim 描述的 SPF
    `*NET/*R/*C` 格式重建（agent 原文即真实 SPF 格式规范，非编造）。
  - hidden B：结构性差异（net 名 / RC 值 / 节点数 / 段数 / 含 *CC 耦合电容 / 含无 R 的 net），
    非仅文件名替换。
  - 判分有牙：subprocess 真跑候选脚本在 B 上，断言解析结果结构（非文本相似）。
- **域**：spice_sim（SPF/SPEF 寄生参数是 spice 仿真输入；RC 提取属寄生分析前置）。
- **layer**：L1（offline Python 文本解析，无 EDA 二进制调用）。
- **track**：faithful（用真实用户原话作 prompt，A 格式 verbatim 自 trace）。
- **tier**：B（harness-for-teeth reframe，A 文件 format-faithful 重建而非真实文件 scp）。

## case 设计要点
- **case_id**: EDA-Eval-DesignFlow-SpfRcExtract-001
- **deliverable**: submit.zip 顶层含 `spf_rc_extract.py`，参数化 `--spf <file> --net <name>`，
  stdout 输出该 net 的 RC 结构化 JSON。
- **assertions k=14**（a-n）：见 reference/check.py CONDITIONS 表。
- **negatives 5**: empty_shell / print_expected / hardcode_a / core_deleted / nosim_stub。
- **隐藏输入 B**：design_B.spf — 6 net（CLK_TREE 6 段贯穿线 / VCC / DQ0 / ROW0 / VSS 无 R /
  COUPLED_NET 含 *CC 耦合电容），net 名 / RC 值 / 节点 / 段数全异于 A。
