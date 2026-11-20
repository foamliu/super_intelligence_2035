# trace_deepread — k7hc6 (tongfanl@hfhds201) · VecgenProbeEmptyDiag

## trace
- session: `1791457291368_k7hc6` (tongfanl, hfhds201, mc=76, 76 msgs, last=assistant COMPLETE)
- path: `/home/tongfanl/.cline/data/sessions/1791457291368_k7hc6/1791457291368_k7hc6.messages.json`
- discovery: 11-05 重扫令 hfhds201 cron 盲区 270 sessions top-100 diff ledger_B(1792 anchors) → 9 非内部 not-in-ledger (全 tongfanl) → peek 9 → k7hc6 CLEAN A-faithful (上轮 11:02 取 xd7ut，本轮取 k7hc6)

## A-faithful 选轮
- **U#0（任务说明轮，逐字作 prompt）**：用户粘贴 `./runsti/gen_stimulus_ltf` 的终端输出 —— 三次 vsim 提交（TT/FF/SS, WTM001_normal_check 2b16g_BL02_12800 X2P3），每次都触发 d6vecgen `width==X2P3 bank array must start with 2b16g, here is 2b32g` 警告，结尾 `[INFO] Pass:2, Error:1`。**提出需求**（隐式：这次跑出了什么问题），**未给根因/修复** → 符合 A-档选轮 ✓
- U#28「说中文」、U#30「有什么问题吗？」：后续追问/澄清，不入 prompt（U#30 已被金标准 A#75 回答，但作 prompt 会丢 U#0 的 Pass:2/Error:1 上下文，故用 U#0）

## 金标准（assistant A#75，COMPLETE）
诊断 d6vecgen 命令 `/home/coverage/DDR6/d6vecgen -q verilog -p dscqa -v V0 -f cfg_files/cfg_WTM -l log/stimulus_tongfanl/WTM_fsm_1008 -d "DQSELH"`，发现 **3 个问题**，核心是问题 1：

### 问题 1（最关键）: FF 工艺角 probe.tcl 为空
- **现象**：FF `probe.tcl` = 0 字节空文件；TT/SS `probe.tcl` = 35 行（含 `run`/`exit`）；仿真器报 `xmsim: *W,NORUNCMD: No 'run' command issued.` → 仿真未运行 → 无 stimulus.list/trantime.sim → d6vecgen 判 ERROR
- **根因**：`bin/vsim` 中 `gentbprobefile("local")`（1127-1131 行）：
  ```perl
  } elsif ($config eq "local") {
      if(-e "$worktb/probe.tcl") {}         # 已存在就跳过！
      else { if(-e $linkfile) { system("cp $linkfile $worktb/."); } }
  }
  ```
  "local" 模式下若 `$worktb/probe.tcl` 已存在（即使空）就不复制 → 首次 FF 因 NFS/cp 瞬态失败生成空文件 → 后续重试因空文件已存在永不修复 → 自我 perpetuating 错误。TT/SS 首次成功复制，故正常。
- **修复**：`if(-e "$worktb/probe.tcl" && !-z "$worktb/probe.tcl") {}`（存在且非空才跳过）

### 问题 2: BL0 vs BL02 截断
- vecgen.rpt 33-41 行 9 个 ERROR，名称含 `BL0`（少 "2"，应为 `BL02`），涉及 MCS/MCP 双 SubChannel 测试 → 突发长度参数 `BL02` 被截断成 `BL0`（独立问题，本轮 case 不聚焦此项）

### 问题 3: cp sdf/* 报错
- `cp: cannot stat '.../sdf/*': No such file or directory`（SDF 目录缺失，次要）

