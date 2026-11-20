# Deepread: 5uqoi — Verdi FSDB dumper 加载失败诊断 (multi-root-cause env-debug cascade)

**session**: `1793189553608_5uqoi` · **user**: dsgao · **host**: 10.129.32.75 (hfeg0plg89 登录节点 / hfpdcnd017+hfebhds109 bsub 计算节点) · **match_count**: 126 · **domain**: eda_other
**trace**: `/home/dsgao/.cline/data/sessions/1793189553608_5uqoi/1793189553608_5uqoi.messages.json` (950KB / 98 msgs / 10 user-turns / 45 tool calls)
**旧判定**: r375 peek `REVIVABLE_QA env-config/how-to` weak → r638 按 11-15 令复活
**新判定**: 可造 (C-A debug-Q&A/env-config, evidence anchor 强 = 11 份真实环境文件可 trace-embed)

---

## 一、用户真实意图 (逐字)

U#0 (msg 0, 用户原话, 逐字):
```
=====================================
*Verdi* WARNING: 'Enable FSDB dumping with option -debug/-debug_pp/-debug_all and option -P along with novas.tab file' will be deprecated in VERDI2024.09.
*Verdi* WARNING: Please use '-debug_access' along with a proper setting on VERDI_HOME environment variable in vcs compilation. ...
*Verdi* Loading libsscore_vcs202312.so
*Verdi* Cannot load libsscore_vcs202312.so from following VERDI_HOME or NOVAS_HOME
/apps/synopsys/verdi/V-2023.12-SP2-3/bin/verdi/share/PLI/lib/LINUXAMD64/
*Verdi* Failed to load FSDB dumper.
```
U#1: 「用中文回答一遍」

**意图 = 诊断 Verdi FSDB dumper 加载失败根因 + 给修复方案**。用户在 drcpa 项目跑 `bsub -I make verdi` 想用 Verdi 看 wave.fsdb 波形，Verdi 启动时 FSDB dumper 加载失败。session 随后展开为 **4 个独立根因的级联诊断**（用户每次贴新报错，agent 逐层定位）。

## 二、agent 工具链 (45 calls)

`read_files` 16 · `list_allowed_files` 12 · `editor` 9 (修 .bashrc + makefile) · `run_approved_command` 6 (check_verdi_lic.py / check_verdi_paths.py) · `get_agent_policy_status` 1 · `skills` 1

真实环境只读检查：Verdi 安装目录 PLI lib 列表、`bin/verdi` symlink → `.wrapper`、`.bashrc`、`.cshrc`(ENOENT)、`/apps/bin/.bashrc.common`、verdi modulefile、`hf_tool_version`、`.wrapper` L1808-1825、`/etc/bashrc`+`/etc/profile`、`~/drcpa/makefile`、wv/vcs modulefile。真实写操作：editor 修 `.bashrc` L73-78 + makefile verdi target (加 `unset NOVAS_HOME`)。

## 三、4 个根因 (级联, 每个独立可失败)

