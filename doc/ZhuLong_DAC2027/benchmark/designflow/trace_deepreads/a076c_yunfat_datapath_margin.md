# Deep-read: a076c (yunfat @ hfeg0pkn004) — DDR datapath margin skill

- session: `1795081185032_a076c` (yunfat @ hfeg0pkn004)
- mc=89, domain=waveform (waveview:122 / pyaether:99 / synopsys:52 / analog:20)
- 170 msgs / 585KB messages.json
- read: r1189 (scp .75←hfeg0pkn004, python parse)

## 真实用户意图

用户 yunfat 想写一个 pyAether skill 测量 DDR datapath 的 margin。经 brainstorming 三轮 ask_question 对齐：
1. margin 类型 → **setup/hold 时序裕量**（不是电压裕量）
2. 采样时序 → **DDR 双沿**（rise + fall 都采样 data，setup/hold 逐沿配对）
3. 数值形态 → **实测 TSETUP/THOLD + 可选对比 spec min，margin=measured-spec，可判 pass/fail**

## agent 工具链与产物

- brainstorming → skill-creator 流程对齐设计
- 写设计规格文档 `docs/superpowers/specs/2026-11-19-datapath-margin-design.md`
- 实现 `datapath_margin.py` 三模块：
  - `compute_margin(data, strobe, spec)` — 逐 strobe 沿算 t_setup/t_hold + spec 判 pass/fail
  - `shmoo_scan(margin_cases, spec)` — 多 case 聚合最坏裕量
  - `eye_margin(data, strobe)` — UI 折叠，eye width/height
- 沙箱自测（SandBox_MCP_Server__run_code 内联）：NORMAL_NO_SPEC / WITH_SPEC（1 pass 4 fail 手算一致）/ DC_DATA 零摆幅 bug 修复（min==max 阈值退化误判伪边沿 → 加 hi==lo→[] 防护）/ DC_STROBE 不崩
- 落 skill 四件套：SKILL.md + datapath_margin.py + references/timing_theory.md + references/reader_integration.md
- 用户要求用真实 finesim.fsdb（87GB）跑端到端 → 沙箱 glibc 2.12 < fscript 2.17、wv 无执行权限、ae 未装 → agent **如实报告无法读真实 fsdb，不伪造波形**（红线守住了）
- 后续纯文档增强：已知陷阱表 / reader_integration GLIBC 兜底 / end_to_end_usage 指南

## 抽取为 case 的内核

纯 Python 波形时序/眼图裕量计算（离线 L1）：
- 输入 `(t,v)` 采样波形列表，输出结构化 setup/hold/margin/pass + shmoo 聚合 + eye 指标
- check 用独立参考实现逐字段校验，hidden B（不同时序/spec/UI）防背题
- 三假（print_only/core_deleted/hardcode_a）全 FAIL：hardcode A 答案在 B1 上 report 数/t_setup 全失配

## 为什么适合 L1

- 不依赖 live EDA 沙箱状态（纯算法，输入是数据不是工具状态）
- 可构造确定性 hidden B（手算 setup/hold/eye 真值）
- 真实意图完整保留（DDR 双沿 setup/hold + shmoo + eye 三模块都来自用户真实需求）
