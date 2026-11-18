# trace_deepread: 1789961307805_2uipn — PyAetherMoveInstHowto-001

- **session**: `1789961307805_2uipn.messages.json`
- **user / host**: ziyuny @ hfeg0plg104 (10.129.8.236)
- **match_count**: 83 (pyaether:169;dbget:143;aether:58;cellview:53;dbopencv:31;rtl:22;netlist:22;lvs:14)
- **NMSG**: 87, file 319120B, mtime Sep 21 13:19 (alive, retrieved via scp r746)
- **domain**: layout_aether (pyAether API heavy, aether:58)
- **ledger**: parked r599 (2026-11-15) as "r599 peek REJECT: ziyuny 'give me a reference' Q&A for auto-placement move inst, borderline Q&A"; under 11-15 §二 revival howto-Q&A is legitimate → revived r746

## 用户真实意图（U#0 原话）

`<user_input mode="act">如果我现在在aether有一个版图，已经根据SDL生成了layout，有初步的placement。如果需要写脚本，通过aether的接口来做自动placement，能给我一个参考吗？move inst的功能</user_input>`

真实交付意图 = 给一个 pyAether 自动 placement / move inst 的参考脚本。用户在已有 SDL 生成 layout 的前提下，希望用脚本通过 Aether 接口批量调整 instance 位置。这是 howto-Q&A：用户问"怎么做"，需要回答用什么 API。

## 助手行为（msg#1 - msg#30+）

1. RAG 多角度检索 pyAether API：
   - "move instance to a new position in layout"
   - "get instance location and bounding box from cellview"
   - "query all instances in a layout cell"
   - "set instance origin transform dbSetInst"
   - "instance iterator get instances dbGetInstList"
   - "set transform move instance to coordinate dbSetInstTransform"
   - "inst move or origin placement emyInst"
   - "move figure or shape by delta offset dbMoveFig"
2. 调 RAG_MCP_Server__get_api_details 查 leGuiMove / aeGetCellView / aeGetCurDesign / dbGetInstTransform / dbFindInst / emyGetAllInstHeaders / dbInstanceQuery / emyBaseNameFindInsts / aeMoveObj / leGuiAdvInstancePlacement / dbGetInstTransformF / dbTransformPoint / dbMoveFig / dbCrtInst / dbCopyFig / getBBox / dbSaveCV
3. 核心发现：**dbMoveFig(fig, offsetPoint, dst, orient, mag)** — 官方示例本身就是"dbFindInst 找到 inst → dbMoveFig 移动"——这就是用户要的 move inst 功能
4. 配套接口：dbGetInstTransformF 读当前位置/朝向、getBBox 读外形、dbInstanceQuery 遍历所有 inst、dbSaveCV 保存
5. msg#24/26/28 通过 editor 写入 /home/ziyuny/auto_placement.py 参考脚本（pyAether 自动 Placement 参考脚本，调用 emyInitAether → aeGetCurDesign → aeGetCellView → dbInstanceQuery 遍历 → dbFindInst 按名找 → dbGetInstTransformF 读现位 → getBBox 读大小 → dbMoveFig 移动 → dbSaveCV 保存）
6. msg#30/32 写 check_syntax.py 做 py_compile 语法校验

## Reframe（11-15 §二 revival）

- **mode**: mock-behavioral `pyaether-move-inst-howto-Q&A`（r744 AeGetSelSetInfoHowto 同族 pyAether API howto）
- **mode ③evidence-only** (P-006 r618 (C)-(A) 分流，同 r744)：howto-Q&A on 固定 docs（无 process 可在 B 上重跑）⇒ SUT 仅产 report.json；B/B2 作 judge-self-check
- **牙齿来自**：①content-correctness（≥18 断言） + ②evidence-verification + B/B2 cross-input + anti-stub + robustness/determinism
- **A** = sample_input/docs/*.txt（pyAether ref-manual fragments + cheatsheet，含 move-inst 核心 API：dbMoveFig + dbFindInst + dbGetInstTransformF + getBBox + dbInstanceQuery + dbSaveCV + aeGetCurDesign + aeGetCellView + Universal Method: dir）
- **B** = hidden/b/docs/*.txt（不同 chapter/api 名变体：dbMoveFigure/dbFindInstance/dbGetInstTransform/figGetBBox/dbInstQuery/dbSaveCellView/aeGetCurrentDesign/aeGetCellViewByName/members）
- **B2** = hidden/b2/docs/*.txt（更不同变体：aeMoveObj/aeFindInst/emyGetInstTransform/emyFigBBox/emyInstList/emySaveCV/aeGetActiveDesign/aeOpenCellView/listAttr）
- **每条 fact** 配 evidence (doc filename + exact source line)，B/B2 cross-input guard 防 hardcode

## 与 r744 AeGetSelSetInfoHowto 的 distinctness

r744 取 aeGetSelSet 选中对象信息查看 howto；本例取 move inst / 自动 placement howto，不同 API 族（move/find/transform/bbox/iterate/save/design/cellview），不同 trace source（ziyuny vs jianingw），不同真实意图。同 mode ③evidence-only 同 mock-behavioral 同 layout_aether howto-Q&A 子型，但 case 内容完全独立。
