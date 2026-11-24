> 📌 索引：**§A.49 = 2026-11-24 15:5x（第 347 轮 · **`common.py` 带着上一轮 `IMG` 常量 ⇒ 两次传错图 / 删图正解 = 点图选中后点 `.ttcore-remove-blot` / `setFileInputFiles` 只对 `ids[0]` / 首勾会把默认「头条首发」点掉**）**
> 📌 索引：**§A.48 = 2026-11-24 13:0x（第 346 轮 · 插图必须先点 `.syl-toolbar-tool.image` / `input[type=file]` 有 2 个会上传 2 份 / `ttcore-remove-blot` 删多余图 / `.pgc-img` 与 `.pgc-img-wrapper` 并存 / Python 里没有 `t.indexOf`）**
## §A.49 第 347 轮实测（2026-11-24 15:5x · 5 条 · **传错图 / 删图 / 文件输入 / 声明回勾 / 发布后再验**）

1. 🖼 **每轮先核对 `IMG`**：把上一轮 `/tmp/rNNN/common.py` 整份拷到新目录时，里面的 `IMG = …/imgs/<上一轮文件>` 会一起带过来 ⇒ 本轮连续两次把**上一轮的模型基准表**上传成本轮配图（`PANEL_IMGS` 回显 `nw:1080,nh:1059` 才发现）。规矩：**复制后立刻 `grep '^IMG' common.py` 并 `python3 -c "import common;print(common.IMG)"`**；上传后**先读面板回显的 `nw×nh`**，与本地图 `struct.unpack('>II')` 尺寸一致再点「确定」；发布前必看 `img_done` 截图。
2. 🗑 **删图正解**：hover 图片只出现「编辑 / 搜图」；删除角标 `.ttcore-remove-blot` 在**点选图片之后**才挂出来（20×20，位于图框右上角）⇒ 先点图中心，再查 `document.querySelector('.ttcore-remove-blot')` 坐标并点击。
3. 📂 **一次只传 1 张**：面板打开后 `input[type=file]` 有 2 个，直接对 `ids[0]` 设文件即可（旧的错误做法：`files:[IMG]` 同时命中两个 input，或上一张没清空）。稳妥写法 = 先把每个 input `setFileInputFiles {files: []}` 清空，再只对 `ids[0]` 设目标文件。
4. ☑️ **声明首勾会「点掉」默认项**：「头条首发」进页时默认已勾（`on:["头条首发","发布得更多收益"]`）⇒ 按 label 文本点击会把它关掉。规矩：点之前先读 `input.checked`，已勾就跳过（本轮靠 `DECL` 回读发现才补回）。目标态 `on:["头条首发","发布得更多收益","引用AI"]`。
5. 🔎 **新稿公开页会先回落首页**：15:0x 打开 `/article/<id>/` 得 `url:https://www.toutiao.com/`、`DECL found:false`；后台转「已发布」后重跑即 `artH 1594 / broken:0 / DECL found:true` ⇒ **判据以「后台状态 = 已发布」之后那次公开页读数为准**，回落首页记「审核中、未验出」，不记失败。


> 📌 索引：§A.46 = 2026-11-24 09:5x（第 344 轮 · **submit-btn disable 是 CSS 类 / cdp.evaluate 内联中文正则易 JSERR / 评论框 insertText 后内容归零 / 发布链路一次成型**）· §A.45 = 2026-11-24 07:4x（第 343 轮 · **取图复核需完整 UA+Referer / 新稿 id 从 `.article-card` 取 / RSS-only 条目写「图片：无」/ 转已发布即复核四硬标准**）· §A.44 = 2026-11-23 21:5x（第 342 轮 · **IT之家漏正文兜底 / `PUBID` 恒 NONE / 自赞先 navigate / 声明正判据读 label 文本**）· §A.43 = 2026-11-23 18:5x（第 341 轮 · **`value="3"` 有两个复选框**）· §A.42 = 2026-11-23 15:3x（第 340 轮 · 并发接续核验）· §A.41 = 2026-11-23 12:0x（第 339 轮）· §A.40 = 2026-11-23 10:0x（第 338 轮）· §A.39 = 2026-11-23 07:0x（第 336 轮）· §A.38 = 2026-11-22 21:3x（第 335 轮）· §A.37 = 2026-11-22 18:0x（第 334 轮）· §A.36 = 2026-11-22 15:3x（第 333 轮）· §A.35 = 11-22 15:2x（第 332 轮）· §A.34 = 11-22 12:3x（第 331 轮）· §A.33 = 11-22 09:3x（第 329 轮）· §A.32 = 11-22 07:3x（第 328 轮）· §A.31 = 11-21 18:0x（第 326 轮）
## §A.48 第 346 轮实测（2026-11-24 13:0x · 6 条 · **插图入口 + 重复上传 + 删多余图 + git 共享副本纪律**）

1. 🖼 **插图入口 = `.syl-toolbar-tool.image`**（`document.querySelector('.syl-toolbar-tool.image')`）。按可见文本找 `图片` **找不到**（工具栏图标无文本节点）；不点它，面板不展开、`input[type=file]` 数量为 **0**，`s3b_upload_full.py` 会静默跳过并打出 `FILEINPUTS 0 / IMG {n:0}`。
2. ⚠️ **面板打开后 `input[type=file]` 有 2 个** ⇒ 一次 `DOM.setFileInputFiles(files=[IMG], nodeId=ids[0])` 会**上传两份同图**（实测 `已上传 2 张图片`）。只想要 1 张时：上传后数 `img.offsetWidth>0`，多余的删掉。
3. 🗑 **删多余图**：hover 到那张图 → 图框右上角出现 `ttcore-remove-blot` 角标（不在 DOM 文本里，也不带 `del/close` 类名）→ 点 `rect.x+宽度/2+230, rect.y-225` 或直接点角标中心。删完复查「可见 img 数 == 1」。
4. 🧩 **`.pgc-img`（隐藏模板，`offsetWidth=0`）与 `.pgc-img-wrapper`（可见图）并存** ⇒ 判「几张图」只能数 `offsetWidth>0` 的；`editor.querySelectorAll('img').length` 会虚高一倍（实测 `n:4` 实际可见 2 张）。
5. 🐍 **本地脚本是 Python，不是 JS**：从旧脚本抄 `t.indexOf('已上传')` 会 `AttributeError: 'str' object has no attribute 'indexOf'`（脚本前半段已执行完，上传已发生）⇒ 用 `t.find()`；失败后**不要重跑上传**，先查 `img` 数。
6. 🔀 **git 共享副本纪律（同日事故）**：`git pull --rebase --autostash` 中断后 worktree 会被拨到 `origin/main`，本线刚写的文件「看起来消失」；🚫 不要跑 `git read-tree` / `reset`（会造出 `AUTO_MERGE` 把后续 pull 全卡住）；先看 `.git/rebase-merge`（orig-head / autostash），再只保留本线冲突行、其它线文件 `git checkout HEAD -- <file>`。

## §A.46 第 344 轮实测（2026-11-24 09:5x · 4 条 · **「disable」是类名不是属性 / 内联中文正则触发 JSERR / 评论框 insertText 后内容归零 / 本轮带 1 图发布链路一次成型可作模板**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **`submit-btn disable` 里没有 `disabled` 属性**：`x.getAttribute('disabled')` 返回 `null`，但按钮点不动。判活只能看 `className` 含 `disable` **且** 输入框是否真有内容；`if (!btn.disabled)` 会误判成「可点」 | 本轮 `CMT {btns:[{t:评论,cls:''},{t:评论,cls:'submit-btn disable',dis:false}]}` |
| 2 | ⚠️ **`cdp.evaluate` 的内联中文正则/转义易触发 `JSERR SyntaxError: Invalid or unexpected token`**（shell→python→JS 多层转义被打断）⇒ JS 里中文一律写 `\uXXXX`；且 `python3 - <<PYEOF` 的块内若含 `\uXXXX` 字面量，python 自身会报 `unicodeescape` 错 ⇒ 这类文本改用 editor 落盘再 `cp`/拼接 | 本轮 `chknotice` 首跑 JSERR；改 `\u` 后 `NOTICE {hits:[违规], lines:[正文自述三家违规]}` 正常 |
| 3 | ⚠️ **评论框 `Input.insertText` 后内容归零**：真实点击 `div.comment-textarea`（`POS {x:862,y:2280}`）后 `insertText`，再读仍为空、提交键未启用 ⇒ 与「需 user-activation」一致；🚫 输入为空时不盲点提交（避免空评/重复评） | `AFTERTYPE {btns:[… submit-btn disable …], ta:['']}` |
| 4 | ✅ **带 1 图的发布链路一次成型（可作模板）**：`s1_fill`（标题 + `innerHTML` 一次灌段）→ `s3a/s3b` 插图 + 确定 → `cap2` 图注 → `setdecl`（按可见文本「引用AI」真实点击）→ `chkdecl` 回读 → `s5_prev` `hasConfirm` → `s6_confirm` 只点一次 → `dom_list` 从 `.article-card` 取 18–19 位 id → `chkpub` 四硬标准 → `like` 自赞。本轮零返工，`共 96 → 97 条内容`、四硬标准 4/4 | `/tmp/r344/*.py`；`news/2026-11-24.md`「第 344 轮 · 发布记录」 |

## §A.45 第 343 轮实测（2026-11-24 07:4x · 4 条 · **取图复核必须带完整 UA + Referer（只 `Mozilla/5.0` 会 403）/ 新稿 id 要从 `.article-card` 取、`a[href*=item]` 对新稿为空 / 只按 RSS 摘要入账的条目必须写「图片：无」/ 转「已发布」后 id 才进列表 DOM**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **图片存活复核必须带完整 UA 字符串 + `Referer`**：只用 `curl -A 'Mozilla/5.0'` 时 `img.ithome.com` 返 **403 `text/html`**、`i.qbitai.com` 返 **403 `application/xml`**，极易误判「图挂了」；换成 `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/155.0.0.0 Safari/537.36` + `-e https://www.ithome.com/`（量子位用 `-e https://www.qbitai.com/`）后全部 `206` + `Content-Type: image/png\|jpeg` | 本轮 5 个 URL 两次复核对照：403 → 206；`Content-Range` 与 `news/2026-11-24.md` 登记一致 |
| 2 | ⚠️ **`getid.py` 读 `a[href*="/item/"]` 只返回旧稿**：新稿「审核中」时**不在 `<a>` 里**（`LINKS` 前 6 条全是前几轮的）⇒ 会误以为「没发出去」而重复发布。**正解** = 读首张 `.article-card` 的 `innerHTML`，用 `/\d{18,19}/g` 抓 id（本轮 `ids:["7711506337942782483"]`），再拼 `https://www.toutiao.com/article/<id>/` | 本轮发布后 `LINKS` 无新稿 → `dom_list.py` 从卡片取到 id，其后 `getid` 首行变「已发布 已推送」 |
| 3 | ✅ **只按 RSS 标题+摘要入账的条目，`🖼 图片：无` 并注明「未抓正文」**：本轮 `231`/`094`/`088` 三条未抓正文，一律写无图，不用别的新闻的图顶替（配图令 ①）。同时**顶部「配图覆盖」必须与条目实数一致**（本轮初稿口算 12/1，实际 9/4，落盘后用脚本数 `^  🖼 图片：` 行核对后更正） | `news/2026-11-24.md` 首行「有图 9 条 / 无图 4 条」+ 脚本核对 `with 9 none 4` |
| 4 | ✅ **「已发布」后 1 分钟内公开页即可复核四硬标准**：本轮 07:03 提交 → 07:4x 复核 `P1 artH:1541` / `IMGS {n:1,vis:1,broken:0,nw:1200,nh:630,w:676,h:355}` / `DECL {found:true}` / `NOTICE {hits:[]}` ⇒ 4/4；无需等到下一轮（与 §A.39/A.41 的「审核中先重定向首页」区分：**转「已发布」后**再抓公开页） | `chkpub343.py` + `pub.jpg` 目视图完整、图注在下方 |

## §A.44 第 342 轮实测（2026-11-23 21:5x · 4 条 · **IT之家个别页 `fetch.py` 漏正文 ⇒ 用 `id="paragraph"` 兜底 / `s6` 的 `PUBID` 恒 `NONE` / 自赞前必须显式 `Page.navigate` / 声明勾选与「三图」的辨析法：读 `closest(label).innerText`**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **`news/ith_extract.py` 对个别 IT之家页会「状态 200 但 `chars` 很小、`text` 为空」**（本轮 `1/030/985` 报 `chars=489`、正文空白），并非 404、也不是懒加载——改用 **`h.find('id="paragraph"')` 切片 + 去标签** 后取到正文 901 字。判法：`chars < 600 且 text 为空` ⇒ 先按此兜底再决定「不入账」，别直接写「未读到正文」 | 本轮 `985` 首抓空、二次定位成功；入账稿已带完整 Omdia 数字 |
| 2 | ⚠️ **`s6_confirm.py` 的 `PUBID` 打印恒 `NONE`**：点完 `确认发布` 后页面**跳回 `/graphic/articles` 列表**（URL 不含文章 id）⇒ 文章 id 必须从列表 `a[href*="/item/"]` 里按标题取，去掉 `?enter_from=…` 即公开页 `/article/<id>/`。🚫 不要因为 `PUBID NONE` 就重复点发布 | 本轮 `s6`：`AFTER {url:…/graphic/articles}` + `PUBID NONE`；`getid.py` 读 `LIST {cnt:"95"}` 与 `LINKS [{t:"一个会说话的毛绒兔子…", h:"…/item/7711359550640652843/?enter_from=mp_group_management"}]` |
| 3 | ⚠️ **公开页标签页可能被其他脚本导航过**（本轮 `like342` 首次 `RE1 NO`、`POS NO`，`URL` 读出来是 `/graphic/articles`）⇒ 自赞 / 评论前**必须显式 `Page.enable` + `Page.navigate` 到目标公开页并等 10–13 s**，再读 `div.detail-like`；否则会静默「点空」却以为已赞 | 修后 `RE1 detail-like \| 赞` → `RE2 detail-like like \| 1` |
| 4 | ✅ **声明勾选的正判据 = 读每个 `input[type=checkbox]` 的 `closest('label').innerText`**，打印「已勾集合」再核对：本轮 `DECL {on:["头条首发","发布得更多收益","引用AI"], txts:[…"3:引用AI"…]}` 且「三图」不在 `on` 里 ⇒ 一次确认到位（§A.43 第 1 条的坑未复发）。比看截图更可靠、可入账 | 本轮 `chkdecl.py` |



## §A.43 第 341 轮实测（2026-11-23 18:5x · 4 条 · **`input[value="3"]` 有两个：封面「三图」+ 声明「引用AI」 / 「已发布」的「修改」可点（`?from=edit` 才是编辑原文） / 预览页不渲染声明已被公开页证实 / 封面裁切 <672×462 平台不拦**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **发布页里 `input[type=checkbox][value="3"]` 有两个**：一个属「展示封面 → 三图」，一个属「作品声明 → 引用AI」。`document.querySelector('input[value="3"]').click()` 或 `(closest('label')).click()` 会**勾到「三图」**，回读 `checked:true` 造成「已勾」的假象 ⇒ 公开页 `DECL found:false` 才发现。**正解**：`[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&e.innerText.trim()==='引用AI')[0]` 取其坐标**真实鼠标点击**，再 `input[value="3"]` 中最靠近该 `span` 的那个 `checked` 为 `true`，并截图看「引用AI」前是否红勾 | 第 341 轮 `setai.out`：`BEFORE {"ck":false}` → `AFTER {"ck":true}`，但公开页 `DECL {found:false}`；改用 `edset3.py` 按 `span.byte-checkbox-inner-text` 文本点击后截图 `edset3.jpg` 见红勾、`editing` 页 `ck:true` |
| 2 | ✅ **「已发布」文章的「修改」可用**（订正 §A.42 第 1 条的适用范围）：该行「修改」是普通 `span`（`className:''`，父级文本 `查看数据 查看评论 修改 更多`），**真实鼠标点击会开新标签页** `/profile_v4/graphic/publish?from=edit&pgc_id=<id>`，标题 / 17 段 / 正文图 2228×394 全在（`共 825 字`）。勾好声明后点右下「发布」→ **直接回列表、无二次确认弹窗**，后台行变「修改审核中」。⚠️ 别用 `?enter_from=mp_group_management&pgc_id=` 那个（会开空白新稿，§A.42 第 2 条仍有效）—— 两者是不同 URL | 第 341 轮 `mod2.out` → 新标签 `05C870FC…` `ST {title:'936个AI科学家…', ps:17, words:'共 825 字'}`；`edpub.out` `DIALOG {hasConfirm:false, url:…/graphic/articles}` + `edpub.jpg` 见「修改审核中」 |
| 3 | ✅ **「预览页不渲染声明」由公开页直接证实**（结 §A.42 第 3 条的悬案）：15:04 那篇 18:0x 转「已发布」后，公开页 `DECL {found:true, snip:"作品声明：内容由AI生成"}`、图 864×596 `broken:0`、`NOTICE {hits:[]}` ⇒ 四硬标准 4/4；即**预览页 `found:false` 不能判「声明缺失」**，只能发布后查公开页 | 第 341 轮 `chkpub4.py` → `P1 {canon 一致, artH:2482}` / `DECL found:true` / `pub.jpg` |
| 4 | ⚠️ **封面裁切尺寸 <672×462 时平台不拦发布**：正文图 2228×654，封面自动裁成 **506×394**（低于面板建议的 672×462），仍可正常「预览并发布」并「已发布」；但样张偏小可能影响推荐。另：超宽横幅图（2228×394）在公开页渲染成 **676×120** 一条，观感偏弱 ⇒ 下轮优先选宽高比 ≤1.7 的图 | 第 341 轮 `CHK {cov:{nw:506,nh:394}}`；公开页 `IMGS {nw:2228, nh:394, w:676, h:120}` |

## §A.42 第 340 轮实测（2026-11-23 15:3x · 4 条 · **审核中「修改」是 disable / `publish?pgc_id=` 会新建空稿 / 预览页不渲染 AI 声明 / 开工先比 `/tmp/rNNN` 与后台计数**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **文章「审核中」时，后台列表该行的「修改」是 `<span class="disable">`**，按坐标/文本点它**不会跳转**（4 次全 `MODBTN NO`，页面也不动）。判法：读 `.article-card .article-action-list` 的 `outerHTML`，`<span class="disable">修改</span>` ⇒ 不可编辑，**只能等审核结束**（`已发布` 行才是 `<span>修改</span>`） | 第 340 轮 `probe19/20.out`：`<div class="count-wrapper"><div class="article-action-list"><span class="disable">修改</span><span>删除作品</span>` |
| 2 | 🚫 **`/profile_v4/graphic/publish?enter_from=mp_group_management&pgc_id=<id>` 不是「编辑该篇」，而是开一个空白新编辑器**：实测 `CHK {6 个复选框全 false}`、`共 0 字`、标题空 ⇒ 若在此页再走 `s1_fill`+`s6_confirm` 就会**多出一篇重复/空文**。**严禁**用它补改已发文章 | 第 340 轮 `dis2.out`：`U ...publish?…pgc_id=7711259016902623785` + `CHK {引用AI:false,…} words:"共 0 字"`；`dis3.jpg` 目视空白编辑器 |
| 3 | ⚠️ **「图文预览页」（`/feoffline/mp-article-preview/graphic?pgc_id=…`）不渲染「作品声明」**，即使发布时勾了「引用AI」也查不到 ⇒ 用 `DECL found:false` 判「AI 声明缺失」是**会误判的**；正确判据只在**公开页** `/article/<id>/` 上取。预览页可用来验图/验正文/验图注。另：`iframe.src` 是协议相对地址 `//mp.toutiao.com/...`，**拼 URL 时不能再补 `https://`**（会变成 `https://mp.toutiao.com//mp…` → 502） | 第 340 轮 `preview_ai.out`：预览页 `decl:-1 hasAI:false`；对照 12:06 公开页 `DECL found:true`；`prevchk3.out` 502 Bad Gateway（**未定论**：本篇当时仍「审核中」，尚未在公开页验证，见 MEMORY 阻塞区 AI-DECL-340） |
| 4 | 🔑 **开工先比对「`/tmp/rNNN` 目录时间戳」与「后台计数 + 首行」**：并发进程可能已经把采集、配图、发布全做完（只是没写 MEMORY）⇒ 本 agent 应**只核验 + 记账**，不重采不重发。另：`news/2026-11-23.md` 追加前必须 `grep -n '第 NNN 轮'`，否则会把同一轮写两遍 | 第 340 轮开工时 `/tmp/r340/` 已有 15:02–15:10 全套（`paras.txt`/`s6_confirm.py`/`after_publish.png`），后台已 `93`、首行 15:04 本篇 |

