# deepread: 1794999346452_d1jo3 (scarle @ hfeg0plg102) — schematic_netlist

- mc=660, 375 msgs, D-dominant (aether:3470/netlist:2589/schematic:1425/lvs:638/analog:568)
- 真实意图：在 Aether 中自动抽取 `stdcells_ac/invVx2` (schematic) 的网表，要求完全自动化无需手动 console。
- 用户消息流：
  - U#0: 打开 Aether + G5CIPPingtai 项目 DSCQA
  - U#68: 打开库 standcell_ac，找 cell invVx2 / view schematic，菜单 Tool/MDEL2/Simulation/Netlist 抽网表
  - U#200: dbOpenCV 报错 "Unable to lock database file"
  - U#221: 要求在已打开 Aether 中抽网表，完全自动化不需手动 console
  - U#265/275/292: aether -tclFile / aether_auto.tcl 没执行；source aether_open.tcl 后 seGuiShowNetlist 没弹窗
  - U#339: source aether_open.tcl → "Done!" 后如何抽网表
  - U#341: seGuiShowNetlist 步骤三后没弹抽网表窗口
  - U#355: oa:0x7fd8b00fe31a 值非0（trace 末尾，未拿到网表）
- 助手路径（均失败）：`aether -tclFile`（非支持参数）、`aether_auto.tcl`(dbOpenCV+seGuiShowNetlist，dbOpenCV 因锁返回0)、`aether_open.tcl`、查 RAG_MCP search_apis（pyAether aeOpenDesign 是 Python 不能在 tcl 用）。
- 关键技术事实：Aether 无 `-tclFile`；`dbOpenCV -lib stdcells_ac -cell invVx2 -view schematic -mode r` 因库锁返回0；`seGuiShowNetlist` 需先成功打开 schematic editor 才弹窗；pyAether(aeOpenDesign 等) 是 Python API，不能在 .tcl 用。
- 台账：原被 shard C r786 parked（标注 "wrong-shard D (netlist-extraction) + ends unresolved"），本轮回收到 D（mark --force）。
- 造题：SchNetlistExtract-001（L1, schematic_netlist）。把核心交付「从 schematic 抽结构化 SPICE 网表」固化为 extract_netlist.py：读 schematic.json → 生成 .spi（.subckt/M行/.ends）。A=invVx2(2 MOS 反相器)，隐藏 B=nand2x1(4 MOS NAND，含内部网络 nint)。12 断言，3 neg 全 FAIL，anti-hardcode（硬编码 A 在 B 上 ④cell名/⑤实例数全错）。
