# 深读笔记 — 1794795187792_3dlpk（DDR5 netlist STA 路径最后一级模块统计 · L1 produce-task）

- **trace**: `/home/qiangw/.cline/data/sessions/1794795187792_3dlpk/1794795187792_3dlpk.messages.json`（qiangw @ hfhds209=10.129.32.83, mc=194, 820KB, 100 msgs / 58 user / 42 assistant）
- **来源**: r944 fresh D-pure 候选 7 条之一（cross-shard dup pre-check 0/4 clean ✓）；r945 选料（其余 6 条或 L2 real-sim 超 40min 预算、或意图碎片化，详见 r945 MEMORY）
- **keywords**: netlist:552;verilog:337;drc:249;lvs:129;cmos:72;analog:52;schematic:14 — D-pure（drc/lvs kw 来自项目名 drcpa 的文件路径，非真实 DRC/LVS 工具调用；实际任务是 verilog netlist 路径解析，纯 schematic_netlist 域）
- **domain**: schematic_netlist（verilog netlist 模块层级解析 + STA 路径统计）

## 用户意图演进（多轮，A-faithful 取核心 5 轮）

| 轮 | 用户原话 | 子任务 |
|---|---|---|
| U0 | （粘帖 3 条 STA 路径，含 driver pin） | 提供数据 |
| U1 | 「帮我写个脚本用于删除包含 driver 的括号里面所有内容」 | 清洗 |
| U16 | 「这是一个网表文件：/rundata/drcpa/V0/.../netlist」 | 指定 netlist |
| U20 | 「帮我找到这个 STA 路径在次网表中的模块名字：I_Array6G_T_0/.../GroupBC[3]」 | 模块查找 |
| U49 | （粘帖 20 条路径） | 数据 |
| U58 | 「帮我将以上路径的最后一级所属模块名进行次数统计」 | 统计 |
| U62 | 「请对以上路径最后一级所属模块进行统计，并对属于同一模块的路径进行去重」 | 去重 |
| U81 | 「请对以上路径最后一级所属模块进行统计，同时对于最后一级属于同一模块的路径只保留出现的第一条，然后输出，输出格式为：路径, 最后一级所属模块的名, 出现次数」 | 完整规格 |
| U84 | 「按照以上操作对此文件进行处理，并将处理过程总结成 python 脚本：<tttt.list>」 | 总结成脚本 |
| U101 | 「这个脚本如何使用，如何指定网表和待处理文件」 | CLI 接口 |
| U124 | 「请再给这个脚本增加一个排序功能，按照模块次数来对行进行从大到小的排序」 | 排序 |

**A-faithful 判定**: 用户在 U1/U81/U84/U124 提出「需求/目标」，未给根因或修复方案（U1 给的是任务规格不是修复）✓。多轮意图合并成单一 produce-task：写一个通用 python 脚本，对 netlist + STA 路径列表，解析层级、统计、去重、排序、输出 CSV。

## GOLD（assistant 最终交付，msg 末尾）

- **文件**: `/home/qiangw/Desktop/path_analyzer.py`（4766B / 130 行，ssh fetch ✓）
- **逻辑**:
  1. `parse_netlist(fpath)`: strip 块/行注释 → 正则 `module X` / `endmodule` 切模块范围 → 正则 `(\w+)\s+(\w+)\s*\(` 找实例（排除 verilog 关键字）→ 返回 `{module: {inst_name: module_type}}` 和模块范围表
  2. `resolve(hi, top, parts)`: 从 top（默认 'DDR5TOP' 或第一个模块）逐级下钻，每段先 `re.sub(r'\[.*?\]','')` 去总线位，若 inn 不在 im 字典则前缀模糊匹配，再不行标 `wire(in <cur>)` 并停
  3. `get_lm(pairs, note)`: 若 note 含 'wire' 则返回 wire 所在模块名；否则返回 pairs[-1][1]
  4. `Counter` 统计 + `OrderedDict` 保留首条 + `sorted(-count, name)` 排序
  5. CSV 输出 `path, last_module, count`，路径含逗号/引号则 CSV 转义
- **CLI**: `python3 path_analyzer.py <netlist.v> <path_list.txt> [-v]`

## 判定：buildable（L1-realrun-python produce-task，howto-reframe 快速范式）

- ✅ 真实 trace + D-domain（verilog netlist 层级解析，纯 schematic_netlist）
- ✅ A-faithful（用户提需求未给修复）
- ✅ GOLD = 完整通用脚本（130 行，无硬编码，对任意 netlist+path_list 通用）
- ✅ L1-realrun-python：判分只需 subprocess 跑脚本 + 解析 CSV 输出，无需 EDA 工具/FineSim
- ✅ 适合 howto-reframe 快速范式（B = 合成平行 netlist + 路径列表，token-disjoint from A）

## 处置（r945 已合成落库）

- **case_id**: EDA-Eval-DesignFlow-StaPathLastModStatQA-001
- **A 资产**: 合成 netlist_A.v（drc5a_ddr5，13 模块）+ path_list_A.txt（12 路径）+ question_A.txt
- **B hidden**: 合成 netlist_B.v（drc6b_lpddr6，9 模块，token-disjoint）+ path_list_B.txt（12 路径，6 unique 模块: drc6b_row_dec=4 / drc6b_sense_amp=3 / drc6b_col_dec=2 / drc6b_dq_driver=1 / drc6b_dq_monitor=1 / drc6b_dq_receiver=1）
- **reference**: path_analyzer.py（GOLD verbatim，通用）+ reference_submit.zip
- **check.py**: 12 断言 a-l（zip+compile+exit0+表头+6行+首行drc6b_row_dec=4+sense_amp=3+col_dec=2+count非递增[4,3,2,1,1,1]+去重+反硬编码B-token/A-token+3-seed md5 幂等）
- **self-verify**: reference 12/12 PASS ✓ + 3 neg（empty_stub/print_only_stub/core_deleted_stub）全 FAIL ALL_NEG_FAIL=True ✓
- **k_rationale=k_check=12** ✓（>=8 硬闸门）
- **D.jsonl**: 509 → 510
- **ledger**: 3dlpk mark case ✓
