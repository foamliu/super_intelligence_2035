# Deepread r929 — oa2tl (pdsong @ hfeg0pgn024) — calibredrv 16 分支→三角函数坐标变换重构

**session**: `1795003452646_oa2tl.messages.json` · 129 msgs · mc=68 · keywords calibre:491/.gds:178 dominant · domain=physical_verify
**user**: pdsong @ hfeg0pgn024
**路径**: `/home/pdsong/script/PDN_scripts/getLocbycells/getLocbyDecendCells.tcl` (calibredrv TCL, 抓 descendant cell M0-M3 pin 坐标 → PDN.ploc)

## 真实任务流（7 个 user turn）

1. **msg 0** 分析脚本 → assistant 读 tcl + 同目录 cellspin.txt/cells.rep/PDN.sp/location_transform.tcl，给出 calibredrv 脚本完整分析。
2. **msg 7** "结果回去看 gds 坐标没在 M2 上" → **根因=单位混用**：cellspin.txt 的 `loc`(如 52.16,7.68)是**微米**，而 calibredrv `iterator ref` 返回的摆放原点 `$x/$y` 是**数据库单位**(整数，grid≈4000 db/um)。原公式 `($x_bot + $x)*$mag/$grid` 把微米直接加 db 再整体÷grid → 微米偏移被 grid 除掉(52.16→0.0130um，几乎没生效)，pin 落到 cell origin 不在 M2。**修复**: loc 先 ×grid 转 db 再加：`set x_bot [expr {$x_bot * $grid}]`。用 unit_check.py 验证修改前 -2886.990(吻合 PDN.sp 错误值) → 修改后 -2834.843(52.16um 偏移被还原)。
3. **msg 21** "包装成命令行参数(gds + cellspin input)" → 加 `-gds/-input/-out` flag 解析 + 位置参数回退 + 环境变量回退(GDS_FILE/CELLPIN_FILE/PDN_OUT) + PrintUsage proc + 缺参/gds 不存在报错。
4. **msg 21→54** 验证暴露 2 个 **TCL 真实 bug**：
   - `puts "... [-out <PDN.sp>] ..."` 双引号内 `[...]` 触发**命令替换**(-out 当命令执行) → 改花括号 `{}`。
   - `switch ... -h -help { set showHelp 1 }` 多 pattern 共用 body → 词数奇数 → `extra switch pattern with no body` → 拆成 `-h`/`-help`/`--help`/`help` 各独立分支。
   - 用 tclsh(本机有 /usr/bin/tclsh) 验证 -h/--help/no-arg/bad-gds/位置参数全部正确。
5. **msg 61** "注释行中文改英文" → 3 处中文注释(头部用法/位置参数回退/环境变量回退)+ 补回单位换算修复的英文说明注释。ascii_check.py 扫描 non-ASCII lines: 0。
6. **msg 79** 重新分析 → 发现文件被加了 bash 自执行包装头 `#!/bin/bash` + `exec calibredrv "$0" "$@"`，默认输出改 `.ploc`。
7. **msg 83** "-h 输出的是 calibredrv 的用法不是脚本用法" → calibredrv 拦截 `-h`。本机 calibredrv VCO=aoi vs aok 环境不匹配跑不起来，但推断 calibredrv 只拦截自己认识的选项，不认识的透传。**解决**: 加 `help`(无横线) 关键字分支(calibredrv 不当自己选项) + PrintUsage 加提示 `-h is consumed by calibredrv itself`。tclsh 验证 help/-h/-help/--help 全部打印本脚本用法。
8. **msg 107** "坐标转换繁琐易错，用三角函数实现" → **核心重构**：原 16 分支(mirror 0/1 × angle 0/90/180/270，每段几乎重复的坐标换算) → 统一旋转矩阵：
   ```tcl
   set m     [expr {$mirror == 0 ? 1 : -1}]
   set theta [expr {$angle * 3.141592653589793 / 180.0}]
   set y0    [expr {$y_bot * $m}]
   set x_rot [expr {$x_bot * $cos_t - $y0 * $sin_t}]
   set y_rot [expr {$x_bot * $sin_t + $y0 * $cos_t}]
   ```
   - 用 replace_block.py(行定位+括号配平)替换 127-232 行(16 分支) → 文件 241→136 行，花括号配平=0。
   - **等价性验证** verify_trig.py: `orig()`(16 分支) vs `trig()`(旋转矩阵) 对 16 个 mirror×angle 组合 **0 mismatch**，且 trig 支持任意角度(30°/-45° 等)。
   - 保留完整管线: `(x_rot + $x) * $mag / $grid` → `%.3f` + round → port name。

## 合成 (档B fixture-driven reframe)

- **reframe 聚焦** msg 107 的三角函数重构 = 最自包含、最可判分的核心价值。
- **gold**: trig_transform.py 实现 `trig_transform(mirror,angle,x,y)` 旋转矩阵 + `orig_transform`(16 分支金标准) + 16-case 等价性自检 + 任意角度(30/45/-45/120) + 完整坐标管线(loc micron×grid→db→rotate→+origin×mag÷grid→%.3f+round→port name)。
- **A** cellspin_a.txt: 4 cells(VcslStbyIPTOP/VcslActYdecIPTOP/VcslpPumpCoreUpIP/VcslPrechIPTOP)/6 pins，角度∈{0,90,180,270}，mirror 0/1。真实 cell 名 + 合理 db origin。
- **hidden B** cellspin_b.txt: 3 cells(DqPreamplpIP/DqSabeNandIP/ClkDqDblTop)/6 pins，含任意角度 30/45/-45/120 + 0/90 cross-check，不同 power(vdda!/vdio!/vdd!)。B≠A(cells/coords/angles/powers 全异)。
- **ref_16branch.py**: orig 16 分支 Python 镜像(金标准)，仅支持 0/90/180/270，任意角度 raise。
- **check.py k=14**: 结构(a/b/c) + 等价性(d) + 任意角度(e) + 格式(f/g/n) + 数值正确(h/i) + 镜像(j) + 反硬编码 A(k) + B≠A(l) + 3-seed(m)。
- **3 neg**: naive_empty→c / naive_print→f / neg_delete_core→d，FAIL-distinct。
- grid=4000 取自真实脚本 `[$L units microns]`。

## 落库
- C.jsonl 567→568 (CoordTransformTrigRefactor-001, physical_verify, k=14)
- ref PASS 14/14 + 3 neg FAIL-distinct + §4.9(a)(b)(c) + roundtrip sha256 770a973876d51fd7 ✓
- ledger mark oa2tl → case
