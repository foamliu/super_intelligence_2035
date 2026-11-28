# Deepread: 1789549789400_5xagb — cross-scope-jump netlist trace enhancement

> **状态**：DEBT（深读完成，合成待下一轮）。本笔记可直接复用，无需重读 trace（§3）。
> **轮次**：r1680（2026-11-29）

## 0. trace_source（溯源，全产物不脱敏）

| 字段 | 值 |
|:--|:--|
| session_file | `1789549789400_5xagb.messages.json`（dir: `1789549789400_5xagb/`） |
| user | wellesc（Welles Chen, E0017912, PDC/DE/DFMP/Design Team 3, welles.chen@cxmt.com） |
| host | hfeg0plg17（10.129.32.75 fleet；ssh BatchMode OK ~4s） |
| match_count | 180（keywords: netlist:436; waveview:28; analog:9; mosfet:8; hspice:5; transistor:2; lib.defs:2; aether:1） |
| size / msgs | 1,146,319 bytes / 167 msgs（1233 user / 1173 assistant 计数含 tool_result；实际对话 ~83 轮）|
| domain | schematic_netlist（D shard） |
| 代码库 | `/home/wellesc/AutoDebugWithPassRef_V1/AutoDebug_Project/`（DRAM debug agent） |

**real_task_summary**：wellesc 的 DRAM debug agent (`AutoDebugWithPassRef_V1`) 在追踪 fail net `dq0<0>`（pattern PerBnk_ActWrPreActRd_4b4g_B0_tck0.313ns, Fail SS0.88v-40c）时，`NetlistIndex.trace_to_leaf` 在非 leaf driver（`xi_channel` 等）无 `fanin_dag` 时直接 `break` 返回 `partial`，17 轮无进展。用户要求增强：非 leaf driver 无 `fanin_dag` 时，自动经 `get_hierarchy_path` 解析 port→actual_net 映射、跨 scope 跳转继续追踪，而非返回 partial。assistant 实现 `_cross_scope_jump`（3 策略）+ 修改 `trace_to_leaf` 4 个 break 点 + 写 `test_cross_scope_jump.py`。

## 1. 对话流（user intent）

- **U0**：粘贴 debug agent 日志（WS4 Loading debug context，Pattern PerBnk_ActWrPreActRd_4b4g_B0_tck0.313nsRL68WL32TS_12800_RDQSENtENc，Fail SS0.88v-40c / Pass FF1.15v130c，Fail nets ['dq0<0>'], Fail time 836.020n）。
- **U3**：「分析一下是否有问题」→ assistant 深读 `agent.py` / `netlist_indexer.py` / `tools.py` / reports，产出报告：trace_to_leaf 在根层级 Iter 1 就失败（非 leaf driver 无 fanin_dag → break → partial），对比同 pattern 14:12:56 成功运行（65+ 步找到 root cause）。
- **U32**（核心意图）：「增强：当非 leaf driver 无 fanin_dag 时，自动尝试 get_hierarchy_path 解析 port→actual_net 映射，跨 scope 跳转继续追踪，而不是返回 partial。」
- assistant 实现：插入 `_cross_scope_jump` 方法 + 修改 `trace_to_leaf` 4 个 break 点 + 写 `tests/test_cross_scope_jump.py`。

## 2. 数据结构（netlist_indexer.py，faithful reframe 基础）

`NetlistIndex` 类核心字段/方法（来自 read_files + test 固件）：
- `subckts: dict[str, SubcktDef]` — `SubcktDef(name, ports: tuple, params: frozenset)`。
- `scope_instances: dict[scope, dict[inst_name, (cell_type, port_nets_tuple)]]` — 层级实例树，`ROOT` 为根 scope。
- `fanin_dag: dict[cell_type, dict[net, list[driver_dict]]]` — 每种 cell 的 fan-in DAG；非 leaf block（如 `channel_top`）可能无 entry → 死点。
- `get_fanin(net) -> {drivers:[...], ...}` — 有 inferred-drivers fallback（inspect scope_instances）。
- `resolve_net_aliases(net) -> list[str]` — port→actual_net 映射，向上追溯 parent scope。
- `get_hierarchy_path / get_hierarchy` — scope 钻取。
- driver_dict: `{instance, cell_type, driver_pin, is_leaf_cell, upstream_nets:[{net, pin_dir}], ...}`。
- `trace_to_leaf(net_path, max_depth=20) -> dict` — DFS fan-in 到 leaf std_cell，返回 `{status: 'leaf'|'partial', chain:[{level, net, note, jump_target?, alt_drivers?}], ...}`。

