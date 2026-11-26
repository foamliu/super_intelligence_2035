# deepread — rl62o (cliu @ hfeg0pkn004, mc=216, schematic_netlist)

## trace
- session: 1793754046092_rl62o, 136 msgs, 501KB, single user turn
- scp from hfeg0pkn004:/home/cliu/.cline/data/sessions/1793754046092_rl62o/1793754046092_rl62o.messages.json

## user intent (U#0, 逐字原文, A-grade seed ✓ — 提出目标，未给根因/修复)
> 请用@/home/wellesc/runStdCellTB/tb_family环境检测这个目录@/home/cliu/drcoa/1022/tb_skill/simlib_drcoa_stdcells.sv文件有没有逻辑写错的情况

## assistant gold chain (msg 1-135)
1. policy check + list_allowed_files on /home/cliu/drcoa/1022/tb_skill 和 /home/wellesc/runStdCellTB/tb_family
2. read simlib_drcoa_stdcells.sv + Readme.md + SKILL.md
3. explore: 1578 modules (1529 unique) in simlib; tb_family 部署缺 families_index.json/src/templates/golden_dut 但 base lib + tb templates 存在
4. _map.py: 1529 unique modules → 1411 mapped to tb family, 118 NOT mapped; per-family counts (inv/inven/invhiz/nand3/nor2/nor3/oai21/aoi21/aoi22/mx2/latq/buf ...)
5. _declcheck.py (static): for each module, parse header port list vs declared input/output/inout → find HEADER_NOT_DECLARED defects
   - 初版 regex bug (depth=0 错过开括号) → 16492 false positives → 修 depth=1 → 305 flagged
6. xrun 编译 pilot cell (invLVCAx1) TB → rc=1 → grep_log → `xmvlog: *E,INVLIO (simlib_drcoa_stdcells.sv,10|36): port 'vwlp' not declared input/output/inout`
   - **确认真缺陷**: module `latqYx1` (line 10) header 列出 port `vwlp` 但从未声明方向 → 整文件无法编译
7. _fixcopy.py: 生成 simlib_fixed.sv (给 latqYx1 的 vwlp 加 inout 声明), 79997 lines
8. xrun 编译 fixed copy → rc=0, 0 errors → 确认 latqYx1 的 vwlp 是唯一 compile-blocking 缺陷（其余 304 static flag 是 packed one-line 声明/named port 的 false positive）
9. 行为验证: tb_family TB 跑 14 pilot cells (invLVCAx1/nand2CSColx1/nand3CSColx1/oai21GFSx2/aoi21LFsRowx1/invenMx1/.../latqYx1) → 全 PASS (chk=N miss=0)
10. _gen_batch.py: 生成 167 canonical TBs across 12 families; _mkbatches.py: 12 batches; 批量跑

## 金标准（用户实际接受的结果）
- 唯一 genuine compile-blocking logic defect: **module `latqYx1` (line 10), header port `vwlp` 未声明方向（input/output/inout）**
- 修复后整 1529-module 文件 xrun 编译干净 (rc=0)，14+ pilot cells 行为 TB 全 PASS
- 其余 304 static HEADER_NOT_DECLARED flag 是 false positive（packed one-line 声明）
- 118/1529 modules 未映射到 tb family（无对应 TB 模板，非缺陷）

## 资产获取
- /home/cliu/drcoa/1022/tb_skill/simlib_drcoa_stdcells.sv: cliu 私有，80K 行过大 → 采 B-grade synthesized
- /home/wellesc/runStdCellTB/tb_family: wellesc 私有 → 同
- 合成忠实复刻 trace 结构: SV simlib (多 module + header/declared port + ONE undeclared-port defect) + tb_family 环境 (Readme/SKILL/lib base/scripts/templates)

## case 设计
- id: EDA-Eval-DesignFlow-SimlibLogicCheck-001
- domain: schematic_netlist, B-grade synthesized, L1 (offline Python 静态解析 SV)
- A: simlib_drcoa_stdcells.sv (30 module, defect=latqYx1/vwlp) + tb_family/ (Readme+SKILL+lib+scripts+templates)
- hidden B: simlib_drcoa_stdcells_B.sv (35 module, defect=oai22CSx1/vssx) + tb_family_B/ (不同 family 分布)
- ref: analyze_simlib_logic_ref.py (parse SV → modules + header/declared ports → HEADER_NOT_DECLARED defects → family mapping → report.json)
- check.py: 15 条 a-o (zip/py_compile/B-run exit0/顶层键/total_modules/mapped/unmapped/defects list/defect 字段/compile_blocking module/compile_blocking port/families dict/family_coverage/3-seed md5/反硬编码 A≠B)
