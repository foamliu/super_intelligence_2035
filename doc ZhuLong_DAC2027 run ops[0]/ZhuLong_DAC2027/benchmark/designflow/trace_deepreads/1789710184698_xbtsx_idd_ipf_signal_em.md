# trace_deepread: 1789710184698_xbtsx (yongk1li @ 10.129.8.125, mc=77)

## 用户与场景
- 用户: yongk1li (CXMT DRAM 设计团队, signal-integrity/可靠性)
- 工作目录: /home/yongk1li/Desktop, 可写 /home/yongk1li/bin, /home/yongk1li/Desktop
- 项目: /home/yongk1li/bin/totem_sc_signal_em/ — Totem-SC Signal EM (信号电迁移) launcher (Tkinter GUI)
- 配套脚本: idd_to_ipf_flow.py — Finesim IDD 仿真 CSV → Totem-SC IPF 功耗文件

## trace 对话流 (85 msgs)
1. "你是什么模型" (meta 问询) → agent 自介 zhulong
2. "/home/yongk1li/bin/totem_sc_signal_em/ 这个是干嘛的?" → agent list+read README/totem_sc_signal_em.py → 解读为 Totem-SC LPE/Signal EM/Rpt 流程 GUI 工具
3. "/proj/drcoa/V0/workdir/yongk1li/simulation/DDR5TOP_4_channel_gds_only/white_box_cell/idd_to_ipf_flow.p 看看这个脚本是干嘛的" → agent read idd_to_ipf_flow.py (265 行) + output.ipf → 解读: IDD CSV → IPF 功耗文件, 按 OUTPUT_SPECS 规则提取 cell 实例 × 电压算功耗, GDS 纠正大小写, 归一化扩充 100 实例
4. "能修改这个脚本吗" → agent 确认 policy, 可写 ~/bin
5. **核心修复请求** (用户原话):
   > "1. 不许兼容 老功能:  2.CSV 里 cell 名都是小写（bcenterca），但规则里写的是 BCenterCA，直接 in 比较匹配不上。需要在 apply_spec 里做大小写不敏感比较："
6. agent 尝试 editor 改 /rundata/... 路径 → 拒 (outside writableRoots) → run_commands 也禁 → 用户: "如果不行就 修改 ～/bin/idd_to_ipf_flow.py 这个文件" → agent 在 ~/bin/ 副本上修改

## 脚本核心逻辑 (idd_to_ipf_flow.py, 492 行)
- INPUT_DIR=./IDD, 每 CSV = 一个 power domain (文件名去 ! 查 POWER_DOMAIN_VOLTAGES)
- 阈值: root idd > IDD_THRESHOLD(1000 uA) 才保留
- OUTPUT_SPECS 多规则: {level, father, include, exclude, leaf_fallback}
- get_level_instances: root=L1 逐层展开, leaf-fallback (到底叶子携带到目标层, 记 carried_set)
- apply_spec: father 看父节点 cellName (补偿叶子看自身), include/exclude 看自身
- power = voltage * idd * 1e-6
- GDS 流式读 STRNAME 建 lowercase→正确大小写 map (本 case 改读 gds_cell_map.json, 因 GDS 路径常权限拒)
- normalize_entries: 按 (power_pin, base_name) 求均值, 每 cell 扩充 NORMALIZE_INSTANCE_COUNT=100 实例 (首行无后缀, _0.._98)
- 输出: output.ipf (2 行 header + inst\tpower(%.8f)\tpin), WHITE_BOX_CELLS, idd_inst_dump.txt

## 两处 bug (用户要求修)
1. legacy compat: TARGET_LEVEL/TARGET_CELLS/TARGET_FATHER_CELLS + main() `if not OUTPUT_SPECS: fallback` 分支 → 删
2. apply_spec 大小写敏感: _to_set 用原始字符串, CSV 小写 "bcenterca" vs 规则 "BCenterCA" 不匹配 → 改 _to_lower_set + .lower()

## case 化决策
- A 档 trace-faithful: 用 yongk1li 原话两条修复要求作任务说明
- L2: 修 bug + 跑脚本产 IPF, check 在 hidden B subprocess 真跑 + 解析结构
- Input A: vcc.csv (5 层, lowercase cell, root idd 5000) + gds_cell_map.json
- hidden B: vdd1.csv (root idd 6000, father BCenterCA vs csv bcenterca 失配) + viso.csv (root idd 800 <= 阈值, 应跳过) + 不同 gds map
- 10 断言 k_check==k_rationale==10≥8
- ~/bin/ 版已是修复后 (作 reference); /rundata 原版权限拒, 我据 diff 重构 buggy v1 (case-sensitive apply_spec + legacy block)
