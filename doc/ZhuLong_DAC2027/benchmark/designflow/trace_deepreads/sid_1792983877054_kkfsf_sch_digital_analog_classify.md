# 深读笔记 — sid 1792983877054_kkfsf (jcgu @ hfeg0pin003 / 10.129.32.236)

- **trace**: `/home/jcgu/.cline/data/sessions/1792983877054_kkfsf/1792983877054_kkfsf.messages.json`，142 msgs，679KB，mc=242，model=deepseek-v4-flash
- **tools**: 251 pyAether · 144 schematic · 84 dbGet · 67 "lang":"pyAether" · 32 cellview · 26 netlist · 2 calibre
- **domain**: layout_aether（Aether pyAether schematic cellview 器件枚举与数字/模拟分类）

## 用户轮（逐字 USER#0-8）
- #0「能获取已经打开的aether吗」(探索性)
- #1「在ztest library下面创建一个新cell，cell name是test_ai, view name是layout」(layout 创建)
- #2「用户名是jcgu，在GUI内运行」
- #3「你是怎么判断是在哪个aether GUI上执行命令的」(追问)
- #4「删除ztest library下test_ai这个cell」(删除)
- #5「如果我在当前terminal启动两个项目的aether GUI界面…沙箱会访问哪个项目」(沙箱路径)
- #6「如何查看沙箱的 cds.lib 配置指向哪个物理路径」
- **#7「请分析一下ztest/AF_AryDecCtrl这个cell的schematic是数字电路还是模拟电路」** ← A-档合格 seed（纯意图，无根因/无方案）
- **#8「请分析一下ztest/AG_Bandgap这个cell的schematic是数字电路还是模拟电路」** ← A-档合格 seed

## 真实工具链（msg 103-141）
`dbOpenCV(lib=ztest, cell=<cell>, view=schematic)` → `aeDesignIsSchematic(design)` → `design.instCount/netCount/terminalCount` → `design.instances` → 逐 `inst.libName/cellName/viewName/name` 统计 master。
- 踩坑：`aeDesignIsSchematic()` 缺 cv 参数；`emyDesignGetBlock` 不存在；`design.getBlock()` 不存在；最终用 `design.instances` + `inst.libName/cellName` 成功。
- RAG search_apis × 多轮（emyFigGroupGetAllLevelFigs / emyRefGetMasterName / emyBlock / dbOpenCV）。

## 真实产物（gold）
### AF_AryDecCtrl（msg 130/133）→ 纯数字
- 50 insts / 44 nets / 15 terminals（9 in PIN0-8、6 out PIN9-14）
- 30 stdcells_ac：invLx1(8)/invLx2(1)/invLx3(4)/invLx4(2)/invLx6(1)/nand2Lx1(1)/nand3Lx1(2)/nand3Lx2(1)/nor2Lx1(4)/oai21Lx1(1)/dlyg6of8Ls2(1)/dlyg8of8Ls2(1)/dlynrc1500ps(2)/dlynrc2000ps(1)
- 5 电源/标注：TECHLIB/switch(2)、TECHLIB/vcc(2)、TECHLIB/noteSymbol(1)
- 判据：全 stdcell 数字门 + 延迟单元，无 BJT/MOS/电阻/运放 → **纯数字**

### AG_Bandgap（msg 136/141）→ 模拟（混合）
- 顶层 23 insts / 34 nets / 19 terminals（10 in、7 io、2 out）+ 2 probeI + 2 子模块
- ① AG_BandgapCore（drvqa_cmos_analog，138 insts）：4 bjtpnp10a36(PNP 带隙核心) + 21 ntn_m + 31 ptk/ptk_lv + 5 ptn/ptn_lv + 9 ntk/ntk_lv + 1 DPWDNW + 6 probeI + 23 switch(修调) → **纯模拟核心**
- ② AG_BandgapCtrl（69 insts）：26 inv(Lx/Vx) + 7 nand + 5 AG_lvlshftRSTL_Vcc2Vdd1(电平移位) → **数字控制**
- 判据：BJT + 大量 MOS + 电阻 + 修调开关阵列 → **模拟（带数字控制子模块的混合信号）**

## 本轮 case 设计（B-档 synthesized, L1-boundary, layout_aether）
**case_id**: EDA-Eval-DesignFlow-SchDigitalAnalogClassify-001
**任务**: 给 SUT 真实 Aether schematic inspection dump（bundle_A.json = AF_AryDecCtrl 的 master 枚举），写单文件 `sch_digital_analog_classify.py`，按器件类型（数字 stdcell inv/nand/nor/dff/dly vs 模拟 bjt/ptk/ntn/ntk/DPWDNW/probeI/lvlshift）分类 DIGITAL/ANALOG/MIXED + 结构化 markdown 报告 + stdout 摘要；判分在隐藏 B1(AG_Bandgap->ANALOG)、B2(DF_Div2Ctrl->DIGITAL)、B3(malformed->exit1) 真跑。
**为何 B-档**：A-档 faithful 需真连 Aether+drcoa/ztest 库，SUT 沙盒无该库→不可复现；故把真实 master 枚举 dump 成 JSON bundle，SUT 结构化分类，与 r146/r148 同口径。
**资产**：A=AF_AryDecCtrl bundle(50 insts/30 stdcells)；B1=AG_Bandgap bundle(顶层+2 子模块，base64 内嵌 check.py)；B2=DF_Div2Ctrl bundle(42 insts/dff/nand/inv，DIGITAL)；B3=malformed。
**reference**: sch_digital_analog_classify_ref.py（正则分类 + 递归 sub_modules）。
**判分 14 条断言 (a-n)**：见 jsonl metadata.test_rationale。k_rationale=k_check=14>=8 GATE ✓。
**自验**：ref PASS 14/14 + negative_selftest NEG_RC=0（5 fake distinct FAIL: fake_empty->c / fake_print_expected->h / fake_core_deleted->e / naive_always_digital->d / naive_libonly->e）+ §4.9 三假全 FAIL。
**leakage 隔离**：SUT 沙箱只含 assets（bundle_A.json/prompt/task_brief）；check.py/ref/jsonl/test 不进沙箱；B1/B2/B3 base64 内嵌 check.py。
