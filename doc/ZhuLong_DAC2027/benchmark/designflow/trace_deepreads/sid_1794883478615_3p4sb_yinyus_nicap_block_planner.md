# Deep-read: sid_1794883478615_3p4sb (yinyus @ hfeg0plg67, mc=460)

> r788 deep-read · shard C · domain 修正：**layout_aether**（ledger r786 标 physical_verify 误，实际是 Aether schematic/symbol cellview 批量建实例+连线）

## 1. Trace 定位
- session: `1794883478615_3p4sb.messages.json` @ `/home/yinyus/.cline/data/sessions/` on hfeg0plg67
- 1.31MB, 359 msgs (164 user / 173 assistant), 10 real `<user_input mode="act">`
- 工具分布：editor×50, run_approved_command×51, read_files×34, list_allowed_files×23, search_apis×9, skills×2
- **0 个 write_to_file/create_file**（所有写盘经 editor + run_approved_command）

## 2. 真实任务（用户原话摘录）
- U#1：注入 `nicap-block-create` skill_instructions，要求按 CSV 批量从模板 cell 生成多个副本单元摆进新建 schematic cell
- U#2：「无误 直接建立verify cell」
- U#3：「verify的bloc放置存在问题 要至上而下防止 你放反了」← **关键纠错：block 摆放方向必须从上到下（y 递减）**
- U#4-U#11：迭代调整（symbol 不存在检查、表头严格匹配、删除 verify cell、命名规则等）
- U#12（末轮）：「在强化一条规则 在建立前 一定要在建立前！ 检查我给的cellname 的symbol是否存在 而不所建cell之后才检查到没有 避免建立残缺文件造成干扰」← **核心硬规则：symbol 存在性检查必须在 dbNewCellView 之前**

## 3. 真实交付（trace-end-gold · 已确认磁盘存在）
- 主脚本：`/home/yinyus/.cline/skills/nicapblock-create/scripts/nicap_block_create.py`（8634 字节，已 scp 验证）
- SKILL.md：同目录（18325 字节，version 2.0.0，含完整 5 步工作流 + 重建骨架 + 9 陷阱表）
- README.md：4971 字节
- 示例 CSV：`example_data.csv`（9 行，I2_Number 1-9，3 block）
- 助手末轮 @A#358 自报流程顺序：「parse_args → 读模板实例 → 读模板 wires → 读 CSV+表头校验 → Cell symbol view 检查(第108-136行) ✅ 在 dbNewCellView 之前 → block 分组+摆放 → dbNewCellView → 建实例 → 建 wire → 保存」= trace-end-gold 成立

## 4. 离线可验核心识别
脚本分两段：
- **规划段（纯 stdlib，可离线验）**：argparse 参数 → 读 CSV + 表头严格校验（TPL_HEADER 7 列精确匹配，不匹配打印 missing/extra + exit 1）→ 收集 I0/I1/I2 唯一 (lib,cell) → symbol 存在性检查（发生在 dbNewCellView 之前，缺失则打印 missing_symbol + exit 1，不留残缺 cell）→ 按 (I0_lib,I0_cell,I1_lib,I1_cell) 归 block → 网格摆放数学（origin=(2,-1), spx=3, srow=3, sblock=7, per_row=10；**y 只减不增**从上到下；block 间 cur_base_y -= bot*srow - sblock）→ 实例命名 `I_<cell>_<series>`（cell_series 全局按 cellname 计数）+ I2 向量后缀 `<n:0>`（n=I2_Number-1，==1 无后缀）→ wire 平移 (ux,uy) → DRY-RUN vs --save
- **执行段（需 Aether/pyAether，SUT 不可达）**：dbOpenCV 读模板 slots/wires、dbNewCellView、dbCrtInst、dbCrtSchWire、emyDesignSave

## 5. 关键 SVRF/数学发现
- **y 方向约定**（U#3 纠错的核心）：origin 为布局顶部参考，y 大=上、y 小=下；换行/换 block 一律 y 递减。msg#170 早期版本 block1 在 y=+7/+14（向上=错），msg#182 修正为 y=-7/-14（向下=对）
- **series 全局计数**：vss 在 block0 作 I1（series 0,1,2）、block1 作 I1（3,4,5）、block2 作 I0（6,7,8）→ 同 cellname "vss" 跨 block 跨 slot 连续计数到 I_vss_8
- **I2_Number 后缀**：==1 无后缀；>1 加 `<N-1:0>`（如 Number=4 → `<3:0>`），后缀加在完整名 `I_<cell>_<series>` 之后
- **symbol 严格只查 symbol view**（不 fallback schematic/layout），因 dbCrtInst 用 symbol 视图

## 6. Reframe 方案（design_flow · L1 · 档 B）
- 真实脚本规划段抽成纯 stdlib `nicap_block_planner.py`，模板 slots/wires 预提取为 `template_meta.json`（SUT 无 Aether 读不到模板，故预提取）
- symbol 存在性检查改读预置 `symbol_registry.json`（list of [lib,cell] 有 symbol view 的对）
- 输入：params.json + template_meta.json + rows.csv + symbol_registry.json → 输出 plan.json（header_valid/missing_symbol/blocks/instances 带 abs 坐标+名字/wires/top_to_bottom 标志）
- 隐藏 B（anti-hardcode）：不同 template/CSV/params，全 valid → 必须 produce 与 A 不同的 plan
- 隐藏 C：registry 缺一个 cell → missing_symbol 非空 + instances=[]（ordering 不变量：symbol 检查在 create 之前，缺失则不建）
- 隐藏 D：bad-header CSV → header_valid=false + missing/extra 列报告 + instances=[]
- k_check=17（a-q）：zip/compile/A-plan-deep-compare/top-to-bottom/wires/B-anti-hardcode-deep-compare/C-missing-symbol-ordering/D-bad-header/determinism/4-negatives-regression

## 7. 判定
- **采用**，case_id = `EDA-Eval-DesignFlow-NicapBlockPlanner-001`，domain=layout_aether
- r786 标 "fresh mid-mc C candidate" 正确；r786 未深读，r788 深读确认 trace-end-gold 成立 + 离线可验核心清晰
