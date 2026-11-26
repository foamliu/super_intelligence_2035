#!/bin/bash
# pi-SUT debug run for EDA-Eval-DesignFlow-PDKQA-001
# design_flow deliverable case: build DRC test-env (Calibre VCO bypass) -> outputs/submit.zip
# check is all-local Python (no .75 sandbox needed; the env bug is static-analysed).
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/.pi_debug/EDA-Eval-DesignFlow-PDKQA-001
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
export PI_OFFLINE=0

PROMPT="$(cat prompt.txt)

INSTRUCTIONS FOR YOU (the agent under test):
- 你的当前工作目录就是任务工作区。所有附件（DrcQa.py / calibre_env_excerpt.sh /
  env_symptoms.txt / known_issues.md / tests_skeleton/）已经在当前目录里，直接读取即可。
- 先读 calibre_env_excerpt.sh 与 env_symptoms.txt 定位 Calibre VCO 根因，再按 prompt
  产出三份交付件并打包成 outputs/submit.zip（zip 根目录，扁平文件名，不要加子目录）：
    test_env.py  smoke_report.md  PHASE2_REPORT.md
- test_env.py 要点：
  (1) 把 /apps/local/python/python-3.7.1/x86_64/lib 加到 LD_LIBRARY_PATH（修 libpython3.7m）；
  (2) Calibre VCO 绕过：在 /tmp/calibre_fake_home 建假 MGC_HOME，其 bin/calibre_vco 桩脚本
      返回 'aoi'，再建桩 /tmp/libXss.so.1，LD_LIBRARY_PATH 指向真实 aoi lib；
  (3) 绕过桩要在模块导入时自动重建：检查 /tmp/calibre_fake_home 与 /tmp/libXss.so.1 是否
      存在，缺失则重建，并在模块末尾模块级调用一次 setup 函数；
  (4) 提供 check_calibre_env()->(ok,msg)、get_real_path、chdir_to_data_dir、print_result。
  注意：只设 CALIBRE_HOME 是无效的（calibre_env 无条件运行 calibre_vco），必须用假 MGC_HOME 绕过。
- smoke_report.md：列出全部 17 个 supportFuncnames 的冒烟结果。11 个 text checker 记 PASS，
  drcSyntax 记 PASS，其余 5 个 pattern QA checker 记 CAN_START（不要记 PASS/SKIP/FAIL）。
  17 个 checker 名字必须与 DrcQa.py 的 SUPPORT_FUNCNAMES 完全一致。
- PHASE2_REPORT.md：定位 calibre_env 里 \$SW_WKSTN_ / \$MGC_VCO_ 带下划线的 shell 变量名解析
  bug；明确记录\"只设 CALIBRE_HOME 的正规方案已尝试且无效\"；记录恢复的假 MGC_HOME + 桩 libXss 绕过。
- 这是纯静态环境建立任务，不需要调用真实 Calibre 或 eda_flow MCP 沙盒。
  判分只校验 outputs/submit.zip 内的三份文件（本地 Python 校验器）。
- 你可以自行用本地 python3 跑 _check.py 自检（它定义了 check(deliverable, workdir)）：
    python3 -c \"import sys; sys.path.insert(0,'.'); import _check; print('PASS' if _check.check('outputs/submit.zip','.') is True else 'FAIL')\"
  如果自检不通过就继续修复，直到通过。
- 全部完成后，在最终回复里打印一行 'DESIGN_FLOW_VERDICT=PASS' (或 FAIL)。"

echo "=== pi-SUT PDKQA-001 start $(date '+%Y-%m-%d %H:%M:%S') ==="
timeout 1700 pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "$PROMPT" > pi_run.log 2>&1
ec=$?
echo "=== pi exit=$ec end $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== outputs/submit.zip ==="
ls -la outputs/submit.zip 2>&1
echo "=== tail pi_run.log ==="
tail -30 pi_run.log
echo "=== local check ==="
export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH
python3 -c "import sys; sys.path.insert(0,'.'); import _check;
try:
    r=_check.check('outputs/submit.zip','.'); print('CHECK_RESULT:', 'PASS' if r is True else r)
except Exception as e: print('CHECK_RESULT: FAIL ->', type(e).__name__, str(e)[:300])" 2>&1
