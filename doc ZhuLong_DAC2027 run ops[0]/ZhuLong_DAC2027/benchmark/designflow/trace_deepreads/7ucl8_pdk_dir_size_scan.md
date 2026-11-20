# Deep-read: 7ucl8 — PDK dir size scan + HTML report + autoMail

- **trace**: `1792473082105_7ucl8.messages.json` (xxchen / hfeg0pkn005 / 10.129.2.14 / mc105)
- **source path**: `/home/xxchen/.cline/data/sessions/1792473082105_7ucl8/1792473082105_7ucl8.messages.json` (333KB / 69 msgs / 38 tool calls)
- **tools hit**: innovus 6 + calibre 6 (digital-dominant, A=0 D=1) — but the actual task is a Python disk-usage scanner targeting `/home/pdk` (PDK storage). Domain = **eda_other** (EDA-context tooling/automation; user is EDA engineer, target is PDK dir). Level = **L1** (offline Python; grading runs candidate via subprocess on synthetic fixture → §4.2 structural, no EDA binary).
- **fetched artifacts** (real, from 10.129.2.14):
  - `gold_pdk_dir_size_check.py` (456 lines, 17950B) — the accepted tool, complete & runnable.
  - `autoMail.py` (real, /home/xxchen/mail/autoMail.py — read via trace tool_result; password masked in asset).
  - `input.js` (real sample — the input.js format reference).

## User turns (verbatim, A-faithful source)

**UI#1** (ts=1792473082663, clean 提出需求):
> 帮我用python写个程序，检查 /home/pdk 这个目录下每个子目录的大小，筛选大于200G的目录输出html文档，按照从小到大的顺序写给我。使用/home/xxchen/mail/autoMail.py + input.js 方式 发给我。

**UI#2** (ts=1792475996350, additional constraints — 提出额外需求, NOT a root-cause/fix):
> 不要查.snapshot目录
> 脚本查询目录最大时长需要设置为1h。

→ rule ② check: neither turn points out root-cause or gives a fix; both are requirement turns ⇒ **A-faithful ✓**. Prompt = UI#1 + UI#2 verbatim.

## Assistant tool chain (38 calls)
T1 get_agent_policy_status → T2/T3 list_allowed_files (/home/xxchen/mail, /home/pdk: 53 subdirs) → T4 read_files(autoMail.py + input.js) → T5-T7 recon (workspace, soa module) → T8 editor todo.md → T9-T12 editor pdk_dir_size_check.py (322→456 lines, multi-segment) → T13 run (real /home/pdk → SIGKILL timeout) → T14-T18 refactor for resumable scan (post-order iterative + subtree checkpoint + --max-runtime) → T19 read_files verify → T20-T26 test on synthetic tree (test_build_tree.py: small1/mid/big/loose.txt/biglink-symlink; threshold 0.5MB → 2 dirs ascending mid 1.6MB < big 2MB; symlink & loose file ignored ✓; --fresh + tiny runtime → partial exit + save state ✓; rerun → resume ✓) → T27-T38 real /home/pdk scan (multi-run接力; .snapshot huge; save_interval 15→3s; checkpoint-attach bug fix at T33-T35; .snapshot accumulated 34860 subtree checkpoints).

## Gold = `pdk_dir_size_check.py` (human-reviewed, used as-is — trace-faithful)
**Functionality**:
- CLI: `--root` (default /home/pdk), `--threshold` (GB float, default 200), `--out-dir`, `--state`, `--max-runtime` (sec, 0=unlimited), `--fresh`, `--receivers`.
- Scans every first-level subdir of root; size = sum of apparent file sizes (st_size), post-order iterative; **symlinks not followed** (entry.is_symlink → continue; top-level symlinks filtered via os.path.islink); permission-denied entries skipped+counted.
- Resumable: subtree-level checkpoint state file (JSON), save_interval (3s default), `--max-runtime` clean exit at dir boundary, `--fresh` ignores state.
- Filter `bytes > threshold*GB`; **sort ascending** by (bytes, name).
- Writes `pdk_dir_size_report.html` (standalone, CSS, info table: scan_time/host/root/threshold/scanned/matched/matched_total/all_total/skipped; rows: #/子目录/GB/可读大小/比例条/完整路径; note about 1GB=1024^3 + apparent-size + symlink + autoMail).
- Writes `input.js` (JSON, ASCII): `{Text, subject, receivers, filePath:[html_path]}` — consumable by `python3.7 /home/xxchen/mail/autoMail.py input.js`.
- Console summary (ascending) + hint to run autoMail.

**Gaps vs UI#2 (human review)**: gold does NOT explicitly exclude `.snapshot` (UI#2 asked) and default `--max-runtime` is 0 not 3600 (UI#2 asked 1h). Trace ends mid-scan (T38) without explicit user acceptance. Per rule ④ (gold = trace actual product, human-reviewed, assertions only on facts), check.py asserts **what the gold actually does** (scan/filter/ascending HTML/input.js 4-keys/CLI/--max-runtime/symlink-skip/cross-input/anti-hardcode). `.snapshot` exclusion is NOT asserted (gold doesn't implement it); fixture_B contains no `.snapshot` to avoid ambiguity. `--max-runtime` asserted via explicit flag (not default value).

## Fixture plan (synthetic, grading-only — not in SUT sandbox)
- **build_fixture.py** builds two synthetic trees (no real /home/pdk needed):
  - **fixture_A** (visible-name reference, but NOT shipped to SUT — stays in reference/): dirs `small1` (100KB, below), `mid` (1.6MB nested: b.bin 1MB + nested/c.bin 600KB), `big` (2MB), `loose.txt` (root file, ignored), `biglink`→big (symlink, ignored). Threshold 0.0005 GB (~0.5MB) → 2 dirs ascending [mid 1.6MB, big 2MB].
  - **fixture_B** (hidden, structurally different): dirs `pdknodeB_alpha` (0.8MB), `pdknodeB_beta` (2.4MB nested: x.bin 1.4MB + nested/y.bin 1MB), `pdknodeB_gamma` (0.3MB, below), `tinyB` (50KB, below), `linkB`→pdknodeB_beta (symlink, ignored), `readmeB.txt` (root file, ignored). Threshold 0.0005 GB → 2 dirs ascending [pdknodeB_alpha 0.8MB, pdknodeB_beta 2.4MB]. B's dir names + sizes + count ≠ A → cross-input guard + anti-hardcode.
- check.py builds fixture_B in a temp dir, runs candidate `pdk_dir_size_check.py --root <B> --threshold 0.0005 --out-dir <out>` via subprocess, asserts HTML + input.js structure.

## Anti-leak
- SUT sandbox assets: prompt.txt + task_brief.md + autoMail.py (password masked) + input.js only. **0** check.py / gold / fixture / negative / hidden B.
- check.py + gold + build_fixture + negative + reference_submit.zip all in `reference/` (never enters SUT workdir).
- Judge runs in独立 /tmp; check.py builds fixture_B itself.
- anti-hardcode assertion (p): grep candidate source for fixture_A literals (`small1`,`mid`,`big`,`biglink`,`loose`,`pdknodeB`? no — B names are in fixture not source). Guard fixture_A-specific literals: `small1`, `mid`, `big`, `biglink`, `loose.txt`, `1.6`, `2.0` (MB sizes as bare literals). Defeats fake_print_expected that hardcodes A's "mid 1.6 / big 2.0" output.
