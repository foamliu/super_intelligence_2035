# trace_deepread — sr0ca · DQSELH/DQSEL_LH define 命名不一致诊断 Q&A

## trace 溯源
- session: `1791784530809_sr0ca` (subdir-path ALIVE: `sessions/1791784530809_sr0ca/1791784530809_sr0ca.messages.json`, 1,249,327B / 113 msgs, mtime Oct 12 16:00)
- user: `tongfanl`  host: `10.129.32.80` (hfhds206)  match_count: 173  shard: A  domain: verification
- r528 parked「file-deleted-postscan」假阴性复苏（flat-path NOFILE，subdir-path ALIVE，同 r821/r822 path-bug revival 第三例）
- D shard 2026-11-06 旧规则 parked「Q&A: asking gen_wtm_write_data function behavior, not produce」—— 按 2026-11-15 任务初衷重审，analysis-Q&A 已是合法任务形态；且 sr0ca 是 verification（A 域），非 D 域（waveform/schematic_netlist/analog）。r823 --force override 认领。

## 用户原话 (verbatim, 8 轮 user turn)
本 session 是 DDR6 DSCQA vecgen WTM pattern 的多轮 verification/debug 对话。8 个 user turn：
1. U#0: `.../WTM001_normal_check.v 帮我看下其中的gen_wtm_write_data函数，是不是只能为每个DQ设置一样的造错？`
2. U#6: `帮我检查下/home/tongfanl/DDR6/DSCQA/analogsim/WTM>WTM001_normal_check.v写的有没有问题？`
3. U#23: `WTM001_normal_check.v WTM002_normal_check.v 改好了，这两个都检查下`
4. U#35: `改好了，再检查下`
5. U#39: `` `ifdef X1P12 ... `elsif X1P6 ... `endif  1P12和1P6能合在一起写吗 ``
6. U#43: `看下.../runsti/gen_stimulus_ltf这个脚本，分析下DQSEH和DQSEL_LH的关系`（笔误 DQSEH）
7. **U#64: `看下/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local环境中的./runsti/gen_stimulus_ltf这个脚本，分析下DQSELH和DQSEL_LH的关系`**（← 本 case 采纳的用户意图）
8. **U#101: `不是，我问的是/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local环境中，DQSELH和DQSEL_LH两个define的关系`**（← 用户澄清，锁定意图）

## 造题意图 (任务初衷对齐)
真实用户意图 = DDR6 vecgen 环境里两个看起来同名实则不同的 define（`DQSELH` vs `DQSEL_LH`）的关系诊断 Q&A。这是合法的 analysis-Q&A 任务（顶部任务初衷：「没有任何预设题型清单可以否决一个真实用户意图」）。沿用 r818 NoConnPurposeExplainQA-001 / r817 DdjocCircuitPlanReconQA-001 范式（S5 第二范式 analysis-Q&A + specificity oracle + refuse-to-hallucinate）。

