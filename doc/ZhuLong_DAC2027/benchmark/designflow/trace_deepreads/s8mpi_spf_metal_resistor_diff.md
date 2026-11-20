# trace_deepread — s8mpi (StarRC SPF 两层抽取 metal-电阻差异 Q&A)

- **session**: `1793779407315_s8mpi` (xxchen @ hfeg0pkn001 / 10.129.2.10)
- **mc**: 37 (netlist:287; lvs:159; .gds:39; calibre:36; cmos:32; .spi:27; schematic:10; analog:10)
- **agent**: `lead`; 122 msgs, 1.15 MB messages.json
- **trace 源可达性**: 文件在 `/home/xxchen/.cline/data/sessions/1793779407315_s8mpi/` 下，经 .75 ssh 10.129.2.10 scp 取回（r888 报的 ssh-block 是本地直连 .75 超时；改 eda_flow run_commands 在 .75 上 ssh 即通）。真实 SPF (DqPad.spf 447MB / IO_DqIoTopD6.spf) 在 xxchen 私有 /rundata 路径不可复用 → B-grade 重建 mini-SPF。

## verbatim 用户原话（U#0，本 case 选定子意图）

「我当前有两个starRC 抽取的 不同层级的cell  top层DqPad ，下一层IO_DqIoTopD6
我runTrace 跑出来的报告：
IO_DqIoTopD6:  traceNet_none_DqIbLatch_DRN.rep
DqPad:traceNet_1260769_DqIbLatch_DRN.rep
中path resistors 中下一层中不含metal部分，top层确含有metal部分。
根据starRC的cmd:  star_cmd_RCC 定义并不抽取power的电阻，所以不带更合理。
你能通过分析这两个目录找出 spf 表现不同的原因吗？」

## 助手关键产物（trace 内 agent 真实读到/算出的）

- 目录: `/home/xxchen/workspace/small_tool/spf_Analysis/{DqPad,IO_DqIoTopD6}/`
- runTrace 命令: `python3 ../traceSPFresNode.py -o traceNet_*.rep --progress-gb 2 <spf> "<hier_path>.MMP1:DRN"`，target = `XI_IO_DqIoTop.XI_IO_DqIoD6.XI_IO_DqRcv.XI_IO_DqIbGrp.XI_IO_DqIbDfeSlicer_OF.XI_IO_DqIbLatch.MMP1:DRN`，matched_net = `vdd2dq!`
- top 报告 `traceNet_1260769_DqIbLatch_DRN.rep`：net vdd2dq! 段含 metal 电阻 (M0..M5, 526856 resistors)；子层 `traceNet_none_DqIbLatch_DRN.rep` 仅 8321 resistors，无 metal。
- agent 写 `analyze_spf_diff.py`（对比两 SPF net 段电阻按 `$lvl` 计数 / diff star_cmd_RCC / layer_map / scan_power_nets）。
- star_cmd_RCC 两份: top `POWER_EXTRACT: DEVICE_LAYERS` / sub `POWER_EXTRACT: NONE`（BLOCK/IGNORE_PORT/COUPLE_TO_GROUND 亦有差异）。

## 意图判定与 case 设计

- **用户真实意图**: Q&A investigation — 找 spf 表现不同的原因（top 含 metal、子层不含）。旧规则判「Q&A not produce-task」parked；**按 2026-11-15 用户令「Q&A-investigation/explain 类全部恢复为可造」revival**。
- **domain**: schematic_netlist（SPF 寄生网表，netlist-grounded）
- **reframe**: 套 r880/r884/r887 netlist-grounded explain Q&A 范式 → 候选交付 `spf_resistor_layer_diff.py`（按层分类电阻 + star_cmd_diffs + verdict + root_cause）。
- **B-grade gold**: 真实 SPF 不可复用 → 按真实结构（net vdd2dq! / 层名 M0..M5/DEV/VIA/CT / star_cmd_RCC POWER_EXTRACT 选项）重建 mini-SPF。
- **data-driven 3×B**: B1 (net vss2dq! / 层 5-6-7 / 计数 4-1-1-1) / B2 robustness (net vcc2dq! / top metal=6 反硬编码 B1) / B3 cross-input (net ghost_net! 不存在 → 优雅)。模块名/规模/层号与 A 全异，反硬编码有牙。

## 近重判（dedup）

- s8mpi 在 pool_reaudit 未单独标记，ledger 仅本 shard 一条（analog_context, parked→case）。无 cross-shard dup（4-shard 联合台账验）。hk622 是同 host 不同 session/不同用户任务，非重复。可造。
