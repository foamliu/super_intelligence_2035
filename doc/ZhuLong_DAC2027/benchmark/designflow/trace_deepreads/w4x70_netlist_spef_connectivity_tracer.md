# 深读笔记 — w4x70 (netlist/SPEF connectivity tracer for back-annotation debug)

## 元数据
- **session_file**: 1788172501150_w4x70
- **host**: hfeg0pkn003 (10.129.2.12)
- **user**: haoyut (脱敏；与 82ybr 同用户，DRAM STA signoff 工程师)
- **match_count**: 764 (keywords: netlist:1394;cmos:269;virtuoso:214;analog:171;schematic:94;transistor:62;synopsys:44;dbopencellviewbytype:38)
- **file size**: 3,116,440 bytes (3.1MB)
- **messages**: 1181 total (596 user / 585 assistant) / 551 tool_use (run_commands 446 / read_files 54 / editor 51) / 551 tool_result
- **real user messages**: 45
- **domain**: analog_context (netlist/SPEF connectivity tracing for parasitic back-annotation debug；与 82ybr 同域但不同任务角度)
- **date range**: 2025-08-31 ~ 2025-09-07 (session mtime)

## 用户完整工作过程（5 阶段）

### 阶段 A：环境全景 + 反标报告分析（msg 1-100）
- 用户在 `/proj/iejoad/V0/simdir/verilog/haoyut/verilog.pim.iejoad.AIagent/AI_spef` 工作
- 目标：研究如何通过读取 cvps(SPEF) 文件和 netlist/pt_dir 下的网表，结合反标报告中的未反标 pin/net，提取对应 SPEF 和 netlist 信息，用同样的 hierarchy 结构表现形式对比，针对不同反标 error 有不同分析结果
- agent 探查目录结构 → 找到 parasitics_command.log / netlist_pt / DRAMTOP.spf.TYP_98.cvps
- **PARA error 类型统计**（parasitics_command.log，PrimeTime U-2022.12-SP5）：
  - PARA-162: 101 · PARA-124: 101 · PARA-044: 101 · PARA-043: 101 · PARA-003: 51 · PARA-040: 50 · PARA-004: 14
  - 每类最多显示 100 条，但实际 10000+ 条反标失败
  - PARA-043 = 耦合电容 invalid capacitor (pin not connected to net)
  - PARA-044 = pin 未连 net
  - PARA-124 = net 找不到
- error 示例：`Error: Invalid capacitor (I_Array16GTop/.../I34_1_:A2 5.29591e-06) on net .../ACLevelA[1]: Pin '...I34_1_/A2' is not connected to net`

### 阶段 B：netlist 层级连接关系提取（msg 100-300）
- 用户给一个节点名（如 `I_Array16GTop/I_Array8G_SC1/I_Array2GB_SC1/I_ArrayCtrlX2B23/I_BankTopX2/I_CMAryB_222/I34_1_`），要求还原前后连接关系
- agent 解析 netlist_pt（结构化 Verilog，1770 modules），索引 module/instance/pin/net
- 查找 instance 的 port 连接（`.A(net017), .B(net014), .Y(net016)`），向上追溯 driver pin，向下追溯 load pin

### 阶段 C：net_tracer 工具构建 + 格式迭代（msg 300-700）
- 工具版本演进：annot_analyzer.py → net_tracer_v4.py → net_tree_v5.py → net_tree_v6.py → net_trace.py
- **格式迭代**（用户反复要求优化可视化）：
  - v1: `I1(nor2GFLx4).Y --> [net016] --> I163(nand2PFLx2).Y --> [net017] --> I25(invGFLx4).Y`
  - v2: 倒序（driver 在左）：`I25(invGFLx4).Y --> [net017] --> I163(nand2PFLx2).Y --> [net016] --> I1(nor2GFLx4).Y`
  - v3: 加 pin 名：`.A(net_62) --> .B --> [RRH12N[1]] --> I25(invGFLx4).Y --> .A --> [net017] --> I163(nand2PFLx2).Y`
  - v4（最终）：`UPSTREAM (left=driver, right=target)` + `DOWNSTREAM` 分段，`.A(net_62) --> I25(invGFLx4).Y --> [RRH12N[1]] --> .B --> I163(nand2PFLx2).Y --> [net017] --> .A --> I1(nor2GFLx4).Y`
  - 用户还要求斜杠树形（`/` `\\` 分支），但最终认可 --> 链式格式
- **输出格式**（最终版）：
  ```
  [tree] indexing ... 1770 modules
  ======================================================================
  TRACE: RowRedComp64/net016
  Module: RowRedComp64  Depth: 3
  ======================================================================
  UPSTREAM (left=driver, right=target):
  ----------------------------------------------------------------------
    .A(net_62) --> I25(invGFLx4).Y --> [RRH12N[1]] --> .B --> I163(nand2PFLx2).Y --> [net017] --> .A --> I1(nor2GFLx4).Y
  DOWNSTREAM (left=target, right=load):
  ----------------------------------------------------------------------
    [net016] --> I1(nor2GFLx4).Y --> ...
  ```

### 阶段 D：SPEF vs netlist 连接对比（msg 700-1000）
- 用户要求用 SPEF 也生成一版连接关系，与 netlist 对比
- 用户关注的不是 SPEF 的 RC 值，而是 SPEF 中的连接与 netlist 是否对得上
- agent 用 extract_spef.pl 提取 SPEF 连接 → 与 netlist 连接对比
- SPEF = Synopsys StarRC 生成（merge trivial 节点），netlist = Cadence SI 完整层级 → 名称对不上（与 82ybr 同一根因）

