# Trace 深读 · yuankong 1793611022749_w9aze @ hfhds201 · NoStimulusVecDiag-001

**trace**: `/home/yuankong/.cline/data/sessions/1793611022749_w9aze/1793611022749_w9aze.messages.json`
**size**: 457,631 B / 71 msgs / spice_count=1227 · mc=1227 · domain=spice_sim · track=faithful

## 用户意图（USER#0 原话逐字，A-档任务说明）
```
/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage/log/Vec_Dynatrim/vecgen.rpt/run_extract_stmi_ky这个脚本运行没有产生激烈帮我分析下原因,/rundata/drcpa_sim/V0/simdir/finesim/Finesim_stimulus/verilog.ddr5.drcpa.Coverage_test/run_extract_stmi_ky这个脚本产生了激励可以参考下
```
- 纯目标轮：给两个 run_extract_stmi_ky 路径（failing=Coverage 侧未产生激励 / working=Coverage_test 侧产生了激励可参考）+ "分析下原因"。
- 🚫 未给根因、未给修复方案 → 符合 A-档选轮规则。
- USER#1–3 是 USER#0 的重复（4 次重发，session 启动重试）。
- USER#54 是后续澄清轮（"编译有错误 ncverilog.log 中为什么没有任何打印信息，之前都有的"），按 A-档规则不入任务说明，可作 hint。

## assistant 工具链（关键步骤）
1. `read_files` 试图读两个路径 → 失败侧 ENOTDIR（`vecgen.rpt` 不是目录）。
2. `list_allowed_files` 探测两侧目录结构 → 发现 `vecgen.rpt` 是**报告文件**，不是目录；真实脚本在 `.../Coverage/run_extract_stmi_ky`。
3. `read_files` 读两侧 `run_extract_stmi_ky` → failing 用 personal vecgen (`/rundata/drgqa/.../yuankong/personal_file_ky/script/vecgen`)，working 用 `/apps/cad/bin/vecgen`。
4. `read_files` 读 `vecgen.rpt`（报告）→ `Dynatrim040_..._9600_TT.x16 **ERROR**` 重复 11 次；`vec_fail.cfg` 记失败 pattern。
5. `read_files` 读 `xmverilog.log` → `*E,NOTSTT` (expecting a statement) + `*E,EXPENM` (expecting 'endmodule')，`errors: 90`，status 1。
6. `read_files` 读 pattern 源文件 `Dynatrim040_Multi4bank_tCCDM.v` → 发现 `parameter MA_cm1_cl_WrColPlsGen = 9'o504;` 等声明在 `task do_dynatrim; begin ... end endtask` **过程体内**（line 10 起），SystemVerilog 禁止 → 真正根因。
7. `list_allowed_files` 对照两侧 pattern 目录 → working 侧含 `stimulus.vec`/`stimulus.list`/`vec.text`/`vec_probe.text`/`trantime.sim`/`A_Compare.rpt`/`A_Summary.rpt`/`ncsim.shm`；failing 侧全无（只有生成的 `.v`/`.run`/`xmverilog.log`/`ncverilog.log`）。
8. `editor`+`run_approved_command` 写 `/home/yuankong/diag_ky.sh` 辅助 grep（确认 `cm1_cl_WrColPlsGen` 只此一个 pattern 用，是新加的）。
9. `read_files` 对比 working pattern `Allbank001_WrWrpRda.v`（parameter 在 module 体内合法声明）→ 给修复建议。
10. msg 53 给出完整结论（中文）；USER#54 追问 ncverilog.log 为何没打印 → msg 70 答：编译错误这次写到 `xmverilog.log`（真实工具日志），`ncverilog.log` 被工具换成只写 "Job ... is done" 行。

