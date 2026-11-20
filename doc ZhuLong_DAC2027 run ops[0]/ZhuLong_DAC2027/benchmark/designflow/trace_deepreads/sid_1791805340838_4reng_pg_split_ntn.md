# 深读笔记 — sid 1791805340838_4reng (jianhaiq / hfeg0pkn004 / 10.129.2.13)

- mc=163, tools: 243 calibre + 25 netlist + 21 pyAether + 4 lang:pyAether (+editor 47 + read_files 37)
- session meta: model deepseek-v4-flash, cwd /home/jianhaiq, started 2026-10-12 11:42, ended 2026-10-16 06:02, **status=failed (terminal_marker=failed_external_process_exit / stale_session_reconciler)** — 进程外部退出，非用户拒绝
- 203 msgs / **1 user_input turn**（单轮完整需求委托）
- domain: **pg_layout**（PG_drawing / PG_NCH / PG_pin / ATTACH label = power-ground 甩脚/打标）

## T0 = U[0] 逐字原文（A-档 seed，纯需求，无根因/无修复，合规）
> 帮忙写一个python脚本，具体需求如下：
> 第一步：使用 /home/pdk/jianhaiq/11_AI_workspace/01_PG_split/gds_cdl/NTN_right_layout.gds 和 .../GateRes_right_layout.gds 两个pattern，第一个是mos，第二个是res；使用两个pattern，产生一个新的名为 ntn_to_ntn.gds 的版图文件，ntn_to_ntn.gds 文件中的pattern是这样的：存在两个上下镜像对称的mos，两个mos中间有一个竖着放置的res;使用PG_drawing将mos的PG_NCH和res的PG_drawing连在一起；在产生的ntn_to_ntn.gds文件中，镜像ntn中的下方ntn上，使用PG_pin层在非PG_NCH和AT4_NCH重叠区域的PG_NCH上打上名为ATTACH5的label，在镜像ntn中的上方的ntn的PG_NCH和AT4_NCH重叠的区域打上名为ATTACH7的label；
> 第二步：使用 .../NTN_right.cdl 和 .../GateRes_right.cdl 两个网表文件，生成一个新的名为 ntn_to_ntn.cdl 的文件；ntn_to_ntn.cdl中存在两个mos，一个res的信息；
> 第三步：使用生成的ntn_to_ntn.gds和ntn_to_ntn.cdl文件，和路径下的calibreLVS.rule文件，runlvs

## 真实附件（5 个，均在 10.129.2.13:/home/pdk/jianhaiq/11_AI_workspace/01_PG_split/）
- gds_cdl/NTN_right_layout.gds (2048B): cell `NTN_right`, bbox [[-0.874,-0.4],[1.674,1.9]], 23 polygons, 含 (30,3)=PG_NCH×3, (4,3)=AT4_NCH×1, (4,2), (30,6) + 多 drawing 层
- gds_cdl/GateRes_right_layout.gds (2048B): cell `GateRes_right`, bbox [[0,-0.7],[0.44,3.45]], 20 polygons, 含 (30,0)=PG_drawing×1, (30,20),(30,13),(20,0),(152,0)×8,(51,0)×8
- gds_cdl/NTN_right.cdl (161B): `.INCLUDE ...empty_device.spi` / `.PARAM` / `.SUBCKT NTN_right D G S B` / `MMN0 D G S B ntn W=1.5e-06 L=4e-07 nf=1` / `.ENDS`
- gds_cdl/GateRes_right.cdl (195B): `.SUBCKT GateRes_right PLUS MINUS` / `RR0 PLUS MINUS $[rnpo_2t_ckt] w=4.4e-07 l=2.75e-06 flag_res=1 nm=4` / `.ENDS`
- calibreLVS.rule (202KB, 4437 行): CXMT G4B-CIP DRAM Calibre-LVS rule deck (真实 PDK LVS 规则)

