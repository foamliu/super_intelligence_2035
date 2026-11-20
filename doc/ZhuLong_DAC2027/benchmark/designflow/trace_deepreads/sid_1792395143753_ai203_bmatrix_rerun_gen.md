# trace_deepread — sid 1792395143753_ai203 (yuankong @ hfhds201) — bmatrix rerun 生成

## meta
- session_file: `1792395143753_ai203.messages.json`
- user: yuankong / host: hfhds201 / msgs: 14 / size: 45801 / mtime: 2026-11-07 ~07:3x
- tools: list_allowed_files=4, get_agent_policy_status=1, read_files=1, ask_question=1
- shard B domain: spice_sim (finesim drcpa batch sim 作业 rerun)
- 选料路径: hfhds201 本机 281 cline session diff ledger B(335 anchor)→ unscouted top~40 by mtime(size>8KB)→ 本轮 scout 17 候选(wn9jo/w9aze/9kzwd/ziy0b/p33gv/9txq4/wg5u2/reo1p/mrmfn/y91i6/zlqaz/fg7ey/03efi/bg39v/3qfwd + ai203)→ 多为 digital(coverage/vecgen/PDK/vsim)或 consulting 或 dup(wg5u2=LibCellListGen-001 同 drvqa Library/Cell 解析)→ **ai203 CLEAN A-档✓**

## 对话流（user 轮逐字）
- USER#0: 「可以帮我写个脚本吗」(开场)
- USER#10: 「写个python的」(指定语言)
- USER#12 (关键 A-档 feature 轮, 逐字原文):
  「帮我写个脚本，我可以在某个路径下，例如/proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_csgd，执行bmatrix -f，会得到下面的文本
  Fail      primesim.CRC001_Dualbank_act_wr_rd_err_RPre_2A_RPst_1P5_WPre_3_WPst_0P5_CRC_01_0_tCH_50_BL32_OTF_4b8g_BbK_9600_TT_CSGD.x4.TT0.94V25C.X4
  Fail      primesim.CRC001_..._SS_CSGD.x8.SS0.94V-40C.X8
  Fail      primesim.CRC001_..._SS_CSGD.x8.SS0.94V110C.X8
  Fail      primesim.CRC002_..._TT_CSGD.x8.TT0.94V25C.X8
  Fail      primesim.CRC002_..._FF_CSGD.x16.FF1.3V-40C.X16 ，将其转换成另一种格式，生成文件sim.save_rerun,格式转换示例，例如把
  Fail      primesim.CRC001_..._SS_CSGD.x8.SS0.94V-40C.X8 转换成，
  /rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD/CRC001_..._SS_CSGD.x8.SS0.94V-40C X8这样的格式」
  → **CLEAN A-档✓**: 纯需求轮, 给目标(写脚本)+输入格式(bmatrix -f Fail 行)+转换示例(全 input→output)+输出文件名(sim.save_rerun), 未给根因/修复。

## A-档选轮判定
- USER#12 是「提出需求/表达目标」轮 ✓; 不含根因诊断、不含修复方案 ✓。
- USER#0/#10 仅是开场澄清(写个脚本/python), 非需求主体。

## assistant 响应
- msg[1]: 询问脚本类型/功能/环境/输入输出 + list_allowed_files + get_agent_policy_status
- msg[4]: 探索 /home/yuankong 下 cross_probe_*/inst_rename_results + read find_file.sh/search_param.py/old/find_ddr5.*
- msg[9]: 再次询问用途/语言/输入输出
- msg[13]: 理解需求后 **ask_question** 问「输出基路径(output prefix)是怎么确定的?固定/参数/推导/留默认?」, 给 4 选项(含固定路径 `/rundata/.../Vec_CSGD/`)
- **trace 末轮 = ask_question, 用户未答, 未产出最终脚本** → trace 不完整, 但 USER#12 转换示例自含完整 spec(基路径在示例中给出 = `/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD/`)。

## 转换规则（从 USER#12 示例反推, 唯一确定）
- 输入行: `Fail<spaces>primesim.<job>`  (job 形如 `CRC001_..._CSGD.x8.SS0.94V-40C.X8`)
- 1) 去掉 `Fail` 关键字 + `primesim.` 前缀 → `<job>`
- 2) `<job>` 最后一个 `.` 换成空格 → `<body> <suffix>` (suffix = 末尾 Xn token, 如 X8/X4/X16/X2)
- 3) 前拼 BASE 路径 → `<BASE>/<body> <suffix>`
- BASE = `/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD`
- 非 Fail 行(Pass/空行/Other)跳过(用户示例只给 Fail 行, sim.save_rerun 是 rerun 文件, 只列需重跑的 Fail case)
- 输出文件: `sim.save_rerun`

## 验证示例（USER#12 给的）
- in : `Fail      primesim.CRC001_..._SS_CSGD.x8.SS0.94V-40C.X8`
- out: `/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_CSGD/CRC001_..._SS_CSGD.x8.SS0.94V-40C X8`
- 校验: job=`CRC001_..._SS_CSGD.x8.SS0.94V-40C.X8` → rsplit('.',1)=`['CRC001_..._SS_CSGD.x8.SS0.94V-40C','X8']` → BASE+'/'+'CRC001_..._SS_CSGD.x8.SS0.94V-40C'+' '+'X8' ✓

## case 合成（EDA-Eval-DesignFlow-BmatrixRerunGen-001, spice_sim A-faithful L1）
- 交付=通用 `bmatrix_rerun_gen.py <bmatrix_output_file> [output_file]` (便携 L1 Python, 只做文本转换; "执行 bmatrix -f" 部分环境 specific 不做, 输入为其输出文本)
- A (SUT 可见, testdir_A/bmatrix_output_A.txt): 6 Fail(CRC001×2/CRC002×2/CRC005×2, X4/X8/X16, TT/SS/FF 角点) + 2 Pass → 6 输出行
- hidden B (check 跑, hidden/testdir_B/bmatrix_output_B.txt): 5 Fail(CRC003×1/CRC004×2/CRC006×1/CRC007×1, X2/X8/X16/X4, 含 X2 新后缀) + 3 Pass + 1 空行 + 1 Other → 5 输出行; A≠B✓
- reference=bmatrix_rerun_gen_ref.py + check.py k=12 断言 a-l + negative/(5 stub: empty/print_only/hardcode_A/include_pass/no_dot_transform)
- 自验: REF PASS 12/12 + 5 neg 全 FAIL + §4.9 (a)empty shell (b)print only (c)core-cut 全 FAIL = SELFTEST PASS
- 断言闸门: k_rationale=12 == k_check=12 ≥ 8 ✓

## 收尾
- 落库: B jsonl 125→126, ledger ai203 mark case (covered 128→129, spice_sim 97→98)
- WAITING:0, DEBT:0
