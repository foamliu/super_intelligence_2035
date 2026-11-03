# LEF 布线规则汇总工具

读取一份 LEF 技术库（techlef）文件，汇总每一层**走线层**与**通孔/切割层**的布线规则，
并输出为结构化 JSON。

## 文件清单

| 文件 | 说明 |
|------|------|
| `lef_rules.py` | 解析器与汇总脚本，接受一个 techlef 路径作命令行参数，stdout 输出 JSON |
| `rules_report_A.md` | 针对 `tech_thk2d0_m5.lef` 的人工可读汇总报告 |
| `README.md` | 本说明文档 |

## 使用方法

```bash
python3 lef_rules.py /path/to/tech.lef
```

示例：

```bash
python3 lef_rules.py assets/tech_thk2d0_m5.lef
python3 lef_rules.py /home/pdk/chengleiy/e_innovus/QA/tsi/tech_thk2d0_m5.lef
```

标准输出（stdout）为一个 JSON 对象。

## JSON 结构（schema）

```json
{
  "routing_layers": [
    {"name": "...", "direction": "...", "width": 0.0, "pitch": [],
     "max_width": null, "area": null, "offset": null, "spacing_table": null}
  ],
  "cut_layers": [
    {"name": "...", "spacing": 0.0, "adjacent_cuts_spacing": null}
  ],
  "vias": [
    {"name": "...", "cuts": 1, "resistance": 0.0, "layers": ["...", "..."]}
  ],
  "viarules": [
    {"name": "...", "layers": ["..."], "has_spacing": false,
     "enclosures": {"M1": [0.0, 0.0]}, "width_range": {"M1": "min TO max"}}
  ]
}
```

### 字段说明

- **routing_layers**：所有 `TYPE ROUTING` 层。
  - `direction`：`HORIZONTAL` 或 `VERTICAL`（可能为 `null`）。
  - `width`：`WIDTH` 数值。
  - `pitch`：`PITCH` 数值列表（可能 1 或 2 个值）。
  - `max_width`：`MAXWIDTH`（缺失时为 `null`）。
  - `area`：`AREA`（缺失时为 `null`）。
  - `offset`：`OFFSET` 数值列表（缺失时为 `null`）。
  - `spacing_table`：`SPACINGTABLE` 解析结果，结构为
    `{"parallel_run_length": [...], "width": [...], "spacing": [[...], ...]}`；
    若该层只有简单 `SPACING`（如 C4_bump、RDL）则为 `null`。
- **cut_layers**：所有 `TYPE CUT` 层。
  - `spacing`：普通 `SPACING` 数值。
  - `adjacent_cuts_spacing`：`SPACING <v> ADJACENTCUTS ... WITHIN ...` 中的 `<v>`；缺失时为 `null`。
- **vias**：所有 `VIA` 定义。
  - `cuts`：该过孔 CUT 层上的 `RECT` 数量（1/2/4 孔等）。
  - `resistance`：`RESISTANCE` 数值。
  - `layers`：VIA 内 `LAYER` 出现顺序。
- **viarules**：所有 `VIARULE ... GENERATE` 规则。
  - `layers`：规则内 `LAYER` 出现顺序。
  - `has_spacing`：该规则是否含 `SPACING` 声明（true/false）。
  - `enclosures`：dict，键 = 层名，值 = `[overhang1, overhang2]`。
  - `width_range`：**扁平 dict**，键 = 层名（如 `"M1"`），值 = `"min TO max"` 字符串
    （如 `"0.88 TO 14"`），**不是**嵌套 dict。

### 数值类型

数值 token 保留原文拼写：整数（如 `12`、`3`）输出为 JSON 整数，小数（如 `8.88`、`0.68`）输出为 JSON 浮点。