## 金标准（用户实际接受的结果，msg 53 + msg 70）
1. **路径错误（次要）**：`vecgen.rpt` 是报告文件不是目录，`.../vecgen.rpt/run_extract_stmi_ky` 不存在（ENOTDIR）；真实脚本在 `.../Coverage/run_extract_stmi_ky`。
2. **真正根因（critical）**：失败 pattern `Dynatrim040_Multi4bank_tCCDM.v` 在 `task ... begin ... end` 过程体内声明 `parameter` 常量（`MA_cm1_cl_WrColPlsGen` 等），SystemVerilog 禁止 → `xmverilog` 编译失败（`*E,NOTSTT`、`*E,EXPENM`、90 errors、status 1）→ `vecgen` 标记 pattern `**ERROR**` → 无激励产出。
3. **激励对照（symptom）**：working 侧 pattern 目录含 `stimulus.vec`/`stimulus.list`/`vec.text`/`vec_probe.text`/`trantime.sim`/`A_Compare.rpt`/`A_Summary.rpt`/`ncsim.shm`；failing 侧全无。
4. **vecgen 二进制（次要）**：failing=personal 路径，working=`/apps/cad/bin`；实为同一脚本 `cxmt_genStimuVec.pl`（路径拷贝），差异不在二进制而在 pattern 文件。
5. **log 命名（USER#54 答）**：编译错误写到 `xmverilog.log`；`ncverilog.log` 只有 `Job ... is done` 行。

## case 合成（NoStimulusVecDiag-001，spice_sim A-faithful L1）
- **交付**：`gen_no_stim_diag.py <failing_run_dir> <working_run_dir> <outdir>` → `root_cause_report.json` + `root_cause_report.md`。
- **资产**（按真实结构合成，A=DDR5/Dynatrim，hidden B=LPDDR5/ZQCal，结构与判据与真实一致）：
  - `failing_A/`：`run_extract_stmi_ky`(personal vecgen) + `log/Vec_Dynatrim/vecgen.rpt`(报告文件, 11 ERROR 行) + `vec_fail.cfg` + `<pattern_dir>/`(pattern .v 在 task body 内声明 parameter → NOTSTT/EXPENM, 90 errors, status 1; `xmverilog.log` + `ncverilog.log` 只有 Job done; 无 stimulus.*)
  - `working_A/`：`run_extract_stmi_ky`(/apps/cad/bin/vecgen) + `log/Vec_CRC/<pattern_dir>/`(valid .v, clean xmverilog.log, 含 stimulus.vec/.list/vec.text/vec_probe.text/trantime.sim/A_Compare.rpt/A_Summary.rpt/ncsim.shm)
  - `hidden/failing_B` + `hidden/working_B`：LPDDR5 命名，不同 SV 错误码（NOISBN/SYNTX）、不同 error count（55）、不同 vecgen.rpt ERROR 行数（7）、不同 stimulus 值/cycle 数；结构与 A 一致。
- **check.py**：12 条独立断言（a–l），见 reference/NoStimulusVecDiag-001/check.py 头注释。k_check=12 == k_rationale=12 ≥ 8 ✓。
- **自验**：ref PASS(12/12) ✓ · 3 negatives（fake_empty/fake_core_deleted/fake_print_expected）全 FAIL（f/i/k 不同条失败）✓ · §4.9 三假（空壳/print-expected/core-deleted）全 FAIL（c/k/i 不同条失败）✓。
- **negative_selftest.py** PASS ✓。
- **ledger**：9kzwd... → mark case（148 covered / 1511 target = 9.8%）。

## 与现有 case 的区别
- 不与 CovMissBinExtract-001(ericw) 重叠：本 case 是**诊断 vecgen 未产生激励的根因**（路径错误 + SV 语法 + 激励对照），CovMissBinExtract 是**解析覆盖率结果抽取未命中 bin**。
- 不与 DcLogErrDiagnose / IrunSimDiagnose 等 Diag case 重叠：那些是 innovus/irun 日志诊断，本 case 是 finesim vecgen 激励抽取链路的诊断（spice_sim shard B 专属）。
