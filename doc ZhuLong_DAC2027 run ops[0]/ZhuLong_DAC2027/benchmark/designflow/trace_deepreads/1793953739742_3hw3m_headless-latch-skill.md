# 深读笔记 · 1793953739742_3hw3m (ruifan@hfeg0plg36, mc=525)

> r294 选料深读（DEBT:1，>2MB/>600msg 触发 §3 单轮深读例外，r295 必须交付 case）
> trace: 2.9MB / 878 msgs / status=completed / exit_code=0 / model deepseek-v4-flash
> forkedFrom: 1793952785938_fmd3i（同任务前序会话）
> domain: **layout_virtuoso**（SKILL 自动化 + headless Virtuoso + CSV 抽取）
> 发现来源：**fresh scan 20261109_224902**（推翻 r292「自然饱和」判定 —— 11-05 scan 池耗尽但 11-09 fresh scan 有新 ruifan layout_virtuoso 会话）

## 任务全貌（用户真实意图链，19 条 user_input）

用户 ruifan 在 `/home/ruifan/agentdir/dejoa/V0` 驱动一个**多轮迭代**的 SKILL 自动化任务，最终产物 = 一个打包好的 cline skill `Generate-CM-MA-OP-Address`：

1. `在当前目录执行命令 df2_LP dejoa V0`
2. `执行skill脚本 /apps/imctf/cad/init/settings_cdns/skill/special/se/CXMTseGetAllLatchInfo.il，运行主函数 CXMTseGetAllLatchInfo_GUI()，自动点击apply，或直接运行callback CXMTseGetAllLatchInfo(hiGetCurrentForm())`
3. `请重新执行上述的完成流程...产生最终的csv文件`
4. `成功弹出来界面，但还是没有apply成功。csv文件内容为空`（诊断：GUI 弹出但 apply 失败）
5. `在不启动virtuoso界面的前提下，运行该功能对应的函数 CXMTseGetAllLatchInfo(mainForm)直接输出csv文件`（**关键目标轮**：headless 无 GUI 直接输出 CSV）
6. `virtuoso界面依旧会启动，希望不启动virtuoso的界面，直接运行函数，请再优化`（再优化 headless）
7. `希望实现根据用户的描述，自动解析出项目名和版本...生成命令df2_LP dejoa V0，然后执行上述的完整流程`（**关键目标轮**：NL→命令→完整流程）
8. `将上述流程包装成一个完整的skill`（**关键目标轮**：打包成 SKILL）
9. `skill目录里，仅保留skill相关的文件`
10. `不要每次都在skill目录下产生文件...放在项目workdir下面的用户目录中`（skill 目录固化只读）
11. `需要能够让任意用户来使用该skill, 用户名需要改成变量获取的形式，不能固定`（**关键约束**：username 变量化）
12. `Extract Full MA Address，默认的是YES，需要支持用户描述不抽取所有MA address, option选择NO`（**关键功能**：extract Yes/No 选项）
13. `将skill的命名改为Generate-CM-MA/OP-Address`
14. `为我写一份完整的介绍上述SKILL用法的说明书`

**§A rule 2 判定**：轮 5/7/8/11/12 是「提出需求/表达目标」轮，可作 A 档任务说明。轮 4（指出根因 CSV 空）不可作任务说明但可作 hint。**推荐 A 档任务说明 = 轮 7 原文**：「在上述基础上，希望实现根据用户的描述，自动解析出项目名和版本，例如，帮我在dejoa项目，V0版本，运行上述函数，需要能自动识别项目为dejoa，版本为V0，生成命令df2_LP dejoa V0，然后执行上述的完整流程」+ 轮 8「将上述流程包装成一个完整的skill」。

## 金标准（用户实际接受的产物）

**SKILL 目录**：`/home/ruifan/.cline/skills/Generate-CM-MA-OP-Address/`（status=completed, exit_code=0, 用户最后请求写说明书 → README.md 已生成 13671B）

| 文件 | 大小 | 作用 |
|---|---|---|
| SKILL.md | 5547B | skill 元数据 + 验收标准 + 输出规格 + 已知陷阱 |
| README.md | 13671B | 完整用法说明书（最后请求） |
| auto_run.py | 7359B | 入口：NL 解析 proj/ver + 校验 + 生成命令 + 调 pipeline |
| run_pipeline.sh | 3949B | 参数化无 GUI 完整流程 |
| headless_latch.il | 2631B | 无 GUI IL 模板（构造 form + 直接调 callback + exit） |
| skill_client.py | 1630B | TCP 客户端向 bridge 127.0.0.1:55447 发 SKILL 代码 |
| run_skill.sh | 319B | 包装 skill_client.py |
| hide_windows | 22848B | 编译好的 X11 工具，unmap 指定 PID 的所有窗口 |