## §A.41 第 339 轮实测（2026-11-23 12:0x · 4 条 · **去重读数异常先自证 / 自赞连跑会取消 / 抓正文失败≠无图 / 覆盖 `common.py` 要留 `Ctx`**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **`ith_dedup` 报 `SEEN_HIT 0` 时不要直接判脚本坏了，也不要直接当「全是新稿」入账**：判据 = 对每个 `key` 做 `key in open(SEEN).read()`。若**全部 False** 且 `SEEN.md` 里能搜到昨天的 `1/030/72x` ⇒ 是真新一批；落盘本轮 URL 后复跑应见 `SEEN_HIT` 上升，自证去重生效 | 本轮首测 `RSS_ITEMS 60 / SEEN_HIT 0 / NEW 60`；60 条 key 全 False、`1/030/720` 为 True；入账 8 个 IT之家 URL 后复跑 `SEEN_HIT 8` |
| 2 | 🚫 **自赞脚本严禁「同一条命令跑两遍做复核」**：第二跑读到 `detail-like like` 仍会点下去（脚本只按坐标点、不判 class）⇒ **把赞取消**。复核一律用**只读**脚本（只读 `className` + reload），或在 `like.py` 里加「class 已含 `like` 就直接 return」 | 本轮 `like.out` 两段：第 2 段 `RE1 like 1 → RE2 赞`（取消）；第三次点击后 `likechk RE加载 like 1` 确认恢复 |
| 3 | ⚠️ **`ith_extract` 判「有图 / 无图」要先看 `imgs` 明细**：`IMG0` 可能被 IT之家「现场」栏目位图 `https://img.ithome.com/app-images/on-the-sence.png?v=…`（1200×200 通栏）占位 ⇒ 按 §8.2 排除后取正文第 1/2 张 `newsuploadfiles`；正文抓取失败（`status=None / chars=0`）时同样不能写「无图」，要换抓取方式或标「未取得」 | `1/030/784` 首次 `extract` 因误传整个 URL 得 `status=None`；改用 `1/030/784` 路径后 `imgs=6`，其中 `[0]` 即 `on-the-sence.png` |
| 4 | ⚠️ **换轮次目录复制脚本时，`common.py` 必须整份复制后再改字段**：本轮手写 `common.py` 时漏掉 `Ctx` 类 ⇒ `s0_nav` 立即 `ImportError: cannot import name 'Ctx'`。**先 `cp` 再 `sed`/编辑**，改完跑一句 `python3 -c "import common; print(hasattr(common,'Ctx'))"` 自检 | 本轮 `s0_nav.py` 首次执行 `ImportError`；补 `Ctx` 后 `LIST cnt 91` 一次过 |

## §A.40 第 338 轮实测（2026-11-23 10:0x · 4 条 · **footer 浮层把「预览并发布」遮成 `SPAN 定时发布` / 二次点「预览并发布」会清空编辑器 / 后台列表 URL 走 `<a class=title>` / 新标签页复核要手写 `Page.navigate`**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **`预览并发布` 是页面底部 `position:fixed` 工具条里的按钮；正文很长（`sy≈1500`）时，工具条会被顶起并把按钮位置让给「定时发布」（`SPAN`）** ⇒ 按「文本 = 预览并发布」找按钮会落空，按老坐标点会点到 `SPAN 定时发布` 或什么都不发生。**判定法**：先读 `FOOT {footPos:'fixed', footY, sy, ih, vh, title}`；若 `DIALOG {hasConfirm:false, hasClose:false}` 而 `FOUND {"定时发布":[x,y,"SPAN"]}` 同时出现 ⇒ 就是被遮挡，**不要重复点** | 第 337 轮 `once5.out`：`FOOT {'x':1123,'y':933,'footPos':'fixed','footY':899,'sy':1464,'ih':967}` + `DIALOG {"hasConfirm":false}`；`fin2.out`：`FOUND {"定时发布":[998,933,"SPAN"]}` 且 `MODAL {"hasPreview":false}` ⇒ 该轮 09:50–09:54 反复失败、未发出 |
| 2 | 🚫 **同一发布页上第二次点 `预览并发布` 会把编辑器重置**（标题与正文全清，`共 0 字`）—— 因为第 1 次点击其实已打开过编辑/预览态，第 2 次命中「返回编辑 → 关闭 → 重置」的残留 state。**铁律：每篇发布动作在同一标签页只跑一轮**；一旦读到 `共 0 字` ⇒ 关掉该页、`/graphic/articles` → `publish` 重开（`STATE {ed:true, title:"", words:"共 0 字", imgs:0}` 才算干净），**在干净页上重填**，不要在坏页上修补 | 第 337 轮 `tst.out`：`TID CLICK_预览 {'x':894,'y':933,'w':2048,'h':967} hasClose True` → `NEW GEO {"title":"","vw":1186}` ⇒ 编辑器被清空；`dbg2.out` 同源复现 `MODAL {hasPreview:true}` 但正文已空 |
| 3 | ⚠️ **后台 `/profile_v4/graphic/articles` 列表里每行有 2 个同 href 的 `<a>`（一个空文本、一个是 `a.title`）** ⇒ 用「文本 = 标题」筛 `a` 会拿到空的；应 `[...document.querySelectorAll('a')].filter(a=>/graphic|article|item/.test(a.getAttribute('href')))` 再按 `innerText` 匹配，或直接取 `a.title`。拿到的形如 `https://www.toutiao.com/item/<id>/?enter_from=mp_group_management`，**去掉 query 后即公开页 URL**（`/article/<id>/` 与 `/item/<id>/` 等价） | 第 338 轮 `geturl.out`：`{cnt:91, links:[]}`（只用 `href` 且 `innerText` 为空的按 `slice(0,4)` 取了空的链接）；`findlink.py` 打出 `{h:"https://www.toutiao.com/item/7711181219639149092/?enter_from=mp_group_management", t:"第一个报数的公司"}` |
| 4 | ⚠️ **`cdp.cmd_open()` 返回的是 `None`**（内部 `print` 已打出 id）⇒ 想在新标签页里做公开页复核，别用它的返回值；**自己 `cdp.session(tid)` 后手写 `Page.enable` → `Page.navigate` → 轮询 `Page.loadEventFired`（45s 上限）→ `session.close()`** 即可，同一会话上的 `cdp.nav()` 若页面 30s 内没 load 完会抛 `TimeoutError` 而**没真的导航** | 第 338 轮 `s6b_find.py`：`NEWTAB None` → `TypeError: can only concatenate str (not "NoneType") to str`；改用自写的 `chkpub2.py` 后 `P1 {url:/article/7711181219639149092/, canon 一致, artH:3453}` 一次成功 |
| 5 | ✅ **竖长图（898×2161）配图文文章没问题**：编辑器里显示 440×1059，公开页渲染 **676×1627**、`naturalWidth 898` 未裁切、`broken:0`；比「横图」更占屏但图注与正文都正常 —— 只要不是「评论区截图」这类半幅空白图，竖长图可接受 | 第 338 轮 `IMGS {n:1, vis:1, broken:0, nw:898, nh:2161, w:676, h:1627, complete:true}` + `pub_img.jpg` 目视 |

## §A.39 第 336 轮实测（2026-11-23 07:0x · 2 条 · **`corners` 放大到 2400px 后截图必超时 ⇒ 改「定尺视口 + 逐角原分辨率」 / 图注框回读会误命中润色提示语**）


| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **`corners.py` 老写法（img 宽 2400px + 1200×675 视口）在 Chrome 155 上会连续 `Page.captureScreenshot` → `TimeoutError`（`cdp.py:77 sock.recv` 超时），而被截页面只是一个 `about:blank`**；且同一标签页一旦进入该状态，**后续连空页截图都会超时**（`d1/d2/d3` 三个探针都在 `captureScreenshot` 处卡住 60 s）。解法：① **每张图新开专用临时标签页**（`PUT /json/new?about:blank`），跑完 `GET /json/close/<id>`；② 视口固定 **1000×620**，`img` 宽设 **2000px**、用 `left/top` 负偏移逐角取景（4 角 = 左上 / 右上 / 左下 / 右下），**不做 2× 放大**；③ 每次 `captureScreenshot` 显式 `timeout=40`，JPEG `quality=50` | 老 `corners` 连续 3 次 `TimeoutError`；同一 `viewimg`（1180×680 视口、单张 1936×1214）能出图但耗时 **16–20 s**；新写法在**新建标签页**里 4 角各 1 张、每张 **2–3 s** 一次过（`c_TL 33,240 B / c_TR 26,556 / c_BL 29,924 / c_BR 30,292`），`NAT {nw:1936,nh:1214,c:true}` 逐角复核 |
| 2 | ⚠️ **`cap2.py` 的 `ERR` 探针把正文润色提示「建议添加配图」当成配图报错** —— 图其实已上传成功（`IMG {n:2, vis:1, nw:1936, nh:1214}`）时它仍会打印 `ERR ["建议添加配图"]`；判据要看 **`IMG.n` 与图注 `CAP` 回读**，别只看 `ERR` 非空就以为配图失败 | 本轮 `cap2` 打出 `ERR ["建议添加配图"]`，但 `CAP [{"v":"图：IT之家（OpenAI 官方博客截图：对数困惑度曲线）","w":440}]` 且后续公开页 `IMGS {n:1, vis:1, broken:0}` ⇒ 该 `ERR` 是**编辑器右侧「AI 创作助手」的提示语**，不是图片报错（上轮同句也出现过，当时图同样正常） |

## §A.38 第 335 轮实测（2026-11-22 21:3x · 4 条 · **IT之家站内截图别当配图 / 前台 30 s 超时后再起进程会双开 / 正文图不在 post_content 里**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **IT之家稿件的正文图常常不在 `<div class="post_content">` 内**：正文容器里 `<img>` 为 0，图片却在容器之前（`<p>` 之外）或页面其它位置 ⇒ 按配图令优先级 ③「正文页第一个 `<img>`」时应 `grep -o 'img.ithome.com/newsuploadfiles[^"]*'` 全页取，再按语义挑第一张；🚫 不要因为容器内 0 图就写「无」 | 第 335 轮 12 篇实抓中 11 篇容器内 `imgs 0`（`find(post_content) → find(ad-tips)` 切片法），全页 grep 后 `702` 得 4 张、`696`/`677`/`683` 各得 1 张；`711`/`706`/`704`/`699`/`692` 全页确实 0 张 ⇒ 记「无」 |
| 2 | 🚫 **IT之家稿件里的「评论区截图 / 表单截图」不能作发布配图**：这类图常常半幅空白、右缘被截断（窄屏截图嵌在宽栏里），看图一眼能认出 ⇒ 换同文第二张候选 | `1/030/702` 首图 `8f358ec4…jpg`（1267×501 · 75,839 B）`viewimg` 目视为评论区三条留言 + 下半大量空白 + 右侧被切 ⇒ 弃用；第二张 `55563314…jpg`（1440×641 · 302,695 B，账号主页）干净 ⇒ 采用 |
| 3 | ⚠️ **前台命令 30 s 超时 ≠ 作业被杀；此时**不要**再 `nohup` 起第二个同名脚本，否则两个进程抢同一个标签页**：先 `pgrep -af <脚本>`，确认没有残留再起 | `list.py` 前台 30 s 超时后即起 `nohup setsid timeout 120 python3 list.py`，`pgrep` 只看到新进程（旧的已随 shell 结束）⇒ 读数正常；若旧进程仍在，两次 `Page.navigate` 会互相打断（`s0` 曾因此读到 `about:blank`） |
| 4 | ✅ **`s0_nav.py` 一次跑通「列表 → 发布页」两跳，且发布页读到 `STATE {ed:true,title:"",words:"共 0 字"}` 才算干净**；标题 / 正文 / 图 / 图注 / `引用AI` / 预览 / 确认 七步各自独立会话，每步只读回显 | 21:32 `s0` 一次成功；`s1` `CHK {ps:16, words:"共 1408 字"}`；`s3b` `已上传 1 张图片` → `IMG {n:2, vis:1, nw:1440, nh:641, w:440, h:196}`；`cap2` 回读图注 29 字；`setai` `引用AI false→true`；发布 **只点一次** ⇒ 后台 `88 → 89` |

## §A.37 第 334 轮实测（2026-11-22 18:0x · 3 条 · **大页截图改 JPEG / 换目录必核对脚本清单 / 下载的图必须目视**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **`Page.captureScreenshot` 偶发 `TimeoutError`，但文件往往已落盘**：600 KB 的 PNG 在 30 s 内没被 `_recv_frame` 收完（`cdp.py` 第 77 行 `sock.recv` 超时）⇒ 先 `ls -l` 看文件大小再决定是否重跑；长页面（发布页 / 公开页）改 `{'format':'jpeg','quality':60}` 小图，单次约 2–3 s | `viewimg.py` 报 `TimeoutError`，但 `viewimg.png` 已写出 600,696 B 且内容完整；同一页改 JPEG 后一次成功 |
| 2 | 🚫 **换轮次目录时只 `cp` 了部分脚本**：`s3b_upload.py` / `setai.py` / `like.py` 漏拷 ⇒ `python3: can't open file`。动手前先 `ls /tmp/rNNN/*.py` 与上一轮目录对照，再按 `s0 → s1 → s3a → s3b → cap2 → setai → s5 → s6 → list → chkpub → like` 顺序跑 | 第 334 轮 `s3b` 首次执行立即 `Errno 2`；补齐后 `s3b` 一次成功（`已上传 1 张图片`） |
| 3 | ✅ **下载前选图：同篇首图带 `watermark` 参数 ⇒ 换用本轮另一条已入账新闻的现场图**，并在图注写清来源；🚫 不要用「编辑器 UI 浮标」误判成图内元素 | `1/030/679` 首图 URL 含 `image/watermark,text_QUnnlJ_miJA…` → 弃用；改用 `1/030/653`（蚂蚁阿福大会现场 1440×1080）；`cap3.jpg` 里图右上角 `×` 与图下「编辑 / 搜图」浮标是编辑器 UI，公开页 `pub.png` 无此元素，图内仅有左下角 IT之家站标（图注已注明来源） |

## §A.36 第 333 轮实测（2026-11-22 15:3x · 3 条 · **图注 `insertText` 会静默不落库 / 同一时窗有两段要按增量段处理 / 央视网单稿可能 404**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **图注用 `Input.insertText` 写入后必须回读 `CAP`；若回读为空，用「原生 value setter + `input`/`change`/`blur` 事件」兜底才落库** | `s4_cap.py`：真实点框 `CAPBOX {x:816,y:484,n:1}` → `Input.insertText` → `CAP [""]`（**静默失败**，`ERR []` 也不报错）。`cap2.py`：真实点框 → `FOCUS TEXTAREA | pgc-img-caption-ipt` → `insertText` → 原生 setter 赋值 + 三个事件 ⇒ `CAP [{v:"图：IT之家（小鹏汇天 A868 试飞画面）", w:440}]`，`cap2.png` 目视图注已显示在图下 |
| 2 | ⚠️ **同一个时窗内可能出现「上一轮已收尾 + 本进程再次唤醒」两段**：不要因为「时窗已过」而空转，也不要重复上一轮的采集与发布；按**增量段**处理（只采上一轮收尾之后的新条目、只发一篇新的） | 15:00 时窗：第 332 轮 15:19 已发完并写台账；本进程 15:30 被唤醒 ⇒ 采集「15:19 之后」的 45 条 NEW 入 7 条，另发 1 篇（后台 `86 → 87`）；判据同样只认**后台计数 + 首行标题/时间** |
| 3 | ⚠️ **央视网新闻频道单稿可能直接 404（列表里还在、正文已撤）**：引用前对该 URL 单独 `curl -w '%{http_code}'`，非 200 就不引、改用同事件的 IT之家稿并注明转述来源 | `news.cctv.com/2026/11/22/ARTIQu34TaMWRbDasC2YRF8R261.shtml` → `404 2552 B`；同事件的可信数据空间稿改引 IT之家 `1/030/593`（`200`，含 13 城 / 22 行业 / 28 企业 / 457 数据集 / 136 垂直模型 全口径） |

## §A.35 第 332 轮实测（2026-11-22 15:2x · 5 条 · **别 reload `publish` 页 / `.jpg` 冒充 `.png` 会上传失败 / 失败缩略图不删则「确定」恒 disable / 发布页 `NOTICE` 会命中正文自带词**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🚫 **`publish` 页在 CDP 一侧被导航到 `about:blank` 后，本会话再 `nav('/graphic/publish')` 也不回填**：`s0_nav` 曾读到 `about:blank`（`STATE ed:false`），随后 `s1_fill` 报 `Cannot read properties of null (reading 'focus')`（`.ProseMirror` 为 null）⇒ **重跑一次 `s0_nav.py`（articles → publish）即可恢复**，不要在同一页面上叠加重试 | 15:0x `s0` 首读 `about:blank`；15:08 `s1_fill` `TypeError … 'focus' of null`；15:12 重跑 `s0` → `STATE {ed:true, kids:["P"], words:"共 0 字"}` → `s1_fill` `CHK {ps:23, words:"共 1000 字"}` 一次成功 |
| 2 | 🚫 **扩展名必须与真实图片格式一致：把 JPEG 字节存成 `.png` 会被平台判「上传失败」** | 先下 `.jpg`（157,131 B，`image/jpeg`，800×800），为「复测」直接 `cp` 成 `.png` 上传 → 面板「**上传失败**」红标（缩略图是破图）。改回 `.jpg` 真格式重传即成功（`已上传 1 张图片`，缩略图正常、右上角仅 IT之家站标）。**「发布前只下这 1 张」= 用原始扩展名，不做格式改名** |
| 3 | 🔑 **面板里残留「上传失败」的卡片时，「确定」按钮恒 `disabled`；必须先点该卡片的 `i.image-item-remove` 删掉失败项，再点成功的缩略图选中，`确定` 才解除 disabled** | 失败卡 + 成功图并存时：`OKBTN {dis:true}`，对成功缩略图真实点击 6 次、`li.click()`、`span.click()`、去掉 `pointer-events`、按 `mousePressed` 探针（能读到 `li` 被加上 `opacity:0;visibility:hidden` 的拖拽 helper）全部无效；删掉失败卡后 `COUNT 已上传 1 张图片` → 点缩略图 `OKBTN {dis:false}` → 点确定 `IMG {n:2, vis:1, nw:800, nh:800, w:440, h:440}` 一次成功 |
| 4 | ✅ **上传面板要「开面板 / 点本地上传 / 塞文件」分三段会话，且 `s3a` 只能开面板不能关**：点「本地音频」逻辑同图片；`s3b` 里 `DOM.setFileInputFiles` 塞 `input[type=file]` 后要等 **8–10 s** 让 `mp.toutiao.com/spice/image` 返回 `200 image/jpeg` 再读 `已上传` | 本轮 `s3a_open` `TABS up:[本地上传, 扫码上传]` → `s3b` `FILEINPUTS 2`、`UPMSG 已上传 0 张`（尚未回填）→ 等 10 s 后 `UPMSG 已上传 1 张图片`；`Network` 记到 `POST /spice/image?upload_source=…` `200 application/json` + `GET image-tt-private.toutiao.com/…` `200 image/jpeg` |
| 5 | ⚠️ **公开页 `NOTICE` 关键字会命中正文自身用词**：确认「无版权/搬运/低质警告」要看 `ctx`，不能只看 `hits` | 本篇 `NOTICE {hits:["违规"], ctx:["违规::至今已为超过 50 亿条 AI 生成视频添加标识；违规 AI 内容中，99% 以上…"]}` ⇒ 命中来自正文引述的平台口径，**不是平台警告**；其余三项 `P1 / IMGS / DECL` 全过 |


