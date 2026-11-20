# rs1eo — TclAreaCsvAnnotate (schematic_netlist, B-grade L1)

- **trace**: 1793089586575_rs1eo · rose3wang@hfeg0pkn003 · mc=18 · netlist:71;cmos:28
- **user原话 (U#0, 逐字)**: 「/proj/lacaa/V0/workdir/rose3wang/DK/TimingLib/Pra_1/cell_area.csv /proj/lacaa/V0/workdir/rose3wang/DK/TimingLib/Pra_1/gen_template/template_verbose_v1.tcl 吃csv文件，修改tcl里面对应的area」（用户重复 3 次 U#0/U#1/U#2 同一需求；U#3「输出文件在哪里，python呢」追问产物位置）
- **意图**: 读 cell_area.csv（cell,area 两列），把 template_verbose_v1.tcl 里 set_cell_define 块中对应 cell 的 ` area <val>` 属性值替换为 CSV 给的值，原地写回（或输出到指定文件）。
- **真实数据形态**:
  - CSV: `cell,area` header + 行（实测仅 2 行：PDCAP,12.000 / PFILL005D_X,3.555）
  - TCL: 638 行；典型块结构：
    ```
    ### define template for cell PDCAP###
    set_cell_define  \
               -attrs " area 369.729549" \
               PDCAP
    ```
    area 属性行 = `-attrs " area <float>" \`（area 前有一空格）；cell 名在后续 1~4 行（中间可能夹其它 `-attrs` 行或纯 `\` 续行）。
- **金标准机制**（agent update_area.py 逐字读自 rose3wang workspace，self-contained 化）:
  1. `csv.DictReader` 建 `area_map{cell: area}`
  2. 逐行扫 TCL；遇含 `-attrs "` 且 ` area ` 的行 → 向后 1~4 行找 cell 名（跳过纯 `\`、`-`/`\`/`#` 开头行，取首个词）
  3. cell 在 area_map ⇒ `re.sub(r'area\s+[\d.]+', f'area {new_area}', line)` 替换
  4. 写回（argparse: `<csv> <tcl> [-o out]`，无 -o 则原地改）
  - 实测结果：PDCAP 369.729549→12.000（行415）、PFILL005D_X 5.6051→3.555（行509），modified_count=2
- **B-grade 合成设计**（A/B/C 不相交）:
  - A（SUT 可见）: 4 cell filler/cap 家族（PDCAP/PFILL005D_X/DCAP_HV/ANTENNAN_X2），4 种 block 结构（cell 名 1/2/3 行后 + 夹杂 decoy -attrs）；2 个 tcl 里有但 CSV 没有的 cell（保持不变，测「不误改」）
  - B（hidden）: 5 cell 不同家族（FILL1_X/FILL2_X/DCAP_X4/ANTENNAD_X8/DCAP_V3），area/block 顺序/结构全不相交；3 个 tcl-only decoy cell
  - C（嵌入 check.py）: 4 cell 又一家族（BUMP_X/DCAP_M2/POCAD_X/FILLT_X1），反硬编码
  - 边界用例：空 CSV（仅 header）→ 不改；CSV cell 不在 tcl → 不崩；无 set_cell_define 的 tcl → 原样输出
- **维度正交论证**（非 dup）: 现有 CSV 类 case = SpfMosCapRatio（DSPF cap 求和比例）/ #543 CsvBackfillTableUpdate（Qt C++ 表格回填，软件工程非 EDA）/ all_devices_list 加权 CSV 生成 — 均「生成/汇总 CSV」或「C++ 表格回填」，本 case = 「CSV 驱动 TCL area 属性定点替换 + set_cell_define 块结构 look-ahead 解析」，机制不同。✓
- **SUT**: `tcl_area_csv_annotate.py` 纯 stdlib（csv/re/sys/argparse），禁 subprocess/socket/urllib/ctypes/eval/exec，禁 B/C 字面量。
- **check.py 14 条件 a-n**: 独立 oracle（o_parse_blocks / o_apply，不 import SUT）+ subprocess 真跑 SUT on B/C/empty/missing/unrelated + 3-seed sha256。