**测试固件层级**（test_cross_scope_jump.py，可直接复用为 A/B fixture 模板）：
```
top (ROOT)
  xi_channel  (channel_top: dq0<0>, dqs0, vdd, vss)        ← 非 leaf, fanin_dag 空 → 死点
    xi_chansc0 (chansc: dq0<0>, dqrdl<0>, vdd, vss)
      xi_dqsc0 (dqsc: dq0<0>, dpre0<0>, vdd)
        xi_dqpadm6_0 (dqpadm6: dq0<0>, dbus<0>, vdd)
          xi_dqio (dqio: dq0<0>, dqpu, dqpd, vdd)          ← leaf-ish, 有 fanin_dag
            xi_inv0 (inv: a, y)                            ← std_cell leaf
  xi_dqldmdl  (dqldmdl: dq0<0>, vdd)                       ← load model
```
死点场景：`dq0<0>@ROOT` 的 driver `xi_channel` 是非 leaf 且 `channel_top` 无 `fanin_dag` entry → 旧逻辑 break/partial；增强后应 S1 钻入 `xi_channel.dq0<0>`（其 scope 内 `xi_chansc0` 驱动）继续追踪到 `xi_inv0` leaf。

## 3. Gold 参考：`_cross_scope_jump`（assistant 实际写的代码）

```python
def _cross_scope_jump(self, current_net: str, drivers: List[dict],
                      visited: set, max_attempts: int = 15) -> Optional[str]:
    """非 leaf driver 无 fanin_dag 时，3 策略跨 scope 续追。返回下一 net 或 None。
    S1: Drill INTO non-leaf drivers via inst.driver_pin（+ alias 解析）。
    S2: Resolve current_net aliases at parent scopes（resolve_net_aliases 向上）。
    S3: Follow non-self-loop upstream_nets of drivers（跳过 power/ground）。
    """
    current_aliases = set(a.lower() for a in self.resolve_net_aliases(current_net))
    current_aliases.add(current_net)
    attempts = 0
    # S1: drill into non-leaf drivers via port mapping
    for d in drivers:
        if attempts >= max_attempts: break
        inst = d.get("instance", ""); drv_pin = d.get("driver_pin", "")
        if not inst or not drv_pin: continue
        if d.get("is_leaf_cell", True): continue          # leaf 终端不钻
        candidate = f"{inst}.{drv_pin}".lower()
        if candidate in visited or candidate in current_aliases: continue
        attempts += 1
        try:
            fi = self.get_fanin(candidate)
            if fi.get("drivers"): return candidate
        except Exception: pass
        for alias in self.resolve_net_aliases(candidate)[:5]:
            if attempts >= max_attempts: break
            alias_l = alias.lower()
            if alias_l in visited or alias_l == candidate or alias_l in current_aliases: continue
            attempts += 1
            try:
                fi = self.get_fanin(alias)
                if fi.get("drivers"): return alias_l
            except Exception: pass
    # S2: resolve current_net aliases at parent scopes
    for alias in self.resolve_net_aliases(current_net):
        if attempts >= max_attempts: break
        alias_l = alias.lower()
        if alias_l in visited or alias_l == current_net: continue
        attempts += 1
        try:
            fi = self.get_fanin(alias)
            if fi.get("drivers"): return alias_l
        except Exception: pass
    # S3: follow non-self-loop upstream_nets
    for d in drivers:
        for u in d.get("upstream_nets", []):
            if attempts >= max_attempts: break
            u_net = u.get("net", "")
            if not u_net: continue
            u_net_l = u_net.lower()
            if u_net_l in current_aliases or u_net_l in visited: continue
            if u.get("pin_dir") in ("power", "ground"): continue
            attempts += 1
            try:
                fi = self.get_fanin(u_net_l)
                if fi.get("drivers"): return u_net_l
            except Exception: pass
    return None
```

