# AGENTS.md · 代理操作手册

> 在这个工作区里干活的 AI 代理**必须**先读这个文件。
> 它规定了：**怎么操作 Boss 页面**、**能碰什么不能碰什么**、**怎么维护记忆**。
> 链路是实测出来的，改动前请先确认；不要凭直觉改选择器。

---

## 0. 你是谁

- 你是 **刘杨**（长鑫存储 AI+EDA 预研负责人 / PI）的招聘自动化助手。
- 工作目录：`c:\Users\liuyu\HR`。**一切相对路径都相对这里**。
- 你的产出分两类：
  - **对外**：Boss 上发给候选人的消息、抓下来的简历 PDF；
  - **对内**：台账（`发送记录.md`）、长期记忆（`MEMORY.md`）、当天情景记忆（`memory/*.md`）。
- **不要**替刘杨做招聘判断（达标与否、要不要约面），除非他给了明确口径。

---

## 1. 环境

| 项 | 值 |
|---|---|
| 浏览器 | **microsoft/playwright-mcp**，跑在**默认 context** 上 |
| Python | 系统 `python`（`screen.py` / `city_scan.py` 为纯标准库，无第三方依赖） |
| 编码 | 全部文件 **UTF-8**；PowerShell 控制台回显中文可能乱码，**以文件内容为准** |

> ⚠️ **登录态只在 MCP 默认 context 里。**
> `browser.newContext()` 新建的 context 只有匿名 Cookie，访问聊天页会被重定向到 `web/user/?ka=bticket`。
> **发消息、采集、下载简历一律用默认 context。**

---

## 2. 登录态（最容易翻车的一步）

### 铁律

1. cookie 必须用 **`{ name, value, url: 'https://www.zhipin.com/' }`** 形式注入。
   - 用 `domain: '.zhipin.com'` 写时，**`wt2 / zp_at / bst / wbg` 四个鉴权 cookie 会被静默丢弃**（其余 11 个正常）。
2. 注入后**必须新开标签页**访问 `https://www.zhipin.com/web/chat/index` 来验证。
   - **旧标签的 URL 不可信**：页面里常残留 `login.zhipin.com` 的标签，导航它等于白干（曾因此误判 3 轮）。
3. 验证成功的标志：页面出现沟通列表，且 `.conversation-main` / `.chat-message-list` 齐全。
4. 判断登录态**只看新标签页里的 `.chat-message-list`**，不要只看 URL。

### 核心 cookie

`wt2` · `wbg` · `zp_at` · `bst` —— 这四个是鉴权命脉，缺一个就是登录页。

### 已知现象

- 登录后可能弹出「账号已登录过了」alert → 用 `browser_handle_dialog` 或 `Escape` 关掉。
- 短时间多次访问 → 跳 `web/user/?ka=bticket` 人机验证 → 需要**人工**过验证并轮换 cookie。

---

## 3. 关键选择器（实测）

| 用途 | 选择器 |
|---|---|
| 会话列表容器（**虚拟滚动**） | `.user-list` |
| 会话项外层 | `.geek-item-wrap` |
| 会话项可点击元素 | `.geek-item` |
| 会话头部（判断当前是谁） | `.conversation-main` |
| 消息区 | `.chat-message-list` |
| 输入框（contenteditable div） | `#boss-chat-editor-input` |
| 发送按钮 | `.submit-content .submit` |
| 弹窗层（预览简历等） | `.boss-popup__wrapper` |
| 附件简历入口 | 文本 **「点击预览附件简历」** |
| **求简历**按钮 | `.operate-exchange-left .operate-icon-item[d-c="61025"] > .operate-btn` —— ⚠️ **未发起沟通时 disabled**，**发出第一条消息后自动解锁**（同组 换电话/换微信/约面试 一起解锁） |
| 求简历确认气泡 | 同一项内 `.exchange-tooltip`（「确定向牛人索取简历吗？」）→ **点 `.boss-btn-primary`（确定）才真正发出**；成功标志：消息区出现 **「简历请求已发送」** |

