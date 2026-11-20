# Deepread — 1793760248797_9sga3 (hswang@hfeg0plg94, mc58, physical_verify)

## trace 来源
- session: `1793760248797_9sga3.messages.json` (子目录 `1793760248797_9sga3/` 下)
- user: `hswang`  host: `hfeg0plg94` = 10.129.8.226  match_count: 58
- scan: `ssh_eda_search_20261116_072610`
- keywords: `synopsys:148;drc:138;netlist:126;lvs:50;.cdl:24;.gds:23;pex:12;analog:12`
- 106 msgs / 691 KB / 5 real user turns (U#0/U#38/U#39/U#52/U#58)
- deepread round: r659 (2026-11-16). DEBT 1 (fresh deepread, synthesis next round).

## 1. User Intent (verbatim, trace-faithful A-档)

**U#0 (primary task — 提出需求型)**:
> 你当前的工作目录是/proj/drcpa/V0/workdir/hswang/simulation/SPF，比较该目录下WrC10_shielding/D_WrC10.spf_RCC文件和WrC10/D_WrC10.spf_RCC文件的区别

= 比较 SPF RCC 模式 parasitic 提取文件 (WrC10_shielding vs WrC10, 有/无 power shielding)，识别结构差异。**physical_verify / PEX 分析 Q&A**（新标准下合法用户意图）。

**U#38**: 「可以从文件内容中看出哪个RCC」(追问识别标志)
**U#39**: 「可以从文件内容中看出哪个RCC文件添加了Power shielding吗」(聚焦 shielding 识别)
**U#52**: 「删除」(清理临时脚本)
**U#58**: 粘贴 C34578_152… 耦合电容数据块 (tREFI3P9 网的 RCC 耦合/对地电容行，要求分析该网)

## 2. 助手实际做了什么（工具链 + 关键产物）

1. **MSG#7 read_files** 读取两份 RCC 文件（路径 `/rundata/drcpa_sim/V0/simdir/finesim/workdir/hswang/simulation/SPF/WrC10_shielding/D_WrC10.spf_RCC` 与 `WrC10/D_WrC10.spf_RCC`）。
2. **MSG#9–33 editor** 写 4 个比较脚本：`compare_spf.py`(行数/diff)→`compare_spf_struct.py`(结构: *D_NET/*NET/C/Cg/RES 行计数)→`compare_spf_conn.py`(连接对 Counter)→`compare_spf_netidx.py`(net index 对比)。逐步从粗 diff 收敛到结构化指标。
3. **MSG#40 editor** 写 `compare_spf_shield.py`——专门识别 shielding：解析 RCC 中 ground reference net 出现频率 + 耦合衰减模式。
4. **MSG#47/49 read_files** 读 `star_cmd_RCC` + `lpe.config_pro`（StarRC 提取配置，确认 shielding 是 PEX config 层的选项）。
5. **MSG#52–87** 用户粘贴 tREFI3P9 网的耦合/对地电容原始数据；assistant 用 editor 分块写入 `refi_p1.txt`..`refi_p13.txt`（13 个数据块），覆盖该网全部 585 条耦合电容(C 行) + 20 条对地电容(Cg 行)。
   - 数据格式样例：
     - 耦合 `C34578_152 XI_R_RowCtrl.XI45.Detection_PassB:17 XI_R_RowCtrl.tREFI3P9:18 4.8559e-17`
     - 对地 `Cg34409_275 XI_R_RowCtrl.tREFI3P9:11 0 7.59385e-16`
6. **MSG#89–99 editor** 写 `analyze_refi.py`：glob refi_p*.txt → 正则解析 C/Cg 行 → 聚合统计（net_total from *|NET 声明、coupling count/sum、ground count/sum、按攻击者 net 聚合）。两次 bugfix：① *|NET 声明行未存入数据块 → net_total=None 容错；② 分组逻辑两端搞反 → 固定取"非 tREFI3P9 那端"作攻击者。
7. **MSG#101 cleanup_refi.py** 删临时数据文件。
8. **A#105 最终分析报告**（用户隐式接受，会话结束）：

| 项目 | 数值 | 占比 |
|---|---|---|
| 网络总电容(*\|NET 声明) | 0.0288347 PF ≈ 28.83 fF | 100% |
| 耦合电容(C) | 12.26 fF (585 条) | ~43% |
| 对地电容(Cg) | 15.85 fF (20 条) | ~55% |

## 3. gold 判定（会话内接受态）

- **核心交付** = `analyze_refi.py` 解析单网 RCC cap 数据 → 结构化统计（总/耦合/对地电容 count+sum + 攻击者聚合）。
- **接受态** = A#105 报告给出 tREFI3P9 网的 28.83fF/585C/20Cg/12.26fF/15.85fF，会话随后结束（用户无追问/否决 = 隐式接受）。
- **shielding 识别**（U#39）的答案：shielding 体现为 RCC 文件中 ground-reference 耦合占比升高 + 跨域长距离耦合被 shield net 截断（compare_spf_shield.py 的判定逻辑）。

## 4. 可造性判定（新标准 2026-11-15）

- **用户意图真实** ✓ (physical_verify PEX RCC 比较 + shielding 识别 = 真实后端任务)
- **gold 有牙** ✓ (analyze_refi.py 产出结构化数值，可断言 count/sum/balance/top-aggressor)
- **reframe 子型** = `spf-rcc-net-cap-structured-extract`（承 r630 LVS-report-extract / r631 ERC-deck-extract 模式，distinct vs r652=pex-batch-path-resolve / r657=3dlvs-gui-config）

## 5. 资产可达性（r659 实测） — r660 已交付；r674 重选重复已 revert

- **live RCC 文件** `/proj/drcpa/.../D_WrC10.spf_RCC`：ssh 10.129.8.226 以 e0031982 身份 → **Permission denied**（hswang 私有项目目录）。
- **trace 内含完整数据** ✓：assistant 的 editor tool_use（MSG#61–87）逐字保存了 refi_p1.txt..refi_p13.txt 的全部 C/Cg 行 + analyze_refi.py 源码（MSG#89 new_text）。**下轮从 trace tool_use input.new_text 提取**即可获得 grounded asset，无需 live 文件访问。
- **提取方式**：`python3` 遍历 msgs → 找 editor tool_use path=refi_p*.txt → 抽 input.new_text → 拼接成 asset A 的 RCC cap 数据文件。

## 6. 拟造 case 设计（下轮 r660 合成）

- **deliverable** = `spf_rcc_net_cap_analyzer.py <rcc_cap_data.txt> <output.json>`：解析单网 SPF RCC cap 行(C/Cg/*|NET) → 结构化 JSON
- **asset A** = tREFI3P9 网的真实 cap 数据（从 trace MSG#61–87 提取，~605 行）
- **hidden B** = 另一网（如 VPURSTDDT 或合成变体：不同 net_total/不同攻击者分布/不同 C:Cg 比例），结构同 A 取值不同
- **check() ≥8 条件 a-?**：①zip 含 1 文件 ②py_compile ③subprocess 跑 B ④net_total 标量 ⑤coupling_count ⑥coupling_sum(容差) ⑦ground_count ⑧ground_sum(容差) ⑨cap_balance(耦合/总 比例区间) ⑩top_aggressors list 非空 ⑪攻击者聚合 key 含 "XI_R_RowCtrl.XI45"/"XI_R_CBRCNTT_49" 等 ⑫确定性(双跑一致) ⑬anti-hardcode: B 的 net_total ≠ A 的
- **negative** = empty_shell / print_expected_A / core_deleted(去 Cg 解析) / naive_count_only(只数行不算 sum)
- **k 预估** = 13–15, ≥8 ✓

## 7. 台账状态
- r659 claim ✓ (ledger_C: 1793760248797_9sga3 status=claimed)
- **r660 已 mark case** ✓ `EDA-Eval-DesignFlow-SpfRccNetCapAnalyzer-001`（16 conds a-p, hidden B victim RowAddrCtrlB, DEBT cleared）
- **r674 重选重复 → REVERT**：r674 据 r659 deepread「claimed 待合成」视图重选 9sga3，未察觉 r660 已交付；构建 SpfRccNetCapExtract-001(20 conds, 更全) 后 review 命中「同 trace 同 visible-A 同任务」→ C.jsonl line 419 + reference/assets 全 revert(commit 8603317d9)，ledger 9sga3 → parked(duplicate-caught)。教训：选料须先 grep session 于 shard jsonl + ledger case 行双复核。
