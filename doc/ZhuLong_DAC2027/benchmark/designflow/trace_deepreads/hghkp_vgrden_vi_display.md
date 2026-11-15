# hghkp — bensonh WaveView 打开 vgrden 电压和电流波形

## trace 溯源
- **session**: 1794373848190_hghkp
- **user**: bensonh @ hfeg0plg104 (10.129.8.235)
- **mc**: 32
- **session_file**: /home/bensonh/.cline/data/sessions/1794373848190_hghkp/1794373848190_hghkp.messages.json
- **total msgs**: 53

## 用户原话（逐字）
U#0/U#1/U#2（重复 3 次，act 模式）：
> 打开vgrden电压和电流波形

## trace 摘要
用户 bensonh 在 hfeg0plg104 上用 WaveView 看仿真波形，要求打开 vgrden 的电压和电流波形。
- 用户连续 3 次发送同一请求（act 模式），助手开始搜索文件系统。
- 助手 list_allowed_files 遍历 /home/bensonh、/proj/ddgoa/V0、/rundata/ddgoa 等目录。
- 在 /rundata/ddgoa/V0/simdir/finesim/workdir/bensonh/simulation/prc/res/ 下找到 **cgate.fsdb** 波形文件。
- 读取 signallist.prc / signallist_onesec.prc / cgate.sp（.param vdd2h=1.12, vdleq=1.13, vpcsg=1.6, vnoc=1.13, vblh=0.8, vwlp=2.6）。
- trace 在 53 msgs 处截断（助手仍在探索，未见最终交付）。

## 用户真实意图
打开一个波形文件（FSDB），在 WaveView 中显示 vgrden 这个信号的**电压**和**电流**两个波形。
= open-tool / waveform-display（有具体信号目标 vgrden + voltage + current）。

## case 设计（mock-shim tool-launch，套 #672 WvHierSignalOpen 范式）
- **区别 #672**：#672 = 单一层次化信号名解析（net1069 → xi_c_top.xi_array16gtop.v(net1069)）；本例 = 从基础网络名构造 V()+I() 双信号并都显示。
- **reframe**：用户意图=open waveform + display V+I，design_flow 契约需在隐藏 B 上跑候选 → mock-shim tool-launch orchestration（候选写 open_signal.tcl，source signal_spec.tcl 读 target_signal/filepath → 构造 V($name)+I($name) → sx_find_wave_in_all_files 解析 wave_obj → sx_display_wave 可靠显示 → sx_update_wv 刷新）。
- **可靠 vs 不可靠 API**（对应 #672 核心教训）：sx_find_wave_in_all_files + sx_display_wave（对象句柄，可靠）vs sx_display（按名字字符串，不可靠——trace 中"命令执行了但波形没 probe 出来"）。
- **data-driven**：A target=vgrden, filepath=/rundata/.../cgate.fsdb；B target=vpcsg, filepath=/proj/.../wave.fsdb；B2 target=GONE_NET（不存在→error）；B3 target=vdd2h, filepath=""（快速路径，文件已打开）。
- **反硬编码**：A 专属标识符 vgrden/cgate.fsdb/bensonh 路径不泄入候选源码；B 用中性信号名 vpcsg/vdd2h。

## check.py 15 条件 (a-o)
a) zip 合法含 open_signal.tcl
b) source signal_spec.tcl
c) B 运行 exit 0
d) B: sx_open_sim_file_read 被调用（filepath 非空→须打开文件）
e) B: sx_find_wave_in_all_files 查 V(target)（电压）
f) B: sx_find_wave_in_all_files 查 I(target)（电流）
g) B: sx_display_wave 被调用（可靠显示）
h) B: sx_display 未被调用（不可靠 API 规避）
i) B: sx_update_wv 被调用（刷新）
j) B: V+I 两个 wave_obj 都显示（≥2 个有效 WAVE_* 句柄）
k) B: V(B_target) wave_obj 显示（data-driven 电压）
l) B: I(B_target) wave_obj 显示（data-driven 电流）
m) 反硬编码：A 专属标识符不在候选源码
n) B2（信号不存在）exit 非零；B3（filepath 空）exit 0 + 不调 open + V+I 都显示
o) 确定性：重跑 B 调用日志 + 状态字节一致

## 自验
- REF PASS 15/15 ✓
- NEG_RC=0（8 negs 全 FAIL，6 distinct labels）✓
- §4.9 三退化（empty→a / print-only→b / core-deleted→e）全 FAIL ✓
- k_rationale == k_check == 15 ≥ 8 ✓
