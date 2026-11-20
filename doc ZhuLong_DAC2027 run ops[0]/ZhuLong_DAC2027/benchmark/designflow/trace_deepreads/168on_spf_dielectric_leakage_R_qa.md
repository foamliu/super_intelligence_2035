# 深读笔记 · 168on · SPF 介质漏电电阻分析 Q&A

> session: 1793698898572_168on · user: yh1yang · host: hfeg0pkn002 (10.129.2.11) · mc=22 · domain: schematic_netlist
> trace_source: yh1yang/hfeg0pkn002/1793698898572_168on.messages.json (30 msgs, 97KB)
> 深读轮: r780 (2026-11-16) · DEBT: 合成未完成，r781 首要任务

## 一、用户意图（A 档 verbatim prompt = M0）

```
/rundata/m2701/V0_DDR2/ver/pex/yh1yang/ROmulti/ROmulti.spf.TYP_98_RCC
- 这个后仿提取的网表里，是否会添加不同走线之间介质引起的漏电电阻呢，请帮我查看下，只需给出简单结论即可，而且不要修改到网表，只准查看
```

**任务形态**：analysis-Q&A（P-006 r618 CLOSED (C)-(A) 分流 · evidence-verification 模式）。
用户要「简单结论」+「只准查看」⇒ 交付物 = 结构化结论报告（JSON），不是脚本，不是改网表。
A 档选轮规则：M0 是「提出需求」轮（✅），M28 是「用户已给假设」轮（❌ 不作 prompt，可作 hint 不进 prompt）。

## 二、金标准（trace 末尾用户实际接受的结果 = M27 assistant 结论）

用户 M0 问「是否添加不同走线之间介质引起的漏电电阻」，assistant 用 Python 解析 SPF（StarRC DSPF 1.3）后给结论：

**结论：没有添加不同走线之间介质引起的漏电电阻。**

依据（M26 run_approved_command stdout，assistant 自写 analyze_spf2.py 统计）：
- 文件格式：DSPF 1.3，StarRC R-2020.09-SP5，corner TYP_98，温度 98°C
- net sections: **203**
- non-comment element lines: **48181**
- **电阻 R\* 共 13439 个**：
  - to ground(0): **0**
  - via instance pin（同 net 内部互连串联 R，如 MOS GATE 引脚到 net 子节点）: **2280**
  - between two genuinely DIFFERENT nets（neither pin）: **0** ← 关键证据
  - 样本：`R: XI_switch4.XI_t2<0>.MNM0:GATE <-> c<1>:25 = 92.8558`（同 net 互连 R）
- **电容 C\* 共 34064 个**：
  - ground caps (.. 0 ..): **4481**
  - coupling caps across DIFFERENT nets: **29370**（如 `vbulkn! <-> c<1>`）← 走线间耦合是纯电容
- 走线间介质耦合 = 纯电容，未并联漏电电阻；无到地/衬底漏电电阻（ground R = 0）

assistant 结论原文（M27）：
> 这个后仿提取的网表（DSPF/SPF）里，【没有】添加"不同走线之间介质引起的漏电电阻"。
> 电阻元件共 13439 个：全部是单根线网内部的金属/过孔串联寄生电阻。
> 没有任何一个电阻是连接两条不同走线（不同 net）的：数量为 0（排除器件引脚后）。
> 不同走线之间的耦合全部用理想耦合电容（C）建模：跨 net 耦合电容约 28755 个，没有并联对应小电阻。
> 走线间介质耦合体现为纯电容，未引入漏电电阻。

## 三、资产可达性（关键约束 · P-005 第八型）

资产 A = `/rundata/m2701/V0_DDR2/ver/pex/yh1yang/ROmulti/ROmulti.spf.TYP_98_RCC`
- r780 实测：e0031982（沙盒 ssh 身份）`ls/grep` 该文件 = **Permission denied**
  （/rundata/m2701 归 m2701 组；yh1yang ∈ m2701w 组可读，e0031982 不可读）
- 即 yh1yang 在 cline 内能读（trace M5/M26 实证），但 benchmark 造题 agent（e0031982 身份）读不到原文件
- ⇒ **asset_fidelity = synth_deck**（P-005 r519 CLOSED 第八型）：合成一份结构等价的 DSPF 文件作资产 A，
  复现真实统计（203 nets / 13439 R / 0 cross-net R / 0 ground R / 2280 pin-R / 34064 C / 29370 coupling C）
  + 真实样本行（`XI_switch4.XI_t2<0>.MNM0:GATE <-> c<1>:25 = 92.8558` 等）