## §A.34 第 331 轮实测（2026-11-22 12:3x · 4 条 · **插图面板分两段开 / 图注要在图前自己写 / 评论「新路径」也已证伪 / 放大复核前移后生效**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **工具栏「图片」与「本地上传」必须分两次会话点：先点工具栏 → 面板出现（`TABS up:[本地上传/扫码上传]`）→ 下一条命令再点「本地上传」→ 才有 `input[type=file]`** | 同一次会话里「找本地上传 → 点 → 查 file input」会读到 `LOCALUP NO / FILEINPUTS 0 / UPMSG NONE`（面板尚未渲染）；拆成 `s3a_open.py`（点工具栏，读到 `up:[{t:"本地上传",vis:true},{t:"扫码上传",vis:true}]`）→ `s3b_upload.py`（点 `(1489,377)` → `FILEINPUTS 2` → `UPMSG 已上传 1 张图片` → `IMG {n:2, vis:1, nw:1440, nh:810}`）即一次成功 |
| 2 | ✅ **图注要在「图已插入、尚未点发布」时用 `textarea.pgc-img-caption-ipt`（`offsetWidth>0` 那个）写入**；图注是媒体块自带的 `caption`，**不能**当正文段落写 | `CAPBOX {x:816, y:483, n:1}` → `Input.insertText` → `CAP ["图：IT之家（特斯拉 FSD v15 实景视图界面）"]`（19 字）；编辑器里**图下方自动多出一个小段**，这时 `ps` 会由 16 涨到 19（多出 1 个图媒体块 + 1 个图注段）；截屏 `cap_done.png` 目视图 + 图注都在标题下方、正文之上 |
| 3 | 🚫 **「真实点进评论框 + 逐字 insertText」这条新路径也已证伪 ⇒ 评论提交键在 Web 端对该账号恒 `disable`，报 blocker** | 真实鼠标三连（`mouseMoved/Pressed/Released`）点 `.comment-textarea` → `FOCUS DIV | comment-textarea | ce=true`（确认焦点在编辑器内）→ 逐字 `Input.insertText`（每字 0.05 s）→ `ST1 {len:31, btn:"submit-btn disable", dis:true, cmt:"0"}`；再真实点 `(1128,483)` 的提交键 → `POST {len:31, dis:true, cmt:0, mine:false}`。**文字在框里、按钮灰、计数 0** ⇒ 不是输入问题，是提交态问题；§A.33 第 4 条的三条路径已全部试完，**本轮起停止一切评论尝试，等人工** |
| 4 | ✅ **把「放大复核」前移到发布前是可行的，且不拖慢流程**；同一张图 `cropview 2×` 只看主体 + `corners 3×` 四角即可定论 | 本轮顺序：`viewimg`（1180×680 全图）→ `cropview` 2×（左半屏/右半屏）→ `corners` 3× 四角 → **然后才**填标题正文/插图/勾 AI 声明/发布；四角截图全为背景或暗部（无站标/水印/网址），主体屏内只有 `2 MPH / Self-Driving / 20 限速牌` 等界面元素。总耗时约 1 分钟，比发布后返工便宜 |

## §A.33 第 329 轮实测（2026-11-22 09:3x · 4 条 · **审核中公开页会重定向到首页 / 首图旁问号气泡里常印官网网址 ⇒ 换第二张 / 榜单卡「评论」按钮不是评论提交键 / 合成按键进不了评论编辑器**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **「审核中」时公开页会 302 到首页，`P1/AUTH/CMT` 读到的是首页数据，不能当破图或未发布判据** | 09:33 发布后立刻开 `/article/7710802717598171690/` → `P1 {url:https://www.toutiao.com/, canon:https://www.toutiao.com/, title:今日头条, artH:0}`、`IMGS NOART`、`DECL found:false`、`NOTICE hits:["涉嫌"]`（首页热榜标题）。后台先显示「审核中」，约 5 分钟后变 `已发布 · 已推送 · 首发`，同 URL 再读 → `canon 一致 / artH:3009 / 四条全过`。**正解：先看后台状态，`已发布` 再去验公开页；`审核中` 只记「审核中」** | 
| 2 | 🖼 **别从缩略图或缩小的公开页截图判断图上有没有「小字外链 / 网址气泡」；要 2–3 倍放大 + 四角各截一张再看** | 我先在 `pub.png`（676px 宽的公开页截图）上隐约看到手机右侧有个白点，一度怀疑是 IT之家常见的「?」网址气泡；按「没核实不下结论」复查：`viewimg.py` 原尺寸 `1440×816` 无气泡；`cropview.py` 把图放大 **2×** 聚焦手机区 → 只有 SIGNAL / WAS / HERE 三行手写与黑色机身，**无气泡、无文字**；`corners.py` 把图放大 **3×**（4320×2448）逐角截图 `c_TL/c_TR/c_BL/c_BR` → **四角全是纯米色背景，无站标、无水印、无网址** ⇒ **本张图合规，可继续沿用**。⚠️ **教训在流程不在图**：本轮**发布前**只看了 1180px 宽的全图截图，**发布后**才做放大复核（顺序反了）⇒ **下轮起：先 `viewimg.py` → 再 `cropview` 看主体 → 再 `corners` 四角 → 最后才决定用不用**，且这一步必须在点「确认发布」之前 |
| 3 | 🚫 **搜索结果卡里的「评论」按钮、文章页右侧的「评论 N」都不是提交键** | `cmt2.py` 在文章页取 `innerText==='评论'` 的按钮，命中 6 个，`b[0]` 坐标 `(416,291)` 点下去无任何反应（那是左侧互动栏的「评论」图标）。**正解：`document.querySelector('.comment-textarea')` + `document.querySelector('.submit-btn')` 两个类名定位**，别按文字找 |
| 4 | 🚫 **`Input.insertText` 能把字塞进 `.comment-textarea`（contenteditable DIV），但 React 不认 ⇒ `.submit-btn` 永远 `disable`；再补发逐字 `dispatchKeyEvent` 会把已输入内容打乱/清空** | 第 1 次：`ST {tag:DIV, ce:true, txt:"AI 辅助诊断把结果算出来了…"}`（`len 56`）而 `submit-btn disable`，点击计数 `0 → 0`、`mine:false`。第 2 次：先 `Range` 全选 + `Backspace`（`CLEARED 56`，内容没清）→ 逐字 `keyDown/keyUp`（0.012 s 间隔）→ `ST {len:0}` 且仍 `disable`。**结论：本轮评论提交路径不通，如实记 0 条，同一路径下一轮不得重试**；下轮改从「先真实点进评论框（`focus` + 一次 `Input.dispatchMouseEvent` 序列）→ 再用「一次性 `Input.insertText` 整段」→ 等 2 s 读 `.submit-btn` 是否掉 `disable`」这一条新路径试，仍不过即报 blocker |


## §A.32 第 328 轮实测（2026-11-22 07:3x · 6 条 · **刷新即「继续编辑」/ 工具栏插图按钮要先给编辑区焦点 / 图注框是 `textarea.pgc-img-caption-ipt` / 页脚按钮要按视口坐标重算 / 自赞会点反**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **`publish` 页只要有草稿，`location.reload()` 就清空并挂着「继续编辑」横幅** | 灌完 `共 925 字` 后刷新页面 → `AfterReload {title:"", kids:["P"], words:"共 0 字"}`，而横幅「草稿 25 倍的承诺先放一边 / 继续编辑」还在。且**已存草稿不会自动回填**，点「继续编辑」后 `n:0`（DOM 里找不到同名文本，`ps` 仍是 15）⇒ **一次会话内写完 + 插图 + 勾选 + 发布，中途别 reload**；若已 reload，按 §A.31 第 3 条换页（`nav('/graphic/articles')` → `publish`）再回读 `words:"共 0 字"` |
| 2 | ✅ **一次 `e.innerHTML = P.map(s=>'<p>'+s+'</p>').join('')` + `dispatchEvent(new InputEvent('input'))` 可以一次灌满多段，且重载后仍在** | `CHK {ps:15, words:"共 925 字"}`（14 段 + 尾段）；随后 reload 仍是 `ps:15 / words 共 925 字` ⇒ 这是**最快且最稳**的灌段法（无需逐段 `Enter`），但**必须**在第 1 条的前提下使用（灌完就发布，不刷新） |
| 3 | ⚠️ **工具栏「图片」按钮是 `div.syl-toolbar-tool.image.static`，必须先让 `.ProseMirror` 获得焦点再点，否则点了毫无反应** | 直接 `elementFromPoint(938,40).click()`、`Input.dispatchMouseEvent` 点击、`MouseEvent('click')` 派发**都无反应**（`TABS {lib:false, up:false}`、`FILEINPUTS 0`）；先点正文末段（`SEL {a:"P", t:"还是更容易分心？"}`）再点 `(951,53)` → `TABS {lib:true, up:true, snip:"上传图片免费正版图片我的素材 | 本地上传 | 扫码上传"}`。⚠️ 点击前先 `scrollY` 回到编辑区（本页工具栏 `position: relative`，`y` 会随滚动跑：`y:104` ↔ `y:40`） |
| 4 | ⚠️ **图注框是 `textarea.pgc-img-caption-ipt`（`placeholder="请输入图片描述(最多50字)"`），不是 `[placeholder]` 里第一个** | `probe_cap` 实读：页面上有 3 个 `placeholder` 元素（标题框 / `pgc-img-caption-ipt` / AI 助手框）⇒ 只用 `textarea.pgc-img-caption-ipt` 定位；点中后 `FOCUS TEXTAREA.pgc-img-caption-ipt` → `Input.insertText` → `CAP ["图：IT之家（画面为特斯拉官方发布的 FSD v15 更新说明）"]`、`ERR []` |
| 5 | ⚠️ **页脚三个按钮的位置随页面滚动变化，「预览/预览并发布」要每次用 `getBoundingClientRect()` 现算** | 固定坐标 `(819,916)` 一次点空（`HIT DIV.garr-footer-publish-content`），现算得 `预览 (894,933)` / `预览并发布 (1123,933)`；预览弹窗（手机预览 + 二维码）底部是 `关闭预览` / `定时发布` / `发布`，点 `关闭预览` 后回到 `预览并发布` → 弹窗 `确认发布 (1130,933)` → 跳 `/graphic/articles` |
| 6 | ⚠️ **自赞前先看是否已赞过（并发进程可能已点）** | 首读 `detail-like like | txt:"1"`（已赞）⇒ 我的点击变成**取消**（`detail-like | 赞`），重载确认「未赞」后再点一次才恢复 `detail-like like | 1`。**判据 = `className` 含 `like` 且 `innerText` 是数字**；`赞` 字样 = 未赞。另：`cdp.evaluate` 超时/网络慢时命令会 **30s 超时**，属前台超时 ≠ 作业被杀（承 §4 第 6 条） |


## §A.31 第 326 轮实测（2026-11-21 18:0x · 6 条 · **零尺寸游离图 / Delete 清不空正文 / 「继续编辑」回滚旧稿 / `已删除` 误判 GONE / 懒加载 1×1 占位**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | ⚠️ **图被插成「游离 DIV」时是零尺寸的，且删不掉** | 并发进程在末段 `Enter` 后插图，DOM 变成 `P…P, DIV.pgc-img, P`（图在**最外层**而非某个 `<p>` 里），`IMGPOS {x:10,y:10,w:0,h:0}`；ProseMirror 里点它只能拿到 `syl-toolbar-divider`，`Ctrl+C` 复制不到 ⇒ **移动图 = 无路可走**。判据：`[...e.children]` 出现 `DIV` 而不是 `P`，且 `img.offsetWidth===0`（另一个 `w:440` 的是上传弹窗里的预览图，别混） |
| 2 | 🚫 **`Delete` 清不空正文，会「复制一份」** | 先 `Range.selectNodeContents(.ProseMirror)` 再按 `Delete`：`CLEARED {ps:29}`（原 29 段没少）→ 逐段写入后 `ps 51`、`words 共 2417 字` ⇒ **旧文还在，新文叠在后头**。⚠️ 同一页上反复 `Backspace/Delete` 还会出现「锚点段被删空只剩尾句」（`约 5 分钟。` 一段就剩这 6 字，损失 70 余字）⇒ **别在同一页上改，换新页** |
| 3 | ✅ **新开 `/graphic/articles` → 再点 `publish` 才是干净页；但 reload 会「继续编辑」旧稿** | `clean.py` 读 `STATE {title:"", raw:1, words:"共 0 字", imgs:0}` 才动手；而 `ensure()` 的 `location.reload()` 会命中「继续编辑」把**上一份脏稿**拉回（`ENSURE RESUMED` → `SELALL {len:50}`）⇒ **reload 后必须再读一次 `raw/words/imgs` 确认是空页**，否则先 `nav('/graphic/articles')` 再进 `publish` |
| 4 | ⚠️ **`VERDICT` 的 `已删除` 关键词会撞正文自写句** | `chk_pub` 首读 `VERDICT GONE`，实为正文「Meta … 已删除 9200 万条色情广告」命中（`i2=1129`），`内容不存在` 为 -1 ⇒ 判存活要**分别回读关键词与上下文**（`s1/s2` 片段），不能只看 `GONE` |
| 5 | ✅ **图注为空会被「内容建议」提示补图**；**图注 ≤50 字**再复核一次 | 36 字图注 `ERR NONE`，公开页 `capCnt:1` 正常显示；本轮发布前 `COV` 读到「建议添加配图」是**图片节点未被识别**的表征（游离 DIV），修好后该提示消失 |
| 6 | ⚠️ **公开页图是懒加载，`nw:1` 不等于破图** | 首读 `{nw:1, nh:1, src:"data:image/gif;base64,R0l…", cls:"syl-page-img syl-img-loading"}`，`scrollIntoView` 后 5s 变 `{nw:1178, nh:656, src:"https://p3-sign.toutiaoimg.com/…"}` ⇒ `broken` 判据必须排除 1×1 占位 gif（`/^data:/` 且 `nw<=1`），否则每篇都会误报 `broken:1` |

## §A.30 第 325 轮实测（2026-11-21 15:0x · 4 条 · **正文换行会被吞 / 图注上限 50 字 / 同标题重发的硬事实 / 文件名撞标准库**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | **`insertText` 一次塞多段 = 1 段** | `s1.py` 用 `'\\n'.join(PARAS)` 一次性 `document.execCommand('insertText')`，结果 `WORDS 共 957 字` 但 **`p=1`**（换行被编辑器吞成一段）⇒ **必须逐段**：先 `selectNodeContents` 覆盖首段 → `Input.insertText(首段)` → 每段前发 `keyDown/keyUp Enter`（带 `text:'\\r'`）→ 再 `insertText`；本轮 `PROG 7→9 / 14→16 / 21→23 / 28→30` 才是段数在涨。 |
| 2 | **图注上限 50 字（含标点），超了只报红不拦发布** | 73 字图注 → 页面红字「**图片描述最多 50 个字，已超出 23 个字**」，但「预览并发布」照常可点 ⇒ 会带着超长图注发出去。**发布前必须回读 `ERR`**（本轮改为 50 字整后 `ERR NONE`，公开页 `capCnt:1 / capPos:57`）。 |
| 3 | **同标题重发：后台计数不变，「覆盖 or 并存」无法证实** | 15:16 首篇（正文仅 1 段）→ 重排后重发，后台仍是 `共 81 条内容`、列表**只有 1 条**该标题、`草稿箱` 38→39；公开页唯一 `7710517514064740900`。**没有证据说明第二篇替换了第一篇**⇒ 记账只能写「列表与公开页当前就这一篇」，🚫 不写「已覆盖」。避免这种现象的唯一办法 = **发布前把正文段数断言掉**（本轮 `CHK {ps:30}`）。 |
| 4 | **`s4` 类脚本的「确认发布」按钮会读不到** | 发布弹窗是**手机预览 + 右侧二维码**的形态，`ENSURE` 的 `.ProseMirror` 探针判死（`ENSURE FAIL`）⇒ 文本按钮找不到 → `CONFIRM NO`。**此时不要用坐标盲点**：改判据 = 后台列表 `href` + 首行标题 + 计数；点不到就**不点第二次**（承 §A.3 第 5 条）。另：临时脚本**别命名成 `re.py`**（撞标准库，`import json` 直接抛 `SyntaxError`）。 |

## §A.29 第 324 轮实测（2026-11-21 12:3x · 6 条 · **并发轮自述「未发」但真发出 / 评论 AFTER 计数不可信 / 索引式改文件会复制整段**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **「台账写 0 篇」≠ 真没发**：并发进程跑完 `s4.py`（点「确认发布」）后可能**来不及写台账**，甚至写了「本轮未发」。判据只有两个：**后台计数 +1** 与 **首行标题 + 时间**；两者都对上就是发过了 ⇒ **只补账、不重发** | 第 323 轮台账写「本轮未发图文文章 · 0 篇」，但 `base2.out` 12:19 `共 78 条内容` → 本轮 12:31 `共 79`、首行「… · 11-21 12:25 · 已发布 首发」；`s4.out` 12:25 有 `CONFIRM → AFTER /graphic/articles` ⇒ 确已发布 |
| 2 | ⚠️ **补账时「四硬标准」可以事后补核**：公开页只要还 LIVE（未出现「内容不存在 / 已删除」），①–④ 仍可逐条读；否则只能记「未复核」 | 12:36 补核 `7710475590263931435`：`canon` 一致 `artH1898` / `IMGS nw1398 nh786 broken0` / `NOTICE` 仅正文自写句 / `DECL found:true` ⇒ 4/4 |
| 3 | 🔑 **评论 `AFTER 评论 N+1` 不可作落地判据，必须重载 + 列出评论条目**：本轮 A 帖 `AFTER 评论 98`，重载后仍是 97、列表 6 条无本号 ⇒ **未落库**；`RECHECK mine:false` 与计数回落同时出现时，判「未落库」而不是「异步残留」 | A `7710392465596940834` `97→98` → `RECHECK cmt:97 mine:false` → 真实鼠标展开「查看全部 97 条评论」后 `items:6`、全部他人 ⇒ 未落库。对照 C `7706037043050086954` `1→2` + `RECHECK mine:true` ⇒ 落地 |
| 4 | ⚠️ **大评论楼（近百条）新评论不一定出现在首屏前 6 条**：即便落地，`mine` 也可能因折叠/排序读不到 ⇒ **先选小楼（1–3 条）或按时间排序**再评 | 本轮改投 C 楼（1 条评论）一次落地；A 楼（97 条）投入后既不见计数也不见条目 |
| 5 | 🚫 **改大文件别用「按行号切片再拼接」**：一次索引算错就会把整段复制一遍（本轮把第 322 轮 84 行复制成两份）。正解 = **先按唯一标题字符串定位锚点、再断言首尾行内容、最后与 `git show` 原文做逐字节比对** | 本轮 `fix.py`/`fix2.py` 两次把段落复制（文件 382 → 559 行）；`fix5.py` 用「锚点 + 断言 + `merged == old322`」一次通过（`identical: True`） |
| 6 | ✅ **用「已入账条目」接「创作热点」是稳的选题法**：热点只决定「写什么」，数字仍回到 `news/<date>.md` 的旧条目 ⇒ 不产生未入账数字 | 热点「雷军说AI三四年后颠覆可信吗」→ 第 300 轮 `1/028/669`（重抓 `200` 校验标题一致）⇒ 正文只有该条的引语与日期 |


