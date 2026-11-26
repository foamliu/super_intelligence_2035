# 深读笔记 · 1793322661521_d3ytc (zhiguo1w @ hfeg0pkn001/10.129.2.10)

- **trace**: 1793322661521_d3ytc.messages.json (8.2MB, 175 msgs, 73 user turns)
- **user**: zhiguo1w — **NEW (0 case in ledger_C)**；agent=lead calibre Dummy 脚本分析
- **mc/tools**: tot=59, 59 calibre + 1 pyAether (cron 口径)；真实 session 以 read_files/list_allowed_files/run_approved_command(python-runner) + editor 为主，无真跑 calibre（用户在 cline 里读脚本+配置，分析逻辑）
- **workspace**: /home/zhiguo1w（用户家目录，临时 grep*.py 脚本写这里用完即清）；分析对象 /home/pdk/zhiguo/Dummy/learning/script/0.3.3/（PDK 只读）+ 用户附件 calibreDummy.rule / calibreDummy_chip.rule / QA_chip.gds / QA_chip.drc.results
- **claimed + 出 case**: r273 (2026-11-09)，EDA-Eval-DesignFlow-DummyRuleCfgParse-001

## 用户真实意图（U#0 提出需求，未给根因 → A-faithful eligible，本案做 B 档）
- U#0：「帮我分析一下该文件夹下的所有文件，并分析出*_Info的读取和使用方法已经配套的脚本，路径为/home/pdk/zhiguo/Dummy/learning/script/0.3.3/」
- 后续多轮细化：U#52「按照这个config运行，M1A_Info怎么其作用」+附件 calibreDummy.rule；U#58 calibreDummy_chip.rule 问 M1A_Info + BLOCK LIST M1A PROHIBIT CMP；U#70「总结 defineMainBLK_Info* 各种方式区别与联系」；U#74「在该gds加dummy为什么没生成SCC，为什么AT4/PG只生成在DGX/KGX」+QA_chip.gds；U#99 跑出结果 QA_chip.drc.results；U#115「分析 LendSpace 作用逻辑」；U#143「[list 1] [list 2 3 4 5] 代表什么」；U#147/149/151 spec_empty/LendSpace/selBigPattern 作用；U#159 Array_spaceMax；U#167 CMP_RECT_SHIFT_MARK_X。
- **本质**：code-comprehension / config-schema 分析。assistant 真实产物 = 一系列临时 grepinfo*.py / grep_*.py（grep _Info 定义、ADDINFO flow、M1A SVRF、SCC/AT4/PGZ 规则、LendSpace、selBigPattern、Array_spaceMax、CMP_RECT_SHIFT_MARK_X），用完即 cleanup_tmp.py 清掉。最终交付是**散文解释**，非可运行产物。

## 为何 B 档重定义为「calibreDummy.rule 配置解析器」(L2)
- 真实 assistant 产物是临时 grep 脚本 + 散文，无确定可判分交付。
- 但用户的**核心信息需求**=「把这份 TCL 配置的结构化信息提取出来」（掩模/cmp 参数/层 Info/BLOCK 表/字段 schema）。
- 重定义：写独立 `parse_dummy_rule.py`，吃 calibreDummy.rule → 结构化 JSON。check.py 在 hidden B 上 subprocess 真跑候选(L2)，断言 JSON 结构 ≥8 条件。
- A = 真实 calibreDummy.rule 的 frame 分支（忠实结构，361 行原文裁剪保留全部结构模式：GDS_TYPE 分支、TYPE_* list、*_cmp 三种 schema(MP/LINE/RECT/SOH)、*_lay、*_Info(concat 拼接)、Info_Extent/overUnderExtent/Size、CMP_BLK_OR+SOH_BLK_OR 两张 BLOCK 表、KEY_CMP_MP+KEY_SOH schema、$var 引用、[lindex ...] 计算式、反斜杠续行）。
- B = chip 分支，含 TYPE_CMP_MPstack 子掩模(AT4b/AT4s/PGZb/PGZs)、不同 globals/BLOCK 表，外加一个 frame 分支 TYPE_SOH 覆盖（必须不生效，防 wrong_gds_branch）。

## grounding（scp 真实附件到 .75 workdir）
- calibreDummy.rule (27889B, 361 行) — 用户 U#52 附件，frame 分支生效；A 资产忠实复刻其结构。
- calibreDummy_chip.rule (3.6MB, 23705 行) — U#58 附件，expanded SVRF 输出，太大不用作资产。
- 真实脚本树 /home/pdk/zhiguo/Dummy/learning/script/0.3.3/（common/defineBLK/drc/genDummy/typeFlow/init.tcl/output）— 经 read_files/list_allowed_files 在 trace 里读到，未 scp（重定义不需）。

## 选料决策
- r273 选料：r272 出完 knbkz(layout_aether) 后，r273 触发 .75 rescan 扫 eda_trace_2026110{6,7,8,9}.log，python 过滤(lay≥15 ∧ sim≤lay*1.1)得 650 fresh(未排 ledger)，排 ledger_C 469 normalized sid 后 359 fresh，其中 NEW-user 24 条。
- 顶部 NEW-user 候选 peek：xpor0(e0044587,lay=396)=harness/policy-engine token 消耗测试 REJECT；98ha6(e0032903,lay=61)=skill-writing/RAG harness REJECT；th4j1(e0044587,lay=33)=RAG_MCP_Server 测试 REJECT；**d3ytc(zhiguo1w,lay=59)=CLEAN 真实 calibre Dummy 配置分析种子 → 选用**。
- adminai@pkn004 10 sessions 全 virtuoso-only(疑似测试账号)不取；npkmm=e0031982 自身不取。
- d3ytc: NEW user, 59 calibre, 175 msgs 73 user turns, A-faithful eligible, physical_verify domain, 真实可判分重定义=配置解析器 → claimed r273。

## DISTINCT from 现有 physical_verify 系
- r237 DrcLogTeardownReport / r259 DrcConnectGraphGen / r239 DrcRuleTimeRank / r255 CmMaOpTableGen / r250 HcellPairGen / r251 LvsAmbiguityDiag / r256 LdrSvrfRuleGen / r262 SacapSpfCouplingExtract / r266 DrcPatternGeomGen 等 = 解析 DRC/LVS log 或翻译 SVRF/PVRS 规则。
- 本案首次 ground on「Calibre Dummy-fill 配置 schema 抽取」：从 TCL .rule 配置(GDS_TYPE 分支选择 + *_cmp 三种 schema + *_lay + concat 拼接 Info + BLOCK 表 + KEY schema)提取结构化 JSON。不同输入类型、不同核心算法。

## 自验（r273）
- golden parse_dummy_rule.py 在 B 上 15/15 PASS ✓
- 3-run sha256 一致 (0302790a114d5ced711a7bc94b5f12a6a0ae7a04ece907e78513db8e9b5ee17c) ✓
- 5 negative 全 FAIL (NEG_RC=0): empty_shell→c, print_expected→f, core_deleted→j, naive_only_scalars→e, wrong_gds_branch→e(TYPE_SOH 被 frame 覆盖) ✓
- §4.9 三假 (empty/print/core) 全 FAIL ✓
- test==disk check.py sha 38639bc5... 一致 ✓
- 断言闸门 k_rationale=k_check=15≥8 GATE PASS ✓
