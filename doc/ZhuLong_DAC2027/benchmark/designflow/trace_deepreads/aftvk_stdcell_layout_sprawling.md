# aftvk 深读 · jieran@hfeg0plg70 · 1793963596117_aftvk (mc=1034)

## 元数据
- session: 1793963596117_aftvk (3.35MB messages.json, 741 msgs / 379 user / 362 assistant)
- user: jieran @ hfeg0plg70
- ledger 旧记录: parked 2026-11-06 21:20 "netlist file path (jieran)" (空 user/host/mc，早期入库)
- summary.tsv mc=1034, kw: pyaether:1135;dbopencv:567;aether:526;lvs:510;.lef:488;drc:450;schematic:353;cellview:340

## 任务形态（真实用户意图）
 sprawling 多任务 stdcell layout 绘制教学/迭代。用户 U#0 给 netlist → U#1「根据这个netlist帮我绘制版图，命名layout_tet」→ U#3 学习 DRC rule + ac 库 + 输出学习笔记 + 优化 layout_test → U#5 5 条 stdcell 绘制规则（MT2/MOU/PG drawing、Pin 在 MOU、power Pin 左上角 0.02x0.02、merge 管子、DRC/LVS clean）→ U#11 完整 stdcell 绘制流程 5 步（spacer→XL 调管子→对齐→连接→打 Pin）→ U#16 画 nand2LVSx6 → U#17 修正（nf 数量/管子高度/spacer 宽度/DRC-LVS clean）→ U#19 画 nand2IOLVIOx1 → U#20 对比两个版图差距 → U#22 学 bindkey → U#25-27 用 i 调管子而非 XL → U#29 重绘 nand2IOLVIOx1 → U#32-40 多轮「放好管子后绘制 standcell」迭代 → U#40（末轮）「重新绘制，严格根据stancellor的绘制规则，高质量绘制」。

## 助手行为
- 238 SandBox_MCP_Server__run_code (pyAether) + 33 editor + 23 read_files + 20 RAG search_apis + 8 get_api_details + 5 run_approved_command
- **0 write_file 调用** —— 所有修改通过 SandBox run_code / editor 直接操作 .oa 文件
- 真实产物落 .oa layout view 在 /proj/dscqa/V0/libs/dscqa_work/*（生产服务器，非沙盒可达）

## 判定：REJECT（结构性非可移植，非 weak-reason 复活候选）
1. **GUI 交互式 layout 绘制**：238 pyAether run_code 调用，逐 msg 修改 .oa；非脚本化 produce-task，无可离线 reframe 的 gold 脚本
2. **gold = .oa layout 在生产服务器** (/proj/dscqa/...)：SUT 沙盒不可达该路径，且 .oa 二进制不可 ship
3. **末轮仍在迭代**「重新绘制，严格根据stancellor的绘制规则」—— 无 clean trace-end-gold（§A rule 4 fail）
4. **多任务交织**：layout_test + nand2LVSx6 + nand2IOLVIOx1 + 学习笔记 + bindkey 学习 + skill 调用，无单一 clean produce-task 可抽取
5. **2026-11-15 复活令不适用**：旧 parked 理由「netlist file path」虽简陋，但真实阻因是 GUI 依赖 + .oa 非可移植（同 r786 8ur5y REJECT pattern），非 analysis-Q&A/doc-search/setup 类 weak-reason

## 处置
- ledger 旧记录已 parked 维持；本轮 r790 在 MEMORY_C 标注「深读复核维持 REJECT」
- 不进 case 队列；不消耗为新 case
- 池确证：top-13 C-pure fresh（mc≥542）全在 ledger，aftvk 复核维持 REJECT ⇒ 高 mc fresh 池确证趋薄（与 r786 一致）
