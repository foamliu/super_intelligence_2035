# 深读笔记：2s98f — count_cell_usage.py（层次化 cell 调用次数统计）

- session: `1795687697314_2s98f.messages.json`（1.67MB, 323 msgs: 178 user / 145 asst）
- 用户: jcgu @ hfeg0plg81，mc=281，keywords: schematic:667+pyaether:357+dbopencv:426+aether:143+cellview:161+netlist:74
- 台账: domain=schematic_netlist，FRESH（4-shard 台账无 2s98f；jcgu 仅有 A/B shard parked wrong-domain 记录，本 session 为 D 域 schematic 主导）
- 取回: .75 eda_flow open_session(r1641) 秒级 + scp→hfeg0plg81 per-session subdir 取回 2s98f.json

## 用户真实意图（逐字首条）
> 「帮我写一个pyaether的脚本，我想从电路的top cell中检查某几个cell被调用的次数，这里有个点需要注意，如果中间层的instance是多bit的，如I1<0:5>，这时候就需要展开进行统计，注意这种多层hierarchy结构调用时的统计要完整，脚本可以在DM中直接运行函数,要求分别统计出每个cell被调用的数量和总量，可以输入到一个文件里，请完成这个脚本」

## 迭代调试逐步明确的 4 条核心语义
助手写 `count_cell_usage.py`（DFS 遍历 schematic hierarchy 统计 target cell 被调用次数），用户多次实测 DBG 反馈，逐步逼出 4 条语义：

1. **vector / array 展开**：`I1<0:5>` → 6 个实例；array `NxM` → N*M；vector+array 组合相乘。（首条需求 + U241 vector 递归问题）
2. **multiplier 传播**（U241/U244）：递归进入一个 vector master（如 `I0<0:1>` 展开为 2）后，它内部的每个子 cell 都要乘以 2（外层展开因子逐层累乘）。修复前子层 cell 只加 1 次没乘 vector 宽度 → 加 `multiplier` 参数，计数 `effective_cnt = cnt * multiplier`，递归传 `multiplier * cnt`。
3. **stop_libs 只阻递归不阻计数**（U114）：`stop_libs`（如 TECHLIB）不再往下查 hierarchy，但**该 cell 本身的调用次数照常统计**。用户原话：「stop libs应该是不往下继续查hierarchy,而不是这个lib里的cell不统计」。原代码 `if h_lib in stop_libs: continue` 把计数也跳过了 → 改为「计数照常，只不递归」。
4. **per-path 环检测**（U281）：全局 `visited` 集合阻塞了重复出现的 sub-cell——同一 sub-cell 经两条不同兄弟路径到达时，第二条因 id 已在 visited 被完全跳过，致 11 个 target cell 只查到 2 个。修复：改 per-path `path_ids`（copy+add），兄弟路径各计一次，仅当前路径上重复才算环。

## pyAether 运行时坑（不可合成，reframe 掉）
- `design.instHeaders` 是一次性迭代器，`len(list(headers))` 消费后 `list(headers)` 为空；且访问 instHeaders 后 `design.instances` 也返回空 → 彻底弃用 instHeaders，只用 `design.instances`。
- `inst.getMaster()` 在 schematic sub-master design 上返回 `.instances` 为空 → 改用 `dbOpenCV` 重新打开 master design 递归。
- 这些是 pyAether/Aether 运行时特定行为，eval 沙盒无 Aether DB，不可合成 → reframe 为 spec-JSON 驱动纯图计数器判分。

## case 合成（task_id=CellUsageHierCountProduce-001, LIVE-NA judge_layers=[L0,L1]）
synthesized-reframe：把「pyAether schematic hierarchy cell 计数」reframe 为通用 spec-JSON 驱动纯图计数器 `count_cell_usage.py(spec)->report.json` + hidden-B 反硬编码。

**spec schema**: `{top, top_lib, view, stop_libs[], target_cells[], cells{<name>:{lib, instances[{inst,cell,lib,vector?<lo:hi>,array?<NxM>}]}}}`

