# Deepread: 1795410189347_amn6z (e0039786 @ hfhds201) — layout_virtuoso

## 会话元数据
- session_file: `1795410189347_amn6z.messages.json` (239 msgs, 1.2MB)
- user: e0039786, host: hfhds201, match_count: 292
- cwd: `/proj/lacaa/TV1_FS_Virtuoso/agentdir/e0039786` (= `/ai_sandbox/lacaa/TV1_FS_Virtuoso/agentdir/e0039786` via different mount; Permission-denied to e0031982)
- domain: layout_virtuoso (keywords: dbcreaterect:1724;drc:1499;virtuoso:1451;calibre:286;cellview:254;dbopencellviewbytype:74;.gds:69;ddgetobj:63)
- 关键词 drc 高是因为 session 后段（MSG 39+）转入另一个 BORD/layermap 子任务；前段（MSG 0-38）是核心 layout 任务。

## 真实任务（MSG 0 user_input）
> 使用路径 /proj/lacaa/TV1_FS_Virtuoso/agentdir/e0039786 的 skill，生成一个新的电路

skill = `PARA_inverter_array.il`，已生成过：
- `PARA_emit_n2.il` (n=2, drive x2)
- `PARA_inverter_D4x4_circuit.il` (n=4, drive x4)

agent 取 n=8 (drive x8)，输出 `PARA_inverter_D4x8_circuit.il`。

## skill 核心逻辑（MSG 36 最终自测代码全文提取）

### paraCellPitch / paraCellCatalog
- `paraCellPitch()` = `0.255`
- `paraCellCatalog()` = 75 条矩形 `[layer, x1, y1, x2, y2]`（单元内坐标，um）。
  层种类：MGC, M1, V0R, GT, M0C, M0, V0G, GFW35, V0D, AMN, AA, DEV, BORD, CM1B, CM1A, SDB, VT, PSR, NSR, NW。
  关键索引（agent MSG 23 确认）：CATN=75, idxDEV=65, idxVDD=29, idxGND=35。
  - idxVDD=29: `M1 0.046500 0.218300 0.301500 0.268300`（全宽 VDD bar，width=0.255>0.24）
  - idxGND=35: `M1 0.046500 0.014300 0.301500 0.064300`（全宽 GND bar）
  - idxDEV=65: `DEV 0.046500 0.039300 0.301500 0.243300`（单元边界框）

### paraPlace(n ox oy sx sy)
```
for k in 0..n-1:
  dx = k * pitch
  for r in catalog:
    placed = [layer, ox+sx*(x1+dx), oy+sy*y1, ox+sx*(x2+dx), oy+sy*y2]
```
返回 n*75 条，stage 0 在前，每 stage 内 catalog 顺序不变。

### paraVerify(n ox oy sx sy) — bug 修复核心
- 非退化：每条 placed 矩形 x2>x1 且 y2>y1
- 相邻 stage DEV/VDD/GND x 首尾相接

**原 bug**（MSG 13/18 之前）：用严格 `!=` 比较 → n=8 时 `k*0.255` 浮点累加致 `pdev.x2 != ndev.x1`，paraVerify(8) 误报 `FAIL n=8`（几何上其实相接，MSG 25 打印所有边界连续）。

**修复**（MSG 29 最终）：用容差 `abs(a-b) > eps`（eps=1e-6）代替严格 `!=`。修复后：
- `PASS n=8 rects=600`
- `PASS n=1 rects=75`（边界 n=1）
- `PASS n=8 rects=600`（带平移缩放 paraVerify(8, 10.0, -5.0, 2.0, 3.0)）
- `array span x=[0.0465..2.0865]`（MSG 37）

## agent 工具链
list_allowed_files → read_files (PARA_emit_n2.il / PARA_inverter_array.il / SKILL.md) → skills(eda_agent) → editor(get-username.sh) → run_approved_command → SandBox_MCP_Server__run_code (多次 inline SKILL 执行 + paraVerify 调试) → editor(PARA_inverter_D4x8_circuit.il 写盘) → read_files(核对) → run_approved_command(cleanup.sh) → list_allowed_files(确认交付)

