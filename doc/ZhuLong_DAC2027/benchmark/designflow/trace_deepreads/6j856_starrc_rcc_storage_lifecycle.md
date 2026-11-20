# Deepread: 1794898269989_6j856 (mwxi @ hfeg0plg33, mc=251)

## Trace metadata
- session: 1794898269989_6j856.messages.json (147KB / 44 msgs)
- user: mwxi (ethanw in LSF job context, mwxi is the clinde user)
- host: hfeg0plg33 (10.129.32.76)
- mc=251, keywords: lvs:101;pex:38;netlist:38;calibre:35;.spi:28;.cdl:5;.gds:4;drc:2
- domain: **physical_verify** (Calibre LVS + StarRC RCC extraction lifecycle)
- 7 user turns (U#0,1,7,13,22,32,38), 6 user_input + 1 context-summary

## User real intent (verbatim)
- U#0 (context summary, 2461 chars): "分析 LSF 作业 job_id=2971697（合肥 HF 环境，ethanw，star 队列）的配置、资源需求、输出路径、日志位置，并统计该 job 产生的文件大小（过程文件/结果文件），为存储规划提供依据" — storage planning for StarRC RCC LPE job
- U#1: "我不需要你知道具体的每一个文件大小，只需告诉我在哪个nas路径下需要多大的存储即可"
- U#7: "过程文件最大需要多少 脚本执行需要多长时间 结束结果文件有多大 这些可以找到吗"
- U#13: "job结束，过程文件有多大，会有记录吗"
- U#22: "你找一个已经跑结束的job配置文件看一下 有没有这些信息的记录，不用实际去du"
- U#32: "过程文件job结束会自动删除吗"
- U#38: "过程文件、结果文件的路径配置文件有记录吗"

**Single intent**: storage lifecycle analysis of Calibre LVS + StarRC RCC extraction jobs — which files are process (auto-deleted) vs result (kept), where are paths/configs recorded, how big do they get, for NAS storage planning.

## Real config files (extracted from trace tool_results)

### lpe.config (DqPad_CIO finished job 2962081, idx30)
Key=value pairs (50+ keys). Notable:
- process = cxmtV2B, project = drvqa, version = v0
- mode = RCC (RC extraction with Coupling Caps)
- CORNER = TYP, Temperature = 98, tf_mode = TYP
- cdl = .../DqPad_CIO.cdl, cdl_top = DqPad_CIO
- gds = .../DqPad_CIO.gds, gds_top = DqPad_CIO
- hcell = /proj/drvqa/V0/ver/lvs/hcells-lpe
- skip_cell = /apps/imctf/cad/script/runlpe/skip_cell
- REDUCTION = NO (job 2971697 had REDUCTION=YES causing node explosion)
- Core_Num = 8
- POWER_EXTRACT = YES, POWER_NETS = vdd1! vddq! ... (40+ power nets)
- CHK_LPE_LVS = YES, RUN_LVS_MODE = hier, Sub_Dio = YES
- Cap_Rep = YES, CHK_LN_NET = YES

### runlpe.sh (wrapper, idx36) + runlpe.pl cleanup lines (idx36 grep)
runlpe.sh (bash wrapper):
- `rm -rf .../lpe.log` (pre-run)
- `bsub -Is -q star -n 8 /apps/imctf/cad/script/runlpe/runlpe -config .../lpe.config |& tee .../lpe.log`
- post-run: `rm -f DqPad_CIO.spf_RCC` then `ln -sf lpe/DqPad_CIO/DqPad_CIO.spf_RCC .` (SPF symlink to parent)
- same for `DqPad_CIO.spf.*_RCC` glob

runlpe.pl cleanup (grep rm/cleanup/delete, 7 hits):
- L542: `system("rm -rf svdb CCI_DB");`
- L599: `system("rm -rf CCI_DB");`
- L1008: `if (unlink $starSumFile) { ... }` (deletes star_sum file)
- L1029: `system("rm -rf $corner_path");`
- L1140: `system("rm -rf $new_spffilename");`
- L1224: `system("rm -rf *spf*_ori");`

### star_cmd_RCC (StarRCXT extraction options template, idx42)
Key:value pairs (StarRCXT format, `KEY: VALUE` not `=`). Notable:
- BLOCK: DqPad_CIO
- CALIBRE_RUNSET: lpe_RCC.rule
- TCAD_GRD_FILE: /apps/.../cxmtV2B_drvqa_1p12m3x8y1z_98C_AC_TYP.nxtgrd
- MAPPING_FILE: /apps/.../starrc_mapping
- EXTRACTION: RC
- OPERATING_TEMPERATURE: 98
- NUM_CORES: 8
- REDUCTION: NO
- NETLIST_FORMAT: SPF
- COUPLE_TO_GROUND: NO
- POWER_EXTRACT: YES, POWER_NETS: (same 40+ nets)
- SKIP_CELLS: !*
- XREF: YES, CELL_TYPE: LAYOUT, NET_TYPE: LAYOUT
- LPE_DEVICES: (3 lines of device flags)

### Run directory listing (idx30 ls output)
Process files (auto-deleted by runlpe.pl):
- CCI_DB/ (rm -rf L542/L599)
- DqPad_CIO.gpd/ (NOT explicitly deleted — kept? actually partition DB, large)
- star/ (StarRC work dir, large 5.3GB in job 2971697)
- svdb/ (rm -rf L542)
- chkLnNet/ (not in cleanup grep — kept?)

Result files (kept):
- DqPad_CIO.spf_RCC (508MB, final SPF, symlinked to parent)
- DqPad_CIO.spf_RCC_cap.rep (1.2MB)
- DqPad_CIO.star_sum (4.4MB, but unlink $starSumFile in runlpe.pl L1008 — actually DELETED!)
- layout.spi (780KB)
- cci_lvs.log (3.1MB)
- lpe.log (435KB)
- layout_top.lvs.rep, layout_top.lvs.rep.ext
- DqPad_CIO.cc.rep (106KB, coupling cap report)

**Key finding**: star_sum is actually DELETED by runlpe.pl (unlink $starSumFile L1008) — user asked "过程文件job结束会自动删除吗" and answer is YES for svdb/CCI_DB/star_sum/corner_path/*spf*_ori.

## Reframe design (档 B, L1-boundary, static-parse)

**Case ID**: EDA-Eval-DesignFlow-StarRcRccStorageLifecycle-001
**Domain**: physical_verify (Calibre LVS + StarRC RCC extraction)
**Sub-type**: StarRC RCC storage lifecycle analyzer (fixture-driven static parse)

### Reframe
Given a triple of real StarRC RCC LPE config files (lpe.config + runlpe.pl cleanup excerpt + star_cmd_RCC template), produce a Python analyzer that parses all three and emits a structured JSON storage lifecycle report:

```json
{
  "config_summary": {  // from lpe.config (key = value)
    "process": "...", "project": "...", "version": "...",
    "mode": "...", "CORNER": "...", "Temperature": "...",
    "cdl_top": "...", "gds_top": "...",
    "Core_Num": <int>, "REDUCTION": "...",
    "POWER_EXTRACT": "...", "hcell": "...", "skip_cell": "..."
  },
  "process_files": [  // from runlpe.pl rm -rf / unlink lines
    {"name": "svdb", "cleanup_action": "rm -rf", "source_line": 542},
    {"name": "CCI_DB", "cleanup_action": "rm -rf", "source_line": 542},
    {"name": "CCI_DB", "cleanup_action": "rm -rf", "source_line": 599},
    {"name": "star_sum", "cleanup_action": "unlink", "source_line": 1008},
    {"name": "$corner_path", "cleanup_action": "rm -rf", "source_line": 1029},
    {"name": "$new_spffilename", "cleanup_action": "rm -rf", "source_line": 1140},
    {"name": "*spf*_ori", "cleanup_action": "rm -rf", "source_line": 1224}
  ],
  "result_files": [  // from runlpe.sh + star_cmd_RCC (kept, not in cleanup)
    {"name": "spf_RCC", "path_template": "{top}.spf_RCC", "source": "runlpe.sh symlink"},
    {"name": "cc.rep", "path_template": "{top}.cc.rep", "source": "star_cmd_RCC COUPLING_REPORT_FILE"},
    {"name": "layout.spi", "path_template": "layout.spi", "source": "run dir"},
    {"name": "lvs.rep", "path_template": "layout_top.lvs.rep", "source": "run dir"}
  ],
  "starrc_options": {  // from star_cmd_RCC (KEY: VALUE)
    "BLOCK": "...", "EXTRACTION": "...", "OPERATING_TEMPERATURE": "...",
    "NUM_CORES": <int>, "NETLIST_FORMAT": "...", "REDUCTION": "...",
    "TCAD_GRD_FILE": "...", "MAPPING_FILE": "..."
  },
  "cleanup_count": <int>  // total rm/unlink commands in runlpe.pl
}
```

### Visible A (assets/, in SUT sandbox)
- lpe_config_A.txt (real DqPad_CIO lpe.config, 60+ lines)
- runlpe_cleanup_A.txt (runlpe.pl cleanup excerpt with line numbers, ~10 lines)
- star_cmd_RCC_A.txt (real star_cmd_RCC template, ~80 lines)
- task_brief.md (user intent + reframe description)
- hidden_manifest.json

### Hidden B (in check.py, NOT in SUT sandbox)
Synthesized different config:
- process = cxmt14G6, project = drpoa, version = v1, mode = RC (not RCC)
- CORNER = CMAX, Temperature = 125
- cdl_top = AoiMux8x, gds_top = AoiMux8x
- Core_Num = 4, REDUCTION = YES
- POWER_EXTRACT = NO
- runlpe cleanup: different line numbers, different targets (e.g. rm -rf r3d_db, rm -rf $temp_path)
- star_cmd_RCC: BLOCK = AoiMux8x, EXTRACTION = R, OPERATING_TEMPERATURE = 125, NUM_CORES = 4

### Hidden B2 (cross-input guard)
Third config that shares SOME keys with A but differs in others:
- process = cxmtV2B (same as A), project = drvqa (same as A), but mode = R (different), CORNER = CMIN (different), Temperature = 0 (different)
- Core_Num = 1 (different), REDUCTION = YES (different)
- runlpe cleanup: subset of A's targets (only svdb + CCI_DB, no corner_path)
- star_cmd_RCC: BLOCK = SameTopAsA (same cdl_top as A but different EXTRACTION)

Defeats: hardcoded A answers fail B (different process/mode/corner); hardcoded B answers fail B2 (process same as A but mode different → must actually parse).

### Check.py teeth (15, a-o)
a. exit 0
b. valid JSON with required top-level keys (config_summary, process_files, result_files, starrc_options, cleanup_count)
c. config_summary.process == expected (B's process)
d. config_summary.mode == expected (B's mode)
e. config_summary.Core_Num == expected int
f. config_summary.REDUCTION == expected
g. process_files contains "svdb" with cleanup_action "rm -rf"
h. process_files contains "CCI_DB"
i. process_files contains "*spf*_ori"
j. result_files contains "spf_RCC"
k. result_files contains "layout.spi"
l. starrc_options.EXTRACTION == expected
m. starrc_options.OPERATING_TEMPERATURE == expected (str or int)
n. starrc_options.NUM_CORES == expected int
o. B2 cross-input guard: B2's process==A's process but B2's mode != A's mode → check config_summary.mode == B2's mode (not A's)
p. cleanup_count >= 4

### Negatives (5)
1. empty_stub: produces `{}` → fails b (missing keys)
2. print_only: prints expected JSON string, doesn't write file → fails b (no file or invalid)
3. core_deleted: parser returns hardcoded A values regardless of input → fails c (B has different process)
4. naive_config_only: only parses lpe.config, empty process_files → fails g (missing svdb)
5. naive_starrc_only: only parses star_cmd_RCC, empty config_summary → fails c (missing process)

### §4.9 coverage
- (a) empty_stub → fails b
- (b) print_only → fails b
- (c) core_deleted → fails c

## Intent audit
KEEP — mwxi's real intent (StarRC RCC job storage lifecycle: process vs result files, cleanup behavior, config-driven paths, NAS planning) is fully preserved. Reframe unifies the multi-turn Q&A into a single produce-task (static config parser → JSON storage report). No logic added or removed — the parser extracts exactly what the user asked about (which files deleted, which kept, where configured). U#0 context summary and U#1/7/13/22/32/38 verbatim user questions inform the task_brief. C-domain physical_verify (Calibre LVS + StarRC RCC = parasitic extraction flow). 2026-11-21 produce-task legit.
