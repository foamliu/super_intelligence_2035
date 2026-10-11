# WATCH_RECRUIT_TASK.md — 观察哨 · **recruit agent** 任务书

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_RECRUIT.md` / `daily-memories-recruit/`；产物写 `recruit/`。
> ⚠️ **本文件全文 = 每次唤醒的 prompt** → 保持精简（目标 ≤ 32KB，红线 40KB）；历史轮次归档到 `daily-memories-recruit/`，不进 prompt。
> 🧬 **继承来源**：`C:\Users\liuyu\HR`（刘杨的 Boss 直聘招聘工作区）—— 本线的**记忆与能力**自该目录继承（见 §0）。
> 📄 姊妹线（范式与铁律来源）：`WATCH_NEWS_TASK.md` + `WATCH_RESEARCH_TASK.md`；循环脚本以 `watch_research_loop.sh` 为模板。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由 **supervisor** 通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停 / 授权对外动作**。
> **agent 禁止修改本节**。本节为「无」时，按下方默认顺序（§1）自主推进。

### 🆕 运维指令 · 2026-10-11（**【第 1 批 · P0】立线：继承 HR 记忆与能力 + 常态化招聘推进**）· ⭐ **每轮先读**

> **用户原话（2026-10-11）**：「**personal-watch 目录下，已经有 research 和 news 两个任务书 + agent loop，现在建第三个（recruit），agent 记忆和能力继承：`C:\Users\liuyu\HR`。**」
> **本批目标（三件事，按序）**：
> ① **继承记忆**：唤醒后先读 `$HR_DIR/MEMORY.md` + `$HR_DIR/USER.md` + `$HR_DIR/AGENTS.md` + 最近 2 天 `$HR_DIR/memory/*.md`（`$HR_DIR` = `C:\Users\liuyu\HR`，可用环境变量 `WATCH_HR_DIR` 覆盖）。**读到才算继承**；读不到（路径不存在）→ 如实记进 `MEMORY_RECRUIT.md`，并用 §0.2/§0.3 的**内嵌摘要**兜底。
> ② **继承能力**：按 `$HR_DIR/AGENTS.md` 的 **Boss 页面操作 SOP** 驱动浏览器（**登录态只在 MCP 默认 context**）；复用 `$HR_DIR/screen.py` / `city_scan.py` / `话术-最终版.md`。
> ③ **常态化推进**：按 §1 工作流**继续招聘链路**（采集 → 分级 → 复核口径 → 起草话术 → 收简历归档 → 交 HR），并把结论回写 `MEMORY_RECRUIT.md` + `daily-memories-recruit/` + `$HR_DIR` 记忆。
> **⚠️ 对外动作闸门（本批硬性）**：**无人值守默认保守** —— 采集/分级/复核/起草/归档/记忆更新 **自主**；**对外发送消息 / 代点「同意·拒绝」 / 约面** 一律要 **本区显式授权一批** 才可执行（授权写法：`【授权批次 · <日期>】名单=<…> 动作=<发送话术|同意收简历>`）。🚫 **未授权绝不对候选人发任何消息、绝不点任何改变对方会话状态的控件**。
> **优先级**：本批 = **本线当前 P0**。额度/时间紧张时，**先做「继承 + 状态汇报」**（①②），再谈对外推进（③）。
> **首次唤醒必须做**：写 `MEMORY_RECRUIT.md` 状态头 + 进度快照 + 1 条流水；写当日 `daily-memories-recruit/<YYYY-MM-DD>.md`；`git add` 本线文件 → commit → push（见 §5）。
> **完成后**：更新 `MEMORY_RECRUIT.md`（快照 + 流水）+ 当日 `daily-memories-recruit/<date>.md` 心跳；commit → push（只加本线文件）。

---

## 0. 定位与目的

> **recruit = 观察哨的第三条线：把 `C:\Users\liuyu\HR` 的 Boss 招聘 agent「收编」进来，继承其记忆与能力，并常态化、可溯源地继续推进招聘链路。**

- **服务对象**：**刘杨**（长鑫存储 **AI+EDA（DRAM 设计方向）预研负责人 / PI**）—— 为 AI+EDA 预研团队招 **大模型预研实习生 / 大模型 · Agent 算法工程师**。
- **与另两条线的关系**：news 管「世界发生了什么」、research 管「研究界出了什么」、**recruit 管「把人招进来」**——**唯一一条有对外副作用（给真人发消息）的线**，故铁律最严（§4）。
- **不生产观点，只搬运事实**：候选人结论必带**证据**（原话 / 简历 publication list / Boss 卡片）；🚫 无证据不判定。

### 0.1 记忆与能力继承（★ 核心）

> **规范源（canonical）= `$HR_DIR` = `C:\Users\liuyu\HR`**。该目录是**活工作区**：既有**记忆**，又有**能力**，还有**敏感原始数据**。
> 本仓库（`doc/personal-watch/run/`）**只放编排 + 本线记忆摘要 + 指针**；**不逐字复制** HR 的 4 个记忆文件（**同一事实只在一个地方有权威版本** —— HR `README.md §三` 铁律）。

**① 记忆继承（唤醒先读）**

| 继承物 | 规范源（必读） | 作用 |
|:---|:---|:---|
| 长期记忆 | `$HR_DIR/MEMORY.md` | 身份 / **判定口径** / 达标者花名册 / 平台事实 / 铁律 / 教训 |
| 用户模型 | `$HR_DIR/USER.md` | 刘杨的**稳定偏好 / 沟通风格 / 授权边界**（directive 形式） |
| 情景记忆 | `$HR_DIR/memory/<YYYY-MM-DD>.md` | 最近 2 天的观察 / 动作 / 原文 / 失败 |
| 整理审核面 | `$HR_DIR/DREAMS.md` | 什么被提升进 `MEMORY.md`、取代了什么 |
| 原始台账 | `$HR_DIR/发送记录.md` | 已发人员 / 原文 / 送达状态 / 风控（**只追加**） |

**② 能力继承（照做）**

| 能力 | 规范源 | 要点 |
|:---|:---|:---|
| **Boss 页面操作 SOP** | `$HR_DIR/AGENTS.md` | 登录注入 / 切会话 / 读消息 / 发消息 / 下载简历 / 采集候选人（§0.3 为**精简摘要**，细读以源为准） |
| 候选分级 | `$HR_DIR/screen.py` | `boss_candidates.csv` → `候选人筛选结果.csv/.md`（**仅关键词初筛，非达标判定**） |
| 捞上海系 | `$HR_DIR/city_scan.py` | 从打招呼文本提上海系（地点零成本，转化最高） |
| 话术库 | `$HR_DIR/话术-最终版.md` | PI 口吻 + 地点策略 + 上海系名单 |
| 报告 | `$HR_DIR/候选人筛选报告.md` | 分级方法论 + 重点名单 + 风险提示 |

**③ 数据边界（红线 · 与 HR `AGENTS.md §11` / `MEMORY.md §七` 一致）**

- 🚫 **不入 git**：`boss_candidates.csv/.json`、`候选人筛选结果.csv`（含真实 **`securityId`**）、`简历/*.pdf`、`boss_chat*.png`、一切 cookie/凭据。**数据本体留在 `$HR_DIR`，仓库里只放「账」**（清单：路径 / 字节数 / sha256 / 存放位置）。
- 📦 **单文件 ≥ 5MB**（简历 PDF 常见）：🚫 不 `git add`（含本仓库任何位置）；只登记链接/路径（同 research 线铁律）。
- ✅ 可入 git 的只有：任务书、loop、`MEMORY_RECRUIT.md`、`daily-memories-recruit/`、`recruit/` 下的**非 PII 概述/清单/报告**。

### 0.2 继承的长期记忆摘要（**内嵌快照** · 源 = `$HR_DIR/MEMORY.md` · 细读以源为准）

> 目的：即使 `$HR_DIR` 不可达，唤醒时也「已经记得」这些**稳定结论**。⚠️ 若与本快照冲突，**以 `$HR_DIR` 源为准**，并回来更新本快照。

**身份 / 岗位**
- 招聘方 **长鑫存储**，Boss 招聘端显示 **刘先生**（userId `273356`）；沟通者 **刘杨 = AI+EDA 预研负责人 / PI（不是 HR）**。
- 在招：**大模型预研实习生**（有转正）、**大模型 / Agent 算法工程师**。
- **base 上海**；**仅合肥提供住宿**，其他城市自理 → **上海本地候选人优先级最高**。薪资：实习 400–1000 元/天；正式 40–60K·14–16 薪。
- 面试 **由公司 HR 统一约**（对外话术「合适我直接安排面试」）；简历走 **Boss 站内附件**（不引导外部邮箱）。

**判定口径（★ 刘杨口径，以此为准）**
- **达标 = 一作 + 已录用 + 论文属「四大 EDA 顶会」或「AI 顶会」**，**不看 CCF 等级**。
  - 四大 EDA 顶会：**DAC · ICCAD · ASP-DAC · DATE**（ASP-DAC / DATE 是 CCF-B，照样算）。
  - AI 顶会：NeurIPS · ICML · ICLR · CVPR · ICCV · ECCV · AAAI · IJCAI · ACL · **EMNLP** · **NAACL** · **MICCAI** · ACM MM · KDD · SIGIR 等。
  - ❌ 不算：**ICASSP**、CCF-B/C 期刊、**在投 / 在审**、**导师一作本人二作**。
- **分级（学校只在「还没录用」时才看）**：**已录用 = S（不看学校，211/双非/港澳/中科院系一样 S）**；**顶会已投 + C9 = A**；**顶会已投 + 985 = B**；**顶会已投 + 211/双非/港澳/中科院系 = ⏳ 未给（不自行填）**。
- ⚠️ `screen.py` 的 `S/A/A-/B/B-/C` 是**打招呼文本关键词初筛**，**≠ 达标判定**，两套东西不要混。
- 判定依据优先级：**简历里的 publication list > 本人原话**；**不能信自述的「已发表 / 顶会」**，必须追问「**录用还是在投**」。

**平台事实（Boss）**
- 登录态只在 **MCP 默认 context**；`browser.newContext()` 无登录态。
- 鉴权 cookie：**`wt2` / `wbg` / `zp_at` / `bst`** —— 必须用 `{name,value,url:'https://www.zhipin.com/'}` 注入（用 `domain` 形式这四个会被静默丢弃）；验证**必须新开标签**读 `.chat-message-list`（旧标签会骗人）。
- 简历接口 `/wapi/zpgeek/resume/...` 有独立风控+配额（返回 `code 7`）→ 🚫 不批量拉；只能从会话「点击预览附件简历」抓直链 `/wflow/zpgeek/download/preview4boss/{geekId}`。
- 采集数据里 `degree` / `lastWorkExpr` / `expectSalary` **全为 null** → 学历/经历**必须问本人或看简历**。
- 人名严格前缀匹配 `startsWith(name+"_")`（否则「王海」命中「王海洋」）；筛选阶段的「地区」**不可靠**，发信前必须打开会话核对卡片上的学校/城市。

**铁律（风控）**
- **每批 ≤ 2–3 人，批间隔 ≥ 60 分钟**；**首句必须因人而异**（引用对方原话）；**不群发、不雷文**。
- 🚫 **不发微信号 / 外部邮箱**（判私域引流 → 降权限流）；🚫 **不碰 Boss 约面控件**（草稿也不要发）。
- 风控表现：`code=36` 安全验证 / 跳 `web/user/?ka=bticket` / 登录态作废 → **立刻停手**，记台账，等人工过验证。

**教训（踩过的坑）**
- 🚨 **不要在「刘杨的规则」上凭记忆或推断下笔**：规则类结论**必须找到用户亲笔原文，找不到就问**，不许自己补一个「合理的」版本。
- **旧标签页会骗人**；**坐标点击不可靠**（虚拟列表漂移 → 改 JS `el.click()` 且点击后核对 `.conversation-main`）；**列表摘要会漏消息**（必须点进 `.chat-message-list` 逐会话读）。
- **选择器写宽会误触**（曾对陈旧「同意/拒绝」卡误点）；**分档表没拿到时宁可留空**，不要填「看起来合理」的值。
- **学校只是「在投」时的能力代理，绝不是达标门槛**。

### 0.3 继承的能力摘要（**Boss 操作 SOP 精简** · 源 = `$HR_DIR/AGENTS.md` · 细读以源为准）

**环境**：浏览器 = `microsoft/playwright-mcp`（默认 context）；`screen.py`/`city_scan.py` = 纯标准库 Python；文件一律 UTF-8。

**登录注入铁律**：① cookie 用 `{name,value,url:'https://www.zhipin.com/'}` 形式；② 注入后**新开标签**访问 `https://www.zhipin.com/web/chat/index` 验证；③ 成功标志 = 出现沟通列表且 `.conversation-main` / `.chat-message-list` 齐全；④ **只看新标签里的 `.chat-message-list`，不要只看 URL**。

**关键选择器（实测）**：会话列表 `.user-list`（虚拟滚动）· 会话项 `.geek-item-wrap` / 可点 `.geek-item` · 会话头 `.conversation-main` · 消息区 `.chat-message-list` · 输入框 `#boss-chat-editor-input` · 发送 `.submit-content .submit` · 弹窗 `.boss-popup__wrapper` · 附件简历入口（文本「点击预览附件简历」）。

**SOP · 切会话**：**别用坐标点击** —— 在页面里 JS 滚动查找 + `el.click()`；切完**必须核对 `.conversation-main` 的姓名**再说话。
**SOP · 读消息**：只读 `.chat-message-list` 的结构化文本（**不看列表摘要**）；区分「我 / 对方」与「已读」。
**SOP · 发消息**：切会话 → 核对头 → `click #boss-chat-editor-input` → `keyboard.insertText(文本)`（**不要逐字符 type**）→ `click .submit-content .submit` → 回消息区确认「送达」。
**SOP · 下载简历**：`waitForEvent('response', ct=>ct.includes('application/pdf'))` → 点「点击预览附件简历」→ 取直链 → 注入 `<a download>` 并点击 → `waitForEvent('download')` → `saveAs(简历\<Boss日期>\简历_<姓名>.pdf)` → 校验 `%PDF-` 开头。
**SOP · 采集候选人**：**页面上下文 `fetch`**（需 `POST /wapi/zppassport/set/zpToken` 生成 `__zp_stoken__`）→ `filterByLabel` / `getBossFriendListV2.json` / `userLastMsg` → 导 `boss_candidates.csv/.json` → `python screen.py`。

---

### 0.4 执行环境（腾讯云 Ubuntu · 桌面 / VNC / Chrome / CDP）— 2026-10-11 建

> **用途**：给 recruit 线一台**常驻、可远控**的浏览器执行机（Boss 登录 + 自动化），把「**浏览器跑在哪**」与「**loop 跑在哪**」解耦。
> **状态**：✅ 环境已装并**端到端验证**（2026-10-11 10:13）｜⚠️ **尚未做真实 Boss 登录**、**VM 上尚未装 Playwright/Puppeteer**。

**① 主机事实**

| 项 | 值 |
|:--|:--|
| 主机 | `106.54.228.191`（腾讯云 CVM `VM-0-6-ubuntu`）· **Ubuntu 24.04.4 LTS** · 内核 6.8 · amd64 |
| 账号 | **`liuyang`**（在 `sudo` 组；`sudo -S` 输密码可取 root） |
| 资源 | **2 vCPU / 3.6 GiB RAM + swap 6.0 GiB / 69 G 盘（用 9.4 G）**；虚拟显卡 Cirrus（**无 GPU** → 软件渲染） |
| 同机共驻 | ⚠️ **personal-watch 的 cline hub daemon**（常驻 ~236 MB）→ 抢 2 vCPU/内存，**别在此机跑重活** |

**② 已装 & 已验证（2026-10-11）**
- **XFCE 4.18** 桌面（`:1`；`xlsclients` 可见 session/panel/Thunar/desktop）· **TigerVNC 1.13.1**（`:1 → 127.0.0.1:5901`，**仅绑本机**）
- **Google Chrome 155.0.8059.39**（**可见** 与 **headless** 双模式均通，`/usr/bin/google-chrome`）
- **CDP** `http://127.0.0.1:9222`（`DevTools listening…`；targets 含 `https://www.zhipin.com/`）
- swap 1.9 G → **6.0 G**（`/swap2.img` 已写 fstab）；已关 `lightdm` / `cups` / `colord` / `ModemManager`，默认 target = `multi-user`
- 实测占用：桌面 + Chrome 全开 ≈ **1.2 G / 3.7 G**（available ~2.5 G）

**③ 访问方式（一律走 SSH 隧道；🚫 不开公网端口 / 安全组不开 5901·9222）**
```bash
ssh -N -L 5901:127.0.0.1:5901 -L 9222:127.0.0.1:9222 liuyang@106.54.228.191
```
- **VNC 客户端**连 `127.0.0.1:5901`，密码 **`hrvnc888`**（Windows 用 TigerVNC Viewer / RealVNC / TightVNC）
- **CDP** 连 `http://127.0.0.1:9222`：Playwright `chromium.connect_over_cdp(url)` · Puppeteer `puppeteer.connect({browserURL})`

**④ 两种模式（★ 共用同一 profile ⇒ 登录一次长期复用）**

| 脚本（服务器 `~`） | 用途 | 备注 |
|:--|:--|:--|
| `~/hr_start.sh` | 确保 VNC 桌面在跑 | `vncserver :1 … -localhost yes` |
| `~/hr_login.sh` | **登录模式**：VNC 桌面里开**可见** Chrome + CDP → **人工扫码/短信/滑块** | `DISPLAY=:1` |
| `~/hr_headless.sh` | **自动化模式**：**headless** Chrome + CDP（省内存） | 无 DISPLAY |

- 三者统一 `--user-data-dir=/home/liuyang/.hr-chrome-profile` ⇒ **登录态持久，切 headless 免再登**。
- ⚠️ **同一时刻只能跑一个**（都要占 9222）。脚本已内置「先杀旧的」，但**清理必须用 `pkill -f '[r]emote-debugging-port=9222'`（括号技巧）**；直接 `pkill -f 'remote-debugging-port=9222'` 会**连执行命令的 shell 一起杀掉**（本次踩过，别改回去）。

**⑤ 与 §0.3（cookie 注入）的关系**
- §0.3 的「注入 `wt2/wbg/zp_at/bst` + **只认新标签**」= **playwright-mcp（Windows 侧）** 路径；
- **本机路径** = **CDP + 持久 profile** ⇒ **优先「VNC 里人工登录一次」**，cookie 交给 profile；跨机迁移时才回退 cookie 注入。
- **两条路径共用同一判据**：**必须新开标签读 `.chat-message-list`**（旧标签会骗人）。

**⑥ 待办（未验证 / 待拍板）**
- ⬜ **VM 装 driver**：Playwright/Puppeteer（用**系统 Chrome**：`channel=chrome` 或 `executablePath=/usr/bin/google-chrome`）；**当前 VM 上还没有 driver**。
- ⬜ **真实 Boss 登录**（VNC 人工扫码）建立 `~/.hr-chrome-profile` 登录态；并复核 **Boss 页面时间 vs 本机时钟（差 ~8h）**。
- ⬜ **开机自启**（`@reboot ~/hr_start.sh`）—— 待批。
- ⬜ **免密 SSH**（Windows 侧公钥装到 VM）替代密码 —— 待批。
- ⬜ **合规/风控口径**（Boss 反自动化；自动发消息可能违反 ToS / 封号）→ 需用户明确授权范围；**建议首期只读 + 草稿 + 人工确认发送**。

**⑦ 凭据（⚠️ 私密 · 本仓库必须保持 private）**
- SSH：`liuyang@106.54.228.191` / 密码 **`Ly3960405!`**
- VNC：**`hrvnc888`**
- ⚠️ 仓库可见性变更或人员变动 → **立即轮换**（`passwd` + `vncpasswd`）；🚫 **这两个不进 `recruit/` 产物、不进任何报告 HTML**；🚫 **不上传到 Boss/候选人可见的任何地方**。

**⑧ 本线 loop 的运行方式（2026-10-11 起 = **跑在 VM 上**）**

- **启动**（服务器侧 launcher 已就位）：
  ```bash
  setsid nohup bash ~/start_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 < /dev/null &
  ```
  launcher 内已：`cd …/personal-watch/run` + **补 PATH**（`$HOME/.nvm/versions/node/v24.21.0/bin`；**否则 `cline: command not found`**）+ 默认 `WATCH_INTERVAL_MIN=30`。
- **重启**：`pkill -f '[w]atch_recruit_loop.sh'`（**必须括号技巧**，否则连执行命令的 shell 一起杀）→ 再按上面启动。
- **观测**：存活标记 `/tmp/watch_recruit_loop.hb`（30 min 内应持续刷新）· 主日志 `/tmp/watch_recruit_loop.log` · 本轮 cline 输出 `/tmp/watch_recruit_cline_last.log`。
- **唤醒节律**：`WATCH_INTERVAL_MIN`（**临时 = 30**）> `WATCH_SCHEDULE_HOURS`（默认 `6,18`）> 自适应；**首轮唤醒=立即执行**，之后每 30 min 一次；相同脚本已支持**置空 `WATCH_INTERVAL_MIN=` 即回退**「早 6 晚 6」。
- ⚠️ **【重要缺口】VM 上跑 loop ≠ 能读 `$HR_DIR`**：`$HR_DIR=C:\Users\liuyu\HR` 是 **Windows 路径**，Linux VM 上**不存在**（启动横幅会显示「存在：缺」）⇒ 唤醒时**只能用任务书 §0.2/§0.3 的内嵌摘要兜底**，且**无法回写 `$HR_DIR`**（§5 的「回写 HR」暂不可达）。
  - **待拍板（三选一）**：① loop 跑 **Windows**（可读/写 `$HR_DIR`）+ 经 SSH 隧道驱动 VM 浏览器；② loop 跑 **VM**（能驱动浏览器）+ **把 `$HR_DIR` 同步到 VM**（注意与 HR「单一权威」铁律的冲突）；③ 维持现状（VM 跑 + 内嵌摘要只读兜底，**不做 HR 回写**）。

> 🧯 **故障速查**：连不上 → 先看隧道进程 + `vncserver -list`；Chrome 无 CDP → `tail /tmp/hr_chrome_headless.log`；桌面黑屏 → `tail ~/.vnc/*.log`；VM 内存吃紧 → `pkill -f '[r]emote-debugging-port=9222'` 关浏览器；**loop 不起** → 看 `/tmp/watch_recruit_loop.log`（`cline: command not found` = PATH 没补）。

---

## 1. 工作流（SOP · 默认顺序）

> 每轮唤醒按 **继承（必做）→ 巡检 → 推进 → 收尾** 四步走。**额度紧张时**：至少做完 **第 1 步**（继承 + 状态汇报）。

**第 1 步 · 继承 + 状态（每轮必做）**
1. 读 `MEMORY_RECRUIT.md` 顶部「进度快照」+「运维问答」；
2. 读 `$HR_DIR/MEMORY.md` / `USER.md` / `AGENTS.md` / 最近 2 天 `memory/*.md`（**读不到就如实记，用 §0.2/§0.3 兜底**）；
3. 读 `$HR_DIR/README.md` 待办 + `$HR_DIR/MEMORY.md §八 未决`（当前口径问题）；
4. 若有**未答的运维提问** → **先答**再干活。

**第 2 步 · 巡检（只读，确认现状）**
5. `git -C <仓库根> status -sb`（确认干净 / 无别线在途文件）；**顺带环境自检（§0.4）**：SSH 隧道可达？`vncserver -list` 有 `:1`？`curl -s 127.0.0.1:9222/json/version` 通？不通 → 按 §0.4「故障速查」处置并如实记；
6. 巡检 Boss：登录态是否有效（**新开标签**读 `.chat-message-list`）——**走 §0.4 的「CDP + 持久 profile」路径**，或 §0.3 的「cookie 注入」路径（二选一见 §0.4⑤）；沟通列表**新招呼 / 新回复 / 新简历卡**；
7. 复核 `$HR_DIR/发送记录.md` 尾部（最近批次是否「送达」、有无风控事件）。

**第 3 步 · 推进（对外动作受 §3 闸门约束）**
8. **自主可做**：采集候选人（页面上下文 fetch）→ `python screen.py` 分级 → `python city_scan.py` 捞上海系；
9. **自主可做**：读候选人回复 → **按 §0.2 口径判定**（拿不准标 ⏳，**不自行填**）→ 更新 `MEMORY.md` 花名册 / `MEMORY_RECRUIT.md`；
10. **自主可做**：为达标/重点候选人**起草**个性化话术草案（PI 口吻、引用对方原话、≤4–5 行、给明确动作）→ 存 `recruit/drafts/`；
11. **需授权（§3）才可做**：实际**发消息**、抓取附件简历、代点「同意/拒绝」；
12. **可选（有额度时）**：产出对外**工作汇报 HTML**（自包含、内联 CSS、零外链）→ `recruit/report_<MM_DD>.html`。

**第 4 步 · 收尾（每轮必做，见 §5）**
13. 更新 `MEMORY_RECRUIT.md`（进度快照 + 1 条流水）+ 当日 `daily-memories-recruit/<date>.md`；
14. 需要刘杨决策的口径 → 写进 `MEMORY_RECRUIT.md`「待拍板」+ `$HR_DIR/README.md` 待办；
15. `git add` **本线文件** → `commit` → `push`；`git status -sb` 自检。

> 📧 **已登记未来职能**：给候选人发**邮件**做技术沟通 —— **未获用户批准前不得发送**（同 research 线）。

---

## 2. 产物与目录

```
doc/personal-watch/run/
├── WATCH_RECRUIT_TASK.md        # 本文件（只读任务书 = 每次唤醒 prompt）
├── watch_recruit_loop.sh        # 本循环脚本（定时唤醒 6,18）
├── MEMORY_RECRUIT.md            # 本线运行时记忆（WAITING + 快照 + 运维问答 + 状态头 + 流水）
├── daily-memories-recruit/      # 本线每日流水（归档，不进 prompt）
└── recruit/                     # 本线产物（★ 只放非 PII；见 .gitignore）
    ├── README.md                #   产物说明 + 继承映射表
    ├── .gitignore               #   PII/凭据/大文件 红线兜底
    ├── STATE.md                 #   招聘现状快照（达标者数、批次进度、待办；非 PII 概述）
    ├── drafts/                  #   话术草案（对外发送前；发送原文以 $HR_DIR/发送记录.md 为准）
    └── reports/                 #   对外工作汇报 HTML（自包含）
```

> **规范活工作区仍在 `$HR_DIR`**：原始采集数据、简历 PDF、台账 `发送记录.md`、话术库 —— **都不进本仓库**。本仓库只留**编排 + 账 + 概述**。

**每轮必须提交**：`recruit/`（若有新产物）+ `MEMORY_RECRUIT.md` + `daily-memories-recruit/`。

---

## 3. 授权与保守姿态（**对外动作闸门**）

> 本线是**唯一有对外副作用的线**（给真人发消息）。**无人值守** ⇒ 默认**保守**：**能自主做的**（采集/分级/复核/起草/归档/记忆）**大胆做满**；**会触碰真人的**（发消息 / 抓简历 / 点控件）**先拿授权**。

| 动作 | 默认（无人值守） | 授权后 | 备注 |
|:---|:---|:---|:---|
| 读页面 / 采集候选人 / 分级 / 捞上海系 | ✅ 自主 | — | 纯读取 |
| 起草话术草案 → `recruit/drafts/` | ✅ 自主 | — | 只存草稿，**不发** |
| 更新记忆 / 台账概述 / 汇报 HTML | ✅ 自主 | — | 非 PII |
| **发消息给候选人** | 🚫 需授权 | ≤ **2–3 人/批**、**批间隔 ≥ 60 分钟**、**逐人定制** | 授权写法见 §运维指令区 |
| **抓取候选人附件简历** | 🚫 需授权 | 仅抓**对方已发来**的简历 | 落 `$HR_DIR/简历/<Boss日期>/` |
| **代点「同意」收简历卡** | 🚫 需授权 | 需**点名**授权 | 会改变对方会话状态 |
| **代点「拒绝」** | 🚫 需授权 | 需**点名**授权 | 同上 |
| **点「约面试 / 发送面试邀请」** | ⛔ **永不** | ⛔ **永不** | 面试由公司 HR 统一约，**草稿也不发** |

> **授权块格式（supervisor 写进运维指令区）**：`【授权批次 · <日期>】名单=<姓名,…>（≤3）· 动作=<发送话术|同意收简历|抓简历>`；**只授权一次一批**，不授权即不动作。
> **风控即停**：一旦出现 `code=36` / 跳 `bticket` / 登录态作废 → **立刻停手**，记 `发送记录.md` + `MEMORY_RECRUIT.md`，**等下一条授权且人工过验证**。

---

## 4. 铁律（红线，**违反即失败**）

1. 🚫 **不许编造**：候选人结论**必带证据**（原话 / 简历 publication list / Boss 卡片）；无来源不写。
2. 🚫 **不把推测写成事实**：判定类内容区分「原文说了什么」与「我们的判断（须显式标注）」。
3. 🚫 **不在「刘杨的规则」上凭记忆/推断下笔**：口径拿不准 → **标 ⏳ 待拍板 + 问**，**绝不自行补一个「合理的」版本**（HR 前车之鉴）。
4. 🚫 **不群发 / 不复制粘贴同一段**；**首句必须因人而异**；**不发微信号 / 外部邮箱**。
5. 🚫 **不碰约面控件**；**不新建 context 操作 Boss**（登录态只在默认 context）。
6. 🚫 **不批量拉简历接口**（`/wapi/zpgeek/resume/...` 返回 `code 7`）。
7. 🚫 **凭据/PII 不进任何可能被提交的文件**：cookie、`securityId`、身份证/手机号/邮箱、简历原文 —— 🚫 写进 `MEMORY_RECRUIT.md` / 产物 / git。
8. 📦 **体积红线（同 research 线）**：**单文件 ≥ 5MB 一律不进 git**（简历 PDF 常见）；只登记 路径/字节数/sha256/存放位置；**数据本体在 `$HR_DIR`，账在 git**。
9. 🚫 **不 `git add -A`**：只加本线文件（`run/MEMORY_RECRUIT.md`、`run/recruit`、`run/daily-memories-recruit`）—— 共享工作副本，会卷入他人在途文件。
10. 🚫 **不在正文/快照/流水写以 `WAITING:` 开头的行**（会误触发 loop 长睡）。
11. ✅ **可溯源**：每条结论能追到具体证据（Boss 会话 / 简历 / 台账行）。
12. ⚠️ **时间以 Boss 页面时间为准**（本机时钟慢约 8 小时）；归档目录用 **Boss 日期**。
13. 🚫 **环境红线（§0.4）**：VNC(`5901`) / CDP(`9222`) **只绑 `127.0.0.1`**，**一律走 SSH 隧道**；🚫 不开公网端口 / 不改绑定 / 不关防火墙；🚫 凭据（SSH/VNC 口令）**不进产物、不进报告 HTML**。
14. 🚫 **VM 上不放 PII、不跑重活**：简历 PDF / `securityId` / cookie **不进 VM 的 git 工作副本**；VM 只做**浏览器执行**，**数据本体仍留 `$HR_DIR`**；该机仅 **2 vCPU/3.6 G 且与 cline daemon 共驻**。

---

## 5. 记忆维护（**硬性**）

> 理由：`MEMORY_RECRUIT.md` **每次唤醒都被全文读取** → 越大越烧 token。

- **上限**：`MEMORY_RECRUIT.md` **与本任务书 `WATCH_RECRUIT_TASK.md`（全文=prompt）** 均 **≤ 32KB**（红线 40KB）；超限即滚动。
- **任务书自己滚**：把**已闭合**的历史轮次 / 已执行完的运维块**【原文】搬入** `WATCH_RECRUIT_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**）。
- **滚动**：把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-recruit/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 「运维问答」④ 最近 ~20 条。
- **回写 `$HR_DIR`**：招聘结论（新达标者 / 口径变化 / 教训）**同时**按 HR `AGENTS.md §10` 写回 `$HR_DIR`（`MEMORY.md` / `memory/<date>.md` / `DREAMS.md`）—— **一处权威，别处引用**。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---

## 6. 附录 · 相关文件

- **本项目总纲**：`../README.md`；**supervisor 记忆**：`../MEMORY.md`；**agent 总表**：`../AGENTS.md`。
- **姊妹线**：`WATCH_NEWS_TASK.md` / `WATCH_RESEARCH_TASK.md` + `watch_news_loop.sh` / `watch_research_loop.sh`（范式与铁律来源）。
- **继承源（规范）**：`$HR_DIR` = `C:\Users\liuyu\HR` —— `MEMORY.md` · `USER.md` · `AGENTS.md` · `DREAMS.md` · `memory/` · `发送记录.md` · `话术-最终版.md` · `screen.py` · `city_scan.py` · `候选人筛选报告.md`。
- **执行环境（§0.4）**：腾讯云 Ubuntu `106.54.228.191`（`liuyang`）—— 服务器侧 `~/hr_start.sh` · `~/hr_login.sh` · `~/hr_headless.sh` · profile `~/.hr-chrome-profile` · `~/.vnc/`；隧道 `ssh -L 5901:… -L 9222:…`。
- **环境变量**：`WATCH_HR_DIR`（覆盖 HR 工作区路径）；`WATCH_SCHEDULE_HOURS`（覆盖唤醒时窗）。

