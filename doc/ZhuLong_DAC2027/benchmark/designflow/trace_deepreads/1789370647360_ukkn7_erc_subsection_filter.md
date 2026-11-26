# 深读笔记 — 1789370647360_ukkn7 (e0031668 / hfeg0plg91)

- **session**: `1789370647360_ukkn7.messages.json`（1,616,161 B，867 msgs：447 user / 420 assistant，agent=lead）
- **host/user**: hfeg0plg91 / e0031668；工作目录 `/home/e0031668/work/ERC`
- **match_count**: 1478（755 netlist · 731 virtuoso · 48 schematic · 42 cellview · 16 calibre · 15 hspice · 7 pyAether）
- **domain**: schematic_netlist（ERC 报错表 + AETHER-SE spice 网表后处理）
- **shard**: D

## 用户真实意图（逐字原文，按轮）
1. `msg[0]`（纯需求轮，A 档可用）：「你的工作目录是：/home/e0031668/work/ERC，ERC_AI_CHECK 代码在 ERC/codes下，请基于codes下的run_all.sh，对ERC/drcpa/下的数据文件跑完所有follow，只看erc报错里面的2.1-2.8 的；」
2. `msg[77/95]`：同上（重发，llm_config.json 已配好；要求执行完 pipeline）
3. `msg[279]`：「确认下现在run到哪一步了，virtuoso 为何没有调用起来」（指出工具未起，给出方向但非根因）
4. `msg[669]`：「我知道了，这是个aether项目，你需要启动aether去检验而不是virtuoso」（**用户指出根因 → 不可作 A 档任务说明**，可作 hint）
5. `msg[783/785]`：「先停下吧，可能是登陆节点的问题，等我换个登陆节点 / 我已经更换了登陆节点，你再试试」
6. `msg[828]`：「我一般是通过vir命令进入选择项目的界面，在选定项目和版本后再通过 aetherLE或aetherSE进入aether」（**用户给出修复方案 → 不可作 A 档任务说明**）
7. `msg[865/866]`：「step3及以后的flow，现在的代码只提供了virtuoso环境的脚本.il，这个项目是aether的，需要你改写一套aether flow」（**用户给出后续需求**）

## assistant 工具链
`list_allowed_files` → `read_files`(run_all.sh / analyze_errors_v1.py / prepare_new_netlist.py / ERC_Wesign.csv / netlist) → `search_codebase`(filter_erc_by_section / erc_section) → `editor`（逐行改 `prepare_new_netlist.py`：把只按主 section "2" 过滤改成支持子段 2.1-2.8；文件含 `\r\n` 故单行替换）→ `editor` 新建 `run_drcpa_218.sh`（软链数据文件到 codes/）→ `get_agent_policy_status`/`run_approved_command`（policy 限制 shell，改由用户执行）→ 后续切 aether：`run_aether_py.sh` / `aether_db.py` / `aether_get_cell_chains.py` / `aether_verify_paths.py`（pyAether 校验实例路径）

## 关键产物（host 上实际存在）
- `/home/e0031668/work/ERC/drcpa/ERC_Wesign.csv`（27007 行；分号分隔；列 `#Chkitem,Dev|Node,Hierarchy,Subinfo,Attributes,Status,Part`；Chkitem 形如 `2.1_ChkMosVgs_2.0`、`3.8_ChkMosFwBias_1.2`）
- `/home/e0031668/work/ERC/drcpa/netlist`（353295 行；AETHER-SE 导出；顶层 DDR5TOP）
- `/home/e0031668/work/ERC/drcpa/vtable_real.csv`（411 行）
- `codes/prepare_new_netlist.py`（修改后支持子段过滤）、`codes/run_drcpa_218.sh`、`codes/ERC_Wesign_section2.1_..._2.8.csv`（6MB 过滤产物）

## 真实 section 分布（ERC_Wesign.csv，awk 统计）
```
3.1=7920  2.2=5412  2.7=2171  3.8=2040  4.1=2033  2.1=1760  5.1=1756
2.6=1155  2.8=1066  3.4=458  4.3=360  3.5=270  3.9=235  3.6=144
4.2=103  5.2=74  3.2=46  2.4=3
```
→ 2.1-2.8 现存：2.1/2.2/2.4/2.6/2.7/2.8（2.3/2.5 为 0）；需排除 3.x/4.x/5.x。**真实数据无 2.10/2.11**（边界用例需合成）。

## 合成决策（B 档）
- trace 末尾用户尚未「接受」完整结果（停在「改写 aether flow」需求上），A 档金标准不可锚定 → 取 **B 档 synthesized**。
- 选取最自洽、可验证的子问题：**ERC 子段过滤（2.1-2.8）+ summary 统计**。这是 trace 中 assistant 真正解决、且产物可独立验证的一环。
- A（SUT 可见）：从真实 ERC_Wesign.csv 按 section 采样 689 行（保留真实 Chkitem/hierarchy 模式，无 2.10）+ 真实结构 netlist 片段。
- B（隐藏，check 仅跑此）：合成 1275 行，**含 2.10/2.11 边界（71+29）**与 2.3/2.5，分布与 A 不同 → 击败前缀硬编码与 print 式欺诈。
- check.py：14 条独立断言 (a)-(n)，含 subprocess 真跑候选 (l) + 跨输入守卫 (m，合成 mini 输入击败硬编码 B 答案)。
- 5 个负样本（3 个 §4.9 假提交 + 2 个 naive）均 FAIL，各击中不同 label。

## 闸门
- k_rationale = 14 == k_check = 14 >= 8 ✓
- test==disk roundtrip ✓；test 以 `def check(` 开头 ✓
- ref PASS / 5 negatives ALL-FAIL（NEG_RC=0）✓
- level=L1（离线 Python 解析真实结构 ERC CSV+netlist；该 shard 已有 L2 案例，本条为 schematic_netlist 域覆盖补牙，L1 在 §5 配额内）
- track=B
