# Deepread: xpue4 — group-gen-sdl skill「打开 DM + cell 视图」补充

- session: `1793328605482_xpue4.messages.json`
- user: jcgu @ hfeg0pin003 (10.129.32.236), mc=165
- keywords dominant: aether:570 / schematic:297 / drc:216 / pyaether:112 / analog:72 / dbopencv:63 / netlist:26 / cellview:19
- size: 671561 bytes / 205 msgs (106 user / 99 assistant)
- 真实 user_input（5 条，`<user_input mode="act">` 标签内）：
  - msg11「要做这两点」（承接 msg0 半自动绑定恢复固化 + 临时文件清理）
  - msg39「测试一下这个skill:在train/AI_drcqa项目中，ztest/AG_GRefAmpVpcsgRef_IPD ztest/AG_TSCompCore_IPD这两个cell生成group」
  - msg103「两个都做」
  - **msg121（A-faithful seed）**「关于这个skill，补充一点：group生成完，将aether DM和生存的cell的layout/schematic view都打开，方便用户查看」
  - msg184「为什么我在新对话里运行这个skill，总是会卡死，是不是进入到死循环还是其他什么原因，请分析一下」（debug-Q&A，分析 pythone 阻塞 + DISPLAY + 锁，非交付型）

## msg121 上下文与 GOLD（msg137/147/153/183）

用户在 group-gen-sdl skill 已可用后，补充「生成完后打开 DM + cell 的 layout/schematic 视图，方便查看」。skill 主体 `group_gen_sdl.py` 由 `run_group_gen.sh` 逐 cell 独立 pythone 会话调用，每 cell 结尾 `aeCloseAllWindows()`（避免下个 cell 在共享 GUI 里被 isInSDL=False 污染）→ 故「打开视图」不能在逐 cell 会话里做，必须在全部 cell 处理完后用**独立 pythone 步骤**打开。

agent 交付 `scripts/open_dm_and_views.py`：
- `emyInitAether('-adv')` + `emyAppExt.s_bQueryBatch=True` / `s_isFormHide=True` 压制弹窗
- `aeDMShow(True)` 打开 Design Manager（`aeGetDmWindow().show()+raise_()` 兜底）
- 逐 cell：`aeOpenDesign(lib, cell, 'schematic')` + `aeOpenDesign(lib, cell, 'layout')`
- layout：用 `aeGetWndList('design')` + `haswin()` 检测；未建出窗口则 `dbOpenCV(layout,'a')` + `aeCreateWindow(cv)` + `aeDisplayWindow(wid)` fallback
- 收尾**保持窗口不关闭**（不调 `aeClose*`）

CString bug（msg147 修）：`windowTitle()` 返回 `CString`（非 Python str），`cell in t` 抛 `TypeError: argument of type 'CString' is not iterable` → 改 `str(t)` 后再 `in` 判断。

端到端验证（msg183）：
```
[dm] DM 已显示(aeDMShow)
[GRef schematic] ✓  [GRef layout] ✓(fallback da=2)
[TSCompCore schematic] ✓ [TSCompCore layout] ✓(fallback da=5)
[done] 视图/DM 保持打开, 供查看
```

## 选为 A-faithful seed 理由

msg121 是「提出需求 / 表达目标」的用户轮（用户**没有**给出根因或修复方案，符合 A 档选轮规则）；交付物清晰可判定（一个独立脚本，调用 pyAether API 打开 DM + 视图）；判分有牙（mock pyAether 在隐藏 B 上验证 API 调用序列 + 反硬编码 + CString 处理 + 窗口保持打开）。

msg11/39/103 是承接式短轮或测试请求，不适合单独造 case；msg184 是 debug-Q&A（分析型，无独立交付物）。

## 合成

- case_id: `EDA-Eval-DesignFlow-OpenDmViewsProduce-001`
- domain: analog_context（Aether 模拟 layout/schematic 视图操作）
- grade: A（U#121 verbatim seed）
- track: A-faithful
- asset_fidelity: synthesized-reframe produce-from-scratch
- 资产 A: `task_brief.md`（verbatim U#121 + 交付接口）+ `context_A.md`（真实 skill 上下文 + pyAether API + CString/fallback 陷阱）
- 隐藏 B: 3 seed (B1=analog_lib 3 cells / B2=pll_aux 2 cells / B3=rf_rx 4 cells，与 A 的 ztest/AG_* 完全不相交，cell 数 2/3/4 变化) + `mock_pyAether.py`（记录 aeDMShow/aeOpenDesign/dbOpenCV/aeCreateWindow/aeDisplayWindow/aeGetWndList 调用；windowTitle() 返回 _CString 触发 str-coerce 陷阱；aeClose* 可记录以验证「保持打开」）+ `hidden_manifest.json`
- check.py 12 断言 a-l（k_check=k_rationale=12 ≥ 8）
- reference_solution: `open_dm_and_views.py`（基于 trace GOLD msg137+msg147 修复版重构，加 report.json 输出）
- 3 negatives: empty_shell（CLI 守卫 FAIL）/ print_expected（aeDMShow 未记录 FAIL）/ delcore（aeOpenDesign loop 删除 FAIL）

## 与既有 case 关系

- D 域 analog_context skill-augmentation produce-from-scratch 首例（既有 SchPinAddProduce-001 是 schematic_netlist 域 add-pin produce，HierSigFixProduce-001 是 netlist script-fix produce，Ddr5WriteTaskParamExplainQA-001 是 verilog-source-as-fixture parser produce）
- path-bug revival 第 6 例 case（承 r970 PolicyNdjsonDestrScan / r971 SchPinAddProduce / r972 DBCOA ZqCal / r973 HierSigFix / r974 Ddr5WriteTask，连续 6 case streak）
- 首例「mock pyAether + CLI 脚本 subprocess-style 调用」判分范式（既有 mock 是函数级 import 调用，本 case 是 main() + sys.argv patch）
