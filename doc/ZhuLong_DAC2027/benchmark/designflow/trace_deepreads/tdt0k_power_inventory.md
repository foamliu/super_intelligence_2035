# 深读笔记 · tdt0k · boyangma@hfeg0plg53 · mc=93 · domain=analog_context

## trace 来源
- session: 1794221506176_tdt0k (boyangma@hfeg0plg53)
- summary: mc=93, keywords cmos:795;analog:258;schematic:195;aether:136;netlist:74;opamp:16
- 项目: DDGOA V0 (LPDDR5/LPDDR5X DRAM, 顶层 WOWTOP)

## 用户意图（2 个真实用户轮）
- U#1: 「项目电路用到了那些电源」→ 枚举项目电路用到的所有电源
- U#2: 「能不能直接跳转到电源到产生位置以及使用的位置，或者给出 hierarchical 路径」→ 给出每个电源的产生位置与使用位置的层级路径

## 助手工具链（纯 Aether 文件探查 + 读文件，无真跑商业 EDA）
- list_allowed_files 大量目录枚举 (/ai_sandbox/ddgoa, /proj/ddgoa/V0, commonIP/...)
- read_files: padInfo.log, padname mapping, cds.lib, lib.defs, setup/config, aether.rc.cdl, model.map, cell_map .netlist.map
- 最终两段 markdown 报告（U#1 电源清单 + U#2 层级路径）

## 关键产物（金标准 = 助手最终报告）
### U#1 电源清单
- 外部 PAD 输入电源: VDD1(core 1.05V), VDD2H(IO 高压 1.8V), VDD2HS(VDD2H 强驱动), VDD2L(IO 低压), VDDQ(DQ 1.05V), VSS(地), VSSQ(DQ 地)
- 内部 LDO 稳压: vintcore!/vintbus!/vintcoredq!/vintio!/vad2o!/vad2e!/vdleq!
- 内部 Charge Pump: vpp!(字线升压), vblh!(位线高), vwln!(字线负压), viso!(隔离), vwlp!(字线低压), vcslp!(列选), vpcsg!
- 内部参考/偏置: vglbref, vbpsa!/vbnsa!, vfsrd*!(反熔丝系列)

### U#2 层级路径（Library/Cell/View 格式）
- 外部电源 → ddgoa_top/WOWTOP/schematic 全局 net
- 内部 LDO → ddgoa_cmos_top/DLDO_signal/schematic，挂在 ddgoa_cmos_top/SpineTop/schematic 的 inst DLDO_signal
- 内部 Pump → commonIP/PumpVppIP/schematic / PumpVblhIP / PumpVnwlIP / PumpVisoIP ...，挂在 SpineTop
- 使用位置: Channel 块使用 vintcoredq!/vblh! 等

## 文件格式（实测）
- cell_map .netlist.map: `Library/Cell/view\t\tcellname`（如 `commonIP/PumpOscVccIP/schematic\t\tPumpOscVccIP`）
- padname mapping: PAD 名列表（含电源 PAD 与信号 PAD）
- padInfo.log: 电源 PAD 描述（名称/类型/电压）
- model.map / aether.rc.cdl: 模型与 CDL 配置（本轮访问受限，靠助手报告重建格式）

## B 档合成方案（自包含）
私有 /proj/ddgoa 项目 + Aether cellview 不可复刻 → B-grade synthesized 自包含：
- 可见 A: padname_A.txt(PAD→type, 电源 PAD + 信号 PAD) + padInfo_A.log(电源 PAD 描述) + netlist_A.cdl(层级 CDL: WOWTOP→SpineTop/Channel, 生成器叶子 DLDO_*/Pump*IP 输出内部电源 net, 消费块连接内部 net) + cellmap_A.tsv(Library/Cell/view→cellname)
- 隐藏 B: 同构全不相交(电源名/内部 net 名/lib 名/inst 名/计数全不同)
- SUT 交付 power_inventory.py(--padname/--padinfo/--netlist/--cellmap/--outdir) 纯 stdlib → power_inventory.json(external_supplies[]+internal_supplies[]+summary)
- 判分: 独立 oracle 解析 A+B 比对 (≥15 条件 a-o)

## 维度正交
既有 D case: TopoReconstructExtract-001(拓扑提取)/DirectivePairAudit-001(SV 指令配对)/LvsConnDiagnose-001(LVS 报告解析)/SramHierAdapter-001(SRAM 派生)/HciStressWindowExtract(波形应力窗口)。
本 case = 电源供应清单 + 层级产生/使用路径(从 padname/padInfo/层级 CDL/cellmap 提取电源 inventory)，机制/产物全不同。
