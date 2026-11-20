# 深读 trace 记录：x4b0p（PDK QA DRC 框架迁移 · Calibre VCO 环境绕过）

> 即时令 IX §五 要求：本轮先深读 1 条真实 trace，理解完整对话流，下一轮提炼成 case。本文件为脱敏深读笔记。
> 原始 messages.json 2.07MB / 537 msgs / 299 user / 238 assistant / 286 tool_result，
> 已 scp 到 .75 workdir 解析后 close_session keep=false cleaned（不入库，不入 git）。
> 与已用的 ukkn7（haoyut? no—ukkn7=e0031668/ERC-aether）、9knot（vincelu/SiliconSmart）和并行 agent 的 m2vah（e0014566/rscalc-autovia）**无交集**（不同用户 xinqiaoz / 不同主题 PDK QA DRC 迁移 / 主机 hfeg0pkn004），避免冲突。

## trace 来源（脱敏）
- host: `hfeg0pkn004`（10.129.2.13；同 session 亦出现在 hfeg0plg56/hfeg0plg76/hfeg0plg17/hfeg0plg49，NFS 共享 home）
- user_hash: `7fa3eec75ddd`（sha1[:12] of real username xinqiaoz）
- session_file: `1788770994295_x4b0p`（实际路径 `<ip>:/home/xinqiaoz/.cline/data/sessions/1788770994295_x4b0p/1788770994295_x4b0p.messages.json`，2,070,609 字节）
- session_msgs: 537
- summary.tsv match_count: **1367**（dedup 后该 session 排名第 2，仅次于 ukkn7 1478；高于 9knot 862）
- keywords: `calibre:4451;pdk:2168;.gds:149;synopsys:56;skipper:37;hspice:20;aether:19;.def:3`
- tool_use 分布: run_commands 141 · editor 113 · read_files 28 · search_codebase 2 · RAG search 1 · skills 1
- real_task_summary: **PDK QA System（pdkQaSystem）Windows→Linux 迁移**——4 阶段（Phase 0 环境建立 / Phase 1 代码理解 / Phase 2 测试建立 / Phase 3 技能安装），核心卡点是 **Calibre 2020.1_36 在 RHEL 8（VCO=aok）上的 VCO autoswitch 环境基础设施 bug**，最终以"假 MGC_HOME + stub libXss"绕过方案解决，6 项 Pattern QA 验证"能启动"。

## 用户真实目标（13 条 user message 提炼）
用户手头有一个 **PDK QA System**（`/home/xinqiaoz/PDK_QA/pdkQaSystem/`，Windows 副本迁移到 Linux），由"Windows AI"做架构设计、"Linux AI"（本 trace 的 agent）做执行，分阶段推进：

- **Phase 0（环境建立）**：读 `migration_package/README.md` + `MIGRATION_SOP.md`，建 `CLAUDE.md`/`rules/`/`docs/`/`business_background/`，产 `PHASE0_REPORT.md`。关键发现：`IMCP/` 是符号链接→共享基础设施**未经授权不修改**；`which calibre` 直接在 PATH。
- **Phase 1（代码理解）**：读 `DRC/DrcQa.py`（主入口）+ `common/Checker.py`（基类）+ `common/deckInfo/`（DrcInfo/CalibreDeckInfo）+ `common/designManual/`（LdrInfo/LayerDefinition/TruthTable/FractureTable/EdrInfo）+ `DRC/text/` + `DRC/pattern/` 各 checker；从 `DrcQa.py` 提取 `supportFuncnames` 实际清单；为每个 checker 写详细设计文档到 `docs/checkers/`；扩展 `CLAUDE.md` §4.3 路由表；修 `docs/` 里不适用的 Windows 描述。
- **Phase 2（测试建立）**：先解决 2 个环境问题（Python `libpython3.7m.so.1.0` 缺失；Calibre VCO `aok` vs `aoi`），建 `DRC/tests/` 目录，为 17 个已注册 checker 建冒烟测试，跑出基线，记 PASS/FAIL。**关键纠偏（USER #6 idx 208）**：agent 非交互不加载 `.bashrc` → 不继承 `module load calibre` → 用户指示"直接看我的 .bashrc 继承脚本环境"。
- **Phase 3（技能安装）**：安装 `drc-rule-explainer` 技能，`svrf_ur_2020.md`（SVRF 手册 6MB）由用户手动就位，验证 rule 解释流程（定位 rule→递归展开 layer→查操作符→产中文解释）。
- **核心需求**：分阶段推进，每阶段产 REPORT 由 Windows AI 审核；**不修改用户源码**（发现问题只记录在 report）；最终 git commit。

