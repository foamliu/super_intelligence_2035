# r642 深读 — jzeng @ hfeg0pkn003 / session 1794642438159_m8n71

- **user**: jzeng  **host**: hfeg0pkn003 (10.129.2.12)  **session**: 1794642438159_m8n71
- **mc**: 25  **keywords**: drc:151;.gds:41;pyaether:24;dbget:16;aether:11;calibre:10;dbopencv:8;netlist:6
- **domain**: layout_aether (pyAether via-generation 脚本修改)
- **msgs**: 106 / 2 real user turns / 748KB
- **trace_source**: real_task_summary = "修改 IMCleAutoVia.py，让 V4 孔能在横向 0.55um M4 与纵向 0.55um M5 间打出（长边上下/短边左右），按 enclosure choice (bottom=dir_3D_Y, top=NONE) 条件化 enclosure 参数，并强制 V4 方向 R90"

## 用户原话（逐字，未脱敏）

**U#0** (msg 0): `<user_input mode="act">/home/jzeng/Desktop/IMCleAutoVia.py优化该脚本，使其在横向0.55um宽度的M4和纵向0.55um宽度的M5之间可以打出V4孔，该V4孔长边为上下走向，短边左右走向，V4 Parameter如下，Enclosure choice of bottom layer: dir_3D_Y; Enclosure choice of top layer: NONE</user_input>`

**U#76** (msg 76): `<user_input mode="act">增加条件V4方向为R90</user_input>`

两轮均为「提出需求」型（未给根因/方案）→ 符合 A 档选轮。

## agent 行为

直接用 `editor` 工具修改 `/home/jzeng/Desktop/IMCleAutoVia.py`（1849 行 pyAether auto-via 脚本）。逐行读取后做 9 处定点编辑，未跑脚本（pyAether/OA/techdb 不可在 agent 沙盒跑）。用户在 U#76 后未再追问 → 接受态 = 最终脚本。

## gold = 最终修改态（9 处编辑）

### Feature 1（U#0）: enclosure-choice 条件化 enclosure 参数

1. `IMCleGetRectProp` & `gen_via_from_y` 新增 `botEncChoice=''`/`topEncChoice=''` 初始化
2. 两处 label 解析新增 `botEncChoice:` / `topEncChoice:` handler（strip 后存字符串）
3. `IMCleCrtViaAndSetDefOverrideEx` 签名加 `botEncChoice='', topEncChoice=''`，body 改条件 append：
   - `botEncChoice=='NONE'` → 跳过所有 layer1 enclosure
   - `botEncChoice=='DIR_3D_Y'` → 只 `layer1YEnclosure`
   - else → legacy（layer1X + layer1Y）
   - `topEncChoice=='NONE'` → 跳过所有 layer2 enclosure
   - else → legacy（layer2X + layer2Y）
4. 5 个 call site（IMCleGetRectProp 3 + gen_via_from_y 2）传 botEncChoice/topEncChoice

### Feature 2（U#76）: R90 旋转感知轴映射 + V4 R90 强制

5. `IMCleCrtViaAndSetDefOverrideEx` 旋转感知：
   - `_isRotated = orient in ('R90','R270')`
   - `DIR_3D_Y` + R0 → `layer1YEnclosure`；+ R90 → `layer1XEnclosure`（via Y 映射到 layout X）
   - `DIR_3D_X` + R0 → `layer1XEnclosure`；+ R90 → `layer1YEnclosure`
   - top 同理（topEncChoice != NONE 时）
6. `IMCleGetRectProp`：V4 + dir_3D_Y + NONE → `orient='R90'`
7. `gen_via_from_y`：V4 + dir_3D_Y + NONE → `orient='R90'` + `direct='horizontal'`

## 物理意义

V4 via 的 tech 定义里 bottom(M4) enclosure 只在 via-cell 内禀 Y 方向有效（dir_3D_Y）、top(M5) 无 enclosure（NONE）。原脚本无条件传 4 个 enclosure 参数 → V4 创建失败。修复后按 choice 跳过/选轴；R90 时 via 内禀 Y 映射到 layout X，故传 layer1XEnclosure。V4 长边上下走向 = R90。

## 与 r634 (ozhy4) 区别

r634 = 同一脚本 IMCleAutoVia.py 的非 ASCII 字符清洗（→/中文注释）；r642 = 同一脚本的 via enclosure-choice 功能增强。同 artifact 不同意图，非 same_trace_group near-dup。

## B 档 reframe

真实 1849 行脚本 + pyAether/OA/techdb 不可达沙盒 → 合成紧凑可运行 mock（保留 via 创建结构 + label 解析 + 3 call branch）。deliverable = 修改后的 IMCleAutoVia.py。check() 注入 mock `ae`，跑场景电池（V4 R90 dir_3D_Y NONE[gold] / V4 R0 / legacy / NONE-NONE / dir_3D_X / 交叉输入 V5 / label force-orient 管线 / gen_via_from_y），断言记录的 params.append 序列。子型 `pyaether-via-enclosure-choice-r90-force`。
