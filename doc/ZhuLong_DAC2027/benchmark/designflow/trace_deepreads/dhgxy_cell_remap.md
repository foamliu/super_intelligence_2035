# deepread — dhgxy (e0039602 @ 10.129.8.136, mc=91, schematic_netlist)

source: `/home/e0039602/.cline/data/sessions/1791957763339_dhgxy/1791957763339_dhgxy.messages.json` (189 KB, 6 user turns)
assets real: `/home/e0039602/Documents/netlist_change_copy/{netlist, simlib_base.sv}` (4338 B + 71785 B)

## user turns (verbatim)

- **U#1** 「你现在在哪个文件夹下，文件夹当中有哪写文件」 — orientation (agent: ls → `netlist` + `simlib_base.sv`)
- **U#2** (A-faithful produce-demand, no root cause given):
  > 请修改 netlist 文件。其中有些模块用到的 cell 在 simlib_base.sv 中不存在，无法直接读取，请结合 simlib_base.sv 把它们替换掉。
  > 约束如下（务必严格遵守）：
  > 优先复用 simlib_base.sv 中【自带电源/衬底引脚】的物理单元积木
  > 分工规则（这是重点）：
  > 凡是有"延时/时序/驱动强度"等物理效应的部分，必须用库内物理单元实现， 并把 vcc_/vss_/vbulkp_/vbulkn_ 等电源与衬底脚真实接进这些物理单元；
  > 凡是对输出没有延时、没有物理影响的纯逻辑输入合并，一律直接用 位与 &（或 |、^ 等）逻辑表达式在这个物理单元的前端拼接完成， 不要再把它们拆成单独的晶体管堆或单独的门级模块。
  > 不要下面这两种做法：
  > 不要用纯行为/无电源脚的 UDP 原语来形成单纯的逻辑电路， 因为它无法承接 vcc/vss/bulk，电源腿会变成悬空摆设；
  > 尽量不要把每个 NAND 输入都做成独立的 pp/nn 晶体管串并联堆，除非没有模块可以实现对应功能 那既啰嗦又违背第2条"无延时输入用 &"的规则。
  > 每个被替换的 cell，先用真值表和器件原理分析，再用 simlib_base.sv 里的 物理单元 + & 组合式地复原出逻辑功能，并保持时序/保持行为一致。
  > 改写时保留原 cell 的所有参数与连接关系（电源脚、衬底脚、端口名都要保留）。
  > 输出要求：在对话窗口打印每处被替换的原始行和替换后的行；无须实际改写 netlist 文件；最后用真值表穷举（含保持态/上一值）验证替换前后等价。
- **U#3** 「在完成我这个任务过程中，你生成了哪些脚本来辅助」 — meta Q (agent: 列出 _grep_modules.py / _verify.py / _cleanup*.py)
- **U#4** 「你是如何扫描netlist文件来判断哪些需要转换呢」 — meta Q (agent: 集合差集 用到 − 库内)
- **U#5** 「simlib_base.sv 里我看到里面只有约 8 行真正是带电源/衬底脚的物理基础单元，其中能直接承接逻辑门的只有 inv_base...」 — meta Q (agent: 重扫确认 10 个全 4 脚物理积木，可拼 NAND 的只有 inv_base/invYx_base)
- **U#6** 贴 Liberate charScript 片段 (`add_latch IY IYN !S 1 -clear S&!(R0&R1)`) 问「这个文件和之前的netlist文件是一个含义，请你看一下这个文件如何理解」 — meta Q (agent: charScript 视角 vs 结构 netlist 视角；锁存建模)

U#3-#6 全是元问题/澄清，**唯一 produce-demand = U#2**（A-faithful：提需求未给根因/修复）。

