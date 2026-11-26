# 深读笔记 · 1794471268159_nh28n (curryxu / hfeg0pkn002 / mc=205 spice)

- session: `1794471268159_nh28n`，user=curryxu，host=hfeg0pkn002(10.129.2.11)
- 61 msgs，4 个 user 轮，model=deepseek-v4-flash，cwd=/home/curryxu
- 标题(meta.title): 6GHz 方波激励 testbench（PLL_GDCA 延迟链）
- 可达性: home 目录在 10.129.2.11 可读，会话存为目录 `1794471268159_nh28n/`，内含 `.messages.json`(318KB) + `.json`(meta)；产物 `/home/curryxu/PLL_GDCA_tb_6G.sp` 已 scp 到 .75 workdir。netlist 在 `/proj/m2701/V0_DDR4/workdir/curryxu/simulation/PLL_GDCA/hspiceD/schematic/netlist/netlist`，**项目目录对 e0031982 权限拒绝**，且 trace 内 read_files 的 tool_result 文本被 cline 清空（未持久化文件正文）⇒ **A 档不可行**，改 B 档：按 assistant 文字描述合成忠实 netlist。

## 用户原话（4 轮）
1. `写个.sp激励文件的脚本，电路是这个, 输入为6Ghz的方波，P<2:0>先都置0，然后加上扫描P<2:0>0或1的部分` + netlist 路径
2. `加上输出节点的占空比检测`
3. `这个DCA电路有什么问题，如何优化`（讨论，无新产物）
4.（后续轮）讨论时间常数/ResCtrl

## assistant 工具链
read_files(netlist/header/footer/input.ckpt/model.sp/V0P5_pre_post_simu.lib) → skills(spice_tb_stimulus) → read skill refs → editor 写 `/home/curryxu/PLL_GDCA_tb_6G.sp`（写入根受限，改写 home）→ run_approved_command 跑自检 `_check_stim.py` → editor 加占空比 measure → 再跑自检。

## 电路理解（来自 assistant 文字，netlist 正文未持久化）
- PLL_GDCA = 可控延迟链（DCA = delay-cell array），**扁平顶层 netlist**（无 subckt 包裹）
- 端口: `IN` `OUT` `P<0>` `P<1>` `P<2>` + 全局电源 `vcc!` `vss!` + body `vbulkn!` `vbulkp!`
- 4 级 inverter 链，`P<2:0>` 各位开关 NMOS/PMOS 电容负载到链节点以调延迟
- model: `test_model_v0p3/hspice`，corner 段 `top_tt/top_ss/...` + `pre_simu/post_simu`；m2701 HL22 22ULL 0.8V

## 产物 PLL_GDCA_tb_6G.sp（89 行，已拿到全文，见 reference/stim_A.sp）
- 13-section 骨架；option(post/probe/measfile/...)；`.lib '...corners_0p8.env' tt_25_pre`
- `.param freq=6e9 tck=1/freq duty=0.5 tr=15p tf=15p pw=tck*duty-tr sim_finish=tck*12`
- `.inc '.../netlist'`；电源 VCC/VSS/VBULKN/VBULKP
- `VIN IN 0 pulse(0 pvcc 0 tr tf pw tck)` —— 6GHz 方波
- `VP2/VP1/VP0` 由 sweep 参数 P2/P1/P0 驱动
- `.data Pcode P2 P1 P0` 8 行 000→111，`.enddata`；第一行 000 为全 0 基线
- `.tran 1p 'sim_finish' sweep data=Pcode`
- `.probe v(IN) v(OUT) ...`
- `.measure tran tpropre/tpropf`（IN→OUT 传播延迟，第5边沿）
- 占空比: `OUT_DUTY_HIGH`(rise5→fall5) + `OUT_DUTY_LOW`(fall5→rise6) → `OUT_DUTY=H+L` → `OUT_DUTY_H=H/DUTY*100`、`OUT_DUTY_L`（半周期测两次再 param 合成，避免内置 DUTY 关键字可移植性问题）
- `.end`
- 自检 `_check_stim.py` 输出: `.lib=2 .data=1 .enddata=1 sweep rows=8 .tran=2 .measure=8 has VIN pulse=True has freq 6e9=True P bits driven=True netlist inc=True model libs=True`，sha256=72f857b3...

## case 设计（B 档 synthesized netlist）
- 交付 = 参数化生成器 `gen_stim.py`（读 netlist 路径 + freq + 端口配置 → 产 .sp）+ 对 A 的产物 `stim_A.sp`
- check.py 跑 gen_stim.py 于 **隐藏 B**（不同电路：6 级、端口改名 CLKIN/CLKOUT/S<2:0>、8GHz、0.9V），断言 B 的 .sp 正确（subprocess 真跑 §4.2）
- 12 条独立断言（k_check=12≥8），三假提交全 FAIL，3 个 negative
