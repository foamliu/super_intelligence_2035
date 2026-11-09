# trace_deepread: v5icx — anasim_pro runsim_control 队列→core 策略

- **trace**: `1793957358059_v5icx.messages.json` · yanxvwei @ hfeg0pkn002 (10.129.2.11) · mc=71 (71 hspice / 7 netlist / 1 schematic) · 107 msgs / 586KB · mtime 2026-11-06 17:29
- **shard**: B (spice_sim) · **track**: B-synthesized (非 A-faithful，多轮演进需求)
- **case**: `EDA-Eval-DesignFlow-QueueCorePolicyPatch-001` (spice_sim, L1, k=20)

## 工具分布
list_allowed_files×4 / get_agent_policy_status×1 / run_commands×1 / search_codebase×1 / read_files×14 / **editor×17** / run_approved_command×17

## 用户轮（5 轮，逐字原文）
- **U#1 (msg 0)**: `/home/yanxvwei/sos_ws/anasim_pro/ ansim_pro点击Run按钮，会执行什么命令，job的线程数是如何定义的` — 诊断咨询（问 Run 按钮执行什么命令、线程数如何定义）
- **U#2 (msg 59)**: `在queue为fqueue2h时，core_spinbox将线程数设置为1，先告诉我修改那些代码，我给你开放权限后修改` — 提需求（先告知后改）
- **U#3 (msg 67)**: `做修改1，2.只做「选中 fqueue2h 时把值设为 1」，用户仍可手动改大。权限已打开，` — 提需求（限定范围 + 权限开放）
- **U#4 (msg 81)**: `继续改代码，如果不是fqueue2h，默认为6` — 提需求（补 else→6）
- **U#5 (msg 94)**: `将fqueue3_ams2的core也设置为1，tabs/runsim_control.py的权限以开放` — 提需求（追加 fqueue3_ams2）

## A-faithful 判定
**非 A-faithful**：需求跨 U#2→U#5 多轮演进（fqueue2h→1 → +else→6 → +fqueue3_ams2→1），无单轮自包含「提出需求未给根因/修复」的轮次可独立成题。U#2/U#3 已含明确修复方案（"core_spinbox 设为 1"），违反 A-faithful 选轮规则②。→ 作 **B-synthesized** 候选，把多轮演进的需求融合成单条合成 task_brief。

## 金标准（用户最终接受，msg #95 editor）
真值文件 `/home/yanxvwei/sos_ws/anasim_pro/tabs/runsim_control.py`，assistant 在 4 次 editor 调用中演进到最终态：

1. **msg #68**（U#3 后）：`on_queue_selected` 末尾加 `if selected_queue == "fqueue2h": self.core_spinbox.setValue(1)`；`refresh_lsf_queues` blockSignals(False) 后加 `self.on_queue_selected(self.queue_combo.currentText())`
2. **msg #82**（U#4 后）：合并为 `self.core_spinbox.setValue(1 if selected_queue == "fqueue2h" else 6)`
3. **msg #95**（U#5 后，**最终金标准**）：
   ```python
   # 队列核心数策略：fqueue2h / fqueue3_ams2 为 1，其余队列默认 6（均仍可手动调整）
   self.core_spinbox.setValue(
       1 if selected_queue in ("fqueue2h", "fqueue3_ams2") else 6)
   ```
   refresh 保持 `self.on_queue_selected(self.queue_combo.currentText())`（msg #68 已加，后续保留）

期间 assistant 还写了若干临时 py_compile 检查脚本（_pycompile_check.py / _pychk.py）与 cleanup 脚本（_cleanup_tmp2/3.py / _cln.py），用 run_approved_command 跑完即删——**这些脚手架不得出现在交付里**（check.py 断言⑲拦截）。

## 真实代码结构（来自 read_files msg 17/31/38/61）
- 类 `RunSimControlTab(SimExecutionMixin, LSFMonitorMixin, FileStateMixin, SearchReplaceMixin, SpecManagerMixin)`，PyQt5
- `_setup_ui`：`queue_combo=QComboBox()`，`currentTextChanged.connect(self.on_queue_selected)`；`core_spinbox=QSpinBox()`，`setRange(1,16)`，`setValue(1)`
- `on_queue_selected(self, selected_display)`（原 line 1555）：`selected_queue = selected_display.split()[0]` → 赋 `user_selected_queue`/`queue_var` → `log_terminal`（**原始无 core 映射**）
- `refresh_lsf_queues`（原 line 1563）：后台 bqueues 轮询，重填 queue_combo，`blockSignals(True)`→clear→addItems→`setCurrentText(new_selection)`→`blockSignals(False)`（**原始未重应用策略**）

## 资产合成（B-synthesized 忠实裁剪）
- 资产 `runsim_control.py`：保留真实类名/方法名/属性名/信号槽连接/blockSignals 流程/初始值，裁剪到自包含可运行（用 Qt-like stand-in 类替代 PyQt5，使 py_compile + 方法体 exec 无需 PyQt5 安装）。`on_queue_selected` 为原始无映射版，`refresh_lsf_queues` 为原始未重应用版。
- task_brief.md：合成需求（融合 U#2~U#5：fqueue2h/fqueue3_ams2→1，else→6，refresh 重应用，可手动改大，不破坏既有行为）+ 交付接口（outputs/submit.zip 顶层 runsim_control.py）。
- hidden B：check.py 用隐藏 decoy 队列名（fqueue4h / fqueue9zz / fqueue2h_alt，不在资产 lsf_queues 里）验证泛化 else→6 规则，反硬编码。

## check.py 设计（k=20）
AST 提取候选 `on_queue_selected` 方法源 → exec 方法体于 mock（_CoreRecorder 记录 setValue / _MockSelf 提供 user_selected_queue/queue_var/log_terminal），逐队列验证 core 值；subprocess 真跑 py_compile；refresh_lsf_queues 源级验证 on_queue_selected 调用在 blockSignals(False) 之后；3 seed 随机扫；负样本 4 个（stub/always1/core-deleted/refresh-missing）全 FAIL。
