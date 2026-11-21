# 深读笔记 · 1795152225461_8igoq · GENGUI 工具包 provenance 分析

## trace_source
- session: `1795152225461_8igoq`
- user: `mingyu1l`  host: `hfeg0pkn005`  mc: 11  domain: spice_sim
- 扫描快照: `ssh_eda_search_20261121_005100/summary.tsv`（B shard keywords 过滤后）
- keywords: `hspice:18;netlist:9;.lef:8;verilog:2;mixed-signal:2;waveview:1;mosfet:1;cmos:1;`
- msgs: 11（user 6 / assistant 5），仅 1 条 user text msg
- ledger: r968 claim（2026-11-21）

## 用户原话（trace-faithful）
U[0]（唯一 user text msg，mode=plan）:
> `/proj/drvqa/V0/workdir/junlingw/GENGUI/`
> `kan kan zhe ge wen jian jia xia de jiao ben zai gan shen me`
> （看看这个文件夹下的脚本在干什么）

纯 code-comprehension / explain 任务。assistant 用 `list_allowed_files` 列目录 + 4 次 `read_files` 读 14 个文件后给出解释。**11-15 重审后合法**（analysis-Q&A / explain 类全部恢复可造）。

## GENGUI 工具包结构（14 文件，~1436 行，~90KB）

### 三段式组装器（builder_*→finesim_tb_generator.py）
| 脚本 | 行 | 作用 | OUT |
|:--|--:|:--|:--|
| `builder_p1.py` | 65 | 建 finesim_tb_generator.py Part1: header+engine setup（import fengine/fgrammar） | `finesim_tb_generator.py`（先 remove 再建） |
| `builder_p2.py` | 56 | 追加核心逻辑 Part2 | 同上（append） |
| `builder_p3.py` | 94 | 追加 tab builders Part3 | 同上（append） |

### 核心库（被 GUI import）
| 脚本 | 行 | 作用 | 关键定义 |
|:--|--:|:--|:--|
| `fgrammar.py` | 292 | FineSim/HSPICE Grammar Rules | `class G` |
| `fengine.py` | 173 | FineSim/HSPICE SPICE Netlist Generator Engine | `class TBGenerator` |

### GUI 入口（组装产物）
| 脚本 | 行 | 作用 | 关键 |
|:--|--:|:--|:--|
| `finesim_tb_generator.py` | 40 | FineSim SPICE Testbench Generator - 8-Tab GUI（tkinter） | `class App`，import G(fgrammar)+TBGenerator(fengine) |

### CLI .sp 生成器（独立，不依赖 GUI）
| 脚本 | 行 | 作用 | OUT |
|:--|--:|:--|:--|
| `gen_spice_tb.py` | 299 | 综合 G5 SPICE testbench（含 add_corner，多 corner） | `spice_testbench.sp` |
| `gen_spice_tb_v2.py` | 273 | G5 SPICE testbench v2（简化，无 corner） | `spice_testbench.sp`（覆盖） |
| `gen_tb.py` | 82 | 写 G5 testbench SPICE deck | `G5_testbench.sp` |

### 工具
| 脚本 | 行 | 作用 |
|:--|--:|:--|
| `check_all.py` | 29 | 全工程语法检查（import G/fgrammar） |
| `check_syntax.py` | 10 | 单独检查 finesim_tb_generator.py 语法 |
| `fix_indent.py` | 35 | 修 finesim_tb_generator.py 缩进 |

### 输出产物（已存在于目录，由 generator 写出）
- `spice_testbench.sp`（282L）— 由 gen_spice_tb.py / gen_spice_tb_v2.py 写
- `G5_testbench.sp`（74L）— 由 gen_tb.py 写

## 依赖图（关键判分锚点）
```
fgrammar.py (G) ─┐
                 ├─→ finesim_tb_generator.py (App, GUI)  ← builder_p1/p2/p3.py 组装
fengine.py (TBGenerator) ─┘

gen_spice_tb.py ──→ spice_testbench.sp
gen_spice_tb_v2.py ──→ spice_testbench.sp (覆盖)
gen_tb.py ──→ G5_testbench.sp

check_all.py ─→ fgrammar (G)
check_syntax.py ─→ finesim_tb_generator.py
fix_indent.py ─→ finesim_tb_generator.py
```