## SKILL.md 验收标准（直接映射 check.py 断言）

1. 给定「帮我在dejoa项目，V0版本，运行上述函数」，auto_run.py 解析出 proj=dejoa, ver=V0，打印 `[生成命令] df2_LP dejoa V0`
2. `/proj/dejoa/V0/workdir/<USER>` 存在才继续，否则报错退出
3. 运行期间 virtuoso 窗口从未可见（hide_windows 启动后 ~4s unmap）
4. 最终 CSV >1000 字节，首行表头 `MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block`
5. run_common.log 出现 `generated command:` 与 `ALL DONE`
6. virtuoso 最终退出，bridge 端口 55447 关闭

## 输出规格（CSV/ErrorInfo）

CSV（UTF-8, 逗号分隔, 首行表头）：
```
MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block
0000,000,0,Test,cm0_ts_Comp,cm0_ts_Comp,CMAryA;CMCenterL;CMCenterR;CMDqL;CMDqR
```
ErrorInfo（每行一条 ERROR）：
```
[ERROR1] same Latch with differnent testmode: cell : dejoa_digital ("CMCenterL" "CMCenterR") testmode: cm1_sp_SparePQ<8> MACode: 0376
```

## 关键代码要点（用于 check.py 断言设计）

### auto_run.py
- `parse_proj_version(text)` → (proj, ver)；ver 正则 `(?:[Vv]\s*)(\d+)(?!\d)` → `"V"+group`；proj 正则 `([a-z0-9_]{3,12})(?:项目|工程|project|Project)?`，排除噪音词
- `parse_extract(text)` → 'Yes'/'No'；否定模式（不抽取所有MA地址/不全量/extract no 等）→ 'No'，默认 'Yes'
- `validate(proj,ver)` → 检查 `/proj/<proj>/<ver>/workdir/<USER>` 是否存在
- `CUR_USER = os.environ.get("USER") or getpass.getuser()`（**变量化，非硬编码 ruifan**）
- main: 解析 → 校验 → 打印 `[生成命令] df2_LP {proj} {ver}` → 打印 `[Extract Full MA Address] {extract}` → gen_il → 调 `bash run_pipeline.sh proj ver il`
- 退出码 = pipeline 返回码

### headless_latch.il（模板）
- `leGlobalVariables->project = "dejoa"`（gen_il 替换为实际 proj）
- `?defValue __EXTRACT__`（gen_il 替换为 "Yes"/"No"）
- 加载 `/apps/imctf/cad/init/settings_cdns/skill/special/se/CXMTseGetAllLatchInfo.il`
- form 字段名**必须**：`myLib`（Library combo, defValue=lib）, `extractFld`（Radio Yes/No）, `searchCellsComFld`（String, CM cells）
- `hiCreateAppForm(?name 'autoForm ?fields list(myLib extractFld searchCellsComFld) ?callback "CXMTseGetAllLatchInfo(hiGetCurrentForm())")` —— **不调 hiDisplayForm**
- `errset(CXMTseGetAllLatchInfo(autoForm) t)` —— 直接调 callback，传 autoForm（不是 hiGetCurrentForm()）
- CSV 路径 `allCMAdr_MAandOP_20261106.csv`（gen_il 替换日期为今天）
- 末尾 `exit()` —— 退出 virtuoso
- 全程 poport/errport 重定向到 callback_out.log / callback_err.log

### run_pipeline.sh
- 3 个 RHEL8 env 必须同时设：
  - `OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x`
  - `LD_PRELOAD="/lib64/libstdc++.so.6 /lib64/libfreetype.so.6"`
  - `CXMT_START_EDA_AGENT_SERVER=1`
- 开头 `pkill` 本用户 virtuoso/EDAAgent_Server/cds 进程（清旧残留）
- 启动 virtuoso + bridge(55447) + hide_windows unmap + 发 IL + 等 CSV

## check.py 断言草案（≥8，k 待定，对照 SKILL.md 验收标准）

