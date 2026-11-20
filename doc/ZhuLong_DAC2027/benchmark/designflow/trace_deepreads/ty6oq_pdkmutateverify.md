# trace_deepread: 1793872363785_ty6oq (chengleiy @ hfeg0pkn005, mc=90)

**session 性质**: PDK QA tooling 迭代。agent 在 chengleiy 的 `/home/chengleiy/scripts/pdk_qa_tools/` 上迭代 file/model/deck/device/vttf compare 模块 + pdk_compare.py 主流程, 用真实 SMIC28 PDK 验证 QA 脚本准确性。innovus=220 来自 `/home/pdk/chengleiy/e_innovus/` 路径提及, 非 PNR 工具实跑。真跑工具 = python-runner 跑纯 Python 脚本(pdk_mutate/verify/diagnose/compare_content), 无 EDA 二进制。

**对话流** (164 msgs, 100 user/64 asst, agent=lead):
- USER#0: 整理 pcell + QA 脚本, 看有没有能用的 (`/home/pdk/chengleiy/e_innovus/from_out/linux/PCELL` + scripts)
- USER#33: 三任务 (form pcell skill from 手册; merge QA scripts 进我的 scripts dir 防覆写; virtuoso 启动需特殊命令, 查 python-virtuoso bridge)
- USER#75: 以前的脚本和现在导入的脚本有同名文件吗? → agent compare_content.py md5 全树对比 → 0 内容相同, 3 路径同名内容不同(FileIO/FolderHandle/pdkRe, pdkRe 静默行为变化最危险)
- USER#81 (A档选轮): 用真实 PDK 验证 QA 脚本准确性(删器件/加器件/改值)
- idx82-100: agent 探 PDK 结构(smic28hkmg TECHLIB + models/spectre + Calibre/DRC,LVS + 4469 文件), 读 5 compare 模块, 设计 6 项变异方案
- idx113-119: agent 写 pdk_mutate.py (硬链接复制 PDK + M1 删 npn/M2 加 dnd09_qatest/M3 删 dnd25 symbol/M4 改 display.drf/M5 改 spe.lib/M6 改 LVS deck LAYER MAP 10->11 + 记录 ground_truth.json)
- idx120-131: agent 写 pdk_verify.py 跑 pdk_compare → 10/11 检出 (M6 layer_changes 漏检, 同名 LAYER 多行字典覆盖粗粒度; 文件级 modified 兜底); pdk_diagnose.py 查根因; SKILL.md 陷阱 10/11/12 记录
- USER#132: 二进制文件不用对比是加密的 → agent 改 file/model/deck compare 跳过二进制内容对比(只保留存在性对比), 重跑 0 decode 错误, skipped=2534, 21.8s, 10/11 检出一致
- USER#150: 验证重跑确认
- USER#155: 提完整 pipeline (提器件→导 CDF→写 config→新旧平台 pattern→跑 LVL) → trace 末尾中断于 #163 (未达用户接受)

**A档选轮**: USER#81 (clean 需求, 无根因/无修复方案)。USER#132 disqualified (给根因「加密」+修复方向「不用对比」)。USER#155 trace 末尾中断不可作金标准。

**金标准**: idx113-119 真实 pdk_mutate.py + idx120-131 验证报告 (10/11 检出)。泛化为 generic pdk_mutate.py (读任意 PDK 树 schema: techlib+display.drf + cells/views + models/*.lib + Calibre/LVS/*.lvs)。

**case**: EDA-Eval-DesignFlow-PdkMutateVerify-001 (eda_other, A档, L2-static, 14 conds a-n)。资产 A = 迷你 SMIC28 PDK 重建 (50 文件)。hidden B = osm18rf 不同 PDK (36 文件, embedded in check.py)。
