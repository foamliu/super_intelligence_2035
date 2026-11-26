# trace deepread — 1791861649073_wj4ab (kenwang / hfeg0pkn005 / mc253)

- session: `/home/kenwang/.cline/data/sessions/1791861649073_wj4ab/1791861649073_wj4ab.messages.json` (3.03MB / 342 msgs: 189 user / 153 assistant), cwd `/home/kenwang/zl`, model deepseek-v4-flash, 2026-10-13 ~ 2026-10-30, completed.
- domain: Calibre DRC 自动化（pnr_signoff）；工具分布 calibre:65 + innovus:2 + hspice/spectre/virtuoso 少量。
- 会话主线：用户 kenwang 围绕 `/rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/` 下 drc_auto.py（Calibre DRC rule deck 自动渲染驱动脚本）反复调试，跨多个子目录 test_0/test_1/test_2/V05_coding_rebuild/share 等。

## 各用户轮性质（A-档选料）
- [0] **提需求轮（A-档选用）**：报 `Fatal Python error: initfsencoding / ModuleNotFoundError: No module named 'encodings'` + `./ts_auto.sh: line 8: ... Aborted (core dumped) ./drc_auto.py main.rule 18 18 ...`，问「drc_auto.py 中需要调整一下 load Python 的版本，请参考 .bashrc 文件应该如何修改呢」。**仅复述工具报错+问如何改 Python 版本，未给根因/修复 → 规则②不命中 → A-faithful 干净**。
- [14] 新错（`from: command not found` / `import: unable to grab mouse`）—— 系用户应用 [0] 修复后 sed 残留首行 `###!/apps/local/bin/python3` 致内核未识别 shebang 当 bash 执行；非本轮任务（[0] 修复已生效的铁证）。
- [20] GLIBC 版本不匹配（删后报错）；[44]/[55]/[79]/[81]/[87]/[94]/[104]/[112]/[115]/[117]/[135]/[145] render_block eval 语法/KeyError $<yx_start>；[149] MASK connectivity MOM_M13s；[167] EXT3 line 78149；[197]/[206]/[212] 对照 design rule 检查新开发的 drc code；[221]/[226] Degenerate boundary；[228]/[255]/[278]/[316]/[318] SAQP_M1.rules rule 开发（按 ev 参考 + drc 文件 layer 名整合）。**这些轮多为「贴新报错」或「给修复/给约束」，规则②多命中或非提需求轮，不选 A 档。**

## 金标（trace [8] + [13] 助手诊断，用户应用后 [14] 出新错 = 修复生效）
- **根因**：`drc_auto.py` shebang 硬编码 `#!/apps/local/bin/python3`（Python 3.7 二进制）；`.bashrc` 执行 `module switch python/3.11.9`，把 `PYTHONHOME`/`PYTHONPATH`/`LD_LIBRARY_PATH` 指向 Python 3.11.9 的 stdlib 路径。运行 `./drc_auto.py` 时内核按 shebang 启动 3.7，3.7 初始化查找自己的 `encodings` 模块，但环境变量被 module 改写指向 3.11.9 stdlib → 3.7 找不到 `encodings` → `Fatal Python error: initfsencoding` 崩溃。
- **修复**：将 shebang 改写为 `#!/usr/bin/env python3`，使其跟随 PATH 中 module 加载后的 python3（=3.11.9），统一解释器与 PYTHONHOME/PYTHONPATH，消除 encodings 启动致命错。助手给出 `sed -i '1s|#!/apps/local/bin/python3|#!/usr/bin/env python3|' ...`。
- **备选**（不采为金标）：保留 shebang 但在 ts_auto.sh 调用前 `unset PYTHONHOME PYTHONPATH` + 显式 `python3 drc_auto.py ...`。

## 资产合成（真实 /rundata permission-denied → 合成 fixture 忠实复刻结构）
- A = prompt.txt（[0] 逐字原文）+ task_brief.md（3 行接口）+ drc_auto_A.py（shebang `#!/apps/local/bin/python3` + 忠实复刻 trace 结构：parse_args/render_template/render_block/COMMENT_FILE_CACHE/EV_VARS/main，含 eval cond 渲染）+ .bashrc_A（含 `module switch python/3.11.9` + module load + PATH/LD_LIBRARY_PATH）。
- hidden B = drc_auto_B.py（不同硬编码 shebang `#!/usr/bin/python3.6`）+ .bashrc_B（`module switch python/3.8.10`，不同 module 组合）+ hidden_manifest.json。B 测试泛化：候选须从 .bashrc 读 module python 版本（3.8.10 ≠ A 的 3.11.9），须改写任意绝对路径 python shebang 为 env 形式，不得硬编码 A 专属字面量。

## 交付件 = fix_shebang.py + diagnose.json
- gold fix_shebang.py（纯 stdlib；CLI `python3 fix_shebang.py <drc_auto_py> <bashrc> <output_py>`）：regex `module\s+(?:switch|load)\s+python/(\d+\.\d+(?:\.\d+)?)` 提版本；regex `^#!\s*(/\S*python\d[\w.\-]*)\s*$` 识别硬编码绝对 shebang → 改写为 `#!/usr/bin/env python3`，正文逐行保留；diagnose.json 含 root_cause/shebang_before/shebang_after/module_python_version/env_vars_conflict/fix_summary。源码 0 A/B 专属字面量。

## check.py = 15 条独立断言 (a)-(o)
ref PASS 15/15；4 negative（fake_empty→(a) / fake_print_expected→(n) / fake_core_deleted→(d) / naive_stub→(m)）全 FAIL；§4.9 (a)空壳(b)print期望(c)删核心 三假覆盖。k_rationale=15=k_check=15≥8 GATE PASS ✓。

## 难度评估
L2（subprocess 在 A+B fixture 上跑候选 fix_shebang.py，§4.2 结构判分；Calibre 二进制不参与=静态 shebang/bashrc 结构判分）。A-faithful 真实难度 = 模型须从 verbatim 报错+问句推断：①读懂 shebang 硬编码绝对路径 vs .bashrc module switch python/<ver> 的环境冲突；②定位根因 = PYTHONHOME/PYTHONPATH 被改写致 encodings 启动致命错（非 GLIBC/非权限）；③写 fix.py 从 .bashrc regex 提版本 + 改写 shebang + 保留正文 + 6 键 diagnose；④泛化到隐藏 B（不同 shebang 绝对路径 / 不同 module 版本 3.8.10，不得硬编码 3.11.9/ /apps/local/bin/python3）。预期 ≤10% pass（A-档目标）。
