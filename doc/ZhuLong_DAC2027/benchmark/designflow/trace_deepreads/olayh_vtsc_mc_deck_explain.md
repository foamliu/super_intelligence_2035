# Deepread — 1792732271802_olayh (junweix@hfeg0pkn002, mc21, spice_sim)

## trace 来源
- session: `1792732271802_olayh.messages.json` (子目录 `1792732271802_olayh/` 下)
- user: `junweix`  host: `hfeg0pkn002`  match_count: 21
- scan: `ssh_eda_search_20261115_081559`
- 13 msgs / 52.8KB

## 用户真实意图
用户 junweix 在 cline 中依次给出 **3 个 SPICE 网表文件路径**，每个都只贴路径（`<user_input mode="act">…path…</user_input>`），不附加具体问题。意图是让 agent **读文件并讲解这些仿真网表到底在做什么**。这是典型的 explain/介绍 Q&A 任务（无 produce 交付物需求）。

三条路径：
1. `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/hanhu/ddgoa/1_VtscRef_pre/9_shift.sp` — Vtsc 参考电压 shift（PWM 移位补偿）瞬态仿真
2. `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/junweix/ddgoa/0_VtscAct_pre/2_mc_iload.sp` — Vtsc Active 电路带载（2.5mA）蒙特卡洛瞬态仿真 ← **本 case 选此条**
3. `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/junweix/ddgoa/0_VtscAct_pre/2_mc.sp` — Vtsc Active 电路空载（iload=0）蒙特卡洛瞬态仿真（与 #2 配对算负载调整率）

## agent 工具链
每条：`read_files`（读 .sp）+ `list_allowed_files`（列目录）。无 produce 操作。3 个文件全部成功读取并产出结构化讲解。

## #2 网表（2_mc_iload.sp）结构 — agent 逐字引用的 SPICE 行
- `.inc './Setting.sp'`
- 电源参数：`pvdd1=1.8` `pvcc=1.05` `pvss=0` `pvwlp=2.95` `pvtsc=1.17` `pvdleq=1.17`
- `.param iload=2.5m`
- 电源/控制 vsource：`vvdd1 vdd1! 0 pvdd1` … `vvtscref vtscref 0 pvtsc`
- 控制信号全 DC 高：`vpwronlsvdd1`/`vpwron3`/`vpwronlsvccp`/`vpwronrst`/`vvtrlen ctrlen`
- 负载电流源：`ivtsc vtsc! 0 iload`（2.5mA 灌入 vtsc!）
- 差分输入短接共模：`v123 fbin fbout 0` `vcmrr inb ina 0`
- 激励：`.tran 100p 10u sweep monte=100`
- 分析：`.dcmatch v(vtsc!) THRESHOLD=1`
- 测量：`.meas tran vload avg v(vtsc!) from 2u to 10u`
- 角点：`.param mis_flag=1`
- `.end`

## 仿真意图（agent 总结，正确）
Vtsc Active 缓冲器/稳压器在 2.5mA 负载下的**负载调整率蒙特卡洛仿真**：100 样本统计 v(vtsc!) 的均值 μ 与标准差 σ，评估大负载下的匹配性能。与 2_mc.sp（空载）配对 → LoadReg = (Vunload − Vload)/2.5mA。

## case 合成决策
- **form**: explain/介绍 Q&A → 产出生成式结构化讲解报告
- **A 档 trace-faithful**：A 网表 `doc/mc_iload.sp` 由 trace 中 agent 逐字引用的 SPICE 行重建（原始文件权限受限，junweix 所有不可直读；trace 引用即真值）
- **hidden B cross-input guard**：合成 Bandgap Vref MC 网表（不同电路/电源/参数/负载/monte/测量/信号），单源 `_gen_B.py` 产 B 输入 + `_gt_B.json`
- **判分牙**：check.py 独立解析 B 网表，对账 25 条断言（top_function/line_count/power_domains/parameters/voltage_sources/current_sources/shorted_pairs/stimulus/analyses/measurements 全 cross-input + A-leak 守卫 + cross-input 在 A 上 top_function==VtscAct LoadReg MC + 确定性 3 rerun + 4 假提交回归）
- **k_check == k_rationale == 25**
- 自验: ref 25/25 PASS + 4 negs(空壳/print-only/hardcode-A/deleted-core)全 FAIL

## 台账
`mark olayh -> case EDA-Eval-DesignFlow-VtscMcDeckExplain-001`（r676）
