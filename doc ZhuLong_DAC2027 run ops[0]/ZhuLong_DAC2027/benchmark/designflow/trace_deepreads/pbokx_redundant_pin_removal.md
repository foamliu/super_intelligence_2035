# pbokx — pyAether 冗余 pin 清除脚本补全与多轮精化

- session: `1793241530970_pbokx`
- user: `haiquanp` @ `hfeg0plg36` (10.129.32.46)
- mc: 57 (pyaether:150;aether:75;virtuoso:14;lvs:9;dbget:8;schematic:7;cellview:7;drc:6)
- domain: **layout_aether** (pyAether / Aether cellview pin 编辑)
- 73 msgs / 6 real user_input turns
- 复现：messages.json 348KB，scp 自 10.129.32.46:/home/haiquanp/.cline/data/sessions/1793241530970_pbokx/

## 用户真实意图（逐轮原文）

- **U#0**（骨架补全）：`cv = ae.aeGetCurDesign() ... undoFlag = ae.aeEnableUndo() for pin in redundant_pins: ae.dbDelete(obj=pin) ...` — 给出 pyAether 骨架，要求补全「遍历 cv.terminals，找出冗余 pin，删除」。
- **U#22**：最终输出的代码不带注释，print 的信息用英文表示。
- **U#32**：你输出的代码不需要遵循 python 的缩进规则吗？为什么；输出一版带缩进的版本。
- **U#34**：报错 `AttributeError: 'NoneType' object has no attribute 'layerName'`（`pin.fig` 为 None）。
- **U#40**：`pin.fig` 为 None 时，属于 ghost pin，把这个 pin 加到 redundant_pins 里，后续一起清除。
- **U#46**：1.封装成函数 2.`ae.dbDelete` 的调用结果会自动回显一个 True 到 aether python 控制台，污染日志；是否有方法控制。
- **U#57**：函数调用增加一个参数 `except_pins = []`，匹配 `terminal.name`，在这个 list 里的 terminal 不做 remove redundant pin 的动作。
- **U#63**：报错 `'list' object has no attribute 'terminals'`（调用 `remove_redundant_pins([...])` 时 list 被当作 cv）。

## 助手 gold 链

1. skills(eda_agent) → 路由 pyAether 域
2. RAG search_apis（terminal pins layerName / dbDelete aeEnableUndo）+ get_api_details(emyTermGetPinFigs/aeDeleteObj/dbDelete)
3. read_files case_006_convert_pins_to_labels.md（参考 case study）
4. **3 次 ask_question 消歧**（规则定义的关键，见下）
5. editor 写 `/home/haiquanp/Desktop/remove_redundant_pins.py`
6. 多轮 editor 修订：去注释+英文 print → 修 `pin.fig is None` (先当特例跳过 → 后改为 ghost pin 入清除列) → 封装函数 + `_ = ae.dbDelete(obj=pin)` 吞回显 → 加 `except_pins` 参数 → 修签名 `except_pins` 第一位置参 / `cv` keyword-only
7. read_files 反复校验最终文件

## ask_question 消歧（规则来源）

- **Q1（保留策略）**：terminal.pins=[p0(M1),p1(M3),p2(M3)] 时保留谁？
  → 用户答：**规则1与规则2合并：每个 terminal 最终只保留 1 个 pin ——「最高金属层中下标最小（terminal.pins 中靠前）的那个」，其余全部删除**（保留 p1，删除 p0、p2）。
- **Q2（层名格式）**：`str(pin.fig.layerName)` 返回格式？
  → 用户答：**严格就是 'M1'..'M6'（不带 purpose 后缀），直接字符串相等判断即可，不在这个集合里就视为「特例」**（跳过该 terminal 并 print name）。
- **Q3（脚本结构/输出）**：是否打印汇总、是否做成函数？
  → 用户答（早期）：**保持顶层脚本结构，删除完成后打印汇总「共清理 N 个冗余 pin」**。（后期 U#46 改为封装函数。）
- **Q4（cv 传参）**：cv 默认由 `ae.aeGetCurDesign()` 获取，不应作为输入参数；调用 `remove_redundant_pins([...])` 的 list 是 except_pins。
  → 助手把签名改为 `remove_redundant_pins(except_pins=None, *, cv=None)`，cv=None 时内部 `ae.aeGetCurDesign()`。

## 最终 gold 脚本（trace 末尾用户接受，A#70 read_files 校验）

