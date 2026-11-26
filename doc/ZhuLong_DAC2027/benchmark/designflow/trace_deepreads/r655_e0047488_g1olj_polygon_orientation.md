# r655 deepread: e0047488@g1olj@hfeg0pkn003 (10.129.2.12)

- session: 1794463882487_g1olj.messages.json (748KB, 56 msgs, 36 user turns)
- user: e0047488, host: hfeg0pkn003, mc=76, keywords: aether:296;drc:264;cellview:70;dbcreatepolygon:39;virtuoso:33;schematic:31;floorplan:20;calibre:20
- tools: virtuoso 31, cellview 26, schematic 12, pyAether 9, dbCreateRect 6, skill 5, dbGet 4, synthesis/netlist/hspice 1 each
- domain: physical_verify / layout_aether (DRC measurement geometry + polygon construction)

## User intent (trace-faithful, 逐字)
- U#0: "请问aether等软件以及DRC等中，'量测函数'的量测方法，多边形的构造/表征方式，是如何的？我想从这个角度分析、指导我们在用模型构建pattern图形时，如何设计数据结构"
- U#22: "抛开我们当前的项目不谈，我正在尝试从aether的角度出发来理解、分析数据结构。多边形或边的interior-facing和exterior-facing是如何确定的？"
- U#25: "你的意思是，基于：1.最小充分集 = 有序顶点环 + 环方向约定（外环 CCW / 洞 CW）+ 拒绝自相交。 2.任何布尔/SIZING 运算后，重新规范化环方向 就可以构建出基础数据结构，以此推导所有的函数操作？"
- U#35: "R-tree 空间索引、梯形/矩形分解 分别是指什么"

## Assistant artifact (gold)
- `/home/e0047488/QA_pattern_repo_linux/workspace/orientation_demo.py` (174 lines, 7061 bytes)
- 验证程序全部通过 (assistant 末段确认)
- 实现 7 个纯几何谓词: signed_area / left_normal / winding_number / in_material / check_invariant / facing_pair / offset_loop_orthogonal
- 验证 P1-P5 命题: 简单环方向(rect/L/U) / donut(外CCW+洞CW) / facing对(Width/Space) / sizing(扩张+收缩重规范化) / 自相交环(bowtie不变量破坏)

## Gold 判定
- 用户 U#25 总结出"最小充分集"命题 → assistant 产 orientation_demo.py 验证 → 用户 U#35 转问 R-tree(隐式接受 orientation 答案，前进到下一话题)
- gold = orientation_demo.py 的 7 谓词 + P1-P5 验证逻辑，全部自测 PASS
- 核心 deliverable: 实现"从环方向推导所有几何谓词"的验证工具

## B档 mock-behavioral reframe
- 真实 orientation_demo.py 在 /home/e0047488/QA_pattern_repo_linux/workspace/ (沙盒不可达)
- reframe: 合成紧凑可运行 task_brief + context.md (描述命题) 作 asset A
- deliverable = `polygon_orientation_tool.py` 实现几何谓词 + self-verify 命题
- hidden B = 不同 polygon shapes (trapezoid / T-shape / donut-v2 / stepped-notch) 反硬编
- check() 跑候选模块的几何谓词 against hidden B，断言精确几何结果 (area/winding/facing/sizing/invariant)
- distinct vs r652(pex-batch-path-resolve) / r650(cut-layer-idx-bugfix) / r645(svrf-antenna-rule-family) / r642(via-enclosure-r90) / r634(nonascii-sanitize): 本 case = polygon-geometry-predicate-verify 子型

## trace_source
- user: e0047488, host: hfeg0pkn003, session_file: 1794463882487_g1olj.messages.json, match_count: 76
- real_task_summary: 用户探索 aether/DRC 量测函数的多边形数据结构原理(环方向/绕数/facing/sizing/自相交)，assistant 产 orientation_demo.py 验证"有序顶点环+环方向约定+拒绝自相交→推导所有几何谓词"命题，全部 PASS
