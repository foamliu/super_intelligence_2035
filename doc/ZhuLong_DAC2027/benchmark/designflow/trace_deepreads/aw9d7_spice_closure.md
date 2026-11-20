# Trace deepread — aw9d7 (dsgao @ hfhds201, mc273) — shard D #355

**session**: `/home/dsgao/.cline/data/sessions/1793260818025_aw9d7/1793260818025_aw9d7.messages.json` (1.31MB / 302 msgs / 5 user turns)
**scan kw**: netlist:740 schematic:684 hspice:45 calibre:7 spectre:5 synthesis:4
**shard A parked note**: "spice_sim TM testbench for DRAM array (finesim proxd flat transistor netlist 47K, TM config bits tb-driven not structural); same drcpa/dsgao" — unfit shard-A digital, D-domain primary.

## 用户轮（全 clean produce，无根因/修复给出）
- **U#0**: `/proj/drcpa/V0/workdir/dsgao/simulation/drcpa_work_Ras_Tscodecomp_schematic_ALPS/netlist  xie yi ge tb qu yanzheng zhe ge dian lu yong finesim fangzhen` — 写 TB 用 finesim 验证 Ras_Tscodecomp 电路
- **U#152**: `在当前网表路径来写tb,` — 把 tb 写到当前网表目录（U#0 的位置细化）
- **U#166**: `/proj/drcpa/V0/workdir/dsgao/R_2stepOcCtrl.netlist 这个电路的输入ts<2:0>结合/proj/drcpa/V0/workdir/dsgao/Ras_Tscodecomp.netlist LT HT NT 来优化这个逻辑` — 优化 R_2stepOcCtrl 逻辑（复用 Ras_Tscodecomp 的 HT/LT/NT）
- **U#188** ★: `@/proj/.../drcpa_work_RasSim_Banklogic_Xdec_Array_schematic_ALPS/netlist.presim  分析一下这电路，然后搭建tb去验证cm1_ro_TsLT,cm1_ro_TsHT,cm1_ro_SaNPHT,cm1_ro_SaNPHtLtEn,cm1_ro_NcAdjEnN,cm1_ro_NcAdjHT 这些TM 功能，可以多写几个tb 分别去验证，产生的文件要求和网表同路径` — 分析 netlist.presim + 搭多个 TB 验证 6 个 TM 信号，文件与网表同路径
- **U#252**: `@/proj/.../TM_full.sp  参考这个tb 去写验证这些TM的tb` — 参考 TM_full.sp 的模型库/角/电压约定重写 TM 验证 TB

## assistant 工具链（U#188 主线）
read_files netlist.presim（整套子电路库，顶层 RasSim_RasBnkLogic）→ 定位 6 个 TM 信号的生成块：
- `cm1_ro_TsLT/TsHT` + `ts<2:0>` → **Ras_Tscodecomp** → `HT/LT/NT`（温度区间 1-of-3 分类）
- `HT` + `cm1_ro_SaNP<3:0>` → **Ras_SaNPCtrl** → `cm1_ro_SaNPHT/SaNPHtLtEn`
- `cm1_ro_NcAdjHT/NcAdjEnN` → RasSim_RasBnkLogic 顶层集成处生成
→ **关键创新**：写**依赖闭包抽取脚本**，从 netlist.presim 把 Ras_Tscodecomp + Ras_SaNPCtrl 及其用到的全部 std cell / MOS 叶子子电路（传递依赖）抽成独立网表，方便做单块 TB → 写 3 个聚焦 TB（tb_Ras_Tscodecomp / tb_Ras_SaNPCtrl / 级联 TB3）→ run_approved_command finesim 跑通（G5_CIP ss 模型库, shrink=0.256）→ fsdb_reader.py 读 FSDB 验证逻辑（512/1024/16 组合 0 mismatch）→ 全 PASS。

## A-faithful 判定
- U#188 = clean produce（提目标 + 给方法「搭多个 TB」+ 给输出位置「与网表同路径」，未给根因/修复）✓ A-档资格
- **不可行**：真实 netlist.presim = 47K 晶体管 proxd flat 网表（体积过大不宜作 A 附件）+ 真实交付 TB 文件在 /proj/drcpa/V0/workdir/dsgao/（dsgao 私有，.75 as e0031982 不可读，已验证）+ live finesim 验证（L2，受 license/sandbox 限制不可移植）
- → **B 档 synthesized L1**：离线复刻 assistant 的**依赖闭包抽取** facet（trace-faithful 而非 file-faithful）

