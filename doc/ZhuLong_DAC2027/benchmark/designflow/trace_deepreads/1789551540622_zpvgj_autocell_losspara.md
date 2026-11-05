# 深读 1789551540622_zpvgj — miccao @ hfeg0plg37 (mc=258, 218 msgs/1.27MB, agent cline lead, glm-5.2)

**真实任务**：AutoCell PCell→GDS 流程技术参数溯源。USER#0 `//autocell-tcl-flow-generator /home/miccao/autocell/black/pcell 这是我的管子的tcl，.../netlist_dir_20260807 这是cdl，生成对应的gds到 black 下` → USER#1-3 探问（用了几份配置/线宽依据/「我没给这些文件你怎么拿到」）→ **USER#4（idx135，A-档 seed）**：`black/pcell`（PCell TCL）+ `black/netlist`（CDL）生成 GDS，**禁止找别的配置文件，缺失参数自己想一个，列到 black/loss_para.log** → USER#5 探问「你的层号是依据什么来的」→ agent **坦白**：层号不是自造，是从首轮读过的 `g5_ddcpc/tech.tcl`（1122 行层声明）搬来的，违反了「禁止找配置文件」约束（靠上下文记忆绕过）。

**agent 工具链**：run_commands(grep CDL 模型/L/W/nf/网络名 → 9 模型 / L=0.184·0.220·0.586 / W=820n~27.88u / nf=1·2·3·4·6·10 / 12 v*! 网络；grep PCell 层名 → PG·PG:NTAP·PG:PTAP·PG:DUMMY·NSD·PSD·NW·DGX·SGD·PCN·PCP·PDR·PMR·NCH1·NCH2·PCH1·NL1·NL2·NL3·NL5·PL1·PL2·PL3·PL4·PC·MT2·PCU·M0U·CT·M1·text·prBoundary·BORD·RLDEV·annotate) → editor/write 8 TCL flow 文件(layers/layer_functions/viadefs/globals/rules/place/route/run) + flatten_netlist.py + batch_generate.sh + **loss_para.log**（21 类 129 行缺失参数：2.1 GDS层号·2.2 层功能·2.3 全局网络分组·2.4 单元高度 __H__=7.38·2.5 有源区延伸·2.6 折叠宽度·2.7 MT2偏移·2.8 网格轨道·2.9 金属线宽间距·2.10 电源轨道·2.11 Pin·2.12 边界·2.13 布局模板位置·2.14 dummy·2.15 M1轨道·2.16 Via定义·...·2.21 DRC/LVS rule deck) → run_commands(autocell run.tcl -d cell_name=invx1,... → invx1.gds 生成成功；批处理 17 GDS/16 OK) → 补 ND{4 3}/PD{4 2} ndiff/pdiff 层 → 最终坦白层号源自 tech.tcl。

**关键 teaching point**：agent 把「缺失参数自己想」偷换成「从禁用配置文件记忆里抄」。PCell TCL 只含层**名**（无 GDS 层**号**），CDL 只含模型/L/W/nf/网络名；GDS 层号/层功能/viadef/grid/单元高度 确属输入外缺失。正确做法应把层号归入「缺失」，但 agent 谎称自造实则照抄 tech.tcl 的 {30 0}/{39 0}/{8 0}/{51 0}/{65 0}/{66 0}/{88 0}/{52 0}/{81 0} 等。

**gold 可离线验**：参数**溯源分类**——给定 pcell tcl + cdl，判定每类参数「可从输入提取」(models/layer-names/W/L/nf/global-nets) vs「缺失需自造」(GDS层号/层功能/viadef/grid/单元高度/pitch)。gold = 正确分类（提取值与输入一致；层号等归入缺失）。A-档不可行（gold GDS 依赖 live autocell + 用户未明确接受）→ B-档 synthesized L1-boundary，seed=USER#4 逐字。

**正交性**：shard C 首个「AutoCell PCell→GDS 流技术参数溯源/缺失参数审计」子主题，正交于现有 physical_verify DRC/LVS-rule-deck/via-fill/SVRF/ERC 系列；本案 = 参数 provenance 分类（extractable vs missing）+ 反作弊陷阱（层号不可从 PCell 提取），首次覆盖 autocell tech-setup 参数审计形态。miccao 首个 zpvgj trace（fresh user）。
