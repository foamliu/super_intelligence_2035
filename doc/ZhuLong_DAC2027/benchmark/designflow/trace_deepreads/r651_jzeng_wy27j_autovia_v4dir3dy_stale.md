# r651 deepread — wy27j (jzeng @ hfeg0plg85) — AutoViaV4Dir3DY 已落库 + 0-gold

> **结论**：stale reaudit 条目 + 0-gold，不造。本 deepread 仅作 r651 选料失败证据 + r568 case gold 复核线索。

## trace 元数据
- session: `1794643455102_wy27j` (jzeng @ hfeg0plg85, .75 本机 10.129.32.75)
- file: `/home/jzeng/.cline/data/sessions/1794643455102_wy27j/1794643455102_wy27j.messages.json` (1,236,868 bytes / 130 msgs / 3 user-text turns)
- scan keywords: drc:394;pyaether:109;.gds:82;dbget:47;dbopencv:32;calibre:21;netlist:10;cellview:9
- match_count: 77 (mc≥10 ✓)
- domain: layout_aether (pyAether via 生成脚本)

## 用户意图（3 real user turn）
- **U#1**: `/home/jzeng/Desktop/IMCleAutoVia.py优化该脚本，使其在横向0.55um宽度的M4和纵向0.55um宽度的M5之间可以打出V4孔，V4方向为R90，Parameter如下，Enclosure choice of bottom layer: dir_3D_Y; Enclosure choice of top layer: NONE;在生存孔的位置需要自动补上部分M4来满足V4 Parameter的要求` — 提出需求型，A 档合规（未给根因/方案，仅给规格）
- **U#2**: `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 78200... 解决这个问题` — 副问题（脚本加载 ASCII 解码失败）
- **U#3**: `测试之后没有办法生成V4，平台是G5` — **测试失败反馈**，其后 0 assistant 回复

## assistant 工具链
1. read_files IMCleAutoVia.py 多段（~1895 行，分段读 1-200/200-400/.../1755-1895）
2. RAG_MCP_Server__search_apis + get_api_details（aeCreateRect / dbCrtRect / emyGetViaDefByLayer / emyGetCustomCutLayer / emyTechFindViaDefs / techFindLayer / dbCrtVia / dbGetTrueOverlaps / dbCopyFig 等）
3. editor 修改 IMCleAutoVia.py：
   - 新增函数 `IMCleAddM4FillForV4Dir3DY(cv, refBBox, orient, botEncY)` — 在 via cut 位置补 M4 fill 满足 bottom enclosure dir_3D_Y 要求
   - 修改 `IMCleGetRectProp` 函数（~L1246-1268）：V4 + dir_3D_Y + R90 时调用上述 fill 函数
   - 修改 `gen_via_from_y` 函数（~L1773）：同上对称处理
4. run_approved_command python-runner：检测非 ASCII 字节 → 找到 L1412 em-dash `—` (U+2014, 0xe2 0x80 0x94) → editor 改为 `--` → 复扫 0 非 ASCII
5. trace 末尾：assistant 总结 UnicodeDecodeError 根因 + 修复说明 → U#3「测试之后没有办法生成V4」 → **0 assistant 回复，session 结束**

## gold 状态（关键）
- assistant 完成了脚本编辑（3 函数修改 + 非 ASCII 修复）
- 但 **U#3 = 用户测试失败反馈，其后无 assistant 回复** ⇒ trace 末尾用户未接受结果
- ⇒ **gold 未达成**，不能作 A 档金标准

## 与 r568 关系（关键）
- ledger_C.tsv: `1794643455102_wy27j ... case ... 2026-11-14 20:36 r568 modify-existing pyAether IMCleAutoVia.py add V4 via capability M4/M5 R90`
- jsonl_C: `{"task_id": "AutoViaV4Dir3DY-001", "mode": "design_flow", "entry_point": "outputs/submit.zip", "prompt": "我是版图工程师，用 pyAether 写自动打孔脚本。现在需要给 IMCleAutoVia.py 加一个 V4 孔功能..."}` — 已落库
- ⇒ **本 session 已于 r568 造过 case**，pool_reaudit_C.tsv r622 行漏对 ledger case 行去重，stale 标「可造」
- r568 当时以 assistant 脚本编辑作 gold 入库，**未核 trace 末尾用户接受状态**（U#3 测试失败）

## r651 处置
1. pool_reaudit_C.tsv wy27j 行改为「不可造 · stale + 0-gold」
2. ledger 已有 case 行，无需重复 park
3. **DEBT:1**：r568 AutoViaV4Dir3DY-001 gold 严谨性待复核（ETA r652）——重跑 reference check.py，若 ref PASS 则 case 合规仅 trace 未闭环；若 ref FAIL 则需 retire 或 v2

## 教训
- r646 已教「选料前 grep ledger 排除已 case」，r651 再踩（浪费 ~20min deepread 已交付 case）
- 选料前 grep ledger **强制化**写进下轮 SOP
- revival 候选 deepread 第一件事 = 看 trace 末尾 5-10 条 user/assistant 消息确认用户接受状态（倒序省 80% 时间）
