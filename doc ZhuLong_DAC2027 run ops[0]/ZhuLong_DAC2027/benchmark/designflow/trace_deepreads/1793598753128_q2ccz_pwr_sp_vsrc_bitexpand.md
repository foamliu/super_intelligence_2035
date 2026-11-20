# 深读笔记 · q2ccz · pwr.sp v-source bit-range expansion

- **session**: `1793598753128_q2ccz.messages.json` (qilongw @ hfeg0plg52 / 10.129.35.68)
- **mc=18**, keywords: `schematic:43` (pure schematic_netlist domain)
- **fresh-sid** (不在 4-shard ledger) + **fresh-USER** (qilongw 不在 D-ledger user)
- 18 msgs / 9 user turns / 1 produce-task turn (U#0)

## U#0 逐字（用户提出需求轮，未给根因/修复）

```
请按照/proj/ddgoa/V0/workdir/qilongw/simulation/work_qilongw_BCTK_RowRed_schematic_ALPS/sim1/pwr.sp文件中对
vRaG0<15>\tRaG0<15> 0 0v
vRaG0<14>\tRaG0<14> 0 0v
的定义，对RaG0<15:1>, RaG1<15:1>, ..., RaG7<15:1>, RaNG0<15:1>, ..., RaNG7<15:1>进行相同的定义，并将结果另存为pwr2.sp
```

**意图**：读 pwr.sp，识别既有 v-source 比特定义行格式 `v<net><<bit>>\t<net><<bit>> 0 0v`，按此格式为 16 个 net 组（RaG0..RaG7 + RaNG0..RaNG7）逐比特（bit 15 down to 1）展开成 v-source 行，保留原 header，另存为 pwr2.sp。属 SPICE power-deck vector v-source bit-blast（DRAM 行译码电源开关的 per-bit 电源激励生成）。

## 输入 pwr.sp（实测 7 行，从 session tool_result 还原；/proj 路径权限拒，文件本身可读）

```
vPwrOn1          PwrOn1         0 0v
vPwrOn3          PwrOn3         0 0v
vRHRExt          RHRExt         0 0v
vcm1_ts_PPRResourceReduceout          cm1_ts_PPRResourceReduceout         0 0v
                                                          <- 第 5 行空行
vRaG0<15>	RaG0<15> 0 0v
vRaG0<14>	RaG0<14> 0 0v
```

- **header v-source 行（4 行）**：用空格分隔字段（多空格），无 `<>` 比特下标 —— 须原样保留。
- **空行（1 行）**：须原样保留。
- **比特定义 sample 行（2 行）**：`vRaG0<15>\tRaG0<15> 0 0v` —— TAB 分隔 vname 与 netname，`0 0v`（node=0, val=0v）。这两行将被全量展开（bit 15/14 已含于 <15:1>）取代。

## 金标准（agent 写的 gen_pwr2.py，逐字读自 /home/qilongw/gen_pwr2.py）

```python
#!/usr/bin/env python3
"""Generate pwr2.sp with full RaG* and RaNG* definitions."""
groups = [f"RaG{i}" for i in range(8)] + [f"RaNG{i}" for i in range(8)]
output_path = "/proj/.../sim1/pwr2.sp"
lines = []
lines.append("vPwrOn1          PwrOn1         0 0v")
lines.append("vPwrOn3          PwrOn3         0 0v")
lines.append("vRHRExt          RHRExt         0 0v")
lines.append("vcm1_ts_PPRResourceReduceout          cm1_ts_PPRResourceReduceout         0 0v")
lines.append("")
for grp in groups:
    for bit in range(15, 0, -1):   # 15 down to 1
        lines.append(f"v{grp}<{bit}>\t{grp}<{bit}> 0 0v")
with open(output_path, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Generated {output_path} with {len(lines)} lines")
```

**实测产物**：pwr2.sp 245 行 = 4 header + 1 空行 + 16 组 × 15 bit = 4+1+240 = 245 ✓
（agent 报告 245 lines，exit 0）。验证读取 pwr2.sp 前 42 行与上述结构一致（M#16）。

## B-grade 合成设计（A/B/C 全不相交）

**任务结构（SUT 接口）**：
```
pwr_sp_bit_expand.py <input.sp> <output.sp> --groups <comma-list> --bit-hi <N> --bit-lo <M>
```
SUT 须：
1. 读 input，用正则 `^v(\w+)<(\d+)>(\s+)(\w+)<(\d+)>\s+(\S+)\s+(\S+)\s*$` 识别**比特定义 sample 行**
2. 非比特行（header v-source + 空行 + 注释等）**原样保留**于输出开头（顺序不变）
3. 从第一条 sample 行抽取格式：`sep`=vname/netname 间分隔（TAB）、`node`、`val`
4. 对 `--groups` 列表每个组，按 bit_hi..bit_lo（降序）生成 `v{grp}<{bit}>{sep}{grp}<{bit}> {node} {val}`
5. 输出 = header_lines + expansion，逐行 `\n` 连接，末尾加 `\n`

| 维度 | A（SUT 可见） | B（hidden） | C（嵌入 check.py，反硬编码） |
|:--|:--|:--|:--|
| group 前缀 | DaG / DbG | SaG / SbG | WaG / WbG |
| 组数 | 8+8=16 | 6+6=12 | 2+2=4 |
| bit range | <7:1>（7 bit） | <11:2>（10 bit） | <5:0>（6 bit） |
| header v-source | 3 行（VddA1/VssA2/ClkA3）+ 空行 | 4 行（PwrB1/PwrB2/PwrB3/PwrB4）+ 空行 | 2 行（VddC1/VssC2）+ 空行 |
| sample 行 | DaG0<7>/<6> | SaG0<11>/<10> | WaG0<5>/<4> |
| node/val | 0 / 0v | 0 / 1.2v | gnd / 0v |
| 总行数 | 4+16×7=116 | 5+12×10=125 | 3+4×6=27 |

A/B/C：group 前缀、组数、bit range、header 内容、sample 行、node、val **全不相交**。
关键反硬编码：B 的 val=1.2v（≠A 的 0v），C 的 node=gnd（≠A/B 的 0）—— SUT 若硬编码 `0 0v` 则 B/C 全错。

## domain = schematic_netlist（SPICE power deck 文本变换，DRAM 行地址译码电源激励 bit-blast）

## 维度正交（非 dup 论证）

- **SpiceMeasGroupExpand-001**：.meas 测量 deck 按 sample 下标 append 链式 td 行扩组 —— 机制 = 测量族 td 链式引用扩展；本 case = v-source 比特行 bit-blast。不同。
- **SpiceMismatchSweep-001**：per-corner `.param` 行注入 —— 机制 = sweep 值替换；本 case = 比特行生成。不同。
- **GrDecPwrSwitchTbGen-001**：从 CDL 网表生成 row-decode 电源开关 TB —— 机制 = TB netlist 合成；本 case = pwr.sp v-source 展开。不同。
- **BitcellMcSpGen-001**：6T SRAM bitcell MC HSPICE .sp deck 生成器 —— 机制 = 全 deck 合成；本 case = 既有 deck 增量展开。不同。
- **PwrIremCfgFix-001** / **PwrCornerSweep-001**：配置修复 / 波形 corner sweep —— 均非 v-source 比特展开。不同。

⇒ `PwrSpVSrcBitExpand-001` 任务族无，机制正交，**非 dup ✓**。

## check.py 14 条件 a-n 草案（独立 oracle，subprocess 真跑 SUT on B+C）

a. zip 含 py + py_compile + 无禁 import/call + 无 B/C 字面量泄漏
b. SUT 跑 B 退 0 + 输出非空
c. B 输出行数 == oracle（header_B + groups_B × bits_B）
d. B header 行（非比特行）原样保留逐行匹配 input B
e. B 全部展开行匹配格式 `v<grp><<bit>>\t<grp><<bit>> <node> <val>`
f. B 组顺序正确（SaG0..SaG5, SbG0..SbG5）
g. B 每组 bit 范围正确（11..2 降序，无缺/重）
h. B node/val == sample 抽取（0 / 1.2v）
i. B 展开行数 == len(groups)×(hi-lo+1) = 12×10 = 120
j. 反硬编码跑 C 退 0 + 输出匹配 C-oracle（4 组 × 6 bit + 3 header = 27 行，node=gnd val=0v）
k. C 输出 ≠ B 输出（disjoint）
l. §4.9 empty FAIL
m. §4.9 print_only FAIL
n. §4.9 core_removed FAIL
（+ 3-seed sha256 一致 + hardcode_A neg FAIL on B/C）

DEBT 0→0（#550 的 DEBT 本轮偿付）。
