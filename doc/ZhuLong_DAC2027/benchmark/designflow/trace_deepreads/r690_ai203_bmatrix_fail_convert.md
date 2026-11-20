# r690 — ai203 deepread + BmatrixFailConvert-001 合成

**轮次**: r690 (单轮闭环: l0x4z 不可造诊断 + ai203 深读 + 合成 BmatrixFailConvert-001)
**日期**: 2026-11-17
**shard**: A
**trace 源**: `1792395143753_ai203.messages.json` @ `/home/yuankong/.cline/data/sessions/1792395143753_ai203/` (.75 本机可读)
**user/host**: yuankong @ hfhds201 (.75 本机) / 亦分布于 hfhds206/210/211, hfeg0pfn023/036 等
**mc**: 5 (11-16 快照, keywords drc:65;verilog:23;netlist:11;pyaether:1)

## 一、l0x4z 不可造诊断（r689 复活线索 A 复审）

trace `1791883133340_l0x4z.messages.json` (36 msgs, 1 user turn):
- U#0 verbatim: `AddressParameter.v中的COLA赋值给了谁`
- 助手在 trace 中 4 次 `search_codebase` 全 30s 超时, `run_commands` 被 policy 禁用, `run_approved_command` 需 .sh filePath, `find_file.sh` 全盘 `find /` 超时 SIGKILL, 最终放弃并 ask_user 「文件不在可见 workspace」。
- **关键事实**：`find /home/yuankong -name 'AddressParameter*'` 在 .75 本机 30s 返回空 —— **真实文件不存在**（不在用户 home, 也不在 .75 任何可读位置）。
- 判定：**不可造**。理由 = 顶部任务初衷第 3 条「真实性=唯一来源」+ 第 2 条「交付结果=判分对象」：用户意图是要在自己真实 AddressParameter.v 里查 COLA 赋值，但真实文件不在 trace 也不在用户磁盘 → 无 evidence anchor，写不出能区分真假交付的 check()（A 档无文件可放，B 档合成=发明用户没要求的内容，违「任务形态=用户意图」）。归类 parked_unmakable (no evidence anchor)。
- **不计入"mc≥5 池枯竭"判据**：l0x4z 是"无真实 trace 文件支撑"的不可造，不是"能忠实还原意图且可判分"口径的枯竭。

## 二、ai203 深读（r689 复活线索 B 复审 → 确认可造）

trace `1792395143753_ai203.messages.json` (14 msgs, 3 user turns, 45KB):

### 用户真实意图（trace-verbatim, 3 turns 收敛）
- U#0: `可以帮我写个脚本吗` (开放)
- U#10: `写个python的` (定语言)
- U#12 (核心, verbatim): `帮我写个脚本，我可以在某个路径下，例如/proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_csgd，执行bmatrix -f，会得到下面的文本` + 5 行真实 `Fail  primesim.<TestName>.<xN>.<Corner>.<XN>` 输出 + `将其转换成另一种格式，生成文件sim.save_rerun,格式转换示例，例如把<1 行 input>转换成，<1 行 output>这样的格式`

### 5 行真实 Fail 输出（A 档 evidence, verbatim from U#12）
1. `Fail      primesim.CRC001_Dualbank_act_wr_rd_err_RPre_2A_RPst_1P5_WPre_3_WPst_0P5_CRC_01_0_tCH_50_BL32_OTF_4b8g_BbK_9600_TT_CSGD.x4.TT0.94V25C.X4`
2. `Fail      primesim.CRC001_Dualbank_act_wr_rd_err_RPre_4_RPst_1P5_WPre_3_WPst_1P5_DM_EN_CRC_00_1_CRC_11_0_ROffest_1_tCH_50_BL16_4b8g_BfM_7600_SS_CSGD.x8.SS0.94V-40C.X8`
3. `Fail      primesim.CRC001_Dualbank_act_wr_rd_err_RPre_4_RPst_1P5_WPre_3_WPst_1P5_DM_EN_CRC_00_1_CRC_11_0_ROffest_1_tCH_50_BL16_4b8g_BfM_7600_SS_CSGD.x8.SS0.94V110C.X8`
4. `Fail      primesim.CRC002_Dualbank_low_up_nibble_crc_err_RPre_3_RPst_0P5_WPre_2_WPst_0P5_DM_EN_CRC_00_1_tCH_50_BC8_OTF_4b8g_BJb_2666_TT_CSGD.x8.TT0.94V25C.X8`
5. `Fail      primesim.CRC002_Dualbank_low_up_nibble_crc_err_RPre_3_RPst_1P5_WPre_2_WPst_1P5_DM_EN_CRC_11_1_tCH_50_BC8_OTF_4b4g_B7c_8800_FF_CSGD.x16.FF1.3V-40C.X16`