### RC1 — VERDI_HOME/NOVAS_HOME 指向 verdi 二进制而非安装根 (FSDB dumper)
- **现象** (U#0): dumper 从 `/apps/synopsys/verdi/V-2023.12-SP2-3/bin/verdi/share/PLI/lib/LINUXAMD64/` 加载失败
- **根因**: `.bashrc` L73-74 `export NOVAS_HOME/VERDI_HOME=/apps/synopsys/verdi/V-2023.12-SP2-3/bin/verdi` — `bin/verdi` 是 symlink → `bin/.wrapper` (启动器**文件**, 非目录)。dumper 拼 `$VERDI_HOME/share/PLI/lib/LINUXAMD64/` → 不存在路径
- **核实**: read_files 读 `.../share/PLI/lib/linux64/libsscore_vcs202312.so` + `.../LINUXAMD64/libsscore_vcs202312.so` 均 success (ELF 二进制存在)；list_allowed_files `bin/verdi` 显示是 symlink 非 dir
- **修复**: VERDI_HOME/NOVAS_HOME 指向安装根 `/apps/synopsys/verdi/V-2023.12-SP2-3` (或交给 module 管理)；库版本 `libsscore_vcs202312.so` ↔ `ds/vcs/2023.12-SP2-3` 匹配

### RC2 — 登录节点 GLIBC 太老, Verdi 2023.12 无法运行
- **现象** (U#3/msg43): `verdi -licdebug` 在登录节点 hfeg0plg89 报 `GLIBC_2.14/2.15/2.17 not found` (Novas + libvfs.so) + `line 1817: [: -v: unary operator expected`
- **根因**: 登录节点老 OS (glibc <2.14, CentOS 6.x)；`.wrapper` L1817 `[ -v VERDI_ENABLE_EDR_STP ]` 是 bash 4.2+ 语法，老 bash 不认
- **核实**: read_files `.wrapper` L1808-1825 确认 L1817 用 `[ -v VAR ]`
- **修复**: Verdi 2023.12 只能 `bsub -I` 在计算节点 (新 OS) 跑，不能在登录节点直接跑

### RC3 — License server 端 -8,544 (非本地/非占满)
- **现象** (U#4/msg47, bsub 计算节点 hfpdcnd017): licdebug 显示 `Verdi` feature: hl04-hl08 → FlexNet **-8,544** "Invalid (inconsistent) license key — license file has been altered"；hfds4/hfrdap200/201 → **-5,147** (No such feature)；`VERDI-ULTRA` fallback → -5,147 全 8 台 (不存在)。`*WARN* Verdi-Elite (Verdi) license is not available. Try Verdi-Apex (Verdi-Ultra)`。换节点 hfebhds109 报错一字不差
- **根因**: license server 端问题 (license 文件被改动/损坏 或 snpslmd vendor daemon 太老无法校验 2023.12 新签名)。**非** -4 (非占满)、**非** 本地网络 (客户端成功连上全部 8 台拿到明确应答)
- **核实**: read_files `hf_tool_version` L34 `SNPSLMD_LICENSE_FILE=12000@hl04:12000@hfds4:...:12000@hfrdap201`；`.bashrc.common` L26 `LM_LICENSE_FILE=59001@hfds2:1881@hfds1`；run_approved_command check_verdi_lic.py → 沙箱无 DNS 无法探测 (但 licdebug 输出本身已足够)
- **修复**: CAD 修 license server；绕过 = 切旧版 Verdi (U-2023.03-SP1-1 / R-2020.12, 旧签名格式可校验)；或 `unset SNPSLMD_LICENSE_FILE` 回退 LM_LICENSE_FILE server

### RC4 — module switch 后 NOVAS_HOME/VERDI_HOME conflict + 手改 .bashrc 路径不存在
- **现象** (U#6/msg58): `module switch ds/verdi/U-2023.03-SP1-1` 后 `bsub -I make verdi` 报 `NOVAS_HOME conflicts with VERDI_HOME. To solve ... unset NOVAS_HOME`
- **根因 (三层)**: ① module switch 把 VERDI_HOME 切到 2023.03，但 .bashrc 硬编码 NOVAS_HOME 还指 2023.12 → 冲突；② 用户手改 .bashrc L73-74 为 `/apps/synopsys/SRB/verdi/V-2023.12-SP2-3` (带 `V-` 前缀) — **该路径不存在** (list_allowed_files `/apps/synopsys/SRB/verdi` 真实条目 = `2023.12-SP2-3` 无 `V-` 前缀)，保留会令 FSDB dumper 复发；③ 长期开着的旧 shell 残留旧 NOVAS_HOME 被 bsub 传播到计算节点 (.bashrc 改动只对新 shell 生效)
- **核实**: list_allowed_files `/apps/synopsys/SRB/verdi` (真实条目 2023.12-SP2-3/M-2017.03/R-2020.12/U-2023.03/W-2024.09)；read_files wv/vcs modulefile (不设 NOVAS_HOME)；read_files /etc/bashrc+/etc/profile (不设 NOVAS_HOME) → 排除全局来源；run_approved_command check_verdi_paths.py → module 路径 `SRB/verdi_2023.12-SP2-3` 下 libsscore_vcs202312.so 齐全，U-2023.03 只有 libsscore_vcs202303.so (切旧版只能看波形不能重跑仿真)
- **修复**: 注释 .bashrc 硬编码 NOVAS_HOME/VERDI_HOME (交给 module) + 加 `unset NOVAS_HOME`；makefile verdi target 加 `unset NOVAS_HOME;`；旧 shell 手动 `unset NOVAS_HOME`

## 四、可嵌入资产 (11 份, trace-embedded, asset_fidelity=original)

从 trace read_files tool_result `result` 字段 (含行号, 合成时剥离行号还原) + user 贴的报错原文抽取：

| 资产文件 | 来源 | 用途 |
|---|---|---|
| `verdi_fsdb_load_error.log` | U#0 原文 | RC1 现象证据 |
| `verdi_licdebug_glibc_error.log` | U#3/msg43 原文 | RC2 现象证据 (GLIBC + [: -v) |
| `verdi_licdebug_license_fail.log` | U#4/msg47 原文 (full, 含 -8,544/-5,147/VERDI-ULTRA 表) | RC3 现象证据 |
| `verdi_novas_conflict_error.log` | U#6/msg58 + module list | RC4 现象证据 |
| `bashrc_dsgao.txt` | read_files .bashrc (L1-84, 含 L73-78 错误 export) | RC1/RC4 环境证据 |
| `bashrc_common.txt` | read_files /apps/bin/.bashrc.common (L1-100, L26 LM_LICENSE_FILE) | RC3 license 环境证据 |
| `hf_tool_version.txt` | read_files hf_tool_version (L1-60, L34 SNPSLMD_LICENSE_FILE) | RC3 license server 列表证据 |
| `verdi_modulefile_2023.12.txt` | read_files ds/verdi/2023.12-SP2-3 modulefile (L1-17, VERDI_HOME + SNPSLMD) | RC1/RC3 module 管理证据 |
| `makefile_drcpa.txt` | read_files ~/drcpa/makefile (L1-32, verdi target + VERDI_PLI 硬编码) | RC4 makefile 不引用 NOVAS_HOME 证据 |
| `verdi_wrapper_1817.txt` | read_files .wrapper L1808-1825 (L1817 [ -v ]) | RC2 bash 4.2+ 语法证据 |
| `verdi_pli_check.txt` | run_approved_command check_verdi_paths.py stdout (EXISTS/MISSING 表) | RC1/RC4 库存在性证据 |

## 五、合成计划 (下轮执行)

- **case_id**: `EDA-Eval-DesignFlow-VerdiFsdbLoadDiagnose-001`
- **category**: C-A debug-Q&A / env-config (multi-root-cause 诊断报告型)
- **domain**: eda_other
- **trace_source**: {user: dsgao, host: 10.129.32.75, session_file: 1793189553608_5uqoi, match_count: 126, real_task_summary: "Verdi FSDB dumper 加载失败根因诊断 (4 级联根因: VERDI_HOME 路径错/GLIBC 太老/license -8,544/NOVAS_HOME 冲突)"}
- **prompt**: trace-faithful A 档, 用 dsgao 原话 + 真实路径/工具/报错串, 要求交付结构化诊断报告 JSON, 不产脚本
- **deliverable**: `verdi_fsdb_load_diagnosis_report.json` (only)
- **报告结构**: `report_overview` / `root_causes` (4, 每个含 id/category/evidence{error_string,env_path,file_line}/fix{action,commands,expected}) / `error_chronology` (按 U#0→U#6 顺序) / `environment_findings` / `fix_actions` / `evidence` (token→source 映射) / `methodology` / `conclusion` / `confidence`
- **check() 条件 (k≥16)**:
  - content-correctness (a-n, ~14): 4 RC 各验 category + 关键 evidence (error 串/路径/行号) + 正确 fix；report_overview/error_chronology 结构；environment_findings 含 license server 列表 + GLIBC 版本
  - evidence-verification (o): 每个 RC 的 evidence token 必须能在 A_FILES 中定位 (grep 真实串, 如 `libsscore_vcs202312.so`, `GLIBC_2.17`, `-8,544`, `NOVAS_HOME conflicts`)
  - B-judge-selfcheck (p): 隐藏 B = 变体环境 (Verdi 2024.09-SP2 + 不同 license server 集 hl09-hl12 + GLIBC_2.18 not found + NOVAS_HOME 已 unset + .bashrc L80 错配), 内嵌 `_parse_b` 独立解析, ≥6 anti-hardcode 维度全异于 A (版本/路径/server 列表/GLIBC 版本/冲突变量/错误行)
  - 3-seed (q): 随机抽 RC 子集 3 seed 结论一致
- **A_FILES**: 11 份证据文件 base64 内联进 check.py (自包含, 占位符 + chr(92) 规避 write_file 转义腐蚀, 同 r635/r637)
- **negatives** (5, 全 FAIL distinct): empty→a / print-no-ev→o / wrong-rootcause→(把 4 RC 归因为单一 license 占满)→c / core-deleted→(删 2 个 RC)→e / b_overfit→(硬编 A 串在 B 上误 PASS)→d
- **§4.9 三假**: (a)空壳 (b)只 print 期望串 (c)删核心 (参考解去掉 RC3+RC4) 全 FAIL
- **自验**: ref k/k ALL PASS + 5neg 全 FAIL distinct + §4.9 全 FAIL + e2e jsonl test field 独立跑 PASS

## 六、备注

- 真实性: dsgao/hfeg0plg89/hfpdcnd017/10.129.32.75 全部保留原值 (§红线 2 不脱敏)；仅 license server 主机名是真实环境配置 (非 key/token)
- 资产路径: `/proj/drcpa/` 与 `/apps/` 在沙箱可能不可达 → trace-embedded (从 trace read_files 结果重抽, 行号剥离还原), asset_fidelity=original, 同 r631/r635/r637 模式
- 4 RC 级联但独立: 每个 RC 的 evidence + fix 独立可验, 满足 §4.3「≥8 独立条件每个单独可 FAIL」
- 无多模态需求 (纯文本诊断报告)
