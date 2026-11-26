# 深读笔记 · 20qq6 · yohannw @ hfeg0pnd001 · layout_virtuoso bridge rename-and-port

**Session**: `1794736845081_20qq6.messages.json` (308KB / 115 msgs: 64 user / 51 assistant)
**User**: yohannw @ hfeg0pnd001 (10.129.32.189) · mc=209 · keywords `virtuoso:551;pyaether:1`
**Domain**: layout_virtuoso (SKILL/Virtuoso bridge tooling maintenance)
**Selected**: r714 (shard C), fresh-filter (mc≥10, C-keyword, 4-shard ledger union dedup), top-1 candidate
**Trace source path**: `/home/yohannw/.cline/data/sessions/1794736845081_20qq6/1794736845081_20qq6.messages.json` on hfeg0pnd001

## 真实用户意图（逐字）

**U#0**（提出需求）:
> `/home/yohannw/workdir_26Q4/1115_virtuoso_bridge_fix_roy目录下，搞清楚这三个程序的调用关系，我需要更名移植到其他地方`
> `server.py    start_server.sh    zl_eda_virtuoso.il`

**U#6**（明确更名 + 内部调用同步）:
> `更名：server.py：CXMT_zhulong_EDAAgent_Server.py`
> ` start_server.sh： CXMT_zhulong_EDAAgent_Server.sh`
> ` zl_eda_virtuoso.il： CXMT_zhulong_EDAAgent.il`
> `需要注意内部调用的名称调整`

后续轮（U#101/U#103/U#111）是比对 `.bak` 发布版与当前 `.il` 的差异 + 解读 `checkWhitelist` + 找其他差异（prose Q&A，非本轮 reframe 主料）。

## cline agent 工具链（51 assistant turns）

1. `list_allowed_files` `/home/yohannw/workdir_26Q4/1115_virtuoso_bridge_fix_roy` → 列出 7 文件（3 源 + .bak + CXMT_ 已存在的发布版）
2. `read_files` 三个源文件多段（server.py 1-30 / start_server.sh 1-15 / zl_eda_virtuoso.il 多段）→ 搞清调用关系：
   - `zl_eda_virtuoso.il` 的 `LAUNCH_SCRIPT` 指向 `start_server.sh`
   - `start_server.sh` 的 `SERVER_SCRIPT` / `FALLBACK` 指向 `server.py`
   - `server.py` docstring + `SERVER_NAME` 自引用
3. `editor` 多轮 edit（≥10 次）逐处替换内部引用：
   - start_server.sh: `SERVER_SCRIPT=...server.py` → `...CXMT_zhulong_EDAAgent_Server.py`；`FALLBACK=.../server.py` → 同；comment + error msg
   - zl_eda_virtuoso.il: `LAUNCH_SCRIPT = ".../start_server.sh"` → `.../CXMT_zhulong_EDAAgent_Server.sh`；fallback `strcat`；comment
   - server.py: docstring `[server.py]` → `[CXMT_zhulong_EDAAgent_Server.py]`；`SERVER_NAME`；usage 示例
   - 多次 editor "No replacement performed"（已替换/大小写不匹配）→ retry
4. `run_approved_command` 写 `_do_rename.py`（python `os.rename` 3 文件）+ run → 输出 "Renamed: server.py -> CXMT_zhulong_EDAAgent_Server.py" 等 3 行
5. `run_approved_command` 写 `__cleanup.py` 删 `_do_rename.py`（destructive classification）
6. `read_files` 验证改后内容（CXMT_zhulong_EDAAgent_Server.py:1-35 等）
7. 后续 Q&A：`read_files` `.bak` 对比 `checkWhitelist` procedure（whitelist 文件读取 + 用户匹配 + hiDisplayAppDBox 拒绝框）+ 找其他差异

**关键产物**：3 个更名后的文件（CXMT_zhulong_EDAAgent_Server.py / .sh / CXMT_zhulong_EDAAgent.il），内部引用全部同步更新。

## 调用关系图（真实 3 文件 bridge）

```
zl_eda_virtuoso.il  ──LAUNCH_SCRIPT──>  start_server.sh  ──SERVER_SCRIPT/FALLBACK──>  server.py
      (.il SKILL)                          (.sh wrapper)                              (.py TCP server)
   ipcBeginProcess                       exec python                          socket + stdin/stdout
   "bash " LAUNCH_SCRIPT                 "$SERVER_SCRIPT"                     child of SKILL
```