- 合成可行性：DSPF 是文本格式（`*|NET <name>` 节 + `R/C <name> <node1> <node2> <val>` 行），
  Python 脚本可参数化生成 N nets × M R/C 元件，控制 cross-net R 计数（A=0, B>0）⇒ 满足 §4.1「check 只跑 B」+ §4.2 subprocess + §4.9 anti-hardcode

## 四、B 变体策略（隐藏输入 B · anti-hardcode）

B = 合成另一份 DSPF，**结构相反**：含跨 net 漏电电阻（dielectric leakage R between different nets）。
- A: cross-net R = 0（结论 = 无漏电电阻）
- B: cross-net R = K（K≥3，结论 = 有漏电电阻）+ 不同的 net 数 / R 总数 / C 总数 / pin-R 数
- agent 只见 A，check() 跑候选 analyzer 于 B：若候选硬编 A 的「cross-net R=0」结论，在 B 上 FAIL（B 有 cross-net R）
- 8+ anti-hardcode 维度全异：net_count / R_total / cross_net_R / ground_R / pin_R / coupling_C / ground_C / sample_R_value

## 五、check() 断言计划（≥8 独立条件 · k_rationale == k_check ≥ 8 · ①②… 标号）

交付物 = `spf_leakage_report.json`（候选 analyzer 跑在 A 上产的结论报告）。
check() 解 JSON + 独立复算 A 的统计 + 跑候选 analyzer 于 B 验证泛化：

① zip 含 spf_leakage_report.json + analyzer 脚本（py_compile pass）
② report.dielectric_leakage_R_present == false（A 的正确结论）
③ report.R_total == 13439（A 的 R 总数，容差 ±0）
④ report.cross_net_R_count == 0（关键证据：跨 net R = 0）
⑤ report.ground_R_count == 0（到地漏电 R = 0）
⑥ report.coupling_cap_count > 0 且 == 29370（跨 net 耦合电容存在，证明走线间耦合是电容性）
⑦ report.instance_pin_R_count == 2280（同 net 互连串联 R 计数）
⑧ report.net_sections == 203（net 数）
⑨ evidence-verification：report 须含 ≥1 个具体 R 元件样本（如 `XI_switch4.XI_t2<0>.MNM0:GATE <-> c<1>:25 = 92.8558`），check() 独立 grep A 输入验证该样本行真实存在（fabricated evidence FAIL）
⑩ cross-input guard（B judge-self-check）：check() 跑候选 analyzer 于 hidden B，断言 B 的结论 == true（B 有 cross-net R），且 B 的 cross_net_R_count ≥ 3（agent 硬编 A 的「cross-net R=0」在 B 上 FAIL）
⑪ anti-stub：空壳 / 只 print 期望串 / 删核心 三假提交全 FAIL（空壳→①/②，print_only→⑩ B 上结论错，删核心→④/⑥）
⑫ 确定性：3 seed 重跑候选 analyzer 于 A，结论 + 8 统计字段全一致

k_check = 12 ≥ 8 ✓。test_rationale = `12 条断言：① zip+py_compile ② dielectric_leakage_R_present=false ③ R_total=13439 ④ cross_net_R_count=0 ⑤ ground_R_count=0 ⑥ coupling_cap_count=29370 ⑦ instance_pin_R_count=2280 ⑧ net_sections=203 ⑨ evidence R 样本可核验 ⑩ B judge-self-check cross_net_R≥3 ⑪ 三假全 FAIL ⑫ 3-seed 确定性`

## 六、合成 checklist（r781 首要）

- [ ] 写 `gen_dspf.py`：参数化合成 DSPF A（203 nets, 13439 R 全 same-net, 0 cross-net R, 34064 C 含 29370 coupling）+ B（不同 net 数, 含 K≥3 cross-net R, 结论=true）
- [ ] assets/EDA-Eval-DesignFlow-SpfDielectricLeakageQA-001/ROmulti.spf.TYP_98_RCC (A) + hidden/ROmulti.spf.SS_40_RCC (B) + hidden_manifest.json
- [ ] reference/spf_leakage_analyzer_ref.py（解 DSPF，产 spf_leakage_report.json）+ reference_submit.zip
- [ ] reference/check.py（12 条断言 a-l）+ negative/（4 negs: empty / print_only / deleted_core / naive_wrong_count）+ negative_selftest.py
- [ ] 自验：ref 12/12 PASS + 4 neg FAIL + §4.9 三假 FAIL + 3-seed 确定性
- [ ] 追加 EDA-Eval-DesignFlow_D.jsonl + ledger mark --status case
