# trace_deepread · vqpd5 · LPDDR5 TB 学习文档生成 (doc-search / analysis-Q&A)

> 2026-11-16 r630 deepread. trace = wenfeiz @ hfeg0pkn004, session 1794539090854_vqpd5, mc64, digital.
> 复活来源: r503 以旧 weak 筛子「doc-gen not produce-task」parked; 11-15 令退役旧筛子, doc-search/analysis-Q&A = 真实用户意图, pool_reaudit_A.tsv 已标「可造 (revived: doc-search)」. 本轮 5th A-domain strict-peek top 40 去重 11 unique → 10/11 case/跨域 + **vqpd5 唯一 parked 可复活**.

## 一、用户真实意图 (trace-faithful, USER#1 原话)

> `/proj/ddgoa/V0/workdir/wenfeiz/sos_manage_lpddr5/lpddr5_tb/`
> 这个lpddr5 TB，我要学习这个TB，生成一个文档：1 大致介绍一下TB结构. 2 TB怎么运行的？3 以basiccheck这个pattern为例，介绍下一个pattern怎么在这个环境跑起来的

**意图 = doc-search / analysis-Q&A**: 学习一个 LPDDR5 testbench, 生成结构化文档 (①TB 结构 ②TB 运行流程 ③basiccheck pattern 跑起来流程). 后续 USER#2-#11 全是同一 TB 的追问 (cmd_cal 计算 / Write task / Read task / FIFO 时序 / Deselect NOP / dorandcasfsoff / 仲裁信号 / gvim 配置), 均为 TB 内部理解 — 佐证主意图是「学懂这个 TB」.

## 二、trace 概况

- archive 391 msgs (3.6MB) + active 119 msgs (387KB) = 510 msgs, 179 tool_use, 112 read_files.
- 工具链: list_allowed_files (27 次, 摸 TB 目录树) + read_files (112 次, 读 TB 源码) + editor (生成 LPDDR5_TB_学习文档.md → lpddr5_tb_learning.txt) + ask_question.
- 交付物 (trace 内): `LPDDR5_TB_学习文档.md` (后因 gvim 打不开 .md 改 `lpddr5_tb_learning.txt`), 含框图/流程图.

## 三、TB 结构 (evidence anchor — 从 trace list_allowed_files + read_files 还原)

TB root = `/proj/ddgoa/V0/workdir/wenfeiz/sos_manage_lpddr5/lpddr5_tb/` (private /proj, .75+ssh hfeg0pkn004 均 NOT_ON_75/NOT_ON_HOST — 文件已蒸发, **但 trace 内 read_files 结果含源码内容**, 可从 trace 抽取作 assets/A).

```
lpddr5_tb/
├── A_Pattern_Sim.v          (symlink, 顶层 pattern sim 入口)
├── lpddr5_test.sv           (主 TB, 9321+ 行, agent 分块读 1-18/100-200/200-400/400-700/700-900/900-1200/9200-9321)
├── lpddr5_package.sv        (类型/常量包)
├── lpddr5_interface.sv      (CA/DQ 接口)
├── assertion/readme         (断言说明)
├── bin/                     (vsim, genpat.pl, tbmanage, bj_rerun, bj_rerun_print — 多为 symlink)
├── config/                  (tbconfig, files — 编译/仿真配置)
├── coverage/
├── patterns/function/
│   ├── cmds_2rank/  cmds_act1act2/  cmds_auto/  cmds_basiccheck/
│   ├── cmds_testmode/  cmds_onebank/  cmds_modereg/
│   └── (cmds_onebank/OneBankWrRdPre.v, ActWr0RdAp0.v — agent 读)
├── patterns/proj_function/
└── Regressions/
    ├── function/   (basiccheck.run, basiccheck.inc, 2rank.run/.inc — *.run+*.inc 对)
    └── pte_function/ (seqlist_*.txt_processed_verilog.inc)
```

**关键源文件 (assets/A 候选, 从 trace read_files 结果抽)**:
1. `lpddr5_test.sv` — 主 TB (module/task 层次: cmd_cal, Write, Read, load_cmdR/F, loadwrcontrol, shift_dq_fifoonecycle, load_wck_fifofirstcycle, update_state, dorandcasfsoff 等)
2. `lpddr5_package.sv` — 类型/常量
3. `lpddr5_interface.sv` — CA/DQ 总线接口
4. `bin/vsim` — 仿真启动脚本 (agent 读 1192-1500 行段)
5. `bin/genpat.pl` — pattern 生成 perl 脚本
6. `config/tbconfig` + `config/files` — 编译/文件清单配置
7. `Regressions/function/basiccheck.run` + `basiccheck.inc` — basiccheck 回归用例定义 (运行入口 + 包含文件)
8. `patterns/function/cmds_onebank/OneBankWrRdPre.v` + `ActWr0RdAp0.v` — 具体 pattern .v (单 bank 写读 pre / act-wr-rd-ap)
9. `assertion/readme` — 断言说明

## 四、TB 运行流程 (从 trace agent 生成文档 + 源码还源)

