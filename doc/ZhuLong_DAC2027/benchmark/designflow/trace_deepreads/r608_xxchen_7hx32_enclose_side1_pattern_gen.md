# r608 deepread: 7hx32 — xxchen enclose_side1 + waiveMark produce-task

**Session**: 1794626078120_7hx32
**User**: xxchen (hfeg0plg19 / 172.16.8.164, also on hfeg0plg105 / 10.129.8.237)
**mc**: 370 (drc:1135; .gds:199; analog:10; pdk:7; gdsii:2; dbcreatepath:2; dbcreatelabel:2; rtl:1)
**Domain**: physical_verify (DRC pattern tool development)
**Trace**: 265 msgs / 3 user_input
**Agent**: deepseek-v4-flash, editor(60) + run_approved_command(40) + read_files(25)

## User intents (原话)

### UI#0 (setup): "阅读AGENTS.md\n阅读PROJECT.md"
Agent reads DRC_pattern_tool project docs (AGENTS.md: PDK expert role, workflow rules; PROJECT.md: QACILL config format, function catalogue, manual refs).

### UI#1 (produce-task #1): 新增功能 waiveMark
> config中配置了 waive相关信息，使用的layer层次，以及是否产生。
> TOOL     TECH     waiveLayer     321;51
> TOOL     TECH     waiveFlag      True
> QACILL  PW_ENC_005_00_p     enclose          PWx->NMOS_thin         0.650     {layer2_device ACTIVE} {w 1.0} {l 0.5} {waive bad 5}
> 新增一个 参数 wavie bad 5
> 含义为： 给bad pattern 5 增加 waiveMark
> 要求：这个waiveMark应该要做成一个通用的功能，有点类似 auxRegion，但是只针对指定pattern。
> 要求每个function都可以支持waiveMark这个功能，代码尽量精简，逻辑清晰，便于统一维护。

### UI#2 (produce-task #2 — 本 case 选用): enclose_side1 约束
> ### QA pattern debug: PW_ENC_006_00_c
> QACILL  PW_ENC_006_00_c     enclose_side2    PWx->NMOS_thin         0.560     {layer2_device ACTIVE} {w 1.0} {l 0.5} {auxRegion CORE} {enclose_side1 0.234}
> 分析如下：
> bad pattern 4 的形状特征相比较 
> QACILL  PW_ENC_006_00_p     enclose_side2    PWx->NMOS_thin         0.820     {layer2_device ACTIVE} {w 1.0} {l 0.5} {enclose_side1 0.650}
> 发生了明显的变化，layer2_device 直接超出了 layer1外面。
> 所以我发现这个function对应的参数需要新增加一个参数 enclose_side1
> 所有的good 和 bad pattern 都至少要满足enclose_side1 ， 贴边的和超出去的case就都需要被排除掉。
> U型的case，需要把U型concave edge的 enclose 值也改成 满足 enclose_side1

## Agent actions (UI#2)
1. read_files: enclose_side2.py (current function code), good_pattern/2, bad_pattern/4 (existing patterns)
2. 分析根因: enclose_side2 函数未消费 QACILL 里已配的 {enclose_side1 0.234}，导致 bad pattern 把 AA top/right 削成负包覆（AA 超 PW）或太薄（贴边 min 0.1599 < 0.65）
3. editor: 修改 enclose_side2.py — context 读取 enclose_side1，钳到 [0, value-checkStep] 并 snap 网格；缺省 0 时告警
4. editor: 修改 good_pattern/2 — 薄边 0.08 → enclose_side1（L/R=value, B/T=encl1; 相邻边对均有一边 value → 仍 GOOD）
5. editor: 修改 bad_pattern/4 — 原 L 形（AA 右上暴露）→ "C" 六边形: L/B=value, R/T=encl1, 凹台阶放 x=ax0（保证 value>AA 半宽时 AA top 仍全在 thin 区），凹口不触 AA → 相邻 top+right 仍 BAD
6. run_approved_command: 跑 verify 脚本验证 pattern 完整性
7. 更新 lessons.md + manual

## 最终交付
Agent: "所有修改完成并验证通过" — enclose_side2.py 新增 enclose_side1 消费 + good/bad pattern 几何调整 + U型 concave edge 约束 + 文档同步。

## B档 mock-behavioral reframe
源代码在 xxchen 私有 workdir /home/xxchen/workspace/DRC_pattern_tool（沙盒不可达）→ asset_fidelity=synth。
把「为 enclose_side2 函数新增 enclose_side1 约束并生成满足约束的 good/bad pattern」参数化为纯 Python3 `enclose_side1_pattern_gen.py <config.json> <out_report.json>` (stdlib only)。
- 解析 QACILL 配置行: cell/function/layer1->layer2/value/layer2_device/w/l/auxRegion/enclose_side1
- 生成 good 矩形图案: right margin ≥ value (side2), left/top/bottom margin ≥ enclose_side1 (side1)
- 生成 bad 矩形图案: right margin < value (违反 side2), left/top/bottom margin ≥ enclose_side1 (满足 side1)
- 生成 bad U型图案: 臂 right margin < value (违反 side2), 凹槽 right margin ≥ enclose_side1 (满足 side1)
- 所有坐标 snap 到 grid, 确定性 JSON (sort_keys=True)

输入A(PW_ENC_006_00, value=0.560, encl1=0.234, 3good+2bad_rect+2bad_ushape, grid=0.001);
隐藏B(AN_ENC_003_01, value=0.420, encl1=0.180, 4good+3bad_rect+2bad_ushape, grid=0.005);
隐藏B2(ISO_ENC_007_04, value=0.300, encl1=0.150, 2good+2bad_rect+3bad_ushape, grid=0.002) 反硬编。

## 旧判 parked 原因 → 新判
r577 peek REJECT: "known-reject xxchen r577 top500-fresh drc-dominant"
新判 (2026-11-15 令): modify-existing 是真实用户意图，xxchen 是已知 produce-task 用户 (r545/r587/r594/r606)，enclose_side1 约束是 PDK QA 工具开发的合法任务 → **可造** (B类误杀复活)。
