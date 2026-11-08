# Deep-read: 1788767030730_6azjv (rongjiez / hfeg0pkn005, mc=74)

## Trace
- session_file: `/home/rongjiez/.cline/data/sessions/1788767030730_6azjv/1788767030730_6azjv.messages.json`
- user: rongjiez, host: hfeg0pkn005 (10.129.2.x), 460 msgs, 13 real user inputs
- domain: schematic_netlist (MOS model-QA testbench 生成)

## Real task (用户原话)
- msg0: 「@runModelQA.pl 帮我分析一下这个perl脚本代码」
- msg14: 「现在这个代码写的很乱，现在需要进行重构，重构后输入是目录下的input.cfg文件，输出是Testbench，runcmd，仿真结果，重构后逻辑为如下伪代码： scale，shrink，drnPortName = getSSD(spFile); PVT = getPVT(cfgFile) ... foreach device(devices) parameters = getParameter(device) ... generatetGmTestbench(parameter) runsimulation ... generateReport exit」
- msg188: 「现在前端保存的cfg文件格式变了，新的cfg文件为目录下的input_new.cfg，主要变化为将device参数展平」
- msg356: cfg 格式再次升级（删 scale、电压多值、port_name=d/g/s/b、device 参数行展平、bias 含 extract 子串）

## 关键真实产物
- `/home/rongjiez/jira_dev/mpqa/mp_1/scripts/input.cfg`（真实 cfg，已采为 assets A）:
  - model = /apps/imctf/models/cxmt10G5/v0.0/Model_v0d0_10G5.sp
  - scale=1, shrink=0.268, drnPortName=drn, vth measure method=slope
  - corner=tt/ss/ff, voltage vdd=1.03, voltage vpp=3.0, temperature=-10/25/98
  - 4 个 device: ntn(w1.440u l0.175u nf1), ptn(w3.261u l0.175u nf1), ntk(w3.261u l0.433u nf1), ptk(w6.519u l0.433u nf1)
  - bias 格式 `vth=0.05/vdd/0/0 isat=vdd/vdd/0/0 ioff=vdd/0/0/0 cg=0/vdd/0/0`（vg/vd/vs/vb 斜杠四段，电压名需解析为数值，前导 - 取负）
- `runModelQA.pl` 子程序: generate_temp_netlist (模板头 .lib/.option scale/.temp/.param/***)、generate_idsat_netlist / generate_ioff_netlist / generate_vth_netlist / generate_cgg_netlist / generate_idvd_netlist / generate_idvg_netlist
- agent 重构产物: `runModelQA_new.pl`（perl）

## 合成映射 (schematic_netlist, track=synthesized)
把「读 cfg -> 生成 testbench 网表」一段独立成 Python3 CLI `gen_modelqa_tb.py`：
- 解析 input.cfg -> devices.json (PVT 块 + devices 列表，每个 device 含 w/l/nf + measurements{vth,isat,ioff,cg} 的原始 bias 串)
- 生成 template.sp (lib/scale/temp/param/***) 
- 每个 device×corner×temp 生成 `<dev>_<corner>_<temp>_idsat.sp`（MOS 实例 + 4 个电压源取自 isat bias 四段 + .dc 扫描 + .measure idsat）
- bias 电压名解析为数值（vdd->1.03 等），前导 - 取负

## 隐藏 B (不同规模/结构)
5 个 device (nmos/pmos/nhvt/phvt/nio) × 2 corner (ff/ss) × 2 temp (0/85) = 20 idsat 网表；电压名 vcc=0.9/vbb=2.5（非 vdd/vpp），w/l/nf 与 corner/temp 数量都与 A 不同（A=4×3×3=36）。

## 检验
- check.py 12 条件 a-l；ref PASS 12/12；4 negative (empty/print_only/naive_hardcode/wrong_parse) 全 FAIL，首错分别为 b/c/h/d（互异）；negative_selftest rc=0；§4.9 三假提交 (empty-zip/print-expected/core-deleted) 全 FAIL。
- check.py sha256=0f32ce8a539abf2e4304e51d8f2834211e95699673b3cee3f6b5279f472c15e7
