## 交付接口
- 交付件：`outputs/submit.zip`，含 `port_catch.py`（通用 CDL 网表实例端口连通性抓取器，纯标准库，CLI `port_catch.py <netlist> <inst_fullpath> [-o out.json]`）+ `report_A.json`（对 A 网表目标 `nand2_CPSel.XI1` 的输出）。
- 可见输入 A：`assets/EDA-Eval-DesignFlow-PortCatch-001/nand2_CPSel_A.netlist`。
- 判分：独立环境跑你的脚本于 A 与隐藏 B，对账端口/方向/连线/邻居 + 跨输入守卫。
