# trace_deepreads/nr884_redbist_flow_recon.md — thomas1w redbist LPDDR5 BIST 流程重建

## trace 元信息
- session: `1793603150610_nr884` · user: `thomas1w` · host: `hfeg0pkn005` (10.129.2.14) · mc=159
- model: deepseek-v4-flash · cwd: /home/thomas1w · 163 msgs · 1.2MB · 2026-11-02
- keywords: verilog:936;netlist:292;cmos:89;rtl:53;schematic:38;aether:30;systemverilog:19;analog:16
- tools profile: netlist-dominant + verilog → digital-lean, 干净 A-faithful 候选

## USER 干净需求轮（A-faithful 候选，均非根因/修复）
- USER#1 (msg 0) 逐字：「/rundata/.../V0_WOWTOP_2026Oct29.172927/netlist  这是chip的网表，看下redbist的测试流程和数据流行，怎么产生测试期望值，记忆错误的地址」← 本 case 选用
- USER#37 (msg 68)：「这个是我的测试用例，我现在要在注错之后，对错读的地址进行检查，但是我这里的注错是随机给的，这个用力用过怎么给出错误地址的期望值」
- USER#59/65/74/75/86：均追问 ROW/COL 地址如何得到、注错如何做（需求/目标，非修复）

## assistant 重建结论（trace 末尾用户接受的分析）
1. **网表**：51MB 扁平化 post-layout LPDDR5 DRAM 网表，~6099 modules，片上 Memory BIST 只有网表无 RTL。
2. **两套 BIST**：
   - 主 BIST `mBist`：mBistTop(435549)→mBistCmdGen(428287)+Bistwritedata(433990,期望值生成器)+mBistPat(431536)+mBistAddrGen(429898)
   - 冗余 BIST `RedBist`：RedLatBistTop(428137)→RedLatBistPat(426612)+RedBistAddrGen(425506)+RedBistCounter(424226)+RedBistRACnt/BACnt/RdCACnt
   - 集成 BistBlock(436162)+BistOscNew(422801)+BistSel(435962)
3. **测试流程**：TS reg(cm0_ts_*/cm1_ts_*) 配置 → BistSel 选通 + BistOscNew 出 BistClk → FSM 按 ACT→WR→RD→比较→PRE→REF 遍历，两遍 + 保留测试。
4. **注错机制**（TM_RedBist.sv，613 行，30853B，real path /proj/ddgoa/V0/workdir/thomas1w/sos_manage_lpddr5/.../cmds_testmode/TM_RedBist.sv）：
   - `col_single_bit_force`(行366)：路径模板 `...I_Array1GBK<bk>.I_m<ydec>Meg_YS_<fn>.I_ColRedBlock384_5.I_ColRed12_S<colred>.I_ColRed<cr>.I_ColRed2New_<v3>.I_latqLx1_0_<col_lat>_.net025`
   - `row_single_bit_force`(行502)：`...I_BankTopX2B<bg>.I_BankLogic_17.I_RowRed768.I_RowRed_S<rowred>.I_RowRed2_S<rowred2>.I_RedLatCom_S<latcom>_<row_lat>_.Out`
   - 多比特：rcsl_1_force(ColCom8)/rcsl_8_force(FzCPN0)/rwl_8_force(Mn1)
   - redbist_force_always_err：全 bank RowRedFailEn=1
5. **RandForce 类**(行257)：colred[0:30偶]/cr[1:2]/v3[0:6]/col_lat[0:15] | rowred[0:7]/rowred2[0:23]/latcom[0:1]/row_lat[1:15] | arr(arr_W/arr_E)/bk/ydec/fn/ccr/bg/bt
6. **期望值机制（核心洞察）**：期望错误地址 = rdf 这组随机坐标解码出的 location，force 注错不会打偏 → 留住 rdf 即有期望值。
7. **错误计数**：Col_Single_Error_Count_Read / Row_Single_Error_Count_Read 按 bank hex 分 4 组(err_bk[4])，MRR_Exp(.ma(MR112..MR115)) 回读；redbist_common_task(行538) 带 rdf 调用。
8. **fuse 映射（已废弃）**：col_fuse_table/row_fuse_table + fuse_mapper_col/row.py → fuse_commands_*.sv；USER#59/74 明确已舍弃，注错改为 net-level single/multi-bit force。

## A 资产重建（faithful，从 trace 真实结构 + msg114 真实 SV 内容）
- tm_redbist_A.sv：Col_Single_Error_Count_Read(真实，MR112-115, err_bk[4], bank hex 2/0/F/D|A/8/7/5|3/1/E/C|B/9/6/4) + Row_Single_Error_Count_Read + col/row_single_bit_force(真实路径模板) + rcsl_1/8/rwl_8 + redbist_force_always_err + RandForce 类(真实范围) + redbist_common_task
- netlist_bist_modules_A.txt：真实模块名+行号 (mBistTop 435549, RedLatBistTop 428137, BistBlock 436162, ...)
- tm_redbist_run_A.txt：rdf.randomize()→col/row_single_bit_force→redbist_common_task 序列

## hidden B（结构对立，Gen2 变体 LPDDR6 32-bank/8 组）
- 模块名全改 G2 后缀；路径模板 I_ColRedBlock512_7/I_ColRed16/I_RowRed1024/I_BankLogic_31
- RandForceG2：colred[0:46:even]/cr[1:3]/v3[0:8]/col_lat[0:31] | rowred[0:15]/rowred2[0:47]/latcom[0:3]/row_lat[1:31]
- MRR MR116-123, err_bk[8], 8 bank groups, redbist_common_task_g2
- A/B 在所有关键字段（模块名/路径模板/类名/字段范围/MRR/bank_groups/common_task）全对立

## case 交付
- RedBistFlowRecon-001 (digital, A-faithful, L1-static, 16 conds a-p)
- 交付 redbist_flow_recon.py + redbist_flow.json，check subprocess 真跑候选于隐藏 B
- 自验：ref PASS 16/16 + 5 negs FAIL NEG_RC=0 + §4.9 三假 FAIL + jsonl test roundtrip PASS + A≠B anti-hardcode