## 17 个已注册 checker（supportFuncnames，从 DrcQa.py 提取）
1. ldr · 2. drcSyntax · 3. drcLayerMap · 4. drcValue · 5. drcOption · 6. drcPowerList · 7. drcDeriveLayerVsFracture · 8. drcDeriveLayerVsFractureAndTruthOverall · 9. uselessDeriveLayer · 10. patternDeviceLayer · 11. patternLayerVsFracture · 12. emptyDeriveLayer · 13. drcWithPattern · 14. patternLayerVsDesignRuleLayerChange · 15. drcConsistencyWithChangedLdr · 16. drcCountWithinOption · 17. antMetalThk

- 11 个 **text checker**（不依赖 Calibre 运行）：ldr / drcLayerMap / drcValue / drcOption / drcPowerList / drcDeriveLayerVsFracture / drcDeriveLayerVsFractureAndTruthOverall / uselessDeriveLayer / drcConsistencyWithChangedLdr / drcCountWithinOption / antMetalThk
- 6 个 **Pattern QA checker**（依赖 Calibre/calibredrv 运行）：drcSyntax / emptyDeriveLayer / patternDeviceLayer / patternLayerVsFracture / patternLayerVsDesignRuleLayerChange / drcWithPattern
- 死代码：`drcRuleContainsDeriveLayer` 未注册（用户未确认恢复，保持死代码状态，不改 supportFuncnames）

## 🎯 核心技术卡点：Calibre VCO 环境基础设施 bug（建 case 的"牙齿"来源）

### 现象
所有 Calibre 命令（`calibre`/`calibredrv`/`rules_syntax_checker`）在 agent 非交互进程中报 VCO 错误退出。用户在自己终端跑正常。

### 根因（agent 深挖 calibre_env 脚本 line 124-189 后定位）
- 机器 OS = **RHEL 8（VCO=`aok`）**，但安装的 Calibre 2020.1_36 树是 **`aoi`** 版本。
- agent 作为非交互进程**不加载 `.bashrc`** → 不执行 `module load calibre` → `CALIBRE_HOME` 未设置。用户的交互 shell 因有 `CALIBRE_HOME=/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18` 而跳过 autoswitch，直接用 aoi 树。
- **但**：`calibre_env` 脚本**无条件**运行 `calibre_vco` 检测 OS（返回 `aok`），然后执行 autoswitch 逻辑。autoswitch 中的 grep：
  `echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'`
  有 **shell 变量名解析 bug**：`$SW_WKSTN_` 和 `$MGC_VCO_` 被 bash 解析为**含下划线的变量名**（空值），而不是 `$SW_WKSTN` 后接 `_` → grep 匹配失败 → autoswitch 未启用 → 找不到 aok 树 → 报错退出。
- `CALIBRE_SKIP_OS_CHECKS=1` 也不能跳过此检查。

### 方案演进（关键 — 这就是 case 的"牙齿"）
1. **临时 hack 方案（agent 首创，实测有效）**：假 `MGC_HOME` 目录 + 一个返回 `aoi` 的 `bin/calibre_vco` stub 脚本跳过 VCO 检查 + stub `libXss.so.1`（缺失的 lib 依赖）+ `LD_LIBRARY_PATH` 指向真实 aoi lib（`pkgs/mgls.aoi/lib`/`shared/lib`）+ 本地 `lib/` + `/tmp`。6 项 Pattern QA 验证"能启动"（启动→kill→清理，exit=124 来自 timeout 证明 calibre 已启动在跑）。
2. **Windows AI 正规方案（设 `CALIBRE_HOME`）**：agent 按指示把 test_env.py 改成只设 `CALIBRE_HOME`/PATH/`LD_LIBRARY_PATH`（删 hack）。**实测无效**——VCO 错误回归（因 calibre_env 无条件跑 calibre_vco）。Windows AI 审核结论：确认这是 Calibre 安装环境的 bug（calibre_env 脚本 shell 变量名解析问题），**非应用层可修复**。
3. **最终方案（USER #11 idx 433 指示恢复）**：恢复 hacky 绕过方案（假 MGC_HOME + libXss stub），并要求 test_env.py 导入时**自动重建**（检查 `/tmp/calibre_fake_home/` 和 `/tmp/libXss.so.1` 是否存在，不存在则重建）。定性为"环境基础设施 bug，非项目责任"，记 `docs/known_issues.md` K10。

