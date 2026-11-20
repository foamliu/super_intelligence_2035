# 深读笔记 · 9sga3 · hswang · SPF RCC 结构差异 + Power Shielding 判定

> trace: 1793760248797_9sga3 · user hswang @ hfeg0plg94 · mc=58 · domain **analog_context**
> 沙盒路径: `/home/hswang/.cline/data/sessions/1793760248797_9sga3/1793760248797_9sga3.messages.json` (691KB / 106 msgs / 5 user turns)
> 资产可达性: ❌ 真实 SPF_RCC 在 `/proj/drcpa/V0/workdir/hswang/simulation/SPF/{WrC10_shielding,WrC10}/lpe/D_WrC10/D_WrC10.spf_RCC`（Permission denied，私有 /proj）⇒ **B-grade synthesized**（D 域资产可达性枯竭第三模式实证，r514 P-002 @D 已表态）
> 台账: ledger_D 9sga3 claimed (analog_context)；w4596 误 claim→parked；sao7s task-family dup→parked

---

## 1. 用户原文（5 轮，逐字）

**U0**：「你当前的工作目录是/proj/drcpa/V0/workdir/hswang/simulation/SPF，比较该目录下WrC10_shielding/D_WrC10.spf_RCC文件和WrC10/D_WrC10.spf_RCC文件的区别」

**U38**：「可以从文件内容中看出哪个RCC」（截断）

**U39**：「可以从文件内容中看出哪个RCC文件添加了Power shielding吗」

**U52**：「删除」（清理助手临时脚本，非产）

**U58**：（粘贴 ~49KB 网表片段：`XI_R_RowCtrl.tREFI3P9` 网络的 R/C/Cg 耦合电容段，来自另一个设计 "RCC 文件 1"）—— 这是**第二个独立子任务**（单网耦合分析），与 Task A 不同机制，本轮**不取**，留作备选。

## 2. 助手金标准（两条核心产出）

### 金标准 #1（A37）：SPF_RCC 结构差异报告
- **文件基本信息**：两文件均为符号链接 → 各自 `lpe/D_WrC10/D_WrC10.spf_RCC`；同设计 `D_WrC10`、同 `.SUBCKT` 端口 `CA10WrD CA10WrN In WrLatDHL WrLatDLL vbn! vbp! vcc! vss!`、同工具 StarRC R-2020.09-SP5；仅 `*DATE` 不同（17:07 vs 17:44）、文件大小 78734 vs 77965、数据行 1178 vs 1159。
- **元件计数**：shielding=818（R=326, C=492）；baseline=799（R=327, C=472）⇒ shielding 多 20 电容、少 1 电阻、共多 19 元件。
- **结构性差异**（按**元件连接节点对**而非编号对比，因编号有索引移位）集中在内部差分写锁存网络 **net5/net6/net7/net8** 的 RC 网格：
  - net7（shielding idx16 / baseline idx11）：53 vs 48 元件；shielding 分 16 个 RC 子节点（net7:11…16），baseline 15 个。
  - net5（idx22）：54 vs 56；baseline 多 1 RC 子节点 net5:15（多 1 电阻）。
  - net8（idx23）：241 vs 230；shielding **多 11 电容**。
  - net6（idx24）：233 vs 228；shielding **多 5 电容**。
  - 新增电容主要是 net5/6/7/8 之间的**互耦合电容**（如 net6:31↔net5:12/13、net8:31↔net5:12/13、net6:33↔net7:12）+ 部分新增对地 Cg。
- **数值差异**：共有元件值差 0.1%–0.5%（重复抽取波动）；逐网络总电容对比（PF）：In 0.00100951→0.00100853、CA10WrD 0.54783→0.54661、CA10WrN 0.54996→0.54971、net5 0.082532→0.081690、net7 0.073673→0.077843（shielding 较小）、net6 0.004796→0.004724、net8 0.004799→0.004700、WrLatDHL 0.00333234→0.0033314、WrLatDLL 0.0033421→0.00334311。

