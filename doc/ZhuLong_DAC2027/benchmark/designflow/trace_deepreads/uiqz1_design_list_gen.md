# 深读笔记: uiqz1 — CXDP 设计流 gen_design_list.pl (digital)

## trace
- session: `1792843726821_uiqz1`
- user: e0043890 @ hfeg0pnd002 (mc=212)
- size: 2.28MB / 857 msgs / session 文件最后修改 2026-10-31 16:09
- tools: cline 在 SoC 团队 CAD 团队联合打造的 CXDP 前端流程环境上工作；核心交付是 perl 脚本 `gen_design_list.pl`
- ledger: 行 194（claim 2026-11-07 11:44 → case 2026-11-07 12:44, case_id=EDA-Eval-DesignFlow-DesignListGen-001）

## 用户意图
USER#5（干净需求轮，A-faithful rule2 未违反）逐字需要：「写 perl 脚本 `gen_design_list.pl`，读取 `CXDP_DESIGN_CFG` + `CXDP_PROJ_CFG`，生成 `designlist.f`（含 RTL 绝对路径）供 SG-Lint 使用」。
- 脚本在某模块的 `lint/run` 目录下用 `perl gen_design_list.pl` 执行
- CFG 文件是 `键 = 值` 格式，`#` 开头注释，值里可能出现 `$(变量名)` 引用（CXDP_DESIGN_CFG 优先于 CXDP_PROJ_CFG）
- `CXDP_DESIGN_ROOT` 给出设计根目录（相对 lint/run，如 `../..`），`CXDP_RTL_SRC_DIR` 是 RTL 源目录名（相对设计根），`CXDP_RTL_FILE_LIST` 是 RTL 清单文件名
- 清单文件每行一个 RTL 文件名或 glob（如 `*.v`），`#` 开头注释；要把 glob 展开、注释/空行跳过，解析成 RTL 绝对路径写入 `designlist.f`（写在 lint/run 下）

## assistant 工具链 / 真实产物
1. 探 CXDP 设计流目录结构（`create_cxdp_dir.py -name <mod> -proj_cfg <proj_vars>` 创建模块目录，设计文件放 `<mod>/src_rtl`）
2. 读取真实 `CXDP_DESIGN_CFG` / `CXDP_PROJ_CFG` 格式样例
3. 写并迭代 `gen_design_list.pl`（msg#105 为最终 gold 版本）
4. 真实 `designlist` 清单内容样例（`*.v` glob 形式 + `##TOP_MODULE` 头）

## A-faithful 判定
**B 档 synthesized**：真实 `/proj/lacaa` 资产从 e0031982 不可达（698 机器只读、/proj 路径不可挂），无法把真实 CXDP 模块树原样附加给 SUT。但任务本身（CFG 解析 + glob 展开 + 绝对路径生成）逻辑清晰、可移植性强，适合 B 档合成：A=cla_top 致敬样例，B1=pwr_ctrl，B2=axi_bridge（带 `$(CXDP_RTL_BASE)` 变量 + 显式 filelist.f）。

## 合成 plan
facet = **CXDP designlist.f 生成器**(`gen_design_list.pl`，perl)
- 输入: 某模块 `lint/run/` 下的 `CXDP_DESIGN_CFG` + `CXDP_PROJ_CFG`
- 解析: `键 = 值`，`#` 注释，`$(VAR)` 展开（DESIGN_CFG 优先于 PROJ_CFG）
- 路径: `CXDP_DESIGN_ROOT`（相对 lint/run）→ `CXDP_RTL_SRC_DIR`（相对设计根，可能是 `$(CXDP_RTL_BASE)` 需进一步展开）→ 读 `CXDP_RTL_FILE_LIST` 清单
- 清单: 每行文件名或 glob（`*.v`），展开 glob，跳过注释/空行
- 输出: `designlist.f`（写在 lint/run 下），含 RTL 绝对路径

### 三棵树（B 档差异化）
- **demo_a / cla_top**: `src_rtl`，清单 `designlist` 内含 `*.v`，5 个 RTL（cla_top/cla2/cla4/cla_recursive/full_adder）— SUT 可见
- **demo_b1 / pwr_ctrl**: `src_rtl`，清单 `rtl_files` 内含 `*.v` + 一行注释，4 个 RTL（pwr_ctrl/pwr_fsm/pwr_gate/pwr_seq）— hidden
- **demo_b2 / axi_bridge**: `CXDP_RTL_SRC_DIR = $(CXDP_RTL_BASE)`（在 PROJ_CFG 里定义为 `rtl_src`），清单 `filelist.f` 是显式列表（无 glob）+ 注释，3 个 RTL（axi_bridge/axi_master/axi_slave）— hidden

