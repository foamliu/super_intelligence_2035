# r595 deepread — xxchen / 1793697346047_5zola / must_be_surrounded (DNW_F_013_00)

**shard C · r595 · 2026-11-15 · 0-case round (DEBT:1, synthesis deferred to r596)**

## 选料路径
- fresh-pool: `summary_1115_081559.tsv` (4543 sessions) → C-keyword mc≥10 → 4-shard ledger anchor normalized cross (`sub(/\.messages\.json$/,"")`) → **392 truly fresh** (与 r594 的 394 一致口径，anchors=3485)。
- top by mc peek 5 (8v2mb/c5bgl/nu82p/ya8nn/ji8or) 全 REJECT（Q&A / run-existing / prompt-handoff，见下）。转 next-tier mc 50-70 + known-author (xxchen) 过滤 → **5zola (xxchen, mc=55, drc:198;dbcreatelabel:2;dbcreatepath:1)** ACCEPT。
- xxchen = r591 VirlayerNotParse-001 同作者，QA Pattern Tool 持续开发者，已知 produce-task 作者。

## trace 5zola 概要
- sid=`1793697346047_5zola`，user=xxchen，host=hfeg0pkn001@10.129.2.10，mc=55，25 msgs / 260KB
- tools: `read_files=7, list_allowed_files=5, get_agent_policy_status=1`（**无 write/editor/run_code** —— 本 session 仅上下文收集，实现未在本 trace 内完成）
- **user_input 3 条**：
  - U1（Context summary，多轮延续）：列出前序任务 `inside_surround_ring`（DNW_F_012_00，已 Done+验证通过），含文档路径修正、function 实现入口+good 1-2/bad 1-7 pattern、框架 1 行改动
  - U2：「阅读当前 AGENTS.md」
  - U3（**核心 produce-task**）：「新增 function: `must_be_surrounded` Nguardring->Pguardring {layer1 ringCut DNW}。1) LDR 描述：DNW_F_013_00 N+ Guardring of NW(DNW Guardring) must be surrounded by P+ Guardring of outside PW。DNW_F13 check。2) manual qa GDS 参考：temp_manual_gds/DNW_F_013_00.gds」
- **assistant 响应**：msg8 收到新任务→列 6 步计划（收集上下文/写 todo/实现 simple/manual 同步/验证/记录）→msg11/13/17/20 持续读 inside_surround_ring 范本、qa_config QACELL 行、VIRLAYER 定义、pattern_common 基类、参考 GDS 解码脚本。**session 在实现开始前结束**（agent 仅读到上下文）。

## 关键配置（trace + 范本解码）
- 框架根：`/home/xxchen/workspace/DRC_pattern_tool/`，当前版本 `0.5/device_rule1/`（trace 时为 0.4，工作已迁 0.5）
- `qa_config_device.txt` QACELL 行（trace msg13 读到，第 97 行）：
  `QACELL DNW_F_013_00 must_be_surrounded Nguardring->Pguardring check {layer1 edgeCut DNW}`
  （配置用 `edgeCut`，U3 用 `ringCut` —— 实现需两种写法都兼容）
- VIRLAYER：`Pguardring = AT4;PCH & PSD+0.05`，`Nguardring = AT4;NCH & NSD+0.05 & NW+0.1`
- 参考金标准 GDS：`temp_manual_gds/DNW_F_013_00.gds`

## GOLD（must_be_surrounded 已在 0.5 实现 —— fetch 确证）
**gold 路径**：`0.5/device_rule1/QA_Pattern_tool/function/must_be_surrounded/simple/`
- `must_be_surrounded.py`（入口，~250+ 行，已 fetch 头部）：`MustBeSurroundedContext(PatternContextBase)`，依赖 `pattern_common`/`function_common.create_generator`/layer_map/virlayer_manager
- 核心语义（docstring 详述）：
  - rule fires on **Nguardring COMPOSITE** (AT4;NCH & NSD+0.05 & NW+0.1)。移除任一 ingredient → composite 空 → check 不触发：
    - no NW → composite empty (good 4/5/6/8)
    - no N+ active → composite empty (good 4/5/8)
    - no DNW → not a DNW guardring (good 7)
  - composite 存在时必须被 **Pguardring composite** (AT4;PCH & PSD+0.05) 从外侧环绕：
    - P+ ring outside → pass (good 1/3)
    - P+ solid region covering → pass (good 2)
    - P+ ring missing → fail (bad 1/2/4)
    - P+ ring on wrong side (inside N+ ring opening) → fail (bad 3)
  - `ringCut` 语义：layer1 是 CUT DNW 边界的 RING，band 中心在 DNW 边界（一半内一半外）
  - 设计常量：DNW 12×12 (ring) / 13×5.5 (solid-rect)，active ring width 0.4，P_GAP 1.0，NSD+0.05→0.5 / NW+0.1→0.6 / PSD+0.05→0.5，marks whole+0.6 / DNW+0.8