```python
import pyAether as ae

LAYER_ORDER = {"M1": 0, "M2": 1, "M3": 2, "M4": 3, "M5": 4, "M6": 5}


def remove_redundant_pins(except_pins=None, *, cv=None):
    if cv is None:
        cv = ae.aeGetCurDesign()
    if cv is None:
        print("Error: No design is open")
        return 0
    if except_pins is None:
        except_pins = []

    redundant_pins = []
    for terminal in cv.terminals:
        if terminal.name in except_pins:
            continue
        if len(terminal.pins) <= 1:
            continue
        pins = terminal.pins
        ghost = [p for p in pins if p.fig is None]
        redundant_pins.extend(ghost)
        valid_pins = [p for p in pins if p.fig is not None]
        layer_idx = []
        is_special = False
        for p in valid_pins:
            lname = str(p.fig.layerName)
            if lname in LAYER_ORDER:
                layer_idx.append(LAYER_ORDER[lname])
            else:
                is_special = True
                break
        if is_special:
            print(terminal.name)
            continue
        if not valid_pins:
            continue
        max_idx = max(layer_idx)
        keep_idx = None
        for i, p in enumerate(valid_pins):
            if LAYER_ORDER[str(p.fig.layerName)] == max_idx:
                keep_idx = i
                break
        for i, p in enumerate(valid_pins):
            if i != keep_idx:
                redundant_pins.append(p)

    undoFlag = ae.aeEnableUndo()
    for pin in redundant_pins:
        _ = ae.dbDelete(obj=pin)
    undoFlag.disable()

    return len(redundant_pins)


n = remove_redundant_pins()
print(f"Cleaned {n} redundant pin(s)")
```

## 规则汇总（reframe 判分依据）

1. 函数签名 `remove_redundant_pins(except_pins=None, *, cv=None)`：`except_pins` 第一位置参，`cv` keyword-only；`cv=None` → 内部 `ae.aeGetCurDesign()`；`aeGetCurDesign()` 返回 None → print "Error: No design is open" + return 0。
2. 遍历 `cv.terminals`：`terminal.name in except_pins` → 跳过；`len(terminal.pins)<=1` → 跳过。
3. **ghost pin**（`pin.fig is None`）→ 直接加入 redundant_pins（与层逻辑独立，先一次性挑出）。
4. 非 ghost pin：`str(pin.fig.layerName)` 严格匹配 `M1..M6`（LAYER_ORDER）；任一 pin 层名不在集合 → **特例**：print `terminal.name` + continue（该 terminal 不删除任何 pin）。
5. 正常 terminal：保留「最高金属层中 `valid_pins` 下标最小」的 pin，其余 valid pin 全部加入 redundant_pins。
6. `ae.aeEnableUndo()` → 循环 `ae.dbDelete(obj=pin)`（**`obj=` 关键字**，返回值用 `_ = ` 吞掉以抑制控制台 True 回显）→ `undoFlag.disable()`。
7. 顶层 `n = remove_redundant_pins(); print(f"Cleaned {n} redundant pin(s)")`；无注释、英文 print。

## reframe 思路（B 档）

- A 档 gold = live pyAether `ae.aeGetCurDesign()` + 真实 Aether cellview，依赖 live Aether 库不可复现，且无 ≥8 独立硬断言牙 → reframe 为**离线 mock 注入**判分：check.py 向 `sys.modules['pyAether']` 注入 fake 模块（`aeGetCurDesign` 返回 mock design / `aeEnableUndo` 返回 mock flag / `dbDelete(obj=)` 记录被删 pin tag），exec 候选脚本，按规则独立计算期望删除集，比对 `dbDelete` log。
- 候选只许 `import pyAether as ae` + stdlib（pyAether 被 mock 注入，无需真实 Aether）。
- visible A fixture（manifest_A.json，进 SUT 沙箱）与 hidden B fixture（manifest_B.json，不进 SUT 沙箱）terminals/pins/层/except 全反相，防硬编。
- 子型：**pyAether cellview pin 编辑脚本补全 + 多轮规则精化** reframe（layout_aether）。与 VirtCellNameFromIlProduce（.il 解析推断 cellview）/ VirtBridgeStatusDiag（桥接 TCP 可达性）/ VirtuosoOpenCellQueryGen（生成 open 脚本）正交：本案=**pyAether API 调用语义脚本补全**（terminals/pins/fig/layerName/dbDelete/aeEnableUndo）。

## 意图审计

- **keep**：haiquanp 真实意图（补全 + 多轮精化冗余 pin 清除 pyAether 脚本）完全保留。reframe 是 grounding（把「在 live Aether cellview 上操作 pin」沉淀为「mock 注入 + 规则等价校验」，单文件化 + 离线化），非加难。所有规则来自用户 ask_question 答案与报错反馈，未引入用户未要求的内容。
- 2026-11-15 reaudit 后 env-config/flow-driving 合法（脚本补全属真实 layout_aether 用户意图）。
