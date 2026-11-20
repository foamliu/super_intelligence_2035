# 深读笔记：fdnle — SPEF/netlist mismatch 模块级定位分析

- **trace**: `1792743458736_fdnle.messages.json` (haoyut@hfeg0pkn003, 10.129.2.12, mc305, 751 msgs, 2.95MB)
- **扫描关键词**: analog:1285; netlist:992; verilog:289; cmos:129; **primetime:70**; waveview:50; aether:49; pyaether:35
- **工具计数**: 806 netlist + 3 pyAether + 3 cellview + 2 synthesis + 2 schematic + 2 calibre（primetime:70 在关键词层确认数字前端/时序内容，非纯模拟）

## 用户意图流（所有 user text 轮）

- **U#0** (context summary): 续接前会话 — 让我直接读 log 的真实内容,从样本中理解问题的本质,而不是统计。先看 log 的完整结构…
- **U#25**: 继续
- **U#57** ← **A档任务说明（逐字）**: 「需要你进行一些分析 看是哪一些模块的问题较多 并且尽可能的精准一点而不是共同的上层模块」**纯目标轮,未指出根因/方案 ✓**
- U#75: 你把这些能输出成一份 report…把这个清单也放在 report 中吗
- U#131/171/199/261: report 格式/pdf/打开方式（交付形态,非任务目标）
- U#263: 我们的 spef check release 如果我要将它结合成个 skill 我们需要怎么做
- U#271: 详细 config.sh 设计(PT_LOG/SPF_SRC/READ_PARASITICS_PATH/NL_PT/NL_SWITCH)— 给出方案,hint 非 A档
- U#317/319/357/363/407: skill 搬迁/路径/模板细节
- U#409/411/413: 清空分析工具重新开始(只清 spef analysis,保留 spef check)
- U#459: 不依靠工具固定规则…以错误所在位置相关…区域选择在不是很上层但又能很典型的区域内…再显示出问题是什么类型（设计指引,半目标）
- U#541/597/629/691/701: 模拟优先级后置/full hierarchy/不用 NF 表达成缺失/数量核对/排序+示例
- U#717: 5 万多个中模拟相关模块优先级不高单独放,剩下的按数量排,不同 bank 的例化 cell 算作一类,贴 full hierarchy 示例,数量前 5 再给主要问题分析（详细 spec）
- U#727: 把这次回答的模板/思考逻辑按 skill 写出来,触发条件=跑完 spef check 产生 log 或用户说"你帮我分析下 log"
- U#735: 换另外的项目可能问题完全不同,skill 要能满足更多未知情况

## 选轮判定
**U#57 = A档任务说明**（纯目标：按模块粒度精准定位问题集中的模块,不要共同上层）。其余 user 轮要么是交付形态（report/pdf）、要么已给出方案/详细 spec（U#271/717）、要么是续接/格式追问。

## assistant 工具链（U#57 → msg#74 金标准）

1. 写 `/home/haoyut/spef_analysis/module_map.py` — 每条问题网映射到归属 cell 类型（取最深父实例,去 `I_` 前缀 + 数字/数组后缀）
2. 跑 → 发现 P1/P2 把问题摊到大量内部重复阵列单元（R_RowRed 14944/RowRed2Unit 7936/T_CmFsLatchX6L 9902）,不是有用"模块"
3. 写 `p0_focus.py` — 聚焦 P0（SPEF_NOT_FOUND）,处理 `I` 叶实例噪声 + 重复阵列
4. 跑 → P0 集中在模拟 LDO 控制（AG_NewBLSA_VblenActLDOCtrl ≈970/AG_DigGen* ≈560）+ R_NcCtrl(160)
5. 写 `final_map.py` — 结合 ownership + name map,G0（真缺,leaf 0 次）vs G1（改名/层级）分拆,按模块分布
6. 跑（修打印 bug `tl[:,:60]` → `tl[:60]`）→ G0=181/G1=2737
7. **msg#74 金标准报告**：G0 181 按模块分布表（R_NcCtrl 32/R_trimEqOff 32/AG_DigGenCompLogic 16/D_BnkGTopBGRptPrcTop 16/BnkGTop_{BD,AC,GE,HF} 10×4=40/BCenterL+R 14+13=27/BCenterDQ 7/DMPad 4 等=181）

