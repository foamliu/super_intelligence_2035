# r1098 深读：2m9z2 / xkwxk — junlingw GENGUI Netlist topic（.inc 路径 /rundata→/proj 约束）

> ⚠️ **本深读不可合成 case**：2m9z2 已被 shard D 声明为 PyDepGraphAudit-001（2026-11-23 15:49），
> xkwxk 已被 shard D 声明为 SpiceOptionAudit-001（2026-11-23 16:34）。
> 两 session 是同用户(junlingw)同项目(GENGUI)的姊妹会话，netlist topic 内容一致但均跨 shard 被 D 占。
> 深读价值：理解 junlingw GENGUI Netlist tab 的 /rundata→/proj 路径约束设计，为后续若 D 释放或新 scan 出现同主题 fresh session 做准备。

## trace_source
- session: 1795074908715_2m9z2（748 msgs / 2.36MB）+ 1795072422981_xkwxk（741 msgs，姊妹）
- user: junlingw @ hfeg0pkn005（.75 scan 也见 hfeg0plg99，但 plg99 不可达；**pkn005 经 .snapshot/hourly-new.2026-11-22_2100/ 可读**）
- match_count: 190（2m9z2）/ 186（xkwxk）；keywords: .lef:494 netlist:269 hspice:74 synopsys:77 pyaether:44
- domain: spice_sim（FineSim testbench 生成器 GUI 项目）

## 项目背景
junlingw 开发 **GENGUI**（`/proj/drvqa/V0/workdir/junlingw/GENGUI/`），一个 FineSim testbench 生成器 GUI
（`finesim_tb_generator.py` tkinter + `fengine.py` deck 引擎）。80+ user 任务覆盖各 topic
（Process/Lib/Netlist/Power/Source/Analysis/Options/Measure/Output/Corners/Param）。
本深读聚焦 **Netlist topic**（msg 674–747）。

## Netlist topic 用户意图演进（msg 674–747）
1. **U#363 (msg674)**：新建 topic「netlist」放第 2 位，可视化文件对话框打开并导入网表，显示路径。
   → assistant patch `_tabs` 插入 "Netlist" 第 2 位，新增 `_tnl` + `_open_netlist`（`filedialog.askopenfilename`）。
2. **U#369 (msg685)**：对话框默认查看所有文件类型；打开后加 Undo/Redo/Save；不点 Save 不改文件；**最后输出生成 `.inc '路径'`**。
   → fengine `_model` 加 `if inc_nl: L.append(f".inc '{inc_nl}'")`；`_tnl` 加 Undo/Redo/Save 按钮（ScrolledText undo）；filetypes All files 放第一。
3. **U#378 (msg703)**：为什么打开路径是 /rundata？应该是 /proj。
   → 原因：tkinter filedialog 默认从进程 cwd（/rundata）开始。加 `initialdir="/proj"`。
4. **U#382 (msg710)**：按 proj 点开最后路径还是 rundata。
   → `initialdir` 被原生对话框「记忆上次目录」覆盖。加 `os.chdir("/proj")` 双保险。
5. **U#386 (msg717)**：还是 rundata。
   → 改自绘文件浏览器 `_net_browser()`，从 /proj 根开始，不依赖系统对话框。
6. **U#390 (msg724)**：自绘界面直接坏了。
   → bug：按钮 `command=openpick` 在 `openpick` 定义前引用 → NameError。修：先定义全部函数再创建控件，grid 布局。
7. **U#394 (msg731)**：只剩文字没图标。
   → Listbox 无图标。改回原生 filedialog（有图标），`initialdir=self._nl_last`。
8. **U#399 (msg740)**：**「我不关你打开的链接最后是啥，最后输出的必须得是 /proj 不能是 /rundata」**（核心诉求）。
   → 恢复自绘浏览器，**Up 限制在 /proj 以内**（`par.startswith("/proj")` 门槛），选到的文件必在 /proj 下 → `.inc '/proj/...'` 铁定 /proj 开头。
9. **U#403 (msg747)**：这次输出对了是 proj，但可视化图标又没了。（session 结束，未继续）

## 核心交付逻辑（可 reframe 的部分）
最终方案的自绘浏览器 + .inc 发射：
- `state["dir"] = os.path.abspath("/proj")`（起始根）
- Up 按钮 `up()`：`par = dirname(state["dir"])`；**若 not par.startswith("/proj") 则不移动**（Up guard，不能跳出 /proj）
- 列表只列 /proj 子树内的目录/文件
- 选定文件 → `self.nlpath = fn` → fengine `data["nl_include"] = fn` → 输出 `.inc '<fn>'`
- 因 fn 必在 /proj 下 → `.inc '/proj/...'` 保证 /proj 前缀，**绝不可能 /rundata**

## reframe 草案（若未来可合成）
**NetlistIncPathGuardProduce** — 给定 root + 候选文件路径列表 + 一个选择，产出：
1. valid 路径（normalized abspath startswith root+"/"）vs rejected（/rundata 等）
2. Up-guard：每个目录的 parent 是否被阻塞（parent 不在 root 下 → blocked）
3. 选定文件 → `.inc '<normalized abspath>'`（仅 valid 时发射）
4. anti-hardcode：B 用不同 root（如 /proj/chip28）+ 不同路径

L1 纯 Python，k≈10+ 条件（root-prefix / Up-guard / .inc 格式 / reject /rundata / 路径规范化 / anti-hardcode / 确定性）。
**未合成原因**：两 session 均被 shard D 跨 shard 声明，ledger claim 拒绝。

## 连通性发现（r1098 关键）
- **hfeg0plg11 现在可达**（e0031982 免密）—— r1097 记录其不可达，已变。
- **hfeg0plg76 现在可达**（e0031982 免密）—— r1097 记录其不可达，已变。
- hfeg0plg99 仍不可达（timeout）。
- 2m9z2/xkwxk 在 pkn005 的 `.snapshot/hourly-new.2026-11-22_2100/` 可读（嵌套路径 sessions/<sid>/<sid>.messages.json）。
