# Deepread: 1794881626386_mmldo (yzwang@hfeg0pkn004, mc=99, layout_aether)

- user: yzwang (DRAM/物理版图工程师, fresh across all 4 shards)
- host: hfeg0pkn004 / 10.129.32.75-side ssh
- session: 1794881626386_mmldo (124 msgs / 612948 bytes, scp'd to .75 workdir)
- match_count: 99 (dbcreaterect/dbcreatepath/dbcreatelabel/pdk/dbcreatepolygon/gdsii/drc dominant)
- domain: layout_aether
- claimed: trace_ledger.py --shard C claim (r965)
- case: EDA-Eval-DesignFlow-PcellBorderEnclosureFix-001 (C.jsonl 599→600, k=16)

## 用户原始任务

> 我在/home/pdk/yzwang/06_AI_workspace/test12放置了一个gds文件和两个pcell文件，现在的问题是当参数设置成某一种形式时，生成的pattern超出了OPC02_mark1，请分析原因，并将其修复。

## 真实任务流（assistant 行为）

1. `list_allowed_files` /home/pdk/yzwang/06_AI_workspace/test12 → `BL_S_002_00.gds` + `oneOrTwoLayerSpaceFail.il` + `oneOrTwoLayerSpacePass.il`。
2. `read_files` 读两个 pcell IL（SKILL 风格，1400+ 行/文件），识别结构：`dbCreateRect`/`dbCreatePath`/`dbCreateLabel` 生成 layer 43/7 V1 pattern + layer 4001/51 highlight + layer 4002/51 recognition（= OPC02_mark1 whole-cell border）。文件末尾 `;to create the whole cell border` 段用 `borderTop`/`borderRight` 公式画 `lpprecognition` 整单元矩形。
3. 写 `/home/yzwang/gds_parse.py` 解析 GDS（struct/stream record 解析），多次 SIGKILL 超时（stdout 缓冲未 flush），加 `flush=True` + progress 后跑通：解码 UNITS（db_unit=1e-10），发现 GDS 里有顶层 + PASS cell（`oneOrTwoLayerSpacePass_*`）+ FAIL cell（`oneOrTwoLayerSpaceFail_*`）。
4. 实测外包框：FAIL cell pattern（43/7）最大 y=11067，OPC02_mark1（4002/51）border top 仅 8629 → **溢出 +2438**；PASS cell pattern 最大 y=10713，border top 仅 8274 → **溢出 +2439**。x 方向右侧够（47067 > 41700）。
5. 回溯 IL border 公式：`borderTop = basey + 3*1.5*layer1width + 3*layer2width + step`，`borderRight = basex + 6*1.5*layer1width + 6*layer2width + ...`。**根因**：margin 只挂钩 `layer1width/layer2width/step`（横向宽度），漏掉 pattern 沿 y 方向实际延伸（`layer1length/space/layer2length`），导致 recognition 矩形比 pattern 外包框小约 2400 单位。
6. 修复：写 fix 脚本，在两个 IL 的 border 公式补齐 `+ layer1length + space + layer2length`（borderTop 3 处 + borderRight 3 处/文件 = 6 行/文件）。脚本输出：`oneOrTwoLayerSpaceFail.il: changed lines=6, borderTop term in 3, borderRight term in 3`，corrected copies 落 `/home/yzwang/fixed_test12`。
7. 验证：`difflib.unified_diff` 确认仅 border 行改；括号平衡检查 `orig_paren_delta=0 fixed_paren_delta=0`（SKILL 语法未破坏）。原文件在 `/home/pdk/...`（agent 只读区），修复副本落自己 workspace。
8. 最终答案：原因分析表（fail/pass 溢出量）+ 根因（border 公式漏项）+ 修复（补 layer1length/space/layer2length）+ 验证（diff 干净 + 括号平衡）。

## 跨 shard 串台检查

- 4-shard ledger: yzwang 仅 C（本 claim）。
- 4-shard jsonl: 无 yzwang。
- 子型 `pcell_il_border_enclosure_fix`（pcell IL border 公式溢出修复）首例。

## 合成（reframe fixture-driven）

- 交付：`pcell_border_fixer.py`（Python3 标准库，离线），读简化 pcell IL（param 声明 + 4 条 border 赋值行 + dbcreaterect/dbcreatelabel/dbcreatepolygon 图案行），独立计算所有图案外包框，把 4 条 border 行改写为能完全包住所有 pattern 的值（四周留 margin），其余行原样保留，修正 IL 输出到 stdout。
- visible env_A (`pcell_OPC02_mark1_A.il`): basex=0/basey=0/patHeight=2400/patWidth=3200/bandHeight=200/margin=100，borderTop 漏 top band → 溢出 top 200。
- hidden env_B (`pcell_OPC02_mark1_B.il`): basex=500/basey=200/patHeight=1800/patWidth=3000/bandWidth=200/margin=150，borderRight 漏 right band → 溢出 right 200（不同侧/不同量）。
- check.py 16 条断言 (a-p)：zip 合法+含脚本 / py_compile / B 运行 exit0 非空 / 含 4 条 border 行 / 保留 dbcreate* 行数 / borderLeft≤minX / borderRight≥maxX / borderBottom≤minY / borderTop≥maxY / ≥1 border 改动 / B cell 名 / B≠A 输出 / 3-seed md5 一致 / 空zip FAIL / echo桩 FAIL / 硬编A桩 FAIL。
- reference_solution: `pcell_border_fixer.py`（安全 eval + IL 解析 + 外包框 + border 改写）。ref PASS 16/16。
- negative (4): neg_no_fix（原样输出）/ neg_hardcode_a（固定输出 A）/ neg_empty / neg_echo。selftest: ref PASS + 4 neg 全 FAIL。
- §4.9 degenerate（check.py 内建）: empty-zip / echo-stub / hardcode-A-stub，全 FAIL。