### 阶段 E：Virtuoso 集成 + 完整 hierarchy（msg 1000-1181）
- 用户要求用 Virtuoso 打开对应位置的 view 并 probe net016
- 用户要求输入完整 hierarchy（`DRAMTOP/I_Array16GTop/I_Array8G_SC1/.../I_RowRedComp64_17/net016`）
- 用户发现工具未显示完整 hierarchy，要求从顶层 DRAMTOP 开始
- 讨论 netlist_pt vs 普通 netlist 的区别（specify specparam CDS_LIBNAME/CDS_CELLNAME）

## 关键技术点（case 牙齿来源）

1. **结构化 Verilog 解析**：parse `module X (ports); ... instance_name cell_name ( .pin(net), ... ); endmodule` → 建立 module→instance→pin→net 索引
2. **net 连接追踪**：
   - 给定 net name → 找所有连接该 net 的 instance.pin → 对每个 pin 判断是 input(上游) 还是 output(下游)
   - 上游：output pin(net) → 该 instance 的其他 input pin → 各 input pin 连的 net → 递归
   - 下游：input pin(net) → 该 instance 的 output pin → output pin 连的 net → 递归
3. **cell type 识别**：从 `instance_name cell_name (...)` 提取 cell（如 invGFLx4/nor2GFLx4/nand2PFLx2）
4. **bus 位处理**：`RRH12N[1]` vs `RRH12N` 需要分别处理（bit-level vs bus-level）
5. **hierarchy 路径解析**：`DRAMTOP/I_Array16GTop/.../I_RowRedComp64_17/net016` → 逐级 resolve module → 在 leaf module 内搜 net
6. **PARA error 分类**：按 PARA-xxx 编号分类统计 + 提取每类的 net/pin 信息

## case 提炼方向（下轮合成）

- **task_id**: EDA-Eval-DesignFlow-Analog-001 (analog_context 域首条 proper)
- **domain**: analog_context
- **prompt 要点**：给一个结构化 Verilog 网表（DRAM fragment，~30 modules，含 invGFLx4/nor2GFLx4/nand2PFLx2 等标准单元）+ parasitics 反标错误日志（PARA-043/044/124 各若干条）。要求：(1) 构建一个 Python 网表连接追踪器，给定分层 net 名 + 深度 N，输出上下游连接链（pin→instance(cell).pin→[net]→... 格式）；(2) 汇总反标错误按 PARA-xxx 类型分类。交付 net_trace.py + sample_output.txt + error_summary.txt，打包 outputs/submit.zip。
- **attachments**（合成脱敏）：
  - `dram_fragment.v` — 合成结构化 Verilog（~30 modules，真实 cell 名 invGFLx4/nor2GFLx4/nand2PFLx2/aoi21PFDx2_H 等，含 bus bits）
  - `parasitics_command.log` — 合成反标日志（PARA-043/044/124 各 ~10 条，含 hierarchy net 路径 + pin 名 + 错误描述）
  - `task_brief.md` — 任务说明 + 输出格式要求 + 约束
- **entry_point**: `outputs/submit.zip`（内含 net_trace.py / sample_output.txt / error_summary.txt）
- **test 思路**（Python 双参 check(deliverable, workdir)）：
  1. 解 zip 校验 3 文件齐全
  2. net_trace.py 可执行（python3 -c import 语法检查）+ 用附件 dram_fragment.v 实跑 `--net RowRedComp64/net016 --depth 3` 验退码 0
  3. sample_output.txt 含 `TRACE:` / `UPSTREAM` / `DOWNSTREAM` 段头 + `-->` 连接链 + cell type 在括号内（`I1(nor2GFLx4)`）
  4. 连接链正确性：net016 的 driver = I1(nor2GFLx4).Y，上游 net017→I163(nand2PFLx2).Y→net016，net014→I0(nand2PFLx2).Y→net016（断言具体 instance/cell/net 名匹配）
  5. error_summary.txt 含 PARA-043/044/124 分类 + 各类计数 + 至少 1 条样例 net/pin
  6. bus bit 处理：`RRH12N[1]` 和 `RRH12N[0]` 分别出现在连接链中（非合并为 RRH12N）
  7. hierarchy 解析：支持完整路径 `DRAMTOP/.../RowRedComp64/net016`（非仅 leaf module 名）
- **test 牙齿**（区分 naive 与正确）：
  - naive 只列 instance 名不带 cell type → FAIL(3)
  - naive 只追单方向(只 upstream 或只 downstream) → FAIL(3)
  - naive 不处理 bus bit（RRH12N[1] 合并为 RRH12N）→ FAIL(6)
  - naive error_summary 只计总数不按 PARA-xxx 分类 → FAIL(5)
  - naive 不支持完整 hierarchy 路径（只搜 leaf module）→ FAIL(7)
  - naive 连接链不含 pin 名(.A/.B/.Y) → FAIL(4)

## 脱敏要点
- user: haoyut → hash
- 路径: /proj/iejoad/V0/simdir/verilog/haoyut/... → /proj/PROJECT/V0/simdir/...（去人名）
- host: hfeg0pkn003 → 保留（溯源）
- cell 名: invGFLx4/nor2GFLx4/nand2PFLx2/aoi21PFDx2_H → 保留（真实标准单元名，非 PII）
- 设计名: DRAMTOP/LOGICTOP/RowRedComp64 → 保留（通用 DRAM 结构名，非 PII）
