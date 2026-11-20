# r842 — 意图审计 · digital 历史存量批 119 case · 审计收尾 100%

> 2026-11-15 最高优先令「重审已造的题」续做 · shard A · 2026-11-20
> 本轮 0-case 审计轮（A-pure 枯竭 r838 第 8 次确认，转审计）

## 产出

- `designflow/intent_audit_A.tsv` 325 → 444 行（+119 digital）
- 判定：**keep=119 / off_intent=0 / over_constrained=0 / downgraded=0**
- 与 r836/r837/r839/r840/r841 一致：旧配额扭曲是「选题模具」问题，非「已造题内容」问题
- 审计进度：**415/415 = 100% ✅（全部 4 域审完）**
  - digital 151/151 ✅（本批 +119 收尾，前 32 在 r836 batch2 generic-named）
  - eda_other 93/93 ✅（r840）
  - pnr_signoff 41/41 ✅（r839）
  - verification 130/130 ✅（r841）

## 形态分布（本批 119 digital）

| 形态 | 数量 | 11-15 reaudit 合法性 |
|:--|--:|:--|
| debug-Q&A | 48 | ✅ 合法（诊断/推测/根因） |
| produce-task/flow-build | 30 | ✅ 合法（生成/编写/搭建） |
| analysis-Q&A | 29 | ✅ 合法（分析/总结/查看/抽取/清点） |
| fix/migrate/merge | 11 | ✅ 合法（修改/迁移/替换/融合/适配） |
| concept-Q&A | 1 | ✅ 合法（概念问答） |

档位：A档 trace-faithful 74 / B档 synthesized 45（B 档 = 真实资产不可 headless 复现的合法 reframe）。

## 深核样本 12 例（diverse: 跨形态/档位/mc/用户）

逐条比对 `metadata.trace_source.real_task_summary` vs `prompt` vs `test_rationale`，全部 **keep**：

1. **AccAutoConnectSumm-001** (e0045144 mc18, analysis-Q&A): 用户原话「对 acc_auto_connect.pl 做全面总结,功能描述+校验+常见问题清单」→ check 验 summarize 脚本产出 JSON 含 script_purpose(RTL connect)/run_mode/output 等结构。忠实还原总结意图，非脚本化加难。
2. **AhbMasterVerilog-001** (e0045144 mc39, RTL authoring): 「please help me used verilog write AHB master design」→ check 验 ahb_master.v 端口/FSM/TRANS 类型。A档 faithful，无超意图。
3. **AsyncResetSyncRelease-001** (e0045128 mc22, concept-Q&A): 「异步复位同步释放电路是什么样的」→ check 验 2-FF reset_sync 行为模型在隐藏 B 时序上的 assert/sync deassert。Q&A 合法（11-15），行为模型 reframe 忠实。
4. **CPU8bitVerilog-001** (aaronji mc10, RTL authoring): 用 Verilog 写 8 位 CPU + 自检 TB → check 验 cpu8.v 16 指令/FSM/标志/ALU/TB 覆盖。忠实还原。
5. **CombSdcGen-001** (e0046913 mc89, DC flow): 「如何生成带真实时钟/IO 占位的 cla_top.sdc...帮我生成一份」→ check 验 gen_sdc.py 产 SDC 含 create_clock/set_input_delay。A档 faithful。
6. **CovFMFlow-001** (lorikx mc203, flow-build): 「再开两个文件夹,一个覆盖率检查,另一个形式验证,参考那个文件夹」→ check 验 cov/+fm/ 10 文件结构(fm.tcl source common_setup/URG/VCS coverage)。忠实还原 flow-build。
7. **CrcErrBitDiag-001** (tongfanl mc367, debug-Q&A→script): DDR6 CRC 注错诊断 3 问 → check 验 crc_err_bit_diag.py 诊断 DQ 重排/pad 段/CRC 段。reframe 合法（不可 headless 跑 xrun）。
8. **DCDirSwitch-001** (alan3zh mc324, produce-task): 「../tools/ 加 python 切换 DC_RESULT_DIR + 根 Makefile scan/replace」→ check 验 set_dc_result_dir.py + Makefile 两目标。忠实还原。
9. **DcUpfDiag-001** (alan3zh mc440, debug-Q&A): 「检查 dc.tcl/upf,推测 save_upf 为空 + netlist 无 VDD/VSS」→ check 验 diagnose_upf.py 诊断 root_cause/is_defect/evidence。A档 faithful（用户只给症状，rule 2 OK）。
10. **FiMergeVcs-001** (lorikx mc8, merge): 「@ppc_inject_fault.v line704-958 帮我融合到 @sp_sram.v」→ check 验 sp_sram.v v15.2 含 5 注入任务/parser/apply。A档 faithful merge。
11. **FindVfilesSymlink-001** (guomings mc6, produce-task): 「找到 libs/latest/ 下所有 .v 绝对路径,包括软链接,输出到 vlist」→ check 验 find_v_files.py followlinks+环路保护+去重排序。忠实还原。
12. **FlatNet-001** (yiminh mc526, B档 synthesized): 420MB CDL→flat Verilog 3 规则(no-\escape/no-ICV/no-VDD-VSS) → B 档小重建网表同 3 规则,check 验 flatten 输出。真实资产不可移植,B 档合法。

