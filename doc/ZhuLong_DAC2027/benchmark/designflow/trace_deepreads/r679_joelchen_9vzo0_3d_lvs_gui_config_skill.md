# Deepread r679 — joelchen 9vzo0 (10.129.33.128, mc35)

## trace_source
- user: joelchen, host: 10.129.33.128 (hfeg0plg...), session: 1792379734870_9vzo0
- match_count: 35, keywords: cmos:298;lvs:198;schematic:76;drc:54;gdsii:45;calibre:35;netlist:9;aether
- 26 msgs / 15 user / 11 assistant / 12 tool_uses (4 read_files, 4 editor, 2 list_allowed_files, 1 search_codebase, 1 skills)

## 真实用户意图（user turns, 逐字原文）
- U1 (核心 produce-task):「3D LVS GUI config skill：/home/joelchen/config_skill_example 是一份DEGPA项目V0版本的3D LVS GUI的config，在GUI界面load该文件后可以自动填入相关内容。我需要生成一个skill，能够基于用户提供的必要信息，针对特定项目的特定版本自动生成config文件内容，从而节省针对不同项目手动配置文件的时间消耗。 接下来，我来讲述config文件内容的具体细节：首先是[System Options] 部分，System Source指系统级网表路...」
- U2:「帮我加载一下你生成的这个skill」
- U3 (refine):「微调一下这个skill，多块die的Layout Path等号后不填写，不需要向用户询问该信息，请帮我重新生成」

## assistant 工具链（真实产物）
1. read_files `/home/joelchen/config_skill_example` (DEGPA V0 实际 config, 4 段: System Options/Chip Options/Interface/Connectivity)
2. list_allowed_files /home/joelchen, /home/joelchen/skills; search_codebase INDEX.md
3. read_files INDEX.md, skill-creator/SKILL.md, calibre... skill
4. editor 创建 `/home/joelchen/skills/3d-lvs-gui-config-generator/SKILL.md` (184 行, 三次追加) + 更新 INDEX.md
5. read_files 验证两文件完整
6. skills load (失败: 注册表无) → read_files 直读加载

## 金标准 = 用户接受的真实产物
- `/home/joelchen/skills/3d-lvs-gui-config-generator/SKILL.md` (184 行, 已 scp 到 .75 session)
- 用户 U3 接受: 多块 die Layout Path 等号后不填写

## 提取的硬规则（reframe 依据）
**4 段顺序**: [System Options]→[Chip Options]→[Interface]→[Connectivity]
**键值分隔**: ` = `; 留空字段 `Key =`
**[System Options] 固定/留空**:
- 留空: System Source, Source Top, Placement, PVRS Rules, Run Directory
- 固定: 3D Port Layer=1, Ignore Top Port=0, Bump Number=10000, CPU Number=32 (NOT 64 样例陷阱)
**[Chip Options]**:
- Chip Name = CmosDie + ArrayDie/ArrayDie1..M (M=1 无编号 ArrayDie, M≥2 ArrayDie1..M)
- Layout Path 1..N: 每 die 一行, 等号后一律留空 (U3 核心规则), 键名 `Layout Path 1` (Path 后空格)
- Layout Format = N × gdsii (空格)
- Layout Top = N 个 gds top (空格, 顺序同 Chip Name)
- Source Path = 留空
- Source Format = N × spice (空格)
- Source Top = N 个网表 top (空格)
- Hcell = N 个 hcell 路径 (空格)
- LVS Rule Path = N 个 rule 路径 (空格)
- Lcv Layout = `<proj>_cmos_top * layout,<proj>_array_core * layout` × M (逗号, 无空格; cmos 1 项 + array M 项)
- Lcv Schematic = 同上 layout→schematic
- Other params = N × `{}` (空格; NOT 样例 var(...) 陷阱)
**[Interface]**:
- Main Instance Name = 留空
- Instance Name = `Bot_Inst Top_Inst` (M=1) / `Bot_Inst Top_Inst1..Top_InstM` (M≥2); Bot_Inst↔CmosDie, Top_InstN↔ArrayDieN
- Master Name = 与 Chip Name 逐字符一致
- Location = N × `(0 0)` (空格)
- Magnify = N 个 shrink (空格)
- Rotate = N 个旋转/镜像 (空格)
- X-axis Mirror = N × `/` (空格)
**[Connectivity]**:
- Connectivity Name = P × `LOGIC_DRAM_TOP` (空格; P=堆叠对数, NOT 写死 1)
- Instance Name = 每对 `Bot_Inst Top_InstN` (对内 下/上), 多对逗号连接 (无空格)
- Layer = 每对 2 个 layer (对内 die1/die2), 对间逗号 (无空格)

**已知陷阱 (judge 可验)**: CPU=64→32, Layout Path 填路径→留空, Other params var(...)→{}, Layer HLP→HLPnet 全名

## reframe 决策
SKILL.md 是 text artifact, 静态子串查违反 §4.3 → **mock-behavioral reframe** (承 r645-r678 家族):
新子型 `3d-lvs-gui-config-gen` (SKILL→Python generator), distinct vs r678=spf-coupling-sort/r677=exempt-row-layout-fix/r673=skill-load-il。
deliverable = 纯 stdlib `lvs_gui_config_gen.py`, 输入 JSON spec (project/dies/stacking_pairs), 输出 4 段 config 文本到 stdout。
check() subprocess 跑 B (全异 project/die 数/堆叠对) + B2 (退化 M=1), 解析输出 config, 验 ≥16 结构条件 (段序/留空/计数/命名/固定值/陷阱/防硬编/确定性)。

## 选料对照 (本轮 peek 3)
- 9vzo0 (joelchen mc35): **VIABLE ✓ BUILD**
- 1kbzp (ruifan mc35, aether:129): U1「start aether」/「-adv」/「python3 start_aether.py」= GUI launch, 无 produce-task → **teeth-fail park**
- 8dr7s (mhyu mc35, pdk:39): U1「分析 .spz 文件 pre_sim 相关内容 + 变量交叉引用」= 开放式 prose 分析, check 无 ≥8 独立非子串条件 → **teeth-fail park** (排除标准②判分无牙; 任务类型合法但不可造)
