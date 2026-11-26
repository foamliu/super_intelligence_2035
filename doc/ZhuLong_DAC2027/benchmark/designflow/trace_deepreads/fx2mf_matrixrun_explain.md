# Deepread: fx2mf — MatrixRun 目录文件含义解释 (explain Q&A)

- **session**: `1793672369557_fx2mf.messages.json` (子目录 `1793672369557_fx2mf/` 下)
- **user/host**: johnl @ hfeg0pkn001 (mc=104, spice_sim)
- **trace 路径**: `.75:/home/johnl/.cline/data/sessions/1793672369557_fx2mf/`
- **trace 大小**: 318KB / 34 msgs / 1 条 user_input

## 用户意图（U#0 原话）
```
<user_input mode="act">/rundata/drcoa/V0/simdir/finesim/drcoaF/MatrixRun/MatrixRun_Netlist_SpfBA_20260807PM_mBist   你看下这些文件什么意思</user_input>
```
**意图**：解释一个 FineSim/PrimeSim MatrixRun 仿真目录里一堆文件/子目录分别是什么意思。典型 explain/介绍 Q&A（verb "你看下…什么意思"）。

## 助手工具链
1. `list_allowed_files` 列目录 → 294 个 entry（脚本 + split 碎片 + corner 子目录）
2. `run_approved_command(python-runner)` 跑自写 `_categorize.py`：按扩展名/前缀分类统计 → TOTAL 294 / 13 SUBDIRS / 扩展名计数（sp×10, py×8, sh×5, log×2 …）
3. `read_files` 读流程脚本（01_gen_measures.py / 03_measure_run.sh / 02_measure_fscript_gen.py / 04_margin_measure.py / 01_gen_signal_measure_trtf_duty.py / 04_signal_measure_report_trtf_duty.py）— tool_result 在 trace 里空（未捕获内容）
4. 再跑 `_categorize.py` 列 corner 子目录内部 + 裸 split 碎片 head
5. 清理临时脚本 → 最后一条 `run_approved_command` 返回 `code_sidecar_sigterm`（会话被 sigterm 结束，**最终完整解释未写进 messages**）

## 目录结构（从 categorize 输出还原）

**根目录** `MatrixRun_Netlist_SpfBA_20260807PM_mBist`（294 entries / 13 subdirs）

**流程脚本（编号流水线）**：
- `01_gen_measures.py` — 生成 measure 语句
- `01_gen_signal_measure_trtf_duty.py` — 生成 signal measure（tr=transition / rf=refresh / tf? / duty）
- `02_measure_fscript_gen.py` — 生成 measure fscript
- `02_signal_runsp_gen_trtf_duty.py` — 生成 signal runsp
- `03_measure_run.sh` — 跑测量仿真
- `04_margin_measure.py` — margin 测量
- `04_signal_measure_report_trtf_duty.py` — signal measure 报告
- `05_format_split.py` — 格式化/切分（产出裸两位数 split 碎片 aa/ab/…/bz/ca…）

**结果子目录**：`margin_result` / `meas_log` / `signal_result` / `minimal_patches`

**Corner 仿真子目录（9 个）**：
- `primesim.DFT_mBist_CPF_CheckerBoard_WPst_0P5_tCH_50_BL16_4b8g_B0M_8240_FF_NODLLK.x8.FF1.3V-40C.X8`
- `…_FF_NODLLK.x8.FF1.3V110C.X8`
- `…_SS_NODLLK.x8.SS0.94V-40C.X8`
- `…_SS_NODLLK.x8.SS0.94V110C.X8`
- `primesim.DFT_mBist_RF_CheckerBoard_…` ×4 (FF/SS × temp)
- `primesim.DFT_mBist_RF_CheckerBoard_…_TT_NODLLK.x8.TT1.1V25C.X8`

命名解析：`primesim.<design>.<pattern>_<params>_<process>_NODLLK.x8.<voltage><temp>.X8`
- `primesim` = Synopsys PrimeSim/FineSim 仿真器
- `DFT_mBist` = DFT memory BIST（存储器内建自测）
- `CPF` / `RF` = 测试模式（CPF = maybe Check-Pass-Fail?；RF = Read-FAST/Refresh?）
- `CheckerBoard` = 棋盘测试 pattern
- `WPst_0P5_tCH_50_BL16_4b8g_B0M_8240` = 参数（写后停顿 0.5 / tCH 50 / BL16 / 4b8g / B0M / 8240）
- `FF/SS/TT` = process corner（Fast-Fast / Slow-Slow / Typical-Typical）
- `NODLLK` = no-DLL mode
- `x8` = device width
- `FF1.3V-40C` / `SS0.94V110C` / `TT1.1V25C` = 电压×温度

