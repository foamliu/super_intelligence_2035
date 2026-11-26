# Deepread: oh3te — AutoCell CDL→GDS standard-cell layout synthesis

**trace_source**: user=miccao, host=10.129.32.47 (hfeg0pgn045), session=1790127432240_oh3te.messages.json, mc=202, size=561KB, nmsgs=37, nturns=1 (single-turn produce)
**scan keywords**: .gds:484;netlist:242;calibre:112;.cdl:82;schematic:43;pdk:21;aether:17;lib.defs

## User intent (U#0, verbatim, 仅掩码)
> [autocell-tcl-flow-generator] /home/miccao/autocell/ddcpc/cell_constraints_template.txt这是我的配置文件，运行路径是/home/miccao/autocell/demo/show，网表路径是/home/miccao/autocell/ddcpc/netlist/train_proplus_decqa_20260903/netlist_dir_20260807/xord2x2.cdl，生成的gds请放到/home/miccao/autocell/demo/show下.autocell用/apps/proplus/autocell.1.2026.8。

A-faithful 判定：纯 produce 单轮 + user-accepted 产物存在。但产物在 /home/miccao 私有 + autocell 商业工具 + GDS 二进制不可附加 → **A-faithful 不可行 → B 档 synthesized**。

## Assistant tool chain
1. `skills autocell-tcl-flow-generator` (skill 调用，参数=配置/运行路径/网表/gds 路径/autocell 路径)
2. `read_files` cell_constraints_template.txt + xord2x2.cdl
3. `list_allowed_files` /home/miccao /apps/proplus/autocell.1.2026.8 /home/miccao/autocell/ddcpc /demo/show
4. `read_files` existing flow: run.tcl / layers.tcl / layer_functions.tcl / viadefs.tcl / globals.tcl / rules.tcl / place.tcl / route.tcl / tech.tcl / xord2x2_flat.cdl / autocell_stdout.log / log.autocell
5. `editor` run.tcl (改 stale set_external_engine 路径) → 被 policy 拒（writableRoots 不含 show/）
6. `editor` /home/miccao/.cline/scripts/data/run_autocell.sh (新建 shell 脚本，env+path+autocell 调用)
7. `run_approved_command` shell-runner /home/miccao/.cline/scripts/data/run_autocell.sh → exit 0，AutoCell v1.26.8 跑通
8. `list_allowed_files` /demo/show → 验证产出文件
9. `read_files` xord2x2_flat.cdl + xord2x2_placement.json → 全验通过

## 真实产物（user-accepted，/home/miccao/autocell/demo/show/）
- run.tcl — 主 flow，source 7 个 tech 文件，create_schematic/cell + 配置 placer/router + generate_layout + write_layout
- layers.tcl (1128 行) — GDS layer/datatype 声明
- layer_functions.tcl (26 行) — 语义功能 (ndiff/pdiff/poly/via1/via2/m1/m2/m3...)
- viadefs.tcl — via 定义: PC_N/PC/PC_small/PCU_L/Z/N, CT_N/F/P
- globals.tcl — 全局 net 别名: VDD={vccz!,vdd1!,vpcsg!,vcc!}, VSS={vssz!,vkb!,vss!}, VPW={vbn!,vkb!}, VNW={vbp!,vdd1!,vpcsg!,vcc!}
- rules.tcl — 设计规则 (min_width/area/spacing/eol_spacing) + tech-level calibre DRC/LVS engine
- place.tcl — device classes (ptn, ntn_m) + templates (n, p, p_n) + boundary/dummy/connectors
- route.tcl — router options + via instances + pin templates (pin11–pin55, pinz11–pinz55) + routing grids (poly/m1/m2/m3/pin)
- xord2x2_flat.cdl — 展平网表 (8 transistors)
- xord2x2_placement.json — placement 结果
- autocell_stdout.log / log.autocell / calibre_drc_flat.log — 日志
- GDS output (hierarchical)

## 关键参数（assistant 总结表）
| 参数 | 值 |
|---|---|
| Process | planar (G5 DDCPC) |
| Cell | xord2x2 (XOR2, 2× drive) |
| Kit/Layout spec | x / x_pin22 |
| PMOS type | ptn (W=5.576u, L=184n, nf=2) |
| NMOS type | ntn_m (W=3.28u, L=184n, nf=2) |
| Netlist mode | per_cell (flat) |
| Placement mode | auto |
| Hierarchy | -hierachy (hierarchical GDS) |
| AutoCell binary | /apps/proplus/autocell.1.2026.8/autocell/linux/x86_64/bin/autocell (v1.26.8) |

