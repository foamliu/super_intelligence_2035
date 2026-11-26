# trace_deepread: 1795003444673_w3kbh (warrenm@hfhds209, mc211, netlist:1680/verilog:1032)

**会话**：306 msgs, 1.4 MB messages.json
**用户**：warrenm (DRAM 验证工程师，DDR5 write-leveling flow)
**主机**：hfhds209 (Cadence Virtuoso + cimi RAGFlow 知识库环境)
**scan**：mc211, keywords netlist:1680 / verilog:1032 (D-pure, schematic_netlist dominant)

## 用户真实意图（A-faithful U#0/U#3 verbatim）

> 给我一个skill，我会给你一个网表文件的路径，要求这个skill会根据我提供的网表文件路径
> 去读其中的网表文件，在每次更新网表的时候我会提供新的路径，如果没有新的地址的话那就默认旧的网表地址。
> 同时我会给这个skill一个pattern的路径，这个skill可以根据pattern中的代码和网表
> 给我列出来pattern要验证信号在网表中的层次结构。注意，生成的skill对所有的文件只能进行读，不可进行任何的写动作

U#23 给出真实路径：
- 网表：`/proj/drgqx/V0/simdir/verilog/warrenm/verilog.ddr5.drgqx.move_test/netlist/V0_WOWTOP_2026Oct14.161707/netlist`
- pattern：`/proj/drgqx/V0/simdir/verilog/warrenm/verilog.ddr5.drgqx.move_test/patterns/cmds_writeleveling/write_leveling_external1.v`

## 任务本质（produce-task，clean）

写一个**只读**工具：输入 netlist 路径 + pattern 路径 → 解析 Verilog 网表建 module DB（ports/wires/instances）→ 找 top（未被例化的 module）→ 从 pattern 提取标识符并过滤 SV 关键字/数字字面量/pattern 自身 module 名 → 从 top 向下递归遍历实例树，对每个标识符记录它作为某 module 的 port 或 wire 出现的全部层次路径 → 输出每个信号 `[i/N] SIG \n TOP.inst.inst.sig (port of MOD)` 形式。网表/pattern 路径都可在后续调用更新（不传沿用旧值），全局缓存跨调用复用。

## assistant 实际产物

- `editor` 工具 22 次调用，写出 `/home/warrenm/cds_findSignalHierarchy.il`（SKILL 脚本，~600 行）：
  - `cds_parseNetlist` — 逐行解析 module/ports/wires/instances，处理续行/注释/总线
  - `findTop` — 未被任何模块例化的 module 即 top
  - `cds_extractPatternSignals` — 提取标识符过滤 SV 关键字/数字
  - `cds_findSignalHierarchy` — 从 top 向下 DFS，列每个信号的完整层次路径
  - 全局缓存 `cds_g_netlistPath/cds_g_patternPath/cds_g_modules` 跨调用复用
  - 通配符 `*`/`?` 匹配；只读（`infile`/`gets`，无 `outfile`/`fprintf` 写文件）
- 因 `SandBox_MCP_Server__run_code` (pyAether @ 10.129.8.232:43388) 连接被拒，无法在沙盒里跑 SKILL，改用 Python 镜像同算法跑 `write_leveling_internal.v` 的层次分析（A#142 给出 DDR5 write-leveling 信号在门级网表中的对应：WrLevelEn→`WOWTOP.Channel.*.WrLevelEn`、`MR3_WLVL_SETLBo`、`WICAP5_EN` 等）

## 后续用户轮（非本任务核心，记录供后续造题）

- U#102/U#107：换 pattern (write_leveling_internal.v) 再列层次结构 — 同工具不同输入
- U#143-U#209：追问 SKILL 是否能根据 spec/lib/sdf 反推模块功能（agent 解释 SKILL 能做检索但不能做语义推断，需结合 JEDEC 标准人工分析）
- U#211-U#305：用户关联 cimi 知识库 (RAGFlow)，要 agent 用 `python_runner` profile 执行 `cimi-kb-search` skill 检索 `JESD79-5C.01_v1.31.pdf`（DDR5 标准）— agent 工具列表缺 `run_approved_command`，反复失败，最终用户自己跑 `kb-search-cli.py retrieve "JESD79-5C"` 拿到 41 条结果。**这一段是独立子任务（KB 检索执行能力），非本 case 范畴**。