**4 个 break 点改造**（trace_to_leaf 内，模式一致）：
1. `best_driver is None`（all drivers self-loops / 非 leaf 无 fanin_dag）→ 调 `_cross_scope_jump(current_net, drivers, visited)`；命中且未 visited → `chain.append({...,jump_target,note})` + `current_net=jump_target; continue`，否则原 break。
2. `new_net is None`（non-logic dead-end）→ 同上。
3. `ups` 空（driver_pin self-loop）→ 同上。
4. `parent_scope_net` 已 visited 的 fallback → 同上（`_cross_scope_jump(current_net, [], visited)`）。

chain 节点新增 `jump_target` / `note` 字段记录跨 scope 跳转。

## 4. 合成计划（下一轮直接执行）

- **task_id 建议**：`CrossScopeJumpProduce-001`（D shard, schematic_netlist）。
- **verdict**：`LIVE-NA`（deliverable = Python 模块 `net_trace_enhance.py`，纯文本/数据结构解析判分，无真实 EDA 二进制依赖）→ `judge_layers=[L0,L1]`。
- **reframe**：真实场景 prompt（wellesc DRAM debug agent 追踪 fail net `dq0<0>`，trace_to_leaf 在非 leaf driver `xi_channel` 无 fanin_dag 时返回 partial）。任务：实现 `_cross_scope_jump(current_net, drivers, visited)` 三策略 + 修改 `trace_to_leaf` 4 break 点，交付 `net_trace_enhance.py`（含 `NetlistIndex` 子类或 monkey-patch）+ `report.json`。
- **A visible**：`NetlistIndex` 基类骨架（subckts/scope_instances/fanin_dag/get_fanin/resolve_net_aliases）+ A 固件（上述 channel_top 层级，`dq0<0>` 死点场景）+ 期望 chain 结构。
- **hidden B**：token-不相交的 DRAM DQ 层级（如 `ddr0/dq1` 经 `xi_bufio`→`xi_pgen`→`xi_repeater`→`xi_dqpad`→ leaf，corners/实例名/端口名全不同，A 硬编码器在 B 全错）。
- **check.py（≥8 conds，subprocess 跑 B）**：① 模块可 import 且含 `_cross_scope_jump` 与 `trace_to_leaf` ② B 上 `trace_to_leaf('dq1@ROOT')` 返回 `status=='leaf'`（非 partial）③ chain 末节点是 std_cell leaf ④ chain 含 ≥1 个 `jump_target` 节点（证明跨 scope 跳转发生）⑤ jump 目标 net 不在 visited（无死循环）⑥ S1 钻入路径正确（`inst.driver_pin` 候选）⑦ S3 跳过 power/ground upstream ⑧ 3-seed 确定性（同 B 跑 3 次 chain md5 一致）⑨ 反硬编码：A 硬编码串在 B 上 FAIL。
- **negatives（≥2 + §4.9 trio）**：empty stub / print_only（打印 A 期望 chain）/ core_deleted（`_cross_scope_jump` 直接 `return None`）/ naive_no_jump（不改 break 点，仍 partial）/ hardcode_a。全 FAIL，first-fail distinct。
- **自验**：ref PASS 9/9；neg全 FAIL；SKIP_RUN=1 eval/run_one.sh PASS；test sha 三方同步。
- **现有可复用资产**：本笔记 §2/§3 的 gold 代码 + 测试固件层级；`.75` workdir `gold_extract.txt`（74KB，31 editor calls 完整 gold + test_cross_scope_jump.py 全文）—— **下一轮可重新跑 extraction 拉取，或直接用本笔记**。

## 5. DEBT 说明

- 本轮只做深读，未合成 case。理由：trace 重读 + 1100 行 netlist_indexer 代码理解 + faithful 自包含固件构建 + ≥8 断言 check + hidden-B token-不相交 + 5 neg + §4.9 trio + 自验，工作量大；为不造 weak/rushed case（项目红线「不为凑数造 weak case」），按 §3「本轮只深读 + DEBT」处置。
- 下一轮直接从本笔记合成（§4 计划已具体到断言级），无需重读 trace。
- ledger 已 `mark --status deepread`；covered 不变（待 case 落库后 mark case）。
