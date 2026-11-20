# 深读笔记 · 1794894403458_lk95a (ryanren / hfeg0pfn048 / mc=48)

- session: `1794894403458_lk95a`，user=ryanren，host=hfeg0pfn048(10.129.2.13)
- 26 msgs，3 个实质 user 轮，model=deepseek-v4-flash，cwd=/home/ryanren
- 标题: HSPICE iprobe 电流探测 stimulus 审计（pumpcore_sim_spf）
- 可达性: 真实 stimulus `/rundata/dscqa/V0/simdir/hspice/ryanren/pumpcore_sim_spf/tb/01_stimulus.sp` 与真实 netlist `/proj/dscqa/V0/workdir/ryanren/simulation/Ryantest_pumpcore_sim_spf_schematic_ALPS/Ryantest_pumpcore_sim_spf_schematic.netlist` **均对 e0031982 权限拒绝**（ryanren 私有）⇒ A 档不可行，改 B 档：按 assistant 文字描述合成忠实 fixture。

## 用户原话（3 个实质轮）
1. `01_stimulus.sp这个激励文件有什么问题吗，我要看一个iprobe名字叫Iwlp的电流，其他的不看，检查一下我写的有没有问题`
2. `不是电压源，是电路里面接在输出端口的probe用来测量电流的但是我现在网表太大仿真太慢，所以我想只保留这个电流值。网表：/proj/.../Ryantest_pumpcore_sim_spf_schematic.netlist`
3. `/rundata/dscqa/V0/simdir/hspice/ryanren/switch_pumpcore_test/tb这个路径里面的01开头激励文件，里面的meas语句有问题吗为什么我没有输出测量结果`

## 用户真实意图
用户在大 SPF 网表（3669 行）中有一个名为 `XIwlp` 的 iprobe 子电路实例（probeI 类型，零压源），想在 stimulus `.sp` 中正确探测其电流且**只保留这一个 probe**（加速仿真）。用户的 stimulus 写了 `.probe tran isub(XIwlp)` —— 这是错的（`isub()` 测子电路管脚总电流，对二端 probeI 恒为 0）。

## 关键技术事实（来自 assistant 完整读网表后的诊断）
- `probeI` 子电路定义：`.SUBCKT probeI A B` / `v0 A B DC=0` / `.ENDS`（二端零压源 iprobe）
- 顶层 iprobe 实例：`XIwlp net0 net3 probeI`（line 3638）—— 测 net0→net3 电流（Vwlp 泵输出到 vwlp! 网络的电流）
- net0 ← Vwlp 泵输出端，net3 ← 通过 switch_close(0.001Ω) 接到 vwlp!
- 用户 stimulus 第 121 行 `.probe tran isub(XIwlp)` **错误**：isub() 对二端器件恒为 0（KCL：流入=流出）
- 正确写法：`.probe tran i(XIwlp.v0)` —— 引用 probeI 内部零压源 v0 上的电流
- 用户要求"只保留 Iwlp 电流"：删掉其余 probe，仅保留 `.probe tran i(XIwlp.v0)`

## case 设计（B 档 synthesized fixture）
- **交付** = 参数化审计生成器 `iprobe_audit.py`（读 manifest + netlist + stim → 审计 + 产纠错瘦身 stim + JSON 报告）
  - CLI: `python3 iprobe_audit.py --manifest <manifest.json> --netlist <netlist.spf> --stim <stim.sp> --out_dir <dir>`
  - manifest 字段：`iprobe_instance`（如 "XIwlp"）、`probe_subckt`（如 "probeI"）
  - 脚本职责：
    1. 在 netlist 中定位 `<iprobe_instance> <nodeA> <nodeB> <probe_subckt>` 行，提取节点
    2. 在 netlist 中定位 `.SUBCKT <probe_subckt> ...` 定义，提取内部零压源 instance name（如 v0）
    3. 扫描 stim 的 `.probe` 行：检测 `isub(<iprobe_instance>)` 标为 INCORRECT（恒为 0），检测 `i(<iprobe_instance>.<v0>)` 标为 CORRECT（若存在）
    4. 产 `corrected_stim.sp`：保留 stim 主体，把 probe 区替换为仅 `.probe tran i(<iprobe_instance>.<v0>)`
    5. 产 `audit_report.json`：含 iprobe_instance / probe_subckt / internal_vsource / nodes / stim_issues / recommendation
- **check.py** 跑 iprobe_audit.py 于 **隐藏 B**（不同命名：probeJ 子电路 + XJvdd netA netB probeJ，内部零压源 v1，stim 用 isub(XJvdd) 错误），15 条独立断言（a-o）
- **3 个 negative** + **§4.9 三假提交**全 FAIL，k_check=k_rationale=15>=8

## 选料
- candidates_mc10.tsv (210 行) 排除 all_ledger_sids(4089) → D-pure 过滤(netlist/schematic/analog/waveview dominant, 排 drc/lvs/calibre/pex/skill-creator) mc10+ → 多个 TRULY_FRESH 候选
- 高 mc 候选多为 skill-creator meta-work（alan17z 1n4ta/e243s/gwgz1, tongfanl onepv, tongni 1j0zt）或跨 shard dup（nh28n→B DcaStimSweepGen-001, 2gneu→B SimLogCompareReport-001, lvyy→B CmlBwExtensionHandbook）或 clarawu RON near-dup（euwld/svju2/exvvj）
- 选 lk95a (ryanren mc48, schematic_netlist, iprobe 电流探测审计): D-pure 干净 produce-script，用户真实意图明确，check() 有牙（subprocess 真跑 + 结构断言 + anti-hardcode）
- ledger lk95a claim ✓
