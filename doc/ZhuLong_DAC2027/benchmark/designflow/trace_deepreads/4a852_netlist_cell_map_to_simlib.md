# 4a852 — e0039602 netlist cell-mapping to simlib_base.sv (schematic_netlist 域)

## trace 元数据
- session: `1791963281932_4a852.messages.json` (e0039602 / hfeg0plg85, mc=661)
- size: 2.32MB, 555 msgs (253 user / 228 assistant, 63 substantive user turns), 109 editor / 62 run_approved_command / 35 read_files
- keywords: netlist 2738 / schematic 44 / pyAether 3 / synthesis 1
- model: deepseek-v4-flash；cwd /home/e0039602/Documents/netlist_change_copy/
- trace-keyword 域 = schematic_netlist，**实产 case 域 = schematic_netlist**（netlist cell→物理单元映射引擎）

## 主线（63 条 user msg 提炼）
e0039602 手头一个 DRCOA DRAM 的 Verilog netlist（`netlist_change/netlist`，76KB），其中部分 cell（nand2IOLVx2 / nand3IOLVx2 / ntn_lv / ptn_lv / invDSx1 / invenLVSx1 / invCS / invhizCS / invenCS / parasiticRC2 …）在 `simlib_base.sv`（25 个物理单元积木：inv_base / invYx_base / inven_base / invhiz_base / passg_base / nn / pp / dlyrc_base / fba* …）中**不存在**，仿真器无法直接读取。用户要求**按 11 条映射约束**把缺失 cell 替换为 simlib_base 中"最接近的单个物理单元"：
- 映射原则：不复刻管级骨架，最高抽象映射；CMOS 反相器对（NMOS+PMOS）→ 单个 inv_base；NAND/NOR → inv_base(.A(a & b))/inv_base(.A(a | b))（输入在物理单元前端一步合并）。
- 分工：延时/驱动强度落物理单元，电源/衬底脚 vcc_/vss_/vbulkp_/vbulkn_ 真实接入；纯逻辑合并用 &/|/^。
- 清理：死结点（只被驱动从不被读）驱动器删除；寄生 RC → trireg(medium) 建模。
- 风格：`celldefine、spec_gates_begin/end、specparam …*`CDLYW、端口/参数顺序一致。
随后用户把流程**规范为一个项目** `netlist_cell_convert/`（顶层 `run.py` + `src/` 模块，先确定性解析 netlist→列缺失 cell→查 simlib→调 LLM agent 生成映射→写 `result_map_*.txt`），并反复打磨：按 ~10 cell/批切分、每 module 调一次、token 上限 80% 截断、解析失败回退大模型、时间戳输出、去绝对路径可移植、每批跑完即写、history.md 总结。最终用户认可（U[533]「目前这个任务完成的不错」）并要求撰写学术文档。

## 关键真实 artifacts（hfeg0plg85:/home/e0039602/Documents/netlist_change_copy/）
- `netlist`（4338B，5 module / 14 缺失 cell 实例 — A 档输入，已 scp）
- `simlib_base.sv`（71785B，25 module — 物理单元库，已 scp）
- `history.md`（任务总结）
- 大网表 `netlist_change/netlist` 76KB（隐藏 B 素材池）

## 物理单元引脚签名（simlib_base.sv 实测）
- `inv_base(Y, A, vbulkn_, vbulkp_, vcc_, vss_)` — 反相器
- `inven_base(Y, A, EnN, En, vbulkn_, vbulkp_, vcc_, vss_)` — 使能反相器
- `invhiz_base(Y, A, EnN, En, vbulkn_, vbulkp_, vcc_, vss_)` — 三态反相器
- `passg_base(Y, vbulkn_, vbulkp_, A, En, EnN)` — 传输门
- `nn(B,D,G,S)` / `pp(B,D,G,S)` — 裸 NMOS/PMOS（仅无物理单元可用时降级）
- `dlyrc_base` / `fba*` 家族 / `fgc_pwrstate_monitor`

