# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `wo_sandbox` / `wo_selfexpl`（tab:main-ablation 这两行暂缓）· `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑） |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_ZHULONG.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ZHULONG_TASK_ARCHIVE.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `zhulong 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**29KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动。


### 🧭 运维规程 · 2026-10-06（**【每轮唤醒必须自己 commit+push】** —— 不许依赖 loop 兜底）· 常驻

> **用户指令（2026-10-06）**：与 BaiZe 四线同口径 —— **每条线每次唤醒都要推送**。本线此前明文写「靠外层 loop 每 ~5h 兜底」⇒ **自本轮起作废该口径**（§11 已同步修改）。
> **为什么**：运维**只能靠 git 判断你是死是活** —— 2026-10-06 data 线心跳文件近 2h 未更新，被**误判成卡死并上机排查**。🚫「loop 每 N 小时兜底」**不再作为交付保障**，只是保险丝。
> **每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡**：
> 1. **写心跳**：更新 `run/MEMORY_ZHULONG.md` 顶部状态头 / 执行看板 / 成绩表 + 追加 1 行操作流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮（**当天文件必须建**）。
> 3. **自己提交 + 推送**（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong <阶段/轮次>: <一句话>"` → `git push origin main`。🚫 **绝不用 `git add -A`**（多项目共用工作副本，会卷入别线在途文件）。
> 4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind。**push 失败**（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下轮第一件事补推**。
> ⏱️ **判死判据（硬）**：**心跳文件 >60min 无新提交 ⇒ 按卡死处理**（不再等你）。**你干得再多，心跳不动 = 仍会被判死。**


### 🧭 本轮（2026-10-11 上午）执行顺序 —— **换回旧 4 端口 + 修 RAG + 删 hook → 推进 r2–r5**

> ➡️ **按 `(九)` 执行**（`.env` 端口集换回 `8650/8651/8652/8654` + `RAG_RECALL_URL`→`9006` + 删 `~/.cline/hooks/PreToolUse` + `.env` stash 回退 + **回退 `timeout:180`** → 重跑 r2–r5）。
> ⚠️ **`(九)`⓪ 先自查「中继执行了没有」**（`outbox.md` 有无 RUN_ID 32）——**中继近 11h 无活动、已判「疑似失联」**；若确实失联，`(九)`⓪ 授权你**自己照 `run/ops/inbox.md` 的 RUN_ID 32 块执行**（含重启中继），别干等。
> ❌ `(八)` 已被 `(九)` 取代；`(七)/(六)/(四)/(三)` 已完成或作废 —— **勿重复**。

### 🆕 运维指令 · 2026-10-11（九）— 🔄 换回旧 4 端口（`8650/8651/8652/8654`）+ RAG→`9006` + 删 hook + `.env` 回退 + 重跑 r2–r5【最高优先 · 覆盖 (八)】

> **用户令（2026-10-11 上午）**：「停掉当前评测；删 `~/.cline/hooks/PreToolUse`；`eda_fastmcp/.env` 本地改动 stash（回退昨晚改动）；**测试/应用端口 `8650`、`8651`、`8652`、`8654`**；改 `.env`；**ragrecall 端口重新设为 9006**；**重启 full r2-r5 及后续评测**。」
> **本块应交由 ops 中继 `RUN_ID 32` 代做**（停评测/删 hook/`.env` 备份+stash/写新 `.env`/重启 `eda_fastmcp`/4 端口实测/**4/4 健康才起 r2**/**回退两处 `cline_mcp_settings.json` 的 `timeout:180`**）。⚠️ **用户二段令（10-11）：「昨晚的改动都是垃圾，全部回退，没有任何亮点」** ⇒ 32 块的 timeout:180 回退即按此令执行（**已推翻「保留」判断**）。

