# 深读笔记 · sid 1794465768817_w8jus · ghyang @ hfeg0pkn003/10.129.2.12 · mc77

**domain**: schematic_netlist (kw netlist:371;schematic:121;cmos:63;pex:58;drc:24;hspice...)
**trace**: messages.json 468KB / 82 msgs / 5 user turns · 真实场景 DDGOA SRAM 仿真 deck 引用一致性核查

## 用户意图（逐轮原文）
- U0: 「在这个路径下 /proj/ddgoa/V0/workdir/ghyang/DDGOA/ 有 Yiotwist_case5spf 8 个文件夹，帮我检查每个文件夹下同名的 sim*.sp 文件是否一致」
- U1: 「再次帮我检查这八个路径下对应的同名 sim*.sp 文件，并且重点检查其中 include 的 netlist 和 SPF 文件是否指向同一个文件，其中 *spf* 文件夹应该与 *spfmerge* 分别对应，也就是说这里会有 4 组不同的 SPF_msaq 文件，同样的 SPF_array 文件仅在 merge 中被引用，两种不同的 netlist 文件被分别引用，整理出这些文件引用的三组文件」
- U2: 「修正 sim_p2a4_pl3.sp 第 8 行的笔误」
- U3: 「再帮我检查这个路径下的八组 run-all 文件是不是一致，在这个路径下能不能生成一个可执行文件，让我手动运行后可以依次到对应目录下执行 8 个 run-all」
- U4: 「按照你提供的脚本，我运行了仿真文件，现在统计下任务执行的进展，执行失败的文件读对应的 log 文件分析原因」

## 助手工具链
list_allowed_files(8 文件夹) → read_files(sim*.sp) → run_approved_command(md5sum 比对) → editor(compare_sim_files.py) → 报告 3 版本组(A 单独 / B=spf1-3 / C=merge-3) → U1 → read_files(.inc 内容)+search_codebase → editor(trace_symlinks.py) → run_approved_command(readlink -f 解析 symlink) → 完整引用矩阵报告 → U2 → editor 修 4 个 sim_p2a4_pl3.sp 第 8 行 `.inc "./SPF_msaq"`→`.inc "./SPF_array"` → U3 → editor(DDGOA_run_all.sh) + make_executable.py → U4 转分析 log（env 依赖不进 case）

## 真实 deck 格式（关键）
SPICE 仿真 deck `sim_p1_pl3.sp` / `sim_p1a3_pl3.sp` / `sim_p2a4_pl3.sp` 每文件夹 3 个，include 行形如：
```
.inc "./netlist_twistYio"
.inc "./SPF_msaq"
.inc "./SPF_array"        # 仅 merge 组
```
- `netlist_twistYio` 是 symlink：spf* 组 → netlist_ALPS(16.2MB)；merge* 组 → netlist_ArySpf_MAT1(16.5MB) —— **2 种 netlist**
- `SPF_msaq` 是 symlink：每对 (case5spf, case5spfmerge) 共享一份 —— **4 种 SPF_msaq**（balance/balance1/balance2/balance3）
- `SPF_array` 是 symlink：仅 merge 组引用，4 文件夹指向同一文件 —— **1 种 SPF_array**
- 笔误：case5spfmerge*/sim_p2a4_pl3.sp 第 7-8 行都是 `.inc "./SPF_msaq"`（第 8 行应为 SPF_array）

## 合成计划（case_id EDA-Eval-DesignFlow-SpIncludeTrace-001）
**可移植化**：真实 netlist/SPF 是 16-471MB 私有文件 + symlink → 合成小占位文件（regular file，内容区分），用 **content-md5** 判同/异（替代 realpath，zip 可移植）。

**SUT 产**：`sp_include_tracer.py`（纯 stdlib CLI `python3 sp_include_tracer.py <root> [-o OUT]` → stdout JSON）：
- 遍历 `<root>/*/sim*.sp`，提取 `.inc "X"` 行（include target 原文，有序）
- 相对 deck 所在 folder 解析 X → 目标文件，md5 哈希内容
- 按 basename 类别分类：`netlist*`→netlist / `SPF_msaq`→SPF_msaq / `SPF_array`→SPF_array
- 输出 JSON：folders{decks{inc列表}} / deck_groups(同 deck 内容 md5 的 folder 簇) / include_groups{类别:[{hash,folders}]} / duplicate_includes(同 deck 内重复 .inc target)

**visible A**（SUT 可见示例，4 folder）：case5spf/case5spf1/case5spfmerge/case5spfmerge1，2 netlist / 2 SPF_msaq / 1 SPF_array / 1 typo(case5spfmerge sim_p2a4 重复 SPF_msaq)
**hidden B**（check 主跑，6 folder）：case5spf/spf1/spf2/merge/merge1/merge2，2 netlist / 3 SPF_msaq / 1 SPF_array / 1 typo(merge sim_p2a4)
**hidden C**（跨输入反硬编码，4 folder）：不同 folder 名 + 不同组数（2 netlist / 2 SPF_msaq / 0 SPF_array / 无 typo）—— 反硬编码 A/B folder 名与组数

**check.py 16 cond a-p**：a zip合法仅1个.py / b py_compile / c 源码不硬编码 A/B folder 名+内容字面量 / d B运行exit0 / e 输出合法JSON / f folders集=B / g 每folder decks inc列表=oracle / h deck_groups=oracle / i netlist distinct hash 数=oracle / j netlist folder集=oracle / k SPF_msaq distinct 数=oracle / l SPF_msaq folder集=oracle / m SPF_array distinct 数=oracle / n SPF_array folder集=oracle / o duplicate_includes=oracle / p 跨输入 C netlist+SPF_msaq+SPF_array distinct 数=oracle_C 且 duplicate=oracle_C（反硬编码）。内嵌 oracle 独立 walk B/C 树自算，非文本相似。

**negatives**：empty_shell(→d) / print_only 硬编码 B 输出(→e/f) / hardcode_a 硬编码 A folder 名(→c) / core_removed 不解析 .inc(→g) —— distinct failure labels 全 FAIL。

**test_rationale**：16 条断言 ①zip 内仅 1 个 .py ②py_compile 通过 ③源码不含 A/B 任何 folder 名与内容字面量 ④B 运行 exit 0 ⑤stdout 合法 JSON ⑥folders 集合 == B 的 6 folder ⑦每 folder 每 deck 的 .inc target 有序列表 == oracle ⑧deck_groups(folder 按全部 deck 内容 md5 等价分簇) == oracle ⑨netlist 类 distinct 内容 hash 数 == 2 ⑩netlist 各 hash 的引用 folder 集 == oracle ⑪SPF_msaq distinct 数 == 3 ⑫SPF_msaq folder 集 == oracle ⑬SPF_array distinct 数 == 1 ⑭SPF_array folder 集 == oracle ⑮duplicate_includes(同 deck 内重复 .inc target) == oracle(B: case5spfmerge/sim_p2a4_pl3.sp SPF_msaq count=2) ⑯跨输入 C: netlist/SPF_msaq/SPF_array distinct 数 + duplicate == oracle_C（反硬编码 A/B）。

**难度评估**：L2（真解析 SPICE deck include 语法 + 路径解析 + 内容哈希分组 + 重复检测 + deck 内容簇），netlist-text-transform/parse 子类，D 域连续第 7 轮此类。SUT 须正确处理：(a) `.inc "X"` 引号内 target 提取；(b) target 相对 deck folder 解析；(c) 类别按 basename 前缀；(d) 同一 deck 内重复 target 检测；(e) deck 簇按全 deck md5。naive-count / print-only / 硬编码 A 均被多条件拦。