## assistant 工具链（gold 推导）
editor 47 次，分 3 代迭代：create_ntn_to_ntn_v2.py (i=38-126) → build_ntn.py (i=130-152) → make_ntn.py (i=154-180) → **mkntn.py (i=182-194, 最终交付)**。
- i=15 SandBox run_code: 探测 gdspy/numpy/pyAether 可用性 → gdspy available
- i=84/200 run_approved_command: 真跑 calibre LVS（profile=run_pyaether / 直接 calibre -lvs）
- i=198 SandBox run_code: `py_compile.compile('/home/jianhaiq/mkntn.py')` → **Syntax OK**
- 末 assistant text: "The script /home/jianhaiq/mkntn.py is complete and syntactically clean" + 三步交付摘要

## gold = mkntn.py（trace 最终版，自包含 Python3 + gdspy）
逻辑（从 5 个 editor event 复现）:
1. **create_gds()**: 读 NTN_right_layout.gds + GateRes_right_layout.gds（gdspy.GdsLibrary.read_gds），取 mc[0]/rc[0] 首个 cell（**输入泛化**，非硬编码名）；算 mos 宽高 mw×mh / res rw×rh；新建 top cell `ntn_to_ntn`；放置 3 个引用：MN0 R0@(0,0)、MN1 x_reflection@(0,m2y)（上下镜像对称）、RR0 R0@(rx,ry)（res 竖放两 mos 中间，rx=(mw-rw)/2 居中, ry=mh+GAP）；PG_drawing 层 (30,0) 画 2 个矩形连接 mos PG_NCH 与 res PG_drawing（MN0 gate→RR0 PLUS, MN1 gate→RR0 MINUS）；PG_pin 层 (30,251) 打 2 个 Label：ATTACH5@(cx,l5y) [下方非重叠区]、ATTACH7@(cx,l7y) [上方 AT4_NCH+PG_NCH 重叠区]；write_gds(OG, unit=1e-9, precision=1e-9)
2. **create_cdl()**: textwrap.dedent 模板生成 `.SUBCKT ntn_to_ntn D G S B MINUS` + `MMN0 D G S B ntn W=1.5e-06 L=4e-07 nf=1` + `MMN1 D MINUS S B ntn ...` + `RR0 G MINUS $[rnpo_2t_ckt] w=4.4e-07 l=2.75e-06 flag_res=1 nm=4` + `.ENDS`（trace 硬编码 W/L；**gold 改为从输入 CDL 解析 MMN/RR 行**以过 cross-input B）
3. **setup_lvs()**: 生成 lvs_ntn_to_ntn.rule（LAYOUT PATH/PRIMARY/SYSTEM + SOURCE PATH/PRIMARY/SYSTEM + LVS REPORT + INCLUDE calibreLVS.rule）
4. **run_lvs(rp)**: shutil.which('calibre') → subprocess.run([cal,'-lvs',rp], cwd=LV)（可选，check.py 不实跑 calibre，只验 rule 文件结构）
5. **main()**: CLI: `--lvs`/`--lvs-only`/`--help`

层常量: PG_drawing=(30,0) LPD, PG_NCH=(30,3) LPN, PG_pin=(30,251) LPP, AT4_NCH=(4,3) LA4, GAP=0.5e-6

## 难度定位
- **L1-boundary**（离线 Python+gdspy 生成 GDS/CDL/rule，check.py subprocess 真跑候选 on hidden B，判分机无需真 calibre/Aether，满足 §4.2）
- pg_layout 域新增 PG-split 甩脚/打标主题（与 PGLayout/PGAssemblyLVS/PRBoundary 主题不同：跨 pattern 镜像拼接 + PG_drawing 连接 + PG_pin ATTACH label + CDL 合并 + LVS rule 生成）
- cross-input guard: B 用同文件名但内部 cell 名/尺寸/W-L 不同（NTN_variant_B/GateRes_variant_B），硬编码 A 名的解在 B 上失败

## 阻塞/备注
- 真实 mkntn.py 已不在远端（ls 报 No such file），从 editor event 复现；末版逻辑完整、py_compile 通过
- status=failed 系 stale 进程退出，非用户拒绝；单轮委托无显式"成功了"轮 → gold = assistant 末版交付物，人工复核（按 spec 验 GDS/CDL 结构正确）
