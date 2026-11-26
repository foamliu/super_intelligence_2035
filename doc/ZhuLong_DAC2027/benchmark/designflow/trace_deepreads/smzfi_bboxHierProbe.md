# 深读笔记 · smzfi · bbox→电路层级 probe 分析

> session: `1793242667594_smzfi` · user: jialeshan · host: hfeg0plg52 (10.129.35.68) · mc=108
> keywords: schematic:504;aether:424;cellview:330;netlist:109;virtuoso:81;verilog:54;lvs:36;waveview:29
> 台账状态: **parked 2026-11-14 06:06** "SKILL source-locating Q&A env-dep"（本深读建议复活，见下）
> trace 来源: scp 10.129.32.190:/home/jialeshan/.cline/data/sessions/1793242667594_smzfi/1793242667594_smzfi.messages.json (830KB, 123 msgs, 66 user / 57 assistant)

## 用户真实意图（三段演进）

- **U1 (idx0)**：「virtuoso 中有个菜单 cxmt，下面有个目录叫 Circuit Explorer。这里面有很多接口，其中一个叫 Design Review Platform。你知道它到源代码是哪个」→ 纯源码定位（retrieval）。
- **U30 (idx50)**：「重点看这个函数里面哪里是用到 bbox 的坐标来 probe 电路层级的」→ **可压缩的 produce 子任务**（code-grounded analysis Q&A）。
- **U30 之后**：演进为 WeSign C++ ↔ SKILL/pyAether IPC 集成调试（`IMCinutHierPathCrossCB` 传 bbox 触发 zoom，遇 `unbound variable - box` / 窗口非设计窗口），agent 最终交付简化 Aether 直调代码（idx122）。

## 源码定位链（U1 答案，作上下文不进判分）

- 菜单定义：`/apps/imctf/cad/init/settings_cdns/skill/hi/IMChiUserPullDownMenuPostInstallTrigger.il:305` 注册 `?callback "CXMT_Tools_Monitor(\"Circuit Explorer\" \"Design Review Platform\") CXMTutDesignReviewTrigger()"`
- 触发器 `CXMTutDesignReviewTrigger` → 主源文件 **`/apps/imctf/cad/init/settings_cdns/skill/special/ut/IMCutDesignReview.il`**（2962 行，130KB，2009-2018 Bai Li 等）

## U30 子任务 ground truth（r858 造题用）

**fixture**：`IMCutDesignReview.il` 全文（2962 行）作为 asset A（真实文件，文本）。**不依赖 live /apps 环境** ⇒ 复活理由（11-14 parking 的 env-dep 仅针对 U1 retrieval，U30 analysis 把 .il 当文本文件分析，环境无关）。

**bbox→电路层级 probe 的真实代码位置**（grep `bBox|zoomBbox|IMCinutHierPathCrossCB|procedure(` 实测）：

1. **核心函数** `IMCinutHierPathCrossCB(hierPath @key (win hiGetCurrentWindow()) ...)` @ **line 1433**；let 引入 `zoomBbox` @ 1443。
2. **inst 分支**（oaType="inst"）：@ **lines 1130-1136**（_innoDesignHiliteHiliteCB 内）+ 重复 @ **lines 1617-1624**（IMCinutHierPathCrossCB 内）
   - `zoomBbox=instId->bBox`（首个 inst 初始化）
   - 否则 `zoomBbox=list(min(xCoord(lowerLeft(zoomBbox)) xCoord(lowerLeft(instId->bBox))):min(yCoord(...) ...  max(xCoord(upperRight(zoomBbox)) xCoord(upperRight(instId->bBox)))...)` —— **bbox 并集**累加多个 inst 的包围盒
3. **net/shape 分支**（oaType="net"）：@ **lines 1148-1153** + 重复 @ **lines 1656-1660**
   - `foreach(shape wid->cellView->shapes` 遍历 → `zoomBbox=shape->bBox` + 同样 min/max 并集
   - instTerm bbox：`cxmt_getInstTermBbox(wid netName)` @ **lines 1669/1674**
4. **box 分支**（oaType="box"）：@ **lines 1166-1168 区域**
   - `zoomBox = parseString(item ":")` → `list( car(zoomBox):nth(1 zoomBox) nth(2 zoomBox):nth(3 zoomBox) )` —— 解析 "llx:lly:urx:ury" 字符串成 bbox
5. **最终 zoom**：`when(zoomToHighlight && zoomBbox hiZoomIn(wid zoomBbox))` @ **line 1168**（_innoDesignHiliteHiliteCB）；IMCinutHierPathCrossCB 内对应 zoom 在 1670s。
6. **cross-probe 派发**：`IMCutDesignHiliteCB` @ **line 1345**，let 引入 `dbBox boxs_llx ... Bbox`；@ 1366 `dbBox = nth(3 review)` → @ 1369 `zBox = parseString(dbBox ":")`；@ 1413/1416/1419/1422 分别以 oaType "inst"/"net"/"box"/"text" 调 `IMCinutHierPathCrossCB`。
7. 几何辅助：line 610 `?bBox list(200:200 1500:1000)`（GUI form 默认 bbox）。

