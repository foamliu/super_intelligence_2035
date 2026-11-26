# 深读 ppwfb — Totem-SC DDR5 XTR.119 电源网短路审计

- **trace**: 1790844649225_ppwfb · user thomasz · host hfeg0pkn004(10.129.2.13) · mc126 · domain schematic_netlist
- **msgs**: 78 total · 6 real user turns（mode=act）· 中等深度 trace
- **工具链**: read_files / list_allowed_files / search_codebase（超时）· 全程在 `/rundata/totem/drcoa/IR/20260918/DDR5TOP_IDD5B_9200_X8_TT1.166v98c/` 只读分析，无修改
- **A-faithful produce-task = U#0**（读 run.log 解释 short 相关 warning）+ 后续 5 轮追问细化

## 用户原话（6 轮）
- **U#0**: `/rundata/totem/drcoa/IR/20260918/DDR5TOP_IDD5B_9200_X8_TT1.166v98c/run.log 读取一下这份文件，解释一下short相关的warning`
- **U#27**: `WARNING<XTR.119> There is a short found between $TypeNet1 Net($Net1) and $TypeNet2 Net($Net2) at Layer($Layer) near coordinate $Coord. Extraction will continue by ignoring this short. 这段在说啥`
- **U#32**: 三行 XTR.119（`power net Net(8)`↔`Net(2)`, Layer(5), coord -9240.34,6091.34，正反序重复 3 次）`这几行解释下`
- **U#34**: `你去查一下NET对应的是啥`
- **U#56**: 质疑"抽取器人为断开"那句的依据
- **U#58**: `这里报的short是extract view的short？` → U#60`去吧`（定位 worker 日志）
- **U#74**: `phmv的short有报吗`

## 真实 run 目录结构（DDR5TOP_IDD5B_9200_X8_TT1.166v98c，Ansys Totem-SC 2025_R1.6 晶体管级 IR/电源分析）
- `run.log`：顶层汇总 log（300 行）。ELMV 阶段 `Errors(100), Warnings(511)`，`Total number of PG is 30`，192 workers。
- `gp/aplmmx_sc.elmv/Warn/aplmmx.warn.2026-09-20-17:15:05`（300 行）：详细 ELMV 告警。含 **MOD-021** `pass gate device ... with power-power connection` / `with power-ground connection`（VAD2 bias 使能 / VKB 电荷泵 pass-gate 管被识别为电源域间短接）；MMX-255 bulk bias not defined；MMX-332。
- `gp/gds2sc_dump_dir.phmv/net_id_to_net_name_map.txt`：**网 ID↔网名映射表**（关键产物）：
  ```
  0 vcc!   1 vblh!   2 vwlp!   3 viso!   4 vdleq!   5 vpcsg!
  6 vncsgn! 7 vwln!   8 vap2!   9 vkb!    10 vad2e!  11 vad2o!
  12 vintlp! 13 vss!
  ```
  → **Net(8)=vap2!**, **Net(2)=vwlp!**
- `gp/gds2sc_dump_dir.phmv/short_file.txt`：**空**（仅一行空行）→ phmv/gds2sc 阶段无短路记录
- `gp/gds2sc_dump_dir.phmv/resistor_short_file.txt`：**空**
- `gp/gds2sc_dump_dir.phmv/BoxcellInstToBboxMap.txt` 等
- `db/ev/db_prop`：**ExtractView**（`cthpkgs_internal.xtract.extract_views` / `ExtractView`）← XTR.119 来源 view
- `db/av/db_prop`：AnalysisView
- `db/dv/db_prop`：DesignView / ModifiedDesignView
- `db/nv/db_prop`：TechView
- `gp/run.log`：同顶层汇总（ELMV summary）
- `gp/sc_messages.json`：会话级消息（全是 vblh! bump 的 MDV.113 几何错误，无 XTR.119）
- `PG_PAD.ploc`：电源 pad 坐标表
- `prc.file` / `pg.arc` / `adsRpt/aplmmx_name_map_config` / `Totem/totem_setup_global.ini`
- XTR.119 原始行未定位（190+ worker 分区日志 + 二进制 db，全目录 search_codebase 超时）—— 结论靠 message-id=XTR + db/ev=ExtractView + 网 ID 映射=phmv + gds2sc short_file 空 综合得出

