# Deepread — siyuji @ hfeg0plg72, session 1795069774803_nghfa (mc54)

**trace source**: .75 ssh 10.129.8.110 `/home/siyuji/.cline/data/sessions/1795069774803_nghfa/1795069774803_nghfa.messages.json` (879KB, 159 msgs)
**keywords**: netlist:438; hspice:292; dbget:152; synopsys:19; vhdl:8; transistor:2

## 用户真实意图

siyuji 有一个 Synopsys CCK 串扰分析 Tcl 脚本 `~/Desktop/scripttest/zlong/xtalk.tcl`（实读 1218 行 / 40KB，依赖 `inn::dptbl` / `inn::netlist` / `dspfParser` 三个不可移植 CCK 库），自己完全看不懂。

**用户原话 #1**：
> 由于我对这个脚本非常不理解，所以能否把这个脚本中的每一步输出结果都打印出来，在一个非常小的block中去测试，对照着所有的输出内容理解脚本的功能

**用户原话 #2**（纠正 assistant 跑偏去用 python 重写）：
> 你只对我给你的xtalk.tcl的内容进行分析后，尽量输出其中的变量，方便我去理解这个代码的每一步处理，并非是让你用python写，你是没有内置tcl的语言包吗，对于cck的API你无需改动，只需要把变量内容输出即可

即：产出一个**插桩调试版 Tcl 脚本**——在每一步后面插 `puts` 打印变量值，CCK API 一行不动，不要 python 重写。

## assistant 实际表现（trace 摘要）

assistant 读 xtalk.tcl（[1]），尝试多种方式生成 `xtalk_debug.tcl`（editor / shell heredoc / python 生成），**反复踩 Tcl `[...]` 双引号命令替换坑**（[37]-[49] 多轮修转义），又踩 cline python-runner sandbox 的 f-string `{}` 坑（[61]-[75]），最后 [143]-[157] 文件被 cleaner 误截断在 `genunit` 内的 `exit`，session 结尾仍在 "I need to rewrite the entire debug file properly" —— **未干净交付**。

## xtalk.tcl 结构（实读）

- 11 个 proc：`mkindex` / `getModelList` / `genunit` / `gen_top` / `explore_inst` / `::getResOrient::*` / `CalcPdrv` / `CalcNdrv` / `get_driver`
- 3 个 package require：`inn::dptbl 1.0` / `inn::netlist 2.0` / `dspfParser 1.0`
- ~30 个 CCK API 调用：`cckExplore` / `cckGetInstType` / `cckGetInstFullName` / `cckGetInstModel` / `cckGetInstProp` / `cckIsPseudoCap` / `cckIsPmos` / `cckGetInstTerminalNode` / `dspfRead` / `dspfParser::getNetCap|getNetCCap|getNetGCap|createCCKTbl` / `inn::netlist::SelectRailTbl` 等
- 340 个 `set` 赋值

## reframe（portability + harness-for-teeth）

原 xtalk.tcl 依赖 Synopsys CustomSim CCK 私有库，判分沙盒不可便携 → 泛化成参数化生成器 `tcl_debug_instrument.py`：读 spec（描述 Tcl 脚本由 banner/code/puts_var 段顺序组成）→ 输出 `<script_name>_debug.tcl`。判分在隐藏 B（IR-drop，结构完全反过来）上跑生成器 + 静态校验。核心牙 = CCK code 段逐字保留 + 插桩 puts 的 `[`/`]` 转义（用户踩的坑）+ `$var` 取值不转义 + proc/banner 保留 + 确定性 + 反硬编码 A + anti-stub B2。

case_id = `EDA-Eval-DesignFlow-TclDebugInstrumentGen-001`，k_check=k_rationale=16(a-p)，5 neg 全 FAIL，ref 16/16 PASS。