**⓪ 先自查「中继执行了没有」（30 秒，每次唤醒必做）**
- `grep -c '^## RUN_ID 32' run/ops/outbox.md` **≥1** ⇒ 已执行 → 走 ①（并按 ① 复核 r2 是否已起）。
- **= 0** ⇒ **判中继失联**（**判据**：中继**最后一次成功执行是 10-10 20:59 的 RUN_ID 31**，此后无回写；⚠️ **不要**拿 `inbox.md` 的 mtime 计时 —— 运维会**原地修订** RUN_ID 32 块，修订**不算**重新计时）⇒ **你自己照 `run/ops/inbox.md` 里 RUN_ID 32 那个 bash 块执行**（244 行/幂等；原文即完整食谱：① 停评测——**只杀评测侧**，`pkill -f run_cline_script` 会误杀编排侧 cline；② 删 `~/.cline/hooks/PreToolUse`；③ `.env` 备份 + `git stash push -- .env`；④ 写 `PROXY_PORTS=8650,8651,8652,8654` + `SANDBOX_ENDPOINTS`（按 `.env`/HEAD 既有映射逐条核对，勿臆测 workdir）+ `RAG_RECALL_URL=http://localhost:9006/recall`；⑤ 重启 `eda_fastmcp`；⑥ 4 端口 `run_code` 实跑；⑦ **仅 4/4 健康才** 起 r2；⑧ **回退两处 `cline_mcp_settings.json` 的 `timeout:180`**）。**执行完**：把 `inbox.md` 的 `<!-- RUN_ID: 32 -->` 置 **33**、并把该 bash 块降级为 text 围栏（占位，防中继复活后重复执行）；并顺手重启中继：`pgrep -af zhulong_ops_relay.sh`（无 → `env PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" https_proxy=http://172.19.92.23:13128 setsid bash doc/ZhuLong_DAC2027/run/zhulong_ops_relay.sh > /tmp/zhulong_ops_relay.log 2>&1 < /dev/null &`）。结论写进 `MEMORY_ZHULONG.md`。

**🔧 infra 速记（2026-10-11 实战；复用细节见 `MEMORY.md` §7 第 18/19 条）**
- **中继/loop「失联」≠ 进程死**：远端 `.last_run_id`/`outbox` 长期不动，多因 **GitHub/proxy 断 → `push FAILED (will retry next cycle)`**（看 `/tmp/zhulong_ops_relay.log` 尾）。**修法**：`pkill -f 'zhulong_ops_relay[.]sh'` → `setsid bash <脚本>`，**显式注入 `PATH=$HOME/.local/node-20/bin:$HOME/.bun/bin:$PATH` + `https_proxy=http://172.19.92.23:13128`** ⇒ 30–60s 内自 fetch 并补跑积压 RUN_ID（10-11 **08:07:34 重启 → 08:07:38 跑完 RUN_ID 32**）；**loop 同法**（RUN_ID 33 已重拉）。
- **跨机救援桥 = BaiZe 中继（跑在 2.29）**：其块内 `timeout 240 ssh -p 3333 -o BatchMode=yes app.e0031982@localhost 'bash -s' <<'EOS' … EOS 2>&1 | cut -c1-190` 即**在 36.15 执行**（**36.15 ✗ 2.12 不可直连**；桥先例 RUN_ID 83/84/85/86）；**跨通道下发要错开 ≥30s**（push 撞车 → 记录只留本地，要下一次 run 才补推）。

**📌 2026-10-11 08:2x 实况**：中继已救活并跑完 **RUN_ID 32/33**（exit=0）；`bash scripts/start.sh` **仍 exit=1**（`:8090` 未监听，但 `python main.py` 有 3 个进程在），4 端口在 08:14 实测 `run_code` 0 字节、**08:2x 已恢复 4/4 健康**（以 agent 自查为准）；**loop 已于 08:13:55 重启**（`cline OK`）。⇒ **唯一硬阻塞 = `/home` 100%（4G < 8G 门槛）** ⇒ 未起 r2、`WAITING=1` 回报；**在运维裁定「可否带 4G 起跑」前不要开跑。**

**① 若中继已执行 → 读 `outbox.md` 末尾 RUN_ID 32 的三件事**：(a) 4 端口实测结果；(b) `.env` 最终关键行（应 `PROXY_PORTS=8650,8651,8652,8654` + `RAG_RECALL_URL=http://localhost:9006/recall`）；(c) r2 是否已起（eval PID / log `/tmp/ABL_full_r2_8650set.log` / 四 override / **hook 是否被重新部署**）。

**② 状态记账（先改状态头再干活）**：`CONFIG=full`(锚点) · `ROUND=2` · `.env` 臂配置不动；**`r2_new`（batch `2026_1010_234408`）判 ❌作废**（code-gen 146/158 但 **eval Steps 5–7.1 未跑 = 无 official Pass@1**；log/batch 留证，不并入成绩）；**`r1=88.0%` 保留**；**端口口径 = `8650/8651/8652/8654` @ `10.129.32.75`**。
⚠️ **披露清单**（写进结果报告「披露」节）：`.env` 端口集回退 + `RAG_RECALL_URL`→`9006`（原 `9012` 死）+ 删 `~/.cline/hooks/PreToolUse` + `cline_mcp_settings.json` 的 `"timeout": 180`（`(八)`③）—— **本轮已随 RUN_ID 32「3.6 步」一并回退**（用户 10-11 二段令：「昨晚的改动都是垃圾，全部回退，没有任何亮点」）。