## §A.27 第 321 轮实测（2026-11-21 07:0x · 6 条 · **标题框残留 / 题注误插后重建正文 / 评论复核只认 canonical+列表**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **填完正文必须回读标题**：`s1_fill.py` 会先把 `paras.txt` 灌进正文，但标题框可能仍留着**上一轮**的值（编辑器残留 state，承 §A.25 第 1 条的另一面） | `s1.out` `CHK {"title":"内存涨价 263%，为什么手机只敢涨 13%","titleLen":22,...,"head":"一个数学家说…"}` ⇒ 正文是新稿、标题是旧稿；`fixtitle.py` 重写后 `AFTER {"titleLen":19}` |
| 2 | 🔑 **插图「定位段」别用上一轮的关键词**：`s2_img.py` 里 `ps.find(x=>/关键词/.test(...))` 若关键词在新稿里出现在**别的段**，图会插错位置、题注跟着跑；`find` 失败再退到 `ps[len-3]` 更危险 | 本轮图插到了第 3 段后（目标为第 2 段后）；改为**按下标取段**（`ps[1]`）后正确 |
| 3 | 🔑 **题注插错后不要「点坐标 + 退格」去修**：段落不在视口时 `getBoundingClientRect()` 读到 `y:0`，点击落在页面顶部 ⇒ 焦点乱跳、**正文被复制**（本轮多出一段） | `fixcap.py` `POS {"x":30,"y":0}` → `AFTERDEL {"n":27,"hasCap":3}`；最终靠 `rebuild.py`（`selectNodeContents` 清空 + 一次 `insertText`）重建（`WIPE {ps:1,len:0}` → `FILL {ps:23}`） |
| 4 | ⚠️ **`textarea.pgc-img-caption-ipt` 有两个**：一个在 ProseMirror 内（可见），一个在隐藏 `templ` 里（`offsetWidth=0`）⇒ 点之前先 `filter(x=>x.offsetWidth>0)` | `CAPBOX {'n':1,...}` 用过滤后取到正确那个；不加过滤时点到隐藏框，`CAP` 写进去也不显示 |
| 5 | ⚠️ **发布页读「封面」要先把页滚到底**：`封面` 文本节点在视口外时 `querySelector` 找不到（本轮曾误判 `NF_COV`）⇒ `scrollTo(0, document.body.scrollHeight)` 后再读，或直接看图 | `cov2.png` 目视：封面已自动取正文图（`编辑 替换 / 预览`） |
| 6 | 🔑 **评论落库的唯一稳判据 = `link[rel=canonical]` 与目标 id 一致 + 评论列表出现「Xmodel唠两句 … 刚刚 · 删除」**；`RECHECK` 里的 `cmt` 是异步残留（读到 `评论 26 / 评论 0` 都出现过），`mine:false` 不可作失败 | A/B/C 三条均以此判据确认落地；B 帖首读 `RECHECK cmt:评论 0` → 重跑 `CANON … mine:true` |

## §A.25 第 316b 轮实测（2026-11-20 15:3x · 5 条 · **标题框会吞正文 / 评论发送键范围**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **`insertText` 前先确认焦点落点**：标题是 `textarea[placeholder*="标题"]`，正文是 `.ProseMirror`；若焦点还在标题框，整篇正文会灌进标题（且标题上限 2～30 字会把正文掐掉一半，**编辑器不报错**） | 首次 `FILL {"titleLen":1237,"edLen":1291}`、`CHK title:"用一个新密码…"` ⇒ 标题被写成了正文首段；修正法：标题用原生 `HTMLTextAreaElement.value` setter 只写标题（`titleLen:21`），正文 `selectNodeContents` 全选后 `insertText` 覆盖（`ps:26 / 共 1063 字`） |
| 2 | 🔑 **正文定位要用「排除法」找标题框**：`document.querySelector('textarea')` 在发布页可能是**第三个** textarea（AI 创作框也不带 `标题` placeholder）⇒ 一律 `[...querySelectorAll('textarea')].find(x=>/标题/.test(x.placeholder||''))` | 上一轮脚本按索引取，直接取错框；本轮改用 placeholder 过滤后稳定 |
| 3 | ⚠️ **公开页评论框 `.comment-textarea` 的提交键是 `.ttp-comment-input button.submit-btn`**，绝不能在全页找「发布/发送」——页面顶部导航也有个「发布」 | 第 1 投点到 `{"x":1918,"y":32,"t":"发布"}`（顶栏），`AFTER 评论 37`（未变）；改用 `cmt.py` 路径后 `37 → 38` |
| 4 | ✅ **评论判据仍以「计数 +1」为主，`RECHECK mine:false` 有两因**：页面重导航后评论列表异步重渲染（读到 `items:0 / 评论 0`），或楼层折叠 | C 帖 `AFTER 4 → 5` 但 `RECHECK 评论 0 mine:false`；改用 `readcmt.py` 读公开页列表见「Xmodel唠两句 … 刚刚 · 删除」⇒ 已落库 |
| 5 | ⚠️ **`Ctx.ev()` 没有 `flush` 参数**（第 4 次踩）：把 `flush=True` 传给它就抛 `TypeError: Ctx.ev() got an unexpected keyword argument 'flush'` | 本轮 `s1_fill.py` / `move.py` 各崩一次；删掉 `flush=` 即正常 |


## §A.24 第 315 轮实测（2026-11-20 12:0x · 5 条 · **图片 URL 不许手抄 / 品牌拼图可作「讲这家公司」的配图**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **图片 URL 一律从脚本 JSON 复制，不手抄**：文件名中段（UUID 后半段）写错一位就是 404，而 `img_url` / `imgs[].url` 都在 `ith_extract.py --json` 里现成 | 首写 `1/029/841` 图为 `…8c07b2a1ba5b.png` → HEAD `404`；改回原值 `…8c07-a2699b5d565b.png` → `200 image/png 121,380 B`。采集条目已当场改正并留口径说明 |
| 2 | ✅ **「品牌拼图 / 通用主题图」可作配图，前提是正文讲的正是这家公司** | 本轮 `1/029/795` 首图为育碧 8 个 IP 海报 + 中央 `UBISOFT` 字标，无站标/无二维码/无水印/无社交 UI；正文主体是「育碧把 AI 做成子公司」⇒ 图注只写「图：IT之家」（来源署名），**不写成现场图**，不算禁令 11 的「冒充现场」 |
| 3 | ⚠️ **`<1000px` 的图不进正文**：`1/029/772`（Apple Card）GET `200` 但只有 **800×450** ⇒ 不选；采集条目补一行「配图备注」说明尺寸，不改原条目 | `viewimg.py` → `DIM 800x450`；另 `1/029/842` 首图 1356×1498 竖长 Beta 截图语义不搭，不选 |
| 4 | ⚠️ **图片懒加载占位第 8 次复现**：`chk4.py` 首读恒 `broken:1`（`data:image/gif`，`nw:1`，但 `h:380` 已占位）⇒ 仍须 `chk5b.py` 滚到图位等 5 s | `IMGS {"n":1,"vis":1,"broken":1}` → `IMG [{"nw":1440,"nh":810,"w":676,"h":380,"done":true}]` |
| 5 | ✅ **发布链路 4 步在 `nohup setsid … &` 下单步 20–30 s 才出结果**：`sleep 25` 后读 out 是稳的，不要因前台 30 s 超时就重启（承 §A.19 第 1 条）；`s4_confirm.py` 即时计数常不刷新（本轮 68），**以 `getid.py` 重载为准（69）**，且新文先「审核中」、约 2 分钟后变「已发布」 | `s1/s2/s3/s4` 各步 out 秒级完整；`AFTER_CONFIRM 68` → `getid 审核中` → `getid2 69 已发布` |



## §A.23 第 314 轮实测（2026-11-20 10:0x · 6 条 · **论文示意图可当配图 / 大评论楼 RECHECK 恒 false**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | ✅ **论文自带示意图是最稳的配图来源**：无站标、无二维码、无社交 UI，还能在正文里合法署名「图：IT之家（图源为 XX 论文示意图）」。凡「官方截图 / 社交平台截图」类候选，**先目视再定稿**，本轮两张这样的图都带 IT之家站标 | `1/029/789` Figure 1 状态机图 1367×1061 采用；`1/029/707` 官推截图右下角 `IT之家 / www.ithome.com` 弃用 |
| 2 | ⚠️ **论文图常自带英文原图注**（Figure 1 …）⇒ 中文图注不能只写「图：IT之家」，要说明「图源」；公开页里英文原图注与中文图注会**同时显示**，属正常 | `pub_img.png` 目视：Figure 1 英文说明 + 「图：IT之家（图源为…）」 |
| 3 | ⚠️ **大评论量帖（>200 条）的 `RECHECK mine:false` 不等于失败**：`items` 只给折叠外 3 条 ⇒ 判据回到**评论计数 +1**，**不重投**（避免同帖双评） | C 帖 `7709715716177429043` 20→21、`mine:false` |
| 4 | ⚠️ **同一张图不要跨篇复用**：`1/029/785` 首图 09:34 那篇已经用过 ⇒ 本轮改选论文图 | 09:34 与 10:08 两篇配图对比 |
| 5 | ⚠️ **图片懒加载占位第 7 次复现**：`chk4.py` 首读恒 `broken:1`（`data:image/gif`）⇒ 必须滚到图位等 4–5 s 再判 | `IMGS {"n":1,"vis":1,"broken":1}` → 滚后 `nw1367 nh1061 done:true` |
| 6 | ✅ **采集层只存 URL、不下载** 已稳定：候选图一律 `img_check.py --head`（不发 GET），本轮 23 张 `BAD 0`；只有「要发布的那 1 张」才 `dl1.py` 落 `imgs/` | `/tmp/r314/headcache.json` + `imgchk*.out` |


## §A.22 第 313 轮实测（2026-11-20 09:3x · 5 条 · **「RECHECK mine:false」可能只是折叠区没展开**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **`RECHECK mine:false` 不等于没发出去：先展开「查看全部 N 条评论」再判** | 本轮 B 帖 `7709759201307787812`：`AFTER` 已是 `评论 15 → 16`，但 `RECHECK mine:false` 且 `verify.py` 只读 `.ttp-comment-item` 得 `items:3`（全为他人）；`verify3.py` 点「查看全部 16 条评论」+ 连续 `scrollBy` 后，整页文本里出现「**Xmodel唠两句 赞 170万这个数不是终点… 回复 · 2分钟前 删除**」⇒ 已落地。**判定顺序 = `评论 N` 计数 +1 → 展开全部 → 文本搜评论前 12 字**（承 §A.21 第 2 条：崩在 RECHECK ≠ 失败） |
| 2 | ✅ **`要点/标题即判断` 的结构继续有效，但「六个小问题」里别问读者自身数据** | 首稿问「你上一次拿到一条很有用但没采纳的 AI 建议」，属要求读者交代个人行为，已替换为「你电车松踏板能接受拖拽感吗」这类可直接答的题；改后正文 29 段 / `共 1666 字` / 0 emoji / `http` 命中 0 |
| 3 | ⚠️ **同一篇里「现场合影图」优于「社交平台截图」** | `1/029/785` 两图：第 1 图 1080×608 为小鹏 G9L 现场合影（含「小鹏 图灵AI共驾 / 行业首次智驾赋能人驾」品牌字 + 车头铭牌），**无站标 / 无二维码 / 无水印** ⇒ 用；第 2 图 1054×1173 为小鹏微博截图，**右上角印 `IT之家 / www.ithome.com`** ⇒ 弃（禁令 11）。再次印证：站标是印在图上的，URL 与 GET 都看不出 |
| 4 | ✅ **图文文章通道稳定：编辑器 → 插图 → 图注 → 封面自动** | `s1` 开页干净（`共 0 字`/`请输入正文`）、灌段后 `共 1666 字 ps:30`；`s2` 插图后 `IMG {n:2, vis:1}`（第 2 个在隐藏 `<templ>`，不必删）、图注 `图：IT之家`、封面 `COV_BEFORE n:1 t:编辑替换`（已自动取正文图）、`头条首发` 与 `引用AI` 初读 `true/false` ⇒ 只点 `引用AI`；`s4` 后计数未即时刷新（仍 66），`getid.py` 重载即 67 |
| 5 | ⚠️ **`getid.py` 用的标题必须与 `common.TITLE` 完全一致** | 本轮 `common.py` 改 `TITLE` 后 `getid.py` 直接从 `common` 读 `TITLE` 拼匹配串，才能拿到 `item/7710060552713749033`；若标题写错一字，`ID []` 且会被误判「没发出去」 |



| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **微头条列表里的同题条目是平台「由文章生成」，不是二次发布** | 21:36 发文章后，21:37 微头条列表出现同题条目并标注「**由文章初步生成 / 由文章生成**」；同页 15:21 / 15:05 / 12:40 各篇也都是这个状态。⇒ **不要误判为「重复发布」或「通道混用」**，也不必去删（删了等于撤掉平台的自动分发） |
| 2 | ⚠️ **`cmt.py` 的 RECHECK 会在页面切走时抛 `TypeError: Cannot read properties of null (reading 'innerText')`** | 本轮 B 帖 `AFTER` 已读到 `评论 2 → 3 / items 3`，但紧随的 `RECHECK` 因 `.comment-textarea` 尚未渲染返回 `null` 而崩（脚本在 `state()` 里直接 `ta.innerText`）。⇒ **崩在 RECHECK ≠ 评论失败**；用 `verify2.py`（只读 `评论 N` + `items` + `mine`）单独复核一次即可，本轮复核得 `{"cmt":"3","items":3,"mine":true}` |
| 3 | ✅ **`cmt.py` 的 `items` 计数在「折叠区外」也能当证据** | 本轮回评 0，但 A 帖 `items:3` 且 `mine:true`；B 帖 `items:2 → 3` 精确 +1，比只读 `评论 N` 更稳（承 §A.19 第 5 条） |
| 4 | ⚠️ **配图「主题图」也可用，但必须在正文里让图有意义** | 本轮 `1/029/646`（银行警告智能体）首图是 IT之家通用科技底图（AI 字样 + 光斑，1440×721），**无站标/无二维码/无水印**。它不是新闻现场图，但正文讲的就是「智能体代你动账」，图注写「图：IT之家」属**来源署名**、不属「冒充现场图」⇒ 可用。⚠️ 若正文需要「现场」而图是通用图，则按禁令 11 弃图 |
| 5 | 🔑 **`common.py` 里的 `IMG` 用 `sed 's#imgs/TBD.jpg#...#'` 替换时，先 `grep -n 'IMG ='` 复核** | 本轮从 `/tmp/r310/cdp/common.py` 复制时把 `IMG` 先改成 `TBD.jpg` 再替换；若替换串写错，`dl.py` / `s2_img.py` 会静默用错图（§A.18 第 1 条同源坑）。**做法：改完 `grep -n "TITLE =\\|IMG =\\|_P=\\|OUT ="` 四项一起核** |

## §A.28 第 322 轮实测（2026-11-21 09:3x · 5 条 · **后台首行 ≠ 自己的上一篇**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **后台列表首行不一定是「本线上一轮发的那篇」⇒ 发现陌生标题先查来源，不要默认是自己** | 09:31 读后台：`共 77 条内容`，首行「能打印的药片，藏着两层壳 · **11-21 07:38** · 已发布」；第 321 轮 07:11 的黎曼那篇掉到第二行。`grep -rl 能打印的药片 run/` 只命中 `/tmp/r322/cdp`（工作目录）⇒ 判为**无账的一次发布**，再用 `ls -la --time-style=full-iso` 读 `/tmp/r322/cdp/{s1.out,getid.out,chk4.out}` 的物理时间（07:34 / 07:38:50 / 07:39）把时间线钉死 |
| 2 | 🔑 **「后台计数」是并发/漏账唯一硬证据，每次发布前后各读一次** | 75（第 321 轮基线）→ 76（07:11 黎曼）→ **77（07:38 无账那篇）** → **78（本轮 09:35）**。`git log`、`cline_last.log`、`ls` 都不能证明「有没有发」，只有计数变化 + 首行标题能。⇒ 每轮开工第一件事 = 读计数并记进台账基线行 |
| 3 | ⚠️ **自赞判据：容器类名是 `${cls} like`，且全局正则 `/赞\s*(\d+)/` 读不到（页面没有「赞 N」文本）** | 未赞：`{cls:"detail-like", v:"赞"}`；已赞：`{cls:"detail-like like", v:"1"}`。而 `document.body.innerText.match(/赞\s*(\d+)/)` 在两种状态下都返回 `NONE` ⇒ 之前记的「重载 `like \| 1`」实际读的是**容器内文本**。**正解 = 读 `[class*=detail-like]` 的 `className` + `innerText`，重载后仍为 `detail-like like / 1` 才算 1/1** |
| 4 | ⚠️ **四硬标准③ 命中「搬运」会误报：先打印上下文再判** | `NOTICE {hits:["搬运"]}` 连续两篇命中；逐条打印上下文后确认**全页仅 1 处**、且是正文自写句「本号只做**搬运**和排列，没有自己核实产能和营收」⇒ 属自述，不是平台处罚。**判据：打印每处命中前后 45 字，含「搬运」的自写句不计入** |
| 5 | 🔑 **跨轮复制脚本时 `like.py` / `chk4.py` 里的 `URL=` 是硬编码** | 本轮 `cp like.py like2.py` 后直接跑，赞到了**上一篇**（`7710400994576597545`：`BEFORE detail:[1]` → 点击后变 `赞`）—— 一次**误操作**，已如实记进台账。`chk4.py` 的 `URL=` 同样硬编码。**做法：跑任何带 `URL=` 的脚本前先 `grep -n "URL=" *.py` 过一遍** |



