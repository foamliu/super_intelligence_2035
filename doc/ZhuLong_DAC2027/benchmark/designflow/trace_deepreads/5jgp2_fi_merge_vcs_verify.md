# trace 深读：5jgp2（lorikx @ hfeg0pkn004，RTL fault-injection 合并 + VCS 验证）

- sid: 1793929852342_5jgp2 · user: lorikx · host: hfeg0pkn004 · 148 msgs/2 user · 2.01MB · mtime 2026-11-06
- 来源：daily eda_trace_20261109.log fresh(≥11-06) 扫描，pkn004 lorikx kw=8(synthesis)，un-ledgered → ssh 验文件 2.01MB(<2MB 边界，可整轮交付) → CLEAN
- 选用：A-faithful ✓（USER#1 / USER#2 均「提需求 / 表达目标」，未给根因或修复方案）

## U#0 逐字原文（task 说明）
```
@rtl/ppc_inject_fault.v 是同事针对fault inject function优化后的代码，在line704-958，请阅读后帮我融合到 @rtl/sp_sram.v 代码中
```
附件：`rtl/ppc_inject_fault.v`、`rtl/sp_sram.v`（CXMT_SPSRAM_1106_v23 项目）

## U#4（msg#88）逐字原文
```
请你通过vcs验证代码是否有问题，更新testbench/Makefile
```

## 工具链（assistant，82 tool calls）
1. read_files(ppc_inject_fault.v) + list_allowed_files + search_codebase(fault/FAULT_INJ/inject)
2. read_files(sp_sram.v 分段读取 1300-1900/2383-2400/3300-3400 等) → 定位旧版 FI 块(1376-1428)+旧 apply_fi(2383-2399)+读路径调用点(SD@2594, CD@3329-3330)
3. read_files(sim/Makefile) → 确认 VCS 用 `-sverilog`，`faultinj*` target 用 `+defect_bit_left`
4. **editor 5 处融合编辑** sp_sram.v v15.1→v15.2：
   - 替换 1376-1428 旧 FI 块 → 新版完整 FI 块(声明+parser 变量+5 任务+initial+apply_fi)
   - 删除 2383-2399 旧 apply_fi → 留迁移注释
   - 文件头 changelog 增 v15.2
5. editor verify_fi_merge.py(静态结构检查+VCS 编译验证) → run_approved_command(python-runner) → **STATIC CHECKS PASS + VCS 编译 0 error**
6. editor sim/tb_fi_new.v(新接口专项 TB) + run_fi_new_test.py → run → **ALL PASS 12 项检查**
7. USER#4 → read_files(sim/tb_sp_sram.v Test 18) + search_codebase
8. **editor 4 处更新 tb_sp_sram.v v9.7→v9.8**：Test 18 刺激接口自动检测 + 新增 18e-18h 运行时任务测试 + changelog
9. **editor 5 处更新 sim/Makefile**：新变量 `DEFECTS ?=` + 新 target `faultinj_defects`/`faultinj_cd_defects` + usage 文档
10. run_fi_new_test.py 6 项回归 → [2] `*:6:s0` 整列 SAF0 致 23 FAIL（缺陷生效证明，非 DUT bug）
11. **根因定位**：legacy `+defect_bit_left` 只注入 addr0/1，主回归无测试对 addr0/1 做数据值检查 → 全绿；新 `+defects=` 整列注入改变 Test 2/3/14/15/16/21 读值 → FAIL
12. **修正**：默认 `DEFECTS=c0:c3:x,1:0:x`（与 legacy 掩码等价，corner 语法验证）→ 主回归保绿
13. 重跑 6 项回归 → **6/6 PASS**（[1]faultinj/[2]faultinj_defects/[3]faultinj_cd/[4]faultinj_cd_defects/[5]default SD/[6]cd）
14. make faultinj_tv(FI=1 TV=1 CR=1) → **PASS 0 error**
15. list_allowed_files 收尾确认产物

