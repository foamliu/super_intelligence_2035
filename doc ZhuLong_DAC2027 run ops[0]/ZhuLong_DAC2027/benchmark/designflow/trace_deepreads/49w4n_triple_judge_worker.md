# 深读笔记 · 49w4n · e0039602 · triple-generate-judge 编排

> trace_source: user=e0039602, host=hfeg0pkn002, session=1793323182278_49w4n, mc=118
> keywords: verilog:390;netlist:164;pyaether:13 ... (a=390 c=16 b=0 n=164, top=verilog, clean A-dominant digital)
> session 形态：目录 `/home/e0039602/.cline/data/sessions/1793323182278_49w4n/1793323182278_49w4n.messages.json`（autofs，需 `ls /home/<u>/` 触发）
> agent: deepseek-lead；83 msgs；530KB；4 user_text_turns
> 项目：`/home/e0039602/Documents/verilog_lib_trans_v1.4.1`（网表 cell-converter，同 r399 VlibDetConvert / r410 VlibFlowRetryRewrite / r419 SvConvTimeoutSkip 的 verilog_lib_trans 项目，**本轮 deliverable 与三者零重叠**）

## 真实用户意图（4 user turn 全文摘录）

- **U#0（produce-task 主诉）**：「请你仔细阅读这个项目，然后做出以下的修改：将项目改为每个 model 独立调用三次大模型，生成结果，然后再将原始网表，转换规则和三次转换的结果一同拼进一个 prompt 里。然后让一个新的独立调用阅读这个模型，最后输出一个数字，注意仅需要输出一个数字，数字代表判断出来哪个写的更好，然后将这个 AI 判断的写的最好的写入 resultmap 当中，如果三个写的一样或者差不多就用第 1 个，同时你要调整以下 workers 的并行策略，尽量让三个同时生成然后再直接进行对比，如果有重试一次失败的 workers 就直接跳过，记住现在我们只允许重试一次，这样可能会出现比如一个 model 有的失败跳过了有的调用没有失败，那就直接对比没有失败的两个，如果只有一个那就直接选他。当然用于选择的那个调用也有可能出问题，比如没有按要求只输出数字，或者其他问题等等没输出出来，这个最多允许重试一次，不行的话直接选择第一个放入 resultmap，我说完了，你有什么要问的请问，请你确认好怎么做了之后开始执行」
  - **A-faithful 判定**：✅ 合格。user 给的是**行为需求**（3 次并行调用 + 评审选最好 + 重试一次 + 跳过失败 + 评审失败兜底选第一个），**没给实现**（没给代码、没给根因、没给具体函数签名）。agent 须自己读懂项目、设计 helper、改 run_module。
- U#67：「说中文」（style 修正）
- **U#69（refinement）**：「失败的被丢弃。如果只成功 1 个或 2 个，就只对比这几个只成功了一个就不需要对比了哇，直接用就行了」→ **关键补丁**：成功候选只有 1 个时**跳过评审**，直接采用（省一次大模型调用）。
- U#81：「你现在工作在哪个目录下」（Q&A，agent 答 `/home/e0039602/Documents/verilog_lib_trans_v1.4.1`）

## Agent 工程操作（deepseek-lead）

- `list_allowed_files` ×2（项目根 + src/，摸结构）
- `read_files` ×~10：run.py（686 行顶层入口）、config.yaml、README.md、src/parallel_worker.py（270 行，并行 worker）、src/agent_client.py（LLM client）、src/rules_prompt.py / rules_prompt02.py（RULES + build_prompt_parts + OUTPUT_MODE）、src/output_validator.py
- `search_codebase` ×2（`^RULES\s*=`、`build_prompt_parts`、`OUTPUT_MODE\s*=`、`_WORKER\['max429'\]`）
- `editor` ×~12 改 `src/parallel_worker.py`：
  1. 加 import（`from concurrent.futures import ThreadPoolExecutor`）
  2. 新增 `_attempt_generate(cli, prompt, module_name, static)`：单次候选生成，**最多 2 次（只允许重试一次）**；返回 `(result dict, 本次该候选实际调用大模型的次数)`
  3. 新增 `_generate_candidates(cli, prompt, module_name, static, n=3)`：`ThreadPoolExecutor(max_workers=3)` 开 3 线程并行生成；每个失败重试一次再失败则 skip（result=None）
  4. 新增 `_judge_best(cli, blk, cands, module_name)`：独立评审调用 → 输出**仅一个数字**；没按要求/空/调用失败 → **重试一次**；仍无效 → `return 0`（选第一个）
  5. 替换 `run_module` body：并行 3 候选 → 收集成功 → （U#69 后）`if len(cands) > 1: chosen = _judge_best(...) else: chosen = 0` → 写 resultmap