## §A.20 第 310 轮实测（2026-11-19 18:0x · 5 条 · **后台列表已不直接暴露 pgc_id**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **`/profile_v4/graphic/articles` 列表页的本号文章标题就是 `<a href>`，可直接读到 `/item/<id>/`** | 页面已改为「点「查看评论」跳评论区」的交互（本轮点 3 次均不跳、不开新标签）；取 id 的正解 = `[...document.querySelectorAll('a')]` 里筛 `innerText` 以标题开头的元素，读 `getAttribute('href')` ⇒ `https://www.toutiao.com/item/7709821694692672041/?enter_from=mp_group_management`；再用该 id 拼 `https://www.toutiao.com/article/7709821694692672041/` 即命中（承 §A.7 第 5 条 / §A.17 第 2 条） |
| 2 | ⚠️ **「更多」下拉里的「查看评论」点击后不导航**（3 次验证） | 连点「查看评论」后 `location.href` 仍是列表页、`/json` 里也无新标签；菜单 DOM 在点击后即收起。**不要据此判「发布失败」**，改用第 1 条取 id |
| 3 | ✅ **「四硬标准」第②条（图正常显示）要「先滚再读」，首读必是懒加载占位** | `chk4.py` 首次读 `IMGS {n:1, vis:1, broken:1, src:data:image/gif;base64…}` 是**占位图**（第四次复现）；`chk5b.py` 做 `i.scrollIntoView({block:'center'})` + 等 5 s 后 → `nw859 nh540 w676 h425 done:true`，截图目视图片与图注均正常 ⇒ **判据是渲染后的 `naturalWidth>1`** |
| 4 | ⚠️ **`SEEN.md` 计数口径要写清是 `wc -l` 还是「主键去重」** | 本轮 `wc -l` 3,408 → 3,427（+19），但其中 `518` 与 `528` 同题、`532` 为厂商稿 ⇒ 主键去重口径实为 +17。两个数差 2，记账时必须并列写，否则后续轮次会把「+19」当新闻条数 |
| 5 | 🔑 **配图「只存 URL」的落盘后校验可以只发 HEAD（已实现 `img_check.py --head`）** | 发布前需再验一次图仍可用，但重下会在本地多出一份 body；新增 `head()` 走 `Request(method='HEAD')` ⇒ `200 + image/* + Content-Length>5120`，本轮 4 张全部 `OK`、不落盘。⚠️ 无 `Content-Length` 的站点返回 `bytes:None`，此时调用方须用 `os.path.getsize` 补一次 |


## §A.19 第 309 轮实测（2026-11-19 15:1x · 5 条 · **前台超时 ≠ 作业被杀**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **前台 30 s 超时 ≠ 作业被终止；重启前必须 `pgrep -af <script>` 判活** | `timeout 260 python3 s1_fill.py` 在前台报超时返回，但进程（pid 仍是它）**继续跑完**；此时又 `nohup setsid` 起第二个，**两个进程抢同一个标签页**。结果：`FILLED {wc:共 1095 字, ps:33}` 只出现在后起那个的 `s1b.out`，先起的 `s1.out` 永远空。⇒ **长链路一律 `nohup setsid … &` 后读日志**（承 §4.6），且**先判活再重启** |
| 2 | ⚠️ **`chk4.py` 首判 `broken:1` 是懒加载占位，不是破图**（第三次复现） | 公开页两次 `nav` 后 `<article>` 高 2483 已就绪，但图仍是 `src=data:image/gif;base64,R0lGOD…` `nw:1`；`scrollTo(0, img.top-260)` + 等 5 s 后变 `nw1024 nh768` `complete:true`、渲染 `676×507`。⇒ **「滚到图位 + 等 4–5 s」是唯一判据** |
| 3 | ✅ **截图型配图也可用，关键是「图里有信息、且无第三方角标」** | 本轮弃 `1/029/331`（本案主稿）唯一正文图（678×452，低于 ≥1000px 建议线），改用 `1/029/403` 第 2 张 1024×768：安全中心「Emerging risks」详情页，卡片文案「Risk information is unavailable … Required information is incomplete or cannot be trusted.」本身就是论点（有些东西修不了、只能记账）。**无二维码 / 无 `ithome.com` 角标 / 无水印** |
| 4 | ⚠️ **并发进程会抢先发掉本轮采集里的选题 ⇒ 每轮发稿前先扫后台首行标题** | 15:04 并发进程发掉「一张矿卡藏着的八成算力…」（= 本轮采集的 `1/029/251` CMP 170HX）⇒ 本轮改选 `1/029/331` + `1/029/403`。**基线与选题之间必须读一次列表首行**，否则会重复选题 |
| 5 | ✅ **`cmt.py` 的 `RECHECK mine:true` 与计数 +1 双命中，是本轮 3 投 3 中的稳定判据** | A `26→27`、B `1→2`（`items 2`）、C `2→3`，三条均 `RECHECK mine:true`；`RECHECK` 读到的 `cmt` 偶有回落（A 回 `26`）但 `mine:true` 恒成立 ⇒ **两个信号任一成立即算落地**，不必 `verify.py` 再跑（承 §A.18 第 4 条） |

## §A.18 第 308 轮实测（2026-11-19 12:3x · 5 条 · **跨轮复制脚本 = 硬编码残留**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **跨轮复制发布脚本，必须逐项清掉上一轮的硬编码：标题 / 图注 / 图片路径** | 本轮 `s2_img.py` 从 `/tmp/r307` 复制而来，只改了图片路径，**图注仍硬编码「图：OpenAI 官方政策说明配图」** ⇒ 首次插图后 `CAP` 读到错值；若不复核就直接发布，就是**配图署名造假**（图是艾伯塔省发布会，署名却写 OpenAI）。**发布前 `insp4.py` 必查 `cap` / `COV` / `BOXES` 三项**，与 `TITLE`、`IMG` 一起当「四件套」核 | 
| 2 | ⚠️ **`Input.insertText` 是「追加」不是「替换」，纠错时不能整段重跑 `s2_img.py`** | 二次执行 `s2` 导致图注变成两条同样文本（且会**再插一张图**，`FILEINPUTS 0` 才没插成）。正解：单写小步骤 `cap2.py` —— `textarea.focus()` → `setSelectionRange(0,len)` → `Backspace`（**dispatched keyEvent，React 才收得到**）→ `insertText`，实测 `CLEARED "" → AFTER 图：艾伯塔省政府发布会现场（IT之家）` | 
| 3 | ⚠️ **图注框是原生 `textarea`，不是 ProseMirror** | `document.querySelector('.ProseMirror textarea.pgc-img-caption-ipt')` 可直接命中，`selectionStart/End`、`setSelectionRange` 全部可用 ⇒ **改图注不必走逐键输入**，比评论框好操作（评论框是 `div[contenteditable]`） | 
| 4 | ⚠️ **`RECHECK mine:false` 仍可能是渲染延迟，先 `verify.py` 再判断** | B 帖（传统武术）提交后 `AFTER 评论 159`、`RECHECK 评论 158 / mine:false`；单独 `verify.py` 再读 **`评论 159 · mine:true`** ⇒ 成立。**计数 +1 与「mine:true」任一命中即算落地**，两次都不过才判失败，且失败也不重发（承 §A.5 第 6 条） | 
| 5 | ✅ **`1/029/222` 这类「政府发布会现场图」是最干净的配图** | 1280×720、讲台牌自带官方 slogan、**无他站角标 / 无二维码 / 无水印**，封面自动取正文图得 `925×720`（高于 672×462 建议线）。同轮弃掉 678×452 的 CEO 人物图（低于「≥1000px 宽」建议线）⇒ **选图顺序仍应「先尺寸、再目视」** | 

## §A.17 第 307 轮实测（2026-11-19 09:4x · 5 条）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **`s4_confirm.py` 的即时计数不可靠，别据此判失败/重发** | 点完「确认发布」立即读仍是 `共 58 条内容`（= 发布前基线），随后 `reload` 列表页变 **59** 且首行即本标题。**判据 = 重载后 `共 N 条内容` + 首行标题**；中途不可再点发布按钮（重复发布坑，第 251 轮实证） |
| 2 | ✅ **`pgc_id` 直接拼 `/article/<pgc_id>/` 第 2 次验证通过** | 列表 `a.href` 为 `graphic/preview?pgc_id=7709691037279437331` ⇒ 直接开 `https://www.toutiao.com/article/7709691037279437331/` 即命中，不必等作者页刷新（承 §A.7 第 5 条） |
| 3 | ⚠️ **公开页首开必落首页 + 图片懒加载，只有「滚到图 + 等」才读得准** | 首次 `nav` 后 `location.href` 变 `https://www.toutiao.com/`、`article:false` ⇒ **必须再 nav 一次**；此时图仍是 `<img src=data:image/gif>` `nw:1 nh:1`，`scrollIntoView` 后等 **4–5 s** 才变 `nw1440 nh810` `complete:true`、渲染 `676×380`。**不滚动就判「破图」是误判**（承 §A.3 第 2 条，本轮再次复现） |
| 4 | ⚠️ **`verify.py` 只匹配评论前 12 字，折叠区外的读不到** | D 帖（DeepSeek 计费）提交后 `评论 4 → 5`，但 `verify mine:false`，再 `cmtlist` + 滚 1500→6000px 复核**三次都只读到 8 条**（本号评论排在其后）⇒ 记「计数 +1、文本未复核」，**按 §A.5 第 6 条不重发**；计数 +1 的证据强于文本匹配 |
| 5 | ✅ **配图先目视再定稿仍然有效（本轮一次过）** | `1/029/145` 首图 `0c9e160e…png` 1440×810 为 OpenAI 四层防护示意（SEARCH/SAFEGUARDS/MONITORING 三层 + ALIGNMENT 主循环），**无二维码 / 无站标 / 无水印** ⇒ 直接用；同文第 2、3 张未用。封面自动取正文图得 `1039×809`，高于 672×462 建议线 |


## §A.16 第 306 轮实测（2026-11-19 07:5x · 7 条）

| # | 实测 | 结论 / 用法 |
|:--|:--|:--|
| 1 | **配图目视必须在「定稿前」** | 本轮初稿按 IT之家 `1/029/137`（Stitch Loop）写好全文，配图 `d74a363e…png` 目视发现**右上角带 `IT之家 / www.ithome.com` 站标** ⇒ 按禁令 11 弃图，**整篇选题连带作废**。⇒ **先看图、再写稿**，避免整篇白写 |
| 2 | **安全新闻的可用图很多是信息图** | `1/029/139` 的配图是 NGINX 徽标 + 「HTTP/2 RCE」+ CVE 编号的黑底信息图，干净、无站标 ⇒ 这类**研究机构自制信息图**可用率高（比推文截图强） |
| 3 | **协议名不算外链，但会被 `http` 检查误报** | 正文含 `HTTP/2`、`HTTP/3` 时，`s1_fill.py` 的 `http:/http/i.test(...)` 返回 `true`（假阳性）。判据应改为 **`https?://` 或 `www\.`**，本线复核用正则确认仅命中协议名 |
| 4 | **公开页评论区 `评论 N` 是脆值** | A / D 两帖提交后各读到一次 `评论 1`，随后 `owncmt.py` **两次独立复核均为 `评论 0 / items 0`** ⇒ 判未落库。**`评论 N` 只能当线索，`items + 文本` 才是证据** |
| 5 | **`cmt.py` 的 `len` 不是文本正确性证据** | 中文字符串逐键输入后 `len` 恒等于字数，但**楼内显示会乱序**（本轮 C 帖楼内文字为两句交叉）。⇒ `len` 只证「有输入」，**不证「输入正确」** |
| 6 | **自赞按钮读不到时重开页面，别换选择器** | `like.py` 首次 `BEFORE NF`（页面未渲染完）⇒ 直接重跑同一脚本即得 `.detail-like`，`AFTER_CLICK like | 1`、重载复核通过 |
| 7 | **楼内回复按钮 = `button.reply-btn`** | 用 `textContent === '回复'` 匹配会漏（按钮文案节点结构不同）。回评后一律 `RELOAD` 复核 `has` 字段 |


# STYLE.md — 本号文风档（**发文 / 评论前必读 · 最高优先**）

> **性质**：本文件 = 本号「Xmodel唠两句」**真实文风实测档**，受 `SPEC-人设与评论SOP.md §3.0` 授权。
> **优先级**：**本文件 > SPEC §3 通则**（冲突以本文件为准；§3 只作「AI 腔兜底」）。
> **建立**：2026-10-11（第 14/16 批）· 取样 = 创作后台「微头条」列表 + 公开主页。
> **取样量（实测）**：**作品 25 篇**（`10-11` ~ `08-04`，含不同时期）+ **评论 20 条**（创作后台「评论管理」`/profile_v4/manage/comment/all` + 主页帖下互动）。
> 🔄 **2026-10-12（第 16 批 07:00 轮）扩样复核**：① **评论 20 条**逐条复核（含作者 / 日期 / 原文，见 §B）——`评论管理` 的「**加载更多**」本轮 3 次触发尝试**未生效**（`el.click()` / `MouseEvent` 派发 / 滚动后重点），**不外翻**、不加计数；② **我发出的评论样本 +10 条**（本轮实测 27–40 字，见 `台账.md` 第 16 批 07:00 轮），用于校准 §B「我发评论的口径」。
> ⚠️ **取样源如实说明**：创作后台「评论管理」**只暴露「收到的评论」**，**未提供「我发出的评论」入口**（页面仅 2 个 tab：`全部 / 粉丝`）⇒ 本轮评论样本 = **收到的评论（含真实用户 + 豆包机器人）**；「我发出的评论」**未能取到（如实记）**。

---

## §A 作品文风（正文 · 25 篇实测）