- `good_pattern/1-8`：canonical_ring_ring / solid_rect_pguard_solid / ring_nwsolid_ring / pguard_only_no_nguard / bare_dnw_nw_ring / nguard_no_nw / nguard_no_dnw / pguard_inside_no_nguard
- `bad_pattern/1-4`：no_pguard / no_pguard_nw_solid / pguard_inside / rect_no_pguard（bad 带 4001;51 参考标记）
- `update_history.md`
- **范本**：`inside_surround_ring` (0.4) 同结构，bad_pattern/1-7 (no_nw/nw_enclosure_zero/dnw_protrude/no_guardring/guardring_missing_side/guardring_floating/guardring_outside_dnw) + good_pattern

## 拟造 case 形态（r596 交付计划）
- **case_id**：`MustBeSurroundedCheck-001`（physical_verify L2-boundary，承 r591 VirlayerNotParse / xxchen QA Pattern Tool 子型第 3 例）
- **B 档 mock-behavioral**（同 r591/r593/r594 模式）：把"框架内 GDS cell generator"重构为**纯 Python 离线 surround 检查器** `must_be_surrounded_check.py`，输入合成 GDS-like JSON fixture（cells[].polys[{layer, purpose, bbox}] + VIRLAYER composite 定义），判定 Nguardring composite 是否被 Pguardring composite 从外侧环绕（含 composite-empty 豁免 + wrong-side 检测 + ringCut 边界语义）。
- **输入 A**（合成小 fixture）：1 good（canonical N+ three-ring cutting DNW edge + P+ two-ring outside）+ 1 bad（no P+）+ 配置（VIRLAYER Nguardring/Pguardring + QACELL ringCut DNW）
- **隐藏 B**（不同结构）：good（P+ solid covering）+ bad（P+ inside wrong side）+ bad（no NW → composite empty → 豁免 pass）
- **隐藏 B2**（反硬编）：good（bare DNW+NW ring no guardring → 豁免 pass）+ bad（N+ solid rect + solid NW no P+）
- **ref**：`must_be_surrounded_check.py`（忠实 gold 的 composite-empty + outside-surround + wrong-side + ringCut 逻辑，argv 参数化）
- **拟 12-14 条 a-n**：zip 含脚本+py_compile / B exit0+判定 JSON / composite-empty 豁免（no NW→pass）/ composite-empty（no DNW→pass）/ P+ outside ring→pass / P+ solid covering→pass / P+ ring missing→fail / P+ inside wrong-side→fail / ringCut DNW 边界 band 中心 / N+ solid rect 场景 / B2 反硬编（B≠B2 判定集差异）/ 确定性两跑字节一致 / bad 4001;51 标记位置
- **复杂度提示**：gold 逻辑 intricate（composite 聚合 + ringCut 几何 + wrong-side 检测），check() ≥8 断言 + hidden B/B2 + negatives + 自验需**完整一轮预算**，非本轮 ~8min 可竣。故本轮止于 deepread，DEBT:1。

## 同轮 peeked-but-REJECT（已 parked，防重捡）
| sid | user | mc | 判定 | 理由 |
|---|---|---|---|---|
| 8v2mb | e0047488 | 70 | REJECT Q&A | "量测函数/多边形 interior/exterior-facing" 概念问答，read_files+RAG only，无 deliverable（同 r594 g1olj 量测函数 Q&A） |
| c5bgl | e0014566 | 85 | REJECT run-existing | "自动化执行 batch_auto_via.il2"，30 run_commands/run_code 驱动现有 SKILL，deliverable 在 live Virtuoso cellview，无离线 check teeth |
| nu82p | e0014566 | 82 | REJECT prompt-handoff | "read prompt.md and do the job" 单轮 thin |
| ya8nn | e0014566 | 73 | REJECT prompt-handoff | 同上 |
| ji8or | e0014566 | 72 | REJECT prompt-handoff | "read prompt_autovia.md / prompt_powerfill.md" = r586 djvnv dup |
| q2o4p | e0014566 | 67 | REJECT prompt-handoff | "read prompt_flow.md" 单轮 thin |
| werem | e0014566 | 66 | REJECT run-existing | "先跑 gen_autovia_agent.py 再跑 run_autovia_agent.il RunAutoViaNoGui()" live Virtuoso |
| uh5fg | yan1zh | 65 | REJECT Q&A | "怎么判断哪些线是 shielding 坐标" 单轮 Q&A |
| 4a2wn | xxchen | 56 | parked-低优 | "理解 DRC connect QA 工具 connectivity/run.py，记录运行逻辑+检查方法" doc/explain；新标准可造但 check teeth 弱，待 doc-structure-check 模式成熟再回访 |

## 观察
- fresh 池 mc≥10 top 12（mc 67-103）绝大多数为 **Q&A / run-existing / prompt-handoff**（e0014566 prompt-handoff 集群 + xinqiaoz skill-orch A-line + 概念 Q&A），produce-task-at-bar 命中需降到 mc 50-70 + known-author 过滤（xxchen 5zola 命中）。
- 5zola 是"trace 仅含请求+上下文收集、实现在外部（0.5/codebase）"的子型 —— gold 可从 codebase fetch 确证，trace-faithful 依据是 **U3 用户原话 spec**（同 r591 B档 synthesized：gold 从用户意图+框架合成，非直接提取 trace agent 输出）。
- 下轮 r596 第一件事：交付 MustBeSurroundedCheck-001（清 DEBT）。fetch gold `must_be_surrounded.py` 全文 + inside_surround_ring.py 范本 + 2 good/2 bad pattern 文件作为合成依据。
