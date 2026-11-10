# trace_deepread: icxnw (1793670308844_icxnw)

- **session**: 1793670308844_icxnw.messages.json · e0039602 @ hfeg0pkn002 (10.129.2.11) · mc=271
- **keywords**: verilog:634; lvs:383; netlist:322; drc:65; schematic:14; transistor:9; rtl:6
- **size**: 210 msgs / 110 user / ~1.84MB · 项目 verilog_lib_trans_v1.4.2
- **real user turns**: U#0(问 resultmap 写入时机 Q&A) / U#11(问 prompt-only Q&A) / U#14(prompt 把 simlib 模块和示例混在一起, AI 分不清) / U#21(核心 produce: 总结 simlib_base 模块功能列成表格写在「可供实例化物理单元」节开头, 再列积木实现, 最后 fewshot) / U#109(问 prompt 第 5/6 部分)
- **助手工具链**: 大量 read_files/search_codebase 探查 rules_prompt.py / rules_prompt02.py / simlib_base.sv; m80-m205 反复 editor 改 rules_prompt.py / rules_prompt02.py(插入模块功能摘要表、重排 §0-§7 规则 / Building Block Catalog / fewshot 顺序); m94 写 list_modules.py(5 行 regex 提取 module 名); m84-m93 run_approved_command 跑 list_modules.py 输出「解析出 6 model: aoi21DSx1/nand2CS/nand2CSx1/mx4DSx1/nor2DS/rsnor22DSx1 行号」; m149-m167 写 test/check_syntax.py + test_prompt_structure.py 验证 prompt 结构
- **核心意图**: 把 simlib_base.sv 的积木单元解析成**功能目录**(模块名 + 功能分类 + 端口 + 实现), 写进 prompt 的 Building Block Catalog 节, 让 AI 转换 agent 明确能调用哪些积木
- **本 case 取**: U#21 的「解析 simlib → 模块功能目录」子任务(确定性、可自包含), 弃 prompt 模板重排(散文式、不可判分)和 Q&A 轮
- **私有不可复刻**: /home/e0039602/Documents/verilog_lib_trans_v1.4.2 项目目录 + simlib_base.sv 原文 + xrun/tb_family 流 → B-grade synthesized 自包含
- **与既有 D case 非重复核验**: focjw NetTypoScanReport=查 undeclared net(lint), focjw CellFamilyMatch=族类名称配对, jt7be GateLibResultMapFilter=门库 resultmap 过滤, s9bc9 StdcellDetConvert=stdcell 检测转换, r2yjr TbFamilyMergeConverted=合并转换网表; **本 case=模块功能目录生成(解析+分类+端口+时序检测+实例计数→catalog.json+summary.md)**, 产物/机制/状态空间全不同