> **case 牙齿**：naive agent 会采用"干净的正规方案"（只设 `CALIBRE_HOME`）→ **必须 FAIL**（实测无效）；正确答案必须实现假 MGC_HOME + stub libXss 的 hacky 绕过 + 自动重建。test 校验器要能区分这两者。

## test_env.py 结构（agent 最终版，hacky 绕过恢复后）
```python
# test_env.py — Shared test environment setup for DRC QA tests.
# Replicates .bashrc + module load calibre for non-interactive processes.
# Environment infrastructure note: Calibre 2020.1_36's calibre_env script has a
# shell variable name resolution bug on RHEL 8 (VCO=aok) ... (workaround below:
# fake MGC_HOME + stub libXss) is a test environment adaptation.
import os, subprocess, sys

_REAL_CALIBRE = "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18"
_LIB_PATHS = [f"{_REAL_CALIBRE}/pkgs/mgls.aoi/lib", f"{_REAL_CALIBRE}/shared/lib",
              os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"), "/tmp"]

# 1. Python: fix libpython3.7m.so.1.0 not found
_lib_path = "/apps/local/python/python-3.7.1/x86_64/lib"
if _lib_path not in os.environ.get("LD_LIBRARY_PATH", ""):
    os.environ["LD_LIBRARY_PATH"] = _lib_path + ":" + os.environ.get("LD_LIBRARY_PATH", "")

# 2. forbidFileLog (suppress calibre file logging) + sys.path setup

# 3. Calibre VCO bypass: fake MGC_HOME with bin/calibre_vco returning 'aoi' + stub libXss.so.1
#    auto-rebuild at import: check /tmp/calibre_fake_home/ and /tmp/libXss.so.1 exist, rebuild if missing
def _setup_calibre_env(): ...   # create fake MGC_HOME + stub libXss, set LD_LIBRARY_PATH
def check_calibre_env(): ...    # returns (ok, msg); pre-sets up bypass at import
def get_real_path(case, fname): ...
def chdir_to_data_dir(path): ...  # Linux DrcInfo.readDrc() uses CWD to resolve INCLUDE relative paths
def print_result(name, ok, msg): ...
```

## agent 工作过程（141 run_commands + 113 editor）
1. **Phase 0**：建 CLAUDE.md/rules/docs/business_background；记 IMCP 符号链接、`which calibre` 直接返回、非 DRC 目录（LPE/LVS/PCELL/bin/conf/tools 已 .gitignore）。
2. **Phase 1**：逐个读 checker 代码，写 17 份 `docs/checkers/<name>_detail.md`；提 supportFuncnames 清单；修 docs 里 Windows 描述（SoftPlug 已删、pexpect/xlwt/xlrd Linux 原生可用）。
3. **Phase 2**：
   - 解决 Python：`LD_LIBRARY_PATH` += `/apps/local/python/python-3.7.1/x86_64/lib`（libpython3.7m.so.1.0）。
   - 解决 Calibre VCO：3 段方案演进（见上）。
   - 建 `DRC/tests/`（17 子目录 + `run_all_tests.py` + `test_env.py` + `shared/` 符号链接到真实 case 数据 `0806_zhaowei`/`0907_qianxue`/`0811_bq`）。
   - 11 text checker 冒烟 PASS；drcSyntax PASS（`rules_syntax_checker` 8s 完成输出 "syntax check fail" status=False）；6 Pattern QA "能启动"验证（启动→kill→清理，无残留 calibre 进程）。
   - 关键发现记 PHASE2_REPORT §9 给 Windows AI：① INCLUDE 相对路径需 chdir ② drcValue 真实数据 30-60s（1663 行 LDR vs 2647 DRC rule）③ drcCountWithinOption 无多 sheet/option 返 `notCheck` ④ EdrInfo.py `import attr` 是死代码（`@dataclass` 来自 dataclasses 非 attrs），删除可消 attrs 依赖使 antMetalThk 不 SKIP，但按用户要求未改源码 ⑤ F1 需 vdms_precise 专用 case。