### 金标准 #2（A51）：Power Shielding 判定
**结论：不能；两份实际上都没有配置电源屏蔽，"shielding" 仅来自文件夹名。** 依据四点：
1. **SPF 正文无屏蔽标记**：全文检索两份 spf_RCC 仅出现 `GROUND_NET 0`，无 `shield/power/option` 关键字；头部除 `*DATE` 外逐字相同；.SUBCKT 端口/TCAD/工具版本全同；power 网 vcc!/vss! 元件行数一致（各 44）；对地电容 Cg 数量一致（各 160）。
2. **StarRC 命令与配置完全一致**：`star_cmd_RCC` / `lpe.config_pro` 逐行相同——`POWER_EXTRACT: DEVICE_LAYERS/LRSD`、`POWER_NETS` 同列表、`COUPLE_TO_GROUND: NO`、`REDUCTION: YES`、`COUPLING_ABS_THRESHOLD: 1e-17`、`mode=RCC`、`Temperature=98`、`CORNER=TYP`；无任何 SHIELD/Shield 选项。
3. **唯一实质差异是输入版图版本**：`lpe.config_pro` 仅 CDL/GDS 路径不同（`D_WrC10.cdl`/`.gds` vs `D_WrC10_1.cdl`/`.gds`）+ 运行主机/时间不同（hfeg0pgn012/17:07 vs hfeg0pgn013/17:44）。RC 差异来自不同输入版图 + 独立抽取，非抽取选项。
4. **电学特征不符屏蔽**：真 power shielding 典型表现 = 被屏蔽信号网**对 vcc/vss 电容增加、对其它信号网耦合减小**；实际相反——shielding 版多 20 个**信号间耦合电容**，对地电容/power 网处理与另一版完全一致。 ⇒ **判定逻辑**：shielding verdict = (SPF 正文有无 shield 关键字) AND (抽取配置 star_cmd/lpe.config 有无 SHIELD 选项) AND (电学签名：被屏蔽网对地电容↑+耦合↓)；三者皆无 ⇒ verdict="indeterminate / neither file has power shielding configured"。

## 3. SPF_RCC 格式（StarRC RCC 模式 DSPF-like，从助手分析归纳）

```
*DATE 2026-11-03 17:07:42
*RC RCC
*.GROUND_NET 0
.SUBCKT D_WrC10 CA10WrD CA10WrN In WrLatDHL WrLatDLL vbn! vbp! vcc! vss!
*|NET <name> <total_cap>PF
*|R<Rid> <net:node1> <net:node2> <resistance>
*|C<Cid> <net:node1> <net:node2> <capacitance>
*|CG<gCid> <net:node> 0 <capacitance>      # 对地电容（GROUND_NET 0）
.ENDS
```
- net 名可带层级前缀（`XI_R_RowCtrl.XI45.net60:11`），`:` 后为 RC 子节点索引。
- 元件 id（R/C/Cg + 全局编号）有**索引移位**——同物理电容可能编号不同 ⇒ 必须**按 (node1,node2) 连接对**对比，不能按 id。
- 耦合电容 C = 两信号网之间；对地电容 Cg = 信号到 GROUND_NET 0。

## 4. B-grade 合成设计（草案 · 下轮 #516 交付）

**case id**: `EDA-Eval-DesignFlow-SpfRccShieldDiff-001`（analog_context, B-grade synthesized L2, k≥12）

**真实任务机制**：读两份 SPF_RCC，输出结构化差异报告 + power-shielding 判定。

**资产 A（SUT 可见）**：`spf_A_shielding.spf_RCC` + `spf_A_baseline.spf_RCC`（合成小 SPF，同 .SUBCKT 端口 `DqA DqNA InA LatAHL LatALL vbn! vbp! vcc! vss!`，~40-60 nets）：
- A_shielding：多 8 个信号间耦合电容（netA5/6/7/8 之间），少 1 电阻；Cg 数与 baseline 同；无 shield 关键字；*DATE 不同。
- A_baseline：参照。
- `example_report_A.json`：金标准报告（element counts、per-net deltas、coupling-cap delta、total-cap-per-net、shielding_verdict="neither" + evidence）。

