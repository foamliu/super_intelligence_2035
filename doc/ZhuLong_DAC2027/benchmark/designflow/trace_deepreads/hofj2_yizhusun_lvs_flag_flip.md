# 深读笔记 — hofj2 (yizhusun @ hfeg0plg75) · LVS 比对开关翻转

- **session**: `1795158646140_hofj2.messages.json` (nmsg=40, mc=31, pure LVS: lvs:191;pdk:18;calibre:4;aether:1)
- **trace_source**: user=yizhusun, host=10.129.32.75 (hfeg0plg75), match_count=31
- **工作目录**: `/home/yizhusun/99_practice/G5_CIP/QA/practice_patternQA`

## 用户真实意图
"写一个名为 runme 的 gvim 文件，要求：将当前文件夹下的 lvsqa_config.ini 文件中，
`lvs_rightGds_rightCdl = 1` 替换为 `lvs_rightGds_rightCdl = 0`"
→ 切换 LVS 比对模式，关闭 right-GDS vs right-CDL 比对。

## lvsqa_config.ini 格式 (真实)
```
[General]
libName = decoa_lib
pdk_name = decoa_LvsQaldetest
lvs_rightGds_rightCdl = 1
lvs_rightGds_errorCdl = 0
lvs_errorGds_rightCdl = 0
extractSpfFlag = 0

[Paths]
csv_path = /home/yizhusun/99_practice/G5_CIP/QA/practice_patternQA/truth_table.csv
ldeTxt_path = /home/yizhusun/99_practice/G5_CIP/QA/practice_patternQA/newlde.txt
lvs_code_path = /apps/imctf/runset/calibre/cxmtG5_CIP/current/common/LVS/G5_CIP_LP6_lvs_v0d1_Rev10/calibreLVS.rule
lpe_code_path = /apps/imctf/cad/runset/decoa/v0/current/lpe_star

vttf_name = /home/yizhusun/99_practice/G5_CIP/QA/practice_patternQA/TF
Map_Name = /apps/imctf/libs/dfii/cxmtG5_CIP/current/layer.map
Drf_Name = /home/yizhusun/99_practice/G5_CIP/QA/practice_patternQA/display.drf
```
三键 `lvs_rightGds_rightCdl` / `lvs_rightGds_errorCdl` / `lvs_errorGds_rightCdl` = LVS 比对模式开关。

## agent 执行链
1. editor 改 `runme` → `sed -i 's/lvs_rightGds_rightCdl = 1/lvs_rightGds_rightCdl = 0/' lvsqa_config.ini`
2. run_approved_command(shell-runner) 报错: filePath 必须以 .sh 结尾 → 又建 `runme.sh`
3. shell-runner 跑 runme.sh: sed 报 "无法读取 lvsqa_config.ini: No such file or directory" (CWD 不是工作目录)
4. editor 改 runme 用 `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` + `INI_FILE="$SCRIPT_DIR/lvsqa_config.ini"` 锚定路径
5. 试图清理临时 runme.sh / cleanup.py / cleanup.sh (shell-runner/python-runner 后缀限制反复)

关键教训: 脚本要 CWD 无关 (SCRIPT_DIR 锚定)；shell-runner 要求 .sh、python-runner 要求 .py 后缀。

## reframe (case LvsFlagFlipRunme-001)
真实意图=脚本改 ini 一个 LVS 比对开关值。reframe 为可复用 CLI 工具 `flip_lvs_flag.py <ini_path>`：
原地置 `lvs_rightGds_rightCdl=0`、其余字节不动、stdout 打印 JSON manifest
(file/section/key/before/after/changed/total_lines/unchanged_lines)。未改变核心意图，仅升格为可判分 deliverable。

## 判分设计
- 公开 A = 真实 lvsqa_config.ini 原样；隐藏 B (8 键 [General]+7 条 [Paths]+[Options]) 主判分；
  隐藏 B2 (libName/pdk_name/paths 全异) 反硬编。
- check.py 独立 oracle (集合/索引重算) 13 条断言 a-m；
  4neg(stub_noop/stub_print_only/stub_delete_core/stub_hardcode_b) 全 FAIL distinct；
  §4.9 三假 (a空壳/b只print/c删核心) 全 FAIL。
- 自验: ref 13/13 PASS, 4neg 全 FAIL (noop fail c,d,e,j,k,l,m; print_only fail d,e,j,k,l,m;
  delete_core fail d,j,k,l,m; hardcode_b fail l,m)。
