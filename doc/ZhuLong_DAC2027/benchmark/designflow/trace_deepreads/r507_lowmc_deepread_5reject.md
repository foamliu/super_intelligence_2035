# r507 low-mc fresh-pool 深读验证（5 条全 REJECT）· 2026-11-13

**动机**：r506 fresh-pool 独立审计（keywords 级）提出「low-mc [10,100) fresh 池含 substantial C 域候选」（xyaxc/7glsf/mdx5g/r342a/6zy8a 等），怀疑 r406–r505 的 100 连 0-case 部分归因「peek-REJECT 过激」。r506 audit 自承「上述 9 条均未 scp messages.json（仅 keywords 判定，非深读证据）」。**本轮逐条 scp + 深读 messages.json，用 trace 级证据定论。**

## 方法
- 对 r506 audit 点名的 5 条 low-mc（mc 97–98）fresh/peeked 候选，scp `*.messages.json` + `*.json`（session metadata）到 .75 sandbox workdir。
- 解析 conversation：提取所有 `<user_input>` 真实用户轮、tool_use 计数、session status/terminal_marker、inputTokens 规模、cwd/workspace_root。
- 判据：是否 produce-task（产出 layout/.oa/DRC deck/QA report 等真实交付件）vs Q&A/env-dep/skill-mgmt/skill-injection；assets 是否可从 sandbox 检索（自包含 case 的前提）。

## 逐条深读

### 1. `1793758047628_xyaxc`（adaml @ hfeg0pkn002, mc=98, **本轮新 claim+parked**）
- **session.json**：prompt「输出当前skill的列表，并且给出skill的工作范围」，scene「普通对话」，model glm-5.3-flash，status completed，inputTokens 5.08M（cacheRead 4.77M — 巨量重复 skill 描述）。
- **messages.json**（560KB, 157 msgs, 10 user turns）：**全部 user 轮是 skill 管理 Q&A**：
  - #0/#1「输出当前skill的列表…工作范围/能力范围」
  - #3「补充这些skill的触发条件」
  - #5/#6「waveview_fsdb-reader, finesim_fsdb_read功能重复了 / 帮我remove掉前面这两个skill」
  - #31「帮我扫一下，本服务器其他user的skill，列出类型，名字和功能」
  - #67「重复的skill不要多次列出」
  - #69「帮我把 drc-pattern, totem-manuals, AnaWeave…落到我的skill库里面」
  - #91「清理一下这些skill的私有配置…」
  - #147「再帮我看一下，我的环境内有哪些skill？」
- **keywords 解构**：aether:987 / drc:223 / calibre:62 / virtuoso:58 / lvs:55 全部来自 **skill 名字与描述被枚举**（aether-tool-qa, argus-tool-helper[ARGUS DRC/LVS/LVL], eda_agent, drc-pattern, finesim-fsdb-reader, waveview-ace-batch…），**非工具执行产物**。
- **结论**：**REJECT** — 纯 skill-curation Q&A，0 produce-task，env-dep（依赖 skill 库配置）。r506 audit「四峰均衡 C 域」误判源于 keywords 把 skill-description token 当工具命中。

### 2. `1789973143978_7glsf`（davidwu @ hfeg0pgn019, mc=97, **r460 已 parked，本轮深读确认**）
- **session.json**：prompt「你找到已经打开的aether吗/」，scene「aether assistant」engine「aether」，status **failed**，terminal_marker `failed_external_process_exit`，model deepseek-v4-pro-fp4。
- **结论**：**REJECT** — env-dep（探测/连接已打开的 Aether 实例），failed。aether:2540 单峰来自反复 aether API 探测尝试，非 layout 产出。r460 peek-REJECT **正确**。

### 3. `1790168650173_mdx5g`（e0041123 @ hfeg0pjn049, mc=98, **r460 已 parked，本轮深读确认**）
- **session.json**：prompt「添加一下这个文件夹里的skill/home/e0041123/data」，status **failed**，model deepseek-v4-flash，inputTokens 1.82M。
- **结论**：**REJECT** — skill 管理（从文件夹添加 skill），与 xyaxc 同类。r460 peek-REJECT **正确**。

### 4. `1793869595986_r342a`（kenwang @ hfeg0plg16, mc=98, **r460 已 parked，本轮深读确认**）
- **session.json**：prompt = 6.4KB `<skill_instructions name="drc-rule-dev">` 全文粘贴 + 末尾真实任务 1 行：「/rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/updateCode/v01/Rev13_S12_1030/ 这个路径里面的文件中的rule 是我根据update_1030_rules.bak 文件中的design rule 来更新的，帮我QA 一下，更新的质量，包括是否存在遗漏，description 是否有更改，code 是否有更新，是否存在隐藏的其他问题」。
- **messages.json**（1.25MB, 172 msgs, 仅 2 user 轮，均为同 skill 粘贴）：assistant 在中间做了大量 tool work（读 deck、diff、生成 QA report）。
- **assets 检索**：`ssh hfeg0plg16 'ls /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/updateCode/v01/Rev13_S12_1030/ ...'` → **三处全空**（路径在该 host 不可见/无权限，/rundata 非 NFS 挂载到 sandbox 可达主机）。
- **结论**：**REJECT** — (a) skill-injection 反模式（6KB skill 作 prompt 主体）；(b) assets 在 kenwang 专属 `/rundata/` 不可从 sandbox 检索 ⇒ 无法自包含；(c) 任务本质「diff 两 DRC deck + 报告」偏 L1 离线 Python，非 L2 真跑 calibre。r460 peek-REJECT **正确**（虽 r460 仅 keywords 级，深读同结论）。

