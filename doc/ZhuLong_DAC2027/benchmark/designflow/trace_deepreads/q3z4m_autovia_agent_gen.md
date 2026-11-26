# Deepread r807 — e0014566 q3z4m (hfeg0pkn001/10.129.2.10, mc38)

## trace_source
- user: e0014566, host: 10.129.2.10 (hfeg0pkn001), session: 1783476214859_q3z4m
- match_count: 38, keywords: drc:124;virtuoso:77;calibre:14;.gds:11 (physical_verify + layout_virtuoso heavy)
- trace fetched via ssh from .75 sandbox session workdir (121KB messages.json)
- 43 msgs / agent='lead' / 2026-11

## 真实用户意图 (核心回合)

- 用户运行 virtuoso-autovia-runner skill (de-GUI AutoVia 流程)
- 助手任务: 把 SKILL 配置文件 `run_autovia_config.il` (`var = value` 行, `;;` 注释) 内联进 `run_autovia_nogui.il` 流程模板, 生成沙盒安全的自包含 agent .il
  - 替换 `load("run_autovia_config.il")` 块为内联赋值 (process / libName / cellName / pwrnets / viaVIA1..viaCT / coreNum / outCellName 等)
  - 尾部 printf 提示 "请手动 load + 调用 RunAutoViaNoGui()" → 替换为直接 `RunAutoViaNoGui()` 自动启动
  - 头注释改 "AUTO-GENERATED, do not edit manually"
- 助手实际编写 `gen_autovia_agent.py` (config-inliner 工具) 完成上述转换
- trace 终态: AutoVia 运行成功 "AutoVia completed successfully!"

## 档 B reframe 决策 (A 档不可行)

- A 档 gold = 真实 Virtuoso + Calibre DRC + GDS stream-out 的完整 AutoVia 运行
  - 不可行原因: 需生产 fs / Virtuoso license / GDS 文件, SUT 沙盒不可达
- B 档 reframe = 抽离 trace 内助手真实编写的 config-inliner 子工具 `autovia_agent_gen.py`
  - 纯 stdlib (re/sys/os), CLI `<config> <nogui> <output>`
  - 保留原任务全部结构性牙 (load 块替换 / 尾部自动启动 / 头注释 / 幂等 / anti-hardcode)
  - hidden B 用完全不同的 ts22 工艺 + 翻转 via (VIA1=t/CT=nil) + coreNum=8 反硬编码

## case 落库

- case_id: EDA-Eval-DesignFlow-AutoViaAgentGen-001
- domain: physical_verify, tier: B, layer: L1, k_check: 17
- visible A: run_autovia_config_A.il (93 行, cxmt10G4plus/austin/layout_austin6) + run_autovia_nogui_A.il (716 行, 完整 de-GUI AutoVia SKILL 流程模板)
- hidden B: ts22/perilib/peri_top7, viaVIA1=t/CT=nil, coreNum=8, pwrnets="vdd! vss!", 不同 nogui 模板流程体 (inline `r"""..."""` 自包含)
- 17 条断言 (a-q) 覆盖: zip / py_compile / 运行B / 无config load / 内联 process/libName/cellName/pwrnets / via翻转 / coreNum / 尾部自动启动 / 头注释 / anti-hardcode / 幂等 / 缺config退出≠0 / procedure保留 / outCellName
- 自验: ref 17/17 PASS; 4 negative (empty/print_only/hardcode_a/core_deleted) 全 FAIL, distinct FAIL 点证独立牙; §4.9 三假全 FAIL; 幂等 2x byte-identical; jsonl roundtrip test==disk 21239B
- ledger: q3z4m → case
