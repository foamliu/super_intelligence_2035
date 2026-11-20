# 深读笔记：1793864423469_6c7d2 — DecoderNetlistGen-001

- **session**: 1793864423469_6c7d2
- **user**: sinanz @ hfeg0pkn005 (10.129.2.14)
- **host**: hfeg0pkn005
- **match_count**: 322
- **domain**: schematic_netlist
- **messages**: 226 msgs, 1.37MB
- **session path**: /home/sinanz/.cline/data/sessions/1793864423469_6c7d2/1793864423469_6c7d2.messages.json (目录式存储)
- **grade**: B（真实输入 /proj/trgqa/V0_die2 与 /rundata/trgqa 私有 Permission denied 不可附加 → synthesized spec-driven 生成器）

## 真实任务摘要

用户 sinanz 在 Aether 设计项目里用 pyAether 脚本搭建译码器电路并导出 SPICE 网表，再生成 finesim stimulus deck。标准单元库 `stdcells_ac` 可用单元：invLx1 / and2Lx1 / and3Lx1 / nand4Lx1（**无 and4Lx1**，所以 4-to-16 译码器必须用 nand4Lx1 + invLx1 还原）。

## User turns（关键多步 produce）

- **U#0**: "建 3-to-8 和 4-to-16 译码器电路" — CLEAN PRODUCE 起点
- **U#56**: 3-to-8 修正（用户指出错误）
- **U#96→U#135**: 4-to-16 调试 — 因 stdcells_ac 无 and4Lx1，改用 nand4Lx1+invLx1 实现（36 单元 = 4 inv + 16 nand + 16 inv_out）
- **U#161**: 用户要求看网表（dmExportNetlist）
- **U#170**: 加 pin
- **U#196**: 网表正确确认
- **U#208**: 从 input.sp 例子生成 finesim stimulus deck

## Assistant 工具调用

- pyAether run_code: build_decoder_3_8.py（3-to-8 = invLx1 + and3Lx1，11 单元）
- pyAether run_code: build_decoder_4_16_v3.py（4-to-16 = invLx1 + nand4Lx1 + invLx1，36 单元）
- dmExportNetlist: 导出 SPICE 网表查看

## 译码器结构细节

- **3-to-8**: invLx1(3) + and3Lx1(8) = 11 单元。gate pin 顺序 MSB-first：`IAND0 and3 nA2 nA1 nA0 Y0`（A=nA2=MSB literal, last=nA0=LSB literal, Y=Y0）
- **4-to-16**: invLx1(4) + nand4Lx1(16) + invLx1(16) = 36 单元。nand 产 nYk，inv 还原 Yk
- **power nets**: vcc!/vss! 每个实例都带
- **instance naming**: IINV/IAND/INAND/IOUT（前导 X 为 SPICE subckt 实例前缀）

## A-faithful 不可行原因

真实工作目录在 /proj/trgqa/V0_die2 与 /rundata/trgqa，从 .75 ssh 访问 Permission denied 不可读，无法附加真实 spec/网表作为 A 输入。

## 合成方案（B-grade synthesized L1）

spec-driven 结构级 SPICE 网表生成器：
- **gen_decoder_netlist.py** --spec <spec.json> --outdir <dir> → netlist.cdl
- spec.json schema: name/n_inputs/mode("and"|"nand_inv")/inv_cell/out_cell/nand_cell/inputs(MSB-first)/outputs/power_nets/instance_prefix
- 真值表 literal: bit i of k = 1 → Ai, = 0 → nAi
- mode "and": N inv + 2^N out-AND（Yk = AND(literals)）
- mode "nand_inv": N inv_in + 2^N nand + 2^N inv_out（nYk = NAND(literals), Yk = NOT(nYk)）
- gate pin MSB-first 匹配 trace

## 隐藏输入（反硬编码五轴）

- **A** (spec_a.json, 可见 SUT): 2-to-4, mode=and, and2Lx1+invLx1, 6 inst
- **B** (hidden/spec_b.json): 3-to-8, mode=and, and3Lx1+invLx1, 11 inst
- **B2** (hidden/spec_b2.json): 4-to-16, mode=nand_inv, nand4Lx1+invLx1, 36 inst
- 五轴: 不同 n_inputs(2/3/4) + 不同输出数(4/8/16) + 不同模式(and/nand_inv) + 不同门 master(and2Lx1/and3Lx1/nand4Lx1) + A-run≠B-run

## check.py 16 条件 a-p

a(防泄漏+py_compile) b(B exit0+netlist.cdl) c(.subckt header) d(端口数) e(B 实例数) f(B literal 正确 MSB-first) g(power nets) h(.ends) i(实例名前缀) j(B 门 master) k(B2 exit0) l(B2 实例数) m(B2 门 master) n(B2 literal+inv_out) o(反硬编码 A≠B) p(确定性 3x sha256)

## 自验结果

- ref PASS 16/16
- 6 neg FAIL 6 distinct first_fail: empty_shell→(b), print_expected→(b), core_deleted→(e), naive_skip_inv→(e), naive_wrong_literals→(f), naive_hardcode_a→(c)
- §4.9 三假 FAIL
- 断言闸门 k_rationale=16 == k_check=16 ≥ 8 ✓
- 确定性 3x sha256(netlist.cdl) 一致
- test==disk check.py byte-sync (17088B)
