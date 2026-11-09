# z9zx7 — replace_modules.py 修复（endmodule 拼接 + celldefine 包装器保留）

## trace 元信息
- sid: `1793846610746_z9zx7`
- user: cliu @ hfeg0pkn004
- match_count: 161
- domain: schematic_netlist（系统级 SV 标准单元库模块体替换）
- trace 路径: .75 `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/default_designflow_designflow-D-443_0/z9zx7.json`（416 msgs）
- 选取状态: claimed @ 2026-11-09 12:54，本 deepread 后 → case

## 用户原始诉求（U#335 / U#338，原文）
> 帮忙修改脚本 @/home/cliu/drcoa/1022/replace_module/digital/replace_modules.py
> 目前出现上一个cell的endmodule和下一个cell的module连在一起的问题以及需要保留
> 每个cell的 `celldefine 和 `endcelldefine，把新脚本放在目录
> @/home/cliu/drcoa/1022/replace_module/digital

用户给了**现象（两个 bug）+ 目标行为**，未指根因 → A 档任务说明可用原文。
该 session 早段还有 stdcell/ddr6 仿真编排（U#0/U#129/U#210，用 tb_family skill 跑
xrun），与本案无关，**仅 U#335/U#338 的 replace_modules.py 修复是 case 主题**。

## 真实数据规模（agent _probe/_repro_real 实测）
- `new_cells.txt`（fileB）17164 行，267 个 module
- `simlib_drcoa_digital.sv`（fileA）46574 行
- `simlib_drcoa_digital_new.sv`（既有输出）33382 行

## agent 复现 + 根因定位（msg #336–406）
1. 读旧脚本 + 列目录 + 读 new_cells.txt。
2. `_repro_real.py` 调旧 `parse_modules`/`replace_modules` 跑真实文件：
   - **fileB 265/267 个 module body 末尾无换行**（贪婪 `\s*` 把 `endmodule` 后的换行
     吃掉了）。
   - 旧输出 `_out_real.sv` 跑出 **269 replaced**，并出现 **16+ 条 joined 行**，
     形如 `endmodule`celldefine`（行 311/751/...）—— 正是用户报的 bug 1。
3. `_validate2.py` 统计包装器：
   - fileA `simlib_drcoa_digital.sv`：`` `celldefine ``=633 / `` `endcelldefine ``=637
     （**自身已失衡 4**，pre-existing）。
   - fileB `new_cells.txt`：272 / 272（平衡）。
   - 旧输出：包装器被贪婪 span 一起换掉/错位 —— 用户报的 bug 2。
4. `_validate3.py` 用无歧义判定（`endmodule` 同行后跟 `` `celldefine `` 或 `module `）
   确认**真实 joined = 0**（早先 `validate2` 的 `"module "` 是 `"endmodule "` 子串误报）。

## agent 修复方案（msg #377 / #387 / #394 / #406 总结）
重写为**顶层扁平 module 扫描器**：
- `parse_modules`：对每个顶层 `module <name> ... endmodule`，存 body **保证以 `\n` 结尾**
 （剥多余尾换行再补恰好一个）。
- `replace_modules`：扫 fileA 顶层每个 `module ... endmodule` span（连同其后**恰好一个**
  换行）；名字在 fileB 出现则只换**内层 body**，fileA 的 `` `celldefine ``/`` `endcelldefine ``
  + 空行 + 注释**原样保留**；fileB 无同名者**逐字节保留**。
- 验证（`_validate.py`/_validate3.py）：joined=0、fileB body 缺尾换行数=0、
  `` `celldefine ``=823 / `` `endcelldefine ``=827（失衡 4 = fileA 自带，非脚本引入）。
- 清理所有 `_*.py` 临时探针，目录仅留原数据文件 + 新 `replace_modules.py`。

## A-faithful 为何不可复刻 → B-grade synthesized
真实金标准依赖 `/home/cliu/drcoa/1022/replace_module/digital/` 私有源树
（46574 行 simlib + 17164 行 new_cells），沙盒不可复刻。故抽成自包含小型 SV 库：
- 公开 A：`simlib_A.sv`（5 模块，4 `` `celldefine ``/4 `` `endcelldefine ``，nand2_a/nor2_a
  包装器紧挨）+ `new_cells_A.sv`（2 替换体 nand2_a/dff_a）。
- 隐藏 B：`simlib_B.sv`（6 模块，5/5 包装器，or2_b 紧跟 and2_b 无空行、xor2_b/latch_b
  紧挨）+ `new_cells_B.sv`（3 替换体 or2_b/xor2_b/tri_buf_b）。
- 模块名/数量/包装器布局/模块体内容全不同 → 反硬编码。
- 跨输入 guard：候选跑 (simlib_B, new_cells_A) 名字无交集 → 0 替换且输出 == simlib_B 字节一致。

## 与既有 case 的区别性
- `NetlistCellReplace-001`：做 **cell 名替换 + 结构变更**（subckt 重命名/拆并）。
- 本案 z9zx7：**纯模块体内层 swap**，fileA 包装器/空行/注释原样保留，fileB 包装器被忽略，
  仅按名匹配换 `module...endmodule` 内层。操作语义不同，非重复。

## 判分（check.py，14 条 a–n，k_rationale=k_check=14）
a zip 含 .py / b py_compile / c B 退出 0 非空 output / d output 可解析 module /
e 无 joined 行 / f `` `celldefine `` 计数==fileA_B(5) / g `` `endcelldefine `` 计数==5 /
h 替换集合=={or2_b,xor2_b,tri_buf_b} / i 保留集合=={mux2_b,and2_b,latch_b} 逐字节保留 /
j 每 body 以 \n 结尾 / k 模块名集合==fileA_B / l 模块数==6 /
m 反硬编码 (simlib_B,new_cells_A)→0 替换 output==fileA_B / n 3-seed md5。

## 自验
- ref PASS 14/14（CLI 全跑）。
- §4.9 三假 distinct FAIL：empty→c / print_expected(echo fileB)→f / core_deleted→h。
- 3 neg distinct FAIL：naive_no_newline→e / naive_drop_wrappers→f / naive_hardcode_b→m。
- negative_selftest NEG_RC=0（ref PASS + 6 全 FAIL）。
