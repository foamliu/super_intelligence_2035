# 深读笔记 r255 — trace poh36 (m1wang) — CM MA/OP Address Table Generator

- **session**: 1793861227844_poh36 (m1wang@hfeg0pkn002/10.129.2.11, mc=398, kw=270pyAether+34dbGet+16cellview+4calibre+2virtuoso; NEW user m1wang; agent=lead, 430 msgs)
- **选料**: sel_C_r255.py(内置 441 ledger sids 排除 + SAT users incl adaml/mwxi/yohannw/hbpeng/e02141/e0023936/e0047527/gurmanli/rayfeng, layout-affinity score=ΣLAY−0.6×ΣSIM, core=calibre+virtuoso+aether+lvs+drc+innovus≥10)在 .75 上跑 summary.tsv → 67 fresh NEW-user cand。探针 9 条: d0ild(xiwang mode=act schematic-hierarchy SCMOS-finding wrong-domain)/iz8r1(gurmanli env-recon "aether可以load本地脚本吗" parked)/1488k(rayfeng Sentaurus TCAD MCP wrong-domain)/i0izd(e0048306 SKILL CountInstances learning vague pinyin)/w6omm(e0045488 K-library .lib PVT分析 wrong-domain)/7uwtz(e0016033 "hello"+"启动业务场景" skill-activation no-task)/mirbg(yohannw permission denied)/uo4ma(jeoteanl "分析WlvEnDlv信号作用" prose gold violates §4.2)/poh36(m1wang mc398 concrete CM table task)。**poh36(m1wang mc398)**→**organic layout_aether seed**。

## 用户真实意图
- **U#1 (idx=0, mode=act, 提出需求)**: 「你是一个数字电路设计工程师...DRCPA项目...研究DDR5...模块是CM(测试模式)...从TOP层出发查找名称中带有CM的所有cell,并可视化显示出其在电路中的分布」
- **U#2 (idx=178, 提出需求, 未给根因)**: 「在DRCPA项目电路中drcpa_digital的library库中找到Cell名称依次为T_CM4PGen T_CMAry_1...T_CMTsac的cell模块输出CM table，表头为MA(O) MA(H) OP Category Module Name CM Name CM Block...输出名称为CM table+当天日期的Excel文件」(给出列名 + 示例行 `0000 000 0 Test cm0_ts_AsynCkeEn cm0_ts_AsynCkeEn T_CMCenterR`)
- **U#3 (idx=239)**: 同 U#2 + 给出 Aether 菜单路径「CXMT-DFT Toolkit-CMFuse Latch-Generate CM MA/OP Address」

## grounding (agent 真实工作)
1. list_allowed_files / run_approved_command 探项目结构 → DRCPA 主项目 `/proj/m2701/V0_DDR2`，库名 `drjpa_digital`(用户拼成 drcpa_digital)，drjpa_digital 含 1264 cells，T_CM* 实际存在的: T_CMCenterL/R, T_CMAry, T_CMDq, T_CMDqPad/Pad10/32/54/76, T_CMLeft_L1/R1, T_CMRight（部分用户列出的不存在: T_CM4PGen/T_CMAry_1/_2/T_CMDQMid/T_CMDqsbst/T_CMTsac）。
2. pyAether sandbox 试 dbOpenCellViewByType 遍历层次 → sandbox 内部问题，转而读 CAD 源码。
3. **关键 grounding**: read_files `/apps/imctf/cad/init/settings_cdns/skill/special/se/CXMTseGetAllLatchInfo.il`(526 行，真实 DFT 工具源码) + `CXMTseGetLatchInfo.il`。找到菜单 "Generate CM MA/OP Address" = SKILL 函数 `CXMTseGetAllLatchInfo_GUI()` → `CXMTseGetAllLatchInfo(mainForm)`。
4. CXMTseGetAllLatchInfo.il 核心逻辑(已读 120-300 行):
   - `cmStautsTable`: ag→Analog, cl→Column, fc→Function, id→IDD, io→IO, ro→Row, ts→Test, sp→Spare; ddcpb/ddjoc/degpa/degnt 还有 gc→GlobalFunction, rf→Refresh, sc→Scrc, ta→TimingAdjust
   - 输出 CSV `allCMAdr_MAandOP_<date>.csv`，表头 `MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block`
   - `LatchList = rexMatchList("^Cm.*Latch", cells)` 取 latch cell；对每个 CMLatch (T_CM*) dbOpenCellViewByType → CXMTseGetAllLatchInfo_ByCell 填 testmodeInfoTable(key=MA八进制, value=每OP的[cellNameList,op,tmFullName,module])
   - `MALen = length(第一个MA地址key)`；`MAFullLen = 1023 if MALen>3 else 511`
   - extract_sel=Yes: `for(i 0 MAFullLen)`: ma_oct=oct(i)补零到MALen, ma_hex=hex(i)补零到3; 若 ma_oct 在表: 取 entry[j], 非null→计算输出, null→**跳过不出行**; 不在表→输出 `NA,NA,NA,NA`
   - extract_sel=No: `foreach(k sort(keys))`: 仅存在的地址, 不填NA
   - Category: tmFullName 按"_"拆, 第2token→cmStautsTable; sp→"Spare"+`cm([0-9])`单数字; 
   - cellNameStr = `buildString(ciUtilsMakeUnique(cellNameList) ";")` 去重join
   - Cm2Table 行: `NA,NA,NA,cm2Category,cm2Module,cm2,cell`; cm2Category 第2token(sp→"Spare2"); cm2Module=`(.*)<[0-9]*>`去后缀, 全局去重(cm2ModuleList)重复留空
