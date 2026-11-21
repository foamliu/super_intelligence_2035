# fkrdf — Symlink Localize Produce (max7c @ hfeg0plg06, 2026-11-17)

- session: `1794915763924_fkrdf.messages.json` (140 msgs, 665KB, 2026-11-17)
- user: `max7c`, host: `hfeg0plg06` (10.129.x), mc=123 (11-20 scan; absent from 11-21 scan but file ALIVE)
- domain: digital (verilog simdir + vsim perl + sim flow scripts)
- prior ledger status: parked 2026-11-20 20:35 (reason: "path infra issue: sessions are subdirs not flat files, deferred; exucf chosen instead") — NOT a quality reject, just a path-infra deferral. Revived r891.

## 用户意图 (U#0 逐字)

> `/proj/ddjoc/V0/simdir/verilog/max7c/verilog.lpddr5.ddjoc.Nov17/这个目录下有很多link文件，帮我把这些link文件都变成本地文件吧`

U#24 same task on `libs/` subdir. U#34/U#46/U#52 chmod 系列. U#60 fix vsim `-errormax anchor` warning. U#76-#116 async_deploy.log TSACoreBaseNew regex 调试 (analysis/debug-Q&A).

## 助手 gold 链 (U#0 → msg#11/14)

idx=1: `list_allowed_files` 枚举 `verilog.lpddr5.ddjoc.Nov17/` → 识别 FILE/DIR/SYMLINK 三类。
idx=3-9: 多次 `run_approved_command` 失败 (Dynamic profile 'shell-runner' requires filePath) → 用 `editor` 写脚本 → `run_approved_command` (python-runner) 跑。
idx=11: `editor` 创建 `/home/max7c/convert_links.py` (gold 脚本)。
idx=13: `run_approved_command` 跑 `convert_links.py` → stdout: "Found 20 symlinks to convert" + 逐个 `<name> -> <target> (resolved: <resolved>)` + `done (file copied, N bytes)` / `done (directory copied)` + 最终 `All 20 symlinks have been converted to local files/directories.`

## gold convert_links.py 关键逻辑

1. `basedir = '/rundata/.../verilog.lpddr5.ddjoc.Nov17'` (硬编码路径)
2. **非递归** `os.listdir(basedir)` + `sorted()` 排序
3. `os.path.islink(full)` 识别 symlink; `os.readlink(full)` 取 target; `os.path.realpath(full)` 取 resolved
4. `os.unlink(full)` **先删 symlink** (无论 target 是否存在)
5. 分支:
   - `os.path.isdir(resolved)` → `shutil.copytree(resolved, full, symlinks=False)` + "copying directory" + "done (directory copied)"
   - `os.path.isfile(resolved)` → `shutil.copy2(resolved, full)` + "done (file copied, N bytes)"
   - else (broken) → "WARNING: target does not exist or is not file/dir" (symlink 已被 unlink, 不替换)
6. 报告格式: `Found N symlinks to convert:` + 逐行 `  <name>  ->  <target>  (resolved: <resolved>)` + 最终 `All N symlinks have been converted to local files/directories.`

trace 中 20 symlinks: 17 file (.sv/.v) + 3 dir (timing_table, timing_table_ff, timing_table_ss) + 0 broken. 转 U#24 同模式对 `libs/` 10 symlinks.

## case 合成 (r891)

- **case_id**: `EDA-Eval-DesignFlow-SymlinkLocalizeProduce-001`
- **档位**: B 档 synthesized (A 档 infeasible: /proj NFS 路径不可移植 + symlink target 在 SUT 沙箱不存在 + hidden B 需不同结构防背题)
- **fixture A**: `simdir_A.tar.gz` (6 symlinks: 4 file `lpddr5_model.v/lpddr5_test.sv/top.sv/assertion_bind.sv` + 1 dir `timing_table` + 1 broken `stale_link.sv` + 2 reg files `real_pattern.v/run_sim.sh` + 1 real subdir `Regressions/`) — 结构同构 trace 真实场景但缩小
- **hidden B**: `simdir_B.tar.gz` (8 symlinks: 5 file `ddr5_phy.sv/ddr5_ctrl.v/tb_top.sv/monitors.sv/tasks_pkg.sv` + 2 dir `libs_ff/libs_ss` + 1 broken `dead_link.v` + 3 reg files `commands_add0.txt/commands_add1.txt/README.md` + 1 real subdir `assertion/`) — 结构不同防硬编码 (B=8 vs A=6, 不同文件名)
- **ref**: `convert_links_ref.py` faithful 重写 trace msg#11 gold (参数化 basedir, 其余逻辑逐字匹配)
- **check.py**: 14 条独立断言 (a-n) + 3 次重跑确定性; base64 内嵌 hidden B 自包含
  - (a) submit.zip 含 convert_links.py / (b) py_compile / (c) exit 0 / (d) Found 8 symlinks (B 计数, 非 A 的 6) / (e) 零残留 / (f) file-link 变普通文件 / (g) md5 匹配 target / (h) dir-link 变真实目录含文件 / (i) dir 内部 md5 匹配 / (j) reg 文件不动 / (k) real 子目录不动 / (l) broken 被删除 / (m) 报告格式 / (n) 汇总行
- **negatives**: 5 个 (fake_empty/fake_print_expected/fake_core_deleted/naive_only_files/naive_skip_broken) 全 FAIL
- **§4.9 三假**: empty/print_only/core_deleted 全 FAIL
- **k_check = k_rationale = 14 ≥ 8** GATE PASS

## 自验

- ref `reference_submit.zip` PASS 14/14 (a-n) + 3 跑确定性 (rc=0, count=8)
- 5 negatives 全 FAIL (NEG_RC=0)
- §4.9 (a)(b)(c) 三假 (empty/print/core-deleted) 全 FAIL
- ref 在 visible A 上跑也正确 (Found 6 symlinks, 全部转换, stale_link WARNING+removed, 零残留)
- check.py 从任意目录运行 OK (base64 自包含)
