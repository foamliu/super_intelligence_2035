# 深读 6pm3i — joeyl @ hfeg0plg74 (mc=245)

- session: `1795162616964_6pm3i.messages.json`（单文件 634882 bytes / 159 msgs）
- 用户/主机: joeyl @ hfeg0plg74（m2701 V0_DDR4 平台，FineSim/HSPICE 仿真）
- 工具关键词: netlist:1102 / hspice:93（首条 user msg 上下文）；session 偏 Python 脚本 + HSPICE netlist 改写
- 用户首轮要旨: 「用 `/home/joeyl/ulvt_delvto/` 工具包给 netlist 里 ULVT 管子加 vth=-0.2V（即 delvto=-0.2）」；目标 netlist `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/simulation/Bias/hspiceD/schematic/netlist/netlist`
- 真实任务: 把 `_delvto=-0.2` 参数 append 到 netlist 中所有 model 为 `pulvt_ckt` / `nulvt_ckt` 的 X-instance 行；工具 `reduce_vth.py` 读 spec、扫 X-instance、按 model 过滤、行尾追加参数、保持行数、吐 JSON report；`verify_netlist.py` 核对修改设备数（Bias netlist 实改 3 个：XM10/XM9 pulvt_ckt、XM18 nulvt_ckt）
- 后续: 同 session 再跑 delvto=-0.1，以及换 CML_C2C netlist 重跑（不同电路、不同目标管子）
- 性质: **clean produce**（参数化脚本生成 + netlist 改写 + report），属 spice_sim/characterization 边界（HSPICE netlist 后处理），非 debug/resume
- 取用: **A-grade direct reframe** — `DelvtoNetlistModifier-001`：参数化 `reduce_vth.py --spec <json> --data-dir <dir>`，spec 含 netlist/delvto/models/out/report 五字段；append `_delvto=<value>` 到 model∈spec.models 的 X-instance 行，保持行数，emit JSON report（line/inst/model/n_modified/n_lines_orig/n_lines_mod/verified）
- A/B 设计（5 维 anti-hardcode）:
  - A 可见: dir_A/netlist_A.sp（DDR4 Bias 分支，delvto=-0.2，models=[pulvt_ckt,nulvt_ckt]，11 X-instance / 3 target）
  - B 隐藏: hidden/dir_B/netlist_B.sp（CML C2C 分支，delvto=-0.15，models=[nlvt_ckt,plvt_ckt]，8 X-instance / 5 target）
  - 5 维: delvto 值 / 目标 model / instance 命名 / netlist 行数 / 电路上下文 全部不同
- 判分: 12 条独立断言（a-l）：①zip+py_compile+size>200 ②B exit0+产出netlist+report ③report含8顶层键 ④行数保持 ⑤n_modified==oracle ⑥modified model∈target ⑦modified line含_delvto=value ⑧非target行未被误改 ⑨report delvto==spec_B ⑩anti-hardcode A值缺席 ⑪orig无_delvto+mod有 ⑫3-seed sha256一致
- 三假: neg_empty（空 stub）/ neg_print_only（硬编码 A 的 -0.2 + A 的 models，无实际修改）/ neg_core_removed（去掉 model 过滤，append 到所有 X-instance）— 全 FAIL
- 自验: ref PASS 12/12；3 negs FAIL 3/3；3-seed 确定性通过（assertion l）
- 选取原因: B-domain（spice_sim）mc≥5 候选池 fresh top，6pm3i mc=245 netlist:1102;hspice:93 信号最强；clean produce + 参数化脚本 + 明确 A/B 可分离维度，适配 design_flow 双参 check(deliverable, workdir) 契约
- 台账: ledger_B 已 claim（session=1795162616964_6pm3i.messages.json / user=joeyl / host=hfeg0plg74 / match=245 / domain=spice_sim），case-id=EDA-Eval-DesignFlow-DelvtoNetlistModifier-001