## 真实 log 格式（spef_check_release/logs/batch_*.log）

```
======================================================================
  Compare #<seq>  Net: <full_netpath>
======================================================================
  NL: 1 drives, 1 loads  |  SP: 1 drives, 1 loads
  ===========================================================
  NETLIST / SPEF / COMPARISON
  >> <MARKER> <<   (OK | NET NAME MISMATCH | HIERARCHY MISMATCH | SPEF_NOT_FOUND)
     Netlist: <path>
     SPEF   : <path>
======================================================================
  Done.
```
Net path 结构: `Ictop/I_Channel/I_BnkGTopX4_{Top,Bot}/I_BnkGTopX4_gut/I_BnkGTop_{GE,HF,AC,BD}/I_D_BankLogicx2L/I_T_CMAry_1/I_T_CmFsLatchX6L_o476/<net>`

## gold 方法论（haoyut spef_analysis_v2/analyze.py v4,泛化版）

1. parse_blocks: `^\s*Compare #(\d+)\s+Net:\s+(\S+)` + `>>\s*([^<]+?)\s*<<` markers
2. is_leaf_inst: `^I\d+`（I116/I14 等叶实例）
3. seg_to_cell: 剥 `I_` 前缀 + `(_?[A-Za-z]?\d+)+_?$` 尾部数字/数组后缀 → 功能 cell 名
4. **共同父层剥除**（泛化）: 计算所有问题网的最长共享前缀,跳过共享顶层 + 共同父段（用户要求"不是共同上层"）
5. **模拟滤除** is_analog: AG_/NEWBLSA_/VBL/LDO/REFGEN/REFLOGIC/TMSLP/ITEMP/VGCLAMP/DIGGEN/VREF/PLLBIAS/BIASGEN/XTLOSC
6. classify: SPEF_NOT_FOUND→NF | NET NAME MISMATCH+HIERARCHY MISMATCH→NM+HM | NM | HM
7. 按 deepest cell 聚合: total/NF/NM/HM/both/nf_pct/context/category/sample_path
8. categorize: >50% NF→missing | >80% NM→rename | >80% HM→hierarchy | >40% NM→rename+hierarchy | >10% NF→missing-mixed | else mixed
9. 排序: (-NF, -total)

## 本 case 合成（A档 faithful）

- **A（可见）**: `mismatch_log_A.txt` 180 块,真实 BnkGTop 层级（Ictop/I_Channel/I_BnkGTopX4_{Top,Bot}/I_BnkGTopX4_gut/I_BnkGTop_{GE,HF,AC,BD}/…）
- **隐藏 B**: `mismatch_log_B.txt` 220 块,DDR PHY 层级（DdrTop/DfiChan0/I_PhyTopX4_{A,B}/I_PhyPipe_gut/I_{DqCtrl8L_o32,DqsGateDeskew,WriteLevelCtrl,ReadCapture8L,CmdDeskew,ZqCalCtrl,PhyBistCtrl,DqDeskew4L,PhyTopStatus}/…）结构对立
- **隐藏 B'**: `mismatch_log_B_prime.txt` 200 块,SerDes 层级（SerDesTop/LaneGrp0/I_X4Top_{A,B}/I_X4Pipe_gut/I_{LanePcs4L,LanePma4L,TxDeskew,RxCdr,EqCtrl,PllCtrl,LaneBist,GearBox4L,LaneStatus}/…）交叉输入守卫
- **金标准脚本**: `spef_module_localize_ref.py`（analyze.py v4 泛化,去 A 专属硬编码 BnkGTopX4_gut,改为通用共同前缀剥除）
- **判分**: `check.py` 14 条独立断言 a-n,在隐藏 B+B' 上独立临时目录 subprocess 真跑候选

## 泄题隔离确认
SUT workdir 只放 prompt.txt + task_brief.md + mismatch_log_A.txt + hidden_manifest.json；check.py / reference/ / hidden/ / jsonl 不进 SUT 沙箱。
