# 深读笔记 — 1790128993113_iiqrs (jinhaoli @ hfeg0pkn004)

> shard A · domain=verification · mc=218 · claim r401 · 2026-11-11
> trace_source: user=jinhaoli, host=hfeg0pkn004, session_file=1790128993113_iiqrs.messages.json, match_count=218
> session: 96 msgs, 1.32MB, status=completed, model=deepseek-v4-flash, cwd=/home/jinhaoli
> kw: verilog:2235;systemverilog:80;drc:2021;netlist:343;analog:39;schematic:35;cadence:9;aether:7

## 真实用户意图（原话，A 档素材）

1. `/proj/drcpa/V0/simdir/verilog/jinhaoli/vm2_git2 这个路径下的编译和仿真跑不起来，是什么原因？`
2. `已经source 了set_env.sh`
3. `/rundata/drcpa/V0/simdir/verilog/jinhaoli/vm2_git2/dlut_func.sv的discard task有没有问题`
4. `在文件的第356行`

**real_task_summary**: DDR5 DRAM 验证环境（xcelium/xrun）的 reference model 调试。用户报告 vm2_git2 仿真跑不起来，怀疑 `dlut_func.sv` 第 356 行的 `discard` task 有问题。Agent 深读后定位到一个**致命的 SystemVerilog 对象引用 bug**。

## Agent 工具链

- `list_allowed_files` ×27（受 policy 限制，只能列目录）→ `read_files` ×19（按行段读源文件）→ `search_codebase` ×6 → `run_commands` ×2（被 policy 禁用：`Raw shell tool run_commands is disabled`）
- 关键发现路径：列 vm2_git2 结构 → 读 top.sv/global_config.sv/run_build/xrun.log → 读 dlut_func.sv 290-395 行 → 搜 `discard` 调用点（ref_dlut.sv:182 `discard(0)`）→ 分析 `discard_sel` task。

## 定位到的真实 bug（致命 · dlut_func.sv 384-390 行）

`discard_sel` task 把**同一个** `TYPE_DLUT_INFO` 句柄 push 6 次进队列，导致队列 6 个条目全部指向同一对象，前 5 条数据被覆盖丢失。

**buggy 代码**（agent 抓取的真实代码）：
```systemverilog
task discard_sel(bit sc, int bk_num, int num23, int num12);
   for(int arr = 0; arr < 6; arr++)begin
      ...
      if(dlut_info_exp[bk_num] == null)
         dlut_info_exp[bk_num] = new();    // 只在第一次创建对象
      dlut_info_exp[bk_num].sc = sc;
      dlut_info_exp[bk_num].bg = bk_num[2];
      dlut_info_exp[bk_num].ba = bk_num[1:0];
      dlut_info_exp[bk_num].fifo[arr].ac = ...;
      TOP.dlut_info_q[sc][bk_num].push_back(dlut_info_exp[bk_num]);  // 每次都 push 同一个对象
   end
endtask
```

**根因**：`dlut_info_exp[bk_num]` 是 handle（引用），不是值对象。`arr=0` 创建对象 A、改 `A.fifo[0].ac`、push A；`arr=1` 改同一对象 `A.fifo[1].ac`、再 push A（队列里之前的 A 的 fifo[0] 也被覆盖）……最终队列 6 条全是 A，且都显示 arr=5 的状态。

**修复**（agent 给出的 ref 解）：循环内每轮 new 一个新对象：
```systemverilog
for(int arr = 0; arr < 6; arr++)begin
    automatic TYPE_DLUT_INFO new_entry = new();
    new_entry.sc = sc;
    new_entry.bg = bk_num[2];
    new_entry.ba = bk_num[1:0];
    new_entry.fifo[arr].ac = TOP.array_bank_user[sc][bk_num].dfifo.fifo[arr].ac;
    TOP.dlut_info_q[sc][bk_num].push_back(new_entry);
end
```

## 次要问题（同一线索）

- **问题 2（中）· 第 363 行**：`wait(TOP.array_bank_user[sc][bk_num].dfifo.discard)` 是电平敏感，`discard` 保持 1 时 `discard_sel` 会被立即重复触发（潜在死循环）。建议改 `@(posedge ...discard)`。
- **问题 3（低）· global_config.sv 155-158**：`discard` 在 `update_dlut` 函数内组合赋值，fifo 由满变不满时不会自动清零，须等下次 `update_dlut`。
- **环境问题**：09-24 的 xrun.log 高达 1.4TB（磁盘/配额可能满）；`libs`/`libsdb`/`sdf` 三个软链接全指向同事 `stevenh` 的个人目录（权限/变动风险）。