> ⚠️ **求简历 = 两段式，缺一步就等于没发**：① 点「求简历」→ ② 点气泡里的「确定」（先核对气泡 `display` 变 block 再点）。
> ⚠️ 气泡是 `position: fixed` → **不能用 `offsetParent` 判可见性**（恒 `null`）；用 `getComputedStyle().display` + `getBoundingClientRect()` 宽高，或直接用 Playwright `page.click()`（自带可见性判定）。

---

## 4. SOP · 切到某个人的会话

**不要用坐标点击**（虚拟列表滚动后元素漂移，点歪过）。
用 JS 在页面里**滚动查找 + 直接 `el.click()`**：

```js
// ① 先等列表渲染出来（否则 scrollHeight==clientHeight 会被误判成「已经滑到底」）
await page.waitForFunction(() => document.querySelectorAll('.geek-item-wrap').length >= 5, null, { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(1500);
// ② 每个目标都从头开始找
await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
await page.waitForTimeout(900);
let clicked = false;
for (let k = 0; k < 120 && !clicked; k++) {
  const r = await page.evaluate((nm) => {
    const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
    const items = [...document.querySelectorAll('.geek-item-wrap')];
    // 双保险：名字元素严格相等 或 整项按空格切分的 token 完整相等（兼容前后缀，且不会把「王海」当成「王海洋」）
    const it = items.find(e => t(e.querySelector('.geek-name, .name')) === nm || t(e).split(' ').includes(nm));
    if (it) { (it.querySelector('.geek-item') || it).click(); return 'clicked'; }
    const list = document.querySelector('.user-list');
    if (!list) return 'nolist';
    const max = list.scrollHeight - list.clientHeight;
    if (list.scrollTop >= max - 4) return (max < 300 && items.length < 8) ? 'wait' : 'bottom';
    list.scrollTop = Math.min(max, list.scrollTop + 300);   // ⚠️ 细步 300px；800px 会跳过中间项（实测漏人）
    return 'scrolling';
  }, 姓名);
  if (r === 'clicked') clicked = true;
  else if (r === 'bottom' || r === 'nolist') break;
  else await page.waitForTimeout(r === 'wait' ? 2000 : 600);
}
// 之后必须等 2.5s 左右再读，并核对 .conversation-main 的头是不是这个人
```

- ✅ **切完必须核对 `.conversation-main` 的姓名**，否则会在别人的会话里说话。
- 列表滚到底还会出现更早的历史会话（`.user-list` 虚拟滚动 + 「滚动加载更多」）。
- **搜人名一律用严格前缀匹配 `startsWith(name + "_")`** —— 搜「王海」会同时命中「王海洋」。

---

## 5. SOP · 读消息

- 只读 `.chat-message-list` 里的**结构化文本**，**不要看列表摘要** —— 摘要会漏。
- 按需截取尾部；长会话可只读最后 300–400 字。
- 发送方看「我 / 对方」与「已读」标记；时间戳在该条消息上方。

---

## 6. SOP · 发消息

```
1) 切到目标会话（§4），核对 .conversation-main
2) click  #boss-chat-editor-input
3) keyboard.insertText(文本)          ← 不要逐字符 type，慢且易触反骚扰
4) click  .submit-content .submit
5) 回到 .chat-message-list 确认消息已出现且状态为「送达」
```

- **逐人复制粘贴定制文本**；**不要**把同一段发给多人。
- 每条注意（★ **2026-09-23 口径，已取代旧说法**）：**零自我介绍、不复述对方信息、只留一个动作**
  （如 `简历发我一份吧。` / `base 上海可以吗？` / `有顶会论文或开源产出吗？`）；**≤ 1 行**。
- 发出前**必读** `话术-最终版.md` 与 `USER.md` 的边界。


### 6.1 SOP · 求简历（**两段式，且必须先发起过沟通**）