## 金标准映射（trace U[282]/U[284]/U[308]/U[379] 用户接受版，A 网表 14 实例）
| 行 | 原 cell inst | → 目标 | 关键变换 |
|:--|:--|:--|:--|
| L34 | nand2IOLVx2 I6(.Y,.A(S),.B(net16),.vbn,.vbp,.vcc,.vssz) | inv_base I6(.Y,.A(S & net16),.vbulkn_,.vbulkp_,.vcc_,.vss_) | NAND2=inv(AND)，输入 & 合并 |
| L36 | nand3IOLVx2 I0(.Y(net16),.A(R1),.B(R0),.C(Y)) | inv_base I0(.Y(net16),.A(R1 & R0 & Y),…) | NAND3 三输入 & 合并 |
| L61 | ntn_lv MN0(.D(Y),.G(A),.B(inh_vss),.S(inh_vssz)) | 与 L62 合并为 inv_base (.Y(Y),.A(A),.vbulkn_(inh_vss),.vbulkp_(inh_vcc),.vcc_(inh_vcc),.vss_(inh_vssz)) | CMOS 对收敛 |
| L62 | ptn_lv MP0(.D(Y),.G(A),.B(inh_vcc),.S(inh_vcc)) | 删除（已并入 L61 的 inv_base） | pair-merge 删一保一 |
| L85 | invDSx1 I2(.Y(net6)) | 删除（net6 死结点） | dead-node 删除 |
| L87 | invDSx1 I1(.Y(out),.A(in)) | inv_base I1(.Y(out),.A(in), pins remap) | 普通反相器 |
| L89 | invDSx1 I0(.Y(net7)) | 删除（net7 死结点） | dead-node 删除 |
| L115 | invenLVSx1 I30(.Y(Out),.A(Inv1_In),.En(SelN),.EnN(Sel)) | inven_base I30(.Y,.A,.EnN,.En, pins remap) | 使能反相器 |
| L117 | invenLVSx1 I0(.Y(Out),.A(Inv2_In),.En(Sel),.EnN(SelN)) | inven_base I0(…) | 使能反相器 |
| L143 | invCS I6(.Y(net9),.A(QN)) | inv_base I6(…) （net9 被 I1.A 读，非死） | 普通反相器 |
| L145 | invCS I4(.Y(LatF),.A(Lat)) | inv_base I4(…) （LatF 输出端口） | 普通反相器 |
| L147 | invhizCS I1(.Y(QN),.A(net9),.En(Lat),.EnN(LatF)) | invhiz_base I1(…) | 三态反相器 |
| L150 | invenCS I7(.Y(QN),.A(D),.En(LatF),.EnN(Lat)) | inven_base I7(…) | 使能反相器 |
| L152 | parasiticRC2 I3(.MINUS(QN),.inh_vss(inh_vss)) | trireg(medium) 或删除 | 寄生 RC→trireg |

引脚重映射表：vbn→vbulkn_ / vbp→vbulkp_ / vcc→vcc_ / vss→vss_ / vssz→vss_ / vbulkn→vbulkn_ / vbulkp→vbulkp_

## 抽取的 case
- `EDA-Eval-DesignFlow-CellMap-001`（schematic_netlist 域，L1 离线 Python 网表变换引擎，B 档）
- 交付件 = `cell_mapper.py`：吃 `--netlist <f> --simlib <f> --outdir <d>`，确定性解析 netlist→列缺失 cell→按 11 条映射规则 + simlib 物理单元签名，做 pair-merge / dead-node 删除 / 输入 &| 合并 / 引脚重映射，产出 `<outdir>/transformed_netlist.sv` + `<outdir>/result_map.txt`（每行「第N行 <orig> → 转换为 <new>」）
- A（可见）= 真实 5-module netlist + 真实 simlib_base.sv
- 隐藏 B = 合成 NOR 变体网表（nor2IOLVx2/nor3IOLVx2→inv_base(.A(a|b))，跨输入 guard 击破硬编码 & 的 stub）+ 同 simlib，不同 net/inst
- check.py 15 条件 a-o：subprocess 真跑候选于 B，验 zip 结构/CLI 退出码/result_map 格式/NAND→&/NOR→|/CMOS pair-merge/死结点删除/引脚重映射/inven→inven_base/invhiz→invhiz_base/parasiticRC→trireg-or-delete/无 UDP/无裸 nn-pp 堆/cross-input A≠B/缺失 cell 计数/模块端口保持

## 与 D.jsonl 现有 schematic_netlist case 的区别（非重复）
- SubSecFilter-001 / SkillToAether-001：Virtuoso/Aether 网表遍历取链；本 case 是 **Verilog netlist→物理单元库的语义重映射**（gate-level → physical-unit abstraction），无 EDA 工具，纯文本变换 + 语义判定（NAND=inv(AND)、CMOS 对收敛、死结点分析）。
- NetlistChk-001：netlist 语法检查；本 case 是结构变换 + 引脚保真。
