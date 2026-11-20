# Deepread: l36g5 — wei9liu AMS sim config viewlist diagnostic

**Session**: 1793002657891_l36g5  
**User**: wei9liu @ hfeg0plg75  
**match_count**: 168 (spice_sim)  
**Trace file**: .75 → ssh hfeg0plg75 → /home/wei9liu/.cline/data/sessions/1793002657891_l36g5/1793002657891_l36g5.messages.json (647KB, 89 msgs, ~30 user turns)  
**Date**: 2026-10-26  

## 用户真实意图

1. **U#0**: "我在用ADE跑AMS的仿真，路径如下/proj/lacaa/TV1_FS_Virtuoso/workdir/wei9liu/TV1_PSENSOR_FS_SIM/PSENSOR_AMS_SIM/maestro，你帮我跑一下" — 要求助手直接跑 AMS 仿真
2. **U#46**: "本会话里核对这个 test 的设置(tran 起止时间、观测信号、corner/profile 等)有没有问题" — 改问核对 test 设置

## 助手诊断链

### 阶段 1: 探索环境 + 发现写权限阻塞
- `list_allowed_files` 探索 maestro 目录结构
- `read_files` 读 master.tag, active.state → 确认 design=TV1_PSENSOR_FS_SIM.PSENSOR_AMS_SIM, config_V1, AMS
- `get_agent_policy_status` → 写权限仅限 /home/wei9liu, 仿真目录 /proj/lacaa 只读
- `run_approved_command` 固定 120s 超时, 不够跑 AMS 瞬态
- 发现 .cdslck 锁文件 → PID 3119021 (virtuoso@hfechds018) 正在占用

### 阶段 2: 核对 test 设置 (用户第二个请求)
- 深读 active.state (3135 行):
  - tran stop=500µs, enable=true
  - corner=Nominal, temp=27
  - variables: FOSC=145M, FREF=25M, VDD=0.75
  - netlisterMode=AMS-UNL
  - connectRules=ConnRules_18V_full_fast (connectLib)
  - outputs: /RST_N, /net4 valid; /w_process<2:0>, /LATCH, /I_CLK_control_37/QD<5> invalid
  - defaultVsupForVAR=1.8

### 阶段 3: 发现真正根因 — elaboration 失败
- 读 results/maestro/Interactive.41.log → 0 errors, ~30s, 但太短不像完整 500µs AMS
- 读实际仿真目录 /rundata/.../Interactive.41/1/.../psf/xrun.log → **发现核心错误**:
  - `amsspice: *Error: (.../osc_cnt/functional/verilog.v,2): Cannot run the simulation because syntax error 'Unexpected end of line'`
  - `amsspice: *Error: (.../top_psensor/functional/verilog.v,2): ...`
  - `xrun: *E,AMSCOMM: AMSD control block failed to write spice primitives to amscomm.list`
  - `spectre exited before elaboration`
  - core dump: core.158749
- **关键发现**: amsspice (SPICE 解析器) 在解析 Verilog .v 文件 → 语法错误

### 阶段 4: 对比健康运行 + 找到 viewlist 回归
- 读 Interactive.11 (2026-08-18) xrun.log → **正常**:
  - `xmvlog: module PSENSOR_AMS:functional -> errors: 0` (数字编译器处理 .v)
  - 121 modules, 36 unique, 236 always blocks, 完成
- 对比 config_V1 vs config 的 expand.cfg:
  - **config_V1** viewlist: spectre, spice, pspice, verilog, verilogams, behavioral, **functional**, systemVerilog, schematic, veriloga, vhdl, vhdlams, wreal
  - **config** (旧) viewlist: spectre, cmos_sch, cmos.sch, schematic, verilog, veriloga, ahdl, pspice, dspf (无 functional)
- **根因**: config_V1 viewlist 新增 functional → AMS-UNL netlister 把 functional/verilog.v 路由到 amsspice (analog) 而非 xmvlog (digital) → SPICE 解析器无法解析 Verilog HDL → 语法错误 → elaboration 失败

## 可操作化要素

| 要素 | 提取 |
|---|---|
| 设计 | TV1_PSENSOR_FS_SIM.PSENSOR_AMS_SIM, config_V1, AMS |
| tran stop | 500µs |
| corner | Nominal |
| variables | FOSC=145M, FREF=25M, VDD=0.75 |
| connect rules | ConnRules_18V_full_fast |
| 失败解析器 | amsspice |
| 错误类型 | syntax_error on .v files |
| 根因类别 | viewlist_mismatch (functional in viewlist) |
| 健康运行 | Interactive.11 (2026-08-18, xmvlog) |
| 回归指示 | core dump + amsspice syntax error |
| 修复 | 从 config_V1 viewlist 移除 functional，或显式映射到 digital 路径 |

## 造题形态

**B 档 synthesized** — A 档不可行: 真实文件在内部 /proj 路径, 含私有 PDK/库, 不可离线沙盒交付。
合成 mock fixtures (active.state INI 格式 + xrun.log + expand.cfg + healthy_xrun.log + verilog samples) 复刻关键结构。
任务 = 写 diagnose_ams_config.py 解析 fixture 产出诊断报告 JSON。
hidden B = 不同根因 (connect rules 电压不匹配, ConnRules_33V_slow on 1.8V design) cross-input guard。
