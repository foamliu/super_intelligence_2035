# Deepread: sid_1793344639876_ig5hm (jiangbaol@hfeg0pkn003, mc=3, spice_sim)

**Trace**: `/home/jiangbaol/.cline/data/sessions/1793344639876_ig5hm/1793344639876_ig5hm.messages.json` (150KB, 57 msgs, 3 user tasks)

## 三轮用户任务
1. **msg#0-10** (context-continuation): 给 decqa_doubletail SPICE 加 CM/DM 测量 → 生成 `_cm.sp`（前一会话延续，非本轮 A-档选料轮）
2. **msg#11-32**: 给 strongarm `_test_cm.sp` 加差模电流/电压 → 生成 `_test_cmdm.sp`（USER#1 verbatim「该.sp已添加了共模电流与共模电压，在此基础上添加差模电流及差模电压」→ USER「compact」接受）
3. **msg#33-56** ← **本轮 A-档选料轮**: USER#2 verbatim:
   > /proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa_test_cmdm.sp 帮我在这个.sp中比较器out_stg1两端添加电容，value设置为参数，在.paramter中定义该值，生成的结果以新.sp形式呈现

## 选料判定
- ✅ A-档「提出需求」轮：给 .sp 路径 + 目标（比较器 out_stg1 两端加电容）+ 约束（value 参数化、.param 定义、新 .sp 输出）
- ✅ 用户未指出根因、未给修复方案
- ✅ 无附件上传（引用磁盘文件）；金标准 = trace 末尾 assistant 实际产物 `_test_capout1.sp`（已验证）

## assistant 工具链（msg#33-56）
- read_files 读 `_test_cmdm.sp` 1-120 / 120-250 / 164-187 / 250-305 / 305-330 → 理解结构
- search_codebase 查实例化（超时）
- editor 创建 `add_cap.sh`（shell 脚本用 grep/sed/head/tail 改文件）
- run_approved_command shell-runner 执行

## 金标准 `_test_capout1.sp`（由 add_cap.sh 生成，msg#53/55 验证）
- 源文件 `_test_cmdm.sp`：312 行，HSPICE deck（strongarm 比较器 testbench）
- 变换：① 在 `.param cthin=...` 行（line 63）后插入 `.param Cout_stg1 = 1f` ② 在 `.end`（line 312）前插入：
  ```
  * ---- Output caps on out_stg1 (differential load) ----
  * value parameterized by Cout_stg1 (defined in .param)
  Coutp_stg1  XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outp_stg1  vss!  'Cout_stg1'
  Coutn_stg1  XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outn_stg1  vss!  'Cout_stg1'
  ```
- 输出 318 行，.end 仍在末尾
- 关键层次路径：`XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outp_stg1` / `outn_stg1`（差分对，在 .probe slicer1st_out / .meas slicer1st_dly_f0/f1 中引用）
- 地节点：`vss!`

## 资产 fetch
- 真实文件 `/rundata/dscqa/V0_LP6/simdir/finesim/.../strongarm/004_onlySlicer_delay_dejoa_test_cmdm.sp` 权限拒（.75 e0031982 无法读 jiangbaol /rundata）
- → 从 trace read_files tool_result 逐字提取（msg#35/43/45/47 覆盖 line 1-312 全文，无缺行），忠实复现 cmdm.sp 作 asset A
- hidden B = 不同层次名（`XI_sa_cmp.xi_dtail.s_outp`/`s_outn`）+ 不同地节点（`gnd!`）+ 不同 cap 值（2.5f）+ 不同 .param 位置 → 强制泛化防硬编码

## case 设计
- **ID**: `EDA-Eval-DesignFlow-CmpStg1CapAdd-001`（spice_sim, A-faithful, L2）
- **交付**: `add_outstg1_cap.py <in.sp> <out.sp>` 解析 HSPICE deck → 找比较器 stage-1 差分对（.probe 含 stg1/1st 的 `v(a)-v(b)`）→ 加 `.param` + 两对地电容 → 输出新 .sp
- **check.py k=13**：zip+py_compile/B 生成非空/.param 定义 cap 参数/两个电容元素/电容引用参数名/对地或差分连接/stg1 节点匹配/原内容保留/.end 在末尾且电容在其前/.param 在 param 区/跨输入护栏 A 1f≠B 2.5f/电容值参数化非硬编码数字/输出含 .tran
