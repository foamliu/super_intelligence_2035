# 深读笔记 — lyg4g (yazhuok@hfeg0plg96, mc=93, schematic_netlist)

## session
- sid: 1792830418555_lyg4g.messages.json
- user: yazhuok, host: hfeg0plg96
- 379 msgs, ~analog/schematic/netlist/pex domain

## 真实意图
用户 yazhuok 有 StarRC 抽出的 SPF_RCC (DSPF 1.3) RC 耦合网表文件（CXSA 感应放大器阵列的 PEX 输出）。
用脚本 `bl_coupling_total_layer_same_CXSA.py` 解析后计算每根 BL (bitline) net 的耦合电容统计，
发现脚本统计的 Ctotal 与文件 `*|NET` 声明的总电容不一致：
- BLa<0> 脚本统计 0.837063fF vs 文件声明 0.000919766pF (≈0.919766fF)

根因：子节点 (`*|S` 如 BLa<0>:11) 和 instance-pin 节点 (`*|I` 如 XI_...:DRN) 未正确归网导致漏算耦合。
`build_node_to_net` 扫描 `*|NET`/`*|P`/`*|S`/`*|I`/`R` 行建立 node→net 映射，耦合行端点用此映射解析回网名。

## SPF_RCC 格式
```
*|NET <name> <total_cap>PF          # 声明 net 总电容
*|P (node O ...) $lvl=N             # 端口节点
*|S (node ...) $lvl=N               # 子节点
*|I (pin inst PIN ...) $lvl=N       # instance-pin 节点
R<name> n1 n2 val                   # 电阻，n1/n2 归当前 net
C<name> n1 n2 <val_F> $lvl1=L1 $lvl2=L2   # net-net 耦合电容
C<name> n1 0 <val_F> $lvl=L               # 接地电容 (n2=接地网 0)
```

## 分类规则
- BL net 正则: `(?i)^(\w*?)bl([ab])([a-z]*?)<(\d+)>$`，sa 前缀排除
- Csame_type: 同 a/b 字母 (a↔a, b↔b)
- Cdiffer_type: 异 a/b 字母 (a↔b)
- Cground: 对地 (n2=0)
- Cremaining: 非 BL net
- 守恒: Ctotal = Csame + Cdiffer + Cground + Cremaining = *|NET 声明值

## 可离线判分内核
合成小 DSPF/SPF_RCC 文件 (A 可见 4 BL + B 隐藏 6 BL)，脚本解析并输出 summary CSV (fF)：
Ctotal/Csame_type/Cdiffer_type/Cground/Cremaining per BL net。
check() 在 B 上跑脚本校验所有数值 + 守恒 + 子节点解析 + anti-hardcode (A↔B 不同值)。

## 与已有 case 不相交
- r1230 PexSpfQaMonotonicityCheck: SPF 电容单调性（同方向递增）
- 本例: SPF 耦合电容 same/differ 分类 + node→net 归网 + 守恒
- 内核完全不同（分类 vs 单调性）

## case 交付
- task_id: EDA-Eval-DesignFlow-SpfBlCouplingClassifyProduce-001
- k_check=15
- A: 4 BL (BLa<0..1>+BLb<0..1>) + 2 Csl, 9 耦合电容, BLa<0> Ctotal=3.8fF
- B: 6 BL (BLa<0..2>+BLb<0..2>) + 2 Io, 14 耦合电容, 含子节点 BLa<0>:1 + instance-pin XI_X0.XM1:DRN + R1, BLa<0> Ctotal=5.9fF
- §4.9 三假全 FAIL (N1_print_only→A行数错, N2_hardcode_a→B行数错, N3_core_deleted→Csame错)