a. submit.zip 含 8 个文件齐全（SKILL.md/README.md/auto_run.py/run_pipeline.sh/headless_latch.il/skill_client.py/run_skill.sh/hide_windows）
b. auto_run.py 在隐藏输入 B（NL 描述）上 `parse_proj_version` 返回正确 (proj,ver)（subprocess 真跑）
c. auto_run.py 打印 `[生成命令] df2_LP <proj> <ver>`（B 上真跑 main 截 stdout）
d. auto_run.py 的 `parse_extract` 对「不抽取所有MA地址」返回 'No'，对默认描述返回 'Yes'（真跑）
e. headless_latch.il 含 form 字段名 myLib / extractFld / searchCellsComFld（任一缺失 → callback nil->value 崩溃）
f. headless_latch.il 调用 `CXMTseGetAllLatchInfo(autoForm)` 且**不含** `hiDisplayForm`（headless 关键）
g. headless_latch.il 末尾有 `exit()`（virtuoso 退出）
h. auto_run.py 中 username 为变量化（`os.environ.get("USER")` 或 `getpass.getuser()`），**不含**硬编码 `ruifan`
i. run_pipeline.sh 设 3 个 RHEL8 env（OA_UNSUPPORTED_PLAT / LD_PRELOAD / CXMT_START_EDA_AGENT_SERVER）
j. SKILL.md 含 CSV 表头 `MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block`
k. auto_run.py validate 检查 `/proj/<proj>/<ver>/workdir/<USER>` 存在
l. gen_il 把 `__EXTRACT__` 替换为实际 Yes/No（生成的 IL 不含字面 `__EXTRACT__`）

**k_check = 12 (a-l) ≥ 8 ✓**。随机化：B 用不同 proj/ver（如 drcqa/V1、testchip/V3）+ 不同 extract 描述。负样本：(a) 空壳 zip (b) 只 print 期望串的 auto_run (c) 含 hiDisplayForm 的 IL。

## 资产需采集（r295 合成时从 .75 拉取）

- `scp 10.129.32.46:/home/ruifan/.cline/skills/Generate-CM-MA-OP-Address/{SKILL.md,README.md,auto_run.py,run_pipeline.sh,headless_latch.il,skill_client.py,run_skill.sh,hide_windows}` → reference/（参考解）
- `scp 10.129.32.46:/apps/imctf/cad/init/settings_cdns/skill/special/se/CXMTseGetAllLatchInfo.il` → assets/（A 输入，SKILL 函数源 —— 但此文件可能很大/受限，需 peek 大小；若不可得则用 SKILL.md 已记录的字段名/路径作资产）
- 一份真实 CSV 样本（若 /proj/dejoa/V0/workdir/ruifan/ 有 allCMAdr_MAandOP_*.csv）→ hidden/（B 金标准）

## 难度/档位判定

- **档位**：A 档（trace-faithful）—— 任务说明用轮 7 + 轮 8 原文，不补全交付形态
- **层**：L1（结构 + NL 解析 + IL 静态检查，subprocess 真跑 auto_run.py 的 parse）+ 部分 L2（若 sandbox 能跑 run_pipeline.sh 则升级，但 virtuoso+bridge+X11 环境复杂，建议 L1 为主）
- **难度**：中高 —— 多文件包结构 + NL 正则 + SKILL 语义 + headless 约束，猜答案难

## r295 合成计划

1. 从 .75 拉取 8 个 SKILL 文件 → `reference/EDA-Eval-DesignFlow-HeadlessLatchSkillGen-001/`
2. 构造隐藏输入 B：NL 描述用不同 proj/ver（drcqa/V2 + extract No 描述），预期 auto_run 输出对应命令
3. 写 check.py（12 断言 a-l，subprocess 真跑 auto_run.py 的 parse_proj_version/parse_extract/main）
4. 三假提交（空壳/print-stub/删 exit）全 FAIL
5. negative_selftest.py
6. 自验 ref PASS + 三假 FAIL → 追加 EDA-Eval-DesignFlow_C.jsonl → mark case → 日报

## 备注

- ruifan 在 fresh scan 还有 4 个同构候选（fmd3i/k8y6h/7l5ub/wsxpm，均为 fork 关系或同任务延续），若 3hw3m 出完 case 可 mark parked 余下避免主题重叠
- xinqiaoz PDK_QA cluster（fju0e/7ansu/q8hpz/yhfm0/wmv7m/esq76/fxkr4/ihvqf）fresh scan 仍 sim=0 纯 calibre，但 r293 判定全 idle/failed，本轮不取