**Corner 子目录内容**（`primesim.…FF_NODLLK.x8.FF1.3V-40C.X8`）：
- `finesim.elog` (397KB) — 仿真日志
- `finesim.mt0` (18KB) — measure table 输出
- `glitch_meas.P{1-6}_S{1-6}_cm0_ts_ismsel_{6..1}_{6..1}_{FDEVHIGH|FDEVLOW|FLOGICHIGH|FLOGICLOW|FMID|RDEVHIGH|RDEVLOW|RLOGICHIGH|RLOGICLOW|RMID}.pmt` — **2161 个** per-pin glitch margin 测量文件
  - P = Phase（阶段），S = Step（步），cm = corner-mode，ts = timing-set，ismsel = ism-select
  - FDEV/RDEV = Falling/Rising edge **deviation** margin（高/低偏离）
  - FLOGIC/RLOGIC = Falling/Rising edge **logic** margin（逻辑高/低）
  - FMID/RMID = Falling/Rising edge **mid** margin（中点）
- `BiasTrimAccuracy` — bias trim 精度结果
- `crc_alert_chk.rpt` / `.crc_alert_chk.log` / `config_Alert` — CRC alert 校验
- `config_pincheck` / `pincheck` / `crc_alert_chk.rpt_bk` — pin check
- `control` — 仿真控制文件
- `force_power.inc` — force power include
- `netlist` / `netlistHeader` / `netlistFooter` — 网表
- `runscript` / `runscript_2EcH6` — 运行脚本
- `stimulus` — 激励
- `sxcmd` ×4 — Spectre/XA command
- `si` ×3 — simulation info
- `ihnl` / `raw` — 输出子目录（本例空）
- `.spfba_file` — SPFBA 标记文件
- `.sub_2EcH6` — sub 标记

**裸 split 碎片文件**（`05_format_split.py` 产出 + 大网表）：
- `a` (6.9MB) — SPICE continuation（`+BlbMsaq30<2015>…`）
- `a_part_aa` … `a_part_bz` (~52 个, ~255KB each) — split parts
- `netlist.presim.part.aa` (255KB, `*DDR5TOP` header) — presim 网表 split
- `d` (149MB, `.SUBCKT XdecGapx2Bot_DRCOA …`) — 大子电路网表
- `c` (0 bytes), `c；` / `a；` (中文分号命名碎屑)
- `map_define` — map 定义文件
- `tmp`, `presim`, `bash_history`, `.swp`

## 关键知识点（判分要点）
1. **directory_type** = MatrixRun = PVT-corner 矩阵仿真目录（一个 design×pattern 跨多个 PVT corner 跑 margin）
2. **simulator** = FineSim/PrimeSim（`primesim.` 前缀 + `finesim.elog/mt0`）
3. **design_target** = DFT mBist（memory BIST）/ DDR5（`*DDR5TOP` netlist header + BL16/4b8g/x8 DDR5 参数）
4. **flow_pipeline** = 编号脚本流水线 01(gen measures)→02(gen fscript/runsp)→03(run.sh)→04(margin/report)→05(format split)
5. **corner_naming** = `<process>_<mode>_NODLLK.x8.<voltage><temp>.X8`，PVT 3 process (FF/SS/TT)
6. **glitch_margin** = per-pin margin 测量（P/S/cm/ts/ismsel 维度 × FDEV/RDEV/FLOGIC/RLOGIC/MID 边沿类型）
7. **split_files** = 05_format_split.py 产出 + 大网表切分（a_part_* / netlist.presim.part.* / d = 大 SUBCKT）
8. **result_dirs** = margin_result / meas_log / signal_result / minimal_patches
9. **CRC/pin check** = crc_alert_chk + config_pincheck（BIST 校验机制）

## 合成判定
- **A 档不可行**：真实 MatrixRun 目录在 `/rundata/drcoa` 私有 DDR5 设计数据上，且 trace 最终解释被 `code_sidecar_sigterm` 截断未捕获 → 不能离线打包真实目录、也不能拿真实解释当 ground truth
- **B 档 synthesized**：用 mock fixture 忠实复刻目录结构（dir_listing.json + 流程脚本摘要 + corner 命名 + glitch_meas 文件名模式 + split 碎片），任务 = 写 `matrix_run_explain.py(workdir, out_dir)` 解析 fixture 产出结构化讲解报告 JSON
- **隐藏 B** = 另一 design（SRAM repair matrix / 不同 BIST pattern / 不同 simulator 如 HSPICE / 不同 PVT 集），cross-input guard 防 hardcode A
