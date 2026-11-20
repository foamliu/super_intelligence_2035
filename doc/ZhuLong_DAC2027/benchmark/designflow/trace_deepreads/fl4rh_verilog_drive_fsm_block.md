# deepread: 1793866097938_fl4rh — VerilogDriveFsmBlock.pl (mike @ hfeg0plg05)

- session: `1793866097938_fl4rh.messages.json` (1.36MB, 6 user msgs + ~340 tool turns)
- user: mike, host: hfeg0plg05, mc=427, domain=eda_other (dscqa V0 mixed-signal co-sim)
- ledger: 旧 parked (2026-11-09, 旧筛子判 build-automation weak) → r682 按 11-15 新标准复活 → case EDA-Eval-DesignFlow-VerilogDriveFsmBlockGen-001

## 用户真实意图（按顺序）
- U#0: `/ai_sandbox/dscqa/V0/agentdir/mike/verilog_drive_fsm_block_env_reference 我要在这个目录下开发一个VerilogDriveFsmBlock.pl的脚本，接下来你按照plan模式工作，脚本要干以下几件事`
- U#15: `runBlock2（Perl）参考这个文件，但是 input pin需要我来给，我会给你一个文件list`
- U#17: `脚本位置 .../dscqa_array_m0d5G_YS_Bot_sub_schematic_ALPS   pl  input.list`
- U#38: `你开发好脚本 我来执行，然后你去看结果`
- 用户随后跑了 `./VerilogDriveFsmBlock.pl input.list`，回显 `backed up stimulus -> stimulus.bk`。

## 核心事实（trace 原文 + agent plan A#13/A#16/A#22）
真实环境 = dscqa V0 `m0d5G_YS_Bot_sub` block 的 ALPS / VCS-AMS 混合信号协同仿真目录，要把指定 input pin 从「SPICE PWL 模拟激励驱动」切换为「Verilog 驱动」。
- `m0d5G_YS_Bot_sub_in`（85 input pin）/`_io`(4 inout)/`_out`(1151 output)/`_power`(13) 四个 pin list（对应 runBlock2 输入格式）。
- `stimulus`：WaveView 导出的 PWL 激励，22899 行，102 个 PWL source headers。
- 真实 input.list（用户加的）：27 pin = `RCS<19>..RCS<0>`(20bit bus) + `CdeClkC_BL`(1bit) + `ColAdr_BL<9>..ColAdr_BL<4>`(6bit, [9:4])。
- 脚本接口最终收敛：`perl VerilogDriveFsmBlock.pl input.list`（只接一个参数），只做文件生成不跑仿真。

## 交付物行为（脚本契约）
1. 读 input.list，每行首空白分隔 token 为 pin 名，支持 `Name<idx>` bus 位写法，空行/`#` 行忽略。
2. 备份 `stimulus` → `stimulus.bk`（已存在则跳过，不覆盖）。
3. `extract_stimulus`：从 `stimulus` 删除被接管 pin 的 PWL 源块（`VPWL <sig> 0 PWL(` 头 + `+` 续行），大小写/空白不敏感匹配；未接管 pin 保留。
4. bus 位合并 `[hi:lo]`。
5. 生成 `stimulus.v`：`module gen_stimulus`，每 pin 一个 `output reg`（bus 向量 + 单 bit），`timescale 1ps/1ps`，`initial` 初始化 0。
6. 生成 `vcsAD.init`（VCS-AMS 胶水，含 `+incdir+.` + `stimulus.v`）。
7. `netlist` 追加 `.SUBCKT gen_stimulus <pin列表>` + `.ENDS gen_stimulus`（pin 用原始 `<>` 写法）。

## 造题（r682 单轮闭环）
- 形态：C-A produce-task（Perl 脚本生成 + 真跑校验），eda_other。
- A 档可见：`assets/VerilogDriveFsmBlockGen-001/`（input.list/stimulus/netlist 示例 = m0d5G_YS_Bot_sub 的 RCS<2:0>/CdeClkC_BL/ColAdr_BL<5:4>，6 pin）+ task_brief.md（trace-faithful 用户原话 + 脚本契约）。
- B 隐藏变体：`hidden/`（block YS_Top_sub：Data<3:0>(4bit bus) + Clk + RstN(单bit) = 6 driven pin；Vblh/AnalogCtrl 2 个非 driven 必须保留）。与 A 全异（pin 名/bus 宽度/取值）→ anti-hardcode。
- 参考解：`reference/VerilogDriveFsmBlockGen-001/VerilogDriveFsmBlock.pl`（自写实现上述 7 步契约，本地 perl 5.38 跑通 A 与 B）。
- check 10 条 a-j：zip 含脚本 / perl exit 0 / stimulus.bk 创建 / bk==原始 / stimulus 修改(driven 删+remain 留) / stimulus.v module gen_stimulus + bus 合并[3:0] Data / 端口数=3 + Clk/RstN / netlist 追加 .SUBCKT+.ENDS + pin 集合 / vcsAD.init 引用 stimulus.v / 二次运行不覆盖 bk（幂等）。
- 负样本 4 个全 FAIL：neg_stub(空壳→c) / neg_print_expected(只打印→c) / neg_hardcode_A(A 硬编码→e) / neg_core_deleted(删核心 extract+append→e)。
- §4.9 三假全 FAIL（stub/print_expected/core_deleted）。negative_selftest 4/4 FAIL + ref PASS。e2e jsonl test==disk round-trip PASS。
- 注：脚本实现由 deepread 契约自写（trace 里 agent 的脚本被 15+ 次增量 editor 编辑，难以逐 diff 还原；契约来自用户原话 + agent 的 plan A#13/A#16/A#22 + 运行回显，忠实还原用户意图而非逐字节复刻 agent 产物）。
