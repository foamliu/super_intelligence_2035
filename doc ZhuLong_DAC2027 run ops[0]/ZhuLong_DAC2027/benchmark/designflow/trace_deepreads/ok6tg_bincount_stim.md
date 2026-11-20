# trace deepread — 1795086090156_ok6tg (zanezang / hfeahpc501 / 10.129.33.24)

## 元数据
- sid: 1795086090156_ok6tg
- user: zanezang  host: hfeahpc501 (10.129.33.24)
- match_count: 30 (hspice:30; netlist:9; lvs:6; mosfet:5; synopsys:4)
- domain: spice_sim (shard B)
- 来源: r915 698 机重扫 (11/19 summary) → 41 fresh B-domain sid, ranked #19 (score 30)
- 取回方式: .75 eda_flow.run_commands ssh 10.129.33.24 cat messages.json (27KB / 2 msgs: 1 user + 1 assistant)

## 用户原话 (msg 0, 唯一一条 user input, 逐字)
> 我正在写hspice的激励文件，引脚名为MRCode<6:0>,请给我写出激励信号，要求数字信号从0000000依次进位到1111111，每次的周期为1ns，高电平为参数vh,低电平为参数vl

## assistant 交付 (msg 1, 逐字要点)
- 设计思路: 二进制计数第 i 位(LSB=0)是 50% 占空比方波, 周期 2^(i+1) ns / 脉宽 2^i ns / 首次翻转延迟 2^i ns → 7 个 PULSE 源即可精确构成 0000000→1111111, 无需写 128 行数据表
- 给出完整 deck:
  - `.param vh = 1.2` / `.param vl = 0`
  - `VMR0 MRCode<0> 0 PULSE(vl vh 1n 0 0 1n 2n)` … `VMR6 MRCode<6> 0 PULSE(vl vh 64n 0 0 64n 128n)`
  - `.tran 1p 128n` + `.end`
- 时序自检表 (0~1ns=0000000, 1~2ns=0000001, …, 127~128ns=1111111)

## 任务性质判定
- 真实意图: 生成 HSPICE 二进制计数总线 PULSE 激励 deck (one-off 问答)
- trace-faithful A 档: 用户原话直接作 prompt, 真实参数 (MRCode/7/1ns/vh=1.2/vl=0) 作 asset A
- harness-for-teeth reframe: one-off deck → 参数化 `bin_count_bus_stim_gen.py` (读 spec.json{bus_name,width,step,vh,vl} → 输出 deck). 必要性: one-off deck 无独立可失败断言(只能比字符串); 参数化后 hidden B(异 bus/width/step/vh/vl) 可验通用性 + bit-i 方波不变量 → 12 条独立可失败断言, 不需 hspice rerun (PULSE 参数完全决定波形)

## 合成计划
- case_id: EDA-Eval-DesignFlow-BinCountBusStimGen-001
- asset A: spec_A.json (MRCode/w=7/1ns/vh=1.2/vl=0) + task_brief.md + prompt.txt
- hidden B: spec_B.json (DataBuf/w=6/500ps/vh=0.9/vl=-0.1) + hidden_manifest.json
- reference: bin_count_bus_stim_gen_ref.py + check.py (12 断言 a-l) + 5 negatives (empty/print_expected/core_deleted/hardcode_a/no_param)
- 判分: 纯 Python 解析 deck 文本, 验 bit-i 公式 TD=PW=2^i*step, PER=2^(i+1)*step, .tran=2^N*step, 反硬编码 A
- k_check=12 (>=8 ✓), k_rationale=12
