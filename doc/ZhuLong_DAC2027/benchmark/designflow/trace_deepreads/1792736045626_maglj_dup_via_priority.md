# trace_deepread: 1792736045626_maglj (yqlu @ hfeg0pkn005, mc=281, layout_aether)

## session
- path: /home/yqlu/.cline/data/sessions/1792736045626_maglj/1792736045626_maglj.messages.json (1.62 MB, 353 msgs)
- status: user-accepted iterative refinement (no terminal fail); final code ran in /home/yqlu/connectivity_check/

## real task (user msg #2/#3, verbatim intent)
> 帮我优化一下这个Python脚本，现在不能验证 TCP-CT-M1, M0U-CT-M1 这种情况，也就是同一个 CT/M1 既可能连接 TCP 也可能连接 M0U；当版图上同一个位置同时画了 TCP 和 M0U，这个 CT/M1 只能连到 TCP 而不是 M0U。需要在原脚本基础上加一个新功能：查找所有类似 CT-M1 这种出现了两次（含以上）的连接关系，并仿照之前的 pattern 思路，创建对应的 cell 去检查 rule 里这个关系的正确性。

- attachments: main.py (530 lines, gdspy+calibre LVS connectivity-QA pattern generator) + config.cfg (60 lines, connectivity list + conn_layers) — uploaded in sibling session 1793695810575_msv4x/uploads/

## main.py mechanism (real)
- reads `connectivity` (entries `Bottom-Via-Top` 3-layer or `Bottom-Top` 2-layer direct) + `conn_layers` from config.cfg
- `find_all_paths` DFS builds layer-via-layer paths from bottomLayer [PG, AT4]
- `genPattern`/`mosGen` draw good/bad1/bad2 GDS cells (gdspy) per layer×purpose
- `runLVS` invokes `calibre -hier -lvs`, `readReport` parses INCORRECT, writes connectivityCheck.report

## config.cfg real connectivity (18 edges)
M8-HSV-HSP, M7-V7-M8, M6-V6-M7, M5-V5-M6, M4-V4-M5, M3-V3-M4, M2-V2-M3, M1-V1-M2,
TCP-CT-M1, M0U-CT-M1, M1-TSV-BAM, BAM-BPA (2-layer direct), MT2-PCU-M0U, M0C-PCU-M0U,
PG-PC2-MT2, PG-PC2-M0C, AT4-PC1-MT2, AT4-PC1-M0C

duplicate (via,top) pairs in A:
- (CT, M1): bottoms TCP, M0U (TCP appears first → winner)
- (PCU, M0U): bottoms MT2, M0C (MT2 first → winner)
all other (via,top) pairs have a single bottom → not duplicate.

## assistant solution (grounded gold)
added block before `def main()`:
- `find_duplicate_via_top(connectivity)` → `{(via,top): [bottoms]}` for (via,top) used by 2+ bottoms
- `get_priority_from_connectivity(connectivity)` → winner/loser by ORDER OF APPEARANCE (earliest bottom = winner; later = losers). comment: "MT2-PCU-M0U before M0C-PCU-M0U -> via=PCU top=M0U winner=MT2 loser=M0C". NO `priority` config needed.
- `genPriorityCell(via,tm,winner,loser,mode)` → standalone good/bad cell: top/via/winner stacked; loser isolated; modes good (stack only) / bad (winner covers loser + wrong-pin inversion)
- `genPriorityNetlist` / `runPriorityLVS` / `readPriorityReport` / `priorityCheckPatternGen`

## user feedback (msg #333) + fix
- S/G/D three terminals must be SEPARATE coexist blocks (not one big block); ntn_S/ntn_G/ntn_D each on its own spot
- ptk device also needs patterns (not just ntn)
- assistant rewrote coexist block per-device per-terminal

## run result (assistant, in /home/yqlu/connectivity_check)
priority tasks: [('CT','M1','TCP','M0U'), ('PCU','M0U','M0C','MT2')] (early version; final = earliest-winner: ('PCU','M0U','MT2','M0C'))
GDS written 6.9 MB, 538 cells; full main() SIGKILL'd by sandbox timeout (calibre per-cell + gvim); pattern-gen-only run OK.

## case synthesis (B-synthesized, L1-boundary)
- EDA-Eval-DesignFlow-DupViaPriorityCheck-001 (layout_aether)
- SUT writes dup_via_priority_check.py: parse config `connectivity` list → find duplicate (via,top) groups (≥2 bottoms) → winner=earliest appearance, losers=rest in order → emit priority_tasks (one per winner-loser pair) + summary JSON
- asset A = real config.cfg connectivity (18 edges, 2 dup groups: CT/M1 [TCP,M0U], PCU/M0U [MT2,M0C])
- hidden B = reparameterized: 7 edges, 2 dup groups (BB/AA 3-bottom [ZW,XY,MN] winner=ZW NOT alphabetical; DD/CC [RS,PQ] winner=RS NOT alphabetical), 1 non-dup 3-layer (UV-WW-XX), 1 direct (YY-ZZ)
- B-broken sentinel: only direct edges → 0 dup groups
- 16 conditions (a-p); k_check=k_rationale=16; ref PASS; 5 negatives FAIL (NEG_RC=0); §4.9 three-fake FAIL