**资产 B（hidden）**：`spf_B_shielding.spf_RCC` + `spf_B_baseline.spf_RCC`（不同 net 名前缀 `DqB/DqBNA/netB…`、不同 .SUBCKT 名 `D_WrC10_B`、不同元件数差：shielding 多 12 耦合电容、不同 net 集合 netB3/B9/B11）+ `example_report_B.json`。check.py 只跑 B。
- **关键变体**：B 中植入一个**真 shielding 签名**子集——某 netB3 在 shielding 版对地 Cg 显著↑（+若干 Cg）且对邻网耦合↓，但 SPF 正文仍无 "shield" 关键字、配置仍无 SHIELD 选项 ⇒ 期望 verdict 仍为 "neither/indeterminate"（因判定要求三者，电学签名单独不足以断定 shielding，需关键字或配置）—— **测试 SUT 是否会因电学签名就误判 shielding**（抗过度推断）。

**资产 C（anti-hardcode，嵌入 check.py）**：`spf_C_shielding.spf_RCC` + `spf_C_baseline.spf_RCC`（netC 前缀、.SUBCKT `D_WrC10_C`、SUT 未见过），check.py 跨输入跑 C 验证 SUT 无 B 字面量硬编码。

A/B/C net 名前缀（netA/netB/netC）+ .SUBCKT 名 + 端口名 + 元件 id 空间完全不相交 ⇒ 反硬编码。

**SUT**: `spf_rcc_shield_diff.py <spf_shielding> <spf_baseline> --out <report.json>`，纯 stdlib（禁 numpy/pandas/scipy/subprocess/socket/urllib/requests/calibre/pyaether/aether/eval/exec + 禁 B 字面量 netB/D_WrC10_B/DqB）。输出 JSON：
```
{design, subckt_ports, shielding:{file,date,size_bytes,data_lines,elem_count,r_count,c_count,cg_count},
 baseline:{...}, 
 elem_delta:{total, r_delta, c_delta, cg_delta},
 per_net_elem:{net: {shielding_n, baseline_n, delta}},
 per_net_total_cap:{net: {shielding_pf, baseline_pf, delta_pf}},
 coupling_cap_delta:{extra_in_shielding: n, extra_in_baseline: m},
 shielding_verdict: "neither"|"indeterminate"|"file_a"|"file_b",
 verdict_evidence: {spf_has_shield_keyword: bool, config_has_shield_option: bool, electrical_signature: "present"|"absent"|"mixed", reason: "..."}}
```

**check.py 条件草案（≥12，独立 oracle = 重新解析 SPF，与 SUT 实现结构不同：SUT 用 split/状态机，check 用 regex-findall + dict）**：
- a. zip 含 SUT 脚本 + 无禁 import/eval/exec + 无 B 字面量 + 无 check/reference/negative/hidden/jsonl 泄漏
- b. py_compile SUT 通过
- c. B 运行 subprocess 退出 0 + 产出 report.json + 顶层键齐全
- d. shielding/baseline 元件计数 == oracle（r/c/cg 分别精确）
- e. elem_delta.total / r_delta / c_delta / cg_delta == oracle
- f. per_net_elem：逐 net 元件数 delta == oracle（重点 netB3/B9/B11）
- g. per_net_total_cap：逐 net 总电容 == oracle（1e-15 PF 容差）—— **核心数值条件**
- h. coupling_cap_delta.extra_in_shielding == oracle（按 (node1,node2) 连接对集合差，非 id）
- i. shielding_verdict == "neither"（或 "indeterminate"）—— **核心判定条件**：B 中电学签名 present 但关键字/配置皆无 ⇒ 必须不为 "file_a"/"file_b"
- j. verdict_evidence.spf_has_shield_keyword == False（B 两份 SPF 正文确无 shield 关键字）
- k. verdict_evidence.electrical_signature 合理描述（Cg 对地↑ + 耦合↓ ⇒ "present"，否则 "absent"）
- l. 反硬编码：C 跨输入运行，结果与 oracle 一致（C net 名 SUT 未见过）
- m. 3-seed sha256 确定性（dict 排序 + 数值格式化稳定）

**negative（≥3）**：empty_zip / print_only（print 期望 verdict 串但无解析）/ hardcode_B（直接 return B 的 example_report）—— 全 FAIL。
**§4.9 三假**：(a) 空壳 (b) 只 print 期望串 (c) 参考解删核心（删 per-net total_cap 计算）—— 全 FAIL。

