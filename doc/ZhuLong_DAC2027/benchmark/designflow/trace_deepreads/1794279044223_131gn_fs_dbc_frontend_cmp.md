# trace_deepread: 1794279044223_131gn (lorikx @ hfeg0plg15) — FS/DBC frontend tree comparison

**session**: 602795 bytes / 57 msgs / mtime 2026-11-10 15:06 (alive, scp'd via .75)
**user/host**: lorikx @ hfeg0plg15 (10.129.2.10), mc=19, keywords verilog:363;rtl:345;synopsys:19
**shard**: A (digital) — B ledger had parked it 2026-11-11 as "wrong-shard A: digital RTL FS-to-DBC replacement"; r719 --force hatch-claimed for A.

## 用户意图（原话）
- **U#0**: `请对比/home/lorikx/1_TV1/CXTV1_FS001A/frontend/与/proj/lacaa/TV1_TestChips/CXTV1_DBC001A/frontend/的文件区别，这两个路径下的文件基本一致，主要是FS和DBC的区别，请先给我输出一个对比报告文件，所有中间文件和结果文件都可一在/home/lorikx/MY_SANDBOX/DBC_SORT/进行和处理，我后面需要把FS路径下的文件都复制到DBC路径下，但是文件和代码中的FS也都需要同步换成DBC,需要根据情况判断大小写的替换，先做一个对比判断整理一下有多少需要做的`
- **U#48**: `请阅读/proj/lacaa/TV1_TestChips/CXTV1_DBC001A/libs/latest/Vlist文件，这个是DBC适用的filelist，这个列表基本代表了所有需要替换的rtl代码，等挪过来之后这些文件也都需要改成FS的，请再次分析两个frontend文件夹转移所需要改动的部分`
- **U#50/U#55**: `继续`

## 真实交付意图
写一个**可断点续跑**的 Python 对比工具，输入两个并行的 frontend 目录树（仅芯片代号 token 不同 FS↔DBC），产出 Markdown 报告 + CSV 明细：
1. 扫描文件名 + 文件内容中 token 的**四种大小写变体**（FS/Fs/fS/fs）
2. 识别**不能盲替的风险字符串**（fsdb Verdi 波形、fsearch VCS 调试、covg_defs、nfs —— 这些 "fs" 是 EDA 工具词，盲替会破坏仿真）
3. 共有但内容不同的文件分类：`fs2dbc-exact`（DBC 侧恰好等于 FS 侧做大小写敏感替换）/ `naming-only`（差异仅与命名有关但非精确改名）/ `real-difference`（与命名无关的真实差异）
4. 仅在 FS 侧 / 仅在 DBC 侧 / 共有相同 / 共同不同 的文件清单
5. 状态存 `.compare_state.json`，分阶段(walk→md5→scan→diff→report)可反复运行续跑（大目录树扫描易超时被 SIGKILL）

## agent 流水线
list_allowed_files 测两目录可访问性（发现 `/home/lorikx/1_TV1/CXTV1_FS001A` 是符号链接 → `/proj/lacaa/...`）→ editor 分 5 段写 `compare_frontend.py`（445 行，超时被 SIGKILL 在内容扫描阶段）→ 重写 `compare_frontend_v2.py`（529 行，带断点续跑 + 状态 JSON）→ 首轮 run SIGKILL 在 scan 3000/3568 → 二轮续跑完成 scan+diff，报告生成 crash（`LARGE_EQUAL` 条目 md5 list 只有 1 元素索引越界）→ 修分类逻辑 → 三轮 run_completed 出报告 → read_files 验证 report + 9 CSV。

## 实测数据（A 档真实）
- FS: 3568 文件 / 723 目录；DBC: 2505 文件 / 188 目录
- only-in-FS: 2121, only-in-DBC: 1058, common: 1447（相同 768 / 不同 487 / 过大 1 / 错误 191）
- 文件名改名: 459 文件 + 151 目录（FS:315, fs:144, 无 Fs/fS）
- 内容替换: 1320 文件（文本 770 / 二进制 550），风险: 319 文件
- diff: real-difference 476, fs2dbc-exact 7, naming-only 2, too-large 2
- 191 错误中 187 是失效符号链接/已消失 VCS 临时文件

## 造题化（EDA-Eval-DesignFlow-FsDbcFrontendCmp-001）
通用化: `compare_frontend_trees.py <src> <dst> <out> --token-x FS --token-y DBC --risky fsdb,fsearch,covg_defs,nfs` → report_summary.md + 7 CSV + .compare_state.json。
- **A 档（可见）**: FS/DBC 真实芯片代号 CXTV1_FS001A/CXTV1_DBC001A，小规模忠实结构
- **B 档（隐藏）**: FA/DA token + 不同规模/结构/风险字符串（fadb/fasearch/covg_defa），永不进 SUT 沙箱
- check.py 内联独立 ground-truth 重解析，15 条独立断言(a-o)，3 negatives 全 FAIL（neg_empty→b, neg_print_expected→c 硬编码 A, neg_core_deleted→g 删 x2y-exact 检测）
- 自验: reference_submit.zip PASS(15/15) / 3 negatives 全 FAIL / §4.9 三假提交全 FAIL / k_check==k_rationale==15 / e2e(jsonl 内 test 字段提取跑) PASS参考+FAIL负样本
