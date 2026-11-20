# trace_deepreads/y4c5b_JobmonitorFeatPatch.md — shard A r377

- **session**: 1790038213566_y4c5b.messages.json @ /home/rongjiez/.cline/data/sessions/1790038213566_y4c5b/ on 10.129.2.14
- **user/host/mc**: rongjiez / 10.129.2.14 / mc=19 (ledger domain=eda_other)
- **size**: 111 msgs / 3 real user turns / ~1.01 MB
- **A-faithful**: YES. U#0 给 3 项需求未给实现（"界面增加输出路径显示和选择…换一个路径…刷新…别的路径仿真状态"；"表格不需要显示行序号"；"加一个在 run 的 job 数量显示…底部右下角"）。U#1 "我修改了权限你可以直接改吗"。U#2 报告 patch 应用失败（jobmonitor.h Hunk#3 FAILED、jobmonitor.cpp 多个 hunk FAILED + malformed at line 157）。

## user turns
- U#0: 3 项 Jobmonitor 功能需求（输出路径显示/选择、表格不显示行序号、running job 计数）。
- U#1: 改了权限让 agent 直接改。
- U#2: 贴 `patch -p1` 输出，patch 部分失败。

## agent 工具链
list_allowed_files(SRAMAutoSim) → search_codebase(timeout) → read_files(jobmonitor.h/cpp/ui/mainwindow.*) → editor 原位改 jobmonitor.ui/.h → write patch `/home/rongjiez/.cline/scripts/data/jobmonitor_changes.patch`（unified diff, 156 行）→ U#2 报失败后改写完整修改版到 .cline/scripts/data/jobmonitor.{cpp,h,ui}（全文件）。

## base 文件规模（on-disk，agent 已原位改 .h/.ui）
- jobmonitor.cpp = 446 行（未原位改，但 patch 部分应用 → 状态不一致）
- jobmonitor.h = 51 行（原位改后）
- jobmonitor.ui = 231 行（原位改后）
- 共 728 行（小）

## 3 项功能的 agent 实现（从 trace patch + 修改版文件提取）
1. 输出路径：.ui 加 `horizontalLayout_OutputPath`（label_OutputPath + lineEdit_OutputPath + pushButton_Browse）；.cpp 构造函数 `ui->lineEdit_OutputPath->setText(m_outputPath)`；新增 `onBrowseOutputPath()` 用 `QFileDialog::getExistingDirectory`。
2. 行序号：`.cpp initUI` 加 `ui->tableWidget_JobMonitor->verticalHeader()->setVisible(false)`。
3. running 计数：.h 加 `QLabel *m_runningCountLabel;`；.cpp 构造函数 `new QLabel` + `statusBar()->addPermanentWidget`；`loadJsonFile` 统计 RUN/RUNNING 并 `setText("Running: %1")`。

## reframe 决策（B档 synthesized, L1）
- A 不可行：trace 交付件 = 一次性 patch（基于具体 A 文件，patch 在 trace 中应用失败）+ 全文件拷贝；无法在隐藏 B（结构不同）上判分；patch 本身失败不宜作 gold。
- B档：抽同构逻辑做通用 Python 转换脚本 `gen_jobmonitor_patch.py`（读 base_dir → 锚点插入 → 写 out_dir 的三个增强文件），对齐 r367-r373 spec-driven-generator 模式。
- hidden B（结构不同于 A）：5 列含 "Time" 表头 + onExport() 方法 + m_exportPath 成员 + pushButton_Export 按钮。B 保留性条件（l/m/n）强制脚本真正读取 B，击败"吐固定 A 文件"的偷懒解。
- 判分：14 条独立条件 a-n，3 seed 随机化顺序一致性，gold PASS 14/14，5 negative 全 FAIL，§4.9 (a)(b)(c) 全 FAIL。

## 交付
- task_id: EDA-Eval-DesignFlow-JobmonitorFeatPatch-001
- domain: eda_other, difficulty: L1
- A.jsonl 209 → 210