- `run_approved_command` ×~8（profile=python-runner）：
  - `_syntax_check.py`：py_compile → SYNTAX_OK
  - `_check_triple.py`：mock `_FakeClient`（generate 可编程：'crash'/'empty'/'ok'）测 test_all_success / test_all_fail / test_attempt_first_try / test_attempt_retry / test_judge_picks_number → 全 OK
  - `_verify_final.py`：FINAL_VERIFY_OK
  - `_cleanup_tmp.py` / `_cleanup2.py`：删临时文件（自清理）
- 最终：compile + import + mock-behavior 全过，临时文件清理干净，只留 `src/parallel_worker.py` 的修改

## 沉淀的需求（可合成 deliverable 的维度）

→ **新 archetype：parallel-candidate-judge / triple-generate-judge 编排器**（第 5 类，与 r399 parser / r410 flow-policy-rewriter / r418 two-pass-assembler / r419 timeout-skip 不同）

1. **N 路并行候选生成**（ThreadPoolExecutor(max_workers=N)，N=3）← agent `_generate_candidates`
2. **每候选最多重试一次**（失败→重试→再失败→skip）← agent `_attempt_generate` "最多尝试 2 次（只允许重试一次）" + U#0 "只允许重试一次"
3. **失败候选丢弃**（不参与对比）← U#0 "失败的被丢弃" + U#69
4. **独立评审调用**（输入=原始 prompt + N 候选结果；输出=仅一个数字 1..N）← agent `_judge_best` + U#0 "最后输出一个数字，注意仅需要输出一个数字"
5. **评审最多重试一次**（没按要求/空/调用失败→重试→仍无效→兜底选第一个）← U#0 "这个最多允许重试一次，不行的话直接选择第一个放入resultmap"
6. **成功候选 ≥2 才评审**；**仅 1 个直接采用**（跳过评审）← U#69 "只成功了一个就不需要对比了哇，直接用就行了" + agent `if len(cands) > 1`
7. **0 成功 → 整体失败**（无候选可写）← 逻辑推论
8. **写 best 到 resultmap**（chosen_index 指向成功候选槽位）← U#0 "将 AI 判断的写的最好的写入 resultmap"

**TFC（trace-faithfulness coverage）= 8/8 = 100%**（8 维度全可追溯到 U#0/U#69 + agent 实际代码）

## 合成方案：TripleJudgeWorker-001（digital L1 spec-driven-gen B档）

- **deliverable** = `triple_judge_worker.py`（纯 stdlib；暴露 `run_triple(gen, judge, prompt, n_candidates=3) -> dict`；gen/judge 为可调用 mock，便于 check.py 注入受控行为）
- **A（visible）**：spec.md（API 契约 + 8 条规则 + 1 个示例场景：3 成功 + judge "2" → chosen_index=1）
- **B（hidden）**：10 个场景脚本（gen/judge 行为各异：全成功/部分失败/全失败/judge 正常/judge 重试成功/judge 重试失败兜底/judge 越界/单成功跳过评审/重试一次计数/并行计时）
- **check.py**：独立顺序 oracle（无 ThreadPoolExecutor，重算每个场景的 expected dict）+ 16 条件 + 并行计时条件 + 跨输入守卫
- **k 目标**：16（≥8 硬闸门）
- **negative**：naive_empty / print_only / core_removed（删 judge 兜底）/ hardcoded_A（硬编 A 示例答案，B 场景失败）

## 选料决策

- 为何选 49w4n：refined-A fresh 池（240 dedup, 45 truly-4-shard-fresh）top by mc + clean A-dominant + **唯一 clean produce-task**（swhjl/i73zm/ui4hv 全 Q&A/brainstorming weak；ddprg r410 已 peek weak Q&A）。e0039602 = A 域 proven user（r399/r410/r419 三 case，verilog_lib_trans 项目，4 个 case deliverable 零重叠：parser / flow-rewriter / timeout-skip / **本轮 triple-judge-orchestrator**）。
- 4-shard 交叉核对：49w4n ∈ A-ledger？否。∈ B/C/D ledger？否（truly-4-shard-fresh）。无撞车风险。
- 域归属：digital（verilog 网表转换工具的 LLM 编排，离线 Python，无真 EDA 工具驱动）→ L1。§5 L1≤30% 配额：A 域近期 L1 比例已高，但本 case 是 clean produce-task 且新 archetype，可接受（B 档合成纯 stdlib 可验行为）。
