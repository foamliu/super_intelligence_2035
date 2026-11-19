# trace_deepread · 7y204 · PPT 项目汇报生成

- **session**: `1789709017553_7y204` (yzwang @ 10.129.2.10 / hfeg0plg16, mc=23)
- **agent**: lead, 20 msgs / 83KB, 2026-09-18
- **keywords**: pdk:243;drc:87;lvs:59;calibre:56;.gds:4;techfile:2;icfb:2;.lef:2
- **domain**: physical_verify (PDK DRC/LVS QA workspace → 报告生成)

## 用户意图（逐轮）
- U#0 `<user_input mode="act">你可以写一个PPT吗？</user_input>` —— 提出需求
- U#2 `产品介绍/项目汇报` —— 选 PPT 主题（ask_question 选项之一）
- U#4 `{error: Raw shell tool run_commands is disabled}` —— 环境限制反馈
- U#6 policy engine 状态：`profileIds=["hello_world"]`，shell 受限
- U#7 `list_allowed_files /home/pdk/yzwang` 返回工作区目录树：`00_DRC_QA_Patterns / 01_libs / 02_runset / 03_package / 04_GDS / 05_truthtable_QA / 08_scout / 09_scripts / calibreANT.rule`
- U#9/11/13/15/17/19 editor insert 结果（脚本分段写入 `create_ppt.py`）

## 助手真实做的事
1. U#0 后 ask_question 选主题 → U#2 用户选「产品介绍/项目汇报」
2. 尝试 `run_commands` 跑 `python3 -c "import pptx"` → 被策略拦截
3. `get_agent_policy_status` + `list_allowed_files /home/pdk/yzwang` 探明：PDK 验证工作区（DRC/LVS rule + QA patterns + GDS + truthtable QA），shell 禁用，仅 hello_world profile
4. 决定写一个**用户本地可运行的 python-pptx 脚本** `create_ppt.py`，基于看到的 PDK 工作区结构生成「项目汇报」PPT
5. 用 `editor` 分 4 段写入 `create_ppt.py`（168 行，分段因 editor 6000 字符上限）：
   - 头部：颜色常量 + 辅助函数（add_background/add_shape/add_textbox/add_title_bar/add_bullet_list）
   - 第1页封面：「PDK 验证与质量保障 / 项目汇报 / 汇报人：yzwang / 日期：2026年9月」
   - 第2页目录：6 章（项目背景与目标 / 技术方案与流程 / DRC/LVS 验证体系 / 关键成果与指标 / 问题与改进计划 / 总结与展望）
   - 第3页项目背景与目标：左侧项目背景 bullets + 右侧项目目标 bullets（DRC/LVS 流程、覆盖率>=95%、版本管理）
   - 后续页（trace 在第3页后中断，但目录承诺了 6 章）

## 关键产物
- `create_ppt.py`（7455 字节 / 168 行，scp 实取）—— 静态 python-pptx 脚本，硬编码 3 页（封面/目录/背景目标），含辅助函数库

## 任务形态判定（2026-11-15 §二 reaudit）
- 用户意图 = 「写一个 PPT 项目汇报生成脚本」 = **explain / report-generation 类**
- 旧规则下此类判为 weak / 不可造 → **2026-11-15 reaudit 全部恢复为可造** → 合法 user 意图 ✓
- 真实 trace 中 shell 禁用、python-pptx 未装 → 助手只能交付**脚本源码**（非 .pptx 文件）—— 用户拿回本地跑

## 档 B reframe 理由
- A 档 gold = 静态 `create_ppt.py`（硬编码 3 页内容）—— 三个问题：
  1. **静态硬编码 → 无隐藏 B**：脚本无输入参数，A/B 无法在规模/取值/结构上不同 → 违反 §4.1
  2. **判分无牙**：只能查脚本源码字面，print-only stub 打印同形源码即 PASS → 违反 §4.9
  3. **python-pptx 不可装**：沙盒 pip 坏（libffi.so.5 缺），无法动态跑脚本生成 .pptx 验证
- **reframe**：抽离助手真实算法核心「读工作区清单 → 综合结构化 slide 内容（封面/目录/各章/总结）」为**参数化 PPT 生成器** `create_ppt.py <manifest.json> <output.pptx>`，读取工作区清单 JSON（项目名/汇报人/章节/目录树）→ 调用 python-pptx 生成完整 6+ 页 .pptx
- **判分牙**：check.py 提供**桩 pptx 包**（record-only，不依赖真实 python-pptx），exec SUT 脚本，验证 recorded structure（slide 数 ≥6 / 封面含项目名 / 目录页列章节 / 内容页引用工作区目录名 / save 调用 / 反硬编码 A / 确定性 / 缺参退出）
- hidden B = 合成数字实现流程工作区清单（与 A 的 PDK DRC/LVS 工作区结构性差异：项目名/汇报人/章节/目录树全不同）

## 隐藏 B anti-hardcode 设计
- A: project_name="PDK 验证与质量保障" / presenter="yzwang" / dirs=[00_DRC_QA_Patterns, 01_libs, 02_runset, 03_package, 04_GDS, 05_truthtable_QA, 08_scout, 09_scripts]
- B: project_name="数字实现流程质量审计" / presenter="ligong" / dirs=[00_rtl, 01_synth, 02_sim, 03_sta, 04_pnr, 05_signoff, 09_scripts] —— 工艺域反转（PDK 物理 → 数字实现），章节反转，目录名全不同
