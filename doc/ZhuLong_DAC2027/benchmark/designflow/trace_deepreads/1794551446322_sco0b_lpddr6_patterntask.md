# Deepread — 1794551446322_sco0b (eva1li @ hfeg0pplg74, verification, mc=85)

## 来源
- **session**: `1794551446322_sco0b.messages.json` (1.81MB, 347 msgs, agent=lead/zhulong)
- **user**: eva1li, **host**: hfeg0pgn74 (10.129.8.112)
- **domain**: verification (LPDDR6 testbench pattern tasks)
- **旧 parked 原因**: r503 仅看前 8/31 user turn（全是 search/where/what Q&A），判 "analysis Q&A only, no produce-task" 而 REJECT。
- **复活理由**: 11-15 令要求重审 parked 误杀；完整 31 个 user turn 中 USER#15/16/17/18/19 均为 produce-task（提取 task→txt/excel）。旧 reject 基于不完整 peek。

## 用户意图（31 个 user turn 摘要）
- USER#1-14: where/what 类 code-comprehension（CMD_JUMP_cov 调用、TYPE_tb/csfck1_state 定义、PowerUp/compare_enable/SetDataRateSpeedMR/cmdtcal 机制、各宏 HSPEED/LocalPower/ALL_REVD_FUSE/DEFF/USESDF/CBT_SPEED_LIMIT/X24 含义）。
- **USER#15（本 case 选料）**: "整理出 cmds_onebank 这个下面的所有 task，按 task 和描述为一行输出到 patterns/function 下面的 txt 文件" — **produce-task**。
- USER#16: 比对 task 列 vs patlist，删 patlist 里不存在的 task。
- USER#17/18/19: 整理成 excel。
- USER#20-21: 分析 A_Summary.rpt 报错 + 检查 WL/RL/WCK·CK 同步。
- USER#22-31: 各宏/字段含义 Q&A。

## 选料决策
- 选 USER#15：最 concrete、可 check 的 produce-task。
- 真实文件 `/proj/decqa/V0/simdir/verilog/eva1li/1103_lp6tb/patterns/function/cmds_onebank/` 对 .75 与 ssh(e0031982) 均 **Permission denied**（项目目录跨组保护），真实 .v 文件与生成的 txt 均不可读。
- → **B档 synthesized**：按 trace 中真实 LPDDR6 pattern 命名约定（ActMPCWrl0Wr1Rdl0RdAp1MRR 等）+ 真实令牌语义表（从 eva1li cline 会话里 agent 写的 build_onebank_list.py 完整提取）合成 faithful replica `cmds_onebank_A/`（12 .v）+ `hidden/cmds_onebank_B/`（12 .v，task 名与 A 完全不相交）。

## 真实令牌表（从 trace 中 agent 脚本 verbatim 提取）
WFFWFF→WFF(写FIFO)x2 / RFFRFF→RFF(读FIFO)x2 / WFF / RFF / RefAll→REFALL(全组刷新) / Refn,Ref→REF(刷新) / PreAll→PREALL(全bank预充电) / Prepb,Pre / MRW / MRR / MPC / RDC / PDIns / SRPDE,SRPD / SRX / SRE / PDX / PDE / Wrl(\d)→WRL(写长burst)bank<N> / Wrl / Wr(\d)→WR(写短burst)bank<N> / Wr / Rdl(\d)→RDL(读长burst)bank<N> / Rdl / Rd(\d)→RD(读短burst)bank<N> / Rd / Ap(\d)→AP(自动预充电)bank<N> / Ap / CBT→CBT(CA总线训练) / Act→ACT(激活) / CAS / NOP / DES / DSE。
顺序敏感（更长/更具体令牌先匹配）。agent 实测 160 task stray=0。

## case 落地
- **case_id**: EDA-Eval-DesignFlow-PatternTaskDecodeProduce-001
- **domain**: verification, **tier**: B(synthesized), **difficulty**: L1（纯 stdlib 静态解析 + 令牌解码，subprocess 跑 B 验泛化）
- **deliverable**: outputs/submit.zip = build_pattern_task_list.py + cmds_onebank_tasks.txt
- **check**: 15 独立条件 (a-o)：zip 结构 / py_compile / B 运行 exit0 / 行数==B task 数 / B 名集合==期望 / 每行 name<TAB>desc / stray=0 / desc==gold 解码 / 3-run 确定性 / B∩A 名不相交(防 hardcode-A) / A 运行也得对 / A≠B(防单清单) / 注释头格式 / 字典序 / 头计数==行数
- **negatives**: neg_empty / neg_print_only / neg_core_deleted / neg_hardcode_a — negative_selftest 全 FAIL，ref PASS
- **hidden B**: cmds_onebank_B/ 12 .v，task 名与 A 完全不相交（A 用 ActWr0RdAp0 等，B 用 ActRdl0Wrl1Ap1MRR 等）
- **自验**: ref PASS（A 12 task stray=0，B 12 task stray=0）+ 4 neg 全 FAIL + test==check.py 字节级一致 + k_check=k_rationale=15≥8

## 纪律
- ✅ 无脱敏（保留 eva1li/hfeg0pgn74/真实路径），仅未含 key/token
- ✅ cases/A/<task_id>.json 单文件格式（未碰 *.jsonl）
- ✅ 未碰别 shard / 未 git add -A / 未改题图难度
- ✅ eda_flow session 仅只读 ssh 抓 trace，未写远端
