# 深读 phh7f（e0046913@hfeg0pkn003, mc46, rtl:571）

- **trace**: `1793584339937_phh7f.messages.json`（295KB, 39 msgs, 23 user/16 assistant, 5 真实 user 轮）
- **用户**: e0046913 @ hfeg0pkn003（.75 本机，/home 共享）
- **工程**: openE902（玄铁 E902，平头哥开源 RISC-V MCU 内核）— 真实路径 `/proj/lacaa/TV1_digital/simdir/yutingq/opene902-main`（→ `/rundata/lacaa/...` 映射，e0031982 无权限）
- **工具**: cline + agent-policy-engine（list_allowed_files / read_files / search_codebase / run_approved_command[被policy禁]）；全程静态分析（run_approved_command 报 "Dynamic profile shell-runner requires filePath"，未实跑）

## 用户轮（逐字）
- USER#1 (idx0): `/home/e0046913/opene902-main 解读此目录下的README和.md和LICENSE信息，并说明.md是什么文件格式` — 解释工程
- USER#11 (idx15): `set pattern = "\/setup"\`echo '$'\`` ... `解释代码含义` — 解释 setup.csh csh 语法
- USER#13 (idx19): `在source setup.csh时出现报错：bash: setenv: command not found...` — 报错诊断（clean 需求，未给修复）
- USER#15 (idx23): `/proj/lacaa/.../gen_rtl 解读该目录下代码层次及对应功能，并告诉我如何使用verdi打开、verdi能帮我实现什么作用` — **A-faithful 候选**（clean 需求：解读层次 + verdi 用法 + verdi 作用）
- USER#23 (idx37): `帮我用verdi打开整个工程（包含所有rtl）` — 无 gold（trace 在 idx38 截断，assistant 空响应）

## A-faithful 选轮判定
- 选 **USER#15**：clean "提出需求" 轮（解读 + 指引），用户未给根因/修复（符合 rule2）
- gold = idx36 assistant 完整答复（三部分：gen_rtl 层次表 + verdi 打开命令 + verdi 能力清单）

