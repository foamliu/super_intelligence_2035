# Deep-read: 1793785648416_8go01 — stdcell PASS module splice

- user: e0039602 @ hfeg0plg103
- session_file: 1793785648416_8go01.messages.json
- match_count: 248 (167 msgs, 6 real user prompts, 82 tool calls)
- domain: schematic_netlist (stdcell netlist→SV conversion verification flow)

## Project context
verilog_lib_trans_v2: stdcell Verilog netlist → SystemVerilog 转换验证流。
- run.py 把 final_merged_netlist_*.v 里缺失的 stdcell 实例按 cell 名前缀机械转成 base 单元
- tb_family skill: 一组「族模板」tb_<family>.sv + FamilyMap(三层命中 families_index.json→前缀规则→兜底 NO_TBRef) + _run_one_shot.py(构建 TB + xrun 仿真对拍)
- 产出: AIout1104.sv(全 PASS 879 module) / AIout1104_true.sv(一次通过 843) / AIout1104_retrue.sv(改写后通过 36) / result_map_final_20261104_879.txt(最终报告 PASS=879 NODUT=4 移除)

## Real user turns (6)
1. **[0]** 给 8 个 ff 模块(ffrsq 族 4: ffrsqDSx1/ffrsqLVx1_pc60/ffrsqLx1/ffrsqLx2; ffsq 族 4: ffsqIOLVx1/ffsqLVSx2_pc60/ffsqLVx1/ffsqLVx2_pc60)，刚从 AIout110401.sv 移除并替换成 pass 门级版本。要在 result_map_final_20261104_879.txt 里找这 8 个，用 tb_family 判断是否 PASS(不用改，告诉结论)。→ 解析报告:全部 879 PASS/4 NODUT 移除，8 个均 PASS。
2. **[43]** 把这 8 个 pass 的拼接到 AIout1104_true.sv(843，缺这 8 个)。→ 从 AIout1104.sv(879，含 pass 门级版)取 8 个门级块(inv_base/fbr_base/aoi21_base/trireg/notif0/notif1 无 always/assign)追加到 true.sv 末尾，备份后结果 851 module 无重复，块格式 celldefine/endcelldefine + 空行分隔。**← 选作 case 的 produce turn**
3. **[73]** 找 AIout_retrue 里有哪些 model(应含上面 8 ff)，去掉这 8 ff 返回余下名字。→ retrue 36 model，去 8 ff 余 28(and2Lx2/and2Lx4/dlybias*/dlybiasn*/or2*/or3*/xnor2*/xord2*)。
4. **[83]** 用这 28 名字在 simlib_stdcells_ac_copy.sv 找对应 model，用 tb_family_skill 测是否 pass。→ 跑 xrun: 21 PASS / 7 MISMATCH(全是 dlybiasn*，模板极性假设 Y=~A 但 DUT 非反相)。
5. **[128]** Q&A: 解释 `buf #(0,250)(Ain_tmp,A); nmos/pmos/dlyrc_base` 片段功能。(非 produce)
6. **[130]** 读 wellesc 的 tb_family/skill.md 对新 tb_dlybiasn 的介绍，写进本项目 tb_family skill.md。(文档更新，非 produce)

## Why turn [43] chosen as case
- 干净 produce(确定性文本拼接，可独立判分)，不依赖 xrun/仿真/私有库
- 与已有 e0039602 stdcell case 区分: CellMap(映射变换)/StdcellRerunCollect(错误收集)/StdcellStatusPartition(状态分区)/StdcellDetConvert(确定性转换)/TbFamilyResultVerify(族验证)/GateLibResultMapFilter(白名单过滤) — **拼接/合并维度未覆盖**
- 反硬编码自然: A(ff 族 12/8/4-splice) vs B(dffrq/dffsq/latchRS/trireg 族 15/10/5-splice + already_present + not_in_source) 名/数/分支全不同

## Synthesized case design (B-grade)
- case_id: EDA-Eval-DesignFlow-PassModuleSplice-001
- SUT 交付 splice_pass_modules.py(--source/--target/--targets/--outdir)
- 可见 A: AIout_allpass_A.sv(12 门级)/AIout_oneshot_A.sv(8)/targets_A.txt(5: 4 splice + 1 already_present=invDSx1)
- 隐藏 B: AIout_allpass_B.sv(15)/AIout_oneshot_B.sv(10)/targets_B.txt(7: 5 splice + 1 already=mux2Lx1 + 1 not_in_source=fakeNonExist)
- check.py 12 条件 a-l: zip+compile/跑通B产两件/含全spliced/计数对/保留原始+顺序/无重复/门级(含base原语无always/assign)/report字段全对/celldefine包裹/反硬编码A/3-seed字节稳定/cross-input名不相交
- 自验: ref PASS 12/12 + 5 neg(3 three-fake: empty/print/core-deleted + 2 naive: hardcode-A/append-all)全 FAIL，distinct 条件 b/c/h
- D.jsonl 288→289, ledger_D case 285→286
