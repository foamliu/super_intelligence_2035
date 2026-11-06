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

## case 合成 (TclAreaUpdate-001, eda_other, A档, L2-static, 14 conds)
- 资产 A: sizes_A.csv(16 cells 子集, 真 X/Y) + template_A.tcl(16 PDCAP-style 块, OLD area 待更新)
- 泛化 deliverable: update_area.py (通用, 双格式, look-ahead 1-4)
- hidden B: 40nm-style 9 cells(FILL/DECAP/CORNER/TIE/ICG) 不同 X/Y + 2 个不在 CSV(welltie/filler_keep 保留) + CORNER name 在 -attrs 后第2行(测续行 look-ahead) + DECAP 带 pad_cell/bond_pads(测非area属性保留)
- hidden B_direct: cell,area 格式 3 cells(测双格式)
- check.py 14 conds(a-n): 含 zip/运行/X*Y/全匹配/非area保留/结构/CSV外不变/look-ahead/反硬编/双格式/输出存在/float合法/3-seed行序无关
- 自验: ref PASS 14/14 + 3 negs(naive_noop/hardcode42/nowrite)全 FAIL NEG_RC=0; 断言闸门 k=14 PASS; jsonl test==disk check.py sha f20713a10ecb sync
