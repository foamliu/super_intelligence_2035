# trace deepread — 1793775649853_zns2p · shanmei @ hfeg0plg53 · SimProgressCheck-001

## trace 元信息
- session: 1793775649853_zns2p.messages.json (388KB, 45 msgs, 2 user turns)
- user: shanmei, host: hfeg0plg53 (plg 独立子网 10.129.35.69)
- spice match_count: 2853 (hspice markers)
- 来源: 11-05 重扫令 plg 独立子网首扫（06:1x 轮发现 856 新候选）→ 08:1x 轮 scp top 4 候选到 .75 + 本地 peek → zns2p CLEAN

## 用户轮（A-faithful 选轮）
- **U#0 (msg#0) 真实目标逐字**：「我的目录下有一个tb_OTA_stb_farcap的子目录，请在下面corner_stb文件夹中执行check_sim指令，查看仿真完成进度，执行前先执行soure ~/.bashrc指令，保证已经加载自定义的函数」
  - 提出需求（执行 check_sim 查看进度）+ 操作约束（先 source bashrc）→ **无根因/无修复方案 → A-faithful ✓**
  - 注：原文 "soure" 为用户笔误（应为 source），按红线 #2 不脱敏不改写，逐字保留
- U#1 (msg#13)：「我描述的我的目录指的是 /proj/lagat/V0/workdir/shanmei/，我启动软件的目录」
  - 补充路径说明（澄清，非根因/修复）

## assistant 工具链
1. list_allowed_files 探索目录 → 找到 tb_OTA_stb_farcap 在 /proj/lagat/V0/workdir/shanmei/tb_template_shanmei/ 下
2. corner_stb 仿真目录在 /rundata/lagat/V0/simdir/finesim/workdir/shanmei/simulation/tb_OTA_stb_farcap/hspiceD/schematic/hspice/corner_stb/
3. 尝试运行原 Perl check_sim（cxmt_check_sim）→ 失败：Spreadsheet::ParseXLSX 模块缺失
4. 改写 Python 等价 run_checksim.py：
   - glob *.sp 计总作业数
   - glob result/*.lis，读内容按 "total elapsed time" 判 finished
   - 无 .lis 或 .lis 无标记 → running
   - 输出 "Finished simulation: X/Y"
5. 运行结果：0/945 全 incomplete（显示 [Running]）
6. 深查 .lis 文件内容 → 发现 **error** unable to open file netlist + job aborted → 全 failed（非 running）

## 金标准（用户接受的结论）
assistant 最终结论（A#44）：
- 仿真进度：0/945 finished，所有 945 个作业 job aborted
- 根因：netlist 文件缺失（**error** unable to open file ".../netlist/netlist"）
- check_sim Python 等价逻辑：扫描 *.sp 计总数 + result/*.lis 按 "total elapsed time"/"job aborted" 分类 + 无 .lis 归 running

## .lis 文件真实格式（从 trace tool_result 提取）
```
 1 | ****** PrimeSim HSPICE -- V-2023.12-SP1-1 linux64 (Apr 07 2024 8845341) ******
 2 |   Copyright (c) 1986 - 2026 by Synopsys, Inc. All Rights Reserved.
 ...
 8 |   Input File: <name>.sp
 9 |   Command line options: .../hspice -i <name>.sp -o ./result/
10 |   Start time: Wed Nov  4 14:33:22 2026
11-19 | lic: ... (FLEXlm license checkout)
21 |   **error** (<name>.sp:43) unable to open file ".../netlist/netlist" . Either the file doesn't exist or the path is wrong.
23 |                ***** job aborted
24 |  lic: Release primesim token(s)
25 |  lic: total license checkout elapse time:        0.67(s)
```

## .sp 文件名模式
`stb_iloadnear_<load>_vin_<vin>_corner_<proc>_temp_<temp>_vcc_<vcc>.sp`
- load: -1m, 0, 1m | vin: 0.3, 0.45, 0.6 | corner: tt/ff/ss/fs/sf | temp: -40/25/130 | vcc: 0.95/1/1.2

## 案例合成
- **case_id**: EDA-Eval-DesignFlow-SimProgressCheck-001
- domain: spice_sim, track: faithful (A), level: L1
- prompt: U#0 逐字原文
- 金标准通用化: check_sim_ref.py（接受 corner_stb 目录参数，扫描 *.sp + result/*.lis，按 total elapsed time/job aborted/无标记 分类 finished/failed/running，输出进度报告 + JSON）
- A 资产: corner_stb_A/ 20 .sp + 17 .lis（12 failed + 5 finished）+ 3 无 .lis running
- hidden B: corner_stb_B/ 30 .sp + 25 .lis（10 finished + 11 failed + 4 incomplete）+ 5 无 .lis running = 9 running
- check.py 14 断言(a-n) + 4 negative
- 自验: ref PASS 14/14 + 4 negative 全 FAIL + §4.9 三假全 FAIL + 闸门 14==14≥8 + jsonl test sha a83e541e0a==disk
