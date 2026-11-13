# Deepread: fj41f (jerrychu) — STC Characterization Request Form Generator

**Session**: 1794463632688_fj41f · **User**: jerrychu · **Host**: 10.129.2.12 · **mc**: 110
**Domain**: characterization · **Archetype**: produce-task (doc-generation from structured input lists)
**Trace source**: real_task_summary = "Generate STC Characterization Request Form from INPUT directory"

## 1. 用户意图（原话）

msg[0]: `/proj/lacaa/TV1_DBC/workdir/jerrychu/STC/INPUT`
msg[6]: `The directory contain all inputs information for STC characterization. I need a characterization request form which including all items under the directory.`

jerrychu 要求：读 STC INPUT 目录下的所有输入文件，生成一份完整的 STC 表征请求单（CRF），把目录里所有 items 都包含进去。

## 2. INPUT 目录 8 个文件（真实内容）

| 文件 | 内容 | 行数 |
|---|---|---|
| `00_name.tab` | 命名模板 `v[yyyymmdd]_stc[0904]_pex[1030]_spice[V0d1Rev05]` | 1 |
| `01_stc.list` | 3 个 VT 库（LVT/SVT/ULVT）+ 路径 | 3 |
| `02_pex.list` | 2 条 PEX 抽取路径（FS + DBC，GloryEX 9Corner） | 2 |
| `03_spice_model.list` | hspice model.lib 路径 | 1 |
| `04_model_corner.list` | 24 个 model corner（12 _dbc + 12 _fs varactor） | 24 |
| `05_pvt.list` | 16 个 PVT 条件（ssgnp/ffgnp/tt × V × T） | 16 |
| `06_rel.list` | release 目标目录 | 1 |
| `07_cell.list` | 22 个 cell（9 BUFFD + 7 CKBD + 4 DCCKBD，空行分组） | 22 |

## 3. assistant 工具链

1. `list_allowed_files` INPUT 目录 → 发现 8 个文件
2. `read_files` 全部 8 个 INPUT 文件 → 逐文件解析
3. `list_allowed_files` STC/ 上级目录、LPE/、20261020/ → 找参考格式
4. `read_files` LPE/lacaa_pex_config.json + corner_file → PEX 工具配置
5. `editor` 写 STC_Characterization_Request_Form.md（因 policy 改写到 /home/jerrychu/）
6. 多轮 editor insert_line 分段追加（文件太大一次性写不下）
7. 后期改写 Python 生成器 `gen_crf.py`（msg[49]）— 程序化生成

## 4. 最终 CRF 结构（12 节）

- §1 Request Overview（project / date / naming template 4 段解码 / release target / requester）
- §2 Library Information（VT flavors 表 + 库名段解码 + cells×VT 总数）
- §3 Cell List（22 cells 分组：9 BUFFD + 7 CKBD + 4 DCCKBD）
- §4 PEX Configuration（GloryEX / RC mode / 9Corner / FS+DBC 路径）
- §5 SPICE Model（model.lib 路径 + 版本 V0d1Rev05）
- §6 Model Corners（24 corners，DBC 12 + FS 12）
- §7 PVT Operating Conditions（16 条件矩阵：corner/V/T）
- §8 Characterization Matrix Summary（cells × VT × PVT 算术）
- §9 Release Target
- §10 Input File Mapping（哪个文件 → 哪节）
- §11 Notes & Assumptions
- §12 Revision History

## 5. case 化决策

**A 档 trace-faithful → 便携 L2**：
- 8 个 INPUT 文件均为文本 list/tab，无需 EDA license → 便携
- 核心能力 = 解析 8 种结构化输入 + 聚合成完整 CRF markdown
- A（SUT 可见）= 真实 INPUT 8 文件（jerrychu 原值）
- B（隐藏）= 不同 project/VT 数/cell/corner/PVT/PEX/命名模板，结构同构但取值不同
- 判分 = subprocess 跑候选 gen_crf.py 在 B 的 INPUT 上 + 解析输出 markdown + 逐条断言
- **不依赖 LPE/ 外部目录**（PEX 配置从 02_pex.list 路径提取 GloryEX/Corner 数/日期，自包含）
- cross-input guard：在 A 上重跑抓写死

## 6. 断言清单（k=14）

① CRF 非空且含顶层标题 "Characterization Request Form"
② §1 project 名正确（从 B 路径解析）
③ §1 naming template 4 段全解码（v/stc/pex/spice tag 值对）
④ §2 VT flavors 数量 = B 的 01_stc.list 行数 + 全部 VT 名出现
⑤ §2 库名解码 ≥3 段
⑥ §3 cell 总数 = B 的 07_cell.list 非空行数
⑦ §3 全部 cell 名出现（子集校验）
⑧ §3 cell 分组数正确（BUFFD/INV/NAND2 组计数）
⑨ §4 PEX 工具名(GloryEX) + corner 数（从路径 7Corner 提取）
⑩ §5 SPICE model 路径出现
⑪ §6 model corner 总数 = B 的 04 行数 + DBC/FS 拆分对
⑫ §7 PVT 总数 = B 的 05 行数
⑬ §7 PVT 逐条解析 corner/V/T（抽查 3 条）
⑭ cross-input guard：A 上重跑输出 ≠ B（非写死）
