# r542 deepread — 1794396010329_k7jjm (xxchen @ hfeg0pkn001/10.129.2.10)

- mc=322, keywords: drc:1350/.gds:489/pex:5/aether:5/rtl:1/pdk:1/lvs:1/gdsii:1, tools: 1 dbCreatePath
- domain: physical_verify (DRC QA pattern deck generator, gdspy-based)
- 215 msgs (archive JSONL + current dict), 1.1MB current + 3.1MB archive

## USER 轮（3 轮，A档资格判定）
- USER#1 (i=2): "Context summary" 续传（非 fresh produce-task），描述已完成工作 + goal "将 excludeRegion 泛化为全 function 统一机制...exempt 作为独立第二行(Y堆叠)..."
- USER#2 (i=3): `<user_input>` "### QA pattern debug: DNW_F_012_00 ... excludeRegion 为什么没有生效" — Q&A/debug 提问
- USER#3 (i=141): `<user_input>` "问题：excludeRegion 这里的 good 生成的 exclude pattern 把所有的 excludeRegion都堆叠在了一起...需要的是 ESD 带上一组 bad Pattern 占据一行; DCSCR 覆盖上一组bad pattern 占据下一行; X_DEC 覆盖上一组bad pattern 占据下一行。"

### A档资格
USER#3 同时描述了**症状**("全堆一起") + **修复方案**("每个 region 独占一行 Y 堆叠")→ 属"给出修复方案"轮 → **不合格 A档** → 用 **B档 synthesized**。

## assistant 工具链
tools: read_files:24, run_approved_command:39, editor:38, list_allowed_files:5, get_agent_policy_status:1, ask_question:1
- 诊断阶段(i=42-121): 读 GDS/log，发现 user 看的是陈旧 QA_DNW.gds(11-09, 早于 11-11 泛化)→ 工具侧实际生效
- 重构阶段(i=152-185): editor 写 rewrite_exempt.py → 替换 pattern_common.py 的 exempt pass 为 ONE ROW PER REGION
- 验证阶段(i=185-195): verify_rows_new.py 读 GDS cell origin + 层统计; check_logs_new.py 查 ERROR/WARNING

## 核心算法 (ONE ROW PER EXCLUDE REGION) — pattern_common.py exempt pass
GOOD cell 有 `{excludeRegion ESD,DCSCR,X_DEC}` → 每个 region 独占一行 Y-stacked 在 good 行下方:
- region_pairs = [(304,50),(304,67),(302,56)] (marker layers, config order)
- region_names = ["ESD","DCSCR","X_DEC"], region_specs=["RLESD;mark0","RLESD;mark17","RLDEV;mark6"]
- Pass A: 每 region 渲染 bad patterns 为 exempt temp cells (no placement), 只用该 region 的 marker layer 覆盖
- Pass B: 每 region Y 下移排版成独立行, 行内 X 递增; cell 名 `..._p<N>_exempt_<REG>`; label `except <REG> (<spec>) <N>`; 无 error mark (4001;51)

## 实测几何 (verify_rows_new.py, DNW_F_012_00)
- good row y=0
- ESD row y≈-32.2 (7 bad patterns × marker (304,50))
- DCSCR row y≈-61.8 (7 × (304,67))
- X_DEC row y≈-91.4 (7 × (302,56))
- 行距 pitch=29.6, 首行 offset=32.2 (good_row_y - 32.2, 后续 -29.6)
- 单 region (PW_S_016_00 SA): 1 row y≈-39 (7× (302,51))
- log: "excludeRegion 'ESD,DCSCR,X_DEC': 3 region row(s) x 7 bad pattern(s)"

## case 合成方向 (B档, physical_verify, L2-boundary)
**ExcludeRegionRowLayout-001**: 把"live gdspy QA pattern 生成"重构为"读 config.json fixture → 算 excludeRegion 逐 region Y 行布局 → 输出 layout.json"离线可判(核心 ONE ROW PER REGION 算法不变)。
- 交付: exclude_region_row_layout.py
- B: 3 regions (ESD/DCSCR/X_DEC) × 7 bad + 2 good (faithful to DNW_F_012_00)
- B2: 1 region (SA) × 5 bad + 1 good (faithful to PW_S_016_00 单 region)
- 边界: 0 regions → 0 exempt rows
- 16 条件 a-p: 结构2 + B 8(good行/exempt行数/Y堆叠/bad数/marker层唯一/cell名/label/无error层) + B2 3 + 防硬编2 + 空区1 + 确定性1 + 行序1 - 收敛16

## 谱系
produce-task 第十子型 exclude-region-row-layout (判分 code-execution-validation 承 r541 label-flatten), anti-hardcode dual-hidden-config(B+B2).
