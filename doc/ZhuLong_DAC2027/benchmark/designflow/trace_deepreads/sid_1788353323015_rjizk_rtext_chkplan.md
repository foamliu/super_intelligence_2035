# trace_deepread — sid 1788353323015_rjizk (rtext_chkplan)

- **trace**: 1788353323015_rjizk.messages.json (e0014566 @ hfeg0pkn005, mc=339, 569 msgs, 1.4MB)
- **domain**: layout_virtuoso (Cadence Virtuoso SKILL + dbGet + OA, rscalc 电阻流)
- **tool_use**: run_commands×126, read_files×29, SandBox run_code(SKILL)×103, editor×34, skills×1, RAG×1
- **skill**: virtuoso-rtext-checkpoint-designer (+ virtuoso-rscalc-runner)

## 用户原话（A-档 seed, 纯需求）
- U1: `先看一下配置参数 rscalc.config, 获取到 目标 layout. 我现在要用rscalc计算电阻，看看其 powernet 上的RTEXT，没有的话，帮忙在合适的位置上打上。既然不能修改原本的layout, 请先原样拷贝一份这个layout, 然后分析，然后打上RTEXT。另外，请在配置文件rscalc.config 中修改 checkPoints, 以计算这点的电阻。增加的量控制在50左右，分布要广泛典型。不用真正打上RNODE，直接用checkPoints 表示RNODE就可以了。用 skill virtuoso-rtext-checkpoint-designer . 打好RTEXT 与 checkPoints 之后，评估下效果。`
- U2: `开始计算电阻值吧。计算完了之后，出一个报告在。英文报告，不要有乱码。`
- U7/U12: `请你评估下你目前的RTEXT 和 checkPoint 点，看看对于电路版图电阻分布的计算是否合理。`（评估轮，非新需求）
- U8: `好的，就按照你的改进意见改，并且修复短路。...`（修复轮，含根因→不作 A seed）

## 真实任务流
1. 读 rscalc.config → 目标 layout = `auto_austin_case1 / Array16G_T`（bBox (-17884.13,1343.068)-(17884.13,14767.0), w=35768.3 h=13423.9, 33041 shapes/37 inst, Labels 28 / RTEXT 0 / RNODE 0）
2. 拷贝 → `Array16G_T_rscalc`（不改原 layout，验收：原 cell RTEXT=0 RNODE=0）
3. 分析 power nets = vcc / vss；M5/M4 power stripes（垂直 stripe，interleaved vcc/vss X 位置；top M5 stripe 全宽连续）
4. 打 RTEXT（M5/RTEXT layer，via-stack≥2 处）：终值 vcc(-17865.3,1468.5) / vss(17859.8,1468.5)（y=1468.5 底 stripe 中心，via-stack M5/M4/M3/M2/M1=1/2/3/3/2 全叠）
5. 改 rscalc.config checkPoints：50 个（vcc 25 + vss 25），M5+M4，X 覆盖 100% / Y 99.5%，左 62% 右 38%，底 50% 顶 50%，format `list(list(net x y layer)...)`
6. 跑 rscalc（Virtuoso -nograph -replay）→ .rvn 报告 → 英文报告 RsCalc_Report_v2.txt（vcc 99.45M nodes / vss 215.88M nodes，14 vcc data rows，无短路）

## L2 阻塞 → L1-boundary 可验证核心
live Virtuoso/OA + rscalc 被 .75 沙盒阻塞。抽 L1-boundary：**RTEXT/checkPoint 规划器** `rtext_checkpoint_planner.py`（纯 stdlib）。
- 输入 layout JSON: bBox + pwrNets + shapes[{net,layer,bbox}] + rtextLayer/checkLayers/targetCount/coverageMin/balanceTol/viaStackMin
- 输出 plan JSON: rtext[{net,x,y,layer}] + checkpoints[{net,x,y,layer}]
- 算法：RTEXT=每 net 在 rtextLayer stripe 上 via-stack(叠层数)≥viaStackMin 的点（取 max via-stack site 中心）；checkPoints=targetCount 点分布跨 bBox（≥coverageMin X/Y 覆盖），每点落在所标 net+layer 的 stripe bbox 内，net 平衡(50%±tol)，两 checkLayers 都在。

## 资产
- A(可见) layout_A.json: 真 bBox + vcc/vss interleaved M5/M4 vertical stripes + 底 edge via-stack site（M5/M4/M3/M2/M1 叠）
- 隐藏 B: 不同 stripe 位置/数量/层数（杀硬编码）
- 隐藏 B2: 极简跨输入守卫

## 判分 14 条 a–n（见 reference check.py）
①zip+py+compile+stdlib ②rtext 一/net+点在 stripe ③via-stack≥min ④rtext layer ⑤count≈target ⑥cp 点在 stripe ⑦覆盖≥min ⑧net 平衡 ⑨两 layer 在 ⑩反硬编码 B ⑪B2 守卫 ⑫确定性 ⑬net 标注正确 ⑭rtext net==pwrNets
