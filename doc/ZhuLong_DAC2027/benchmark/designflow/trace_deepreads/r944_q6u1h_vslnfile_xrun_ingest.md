# r944 deepread — 1795140188164_q6u1h (VsLnfileXrunIngestAnalyzeQA-001)

- trace: 1795140188164_q6u1h (subdir-path, NOFILE 假阴性已绕过)
- user: e0014036 @ hfeg0pkn004 (10.129.2.13), mc=30
- keywords: verilog:152;netlist:43;rtl:13;systemverilog:5;hspice:4;.def:2;pt_shell:1;cadence:1 → ak=171/ck=0 strict A-pure
- n_msgs: 23 (6 user turns)
- domain: verification (xrun/Cadence Xcelium + 自研 bin/vsim perl + runSim_PPR_new.sh + DDR6 RCD 集成)
- ledger: r943 后 66 fresh A-pure 中 q6u1h = fresh + ak 最高 (171) 之一；本 shard A 归属 (digital/verification)

## 用户真实意图 (trace 逐字)

- U#0 (msg0 context summary): 将 Renesas DDR6 RCD01 行为模型整合进平台 DDR6 验证环境；阶段 3 接入平台，top.sv 补丁未落地。
- **U#1 (msg1, 主问)**：「从之前runSim_PPR_new.sh脚本里面分析DDR6环境的bin/vsim @lnfile 追加 .svp+wrapper + xrun 收编方式」
  → 分析-Q&A：bin/vsim 的 @lnfile 机制 + xrun 如何收编 .svp+wrapper
- U#11/U#12 (msg11/12, debug)：分这个log的报错 /rundata/.../rcd_nop.X1P6_200（暂停未完成）
- U#15 (msg15)：暂停
- U#17 (msg17)：PPR分析文档.md 读取（doc-search，已完成 msg22）

## trace gold (assistant msg10 完整答，含实测行号)

全链路 (runSim_PPR_new.sh:96 → bin/vsim → @lnfile → gentblnfile → genrunfile → xrun):
```
runSim_PPR_new.sh:96（默认分支）
  ./bin/vsim -sr pte_test --msierun --local --debug -d "POST USESDFX PTE MD_OFF SS PPR"
             -b X1P6 -q verilog -l debug/<ts> -f <period> --psdpat -o +<pattern>
  │ 参数解析(640-708) → tbconfig(139-202): ddr6/dscqa/V0
  │ @lnfile 定义(215-247): …top.sv, libs, libsdb, ddr6_idd_tasks.sv, ddr6_model.v
  ▼ runsim(774, chdir $work_dir = simdir)
  ├─ gentblnfile($work_dir,$worktb) (778 → 992-1055)  ★@lnfile 唯一消费点
  │    三级搜索: $work_dir/common/<f> → $work_dir/dscqa/<f> → $work_dir/<f>
  │    命中即 rm -Rf $worktb/<f>; ln -s <命中> $worktb/.  ← 只"物化"进运行目录, 不编译!
  │    libs 特例(1011-1028): mkdir $worktb/libs; ln -s $work_dir/libs/* → $worktb/libs/.
  │    Project 覆盖特例(1042-1051): ...
  ├─ genpatternsfile(779 → 1060-1077): $work_dir/Project/* 链入运行目录
  │    → $worktb/Project/rcd 可达 ✔
  └─ genrunfile(901/970 → 1293-1506) 生成 verilogrun, CWD=运行目录
       xrun 命令行源文件只有两类:
         -v libs/<file>  (1452-1462: ls libs/ 逐文件生成)  ← 库收编点
         top.sv          (1497)                            ← 顶层收编点(include 链)
```

## 关键结论 (修正指南原建议)

1. **@lnfile ≠ 编译收编**：只把文件符号链接进运行目录，xrun 命令行不会出现这些文件名。指南"把 .svp 加进 @lnfile"单独执行无效。
2. **xrun 收编入口只有两个**：`top.sv`（include 链：ddr6_test.sv、ddr6_model.v、netlist…）和 `-v libs/*`。
3. **定制层就是 simdir 本身**：gentblnfile 搜索根 = $work_dir (本 simdir)，不是 /proj 共享区；simdir 里的 top.sv/libs 符号链接决定每次运行收编什么。

## 三种收编方案 (A/B/C)

| 方案 | 做法 | 特点 |
|------|------|------|
| **A. simdir libs 本地化（推荐）** | mv libs libs.bak_日期 && mkdir libs；原 8 simlib 符号链接链入 + 拷入 .svp+wrapper → genrunfile ls libs/ 自动生成 -v libs/<10 文件> | 零脚本改动；只读 shuchao 目录；回退=恢复链接 |
| **B. genrunfile 加两行** | 1462 行 libs 循环后追加 -v Project/rcd/renesas_ddr6_rcd01_a0.svp 与 -v Project/rcd/rcd_wrapper.sv | 改前备份 bin/vsim |
| **C. top.sv include 链** | 须先本地化 top.sv (rm top.sv && cp -L <tborgdir>/top.sv .)，再 ifdef USE_RCD 内 include 两文件 | 与必做的 top.sv 例化/重定向合并 |

## 配套注意

- USE_RCD 宏：runSim_PPR_new.sh DEFINES 追加，genrunfile 1420-1429 自动转 +define+USE_RCD
- msie 快照：源文件集变化首次 -automsie 增量重编译；复用旧 debug/ 前必须清 noregression/

## 造题决策

- task_id: VsLnfileXrunIngestAnalyzeQA-001
- 档次: B档 synthesized (bin/vsim 实体 permission-denied 不可读，按 trace 行号+机制重构 fragments；用户意图+行号 trace-faithful)
- 范式: S5 第二范式 analysis-Q&A + specificity oracle
- fixture A: 5 个重构 bin/vsim fragments (带行号) — vsim_lnfile_def.txt (215-247) / vsim_param_parse.txt (640-708) / vsim_runsim.txt (774-779) / vsim_gentblnfile.txt (992-1055, 含 libs 特例 1011-1028) / vsim_genrunfile.txt (1293-1506, 含 libs loop 1452-1462 + top.sv 1497 + defines 1420-1429)
- check.py: 12+ 断言，re-parse A 提取 expected 行号/函数名/结构事实；inlined HIDDEN_B (不同行号+不同函数名) anti-leak；§4.9 三假 FAIL；refuse-to-hallucinate (报告引用函数名 ⊆ A 函数名集)
- hidden B: inlined (无 separate files)