## 合成 plan（B 档 L1，schematic_netlist domain）
**facet**: CDL netlist → AutoCell placement-plan + device-extraction generator
**生成器**: `gen_autocell_place.py --netlist <cdl> --spec <json> --outdir <dir>`
- 解析 CDL .subckt + MOS 行 (M<name> <D> <G> <S> <B> <model> w= l= nf=) → devices.json
- 按 model 分类 p/n (ptn→p, ntn_m→n)；W/L 转 micron 浮点 (u→×1, n→×0.001)
- placement: PMOS→pmos_row (y=pmos_row_y), NMOS→nmos_row (y=0)；按 CDL 出现顺序排
  - 累进 x = Σ dev_eff_width(W*nf)；orient 在 abut 组内交替 normal/flipH
  - abut: 相邻同 row 共享非 power 扩散net(S/D) → 同 abut_group；power net = spec.power_nets ∪ net_aliases 展平
  - abut_pair_partner = 组内前一设备名(组首 null)
- summary.json: {cell, drive, n_dev, n_pmos, n_nmos, pmos_row_width(Σ pmos W*nf), nmos_row_width(Σ nmos W*nf), n_abut_groups, device_classes{ptn{W,L,nf},ntn_m{W,L,nf}}, net_aliases{VDD,VSS,VPW,VNW}}
- 写 devices.json / placement.json / summary.json

**A (SUT 可见)**: cdl/xord2x2.cdl (XOR2 8T=4P+4N) + spec/spec_A.json (ptn 5.576/0.184/2, ntn_m 3.28/0.184/2, net_aliases 真实 trace 值)
**hidden B**: cdl/nand2d1.cdl (NAND2 4T=2P+2N, 2 abut groups) + spec_B.json (ptn 2.8/0.184/1, ntn_m 1.6/0.184/1, 别名组 2)
**hidden B2**: cdl/inv_x4.cdl (INV 2T=1P+1N, 0 abut groups → 无 abut 分支) + spec_B2.json (ptn 4.0/0.184/4, ntn_m 2.4/0.184/4, 别名组 2)

**反硬编码六轴**: cell 名(xord2x2/nand2d1/inv_x4) / 信号名(内部 net pd1/pd2/i1/i2/a/b 全不相交) / 驱动(2x/1x/4x → W*nf 不同) / device 数(8/4/2) / abut 组数(4/2/0 → B2 无 abut 分支) / net_aliases 不同 + A 字面量禁源码

**check 16 条件 a-p**:
a. zip 解出无泄漏(check/reference/negative/jsonl) + py_compile candidate
b. B-run: candidate exit 0 + 产 devices/placement/summary 三文件
c. devices.json: list + len==spec_B.n_dev(4) + 每设备 keys(name/type/model/W/L/nf/pins)
d. p/n 计数==spec_B(2P/2N)
e. 每设备 W/L/nf 浮点 == spec_B.device_classes[model]
f. 每设备 pins D/G/S/B 网名 == CDL 解析(check 自解 B cdl 对照)
g. placement: row∈{pmos_row,nmos_row} + p→pmos_row/n→nmos_row 一致
h. placement: x/y 浮点 + 同 row x 非递减 + orient∈{normal,flipH}
i. abut 正确: 相邻同 row 共享非 power 扩散net→同 group + 组内 orient 交替 + partner=组内前设备(组首 null)
j. summary: cell==spec_B.cell + n_dev + n_pmos + n_nmos + pmos_row_width(==Σpmos W*nf) + nmos_row_width + n_abut_groups==2
k. summary.device_classes==spec_B + net_aliases==spec_B
l. B2-run: n_dev==2(1P/1N) + n_abut_groups==0 + cell==spec_B2.cell
m. 跨输入 A-run: cell==xord2x2 + n_dev==8 + n_dev_A≠n_dev_B(8≠4)
n. 跨输入 B2 vs B: cell 不同 + n_abut_groups 不同(0≠2) + pmos_row_width 不同
o. 反硬编码: 源码无 A 字面量(xord2x2/pd1/pd2/5.576/3.28) + 无 B/B2 cell 名(nand2d1/inv_x4)
p. 确定性: B-run 3 次 summary.json sha256 一致

**自验**: ref PASS 16/16 + 5 neg FAIL(empty_shell→b / hardcode_a→c / no_abut→i / print_expected→b / ref_core_deleted→h) + §4.9 三假 FAIL + 断言 k=16