**probe 电路层级的关键语义**：bbox 并集（`min` lowerLeft / `max` upperRight）随 `foreach` 累加 → 最终 `hiZoomIn(wid zoomBbox)` 把窗口缩放到覆盖所有高亮 inst/shape 的联合包围盒 = 「用 bbox 坐标 probe/zoom 到电路层级」。

## r858 造题方案（D 域 code-grounded analysis Q&A 子型）

- **case_id 候选**：`EDA-Eval-DesignFlow-BboxHierProbeAnalysis-001`
- **档**：A 档 verbatim（U30 用户原话逐字作 prompt，仅掩码无）
- **task_brief.md**（≤3 行接口）：交付 `outputs/report.md`，分析给定 SKILL 源文件中「用到 bbox 坐标 probe 电路层级」的代码位置。
- **asset A**：`IMCutDesignReview.il`（真实全文 2962 行）
- **hidden B**：`IMCutDesignReview_B.il` —— 改造版：bbox 行号偏移（插入/删除若干注释行使其落在不同行号）+ 变量名部分重命名（`zoomBbox`→`zoomBBox2`，`instId->bBox` 保留语义）+ 一个 decoy bbox（line 610 GUI 默认，非 probe 用）。**不进 SUT 沙箱**，check() 只跑 B。
- **候选交付物**：`bbox_probe_finder.py`（读 .il → 用正则/AST 定位 `->bBox` 赋值 + min/max 并集 + `hiZoomIn` + `parseString(... ":")` → 输出 report.md，含函数名/行号/分支类型/语义说明）
- **check.py ≥8 断言**（对 B 独立验证，反硬编码）：
  1. report.md 存在且为 markdown，含「函数名 IMCinutHierPathCrossCB」
  2. report 列出 inst 分支 bbox 行号，与 check.py 独立 grep B 的 `=instId->bBox`（或重命名后）行号 ±2 容差匹配
  3. report 列出 net/shape 分支 bbox 行号，与独立 grep `=shape->bBox` 行号 ±2 匹配
  4. report 列出 box 分支 `parseString(... ":")` 行号，与独立 grep 匹配
  5. report 指出最终 zoom `hiZoomIn(wid ...)` 行号，与独立 grep 匹配
  6. report 说明 bbox 并集语义（min lowerLeft / max upperRight 累加）—— 关键词检测 `min`/`max`/`lowerLeft`/`upperRight` 至少 3 个
  7. report 区分 inst/net/box 三分支（三个分支类型字串都出现）
  8. report 行号集合与 check.py 独立计算集合的 Jaccard ≥0.7（防漏报/乱报）
  9. （退化闸）空壳 / 只 print 期望串 / 候选删核心逻辑 三假提交全 FAIL
  - 真跑候选脚本 subprocess 在 B 上执行，断言输出结构而非文本相似
- **负样本**：`negative/` 含 (a) 空报告 (b) hardcoded-A 行号 stub（行号写死成 A 的 1130/1148，对 B 必错）(c) always-「line 100」stub；`negative_selftest.py` 全 FAIL。
- **trace_source**：{user: jialeshan, host: hfeg0plg52, session_file: 1793242667594_smzfi, match_count: 108, real_task_summary: "定位 Virtuoso cxmt→Circuit Explorer→Design Review Platform 菜单源码 (IMCutDesignReview.il)，并分析其中用 bbox 坐标 probe 电路层级的代码位置"}

## 复活动作（r858 第一步）

台账 parked 需复活。优先用 ledger 重 claim（若 REFUSED 则手动 mark 改 status=seeded + note "r858 revival: U30 analysis env-independent, .il as text asset"）：
```
python3 designflow/trace_ledger.py --shard D claim --session 1793242667594_smzfi --user jialeshan --host hfeg0plg52 --match 108 --domain schematic_netlist
# 若 REFUSED，查 ledger 是否有 unpark/revive 子命令；无则手动 sed trace_ledger_D.tsv 改 parked→seeded（仅本 shard 文件，合规）
```
出完 case：`mark --session 1793242667594_smzfi --status case --case-id EDA-Eval-DesignFlow-BboxHierProbeAnalysis-001`

## 风险

- .il 2962 行较大但纯文本，作 asset 可接受；hidden B 改造需保证 bbox 语义不变、行号变。
- A 档 verbatim prompt 是中文口语「重点看这个函数里面哪里是用到bbox的坐标来probe电路层级的」——需在 task_brief 指明「函数 = IMCinutHierPathCrossCB / _innoDesignHiliteHiliteCB，文件 = 附件 IMCutDesignReview.il」≤3 行，不写答案。
- 判分用 grep 独立计算 B 的 bbox 行号作 ground truth —— 牙齿来自行号容差 + Jaccard，反硬编码 A 行号。
