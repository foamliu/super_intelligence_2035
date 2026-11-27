# wf513 deepread — wellesc/hfeg0plg17, mc947, digital(netlist/verilog)

- session: `1795168050680_wf513` (wellesc @ hfeg0plg17), 690 msgs / 342 assistant, 1.1MB messages.json
- scan: ssh_eda_search_20261128_014416, dominant keyword `verilog` (mc947; netlist-heavy)
- trace_source: {user: wellesc, host: hfeg0plg17, session_file: 1795168050680_wf513.messages.json, match_count: 947, real_task_summary: 用 Aether emy2verilog 从 drcoa_stdcells 库抽取 Verilog 网表, 与 /proj/drcoa/V0/simdir/verilog/liujun/verilog.ddr5.drcoa.netlist/netlist_stdcell/ 的 A 参考网表对齐}

## 真实用户意图 (4 real user turns)
- U#0 (context summary): si 环境已修复, `ENGINE=si` 产出与 org 参考**语义一致**的网表 (`inh_*` 端口 + `strength` 参数, `AF_nor3Yx1` 实测 `spec=0 wire=2 inh_=8 str=2` 与 A 一致)。问: (1) 接受 si 形态还是加后处理对齐排版(端口用户顺序+4空格缩进+`wire x;`)? (2) 全库抽取是否启动 (`cd /home/wellesc/VerilogNetlistByLib; ENGINE=si LIB=drcoa_stdcells bash run_extract.sh -b`)?
- U#1: "我希望你用 Aether 的 emy2verilog 来抽网表" (否决 si, 要求走 Aether 原生 emy2verilog)
- U#56: 给出 A 参考网表路径 `/proj/drcoa/V0/simdir/verilog/liujun/verilog.ddr5.drcoa.netlist/netlist_stdcell/` 是 A 抽的网表
- U#156: 选路线 1 = Aether 应用层驱动 (pyAether `emyInitAether()` + `dmExportNetlist()`, Aether 自己读 `verilog.rc`), 唯一能逐字复现 A; 需 Aether 进程内运行 (沙箱报 ip_port.json not found, 需先启动 Aether GUI/bridge)

## 助手工具链 (342 assistant msgs, 188 editor / 139 run_approved_command / 4 RAG search_apis / 2 SandBox run_code)
- 主线: 在 `/home/wellesc/VerilogNetlistByLib/_tmp/` 下迭代 ~40 个 Python 脚本驱动 Aether:
  - v1_init_test ~ v7_headless: emyInitAether/dmExportNetlist 探针 (ip_port.json not found → 尝试 headless/offscreen/xcb)
  - w6_fixqt ~ x1_xcb2: Qt/X11 display 修复尝试
  - aa6_merge ~ cc3_getname: cell 名 / db / inh_ 端口属性提取
  - dd1_generate ~ jj4_final: emy2verilog 网表生成 + 后处理 (端口排序, strength 参数, inh_* 端口)
  - extract_lib_netlist.py (6848 chars, 最终版): 全库抽取主脚本
- 关键技术点: `inh_*` 端口 (inherited ports), `strength` 参数, `AF_nor3Yx1` cell 实测 spec=0/wire=2/inh_=8/str=2, verilog.rc 配置, drcoa_stdcells 库

## 合成评估 (DEBT — 本轮仅深读, 下轮合成)
- **Aether-dependent**: 整个任务依赖 Aether 进程 (emyInitAether/dmExportNetlist/pyAether), 非自包含; /proj/drcoa 原始网表权限不可读 (trace 中 read_files tool_result 多为空)
- **自包含候选 sub-task**: 网表语义等价校验器 (验证 si/emy 输出与 A 参考 inh_* 端口+strength+cell 实例数一致) — L1 可行, 但属助手内部验证步骤, 非用户直接意图 (用户要的是抽取本身), trace-faithful 度偏弱
- **结论**: 690 msgs > 600 阈值 + Aether 依赖使自包含合成非平凡; 按 §3 记 DEBT, wf513 保持 claimed, 下轮需决定: (a) 找自包含 sub-task 合成 / (b) mark parked (Aether 依赖, 非自包含)
- 交付 ETA: 下轮 (r1497) 决定合成或 parked
