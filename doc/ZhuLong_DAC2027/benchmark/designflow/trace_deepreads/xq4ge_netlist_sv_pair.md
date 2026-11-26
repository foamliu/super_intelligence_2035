# Deep-read: xq4ge — netlist ↔ simlib sv 配对调整文档

- **session**: 1792030871333_xq4ge.messages.json
- **user/host**: e0039602 / hfeg0plg85
- **match_count**: 248 (eligible 120 fresh)
- **domain**: schematic_netlist
- **case_id**: EDA-Eval-DesignFlow-NetlistSvPair-001
- **track**: A-faithful

## 用户原始需求 (U#0 verbatim)

> 请问再这个文件夹下的netlist文件和simlib_drcoa_digital.sv文件有什么关系，按照我们的任务要求，是netlist这个网表当中有的model当中的cell无法被识别，需要用simlib_base.sv当中的基本模块像搭积木一样实现其中的功能，然后得到simlib_drcoa_digital.sv当中对应的内容，例如第34行 nand2IOLVx2 I6 (.Y(Y), .vbn(inh_vbn), .vbp(inh_vbp), .vcc(inh_vcc), .vssz(inh_vss), .A(S), .B(net16)); → 转换为 inv_base I6 (.Y(Y), .A(S & net16), .vbulkn_(inh_vbn), .vbulkp_(inh_vbp), .vcc_(inh_vcc), .vss_(inh_vss));当然netlist和修改完的sv文件还有一些框架上的不同，这个你不用在意。只需要关注转换的部分就可以。现在的问题是我发现simlib_drcoa_digital.sv文件要比netlist大很多，我初步怀疑是sv文件当中包含了很多不属于这个netlist的，这个netlist只是部分，请你根据这个netlist找寻他在sv文件当中对应的修改，并给我生成一个netlist和原sv文件当中一一对应的调整文件，尽可能按照我上述例如之后的这种格式写明。

## Trace 摘要

- **3 user turns**：U#0 提需求（配对 + 调整文档）；U#2 问剩余 57 个模块去向（agent 纠正：44 叶子单元已被内联到 22 个顶层模块）；U#3 贴 fbs/inven/nor2 的 sv module 源码辅助。
- **agent 产出**：`generate_adjustment.py`（122 行）+ `adjustment_netlist_to_sv.md`（526 行，22 模块逐个配对）。
- **真实数据规模**：netlist 79 module 定义 / 66 unique；simlib_drcoa_digital.sv 638 modules；22 同名配对，44 叶子被内联。

## Gold 脚本核心逻辑 (generate_adjustment.py)

1. `get_modules(path)`：regex `\bmodule\s+(\w+)\s*(\([^;]*?\))?\s*;` 抓 module 名 + 行号 + header + body（到 `endmodule`）。
2. `extract_instances(body)`：跨行续接——累加 line 直到 `;` 出现且 `(` 计数 >0，regex `(\w+)\s+(\w+)\s*\(` 抓 celltype + instname。
3. `clean_net_instances`：过滤 parasiticRC2 / parasitic_capacitor / RNPDIFF3t。
4. `clean_sv_instances`：过滤 fgc_pwrstate_monitor。
5. 分类：A = netlist 与 sv 同名模块（实例名一一对应 netlist→sv）；B = netlist 实例未在 sv 同名匹配；C = sv 实例 netlist 无同名。
6. 端口翻译：vbn→vbulkn_ / vbp→vbulkp_ / vcc→vcc_ / vss→vss_ / vssz→vss_。
7. 逻辑翻译：nand2(A,B)→inv_base .A(A&B) / nand3(A,B,C)→inv_base .A(A&B&C) / nor2(A,B)→inv_base .A(A|B) / inven→inven_base / ntn_lv+ptn_lv→inv_base 合并。

## Benchmark 合成

- **参考解** `gen_netlist_sv_pair.py`：参数化 gold——读 config.json{netlist, sv, output, library, port_translation, logic_translation}，解析两文件模块，按名配对，写 md 含概况计数 + 翻译规则表 + (A) 配对模块（netlist 实例→sv 转换实例 + 实例名对应 + 实际翻译检测）+ (B) 仅网表 + (C) 仅仿真库。
- **资产 A** (drcoa_digital 族)：netlist_A.v 10 modules + sv_A.sv 10 modules (7 配对 / 3 sv-only) → 7A/3B/3C。
- **隐藏 B** (dpfx_digital 族，不同命名 + 不同结构)：netlist_B.v 10 modules + sv_B.sv 10 modules (6 配对 / 4 sv-only) → 6A/4B/4C。
- **check.py 17 条件 a-q**：zip 含 gen + py_compile + 跑 B 退 0 非空 + 5 个概况计数 (10/10/6/4/4) + (A)(B)(C) 三节模块名 + 端口翻译 5 规则 + 逻辑翻译 3 规则 + 跨输入护栏 (drcoa_* 不泄漏 / dpfx_* 出现) + 逻辑转换落地 (nor2→inv_base .A(A|B) / nand3→inv_base .A(A&B&C)) + 非平凡源码 + 3-seed 确定性。
- **4 negatives** ALL-FAIL distinct：empty→c / print_fixed_A→f / core_deleted→l / naive_no_logic_translate→m。
- **自验**：ref PASS 17/17 · §4.9 三假 distinct ✓ · k_rationale=k_check=17 ✓ · test==disk ✓ · D.jsonl 64→65。