```
1) 确认该会话「已发过至少一条消息」—— 未沟通时按钮是灰的（同组 换电话/换微信/约面试 也全灰）
2) page.click('.operate-exchange-left .operate-icon-item[d-c="61025"] .operate-btn')
3) 等 ~1.5s，核对气泡真的展开：.exchange-tooltip 的 getComputedStyle().display === 'block'
   ⚠️ 不要用 offsetParent 判（气泡 position:fixed → 恒 null）
4) page.click('.operate-exchange-left .operate-icon-item[d-c="61025"] .exchange-tooltip .boss-btn-primary')
5) 等 ~4s，确认消息区出现「简历请求已发送」；没出现就如实记「未发出」，不许假装成功
```

- 🚫 同组还有 **「约面试」**（禁区，永不点）、**「换电话 / 换微信」**（同样不许点）。
- 参考实现：`%TEMP%\boss_scan\ask_resume.js`（4 人以内一次一人一确认，跑完写 JSON 报告）。

---

## 7. SOP · 下载附件简历并归档

```
1) 切到目标会话（§4）→ 核对 .conversation-main；确认会话里存在文本「点击预览附件简历」
2) 监听 response（URL 含 preview4boss，或 content-type 含 application/pdf）→ click 该入口
3) 取 response URL —— ⚠️ 它是 **PDF 查看器页**（`content-type: text/html`）：
   https://www.zhipin.com/bzl-office/pdf-viewer-b?url=<encoded 直链>
   → 用 decodeURIComponent 解 url 参数，得到真直链
     /wflow/zpgeek/download/preview4boss/{geekId}?d=…&id=…&authType=…&previewType=…
   → 补 https://www.zhipin.com 前缀。⚠️ 直链带**签名参数**，**禁止截断**（截了必失败）
4) 页面内 `fetch(直链, { credentials: 'include' })` → arrayBuffer → base64 回传 → node 写盘
   （备选：注入 <a href=直链 download=文件名> → evaluate 点击 → waitForEvent('download') → saveAs）
5) 用 JS 隐藏含 iframe 的预览容器 → 复位弹窗（**只做 DOM 隐藏**，不点关闭/其它控件）
6) 校验：文件以 %PDF- 开头、大小合理（可与旧档 Get-FileHash 比对）
```

