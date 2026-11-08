# r268 深读 — fkprl rscalc RTEXT/RNODE 放置规划

**trace**: 1786504317615_fkprl (e0014566 @ hfeg0pkn005/10.129.2.10, mc=640)
**kw**: cellview387 + virtuoso249 + pyAether108 + dbShape35 + dbGet153 + schematic32 + "lang":skill77
**agent**: lead deepseek-v4-flash, 663 msgs, 14 real user turns
**domain**: layout_virtuoso (rscalc 电阻设置准备)

## 用户真实意图（逐字）
- U0(提出需求,未给根因,A档eligible):「请你帮忙看下 Library:auto_austin_case1, Cell:Array16G_B, View:layout 这个版图。我现在要用rscalc计算电阻，看看其powernet上的RTEXT，以及RNODE有没有打齐，没有的话，帮忙打上。」
- U1:「三个 RNODE 标签太少了，能不能通盘分析一下。要想分析清楚版图的电阻情况，需要采样多少点，都打上RNODE标签。」
- U2:「给出脚本，我自己执行吧。」
- U3:「这个点会不会太多，从而导致后续计算电阻非常慢」
- U4:「好了，现在这些都可以编辑了，你帮我把这些都加上吧。」
- U5-U6: SKILL 错误 (setnth undefined / strcat arg type)
- U7-U8:「执行好了，帮我看下。是不是RTEXT 和 RNODE 都打好了。」
- U9-U10: isEditable=nil 调试
- U11:「为啥打不上 RNODE标签呢，我之前都操作过类似的，好奇怪。」

## grounding（agent 真实工作）
- **版图**: auto_austin_case1 / Array16G_B / layout
- **powernet 结构**: 3 个 power net — vcc!(104 pins) / vss!(96 pins) / viso!(16 pins)，**全部 216 个 pin figure 都在 RDL 层**
- **rscalc 标签语义**（agent 从 run_rscalc_nogui.il 推断）:
  - RTEXT = net 级标签，每个 net 在每个参与金属层上需要一个（用于 addNets.txt 自动检测 net 名）
  - RNODE = point 级标签，电阻测量检查点，每个 pin figure 位置打一个（用于 addPoints.txt）
  - PointLayers = list('("MT2" "RNODE") '("M0U" "RNODE") ... '("RDL" "RNODE"))；NetLayers = 对应 "RTEXT"
  - CXMTTransformedLabelToTop: RNODE 标签 text=net name, xy=测量点
- **agent 计算**: 3 RTEXT（每 net 在 RDL 一个）+ 216 RNODE（每 pin 一个，xy=pin 中心）
- **交付**: SKILL 脚本 dbCreateLabel(cvId lpp xy text justify orient font height)，在交互式 Virtuoso 跑（CXMT 拦 -nograph batch），geGetWindowCellView 打开 edit 模式
- **踩坑**: isEditable=nil（窗口未开 edit）→ 改 geOpen edit；setnth undefined → 换 setnth 实现；strcat arg type → 转 string

## 为何 B 档重定义为离线 L2
真实 Virtuoso/OA/rscalc 不可沙盒复现。可离线化核心 = 从 powernet pin 清单（每 net 在某 layer 的 pin 坐标列表）计算 rscalc RTEXT/RNODE 放置方案：
- RTEXT: 每 (net,layer) 对一个（net 名 + 层标识）
- RNODE: 每 pin figure 一个（xy=pin 中心, text=net, layer=pin 层）
判分用 subprocess 真跑候选规划器（L2，非纯文本断言），断言输出结构（rtext/rnode 计数 + 覆盖 + 去重 + net 映射）。

## DISTINCT from 现有 layout_virtuoso 系
- r265 RscalcBsubPollRunner = LSF bsub 非交互提交+轮询状态机（job 提交侧）
- r236 SkillBindkeyFlattenMakeCell = UI bindkey
- r233 InstM0ShapePinIdentify = shape pin 识别
- r224 InnovusPwrRtDiag = Innovus power planning
本案 = rscalc **测量设置准备**（RTEXT/RNODE 标签放置规划：pin 清单→net-layer RTEXT + 每 pin RNODE 检查点），独立。
