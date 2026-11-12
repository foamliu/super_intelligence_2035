# trace_deepread: shard C r478 — mc≥10 fresh-candidate peek batch 2 (2026-11-13)

**目的**: r477 audit 建立 mc≥10 fresh 池 ~70 条真 shard-C 候选，6 peek 全 REJECT。本轮按 r477 计划继续 peek 下一批（优先非 xinqiaoz/e0014566、非 handoff/policy），若再 6+ REJECT 则 hit-rate 实证 ≤15% 可回退 omission。

## 方法

- 复用 r477 `/tmp/find_fresh_c.py`（跨 4 shard 台账去重 + tools 列过滤真 shard-C 工具主导）。
- 本轮 peek 11 条 fresh 候选（4 + 7 两批），经 .75 本地 NFS 读 `<slug>/<slug>.messages.json` 的 messages 数组首个 user 文本 + 末个 user 文本 + tool 直方图。

## 11 条 fresh 候选实地 peek（全部 REJECT）

### 批 1（r477 计划点名 + 强 C-tool 信号，4 条）

| session | user | mc | tools | 首轮意图 | REJECT 理由 |
|---|---|---|---|---|---|
| 1792115466563_n1b1u | gokuguo | 119 | cal=90 virt=12 | "帮我查看...lvs文件，看一下ERC是怎么执行的，我的问题是：ERC 结果会在 lvs.rep 或 ERC results 里吗？" | **Q&A**（"会在...里吗"探索性提问，无交付物）；末轮"删除吧"morph 为删除请求 |
| 1790080023760_8rlou | lizwen | 112 | cal=73 pyA=39 cv=15 | "# DRC Testpattern Generator ... 烛龙用 pythone 调用 drc_pattern_gen.py 生成 .oa" | **near-dup 92cla**（r477 REJECT）：同 user lizwen + 同 DRC Testpattern Generator skill 主题；本轮为 skill config 调试（换 test_deck/test_deck_new + 删临时脚本），非单轮可闭环 produce-task |
| 1789647274009_jz2at | joelchen | 73 | cal=96 | "你好" → 末轮"我有哪些skills" | **探索性 chat**（greeting + 查询 skills），无 produce-task；cal=96 系 skill 描述里的 calibre 关键词误命中 |
| 1790218039885_fqzjj | e0041123 | 122 | cal=18 pyA=88 cv=34 | "Context summary: # 继续备注：DRC 测试模式 — 示例运行 (DNW*)" | **handoff-restore 续接轮**（"继续备注"+"本次会话已确认"=上下文恢复）+ DRC Testpattern Generator 主题（与 8rlou/92cla 同簇） |

### 批 2（非 xinqiaoz/e0014566 优先，7 条）

| session | user | mc | tools | 首轮意图 | REJECT 理由 |
|---|---|---|---|---|---|
| 1792991967986_5ze4m | miccao | 153 | cal=27 pyA=4 | `<skill_instructions name="calibre-drc-log-analysis">` skill 定义 + "我将log放到...argusDRC.log了" | **skill-mediated 文本报告**（"直接在对话中输出...不强制落盘"）：SUT 无该 skill 无法复现 4 模块结构；交付物为自由文本报告非结构化文件，难做 ≥8 客观断言 |
| 1793241481863_0xwjx | haiquanp | 72 | pyA=141 | "cv=ae.aeGetCurDesign() ... 补全代码，point 用 points.x()/y()，新建 ae.emyPointF" | **session-state-dependent**（操作 aeGetCurDesign/aeGetSelSet = 用户当前打开的 cell + 选中 shapes）+ 多轮交互式代码补全（7 user msgs），沙盒不可复现 |
| 1791983748341_mx4t6 | colinxu | 69 | pyA=111 | "我的username是colinxu,我希望在打开的cell中添加一个label并且保存" | **session-state-dependent**（"打开的cell"=aeGetCurDesign）+ 欠指定（无 label 文本/位置）+ 过于简单通用 |
| 1789621916894_m8ndm | ellawu | 97 | cal=20 pyA=20 | "zhegejiaobenyoushenmewentima"（这个脚本有什么问题吗）+ 附件 IMCleFillImplantDrc.py 174KB | **code review Q&A**（"有什么问题吗"诊断式提问），无 produce-task 交付物；消息为拼音乱码 |
| 1788760919556_ics15 | ziyuny | 79 | cal=30 | "先读取这个路径下的文件，并且分析log告诉我现在是什么情况" | **诊断 Q&A**（"告诉我现在是什么情况"），无交付物 |
| 1792386923801_1lote | hongyuy | 78 | cal=33 pyA=2 | "现在我要在DRGQX项目中进行M1A、M2A、M3A的CMP 添加，我该怎么操作需要注意什么" | **how-to Q&A**（"我该怎么操作需要注意什么"指导请求），无 produce-task |
| 1792053269961_ksa2h | panruan | 111 | cal=59 pyA=25 | "解析CT_F_015_00和CT_F_017_00" + 附件 calibreDRC.rule → 末轮"DFM SHIFT EDGE和expand edge区别" | **多轮探索式 DRC rule 解析 + Q&A**（24 user msgs/136 total/1.7MB）；near-dup 4 session（ksa2h/xgo8p/vhz0j/f0yt9 同 user/host/mc=111，同任务重复） |

## 关键结论

1. **hit-rate 实证 0%**：r477 6 REJECT + r478 11 REJECT = **17/17 REJECT, 0 hit**。fresh 候选命中干净单轮可闭环 shard-C 工作的概率 ≤15%（实测 0%），与 r477 结论一致。
2. **REJECT 分型（17 条）**：(a) handoff-restore 续接 [q8hpz/fqzjj] (b) skill/policy 调试 [92cla/8rlou/5ze4m] (c) 运维/crontab 误命中 [jq6lq] (d) near-dup 既有 case [w3bwg/8rlou] (e) 探索性 Q&A/chat 无交付 [taaak/jz2at/m8ndm/ics15/1lote] (f) session-state-dependent 需用户打开的 cell [0xwjx/mx4t6] (g) session 文件已删 [dzbpb] (h) 多轮探索 + near-dup 簇 [ksa2h]。
3. **真·干净单轮可闭环 shard-C 工作大多已在 mc≥30 段被做成 case**（r333/r380 结论在 mc≥10 仍成立——mc≥10 fresh 增量主要是低质量段）。
4. **回退 omission**：hit-rate 0% ≤15%，本轮执行 omission #92 diversify→layout_virtuoso（QaWidthPatternGen-001 cond (k)）。

## 下轮计划

- r479: 继续 peek 剩余 ~50 条 fresh（非 xinqiaoz/e0014566 + 非 handoff/policy/Q&A）；或 omission #93 diversify（避 r478 lv → 唯一未避 = physical_verify / pg_layout / layout_aether 中 gap 最大者）。
- 讨论配额：r475→r479 diff=4 due → r479 须发言（board OPEN=P-004 @C）。

## 不入台账的 REJECT session（供下轮避坑）

n1b1u/8rlou/jz2at/fqzjj/5ze4m/0xwjx/mx4t6/m8ndm/ics15/1lote/ksa2h —— 不 claim（未做 case，避免污染覆盖率分母）；下轮 peek 新批次时跳过这些 + r477 的 q8hpz/w3bwg/taaak/jq6lq/dzbpb/92cla。