**A**(visible) spec_A.json — brk3 hierarchy：
- brk3(ztest): I5→brknetM2A(TECHLIB, vector <0:6>→7, stop_lib 计数不递归); I1→brk2(ztest, cnt1, 递归); I7→brk2(ztest, cnt1, 递归，兄弟路径)
- brk2(ztest): I0→brknetM1A(TECHLIB, vector <0:1>→2, stop_lib 计数不递归)
- brknetM2A/brknetM1A(TECHLIB): leaf
- target_cells=[brknetM1A,brknetM2A,brk2]
- GT: brknetM2A=7, brk2=2(I1+I7 兄弟路径), brknetM1A=4(2 路径×cnt2 each, multiplier 传播), total=13

**hidden B**(token-structurally 不同) spec_B.json — DffTop hierarchy：
- DffTop(core): U0→DffLatch(core, vector <0:3>→4, 递归); U1→BufX2(STDLIB, array 2x3→6, stop_lib); U2→DffLatch(core, cnt1, 递归兄弟路径)
- DffLatch(core): L0→InvX1(STDLIB, vector <0:1>→2, stop_lib); L1→NandX2(STDLIB, cnt1, stop_lib)
- target_cells=[InvX1,NandX2,DffLatch,BufX2], stop_libs=[STDLIB]
- GT: DffLatch=5(U0:4+U2:1), BufX2=6(array), InvX1=10(U0 路径 mult4×L0:2→8 + U2 路径 mult1×L0:2→2), NandX2=5(U0 路径 mult4×L1:1→4 + U2 路径 mult1×L1:1→1), total=26
- A 硬编码器(写死 brk3/brk2/brknetM1A=4)在 B 全错

**reference** `count_cell_usage.py`：spec 驱动通用实现（_expand_count 解 vector/array；count_usage DFS + multiplier + per-path path_ids；malformed→valid=False exit1）。

**check.py 15 conds**：独立 GT DFS 复算(_gt_count 单独代码路径)逐字段比对：
a zip 含 py ②b py_compile ③c A 运行 exit0+valid ④e A brknetM2A==7(vector<0:6>展开7+stop_lib计数) ⑤f A brk2==2(兄弟路径 per-path 环检测) ⑥g A brknetM1A==4(multiplier 传播) ⑦h A total==13 ⑧i A counts 键集合==GT(stop_lib 计数/非 target 不入) ⑨j A vector<0:6>严格7(防 off-by-one 成6) ⑩k B 运行 exit0+valid ⑪l B 各 target==GT(反硬编码) ⑫m B InvX1==10/BufX2==6(array)/DffLatch==5/total==26 ⑬n malformed→exit≠0/valid=False ⑭o 源码无 A 专属 token ⑮p B report 无 A 专属 token。

**LIVE-NA**(deliverable=Python 脚本, check 跑候选 subprocess+独立 GT DFS 复算断言, 无真实 EDA 工具二进制依赖; pyAether/Aether DB 不在 eval 沙盒不强求 L2.live; pyAether 运行时坑 instHeaders/getMaster reframe 为纯图判分) judge_layers=[L0,L1] 无 check_live。

## 自验全绿
- ref check.py on reference_submit.zip → PASS(15/15)
- negative_selftest 4 neg ALL-FAIL distinct first-fail{c,l,e}(trio empty→c/print_only→l/core_deleted→e) + hardcode_a→l(B 键集合不匹配)
- SKIP_RUN=1 eval/run_one.sh workdir leak 自检通过(无 check.py/reference/hidden 泄漏; attachments 仅 spec_A+task_brief 进 workdir)
- 3-way sha sync(disk==JSON test==metadata.check_sha256=f0403761def7459232baa9f229a8d05c37016da61e3d6234d45d74ab32953802 size 9228)
- k_check=15=k_rationale=15
- 框架 auto-build jsonl D 607 case 含本条
- 台账 mark: 1795687697314_2s98f → case(EDA-Eval-DesignFlow-CellUsageHierCountProduce-001)
- non-Lite roster 追加 CellUsageHierCountProduce-001 行(LIVE-NA, judge_layers=[L0,L1])