## gold 要点（idx36，真实事实）
### gen_rtl 层次（顶层例化链）
```
tb → x_soc(soc.v) → x_cpu_sub_system_ahb(cpu_sub_system_ahb.v) → x_e902=module openE902(cpu/rtl/openE902.v, 芯片最顶层)
  → cr_core_top(cr_core_top.v, 内核顶层)
    → cr_core(cr_core.v, 处理器核心)
    → cr_clkrst_top(时钟/复位) → cr_bmu_top(总线管理) → cr_iahbl_top/cr_sahbl_top(biu, AHB-Lite 口)
    → cr_tcipif_top(定时器/CLIC/外设接口) → cr_sys_io(系统IO/打拍)
```
tb.v 定义 `` `define CPU_TOP tb.x_soc.x_cpu_sub_system_ahb.x_e902 ``

### 子模块职责（17 个子目录）
| 目录 | 模块 | 职责 |
|---|---|---|
| cpu | openE902.v cr_core.v cr_core_top.v cr_sys_io.v cpu_cfig.h | 处理器顶层/核心；cpu_cfig.h=配置宏开关(GPR_16/CLIC/USER_MODE/PMP_REGION_8/IBUS_32/BIU_32/HAD_JTAG_2) |
| biu | cr_ahbl_if cr_ahbl_req_arb cr_iahbl_top cr_sahbl_top | Bus Interface Unit：AHB-Lite 读写接口/请求仲裁 |
| bmu | cr_bmu_top cr_bmu_ibus_if cr_bmu_dbus_if | Bus Management Unit：ibus/dbus 仲裁 |
| ifu | cr_ifu_top cr_ifu_ifctrl cr_ifu_ifdp cr_ifu_ibuf cr_ifu_ibusif | 取指单元：预取/PC/ibuf/总线接口 |
| iu | cr_iu_top decd alu branch pcgen mad oper/oper_gpr wb retire rbus vector | 执行单元流水线：译码/ALU/分支/PC/乘加/GPR/写回/提交 |
| lsu | cr_lsu_top ctrl dp unalign | 访存单元：非对齐处理 |
| cp0 | cr_cp0_top status oreg iui lpmd srst | CSR 控制/状态寄存器/特权/复位/低功耗 |
| pmp | cr_pmp_top regs enc comp_hit acc_arb | 物理内存保护 |
| clic | cr_clic_top arb kernel busif ctrl kid sel | 本地中断控制器 |
| clint | cr_clint_top regs busif | mtime/mtimecmp 定时器 + mip.msip 软中断 |
| clk | cr_clk_top cr_clkrst_top gated_clk_cell | 时钟/门控时钟 |
| rst | cr_rst_top | 复位逻辑 |
| had | cr_had_top jtag2 ctrl bkpt regs pin sync trace ddc | 硬件调试：JTAG/断点/trace |
| pwrm | cr_pwrm_top_dummy | 功耗管理（dummy 空实现） |
| coretim | cr_coretim_top_dummy | 内核定时器（dummy 空实现） |
| tcipif | cr_tcipif_top behavior_bus dummy_bus | Timer/CLIC/外设接口桥 |
| filelists | E902_asic_rtl.fl | ASIC 编译清单 |

### verdi 打开（gold 命令）
```bash
cd smart_run
make runcase CASE=<case> SIM=vcs DUMP=on          # VCS 仿真 + dump fsdb（tb.v 230-245 行 $fsdbDumpvars）
cd work
verdi -f ../../logical/filelists/sim.fl -top tb -ssf verilog.fsdb &
# 或只看 RTL: verdi -f ../../gen_rtl/filelists/E902_asic_rtl.fl -top openE902 &
```
- `-f <filelist>`：RTL 清单（建立层次）`-top <module>`：顶层 `-ssf <fsdb>`：波形
- 必须先 `SIM=vcs DUMP=on` 生成 fsdb；iverilog 出 test.vcd（verdi 也支持 -ssf test.vcd）

### verdi 能力（gold 清单）
波形查看/反标 · 层次浏览 · 信号反向溯源(Trace Logic) · 源码-波形联动 · FSM 浏览器 · 信号搜索 · 多波形比较

## 资产可取性
- 真实 gen_rtl 在 /proj/lacaa（e0031982 Permission denied）→ 经 trace tool_results（idx13/25/32 list_allowed_files JSON）重建真实目录树 + 经 gold（idx36）重建真实模块名/层次
- 真实文件内容（E902_asic_rtl.fl/openE902.v/tb.v/Makefile/sim.fl）trace 未存（read_results 空）→ 用真实模块名 faithful 重建

## 合成计划
- **case_id**: EDA-Eval-DesignFlow-RtlHierarchyVerdiGuide-001
- **domain**: digital · **track**: A档 faithful · **层**: L1-static
- **候选**: `gen_rtl_verdi_guide.py`（通用 gen_rtl 风格目录 → 结构化 JSON 报告：design_name/top_module/filelist/rtl_files/submodules{subdir,files,function_hint}/verdi_launch_cmd/verdi_capabilities/sim_dump_method/hierarchy）
- **check**: subprocess 真跑候选于隐藏 B（合成 mini_riscv 树，不同标识符），验 ≥8 字段 + A 反硬编守卫（跑 A 验 design_name=openE902 非 B）+ B' 确定性重跑
- **A 资产**: 重建 openE902 gen_rtl 树（17 真实子目录 + E902_asic_rtl.fl + openE902.v 顶层 + tb.v + Makefile）
- **B 隐藏**: mini_riscv 树（core/decoder/alu/regfile/imem/dmem/cache，top=mini_riscv_core，filelist=mini_asic_rtl.fl，tb_mini.v $fsdbDumpvars）