## 5. 维度正交性（vs 既有 D case，非重复）

| 既有 case | 机制 | 与本 case 区别 |
|---|---|---|
| SPFNetlistCompare-001 (rongtaoy, schematic_netlist) | SPF 网表对比 | 本 case 是 **RCC 提取产物**（R/C/Cg 元件 + 耦合电容）对比 + **shielding 判定**，非 netlist 端口/连接对比；且 user 不同（hswang vs rongtaoy） |
| NetRcPathDiff-001 (yazhuok, schematic_netlist) | Net RC 路径 diff | 本 case 是**全文件元件计数 + 逐网总电容 + shielding 电学签名**，非单条 RC 路径 |
| SpfCapResAnomaly-001 (zongjiuh, analog_context) | SPF net cap + 电阻段求和 + 异常检测 | 本 case 是**两文件对比**（非单文件统计）+ **shielding 判定逻辑**（关键字/配置/电学签名三因素） |
| CouplingPivotStats-001 (#504) | SPF 耦合 CSV 透视 | 本 case 是 RCC 元件级结构 diff，非耦合矩阵透视 |
| SpfResPathTrace-001 (#506) | SPF 电阻路径 Dijkstra | 完全不同机制 |

⇒ **非 dup**：user hswang 在 D.jsonl=0；task family "SPF RCC two-file diff + shielding verdict" 无既有；机制（连接对集合差 + 三因素 shielding 判定）独特。

## 6. 选料方法论（本轮踩坑）

- D-score 排序的**高 mc verilog-heavy** 候选多为 **analysis Q&A / code-comprehension**（"分析下...如何实现"、"告诉我...应该如何改写"），非 produce task：eb49z(chuanqiz 7 uturns 全分析)、swhjl(stevenh 1 uturn "告诉我如何改写")、xinm9(e0025522 菜单"启动业务场景")、bg11w(congyi 后台任务排查)、bp54q(mwxi crontab)、i73zm(eric1ch 找 case+Q&A)、p28m8(e0017484 菜单)、54h58(e0044455 菜单)、3anqw(e0025730 /lvlshft skill)、kkzyd(cliu skill@ sim)、0h2bc(davidwu floorplan layout=C 域)。
- **可用判据**：user turn 含产运动词（比较/解析+输出/生成/提取）+ deliverable 形态明确（报告/文件/JSON）+ 非 /proj 私有或可合成。9sga3(hswang) "比较...区别" + "可以从文件内容看出哪个 RCC 添加了 Power shielding 吗" = 产运动词 + 明确 deliverable（差异报告 + 判定）⇒ 命中。
- **task-family dup 陷阱**：sao7s(yanxvwei compare_wave_new.pl/find_best_shift) = ShiftIntervalReport-001(yanxvwei 同脚本同函数) 的 dup ⇒ peek 阶段必须 grep 现有 case 的 `trace_source.user` + 关键资产名（脚本/函数），不止 session-id。本轮 sao7s peek 完成才暴露 dup（浪费 ~3 min），下轮 peek 前先 grep user。
- **awk 巨型 excl regex 不可用**：ledger `next` 生成的 inline excl regex（~30KB，含 2465 anchors）在 .75 awk 命令行长度限制内不可靠 ⇒ 本轮改用「.75 跑小 awk 取全量 mc≥10 D-keyword 候选 → return_files 取回 → 本机 4-ledger 排除」三步，稳。下轮复用此法（_tmp_fresh.tsv 已存 592 fresh 候选，可直接挑下一个）。

## 7. 下轮 #516 偿还计划

1. 复用本深读笔记 → 合成 SpfRccShieldDiff-001（A/B/C SPF_RCC + SUT + check.py 12+ 条件 + 3 negative + §4.9 三假）。
2. 自验：ref PASS 12+/12+ + 3 neg 全 FAIL + §4.9 三假全 REJECTED + 3-seed sha256 一致。
3. pre-append dup-check（user hswang=0 + SpfRccShieldDiff task family 无 + 9sga3 session 无）⇒ 非 dup。
4. 追加 D.jsonl 322→323 (analog_context 74→75) + ledger_D 9sga3 mark case + 断言 k_rationale==k_check≥12 + MEMORY DEBT 1→0。