## 合成 reframe 决策（synthesized-reframe）

真实 SKILL 脚本无法在判分沙盒里跑（Virtuoso CIW 不在 sandbox）；真实网表 /proj/drgqx/... 受路径与体积限制不可入沙盒。故：
- **reframe 为等价纯标准库 Python 工具** `pattern_hier_resolver.py`，实现完全相同的算法（parse netlist → module DB → findTop → extract pattern idents → DFS 列层次路径）
- **合成 9-module DDR5 网表** (DDR5TOP + clk_gen + ddr_phy(4×dq_io + SyncHsWrLvl) + dq_io(PwyCwlDec) + memctrl + ctrl_core + modereg)，保留真实层次形状（顶层→phy/memctrl 双分支→叶子）+ 真实信号名（CLK/DQ/WrLevelEn/MR2/MR3 = DDR5 write-leveling 标准信号）
- **合成 SV pattern** write_leveling_external1（testbench 例化 DDR5TOP dut，引用 5 个验证信号 + 局部 reg MR3_capture + 循环变量 i）
- 隐藏 B：LP6TOP 7-module，6-bit DQ，phy_unit(6×dqbuf)+WlSync+ctrl_unit/coreg/osc_clk，命名/结构/深度与 A 完全不相交（DQ 位数 6 vs 4、CLK paths 12 vs 15、ctrl 深度 2 vs 3）

## 判分牙设计（18 断言 a-r，subprocess-on-B + recompute-from-B）

- 核心正确性（f-j）：5 个验证信号的层次路径集合 == check 独立解析 B 网表重算的期望**精确匹配**（非文本相似、非子串）
- 反硬编码（m/n）：B 输出 + 候选源码（去注释）中零 A-only 结构 token（DDR5TOP/ddr_phy/X_PHY/X_DQ0..3 等，词边界匹配，避免 X_PHY 假匹配 X_PHYU）
- 只读约束（q）：源码不含 `open('w'/'a'/'x')`/`os.remove`/`shutil.rmtree`/`Path.write_text` 等写动作模式
- 退化守护（p）：空网表 → 优雅处理（无 traceback，出 JSON 或干净退出）
- 确定性（o）：3-seed md5(stdout) 一致
- zip 卫生（r）：submit.zip 不含 check.py/reference//hidden//.jsonl

## 与既有 D 域 case 区分

- r984 NetlistInstHierTrace（Verilog 网表 top-down 实例化父链追溯，给 module 名找完整 inst path）— 本案是 pattern 信号→网表层次路径列出（给信号名找所有出现位置），方向与对象不同
- r985 DQDbusBitMapReconstruct（DQ↔Dbus 位级映射参数推算）— 本案不做位级映射，只做信号名→层次路径
- r986 SchHierParentLocate（schematic cell 库反向查父，给叶子 cell 找顶层→叶子父链）— 本案是正向 top-down 列信号层次，且数据形态是 Verilog 网表（非 OA schematic 例化表）
- r988 Net2FsdbPathMapProduce（FSDB↔Netlist 信号 path 映射，透传 pin 剥离）— 本案不做 FSDB 地址透传剥离，只做 pattern 信号在网表中的层次路径列出

## 自验

- `candidate_ref.py` 在 A 上：top=DDR5TOP, modules=9, CLK=15 paths / DQ=6 / WrLevelEn=14 / MR2=4 / MR3=4
- `candidate_ref.py` 在 B 上：top=LP6TOP, modules=7, CLK=12 / DQ=8 / WrLevelEn=11 / MR2=3 / MR3=3
- `check.py selftest`：REF PASS 18/18 (a-r) + 3 negatives (empty_shell/print_expected/delcore) 全 FAIL
- `negative_selftest.py`：ref_pass=True, all_neg_fail=True
