# Deepread: sid_1794470666600_frplj (finesim_ignore_gen)

- **session**: 1794470666600_frplj · **user**: ynbai · **host**: 10.129.32.84 · **mc**: 302
- **domain**: schematic_netlist (netlist:4738; lvs:80; schematic:45; hspice:37; cmos:36)
- **nmsgs**: 485 · **user turns**: 21 · **trace size**: 1.78MB
- **trace_source**: real cline session, scp via .75→10.129.32.84

## 用户意图（逐轮）

- **U0** (核心 produce): 「写一个脚本，输入为netlist，输出为finesim ignore文件，脚本帮忙抓出来 XIctop.XI_Channel.XI_BnkGTopX4_Top.XI_BnkGTopX4_gut.XI_BnkGTop_AC.XI_D_RWCBG 下的所有instance的hierachy，只到下一级，例如 ...XI_D_RWCBG.XI_D_CasBnkGRptLR，输出到 .../finesim_ignore.list文件中，文件内容为 `.option finesim_ignore = "hierachy"` 例如 `.option finesim_ignore = "XIctop.XI_Channel...XI_D_RWCBG.XI_D_CasBnkGRptLR"` 下一行为下一个instance, netlist文件path为 .../netlist」
- **U1** (spec iteration): 「脚本内加一行，内部存在一个cell name为AbusEnRdCtrl，它对应到instance hierachy不包含在ignore文件中」—— 按 cell name（子电路名）排除
- **U2**: 「生成一个新的脚本，输出八个文件，按照 ...XI_BnkGTop_AC 这一层的hierachy区分，分别为 ...XI_BnkGTop_BD / ...XI_BnkGTop_GE / ...XI_BnkGTop_HF 还有 ...XI_BnkGTopX4_Bot... 下四个，区分为8个ignore文件」
- **U3**: 「脚本使用方法是什么」
- **U4** (包一层): 「把脚本再往上包一层，按照8个hierachy生成8个ignore文件，ignore范围为 ...XI_BnkGTop_AC 下除了 ...XI_D_RWCBG 外的其他cell，以及 ...XI_D_RWCBG 内除了 AbusEnRdCtrl 的其他cell，其他7个bnk同理」
- **U5** (embed): 「打算把该脚本嵌入到抽网表的脚本中...输出path固定...每次抽网表自动更新path下的8个ignore文件」
- **U6** (debug): 「为什么执行后会有输出8个文件是空的情况」

## 助手工具链

list_allowed_files → run_approved_command(readlink/head) → read_files(netlist) → SandBox_MCP_Server__run_code → editor 写 gen_ignore.py / search_subckts.py / gen_ignore_all.py → python-runner 验证 → 多轮 editor 修（文件腐蚀用 make_script.sh heredoc 绕过）→ read_files 验证输出 → cleanup.sh 清理。

## 关键技术发现

1. **目标 XI_D_RWCBG 是 instance（X 行）非 .SUBCKT 定义**：助手初版误判，后修正——先找 X 行，取最后一个 token（子电路名 = `D_RWCBG_DPMux`），再找 `.SUBCKT D_RWCBG_DPMux` 定义，提取其内部直接子实例。
2. **HSPICE `+` 续行**：X-instance 行跨多行，`+` 开头续行，须拼接后取最后 token 才是 cell name。助手初版把 pin 名 `LbusDQ1<7>` 误当 cell name，修正后正确拼接。
3. **只提取 X 行（子电路实例）**：subckt body 里的 R/C/M 器件不是 hierarchy，不进 ignore 文件。
4. **cell name 排除**：U1 要求按 cell name（X 行最后 token）排除 `AbusEnRdCtrl`，非按 instance name 排除。结果 1474 个 instance 中 1 个（XI679→AbusEnRdCtrl）被跳过，输出 1473 行。
5. **输出格式**：每行 `.option finesim_ignore = "full.hierarchy.path.child_inst"` ，一行一个。

## 合成计划

- **case_id**: EDA-Eval-DesignFlow-FinesimIgnoreGen-001
- **domain**: schematic_netlist
- **子类**: netlist-text-transform + spec-by-iteration（与 r622 UlvtDelvtoReducer / r621 SpiceCapMatchFilter 同族，新增 HSPICE 续行拼接 + subckt 定义回溯 + cell-name 排除 三维度）
- **SUT**: `gen_finesim_ignore.py` 纯 stdlib CLI `<netlist> <target_path> [--exclude <cell>] [-o <out>]`
- **visible A**: sample_A.sp — `XI_ROOT`→`SUB_ROOT`，5 个 X 子实例 + R/C/M 器件（gotcha: 只提 X 行），无排除 → 5 行
- **hidden B**: sample_B.sp — `XI_TARGET`→`SUB_T`，6 个 X 子实例含 `+` 续行(Xa3)，--exclude ExclCellB → 排除 Xa2/Xa5 → 4 行
- **hidden C**: sample_C.sp — `XI_LEAF`→`SUB_LEAF`，5 个 X 子实例，--exclude NandCellC → 排除 Xb2/Xb5 → 3 行（跨输入反硬编码，count 5/4/3 全不同）
- **check.py**: 16 cond a-p（内嵌独立 oracle 重新解析 netlist 自算非文本相似）
- **negatives**: 4 个 distinct labels (d/m/f/g)
- **test_rationale**: 16 条断言 ①-⑯
