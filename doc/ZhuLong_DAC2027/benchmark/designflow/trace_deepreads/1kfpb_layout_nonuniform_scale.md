# trace deepread — 1kfpb (wenjiel @ hfeg0plg77, mc=384) — Virtuoso layout 非均匀缩放 SKILL

- session: `1795571289156_1kfpb.messages.json` (490 msgs, 257 user / 233 assistant), user=wenjiel, host=hfeg0plg77, fetchable via ssh from .75 (PATH-FIX 子目录路径不需要，flat file)
- domain: layout_virtuoso (C-shard)
- match_count: 384 (cellview:1860, dbget:420, dbcreatepolygon:378, dbcreaterect:284, virtuoso:257, dbcreatelabel:163, dbcreatepath:116, schematic:23)

## 真实用户意图（原话）
> 生成一个 skill 脚本，应用于 virtuoso layout，将 layout X 方向放大到原来的 1.1 倍，Y 方向缩小到原来的 0.9 倍

## 真实 SKILL `leNonUniformScale.il`（assistant 产出，3 步算法）
1. **flatten**：`geGetEditCellView()` → `leFlattenInst(inst 32 t t nil t t)` 打平所有 instance（最多 32 级 hierarchy），连接性丢失。
2. **convert**：`dbGetPathBoundary`(path→polygon) / `dbConvertDonutToPolygon` / `dbConvertEllipseToPolygon`。pathSeg 保留。
3. **scale**（about origin (0,0)）：
   - rect: `bBox` 两角 ×(xScale,yScale)
   - polygon: 每个 vertex ×(xScale,yScale)
   - pathSeg: 端点 ×(xScale,yScale)，width ×min(xScale,yScale)
   - label: origin ×(xScale,yScale)，height ×yScale（只按 Y，保可读性）；text/just/orient/font 保留
   - 默认 `xScale=1.1`、`yScale=0.9`
   - `dbSetUndoHandle(cv "leNonUniformScale")` undo checkpoint
   - figGroup / marker 不处理

## case 设计（faithful Python 抽象，L0/L1 LIVE-NA）
真实 Virtuoso cellView 无法 ship（需活会话+techfile+许可）⇒ 抽成纯 Python `layout_scaler.py` 引擎，输入/输出 JSON layout，算法/缩放语义/默认值/convert 规则/flatten 规则全与真实 SKILL 一致。
- 代表性简化：instance 只带 origin 偏移（无旋转/mag）；donut→polygon 取 outerRad 8 顶点（内孔丢失，与 dbConvertDonutToPolygon 一致）；ellipse→polygon 8 顶点。
- L0/L1 静态可判 LIVE-NA（Q2 不被骗：stub 硬编码 B 输出在 A cross-input 反结论下必挂；独立复算逐 shape 比对，shape 形状对但坐标错必挂）。

## 交付 EDA-Eval-DesignFlow-LayoutNonUniformScale-001
- `layout_scaler.py` (参考解) + `check.py` (11 断言 sha256=e0785f1f, 14410B, 独立重新实现 flatten/convert/scale 复算逐 shape multiset 比对, B 主判 default 1.1/0.9 + A cross-input 1.25/0.8 反硬编码)
- visible A: layout_A.json (rect+polygon+pathSeg+donut+ellipse+label + 1 instance(rect/donut/label), 打平 9 shape)
- hidden B: 嵌 check.py (NOR2X1, 不同形状/坐标/数量, 2 instances, default 1.1/0.9)
- 5 negative: empty_stub(c2)/print_only(c3)/naive_no_flatten(c4)/hardcode_b(c11)/core_deleted(c7) 全 FAIL distinct
- 自验全绿: REF self-test PASS 11/11 + negative_selftest OVERALL_RC=0(trio c2/c3/c7 distinct) + check() e2e True(ref)/False(cheat) + SKIP_RUN eval/run_one.sh 框架接受(attachments 全部署 prompt.txt+spec.md+layout_A.json, workdir leak 自检通过) + build_jsonl.py --shard C 重建 C.jsonl 644 active 本 case 入列
- ledger mark 1kfpb→case (covered 575→576)
- cases/C 648→649, L2.live 21 不变(本 case [L0,L1] LIVE-NA)