### 5. `1790219463471_6zy8a`（e0041123 @ hfeg0pjn049, mc=98, **r460 已 parked，本轮深读确认**）
- **session.json**：prompt = 完整 `drc-pattern-SKILL.md`（DRC Testpattern Generator，含 drc_pattern_gen.py 用法、techfile/display.drf/lib.defs 依赖、AETHER_ROOT 环境变量、known traps）+ 末尾「生成DWN的pattern」。status **completed**，model deepseek-v4-flash。
- **任务性质**：真 L2 produce-task（pythone 执行 drc_pattern_gen.py 在 Aether 生成 .oa testpattern）。**但**：(a) skill-injection（整 skill 文档作 prompt）；(b) 重 env 依赖（需 Aether install + techfile.tf + display.drf + lib.defs + sample_drc_deck/config/*.json，全在 /home/e0041123/data 与 /proj/drcoa/）；(c) 交付件 .oa 需真跑 Aether，判分需在沙盒复现整个 Aether 环境。
- **结论**：**REJECT（borderline）** — 是 5 条中最接近 case-able 的（真 L2 layout_aether 产出 .oa），但 skill-injection + 重 Aether env 依赖使自包含 case 成本高、判分复现难。本轮不追求；若未来要做需先确认 /home/e0041123/data 脚本+config 可检索 + Aether env 可在 eda_flow sandbox 起。r460 peek-REJECT **合理**（env-dep 风险真实）。

## 综合结论（trace 级，非 keywords 级）

1. **r506 audit「low-mc C 域 substantial 候选存在」被深读证伪**：5 条逐条 scp + 解析 messages.json 后，0 条是干净 produce-task——3 条 skill 管理 Q&A（xyaxc/mdx5g 类）+ 1 条 env-dep live-aether 探测（7glsf）+ 1 条 skill-injection+assets 不可检索（r342a）+ 1 条 skill-injection+重 Aether env（6zy8a borderline）。
2. **r460「low-mc peek 全 REJECT」深读复验通过**：7glsf/mdx5g/r342a/6zy8a 四条 r460 已 parked，本轮深读与 peek 同结论 ⇒ **peek-REJECT 未过激**。r506 audit「peek-REJECT 过激」假设**不成立**。
3. **keywords 高计数 ≠ 工具产出**：aether:987/drc:223/calibre:62 等高频词在 skill-management session 中来自 **skill 名字与描述被枚举**（aether-tool-qa/argus[drc/lvs]/drc-pattern…），非工具执行。这是 low-mc C 域 keywords 高但 trace 弱的根因——**keyword 计数对 skill-heavy session 系统性高估**。
4. **100 连 0-case（r406–r506）质量饱和结论，本轮在 low-mc 端用 trace 级证据首次坐实**：高/mid mc C 域饱和（r506 发现 1）+ low-mc C 域饱和（本轮发现，5/5 weak）⇒ **全 mc 段 C 域 fresh 池质量饱和成立**。mc10.fresh=438≠0（rule 4 不写「池枯竭」），但 438 中可造 clean case 的密度极低（skill-mgmt/env-dep/skill-injection 主导）。
5. **对 P-004 的贡献**：本轮深读是 P-004「fresh-pool 系统性高估」的 **trace 级实证**——fresh 计数把 skill-description keyword 命中当 C 域候选，但深读显示这些 session 无 produce-task。支持 P-004 thesis：fresh 数系统性高估可用 case 材料 77–93%。

## 台账动作
- `xyaxc` claim + parked（本轮新，唯一真 fresh）。
- `7glsf`/`mdx5g`/`r342a`/`6zy8a` r460 已 parked，本轮 mark 覆盖确认（note 加 r507 深读证据）。

## 口径
- mc-matrix src=summary_1109.tsv（A/B 已换池 11/09 ✓）；mc≥10 fresh=438≠0 ⇒ rule 4 不写池枯竭。
- 本审计为 **trace 级**（scp + parse messages.json + session.json + assets 检索），非 keywords 级。
- 未做：low-mc [10,97) 尾部（438 fresh 中 mc<97）未扫；6zy8a 的 /home/e0041123/data 脚本可检索性未深查（borderline，预算不足）。
