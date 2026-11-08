# Deep-read: 1790047784806_lsc1e (GloryEX RC Flow batch setup)

- **user**: simplec @ hfeg0pkn002 (10.129.2.11), mc=143, NEW user (首个 case)
- **agent**: lead, 250 msgs
- **kw**: aether:1028 / .cdl:1013 / netlist:298 / schematic:235 / pdk:158 / pyaether:80 / lvs:72 / cmos:42
- **domain**: physical_verify (GloryEX 寄生 RC 提取 flow 编排)

## 用户真实意图（A-档候选）

**U#1 (idx=0, 提出需求, 未给根因)**：「帮我跑一下glory RC flow」
- U#2 (idx=83):「再跑一次flow 和上次的配置一样」
- U#3 (idx=240):「我已经修改了脚本，重新跑一下」

→ 干净的「提出需求」轮，未给根因/修复方案。✓ A-档 eligible（但真实 CCI_DB/GloryEX license 不可访问，落 B-档重定义）。

## Grounding（agent 工具链真实产物）

1. **flow 主脚本** `gxrc_autorun2.py`（6070B，已全文读）：
   - 配置路径：`QA_list`（case 列表）/ `captab_path` / `layer_map_path` / `gxrc_cmd_path`（gxrc_cci_cmd 模板）/ `cci_path`（CCI_DB 源根）/ `query_cmd_path` / `max_workers=2`
   - `creat_task_file()`：读 case 列表 → 每 case 建 `<run>/<case>/` → `link_file` 软链 CCI_DB → `copy2` gxrc_cci_cmd + query_cmd → `replace_in_file` 替换 `TOPCELL`→case 名、`***.captab`→captab 路径、`***tran.map`→layer_map 路径 → 写 `run` 脚本 `#!/bin/csh\ncd <target>\nbsub -I gxrc -c gxrc_cci_cmd > /dev/null`
   - `main()`：建 `<timestamp>_run/` → 列 task 目录 → 跳过已有 `<case>.dspf` 的 → ThreadPoolExecutor(csh) 跑剩余

2. **case 列表** `CCI_DB/list`（1119B，36 条 sandwich case）：
   `Sandwich_M9_M10_W0P4_S0P4_RDL` ... `Sandwich_M9_M10_W1P5_S1P5_RDL`
   命名：`Sandwich_M<层1>_<层2>_W<宽>P<值>_S<距>P<值>_RDL`

3. **gxrc_cci_cmd 模板**（7626B，已读）：
   `*** Phlexing GloryEX Option File` + `EXT_CELL\tTOPCELL\t` + `CAPTAB\t***.captab` + `LAYER_MAPPING_FILE ***tran.map` + `CALIBRE_INPUT{ QUERY_CMD\tquery_cmd\t}` + `NETLIST_FILE{ FILE_NAME\tTOPCELL.dspf\t}` + `NETLIST_FILE{ FORMAT\tDSPF\t}` + `EXT_MODE\tRC\t` + 多个 `NETLIST_PARAMS{...}` + `EXT_NETS\t*\t` + `CALIBRE_DEVICE_TYPE{...}`

