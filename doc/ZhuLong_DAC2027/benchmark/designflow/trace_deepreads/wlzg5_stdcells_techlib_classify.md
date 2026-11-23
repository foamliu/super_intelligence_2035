# trace_deepread: wlzg5 — stdcells_ac + TECHLIB 库器件识别与分类 (layout_aether)

- **sid**: `1794795450092_wlzg5`
- **user / host**: jiashengz / hfeg0plg92 (10.129.?.?)
- **match_count**: 238 (lvs:1166; aether:534; pyaether:330; schematic:299; cellview:146 — "lvs" 高频是 cell 名 `invLVSx1` 的子串，非 LVS 验证)
- **domain**: layout_aether（Aether 设计库枚举 + schematic/symbol 学习 + skill 沉淀）
- **session size**: 137 msgs, messages.json 789 KB
- **agent tool chain**: list_allowed_files×11, run_approved_command×35, editor×21, read_files×58

## 用户意图（原话时间线）

U[0] @msg0: 「识别一下 stdcells_ac 和 techlib 库里都是什么器件和标准单元，通常来说，有一部分 cell 前三个字是缩写比如 inv 是反相器，lat 是 latch，ff 是 flipflop，LV IOLV 等为器件类型标识器件速度，x 后跟数字代表驱动大小，ptn 为数字电路常用的薄氧管 pmos，ptk 为厚氧管，noConn 为 noconnect，vss 为 vss，vcc vdd 为电源。」

U[1] @msg58: 「学习相应的 symbol 和 schematic 画法，形成自己的理解」

U[2] @msg93: 「沉淀为一个统一的 skill」

U[3] @msg96: 「清理一下多余的打开的窗口 不要把 dm 也关了」

U[4] @msg116: 「提炼成一个统一的 skill」

## assistant 关键产出

- 通过 `dbGetAllCells` 实时查询 Aether 设计库，导出 `stdcells_ac_cells.txt` (1729 cell) + `TECHLIB_cells.txt` (651 cell) 到 `/home/jiashengz/agentdir/train/V0_NCG_HF_Aether/`。
- 写 `README_stdcells_TECHLIB_识别报告.md`：分类两库命名规则 `<功能缩写><器件速度><xN>`，列出 40 类基础逻辑构型 + 后缀表 (L/LV/LVS/IOLV/IOS/CS/DS/GS/B*/H*/Y/V/W/M) + 驱动强度 xN 分布。
- 写 `README_symbol_schematic_画法理解.md`：通过 pyAether 实测打开 `inv/invGS/nand2/ptn/noConn/vss/vcc/vdd1/invLVSx1/ffqLVSx1` 等 cellview，反推 symbol/schematic 画法。
- 写 unified skill `/home/jiashengz/.cline/skills/aether-stdcells-techlib/SKILL.md`。
- 窗口管理：`aeGetWndList("design")` 枚举 23 个 design 窗口逐个 `close()`，保留 DM。

## reframe 子型（本 case）

schematic/symbol 学习 + skill 沉淀 + 窗口管理均依赖 live Aether，不可离线判分。提取**可独立判分**的子型：

**stdcells_ac + TECHLIB cell-name 分类器** —— 给两份 cell 清单（`stdcells_*_cells.txt` 首行 `count=N` + 一行一 cell），按用户 U[0] 给出的命名规则，输出每 cell 的结构化分类 JSON：

```
{
  "name": "invLVSx1",
  "library": "stdcells_ac",     // stdcells_ac | TECHLIB
  "function": "inv",            // inv|buf|nand|nor|and|or|aoi|oai|xor|xnor|ff|lat|mx|passgt|dly|pulse|fb|rsnand|rsnor|invhiz|inven|mos|power|special|passive|pad|esd|other
  "variant": "LVS",             // LVS|LV|CS|DS|GS|IOLV|IOLVIO|IOS|GF|PF|PT|GT|lv|sv1|sv2|...|null
  "drive": 1,                   // xN 整数 or null（primitive 无 xN）
  "category": "stdcell",        // stdcell | primitive_gate | device | power | special | passive | pad | esd | other
  "is_device": false,           // ptn/ptk/ntn/ntk + _lv/_sv 变体
  "is_power": false,            // vss/vcc/vdd*/vssq/vssdll/...
  "is_special": false           // noConn / Mark* / brknet / dummyLine / noteSymbol
}
```
+ 顶层汇总：`total / per_function / per_variant / per_category / device_count / power_count / special_count`。

### 用户 U[0] 规则映射（判分硬约束）
| 片段 | 用户原话 | 分类字段 |
|------|---------|---------|
| `inv` | 反相器 | function=inv |
| `lat` | latch | function=lat |
| `ff` | flipflop | function=ff |
| `LV`/`IOLV` | 器件速度 | variant ∈ {LV, IOLV, IOLVIO, LVS, IOS, CS, DS, GS} |
| `x<数字>` | 驱动大小 | drive=int(N) |
| `ptn` | 数字电路薄氧 PMOS | category=device, is_device=true, function=mos |
| `ptk` | 厚氧 PMOS | category=device, is_device=true, function=mos |
| `noConn` | noconnect | category=special, is_special=true |
| `vss` | vss | category=power, is_power=true |
| `vcc`/`vdd` | 电源 | category=power, is_power=true |

## 为什么合法 produce

- 真实 trace（.75 免密 ssh 到 hfeg0plg92 取到 messages.json 789KB + 真实 cell 清单 1729+651）。
- 用户 U[0] 给出明确命名规则，分类规则有源（不是 agent 凭空造）。
- 子型首例：C 域 layout_aether 现有 case 涉及 pcell/SKILL/DRC/LVS，"cell-name → 结构化分类器"是新子型，与现有 C case 正交（DrcQaConfigParse 是 drcpv config 解析；CdlPortStats 是 CDL 端口统计；AetherNetlistCellListGen 是 HSPICE cell 枚举 — 后者枚举不分类）。

## 质量

- k=14 (a-n)：①zip 结构 ②py_compile ③exit 0 ④JSON schema ⑤total 匹配 ⑥probe-cell 分类正确 ⑦per_function 计数 ⑧per_variant 计数 ⑨device_count ⑩power_count ⑪special_count ⑫anti-hardcode B-specific cell ⑬3-seed 确定性 ⑭drive 解析边界 (x00→0 / 无 xN→null)
- A=sample_a (40 stdcells_ac + 20 TECHLIB = 60 cell) / B=hidden (50 stdcells_ac + 30 TECHLIB = 80 cell)，A/B cell 名无交集，分布不同 (anti-hardcode)
- ref PASS 14/14；3 neg (empty_shell / print_only / hardcode_b) 全 FAIL distinct；§4.9 (a)(b)(c) 三假全 FAIL
- check() 独立 tmp dir 解 zip；SUT workdir 不留 `__chk`