## 合成的 case
**EDA-Eval-DesignFlow-ParaInverterArrayPlace-001** (layout_virtuoso / parametric_inverter_array_place):
- 离线 Python 版本（pyAether/Virtuoso 沙盒不可达 + 源目录 Permission-denied，但 catalog 全文从 trace MSG 36 提取，可离线合成）
- SUT 交付 `para_build.py`：读 catalog.json + config.json，输出 placement JSON（rects + verify + span_x）
- 公开 config_a: n=8, ox=0, oy=0, sx=1, sy=1（trace 真实 D4x8 配置）
- 隐藏 config_b: n=6, ox=1.5, oy=-2, sx=1, sy=1（主判分）
- 隐藏 config_c: n=12, ox=10, oy=5, sx=2, sy=3（cross-input anti-hardcode guard，带缩放）
- k=16 全闸门通过：① negative_selftest.py exit0 (ref PASS 16/16 + 4neg 全 FAIL distinct: empty[cond1]/print_only[cond3]/hardcode_a[cond12+cond15]/delete_core[cond14]) ② §4.9 三假 (a)空壳empty[cond1] + (b)只print print_only[cond3] + (c)删核心 delete_core[cond14] 全 FAIL ③ §4.6 k一致: k_rationale=16==k_check=16==test_rationale ①-⑯ ④ §4.2 真跑: subprocess 候选 para_build.py on hidden config_b+config_c, check.py 内独立复算 place 公式 + DEV/VDD/GND 连续性断言 ⑤ §4.1 hidden B+C: assets/.../hidden/config_b+config_c 不进 SUT 沙箱(attachments 只含 catalog/config_a/task_brief), B/C 与 A 在 n/ox/oy/sx/sy 全不同 ⑥ §4.5 反硬编: cond15 cross-input guard, 候选须在 C 上算 n=12 的 placement; hardcode_a(硬编 n=8) on B cond4 fail(rect 600!=450) + on C cond12 fail(600!=900) ⑦ §4.7 独立临时目录: tempfile.mkdtemp + shutil.rmtree finally ⑧ §4.8 泄漏隔离: SUT 沙箱=cases/C/...json+assets(catalog/config_a/task_brief), 不含 reference/check.py/negatives/hidden ⑨ §4.3 randomization: cond16 3-seed 决定性, config_b 连跑 3 次输出 byte-identical
- **关键设计点**: 容差 eps=1e-6 是判分核心 —— delete_core(保留严格 !=) 在 n=12(config_c) 必 FAIL cond14（n=12 浮点累加足够大触发严格不等）；ref 用 eps 全 PASS
- **end-to-end 验证**: 从 case JSON 提取 test 跑 check.py，ref solve.py PASS + 4 neg 全 FAIL；ref 在 config_a 上输出 rects=600 verify=PASS span_x=[0.0465, 2.0865] 与 trace MSG 37 完全一致

## 与现有 C 域 case 的区别
- 与 CalibreDrcRunsetPatch-001(r1035): Calibre runset 字段补丁 vs Virtuoso 参数化版图 place+verify，产物/断言/trace 全不同
- 与 V4PatchMultiRuleSkip-001(r1026): V4 几何 patch 多规则过滤 vs 反相器阵列 place+连续性校验，算法/产物/trace 全不同
- 与 AutoPlacementStep3-001(r1028): pg_layout 自动放置 step3 vs layout_virtuoso 参数化反相器阵列，domain/产物/trace 全不同
- 与 AetherHiliteCmd-001(r1030): Aether socket hilite 命令 vs Virtuoso SKILL place+verify，平台/产物/trace 全不同
- C 域 layout_virtuoso 子型首例（parametric_inverter_array_place）
