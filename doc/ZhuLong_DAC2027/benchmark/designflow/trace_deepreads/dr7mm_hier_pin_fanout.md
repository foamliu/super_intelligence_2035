# Deepread: 1794376149228_dr7mm (fxian, hfeg0pkn005, mc=446)

## Session meta
- **User**: fxian (DRAM analog designer)
- **Host**: hfeg0pkn005 (10.129.8.112)
- **Match count**: 446 (keywords: schematic:1043;cmos:647;aether:492;pyaether:414;.lef:120;netlist:63)
- **Messages**: 408, ~2.1MB
- **Domain**: schematic_netlist (D shard) — C shard had parked as "wrong-domain: D" (r538)
- **Cross-shard reclaim**: D reclaims from C (C parked, not case)

## User intent
fxian 在 Aether 原理图中搭建了 5 层层次化测试电路验证 `hier_pin_gui.py` 脚本：
```
Top_test → LvL4_test (1 inst) → LvL3_test (8 insts) → LvL2_test (4 insts) → LvL1_test (2 insts) → pin: hello
```
Fanout: 1 → 2 → 8 → 64 → 64

从底层 LvL1_test 的 `hello` pin 往上逐层打 pin。核心问题：
1. **Pin 扇出数量错误**：LvL3 应出 8 个 pin（4 实例 × 2 子 pin），脚本只出 4 个
2. **Pin 命名冲突**：不同层相同 port 名未区分，需追加实例索引（hello_I0、hello_I0_I0）
3. **Pin y 坐标叠在一起**：symbol 上多个 pin y 重复，需按递增规则排开
4. **Wire 连不上 pin**：wire 端点未对准 pin 坐标

用户要求全自动迭代修正（U#346: "直接用现有的电路&脚本 全自动迭代 不需要我的任何许可"）。

## Assistant 工具链
- SandBox_MCP_Server__run_code × 92 (pyAether 操作 Aether 原理图)
- editor × 51 (编辑 hier_pin_gui.py)
- read_files × 23, run_approved_command × 18
- RAG_MCP_Server__search_apis × 7 (查 pyAether API: dbCreatePin/dbCreateTerm/dbCreateWire 等)

## 最终交付
修正后的 hier_pin_gui.py：
- `_PIN_POS`/`_SCH_POS` 会话计数器保证 y 单调递增不重复
- Pin 命名 `<child_pin>_<inst_name>` 逐层累积
- Wire 精确路由到实例引脚点
- 实测 fanout: LvL1=1, LvL2=2, LvL3=8, LvL4=64, Top=64

## 合成为 case
- **Case ID**: EDA-Eval-DesignFlow-HierPinFanoutProduce-001
- **Domain**: schematic_netlist
- **Level**: L1 (离线 Python 解析层次化 netlist，计算扇出/命名/坐标/wire)
- **k_check**: 13 断言
- **Asset A**: hier_netlist_a.txt (1→2→8→64→64, pin=hello, start_y=100, incr=100)
- **Hidden B**: hier_netlist_b.txt (1→2→6→30→30, pin=data_io, start_y=200, incr=150)
- **Hidden A-prime**: hier_netlist_aprime.txt (1→1→3→12→12, pin=clk_pad, start_y=50, incr=80) — anti-hardcode
- **check()**: 13 条独立断言，参考解 PASS，3 负样本全 FAIL
