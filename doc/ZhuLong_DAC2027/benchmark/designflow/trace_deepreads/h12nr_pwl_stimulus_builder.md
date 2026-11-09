# Deep-read: h12nr — mike@hfeg0pkn003 (mc=32, schematic_netlist)

- **session**: `1793865688745_h12nr.messages.json` (directory-based, 15 msgs)
- **user**: mike, host hfeg0pkn003, D-domain (140 netlist + 94 schematic tools)
- **trace_source real task**: mike 在 `/ai_sandbox/dscqa/V0/agentdir/mike/dscqa_array_m0d5G_YS_Bot_sub_schematic_ALPS` 下(plan 模式)要开发一个脚本：**只有一个输入文件，脚本会生成三个文件和一个文件追加**。
- **agent 行为**: 探查目录 → 发现是 ALPS/Finesim DDR6 子块 `m0d5G_YS_Bot_sub` 仿真目录；工作流=上层 Fullchip FSDB 经 `dump_pwl.tcl` 导出 PWL 激励 → 拆分/处理成子块仿真激励；读到 `make_final.py`(处理 `*_pwl_final`) 与 `input.sp`/`run`。`run_approved_command` 的 `shell-runner`/`python-runner` 为动态 profile 需先写 .py 再执行 → agent 写 `inspect_alps_dir.py` 检查各 PWL 文件结构时 **trace 截断，未产出最终脚本**。
- **user 轮**: U#0 是 clean goal statement("脚本只有一个输入文件，脚本会生成三个文件和一个文件追加")→ 合格 A 档选料轮；trace 末尾无用户接受结果(截断)→ 取 B-grade synthesized。
- **私有依赖**: `/ai_sandbox/dscqa/...` 仿真目录与 `make_final.py` 在 .75 共享视图不可读(空)→ 不可复刻。
- **合成决策 (B-grade synthesized)**: 严格忠实于用户声明的契约(1 输入 → 3 文件 + 1 追加)与真实工作流(PWL 激励 finalize for ALPS 子块仿真)：
  - 输入：1 个原始 PWL 激励文件(多信号，`# signal <name>` 分段，`<t_ns> <v>` 行)，刻意注入乱序时间/重复(t,v)行/连续等值段以测试清洗逻辑。
  - 产物 1 `pwl_final.sp`：SPICE PWL 电压源 include 文件(每信号 `V<sig> n<sig> 0 PWL(...)`)，时间严格递增、无连续等值。
  - 产物 2 `pwl_summary.json`：signals/n_signals/t_min_ns/t_max_ns/n_points_total/n_edges/per_signal。
  - 产物 3 `pwl_edges.tsv`：`time_ns\tsignal\tprev_v\tnew_v`，每电压跳变一行。
  - 追加 4：向既有 deck 追加 `pwl_stimulus_include` 块(BEGIN/END + .include + 全部信号名)。
- **A vs 隐藏 B**: A=4 信号(DQ0/DQ1/DQS_t/DQS_c, 23 points, 19 edges, t_max 6.0)；B=5 信号(RDQS0/RDQS1/RDQS2/WCK_t/WCK_c, 30 points, 25 edges, t_max 12.5)。名/数量/取值全不同 → 反硬编码。B 含 RDQS0 重复(7.5,0.9)x2 + 连续等值(12.5/13.0 均 0.9) + RDQS2 乱序(9.0 在 3.0 前)。
- **判分**: check.py 子进程真跑候选脚本 on B + 12 条 a-l 独立条件；独立解析器重算 ground truth 比对；反硬编码 on A。
- **自验**: ref PASS 12/12；§4.9 三假(empty->b/print_expected->l/core_deleted->e)全 FAIL；2 naive(no_sort->d/no_edges->j)全 FAIL；NEG_RC=0 n_distinct=5；3-seed order-independent；anti-hardcode A-vs-B PASS。
- **case_id**: EDA-Eval-DesignFlow-PwlStimulusBuilder-001 (schematic_netlist, B, L2, k=12)
- **byte-sync**: sha db9139578456 size 12109; D.jsonl 268→269.
