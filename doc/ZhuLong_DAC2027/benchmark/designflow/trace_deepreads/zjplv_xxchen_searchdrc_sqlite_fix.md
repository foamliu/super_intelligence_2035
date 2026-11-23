# Deepread note: 1794799001872_zjplv (xxchen @ hfeg0plg18)

- **session**: 1794799001872_zjplv
- **user / host / ip**: xxchen / hfeg0plg18 / 10.129.8.238
- **match_count**: 214  (keywords: drc:1146; calibre:8; .gds:3; pdk:2)
- **msgs**: 124 (329 KB), 3 user inputs
- **cwd**: /home/xxchen/workspace/DRC_search/data/0.2
- **domain**: physical_verify (DRC-rule-search service launch + SQLite legacy compat)
- **case_id**: EDA-Eval-DesignFlow-SearchDrcLaunchSqliteFix-001
- **subpattern**: searchdrc_launch_sqlite_fix

## Real task (synthesized from 3 user inputs)

xxchen 在 DRC_search 项目里要把 searchDRC（一个 DRC 规则搜索 HTTP 服务 v1.0.3，
`searchDRC/backend/server.py`，纯标准库，Python>=3.7）跑在遗留环境 **Python 3.7.1 +
SQLite 3.6.20** 上。直接启动会失败，两处不兼容：

1. `searchDRC/backend/catalog.py` 的 `upsert_dataset` 用 `INSERT ... ON CONFLICT(id)
   DO UPDATE SET document=excluded.document`（UPSERT），需要 SQLite>=3.24；3.6.20 报
   `near "ON": syntax error`。
2. `__init__` 里 `PRAGMA journal_mode=WAL` 需要 SQLite>=3.7.0；且 `searchdrc.sqlite3`
   当前是 WAL 格式（文件头 write/read_version=2），3.6.20 打不开，报
   `file is encrypted or is not a database`。

需要：写 `run.sh` 启动脚本 + 修 catalog.py（UPSERT→INSERT OR REPLACE；WAL→DELETE）+
在 run.sh 启动前把 WAL 库就地转成 DELETE/rollback 模式（PRAGMA journal_mode=DELETE;
VACUUM），文件头变 (1,1)、无 -wal/-shm、数据完整。参考同项目已修好的 `cxmt_instance/`
实例与 `tasks/code-mods.md` 经验记录。

## Assistant tool chain (real trace)

- list_allowed_files / read_files 浏览项目结构
- run_approved_command 跑 sqlite3 查 DB header / python 查版本
- editor 改 catalog.py 与 run.sh
- 验证：起服务、curl /api/health、/api/catalog、/

## Case design (offline Python version)

- **公开 A 档 (config_a/)**：searchDRC/ 原 WAL 库(6 条数据集)+原 UPSERT catalog.py；
  cxmt_instance/ 已修好实例；tasks/ 经验记录；AGENTS.md 约定。SUT 据此写 run.sh + 修
  catalog.py，打包 submit.zip。
- **隐藏 B (config_b)**：WAL 库，9 条数据集（与 A 的 6 不同）；manifest expected=9。
- **隐藏 C (config_c)**：WAL 库，4 条数据集；manifest expected=4。cross-input 反硬编守卫。
- 三个 DB 均 WAL 格式 (2,2)；check 时 SUT 的 run.sh 必须就地把 WAL→DELETE 转换，使服务
  能起来；SUT 的 catalog.py 覆盖到 hidden tool backend。
- check 15 条独立条件：cond1 zip 合法 / cond2 bash -n / cond3 health / cond4 revision=9 /
  cond5 GET / 200 / cond6 无 ON CONFLICT SQL / cond7 有 INSERT OR REPLACE / cond8 无 WAL
  有 DELETE / cond9 DB 头 (1,1) 无 sidecar / cond10 config_c=4 且 !=9 / cond11 PYTHON 环境变量 /
  cond12 启 server.py / cond13 WAL→DELETE 转换步骤 / cond14 catalog 可 import 且 upsert/list
  正确 / cond15 3-seed 决定性。
- **隐藏 B/C 不进 SUT 沙盒**（leak isolation）；check 在独立 temp dir 跑、finally rmtree。
- 反硬编：config_b 期望 9、config_c 期望 4，硬编 9 的会在 cond10 命中 config_c≠4 且 cond10b
  hardcoding suspected。
- 关键设计点：原 catalog.py 用 ThreadingHTTPServer，必须 `check_same_thread=False`，否则
  /api/catalog 在 worker 线程里用主线程创建的 sqlite 连接会抛
  "SQLite objects created in a thread can only be used in that same thread"。SUT 若从头
  重写 catalog 漏掉这点，服务起得来但 /api/catalog 崩 → cond4/cond10 fail（合理失败）。

## Negatives (4 个，distinct primary)

- empty        → cond1 (空 zip 缺 run.sh/catalog.py)
- print_only   → cond3 (run.sh 只 echo 不起服务)
- hardcode_b   → cond10 (造假服务硬编 revision=9，config_c 期望 4)
- delete_core  → cond7 (catalog upsert SQL 整段删掉，无 INSERT OR REPLACE)

3-seed 决定性 (cond15) 在 config_b 上连跑 3 次（每次全新库副本）revision 恒 9、DB 恒 DELETE。

## Verification

- reference solve.py → submit.zip → check.py: **PASS** (15/15)
- 4 negatives: **all FAIL**, distinct primaries (cond1/cond3/cond10/cond7)
- embedded test field (from case JSON) re-run: **PASS**
