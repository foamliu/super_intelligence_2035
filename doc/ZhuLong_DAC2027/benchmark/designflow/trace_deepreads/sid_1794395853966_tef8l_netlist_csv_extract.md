# Deepread: sid 1794395853966_tef8l — netlist→CSV extract (schematic_netlist)

- session: `1794395853966_tef8l`
- user: yinyus @ hfeg0plg58
- match_count: 894, d_ratio: 0.51
- domain: schematic_netlist (+analog_context)
- ledger: claimed r615 shard D

## Trace 真实任务

yinyus 在 ALPS 仿真目录下有一批电容 Y-decoder 单元的 schematic netlist
(`<cell>_schematic.netlist`)，需要把网表里的实例行抽取成 CSV 表格供后续
pivot 分析。

## 网表格式 (ALPS)

- 文件含 `**TopDesStart <cellname>` 标记行 → 顶层设计起始
- 标记后每行是一个实例：`XI_<inst> <net1> <net2> <cellref>` (4 token, 空格分隔)
- `**TopDesEnd` 结束一个 cell 块
- `*` 开头行是注释 (ALPS/SPICE 约定)，需跳过；空行跳过
- 一个库文件含多个 `**TopDesStart` 块 (多个 cell)

样例 (来自 trace)：
```
XI_AG_CXcap1S151x167_1 vss! vncsg! AG_CXcap1S151x167
```

## 用户两步需求

1. **MSG[166] (4-col CSV)**: 读 netlist，找 `**TopDesStart`，抽取其后所有
   token，每 4 个 token 组成一行 → 4 列 CSV `inst,net1,net2,cellref`，
   输出 `<cellname>.csv`
2. **MSG[191] (2-col pivot)**: 在 4-col 基础上 drop col1(inst)，把 col2+col3
   用 `-` 拼成新 col1 `net_pair`，col4(cellref) 变成新 col2 → 2 列 CSV
   `<cellname>_pivot.csv`，header `net_pair,cellref`

## trace 涉及的 9 个 cell

AG_CapYdecBOT_center_normal, AG_CapYdecBotLNormal, AG_CapYdecBotRNormal,
AG_CapYdecTopCenterNormal, AG_CapYdecTopCenterTop, AG_CapYdecTopLNormal,
AG_CapYdecTopLTop, AG_CapYdecTopRTop, AG_CapYdecTopRNormal

(真实 .netlist 文件在 .75 `/proj/drcpa/V0/workdir/yinyus/simulation/`
下，权限拒绝 → 全部合成数据)

## 合成 case 设计

- **id**: `EDA-Eval-DesignFlow-NetlistCsvExtract-001`
- **domain**: schematic_netlist
- 3 个不相交 cell family: A(cap_array, 可见) / B(decoder, 隐藏) / C(sense_amp, 隐藏交叉)
- SUT: `netlist_csv.py <netlist> [--out-dir <dir>]` 纯 stdlib
- 交付: netlist_csv.py + A 的 4 个 CSV (2 cell × {4col, 2col pivot}) 打包 submit.zip
- check.py 14 条独立断言: 文件齐全 / py_compile / 无泄漏 / header / 行数 /
  具体行 / pivot 拼接 / 第二 cell / 隐藏 B 交叉 / 隐藏 C 交叉 / CLI 可运行
- 3 negative: empty_shell / print_only / hardcode_a (hardcode_a 过 A 但在 B 交叉败)

## 结论

clean D-domain produce-task，可合成。synthesis 本轮交付。
