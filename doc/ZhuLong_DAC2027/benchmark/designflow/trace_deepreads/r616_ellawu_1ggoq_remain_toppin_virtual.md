# r616 deepread — 1ggoq layout-remain-top-pin-virtual (ellawu@hfeg0pkn005)

- **session**: `1792723085633_1ggoq.messages.json` (ellawu @ hfeg0pkn005 / 10.129.2.14, mc=109)
- **domain**: layout_aether (pyAether layout script maintenance; keywords: layout / dbOpenCV / aeAddTrace / auto_via / ASSTRM)
- **size**: 282 msgs / 5 real user_inputs / 364 KB (via .75 ssh cat)
- **ledger**: was parked (r537, note "debug/analysis REJECT") → 2026-11-15 intent-audit reaudited 可造 (debug/modify-existing legal under new rules) → r616 revive → deepread (DEBT:1, case synthesis next round)
- **author**: ellawu — known C-line author (r535 PctAgtSpacingDeck-001, r536 EncloseSide2Good5-001, r586 peek 2 session Q&A/modify). Maintains CXMT layout SKILL/pyAether scripts.

## 用户真实意图（逐字原话，仅掩码 key/token）

- U[1] `ae.dmDeleteObj(ae.dmGetObj(lib_name, cell_name, view_name)) 改成用dbDelCV`
- U[2] (贴 dbDelCV 官方 API 文档：`dbDelCV(lib: emyString, cell: emyString, view: emyString="laydbut") -> bool`)
- U[3] `删除用dbDelCV` + 附 `cxmt_layout_remainTopPin_Virtual.py`（脚本全文）
- U[4] `ERROR: (ASSTRM-80158): Cannot open master "auto_via/AF_LvfsblnDrvGrp_sep_VIA_TOP/layout". The structure definition corresponding to this master will be missing. It is in unbound. 报错但是不需要这个文件`（报错但不需要这个文件）
- U[5] `报错导致中断运行`（错误导致脚本中断运行）

**核心 produce-task**：维护 `cxmt_layout_remainTopPin_Virtual.py`（批量去除冗余 top pin、保留虚拟连接的 topmost pin，移植自 SKILL 脚本 `cxmt_layout_rmRedundantAndRemainTopPins*`）。两件事：(1) 把删除临时 cellview 的 API 从 `ae.dmDeleteObj(ae.dmGetObj(...))` 改成 `ae.dbDelCV(lib,cell,view)`；(2) 处理 `ae.dbOpenCV` 打开 trace 临时 cellview 时触发的 `ASSTRM-80158`（引用未绑定 master `auto_via/AF_LvfsblnDrvGrp_sep_VIA_TOP`）—— 该 master 不需要，但报错导致脚本中断，需让脚本继续执行。

## assistant 真实交付（A70 editor old→new = gold fix）

对 `get_delete_pin_list_by_connection(target_pin)` 函数三处改动：

### 改动 1 — 删除 API：dmDeleteObj → dbDelCV
**old**:
```python
temp_obj = ae.dmGetObj(lib_name, cell_name, view_name)
if temp_obj:
    ae.dmDeleteObj(temp_obj)
```
**new**:
```python
# Clean up any existing temp cell view using dbDelCV
if ae.dmGetObj(lib_name, cell_name, view_name):
    ae.dbDelCV(lib_name, cell_name, view_name)
```
（仍先用 dmGetObj 探测存在性，但删除改用 dbDelCV 按名删，不再两步取对象再删）

### 改动 2 — aeAddTrace 只调用一次（修原 bug）
**old**（重复调用，第二次永远走不到 elif）:
```python
if ae.aeAddTrace(pObj=target_pin) == -1:
    ...
elif ae.aeAddTrace(pObj=target_pin) == -2:
    ...
```
**new**（存返回值，只调一次）:
```python
ret = ae.aeAddTrace(pObj=target_pin)
if ret == -1:
    ...
elif ret == -2:
    ...
```

### 改动 3 — dbOpenCV try-except 容忍 ASSTRM-80158 unbound master + fallback
**old**（裸调用，unbound master 直接抛错中断）:
```python
mark_cv = ae.dbOpenCV(lib=lib_name, cell=cell_name, view=view_name, mode="r")
if mark_cv is None:
    print("Error: cannot open temporary cellview")
    return None
```
**new**（try-except 包裹 + dbOpenCVByType 兜底 + 形状读取也容错）:
```python
# Wrap in try-except because aeSaveTrace may create a cellview that references
# unbound masters (e.g. auto_via). The error (ASSTRM-80158) is non-critical:
# we only need the Path/PathSeg trace shapes, not the master references.
try:
    mark_cv = ae.dbOpenCV(lib=lib_name, cell=cell_name, view=view_name, mode="r")
except Exception as e:
    print(f"Warning: encountered unbound master references in temp cellview: {e}")
    print("The trace shapes may still be accessible; attempting recovery...")
    mark_cv = None
if mark_cv is None:
    # Try dbOpenCVByType as fallback (recommended over dbOpenCV since v2025.03)
    try:
        mark_cv = ae.dbOpenCVByType(lib=lib_name, cell=cell_name, view=view_name,
                                    viewType="layout", mode="r")
    except Exception as e2:
        print(f"Error: cannot open temporary cellview even with fallback: {e2}")
        ae.dbDelCV(lib_name, cell_name, view_name)
        return None
...
mark_shapes = []
try:
    mark_shapes = [s for s in mark_cv.shapes
                   if s.objType in ("Path","PathSeg") and s.purpose != "pin"]
except Exception as e:
    print(f"Warning: error reading shapes from temp cellview: {e}")
    ae.dbCloseCV(mark_cv); ae.dbDelCV(lib_name, cell_name, view_name); return None
```

