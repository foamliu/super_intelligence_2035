# trace_deepread: xyou8 — SV used-model extraction (spice_sim, A-faithful)

## 来源
- session: 1793956185129_xyou8 (dir-based)
- user: e0039602
- host: hfeg0pkn004
- msgs: 174, 452967 bytes
- spice keyword matches: 116 (simlib/simulator/vcs)
- mtime: Nov 6

## 用户意图轮（A-faithful 选轮）
- U#1（逐字）：「这个目录下有三组v网表和sv文件对，（copy不用管）请你在三个SV文件当中所有能在网表中找到的model都提取出来（即sv里的model名在网表里被用了，舍弃没有被用的model），构成一个新的格式规范的SV文件，把三个文件里面查到的构成一个」
- 提出 need/goal，无根因、无修复方向 → 符合 A-档选轮 ✓
- U#98（澄清，不入 prompt）：「每个model前面后面不是都有`endcelldefine和`celldefine吗，这个也要保留的」→ 金标准需保留 celldefine 包裹

## 文件对（/home/e0039602/Documents/golden/）
| netlist | simlib SV |
|---|---|
| final_merged_netlist_digitial.v (1.0MB) | simlib_drcoa_digital.sv (2.65MB, 629 modules, 635 celldefine 对) |
| final_merged_netlist_stdcell.v (1.1MB) | simlib_drcoa_stdcells.sv (2.4MB) |
| final_merged_netlist_stdcells_ac.v (2.2MB) | simlib_stdcells_ac.sv (3.0MB) |
- copy 文件忽略（simlib_drcoa_digital_copy.sv）

## 金标准（assistant 末轮完整产物）
- 判定规则：SV model 名 ∩ 网表 module 定义名 = used（网表里真用到的 cell）
  - 助手先试 instance 匹配（INST_RE），命中太少；后改 module 定义匹配（v_mod_names），命中 276+381+887
- 保留每个 model 连同其 `\`celldefine ... \`endcelldefine` 包裹（逐个，非全局一个）
  - digital 有 5 个 model 无 celldefine 包裹（仍保留 model 本体）
- 跨三对去重（按名字），合并成一个 simlib_used_models_merged.sv
- 最终：1543 unique models，1543 `endmodule，无重复、无截断
- 内部一致性校验：36 子模块引用中 6 个在合并文件内已有定义，0 个引用「被舍弃的 model」（无依赖缺口）

## 助手脚本逻辑（_extract2.py）
```
HDR_RE = re.compile(r'\bmodule\s+(\w+)(?:\s*#\s*\([^)]*?\))?\s*(?:\(|;)')
module_names(text) = set(m.group(1) for m in HDR_RE.finditer(text))
extract_cell(text, name):
    找 module name 的 header → endmodule
    向后搜最近未闭合 `celldefine（rfind + 检查中间无 `endcelldefine）
    向前搜 endmodule 后首个 `endcelldefine（仅当有 leading wrapper）
    返回 text[wrap_start:wrap_end]
used = sv_names & v_names; dropped = sv_names - v_names
merged dedup by name (first occurrence)
```

## 合成方案（case: EDA-Eval-DesignFlow-SvUsedModelExtract-001）
- A（真实节选，小规模）：3 对 netlist_*.v + simlib_*.sv，每对 2-3 module
  - pair1: invY/invYx4 used + AbusDrv_unused dropped
  - pair2: nand2/bufLx12 used + CK_LbusDrv_unused dropped
  - pair3: inv(无celldefine)/bufLx24 used + dropMe3 dropped
- hidden B（合成，不同名字/结构）：
  - pair1: invX/bufZ used + dropB1 dropped (sv_total=3)
  - pair2: and2/or4 used, 0 dropped (sv_total=2)
  - pair3: xor5(无celldefine)/mux2 used + dropB3 dropped (sv_total=3)
  - merged 6 (无跨对重叠), all_have_celldefine=false (xor5)
- reference: extract_used_models_ref.py（通用化，6 文件 + -o out.json）
- check.py 14 断言(a-n)：含交叉输入守卫(k: A pair1 kept=={invY,invYx4} & A merged==6) + A-only 泄漏闸门(l) + 3 次幂等(m)
- negatives: naive_hardcode_a(FAIL f)/print_expected_b(FAIL k)/empty_shell(FAIL c)/core_deleted(FAIL j) — 4 distinct
- 自验：ref PASS 14/14 + 4neg ALL FAIL distinct(f/k/c/j) + NEG_RC=0 + §4.9 三假(c/k/j) FAIL + 断言闸门 14==14≥8
