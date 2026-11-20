# trace_deepread: 6f9zc — LPDDR6 cfg 格式转换 (vecgen_LP6 -> lp6vecgen)

- **session**: `1794885045965_6f9zc` (mike @ hfhds201 / 10.129.32.75)
- **match_count**: 174 (keywords: verilog:1704 / netlist:514 / pt_shell:78；实际内容 = LPDDR6 finesim 仿真 cfg 维护 — verification 域)
- **liveness**: ALIVE via SUBDIR path `/home/mike/.cline/data/sessions/1794885045965_6f9zc/1794885045965_6f9zc.messages.json` (1005827 B, 109 msgs). flat-path NOFILE 是 path bug（sessions 是子目录, .messages.json 在 `<ts>_<sid>/` 内），非 rotation 蒸发。
- **trace 源**: r808 A-pure scan fresh 候选；r810 liveness 复验 ALIVE，parked deferred（mixed verilog/analog, 优先级低于 yk8qc）；r811 兑现 DEBT 造题。

## 用户真实意图（原话）

U0：
> /ai_sandbox/dscqa/V0/agentdir/mike/sos_manage_lpddr6_random/verilog.lpddr6.decqa.finesim/analogsim_LP6/Config 我想把这个目录下的.cfg改成当前lpvecgen脚本适配的模式，接下来你工作在plan模式，我会帮助你理解转换规则

U7：
> cfg_new 是最新脚本适配的，我想把别的cfg改成这个格式，需要根据规则去匹配

U20：`NoBnk/NoAry 行保持 # 注释状态不转换，只转有效行`
U22：`5 角：FF1.23V-40C;FF1.23V130C;TT0.92V25C;SS0.92V130C;SS0.92V-40C（与 cfg_new 的 SC0/SC1 行一致）`
U30：`保持原名不动：coverage 侧 patterns/analogsim 里有对应的 S/、C/、T/、idd/ 目录和 Include 文件`
U32：`保持 x6 不变（新 vsim 直接认 x6）`
U34：`顶层 .cfg + 无后缀文件（SC0_Basic 等）+ cov_* 子目录全转，生成 .cfg.new`

后续 U76/U90/U91：让 agent 生成 lp6vecgen 的 userguide（本 case 不覆盖这部分，聚焦 cfg 转换脚本）。

## agent 工具链

- plan 模式：先读 lp6vecgen/vecgen_LP6 脚本源码 + cfg_new 样例 + 多个旧 cfg 文件，对齐转换规则。
- 写 `/home/mike/convert_cfg.py`（378 行，stdlib only：argparse/os/re/sys）。
- dry-run → 修 bug（非 UTF-8 cfg 用 GBK/latin-1 读；legacy 9-field；.swp 跳过）→ real run：152 候选文件，生成 151 .cfg.new，active=4531 / commented=10548 / NoBnk active=0 / problems=0。
- `validate()` 重解析 .cfg.new 模拟 lp6vecgen：8 字段 / speed 在表 / port 合法 / MR 非空 / 无 active NoBnk / 无重复 key。
- `count_new.py` 统计：port 分布 SC0=4076 / MCP=249 / SC1=206。

## 转换规则（从 convert_cfg.py 提取，作 ground-truth）

旧单 `[#][Tag:]V,tck,RL,WL,W,MR,TP,Bank` (8 列逗号) → 新 `[#]Pat Speed Width Port MR TP Bank Corner` (8 列空白对齐)。
旧双 `[#]2SC:V,tck,RL,WL,W,MR,TP,BankA, V,tck,RL,WL,W,MR,TP,BankB` (16 列) → MCP 行 `PatA;PatB speed x(2W) MCP MR TP BankA;BankB Corner`。

- tck→speed 18 项查表（0.278ns→14400 ... 3.75ns→1067；未列但 `\d+(\.\d+)?ns`→TM）。
- RL/WL 丢弃。
- Width 原样（x6 保持）；双行翻倍 x12→x24。
- Port：SC0 默认 / SC1（文件名以 SC1 开头）/ MCP（2SC 双行）。
- MR 去尾 `;`；空 MR → 转换失败（#[UNCONVERTED]）。
- TPara 去尾 `;`；空 → tCH50。
- Bank `<arch>_B<code>`→`<arch>_BL<code>`；`_BL/_BR` 不变；`NoBnk/NoAry` 结尾 → 行必须注释。
- Tag 前缀（2SC:/SCSWAP:/2001:）从 pattern 名去掉。
- 注释行保持 `#`，字段仍转。
- 不可转换 → `#[UNCONVERTED] <原文>` + warning。
- 已是新格式（整文件无逗号）→ SKIP。
- legacy 9-field：第5列纯数字+第6列 x→ 丢第5列；第5/6列同 x\d+ → 丢重复列。
- Corner 固定 5 角。
- 隐藏文件 / .new 跳过；cov* 子目录递归。

## 造题决策

- **域**：verification（LPDDR6 finesim stimulus vector cfg，属仿真验证流程的 cfg 维护）。
- **档**：B档 synthesized。原因：真实 /ai_sandbox/dscqa/.../Config/ 组私有 Permission denied（SUT 沙箱不可读），无法用真实 cfg 做 A 档 trace-faithful 附件。用 trace 提取的规则 + 真实样例结构合成 A 资产（LP6/dscqa 主题 pattern 名），B 隐藏资产用不同 pattern 名/tck/bank/文件集（防背题）。
- **判分范式**：S5 produce-task + hidden-B 真跑 + 独立 oracle。check.py 在隐藏 config_B 上 subprocess 跑提交的 convert_cfg.py，解析 .cfg.new 输出结构，20 条独立断言。
- **hidden-B 防背题**：B pattern 名/tck 值/bank/文件名均与 A 不同（A 用 S_NoBnk_MREffSC0/ParaMeta001/idd4w/SysMeta*；B 用 S_NoBnk_WffRff/PerBnk_ActWrPreActRd/PerBnk_ActCasWrWrCasRdRd + SC1_Golden/emptyMR/cov_1119/sub_test）。anti-hardcode 断言：源码不得含 B-distinctive token。

## 交付物

- `convert_cfg.py`（≥1000B，stdlib only）打包进 `outputs/submit.zip`。
- check.py 解 zip → py_compile → 在 B 上跑 → 20 断言。
- ref = trace 中 agent 的 convert_cfg.py（378 行，已验 PASS 20/20）。
- 5 negatives（empty/print_only/core_deleted/partial/hardcode_b）全 FAIL，命中 ≥4 不同断言组（⑤⑦⑨⑩ / ⑧⑫ / ⑬⑭⑳），证独立。