**③ 分支**：已起 → **先核反作弊**（`ls -l ~/.cline/hooks/PreToolUse` + 新 log 出现「已部署沙盒 hook」+ `ACCESS RESTRICTED` >0；**未部署 ⇒ 立即停本批、判作废、回报**）；随后 `pgrep -f '^bash scripts/run_cline_script'` **有输出=巡检退出**、**无输出=收割**。未起 → `WAITING=1` + 回报不健康端口原文，**不得带病开跑**。

**④ 收割/推进（判据不变）**：`grep -E 'pass \(|PASS_RATE|评估结果汇总|timeout' /tmp/ABL_full_r2_8650set.log | tail -10` → **`timeout ≤ 10` 且 `Pass@1 ≥ 75%`** ⇒ r2 有效 ⇒ r3→r4→r5（同臂 `full` + **四 override**（见 §6 与旧 `(八)`⑥）+ log `/tmp/ABL_full_r3_8650set.log`…；**每轮开跑前 4 端口复检 + `df -BG /home` ≥8G**；不达标最多重跑 3 次 → 仍不达标 `WAITING=1` 回报）→ 5/5 `[88.0, r2–r5]` 算 mean±std → 回填 5 表锚点 → `PHASE=just_finished` → 进 `C2.phi_k10`。产出：各轮 `Pass@1 / timeout` + **「timeout × 端口」表** + hook/canary 复核结论。

### （八）10-10 — 保留 4 端口 + `"timeout": 180` + 重跑 r2–r5【已被 (九) 取代·已归档】

### （七）10-10 — 剔除 8667 + 补 8650–8654 + 调高 MCP timeout【已被 (八) 取代·已归档】

### （六）10-10 — 若 9 端口健康先判别「端口数是否真因」【已被 (七) 取代·已归档】

### （四）10-10 — 根因排查：连续多日 timeout【已完成·已归档】

### （三）10-10 — 先停 zhulong + 实测沙盒端口【已完成·已归档】

### （二）10-10 — 专属沙盒就绪：保 r1 → 重跑 r2–r5【已被 (三)/(四) 取代·已归档】


### （一）10-10 — 切专属沙盒 + C1.full 作废重测【已被 (二) 取代·历史】


### 🆕 运维指令 · 2026-10-09（五）— ✅ 沙盒已修复，可重跑 C1.full r4【已被 2026-10-10(一) 取代·已归档】


### 🆕 运维指令 · 2026-10-09（四）— 🛑 沙盒坏了，r4 已被运维 kill，待命不要重跑【已被(五)取代·历史】

### 🆕 运维指令 · 2026-10-09（三）— 🔄 C1.full r2/r3 复测（模型服务不稳定致大量 timeout）【已归档·被(四)取代】

### 🆕 运维指令 · 2026-10-09（二）— ✅ 沙盒已就绪，可开跑 C1.full r4【已完成·已归档】

