# Deepread: 1788488738438_sroz5 — virtuoso-cli net-label 放置优化

- **trace_source**: user=junxu, host=hfeg0pkn005 (10.129.2.14), session=1788488738438_sroz5.messages.json, mc=1101, 848 msgs, 3.0MB
- **domain**: schematic_netlist (virtuoso-cli skill API 开发/调试)
- **scan**: ssh_eda_search_20261122_172249/summary.tsv (关键词 virtuoso:3211 schematic:1519 cellview:177 netlist:68 pyAether:64)
- **台账**: claimed r1180 (schematic_netlist, fresh mc≥5 池第 1 优先)
- **真实任务摘要**: 用户(junxu)是 virtuoso-cli skill 的开发者。本 session 接手上一位 agent 的 handoff，针对 `name_net` API 的 net-label 放置缺陷进行测试+修复：(1) label 总是打在右侧，当 pin 在器件左侧时 label 与器件重叠；(2) 纵向 net 的 label 应纵向放置在线旁而非横向。多轮用 mx4x1 / fifo_8x3 等器件验证，参考用户手动放好的 SEL0/SEL1 纵向 label。中段穿插 virtuoso 连接诊断（agent 误认 virtuoso 在本地→实际需远程；乱编 ip/port 都报 Bridge reachable 的 bug；hint 应读最新 port file）。尾声修 build_fifo.py 的 DOUT/FULL 输出 pin 方向渲染问题（out pin 看似 input）。

## 任务弧（user_input 时序，848 msgs 中 27 条 user 消息）
1. **MSG 0**（初始 handoff）: 上一位 agent 的 handoff，优化 name_net API — label 总打右侧，pin 在器件左侧时 label 与器件重叠，先测试再改进
2. **MSG ~50**: "net 是纵向的时候，net label 也应该是纵向的"
3. **MSG ~80**: "纵向的 label 有问题，会和器件重叠"
4. **MSG ~110**: "使用一些器件进行验证，将电路图发给我看"
5. **MSG ~140**: "你的电路呢"（催交付）
6. **MSG ~170**: "mx4x1 试一下这个器件"（指定验证器件）
7. **MSG ~200**: "纵向线的 label 不是很理想，纵向线的 label 应该纵向放置在线旁。SEL0 和 SEL1 我手动放好了，你可以参考"
8. **MSG ~230**: "总结一下最近的 api 优化改动"
9. **MSG ~240**: "最近一段时间进行了多次 api 的优化，你简要地梳理一下，不止于这一次会话中的内容"（跨 session 总结）
10. **MSG ~260**: 分析 session 0dxd2 为何 agent 连不上 virtuoso
11. **MSG ~280**: "还是失败了，它们似乎都犯了同一个错误，认为 virtuoso 运行在同一台机器上，实际是需要远程连接的"
12. **MSG ~300**: 命令构造 bug — "你构造的 commands 末尾有重复"
13. **MSG ~320**: "帮我修改下 virtuoso-cli，把这些提示直接放进 connect false 的报错提示里，提醒通常 virtuoso 不是跑在本地的，同时完善 SKILL.md"
14. **MSG ~350**: "我改过把 virtuoso 关掉了，你验证一下。hint 中还要加入两种可能，一种是没有执行一次性的初始化，另一种是需要用户手动进行重启"
15. **MSG ~370**: "/home/junxu/.cline/skills/virtuoso-cli 这个才是工作目录"
16. **MSG ~390**: 乱编 ip/port 都报 "Bridge is reachable" — 连通性检查 bug
17. **MSG ~410**: "127.0.0.1 不应该连通啊"
18. **MSG ~430**: "不对，我乱编 ip 和端口号，都报告 Bridge is reachable"
19. **MSG ~450**: "hint 应该使用最新的 port file"（×2）
20. **MSG ~470**: "看一下 fifo_8x3 这个电路，里面一些器件的连线很怪，怀疑是 stub 自动选择的 direction 有问题"
21. **MSG ~490**: "build_fifo.py 这个脚本构建出来的 DOUT 和 FULL 这两个 out pin 的方向不太对，以至于看上去像是 input pin，api 需要优化"（×2）

## 核心 API 缺陷（label 放置，本 case 焦点）
1. **P0 — label 方向硬编码右侧**: `name_net` 在 net 起点右侧打 label，当 pin 在器件左侧（器件在 pin 右侧）时 label 与器件 bbox 重叠。修复：label 应放在 pin 远离器件的一侧（pin 在左→label 在左，pin 在右→label 在右）。
2. **P0 — 纵向 net label 方向错误**: 纵向 net 的 label 被横向放置。修复：纵向 net（wire 主方向 |dy|>|dx|）→ label orientation="vertical"，横向 net → "horizontal"。
3. **P1 — 纵向 label 与器件重叠**: 纵向 label 放置点未避开器件 bbox。修复：label 锚点 = pin 位置 ± 偏移（沿 wire 方向远离器件），确保 label 点不在任何器件 bbox 内。

## 造题方向（合成目标）
- **case_id**: EDA-Eval-DesignFlow-VirtuosoCliLabelPlacer-001
- **类型**: L1 几何算法（确定性，无需 live EDA）
- **SUT 任务**: 写 `label_placer.py`，读 schematic JSON（devices bbox + nets wire/pins/side），为每个 net 计算 label 放置 (x, y, orientation, justify)
- **规则**: orientation 由 wire 主方向决定；label 锚点 = 第一个 pin 位置，沿 wire 方向偏移 2.0 远离器件（pin side left→x-2, right→x+2, top→y+2, bottom→y-2）；label 不得在任何器件 bbox 内；在 schematic bounds 内；距 wire ≤ 5.0
- **A** = fifo_4x3（可见）：4 器件 + 5 net（2 纵 3 横）
- **B1** = mux_8x1（隐藏）：2 器件 + 4 net（3 纵 1 横）— 结构性不相交
- **B2** = shiftreg_4x1（隐藏）：4 器件 + 5 net（3 横 2 纵）— 与 A/B1 几何不同
- **check.py**: 12 条独立断言 (a-l) — schema 完整 / 每 net 一 label / 无器件重叠 / 纵向 net→vertical / 横向 net→horizontal / bounds 内 / 近 wire / 横向正确侧 / 纵向正确侧 / 确定性 / 反硬编码(B1/B2 同规则) / B1≠B2
- **§4.9 三假**: print_only(静态 A 坐标) / core_deleted(空 label) / hardcode_a(A 坐标硬编码) — 均在 B1/B2 上 FAIL