每个文件都在 content 里以字符串/注释/路径拼接形式引用了其他文件的 basename（及自引用）。

## reframe（mock-behavioral 家族 r645-r713 · 新子型 `cross-file-rename-port-reference-rewrite`）

**真实 trace 是 FS 重命名 + 多文件 edit**（path-dependent：需 ssh 到 yohannw 主机、读真实文件、跑 python os.rename）。reframe 为**纯 stdlib produce task**：

- 输入：`<bridge_dir>` 含若干源文件（.py/.sh/.il 任选）+ `rename_map.json`（旧 basename → 新 basename）
- 输出：JSON 描述
  1. `files`（排序文件名列表）
  2. `rename_map`（回显输入映射）
  3. `call_graph`（每文件 → 它引用的旧 basename 已排序去重列表）
  4. `references`（每文件 → `[{line, col, old}]` 逐处定位）
  5. `rewritten_files`（每文件 → 旧名替换为新名后的内容，键沿用原文件名）
  6. `stale_check`（每文件 → 替换后仍残留的旧 basename 列表，应全空）
  7. `summary`（file_count / total_references / rewritten_count / stale_found / all_renamed）
- 确定性：`sort_keys=True`

**distinct vs r713 NwDerivedLayerRuleExtract=DRC SVRF deck 派生层闭包 / r711 SkillPatternDecoordinate=SKILL .il 去坐标参数化 / r710 DrcRunStatusAnalyze=DRC log 解析** = 本例 **多文件 cross-file 引用定位 + 改写 + 残留校验**（新子型）。

## 11-15 task初衷 B类复活

U#0/U#6 本质是「重构/移植」类任务（rename + internal reference sync），旧规则可能判 refactor/Config 类 weak。按新标准 refactor/port 是真实用户意图 → 合法 reframe-for-teeth（trace agent 有真实 FS 交付，reframe 为给 check() 牙齿做成纯 stdlib compute）。

## asset / hidden / check 设计

- **asset A (visible)**：`server.py` / `start_server.sh` / `zl_eda_virtuoso.il`（微型版，结构同真实 trace，行数缩小）+ `rename_map.json`（A 映射）+ prompt.txt（U#0+U#6 逐字）+ task_brief.md
- **hidden B (反 A)**：`bridge_core.py` / `run_bridge.sh` / `skill_iface.il` + `rename_map_B.json`（旧/新 basename 全异 A：bridge_core.py→ZL_Bridge_Core.py / run_bridge.sh→ZL_Bridge_Launch.sh / skill_iface.il→ZL_Bridge_SKILL.il；路径全异 `/nasdata/zl/sandbox/` vs A 的 `/nasdata/app.e0047722/eda_sandbox/eda_virtuoso/`；注释/docstring 全异）
- **hidden B2 (边角 2 文件)**：`svc_B2.py` / `svc_B2.sh` + `rename_map_B2.json`（无 .il，仅 py+sh 2 文件 edge case）
- **candidate**：`bridge_rename_port.py`（纯 stdlib，argv[1]=bridge_dir；load_files 跳过 rename_map.json；find_references 逐行 str.find 记 line/col/old；build_call_graph 子串存在性；rewrite 按 len(old) 降序 replace 防 prefix 覆盖；stale_check 残留扫描；summary 聚合；json.dumps sort_keys 确定性）
- **check()**：18 条件 a-r，独立 oracle 重新解析 B/B2（不 import reference）
- **3 negatives**：stub_empty→c / stub_print_expected→d / stub_delete_core→j，first_fail 3 distinct ✓

## 自验结果

- reference check.py self-test: **CHECK PASS** (18/18) ✓
- negative_selftest: **3/3 FAIL** (c/d/j distinct first_fail) ✓
- A/B/B2 三 fixture 解析正确 ✓
- 确定性 2x md5 一致 ✓
- 抗硬编码 A∩B rename_map keys 全 disjoint ✓
- jsonl test 字段 round-trip PASS（extract test → check.py → run reference_submit.zip → CHECK PASS 18/18）✓
- k_rationale == k_check == 18 ≥ 8 GATE PASS ✓
- build_jsonl.py --shard C 重建 441 case，--check 1642 case 全过 ✓

## ledger

- `trace_ledger_C.tsv`: 1794736845081_20qq6.messages.json claimed → case (EDA-Eval-DesignFlow-BridgeRenamePortAudit-001)
- covered (mc≥10) +1；layout_virtuoso domain +1
