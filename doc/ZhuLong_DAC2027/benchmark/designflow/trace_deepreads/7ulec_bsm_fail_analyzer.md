# Deepread: 7ulec — Bisection SM Simulation Failure Analyzer

## Trace
- sid: 1794534243942_7ulec
- user: zoeyr @ hfeg0pkn001
- mc: 25 (netlist:77, hspice:4, spice:4)
- nmsg: 86
- domain: schematic_netlist

## Real Task Summary
zoeyr 在 hfeg0pkn001 上用 cline 分析 SRAM Sense Margin (SM) 二分法仿真失败原因。
用户通过二分法 (bisection) 搜索使 SA 输出达到目标 Goal 电压的临界偏置 VTarget，
当 pvblh=0.7V 时仿真失败（.log 中 "FAIL: can't continue bisection, both lower and upper boundary fail"）。
cline 读取 .log (PrimeSim U-2023.03-SP1) 和 .mt0 文件，发现：
- 下边界 VTarget=0.0 → maxvout=0.69918 < Goal=0.7 → fail
- 上边界 VTarget=1.0 → maxvout=0.00281 → fail
- 两者都 fail → 二分法无法启动
cline 随后编写 analyze_bisection_failure.py 脚本自动解析 .mt0/.log 并生成失败分析报告。

## 关键技术点
1. PrimeSim bisection .log 格式：
   - `bisec-opt lower boundary, vtarget = ..., status: success/fail`
   - `bisec-opt upper boundary, vtarget = ..., status: success/fail`
   - `bisec-opt iter = N, vtarget = ..., status: success/fail`
   - `FAIL: can't continue bisection, both lower and upper boundary fail`
2. .mt0 格式：`$DATA1 SOURCE='PrimeSim SPICE'`，列为 vtarget/maxvout/temper/alter#
3. 失败案例 .mt0 只有 2 行（仅上下边界，无迭代）
4. 成功案例 .mt0 有 12+ 行（边界 + 迭代），bisection 收敛

## 合成方案 (B档)
- 任务：编写 bsm_analyzer.py 通用脚本，解析 .log + .mt0，判定 failure_mode，输出 JSON 报告
- 资产 A：失败案例 .log + .mt0（sanitized from real trace）
- 隐藏 B：不同失败案例（maxvout=0.51234, temp=125）
- 隐藏 C：成功案例（lower pass, 10 iterations, temp=-40）
- check.py：16 条条件 a-p
- 3 fake submissions: hardcoded / no-log-parse / always-fail