- **归档路径（★ 2026-09-27 改 · 扁平 + 文件名带日期；分类隔离保留）**：`简历\<实习生|社招>\<YYYY_MM_DD>_<Boss 卡片上的原文件名>`
  - 分类依据 = **Boss 会话头「沟通职位」**（投「大模型预研实习生」→ `实习生\`；投「大模型 / Agent算法工程师」「AI+EDA研究员」→ `社招\`）；
  - **不再建日期子目录**（刘杨 2026-09-27：「日期由文件名体现」，如 `2026_09_27_张三.pdf`）；
    拿不到原名才用 `<日期>_简历_<姓名>.pdf`（旧档 `简历_<姓名>.pdf` 已统一加日期前缀）；
  - **日期 = 下载日期（Boss 页面时间）**；重名加序号（`2026_09_27_2_xxx.pdf`），**永不覆盖已有档**；
  - **只收刘杨给的范围**（实习 = S 级；社招 = 一/二档 + **刘杨点名的「未入档」A 组**）；
  - ⚠️ 工作区换过（`C:\Users\liuyu\HR` → `c:\Users\liuyu\recruit`）：**写当前工作区的 `简历\`**；历史档留在 `HR\简历\`，**只把范围内**的复制进来；
  - 📋 **两个分类目录各维护一个 `README.md`**（清单：姓名 / 档位·论文 / 沟通职位 / 文件名 / 下载日期 / 状态）。
- 🧰 **现成实现**：`%TEMP%\boss_scan\download_resume.js`（**工作区同步留副本**：`download_resume.js` / `send_msg.js` / `ask_resume.js` 三个都在 `c:\Users\liuyu\recruit\`，随 Git 备份；改完 `%TEMP%` 版记得 `Copy-Item` 覆盖回来）
  （`BOSS_NAMES_FILE` 名单文件 · `BOSS_CATEGORY=intern|social` 决定归档到 `实习生\` / `社招\` · `BOSS_DRY=1` 只探测不下载 ·
  `BOSS_OUTDIR` 覆盖归档目录 · `BOSS_REPORT5` 报告路径 · 报告含 `attachEntries` / `pdfs` / `ok` / `bytes`；
  **cookie 只走 `BOSS_COOKIE` 环境变量，不落盘**）。
- ✅ **实测（2026-09-26）**：缪铭凯 194,845 B（**SHA256 与 2026-09-19 旧档完全一致**）· **毕钰** 378,711 B —— 链路正确。
- ⚠️ **脚本侧踩过的三个坑（已修）**：
  1. `content-type` 不是 PDF（见上 `pdf-viewer-b` 那条）→ 必须解 `url=` 参数；
  2. **虚拟列表「加载更多」**：滚到底后**不要立刻停** —— 老会话（如王海 / 顾嘉伟）要再等 ~2s 才追加进来；
     改成「到底 → 记录 `scrollHeight` → 等 2s，高度不变才算到底（连续 4 次）」，修后名单命中率 **11/11**（修前 4/11）。
     每次运行较慢（名单越长越慢，**一批 ≤10 人**跑更稳，超时就让它在后台跑完再读报告 JSON）。
  3. 🚨 **点「点击预览附件简历」入口，别用 `page.click('#挂过 id 的元素')`**（2026-09-26 实测：4 人各 30s 超时）——
     Boss **会重渲染会话消息区**，挂上的 `id` 随即失效（`waiting for locator('#__dl_attach__')`）。
     ★ 改为**在同一个 `evaluate` 里就地 `el.click()`**：先向上找最近的可点击祖先（`A` / `BUTTON` / class 含 `btn|link`，最多 4 层），
     再 `waitForResponse`（`preview4boss` 或 `application/pdf`）→ 重跑 **4/4 成功**。
- ✅ **实测（2026-09-26 社招第 3 批）**：**19 人名单一轮抓下 5 份** —— 马佳旗 147,922 B（原名 `简历（202609）.pdf`）·
  张海鹏 862,293 B（原名）· 王志伟 285,573 B · 葛建帮 1,946,873 B · 杨昆鹏 391,388 B（均 `%PDF-` 开头）。
- 若对方还没同意收简历，会话里会有「对方想发送附件简历给您，您是否同意」卡片 → **卡片未处理前拿不到简历**。
- 🚫 **不要**调 `/wapi/zpgeek/resume/...` 批量拉简历（独立风控 + 配额，返回 `code 7`）。

---

## 8. SOP · 采集候选人

- 接口（**必须页面上下文 `fetch`**，因为需要 `POST /wapi/zppassport/set/zpToken` 生成的 `__zp_stoken__`）：
  - `POST /wapi/zprelation/friend/filterByLabel` → 全部候选人 ID
  - `POST /wapi/zprelation/friend/getBossFriendListV2.json`（body `friendIds=id1,id2,...`）→ 详情 + `securityId`
  - `POST /wapi/zpchat/boss/userLastMsg`（body `src=0&friendIds=...`）→ 最后一条消息
- 输出：`boss_candidates.csv` / `boss_candidates.json` → 再 `python screen.py` 出分级结果。
- ⚠️ `degree` / `lastWorkExpr` / `expectSalary` 在 `getBossFriendListV2` 里**都是 null**，学历与经历**必须问本人或看简历**。

---

## 9. 发送纪律（违反会被限流）

| 规则 | 值 |
|---|---|
| 每批人数 | ~~≤ 2–3 人~~ → ⚠️ **2026-09-26 刘杨放宽：「不需要每批三人，可以更多」** —— 放宽后**仍必须**：① 逐人复制粘贴定制文本（不群发）；② **每人之间保留 20–30s 停顿**；③ **全程盯风控信号**（`code=36` / 跳 `bticket` / 登录态失效 → **立即停手**）。 |
| 批间隔 | **≥ 60 分钟** —— ⚠️ **本轮（2026-09-26）刘杨只放宽了「人数」**，间隔沿用（当日实测：一轮内连发多人，`gap 20s`，未见风控）。 |
| 首句 | **必须因人而异** |
| 内容 | 不群发、不雷文、不发微信号/邮箱 |

> 触发风控的表现：`code=36` 安全验证、跳 `bticket`、登录态被作废。此时**立刻停手**，记进 `发送记录.md`，等人工过验证。

> ★ **触达范围也要「点名」**（2026-09-26 补）：刘杨授权的是 **「社招学校不错的话可以先打招呼要简历」** ——
> 「学校不错」我按**最高学历院校**落成三组：**A 组 = C9 / 985 / 海外 QS 前 100（2026-09-26 授权）**、**B 组 = 211（2026-09-27 点名后已发）**、其余 14 人（**未获点名 → 不动**）。
> ⚠️ **授权不等于「把整个池子都发了」** —— 分层口径要写进 `发送记录.md`，**不放心的组先问，不自行扩大**（同 §11 最后一条）。
> 🔁 **环境变量会跨命令行残留**：只读探测的 `BOSS_DRY=1` 会被下一轮真下载"继承" → 报告看着成功、磁盘 0 文件。
> **每次动工前显式设置**（真下载 `BOSS_DRY='0'`），跑完**三查**：报告 `ok/bytes` → 磁盘文件数 → `%PDF-` 头。

---

## 10. 记忆维护 SOP（每次会话都要做）

**收尾三件事：**

1. **写情景记忆** → `memory/<Boss日期>.md`
   追加：观察到什么、做了什么、原文、结果、失败与误操作。
2. **更新台账** → `发送记录.md`（**只追加**，不改历史；更正也以追加说明形式写）。
3. **必要时提升到长期记忆** → `MEMORY.md`
   只有**稳定、会反复用到**的结论才提升（如：新达标者、新的判定口径、新的铁律、新发现的选择器）。
   提升时在 `DREAMS.md` 里留一条审核记录（哪条从哪来、取代了什么）。

**写入位置速查：**

| 信息类型 | 去处 |
|---|---|
| 刘杨的稳定偏好 / 授权边界 | `USER.md` |
| 非档案的稳定事实、决策、教训 | `MEMORY.md` |
| 当天细节、观察、原文、运行上下文 | `memory/YYYY-MM-DD.md` |
| 需要「条件触发」的未来动作 | `README.md` 待办 / `MEMORY.md` 未决 |
| 什么被整理进了长期记忆 | `DREAMS.md` |

---

## 11. 禁区（不要做）

- 🚫 点 **「约面试」/「发送面试邀请」** 及会话里的面试邀请草稿。
- 🚫 批量 / 群发消息。
- 🚫 新建 context 去操作 Boss。
- 🚫 调简历接口批量拉取。
- 🚫 改写 `发送记录.md` 的历史条目。
- 🚫 在没跟刘杨确认口径前，自行判定某人「达标 / 不达标」并据此行动。
- 🚫 把 cookie、`securityId` 这类凭据写进记忆文件或 README（**工作区可能被提交到 Git**）。

---

## 12. 收工自检

- [ ] 我是否核对过 `.conversation-main`，确认没在别人的会话里说话？
- [ ] 发出的每条消息，是否都确认了「送达」？
- [ ] 下载的 PDF 是否 `%PDF-` 开头、大小合理、放对了日期目录？
- [ ] `发送记录.md` 是否已追加本轮？
- [ ] `memory/<今天>.md` 是否已写？
- [ ] 有没有**误触**过任何「同意 / 拒绝 / 求简历 / 约面试」控件？（有就如实写进台账）
- [ ] 有没有需要刘杨决策的口径问题？写进 `README.md` 待办 + `MEMORY.md` 未决。
