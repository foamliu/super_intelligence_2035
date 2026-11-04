# trace_deepread: wj4ab — DRC 自动化脚本 Python 解释器兼容性排障

- **session**: 1791861649073_wj4ab.messages.json
- **user/host**: kenwang @ hfeg0pkn005 (10.129.2.14 / 10.129.35.75 等)
- **size**: 3.03 MB, 342 msgs, 2026-10-30
- **match_count**: 253；keywords: 65 calibre / 6 hspice / 3 spectre / 2 innovus / 1 virtuoso
- **cwd**: /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/test_2/
- **domain**: physical_verify（DRC 自动化批处理脚本 env 排障，非 DRC 规则/结果分析）

## 用户意图（USER#0，逐字，A-档 seed 提出目标、未给完整根因/修复方案）

> /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/test_2/./ts_auto.sh
> Fatal Python error: initfsencoding: unable to load the file system codec
> ModuleNotFoundError: No module named 'encodings'
> ./ts_auto.sh: line 8: 42818 Aborted (core dumped) ./drc_auto.py main.rule 18 18 xa_start=3 ...
> 有一个问题需要帮忙解决一下，现在文件 drc_auto.py 中需要调整一下 load Python 的版本，请参考一下 .bashrc 文件应该如何修改呢

用户指了修复方向（"调整 drc_auto.py 里 load Python 的版本，参考 .bashrc"）→ B-档 synthesized（非干净 A-档）。
后续 USER#14/#20/#44/#55 给新报错=迭代 hint，不进 prompt。

## assistant 工具链（env 排障段 #0–#43）

read_files(ts_auto.sh / drc_auto.py / .bashrc) → run_commands(probe python3/which/PYTHONHOME/PYTHONPATH/module list) → read_files(/apps/bin/.bashrc.common / /apps/local/bin/python3) → list_allowed_files(/apps/local/bin) → read_files(7 个 modulefiles/tools/python/3.x) → list_allowed_files(/apps/cad/modulefiles/tools/python) → 诊断。

## 真实根因（人工复核 #8/#19/#43）

1. **version mismatch（encodings 报错）**：drc_auto.py shebang 硬编码 `#!/apps/local/bin/python3` → Python 3.7.1；而 .bashrc → .bashrc.common `source /apps/cad/Modules/init/bash` + `module switch python/3.11.9` 把 PYTHONHOME/PYTHONPATH 指向 `/apps/local/python/python3.11.9`。用 3.7 二进制启动但 PYTHONHOME 是 3.11.9 → 3.7 找不到自己的 `encodings` 模块 → `Fatal Python error initfsencoding / No module named 'encodings'`。
2. **malformed shebang（#14 报错）**：用户首改把第1行改成 `###!/apps/local/bin/python3`（## 前缀），第2行 `#!/usr/bin/env python3`；Linux 内核只看第1字节 `#!`，`###!` 不是 shebang → .py 被 bash 当脚本跑 → `from: command not found`。这是用户改坏的中间态，不是独立根因。
3. **glibc incompat（#20 报错）**：shebang 改对成 `#!/usr/bin/env python3` 后，env 解析到 module 加载的 python3 = 3.11.9，但 `libpython3.11.so.1.0` 要求 `GLIBC_2.14/2.15/2.17`，而系统 glibc = 2.12（CentOS 6）→ `version 'GLIBC_2.x' not found`。
4. **解**：modulefiles 系统可用 3.7.1/3.7.12/3.9.1/3.10.5/3.11.0/3.11.9/3.12.9；选 glibc 兼容（要求 ≤ 2.12）的最高版 = **3.10.5**（`/apps/local/python/python-3.10.5`）；`module switch python/3.10.5` + shebang `#!/usr/bin/env python3` + 运行前 unset PYTHONHOME/PYTHONPATH → drc_auto.py 跑通模板渲染。assistant #54 明确"shebang 修正、glibc 兼容的 Python 3.10.5"。

## 关键文件事实（从 trace tool_results 提取）

- drc_auto.py shebang（#16）：`###!/apps/local/bin/python3` / `#!/usr/bin/env python3`（用户改坏的中间态）；原始 = `#!/apps/local/bin/python3`（3.7.1）。
- /apps/local/bin/python3 → symlink → Python 3.7.1。
- .bashrc（kenwang）：`source /apps/bin/.bashrc.common`；.bashrc.common：`source /apps/cad/Modules/init/bash`、`export MODULEPATH=/apps/cad/modulefiles/tools`、`module switch python/3.11.9`。
- module 3.11.9 modulefile：`unsetenv PYTHONPATH/PYTHONHOME` → `set PYTHONHOME /apps/local/python/python3.11.9` → `setenv PYTHONHOME` → `prepend-path PATH $PYTHONHOME/bin` → `prepend-path LD_LIBRARY_PATH $PYTHONHOME/lib` → `setenv PYTHONPATH /apps/local/python/python3.11.9`。
- modulefiles catalog（PYTHONHOME）：3.7.1→python3.7.1 / 3.7.12→python3.7.12 / 3.9.1→python-3.9.12 / 3.10.5→python-3.10.5 / 3.11.0→python3.11.0 / 3.11.9→python3.11.9 / 3.12.9→miniforge3。
- GLIBC 报错原文：`python3: /lib64/libc.so.6: version 'GLIBC_2.15' not found (required by /apps/local/python/python3.11.9/lib/libpython3.11.so.1.0)` × 3 符号（2.14/2.15/2.17）。

## 后续（#44+，不进本案）

Python env 解决后 drc_auto.py 跑到模板逻辑：`KeyError 'Undefined variable $<r_start>'`（#load 单# 被模板引擎当 load 指令递归加载注释规则文件）→ OPEN1 `.drc` 不生成 → 这些是 drc_auto.py 模板代码 bug，与 Python env 无关，不在本案范围。

## 合成决策

gold 依赖 live drc_auto.py（483 行）+ live module 系统 + live glibc → A-档 faithful 不可行（live 文件大、路径脆弱）→ **B-档 synthesized L1-boundary**：把多轮 env 排障离线化为 stdlib Python 解释器兼容性诊断器 `diagnose_drc_pyenv.py`，输入 error.log + shebang.txt + bashrc.env + module.env + modulefiles_catalog.tsv + glibc_compat.json + system_glibc.txt → 诊断 JSON（root_causes / shebang / module_env / system_glibc / failing_python_version / required_glibc_symbols / compatible_versions / recommended_python / env_fix / conclusion）。资产 A 忠实上述事实；hidden B（shebang 3.6.8 / module 3.12.9 / glibc 2.17，无 GLIBC 报错→仅 version_mismatch，recommended 3.12.9）+ B2（shebang 3.9.1 / module 3.11.0 / glibc 2.12→两者根因，recommended 3.10.5）防硬编 A 的 3.10.5/3.11。

## 正交性

正交于现有 physical_verify env 类 case：PDKQA-001 做 Calibre env（LD_LIBRARY_PATH/MGC_HOME/check_calibre_env），ERCFilter/ERCBootPlan/ERCFlowAether 做 ERC，ErcReconLicDiag 做 ERC license-error 根因 + calibre -recon flag，DRCTimeStats/DRConnTiming/DRCHierLossAudit 做 DRC log 拆解，DRCDeckWinClean 做 deck Windows 清洗，DRCReportIpAudit 做 DRC 结果 IP/Chip 分类。本案 = **DRC 自动化脚本 Python 解释器兼容性诊断**（shebang 版本 × module env × 系统glibc × 可用版本表 → 推荐版本 + env_fix），此前无同类。
