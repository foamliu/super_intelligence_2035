# trace_deepread: 1793240332278_86t8o (rose3wang@hfeg0pkn003, mc=278)

**session**: 347 msgs (180 user / 167 assistant, agent=lead). DK/TimingLib multi-task session.
**keywords**: verilog:612;rtl:201;netlist:71;cmos:29;virtuoso:20;dbget:13;bandgap:10;aether:10

## 多任务流（USER 轮）
- [0-2] 吃 cell_area.csv 改 template_verbose_v1.tcl 的 area（旧 cell,area 格式）
- [70] 问 .lib 语法解释
- [72] **★ A档选取**「吃csv文件，修改tcl里面对应的area, 新的area = X * Y」+ 4 路径(sizes.csv/sizes_dbc.csv + v1.tcl/v2.tcl) — clean 需求, 无根因/无修复方案
- [101] 「以新的csv为准，整理新的area」(refinement)
- [111] 删 .lib 含 VDD_VSS 的行
- [139] 把声明端口改成表格内容
- [198] 按 top name 改 verilog 文件名 + 复制 TempSensor/Efuse 20 份
- [302] 写 psensor.v testbench 简单验证
- [336] psensor.v 造两个 150MHz 输出; tb CLK_IN 100M TR=3 (refinement, 给修复方向 → disqualified 作 A档)

## [72] 任务深读（A档金标准）
**意图**: 读 CSV 的 X,Y → 计算 area=X*Y → 更新 TCL 模板中对应 cell 的 area 值。
**agent 工具链** (msg 73-100):
1. read_files sizes.csv + sizes_dbc.csv (Cell Name,X,Y 格式)
2. read_files template_verbose_v1.tcl (lines 413-637) + v2.tcl 多段
3. 映射: sizes.csv(非DBC) → v1.tcl; sizes_dbc.csv(DBC) → v2.tcl
4. editor 重写 /home/rose3wang/update_area.py (msg 42→46→61→63→92, 最终 5749c)
   - 自动检测 CSV 列名: Cell Name,X,Y → area=X*Y; cell,area → 直接
   - 逐行扫描 -attrs " ... area <num> ..." 行
   - 向后 1~4 行找 cell 名(跳过 \ 续行符 / - 选项行 / # 注释)
   - re.sub(r'area\s+[\d.]+', f'area {new_area}') 替换
   - -o 输出或原地写回
5. run_approved_command python-runner 跑 v1(24/26 命中) + v2

## TCL 结构（trace-faithful）
**v1 简单格式** (PDCAP 块, msg 84):
```
### define template for cell PDCAP###
set_cell_define  \
              -attrs " area 369.729549" \
              PDCAP
set_pg_pin -voltage_name "COREVDD1" -pg_type "primary_power" VDDP PDCAP
```
**v2 复杂格式** (DBC IO cells, msg 86/89): -attrs 含 `area <val> pad_cell true pad_driver N bond_pads M`, cell 名 1 行后; -temp 行在 -attrs 之前。

## 真实 CSV 数据 (sizes.csv, 26 cells, msg 97 输出)
PCORNERD 109.905×109.905=12079.109025; PDCAP 49.317×7.497=369.729549;
PENDCAP_X 15.045×109.905=1653.520725; PFILL1D_X 0.969×109.905=106.497945;
PRCLAMPC_X 36.862×33.99=1252.939380; PTOD12UD4D_X 49.98×109.905=5493.051900;
PVDD1CDG_X 74.715×109.905=8211.552075; PVDD2POC_X 38.964×109.905=4282.338420; ...

## case 合成 (TclAreaUpdate-001, digital/eda_other, A档 faithful, L1-static+subprocess, 16 conds)
**最终版 (r273, 2026-11-09 收尾 DEBT 修复)**: 选取 USER#0-2 子任务(cell,area CSV 直读, 非 USER#72 X*Y) — 因 USER#0-2 cell,area 格式可程序化、可 hidden-B 跨输入泛化; USER#72 X*Y 亦可但首版 X*Y 资产与 cell,area check.py 不一致已被弃。
- 资产 A: cell_area_a.csv(cell,area 两列: PDCAP=12.000, PFILL005D_X=3.555) + template_verbose_v1_a.tcl(9 cell 块 set_cell_define/-attrs " area <old>"/cell 名, 含 PVDD2POC_X/Y 多属性 + PDCAP/PFILL005D_X 目标 + PFILL005D_Y 同值异名守卫 + PRCLAMPC_X/PRCLAMPP_X 同值异名守卫 + PFILL01D_X/Y + PFILL1D_X/Y, trace-faithful 重建)
- 泛化 deliverable: update_tcl_area.py (csv.DictReader 建 cell->area 映射 -> ATTRS_RE 匹配 -attrs " area <num>" -> find_cell_name 向后 1-4 行定位 -> re.sub 替换 area 保留同行其它属性 -> -o 输出或原地写回; 仅 Python 标准库)
- hidden B: cell_area_b.csv(cell,area: PRCLAMPC_X=42.0, PFILL1D_X=88.8, PFILL01D_X=7.77) 同模板跑 -> 测跨输入泛化(非硬编 A); 另 CSV_C(PDCAP,99.999) 反 area 值硬编
- check.py 16 conds(a-p): a zip 仅含 update_tcl_area.py / b py_compile / c A exit0+输出 / d PDCAP 369.729549->12.000 / e PFILL005D_X 5.6051->3.555 / f PFILL005D_Y 保持 5.6051(反 naive 全局值替换) / g PFILL01D_X 保持 11.2103(CSV 外不变) / h PVDD2POC_Y 多属性保留 / i 恰好 2 行差异 / j 行数一致 / k -o 源不变 / l B PRCLAMPC_X->42.0 / m B PFILL1D_X->88.8 / n B PFILL01D_X->7.77 / o B 不改 A cell 且 PRCLAMPP_X 不变(按 cell 名泛化) / p 反硬编 PDCAP,99.999->99.999
- 自验(r273): ref PASS 16/16 + 3 negs(neg1_noop->d / neg2_hardcode->d / neg3_nowrite->c)全 FAIL NEG_RC=0 + §4.9 三假(fake_empty->c / fake_print->d / fake_core->d)全 FAIL; 断言闸门 k_rationale=k_check=16>=8 PASS; jsonl test==disk check.py sha 62d13e33c58a sync
- r273 DEBT 修复说明: 本 case 11/06 首版(X*Y 14 conds) 与 11/09 重建(cell,area 16 conds) 半成品状态遗留 — check.py 已升 16 conds 但 reference_submit.zip 仍含旧 update_area.py、jsonl test/rationale/attachments 仍是旧 X*Y 14 conds、negative_selftest 仍按 update_area.py 打包且直接传 bytes 给 check()(类型不符)、shard A jsonl 存在重复行(line86 旧版 + line178 新版)。r273 全部修复: 重生 reference_submit.zip(update_tcl_area.py)、改 negative_selftest(写 temp 文件传路径 + 打包 update_tcl_area.py)、jsonl test/rationale/attachments 同步 16 conds、去重(保留 line178 Nov9 版 删 line86 旧版)、删 stale 资产(sizes_A.csv/template_A.tcl/update_area.py)、ledger 86t8o mark case+case_id。
