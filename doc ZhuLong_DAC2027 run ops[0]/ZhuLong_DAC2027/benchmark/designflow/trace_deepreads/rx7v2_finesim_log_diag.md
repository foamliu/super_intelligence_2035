# 深读笔记 · 1794210513201_rx7v2 (t0002802 @ hfeg0pkn005, mc=17, spice_sim)

- **session**: 1794210513201_rx7v2.messages.json (198KB / 36 msgs / 2 user turns)
- **user**: t0002802 @ hfeg0pkn005
- **domain**: spice_sim (FineSim CRG Core Timing 仿真日志诊断)
- **旧判**: parked "L1 read-log explanation/diagnostic no produce-task" → r618 reaudit 复活 (debug-Q&A 合法形态)
- **trace host**: hfeg0pkn005 (ssh from .75 OK, trace 在 /home/t0002802/.cline/data/sessions/1794210513201_rx7v2/)

## 用户真实意图 (逐字)
- U#0: `/rundata/drgqa/V0/simdir/finesim/workdir/alrenc/REVC_CoreTiming/Final_0831/lsf_job_error.log 帮我检查这个文件中说了什么`
- U#6: `/rundata/drgqa/V0/simdir/finesim/workdir/alrenc/REVC_CoreTiming/Final_0831/Result/SS1.06V-40C.log 告诉我报错原因`

意图 = 解释两个 FineSim 仿真日志的报错原因 (debug-Q&A / explain)。

## 助手诊断链
1. read_files lsf_job_error.log → 16 行，全部是 FSDB Reader (Verdi_T-2022.06-Beta0) 启动 banner + 版权声明，8 次启动跨 09/07、11/04、11/09 三日期，**无任何实际 error 内容** → 建议查 lsf_job.log / finesim.log / bjobs -l
2. read_files SS1.06V-40C.log → 44 条测量语句，17 PASS / 27 FAIL
   - 核心失败: tWLon=failed (字线从未导通) + tSAon=failed (感测放大器从未开启)
   - 连带失败: tWL (targ not found) / tCS / tSEN / RDtoCSL / tRCD / tRAS / tRP / tWR / VMSN_N_MIN(from=0 to=0) / PREtoWLoff_90p / WLoff_20p / EQonMR / VCS_90P
   - 通过: pvpcsg/pvcc/pvwlp/pvdleq/pvwln/pvblh/pviso 电压偏置 + CS_start/ACT_csn_valid/RD_csn_valid/WR_csn_valid/Pre_csn_valid 命令时序 + VILDQ/VIHDQ + tCK_t(312ps) + ACT_PREI(30.6ns) + tOC(2.77ns)
3. 根因: SS/1.06V/-40C 最慢角下 ACT 命令 @1.002321us 已发出但字线驱动器未触发 → WL 不开 → SA 不工作 → 全部 downstream timing 测量失败
4. 6 条可能原因: WL 驱动时序余量 / VPP 过低 / timing chain 断链 / trim/DLL 参数 / VCS 电压域异常 / 仿真波形不完整
5. 后续: 用户选 "1" → agent 用 waveview-fsdb-readerV2-2 从 finesim.fsdb 提取 WL/SAEN/VPP/VCS/VMSN_N 信号

## 合成 case
- **case_id**: EDA-Eval-DesignFlow-FinesimLogExplainDiag-001
- **形态**: A 档 trace-faithful, debug-Q&A → 结构化诊断报告 JSON (parse 2 logs → report)
- **A 文件**: doc/lsf_job_error.log (16 行 FSDB banner) + doc/SS1.06V-40C.log (44 测量, WL/SA 核心失败) + doc/scenario.txt
- **hidden B**: FF/1.16V/125C 角, bitline equalizer/precharge 失败 (tEQoff/tBLEQ/VBLP_MIN 核心失败, tWLon PASS), Verdi_T-2023.12-SP1, REVD/Final_0120/kipfang/drgpb
- **任务**: 写 finesim_log_diag.py(workdir,out_dir) 解析 doc/ 产 finesim_log_diagnosis_report.json (9 顶层键)
- **check.py**: 29 条独立断言 (a..ac), cross-input B guard (corner/version/core-failure 全异) + A-leak guard (13 A token) + 确定性 3 rerun + §4.9
- **自验**: ref 29/29 PASS + 4 negs (empty→h / print-only→h / hardcode-A→l version mismatch / deleted-core→ab cascade<3) 全 FAIL
- **k_rationale == k_check == 29 ✓**
- **新形态**: FineSim measurement-log 核心失败/连带失败分类首例 + bitline-EQ-vs-WL cross-input guard 首例