5. agent 写 gen_cm_table.il(在 Aether CIW load 后调用 CXMTseGetAllLatchInfo)，因 editor size limit 分块写。最终 idx=429 给出完成总结(T_CM* 实际存在清单 + gen_cm_table.il)。

## 为何 B 档重定义为参数化离线 CM-table 生成器
真实 DRCPA/drjpa_digital 库对 e0031982 在 pyAether sandbox 不可访问(项目特定、需真实 Aether 环境)；原交付物 gen_cm_table.il 是调用 CXMT 工具的 SKILL 壳，数值/结构随项目变。故用 trace 的 CXMTseGetAllLatchInfo.il 核心逻辑 grounding，重定义为 `cm_maop_table.py <input.json> -o <out.csv>`(stdlib only)，喂合成的 testmode-info JSON dump(从原理图收集的数据 + 项目配置)。

## 重定义
`cm_maop_table.py <input.json> -o <out.csv>`(stdlib only)，解析 JSON{project, extract_sel, ma_len, category_table, testmode_len, testmode_info{ma_oct:[entries per OP]}, cm2_table[{cell,cm2_names}]}→生成 CSV。
- ma_full_len = 1023 if ma_len>3 else 511
- extract_sel=Yes: for i in 0..ma_full_len: ma_oct=oct(i)补零ma_len, ma_hex=hex(i)补零3; 每 OP: 在表且非null→输出数据行, 在表但null→跳过, 不在表→NA行
- extract_sel=No: for ma_oct in sorted(keys): 仅非null→输出
- Category: tm_full_name split"_", token[1]→category_table; sp→"Spare"+`cm(\d)`首数字
- cellNameStr: unique(cell_names) join";"
- Cm2Table: NA,NA,NA,category(token[1],sp→Spare2),module(去<N>后缀,全局去重),cm2,cell

## DISTINCT from 现有 layout_aether 系
r254 EmyCdlNetlistExtract(schematic→CDL netlist)/r253 PinListPortOrderExtract(cellview terms pin 枚举)/r252 LayStructExtract(layout DB shapes/instHeaders 结构)——本案**首次 ground on Aether CXMT DFT Toolkit CM MA/OP Address 表生成**(CXMTseGetAllLatchInfo.il: MA 八进制/十六进制换算 + 全枚举 NA 填充 + Category 分类 + Cm2Table 去重)。

## case 结构
assets/A(cm_input_A.json ddjma extract_sel=Yes ma_len=3 testmode_len=3, 6 MA keys, 2 cm2 cells + prompt + task_brief)
+hidden(cm_input_B.json degpa extract_sel=Yes ma_len=4 testmode_len=2 扩展category gc/rf/sc/ta, 4 MA keys, 1 cm2 + cm_input_B2.json ddcpb extract_sel=No ma_len=3 testmode_len=3, 3 MA keys, 1 cm2 + cm_input_B3.json degnt extract_sel=Yes EMPTY testmode_info no cm2 + hidden_manifest)
+reference(golden_solution.py stdlib-only + golden_A/B/B2/B3.csv + check.py 17条件 a-q + negative/{empty_shell,print_expected,hardcoded_A,core_deleted,stub_no_parse}.py + negative_selftest.py + reference_submit.zip)

## 自验
- golden self-test 17/17 PASS ✓ (a-q 全过)
- negative_selftest 5/5 全 FAIL ✓ (empty_shell→a, print_expected→a, hardcoded_A→e/g/h/i/j/k/l/m/n/o/q, core_deleted→e/g/h/i/j/k/l/m/n/q, stub_no_parse→e/g/h/i/j/k/l/m/n/o/q)
- §4.9 三假提交(empty/print-expected/core-deleted)全 FAIL ✓
- test 字段==disk check.py 字节相等 ✓(14145B)
- 3-seed sha256(output_B) 确定性一致 ✓ (check 条件 p)
- 断言闸门: k_rationale=17=k_check(a-q)≥8 ✓

DEBT: 0
