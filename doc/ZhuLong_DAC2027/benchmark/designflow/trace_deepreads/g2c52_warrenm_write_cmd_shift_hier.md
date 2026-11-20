# deepread: 1795139735709_g2c52 — warrenm@hfeg0pgn145 — DRAM Write CMD Shift netlist hierarchy

- session: 1795139735709_g2c52.messages.json (924KB, 222 msgs, mc=247)
- user: warrenm  host: hfeg0pgn145  domain: schematic_netlist (D-pure netlist:1049/schematic:446/cmos:413/lvs:241/verilog:172/analog:57)
- agent: lead (cline)

## user inputs (15)
- U#1-2: hello world C/Python (throwaway warm-up)
- U#3: "给我说一下writeleveling是怎么训练的，给我查询cimi知识库后回答" (Q&A)
- U#4 (A-faithful 选取轮): "/proj/drgqa/V0/simdir/verilog/warrenm/verilog.ddr5.drgqa.test/netlist/V0_WOWTOP_2026Sep1.151806/ 结合这个文件夹中netlist文件，和cimi知识库中的文档，给我说一下Write CMD Shift电路的层次结构，并说一下这里模块的作用"
- U#5-6: "可不可以把这个脚本封装为一个skill，对于不同的网表进行解析呢" / "继续做"
- U#7-8: "给我找到关于ECC" / "ECC编码和读纠错模块"
- U#9: "skill的功能是要把要找的模块的层级结构和该模块的具体功能列出来就可以了，不需要列出路径中所有模块的功能"
- U#10: "skill对任何文件没有写的权利，只有读的权利"
- U#11: "红线补充到所有你写的脚本中"
- U#14: "给我找到关于ECC数据纠错的模块"
- U#15: "给我找到Ysa的模块"

## assistant work
- msg#18-24: cimi-kb-search 检索 JESD79-5C.01 LPDDR5 规范, 整理 writeleveling 训练原理
- msg#26-78: 9 轮 probe*.py 解析 40MB Aether emy2netlist Verilog 网表 (3963 module), 回溯父-子实例化关系, msg#78 给出 Write CMD Shift 完整层次链:
  WOWTOP → DDR5TOP → Channel → BCenter → BCenterCA → Controller → D_WrLatencyCtrl → D_WrPwy → D_PwyCmdShift(odd/even) → D_PwyCmdShiftEob → D_PwyDFF4
  + 各模块作用 (D_WrCwlDec/D_WrCwlWrlvl/D_PwyCmdShiftEob/D_PwyCmdShiftP4Ck/D_PwyShiftReg/D_ExtWrCmdShift/D_PwyShiftDFF4N/D_PwyShiftLAT/D_WrEOCtrl/D_CmdDiv2/D_CmAdjWrDrvOnDly)
- msg#80: 确认可封装为 skill
- msg#82-107: skill-creator 规范封装 analyze_hierarchy.py (--keyword/--module/--down), 验证复现原分析, 修 --down depth bug, 落 netlist-hierarchy-analyzer skill (只读)

## synthesized-reframe (本题)
- 真实 40MB NFS Verilog 网表 + cimi JESD79-5C KB → 沙盒不可访问
- 紧凑 21-module fixture 保留真实 DRAM Write CMD Shift 命名 + function_db_A.json (替代 cimi KB)
- produce-script analyze_hierarchy.py: --netlist --keyword --function-db -o, 输出 hier_report.json (keyword_tokens/total_modules_scanned/matched_modules[name/function/port_count/parent_chain/sub_instances]/summary)
- 关键词匹配: 自然语言 token 归一 (cmd->command), 模块命中 = (name+function) 小写包含全部 token
- hidden B: SERDES Align 层级 (命名完全不相交), keyword "SerDes Align"
- check.py 17 断言 a-q, 独立 _gt_parse/_gt_tokenize/_gt_parent_map/_gt_chain/_gt_match 重算, anti-hardcode (A-only/B-only token), 3-seed, A 报告核对
- 自验: ref 17/17 PASS on B, 3 neg (empty/print_expected/core_deleted) 全 FAIL, §4.9 三假全 FAIL, k_check=k_rationale=17>=8 GATE PASS

## 与既有 D 域 case 互补
- r1022 HierNodeConnTraceProduce: 单层级节点 depth-N 前后连接关系递归追溯
- r1017 SignalConnCheckProduce: 全信号扁平连接性表 (driver/load, ND/MD/NL/OK)
- r1016 DecoderLogicNetlistProduce: n-to-2^n 译码器门级网表合成
- 本例 r1027: 按自然语言关键词检索模块 + 顶层→自身 parent_chain + 直接例化 sub_instances (模块级层次检索, 非节点/信号级)
