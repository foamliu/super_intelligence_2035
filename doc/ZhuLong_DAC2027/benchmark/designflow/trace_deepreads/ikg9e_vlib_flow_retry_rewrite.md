# Deepread: ikg9e — e0039602 verilog_lib_trans flow retry-policy rewrite

- **trace**: `1793344469517_ikg9e` · user `e0039602` @ `hfeg0pkn002` · mc=138 · 677KB / 114 msgs (60 user / 54 assistant)
- **scan kw**: verilog:415;netlist:185;drc:18;rtl:15;cadence:13 (clean A-dominant)
- **project**: `/home/e0039602/Documents/verilog_lib_trans_v1.4.2` (gate-level netlist → simlib model translation tool)
- **relation to prior case**: same project as VlibDetConvert-001 (r399/s9bc9/e0039602) but DIFFERENT deliverable — VlibDetConvert = conversion logic (gate-family mapping); ikg9e = FLOW ORCHESTRATION (retry policy + expr_check removal). No overlap.

## User intent (msg#0, A-faithful 原话)
> 请你阅读这个项目，告诉我他的工作流程，然后我知道其中有一步是大模型+py脚本进行真值表检查，现在请你直接将这个功能去掉，全量跑完之后直接做编译校准，编译校准错误后只需要再跑一次进行修改，不要像之前一样三选一

Two explicit asks:
1. **去掉 expr_check / 真值表检查**（"大模型+py脚本"逻辑等价校验，转换后、批量 xrun 前；"三选一"= 生成 3 候选 AI 评审选 1）
2. **改重试策略**：全量跑完 → 编译校准 → 报错只再跑一次修改（单轮单次，不再三选一）

## msg#107 follow-up (hang root cause)
> 为什么每次都是运行到这个model的时候卡住啊
→ agent 诊断：网关持续 502 让单 module 占满 max_module_minutes 时限。修复 = 加瞬时错误累计等待预算（max_transient_minutes），超限自动跳过该 module。

## Agent produce-actions (editor, key files)
| msg# | file | modification |
|---|---|---|
| #20 | run.py | 删 expr_check 调用块（`expr_check.run_batch_expression_check` + `if _ec.get('enabled')`）；注释改"已移除：全量转换后直接批量 xrun" |
| #24 | run.py | 修复回路 `_mayb = int((_xc).get('max_repair_rounds', 2))` → `_mayb = 1`（硬编码单轮单次） |
| #26 | config.yaml | `xrun.max_repair_rounds: 2 → 1` |
| #30 | config.yaml | 删 `expr_check:` 整节（enabled/workers/max_indep/max_repair_rounds） |
| #32 | xrun_check.py | DEFAULTS `'max_repair_rounds': 2 → 1` |
| #36,#41,#43 | parallel_worker.py | 注释 + log + `cfg.get('max_repair_rounds', 2)→1` |
| #72-#82 | agent_client.py | 加 `max_transient_minutes=10`（瞬时 5xx/传输累计等待上限，超限跳过 module）+ `trans_total` 累计 + harderror 升级 |
| #84,#86 | run.py / config.yaml | 构造 agent_client 传 `max_transient_minutes`；config 注释 |

## Invariants the rewrite must enforce (→ check conditions)
1. run.py 无 `run_batch_expression_check` 调用
2. run.py 修复回路 `_mayb = 1`（硬编码，不从 config 取）
3. config.yaml `xrun.max_repair_rounds: 1`
4. config.yaml 无 `expr_check:` 节
5. xrun_check.py DEFAULTS `'max_repair_rounds': 1`
6. rewrite_report.json 存在且 ≥3 条变更
7. run.py 无 `expr_check` 标识符（import 删除）
8. config.yaml xrun 节其他设置保留（stage/timeout 未被误删）
9. run.py 修复回路仍在（`for rnd in range(1,`），只改计数未删循环
10. report 每条含 {file, change} 键

## B档 synthesized 理由
A-faithful 不可行：verilog_lib_trans_v1.4.2 项目在 e0039602 私有 `/home/e0039602/Documents/`，SUT 沙盒不可达。提供合成 mimic（run.py/config.yaml/xrun_check.py 含同构 expr_check 块 + max_repair_rounds 设置），deliverable = 策略改写器。

## 随机化（§4.4）
check 对 B 输入随机扰动 max_repair_rounds 值（2-9）与 expr_check 子值，3 seed 各跑一次，断言不变量在所有扰动下一致（验改写器按结构改，非硬编码 N=2）。

## case plan
- id: `EDA-Eval-DesignFlow-VlibFlowRetryRewrite-001`
- domain: digital · level: L1 (offline spec-driven-gen; A 域 archetype, PIVOT L1 授权待用户裁决)
- deliverable: `vlib_flow_retry_rewrite.py` (--proj-dir/--out, 纯 stdlib)
- A: 3 文件 (run.py/config.yaml/xrun_check.py, N=2)
- B: 3 文件 (N=3, 不同 module/corner/规模)
- k=10 断言, 4 negative, §4.9 a/b/c FAIL