## 合成 case：EDA-Eval-DesignFlow-SpiceClosureExtract-001
- facet：SPICE 子电路依赖闭包抽取器 `gen_spice_closure.py --lib <netlist.sp> --roots <roots.json> --outdir <dir>` → `closure.sp`（根+传递依赖的 .SUBCKT 块，拓扑序）+ `manifest.json`（8 顶层键：roots/n_roots/n_subckts_in_closure/n_leaf_models/closure[]/topo_order/missing/leaf_models）
- 解析：`.SUBCKT <name> <ports...>` 起头 / `.ENDS` 结尾（大小写不敏感）；`X<inst> <nets...> <master>`（末 token=master）；`M<inst> <d> <g> <s> <b> <model> ...`（第 6 token=model）；`*`/`$` 注释跳过；闭包=从 roots 沿 X master 传递可达；拓扑序=库内 deps 排在前
- A=lib_A.sp（Ras TM verify mimic，2 roots Ras_Tscodecomp/Ras_SaNPCtrl，9 子电路 nand_x1/nor_x1/inv_x2/nand_x2/inv_x1+ntn_lv/ptn_lv，2 leaf models ntn/ptn）
- hidden B=lib_B.sp（模拟 CmpCore+BiasGen，2 roots，7 子电路 diff_pair/fold_load/ref_beta+ntn_m/ptn_m，2 leaf ntn_mos/ptn_mos）
- hidden B2=lib_B2.sp（单根 InvChain，4 子电路 inv_iv+nmos_iv/pmos_iv，2 leaf nmos_iv_mod/pmos_iv_mod）— 测单根浅依赖路径
- 反硬编码轴：root 名(Ras_Tscodecomp/CmpCore/InvChain)/子电路名/leaf model 名(ntn/ntn_mos/nmos_iv_mod)/counts(9/7/4 子电路, 2/2/1 roots)/ports 全不同
- check 16 条件 a-p：解 zip 防泄漏+py_compile / B-run exit0+2文件 / 8 顶层键 / B roots==[CmpCore,BiasGen] / B n_roots==2 / B n_subckts==7 / B n_leaf==2 / B leaf_models==[ntn_mos,ptn_mos] / B missing==[] / B closure 含两 root type==root / B topo 合法(库内 deps 在前)+集合==closure / B closure.sp 恰 7 .SUBCKT 且序与 topo 一致 / B 每项 ports==lib_B 头 / 跨输入 A(9 子电路)+B2(单根 4 子电路) / 反硬编码无 A 字面量+3x sha256 确定性
- 自验：ref PASS 16/16 a-p + 5 negatives 全 FAIL（distinct first_fail: c/e/k/m/h）+ §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL + 断言闸门 k_rationale=k_check=16 ✓
- 台账：mark aw9d7→case；schematic_netlist 102→103；D.jsonl 186→187

## 教训
1. **同 shard 同 trace 不同意图复用（重要发现）**：aw9d7 已于 2026-11-05 被 D 做成 RasTbFinesimGen-001（A-faithful，U#0 原话→finesim TB 生成器 facet，台账 entry session 名 `1793260818025_aw9d7` **无 .messages.json 后缀**）；本 case 取同 trace 的 U#188（依赖闭包抽取 facet）。`trace_ledger.py claim --session 1793260818025_aw9d7.messages.json`(**带后缀**) 因台账去重的**后缀敏感 bug**(MEMORY line 13 已记录)未检出已有 unsuffixed entry → claim 成功。这是 u78sz 跨 shard 同 trace 不同意图模式的**同 shard 类比**（同 trace 覆盖不同 user turn + 不同 skill）。建议运维修台账：claim/mark 时对 session 名统一剥 `.messages.json` 后缀再做去重，避免同类漏检
2. **SPICE 依赖闭包抽取是好 L1 范式**：解析 .SUBCKT 库 + X/M 行 + 传递闭包 + 拓扑序，16 条件天然丰富（结构/计数/拓扑序/端口/missing/跨输入/确定性）
3. **B2 单根浅依赖是强反硬编码轴**：硬编码 2-root 或固定深度的 stub 在 B2 上 n_roots/n_subckts 不符
4. **5 negatives 5 distinct first_fail (c/e/k/m/h)** 是强负样本设计——每个 negative 精确打中一个不同 check 条件
5. **legacy jsonl 有 id/case_id 而非 task_id**：dedup 须兼容三种主键
