# deepread: n8v0l — GDS 目录比较 (e0049141)

**session**: `1794806064507_n8v0l` @ `/home/e0049141/.cline/data/sessions/` (host hfeg0plg54=10.129.35.73)
**user**: e0049141  **mc**: 33  **domain**: physical_verify  **size**: 240KB / 37 msgs / 1 真 user 轮
**claim**: r870 (2026-11-20)

## 用户原话 (U#0, trace-faithful, 单轮干净意图)
> 比较一下 /rundata/lacaa/TV1_DBC/ALS_PDK/lvs/public/GDS/FS 和
> /rundata/lacaa/TV1_DBC/ALS_PDK/lvs/wzliao/lvsqa/ALSQA_LVS_V0.5a_20261116/FSQA/cal/data/sample_check/GDS
> 两个路径下的 gds 文件有什么区别？

单轮意图、无后续追问、无给出根因/修复——A 档 trace-faithful 候选；reframe 为 fixture-driven 档 B。

## 助手 gold 链（trace 内）
1. `list_allowed_files` 两目录 → 文件列表被截断
2. `editor` 写 `/home/e0049141/compare_gds_dirs.py`：
   - 扫 `.gds` 文件，计算 only_in_A / only_in_B / common（按 basename）
   - 对 common 文件计算 size + MD5，判 IDENTICAL / DIFFERENT
   - 输出报告 + 写 `/home/e0049141/gds_compare_report.txt`
3. `run_approved_command`（python-runner）跑 → 输出截断 → 改脚本写文件再 `read_files` 分段读
4. `editor` 改写为 `gds_deep_dive.py`：逐记录解析 GDSII 二进制（HEADER version,
   BGNLIB mod-time, LIBNAME, STRNAME 列表, BOUNDARY/PATH/SREF/AREF/TEXT 计数）
   对同名不同文件做内部结构对比，解释"为什么不同"
5. 真实结果：A 115 文件 / B 75 文件；only_in_A 85 / only_in_B 45 / common 30 全不同；
   deep dive nelvt_fs.gds: A ver=600 lib=filemerge.db mod=2026-11-05 15:42:04
   structures(1) BOUNDARY=33 TEXT=4；B ver=600 lib=filemerge.db mod=2026-03-23 18:19:33
   structures(2) ['nelvt_fs','single'] ...

**注**：gold 脚本在 .75 autofs `/home/e0049141/` 已不可读（用户清理）；从 trace
editor new_text + run 输出还原 gold 逻辑。

## reframe 设计（档 B fixture-driven）
真实 gold 跑 190 个真实 PDK GDS 文件（不可复制、依赖真实 PDK 路径）→ reframe 为
**两阶段 GDS 目录比较器**，输入是小型合成 GDSII 二进制目录：
- **文件级**：only_in_A / only_in_B / common（按 basename）+ 对 common 计算 size+MD5
  判 IDENTICAL/DIFFERENT
- **深度对比**（deep_dive）：对每个"同名不同"文件逐记录解析 GDSII，报告
  version / mod_time / libname / structures / elem_counts_total

fixture 控制 6 类差异：only_in_A、only_in_B、identical、diff-timestamp、
diff-structure-count、diff-element-counts。隐藏 B 用不同文件名/数量/时间戳/结构。

## 1 case 落库
`EDA-Eval-DesignFlow-GdsDirCmpDeepDive-001`（physical_verify, L1, 档 B, k_check=15,
子型 GDSII-directory-comparator fixture-driven reframe）。**C 域 physical_verify
GDS 目录比较 + 二进制记录 deep-dive reframe 子型首例**（与 GdsLvlStructDiff 单文件
结构 diff / BatchLvlGdsCmp 批级 cmp / DrcResultCountCompare 计数 cmp 正交：本案
= 两目录文件级集合差异 + 同名不同文件 GDSII 记录字段抽取的离线复刻）。

自验：ref solve.py PASS 15/15 + 7 neg FAIL distinct(b/h/j/l/n/o + b) + §4.9
三假提交（empty_stub/print_only_summary/no_elem_count）全 FAIL + roundtrip sha16
bc8ea2d8c673b23a ✓ + JUDGE-tree（check.py __main__ 独立 dir）PASS。
