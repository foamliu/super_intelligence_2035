# Deepread — 508od (junxu @ hfeg0plg79) — layout dbCreateLabel arg-order fix

- session: `1787217250604_508od`
- user/host: junxu / hfeg0plg79
- match_count: 2503 (virtuoso-dominant)
- shard/domain: C / layout_virtuoso
- case_id: `EDA-Eval-DesignFlow-LayoutLabelArgOrderFix-001`
- track: B (A-archive infeasible — live workspace READ-ONLY + virtuoso license/socket daemon unavailable in SUT sandbox → B-archive reframe as self-contained string-builder fixture)

## 真实任务意图

junxu 在给 Virtuoso SKILL 做一层 Python 业务封装（`/home/junxu/.cline/skills/virtuoso-cli/scripts/virtuoso_cli/api/{schematic,layout,ocean,general}.py`），把常用操作封装成 Python 方法，内部拼出 SKILL 表达式字符串再经 TCP 发给 Virtuoso。layout 模块用 `dbCreate*` 家族（与 Aether 的 `dbCrt*` 对齐，便于两套后端共用顶层命名）。

trace 的 35 条 user_input 流：
- U1-U8：建 virtuoso-cli 业务层（general + schematic 实现，layout/ocean 先建框架）
- U9-U14：搭电路、修 check error、释放写权限
- U15：完善连线 API（schCreateWire）
- U16-U18：**pin API bug**——用户指出「你用错 Pin 了」，GUI 显示真正用的是 `schHiCreatePin()`（schematic 域）
- U19-U22：搭复杂电路（SR latch），线没连到 pin
- U23-U28：**连线 bug**——Q 和 QN 被连到一起、线穿过器件，用户要求 API 自动走线不经过器件
- U29-U34：解释 `_route_around()` 实现
- U33-U35：**auto-router**——用户问「virtuoso 有直接可用的 auto-router 吗」，最终采纳 `schCreateWire "route" "full"`

## 选用的 bug-fix turning point

trace 里 schematic 域的 bug 更显眼（pin API、wire routing），但那些属于 shard D（schematic_netlist），不归 shard C。**layout 域**的真 bug 在 `layout.py` 的 `create_label`（@267/@269 首写 → @307/@311 修正）：

- **buggy**（@269 create_label）：拼 `dbCreateLabel` 时 emit 顺序是 `... to_skill(text) + " " + to_skill(orient) + " " + to_skill(justify) + " \"roman\" " + to_skill(height)`，即 **orient 在 justify 之前**。
- **fixed**（@311 create_label）：docstring 明确写出「Signature: dbCreateLabel(cv, lpp, point, label, just, orient, font, height) -- 7 args after cv」，emit 顺序改为 `... to_skill(text) + " " + to_skill(justify) + " " + to_skill(orient) + " \"roman\" " + to_skill(height)`，即 **justify 在 orient 之前**。

经 pyAether `get_api_details(["dbCreateLabel"])` 查 Cadence 官方文档确认：
```
dbCreateLabel(d_cellView txl_layerPurpose l_point t_label t_just t_orient t_font x_height)
```
即 justification (t_just) 必须在 orientation (t_orient) 之前。trace 的修复与官方文档一致，gold 成立。官方示例：`dbCreateLabel(cv 4 1:1 "myLabel" "centerLeft" "R0" "roman" 2)`（just "centerLeft" 在 orient "R0" 之前）。

## bug 的后果

顺序拼反时，Virtuoso 把 orient 的值（如 `"R0"`）当 justification 槽接收、把 just 的值（如 `"lowerLeft"`）当 orientation 槽接收——两者对调位置后皆属非法取值（`"R0"` 不是合法 justification，`"lowerLeft"` 不是合法 orientation），于是 `dbCreateLabel` 返回 nil，label 建不出来。

## fixture reframe（B-archive）

A 档不可行：live workspace 在远程 host 上 READ-ONLY，且 SUT 沙盒里没有 virtuoso license/socket daemon。B 档 reframe：把 `create_label` 的纯字符串构造部分抽成可单测的 `build_label_skill(layer, text, location, just, orient, height)`，返回 SKILL 表达式字符串（不发 TCP），SUT 无需运行 Virtuoso，只需让产出的字符串参数顺序正确。

- **env_A.tar.gz**（可见）：buggy layout.py + spec.json + manifest.json（A: VDD / M1 drawing / 0,0 / lowerLeft / R0 / 0.1）+ run.py（读 manifest 调 build_label_skill 写 report.json）
- **hidden/env_B.tar.gz**（反硬编码）：manifest_B.json（B: GND / M2 pin / 5.5,3.25 / centerCenter / MYR90 / 0.25——文本/层/坐标/just/orient/height 全不同）
- **check.py** 16 teeth (a-p)：结构检查 + 反硬编码（B 文本/层/坐标/高度）+ 核心修复（just 在 orient 前）+ 回归（orient 不在 just 前）+ 确定性（3-seed 字节一致）+ 源码守卫（build_label_skill 体内 to_skill(just) 在 to_skill(orient) 前）

## 自验

- ref solve.py：PASS 16/16
- 4 neg（only_print / hardcode_A / empty_report / buggy_order）全 FAIL，failset 互异（{e,g} / {h,i,j,k,m,p} / {g} / {k,l,p}）
- §4.9 (a)(b)(c) 三假全 FAIL
- roundtrip sha256 disk==jsonl==re-read = `da622f2b97e0522f5910ebc9ade4f5289b16976c1fa08a402714bf6782146bb6`
- k_rationale = k_check = 16 ≥ 8 ✓
- C.jsonl 573 → 574

## 备注

- 本 trace 的 schematic 域 bug（pin API、wire routing）属于 shard D，本用例只取 layout 域的 create_label arg-order bug，符合 shard C 归属。
- env_A 仅含 layout.py/spec.json/manifest.json/run.py，不含 check.py/reference/jsonl/test 字段，防泄题 ✓
