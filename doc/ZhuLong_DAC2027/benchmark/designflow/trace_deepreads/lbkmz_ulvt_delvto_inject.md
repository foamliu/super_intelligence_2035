# Deepread: lbkmz — joeyl@hfeg0plg74 — SPICE ULVT delvto 注入工具

## trace 概况
- session: `1795053503763_lbkmz.messages.json` (joeyl@hfeg0plg74, mc=246)
- 159 msgs (94 user / 65 assistant), 13 user_input turns
- 关键词: netlist:1103, schematic:100, hspice:93, opamp:24 (D-pure schematic_netlist)
- 工作流: 用 `/home/joeyl/ulvt_delvto/reduce_vth.py` 给多个 SPICE 网表 (Bias/CML_C2C/Solo_Divider/WCKTop/Divider_and_C2C) 的 ULVT 器件 (pulvt_ckt/nulvt_ckt 模型) 注入 `_delvto=<值>` 改变 vth
- 工具: read_files, editor, run_approved_command (python-runner), list_allowed_files, get_agent_policy_status

## 用户轮 A-eligible 判定
- **U#0** "请帮忙用这个：/home/joeyl/ulvt_delvto/ 给这里的netlist：.../Bias/.../netlist 加vth=-0.2v" — 纯目标 ✓★ **选定 (A-faithful)**
- U#21/U#30 "我更新了netlist，请再替换一次" — 重复操作 (纯目标, 同任务)
- U#42/U#64/U#77 处理 CML_C2C/Solo_Divider/WCKTop — 重复操作 (纯目标)
- U#89 "发现个非常关键的问题，对pmos，Vth应该+0.2!麻烦重新替换" — **给出修复方案** 🚫 NOT A-eligible (但是关键领域知识: PMOS/NMOS 符号差异, 后入 config delvto_by_model)
- U#112/U#124/U#132/U#140/U#151 改 delvto 值/换 netlist — 重复操作

## 选定 U#0 理由
- 纯目标(A-eligible), 无根因/fix 方向
- 资产可恢复: reduce_vth.py(313行) + config.cfg + AI_USAGE.md 均可 ssh cat 恢复 (本 deepread 已恢复并用作参考解)
- gold = assistant U#0 产物: 对 Bias netlist 84行, 4 个 ULVT 器件 (XM10/XM9 pulvt_ckt, XNM18/XNM0 nulvt_ckt) 末尾追加 `_delvto=-0.2`, 非 ULVT (nlvt_ckt/plvt_ckt/res_rk) 与 .SUBCKT 定义未改, VERIFY PASS

## 真实工具 reduce_vth.py 算法 (用作参考解 inject_delvto.py)
1. parse cfg (netlist=, delvto=, models=, in_place=, require_x_prefix=)
2. 扫描网表行, 用 '+' 续行聚合成完整语句
3. 跳过空行/`*`/`//` 注释行
4. 对 X 开头实例语句 (require_x_prefix=yes), 在语句代码部分找 model token (大小写不敏感, 精确 token 匹配 model_set)
5. 命中则取 delvto (delvto_by_model 覆盖全局, A-faithful U#0 无 by_model, 用全局 -0.2)
6. apply_delvto: 若已有 `_delvto=` 则替换其值(幂等); 否则追加到语句最后一条物理行末尾(行尾有 `$`/`//` 注释时插到注释之前)
7. 输出 `<原名>_delvto<值>.sp` (in_place=no)

## 关键领域细节 (判分 "牙" 来源)
- token 精确匹配: `pulvt_ckt` 命中, `delvto_user` 不误改 (前非字母数字下划线断言)
- '+' 续行: `_delvto` 在最后一条物理行, 不在首行
- 行尾注释: `$`/`//` 注释保留, `_delvto` 插到注释之前
- 幂等: 已有 `_delvto=` 替换值, 不重复追加
- .SUBCKT 定义行: require_x_prefix + 跳过定义 (只改 X 实例)
- U#89 PMOS 符号: 用户修正 PMOS 应 +0.2 (NMOS -0.2), 后入 config delvto_by_model (A-faithful U#0 gold 不含此, 用全局 -0.2 uniform)

## Case 合成 (r1021 交付)
- task_id: EDA-Eval-DesignFlow-UlvtDelvtoInjectProduce-001
- domain: schematic_netlist
- track: A-faithful (U#0 逐字)
- 难度: L1-static-text-parse + subprocess (离线 Python 解析 SPICE 文本, check 在 B 上真跑候选)
- 交付: inject_delvto.py (config-driven, 同 reduce_vth.py 接口)
- A (可见): netlist_A.sp (紧凑 SPICE, 保留真实结构+命名 pulvt_ckt/nulvt_ckt/XM10/XM9/XNM18/XNM0) + config_A.cfg (delvto=-0.2) + task_brief.md
- 隐藏 B: netlist_B.sp (完全不相交命名 pmos_ulvt/nmos_ulvt/XPA/XPB/XNA/XNC/sa/sb, delvto=-0.15) + config_B.cfg
- gold: inject_delvto_ref.py 逐字改编自真实 reduce_vth.py
- check.py 14 断言 a-n: a zip含inject_delvto.py b py_compile c 反空壳≥400B d B运行exit0 e B输出文件存在非空 f 4 ULVT各含_delvto=-0.15(独立_gt_scan) g 2非ULVT不含_delvto h .SUBCKT/.ENDS定义不含_delvto i XNA _delvto在续行不在首行 j XPB/XNC _delvto在注释之前且注释保留 k delvto值恰-0.15 l 反硬编码零A-only token m 反硬编码含B-only token n 3-seed md5一致
- 自验: ref 14/14 PASS on B + ref on A 产 A gold(4 ULVT改/3非ULVT未改/定义未改)一致 + 3 neg(empty/print_only/core_deleted)全 FAIL NEG_RC=0 + §4.9 a/b/c 三假全 FAIL, k_check=k_rat=14>=8 GATE PASS ✓

## ⚠️ r1021 ABORT (near-dup, 1-task-1-case anti-redundancy)
- 本 deepread 合成的 case (EDA-Eval-DesignFlow-UlvtDelvtoInjectProduce-001) **已 abort 不落库**。
- 原因: lbkmz 与已有 NetlistUlvtDelvtoInject-001 (session 3ydq7, joeyl@hfeg0plg74 mc246) 是 **同一用户/同一任务/同一 U#0 逐字** 的 near-dup (joeyl 集群 lbkmz/3ydq7/fxlzf 三 session 关键词完全一致 netlist:1103/schematic:100/hspice:93/opamp:24, 均重复 ULVT delvto 注入任务)。
- D 已有 2 个 joeyl ULVT delvto case: UlvtDelvtoReducer-001 (qsn6y mc23 早期) + NetlistUlvtDelvtoInject-001 (3ydq7 mc246)。本例第 3 个 = 题库冗余。
- 处置 (守 r1014 precedent): 删 cases/D json + assets/ + reference/ 全部文件, D.jsonl rebuild 回 543, ledger mark --force case→parked (note 记 near-dup 原因)。
- 教训: 选料时 joeyl 集群 (mc246, netlist:1103) 的多 session 是同一重复任务, 需先查同用户已有 case (grep joeyl ledger) 再决定, 勿仅看 session 唯一就认为 fresh。
- deepread + 合成的 inject_delvto_ref.py (逐字改编自真实 reduce_vth.py) + check.py 14 断言设计已验证可用 (ref 14/14 PASS + 3 neg FAIL), 可复用到下一个真正 fresh 的 SPICE delvto/param-inject trace (需重抽 gold + 不相交命名)。