## trace agent 实际行为 (MSG 64-112)
1. read_files `runsti/gen_stimulus_ltf` → 6 行脚本，line 3 = `/home/coverage/DDR6/d6vecgen -q verilog -p dscqa -v V0 -f cfg_files/cfg_WTM -l log/stimulus_tongfanl/WTM_fsm_1009_try -d "DQSELH"`（脚本经 `-d "DQSELH"` 在编译期定义宏 **DQSELH**，无下划线、无 `_LH`）。
2. search_codebase `DQSELH`/`DQSEL_LH`/`DQSEL` → 全 "No results found"（search 只索引 tongfanl 工作目录的 symlink，没跟到 /proj/dscqa 实体）。
3. read_files `ddr6_interface.sv`（全文）→ line 76 `logic DqSelect; //Sel DQ 0-2 or DQ 3-5`（在 `DDR6_Share_interface`，line 68 起）。
4. read_files `ddr6_interface.sv` lines 226-240 → line 229 `` `ifdef DQSEL_LH `` → `DqSelect = 1'b1` / `else` `DqSelect = 1'b0` / `endif`（line 229-233，initial block 尾部，226-228 是 `CK_SYNC=1'b0; clk_sync_err=0; clksync_will_effect=0;`）。
5. search `` `define DQSEL_LH `` / `` `define DQSELH `` → 全 "No results found"（**两个宏在源码里都没有 `define，只可能经命令行 `-d` 传入**）。
6. agent 最终结论 (MSG 100/112)：**命名不一致**——脚本定义 `DQSELH`，代码检查 `DQSEL_LH`，二者不匹配 → `-d "DQSELH"` 永远不会命中 `` `ifdef DQSEL_LH `` → `DqSelect` 恒为 `1'b0`（else 分支），脚本意图被静默忽略。`DqSelect` 选 DQ[0:2] 或 DQ[3:5] 分组。两种改法：(A) 脚本改 `-d "DQSEL_LH"`（推荐，保持代码规范）；(B) 代码改 `` `ifdef DQSELH ``。

## ground-truth 签名 (从 A 动态提取, 非硬编码)
- 环境: `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local`
- 脚本: `runsti/gen_stimulus_ltf`（6 行，line 3 唯一未注释命令）
- vecgen 工具: `/home/coverage/DDR6/d6vecgen`，参数 `-q verilog -p dscqa -v V0 -f cfg_files/cfg_WTM -l log/stimulus_tongfanl/WTM_fsm_1009_try`
- 脚本定义的宏: **DQSELH**（`-d "DQSELH"`，无下划线）
- 代码检查的宏: **DQSEL_LH**（`ddr6_interface.sv` line 229 `` `ifdef DQSEL_LH ``，有下划线 + `_LH`）
- 受控信号: `DqSelect`（line 76 `logic DqSelect; //Sel DQ 0-2 or DQ 3-5`，在 `DDR6_Share_interface`）
- ifdef 块: line 229-233，`DQSEL_LH` → `DqSelect = 1'b1`，`else` → `DqSelect = 1'b0`
- 源码 `define 搜索: `DQSELH` / `DQSEL_LH` / `` `define DQSEL_LH `` / `` `define DQSELH `` 全 "No results found"（两宏均无源码 `define，只经 CLI `-d` 传入）
- 核心诊断: **命名不一致 / mismatch** → `-d "DQSELH"` 不生效，`DqSelect` 恒 `1'b0`
- 修复: (A) 脚本改 `-d "DQSEL_LH"`；(B) 代码改 `` `ifdef DQSELH ``

## B hidden (specificity oracle, 同构改名, judge-only)
- 脚本 `gen_stimulus_hb`：`-d "DQSEL_HB"`（defines DQSEL_HB），不同 cfg/log 路径
- `ddr6_interface_hidden.sv.frag`：`logic DqPick; //Pick DQ 4-7 or DQ 8-11`，`` `ifdef DQSEL_LB `` → `DqPick = 1'b1` / `else` `DqPick = 1'b0`
- `define_search_report_hidden.txt`：`DQSEL_HB` / `DQSEL_LB` / `` `define DQSEL_LB `` / `` `define DQSEL_HB `` 全 "No results found"
- B-only 标识符（报告不得出现）: DQSEL_HB, DQSEL_LB, DqPick, DQ[4:7], DQ[8:11], gen_stimulus_hb, cfg_WTMX, stimulus_hb, WTM_fsm_hb, DDR6_Share_interface_hb, rand_config_if_hb, etc.

## 反造假 / 反退化
- 报告必须基于 A 真实文件内容（脚本 line 3 的 `-d "DQSELH"`、ddr6_interface.sv line 76/229 的真实代码），不能只给通用宏定义教科书结论
- 不得编造 A 中不存在的宏名 / 文件 / 行号 / `define
- 必须明确「命名不一致 → 不生效」的核心诊断（不是只说「它们相关」）
- 必须如实承认源码里没有 `define（refuse-to-hallucinate，搜索结果 No results found）
- markdown 结构: ≥2 个 `##` section，中文主体字符 ≥80
- 3 seed 随机抽样核心签名池 ≥8，防硬编码 / 防 prompt-echo

## 与既有 case 区别（防碰撞）
- 同 user tongfanl / 同项目 /proj/dscqa 的 gf2ud → B shard case `TzqlatLocate-001`（spice_sim，tZQLAT 提取 produce-task）。sr0ca 是 verification 域 analysis-Q&A（DQSELH/DQSEL_LH define 命名诊断），不同 session / 不同文件 / 不同意图 / 不同判分范式 → 非碰撞。
- 同 shard A 的 r818 NoConnPurposeExplainQA-001（Innovus noConn marker）、r817 DdjocCircuitPlanReconQA-001（电路方案重构）同范式但不同域不同主题 → 非碰撞。
