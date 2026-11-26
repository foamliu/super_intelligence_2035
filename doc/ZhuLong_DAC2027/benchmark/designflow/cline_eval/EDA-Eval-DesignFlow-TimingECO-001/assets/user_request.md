以下是我构建STA_flow的描述：“尝试为我在当前目录下（/rundata/lacaa/TV1_digital/simdir/yutingq/STA）构建一个STA flow,工具为PrimeTime，并使用一个demo来跑通。我已经生成了几个关键的文件层次，分别用于存放各种输出件log、rpt、sdc（生成后缀为.sdc的文件）、session（用于在pt_shell中交互）等。我希望任务运行的目录在run下面（因此需要在run目录编写任务运行脚本，我希望这个脚本以cshell语言编写），我希望过程中各个环节读入的脚本存放在scr目录下，且以tcl语言来编写，各个过程中脚本按照读入顺序进行编号（如：sta_main.tcl;1_setup.tcl;2_read_constranit.tcl;……;10_rpt.tcl）。我需要enable几个关键的feature：环境配置、工具选型、子模块lib输入件读入，并且可以通过选项传参来适配不同corner、模式。你可以参考/apps/imctf/cad/script/digital_flow/feint下的synopsys pt reference flow的做法。工具是/apps/synopsys/primetime，但值得提醒的是你可能需要module load 才能正确获取license.（你的思考过程用中文展示给我）”。

由于我对Timing ECO flow不够了解，因此请模仿上述STA_flow的构建要求，并结合前文我需要实现的Timing ECO功能，为我在当前目录下的 TimingECO_flow 目录下，构建一个TimingECO flow, 并使用一个demo来跑通。

前文需要实现的 Timing ECO 功能：
①完成Timing ECO flow与Top STA flow的衔接适配
②制定ECO patch生成策略，和P&R团队对齐
③跑通ECO后时序重签核全流程
④输出流程说明文档

—— 用户原话（trace 1792572733650_pfubi，e0046913，2026-10-21）
