# trace deepread — sid 1790235198981_yku8k (xinqiaoz @ hfeg0pkn004, mc=219)

- **session**: /home/xinqiaoz/.cline/data/sessions/1790235198981_yku8k/1790235198981_yku8k.messages.json (599 KB, 163 msgs)
- **tools keyword**: `962 calibre` (pure calibre), `calibre:991;pdk:387;.gds:87;gdsii:29`
- **agent harness**: cline, raw `run_commands` 被禁用 → 用 `editor` 写约定文件 `SHELL_CMD_AGENT.txt`/`PYTHON_CMD_AGENT.txt` + `run_approved_command` profile `shell_generic_pdkqa`/`python_generic_pdkqa` 执行
- **domain**: physical_verify（Calibre DRC SVRF/TVF deck QA + PDK）
- **用户意图轮**（5 个真实意图轮，其余 continue/复制路径等）：
  - **U#0**：在 `/apps/imctf/develop/dummy/` 查找 Dummy 工艺配置文件（TVF），特征关键词组合 ≥3：`set TYPE_CMP[_RECT/_LINE]`、`set KEY_CMP/KEY_SOH/KEY_CELL`、`set obj_cmp/obj_soH`、`_Info`（set AT4_Info/PGZ_Info）、`set Bord`、`set PRECISION`、`source` 含 `init.tcl`。grep -rl 找候选 → 交集。
  - **U#56**：查找已从 TVF 转换生成的 SVRF 文件（`.svrf`/`.rule`，含 `LAYOUT PATH`+`LAYOUT PRIMARY`+`DFM SPEC FILL SHAPE`+`DFM FILL`，不含 tcl `proc`/`tvf::`/`upvar`，可含 `//` 注释）。
  - **U#80**：G5 节点 `calibreDummy_chip.rule` 太大无法完整复制，提取关键片段（sed -n 按行号）：a) 前 300 行 b) 第一个 `DFM SPEC FILL SHAPE` 行+100 c) 第一个 `= DFM FILL`+50 d) `DFM RDB|RULECHECK`+30 e) `EXT|WIDTH|AREA|ENCLOSE`+30 f) tail -50；统计 shape/spec/fill/SETLAYER 数；拼成带 `=== 标注 ===` 的文件。
  - **U#139/U#147**：把片段文件复制到 `.tmp`、`.tmp/g5_svrf_frags/`。
  - **U#153**（合成所取意图轮，唯一干净交付轮）：把 `.tmp/g5_svrf_frags/` 下 9 个片段文件合并成一个 Markdown。严格 A→B→C→D→E→F→G→H→I 顺序；每片段 `=== FRAG X: 说明 ===` 标头 + 空行 + ` ```svrf ` 代码块；若片段含 ` ``` ` 三反引号，外层用 `~~~` 包裹避免冲突；输出到 `g5_svrf_merged.md`；完成后报告文件大小+总行数。

## agent 真实工作（gold）

写 `/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/merge_fragments.py`（53 行，纯 stdlib）：
- 硬编码 `frag_dir` + `out_path` + 9 元组列表 `(filename, label)`（label 含中文，如 `FRAG A: 头部注释 + TYPE 声明`、`FRAG C: TVF→SVRF 过渡区`）
- 每片段：`out.write(f"=== {label} ===\n\n")` → 若 content 含 ` ``` ` 用 `~~~svrf`/`~~~` 否则 ` ```svrf `/` ``` `；content 不以 `\n` 结尾则补；块后空行
- 末尾统计 `total_lines = content.count("\n")`、`total_bytes = len(content.encode("utf-8"))`，print 三行
- 实跑结果：`g5_svrf_merged.md` 725 行 / 73386 字节 / 9 片段，exit 0
- USER 无追问 → 接受

## 失败模式（合成断言针对这些）
1. 硬编码 A 专属 token（xinqiaoz 路径 / 中文 label / frag_a_head80.txt / G5 / calibreDummy_chip）跨 bundle 穿透 → 跨输入守卫 B2（不同 deck，英文 label）必须不含 A 专属 token
2. 顺序错乱（未按 A→I 严格单调）
3. 围栏不配对（```svrf 开 vs ``` 闭 / ~~~ 配对数错）
4. 片段含 ``` 时未切 ~~~ → 外层被破坏
5. 行数/字节统计与实际文件不符
6. 缺片段文件仍写输出 / 坏 bundle 不退出
7. 非确定性（路径混入 stdout / 输出含时间戳）

## 合成决策
- **B-档 synthesized**（U#153 用户已把交付格式写得很具体 → 取离线可计算核心，泛化为 bundle-driven：frag_dir + ordered fragments[(file,label)] + output + fence_lang）
- **L1-boundary**（纯文本合并，不真跑 Calibre；但 seed 真实来自 calibre SVRF QA，physical_verify 域）
- **gold**: `svrf_frag_merger_ref.py`（CLI `<bundle.json> [--out PATH]`，读 bundle{frag_dir,output?,fence_lang?,fragments:[{file,label}]}，泛化 ~~~ fallback + 行/字节统计 + 缺文件/坏 bundle exit1+stderr）
- **判分**: check.py 在 3 隐藏 B（B1 干净 9 片段 / B2 跨输入守卫不同 deck 英文 label / B3 边界含 ``` 片段+缺文件）subprocess 真跑 SUT，静态解析输出 .md
- k=15 (a-o)
