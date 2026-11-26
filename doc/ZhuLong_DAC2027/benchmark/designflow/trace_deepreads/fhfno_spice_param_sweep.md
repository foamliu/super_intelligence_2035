# 深读笔记: 1794488236128_fhfno (vincentz / 10.129.2.13)

**日期**: 2026-11-13 r478
**session**: 1794488236128_fhfno.messages.json (1.05MB, 79 msgs)
**用户**: vincentz
**主机**: 10.129.2.13 (hfhds222 类)
**match_count**: 1456 (hspice:1456, netlist:157, schematic:39)
**domain**: spice_sim
**agent**: lead (cline)

## 用户意图

vincentz 要求以 `mixbest_V1_RBL_95_no_probe_I.sp` 为基础模板，生成参数化 HSpice 仿真 deck 扫描：
- 9 个变量：Sanadj1-4, Sapadj1-4, R_BL
- 约束：Sanadjx 必须等于 Sapadjx，值只能 0 或 1
- R_BL 取 15 个值：0,5,15,25,35,45,55,65,75,85,95,105,115,125,135
- 总计 16 文件夹 × 15 R_BL 值 = 240 个 .sp 文件
- 后续要求生成 runsim_RBL_NxPx 脚本用 bsub+primesim 批量提交

## Agent 工具链

1. list_allowed_files (多次) — 探索 /home/vincentz, /home/vincentz/H-spice 等目录
2. read_file — 读取模板 .sp 文件 `/rundata/.../mixbest_V1_RBL_95_no_probe_I.sp`
3. read_file — 读取已有 runsim 脚本
4. editor/create — 创建 generate_sp_files.py
5. python-runner — 执行 generate_sp_files.py 生成 240 .sp 文件
6. read_file — 验证生成的 .sp 文件
7. editor/create — 创建 gen_runsim.py
8. python-runner — 执行 gen_runsim.py 生成 runsim_RBL_NxPx

## 关键产物

- **模板 .sp**: 含 .param Sanadj1-4/Sapadj1-4/R_BL + .inc finesimconfig + .inc netlist + .tran + .measure
- **generate_sp_files.py**: Python 脚本，读模板 → 按 16×15 组合替换 .param → 写入 NxPx_RBL/ 文件夹
- **gen_runsim.py**: 生成 runsim_RBL_NxPx bash 脚本，每行 `bsub -q fqueue3 primesim -i {sp} -o {sp}.out`
- **240 .sp 文件**: 16 个文件夹（N0P0_RBL ~ N1P1_RBL），每文件夹 15 个 .sp

## Case 化决策

- **case_id**: EDA-Eval-DesignFlow-SpiceParamSweepGen-001
- **A 档 trace-faithful**: 是（用 vincentz 原始需求作 prompt）
- **Input A**: template.sp (简化模板) + spec.json (15 R_BL 值)
- **Hidden B**: template_B.sp (不同 netlist include) + spec_B.json (8 R_BL 值 [10,20,...,80])
- **check.py**: 10 断言，subprocess 真跑 sweep_generator.py 在 hidden B 上
- **L2**: subprocess 执行候选脚本 + 输出结构断言
