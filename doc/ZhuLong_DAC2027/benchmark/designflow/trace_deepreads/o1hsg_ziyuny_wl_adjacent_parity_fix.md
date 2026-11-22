# deepread: o1hsg — ziyuny wl-adjacent-detect skill refactor (parity_of bug)

- session: `1795092542726_o1hsg` (221 msgs / 1.56 MB)
- user: ziyuny (PDK/DRC 工程师, E0017932)
- host: hfeg0pnd001 / 10.129.32.189
- mc: 188 (drc:1469; calibre:522; pdk:187; .gds:167; lvs:19) → physical_verify
- claim: r974, `trace_ledger.py --shard C claim` exit 0
- case: `EDA-Eval-DesignFlow-WlAdjacentParityFix-001` (subpattern `wl_adjacent_parity_bit_fix`, k=12)

## trace 真实任务

ziyuny 迭代打磨 `wl-adjacent-detect` skill（`/home/ziyuny/.cline/skills/wl-adjacent-detect/`），
用 Calibre DRC deck 检测 WL（word-line）相邻对。8 轮用户消息：

1. 读 skill（SKILL.md + references/ + scripts/）
2. 用 PDK 友好术语重写 DRC deck 中的 DRC 术语
3. 在沙盒测 `rundrc.sh` / `runme.sh`
4. 用 skill-creator meta-skill 重组 skill 结构
5. 把个人调试目录 `/home/ziyuny/zl/wl_adjcent/` 的资产（GDS、deck、parse 脚本、12 份 .rep）
   迁进 skill 自身的 `scripts/` / `references/`
6. 把所有绝对路径改写成 skill 相对（`SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)`）
7. 在敌对 CWD `/tmp` 下零参数验证 `rundrc.sh`
8. 最终 QA：自建 `202611202020` 时间戳目录、从自己所在目录取 deck/GDS、提交 DONE，
   结果与前几次一致（806 对 / 529 WL）

工具：editor(60) / run_approved_command(28, python-runner profile) / read_files(22)。
agent 成功收敛。

## skill 资产（reference）

- `SKILL.md` (14950 B)
- `references/`: absolute-path.md / architecture.md / troubleshooting.md / wl_adjcent_llm.md
- `scripts/`:
  - `A_mblx744_e_wlo_WL.gds` (2.6 MB)
  - `census_names.sh`
  - `parse_wl_pairs.py` (11110 B) ← 本 case 的判分对象
  - `rep2csv.py`
  - `rundrc.sh` (205 行)
  - `wl_adjacent.drc` (24885 B)

## parse_wl_pairs.py 的 parity_of bug（判分点）

`parse_wl_pairs.py` 把 Calibre RDB 输出的 per-source CLUSTER 报告
（`wl_pairs_{m1,m2,m3}_{hsp,m3a,m2a,m1a}.rep`，每行
`CLUSTER <"nameA" ["nameB" ...]> CELL <cell> x1 y1 x2 y2 ...`）
按 `(metal, cell, vertices)` 合并成 WL 相邻表，并用 `--parity {odd,even,split}`
把相邻对按奇偶分类到 `<out>_odd.rep` / `<out>_even.rep`。

严格名 `^s[0-9]+m[0-9]+wl[oe]<[0-9]+>$` 含两个坐标轴：
- `wl[o|e]`：行标记（row marker）
- `<bit>`：末尾 bit 号

**bug**：v1.0 的 `parity_of(name)` 用 `wl[o|e]` 行标记判奇偶（`wle→'e'`、`wlo→'o'`）。
**正确**：奇偶应取末尾 `<bit>` 数字的奇偶（`<1>/<3>→'o'`、`<0>/<2>→'e'`），
`wl[o|e]` 行标记是另一个坐标轴，必须忽略。

当 `wle` 名带奇数 `<bit>`（如 `s00m0wle<1>`）或 `wlo` 名带偶数 `<bit>`
（如 `s11m1wlo<0>`）时，buggy 版把奇偶分错，导致 `_odd`/`_even` 表分类错误、
stdout `pairs: total ..., odd-odd ..., even-even ...` 计数错误。

## case 合成

- A（公开）：`reports_a/`（4 .rep，含多成员簇/单成员/空向量/legacy PAIR/chain-overlap）
  + `parse_wl_pairs_buggy.py`（v1.0 有 bug）+ `task_brief.md` + `hidden_manifest.json`
- 隐藏 B：3 seeded 报告集（seed_1/2/3，cell 名/名号/坐标/金属分布/wl-vs-bit 组合全不同）
  - ref odd/even = 2/3、1/5、5/2
  - buggy odd/even = 6/1、4/2、4/4（全错且各不相同）
- check.py：12 条独立断言（zip/py_compile/3B rc==0/total/odd-odd/even-even/main/odd/even/
  audit/unnamed 内容==独立复算/确定性 PYTHONHASHSEED md5）
- reference solve.py = 修好 parity_of 的 parse_wl_pairs.py → PASS
- 5 negatives（empty_shell/print_only/delete_core/naive_stub v1.0 bug/hardcode_a）→ 全 FAIL
- negative_selftest.py 全绿

## 为什么这个子问题干净可判分

- 纯 Python 离线：parse_wl_pairs.py 只读 .rep 文本、写 .rep 文本，不调 Calibre/DRC deck
- bug 单点（parity_of 一函数）、症状明确（计数 + 表内容错）
- B 可随机化（3 seeds，计数各异，反硬编码）
- 沙盒无需 Calibre / GDS / DRC deck，SUT 只需修一个 .py