## agent tool chain (U#2 处理)
1. `list_allowed_files` / `read_files` → 读 netlist (40 行, 1 module `IO_rsnand21nand31_DL_ACT_MERGE_READ`) + simlib_base.sv
2. `search_codebase` 搜 NAND (只索引到 netlist) → 改用 `editor` 写 `_grep_modules.py` 正则 `^module\s+(\w+)` 扫库 → 26 模块
3. 关键发现：simlib_base 无任何 NAND 门；可用 4 脚物理反相器 = `inv_base` (Y, A, vbulkn_, vbulkp_, vcc_, vss_, 内部 pp/nn)
4. `editor` 写 `_verify.py`：Part1 逐门 4 态穷举 (nand2 9 组合, nand3 27 组合) orig(物理 NAND) vs new(inv(&合并))；Part2 交叉耦合锁存保持态 32 组稳态 → 全 PASS
5. `editor` 写 `_cleanup*.py` 删自身 (用户要求不残留)
6. 打印每处替换 (orig 行 → new 行)

## user-accepted 产物 (gold)
- 替换 1: `nand2IOLVx2 I6 (.Y(Y),.vbn(inh_vbn),.vbp(inh_vbp),.vcc(inh_vcc),.vssz(inh_vss),.A(S),.B(net16))` → `inv_base I6 (.Y(Y),.A(S & net16),.vbulkn_(inh_vbn),.vbulkp_(inh_vbp),.vcc_(inh_vcc),.vss_(inh_vss))`
- 替换 2: `nand3IOLVx2 I0 (.Y(net16),...,.A(R1),.B(R0),.C(Y))` → `inv_base I0 (.Y(net16),.A(R1 & R0 & Y),.vbulkn_(inh_vbn),.vbulkp_(inh_vbp),.vcc_(inh_vcc),.vss_(inh_vss))`
- 电源映射: vcc→vcc_, vssz→vss_, vbn→vbulkn_, vbp→vbulkp_
- 4 态穷举验证全 PASS (含锁存保持态)

## real netlist 结构
module `IO_rsnand21nand31_DL_ACT_MERGE_READ` (Y, R0, R1, S, inh_vcc, inh_vbn, inh_vbp, inh_vss):
- wire net16
- nand2IOLVx2 I6 (.Y(Y), .A(S), .B(net16), vcc/vssz/vbn/vbp)
- nand3IOLVx2 I0 (.Y(net16), .A(R1), .B(R0), .C(Y), vcc/vssz/vbn/vbp)
本质 = SR 锁存: Y = ~(S & net16), net16 = ~(R1 & R0 & Y)

## simlib_base.sv 物理积木清单 (重扫确认)
全 4 脚 (vbulkn_/vbulkp_/vcc_/vss_) + pp/nn 物理实现 (10 个):
inv_base, invYx_base, fbenr_base, fbr_base, fbens_base, fbs_base, fbrs_base, fbsr_base, inven_base, invhiz_base
部分脚: passg_base (仅 vbulkn_/vbulkp_), dlyrc_base (仅 vcc_/vss_) — 不可作逻辑合并积木
原语: nn, pp, switch, alias_short
行为宏: mcore*/msax*/lwdr_test — 无真实电源脚

## case 合成决策
真实 netlist 仅 40 行 / 2 cell → 太小，A 档金标准条件数不足 8 且 hidden B 难做"规模不同"。
→ **B 档 synthesized**：保留真实分工规则与电源映射语义，合成更丰富的 netlist (含 NAND2/NAND3/NOR2/NOR3 + 已在库内的 inv_base 实例作 distractor) + 合成 simlib_base (含 10 个全 4 脚物理积木 + 部分脚 distractor + 行为宏 + 原语)。
金标 = 通用 replace_cells.py：扫描实例化 cell ∩ 不在库内的 → 用 inv_base 替换，NANDk→A=(inputs &)，NORk→A=(inputs |)，保实例名/Y/电源映射，4 态 {0,1,x} 真值表穷举验证，禁 UDP/晶体管堆。
hidden B = 不同 cell 组合 (NAND4/NOR3/NAND2/NOR2) + 不同网名/电源名 + 含已在库内 inv_base 实例(不动)。
L1 真跑候选 (subprocess 在 hidden B 上跑候选脚本)。