### 唯一转换示例（verbatim from U#12）
- 输入：`Fail      primesim.CRC001_Dualbank_act_wr_rd_err_RPre_4_RPst_1P5_WPre_3_WPst_1P5_DM_EN_CRC_00_1_CRC_11_0_ROffest_1_tCH_50_BL16_4b8g_BfM_7600_SS_CSGD.x8.SS0.94V-40C.X8`
- 输出：`/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD/CRC001_Dualbank_act_wr_rd_err_RPre_4_RPst_1P5_WPre_3_WPst_1P5_DM_EN_CRC_00_1_CRC_11_0_ROffest_1_tCH_50_BL16_4b8g_BfM_7600_SS_CSGD.x8.SS0.94V-40C X8`

### 转换规则推导（从唯一示例 + 5 行输入结构）
1. 行首 `Fail` + 若干空格 + `primesim.` 是有效行（Pass/空行/其它忽略）
2. 取 `primesim.` 后到行尾（去尾空白）= `<TestName>.<xN>.<Corner>.<XN>`
   - TestName 无点号（如 `CRC001_Dualbank_..._TT_CSGD`，仅下划线+字母数字）
   - xN = `x4`/`x8`/`x16`
   - Corner 含点号（如 `TT0.94V25C`, `SS0.94V-40C`, `FF1.3V-40C`）
   - XN = `X4`/`X8`/`X16`（与 xN 对应大写）
3. 把**最后一个点号**替换成空格 = `rsplit('.', 1)` 后 `' '.join` → `<TestName>.<xN>.<Corner> <XN>`
4. 前置固定基路径 `/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD/`
5. 输出序 = 输入 Fail 行序

### trace 助手行为
助手（deepseek-v4-flash）在 msg 13 给出需求分析 + 1 个 ask_question（问输出基路径是固定/参数/推导）后**会话结束**（用户未回复）。即 trace 内助手未真正交付脚本，但**用户意图清晰、evidence 完整**（5 真实 Fail 行 + 1 真实转换示例 verbatim 在 trace 内），可基于真实意图合成参考解 + check。

### 可造性判定
- ✅ 真实 trace 源可溯（ai203, yuankong, hfhds201, mc=5, session_file 全路径）
- ✅ 用户意图清晰（produce-task: bmatrix Fail 行 → sim.save_rerun 格式转换）
- ✅ evidence anchor 充分（5 行真实输入 + 1 行真实 input→output 示例，全 verbatim from trace）
- ✅ 可写"有牙" check()（B 隐藏变体 + 真跑候选 + ≥8 独立断言 + 3-seed 随机子集 + 反硬编守门 + §4.9 三假全 FAIL）
- domain 判定：keywords drc:65 dominant 但用户实际任务=SPICE sim regression rerun 脚本（primesim=PrimeSim SPICE 仿真器, bmatrix=matrix run 失败用例收集, sim.save_rerun=重跑清单），归 `eda_other`（utility script for sim flow，同 SpfCouplingSort-001 / VerilogDriveFsmBlockGen-001 类目）
- 档位：**C-A produce-task**（任务说明用用户 U#12 原话 verbatim，附件用 trace 内 5 真实行；参考解自写，因 trace 内助手未完成交付）

## 三、合成计划（BmatrixFailConvert-001）

- case_id: `EDA-Eval-DesignFlow-BmatrixFailConvert-001`
- A 档可见资产 (`assets/`): `bmatrix_sample.txt`（5 行真实 Fail, verbatim）+ `conversion_example.txt`（1 行 input→output, verbatim）+ `prompt.txt`/`task_brief.md`/`prompt.md`
- B 隐藏变体 (`reference/hidden/`): `bmatrix_sample_B.txt` 10 行 = 7 Fail + 3 Pass, ≥5 维全异（CRC003/004/005 vs 001/002；precharge_trailing/MPR_readback/Write_leveling vs act_wr_rd/low_up_nibble；corners TT0.94V85C/SS0.88V-40C/FF1.2V25C/SS0.94V-40C/FF1.3V110C/FF1.3V-40C/SS0.88V110C/TT1.1V85C vs A；x4/x8/x16 不同分布；含 Pass 行；行数 10 vs 5；BL4/BC4/BL32/BC8 vs A；Bqz/Bmn/Bvk vs BbK/BfM/BJb/B7c）
- 参考解 (`reference/bmatrix_fail_convert.py`): argparse 输入文件 (默认 `bmatrix_output.txt`), `LINE_RE = ^Fail\s+primesim\.(\S+)\s*$`, `rsplit('.',1)` 替换最后点为空格, 前置 BASE_PATH, 写 `sim.save_rerun`
- check.py: 15 条独立断言 (a-o), 含 §4.9 三假 FAIL + 3-seed 随机子集 + 反硬编 B-vs-A ≥5 维守门
- negatives: 4 个 (neg_empty_shell / neg_print_expected_B / neg_no_primesim_strip / neg_no_last_dot_replace) + negative_selftest.py
- metadata: domain=eda_other / track=A-faithful produce-task / level=L1 / k_check=k_rationale=15 / trace_source yuankong@hfhds201/1792395143753_ai203/mc=5