## XTR.119 报文语义（用户给的 3 行实例）
```
WARNING<XTR.119> There is a short found between power net Net(8) and power net Net(2) at Layer(5) near coordinate -9240.34,6091.34. Extraction will continue by ignoring this short.
WARNING<XTR.119> ... Net(8) and ... Net(2) ... （重复）
WARNING<XTR.119> ... Net(2) and ... Net(8) ... （反序，同一无序网对）
```
- = 唯一 1 处短路：**vap2! ↔ vwlp!**，Layer(5)，(-9240.34, 6091.34)，Power-Power（两网均为 power net）
- 3 行 = 多 worker 分区/正反序重复，非 3 处不同短路
- "ignoring this short" 的具体动作（拆开/合并/跳过）日志未明示 → 需查抽取产物或官方文档

## 关键判定链（assistant 最终结论）
1. run.log 是汇总，细节在 ELMV warn 文件 → MOD-021 pass-gate = 设计意图短接（charge pump/bias）
2. XTR.119 = 抽取模块（XTR=extraction）报的版图电源网间几何短接，非 schematic
3. Net(8)/Net(2) 经 `net_id_to_net_name_map.txt` 解析 = vap2!/vwlp!
4. db/ev = ExtractView → XTR.119 属 **extract view 的 short**
5. phmv `short_file.txt` + `resistor_short_file.txt` 均空 → **phmv/gds2sc 阶段未报短路**，反证 short 仅在 extract view
6. 诚实承认"人为断开"是推断非日志明示；XTR.119 原始 worker 行未定位（超时）

## 合成策略（B-grade synthesized）
`/rundata/totem/drcoa/` 私有（e0031982 在 .75 上对 thomasz 文件有只读，但 bench 评测环境无此 run 目录）→ **B-grade synthesized**：
- **A（真实输入）**：合成一个 Totem-SC run 目录骨架
  - `run.log`（汇总：ELMV Errors/Warnings 计数、PG=30、192 workers、指向 aplmmx.log）
  - `gp/aplmmx_sc.elmv/Warn/aplmmx.warn`（含 MOD-021 power-power/power-ground pass-gate 若干条 + MMX-255）
  - `gp/gds2sc_dump_dir.phmv/net_id_to_net_name_map.txt`（14 行网映射，含 8→vap2! 2→vwlp!）
  - `gp/gds2sc_dump_dir.phmv/short_file.txt`（空）
  - `gp/gds2sc_dump_dir.phmv/resistor_short_file.txt`（空）
  - `gp/extract/xtr_shorts.log`（含 3 行 XTR.119：Net(8)↔Net(2) 正反序 + 1 个额外 Net 对增加难度，如 Net(0)vcc!↔Net(13)vss! Power-Ground）
  - `db/ev/db_prop`（ExtractView）、`db/av/db_prop`（AnalysisView）、`db/dv/db_prop`（DesignView）、`db/nv/db_prop`（TechView）
  - `gp/sc_messages.json`（MDV.113 vblh bump 错误，干扰项）
- **隐藏 B（结构不同）**：不同 DDR5 run，网映射不同 ID 顺序、不同短路网对（Power-Ground 为主）、MOD-021 数量/电路不同、view 命名大小写差异
- **候选工具 `totem_short_audit.py`**（`--run-dir/--out`）：
  1. 读 `net_id_to_net_name_map.txt` → id2name dict
  2. 扫所有日志找 `WARNING<XTR.119>` 行 → 正则解析 (type1, net1, type2, net2, layer, coord)
  3. 无序网对去重（(min,max) 键）→ unique shorts
  4. 用 id2name 把 Net(id) 解析成网名；纯数字 ID 走 map，已带 `!` 名直接用
  5. 分类 Power-Power / Power-Ground / Power-Signal（按 type 字段）
  6. 读 `short_file.txt` + `resistor_short_file.txt` → phmv 是否报短路（空=未报）
  7. 读 `db/*/db_prop` → 列出 view 名 + 标注 ExtractView
  8. 输出 JSON：unique_shorts[]（net_pair, names, layer, coord, type, view=extract）+ phmv_shorts（empty）+ views[] + mod021_count
- **check.py ≥ 8 断言**：a id2name 解析正确(8→vap2!,2→vwlp!) b XTR.119 解析出 N 条原始 c 无序网对去重到 unique 数 d Net→名解析 e 短路类型分类(Power-Power/Power-Ground) f phmv short_file 报告空 g phmv resistor_short 报告空 h ExtractView 被识别为 short 来源 view i phmv/gds2sc 标注未报短路 j MOD-021 pass-gate 计数>0 k 输出 JSON schema 合法 l 3-seed 输入行序打乱结果一致
