# Deep-read: 1792066483816_us0hd (e0039102 / hfeg0plg74 / mc=166)

## Trace facts
- session: 1792066483816_us0hd, user e0039102, host hfeg0plg74 (also replicated to hfeg0plg49)
- 294 msgs / 1.21 MB / scp'd to .75 /tmp/us0hd.messages.json
- kw: verilog:2918; .def:24; netlist:23; aether:20; analog:16; pyaether:8 → refined-A clean (a=2918, c=22, b=0, n=39; top_tool=verilog). aether/pyaether markers are low (20/8) vs verilog 2918 → A-dominant digital.
- agent: deepseek (lead), tools = list_allowed_files / read_files / editor (write .py) / run_approved_command (python-runner profile) / get_agent_policy_status. Policy engine enforcing (agent-policy.json).

## Two projects in one session
1. **ddgoa project (msg 0–81)** — the clean produce-task, used for this case.
2. drgsa project (msg 99+) — different format (.vpc files, run_vsim_uvs.pl), reused `/regr-case-filter` skill; multi-turn corrections. NOT used (different deliverable shape, longer/branchy).

## ddgoa produce-task (U#0, A-faithful ✓)
User原话 (msg 0):
> /rundata/ddgoa/V0/simdir/verilog/jason17w/regression/verilog.lpddr5.ddgoa.0812/run_normal_allconfig_noprobe_xrun_jack_UVS 这个目录文件下我需要挑选一部分case出来， x8 : ROC_Check; basiccheck; casops; datacopy; rdqstoggle; wckfree; wckosc; zqcal  x8_hibyte : acti2; dcm; ecc; loadmode; wcksync  x8_hibyte_mrconfig : auto; dca; mrr; wcksusp; zqcal_slvormst  x8_mrconfig : auto_direct; linkecc; powerdown; scan_allspeed; wrrrdqsttrain  x16 : auto_daap; cbt; fifordqsttrain; mrw_mrr; wckdqtrain; wrrdfifo  x16_hibyte_mrconfig : onebank; rdqspattern; twobgbank; wck2ckleveling; writex  文件格式还一样，你把其他case删除，只保留我要的这些，保留现在能运行的格式，写一个新文件，不要覆盖原文件

未给根因 → A-faithful 合格。

## Driver file format (real, parsed by agent)
- `#!/usr/bin/perl` shebang + blank line + `system("sleep 5");`
- Section headers (3 styles, order in file): `###-----------------for x16-------------#` → `########---------- x8---------------------------###` → `########---------- x8 hibyte---------------------------###` → `########---------- x8 hibyte mrconfig ---------------------------###` → `########---------- x8 mrconfig---------------------------###` → `########---------- x16 hibyte mrconfig ---------------------------###`
- Case lines: `system("./vsim_uvs -sr <case> [-b \"<bus>\"] -d \"LPDDR5G USESDF PWRBC   \" --noprobe -q bcp_LP1 ...");`
  - backslash-escaped quotes in raw file (`\"x8\"`)
  - x16 section has NO `-b` (bus absent); other sections have `-b "x8"` / `-b "x8 hibyte"` / `-b "x8 hibyte mrconfig"` / `-b "x8 mrconfig"` / `-b "x16 hibyte mrconfig"`
  - most cases commented (`#system(...)`), one active per section (x16: `auto`)
- 34 cases selected across 6 sections in the real run.

## Agent's deliverable + method (msg 81 summary)
- New file: `..._selected` (not overwrite). md5 of original unchanged.
- Method: parse each `vsim_uvs` line → record line no / `-sr` / commented? / `-b` → for each section keep only spec cases → strip leading `#` to make runnable → preserve shebang/blank/sleep/section headers/order/exact params → write new file + chmod 755.
- Flagged 2 spec typos: `acti2`→`act1act2`, `wrrrdqsttrain`→`wrrdrdqsttrain` (real names in driver differ from spec). Confirmed with user.
- Skill沉淀 (msg 82–98): `regr-case-filter` SKILL.md with 8 验收标准 + 6 已知陷阱.

## Synthesis plan — RegrCaseFilter-001 (digital L1 spec-driven code generator, B档)
- **deliverable**: `regr_case_filter.py` (纯 stdlib). CLI: `--driver <path> --spec <path> --out <path>`. Spec file format: lines `<group> : <case1>; <case2>; ...` (mimic user's exact format). 
- **parse**: detect section headers (regex on `###`/`#---`/`for <X>`/`<bus>` markers — robust to 3 header styles), parse `vsim_uvs -sr <case>` lines, track commented state + bus, group cases by current section.
- **filter**: per spec group, keep only listed cases; strip leading `#` (and any leading whitespace before `#`) to uncomment; drop non-listed cases. Preserve exact original line content (params unchanged) except the leading `#`.
- **emit**: shebang + blank + `system("sleep 5");` + iterate original sections in order, emit section header then kept case lines (uncommented). chmod 755 on out.
- **report** (stdout JSON): `{sections: [{name, kept: [cases], dropped: [cases]}], total_kept, missing: [{group, case} (in spec but not in driver), typos_suspected], original_md5, new_md5, orig_unchanged: bool}`.
- **A input**: driver_A.pl (6 sections, ~30 cases, mostly commented, x16 has no -b) + spec_A.txt (subset per group, all names valid). Hidden B: driver_B.pl (different section names: x4 / x8_lowpower / x16_dual / x4_hibyte; different case names; some spec cases MISSING from driver; prefix collision `basic` vs `basiccheck`; one case in spec for wrong group; bus values with spaces like `"x8 hibyte"`).

## 断言条件草案 (k≈14, will finalize in check.py)
a. zip 内 3 文件齐全 (regr_case_filter.py + driver_B.pl + spec_B.txt)
b. regr_case_filter.py 纯 stdlib (无 import 非 stdlib)
c. 输出文件以 `#!/usr/bin/perl` 开头
d. 第 2 行空、第 3 行 `system("sleep 5");`
e. 输出只含 spec_B 列出的且 driver_B 中存在的 case（missing 的被排除且在 report.missing 中列出）
f. 输出每个保留 case 行行首无 `#`（可运行）
g. 每个保留 case 行的 `-sr`/`-b`/`-d`/`--noprobe`/`-q` 参数与 driver_B 原行逐字节一致（仅去 `#`）
h. section header 全部保留，顺序与 driver_B 一致
i. prefix-collision 守卫：spec 写 `basic` 时不会误匹 `basiccheck`（精确名匹配）
j. wrong-group 守卫：spec 把 case X 列在 group G，但 X 只存在于 group H → X 不出现在 G 输出，且 report 标注
k. missing-name 守卫：spec 中的不存在 case 不被杜撰（不生成假 `-sr` 行），report.missing 非空
l. 原 driver_B 未被修改（md5 不变）—— check.py 独立重算 driver_B md5 与运行前后比对
m. report.total_kept == 输出文件中 `vsim_uvs` 行数
n. 输出文件 chmod 755（stat mode & 0o111）
o. spec 里 `;` 分隔 + `:` 分组的解析正确（多 case / 单 case / 空白都健壮）—— 用 B 的随机扰动验证
