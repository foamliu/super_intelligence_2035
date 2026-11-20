# Deepread — wlw3b — DRC QA tool (DrcQa.py) run-failure root-cause diagnosis

**session**: `1793686357167_wlw3b` (e0047722 @ hfeg0pkn001, 10.129.2.10; login node hfeg0plg76)
**mc**: 85 (drc:1658;pdk:221;.gds:95;skipper:48;calibre:41;lvs:1) — strong physical_verify
**trace**: .75 scp 273KB / 43 msgs / 2 real user turns (2026-11-04)
**audit**: r846 fresh deepread. r537 peek parked「Q&A/sim/run-existing」(旧规则 reject)；2026-11-15 reaudit 后 debug-Q&A/env-config 合法 → revival 可造。
**case**: EDA-Eval-DesignFlow-DrcQaRunDiag-001 (physical_verify L1 档 B reframe, debug-Q&A/env-config)

## 真实用户意图

- **U#1** (msg0) 逐字：「帮我看下/home/hbpeng/drcqa/DRC/DrcQa.py这个脚本是咋用的？」
  → 助手 read_files/search_codebase/run_commands 读 DrcQa.py (800+行, line-by-line), 产详细使用说明 (CLI 参数表 16 项 + 14 检查项 + 运行方式)。
- **U#2** (msg26) 逐字：运行命令 `python3 /home/hbpeng/drcqa/DRC/DrcQa.py -c config.ini -ci drcWithPattern` + 完整 traceback (PermissionError)。
  → 助手读 LoggerUtil.py / __init__.py / DrcSyntaxCheck.py / config.ini，诊断根因 + 给 3 套解决方案。

## 根因链（双层，互相独立）

1. **权限层**：运行目录 `/apps/imctf/develop/PDK_QA/DRC/test/drcWithPatternCheck/case1/` owner uid=3333/group=504；当前用户 e0047722 (uid 205260, groups[555]) 不在 group 504，目录 drwxr-xr-x 无 world-write → 无写权限。脚本在模块导入阶段试图在 cwd 创建 `pdkQa.log` → PermissionError。
2. **代码 bug 层**：DrcQa.py 第5行 `os.environ['forbidFileLog']="true"` 意图禁文件日志。但 LoggerUtil.py：
   - `getLogger()` (line 24) ✅ 检查：`if FileUtil.canWrite(logPath) and not os.environ.__contains__("forbidFileLog")`
   - `getConsoleAndFileLogger()` (line 50-63) ❌ **完全不检查** forbidFileLog，总是 `logging.FileHandler(filename=logPath)`
   - `getPdkQALogger()` (line 47-48) `return getConsoleAndFileLogger(name, "pdkQa.log")` → 调用不检查环境变量的函数 → bug，forbidFileLog 保护被绕过。

## trace-faithful 资产（A）

- `drcqa_script_A.py`：摘自真实 msg2/msg38（第1-41行 + argparse 16 参数 + SUPPORTED_CHECK_ITEMS 14 项）。真实 line5 `os.environ['forbidFileLog']="true"`、line33 `logger=getPdkQALogger(__name__)`、toolVersion=1.1.0。
- `logger_util_A.py`：摘自真实 msg29（71 行逐字）。getLogger line24 检查 forbidFileLog；getConsoleAndFileLogger line50-63 无检查；getPdkQALogger line47-48 调 getConsoleAndFileLogger name,"pdkQa.log"。
- `traceback_A.log`：摘自 U#2 真实报错。import 链 DrcQa.py:6→DRC/__init__.py:7→DrcSyntaxCheck.py:5→Checker.py:4→DrcInfo.py:8→LoggerUtil.py:48 getPdkQALogger→:63 getConsoleAndFileLogger→logging __init__:1092→_open:1121。`PermissionError: [Errno 13] Permission denied: '.../case1/pdkQa.log'`。
- `cwd_perm_A.txt`：摘自助手 msg42 诊断。uid 3333/group 504/e0047722 uid 205260 groups[555]/cwd_writable=false。
- `config_A.ini`：本次运行配置（process G5/product DDCPA/version 0.6.2/drc/gds/checkItem drcWithPattern）。

## hidden B（反 A，10 轴全异）

LvsQa 工具（同结构，全置换）：envvar=skipFileLog、log=lvsQa.log、failing_fn=getFileLogger、checking_fn=getStreamLogger、error=FileNotFoundError（缺目录 missingdir）、user=linwei、uid=4321/group=8000（group 匹配但缺中间目录）、CLI -r/-deck/-net（非 -drc）、check items lvs*（非 drc*）。候选必须 regex 解析，不能硬编码 A 答案。

## 档 B reframe

A 档 gold=助手 free-text 使用说明+根因诊断（prose，依赖 live 文件 /home/hbpeng/drcqa 不可达，无 ≥8 独立硬断言牙）→ reframe 为离线纯 stdlib 诊断器 `diagnose_drcqa_run.py`，CLI `<drcqa_script.py> <logger_util.py> <traceback.log> <cwd_perm.txt> <out.json>`，输出结构化 JSON（tool_name/env_var_set/log_filename/cli_args/check_items/traceback/forbidfilelog_audit/permission/root_causes/solutions/conclusion）。

## 自验

- ref check.py → 16/16 PASS (a-p)
- negative_selftest → REFERENCE PASS + 4 negs 全 FAIL，first_fail 标签 distinct (a / c / f / c)
  - §4.9(a) empty → a (zip/compile)
  - §4.9(b) print_expected → f (cli_args B 专属缺)
  - §4.9(c) core_deleted → c (tool_name null != LvsQa)
  - anti-hardcode hardcode_a → c (tool_name DrcQa != LvsQa)
- k_rationale = k_check = 16 ≥ 8 ✓
- roundtrip: jsonl test sha16 == disk check.py sha16 ✓
- attachments 无 hidden/ ✓