### 🆕 运维指令 · 2026-10-09 — ✅ pro-fp4 403 已解决（换 key）+ 🚫 暂不启动 r4（沙盒重启中）【已完成·已归档】


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**：
   ```bash
   cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
   git pull --rebase --autostash origin main          # 先同步（这次用你当前 shell 的代理）
   pkill -f zhulong_loop.sh; sleep 3
   export https_proxy=http://172.19.92.23:13128
   export http_proxy=http://172.19.92.23:13128
   setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
   sleep 4
   # 复核：新 loop 进程应带代理
   _NPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   tr '\0' '\n' < /proc/$_NPID/environ | grep -iE 'https_proxy'
   ```

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 🆕 运维指令 · 2026-10-08（一）— 📝 HTML 报告【已完成·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`（2026-10-08）。产物 `reports/report_2026-10-08_holiday.html`（21870B，8 节齐全，已 commit a4dc5c3c）。

### 🆕 运维指令 · 2026-10-05（八）— ops 中继恢复【已解决·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。ops relay alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-05（七）— 评测侧隔离 config dir【已落地·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。合并线 eval 用 `CLINE_CONFIG_DIR=.cline_eval_zhulong`；编排用 `--config .cline_zhulong`。

### 🆕 运维指令 · 2026-10-05（六）— 试验次序调换 B→C1→C2→S1【已生效·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前顺序 B→C1→C2→S1（§4 已同步）。

### 🆕 运维指令 · 2026-10-04（五）— legacy 组件 loop 保活【常驻·已稳定·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。legacy loop alive ✅（每次唤醒复检）。

### 🆕 运维指令 · 2026-10-04（四）— 正式起始点 C1.wo_retrieval R2【已越过·已归档】
> ⏩ 已归档至 `ZHULONG_TASK_ARCHIVE.md`。当前已推进至 C1.full r1。

### 🆕 运维指令 · 2026-10-04（三）— 中继已恢复 / loop RUN_ID 6 重启【已解决·已归档】

### 🚨 运维指令 · 2026-10-04（二）— 抢救 ops 中继【已解决·勿再执行·已归档】
### 🆕 运维指令 · 2026-10-04：环境迁移 + 合并执行方式 + ops 中继独立

> 本次把 4 个 phase（S1 保真度 / 组件 / S2 Φ / 模型）**合并进本单一任务书 + 单一 loop**，不再按 `ablation_run_conductor_serial.sh` 拆 3 个 task book + 4 个 loop。**执行顺序不变**（README §8）：S1 → 组件 → S2 Φ → 模型。

1. **环境（agent 最终跑在 36.15 服务器，必须用下表 `/nasdata/` 路径）**：
   - `BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp`
   - `PAPER=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/ZhuLong_DAC2027`（唯一可改 LaTeX 树）
   - `GIT_ROOT=/nasdata/app.e0031982/code/super_intelligence_2035`
   - **注意**：当前 2.12 开发机路径前缀为 `/nas_train/`（与 36.15 的 `/nasdata/` 独立挂载，互不关联）。旧 task book 中的 `/nasdata/` 路径在 36.15 上仍然有效，并非迁移关系。
2. **infra 前置校验（PHASE=init 首次启动前必做，不满足则 `WAITING=1` 原地等）**：
   - `df -h /home` 可用 **≥ ~8G**；四 shard 端口 **8664/8665/8653/8669 全 OPEN**；`run_code` 可正常执行（license 可用）。
   - 旧停摆根因即此三项，**没恢复就别开跑，跑出来也作废**。
3. **起始状态（运维在此填实）**：默认 `PHASE=init`，从 `STAGE=S1, CONFIG=omega_low, ROUND=1` 开始；若要延续旧 S1 进度，改填 `CONFIG=omega_low, ROUND=3`，并把 r1=81.6 / r2=82.3 写进 MEMORY 成绩表，r1/r2 不重跑。
4. **ops 中继通道已就绪**：`run/zhulong_ops_relay.sh` + `run/ops/{inbox,outbox,README}.md`。运维通过 git 下发 shell 命令（~20s 轮询），与 BaiZe ops 相互独立。启动命令见 `run/ops/README.md` 或本报告 §6。
   - ⚠️ 只有本区（运维指令区）的 ops 提及是写给人看的。**agent 不要碰 ops/ 目录**（中继专供运维下发命令，agent 写 MEMORY 和日常记录即可）。

### 🆕 运维指令（后续按需追加）

> （预留：运维批准模型消融、调整起始点、或追加 RQ3 SKILL/Tcl 切片时写在这里。）

---

## 1. 🎯 你是谁 · 任务总目标

你是推进 ZhuLong（DAC2027）EDA 消融评测的自动化 agent。每次被唤醒**只做一步**：

> 读 `MEMORY_ZHULONG.md` 恢复状态 → 读 `daily-memories/$(date +%F).md` 恢复上下文 → 判断下一步 → 执行 → 更新 `MEMORY_ZHULONG.md` 与当日流水 → 立刻退出。

不要 sleep/等待（外层循环负责间隔）。shell 命令直接调用工具，**不要调用任何 MCP 工具**。

**总目标**：把论文 6 张表里所有 `[TBD]` 换成实测 `mean ± std`（口径 README §4.1），共 **56 个 `[TBD]` / 30 行**。本任务书覆盖需要跑量的 4 个消融轴（见 §4）；`tab:selfdoc-cost`（离线自探索日志，1 次无重复）不在本循环内。

## 2. 🔒 冻结项（所有臂共用，不得变动）

- 数据集 `EDA-Eval-PyAether` **158 任务**；通过判据 = 生成代码在 sandbox 无错执行且全断言通过；`Pass@1 = 通过/158×100%`。
- 每配置 **5 次独立运行** → `mean ± std`；每次**重排任务顺序** + **全新 agent context**。
- 单任务单 trace、超时 **2500s**、`-p 8 -n`（8 并发 + 禁 Memory Bank 注入）。
- 主 backbone `deepseek-v4-pro-fp4`（**只有 STAGE=B 模型消融才换**）。
- **反作弊 PreToolUse hook 全程启用、所有臂完全一致（冻结变量，不是消融对象）**。
- `cimi_search` / `cimi_fetch` / `vqa` 永远关闭，不要碰。
- 检索默认 = name+description 索引向量检索（只有 S1 显式改变该索引保真度）。

## 3. ⛔ 红线（不得违反）

1. 不复活被否决表述；不自造符号/定律；不把「轮次」当 Φ 的操作轴。
2. 不改 `tab:llm-comparison` 结构（列/行口径已锁定）。
3. 不承诺开放任务用例（开源只覆盖 harness/schema/protocol，不含 benchmark 任务本体）。
4. 不填未测数字（未测留 `[TBD]` 或显式 provisional）。
5. `tab:omega` 口径：`(N)`=Pure LLM（核心 4 全关）；不采用 ICML 的 `(N)=0.0`。
6. 各 hook `errorMessage` 用唯一前缀区分（反作弊 vs `[PHI-BUDGET-EXHAUSTED]`）。
7. 反作弊内部数据不入论文正文（只定性，不带数字）。

## 4. 🗺️ 合并消融总计划（4 阶段 · 15 臂 · 75 轮 · 单循环串行）

执行顺序（**已调换**：因 pro-fp4 额度 403 阻塞 C1，现将 Phase B 提到最前）：**B → C1 → C2 → S1**。

| 阶段 STAGE | 流 | 臂（顺序）| 轮 | 回填表 |
|:--|:--|:--|:-:|:--|
| `B` 模型 | B | `glm-5.2` → `deepseek-v4-flash` → `kimi-k2.6-cloud` → `doubao-seed-2.0-pro-cloud` | 20 | `tab:llm-comparison`(4 行) |
| `C1` 组件 | C | `pure_llm` → `rag` → `wo_retrieval` → `full`(锚点) | 20 | `tab:main-ablation`(4 行) + 锚点行 |
| `C2` S2 Φ | C | `phi_k10` → `phi_k3` → `phi_k1` → `phi_lagged` | 20 | `tab:phi-bound`(k1/3/10/lagged) |
| `S1` 保真度 | A | `omega_low` → `readback_binary` → `readback_none` | 15 | `tab:omega`(L) · `tab:ablation-harness`(B,N) |

**锚点复用（跑一次、多处引用，禁止重复跑）**：
- `C1.full` ×5 = `tab:main-ablation`(full) + `tab:omega`(H) + `tab:ablation-harness`(F) + `tab:phi-bound`(unbounded) + `tab:llm-comparison`(DeepSeek-V4-Pro 主基座)。
- ∴ S1 的 (H)/(F)、C2 的 `phi_unbounded`、B 的主基座臂**全部跳过，不重跑**。

## 5. ⚙️ 统一状态机（字段写 `MEMORY_ZHULONG.md` 顶部）

| 字段 | 取值与含义 |
|:--|:--|
| `STAGE` | `S1` → `C1` → `C2` → `B`（顺序，交叉衔接）|
| `CONFIG` | 当前臂名（见 §4 表）|
| `ROUND` | 1..5 |
| `PHASE` | `init` / `running` / `just_finished` / `done_all` |
| `WAITING` | 0=无异步阻塞（下轮 ~1min 续跑）；1=一轮 eval 正在跑，或 infra 不就绪（下轮 ~30min）|
| `ERROR_COUNT` | 连续失败计数（≥3 强制推进）|

**臂轮转矩阵（PHASE=just_finished 时查下表切下一臂——已调换为 B→C1→C2→S1）**：

```
B:  glm-5.2 → deepseek-v4-flash → kimi-k2.6-cloud → doubao-seed-2.0-pro-cloud → C1.pure_llm
C1: pure_llm → rag → wo_retrieval → full → C2.phi_k10
C2: phi_k10 → phi_k3 → phi_k1 → phi_lagged → S1.omega_low
S1: omega_low → readback_binary → readback_none → done_all
```

> ⚠️ **Phase B→C1 衔接**：Phase B 使用 full 配置（不切 set_ablation），切到 C1.pure_llm 前**必须先执行** `scripts/set_ablation.py pure_llm` + `stop.sh && start.sh` 将 .env 切为 pure_llm 配置。
> ⚠️ **C1→C2 衔接**：切 C2 前执行 `scripts/set_s2_phi.py <ARM>` + `stop.sh && start.sh`。
> ⚠️ **C2→S1 衔接**：切 S1 前执行 `scripts/set_s1_fidelity.py <ARM>` + `stop.sh && start.sh`。

## 6. 🔧 固定命令（所有 `cd` 用 `BASE_DIR` 展开；`<TAG>`=CONFIG 名，`<N>`=轮次 1..5）

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
