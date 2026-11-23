# trace_deepread: 1795144745219_ezpe5 (max7c @ hfeg0pkn005) — async-risk reset waive 生成

- session: `/home/max7c/.cline/data/sessions/1795144745219_ezpe5/1795144745219_ezpe5.messages.json`
- size: 589KB / 163 msgs (83 user / 80 assistant), agent=cline, 7 user turns
- match_count=123, domain=schematic_netlist (netlist:334 analog:55 wv:89 drc:13)
- scp 来源: hfeg0pkn005 (known-good host, .75 经 ssh 免密)

## 真实用户意图（逐 user turn）

1. **(idx0)** 读 `final_report.csv` 第 282 行：cell `I_Array16GTop...I_CasIopu` 的 `I40`，async-risk 出错引脚 `[BC]`/`[B]`，去网表 `V0_LP5TOP_2026Nov13.085035/netlist` 找该 cell，把 B 和 C 引脚外接的信号名发我。
2. **(idx34)** 把 CSV 里所有 async-risk 行扫一遍，看各行出错引脚外接的信号名是啥，输出成一个 log。
3. **(idx84)** 得到引脚外接信号名后，哪几个 cell 的**全部**出错引脚外接信号名都带 rst/reset 复位信号。
4. **(idx96)** 用现有 `.waive` 格式把结果输出成一个 waive 列表。
5. **(idx108)** 把上述过程总结成可执行脚本：输入 final_report.csv + netlist，输出 `/home/max7c/async_risk_reset.waive`。
6. (idx133) 重复 5。
7. **(idx153)** diff 生成的 waive 与现有 `final_report.csv.waive` 差在哪。

## 关键数据格式

### CSV (final_report.csv, 2766 行)
header(12 列): `num,hierpath,inst,instName,type,not_covered_pin,timing violation,waveform path,rising edge gap,falling edge gap,high pulse,low pulse`
- async-risk 行: `type == "async risk"`（2125/2765 行）
- 出错引脚: cols 8-11 的 `[XY]` 前缀，union 所有字符 → pin 集合 (A/B/C/D/Otu)
- hierpath (col1) = 从 root 到失败 cell 父模块的实例名链；instName (col3) = 失败 gate 实例名（可含 `<n>` bus index）

### 网表 (Verilog gate-level, 107MB, 4982 modules)
- `module NAME (ports...); ... endmodule`
- gate 实例: `CELLNAME INSTNAME (.Pin(signal), .Pin(signal), ...);`，INSTNAME 可含 `<n>`
- root modules = 未被任何模块例化的模块

### .waive 格式 (13 字段, 12 逗号)
```
## async-risk reset waive  Nov 20 13:31:36 2026
<hierpath>,inst,<instName>,not_covered,,,,,,,,yes,
```

## agent 算法（最终 generate_reset_waive.py, 10322 chars）

1. `parse_netlist`: 行扫描 → `module_instances[mod][instName_norm]=cellName` + `module_pinmaps[mod][instName_norm][pin]=signal`；`norm_inst(<n>)→_n_`；roots = modules - used_cells
2. CSV 过滤 `type=="async risk"`，对每行：trace hierpath tokens 从 roots → 解析含 instName 的模块 → 取 pinmap
3. `pins_of(row)`: cols 8-11 的 `[...]` 前缀 union 字符
4. 按 (hierpath, instName) 聚合 pin→signal（跨行 union）
5. 过滤: `pairs 非空 AND all(is_reset_like(sig) for sig)`，`RESET_RE=rst|reset (IGNORECASE)`
6. 输出 `## <date>` + 每 cell 一行 `<hp>,inst,<inst>,not_covered,,,,,,,,yes,`

## 结果
- 2125 async-risk 行 → 272 个 cell 全部出错引脚外接信号为复位类
- 21 种 (cell 类型 + 复位信号集合) 去重
- 272 vs 271 一行差异（跨行 union 逻辑 bug，已修）

## 可离线判分内核（本 case 抽取）
纯 Python：netlist parser (module/instance/pin 正则) + hierpath tracer + reset 过滤 + waive formatter。无 live EDA 依赖。A/B 用合成小网表 + CSV（结构性不相交：不同 module/cell/inst/signal 名 + 不同 pin 模式 + bus-index）。

## 复活
→ EDA-Eval-DesignFlow-AsyncRiskResetWaiveGen-001 (L1 schematic_netlist, k_check=18)
