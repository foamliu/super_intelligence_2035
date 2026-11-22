# Deepread: lfb0j — dechaoc@hfeg0pkn004 — hier_sig 脚本改造（netlist hierarchy search）

**trace_source**: user=dechaoc, host=hfeg0pkn004 (10.129.2.x), session_file=1794982121198_lfb0j.messages.json, match_count=297 (netlist:297), domain=schematic_netlist
**live path**: `hfeg0pkn004:/home/dechaoc/.cline/data/sessions/1794982121198_lfb0j/1794982121198_lfb0j.messages.json` (351KB, 90 msgs)
**ledger**: claimed r1129 (mc=297, schematic_netlist)
**date**: 2026-11-22 (deepread), trace from 2026-11-18

---

## 1. 用户真实意图

用户要求修改自己的 Python 脚本 `/home/dechaoc/hier_sig`（Verilog 网表层级搜索工具），改 2 处：

1. **简化输入**：从 `./hier_sig <网表> <cell名> <信号名> [--resolve] [-o FILE]` 改为只需 `./hier_sig <网表> <cell名>`，检索匹配网表里的 cell 名，不需要输入信号名。
2. **路径替换**：在每个输出的层级路径中，将 `DDR5TOP` 替换为 `TOP.Chip`。

**任务形态** = 脚本改造（script-modification），真实交付 = 修改后的 hier_sig 脚本。这是 schematic_netlist 域的合法真实意图（网表层级分析工具改造）。

## 2. Agent 工具链（90 msgs）

1. msg#1: `read_files` 读 `/home/dechaoc/hier_sig`（原始脚本）
2. msg#3-5: `read_files` 分段读完整脚本（~570 行原始）
3. msg#7: 规划修改（docstring/traverse/删除 unused functions/format_default/main）
4. msg#7-77: 多轮 `editor` 编辑 + `read_files` 验证 + `run_approved_command` (sed/cat -A 检查 raw encoding) + python-runner 直接修改
   - 编辑过程中遇到 old_text 不匹配（空白/编码问题），agent 用 sed/cat -A 诊断后改用 python-runner 直接操作
5. msg#69-75: `run_approved_command` 跑 `python3 -c "compile(...)"` 语法检查 PASS + chmod +x + 清理临时文件
6. msg#77: 最终 `read_files` 全文验证

**Agent 最终交付** = 修改后的 `/home/dechaoc/hier_sig`（403 行，已验证语法 OK）。

## 3. 原始脚本 vs 修改后脚本（关键 diff）

### 原始脚本（~570 行，asset A 候选）
- Usage: `python hier_sig.py <netlist> <cellname> <signal> [--resolve] [-o FILE]`
- `traverse(modules, top, cellname, signal, resolve=False, max_depth=200)` — DFS 收集匹配 cell 的实例路径，**末尾追加 `.signal`**
- 有 `_resolve_chain`, `_net_fanout`, `_base_name`, `KIND_LABEL`, `format_resolve` 函数（--resolve 模式用）
- `format_default(results)` — 不做 DDR5TOP 替换，输出含 signal 后缀
- `main()` — argparse 含 `netlist`, `cellname`, `signal`, `--resolve`, `-o FILE`

### 修改后脚本（403 行，reference solution）
- Usage: `./hier_sig <netlist> <cellname>`
- `traverse(modules, top, cellname, max_depth=200)` — DFS 收集路径，**不追加 signal**：
  ```python
  def traverse(modules, top, cellname, max_depth=200):
      results = []
      def dfs(mod_name, path_parts, depth):
          if depth > max_depth: return
          mod = modules.get(mod_name)
          if mod is None: return
          for child_mod, inst_name, conns in mod['insts']:
              child_path = path_parts + [inst_name]
              if child_mod == cellname:
                  results.append('.'.join(child_path))
              dfs(child_mod, child_path, depth + 1)
      dfs(top, [top], 0)
      return results
  ```
- 删除了 `_resolve_chain`, `_net_fanout`, `_base_name`, `KIND_LABEL`, `format_resolve`
- `format_default(results)` — **DDR5TOP→TOP.Chip 替换**：
  ```python
  def format_default(results):
      lines = []
      for path in results:
          lines.append(path.replace('DDR5TOP', 'TOP.Chip'))
      return lines
  ```
- `main()` — argparse 只含 `netlist` + `cellname`（无 signal/--resolve/-o）：
  ```python
  def main():
      ap = argparse.ArgumentParser(...)
      ap.add_argument('netlist', help='netlist file, or directory containing "netlist" file')
      ap.add_argument('cellname', help='cell (module) name to search for')
      args = ap.parse_args()
      text, src_file = read_netlist(args.netlist)
      modules, order = parse_netlist(text)
      tops = find_roots(modules)
      ... traverse + format_default + print
  ```

**修改后脚本完整文件在 .75 host**: `hfeg0pkn004:/home/dechaoc/hier_sig`（403 行，13784 bytes，可直接 scp 取回做 reference）

## 4. 合成计划（next round）

