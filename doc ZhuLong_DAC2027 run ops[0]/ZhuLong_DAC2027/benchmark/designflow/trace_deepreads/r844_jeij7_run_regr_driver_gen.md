# r844 deepread — jeij7 → RunRegrDriverGenProduce-001

## trace
- session `1794385756928_jeij7`, user `e0039102` @ `hfeg0pbn16` (10.129.32.204)
- 306 msgs / agent=lead, provider zjh / glm-5.3-flash, cwd `/ai_sandbox/ddgoa/V0/agentdir/e0039102`
- fork from pxf8v/k45zs; meta title = "这个对话中断了，你总结一下对话，建立一下对话框架"
- agent-policy-engine enforcing (readableRoots=2, writableRoots=1)
- scan mc=143, keywords verilog:982/netlist:16/aether:14 → verification 域

## 用户意图演进
- U#1: 总结中断会话 pxf8v，建立对话框架（fork 续接）
- U#19/20: 验证是否全跑通 / caselist 模板生成到哪了
- U#42: run_项目名文件找不到
- **U#60 (核心 produce-task)**: 按标准模板 `run_ddgoa`(`/rundata/.../jason17w/.../verilog.lpddr5.ddgoa.0812/run_ddgoa`)重写 `run_lpddr5_ddgoa_WOWTOP`，放到 `<WOWTOP>/run_lpddr5_ddgoa_WOWTOP/run_lpddr5_ddgoa_WOWTOP`
- U#79: 标准驱动文件放指定目录
- **U#89**: regr.env 不动 (VPS_PROJECT=vps_project)，把整个对的流程写成 vps 配置 skill 方便另一个 Agent 另一个项目自动配置
- **U#111/156**: 只调这一个 skill / 换项目要灵活 / 不能写死路径 / 模板要提炼可迁移

## assistant 工具链（157 tool_use: read_files×26 / editor×90 / run_approved_command×30 / list_allowed_files×9）
- 读了 pxf8v 中断会话 + `/rundata/ddgoa/.../run_regr/` 框架文件
- 写 `gen_run_perl.py`：解析 caselist (-sr/-b/-d) → 按 byte 段分组(首次出现序) → 渲染 perl 驱动
- 写 `verify_run_perl.py`：校验 system() 行数 / 段头 / case 顺序 / byte+defines / perl -c
- 运行 verify 输出: **330 system() case lines, 6 段头** (`x16` / `x8` / `x8 hibyte` / `x8 mrconfig` / `x8 hibyte mrconfig` / `x16 hibyte mrconfig`), case order identical, byte+defines identical, `perl -c syntax OK`
- sample 行: `system("./bin/vsim_uvs -sr auto -b "x8" -d "LPDDR5G USESDF LocalPower PWRBC FUSA" --noprobe -q vbatch_lp --ncconfig "+ncnowarn+TRTDECAY +ncnowarn+CSINFI +ncsdf_nocheck_celltype" -l "11-10" &");`
- 后半段写 `vps-regr-setup-skill` (SKILL.md + copy_framework.py + gen_standard_driver.py + verify_setup.py + references)，提炼占位符模板

## A 档不可行性（关键）
1. `/rundata/ddgoa/` 对 `e0031982` 身份 **Permission denied**（cadmin:ddgoa 组，.75 eda_flow 核验 `ls /rundata/ddgoa` = Permission denied）→ 真实 caselist + run_ddgoa 模板不可读
2. trace 中 `read_files` 对 `/rundata/ddgoa/.../run_ddgoa` 与生成文件的 tool_result **内容为空**（agent-policy-engine sandbox 剥离文件内容，idx=113/115 len=0）→ 无法从 trace 还原真实文件原文

## B 档 reframe（忠实）
- 从 assistant 自写且完整保留在 editor tool_use 的 `gen_run_perl.py`/`verify_run_perl.py` + verify 运行输出，提炼模板结构与变换逻辑
- 交付物 = 参数化 `gen_run_driver.py`（复刻解析-分组-渲染逻辑）+ A 产物
- caselist_A (可见, 18 cases/4段) / caselist_B (隐藏, 24 cases/5段, 项目 lpddr5_ddgoa_PROTO2, logname 11-15) 结构忠实
- 天然契合 U#89/111/156「换项目要灵活/不能写死路径」可复用诉求

## 判分
- check() 15 条独立断言，隐藏 B 上跑生成器校验结构/顺序/内容
- 自验: ref PASS 15/15 + 3 neg (empty→C2 / print_only→C4 / core_del→C5) 全 FAIL + perl -c OK + 3-seed 反硬编
- k_check==k_rationale==15 ≥8 硬闸门过；jsonl test 字段 sha256 == disk check.py sha256 byte-identical

## 落库
- A.jsonl 415→416, cases/A +1, ledger jeij7 parked→case(--force override r501 park)
- domain=verification (A 域), B档 synthesized, judging_paradigm=produce-task
