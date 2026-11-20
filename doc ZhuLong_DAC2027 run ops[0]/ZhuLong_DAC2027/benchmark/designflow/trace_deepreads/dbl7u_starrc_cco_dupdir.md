# deepread — dbl7u (raylei @ hfeg0plg103) — starRC cco coupling-cap extraction debug-fix

**session**: 1795052358945_dbl7u · user raylei · host hfeg0plg103 (10.129.8.235) · mc=11
· kw drc:660/pex:638/calibre:5/lvs:4/.gds:4 — clean physical_verify (pex dominant)
· 61 msgs / 1 real user turn (duplicated U#1/U#2 — same input re-sent)

## 用户原话 (verbatim, U#1)
「Folder "./IDP_XC2" contains a script "dataSet.py" which is designed to
extract coupling capicitance from startRC runnings (relevant starRC running
files have been linkd to the folder "./cco_extract"), while some error
happens during running the script. Errof information has been recorded in
./IDP_XC2/dataSet.log. Please debug this problem. The dataset just befort
the exit() has benn stored in ./IDP_XC2/dataDebug.pkl (in pandas.DataFrame
format)」

意图分类：**debug-fix**（修一个跑挂的提取脚本），deliverable = 修好的 dataSet.py。
domain = physical_verify / pex (starRC parasitic extraction)。

## 助手 gold 调查链
1. `list_allowed_files ./IDP_XC2` + `read_files dataSet.py, dataSet.log`
2. `read_files dataSet.log:2300-2350` + `dense12_ntn_l2_w4_nf1_M0U1_PC1.spf` (starRC SPEF-like .spf)
3. editor `_debug_analyze.py` (load dataDebug.pkl → shape/columns/dup groups) — 失败：pandas 3.7 不支持 pickle protocol 5
4. editor `_debug_spf.py` — 数 `*|NET` 行：1996 unique nets, 0 dups in one file
5. editor `_debug_spf2.py` — 读 `cco_extract/job8-dense12_.../LPE/*.spf` (19MB) — 1996 nets, prefix histogram S:665 D:665 G:665
6. editor `_which_python.py` — 发现 python3.11.7 可用（pandas 在 3.7）
7. editor `_scan_spf.py` — **关键发现**：397 job dirs / 397 spf files，但 `dense12_ntn_l2_w4_nf1_M0U1_PC1.spf` 出现在 2 处：
   - `cco_extract/job8-dense12_ntn_l2_w4_nf1_M0U1_PC1/LPE/dense12_ntn_l2_w4_nf1_M0U1_PC1.spf`
   - `cco_extract/test/LPE/dense12_ntn_l2_w4_nf1_M0U1_PC1.spf`  ← **stray `test/` dir**
8. editor `_verify_filter.py` — 验证：用 `re.match(r"^job\d+", f)` 过滤后 396 dirs，`test` 被排除，0 topcell 重复
9. **editor dataSet.py (idx 49, gold fix, 670B)** — 把目录选择改成只取 `^job\d+` 的真 job 目录：
   ```python
   dirs = [
       os.path.join(xcdir, f, lpedir)
       for f in os.listdir(xcdir)
       if os.path.isdir(os.path.join(xcdir, f, lpedir))
       and re.match(r"^job\d+", f) is not None
   ]
   ```
10. `_syntax.py` 验证 dataSet.py compiles OK + `import re` present
11. `_cleanup.py` 删调试脚本

## 根因
`dataSet.py` 原本扫 `cco_extract/` 下**所有**含 `LPE/` 的子目录。一个游离的 `test/`
目录里也有一份 `dense12_..._PC1.spf`（与 `job8-.../LPE/` 同名 topcell）→ 同一 topcell
被解析两遍 → `(topcell, order, terminal)` 行重复 → `readSpfCap` 的 "more than one
*|NET entry" / 重复对检查 abort → `exit()` 存 dataDebug.pkl。
**fix** = 目录过滤 `^job\d+`，排除 stray 目录。

## .spf 格式 (starRC SPEF-like)
- `*|NET <name> <cap><unit>F` 行：name 如 `S_MN494`（terminal 前缀 S/D/G + _MN<order>），
  cap 如 `12.3pF`（unit f/p/n/u/m → farads）
- terminal = name.split('_')[0] ∈ {S,D,G}；order = name 中数字；cap_farads = 单位换算
- 重复检测：同一 topcell 的 (order, terminal) 必须唯一

## reframe 设计（档 B fixture-driven judge）
真实 gold 依赖 397 个 19MB .spf + pandas + pickle（不可复现）。reframe 为
**fixture 驱动的 parser-fix judge**：
- 可见 A：小型 `cco_A/` 树（3 个 .spf：job1_inv、job2_buf、stray test/inv 重复）+ bug 版
  `extract_cco_buggy.py`（扫所有目录 → 重复 abort）
- 隐藏 B：不同 topcell 名/网表/电容值/stray 目录（scratch/）的 `cco_B/` 树
- 候选交付 `extract_cco.py`（修好版），CLI `extract_cco.py <cco_dir> [-o out.json]`，
  只扫 `^job\d+` 目录、解析 `*|NET` 行、单位换算、输出结构化 JSON、无重复 abort
- judge 在隐藏 B + 可见 A 上跑候选脚本，15 teeth 核对 net_count / dirs_scanned /
  单位换算 / terminal-order 分类 / anti-hardcode / 3-seed / anti-cheat

C 域 physical_verify starRC pex 提取脚本重复目录修复 reframe 子型首例
（与 SpfLayerCoupleCapAnalyze(DSPF 逐层耦合)/LvsSvdbRepDirStat 正交：本案=修 starRC
cco 提取的目录过滤 bug，deliverable=修好的提取脚本）。
