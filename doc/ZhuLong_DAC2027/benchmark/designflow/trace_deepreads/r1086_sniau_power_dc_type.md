# r1086 deepread — sniau Power Supply DC Type Generator

**session**: 1795137081100_sniau (junlingw @ hfeg0pkn005, mc=193, 755 msgs / 2.4MB)
**scan**: ssh_eda_search_20261123_064315
**domain**: spice_sim (B shard)
**fresh check**: cross-4-shard-ledger 全 NONE (sniau 不在 trace_ledger_B.tsv)

## 会话概述
junlingw 继续开发 GENGUI（FineSim testbench tkinter GUI 生成器，/proj/drvqa/V0/workdir/junlingw/GENGUI/）。同 y9bh6 (r1074 CornerBlockGenProduce-001) / 7q6sq (r1082 McVariationBlockGenProduce-001) 是同一项目的不同 session，但本 session 覆盖不同 topic。

## 选题 msg 616-636：Power 页 DC 类型下拉
- **msg 616**: 用户要求 power 的值改为三种 point/list/range，做成下拉选项栏放在输入值之前
- **msg 618**: 用户明确语义：point=单值→`dc=1.1`；list=多个值→`dc=1.1 1.8 2.5`；range=起-止-步→`dc=1 2 0.1`（都是 DC 值写法）
- **msg 619-636**: assistant 改 finesim_tb_generator.py 的 _tpw (Power tab) + _col (collect) + _supply_dlg (Add/Edit 对话框)：表格加 Type 列(point/list/range)、下拉放 DC 值之前、引擎拼 `dc=`+值。msg 635 实测 3 种 type 输出正确。

## 实测输出 (msg 635)
```
* === POWER ===
VDD_SRC VDD_src 0 dc=1.1
R_VDD_SRC VDD_src VDD 10m
VNL_SRC VNL_src 0 dc=1.1 1.8 2.5
R_VNL_SRC VNL_src VNL 10m
VRA_SRC VRA_src 0 dc=1 2 0.1
R_VRA_SRC VRA_src VRA 1m
```

## 命名约定 (trace 观察)
- 电压源实例名 = spec name (已含 V 前缀，如 VDD_SRC)
- 正端节点 src_node = name 按最后一个 `_` 拆分，后缀小写：VDD_SRC→VDD_src
- 串阻实例名 = R_+name (如 R_VDD_SRC)，接在 src_node 与 net 之间，阻值 r

## reframe
`power_supply_dc_gen.py <spec.json> <out.txt>` 纯 Python 标准库 L1：
- 读 spec {header_text, include_header, supplies:[{name,type,dc,net,r}]}
- type ∈ {point,list,range}，校验 dc token 数：point=1, list≥2, range=3 (全 numeric)
- src_node = prefix + "_" + suffix.lower()
- 输出 header + 每supply两行 (`<name> <src_node> 0 dc=<dc>` / `R_<name> <src_node> <net> <r>`)
- exit: 0 ok / 2 argcount / 3 spec unreadable / 4 validation error

## near-dup 自查
- CornerBlockGenProduce-001 (corner .lib/.alter/.temp/.param vvdd) — 不同 topic ✓
- McVariationBlockGenProduce-001 (.variation mismatch/CCO) — 不同 topic ✓
- ProbeBlockProduce-001 (.probe 块) — 不同 ✓
- SpTemplatePvtGroupRender-001 (SP 模板 PVT 渲染) — 不同 ✓
- Vvdd2cStimRewriteProduce-001 (.sp 电源激励行批量替换) — rewriter vs generator，不同 ✓
- DynPowerScanProduce-001 (ring osc 动态功耗扫描) — 不同 ✓
全不同，无 near-dup ✓

## case = EDA-Eval-DesignFlow-PowerSupplyDcTypeGenProduce-001
- k=14 (a-n)
- A: junlingw 真实 3-supply 配置 (VDD_SRC point/VNL_SRC list/VRA_SRC range)
- hidden B: 5-supply (VCC_CORE/VDDQ_MEM/VTT_REF/VPP_HV/VSS_IO) + spec_invalid (point+2token dc 拒绝)
- 五重 anti-hardcode: ①5 supplies vs A 3 ②B names 全异 A ③B 含 range/list/point 混合 vs A 同 ④B dc 值全异 ⑤B r 值全异 + B-独特 src_node 派生 (VCC_CORE→VCC_core 等)
- check.py 14 条: (a)zip+compile+size (b)valid exit0+invalid exit!=0 (c)header (d)5V+5R (e)V-line format+src_node 派生 (f)type→dc token 数 (g)R-line format (h)dc 值精确 (i)invalid 不产 VBB_NW dc=0.6 0.9 (j)anti-hardcode A 缺席 B 在场 (k)src_node 后缀小写 (l)3-seed (m)supply 顺序 (n)r 值精确
- 3 negs: neg_empty(→a/b) / neg_print_only(硬编 A→c/d/e/f/g/h/j/m/n) / neg_core_removed(无校验+src_node 不小写+dc 截断→b/e/f/g/h/i/k)
- 自验: REF 14/14 PASS ✓; negative_selftest 3/3 FAIL ✓; 3-seed sha256 一致 ✓; A diff MATCH ✓