## 证据链（从 trace tool_result 提取真实 file:line）
1. **vecgen.rpt**（174 行）：FF `2b16g_BL02_12800_FF_DQSELH.X2P3_12800` 跨重试恒 ERROR；TT/SS PASS；另 2b32g_X1P6 全 PASS（对照）
2. **TT/probe.tcl**（35 行）：`run` / `drivers -active` / `process -next` / `exit`（完整）
3. **FF/probe.tcl**：空（0 字节，read 返回空）
4. **FF/*.out**（4 次重试 .out）：均含 `xmsim: *W,NORUNCMD: No 'run' command issued.` + `Exiting ... (total: 00:00:09)`（10 秒即退，未真跑）
5. **TT/runCmd**：6 行 vsim 命令（FF 无 runCmd 文件）
6. **bin/vsim:1111-1134** `gentbprobefile`：copy/link/noprobe/local 四分支；local 分支 `if(-e "$worktb/probe.tcl") {}` 无 `!-z`（bug）
7. **d6vecgen:593**：`Warning: when width==X2P3, bank array must start with 2b16g, here is 2b32g!! I have helped to replace it!!`（2b32g→2b16g 自动替换警告，与 ERROR 正交的 distractor）

## 合成（case EDA-Eval-DesignFlow-VecgenProbeEmptyDiag-001，spice_sim A-faithful L1）
- **参考脚本** `diag_vecgen_probe_empty.py <logdir> <vsim_script> -o out.json`：
  - 解析 `vecgen.rpt`（每行 `<path> <PASS|ERROR>`，容错 `  N | ` 前缀；正则 `_(TT|FF|SS)_` 抽 corner；计 pass/error）
  - 遍历 logdir 子目录，每角查 `probe.tcl`（exists/size/`run`/`exit`）、最新 `*.out`（NORUNCMD / `No 'run' command issued`）、`A_Compare.rpt`/`runCmd` 存在性
  - error_corner = (probe_tcl_size==0 或 has_run==False) 且 out_has_noruncmd 且非 a_compare 的角
  - `detect_skip_empty_bug`：brace-count 定位 `gentbprobefile` 函数体 → 正则定位 `elsif ($config eq "local")` 分支 → 检测 `if(-e ... worktb ... probe.tcl)` 存在守卫 且 分支内无 `!-z`/`-s ` 非空守卫 → bug=True
  - 输出结构化 JSON（input-agnostic，错误角/bug/计数全由输入推导，零硬编码）
- **A 资产** `A_vecgen_log/`：真实提取 —— vecgen.rpt（TT PASS×3/FF ERROR×3/SS PASS×3 + 2b32g PASS×3，pass=7/error=3）+ TT/SS 子目录（真实 35 行 probe.tcl + runCmd + A_Compare.rpt + .out 无 NORUNCMD）+ FF 子目录（空 probe.tcl + .out 含 NORUNCMD，无 runCmd/A_Compare）+ vsim_A（真实 gentbprobefile，local 分支无 !-z = bug；含 A-only 标记 `A_only_vecgen_marker_X1P6_1280_FF`）
- **hidden B** `B_vecgen_log/`：结构不同 —— WTM003 / 2b32g_BL02_9600 / X1P6；**SS 是出错角**（空 probe.tcl + NORUNCMD，无 runCmd/A_Compare），TT/FF 正常；`vsim_B` local 分支**已加 `!-z` 修复** → bug=False（与 A 相反，挡硬编码 corner=FF / bug=True）；pass=5/error=4（与 A 7/3 不同）
- **判分 16 断言(a-p)**：含交叉输入守卫(n: A 上 error_corner=FF & bug=True 证泛化)+A-only 未泄漏(o: outB 无 A_only_vecgen_marker)+3 次幂等(p)
- **自验**：ref PASS 16/16 ✓ + 4 negative 全 FAIL distinct（naive_hardcode_a→f/m/o/c/d, naive_print_expected_b→n, empty_shell→b..., core_deleted→f/g/h/i/j/k/e/n）+ NEG_RC=0 ✓ + §4.9 三假（空壳/打印期望/删核心）全 FAIL ✓ + 断言闸门 16==16≥8 ✓ + jsonl test==disk sha c7f1ec407e2ac5fd ✓
- **落库**：EDA-Eval-DesignFlow_B.jsonl 170→171；ledger mark case（172→173 covered，spice_sim 136→137）
