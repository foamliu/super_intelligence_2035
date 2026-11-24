# Deepread: a6qhz — VCT GAA NMOS Sentaurus sprocess rewrite

- **session**: 1795390906184_a6qhz.messages.json
- **user/host**: e02141 @ hfeg0pkn005 (10.129.2.14)
- **mc**: 163 (synopsys:538; lvs:282; transistor:39; cmos:18; dbget:9; gdsii:6)
- **size**: 2.95MB / 352 msgs (user 186 / assistant 166)
- **agent harness**: lead (not cline) — tools: editor(82), run_approved_command(61), read_files(17), list_allowed_files(5), ask_question(6)
- **domain**: eda_other (TCAD Sentaurus Process simulation) — A-pure (synopsys dominant, a=538 > cd=295)

## User intent (real, trace-faithful)

U#1 (idx 0): 「VCT GAA NMOS结构比较复杂容易出错，实际步骤是这样，先photo/etch 定义AA line space，填充oxide和nitride，然后用垂直于AA 的 WL line/space pattern将 silicon pillar 定义出来，下一步通过填充oxide再etch back到channel length深度，form TiN gate，然后把TiN etch back形成 final gate profile，重新编写process脚本实现这一结构」

→ User wants the Sentaurus sprocess .cmd rewritten to follow the REAL VCT GAA NMOS fabrication flow (6 steps):
1. photo/etch define AA line/space
2. fill oxide + nitride
3. WL line/space pattern (perpendicular to AA) → defines Si pillar
4. fill oxide + etch back to channel-length depth
5. form TiN gate
6. TiN etch back → final gate profile

U#5 (idx 36): target deck = `/home/e02141/devops/VCT_GAA_1111`
U#7 (idx 170): reference = `/home/e02141/devops/example` setup VCT_GAA_1111 process 脚本 (grill-me skill — iterative Q&A refinement)
U#11 (idx 309): sentaurus install path `/apps/synopsys/` → `/apps/synopsys/SRB`, update SKILL.md (secondary task)

## Assistant tool footprint

Files edited (editor tool, 82 ops):
- `/home/e02141/devops/VCT_GAA_1111/VCT_fps_v7.cmd` (11 ops) — **main deliverable** (rewritten sprocess .cmd, 12 numbered sections)
- `/home/e02141/vct_gaa/sprocess_VCT_GAA_NMOS_fps.cmd` (4 ops) — working copy
- `/home/e02141/vct_gaa/run_semtest.sh` (36 ops) — test runner
- `/home/e02141/vct_gaa/diag_v7.sh` (4 ops) — diagnostics
- `/home/e02141/.cline/skills/swb-python-api/SKILL.md` (1 op) — secondary task
- + ~20 helper scripts (deploy, preprocess, check, verify)

## Deliverable structure (VCT_fps_v7.cmd, v7 first creation idx 225)

12 numbered sections mapping to the 6 user steps + implants/contacts/remesh:
- [1] Source deep implant + RTA
- [2] STEP 1a: AA line/space photo/etch (mask protects pillar core y<=Rc, anisotropic etch removes AA space y>Rc)
- [3] STEP 1b: fill AA space with oxide (recessed to Xgtop) + nitride (flush at pillar top)
- [4] STEP 2: WL line/space pattern PERPENDICULAR to AA defines pillar (symbolic photo/strip, 2D cut inside WL line)
- [5] Drain implant + RTA
- [6] STEP 3: fill + etch back to channel-length depth (CMP planarize at Xgwin = Xgbot + Tg)
- [7] STEP 4: gate dielectric (SiO2 Tox selective on Si) + TiN gate (Tg selective on Oxide)
- [8] STEP 5: TiN etch back → final gate profile (directional etch -x, horizontal TiN removed, vertical TiN survives, final Lg exact)
- [9] Drain-end-face dielectric removal
- [10] ILD oxide fill
- [11] Drain plug (Al, anisotropic, masked)
- [12] Device remesh + electrodes + TDR output

Coordinates: x=0 drain/top, x=Xsrc source/bottom; y=0 axis, y=Ymax outer. Cylindrical (yAxis=0).
Mask semantics: positive mask segments PROTECTED, negative mask segments ETCHED.

## Case synthesis decision

- **Tier**: B档 synthesized (real `/home/e02141/devops/VCT_GAA_1111` tree on 10.129.2.14 not sandbox-accessible for SUT; synthesize trace-faithful sprocess .cmd structure)
- **Deliverable**: `parse_flow.py` (general sprocess .cmd step-sequence parser → JSON) + `VCT_fps_v7.cmd` (rewritten sprocess for A input)
- **A input**: template_A.cmd (sparse baseline) + flow_spec_A.json (geometry Rc=6nm/Tg=8nm/Lg=30nm, masks AA_LINE_A/WL_PERP_A)
- **hidden-B**: flow_spec_B.json + VCT_fps_v7_B.cmd (geometry Rc=8nm/Tg=10nm/Lg=40nm, masks AA_ACTIVE_B/WL_WORDLINE_B, zero token overlap with A)
- **check**: run SUT's parse_flow.py on hidden-B VCT_fps_v7_B.cmd → JSON, validate 6 key steps present + ordered + B-oracle match + anti-hardcode (A tokens absent) + determinism
- **domain**: eda_other (TCAD, A-shard)
