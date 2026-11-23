# r1002 deepread: 1794820735285_q8bpv (yinyus@hfeg0plg58, mc=161)

## Trace
- user: yinyus (returning user — also built the skill in earlier session 3p4sb @ hfeg0plg67 r788), host: hfeg0plg58 (10.129.35.82), mc=161
- session: `1794820735285_q8bpv.messages.json`, 312 msgs
- domain: layout_aether (Aether schematic/symbol cellview 批量建实例+连线)
- kw: pyaether:n; dbOpenCV/dbCrtInst/dbCrtSchWire/dbNewCellView/emyDesignSave cluster

## Real task (organic, produce-task)
- yinyus 构建/迭代 `nicapblock-create` skill 位于 `/home/yinyus/.cline/skills/nicapblock-create/` (目录名 hyphen)
- skill 目的: 读严格 7 列 CSV (block,template,cell,params,spx,per_row,srow,sblock,origin), 按 per_row 个 cell 一行 / srow 行间距 / sblock block 间距, 调 pyAether API 批量在新建 schematic cellview 中摆放 instance (dbCrtInst) 并连线 (dbCrtSchWire)
- 示例 example_data.csv: 9 rows / 3 blocks, cell=TECHLIB/drcpa_analog + AG_CXcap 系列, params spx=1.5 per_row=10 srow=3.0 sblock=7.0 origin=(2,-1)
- 核心脚本: `scripts/nicap_block_create.py` (234 行)
- SKILL.md: 290 行 (完整工作流 + 表头校验 + symbol 存在性预检 + 9 陷阱表)
- pyAether API 调用面: dbOpenCV / dbCloseCV / dbCVExist / dbNewCellView / dbCrtInst / dbCrtSchWire / emyDesignSave / emyPointF
- 关键硬规则 (继承自 3p4sb): symbol 存在性检查 (dbCVExist) 必须在 dbNewCellView 之前, 避免建立残缺 cell; block 摆放 y 只减不增 (从上到下)

## SSH deepread (10.129.35.82)
- scp 抓取 skill script (234 行) + example_data.csv + SKILL.md (290 行) 全文
- 脚本结构: argparse → 读 CSV + TPL_HEADER 7 列严格校验 → 收集 I0/I1/I2 唯一 (lib,cell) → dbCVExist symbol 预检 → 按 (I0_lib,I0_cell,I1_lib,I1_cell) 归 block → 网格摆放数学 → dbNewCellView → dbCrtInst → dbCrtSchWire → emyDesignSave
- 规划段纯 stdlib 可离线验; 执行段需 live pyAether (SUT 不可达)

## parked
- fiknl (yh1yang@hfeg0pkn004 mc=154) — DUPLICATE of existing AetherSocketBridgeNav-001 (olgpe forked from fiknl; 同 pyAether socket-bridge nav task) — skip

## B档 reframe (offline-synthesizable, fixture-driven judge)
- live pyAether 不可移植 → reframe 为 B-synthesized fixture-driven judge
- agent 写 standalone solve.py (纯 stdlib + 延迟 `import pyAether`)
- check.py 内嵌 MOCK pyAether 模块 (dbOpenCV/dbCloseCV/dbCVExist/dbNewCellView/dbCrtInst/dbCrtSchWire/emyDesignSave/emyPointF 全部记录到 calls.json via atexit)
- A = real trace example_data.csv 9 rows/3 blocks 逐字保留 (TECHLIB/drcpa_analog + AG_CXcap2S199x128/223x80/295x176 + vcc/vwlp/vbn; spx=1.5 per_row=10 srow=3.0 sblock=7.0 origin=(2,-1))
- B = hidden synthesized 5 rows/2 blocks (BPWR/BCAP/BTmpl 模板 + vdd/vss/vdd2/vss2/BC1-5 目标 cell, template offsets 0/1/2, spx=2.0 per_row=4 srow=2.5 sblock=5.0 origin=(3,-2)) 与 A 全异
- A∩B 全异: cell 名 / block 数 / 行数 / 参数 / origin 全部不同 → 反硬编

## Case design (nicap_block_create_planner, k=15)
- CLI: `python3 solve.py <csv> <out_dir>`
- check.py 15 断言: ①zip含solve.py ②py_compile exit0 ③B exit0+生成calls.json ④solve.py 不 import pyAether(延迟加载) ⑤dbOpenCV==2 ⑥dbNewCellView==2 ⑦dbCrtInst==15(5行×3slot, 反A硬编) ⑧dbCrtSchWire==5 ⑨emyDesignSave==2 ⑩block0 首inst y==-2.0 ⑪block1 首inst y==-7.0 ⑫B inst cell 名属 B 期望集(与A全异) ⑬A demo inst==30 且 A≠B ⑭确定性 md5 一致 ⑮A-only cells {vcc,vwlp,vbn,AG_CXcap2S199x128,AG_CXcap2S223x80,AG_CXcap2S295x176} 在 B calls 中 0 次
- §4.9 三假: empty_shell / print_only / deleted_core (dbCrtInst=0) — all FAIL
- 3 extra negatives: hardcode_a (照抄 A cell 名), naive_stub (不调 dbCrtInst), always_pass (return True) — all FAIL
- Self-verify: reference solve.py PASS 15/15; 6 negatives all FAIL distinct; negative_selftest.py exit 0

## Decision
- A档自包含 (CSV + 纯 stdlib 规划), B档 disjoint anti-hardcode, k=15≥8, 6 neg (含 §4.9 三假) all FAIL distinct → quality gate met.
- task_id = EDA-Eval-DesignFlow-NicapBlockCreatePlanner-001
- 写入 cases/C/NicapBlockCreatePlanner-001.json (只写 cases/C/<id>.json, 不碰 *.jsonl)
- cases/C 580→581