## 拟造任务形态
- **form**: analysis-Q&A code-comprehension（L1 离线 Python 解析），与 r967 XtalkDeepDfsProvenanceAnalyze-001 同 form（不同域内容：Python build-system provenance vs TCL deck provenance）
- **A 档 trace-faithful**: 用户原话「看看这个文件夹下的脚本在干什么」直进 prompt；14 个 GENGUI 文件作可见 A 资产（zip）
- **交付物**: `gengui_provenance.py` 通用 Python 工具包解析器 → 读 `spec.json` → 扫资产目录 → 写 `provenance.json`，含：
  - `files[]`: 每文件 {name, lines, docstring, classes[], defs[], out_targets[], local_imports[]}
  - `build_chain[]`: 三段式组装关系（builder_p1/p2/p3 → finesim_tb_generator.py，part 序号 + append/create 模式）
  - `entry_points[]`: GUI 入口（finesim_tb_generator.py:App）+ CLI 入口（gen_*.py）
  - `output_artifacts[]`: .sp 产物 ↔ generator 映射（spice_testbench.sp←gen_spice_tb.py/gen_spice_tb_v2.py；G5_testbench.sp←gen_tb.py）
  - `import_graph{}`: local import 边（fgrammar→finesim_tb_generator, fengine→finesim_tb_generator, G→check_all）
- **hidden B**: 由 A 经 `build_variant.py` 确定性派生 — 文件改名（builder_p1→asm_part1/fgrammar→spice_grammar/fengine→netlist_engine/App→GeneratorGUI）、函数/类重命名、行号平移；结构同构（3 builder→1 GUI, 2 lib, 3 gen→2 .sp），B 残留 A token=0 anti-hardcode-A
- **check.py ≥8 断言**（拟）:
  1. zip 含 N 文件齐全  2. py_compile 全过  3. run.sh exit 0 产 JSON  4. 顶层键齐全（files/build_chain/entry_points/output_artifacts/import_graph）  5. files 数量·名·行独立复算  6. build_chain 3 段（p1 create / p2 append / p3 append）目标同  7. entry_points 含 GUI(App)+3 CLI gen_*  8. output_artifacts 2 个 .sp + 各自 generator 独立复算  9. import_graph 边（fgrammar→gui, fengine→gui）独立复算  10. anti-hardcode-A 名不相交  11. 2 次确定性
- **k_rationale==k_check ≥8**（硬闸门）

## 资产访问 + 提取方法
- `/proj/drvqa/V0/workdir/junlingw/GENGUI/` 在 hfeg0pkn005 上对 e0031982 **Permission denied**（仅 mingyu1l 可读）
- **14 文件从 trace 的 read_files tool_result 完整可提取**（line-number prefix `  N | ` 须剥），原 trace 在 `hfeg0pkn005:/home/mingyu1l/.cline/data/sessions/1795152225461_8igoq/1795152225461_8igoq.messages.json`（124970B，11 msgs）
- 提取脚本（下一轮直接复用）：
  ```python
  import json,re,os
  d=json.load(open('8igoq.messages.json')); msgs=d['messages']
  usemap={}
  for m in msgs:
      if m.get('role')!='assistant': continue
      c=m.get('content')
      if not isinstance(c,list): continue
      for b in c:
          if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('name')=='read_files':
              usemap[b.get('id')]=[f.get('path') for f in b.get('input',{}).get('files',[])]
  for m in msgs:
      if m.get('role')!='user': continue
      c=m.get('content')
      if not isinstance(c,list): continue
      for b in c:
          if isinstance(b,dict) and b.get('type')=='tool_result' and b.get('tool_use_id') in usemap:
              items=b.get('content')  # list of {query, result}
              for it in items:
                  p=it['query'].split(':')[0]; raw=it['result']
                  lines=[re.sub(r'^\s*\d+\s*\|\s?','',ln) for ln in raw.split('\n')]
                  open('gengui/'+os.path.basename(p),'w').write('\n'.join(lines))
  ```
- 文件清单（14，~1436L / ~90KB）：builder_p1/p2/p3.py, fengine.py, fgrammar.py, finesim_tb_generator.py, gen_spice_tb.py, gen_spice_tb_v2.py, gen_tb.py, check_all.py, check_syntax.py, fix_indent.py, G5_testbench.sp, spice_testbench.sp

## DEBT
- **DEBT: 1 deepread 未合成**（r968 预算不足闭环，~8min 剩余不够走完 assets+reference+hidden B+negative+check.py≥8断言+自验+jsonl）
- 下一轮第一件事：取 `gengui/` 14 文件 → 合成 `EDA-Eval-DesignFlow-GenguiToolkitProvenanceAnalyze-001` → 自验 → 落 B.jsonl
- 模式修正印证 r966：低 mc 段（10-25）存在可造 analysis-Q&A 形态，与 high-mc fresh 难物化形成对照

## 同侪去重
- mingyu1l 在 B.jsonl 既无 case（grep mingyu1l = 0），无 near-dup 风险
- 域内相似 form: r967 XtalkDeepDfsProvenanceAnalyze-001（不同用户 siyuji / 不同工具包 xtalk.tcl）— form 同但内容正交
