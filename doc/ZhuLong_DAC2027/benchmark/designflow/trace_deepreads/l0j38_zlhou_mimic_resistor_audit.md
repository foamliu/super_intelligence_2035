# l0j38 deepread — zlhou@hfeg0plg15 (mc=142, schematic_netlist)

trace: 1795084563745_l0j38.messages.json, 838KB/143 msgs, 2026-11-19, agent=lead (zhulong)

## 真实意图
用户 zlhou 在 `/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/tiling/` 调试抽取网表
`CXN4HC2PS512X8M2B4C1R1W1BW1RE1_FS_420.netlist` 中 `HC2PFS_GCNTCEN_MIMIC` 子电路
的 **RDMIMIC 电阻丢失**问题：`RDMIMIC_END`/`RDMIMIC2GTP` 两节点间本应有电阻，
但抽取网表里没有。用户多次反驳 agent 的错误结论（resThrhd 阈值论、OA floating 论、
R0/R1 overlap 论），最终 agent 通过新旧 leafcell 网表版本对比 + 时间线（11-05 有电阻
→ 11-18 NEW 无 → 11-19 FS_420 无）定位真相，并按用户「怎么跑 erc」查 Aether Verify→Check ERC 步骤。

## agent 工具链（纯 Python 离线分析）
- grep_cx.py / scan_mimic.py / scan_rr.py / scan_log.py：grep 网表定位 GCNTCEN_MIMIC
  子电路、RDMIMIC_END/RDMIMIC2GTP 节点、电阻实例
- cmp_gcnt.py / diff_gcnt.py：新旧两版 leafcell 网表 subckt 对比（有/无电阻）
- oa_strings.py / oa_ctx.py / oa_verify.py：读 OA 二进制 sch.oa 找电阻实例与连接态
  （后发现 floating/overlap 是旧诊断残留文字，非实况）
- dates.py：网表文件时间线；sym_pins.py / oa_term.py：symbol 引脚 vs 网表节点
- grep_erc*.py：查 Aether 手册 ERC 入口

## 抽取内核（L1，不依赖 live EDA 沙箱）
**SPICE 网表子电路结构审计器**：
- parse_netlist → subckts {ports, instances[{name,dev_type,nets}]}
- has_device_between(sub, dev_type, net_a, net_b) → bool（测指定器件是否连两节点）
- floating_nets(sub) → list（端口未被任何实例用 / 内部节点出现在 <2 终端）
- instance_count_by_type(sub) → dict
- diff_subckts(old,new) → {added/removed _instances/_nets/_ports}

诊断「抽取网表丢了 mimic 电阻」= has_device_between(GCNT,'R',END,GTP)==False 而
LCNT==True；floating_nets 抓悬空尾节点；diff 抓版本间移除的器件/节点。

## case 化
- EDA-Eval-DesignFlow-NetlistMimicResistorAudit-001 (schematic_netlist, L1)
- A 可见：mimic_ref_A.netlist(有 R)+mimic_ref_A_new.netlist(无 R)+skill_spec.md
- B 隐藏（不进 SUT）：b1_audit(4 subckt,丢 R bug+floating)、b2_old/b2_new(diff)、
  b3_float(电阻单端悬空) — 名称/拓扑/取值与 A 结构性不相交
- k_check=13；自验 reference 13/13 PASS + 3 负样本全 FAIL