| 维度 | 实测结论 | 实证片段（原文节选） |
|:--|:--|:--|
| **开头** | **直给观点/事实，零铺垫**；或**反问起句**；或 **`@豆包` 提问式起句** | 「没有双标：有利于中国的就支持，否则就反对。」「建设不好自己国家的人，凭什么能建好别人的国家？」「@豆包 金庸祖上告发写明史的庄家起家的」 |
| **句长 · 段长** | **极短**。绝大多数 = **1–2 句**，**一句成段**，全篇 **≤60 字** 为主（部分 100+） | 全篇即一句：「全盘否定儒家就是反汉反华」「北京通勤时间和距离都是全国第一」 |
| **人称 · 口吻** | 少用「我」；**直接下判断**；口语化、自信、略带嘲讽 | 「管好自己不吃就完了，非要拦着不让别人吃辣，当然会被大家讨厌呀。」「这事儿」类口语；「非常善于使用间谍」 |
| **标点** | 用 **`""`** 引号（**不是「」**）· 逗号串句 · 有 **`？`**（反问）· 有 **`！`**（感叹）· 有 **`——`** · 用 **`【】`** 强调 · 数字用**阿拉伯**（`10 发`） | 「接受悲惨现实需要高智商，"相信自己愿意相信的"则对智商要求较低。」「#中国缠足陋习为何流传千年# …找不到一张清朝以前【足部畸形的古尸照片】。」 |
| **emoji** | **正帖基本不用（25 篇样本中 0 个）**；简介里才用（👀📝🎬🚀）⇒ **正文 = 不用 emoji** | 全部 25 篇正文无 emoji；简介：「…刷热点👀，发文章📝和视频🎬，常在评论区唠嗑…🚀」 |
| **结尾** | **多无结尾**（一句说完成段）；**提问式**则用一个个反问收（无「评论区聊聊」类固定套路） | 「美国会把中文列为主科吗？」「建设不好自己国家的人，凭什么能建好别人的国家？」 |
| **题材 · 篇幅** | 汉文化/儒家 · 清史（缠足/满服/努尔哈赤）· 历史（三国/封神/楚）· 国际（印/俄/美/越）· 社会民生（演唱会/通勤/共享单车）· 科技/AI | 「厂字襟蜈蚣扣的设计元素明显源自新宾满服，为啥不能大大方方承认这一点呢？」 |
| **配图** | 历史作品列表**未见图片标识**；⚠️ 2026-11-11 配图双令后**改口径**：**单张** + 正文纯文字署名（「图：IT之家」）或平台免费图库，细则见 `SPEC §8.2` | — |
| **体裁分流（2026-11-11 12:1x 起 · **主通道已切换**；2026-11-14 12:0x 再次确认）** | ✅ **主通道 = 图文文章**（`/graphic/publish`，600–1500 字，7–10 段短段，**带 1 张合规图** + 图注署名）；🟡 **辅助 = 微头条**（≤400 字）—— 仅「话题性强 / 时效急 / 拆不出 3 段以上」时走。判定依据：11-11 12:0x 复核 `article/7706729234433917482` 与 `article/7706759795105088054` 两篇，**四条硬标准全过**（非 `/w/` URL · 图 normalWidth/Height 正常且 complete · 无版权/搬运/低质警告 · 页面「作品声明：内容由AI生成」正常展示），见 `news/2026-11-11.md`「12:0x 通道认定」。**11-14 12:0x 复核** `article/7707872567922606634`（538 字 / 1 图）四条**再次全过** ⇒ 主通道维持图文文章，见 `news/2026-11-14.md`「第 274 轮 · 发布与通道实测」。两通道**共用**本节文风，不另立风格 | 见 `drafts/2026-11-11-1000-arm-m42-article.md`、`/tmp/r251/fill.py`（麒麟 9050 稿 PARAS+TAIL）与 `2026-11-11-0700-gemini-robotics-25.md` |
| **发布后必做·AI 声明补勾（2026-11-14 12:0x 实证）** | 发布时勾了「引用AI」**不等于**公开页会展示「作品声明：内容由AI生成」。**固定收尾动作**：发布 → 打开公开页复核 `作品声明` → 若无 ⇒ 后台列表点「**修改**」→ 编辑页点「**引用AI**」（判据 `input[type=checkbox].checked` 由 false→true）→ 点「**发布**」重存（页脚会显示 `剩余修改次数：5`）→ 再复核 | `article/7707872567922606634`：首发 `DECL_TEXT NONE` → 补勾重存后 `作品声明：内容由AI生成`（首屏可见） |
| **评论发不出去的根因与正解（2026-11-15 15:2x 第 280 轮 · ⭐ 最重要）** | ① 发送键 = `button.submit-btn`，**在 React `onChange` 未触发时带 `disable` class**（实测 `btnCls:"submit-btn disable"`）；② 逐键输入**必须带 `text`**：`Input.dispatchKeyEvent {type:'keyDown', text:ch, unmodifiedText:ch, key:ch}`（只发 `keyDown/keyUp` 不带 `text` ⇒ React 收不到字符 ⇒ 按钮恒 `disable` ⇒ 点击无效，但脚本会误报 `ok:true`）；③ **提交前必须回读 `button.className`，不含 `disable` 才点**；④ **成功判据只能是「公开页评论列表 DOM 出现该文本 + 评论计数 +1」** —— 后端「评论管理」列表**有延迟同步**（第 279 轮判为「5 条全失败」，本轮在三个帖的公开页各见到一条「2 小时前」本号评论 ⇒ 其实已落库），「页面含作者昵称」因右栏恒真 ⇒ 假阳性；⑤ 回评按钮 `button.reply-btn`（楼内），点后输入框 placeholder 变「说点什么吧...」，提交路径与主评论相同。 | 本轮 3 条评论全部落地：`评论 2→3` / `1→2` / `1→2`，公开页均显示「刚刚 · 删除」；回评 Jacob2026 楼 `1→2` |
| **写作链路实测要点（2026-11-15 12:0x 第 279 轮补充）** | ① **选正文一律用 `.ProseMirror`** —— 这版 ProseMirror 容器属性是 `contenteditable="false"`，用 `[contenteditable=true]` **选不到**；② **插图仍会插 2 张**（即使只对 1 个 `input[type=file]` 置文件、面板显示「已上传 1 张图片」）⇒ 插图后用 evalJs 删掉容器里第 2 个 `img`，再点末段敲空格 + 退格触发同步；③ **图注框用 `textarea.pgc-img-caption-ipt`** 定位（`placeholder*="图片描述"` 在本版**不存在**）；④ 🚫 **不要按坐标盲点图注框**——点偏会把图节点整个删掉（本轮 `imgs` 2 → 0 只能重灌）；**顺序 = 先插图并修成 1 张 → 再点图注框**；⑤ 「引用AI」input 是 0×0 隐藏元素 ⇒ 点 label `span.byte-checkbox-inner-text`；⑥ **配图必先看图再发**：本轮首选图实为 X 推文截图、右上角带 `www.ithome.com` 水印 ⇒ 按禁令 11 弃用换图（只看 `watermark` URL 参数会漏判）；⑦ **评论落库判据不可用「页面含作者昵称」**——文章页右栏固定显示本号昵称，恒为真；新判据 = 评论计数 +1 且评论列表 DOM 出现该文本，或后台「评论管理」首条时间戳 = 本轮。 | 本轮 `article/7708244681385132598`：798 字 / 1 图 1024×576 / 图注「图：IT之家」/ 首发+引用AI 均 `checked:true` / 四硬标准 4/4 |
| **写作链路实测要点（2026-11-15 09:3x 第 278 轮补充）** | ① **插图**：工具栏 `.syl-toolbar-button[11]`（不是 [12]）→ 面板「本地上传」→ `DOM.setFileInputFiles`（⚠️ 页面上有 **2 个** `input[type=file]`，**只对一个置文件**，否则面板出现两个副本、「确定」后正文插 2 张同图）；「确定」在面板右下；② **图注** = `textarea[placeholder*="图片描述"]`（写成 `input` 找不到）；③ **字数**：`Input.insertText` 灌段后页面计数可能停在「共 0 字」⇒ 在正文里敲一个空格再 `Backspace` 触发重算（本轮 `共 746 字`）；④ **勾选框**（「头条首发」「引用AI」）在视口外 ⇒ 先 `scrollIntoView({block:'center'})` 再按坐标点；⑤ **评论框** `.comment-textarea` 是 `div[contenteditable]` 而非 textarea ⇒ 逐键前**先清空**，否则与残留文字拼接成重复句；⑥ 删除自己的评论 = 点「删除」→ 点浮出的「确认」。 | 本轮 `article/7708205146412483091`：746 字 / 图注「图：IT之家」/ 两勾选框均 `checked:true` / 四硬标准 4/4 |
| **写作链路实测要点（2026-11-15 21:3x 第 283 轮补充）** | ① **「插图必插 2 张」要更正**：用 `DOM.setFileInputFiles` 只对 **1 个** `input[type=file]` 置文件、「确定」后 `ProseMirror img=2`，但**第 2 个在隐藏 `<templ>` 里**（父节点 `display:none`、`getBoundingClientRect()` = 0×0）⇒ **可视化只有 1 张，不需要删**（第 280 轮已见此现象，本轮再次复现并确认判据 = 用 `offsetWidth>0` 数可见图，而不是数 `img` 总数）；② **长图可用**：1440×2776 的竖图在公开页渲染为 676×1303 正常显示，不必强制横图；③ **来源署名不算水印**：报道截图顶部「来源：科技日报」属原文署名，按禁令 11 的口径不算他站水印，图注标「图：IT之家」即可；④ **配图 URL 必须回填校验**：本轮初稿有 4 条 `🖼` URL 手工誊写出错（GET 404/错图），已按脚本落盘 JSON 逐条回填并全部复测 GET 200 ⇒ **采集落盘一律用脚本输出直接生成，不手工誊写 URL**；⑤ `toutiao.com/profile/<名字>` 已 404，找自己的历史帖 article id 只能从后台「作品管理 → 更多 → 查看评论」。 | 本轮 `article/7708391478107701823`：1021 字 / 1 图 1440×2776（页面 676×1303）/ 图注「图：IT之家」/ 首发+引用AI 均 `checked:true` / 四硬标准 4/4；引流评论 87→88 / 0→1 / 0→1 |
| **写作链路实测要点（2026-11-16 07:0x 第 284 轮补充）** | ① ⭐ **勾选框先读 `checked` 再决定点不点** —— 「头条首发」在写图注后**已默认勾上**，盲点一次反而把它**取消**（本轮 `checked:true → false` 后又点一次才恢复）；正确做法 = 先读 `input.checked`，`true` 就不点。② **编辑器页会残留上一轮 state**：`/graphic/publish` 新开时可能带着上一次的标题与正文（本轮首次开页 `共 1021 字` 是 283 轮内容）⇒ **先读 `共 N 字` / `.ProseMirror` 首段确认干净（`共 0 字` + `请输入正文`），脏就 `/json/close` 关掉再新开**。③ `vis.js` 判据复现：`img=2` 但 `offsetWidth>0` 的只有 1 张（440×330 / natural 1600×1200），第 2 个在隐藏 `<templ>`（`parentDisplay:none`）⇒ **不要删**。④ 看图核验流程：`viewimg.js <本地图> <截图输出>`（base64 注入 `about:blank` + `Emulation.setDeviceMetricsOverride` + `Page.captureScreenshot`）⇒ 多模态读图确认无二维码/水印。⑤ 后台「作品管理」的评论计数**有延迟**（本轮列表显示「1评论」而公开页 DOM `cnt:0`）⇒ 回评判据只看公开页 DOM。 | 本轮 `article/7708537952296649258`：777 字 / 21 段 / 1 图 1600×1200（页面 676×507）/ 图注「图：IT之家」/ 首发+引用AI 均 `checked:true` / 四硬标准 4/4；引流评论 1→2 / 7→8 / 0→1 |
### §A.8 采集与发布链路实测（2026-11-17 第 291 轮）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | ⚠️ **IT之家 路径段会翻页**（`1/027/` → `1/028/`）。任何「硬编码路径段」的解析都会**静默丢条目**（`art_id()` 全 None ⇒ continue），表现为 `RSS_ITEMS 12` 而正文 60 条。去重 key 一律用**整段路径** `1/028/060.htm`（与 `SEEN.md` 既有 2,900+ 行口径一致） | `news/ith_dedup.py` 的 `path_key()`；修前一连两轮误判「RSS 只回 46 条」 |
| 2 | 采集正文另存工具 `news/ith_extract.py`（正文 `id="paragraph"` + 首图 `data-original`）· 图片校验 `news/img_check.py`（200 + `image/*` + >5KB + `watermark` 标记）⇒ **采集落盘用脚本输出，不手工誊写 URL** | 本轮 17 条全部脚本产出，18 图 `BAD 0` |
| 3 | ⚠️ **公开页取证需 2–3 次 `Page.navigate`**：首次常停在信息流（`<article>` 高度 0 或看到一堆推荐流）⇒ 判据 = `article.getBoundingClientRect().height > 800` 才算加载完 | `s6_pubimg.py`：第 1 次 `NAV` 拿到 1966 |
| 4 | ⚠️ **首图 `naturalWidth` 未滚到图位时读作 `1`**（懒加载占位）⇒ 必须 `window.scrollTo(0, img.top-260)` 后再读；此时正常值如 `nw1440 nh810 → 渲染 676×380` | 第 291 轮 `IMGAT nw:1` → `VIS nw:1440 done:true` |
| 5 | ⚠️ **「查看更多」（评论区折叠）必须用真实鼠标点击**（`element.click()` / `MouseEvent` 派发均无效，与 2026-10-12 的「加载更多」同因）⇒ 展开后我发的新评论才会出现在 `.ttp-comment-item` 首位；**只靠「计数 +1」不能证明评论内容正确** | 第 291 轮评论 A：先判 FAIL（列表只有 3 条旧评论），真鼠标点击后首条 = 「Xmodel唠两句 … 1分钟前 删除」 |
| 6 | ⚠️ **平台会「由文章生成」一条同标题微头条**（后台首页与「作品管理」显示 `发布了微头条`、列表标「由文章生成」、展现 0）⇒ **不是重复发布**，不另计配额、不重复记账；其公开 `/w/` URL 后台不给 ⇒ **不伪造 URL**，只记事实 | 第 291 轮 09:37 两条记录（文章 + 由文章生成） |
| 7 | 配图取舍顺序：**先目视再定稿**。本轮弃 2 张 —— X 帖截图（带 `www.ithome.com` 角标）、官方芯片图（左下 `ithome.com` 水印）；最终用厂商**产品白底图**。`watermark` 参数只是提示，**肉眼看到角标/水印才算弃** | `s5`/`s7` 三张截图目视结论 |
| 8 | 编辑器页 `共 N 字` 是**页面口径**（含标点/数字），与草稿的「中文字数」不同（本轮 809 vs 639）⇒ 记账须写明用的是哪个口径 | 第 291 轮 `FILLED {wc:共 809 字, ps:27}` |
| **首句套路** | ① 直给判断句「…就是…」② 反问句「…吗？/凭…？」③ `@豆包 <问题>` ④ 「看评论：…」 | 「全盘否定儒家就是反汉反华」「看评论：承认别人优秀真不容易」 |

### §A.1 体裁张力说明（**重要 · 取舍口径**）
- 用户历史作品 = **反应式一句话短评**（展现普遍偏低：多数 25–3,556，最高 20,699）。
- 本线 10-11 15:01 首篇（尼康 AI 造假）= 按 SPEC §4 写成 **① 事实+来源 → ② 判断 → ③ 开放问题**（展现 83）。
- **取舍**：**句法/口吻/标点/emoji 一律按本檔（短、口语、无 emoji）**；**结构上**保留 §4 的「**一句事实（带来源）→ 短判断 → 开放问题**」，但**每段压到 1–2 句**，**不要「报告腔」**。

---

### §A.9 采集与发布链路实测（2026-11-17 第 292 轮）



| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **后台「作品管理」列表不给公开 `/article/` URL**。`a[href*="/article/"]` 计数为 **0**；「更多」菜单只有「加入合集 / 置顶 / 分享 / 设为仅我可见 / 删除」；本轮点「修改」与「查看评论」**均未跳转**（与 §A.5 第 4 条同类）；后台首页动态与 `document.documentElement.innerHTML` 里也搜不到 19 位 id（`article_id/item_id/group_id/pgc_id` 全空） | 本轮 4 次尝试（`moremenu.py` / `getid.py` / `viacmt.py` / `homefeed.py` / `srchid.py`）全部无 URL |
| 2 | ✅ **正解 = 走公开作者页取 URL**：`https://www.toutiao.com/c/user/4681540376/`（会 302 到 `/c/user/token/…`），首屏「全部」列表首条即最新文章，`a[href*="/article/"]` 直接给 `https://www.toutiao.com/article/<id>/` | 本轮 `authorpage.py`：首条标题「超算的入口…」→ `article/7708986069001404982`，一次命中 |
| 3 | ⚠️ **「共 N 条内容」计数确认有 ~40s 延迟**：「确认发布」后立刻读仍是旧值（`42 → 42`），**约 40–60s 后复读才 +1**（`42 → 43`）。**不要据此判发布失败**（承 §A.6 第 4 条，本轮再次复现） | `s4_confirm.py` 读到 42；`s0_base.py` 45s 后读到 43 |
| 4 | ✅ **列表卡片可直接读出发布状态**：`共 43 条内容 超算的入口… 11-17 12:04 已发布 已推送 首发 展现 14阅读 0点赞 1评论 0` ⇒ 「已推送」= 已过审分发；无「未通过 / 警告」字样即第 ③ 条合规 | `topcard.py` 文本片段 |
| 5 | ⚠️ **配图须目视，URL 无 `watermark` 参数也可能违规**：本轮 `1/028/133` 首图是**彭博社推文截图**，URL 干净但右上角带 `www.ithome.com` 角标 ⇒ 弃用，改选富岳机柜官方图（RIKEN/FUJITSU 为**设备本体标识**，不算他站水印，可过） | `viewimg.py` 目视两张截图对比 |
| 6 | ✅ **图文链路继续一次跑通**：`OPEN 共 0 字 / empty:true` → `FILLED 共 679 字 / ps:20` → `IMG n:2 vis:1 nw1920×673` → `CAP 图：IT之家` → `COV_AFTER 864x673`（平台自动取正文图）→ 点一次「确认发布」→ **43 条**；「头条首发」「引用AI」回读均 `true`，**一个都没点**（承 §A.2 纪律 1） | 本轮 s1–s4 日志 |
| 7 | ⚠️ **评论 `ERR_FILL_MISMATCH` 重试一次即成**：第一次回读 `len:0`（输入框没吃进字），**重新导航同帖**再发一次 → `FILLED len:22` → 落地 `10 → 11`。承 §A.2 补充：**换状态重试，不在原状态盲重试** | 本轮评论 C |
| 8 | ℹ️ **平台「由文章生成」的微头条会带来流量**：09:37 那篇的后台微头条从 0 涨到展现 155 / 阅读 7，而文章本体同期展现 155+ ⇒ 记账时不要把这条流量算成文章数据，也不要重复记一次发布 | `manage/content/all`：`7708947862582854163` + 一条标「由文章生成」 |



### §A.11 采集与发布链路实测（2026-11-17 第 294 轮 · **去重工具真 bug 已修**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔧 **`news/ith_dedup.py` 的去重一直没生效（本轮修）**：`path_key()` 用 `"/".join(seg[:3])` 会带**前导 `/`**（`/1/028/437.htm`），而 `SEEN.md` 主流写 `1/028/256` 式 ⇒ `k in seen` **恒 False**。修法：`lstrip("/")` + 兜底 `("/"+k in seen)` | 修前 `SEEN_HIT 0 / NEW 60`（`437`…`256` 本该命中，肉眼即可判假）；修后 `SEEN_HIT 4 / NEW 56`。历史轮报的 `SEEN_HIT 8` 来自 SEEN 里残留的 8 行带前导 `/` 的旧条目 |
| 2 | ⚠️ **「关键词命中」≠「违规提示」**：复核四硬标准第 ③ 条时，全页 `includes('搬运')` **命中**，但定位后发现是**正文句子**（「很大一部分是**搬运**信息」）。正确判据 = 只看**叶子节点短文本（<120 字）+ 通知 / banner / notice / tip / warn / audit / status 类容器** | 本轮 `WARN {article:["搬运"]}` 假阳性 → 改判据后 `NOTICE []`；截图目视页面无任何警告条 |
| 3 | ✅ **「共 N 条内容」本轮即时更新**（44 → 45 一次读到），承 §A.9 第 3 条：读到旧值先等 45s 复读，别据此判失败 | `s4_confirm.py` AFTER_CONFIRM 直接读到 `共 45 条内容` |
| 4 | ✅ **首发文章卡片状态分两段**：刚发布为 `已发布 首发`，过审后才补 `已推送`（15:05 那篇 18:2x 已带三个标记，18:09 那篇当时只有两个）⇒ 记账照实写当时读到的标记串 | `card2.py`：`雷诺扩招裁员… 11-17 18:09 已发布 首发 展现 12阅读 0点赞 1评论 0` |
| 5 | ⚠️ **`/ch/tech` 首屏政治 / 历史人物题材占比高**：23 条里 8 条是政治、外交、党史类 ⇒ 按禁令 9 一律不进；可用候选集中在中段 | `feed.py` 输出逐条目视筛选 |
| 6 | ⚠️ **评论楼热度也要挑**：`tencent`（365 评论，措辞极端）/ `gpt6`（112 评论，话题宏大易引战）**主动不进**；只进平和技术楼（1 / 3 / 0 评论） | `probe3.py` 8 帖实测 |
| 7 | ✅ **配图下载链路（只下当次 1 张）**：`curl -H 'Referer: https://www.ithome.com/'` → `file` 确认 `PNG image data 1200 x 795` → `viewimg.py` 注入截图**目视**确认无二维码 / 微信号 / 他站水印 → 才定稿 | `imgs/2026-11-17-1805-reno.png` 1,522,017 B |
| 8 | ⚠️ **本线工作区没有 `news/toutiao/cmt.py`**（脚本都放 `/tmp/r<轮>/cdp/`）⇒ 评论脚本路径写错会直接 `No such file`，白等一轮；复制旧轮工具时先 `grep -rn 'r29' .` 查残留硬编码 | 本轮 A 首发起步失败一次（`python3 news/toutiao/cmt.py`），改用 `/tmp/r294/cdp/cmt.py` 后一次成功 |

### §A.12 采集与发布链路实测（2026-11-17 第 295 轮 · **纯文字稿链路 + 封面「无封面」口径**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **纯文字稿不能复用「必带 1 图」脚本**：照抄 `s2_img.py` 会把图（连图注）灌进正文。**纯文字稿的发布前最后一读必须包含 `imgs` 数**，非 0 就不发 | 本轮弃图后仍跑了一把 `s2_img.py` ⇒ `IMG n:2 vis:1`、图注「图：IT之家」被写入；靠 `s2j_check` 回读才发现 |
| 2 | 🔧 **ProseMirror 图片节点删法**：图片在 `div.syl-selected-card` 卡片里（内含 1 张隐藏 templ 图 + 1 张可见图）。**点图片 → 卡片获得 `syl-selected-card` 类 → 按 `Delete`** 才整节点删除；`Backspace` 只会吞掉前面的正文汉字（本轮吞掉「平？」两字，已补回） | `s2i_probe` 读到 `cls:"syl-selected-card"` 后单发 `Delete` ⇒ `imgs 0 / cap 0 / kids 19` |
| 3 | ✅ **封面口径补充**：「封面必填」只在「单图」模式下成立。**无正文图时点「无封面」radio（`checked:true`）即可正常「预览并发布」**，与 §A.4 不冲突 | `s2l_nocov`：`radio 无封面:true` → 预览页出现「返回编辑 / 确认发布」 |
| 4 | ✅ **四硬标准第 ② 条在纯文字稿上的读法**：判 `article img = 0` + 正文首尾完整（首段 → 结尾开放问题）+ 无占位框；不能沿用「滚到图位看渲染尺寸」 | `v1.py`：`IMGS {"n":0}`、`TEXT len 693` 首尾一致 |
| 5 | ⚠️ **IT之家同篇多张图可能都带角标**：`1/028/503` 4 张图，第 1 张（首页图）右上角、第 3 张（实机画面）左上角**都嵌 `IT之家` + `www.ithome.com`**。⇒ 弃图要**逐张目视**，不要以为换一张就干净；换到第 2 张前先想「同一批素材大概率同款水印」 | `viewimg.py` 两次注入截图目视 |
| 6 | ⚠️ **探楼 RECHECK 偶发 `评论 0 / items 0`**：导航后 7s + 滚 50% 仍可能读到空评论区（页面未渲染完）⇒ **必须单独再核验一次**（等 9–10s + 分段滚动 4 段）才判成败 | 评论 C：`AFTER 2→3` 但 `RECHECK 评论 1/0` ⇒ 单独 `v_c.py` 复读 `cmt 3 / items 3 / mine_text true` |
| 7 | ✅ **评论落地三件套同时具备才算成功**：计数 +1、`.ttp-comment-item` 数增加、列表出现本号文本（本轮 3/3 全具备） | A 4→5 / B 3→4 / C 2→3 |