1. **编译**: `config/files` 列源文件 → `bin/vsim` 调 vsim 编译 (tbconfig 配置选项)
2. **pattern 生成**: `bin/genpat.pl` 把 patterns/function/cmds_*/`*.v` (pattern 描述) 转成仿真可跑的 verilog
3. **回归跑**: `Regressions/function/<name>.run` (入口) + `<name>.inc` (include 列表) → tbmanage 调度 → vsim 跑
4. **basiccheck 跑起来**: basiccheck.run → basiccheck.inc 引 cmds_basiccheck/ 下 pattern → A_Pattern_Sim.v 顶层 → lpddr5_test.sv 里 task (cmd_cal→load_cmdR/F→loadwrcontrol→update_state; 读侧 load_wck_fifofirstcycle→dq_out)

## 五、合成计划 (C-A analysis-Q&A 模板, 下轮交付)

- **case_id**: `EDA-Eval-DesignFlow-Lpddr5TbStudyDoc-001` (或 v2 后缀, 视是否算 v1 off_intent 重做 — vqpd5 旧 v1 无, 是 parked 非 off_intent, 故用新 id 非 -v2)
- **domain**: digital (LPDDR5 TB = verification/digital, 本 shard A)
- **档**: A 档 trace-faithful (prompt = USER#1 原话 + 路径)
- **交付物**: `lpddr5_tb_study_report.json` only (结构化报告, 非 .md — 便于 check 解析; 字段: tb_structure / run_flow / basiccheck_pattern_flow, 每段含 name+summary+evidence{file,token})
- **assets/A** (SUT 可见): 从 trace read_files 结果抽取的真实 TB 源文件子集 (上第三节 9 类) + 目录树 listing.txt
- **assets/B** (hidden, judge-self-check only): 一份**同构但取值/结构全异**的 sanitized TB 变体 (改 module 名/任务名/层次/命令序列/寄存器宽度 — 内嵌 check.py 的 _parse_tb 独立解析 B 验判分通用非硬编 A)
- **check() 断言 (≥8, C-A 四件套)**:
  - content-correctness (≥13): report 可解析 / tb_structure 含 3 顶层组件 (test.sv+package+interface) / patterns 子目录名 / Regressions function+pte_function 两类 / bin 工具名 (vsim+genpat.pl+tbmanage) / config 两文件 / run_flow 含 编译→pattern 生成→回归跑 三阶段 / basiccheck_pattern_flow 含 basiccheck.run+.inc 引用 / cmd_cal task 存在 / Write/Read task 存在 / FIFO shift 机制 / WL 延迟概念 / Deselect NOP 空转 / 仲裁信号
  - evidence-verification: 每段 section.evidence.token 真实存在于所引 A 文件 (file+token 回溯)
  - B judge-self-check: check() 内嵌 _parse_tb 独立解析 B, 验判分逻辑通用 (非硬编 A 字面量)
  - 3-seed: 打乱 B 文件块顺序, _parse_tb 提取 B 事实稳定
- **trace_source**: { user: "wenfeiz", host: "hfeg0pkn004", session_file: "1794539090854_vqpd5", match_count: 64, real_task_summary: "学习 LPDDR5 TB 并生成文档 (结构/运行/basiccheck pattern 流程)" }
- **DEBT**: 本轮 deepread done (此笔记), case 合成下轮交付 (trace 3.6MB >2MB 阈值, TASK §3 允许本轮只深读)

## 六、判分可行性 (check 牙齿)

- ✅ evidence anchor 强: TB 源文件可从 trace read_files 结果抽 (file+内容真实, 非杜撰)
- ✅ content-correctness 可独立失败: 13+ 维度每条单 FAIL
- ✅ B judge-self-check: 同构 sanitized 变体, _parse_tb 独立解析, 反硬编
- ✅ 退化提交回归: 空壳→content 失败 / print 期望→evidence 失败 / 删核心→content 失败
- ⚠️ 资产保真度: TB 源文件从 trace 抽 (非 live /proj, 已蒸发) — asset_fidelity=original (trace-embedded, 非文本替身, 文件内容真实可核)

## 七、5th peek 全账 (r630 strict A-dominant, mc 10-150, top 40 去重 11)

| session | ledger | 状态 |
|---|---|---|
| y6liq | A | case (SpiceStructAnalyze-001) |
| gn11a | B | 跨域 (wrong-shard) |
| **vqpd5** | **A** | **parked (r503 旧 weak) → 本轮复活 (DEBT)** |
| iqvz3 | A | case (MbistTwincellDiag-001) |
| mdxo8 | D | 跨域 |
| pnd3n | D | 跨域 |
| 0t5o9 | A | case (ItfCompare-001) |
| 515eb | B | 跨域 |
| sutmr | D | 跨域 |
| twknv | B | parked (r502 Q&A code-comprehension) — 跨域 B, 非 A |
| riotl | B | parked (lpddr6 netlist wrong-shard A) — 跨域 B |

**结论**: 5th peek 11/11 全 touched (case/parked/跨域), 唯一 A 域可复活 = vqpd5 (旧 weak 筛子 parked, 新标准复活). 承 r617/r620/r623/r629 四证, 第五证同 11-16 scan 成立: strict A-dominant mc≥10 可达池里无 net-new 未动过候选, 仅旧 weak parked 可挖. vqpd5 是 r615 3p5vl 之后第 2 条旧 weak 复活候选.
