# r657 trace deepread — joelchen @ hfeg0plg89 session 1792393823402_cuedk

**Source**: `/home/joelchen/.cline/data/sessions/1792393823402_cuedk/1792393823402_cuedk.messages.json` (274KB, 81 msgs)
**User**: joelchen @ hfeg0plg89 (10.129.8.221), mc=100, keywords `lvs:289;cmos:272;drc:96;schematic:82;calibre:71;gdsii:51;aether:30;pyaether:8`
**Domain**: physical_verify (3D LVS GUI config generation)
**Selected via**: fresh non-cluster scan from `ssh_eda_search_20261116_072610/summary.tsv`, mc 10-100 range, non-cluster user filter; ledger grep confirmed unledgered.

## User intent (verbatim, A档 trace-faithful)

- **U#2** (load skill): `/home/joelchen/skills/3d-lvs-gui-config-generator 加载这个路径下的skill`
- **U#3** (skill spec body): full skill spec — 4 sections field rules + 留空规则 + 固定值 + M=1/M≥2 退化 + 格式要点 + 8 条验收标准 + 已知陷阱 (preserved verbatim in `assets/3DLvsGuiCfgGen-001/skill.md`)
- **U#4** (project spec, 提出需求型 — A档合规): drgsa project, 1 CmosDie (DDR5TOP/DDR5TOP, hcell=/proj/drgsa/V0/ver/lvs/hcells, rule=/apps/imctf/runset/calibre/cxmtG6_1C2A/current/drvsa/V2_package_drvsa_v0d5_Rev10_AC/argusLVS.rule, Magnify=1, R90) + 2 ArrayDie (ArrayDie1: Ary32G/Ary32G same hcell/rule, Magnify=1, R90; ArrayDie2: Ary32G/Ary32G_A2 same hcell, rule=Rev10_CA typo, Magnify=1, MXR90)
- **U#5** (stacking): gds paths empty; (CmosDie, ArrayDie1) → HLPnet/HSPnet; (CmosDie, ArrayDie2) → BLPnet/HSPnet (user typo: said ArrayDie1 second time, corrected in U#6)
- **U#6** (correction): 第二对是 CmosDie 和 ArrayDie2 堆叠, HSPnet 是 ArrayDie2 出, gds 路径全部留空

## Gold (assistant final, user-implicit-accept)

Final assistant turn: 8-condition self-check (all ✅) + generated config at `/home/joelchen/config_drgsa` with 4 sections:

```ini
[System Options]
System Source =
Source Top =
3D Port Layer = 1
Placement =
Ignore Top Port = 0
Bump Number = 10000
PVRS Rules =
Run Directory =
CPU Number = 32

[Chip Options]
Chip Name = CmosDie ArrayDie1 ArrayDie2
Layout Path 1 =
Layout Path 2 =
Layout Path 3 =
Layout Format = gdsii gdsii gdsii
Layout Top = DDR5TOP Ary32G Ary32G
Source Path =
Source Format = spice spice spice
Source Top = DDR5TOP Ary32G Ary32G_A2
Hcell = /proj/drgsa/V0/ver/lvs/hcells /proj/drgsa/V0/ver/lvs/hcells /proj/drgsa/V0/ver/lvs/hcells
LVS Rule Path = /apps/.../Rev10_AC/argusLVS.rule /apps/.../Rev10_AC/argusLVS.rule /apps/.../Rev10_CA/argusLVS.rule
Lcv Layout = drgsa_cmos_top * layout,drgsa_array_core * layout,drgsa_array_core * layout
Lcv Schematic = drgsa_cmos_top * schematic,drgsa_array_core * schematic,drgsa_array_core * schematic
Other params = {} {} {}

[Interface]
Main Instance Name =
Instance Name = Bot_Inst Top_Inst1 Top_Inst2
Master Name = CmosDie ArrayDie1 ArrayDie2
Location = (0 0) (0 0) (0 0)
Magnify = 1 1 1
Rotate = R90 R90 MXR90
X-axis Mirror = / / /

[Connectivity]
Connectivity Name = LOGIC_DRAM_TOP
Instance Name = Bot_Inst Top_Inst1,Bot_Inst Top_Inst2
Layer = HLPnet HSPnet,BLPnet HSPnet
```

User did not explicitly reject or correct after final assistant turn → implicit accept.

## Tools used

`list_allowed_files(10)`, `editor(10)`, `read_files(9)`, `skills(3)`, `run_approved_command(3)`, `search_codebase(1)`, `run_commands(1)`

## Case design (B档 mock-behavioral reframe, 承 r655/r656 模式)

- **Reframe rationale**: trace deliverable = single hardcoded drgsa config (one-shot, hardcode-able). To make check() teeth-able with hidden B, reframe deliverable as **general generator script** `gen_3dlvs_config.py` that implements skill rules for ANY spec. Hidden B (vanguard N=4 M=3, distinct names/rotates/magnify=2) + B2 (kestrel M=1 degenerate) defeat hardcoding of N/M/project/die-names/layer-names.
- **A档 trace-faithful preserved**: prompt = user's verbatim words (U#2/U#4/U#5/U#6); skill.md = trace skill spec verbatim; spec_example.json = trace user spec structured (agent-visible schema example only).
- **New sub-type**: `3d-lvs-gui-config-generator` — distinct vs r656=via-enclosure-distance-checker / r655=polygon-geometry-predicate / r652=pex-batch-path-resolve / r650=cut-layer-idx-bugfix / r645=svrf-antenna-rule-family.
- **check.py**: 16 conditions a-p; subprocess runs candidate on hidden B + B2; parser validates 4-section structure + 9 SO keys + 5 empty-format + 4 fixed values + N-count fields + spec-B-derived values (Chip Name/Layout Top/Source Top/Hcell/LVS Rule Path/Magnify/Rotate) + Lcv comma-no-space + Connectivity pairs + M=1 degeneration.
- **Negatives**: 5 (empty-shell / print-expected-A / core-deleted-short-layer / always-pass-stub / wrong-threshold-M-cap), all FAIL with 5 distinct first_fail labels (b/c/f/g/k).
- **§4.9 三假**: neg1(空壳)=b, neg2(只print期望)=f, neg3(删核心)=k — all FAIL ✓.
- **Self-test**: gold PASS, 5 neg FAIL, 5 distinct labels.

## Verification

- gold_ref.py PASS check 16/16 ✓
- negative_selftest.py: gold PASS, 5 neg FAIL, 5 distinct labels (b/c/f/g/k) ✓
- §4.9 (a)(b)(c) 三假全 FAIL ✓
- k_rationale = k_check = 16 ≥ 8 GATE PASS ✓
- test==disk check.py 字节同步 ✓
- check() 用 tempfile.mkdtemp (不在 workdir 留 __chk) ✓
- §4.8 泄漏隔离: SUT 沙箱不含 reference/jsonl/test 字段 (eval harness runtime property) ✓
- C.jsonl 407→408 ✓
