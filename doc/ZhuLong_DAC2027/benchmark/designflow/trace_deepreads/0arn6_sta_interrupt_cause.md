# Deepread: 1794979399113_0arn6 (e0046913 @ hfeg0pkn004, mc20, pnr_signoff/STA)

**r765 选料 · 目录感知 liveness 复查轮**

## 选料背景

r760/r761 把 14 条 a_strong_pure 候选标 parked，理由"NOFILE (cline rotation)"，
并落 `a_pure_verdict_r760=EXHAUSTED_DEFINITIVE` / r761 `CONFIRMED_STRENGTHENED`。
r764 发现该 liveness 检查有缺陷（查文件 `.../3p6ld` 而非含 messages.json 的目录 `.../3p6ld/`），
复查 3p6ld 7/7 hosts 全 ALIVE。r765 据此对 r761 parked 的 14 条做**目录感知 liveness 复查**。

## 目录感知 liveness 复查结果（r765）

- **e0046913 cluster @ hfeg0pkn004: 8/8 ALIVE**（全部 strong A-pure STA: pt_shell/primetime/synthesis/netlist/rtl/verilog）
  - 1794790395375_uyvi5 (mc164, 1.79MB, mtime Nov 16 11:28)
  - 1794807450388_aqetb (mc85, 845KB, Nov 16 16:12)
  - 1794815708056_i7d8w (mc143, 997KB, Nov 16 17:30)
  - 1794885564034_8akpt (mc66, 398KB, Nov 18 09:20)
  - 1794969439750_najzl (mc44, 384KB, Nov 18 11:04)
  - 1794971954921_ejpf0 (mc48, 335KB, Nov 18 11:25)
  - 1794979399113_0arn6 (mc20, 75KB, Nov 18 13:27) ← **本轮选料**
  - 1794980853769_c8v5k (mc54, 689KB, Nov 18 20:27)
- **e0045144 @ hfeg0pkn002: 2/3 ALIVE**（strong A-pure digital/synthesis: verilog/rtl/synthesis/genus）
  - 1794819145943_twfqn (mc39, 452KB, Nov 16 16:52)
  - 1794986928161_u5wma (mc46, 405KB, Nov 18 20:25)
  - 1794793100170_g7hp7 (mc12) → NOFILE (真不存在)
- **zpla8 (tzuo, mc79)**: keywords = drc:1343/netlist:668/mosfet:129/hspice:42 → 实为 **C-domain DRC**，r761 误标 pnr_signoff，非 A-pure，跳过。

**结论：r760/r761「A-pure 枯竭 DEFINITIVE」结论被彻底推翻。10/10 真 A-pure 候选 ALIVE。**
r761 parked 的 14 条中 10 条应复活（9 条待下轮 re-mark 为 fresh；本轮先做 0arn6）。

## 0arn6 深读

- **用户 U0（唯一一条 user_input）**：
  `/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/1116_pa_cpu/sta/all_out/v1.0_Latest/log/sta_pre_WL_ssgnp_v0p675_0c.log 根据log，分析任务中断原因（思考过程中文显示）`
- **任务形态**：单轮 debug-Q&A / 分析诊断。用户给一份 PrimeTime STA 日志，要求分析中断原因 + 中文。
- **真实根因（agent 经读日志+文件系统核查得出）**：
  - **非**崩溃/OOM/超时/license，**而是**流程自身输入校验门 `check_config`（步骤 0, `0_check_config.tcl`）主动中止
  - 缺 pre 网表 `pa_cpu_merged_top.out.v`（`run/src_pre/` 目录整体不存在）→ 1 个致命 error
  - SDC `pa_cpu_merged_top.norm_occ_mbist.sdc` 也缺，但只 warning（非致命）
  - `check_config` 置 `CXDP_BLOCK_RUN=1` → 跳过全部 10 个下游步骤 → exit
  - 早退资源特征：elapsed 4s, TOTAL 1ms, RSS 992kB, 未加载设计
  - 设计/工艺：design=pa_cpu_merged_top, corner=ssgnp_v0p675_0c, stage=pre, delay=WL, rc=RCWORST, LIB_CORNER=WCL
- **agent 交付**：一份中文 markdown 分析报告（结论 + 日志证据链 + 早退资源特征 + 根因 + 修复建议）

## 造题决策

- **case_id**: `StaInterruptCauseAnalyze-001`，domain = pnr_signoff（shard A）
- **判分范式**: B=specificity oracle（静态 markdown 报告，无脚本可跑；沿用 r748/r755/r757 范式）
- **A 资产**: 真实日志 `sta_pre_WL_ssgnp_v0p675_0c.log`（从 trace 的 read_files tool_result 提取，299 行/16KB）
- **隐藏 B**: 合成 `sta_pre_WL_tt_1p0v_25c.log`——同结构 CXDP STA flow，根因不同
  （check_config OK, read_netlist OK, link_design FAILED, 3 unresolved references, design=pa_cpu_b_top, corner=tt_1p0v_25c）
- **check.py**: 15 条断言，subprocess 从 A 日志解析 ground-truth 签名（非硬编码）+ 随机抽 5 步×3 种子
- **k=15**（≥8 硬闸门 ✓），自验 ref PASS 15/15，5 negatives 全 FAIL（noop/print-expected/core-deleted/wrong-rootcause/hardcode-b）

## 下轮建议

1. **re-mark r761 parked 的 9 条 ALIVE 候选**（uyvi5/aqetb/i7d8w/8akpt/najzl/ejpf0/c8v5k/twfqn/u5wma）为 fresh，A-pure 池远未枯竭，可续造题
2. 更新 `summary_stats.json` 的 `a_pure_verdict`（r760/r761 EXHAUSTED → r765 OVERTURNED）
3. paper \Ntasks 同步（A 387）
