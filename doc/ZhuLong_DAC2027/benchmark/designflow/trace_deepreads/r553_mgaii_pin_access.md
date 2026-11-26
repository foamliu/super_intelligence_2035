# r553 deep-read · mgaii (e0047434 @ hfeg0pnd001, mc=113)

**trace**: 1793179751886_mgaii / e0047434 / hfeg0pnd001 / mc=113
**keywords**: .cdl:440;.gds:303;virtuoso:39;transistor:28;lvs:27;pex:24;cellview:22
**domain**: physical_verify (std-cell layout pin-accessibility scoring from CDL+GDS)

## 用户意图演进 (8 user turns, 170 msgs, 1.19MB)
- U#1: "这个路径下有些脚本...从pin accessibility角度评价的；请分析相关脚本，告诉我哪个脚本定义了这样的评价，评价指标是什么，如何使用" = analyze-existing Q&A
- U#2-5: pin 概念澄清 Q&A (internal net pin vs external pin accessibility)
- **U#6/U#8: "请帮我写这个脚本" = produce-task author-new-script** —— 根据 check_access.il 的 pin accessibility 得分逻辑，重新用 python3 写一个相同逻辑、同时读 CDL+GDS（不需 OA）计算 pin accessibility 的脚本。提需求未给根因/方案 → A档合格。
- assistant: read_files check_access.il(680行)+config_access.il+log → editor 分析报告 → read CDL(AN2D1/DFNQD1) → editor gds_pin_probe.py/gds_probe2/gds_probe3/gds_pin_access.py(迭代 6 版) → run python-runner 测 AN2D1/DFNQD1/AN2D2/XOR4D4 → --all 全库 464 cell → editor pin_accessibility评价规则说明.md

## 交付物 (真产物)
- `zl_output/pin_access_score/gds_pin_access.py` (662行): 读 CDL(.SUBCKT ports)+GDS(二进制 struct 解析), 识别 M1 pin(master label==CDL port)/CM1 cut(CM1A/CM1B)/M2(M2_A/M2_B)/V1, 逐 pin 计算 Type/Left/Right/Total/Weighted/Flag
- `pin_accessibility评价规则说明.md` (121行): 评价规则人话说明

## 核心算法 (check_access.il 逻辑, Python 重实现)
**配置** (config_access.il): TOL=0.001; M1 grid yBase=0.046 yPitch=0.028 lPitch=0.204 mMax=4; V0D grid centerBase=0.0255 pitch=0.051; V0G centerBase=0.051; CM1 width=0.018; M2 width=0.031; SKIP_PINS=VPP/VSS/VDD/VBB

**流程**:
1. parse_cdl: .SUBCKT 取 ports
2. parse_gds: 二进制 GDS → structs/instances(sref+transform+bbox)
3. classify_instances: M1 pin(instance master label∈signal ports, cx=(llx+urx)/2,cy=(lly+ury)/2); CM1 cut(CM1A/CM1B, cx=llx+CM1_WIDTH/2); M2(M2_A/M2_B, cx=llx+M2_WIDTH/2); V1(sname==V1, center)
4. CM1 cut records: 按 M1 行 grid (l* lPitch + yBase + m* yPitch) 展开, CM1A 取 m%2==1, CM1B 取 m%2==0, 落在 cut bbox y-range 内 → (cy,cx)
5. edge V0D: leftmost/rightmost V0D in cell bbox → 从所有 left/right 列表删除
6. per-pin: classify x → V0D/V0G/OFF-GRID; 左右搜索步长 half_pitch=0.0255, 碰 CM1 cut 停, V0D 位且未被 M2/V1 挡 → 记可打孔位, V0G 跳过
7. share count: pos_pin_list 按 x-index(v0d_pos_to_index) 聚合所有 pin 的 left/right+self 位 → share_count
8. pos_weight: 1→1.0, 2→0.8, 3→0.4, 4→0.3, ≥5→0.2
9. Total = left+right+(1 if V0D self not blocked); Weighted = sum pos_weight(share) over self+left+right 位
10. Flag: total==1 & w<=1.0 → LOW_BOTH; total==1 & w>1.0 → LOW_RAW; total!=1 & w<=1.0 → LOW_WGT

**注**: LOW_RAW 在此模型不可达 (total==1 ⇒ 仅 1 位 ⇒ weighted≤1.0)，实测 464 cell summary 无 LOW_RAW。

## case 建模 (B档 mock-behavioral, 承 r539-r552 族)
**PinAccessScore-001**: 把"live GDS 二进制解析+pin accessibility 评分"重构为纯 Python JSON layout deck fixture(核心 grid 分类/左右 V0D 搜索+CM1 cut 停+M2/V1 挡+edge 删除+share 加权+flag 分类 算法不变)。
- 可见 A: check_access.il.txt(SKILL 源节选)+cell_A.cdl+layout_A.json+input_spec.json+task_brief.md
- hidden B: cell_B.cdl+layout_B.json+input_spec_B.json; B2: 不同 geometry
- 交付 submit.zip 含 pin_access.py(读 cdl+layout json, 写 pin_access_result.json)
- k_check=17(a-q): 结构2 + 运行1 + per-pin 字段6(type/left/right/total/weighted/flag) + summary1 + 行为3(OFF-GRID total0/ cut right0/ M2 excl) + anti-hardcode B2 + determinism
- oracle: check.py 内嵌独立 _oracle(deck) 重实现评分核心, candidate==oracle 逐字段