### 反硬编码守卫
1. **B1/B2/A 三树结构互异**（清单名/目录名/glob vs 显式/变量展开全不同）
2. 条件 `j`: 候选必须在 A 上也跑通且 A 路径集合 == A 金标（证候选是通用 CFG 解析器，非硬编 B）
3. 条件 `o`: 候选源码不得含 B1/B2 设计名或 RTL 名（pwr_ctrl/axi_bridge/pwr_fsm/...），防直接硬编 B 路径

### check 15 条件 a-o
- a: submit.zip 存在 + 合法 zip + 含 gen_design_list.pl
- b: `perl -c` 语法编译通过
- c: [B1] perl 运行 exit 0
- d: [B1] 产出 designlist.f
- e: [B1] 路径集合 == 期望 4 个 pwr_*.v 绝对路径
- f: [B1] 全部绝对路径且文件真实存在
- g: [B1] 路径排序且唯一
- h: [B2] perl 运行 exit 0 且产出 designlist.f
- i: [B2] 路径集合 == 期望 3 个 axi_*.v 绝对路径
- j: [A] perl exit 0 + 路径集合 == A 金标 5 个 cla*.v（反硬编码守卫）
- k: [B1] 无 A 的 basename（cla*.v）混入
- l: [B2] 路径含 `/rtl_src/`（证 `$(CXDP_RTL_BASE)` 正确展开）
- m: [B1] 无未展开 glob 且无清单文件名作为路径
- n: [B2] designlist.f 无未解析 `$(VAR)`
- o: 源码不含 B1/B2 设计或 RTL 名（pwr_ctrl/axi_bridge 等，防硬编码）

### 自验（.75 + 本地独立 mktemp 双验）
- ref PASS 15/15 a-o（reference_submit.zip = ref_gen_design_list.pl）
- ref 在 A/B1/B2 三树上分别产 5/4/3 条排序绝对路径，与金标一致
- 5 negatives 全 FAIL（naive_empty→d / hardcoded_A→e / hardcoded_B1→o / print_expected→o / core_deleted→e），各 distinct first_fail
- §4.9 三假（empty / print_expected / core_deleted）全 FAIL；额外 empty_zip→a / empty_pl→d 全 FAIL
- 断言闸门 k_rationale=k_check=15 ✓（≥8）

## 教训
1. **perl CFG 解析类任务是 B 档 L1 好范式**：`键=值` + `$(VAR)` 展开 + glob + 相对路径拼接，逻辑清晰可合成，15 条件天然丰富（编译/三树实跑/路径集合/绝对/排序/变量展开/反硬编码）。
2. **`$(CXDP_RTL_BASE)` 是强反硬编码轴**：B2 的 `CXDP_RTL_SRC_DIR` 本身是 `$(CXDP_RTL_BASE)` 变量（在 PROJ_CFG 定义为 `rtl_src`），naive 只取字面值者 l/n 上 FAIL；条件 l（含 `/rtl_src/`）+ n（无未解析 `$(`）双重锁定变量展开正确性。
3. **三树差异化防硬编码**：A=glob(`*.v`)+`designlist` / B1=glob+`rtl_files`+注释 / B2=显式 filelist+变量展开，三树清单名/目录名/展开方式全不同，hardcoded_A 在 e 上 FAIL（A 路径进 B1），hardcoded_B1 在 o 上 FAIL（源码含 pwr_ctrl）。
4. **write_file plain content 腐蚀 perl 反斜杠**：perl 正则里的 `\S`/`\.` 在 write_file plain content 下被转义吃掉；必须用 `run_commands` heredoc（`<<'PLEOF'`）写 perl/python 含反斜杠的文件。UTF-8 中文（prompt/task_brief）用 write_file plain 无碍。
5. **trace_ledger.py mark 需用完整 session_file**：台账行存 `1792843726821_uiqz1.messages.json`（带 `.messages.json` 后缀），mark 传 bare id 会 append 空行而非 in-place 更新；务必传完整 session_file 字符串。