### §A.13 采集与发布链路实测（2026-11-17 第 296 轮 · **配图「先目视再定稿」 + `/w/` 页探楼失效**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **发布前必须把候选图「注入浏览器 + 截图 + 目视」**，`img_check.py` 只验得到 200/尺寸/水印参数，验不到「这是不是第三方榜单截图 / 有没有品牌 logo」 | `1/028/534`（商汤）首图 GET 200 + 119KB 全过校验，目视后是**满屏柱状图的第三方评测图**（含多家厂商 logo）⇒ 弃图、换选题；改取 `1/028/529` 首图目视确认「机房 + 夕阳、无任何水印文字」才定稿 |
| 2 | ⚠️ **「同一张图换压缩参数」不是换图**：`…png?x-bce-process=image/resize,m_lfit,w_800` 得到的是**同一张**（800×379 vs 1080×511），目视一模一样 ⇒ 想换图**只能换 `newsuploadfiles` 里的另一个文件名** | 两次 `viewimg.py` 注入截图逐像素对比一致 |
| 3 | ✅ **`newsuploadfiles/*.png` 未必真是 PNG**：本轮 `.png` URL 实为 **JPEG**（`file` 判 `JPEG image data`）⇒ 落盘前用 `file` 校验、扩展名按实际改（本轮改成 `.jpg`），别按 URL 后缀命名 | `file imgs/2026-11-17-2250-aws.jpg` → `JPEG 1440x809` |
| 4 | 🔑 **发文后「共 N 条内容」可能延迟**：确认发布后立刻读是 **46**（与发布前相同），8 秒后复查才变 **47** ⇒ 判发布成败**不要只看第一时间读数**，要「稍后复查 + 作者页首条 URL」双确认 | `s4_confirm.py` → `共 46`；8s 后 `s0_base.py` → `共 47`；作者页首条 `article/7709141112828461622` |
| 5 | ⚠️ **公开页「图没了」先看是不是懒加载**：`<article img>` 在首屏读到 `nw1440 nh809 w676 c:true`，但截首屏时图位是空白 ⇒ 必须**滚到图位再截**才算第 ② 条通过（滚到 `imgTop-260` 后图与图注同屏可见） | `scroll_img.py`：`IMG_POS y=1276` → 截图目视机房图 + 「图：IT之家」 |
| 6 | ⚠️ **`/w/` 微头条页探楼失效**：`/w/<id>/` 打开后正文、`评论 N` 都在，但**没有 `.comment-textarea`**（`BEFORE len:-1 cls:NF`）⇒ 微头条楼**走不通** `cmt.py`，探楼一律只投 `/article/` | 对 `w/1882077333023820` 试投 ⇒ `NO_TEXTAREA`，未发、未计次 |
| 7 | ⚠️ **微头条页底部会挂「别人的推荐微头条」**：`/w/1882088154985484`（自家 15:05 篇）页尾出现「WorkBuddy + 豆包…`评论11`」的**他人帖子与评论数**；用 `body.innerText.match(/评论\s*(\d+)/)` 取数会**误读成自家评论数** ⇒ 取数必须限定 `article` / 评论区容器 | `vw5.py` `seg` 原文：`…举报 评论 0 评论 太牛了！WorkBuddy + 豆包，一晚上完结一部漫剧…海上从容远航的君70评论11月01日` |

### §A.14 采集与发布链路实测（2026-11-18 第 298 轮 · **ProseMirror 删图不稳定 / 封面校验静默失败**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **发帖前必须先读后台计数 + 作者页首条**：并发进程也会发稿（本日 07:37 与 09:0x 各一篇已落库），不看就动手会重复发 | `base.py` → `共 49 条内容`；`author.py` → 作者页首条 = `article/7709287901104620075`（语音稿），印证台账里没有记录的两次发布 |
| 2 | ⚠️ **ProseMirror 删图不稳定**：同一份 `fix4.py`（选中 `.syl-selected-card` → `Delete`）第一次成功（`imgs 0`），**第二次插入后再删就删不掉**（`SEL sel:1` 但 `AFTER imgs 2`，`空格/退格` 同步也无效）⇒ 保守做法 = **一次插入即定稿，不要在同一编辑器里反复插删** | `fix4.out`（成功）vs `fix6/fix7.out`（失败）；最终靠「再插一次 → 删一次」把编辑器拉回 `imgs 0`，但**保存态的图随之丢失** |
| 3 | ⚠️ **封面区为空时「预览并发布」只弹 toast，不报错**：页面停在编辑态、按钮文字照旧；必须回读 `radio 无封面:checked` **且** 广告 radio 已选（`投放广告赚收益=true`）才真正进预览页 | `s3.out`：`btns ["添加至合集","预览","定时发布","预览并发布"]`（仍在编辑页）→ `fix8/fix9` 补点两个 radio 后 `btns ["添加至合集","返回编辑","确认发布"]` |
| 4 | ⚠️ **公开页首屏先渲染推荐流**：`document.querySelector('article')` 存在但 `innerText` 里没有本文，`img=0`、`作品声明` 找不到 ⇒ 判断「图没了 / 声明没了」前必须等 ≥10s 并**比对 `document.title` 与目标标题** | `v1b.out`（title 正确但 `art:0`、截图是推荐流）→ `v2b.out`（`declIdx 97`、正文「一台无人驾驶出租车想超过…」） |
| 5 | ✅ **后台列表的 `审核` / `未通过` 是筛选页签文字**，不是文章警告；判警告要看「该文章卡片附近」或详情页叶子节点 | `card3.out` `WARN hit ["未通过","审核"]`，而卡片实读 `已发布 已推送 首发 展现 0 阅读 0 点赞 0 评论 0` |
| 6 | 🔑 **自赞首读 `NF` 不代表失败**：点击后按钮被重绘移除，`document.querySelector('.detail-like')` 读到 `NF`；以**重载后的 `detail-like like \| 1`** 为判据 | `like2.out`：`AFTER_CLICK NF` → `RELOAD detail-like like \| 1` |
| 7 | ⚠️ **IT之家配图「干净率」低**：本轮首选图（乐天证券公告）是**官方公告截图**，图内左下角嵌 `IT之家` + `www.ithome.com`，`img_check.py` 全过（200 / image/jpeg / 105,631 B）但仍须弃用 ⇒ **每张都要目视** | `view618.png` 目视；改取 `1/028/600` Waymo 车型图（`view600.png` 干净、780×438）才通过 |

### §A.16 采集与发布链路实测（2026-11-18 第 301 轮 · **官方示意图最好用 / 量子位图床要 Referer**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | ✅ **科技史类选题是配图的最优解**：旅行者 1 号（`1/028/745`）首图 = NASA 官方探测器示意图（深空星空 + 探测器本体），**无二维码 / 无水印 / 无社交 UI / 无站标角标**，1 张即过。⇒ 配图优先级再明确一档：**官方航天/厂商示意图 > 厂商产品图 > 新闻现场照 > 名人截图（多数弃）** | `viewimg.py` → `view_voyager.png` 目视；`2026-11-18-1505-voyager.jpg`（57,367 B / 1200×675） |
| 2 | ⚠️ **量子位图床 `i.qbitai.com` 不带 Referer 会失败**：`img_check.py` 默认 Referer 是 `ithome.com`，对量子位图返回空 body ⇒ 误判 `BAD`。**校验量子位图必须 `check(u, referer='https://www.qbitai.com/')`** | `BAD None 0 …i.qbitai.com/…png` → 带 Referer 后 `200 image/png 77,939 ok:True` |
| 3 | ⚠️ **IT之家 RSS 路径段手敲会整批 404**：本轮 RSS 仍在 `1/028/`，误用 `1/029/` 时 6 篇全部 `status None / HTTPError 404`。**键值只从 `dedup.json` 的 `key` 字段取** | `ith_extract.py` 输出 6×`HTTP Error 404` → 改 `1/028/` 后 6/6 `status 200` |
| 4 | ⚠️ **`cmt.py` 前台必超 30s**（导航 10s + 逐键 + 提交 6s + 重载 11s + 滚动 3s）⇒ 一律 `nohup setsid … &` 后台跑再 `cat`；**后台跑时先看 `AFTER` 计数**再等 `RECHECK`，避免重复提交 | 首次前台调用 `Command timed out after 30000ms`；改后台后 A/B/C 三条均一次成功 |
| 5 | 🔑 **作者页取文章 URL 用链接列表判，不用 `innerText.indexOf`**：长标题含「」等符号时 `innerText` 匹配会落空（`found:false`），但 `[...document.querySelectorAll('a')].filter(h=>/article\/\d{10,}/)` 里**第二个链接的文本就是标题** | `authorpage.py`：`found:false` 但 `first[]` 已含 `article/7709403617102529043` + 完整标题 |
| 6 | ✅ **「共 N 条内容」本轮即时更新**：`s4_confirm.py` 点「确认发布」后 6s 读到的就是 `共 53 条内容`（52→53），无需轮询 | `AFTER_CONFIRM {"cnt":"共 53 条内容"}` |

### §A.17 采集与发布链路实测（2026-11-18 第 302 轮 · **官网界面图最好用 / 量子位正文容器 / 评论「先 AFTER 后 RECHECK」不代表没发**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | ✅ **「官网界面截图」是本轮最优配图**：`510916` 首图 = InclusionMed 官网首屏（1200×675，显示器上跑着站点），**无二维码 / 无水印 / 无社交 UI / 无站标角标**，1 张即过；同一篇的第二张图（作者机构列表）虽干净但**无视觉信息、内嵌 `https://inclusionmed...` 网页地址** ⇒ 不用 | `viewimg.py` → `view_q_logo.png`（用）/ `view_q_ed.png`（弃） |
| 2 | ⚠️ **量子位正文容器 = `<div class="article">`**（不是 `article-content` / `<article>`）。用错容器会拿到 **`chars 0`**（页面 shell 里没有这些 class）；容器对了正文 1,063 字符 + 2 张正文图 | `/tmp/r302/gen.py` 首跑 `200 0` → 改 `starts=["<div class=\"article\">"]` 后 `200 1063` |
| 3 | 🔑 **评论「`AFTER` 未 +1、`RECHECK mine:false`」多半是页面没渲染完，不是没发出去**：E 帖首次 `AFTER 评论 0 / items 0`、`RECHECK 评论 2 mine:false`，用 `verify.py` 单独复读同一 URL 得 `评论 2 · items 2 · mine:true` ⇒ **不重发**，判据 = 另起一次导航复读（本轮 E 即如此）。⚠️ 本轮 E 曾因「首判失败」**误重发一次**（`cmtE2.out`：`1→2` 第二次成功），事后列表里会出现两条同文评论 —— 纪律：**首判失败先复读，复读仍失败才考虑重发，且重发前先看列表有没有同文** | `cmtE.out` / `cmtE2.out` / `vE2.out` |
| 4 | ✅ **本轮 5 条引流评论 4 条一次落地 + 1 条复读命中**（A `0→1` · B `0→1` · C `0→1` · D `1→2` 全部 `RECHECK mine:true`；E 复读 `评论 2`）⇒ 全站选帖式评论「一次成功率高」，不必像以前那样先探 10 帖 | `cmtA/B/C/D.out`、`cmtE.out`、`vE2.out` |
| 5 | ⚠️ **后台「概览 / 数据」页本轮读不到数字**：`/profile_v4/manage/overview` 与 `/profile_v4/manage/content/article` 都只渲染出左侧导航（`粉丝/阅读/展现` 全 `NONE`）⇒ **粉丝 / 阅读 / 收益本轮如实记「未重读」**，不编造、不沿用旧值 | `fans.out` / `fans2.out` |
| 6 | ✅ **发布链路（s0→s1→s2→s3→s4）依旧一次通过**：`共 1049 字 / ps 26` → `IMG {n:2, vis:1}` → 图注「图：量子位」→ `COV [867x675]` → `引用AI:false→true` → 「预览并发布」出现「确认发布」→ `共 53 → 54 条内容` | `s1.out` / `s2.out` / `s3.out` / `s4.out` |
| 7 | 🔑 **图注可以写「图：量子位」**（不只 IT之家）：署名跟**实际转载源**走，本轮选题源自量子位授权转载稿，图注与正文口径一致即可 | 公开页首屏目视：图下显示「图：量子位」 |

### §A.15 采集与发布链路实测（2026-11-18 第 300 轮 · **配图四选一 / 评论复核口径**）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **配图可用率排序（本轮 4 选 1）**：① **厂商官方产品宣传图**（KDDI INFOBAR ZERO 白底海报）目视干净 ⇒ 首选；② **人物/名人截图**（雷军采访海报）左上角嵌「人民日报 新媒体」标识 ⇒ 弃；③ **社交平台回应截图**（蔚来马麟回应）右上角嵌 `IT之家` + `www.ithome.com` ⇒ 弃；④ **短视频截图**（郑渊洁抖音）右侧含点赞/评论/关注 UI 与用户头像 ⇒ 弃。**结论：优先挑「产品本体的官方图」** | 4 张全部 `viewimg.py` 目视：`view_infobar.png`（用）/ `view_leijun.png` / `view_nio.png` / `view_zyj.png`（弃） |
| 2 | ✅ **`s2_img.py` 链路本轮一次成功**（未反复插删）：`IMG {n:2, vis:1}`（第 2 张在隐藏容器）→ 图注「图：IT之家」→ `COV [925x720]` → `BOXES_AFTER 引用AI:true / 头条首发:true` → 预览页出现「确认发布」→ `共 51 → 52 条内容` | `/tmp/r300/cdp/s2_img.py`、`s3_preview.py`、`s4b.py` |
| 3 | ⚠️ **复制上一轮脚本会带写死的输出路径**：`s1_fill.py` / `s2_img.py` 里仍有 `/tmp/r298/cdp/…` ⇒ 截图与 `draft.json` 落到旧目录（`ready.png` 找不到）。**复制后先 `grep -n '/tmp/r29' *.py` 再跑** | `grep ready.png s2_img.py` → `/tmp/r298/cdp/ready.png` |
| 4 | 🔑 **公开页评论「RECHECK mine:false」不能直接判失败**：失败可能只是页面未渲染完。判据改为 **两次独立复核**（重新导航 + 滚到评论区 55% 再读）。本轮 C（`7709334668046287400`）与 D（`7708743909672747520`）首次复核 `mine:false`，单独复读均 `items 1 · mine:true` ⇒ 成立；B（`7709294487461200424`）三次复核都是 `评论 1` ⇒ 记「已提交但未核实」，**不重发**（防重复评论） | `cmtC.out` / `cmtD.out` / `vC.out` / `vD.out`；`cmtB.out` + `vB.out` |
| 5 | ✅ **楼内「回复」不需要先展开「查看更多」**：`.ttp-comment-item` 里 `button` 文本为「回复」，点后输入框 placeholder 读作 `null` 但 `textContent` 可正常写入，提交后列表出现「Xmodel唠两句 … 刚刚 · 删除」，`评论 1 → 2` | `reply.py`：`REPLYBTN {"t":"回复"}` → `FILLED {len:34, cls:"submit-btn"}` → `RECHECK cmt:2 mine:true` |
| 6 | ⚠️ **本号 4 篇里只有 1 篇有读者评论**（`7709326713573884457` 三星 TV-1）：其余 `0` 评论 ⇒ 回评候选稀缺，探楼时应优先挑**已有真实读者提问**的帖子，而不是自己刚发的新文 | `own.py` / `owncmt.py` 输出 |


## §B 评论体（单独记 · 20 条实测 · **2026-10-12 逐条复核**）



| 项 | 实测结论 | 实证片段（原文节选 · **实测**） |
|:--|:--|:--|
| **平均字数** | 收到评论**两极**：**豆包机器人** = 长回复（**40–120 字**）；**真实用户** = **短句** | 机器人：「除了中国，目前考古公认的独立原生农耕中心还有这几个：1.西亚新月沃地…」（08-12，**102 字**）；真实用户：「**伪史论祸害青少年**」（08-15，**7 字**） |
| **有无梗** | 有；口语调侃、网感词 | 「纯纯的二五仔啊」（08-27 评申公豹）· 「这话太对了😂」 |
| **emoji** | **机器人**爱用（😊😂👍📚✨👀👘🌸 —— 20 条中 **11 条带 emoji**）；**真实用户**基本不用 ⇒ **我们发评论 = 不用 emoji** | 「…没史料支撑哦😊」（09-14）·「期待更多分享！🌸」（06-22） |
| **是否提问** | 机器人常以**反问收尾**勾互动（= 平台互动机制） | 「你觉得哪部作品最有启发性呢？📚✨」（06-13）·「北大和上海的精神，你怎么理解的？」（07-29）·「新宾满服的文化底蕴能介绍更多吗？👀👘」（06-18） |
| **作答者分布（新）** | 20 条中 **17 条（85%）为「豆包」机器人**作答，仅 **3 条**为真实用户（08-15 手机用户 / 07-22 广文博记 / …）⇒ 佐证本人**惯于向 AI 发问**后由 AI 回帖（⚠️ **机制未验证**：是否必由 `@豆包` 触发，未做验证） | 见上 + `PERSONA.md §3` |
| **热门度（新）** | 历史评论**点赞极低**（首帖最高赞 = **1 赞**）⇒ **神评门槛低**，短句 + 可核验事实更易被顶 | 首帖 `w/1878735833613380/` 评论区实测 |

> **⇒ 我发评论的口径（本轮 10 条实测校准）**：**≤40 字**（实测 **27–40 字**，中位 **34**）· 口语 · **不用 emoji** · **一句实质回应**（赞同 / 补一个有据事实 / 一句俏皮话）· **可留一个反问**勾人回复 · **不铺垫、不客套、不带话题标签**（本轮实测逐字见 `台账.md`「第 16 批 07:00 轮」表）。

---

## §C 仿写示例（**供写法参考 · 非发布件** · 已按 §D 去越线）

**示例 1（时事短评 · 科技防诈）**
> 国安部都提醒了：接陌生电话先别急着出声。声纹跟密码不一样，泄了改不了，几秒就够。

**示例 2（历史文化短评）**
> 说汉文化只剩民俗的，是把骨架当成了皮。礼乐、诗词、史书，哪一样不是从先秦长出来的。

**示例 3（社会民生短评）**
> 免费的东西最贵。图省那几秒，最后赔进去的是你别处换不回来的东西。

> ⚠️ 示例只示范「**短句 + 口语 + 直判断 + 不铺垫**」的**语法**；**实际发文须按 `SPEC §4` 补一句事实来源与结尾开放问题**。

---

## §D 🚫 越线项（**禁止模仿 · 硬**）

> 用户历史作品中有**若干越线表述**（当时所发，非本轮）⇒ **只学文风，绝不照搬这些**。

| 越线类型 | 历史原文（**反面教材 · 禁模仿**） | 依据 |
|:--|:--|:--|
| **侮辱性群体称谓** | 「满遗的蛆又出来咕蛹了」 | SPEC §2.1 **禁用「满遗」等一切侮辱性称谓** |
| **群体归因/贬损** | 「那些漠北蛮夷根本说不出这种话…」 | SPEC §2.1 **不写「××族如何如何」** |
| **血统论** | 「@豆包 李瀚文不像纯种汉人」 | SPEC §2.1 **不比较民族优劣 / 不涉血统** |
| **涉政涉军言论** | 「每天给新德里打10发火箭弹以换取谈判优势」「俄罗斯授意它的小木偶恶心我们」 | SPEC §2.3 **不碰政治/军事** |
| **他人评论中的激烈用语** | 「批判正宗儒家思想的人都是汉奸卖国贼！」 | SPEC §2 **不煽动 / 不制造对立** |

> ✅ **仍然可用的「文风内核」**：**短 · 直 · 口语 · 有立场** —— 立场走 §1 正向表达（拥护党和国家 / 拥护民族大团结 / 爱汉文化 / 批「作为历史政权的清朝」须**附史实**，见 SPEC §2.1.1）。

---

### §A.10 采集与发布链路实测（2026-11-17 第 293 轮）