4. **query_cmd**（1121B，已读）— calibre LVS 查询命令，定义 CCI_DB 必备文件：
   `CCI_DB.GDS_MAP` / `CCI_DB.agf` / `CCI_DB.devtab` / `CCI_DB.lnn` / `CCI_DB.pdsp` / `CCI_DB.nl` / `CCI_DB.nxf`` / `CCI_DB.ixf` / `CCI_DB.ports_cells` / `CCI_DB.extents` / `CCI_DB.lvs_settings`（每个 `WRITE ./CCI_DB/CCI_DB.<ext>` 一条）

5. **run 脚本样例**：
   ```
   #!/bin/csh
   cd ./20260922105947_run/Sandwich_M9_M10_W0P4_S0P4_RDL
   bsub  -I gxrc -c gxrc_cci_cmd > /dev/null
   ```

6. **真实失败模式**：
   - 4 个 W1P5 case（S0P6/S0P8/S1P0/S1P5）源 CCI_DB 缺 `CCI_DB.lvs_settings` → 失败
   - 部分源目录根本不存在（CCI_DB/list 有 36，源只有 32）
   - 沙盒无 LSF（`bsub` 需 `/etc/lsf.conf`）+ 无 Glory license（`gxrc_t` 需 `PHLEXING_LICENSE_FILE`）→ 实跑报 `-E- License: login failed(266) 错误的命令类型`

7. **agent 修复脚本** `run_glory_flow.sh`：Step1 从 working case 复 lvs_settings 补缺 → Step2 建 task 目录 → Step3 bsub/gxrc_t 跑

## 为何 B-档重定义

真实 GloryEX 工具 + LSF 集群 + license + simplec 的 CCI_DB 源库对 e0031982 在 .75 不可访问，无法取真实 flow 作 A 输入。但 trace 深度 grounds 了「批量 setup + 完整性校验 + 报告」的契约：case 列表驱动、per-case gxrc_cci_cmd 模板替换、run 脚本生成、CCI_DB 必备文件集合（自 query_cmd 提取）、ready_to_run 判定、缺陷分类（missing_source_dir / missing_lvs_settings / incomplete）。故重定义为确定性离线编排器 `glory_rc_flow_setup.py`（stdlib only，不真跑 gxrc），喂合成的 flow_config + cci_db_manifest。

## DISTINCT from 现有 physical_verify 系

**首次 ground on Empyrean GloryEX RC 寄生提取 flow 编排**（case-list 驱动批量 setup + gxrc_cci_cmd 模板替换 + CCI_DB 完整性校验 + 缺陷分类报告）。现有系：calibre DRC/LVS deck 生成（LdrSvrfRuleGen/VssPunchRuleGen/SvrfPvrsRuleTranslate/DrcRuleTimeRank）、calibre LVS 报告 teardown（DrcLogTeardownReport）、LVS 歧义诊断（LvsAmbiguityDiag）、Hcell 配对、SPF RC 聚合审计（SpfRcAggregateAudit）、implant fill deck、DRC pattern/waive deck 等。本案工具不同（GloryEX vs calibre），任务类型不同（flow 编排+校验 vs 规则生成/分析），且首提「CCI_DB 完整性校验 + 缺陷分类」判分维度。

## case 结构

- **assets/A**: flow_config_A.json(8 cases, M9_M10, ts=20261020105947, 6 complete/1 missing lvs/1 missing source) + cci_db_manifest_A.json + gloryex_flow_spec.md + prompt.txt + task_brief.md + manifest_A.json
- **hidden/B**: flow_config_B.json(11 cases, M8_M9, ts=20261105183022, version 2026.06_P005, 6 complete/2 missing lvs/1 missing devtab/2 missing source) + cci_db_manifest_B.json + hidden_manifest.json
- **reference**: golden_solution.py(5502B stdlib-only) + check.py(17556B, 14 条件 a-n) + negative/{empty_shell,print_expected,hardcoded_A,core_deleted,stub_no_parse}.py + negative_selftest.py + reference_submit.zip(1850B)

## 自验

- golden self-test A/B：rc=0，status_report 计数正确（A: total=8/ready=6/missing_source=[W0P6_S0P6]/missing_lvs=[W1P5_S1P5]；B: total=11/ready=6/missing_source=2/missing_lvs=2/task_dirs=9）✓
- check.py vs golden：14/14 PASS ✓
- negative_selftest：5/5 ALL-FAIL（critical logic 条件 d/e/f/g/h/i/j/k 全 FAIL）✓
- §4.9 三假提交（empty/print-expected/core-deleted）：all-pass=False ✓
- test 字段==disk check.py 字节相等 ✓（17556B）
- 确定性：3 跑 sha256 完全一致 ✓
- 断言闸门：k_rationale=14=k_check(a-n)≥8 ✓
- 已落 jsonl_C(247 行) + ledger mark case
