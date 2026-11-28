# 0pwnz — DDR5 pattern RMW detect (mingyu1l@hfeg0plg100, mc=67, schematic_netlist)

## trace
- session 1795678581951_0pwnz.messages.json, 654KB, 61 msgs (32u/29a), agent=lead verification eng
- 两个子任务：

### Task1 (idx0-16) — 可合成核心
用户: `/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen_new/patterns/analogsim/Golden`
「分析这个文件夹下的 pattern 看有没有哪个 pattern 针对同一个 bgbk 进行连续的读写（包括 RMW）」

助手: list_allowed_files → 读 Golden001~Golden011 .v pattern 文件 + Force/*.sp/*.inc force 文件。
- pattern 文件是 Verilog task，含 DDR5 命令序列 (Active/Read/Write/Precharge/MPC/MRR/SREF/Load_Mode)，每条带 bg/bk/col/row/ap 参数
- Force/*.sp 是冗余熔丝注入 force 文件（不是命令 pattern）
- Golden006_Perbank_cs_gd_ref.v = SREF/MRR/Load_Mode，无具体 bank 读写

结论: **Golden007_Multi4bank_1GAP_4a4w4r_rdact_wract.v 最典型（真正 RMW）**，Golden002/Golden009 也含 R→W RMW。
- RMW = 对同一 (bg,bk,col) **先 Read、re-Activate 后再 Write 回同一地址**（read-modify-write）
- Golden007 rdact_wract: A(bg0,bk0)→R(bg0,bk0,colf,ap)→A(bg0,bk0)→W(bg0,bk0,colf,ap) = R→A→W 同址 = RMW
- Golden001_ActWrRdPre: A→W→R→Pre = W 先 R 后 = continuous_rw 但**非 RMW**（方向反）
- Golden002_4a4w4rPre: 每 bank A→W→R→Pre = W 先 R 后 = continuous_rw 非 RMW
- Golden006_cs_gd_ref: SREF/MRR/Load_Mode = no_bank_op
- Force/*.inc/*.sp = force_file 非 command pattern

### Task2 (idx17-60) — 不合成
找 Golden007 5-corner 波形文件。助手写 find 脚本扫 MatrixRun_* 树，发现 case 结构 `primesim.Golden007_*_<PVT>.X4/Golden007_<PVT>.fsdb`，5 corner = FF1.3v-40C/FF1.3v110C/SS0.94v-40C/SS0.94v110C/TT0.94v25C，1707 case 分布 60+ MatrixRun 目录，给出全齐目录表。属文件系统检索 Q&A，无独立算法核心 → 不合成。

## case 合成 plan
- task_id = EDA-Eval-DesignFlow-PatternRmwDetectProduce-001
- reframe: spec-JSON 驱动纯 Python DDR5 pattern 命令序列解析器 + RMW 检测器 `pattern_rmw_detect.py(spec)->report.json`
- LIVE-NA judge[L0,L1]（纯 Verilog 文本/命令序列解析，无真实 EDA 二进制依赖）
- 核心算法语义 encoded 为断言:
  1. 命令序列按 (bg,bk) 分组，识别 Read/Write bank op
  2. **RMW 检测**: Read(bg,bk,col) → re-Active(bg,bk) → Write(bg,bk,col) 同 col（R 先 W 后，中间有 re-Activate）— 区别于 W→R（continuous_rw 非 RMW）
  3. **continuous_rw**: 同一 (bg,bk) 既有 Read 又有 Write（不论方向）— RMW ⊂ continuous_rw
  4. **no_bank_op**: 仅 SREF/MRR/Load_Mode/MPC 无 Read/Write
  5. **force_file 排除**: .inc/.sp force 文件非 command pattern（is_command_pattern=false）
  6. RMW 要求同 col（R colA → W colB 同 bgbk = continuous_rw 非 RMW）
  7. re-Activate 必要性（R→Precharge→W 无 re-Activate 不算 RMW？实际 ap=1 auto-precharge 后必须 re-Activate 才能 W；判定看 R 后是否有同 bgbk Active 再 W）
- ~16 conds a-p（独立 gold 复算 rmw_pairs/continuous_rw_bgbk/classification/bank_accesses + anti-hardcode tokenize + 确定性 md5 + hidden-B 跨输入守卫）
- A visible spec_A.json: 6 patterns 镜像真实 Golden 结构（Golden007 RMW / Golden001 continuous_rw W→R / Golden002 4a4w4r continuous_rw / Golden006 no_bank_op / Golden005_force.inc force_file / Golden009 RMW）
- hidden-B spec_B.json: 6 patterns token-structurally 不相交（不同 bg/bk/col/patname，PatA RMW / PatB W→R / PatC no_bank / PatD force / PatE 4a4w / PatF RMW），A-hardcoder 在 B 全错
- 6 neg(empty/print_only/core_deleted/hardcode_a/wrong_dir_rmw/no_react) §4.9 trio distinct
- check() 返回 {'pass':bool,'detail':str} 严格契约
