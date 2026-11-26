# 深读笔记 · 1793839606322_bghqo

- **session**: `/home/e0039602/.cline/data/sessions/1793839606322_bghqo/` (新 cline 子目录格式)
- **user/host**: e0039602 / hfeg0pkn004 (10.129.2.13) / mc=338 (digital-leaning: 45 synthesis, 338 netlist, 11 schematic, 3 pyAether)
- **msgs**: 254 (1.7MB)
- **domain**: digital（标准单元库 Verilog 转写 + tb_family 族模板覆盖检查）
- **工作目录**: `/home/e0039602/Documents/verilog_lib_trans_v2`（含 tb_family skill: scripts/_familymap.py + 55 族模板 + skill_tools/rerun_*.py + merge_resultmap.py）
- **配套目录**: `/home/e0039602/Documents/netlist_change`（simlib_drcoa_stdcells.sv / block_name_*.log / final_merged_netlist_digitial.v 等）

## 用户意图轮（A 档候选）

- **#0** `请你将outputs当中的 result_map_20261104_202610_c0ef.txt文件，他是用python3 run.py --netlist .../final_merged_netlist_digitial.v --block-list .../block_name_digital.log --workers 6 这个命令跑出来的结果，使用目录下的tb_family skill，对他进行检查并重写错误的` —— 原始意图（check + rewrite，2 步，复杂）
- **#118** `试了下runStdCellTB, 报这个 # _FAIL_Report ## FAIL(DUT)...` —— 调试报错（用户给了根因报告，不适合作 A 档）
- **#123** `我刚给你的这个报错是外部的，请给我解释一下这个错误的原因就行` —— 纯解释请求
- **#125** `skill是怎么判断是否有匹配的族模板的` —— 解释请求
- **#129** `simlib_drcoa_stdcells.sv，请你用同样的方法检查一下tb_family是否可以全覆盖这里面的model` —— **本轮取（A 档 faithful）**：自包含的覆盖检查请求
- **#138** `看一下这个目录下的这两个log里：block_name_stdcell.log block_name_stdcell_ac.log，是否都能命中` —— 自包含但「命中」语义依赖上下文
- **#188** `刚刚不是说TB能检查PASS这里面的四十几个吗，你把这四十几个拿出来仿照AIout1105的格式写一个AIoutTBPass` —— 引用前文数量，上下文依赖
- **#220** `请你修改ruleprompt，增加上让他对这个类别也可以处理...` —— 用户已给根因（V2 才是对的），不适合作 A 档

## 本轮取 #129 的理由

- 提出需求 / 表达目标（检查覆盖率），未给根因或修复方案 → 符合 A 档选轮规则
- 交付物明确：覆盖率判定（能否全覆盖 + 命中/未命中数 + 族分布）
- 资产自包含：1 个 .sv + 1 个 family_map + 方法说明即可重建

## gold（msg #136/#137 助手真实产物）

- simlib_drcoa_stdcells.sv: 1578 module 定义行 / 去重 1529 唯一 model
- 命中族模板 1411，未命中 118（约 7.7%）
- 族分布：inv 457, nand2 164, nor2 83, dlyg2 80, buf 67, nand3 55, ffrq 55, latrq 51, nor3 37, ffsq 36, oai21 33, latsq 32, passgt 30, aoi22 29, latq 24, aoi21 24, inven 20, rsnand23 19, mxi2 15, ffsrq 13, mx2 12, invhiz 10, ffq 9, oai31 8, bufen 8, latrsq 7, mxi3 7, ... 
- 剥已知前缀（T_/AF_/CM_/DF_/D_/C_/R_/PWY_/IO_/DQSM1Count_）后再试，仅多命中 7 个，**最终 111 个始终无族模板**
- 未命中典型：cap_inv*/capinv*（去耦电容反相器，模拟类）、trim*/trimbuf*/trimnand2*（trim 延迟/脉冲）、split2_*（DQS 相位拆分）、DqsGating*、AF_latqn2_CmFsUnit、latnLVSx4_DP_pc60
- 用户接受结论：**不能全覆盖**（约 7.7% 缺口）

## _familymap.py 匹配逻辑（从助手脚本 #133/_coverage_check.py 与命中/未命中样例反推）

1. 解析 `^\s*module\s+(\w+)` 行
2. 可选剥前缀（strip_prefixes，长优先）
3. **最长前缀 + token 边界**：key 必须是名字的前缀，且 key 后紧跟字符**不是小写字母 a–z**（`latqY`→latq 命中；`latqn2`→latq 不命中，因 n 小写；`invenLx1`→inven 命中而非 inv，因 e 小写拒绝 inv）
4. 最长 key 胜出

→ 本轮 case 的 check.py 与 reference solution 即按此规则实现（15 条断言 a–o）。
