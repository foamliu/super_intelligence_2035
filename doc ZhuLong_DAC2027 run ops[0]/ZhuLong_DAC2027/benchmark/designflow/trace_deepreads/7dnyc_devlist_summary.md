# deepread: 7dnyc — device-list summary CSV generator

- **trace**: 1793873169781_7dnyc.messages.json, hairuizh @ hfeg0pkn002, 76 msgs / 4 user turns, mc=80
- **domain**: schematic_netlist (SPICE device list → statistical CSV summary)
- **keywords**: 149 schematic 44 netlist 26 hspice
- **session path**: /home/hairuizh/.cline/data/sessions/1793873169781_7dnyc/1793873169781_7dnyc.messages.json

## user intent (verbatim, A-grade 选轮)
- U#0 (CLEAN PRODUCE, A-grade 候选): `@//proj/drcoa/V0/workdir/hairuizh/simulation/drcoa_array_XdecGapTop_DRCOA_schematic_ALPS/all_devices_list.txt 将该文件总结为两份csv文件，要求分别如下 1. 将所有相同名字和length的device合并成一项，width和nf相加，计数也相加 2. 将所有名字相同的device合并成一项，width和nf相加，计数也相加，length取平均值`
- U#18 (correction, NOT A-grade task): `你是不是搞错了什么，nf和width相加是要考虑数目的呀` — aggregation must WEIGHT nf/width by UsedNumber (count)
- U#28 (extend): `同样处理 @/proj/degnt/V0_CMOS/.../all_device.txt` — second file
- U#42 (extend): `添加以下几项... 1.平均每个管子的width 2.平均面积=length*width 3.真实平均width=平均width*shrink 4.真实平均length=平均length*shrink 5.真实平均面积=真实平均width*真实平均length; 第一个文件shrink=0.256, 第二个=0.855`

## input file format (all_devices_list.txt)
```
# Total Area: 129048.59848
##Device TotalWidth Length nf UsedNumber
ntk 0.90000u 0.47900u 1 48
ntk 1.00000u 0.47900u 1 96
ntk 10.00000u 0.47900u 4 48
...
```
cols: Device, TotalWidth(带u), Length(带u), nf(int), UsedNumber(int). 真实文件 ~40 rows, device names: ntk/ntk_hv/ntk_lv/ntn/ntn_lv/ntn_m/ptk/ptk_lv/ptn/ptn_lv.

## assistant tool chain
read_files(input) → editor(process_devices.py) → run_approved_command(python3) → read_files(output CSV verify) → (U#18 correction) editor fix weighting → rerun → read_files verify → (U#28) editor add file2 → rerun → (U#42) editor add 5 columns → rerun → read_files verify → U#67/U#71 cleanup_drcoa.py remove temp. 用户接受（无 further correction）。

## gold standard (用户实际接受的结果)
`process_devices.py` 产 2 CSV per file (4 total):
- `<stem>_by_name_length.csv`: group by (name, length); 10 cols
- `<stem>_by_name.csv`: group by name; 10 cols
- **10 cols**: Device, TotalWidth, Length, nf, UsedNumber, AvgWidth, AvgArea, RealAvgWidth, RealAvgLength, RealAvgArea

## aggregation (corrected, weighted by UsedNumber)
- CSV1 (by name+length): TotalWidth=Σ(w_i×used_i); nf=Σ(nf_i×used_i); UsedNumber=Σused_i; Length=分组 length; AvgWidth=TotalWidth/UsedNumber; AvgArea=Length×AvgWidth; RealAvgWidth=AvgWidth×shrink; RealAvgLength=Length×shrink; RealAvgArea=RealAvgWidth×RealAvgLength
- CSV2 (by name): 同上但 Length=Σ(l_i×used_i)/Σused_i (加权均长)

## 验证（用真实 file1 ntk@0.479u 11 行）
- Σ(w×used)=43.2+96+480+720+120+245+960+156+192+240+240=3492.2 → CSV "3492.2u" ✓ (msg#26)
- Σ(nf×used)=48+96+192+288+48+196+480+96+96+96+192=1828 → CSV "1828" ✓
- Σused=626 → CSV "626" ✓

## A-faithful 判定
- 真实输入在 /proj/drcoa /proj/degnt（项目私有 Permission denied 不可附加）→ **A-faithful 不可行**
- → **B 档 synthesized**：用 trace 已暴露的真实数据格式造 A，造 hidden B（不同 device 名/数值/scale）+ B2（边例）
- 离线 L1 可验（纯数值聚合，无需 live SPICE）

## 合成 plan
- generator: `device_summary.py --input <list.txt> --shrink <s> --outdir <d>` → `<stem>_by_name_length.csv` + `<stem>_by_name.csv` (10 cols)
- A: 真实前 ~30 行（ntk/ntk_hv/ntn/ptk/ptn），shrink=0.256
- hidden B: 不同 device 名（nch/pch/nch_hv/pch_hv/nch_lv）+ 不同数值 + 不同 scale，shrink=0.855
- hidden B2: 边例（单名 2 length + used=1 行，测 weighting + 单组）
- check 16 条件 a-p: 防泄漏+py_compile / B-exit0+2文件 / CSV1 header 10列 / CSV1 行数=unique(name,length) / TotalWidth=Σw×used / nf=Σnf×used / UsedNumber=Σused / AvgWidth=TW/used / AvgArea=L×AvgW / RealAvgW=AvgW×shrink / RealAvgL=L×shrink / RealAvgArea=RealAvgW×RealAvgL / CSV2 行数=unique(name) / CSV2 Length=加权均长 / 反硬编码无A标记+A≠B / B2 边例守卫 / 确定性 3× sha256
- 反硬编码轴: device 名(A: ntk系 vs B: nch系) + 数值规模不同 + shrink 不同(0.256 vs 0.855) + B2 单组边例
