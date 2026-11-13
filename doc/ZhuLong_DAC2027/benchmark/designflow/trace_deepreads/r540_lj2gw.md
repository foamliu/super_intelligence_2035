# Deepread r540 — 1786535933950_lj2gw (e0014566/hfeg0plg58, mc=395)

## Session meta
- agent: lead, n_msgs=377, n_user_turns=3
- keywords: cellview:840;virtuoso:565;pyaether:204;dbcreatelabel:204;dbopencellviewbytype:168;netlist:...
- domain: layout_virtuoso / pg_layout (rscalc resistance extraction prep)

## User intent (3 turns)
1. [#0] "请你帮忙看下 Library:auto_austin_case1, Cell:Array16G_B, View:layout 这个版图。我现在要用rscalc计算电阻，看看其powernet上的RTEXT以及RNODE有没有打齐，没有的话帮忙打上。既然不能修改原本的layout，请先原封不动拷贝一份这个layout，然后分析，然后打上RTEXT RNODE，RNODE的量控制在30个左右。"
2. [#79] "既然拷贝下来之后就不能再编辑了，想别的方案——拷贝先不保存，将RTEXT RNODE一并写入到layout，最后保存。"
3. [#208] "projname: train, version name: V0_Austin"

## Task = produce-task (layout modification)
- Copy layout cellview auto_austin_case1/Array16G_B/layout → Array16G_B_rscalc
- Analyze power nets (vcc!/vss!/viso!) and their pin coordinates
- Add RTEXT labels (RDL/RTEXT, 1 per net, text=net name without "!")
- Add RNODE labels (RDL/RNODE, ~30 total, sampled along X range of each net)
- Save the modified copy

## Agent tool chain
1. Searched pyAether APIs: dbCopyCellView, leGuiMeasureResistance, aeCreateText/aeCreateLabel, emyNet/emyText/emyDesign/emyBlock classes, emyDesignSave, getBBox, emyShapeGetNetName, emyBaseNameFindNets, techFindLayer
2. Explored workspace /home/e0014566/test_layout_rscalc_flow_11/ — found existing SKILL scripts: add_rtext_rnode_sampled.il, check_rtext_rnode.il, run_rscalc_nogui.il, verify_result.il, rscalc.config, common.config
3. pyAether sandbox failed (connection refused at 10.129.32.75:30582) → switched to SKILL sandbox (Virtuoso)
4. SKILL dbOpenCellViewByType("auto_austin_case1" "Array16G_B" "layout" "" "r") → cvId=db:0x1da6631a, bBox=((-17884.13 -14767.0)(17884.13 100.524)), 16039 terminals
5. Power net analysis: vcc! (104 pins, Y=-1351.52, X=-13449..17501), vss! (96 pins, X=-17664..17664), viso! (16 pins, X=-15870..15819). Total 216 pins.
6. dbCopyCellView(srcCv "auto_austin_case1" "Array16G_B_rscalc" "layout") → SUCCESS (file created at /proj/train/V0_Austin/workdir/e0014566/auto_austin_case1/Array16G_B_rscalc/layout/)
7. Tried to add labels: dbCreateLabel(newCv list("RDL" "RTEXT") ...) → returned db object BUT parent=nil (orphan label)
8. dbSave returned t BUT labels=0 on reopen → labels never persisted

## Completion status: NEVER COMPLETED
- Root cause: CXMT permission system. isEditable=nil on all opened cellviews. dbCreateLabel creates orphan objects (parent=nil) not attached to cellview. dbSave returns t but nothing is saved.
- Agent tried: geOpen edit mode, batch Virtuoso processes (env _CXMT_SH_PROJ_WRITE_CHECK=1), various cds.lib/cwd combinations, disabling CXMT triggers, leCreateLabel/rodCreateLabel/dbCreateNoteLabel — ALL returned nil or orphan objects.
- Final assessment [#375]: "所有API都返回nil——CXMT权限系统阻止了。沙箱的Virtuoso进程没有写权限。"

## Key technical details extracted (sufficient for case construction)
- Power nets: vcc!(104 pins), vss!(96 pins), viso!(16 pins), all at Y=-1351.52
- bBox: ((-17884.13, -14767.0) to (17884.13, 100.524))
- RTEXT: layer=RDL, purpose=RTEXT, 1 per net, text = net name without "!" (e.g. "vcc")
- RNODE: layer=RDL, purpose=RNODE, ~30 total, sampled at evenly-spaced X along each net's pin X range
- RNODE distribution: proportional to pin count (vcc≈14, vss≈13, viso≈2 → 29≈30)
- SKILL APIs: dbOpenCellViewByType, dbCopyCellView, dbCreateLabel(cv list(layer purpose) point text justify orient font height), dbSave
- Existing workflow scripts in test_layout_rscalc_flow_11/rscalc_work/: add_rtext_rnode_sampled.il, check_rtext_rnode.il, run_rscalc_nogui.il

## Case design decision
- Abstract to a Python script task (following r539 FreeTrackFinder pattern): SUT writes rscalc_label_planner.py that reads power net pin data (JSON), computes RTEXT/RNODE label positions, outputs labels.json
- Hidden inputs B (4 nets) and B2 (2 nets) for anti-hardcoding
- Check: ≥14 assertions covering structure, counts, positions, layers, determinism, negative, fake-submit