## 根因 / 关键技术决策（assistant M#30/M#87/M#147）
1. **旧 apply_fi 语义缺陷**：`if(fi_enable) raw^xor_mask; else (raw&and_mask)|or_mask` —— fi_enable=0 仍走 AND/OR 路径(非直通)；FAULT_INJ 构建下 and/or 掩码未初始化 → 读数据 X 化
2. **新 apply_fi 语义**：`((raw & and_mask) | or_mask) ^ xor_mask` —— SAF 先(AND→OR)、XOR 叠加其后；fi_enable=0 数据直通；掩码无条件全初始化(xor=0/and=all-1/or=all-0)
3. **5 个新任务**：inject_one(a,b,t)/inject_range(a,b,t)(a<0 整列/b<0 整行/both<0 全阵列)/clear_fault(a)/clear_all_faults/parse_and_inject —— TB 运行时层次化调用(dut.inject_one，从源文件的 dut.u_sram. 前缀适配)
4. **新 plusarg** `+defects="addr:bit:type,..."`：type x(XOR 默认)/s0(SAF0)/s1(SAF1)，`*` 通配整行/整列，`cN` corner 可移植索引(c0..c5 bits/c0..c2 addrs)
5. **legacy 兼容**：保留 `+defect_bit*` plusarg 作 fallback(Makefile `faultinj*` target 仍用 `+defect_bit_left`)；`+defects=` 存在时优先
6. **SystemVerilog 依赖**：parser 用 `string` 类型 + `len()/substr()/atoi()`，必须 `-sverilog` 编译
7. **parser 变量声明顺序**：置于任务之前(VCS 单遍 parser 要求)，与 ppc_inject_fault.v 原始顺序(变量在前/任务在后)一致

## 金标准（trace 末尾用户实际接受的结果）
- msg#56 静态检查 PASS + VCS 编译 0 error 0 warning
- msg#79 default SD(无 FI) PASS 0 error / CD(无 FI) PASS 0 error(Test 18 正确 SKIP)
- msg#139 6/6 回归 PASS：[1]make faultinj(legacy) PASS / [2]make faultinj_defects(新接口) PASS / [3]make faultinj_cd PASS / [4]make faultinj_cd_defects PASS / [5]default SD PASS / [6]cd PASS
- msg#143 make faultinj_tv PASS 0 error；Test 18 详细：18a Q=ba(缺陷未修复)→18b Q=aa(CR 冗余修复)→18c Q=8a(错误列不修复)→18e-18h 运行时任务全 PASS
- 最终产物：sp_sram.v v15.2 / tb_sp_sram.v v9.8 / Makefile(新 DEFECTS 变量+2 target) / tb_fi_new.v / 验证脚本

## 合成方向（A-faithful, digital, L2-vcs-verify）
- **交付**：`outputs/submit.zip` 含 `rtl/sp_sram.v`(融合后)、`sim/tb_sp_sram.v`(更新后)、`sim/Makefile`(更新后)
- **A 资产**：`ppc_inject_fault.v`(同事优化版，704-958 行完整)、`sp_sram_v15_1.v`(融合前 v15.1 旧版)、`sim/Makefile_v0`(原始 Makefile)、`sim/tb_sp_sram_v9_7.v`(原始 TB) + prompt + task_brief
- **隐藏 B**：用不同 DEPTH/DATA_WIDTH/CM 配置的 sp_sram 模板(反硬编码) + 不同 defects 列表
- **check.py 真跑**：subprocess 调 vcs/iverilog 编译 + 跑 tb，断言输出结构(静态符号 + 编译 0 error + Test 18 PASS 标记)
- **断言**：≥8 条，覆盖：① sp_sram.v 含 5 新任务符号 ② apply_fi 新语义 `((raw & and_mask) | or_mask) ^ xor_mask` ③ fi_enable=0 直通(旧版 else 分支已删) ④ 掩码无条件初始化 ⑤ `+defects=` plusarg 解析 ⑥ legacy `+defect_bit_left` 保留 ⑦ 旧 apply_fi 已删 ⑧ VCS 编译 0 error ⑨ Test 18 PASS 标记 ⑩ 18e-18h 运行时任务测试存在 ⑪ Makefile 含 faultinj_defects target ⑫ DEFECTS 变量 ⑬ tb v9.8 changelog ⑭ sp_sram v15.2 changelog ⑮ iverilog 静态结构检查 PASS ⑯ SD/CD 双模式回归