## 关键事实 / 脚本结构（gold = post-edit 上传版，282 msgs 内确认）

- `LAYER_INDEX = ["PWNW","AAOD","PGPO","MT2","M0U","M1","M2","M3","M4","M5","M6","T2M1","T2M2","T2M3"]`（topmost pin 按 layer precedence 取 index 最大者）
- 主流程 `cxmt_layout_remain_top_pin_virtual()`：`aeEnableUndo` → 遍历 `cv.shapes` 中 `purpose=="pin"` → 跳过无名/全局网（含 `!`）→ `get_delete_pin_list_by_connection(pin)` → 写报告 `rmPins_topPins_withVirtual_list.rpt`（每 pin 一段：pin 名 / 删除层 / 坐标）
- `get_delete_pin_list_by_connection`：aeAddTrace → aeSaveTrace 存临时 cv `layout_auto_remainPin_tmp` → dbOpenCV 取 trace shapes（Path/PathSeg）→ `dbGetTrueOverlapsEx` 找同层重叠 pin → 按 LAYER_INDEX 选 topmost → 其余入 delete_list
- 临时 cv 清理：dbCloseCV + dbDelCV（按名删）
- ASSTRM-80158 根因：`aeSaveTrace` 创建的临时 cv 包含原图所有 instance 引用（含 `auto_via/AF_LvfsblnDrvGrp_sep_VIA_TOP`），该库当前环境 unbound → `dbOpenCV` 解析 master 失败抛错 → 脚本中断。但脚本只需 Path/PathSeg trace 形状，不需 master → try-except 容忍 + 兜底

## B档 mock-behavioral reframe（承 r602-r615 模式，case synthesis ETA r617）

源 workdir 沙盒不可达（ellawu 私有 + Aether license）→ asset_fidelity=synth。参数化纯 Python `layout_remain_top_pin.py <layout.json> <out.rpt>`，**或**带 pyAether mock 的 `cxmt_layout_remain_top_pin_virtual.py`（mock `ae` 记录调用日志）。

**待合成 case**：`LayoutRemainTopPinVirtualFix-001`，domain=layout_aether，layer=L1-boundary（offline Python + mock），track=B。

**输入 A**（真实还原 ellawu 场景）：layout 含若干 net 的重叠 pin（M2/M3/M4 等），1 个 unbound master 引用 `auto_via/AF_LvfsblnDrvGrp_sep_VIA_TOP`；预置 buggy 版（dmDeleteObj + 双调 aeAddTrace + 裸 dbOpenCV）。
**隐藏 B**（反硬编）：不同 net/pin/层结构 + unbound master `auto_via/AF_LvfsblnDrvGrp_sep_VIA_MID`（不同名）+ 不同 LAYER_INDEX 顺序边界。
**隐藏 B2**：无 unbound master 的净 layout（验证正常路径不被 try-except 误伤）+ 全局网 `vdd!`/`vss!` 应跳过。

**check() 拟定 ≥12 条 a-l**（behavioral，跑候选于 B/B2 + 断言 mock 调用日志 + 报告）：
- a: zip 含 .py + py_compile 通过
- b: B exit 0（unbound master 不中断）
- c: mock 调用日志含 dbDelCV（按名删）
- d: mock 调用日志不含 dmDeleteObj
- e: aeAddTrace 每 pin 恰调一次（非两次）
- f: dbOpenCV 失败被容忍（dbOpenCVByType 兜底出现 或 无 abort）
- g: 报告含正确 topmost-kept pin（按 LAYER_INDEX precedence）
- h: 报告含正确 deleted lower pins（lower layer 同 net 重叠者）
- i: 全局网（含 `!`）被跳过（不在报告）
- j: B2 无 unbound master 时正常路径不误伤（topmost 正确 + 无 false delete）
- k: B2 反硬编（B≠B2 删除列表 + unbound master 名不同）
- l: 确定性（两跑字节一致 / mock 调用序列稳定）

**negative**（≥2）：naive_empty（空脚本→b/c 全 FAIL）/ print_expected（只打印期望报告串→g/h FAIL）/ deleted_core（删 try-except + 改回 dmDeleteObj→b/d/e/f FAIL）。

**自验目标**：ref 12/12 PASS；3 neg 全 FAIL；§4.9(a)(b)(c) 三假全 FAIL；NEGATIVE_SELFTEST ALL-FAIL；k=12≥8。

## distinct / same_trace_group
- **distinct** vs r535 PctAgtSpacingDeck-001（SVRF deck 百分比间距规则生成）/ r536 EncloseSide2Good5-001（enclose pattern good/bad 变体生成）/ r539 FreeTrackFinder / r545 PgRailLabelReplace（PG rail 重布 pin）—— 本 case 是 **layout pin 冗余去除脚本维护 + Aether API 升级（dmDeleteObj→dbDelCV）+ unbound master 容错**，新子型 *layout-pin-redundancy-removal-script-fix*。
- **cap-1** same_trace_group `1ggoq-remain-top-pin-virtual`（本 trace 唯一 case）。
- 与 r545 PgRailLabelReplace 都涉及 layout pin/label 处理，但 r545=重布 PG pin（gdstk 几何），本 case=去除冗余 top pin（pyAether trace + 层优先级），check 内核不同。

## 进度
- r616：deepread 完成 ✓（本文件）；case synthesis DEBT:1，ETA r617（清 DEBT 第一件事）。
- 选料经 r616 验证：pool_reaudit_C "可造" 标签的 domain 字段不可全信（gvm3g 标 layout_virtuoso 实为 spice_sim；opm9y 标 layout_virtuoso 实为 schematic/spectre）—— 须 deepread 确认 C-domain。1ggoq 经 deepread 确为 layout_aether（pyAether layout 脚本）✓。
