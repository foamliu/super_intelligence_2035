# trace_deepread: 1789708302199_on45q — netlist signal-name batch renamer

**user**: bensonh  **host**: hfeg0plg104  **mc**: 49  **keywords**: netlist:146;verilog:4;vhdl:2;systemverilog:1;.cdl:1
**session file**: 1789708302199_on45q.messages.json (152KB, 42 msgs, 4 real user turns)
**scanned**: 2026-11-13 snapshot (ssh_eda_search_20261113_131349), peeked via .75 ssh cat.
**archetype (new)**: `netlist-signal-name-exact-batch-renamer` (word-boundary + bit-select-opener exclusion + `.prcsim` output). Distinct from NetlistIncludeRewrite (include path), NetlistPadDriverTrace (signal driver trace), NetlistHierModuleExtract (module body extract), StdcellFamilyRefMatch (family name scoring).

## Real user turns

- **U#1 (idx 0)** [核心 produce-task]: 「写一个脚本，将网表文件中名字为 RdEnL / EqIoL / RwEnNL / WrEnL / SapEnAmid / SapEnBmid / SanEnAmid / SanEnBmid / SapEnCmid / PreEqL / IsoL_E / OcEnL_E / SelL / EqMsamid / SanEnCmid / PCSL / NCSL 的信号名全部替换为 RdEn / EqIo / RwEnN / WrEn / SapEnA / SapEnB / SanEnA / SanEnB / SapEnC / PreEq / Iso / OcEn / Sel / EqMsa / SanEnC / PCS / NCS，然后将修改后的文件重新命名为原文件名+.prcsim，要求精确匹配，例如 RdEnL」(truncated mid-example)
- **U#2 (idx 1)** [重发 + 澄清]: 同 U#1，结尾补全「要求精确匹配，例如只将原文件中的 RdEnL 替换为 RdEn，不替换 RdEnL<1>」—— 明确给出 **bit-select `<1>` 不能替换** 的边界条件。
- **U#3 (idx 40)**: 已搭建电路网表（3 个 MOS XMMN0/XMMN3/XMMP3），「要利用平均电流法算出这三个 MOS」(finesim SPICE 仿真，B 域任务，未取)
- **U#4 (idx 41)**: U#3 澄清版 —— 给 3 个 MOS 栅极阶跃电压，阶跃前后 10ns 算平均电流 → Cgate，写 finesim 脚本。(B 域 spice，未取)

U#1/U#2 是同一任务重发（U#2 补全了 bit-select 边界示例），合成用 U#1+U#2。

## Agent work (produce-task#1, idx 2–39)

agent(get_agent_policy_status + list_allowed_files + run_approved_command[hello_world profile 被拒] + run_commands[被 Agent Policy 拦] + editor×N + read_files×N):
- 沙盒禁用 raw shell / dynamic Python（仅固定 hello_world profile 且 owner 不匹配被拒）→ agent 无法实跑验证，改为逐行审查 + 内置 `--selftest`。
- 产 `/home/bensonh/Desktop/rename_netlist_signals.py`：
  - `REPLACEMENTS` dict 17 对（用户给定顺序）
  - `_INDEX_OPENERS = "<[("` 位选开头字符集
  - `_ALTERNATION = "|".join(sorted(REPLACEMENTS, key=len, reverse=True))` **最长优先**
  - 正则 `(?<![A-Za-z0-9_])(NAME)(?![A-Za-z0-9_<[(])` —— 左 word-char lookbehind + 右 (word-char OR 位选开头) lookahead
  - `process_file`: 读 → `subn` 替换 → 写 `<input>.prcsim`（保留 newline="" 与 surrogateescape）
  - `selftest`: 27 case（17 映射 + 10 边界：`<1>`/`<1:0>`/`[3]`/`(0)`/`foo`/`xRdEnL`/`Rb_RdEnL_Rc` 混合）
  - CLI: `files*` + `-o/--output` + `--selftest`，打印 `(N replacement(s))`
- editor 多次因 payload 过大被拒 → 分块 insert；多次 `def selftest():` 顺序错位 → 修补 `main()` 落在 selftest 中间 → 最终结构正确。

## A-faithful 判定（合格）

用户**给了**: 17 对信号名映射表 + 「精确匹配」要求 + 边界示例（`RdEnL<1>` 不替换）+ 输出命名（原文件名 + `.prcsim`）。
用户**没给**: 正则/alternation 实现、最长优先排序、边界字符集（`<[(`，用户只举了 `<1>` 一例，`[`/`(` 是 agent 推广）、`--selftest` 设计、CLI 结构、surrogateescape/newline 处理。
→ A-faithful 合格（WHAT 充分，HOW 留白）。

## Deliverable / .75 可行性

deliverable = 写 `/home/bensonh/Desktop/rename_netlist_signals.py` + 改私有网表文件 → .75 SUT 沙盒无该路径、私有网表不进沙盒 → **INFEASIBLE** → **B 档合成**。
B 档：mapping 改为输入文件（`--mapping MAP.tsv`），A 给可见 mapping_A.tsv + netlist_A.v，B 隐藏 mapping_B.tsv（15 对，零名重叠 A，含 DataInL/DataInLp 前缀对测最长优先）+ netlist_B.v（不同模块 MEMTOP_B/LEAF_B，不同诱饵）。保留「精确匹配 + 位选排除 + `.prcsim` 输出」核心。

## 合成 case

**EDA-Eval-DesignFlow-NetlistSigNameRename-001** (digital, L1-B, B档, k=16)
- SUT 交 `rename_netlist_signals.py` (stdlib CLI `--mapping/--input/--out/[--report]`)
- 核心 trap: ① 位选 `<N:M>`/`[N]`/`(N)` 不替换（右边界排除 `<[(`）② word-char 前缀/后缀不替换 ③ `//` 注释内名字**要**替换（"全部替换"，无注释排除）④ 最长优先（DataInLp→DataInP 而非 DataIn+p）⑤ 默认 `.prcsim` 命名 ⑥ 跨输入守卫（B 名零重叠 A）⑦ 3-seed mapping 顺序无关
- check.py 16 条件 (a-p) 独立 subprocess 真跑 B + 显式 decoy/marker literal + 3-seed sha256
- 自验: ref SELFTEST PASS 16/16; 5 negative(naive_empty/print_only/hardcoded_A/str_replace_no_boundary/no_bit_select_guard) 全 FAIL; 3 fake(empty/garbage/print_string) 全 FAIL; 断言闸门 k_rationale=k_check=16 ✓
