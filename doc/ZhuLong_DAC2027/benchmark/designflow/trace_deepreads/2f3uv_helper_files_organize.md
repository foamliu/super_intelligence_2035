# trace_deepreads/2f3uv_helper_files_organize.md

**session**: 1793755021637_2f3uv
**user**: daiweilu @ 10.129.35.244 (hfeg0plg101)
**scan keywords**: systemverilog:22; netlist:8; verilog:7; cadence:7; virtuoso:2; .lef:2; .def:2 (mc=18 on 11-18 scan)
**size**: 203976 bytes, 52 messages (34 user / 18 assistant), 4 user turns

## 用户真实意图（4 轮）

1. `USER[1] @msg#0`: 「你可以整理一下/home/daiweilu中你之前生成的辅助文件，按文件夹分类吗」
2. `USER[2] @msg#21`: 「以后你生成的辅助文件可以都按照这样分类吗」
3. `USER[3] @msg#27`: 「整理一下当前文件」
4. `USER[4] @msg#47`: 「我的ctags呢」

真实意图：把工作目录顶层散落的辅助文件（TM_FsPgm/LPDDR5 FsPgm 调试任务生成的搜索脚本、
生成脚本、数据产物、日志、结果目录）按类别归档到 `helper_files/{scripts,data,logs,results}/`，
并固化为可复用的分类约定。第 4 轮确认 `.ctags`（隐藏 dotfile）未被误动。

## agent 工具链

- `list_allowed_files` / `read_files`：探查顶层文件 + 3 个 results 目录内容
- `editor`：写 `organize_helper_files.py`（v1，硬编码 27 脚本 + 7 数据 + 2 日志 + 3 results 目录清单）
- `run_approved_command`(python-runner)：执行整理脚本，39 项归档
- `editor`：写 `helper_files/README.txt`（分类约定固化）
- 第 2 轮「整理当前文件」：写 `organize_current.py`（v2，**按扩展名自动发现分类**，更通用）
- `run_approved_command`：执行 v2，68 项归档
- `list_allowed_files` / `read_files`：核验 `.ctags` 完好未动

## 分类约定（agent 与用户共同确立）

| 分类 | 放什么 |
|---|---|
| `scripts/` | `.py` / `.sh` 搜索/分析/生成/校验脚本 |
| `data/` | `.v` / `.sv` / `.patch` / `.run` / `.txt` / `.json` / `.csv` / `.rpt` / `.list` / `.report` / `.def` / `.lef` 等数据产物 |
| `logs/` | `.log` / `.lck` / `.cdslck` / `.logfile` 日志与锁文件 |
| `results/` | 顶层以 `results` 结尾的整目录（合并内容） |

规则：仅移动不删除；不动隐藏 dotfile；不动系统目录（Desktop/Documents/...）；不动 helper_files 自身；不覆盖已存在目标；非 results/非系统的目录保持原位。

## 域判定

`eda_other`。keywords 里 systemverilog/verilog 来自被整理的 `.sv`/`.v` 文件内容与 `.ctags` 配置，
**非工具调用**。真实意图 = env-config / file-organization（工作目录归档约定）。
旧规则下或被判 env-config/setup weak，**11-15 任务初衷重审后恢复可造**（env-config 类全部恢复）。

## case 工程化（EDA-Eval-DesignFlow-HelperFilesOrganize-001）

- **A 档 trace-faithful**：prompt 用用户 4 轮原话
- **produce-task reframe + hidden-B 真跑**：A = convention.txt + workspace_A.zip（示例，27 文件）+ task_brief.md；B = check.py 内联生成（9 脚本含 collide.py 覆盖测试 / 8 数据含 .json/.csv / 3 日志 / 2 隐藏 / 3 系统目录 / 3 results 目录 / myproject 非结果目录 / 预存 helper_files 含 collide.py+preexisting.py+keep.v）
- **参考解** = organize_ref.py（基于 trace agent 的 organize_current.py 参数化为 argv[1]，自动发现分类）
- **check.py 15 断言**：zip 合法 + 脚本>200B + stdlib-only + py_compile + 退出0+四子目录 + scripts全 + data全 + logs全 + results合并内容 + 隐藏不动 + 系统不动 + 无删除(文件数守恒+myproject不动) + 不覆盖(md5 守恒+collide.py 跳过) + 确定性(3 run 同布局) + 反退化(scripts 非空)
- **5 negatives 全 FAIL**：neg_empty(②) / neg_print_only(⑤) / neg_delete_core(⑤) / neg_overwrite(⑫) / neg_wrong_category(⑤)
- **§4.9 a/b/c**：neg_empty(a) / neg_print_only(b) / neg_delete_core(c) 全 FAIL
- ref PASS 15/15（含 inlined-test e2e 复核）；negative_selftest ALL GOOD

## 备注

- r799 首选 8pb5i(willl mc7) 经深读判 **wrong-shard**（finesim SPICE sim + PEX = B/C 域，synopsys keyword=finesim Synopsys SPICE 误触 A filter），mark parked，转 2f3uv
- 2f3uv keywords 含 cadence:7/virtuoso:2 但真实意图是文件归档（非 layout），systemverilog:22 来自被整理文件内容
