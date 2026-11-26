# Deepread — 1795066647351_jojdp (chuanqiz@hfeg0pnd001, mc95)

## 会话概览
- 126 msgs, 380KB, 6 user_input turns with text
- D-domain 命中: schematic:184 / analog:99 / virtuoso:388 / cellview:75 / cadence:24 / netlist:14 / synopsys:13 / verilog:9
- 工具链: virtuoso-cli (Cadence Python API eda.schematic/eda.general) + read_files + run_code

## 用户意图（真实任务）
用户在 DRAM analogIP 库下用 virtuoso-cli 读取定制延迟单元，做"输入输出逻辑关系"电路理解：
- U#0 (msg#0): virtuoso-cli command instructions（工具调用前置说明）
- U#19 (msg#36, ts=1795056569035): "读取analogIP library下的CustomDlyNcCtrlIP"
- U#30 (msg#58, ts=1795057057829): "能否给出输入和输出的逻辑关系？"
- U#36 (msg#70, ts=1795057848468): "忽略内部信号，能否给出输入和输出的逻辑关系？"（→ GOLD msg#71: CustomDlyNcCtrlIP 端口表 In/Out/OutN/cm1_ro_NcDly<4:0>, Out=In, OutN=¬In, cm1_ro_NcDly 仅配置延时）
- U#37 (msg#72, ts=1795065599943): "忽略内部信号，CustomDlyPulse200nsVbnVbpCtrlBIP这个cell能否给出输入和输出的逻辑关系？"（→ GOLD msg#91: CustomDlyPulse200nsVbnVbpCtrlBIP 端口表 In/Out/OutN/Dly200nsCap inputOutput, 数据通路 In→I5→I13→InBuf→I1→I28(nor2)→net5→I2→net05→I10(nand2)→OutN→I9(inv)→Out, 布尔推导吸收律 OutN=¬In/Out=In, Dly200nsCap 200ns 脉冲成型稳态被吸收）

## 选料判定
- **真实意图**: analogIP 电路单元"输入输出逻辑关系" explain-Q&A（忽略内部信号，顶层端口视角推导稳态布尔关系）—— 11-15 用户令 §二明确恢复 analysis-Q&A / explain 类为可造
- **A-faithful 选轮**: U#72（CustomDlyPulse200nsVbnVbpCtrlBIP）—— 单一干净 "提出需求" 用户轮，未给出根因/修复方案
- **GOLD**: assistant msg#91 完整结构化分析（顶层端口表 + 数据通路 + 布尔推导 + 真值表 + 延迟端口说明）
- **可证伪 check**: 8 键结构化提取 + B cell_name/top_ports/truth_table 精确匹配 + 反硬编码 + 确定性
- **会话覆盖两个相关 cell**: CustomDlyPulse200nsVbnVbpCtrlBIP(A) 与 CustomDlyNcCtrlIP(B)，结构同构 token 不相交 —— 天然 A/B 双轨

## 合成方案（B-grade synthesized-reframe）
- A = customdly_iologic_explain_A.md（8-section markdown 手册，CustomDlyPulse200nsVbnVbpCtrlBIP 真实端口名 Dly200nsCap + 真实门级 I5/I13/I28/I2/I10/I9 + 真实 net5/net05/InBuf + 真实布尔推导吸收律 + 真值表）
- B hidden = customdly_iologic_explain_B.md（同 8-section 结构，CustomDlyNcCtrlIP + cm1_ro_NcDly<4:0> 数控延迟码 + switch/RNPDIFF3t 电阻梯 + NcInvA/NcInvB/NcBuf/NcOutB0/NcInvOut/NcSplit/NcRCLadder/NcDlyDecoder，与 A token 完全不相交）
- reference = iologic_explain_parser.py（通用 markdown 结构解析 → 8 键 JSON，无硬编码；纯 regex/section/table/code-block 解析）
- check.py 12 断言 a-l：zip+py / py_compile+size / A 8键 / B 8键 / B cell_name 正确+反泄露 / B top_ports 4个齐 / B data_path 长度+箭头 / B boolean_derivation 长度+In/OutN/¬ / B delay_port_note 长度+延迟关键词 / B truth_table 稳态2行 / 反硬编码 B 无 A-only token / 3-seed md5 确定性
- 3 negatives: empty_stub / print_only_hardcode_B / partial_parser(删 top_ports+truth_table)

## 自验结果
- reference 12/12 PASS on B
- 3 neg ALL FAIL (ALL_NEG_FAIL=True)
- 3-seed deterministic
- k_rationale == k_check == 12 ≥ 8 ✓
- jsonl test field sha256 == disk check.py sha256 ✓
