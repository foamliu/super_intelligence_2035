# r1073 deepread — 1795067835708_imgh7 (thqu@hfeg0pkn004, mc=48)

## trace 概览
- session 1795067835708_imgh7 / 120 msgs / 515KB / agent=lead / 2026-11-20
- domain: spice_sim (FineSim 多 corner .alter deck + PEX/SPF 后仿 + mt0 收集 + netlist 调试)
- 工程根: `/proj/ddgoa/V0/workdir/thqu/SIM/Dlycell_T05/`
  - `Dlycell_trimTRCDvsTRPVbiasDly_R01/` (TRCD, 5 corner, tb1-8, 0.59-3.84 ns)
  - `Dlycell_trimTWRvsTRP/` (TWR, 5 corner, tb1-8, 0.59-0.95 ns)

## 用户任务清单（按 msg idx）
1. [0-7] Q&A: HSpice `.lib`/`.endl`/`.alter` 语义、换 corner、`.lib tt/ff` 节名联动
2. [8-32] Q&A + 验证: `.inc netlist_0405`（前仿 schematic）+ `.inc xxx.spf.TYP_98_RCC`（PEX 后仿 SPF）替换机制 — 结论: schematic 版 subckt 整段 `*` 注释掉, SPF 提供同名 subckt + 自带晶体管, 实现黑盒替换
3. [33-50] flow-driving: 替换 PEX SPF 路径 + 备份（策略只允许写 /home/thqu, 用户最终直接改 deck `.inc` 指向新 PEX 符号链接）
4. [51-66] env-config Q&A: LSF `bsub`/`bjobs`/`bswitch` 队列管理, `<<Waiting for dispatch>>` 含义, `bswitch` 参数顺序
5. [67-72] Q&A: `invGF` vs `invPF` 区别 (PMOS 接 VCCZ vs VCC, NMOS 接 VSS vs VSSZ), 两组电源网物理独立
6. [73-78, 99-110, 118-119] **deliverable**: 收集 `Result/dlycell.mt0.csv` 测量数据, 按工艺角对应, 单位 ns/ps, 算全局+per-corner min/max
7. [83-98] **debug-deliverable**: `Dlycell_trimTWRvsTRP` 仿真报 `WARNING! .tran keyword is not available in local (dlycell.sp:84)` + `ERROR! no analysis statement exists` → 根因: `netlist_1120` 有 66 个 `.SUBCKT` 但只 65 个 `.ENDS` — 第 1379 行 `.SUBCKT PreBnkCntrl_S` 头部**未注释**, 但 body (1380-1432) 全 `*` 注释, 第 1433 行 `*.ENDS PreBnkCntrl_S` 也被注释 → 未闭合的 subckt 把后续顶层实例 + `.tran` 全吞进 "子电路体内(local)" → no analysis。对比 TRCD 套 `netlist_0405` 正确写法: 连 `.SUBCKT` 头部一起整段注释。assistant 写 `_check_balance.py`（数 .SUBCKT/.ENDS 计数差）+ `_find_unclosed.py`（栈式精确定位未闭合 subckt）
8. [107-117] Q&A: 加 SPF 后 delay 变小原因 — schematic 手工估算电容(Cthin/CapO/Cgatein=0.4f)被更小的提取电容替代; SPF 统计 R=13540, C=34100, X=949, 总电容 ~441.8fF

## reframe 选择 → 任务 7 (unclosed .SUBCKT 诊断)
- 真实用户痛点: FineSim ".tran not available in local / no analysis statement" 是 SPICE 仿真常见 fatal, 根因常是某 `.SUBCKT` 缺 `.ENDS`
- 程序化: `subckt_unclosed_diag.py <netlist> <out_json>` — 解析 `.SUBCKT`/`.ENDS`（区分 active vs `*`-commented, 大小写不敏感, `.ENDS name` 命名匹配）, 栈式定位未闭合 subckt, 分类 pattern（`ends_commented` = 头部 active + 存在 `*.ENDS` 注释行; `missing_ends` = 完全无 .ENDS）, 输出结构化 JSON + verdict + recommendation
- L1 纯 Python, 无 EDA 依赖
- 真实数据两处语法脏数据（解析器须处理）: ① `.SUBCKT` 头部 active 但 body+`.ENDS` 全注释（netlist_1120 的 PreBnkCntrl_S 反模式）② 正确写法: 整段含头部全注释（netlist_0405）— 不能把注释头部误算为 active
- 与现有 B case 区别: DspfSubcktComment(modifier, 注释外层)/DupSubcktDefDiag(duplicate redef)/FineSimNoRefCktFix(missing ref) — 本 case = **unclosed/missing .ENDS**, 缺陷类独立

## case 设计
- **case_id**: EDA-Eval-DesignFlow-SubcktUnclosedDiagProduce-001
- **A** (真实结构采样, ~55 行): 3 个正确闭合 subckt(invPF/invGF/bufGFx2) + 1 个未闭合(PreBnkCntrl_S: 头部 active, body 全注释, `*.ENDS` 注释) + 顶层 .tran/.end — 复刻 netlist_1120 反模式
- **hidden B** (合成, 结构异 A): 5 个正确闭合 subckt(名异 A: Sa_dfe/RingOsc128/ddr5_leaf/Xtop_clkbuf/InvChain4) + **2 个未闭合 via `missing_ends` pattern**(Sa_dfe_X: 头部 active + 真实 X 实例 body + 完全无 .ENDS; RingOsc128_top: 头部 active + 真实 body + 无 .ENDS) — 反 A 的 1-unclosed/ends_commented 硬编
- **check.py 15 条** (a-o): zip+compile+size / B exit0+JSON / 顶层键⊇{total_active_subckt,total_active_ends,balanced,unclosed,verdict,recommendation} / balanced==False / len(unclosed)==2 / 每条 unclosed 含{name,start_line,pattern} / unclosed 名集合==B oracle(Sa_dfe_X+RingOsc128_top) / start_line==oracle(独立复算) / pattern 两条均=="missing_ends"(反 A ends_commented) / total_active_subckt==oracle / total_active_ends==oracle / verdict 含"unclosed"+FineSim error 签名 / recommendation 含".ENDS" / anti-hardcode(A 名 PreBnkCntrl_S 缺席 + A pattern ends_commented 不在 B unclosed 报告) / 3-seed sha256 一致
- **3 negs**: neg_empty(空壳→a/b) / neg_print_only(硬编 A 报告→e/f/g/h/i/j/k fail) / neg_count_only(只数计数差不下钻 unclosed→d/e/f/g fail)

## trace_source
- user=thqu, host=hfeg0pkn004, session_file=1795067835708_imgh7, match_count=48
- real_task_summary: FineSim Dlycell 多 corner 后仿; 调试 netlist_1120 未闭合 .SUBCKT(PreBnkCntrl_S 头部 active/ends 注释)致 .tran local/no analysis fatal; 写 _check_balance.py + _find_unclosed.py 精确定位