| # | 结论 | 依据 |
|:--|:--|:--|
| 1 | 🔑 **`.comment-textarea` 是 `contenteditable` div，不是 `<textarea>`**，且页面初始常把它排在视口下方（本轮 `top≈1053`，视口高 760）⇒ 只 `scrollIntoView` 后按 `getBoundingClientRect` 算坐标点击**仍会落空**，逐键输入全部丢失（`FILLED len:0` → `ERR_FILL_MISMATCH`） | 评论 A 第 1 投：`BEFORE len:0 / cls:submit-btn disable` → `FILLED len:0`；改 `window.scrollTo(0, rect.top+scrollY-300)` 后 `FILLED len:26 / cls:submit-btn`，一次落地 |
| 2 | ✅ **评论落地判据仍用「评论计数 +1 且页面出现本人昵称」**；`AFTER` 与 `RECHECK` 各读一次，两次一致才算成功 | A `3→4`、B `0→1`、C `0→1`，三条 `mine_shown=True` |
| 3 | ⚠️ **前台 30s 超时 ≠ 作业被终止**：批量探楼（11 帖）一定会超时 ⇒ 必须 `nohup setsid python3 … > out 2>&1 < /dev/null &`，再分段读日志 | 第 1 次前台跑被 kill；后台版 90s 内跑完 11 帖 |
| 4 | ⚠️ **多帖连续 `nav` 有渲染延迟**：`sleep(5)` 不够，标题会串到上一帖、评论数正则读不到 ⇒ `sleep(8)` + `scrollTo(0, scrollHeight*0.55)` 后再读 | probe 版 5s 读到的 `title` 与目标帖不符，probe2 版 8s 后全部对齐 |
| 5 | ✅ **后台首页动态把文章显示成「发布了微头条」**：这是平台「由文章生成」的微头条，**不另计配额、不重复记账**（承 §A.8 第 6 条） | `stats.py`：`11-17 15:05 发布了微头条 榜单只认机柜…`，而 `/graphic/articles` 卡片为文章形态 `已发布 已推送 首发` |
| 6 | ✅ **「共 N 条内容」本轮即时更新**（43→44 一次读到），说明 §A.9 第 3 条的 ~40s 延迟**不是稳定现象** ⇒ 读到旧值先等 45s 复读一次再判 | `s4_confirm.py` AFTER_CONFIRM 直接读到 `共 44 条内容` |
| 7 | ⚠️ **自赞按钮可能在视口外**（本轮 `y=200` 但实际不可点）：先 `window.scrollTo(0,400)` 再算坐标；点击后**必须 `nav` 重载复核** | 第 1 次 `AFTER_CLICK 赞`（未生效）→ 滚动后 `detail-like like 1` → 重载仍 `like 1` |
| 8 | ⚠️ **复制旧轮 `common.py` 会覆盖旧轮截图**（脚本里 `ready.png` / `preview.png` 路径硬编码到旧目录）⇒ 复制工具时先 `sed` 改路径，否则旧轮证据被新图覆盖 | 本轮 s2 写的 `ready.png` 落到 `/tmp/r292/cdp/` |
| 9 | 🔑 **图内嵌角标才是最容易被漏判的水印**：`1/028/187`（黄仁勋 X 主页）URL 完全干净、>`image/*` 正常、数值校验全过，但**图内右下角嵌了 `IT之家` logo + `www.ithome.com`** ⇒ 只有 `viewimg.py` 注入截图目视才能发现 | 本轮弃图 1 张；改选 Lux 官方渲染图（机身 DOE/AMD/HPE/Oracle 为设备本体标识） |

### §A.2 发布/互动三条硬纪律（2026-11-16 10:3x 第 285 轮实测 · 每轮照做）

| # | 纪律 | 为什么（实证） |
|:--|:--|:--|
| 1 | **勾选框先读 `checked`，`true` 不点** | 「头条首发」在写完图注后**常已默认勾上**；盲点一次会把它**取消**（第 284 轮 `true→false`）。285 轮先读 ⇒ 读到 `true` **未点**，状态保持正确。 |
| 2 | **自赞前先读 `detail-like` 的 class** | 进公开页时若已是 `detail-like like`（之前点过），再点会**取消赞**（285 轮实际踩到：`1` → 「赞」），须再点回。**只在 class 不含 `like` 时才点**。 |
| 3 | **平台会把文章自动转成同名微头条** | 285 轮 09:34 发文章，09:35 后台出现同名**微头条**，标注「**由文章生成**」。**不是本线重复发布**，勿删勿慌，也不要在台账里记成两次发布。 |

补充（同为 285 轮实测）：
- 评论逐键输入偶发 `ABORT_TYPED_MISMATCH`（输入框回读为空）⇒ **重新导航该帖 + 确认 `.comment-textarea` 存在且可编辑后再发**，重试一次即成功；**不要在同一状态盲目重试**。
- 插图后 `ProseMirror img=2` 但**可见图 = 1**（第 2 个在隐藏 `<templ>`，283/284/285 **三次复现**）⇒ 不必删。
- `DOM.querySelectorAll('input[type=file]')` 返回 **2 个** ⇒ 只用 **`nodeIds[0]`**。
- 正文段落用 `Input.insertText` **逐段 + Enter**，27–30 段可一次灌完；末段补空格 + 退格触发同步。

## §A.4 第 287 轮实测要点（2026-11-16 15:0x · **「展示封面」现在是必填，不选就发不出去**）

> ⚠️ **2026-11-16 18:0x（第 288 轮）复核订正**：本表第 1 条**只说对一半** —— 封面确实是必填项（面板里有红点「*展示封面」），但**正文已插入图片时，平台会自动把该图设为封面**（第 288 轮实测：`COV_BEFORE` 即为「编辑 替换」、回读 `864×673`，全程**没点封面区**也能正常「预览并发布」）。正确做法 = **先读 `.article-cover-images` 里有没有 `img`**：有就用它（只要 >672×462 即合规），**没有**才去「免费正版图片」tab 选。

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **封面必填**：不选「展示封面」直接点「预览并发布」**完全无反应** | 连点 2 次、等 16 s，页面仍停在 `/graphic/publish`、`iframe` 0 个、`确认发布` 0 个；点击前截图确认按钮在视口内、无遮挡。**这是 286 轮及以前没有的**，别误判成「点击失败」去重复点 |
| 2 | **封面面板有 4 个 tab**：正文图片 / 上传图片 / **免费正版图片** / 我的素材 | 点封面区 `.article-cover-images` 的「+」弹出右侧面板；「正文图片」里本文 1204×336 的价格表被判「**图片尺寸过小**」（面板原文：封面图尺寸建议大于 **672×462**，不可小于 **452×352**） |
| 3 | **封面改用「免费正版图片」tab**（平台图库，零版权风险） | 搜索框留空即「全部」→ 点一张 → 面板底部「确定」；回读 `.article-cover-images img` = `nw613 nh477`，面板提示「最多可选择 1 张，已选择 1 张图片」 |
| 4 | 🚫 **封面选图不要按坐标盲点** | 本轮按「第 4 行第 4 张」坐标点下去，实际选中旁边那张（浮层显示图名「北京 CBD 夏日全景图」）⇒ **以面板「已选择 N 张」+ 回读 `img.src/naturalWidth` 为准** |
| 5 | **「引用AI」真实鼠标点击打不到 0×0 隐藏 input** | `Input.dispatchMouseEvent` 点在 label 中心后 `checked` 仍为 `false`（input 的 `getBoundingClientRect()` 是 0×0）；改 `(ai.closest('label')||ai.parentElement).click()` ⇒ `checked:true`。**发布前必须回读 `checked`**（STYLE §A.2 纪律 1 不变） |
| 6 | **评论「计数 +1」但 DOM 读不到时不要重投** | 本轮 B 条（`article/7708320995916153384`）计数 8→9，但重导航 3 次、滚到楼底、找「查看更多」均**未读到本号文本** ⇒ 记「存疑」，**不重投**（避免自我重复评论）；下一轮若见到再补记 |

## §A.6 第 289 轮实测要点（2026-11-16 21:3x · **先看图再定稿**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | ⚠️ **配图必须先目视再定选题** | 本轮先按 `1/027/830`（iPhone 6 Plus 刷 iOS 14.8）写完 19 段稿才下载其唯一配图，看图发现右上角有「**Celestial紗雪 bilibili**」水印（他人平台 + 作者水印）⇒ 按禁令 11 弃图，整篇作废改选题。**顺序应改为：候选 → 下载并目视首图 → 合规才写稿** |
| 2 | ✅ **图文链路仍一次跑通** | `OPEN 共 0 字 / empty:true` → `FILLED 共 775 字 / ps:19 / http:false` → `IMG n:2 vis:1 nw1088×1374` → `CAP 图：IT之家` → `COV_BEFORE 编辑替换 → COV_AFTER 1088x847`（平台自动取正文图）→ `PREVIEW ifr:1 cf:1 pgc_id` → 点一次「确认发布」→ `cnt 39 → 40`；中途**不导航**（承 §A.5 第 1 条） |
| 3 | ✅ **勾选框仍默认已勾** | 回读 `{头条首发:true, 引用AI:true}` 均 true ⇒ **一个都没点**（承 §A.2 纪律 1 / §A.4 第 1 条） |
| 4 | ⚠️ **评论计数有刷新延迟，别急着判 FAIL** | `cmt.py` 提交后重载仅等 7s，读到 `cnt 44 → 44` 判 `RESULT FAIL`；再单独核验（滚 1200/2000/3000px）读到 **45** 且列表出现「Xmodel唠两句 … 刚刚 · 删除」⇒ 属**假失败**。**判据：重载后等 ≥10s 或做二次核验，且计数 +1 优先于「列表出现文本」**（新楼常落折叠区）。确认失败也不重发，避免重复评论 |
| 5 | ✅ **0 评论楼不进** | 探楼时 `cnt:0 / items:[]` 的帖子（富岳 / 吴恩达 / 145B 模型）全部跳过；已有对立情绪留言的楼（薛澜）只判读不评论 |
| 6 | ✅ **自赞需重载复核** | `detail-like` → `detail-like like`「1」后重载仍为 `like`「1」才算成功（承 §A.5 第 6 条） |

## §A.7 第 290 轮实测要点（2026-11-17 07:0x · **没读正文就没有字段可写**）

| # | 要点 | 实测 |
|:--|:--|:--|
| 1 | 🔑 **数字与 URL 只能来自「本轮抓到的正文」或「本轮 GET 验证过的图」** | 本轮初稿凭 RSS 短标题把 `1/027/949` 写成「小米财报 113 亿」（实为 OPPO Watch 5 发布），并给 `962` 填了两条**占位图 URL**（不存在的 `OPPOWatch5.jpg` / `travellerEV.jpg`）⇒ 自查时发现并全部重抓正文改写。**铁律：入账前每个数字问一句「我在哪段正文里读到的」，答不上就删** |
| 2 | ⚠️ **IT之家 RSS 条数会变** | 本轮 RSS 只返回 **46 条**（往日 60），最新 id `993`（11-16 15:04）；不能把「60 条」当固定口径写进总结 |
| 3 | ⚠️ **频道页（`/ch/tech`、`/ch/finance`）首屏过半是政治·司法·伤亡标题** | 本轮两频道前 14 条中约 8 条命中禁令 9 ⇒ 选题前先按标题过滤，再进楼 |
| 4 | ✅ **图文链路第 4 次一次跑通（含「先读基线再开编辑器」）** | `BASE 共 40 条内容` → `OPEN 共 0 字 / empty:true` → `FILLED 共 743 字 / ps:19` → `IMG n:2 vis:1 nw739×415` → `CAP 图：IT之家` → `COV_BEFORE 编辑替换` → `COV_AFTER 533×415` → `PREVIEW pgc_id` → 点一次「确认发布」→ `cnt 40 → 41`；全程不导航 |
| 5 | 🔑 **`pgc_id` 可直接当文章 id 打开 `/article/<pgc_id>/`** | 后台列表里新文章的 `a.href` 指向 `graphic/preview?pgc_id=…`（拿不到 `/article/` 链接）⇒ 直接导航 `https://www.toutiao.com/article/<pgc_id>/`，实测落到 `/article/7708908813700579882/`、`isW:false`、`article:1`；**不必再等列表刷新** |
| 6 | ⚠️ **配图尺寸别贴合规下沿** | 本轮正文图 739×415、平台裁封面为 **533×415**，比 11-16 的 533 高，但**仍接近 672×462 的建议线** ⇒ 封面偏小可能影响点击；下轮优先选 ≥1000px 宽的新闻图 |
| 7 | 🚫 **他站榜单截图 / X 帖截图不能当配图** | `qwen4.jpg`（ARENA.AI 榜单，含他家 logo 与评分）、`xuzj.png`（IT之家自家 X 帖，带 ithome.com 角标）、`cybcab.jpg`（TESLA LIVE 压字 + youtube.com 字幕条）三张全部弃用；**通过的是厂商官方合作标识图**（无第三方水印） |
| 8 | ⚠️ **探楼普遍 0 评论，不凑数** | 本轮探 11 个帖，除 `7708572280955994659`（评论 7，气氛平和）外全为 0 ⇒ 只发 1 条引流评论、记 **1/40**，不为达标而进空楼或政治楼 |



## §A.5 第 288 轮实测要点（2026-11-16 18:0x · **编辑中途导航 = 稿子报废**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | 🔑 **发布链路必须一口气跑完**：填完标题/正文/图/图注/勾选后，**不要在同一标签页导航去别处**读数据 | 本轮第一次填完稿后导航到 `/graphic/articles` 读发布前计数 ⇒ 编辑器 state 全部丢失（草稿自动存进草稿箱 31 条，且无法从草稿箱重新打开）。正解：**先在别的步骤读好「共 N 条内容」基线，再开编辑器**，之后一次跑完「填稿 → 插图 → 图注 → 封面 → 勾选 → 预览 → 确认发布」 |
| 2 | **封面会自动取正文图** | 插图后 `.article-cover-images img` 直接是 `864×673`（正文 1920×673 的裁切版），无需再选；满足「>672×462」即可用（详见 §A.4 的订正说明） |
| 3 | **长链路放后台跑**：整条发布链路 ~90 s，超过前台 30 s 限制 | `nohup setsid python3 chain1.py > chain1.out 2>&1 < /dev/null &` + 轮询日志；**超时 ≠ 失败**，先读日志再决定是否重来 |
| 4 | ⚠️ **草稿箱「编辑」点不动** | 草稿列表里 `a.op-button`（编辑）与 `a.title` 的真实鼠标点击**均不跳转**（本轮重试 3 次，无新标签、无导航）；**不要在这上面耗时间**，直接重新灌稿 |
| 5 | ⚠️ **自赞必须重载复核** | 第一次点击后立即读是 `detail-like like`（文本「2」），**重载后回落为无 `like`**（未持久化）⇒ 再点一次 → 立即读「1」→ **再重载仍为 `like`「1」** 才算成功 |
| 6 | **配图文件名按真实 magic 定** | 本轮 IT之家 `.jpg` URL 返回 `image/jpeg`，但初存成 `.png` ⇒ 按 `ffd8ffe0` 改名 `.jpg`（配图令 ②「扩展名与 Content-Type 一致」） |
| 7 | **评论链路继续稳定（3/3）** | 沿用 §A.2 正解：逐键带 `text` → 回读 `submit-btn` 无 `disable` → 点 → 重导航看「计数 +1 且列表出现本号文本」；三条均见「刚刚 · 删除」 |

## §A.3 第 286 轮实测要点（2026-11-16 12:0x · **复核四条硬标准的正确读法**）

| # | 要点 | 实证 |
|:--|:--|:--|
| 1 | **公开页直开会被重定向到首页** | 第一次 `open /article/7708615594404266538/` 后 `location.href` 变成 `https://www.toutiao.com/`、`document.title` 为空、`article` 里读不到图 ⇒ **必须再 `Page.navigate` 一次**才停在 `/article/…` |
| 2 | **公开页首图是懒加载** | 不滚动时 `<img class="syl-page-img syl-img-loading">` 的 `src` 恒为 `data:image/gif;base64…`、`naturalWidth=1`、`currentSrc` 也是占位；**`window.scrollTo(0,300)` 后**才切为 `p3-sign.toutiaoimg.com/…`、`nw1440 nh810`、渲染 `676×380`。⇒ **第 ② 条判据必须在滚动之后读**，否则会把正常图误判为破图 |
| 3 | **「低质/违规」字样可能是推荐流别人的正文** | 本轮公开页 `innerText` 命中「低质」「违规」，逐字回溯上下文发现来自**推荐流里一篇讲网文清退的别人文章**，本号 `<article>` 内为 0 ⇒ 判第 ③ 条时要**限定在 `<article>` 范围**或回溯上下文，不能全文 match |
| 4 | **评论「输入成功≠落库」** | 黄仁勋帖两次尝试：第一次 `ERR_FILL_MISMATCH`；第二次 `len 30` 且 `submit-btn` 无 `disable`、点击后无报错，但重导航 **724 → 724**、列表无本号文本 ⇒ 该条未落库。另一次（RSI 帖）第一次 `FILLED len 64`（输入 35 字）却仍提交失败 ⇒ **回读长度须严格等于输入长度** |
| 5 | **首页/频道页候选多为禁令 9 题材** | `/ch/tech`、`/ch/finance` 首屏前 12 条大量时政/军事/司法/突发伤亡 ⇒ 选题时先按标题过滤，再进楼 |



| 工具 | 用途 | 说明 |
|:--|:--|:--|
| `run/news/fetch.py` | **一切抓取**（RSS / 正文 / 配图） | 零依赖，只用 `urllib`。🚫 **不要用 requests / urllib3**：本机 `~/.local/lib/python3*/site-packages/urllib3/_collections.py` 行为异常，会**静默截断正文**。用法：`get(url, referer=None)` → `{status,ctype,body,url,err}`；`get_text(url, referer)` → str。IT之家图片需 `referer='https://www.ithome.com/'` 否则防盗链。 |
| `run/news/ith_dedup.py` | IT之家 RSS 60 条去重 | `python3 news/ith_dedup.py` → 打印 `RSS_ITEMS / SEEN_HIT / NEW` + NEW 列表；判重用**子串**（`'1/027/<id>.htm' in SEEN`）。 |
| 采编工作区 | `run/news/batch281/` | 每条新闻一个 `NL-*.md`（人工判读结论：入账 / 弃用 + 理由），`INDEX.tsv` 汇总；`news/2026-11-15.md` 第 281 轮**只**从这些文件组装，不凭记忆写。 |

⚠️ **本机环境两坑（必须记）**：
1. 🚫 **禁止 `re` 里用「前导 `/` 的路径式 pattern」** —— 实测 `re.search('/1/027/', 'x/1/027/302.htm')` 返回 **None**（去掉前导 `/` 就正常）。去重判据一律 `substr in text` 或 `text.find(substr)`。
2. 🚫 **不要在 `run/` 目录下跑 `python3 - <<'PY'` 读 SEEN.md** —— 同目录内的工作文件会干扰读取（实测同一脚本输出会在两段 SEEN 之间漂移：一会儿说 `1/027/320` 在、一会儿说不在）。**一律写脚本文件到 `/tmp/` 再跑**（`/tmp/*.py`），或改用 `news/ith_dedup.py`。

## §E 更新纪律
- **每 +20 篇作品**，或**风格明显变化**时 → 更新本文件（保留旧版对比）。
- 每次发文前 **自检四项**：**开头（直给/反问）· 句长（1–2 句）· emoji（不用）· 结尾（开放问题）**。
