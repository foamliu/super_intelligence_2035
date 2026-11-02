# Tech LEF 布线规则汇总（TLEF Rules）

从工艺技术 LEF 文件 `assets/tech_thk2d0_m5.lef`（LEF 5.7，单位 `DATABASE MICRONS 4000`，即文件中尺寸数值均为微米 µm，制造网格 0.00025 µm）中提取的布线规则汇总。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `lef_rules.py` | 解析 tech LEF 并输出结构化 JSON 的脚本，接受 techlef 路径作为命令行参数 |
| `rules_report_A.md` | 每一走线层 / 通孔层 / 过孔 / 过孔规则的可读汇总报告 |
| `README.md` | 本说明文档 |

## 用法

```bash
python3 lef_rules.py <path/to/techlef>
python3 lef_rules.py assets/tech_thk2d0_m5.lef
```

脚本把结构化 JSON（`indent=2`）写到 stdout。退出码：`0` 成功，`2` 参数错误。

输出示例：

```json
{
  "routing_layers": [ ... ],
  "cut_layers":     [ ... ],
  "vias":           [ ... ],
  "viarules":       [ ... ]
}
```

## JSON Schema

### routing_layers（走线层）

每个 `TYPE ROUTING` 层一项：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 层名，如 `M1` |
| `direction` | string | 布线方向 `HORIZONTAL` / `VERTICAL` |
| `width` | number | 默认线宽（µm） |
| `pitch` | array | 布线节距 `[x, y]` 或 `[x]`（µm） |
| `max_width` | number/null | `MAXWIDTH`（µm），无则为 `null` |
| `area` | number/null | 最小面积（µm²），无则为 `null` |
| `offset` | array/null | `OFFSET`（µm），无则为 `null` |
| `spacing_table` | object/null | 间距规则（见下） |

`spacing_table` 两种形态：

- 层定义了 `SPACINGTABLE`：

  ```json
  {
    "parallel_run_length": [0.0, 1.5, 4.5],
    "rows": [
      {"width": 0.0, "spacing": [0.88, 0.88, 0.88]},
      {"width": 1.5, "spacing": [1.0, 1.0, 1.0]},
      {"width": 4.5, "spacing": [1.8, 1.8, 1.8]}
    ]
  }
  ```

  各 `rows[i].spacing[j]` 对应第 `j` 个 `parallel_run_length` 分段。

- 层仅定义了 `SPACING`（如 `C4_bump`、`RDL`）：

  ```json
  {"spacing": 9.0}
  ```

### cut_layers（通孔层）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 层名，如 `V1` |
| `spacing` | number | 基本间距（µm） |
| `adjacent_cuts_spacing` | object/null | `ADJACENTCUTS` 规则，无则为 `null` |

`adjacent_cuts_spacing`（存在时）：

```json
{"spacing": 1.08, "adjacent_cuts": 3, "within": 1.1}
```

### vias（过孔）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 过孔名，如 `VIA1_1cut` |
| `cuts` | int | 切割（cut）矩形数量 |
| `resistance` | number | 贯穿电阻（Ω） |
| `layers` | array | 过孔跨接的层名，如 `["M1", "V1", "M2"]` |

### viarules（过孔规则）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 规则名，如 `GENV1` |
| `layers` | array | 参与层名 |
| `has_spacing` | bool | 是否定义阵列间距 `SPACING` |
| `enclosures` | object | `{layer: [x, y]}` 各金属层包围量 |
| `width_range` | object | `{layer: {"min": m, "max": M}}` 允许线宽范围 |

详见 `rules_report_A.md`。