## 合成计划（下一轮第一件事 · DEBT:1）

**case_id 候选**：`EDA-Eval-DesignFlow-DiscardRefFix-001`（A 档，trace-faithful）

- **prompt（A 档，用真实用户原话）**：用户报告 vm2_git2 仿真跑不起来，怀疑 dlut_func.sv:356 的 discard task；已 source set_env.sh。要求 SUT 诊断并修复 `discard_sel` 的引用 bug，交付修复后的 `dlut_func.sv`。
- **attachments A**：合成一份含 buggy `discard_sel` 的 `dlut_func.sv`（保留真实代码结构：`task discard_sel` + for 循环 + 共享 handle push_back）+ `global_config.sv` 片段（含 `TYPE_DLUT_INFO` 定义、`dlut_info_q` 队列声明）+ `ref_dlut.sv` 片段（含 `discard(0)` 调用点）。
- **hidden B**：变体——把 bug 移到另一个 task（如 `one_bank_ref_rhr` 里类似的 push_back 共享 handle），规模/取值不同（6→8 次循环、不同 bk_num）。
- **reference/discard_fix.sv**：循环内 `automatic ... = new()` 的修复版。
- **check.py（≥8 断言，L2 静态语义 + Python 句柄模拟）**：
  ① 提交 zip 解出 `dlut_func.sv` 且可解析；
  ② 含 `task discard_sel` 定义；
  ③ `discard_sel` 内含 for 循环；
  ④ 循环**体内**每轮创建新对象（命中 `automatic TYPE_DLUT_INFO ... = new()` 或等价）；
  ⑤ `push_back` 的实参是该新对象，**不是** `dlut_info_exp[bk_num]`；
  ⑥ **反模式缺席**：全文件不存在「push_back(dlut_info_exp[...)」且无循环内 new 的形态；
  ⑦ Python 句柄模拟：用 list-of-dicts 模拟队列，跑 6 次循环后断言队列 6 个条目 `id()` 互异、且各自 `fifo[arr].ac` 保留独立值（不被后续轮覆盖）；
  ⑧ 随机化：循环次数 3 个种子（6/8/10）跑 3 次结论一致；
  ⑨ 修复后 `dlut_info_q[sc][bk_num]` 的 size == 循环次数。
  → k_check = 9（≥8 ✓）。**test_rationale** = `9 条断言：① zip 解出 dlut_func.sv 可解析 ② 含 task discard_sel 定义 ③ discard_sel 内含 for 循环 ④ 循环体内每轮新建 TYPE_DLUT_INFO 对象 ⑤ push_back 实参为新对象而非 dlut_info_exp[bk_num] ⑥ 反模式（push_back 共享 handle 无 per-iteration new）在全文件缺席 ⑦ Python 句柄模拟：6 轮后队列 6 条目 id 互异且 fifo[arr].ac 各自独立保留 ⑧ 3 个随机种子（循环 6/8/10）结论一致 ⑨ 修复后 dlut_info_q size == 循环次数`
- **negative/**：① naive = 删除整个 `discard_sel` task；② always-stub = `push_back(null)` 不创建对象；③ 伪修复 = 把 `if(dlut_info_exp[bk_num]==null) new()` 改成无条件 new 但仍 push 共享 handle（骗断言④但骗不过⑦）。`negative_selftest.py` 三个全 FAIL。
- **三假提交回归**：(a) 空壳 dlut_func.sv (b) 只 print 期望串的 .sv (c) ref 删掉循环内 new —— 全 FAIL。
- **难度**：L2（真跑 Python 句柄语义模拟 + 静态 SV 模式匹配，非纯文本相似）。归 verification 域。

## 待确认 / 风险

- 真实 `dlut_func.sv` 我无读权限（jinhaoli 所有），但 agent 在 session 里抓到了 290-395 行真实代码（见上）。合成时直接用这段真实代码做 A 档附件，保真。
- 是否需要真跑 xcelium/xrun 编译？sandbox 不一定有 xrun；用 Python 句柄模拟 + 静态断言已达 L2 门槛（真跑候选脚本是 Python 模拟器，断言输出结构而非文本相似，符合 §4.2）。
- DEBT 来源：本轮选料 + 深读耗时较多（awk 正则超长被截断 → 改 Python；NFS 同一 session 多主机去重；cline 消息 schema 适配），剩余预算不足以走完自验 + jsonl 闭环，按硬闸门不入库。
