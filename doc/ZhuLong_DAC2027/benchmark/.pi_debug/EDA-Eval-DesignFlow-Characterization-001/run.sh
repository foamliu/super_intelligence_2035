#!/bin/bash
# pi-SUT debug run for EDA-Eval-DesignFlow-Characterization-001
# design_flow deliverable case: patch buggy SiliconSmart config files -> outputs/submit.zip
# check is all-local Python (no .75 sandbox needed for this static config-debug task).
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/.pi_debug/EDA-Eval-DesignFlow-Characterization-001
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0

PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- 你的当前工作目录就是任务工作区。所有附件（5 个 drgqx_cmos_*.tcl + stdcells_ac.tcl
  + configure.tcl + 5 个 *.inst + errors.txt）已经在当前目录里，直接读取即可。
- 按 prompt 诊断并修复每一类 error，把修复后的文件写回当前目录（同名覆盖）。
- 然后把以下 12 个修复后的文件打包成 outputs/submit.zip（zip 根目录，扁平文件名，
  不要加子目录）：
    drgqx_cmos_analog.tcl drgqx_cmos_digital.tcl drgqx_cmos_io.tcl
    drgqx_cmos_stdcells.tcl stdcells_ac.tcl configure.tcl
    ffrqIOLVx2_pc60_odt.inst nor3IOLVIOx1_DQS.inst invYx2_CoM.inst
    IO_TX_LOCAL_DCA_DQS.inst T_CompXor.inst fix_summary.md
- fix_summary.md 要逐条列出每个 error -> 根因 -> 修复，覆盖全部问题类别
  (qualify_library / model verilog->timing / add_latch / forbidden_state xor /
   netlist 名漂移 / default_input_state + </||  / vssFoot 重复 / vwlp pintype)。
- 这是一个纯静态配置修复任务，不需要调用 EDA 工具或 eda_flow MCP 沙盒。
  判分只校验 outputs/submit.zip 内的脚本与配置产物（本地 Python 校验器）。
- 你可以自行用本地 python3 跑 _check.py 自检（它定义了 check(deliverable, workdir)）：
    python3 -c \"import sys; sys.path.insert(0,'.'); import _check; print('PASS' if _check.check('outputs/submit.zip','.') is True else 'FAIL')\"
  如果自检不通过就继续修复，直到通过。
- 全部完成后，在最终回复里打印一行 'DESIGN_FLOW_VERDICT=PASS' (或 FAIL)。

注意 Tcl 注释陷阱：'#' 只有在行首（可前导空白）才是注释；行尾 '...  # disabled'
不是注释，命令仍会执行。qualify_library / set_config_opt qualification_lc_shell
必须用行首 '#' 注释掉。"

echo "=== pi-SUT Characterization-001 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== outputs/submit.zip ==="
ls -la outputs/submit.zip 2>&1
echo "=== tail pi_run.log ==="
tail -25 pi_run.log
echo "=== local check ==="
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
python3 -c "import sys; sys.path.insert(0,'.'); import _check; 
try:
    r=_check.check('outputs/submit.zip','.'); print('CHECK_RESULT:', 'PASS' if r is True else r)
except Exception as e: print('CHECK_RESULT: FAIL ->', type(e).__name__, str(e)[:200])" 2>&1
