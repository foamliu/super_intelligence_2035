# deepread: 1792562522433_6kbdj (colinxu / hfeg0plg55) — SchematicPinAdd

- session: 1792562522433_6kbdj.messages.json
- user: colinxu · host: hfeg0plg55 · mc: 270 · domain: layout_aether
- size: 436905 B · nmsgs: 157 · user turns: 41 (most "请继续"/lock-debug)
- keywords: schematic:473; aether:396; pyaether:239; drc:174; analog:173; cellview:142; dbopencv:134; dbget:123

## 真实任务 (real_task_summary)

USER#1 (verbatim, 单条 clean produce-demand):
> 帮我在 drcqa_analog lib - AG_AmpsUpBankFar cell - schematic view 内添加一个 TESTPIN 这个 pin

两阶段 session:
1. **produce-task** (msgs 1-72): agent 搜 API (dbCreateSchPinEx / aeCreatePin) → 写 `add_schematic_pin.py` (参数化函数) → SandBox_MCP_Server__run_code 跑 → TESTPIN 创建成功 (termCount 30→31, dbFindTermByName 确认)。
2. **issue-handling** (msgs 73-157): USER#73 "我没有找到TESTPIN，并且为什么这个schematic被锁住了" → agent 诊断: 真实库 `/proj/train/V0_NCG_HF_Aether/libs/drcqa_analog/AG_AmpsUpBankFar/schematic/sch.oa` 下有 stale OpenAccess 编辑锁 `sch.oa.cdslck` + `sch.oa.cdslck.RHEL30.hfeg0plg81.18505` (PID 18505 已死) → 删锁 → 重跑创建 → grep -a sch.oa 确认 TESTPIN 落盘 → 但每次 run_code 触碰库都重新放锁 (live 持锁进程 hfeg0plg81:18505) → 探查远程主机 hunt 持锁进程。

## agent 产物 (gold)

`/home/colinxu/agentdir/train/V0_NCG_HF_Aether/add_schematic_pin.py` — 参数化函数 `add_schematic_pin(lib_name, cell_name, view_name, pin_name, direction='input', master_lib='basic', master_cell='in', point=(1.0,1.0), save=True)`:
- `dbOpenCVByType(lib, cell, view, 'schematic', 'a')` 打开 cellview (append)
- 幂等 guard: `dbFindTermByName(cv, pin_name)` 已存在则 skip 返回
- `dbOpenCVByType(master_lib, master_cell, 'symbol', 'symbol', 'r')` 打开 pin master symbol (basic/in)
- `emyPointF(point[0], point[1])` 构造点
- `dbCreateSchPinEx(cv, master, pin_name, direction, pt)` 创建 pin
- 反向验证: `cv.termCount == before + 1` + `dbFindTermByName` 确认
- 持久化: `dbCheckAndSaveDesign(cv=cv)` + 重开只读 `dbOpenCVByType(...,'r')` + `dbFindTermByName` 确认落盘
- 返回 pin 对象

API 调用链 (pyAether): dbOpenCVByType / dbFindTermByName / emyPointF / dbCreateSchPinEx / dbCheckAndSaveDesign / termCount 属性。

## tool chain

SandBox_MCP_Server__run_code: 23 (pyAether 执行) · run_approved_command: 20 · editor: 13 · RAG_MCP_Server__search_apis: 9 · RAG_MCP_Server__get_api_details: 5 · read_files: 3 · ask_question: 2

## B 档合成原因

真实 cellview `drcqa_analog/AG_AmpsUpBankFar/schematic` 是 .75 上真实 OA 库 (sch.oa 二进制, 含产品 pin 名), 无法附入 SUT 沙盒; 且 pyAether 需 live Aether bridge, SUT 沙盒无 bridge。故:
- 合成 visible A = 真实 trace 目标 (drcqa_analog/AG_AmpsUpBankFar, pin TESTPIN, input) — 名字非敏感 (通用 analog lib/cell)
- 合成 hidden B = 不同 cellview (analog_lib/SA_TopCell, pin VREFCAL, output) — cross-input guard
- check 用 mock-pyAether (sys.modules 注入 / PYTHONPATH shim) 记录 API 调用链, 无需 live Aether — 行为级断言 (subprocess 真跑候选)

## 选料筛选损耗 (r397 本 session)

rows 121-400 fresh 池 (mc 248-447) 14 候选 peek:
- 3h21t (e0047527, aether+pyaether mc447) → eda-bridge 连接调试, park
- 53e2m (victorq, aether+pyaether mc315) → SPICE 波形电路诊断, wrong-shard D, park
- r0a7b (t0002638, aether+pyaether mc277) → pyAether print-Hello 连接调试, park
- 8c5jw (t0002638, aether+pyaether mc290) → 截图 API 探测, park
- i6kg9 (t0002607, aether mc288) → 电路查看/截图/仿真 探测, park
- 30a1n (jcgu, aether+pyaether+drc mc265) → group-gen-sdl bridge-wrapper (匹配逻辑在 Aether 内 aeCstRealizeAllFromDesign 非脚本), near-dup NetlistExtractSkill-001 r392, jcgu 6 cases 过密, skill-injection origin, park
- ejp6w (yuchens, aether+cellview+dbget mc347) → 网表 vs CDL 差异对比, wrong-shard D, park
- sy1se (xxchen, drc+.gds+calibre mc318) → drcConnect connectivity 工具, near-dup DrcConnScriptAudit-001 r393, park
- g6wy0 (cliu, drc+lvs mc313) → stdcell TB 仿真验证, wrong-shard D, park
- y91i6 (ericw, drc+verilog mc353) → DRCPA verilog coverage, wrong-shard A, park
- wag72 (e0047600, .gds+lvs mc342) → SP SRAM GDS tiling 但 user turns 全 Q&A/教程更新, 非干净 produce-demand, park
- z9zx7 (cliu, drc+lvs mc267) → stdcell AC 仿真验证, wrong-shard D, park
- sr1fw (miccao, drc+calibre+gds+lvs mc346) → Calibre DRC-H log 拆解 4-模块, near-dup DRCLogTeardown-001 r383, park
- 6kbdj (colinxu, aether+pyaether+cellview+dbget+dbopencv mc270) → 真 fresh clean produce-demand → 交付 r397

C 域「筛选成本枯竭」模式再现 (cf. r393 discuss): rows 121-400 fresh=97 但有效候选被 env-debug/capability-probing/skill-loading/near-dup/wrong-shard 稀释。layout_aether fresh 候选 90%+ 是 bridge-连接调试/截图探测/Hello-验证; physical_verify fresh 候选多 near-dup (sr1fw=r383, sy1se=r393) 或 wrong-shard (cliu/ericw)。无 clean layout_virtuoso/pg_layout fresh 候选。
