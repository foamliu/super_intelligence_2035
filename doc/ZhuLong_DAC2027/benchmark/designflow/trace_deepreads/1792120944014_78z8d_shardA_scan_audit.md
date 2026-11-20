# shard-A 候选扫描审计（轮 37）— 关键战略发现

> 本轮未合成 case。深读 5 条 fresh shard-A 候选，确认 **shard-A digital/verif/pnr trace 是知识/咨询型会话，非 build-and-deliver 任务**——这是 genuine external blocker。但本轮纠正了一个持续 3 轮（33-36）的搜索方法错误，价值在结论本身。

## 🔑 战略发现：前 3 轮搜错列了

- `summary.tsv` 列结构（probe_remote.sh printf 顺序）：`$1=ip $2=host $3=user $4=basename $5=match_count $6=kw $7=tools`
  - **`$6=kw`** = RE1 uniq 计数，**包含** dc_shell/primetime/pt_shell/genus/tempus/icc2/verilog/rtl/starrc/formality 等数字工具词
  - **`$7=tools`** = RE2，**只含** virtuoso/innovus/pyAether/dbGet/dbShape/dbCreate/cellview/schematic/netlist/synthesis/calibre/spectre/hspice/lang/host —— **模拟/版图偏置，根本不含数字/验证工具**
- 轮 33-36 的 next 命令 awk 过滤 `$7 ~ /verdi|vcs|dc_shell|...|rc|pt_shell/` → `$7` 是 RE2（模拟词），永远匹不到 dc_shell/primetime（它们只在 `$6=kw`）。所以"mc≥100 shard-A 工具候选耗尽"的结论是**假象**——搜错列了。
- 正确口径：搜 `$6`（kw）。本轮用 `$6` 找到 **382 条 fresh shard-A 候选**（excl 台账 79 后，含 dc_shell/primetime/pt_shell/genus/tempus/icc2/verilog/rtl/starrc）。
- `daily_eda_scan.sh` 也有同类 bug：step3 awk 的 `e` 正则只含 `virtuoso|innovus|calibre|spectre|hspice|synthesis`，**不含 dc_shell/primetime/pt_shell/genus/tempus/icc2/verilog** → 纯数字 session 在 daily eda_trace_*.log 里被直接丢弃。所以 daily log 也无数字/验证 session（仅 calibre/innovus/synthesis 词能进）。**修这个 awk 即可让 daily scan 产出数字/验证候选。**

## 深读 5 条 fresh shard-A 候选（结论：全部 unfit design_flow）

| sid | user@host | kw 画像 | 结论 |
|---|---|---|---|
| 78z8d | e0045128@hfeg0pkn001 | genus:77 primetime:10 tempus:5 | **Q&A**：问 genus 时间单位→ns / timing report 时间单位 / netlist 层级被展平。助手 RAG 空、sandbox refused，最终给 markdown 答案。无交付物 → parked |
| dse5n | e0046913@hfeg0pkn003 | icc2:62 floorplan:46 primetime:16 synthesis:17 | **咨询**：数字中端工程师问"从零搭 low power flow 全流程，请详述流程细节/工具/前后端对齐/如何指挥推进"。助手 read feint 参考脚本（/apps/imctf/cad/script/digital_flow/feint/{Makefile,scripts/dc.tcl,fm.tcl,pt.tcl,setup/common_setup.tcl}）+ 产长 markdown 方案。**feint 脚本是真实可读资产**，但用户问的是 plan 不是 build → 无可判定交付物。A-档 faithful unfit（prose）。→ parked（备注 feint 资产可作未来 B-档 L2 flow-audit case 的素材） |
| nc938 | e0045128@hfeg0pkn001 | primetime:37 genus:5 icc2:2 | **纯 Q&A**：PT 读 UPF 目的 / 不读 UPF 手配 lib / DC wireload load_pin+driving_cell / clock Fmax 评估 / setup-hold clock uncertainty / DFT 学习路径。全概念 markdown，无工具运行、无交付物 → parked |
| 65efs | e04201@hfeg0pkn004 | primetime:17 tempus:15 genus:7 | **纯 Q&A**：大 netlist 分析方法 / DRJOA DRAM test-mode 减 pump。AskEDA/CIMI KB 多数未配置/未命中，markdown 通用答案。无交付物 → parked |
| f0qtv | t0002987@hfhds201 | genus:88 synopsys:110 .def:61 .gds:28 | **非 EDA**：调试 ZhuLong/cline desktop-app 本身（中文输入乱码 / 切 session 任务停滞 / 追问抢前输出）。108 msgs，0 write_file，1 run_commands。genus/synopsys/.def/.gds 命中是 app 代码库噪声，非 EDA flow → parked |

## 模式结论

shard-A（digital/eda_other/pnr_signoff/verification）trace 里，工程师把 cline 当**知识助手**用（问概念/规划/方法论），不是当 build agent。真实 build-and-deliver 任务（产脚本/报告/zip）在本语料里集中在**模拟/版图**（virtuoso/schematic/layout，shard B/C）。数字域的 build 任务（写综合脚本、跑 STA、产 timing report）即使存在，其交付物（脚本/报告）也往往是用户自己写、cline 只答疑。

## 下一轮可行路径（按可行性排序）

1. **修 daily_eda_scan.sh 的 step3 awk**（把 dc_shell/primetime/pt_shell/genus/tempus/icc2/verilog/rtl/starrc/formality/vcs/veridi 加进 `e` 正则），让 daily scan 重新产出数字/验证 session 候选 —— 可能捞到 build 型 session（11/01-11/04 新 session）。需 t0002965 改脚本（或 agent 提补丁）。
2. **用 feint 参考脚本做 B-档 L2 case**：scope = "写一个 flow-audit 脚本，ingest feint 的 dc.tcl/fm.tcl/pt.tcl + Makefile + common_setup.tcl，输出结构化 low-power-flow manifest（JSON：UPF_MODE 三模式 / power_domain 命令 / isolation / level_shifter / retention / 前中后端工具映射 / 交付件对齐 checklist）"。cross-input guard B = 改造过的 feint 变体（不同 UPF_MODE、不同 power domain 结构）。check() 解析 manifest 结构 + 特定提取事实 + B 复跑。⚠️ 这是 L1（离线 parse，无 EDA 工具运行），违 §5"新建只做 L2/L3"——需升 L2：让候选脚本在 .75 上真跑一个最小 genus/pt dry-run（`genus -f dry_run.tcl` 仅 check 语法/加载）或用 `make -n` 干跑 Makefile。**待评估 genus/pt license 可用性。**
3. **继续扫 `$6=kw` 列更靠后的候选**（382 条里只看了 top 5），重点找有 `write_file`/`create_file` 工具调用或附件产物的 session（build 型信号），而非纯 read/search。需逐条读 session 内容判断，成本高。
4. **接受 blocker，本 shard 转入 B-档 synthesized case 维护**（用 feint 等真实资产造 L2 题），A-档 faithful 暂停直到 daily scan 修好产出新数字 build session。

## 台账动作
78z8d / dse5n / nc938 / 65efs / f0qtv → claim→parked（covered 50 不变，parked 29→34）

## 本轮无 case 交付（DEBT: 0，rewrite_queue 全 done；本轮 0/30 断言达标，无新增 incomplete）
