# 深读笔记 — rser7 (jkxu @ hfeg0pkn004, mc=102)

**session**: `1792829965577_rser7.messages.json` (992KB, 81 msgs)
**user/host**: jkxu / hfeg0pkn004 (10.129.2.13)；同时分布 hfeg0pfn081/087/090
**domain**: schematic_netlist (D)；A/B 均以 wrong-shard/old-Q&A-rule parked
**revival**: r883 revival-from-parked，依据 2026-11-15 用户令（Q&A 造-able）

## 用户真实意图（两轮 user text）

**U1 (msg 0)**: `.../pt_dir_post` 是生成 SDF 的路径，`.../pt_dir_post/parasitics_command.log` 文件显示反标率很低，是什么原因？

**U2 (msg 46)**: `.../pt_dir_post/DDR5TOP.sdf.gz` 这是生成的 SDF 文件，看起来只有 I_PERI0 这一层有 pin to pin delay。

→ 任务形态 = **诊断 Q&A**：用户问"反标率低的原因"+"SDF 看起来只有 I_PERI0 有 pin-to-pin delay 的原因"。无 produce 脚本需求，金标准 = 解释清楚两件事的事实性诊断报告。

## assistant 工具链与关键产物

1. `read_files(sdf.tcl)` → 拿到 PrimeTime SDF 生成脚本全文。
2. `run_approved_command(python-runner, analyze_parasitics.py)` → 多次跑自写脚本扫 `parasitics_command.log`（1,066,065 行，344MB）。
3. `editor(analyze_sdf.py / sdf_analysis.py)` → 写脚本解析 `DDR5TOP.sdf.gz`（20M 行）。
4. `run_approved_command` 跑 sdf 分析脚本，得到层级分布。

## 关键事实（金标准来源）

### sdf.tcl 核心行
- L1: `set blockname DDR5TOP`
- L24: `read_verilog "netlist_pt"`
- L26: `link_design $blockname`
- L28: `read_parasitics -path I_PERI0/I_BCenter   -complete_with zero -verbose /rundata/.../BCenter.spf.TYP_25.cvps`
- L29: `read_parasitics -path { I_Array6G_T_0.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut I_Array6G_T_1.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut }   -complete_with zero -verbose /rundata/.../D_BnkGTopX2gut.spf.TYP_25.cvps`
- L30: `read_parasitics -path { I_Array6G_B_2.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut I_Array6G_B_3.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut }   -complete_with zero -verbose /rundata/.../D_BnkGTopX2gutB.spf.TYP_25.cvps`
- L32: `report_annotated_parasitics -list_not_annotated -pin_to_pin_nets -max_nets 30000000`
- L36: `write_sdf -version 3.0 -context Verilog -compress gzip -include {setuphold recrem} -exclude {checkpins} -significant_digits 3 -output_port_nets -input_port_nets $blockname.sdf`

⇒ **只有 3 条 `read_parasitics`**，只覆盖 `I_PERI0/I_BCenter` 和 4 个 `I_Array6G_{T_0,T_1,B_2,B_3}.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut` 子层级；顶层 DDR5TOP 其余大量子块未做 SPF 反标。

### parasitics_command.log 关键内容
- 头部大量 `Error: Cannot find net 'I_PERI0/I_BCenter/I_BCenterCA/I_D_RepeaterCR/ln_XXXX' in design 'DDR5TOP' (PARA-124)` —— SPF 里的 net 在 link 后的 design 里找不到（层级/net 名不匹配）。
- 尾部 `report_annotated_parasitics` 汇总表：
  ```
  Net Type            |  Total  | Lumped  |  RC pi  | network |Annotated|
    - Pin to pin nets | 1279911 |       0 |       0 |  214883 | 1065028 |
    - Pin to pin nets |     434 |       0 |       0 |       5 |     429 |
  ```
  - 主表：Total=1,279,911；Annotated=1,065,028；network（未反标）=214,883
  - 反标率 ≈ 1,065,028/1,279,911 = **83.2%**（未反标 16.8% = 214,883/1,279,911）
  - 次表（疑似 power/ground 或另一类）：Total=434, Annotated=429, network=5
- 总行数 1,066,065