### case_id: `EDA-Eval-DesignFlow-HierSigScriptModify-001`
- **domain**: schematic_netlist
- **L 层**: L1（离线 Python 脚本改造，读附件写脚本）
- **mode**: design_flow, entry_point=outputs/submit.zip

### asset A（SUT 可见）
- `hier_sig_original.py` — 原始脚本（~570 行，含 signal/resolve/-o，从 trace msg#2 tool_result 提取，或从 host git history / diff 反向重建）
- `netlist_A.v` — 样本 Verilog 网表（含 DDR5TOP 顶层 + 若干 cell 实例化层级，从 trace 引用的 `/proj/ddgoa/.../V0_DDR5TOP_2026Oct14.160646.local` 裁剪构造，保留结构精华）
- `task_prompt.md` — 自然语言任务（真实场景：修改 hier_sig 脚本，2 处改动）

### hidden B（SUT 不可见，check() 只跑 B）
- `netlist_B.v` — 不同 Verilog 网表（不同顶层模块名如 `DDR4TOP`、不同 cell 名如 `IO_PhyDftMerge`、不同层级深度、不同实例数组/总线命名）
- `hidden_manifest.json` — 声明 B 的 cell 名 + 期望输出路径集（由独立 oracle 实时算）

### hidden A'（anti-hardcode 交叉）
- `netlist_Ap.v` — 又一套不同网表（不同顶层 `DDR6TOP`、不同 cell `IO_ZqCalib`、不同层级），嵌入 check.py 字符串保证 SUT 不可见
- A' 与 B 在顶层名/cell 名/层级结构上全维不相交，击穿按 B 硬编码的 stub

### check.py 断言计划（k≥12）
在独立临时目录解 zip，取 candidate 脚本，在 B 和 A' 上 subprocess 执行：
1. zip 内含修改后的 hier_sig 脚本
2. 脚本 `python3 -c "compile(...)"` 语法 OK
3. `./hier_sig netlist_B.v <cellB>` exit0
4. 输出非空（找到了 cellB 实例）
5. 输出每行一条路径（结构：`a.b.c` 点分）
6. 输出路径中 `DDR4TOP` 已替换为 `TOP.Chip`（B 的替换 token）
7. 输出路径不含 `.signal` 后缀（signal 参数已删除）
8. 脚本拒绝 3 位置入参（`./hier_sig netlist cell signal` → argparse 报错 exit≠0）
9. 脚本无 `--resolve` / `-o` 选项（`./hier_sig --resolve` → exit≠0）
10. 输出路径集 == 独立 oracle 从 netlist_B.v 实时算的期望集（拓扑正确）
11. **A' 交叉**：`./hier_sig netlist_Ap.v <cellAp>` exit0 且输出路径含 `DDR6TOP→TOP.Chip` 替换（击穿 B-hardcode stub）
12. **A' 交叉**：A' 输出路径集 == oracle 从 netlist_Ap.v 算的期望集
13. 随机化：在 B 上对 cell 实例抽子集验证一致性

### negative samples（≥3）
- `neg_empty.py` — 空脚本 → FAIL (zip 内无脚本/语法错)
- `neg_print_only.py` — 只 print 固定期望串 → FAIL (A' 交叉：A' 输出≠B 期望)
- `neg_core_deleted.py` — 删 traverse DFS 只留 argparse 壳 → FAIL (输出空≠期望)
- `neg_hardcode_b.py` — 硬编码 B 的 cell/路径输出 → FAIL (A' 交叉：A' 输出≠B 期望)

### test_rationale
`13 条断言：① zip 含修改后脚本 ② 脚本语法 OK ③ B 上 exit0 ④ B 输出非空 ⑤ 输出点分路径结构 ⑥ B 输出 DDR4TOP→TOP.Chip 替换 ⑦ 输出无 signal 后缀 ⑧ 拒绝 3 位置入参 ⑨ 无 --resolve/-o 选项 ⑩ B 输出==oracle 期望集 ⑪ A' 交叉 DDR6TOP→TOP.Chip 替换 ⑫ A' 输出==oracle 期望 ⑬ B 随机子集一致`

## 5. 真实性溯源
- metadata.trace_source: {user: dechaoc, host: hfeg0pkn004, session_file: 1794982121198_lfb0j.messages.json, match_count: 297, real_task_summary: "修改 hier_sig 脚本：简化为 2 参输入(网表+cell)，输出路径 DDR5TOP→TOP.Chip 替换"}
- 真实用户/路径/脚本名保留原值

## 6. DEBT
- 本轮（r1129）只做深读，未合成 case（预算时间紧，MCP 复测 + 候选查询 + 深读已用尽 40min 预算）
- 下轮（r1130）合成 `EDA-Eval-DesignFlow-HierSigScriptModify-001`：
  1. 从 .75 host scp 回修改后脚本做 reference（`hfeg0pkn004:/home/dechaoc/hier_sig`）
  2. 从 trace msg#2 tool_result 提取原始脚本做 asset A（或从 diff 反向重建）
  3. 构造 netlist_A.v / netlist_B.v / netlist_Ap.v（裁剪真实网表结构）
  4. 写 check.py (k≥12) + negative_selftest.py
  5. 自验 + 追加 D.jsonl