4. **Phase 3**：装 drc-rule-explainer 技能，`__svrf__.md` 初始空逐步填，验证 rule 定位→layer 展开→操作符查询→中文输出。
5. 收尾 git commit。

## 从本 trace 提炼 case 的方向（下一轮 §三 固化）
- **domain**: `physical_verify`（DRC/PDK QA 测试环境建立）。新 case id 建议 `EDA-Eval-DesignFlow-PDKQA-001` 或 `EDA-Eval-DesignFlow-DRC-EnvSetup-001`。
- **prompt（自然语言，无函数签名）**：给定 PDK QA System 迁移包（DrcQa.py 含 17 supportFuncnames + DRC/tests/ 骨架 + 真实环境症状描述：libpython3.7m.so.1.0 缺失 + Calibre VCO aok/aoi autoswitch 报错 + calibre_env grep bug 摘录），在沙盒里建 `test_env.py`（解决 Python lib + Calibre VCO 绕过 + 自动重建 + 辅助函数）+ `smoke_report.md`（17 checker 冒烟结果）+ `PHASE2_REPORT.md`（环境问题分析），打包 `outputs/submit.zip`。约束：不改 supportFuncnames、不依赖真实 calibre 运行（沙盒无 calibre 安装，方案要能在无 calibre 环境下被静态校验）。
- **attachments（合成资产，仿真实结构含真缺陷）**：
  - `DrcQa.py`（含 17 项 supportFuncnames + 双 deck 处理骨架）
  - `calibre_env_excerpt.sh`（含 `echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'` 的 bug 行 + calibre_vco 无条件调用）
  - `env_symptoms.txt`（libpython3.7m.so.1.0 not found + VCO=aok ERROR + 非交互不加载 .bashrc + CALIBRE_HOME 已设仍报错）
  - `tests_skeleton/`（17 子目录 run_test.py 骨架 + run_all_tests.py）
  - `known_issues.md`（K10 占位）
- **entry_point**: `outputs/submit.zip`
- **test（Python `check(deliverable, workdir)` 双参，本地静态校验，无需 calibre）**：
  - (a) zip 含 `test_env.py`/`smoke_report.md`/`PHASE2_REPORT.md`
  - (b) test_env.py 设 `LD_LIBRARY_PATH` 含 `python-3.7.1/x86_64/lib`（修 libpython3.7）
  - (c) test_env.py 实现**假 MGC_HOME + stub libXss**绕过（**牙齿**：只设 CALIBRE_HOME 的"正规方案"→ FAIL，因 calibre_env 无条件跑 calibre_vco）
  - (d) test_env.py 有导入时**自动重建**逻辑（检查 /tmp/calibre_fake_home、/tmp/libXss.so.1 存在）
  - (e) test_env.py 有 `check_calibre_env()` 返回 (ok, msg)
  - (f) smoke_report 列全 17 supportFuncnames，结果正确（11 text PASS / drcSyntax PASS / 6 pattern "can start"或 SKIP-by-VCO-resolved）
  - (g) PHASE2_REPORT 正确定位根因（calibre_env `$SW_WKSTN_` 变量名解析 bug）且记正规方案(CALIBRE_HOME)无效+hacky 恢复
- **test 语言**：Python（全本地自测，无需 eda_flow 沙盒，同 Characterization-001 模式）
- **trace_source metadata**：host hfeg0pkn004 / user_hash 7fa3eec75ddd / session 1788770994295_x4b0p / 537 msgs / match_count 1367 / real_task_summary "PDK QA DRC 框架 Windows→Linux 迁移，Calibre VCO aok/aoi autoswitch bug 以假 MGC_HOME+stub libXss 绕过，17 checker 测试建立"

## 与既有 case 的关系
- 第 3 条 proper design_flow case（前两条：Verification-001/ukkn7 ERC-aether、Characterization-001/9knot SiliconSmart）。
- 扩 domain：physical_verify（DRC 测试环境建立）。既有 5 条 physical_verify 均为 legacy scripting 口径；本 case 为该域首条 proper design_flow。
- 牙齿机制与 Characterization-001 同源：真实 trace 里"看似干净的正规方案被实测证伪、必须用 hacky 绕过"——naive agent 易踩"正规方案"陷阱。