### DDR5TOP.sdf.gz 结构
- 顶层**只有一个 `(CELL (CELLTYPE "DDR5TOP") (INSTANCE) ...)`** —— flat 顶层 CELL，所有 delay 都在该 CELL 的 `(DELAY (ABSOLUTE (INTERCONNECT ...)))` 下。
- **只有 INTERCONNECT（线延迟/pin-to-pin），没有 IOPATH（cell 内部 delay）的子 CELL**。
- INTERCONNECT 按顶层子例化前缀分布（assistant 脚本统计）：
  - I_PERI0: 273,991
  - I_Array6G_B_2: 310,949
  - I_Array6G_T_0: 310,949
  - I_Array6G_B_3: 310,949
  - I_Array6G_T_1: 310,949
  - 少量 flat cell（I20/I22/I23/I25/I15/I16/I17/I19）

⇒ **用户"只有 I_PERI0 有 pin-to-pin delay"的观察是误读**：SDF 文件前 ~27 万行都是 I_PERI0 前缀的 INTERCONNECT，再往后才是 I_Array6G_*；用户只看了开头。实际 5 个主要子块都有 pin-to-pin（INTERCONNECT）delay，只是 SDF 是 flat 顶层结构、没有分层 CELL/IOPATH。

## 诊断结论（金标准）

**Q1 反标率低的原因**：
1. sdf.tcl 只对 3 个子层级（I_PERI0/I_BCenter + 4 个 I_Array6G_*.I_D_BnkGTopX2Top.I_D_BnkGTopX2gut）做了 `read_parasitics`，顶层 DDR5TOP 其余子块未提供 SPF → 大量 net 无 parasitics。
2. 即使提供了 SPF，仍出现 PARA-124（Cannot find net ... in design 'DDR5TOP'）：SPF 里的 net 路径与 link 后的 design 实际层级/net 名不一致 → 这些 net 反标失败。
3. 汇总：1,279,911 个 pin-to-pin net 中 214,883 个未反标（network 列），反标率 83.2%。

**Q2 SDF 看似只有 I_PERI0 有 pin-to-pin delay 的原因**：
1. SDF 是 flat 顶层结构：整个 SDF 只有一个 `(CELL (CELLTYPE "DDR5TOP") (INSTANCE))`，所有 delay 都是顶层 CELL 下的 `(INTERCONNECT ...)`，没有分层子 CELL、没有 IOPATH。
2. INTERCONNECT 条目按子例化路径前缀排序，I_PERI0 段在前（~27 万条），其后才是 I_Array6G_* 各 ~31 万条；用户只看了文件开头，误以为"只有 I_PERI0"。
3. 实际 I_PERI0 + 4 个 I_Array6G_* 共 5 个主要子块都有 pin-to-pin（INTERCONNECT）delay；用户观察是采样位置偏差，不是真无。

## case 合成方案

- **形态**：诊断 Q&A，交付 `diagnostic_report.md`（在 submit.zip 内）。
- **A（visible）**：真实 trimmed 资产 —— sdf.tcl（去 /rundata 绝对路径前缀，保留 3 条 read_parasitics 结构）、parasitics_command.log（PARA-124 头部样本 + 汇总表尾）、DDR5TOP.sdf（解压 trimmed：header + 各 hierarchy 若干 INTERCONNECT 样本）。
- **B（hidden，判分只跑 B）**：合成平行场景 —— 设计 LPDDR5TOP、2 条 read_parasitics（覆盖 I_PERI0/I_DCC + I_Array4G_T_0/I_D_BnkTopX1）、不同 PARA-124 net 名、不同汇总数字（Total 985442 / network 178305 / Annotated 807137，次表 Total 387 / Annotated 383）、SDF flat 顶层、层级 I_PERI0 + I_Array4G_T_0 + I_Array4G_T_1。每维度反硬编码。
- **check.py**：解析 report，≥9 条独立断言，验 B 特定数字（反标率/未反标数/total/次表 annotated）、PARA-124 关键词、read_parasitics 条数（2）、覆盖子块名、SDF flat 顶层 + INTERCONNECT-only + 无 IOPATH、实际有 delay 的 hierarchy 清单（修正用户误读）、设计名 LPDDR5TOP。
- **断言数**：9（a-i），满足 ≥8 硬闸门。
