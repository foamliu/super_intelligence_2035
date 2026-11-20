# Deepread: 1790560223344_ayqtu — Cline Skill Registration + Hardcoded Path Rewrite

**session**: `1790560223344_ayqtu.messages.json` (61 msgs, 39 user / 22 assistant, agent=lead)
**user**: simplec @ 10.129.2.11 (hfeg0plg89)
**mc**: 54 — keyword profile `drc:341; aether:121; techfile:53; verilog:34; rtl:30; lib.defs:22; calibre:16; .cdl:9`
**domain**: physical_verify (DRC testpattern generation skill topic)

## Real User Intent (trace-faithful)

U#0 (msg#0, ts=1790560223623): **「加载我路径下的skill」** — load/register skill in user's path.
U#36 (msg#36): **「2」** — selecting option 2 (register the second unregistered skill found, `drc-pattern`).

## Agent Trace (22 assistant msgs)

1. `list_allowed_files` (×4) + `get_agent_policy_status` — explored `~/.cline/` structure
2. `search_codebase` + `run_commands` (`find -iname '*skill*'`) — located skill files
3. `list_allowed_files` + `read_files` — read registered skills (glory-rc-flow, skill-creator) + unregistered `drc-pattern-SKILL.md` at `/home/simplec/.cline/scripts/data/`
4. `read_files` of `drc-pattern-SKILL.md` (msg#32) — source had hardcoded `/home/lizwen/` paths
5. `editor` (msg#49) — wrote `/home/simplec/.cline/skills/drc-pattern/SKILL.md` (4325 chars), replacing `/home/lizwen/` → `/home/simplec/` (current user)
6. `list_allowed_files` verification — confirmed `drc-pattern/SKILL.md` exists
7. `skills('drc-pattern', 'help')` (msg#58) — verified skill loads, returned full SKILL.md content
8. Final summary: skill `drc-pattern` successfully registered with hardcoded path fix

## Skill Topic (DRC Testpattern Generator)

The registered skill generates Testpattern layouts (PASS+FAIL cases) for DRC rules using Aether/pyAether. It uses `run_drc_pattern.sh` to drive `drc_pattern_gen.py` which:
- Parses `test_deck` → `fnmatch` rule matching → reads `drc_rules_spec.json` → `dbCreateLib` → draws PASS+FAIL cells → `dbSaveCV`
- This is a **physical_verify** domain skill (DRC pattern generation)

## 11-15 Task初心 B类复活实证

This trace is an **env-config / setup** task (skill registration with path fix):
- Old rule: env-config / setup / Q&A 类 → 判 weak 不可造
- 11-15 令 §二「旧判为 weak / analysis-only / 不可造的候选：env-config、setup 类 —— 按任务初衷，这些都是真实用户意图，全部恢复为可造」
- 本 session 真实意图 = 注册 skill + 修复硬编路径 → 合法可造

## Reframe: mock-behavioral produce task

Real task path-dependent (需 cline env + read_files/editor/skills tools) → 纯 stdlib 微型 fixture:
- **Sub-type**: `cline-skill-registration-hardcoded-path-rewrite`
- **Input**: source SKILL.md (with `/home/<other>/` hardcoded) + current_user string + target skills dir
- **Output**:
  - `<target>/<skill_name>/SKILL.md` — paths rewritten `/home/<other>/` → `/home/<current_user>/`
  - `<target>/INDEX.md` — updated with new skill entry
  - stdout JSON report (skill_name / hardcoded_paths_found / rewritten_paths_count / original_users / description / ...)
- **Skill_name derivation**: strip trailing `-SKILL.md` from filename
- **Path rewrite**: regex `/home/([A-Za-z0-9_]+)/` → `/home/<current_user>/` (skip if already current_user)

## Hidden B / B2 (anti-hardcode)

- **B** (`lvs-ruledeck-SKILL.md`): fully disjoint from A — skill_name=lvs-ruledeck (vs drc-pattern), current_user=haow (vs simplec), original_users=[wangjun] (vs [lizwen]), description=LVS-related (vs DRC-related). 14 /home/wangjun/ occurrences.
- **B2** (`clean-skill-SKILL.md`): edge case — no /home/X/ hardcoded paths, file should still be created unchanged with rewritten_paths_count=0.

## Distinct from prior shard C cases

- vs r711 SkillPatternDecoordinate (SKILL .il 去坐标参数化): 本例 = skill registration + path rewrite, not .il content parameterization
- vs r716 BridgeRenamePortAudit (cross-file rename + reference rewrite): 本例 = single SKILL.md content path rewrite + INDEX.md update, not multi-file rename
- vs r715 VyEnclosureQaAudit (TVF .ev deck EN rule QA): 本例 = cline skill file, not calibre deck
- 新子型 `cline-skill-registration-hardcoded-path-rewrite`, mock-behavioral family r645-r718

## Check() Teeth

18 conditions a-r:
- (a-b) zip + py_compile structural
- (c) B run exit0 + JSON 11 keys
- (d-j) B-specific assertions: skill_name=lvs-ruledeck / target_skill_md exists + /home/haow/ present + /home/wangjun/ absent + rewritten_paths_count=14 + hardcoded_paths_found contains /home/wangjun/ + original_users=[wangjun]
- (k-m) B INDEX.md: exists + contains lvs-ruledeck + contains B description
- (n-p) B2 edge: exit0 + rewritten_paths_count=0 + target_skill_md == source
- (q) determinism: 2x B runs (same target) md5-identical
- (r) A demo consistency: skill_name=drc-pattern + original_users=[lizwen]

3 negatives (empty_stub/print_only/no_rewrite) → first_fail c/d/f (3 distinct ✓).
Reference 18/18 PASS ✓. k_rationale = k_check = 18 ≥ 8 GATE PASS ✓.