## 关键发现

- **off_intent=0**：本批未发现任何为凑 L2/L3 配额硬加步骤或把用户没要求的东西塞进判分的题。所有 case 的 prompt 要么用用户原话（A档），要么明确标注 synthesized 并保留原 trace 语义（B档）。
- **over_constrained=0**：未发现 check() 判分要求超出用户原始意图的题。debug-Q&A 类的 check 都验「用户想要的诊断结论结构」，produce-task 类验「用户想要的产物结构」，非额外文件结构/实现路径硬约束。
- **downgraded=0**：本批 119 全 standalone，无 v1/v2 对（14 v1/v2 对已在 r837 审完，34 v1 downgraded）。digital 域无旧配额 v1 可下线。
- **形态真实分布**：digital 域 debug-Q&A 占比高（48/119=40%），符合数字域「仿真失败/约束诊断/CRC 注错/时序不满足」真实工作特征；analysis-Q&A 29 含「分析时序弧/清点依赖文件/总结脚本/抽取结构」等真实意图；produce/flow-build 30 含「写 CPU/AHB/SDC/gen_design_list/切目录工具」；fix/migrate/merge 11 含「迁移 DC 脚本/融合 fault inject/适配 TM_FsPgm」——全部 11-15 reaudit 后合法形态。

## 结论

digital 历史存量批 119 case 与 r836-r841 五批一致：**旧配额（L1≤30%/L2≥50%/L3≥20% + 只做 L2/L3 + analysis-only 判 weak）扭曲的是选题模具，不是已造题内容**。所有 415 case 审完，off_intent/over_constrained/downgraded 仅来自 r837 的 34 个 v1（已被 v2 重做覆盖，jsonl 行保留作口径变迁证据）。

**2026-11-15 最高优先令「重审已造的题」全部完成 ✅（415/415 = 100%）**。

## 守纪律

- 任务初衷第 1 条（任务形态=用户意图）：✅
- §4.3/§4.6 硬闸门：本轮无新 case，纯本机 jsonl 审计
- shard 纪律：只审 A 域 case，未碰别 shard 文件
- 本轮无 eda_flow session 操作

## 数据

- A.jsonl 415 不变 · cases/A 不变 · 台账 A 685 不变
- 🎯 通过率: 观察值（未跑 pi）
- 📊 trace 覆盖率: 405/487=83.2%（不变）

## DEBT（下轮）

- (a) 候选池重审 `pool_reaudit_A.tsv` 续做（11-15 令第二半，当前 20 行，A-pure 枯竭下扩池主要靠此）
- (b) cases/A 19 intra-shard dup 清理
- (c) 新全量扫描扩池（🟢 daily≤1，超 40min 预算需专门轮）
- (d) waveview_real_cases 协作
- (e) 6 near-dup 对 cross-case dedup 专门轮
- (f) 6 v1-missing git history 核查
- discuss r842 due r837+4=r841（本应 mandatory 清付，但本轮审计收尾非 case 轮；下轮 discuss 与候选池重审/造题一并清付）
