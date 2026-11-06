# trace_deepread: 1793164782733_wp528 — Calibre SVRF/DRC density-rule training (laryu)

- **trace**: `1793164782733_wp528` (laryu @ hfeg0pkn001, mc=255, 304 msgs, 1.25MB; model glm-5.2; cwd `/home/laryu/`; status interactive)
- **跨 shard 查重**: 选题前对 4 shard ledger grep `1793164782733_wp528` → 全 fresh，无碰撞。
- **真实任务**: laryu 是 DRGQA/PDK QA 学员，在 Calibre SVRF/DRC 训练中逐条粘贴规则请助手解释，并实际 run DRC 调试脚本。39 个用户文本轮，主题分布：
  - U#1-2: **DRC density rule** `POLY_DENORFILL_DenMin_006_03`（PGZ poly 密度 min 检查，window 60x60um step 30um，except BJT region，含 DENSITY op / AREA ratio / RDB / NOT INTERACT exception）→ 本 case 抽取源
  - U#3-4: BORD chip boundary 规则
  - U#5: `area_check { NET AREA RATIO poly gate > 50 }`
  - U#6-7: VIRTUAL CONNECT COLON / NET "vcc!"
  - U#8-24: `getPower.rule` power net extraction（vcc/vss 跨 M1-M5 + V1-V4 via，调试 EXT2/EXT3 connectivity 错误，输出完整 power net 图形）
  - U#25: SVRF Expand Edge 章节
  - U#26-39: `and3GSx1` layout — PG_PCH/PG_NCH 两侧缩小 0.01 + PG_PTAP/PG_NTAP 紧贴 + flatten 输出 GDS + GROW/SHRINK/SIZE + text_drawing 230 0 输出 + DRC MAP TEXT
- **本 case 抽取**: U#1 的 **Calibre DRC density-rule structural parser** 离线确定性核心。density rule 与既有 SvrfRuleExplain-001（EXT spacing rule）结构不同：DENSITY op + WINDOW/STEP/BACKUP + AREA ratio + RDB + NOT INTERACT exception。
- **金标准**: 助手对 density rule 的结构化解释（rule_name / @ intent / [value] threshold / A1=A AND B 层赋值 / DENSITY op 参数 / [AREA()/AREA()] 比率 / RDB 输出 / NOT INTERACT 例外）。断言只对可机械验证的结构字段，不对措辞。
- **A/B**: A = 真实 POLY_DENORFILL_DenMin_006_03（6 layer_refs: PG/PERI_FOR_CMOS/BJT_PNP/BJT_NPN，threshold 0.187，op `<`，window 60/step 30，BACKUP+CORE）；隐藏 B = 构造的 M1_DENSITY_Core_012_01（M1/CORE_AREA/MIM_CAP/MIM_RES，threshold 0.295，op0 `>=` 无 BACKUP，op1 INVERSE，window 40/step 20）→ 不同层/不同算子/不同 window-step/不同 flag mix 杀硬编码。
- **判分 14 条 a–n**: a)zip单py+py_compile+禁pyAether/calibre/numpy b)--help exit0/无参exit!=0 c)隐藏B跑exit0+合法JSON含9键+density_ops非空 d)B rule_name e)B intent f)B threshold.value+kind g)B layer_assigns(B1/B2 expr) h)B density_ops(op0 operator>=/window40/step20/rule_tag/inputs/assigns B3; op1 operator</INVERSE flag/rdb) i)B area_ratios j)B rdb_outputs 顺序全 .rdb k)B exceptions NOT INTERACT l)B layer_refs=[CORE_AREA,M1,MIM_CAP,MIM_RES] m)跨输入守卫 A rule_name+threshold+与B结构不同(window/layer_refs)证非硬编码 n)确定性 B 两次 sha256 一致。
- **自验**: ref PASS 14/14；5 negative(empty/print-expected/core-deleted/hardcode-B/naive-onegate)全 FAIL NEG_RC=5/5（hardcode-B/print-expected→m 跨输入守卫挡，naive→c density_ops 空 挡，core-deleted→l layer_refs 挡，empty→b 挡）；§4.9 (a)(b)(c) 三假全 FAIL；check.py 自包含（A/B 规则内嵌字面量无路径依赖）；泄漏隔离 SUT wd 仅 submit.zip+density_rule_A.txt+task_brief 无 reference/check.py/jsonl/hidden/B。
- **断言闸门**: k_rationale=k_check=14>=8 GATE PASS ✓。
