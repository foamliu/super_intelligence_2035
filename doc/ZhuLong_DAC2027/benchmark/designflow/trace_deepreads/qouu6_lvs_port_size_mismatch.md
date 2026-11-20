# Deepread: 1794538451505_qouu6 — LVS port-size mismatch diagnostic

- **session**: 1794538451505_qouu6
- **user**: ethanw
- **host**: hfhds201 (10.129.32.75)
- **mc**: 9536 (lvs:6025 dominant)
- **domain**: physical_verify
- **trace size**: 4438 bytes, 1 user msg, 0 assistant msg (no gold)
- **claimed**: r888 (revived from r887 parked)

## 用户真实意图（逐字原文）

```
Netlist_SpfBA_20261112PM_BCenterCA_BCenterDLL_BCenterDQ_BnkGTop/netlist,
Netlist_SpfBA_20261111PM_BCenterCA_BCenterDLL_BCenterDQ_BnkGTop/netlist
ERROR! port size mismatch between xi0(268) and d_prcm6abus1400r(348)
ERROR! port size mismatch between xi0(220) and d_prcm6abusdn1400r(284)
Please help me figure out why...
```

用户跑了两个版本（20261112 vs 20261111）的 netlist 做 LVS 比对，遇到 port size mismatch 报错（xi0 的 port 268/220 位 vs d_prcm6abus1400r/d_prcm6abusdn1400r 的 348/284 位），想知道为什么——怀疑改版改了 bus 宽度。

## trace 结构

- 仅 1 条 user msg（`<user_input mode="act">`），无 assistant 回复，无工具调用。
- system_prompt 是 zhulong 通用 agent prompt（非 EDA 专用）。
- 无 gold answer → reframe 需合成 gold。

## reframe 决策（档 B · L1-static-parse）

真实意图 = 把 LVS ERROR 行结构化（哪个 instance、哪两个 netlist、port 宽度差多少、最大差值是谁）。
统一为单一 produce-task：写 `parse_lvs_mismatch.py` 解析 LVS run report → JSON 诊断报告。

grounding 零损耗：
- 保留真实 ERROR 行格式 `ERROR! port size mismatch between <inst>(<n>) and <inst>(<n>)`
- 保留真实 netlist 路径（Netlist_SpfBA_20261112PM_BCenterCA_BCenterDLL_BCenterDQ_BnkGTop/netlist）
- 保留真实 instance 名（xi0 / d_prcm6abus1400r / d_prcm6abusdn1400r）和真实 port 宽度（268/348/220/284）作 visible A

隐藏 B（嵌 check.py）：不同 netlist 路径（runs/drc_run_20261110/top_chip_netlist）、不同 instance 名（u1/data_bus_a/data_bus_b/u2/ctrl_bus）、不同 port 宽度（512/640/384/448/128/96）、不同 ERROR 行数（3 vs 2）→ 硬编 A 答案必 fail B。

## 意图审计判定

**keep** — ethanw 真实意图（诊断 LVS port size mismatch 根因）完整保留。reframe 把单轮 Q&A 统一为 produce-task（LVS run report → JSON 诊断报告），逻辑零加难、零删减，纯 grounding。U#0 用户原话摘要入 prompt。physical_verify LVS port-size mismatch 诊断子型（与 SVRF/GDS 套件、StarRC RCC 存储生命周期 r887、layout_aether hierarchy/DRC testpattern 套件、pg_layout dont_touch r885 正交）。
