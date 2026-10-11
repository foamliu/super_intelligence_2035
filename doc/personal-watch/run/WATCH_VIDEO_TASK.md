# WATCH_VIDEO_TASK.md — 观察哨 · **video agent** 任务书

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_VIDEO.md` / `daily-memories-video/`；本线产物写 `video/`；**主战场 = 短剧项目仓**（见 §1）。
> ⚠️ **本文件 = 每轮「必读」的指令文件**：loop 只把**绝对路径**交给 cline，**agent 必须先用工具读全文**再干活（Windows 命令行长度限制所致，见 §8）→ 保持精简（目标 ≤ 32KB，红线 40KB）；历史轮次归档到 `daily-memories-video/`，不进 prompt。
> 📖 **动手前必读 §4**（`E:\code\stem_fest` 实战经验 · 8 节速览）。
> 🖥️ **本线与观察哨其他线不同：跑在 Windows 11 本机 `hx-c1000`（不是 Linux VM），无人在场（开机自启 + 无人登录）。**
> 📄 姊妹线（范式与铁律来源）：`WATCH_NEWS_TASK.md` / `WATCH_RESEARCH_TASK.md` / `WATCH_RECRUIT_TASK.md`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 本节由 **supervisor** 通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**。本节为「无」时，按 §1 / §2 自主推进。

### 🆕 运维指令 · 2026-10-11（🎬 **立线：`video` = 基于 ComfyUI 制作视频**；首个任务 = 完成《超级智能2035》视频制作）· 用户直令 · ⭐ 最高优先

> **用户原话（2026-10-11）**：「在 personal watch 目录下建个新的 agent 任务书和 loop … **这个新的任务叫 `video`，使命是基于 ComfyUI 制作视频**。第一项任务是：**完成超级智能2035 视频的制作** `D:\Users\Administrator\code\super_intelligence_2035_short_drama`。」

**① 使命（本线唯一目的）**：**用本机 ComfyUI 把《超级智能2035》短剧项目做成「可发布的视频成片」**。
- 主战场 = **短剧项目仓** `D:\Users\Administrator\code\super_intelligence_2035_short_drama`（42 章 · 逐镜分镜脚本已全部完成，**2203 镜 / 约 3h03m**）。
- 工具 = **本机 ComfyUI**（`http://127.0.0.1:8188`）+ **MCP `comfyui-drama`**（见 §0）。

**② 首个任务（P0）= 完成《超级智能2035》视频制作**
- **定义「完成」**：**每一章**都要产出**成片视频文件**（`OUTPUT/<章>/videos/` 或项目约定的成片路径），由「分镜帧 → I2V 视频片段 → 旁白 TTS → BGM/音效 → 合成（含字幕）」这条链路构成；最终按章汇总为可播放的 mp4。
- **不要一上来摊全 42 章** —— 先做「**1 章端到端样板**」（建议从**素材最全的章**开始，如 `OUTPUT/13_外骨骼/` 已有产物），把**流水线跑通并固化脚本**，再**按章滚动放量**。
- **每轮唤醒都要有「看得见的进展」**：要么新增/修复脚本，要么新增成片产物，要么在 `run/video/PLAN.md` 推进状态。🚫 **不得空转**。

**③ 交付物与记录**
- **本线记录**（入 `super_intelligence_2035` 仓）：`run/video/PLAN.md`（总计划 + 逐章状态表）· `run/video/PIPELINE.md`（固化的流水线/SOP）· `run/video/BLOCKERS.md`（阻塞与环境问题）· `run/MEMORY_VIDEO.md` · `run/daily-memories-video/<date>.md`。
- **成片与素材**（入短剧仓）：按项目既有约定（`OUTPUT/`、`ASSETS/`、`scripts/`）；**大文件（视频/音频/模型）不入 git**（遵项目 `.gitignore` + 本线体积纪律，见 §5）。

**④ 验收（硬）**：每个「已生成」的产物都要**亲眼核验存在**：文件存在 + **字节数 > 0** + 用 `ffprobe/ffmpeg` 读**时长/分辨率**（视频）或 `sound_caption` / `qwen3_asr` 回读（音频）。🚫 **不许把「提交成功」当「产出成功」**。

**⑤ 优先级**：本批 = **P0**；本线暂**无其他批次**，全部精力投入「完成成片」。

**⑥ 经验并入（2026-10-11 · supervisor）**：把**同机 · 同 ComfyUI · 同 MCP 工具**且**已全片交付**的 `E:\code\stem_fest`（《如愿·看见》· 126 镜）实战经验并入本任务书 ⇒ **新增 §4**（分镜表口径 / H3 参数 / 资产管理 / prompt 三条禁令 / 音频六层 / 验收判据 / 音画钉长 / 跑批纪律）+ **展开版 `run/video/STEM_FEST_PLAYBOOK.md`**。**读完全文后先读 §4 再动手**（§4 与 §3 铁律**同级硬约束**）。

---

## 0. 运行环境（**Win11 本机 · 无人值守**）

> **本线是本项目唯一跑在 Windows 本机的线**；loop = `watch_video_loop.ps1`（PowerShell），由 **计划任务**在**开机后**自动拉起（见 `register_watch_video_task.ps1`）。

| 项 | 值 |
|:--|:--|
| 主机 | `hx-c1000`（`C:\Users\Administrator`）；**开机自启、无人登录**（计划任务） |
| **ComfyUI** | `http://127.0.0.1:8188` · 根目录 `E:\code\ComfyUI` · **由计划任务 `ComfyUI`（SYSTEM）在开机 +30s 自动启动**（`launch_comfyui_service.bat`） |
| **MCP `comfyui-drama`** | `py -3.10 E:\code\stem_fest\mcp_server\comfyui_mcp_server.py`（`COMFYUI_URL`/`COMFYUI_ROOT` 见 `.cline` 配置）—— **本线的核心工具集** |
| **MCP `web-search`** | `py -3.10 E:\code\stem_fest\mcp_server\web_search_mcp_server.py` |
| Python | `py -3.10` → `D:\Python310\python.exe` |
| ffmpeg | 用于**合成/探测**成片（`ffmpeg -version` 自检；缺则记入 `BLOCKERS.md`） |
| **短剧项目仓** | `D:\Users\Administrator\code\super_intelligence_2035_short_drama`（**独立 git 仓** `github.com:foamliu/super_intelligence_2035_short_drama.git`） |
| 本线记录仓 | `D:\Users\Administrator\code\super_intelligence_2035`（本任务书所在仓） |

> 📍 **本线绝对路径（⚠️ cwd 在短剧仓，写文件务必用绝对路径）**
> - 任务书：`D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\WATCH_VIDEO_TASK.md`
> - 记忆：`D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\MEMORY_VIDEO.md`
> - 日流水：`…\doc\personal-watch\run\daily-memories-video\` · 记录产物：`…\doc\personal-watch\run\video\` · loop 日志：`…\doc\personal-watch\run\video\logs\`
> - 短剧仓（**主战场**）：`D:\Users\Administrator\code\super_intelligence_2035_short_drama`

> ⚠️ **唤醒时先自检**：`ComfyUI /system_stats` 可达？MCP `comfyui-drama` 工具可用？两个仓 `git status` 干净？——**任一异常 ⇒ 记 `BLOCKERS.md` + `MEMORY_VIDEO.md`，本轮改为「只做不依赖它的活」**（如写脚本/计划），🚫 不要傻等。

> 🎯 **COMBO 工作流缓存**：项目 `workflows/` 下有 19 个 `.json`（Z-Image-Turbo 文生图 / **Minimax H3 I2V·R2V·T2V** / LongCat 图像编辑 / Qwen3-TTS / ACE-Step 文生音频 / Woosh 音效 / SeedVR2 超分 等）。**用 MCP 工具跑，不要自己拼 API**（工具已封装）。
>
> 🏭 **参考工程（同机 · 同 ComfyUI · 同 MCP 工具 · 已全片交付）**：`E:\code\stem_fest`（《如愿·看见》· 126 镜）。
> 它的「怎么跑」已抽成 **§4 + `run/video/STEM_FEST_PLAYBOOK.md`**；**§4 没覆盖的先去这两处查**。

---

## 1. 首阶段执行路线（P0「完成成片」的分解）

> 目标：**42 章 → 每章一份成片**。分四步，**一步步来，别跳**。

| 步 | 名称 | 内容 | 产出 |
|:--:|:--|:--|:--|
| **S1** | **环境 & 盘点**（1 轮内完成） | ① ComfyUI 自检（`/system_stats`）② MCP `comfyui-drama` 冒烟（跑 1 张小图）③ 盘点短剧仓现状（`SCENES/` 42 章 · `OUTPUT/` 已有哪些章的素材 · `ASSETS/CHARACTERS/` 定妆 · `workflows/`）④ `ffmpeg` 自检 | `run/video/PLAN.md`（含**逐章状态表**：分镜✅/帧/视频/旁白/音效/合成）+ `BLOCKERS.md` |
| **S2** | **样板章端到端打通** | 选**素材最全的一章**（先用 `OUTPUT/13_外骨骼/`，其帧/视频已有），把链路走通：**分镜帧 →（I2V）视频片段 → TTS 旁白 → BGM + 音效 → 合成 mp4 + 字幕**；把每步**固化成可复用脚本**（建议放短剧仓 `scripts/`，如 `video_pipeline.py`） | **1 章成片 mp4** + `run/video/PIPELINE.md`（SOP + 命令 + 参数） |
| **S3** | **按章滚动放量** | 按 `PLAN.md` 的章序，逐章重复 S2（**一次推进 1–2 章**，别贪）；长任务用 MCP 的异步模式（`wait=False` + `comfyui_get_result`）**避免超时** | 各章成片 + `PLAN.md` 状态更新 |
| **S4** | **汇总与验收** | 全片拼接（`ffmpeg concat`，参考仓内既有 `concat_list.txt`）+ 总时长/分辨率核对 + **抽检**（`sound_caption` 回读音频 / `qwen3_asr` 核对旁白） | 全片成片 + 验收表 |

**⚠️ 大前提（按优先级避让）**：一次只推进**能一轮做完/能异步等待**的最小单元；**视频生成单条 5–15 分钟**，一轮唤醒（~50 分钟预算）**排 3–6 条**为宜；🚫 不要在同一轮里排队几十条把 ComfyUI 堵死。

---

## 2. 每轮唤醒的固定动作（SOP · 逐条做）

1. **读状态**：`MEMORY_VIDEO.md` 顶部（进度快照 / 上轮"下一步"）→ 再读本任务书（= prompt）。
2. **git 同步**：两个仓各 `git pull --rebase --autostash`（**共享副本/多线在用**，别在没 pull 的情况下改）。
3. **自检**（§0）：ComfyUI 可达？MCP 工具可用？`ffmpeg` 在？—— 异常 ⇒ 记 `BLOCKERS.md` 并改做不依赖它的活。
4. **取活**：从 §1 的 S1→S4 里选**本轮能做完的最小一步**；若上轮留了"下一步"，优先续做。
5. **干活**（**要产出**，**按 §4 的配方/禁令/判据**）：写脚本 / 跑 ComfyUI 任务 / 合成 / 核验。**每完成一条就核验一条**（§运维指令区④）；**开跑前过闸门**（`--dry` 核镜数/参考图；prompt hazard 扫描**非 0 退出即禁跑**），**收工时核「进程退出 + 队列清零」**（§4.8）。
6. **回写**：更新 `MEMORY_VIDEO.md`（**进度快照 + 本轮流水**）→ 追加 `daily-memories-video/<YYYY-MM-DD>.md` → 更新 `run/video/PLAN.md`。
7. **提交推送**（**每轮必须自己 commit+push**，不等 loop 兜底）：
   - **短剧仓**：`cd` 到 `D:\Users\Administrator\code\super_intelligence_2035_short_drama` → `git add` **你本轮改动的文件**（`scripts/` `SCENES/` `OUTPUT/` 的文本/清单等；**视频/音频/模型不入库**）→ `commit`（前缀 `video:`）→ `push`。
   - **本记录仓**：`git add -- doc/personal-watch/run/MEMORY_VIDEO.md doc/personal-watch/run/daily-memories-video doc/personal-watch/run/video` → `commit`（前缀 `video:`）→ `push`。
   - 🚫 **不得** `git add -A` / `git reset --hard` / `git clean` / `git stash pop`（会卷入或破坏他线在途文件）。

---

## 3. 铁律与纪律（本线特有）

- 🚫 **不碰 ComfyUI 服务本身**：**不得 kill / 重启 `ComfyUI` 进程或计划任务** —— 它是全项目共用，重启会让在跑任务全废。**只在队列空闲时提交新任务**。
- 🚫 **不碰模型/不改 ComfyUI 安装目录**（`E:\code\ComfyUI` 只读用）；要换模型、加自定义节点 → **先报运维**。
- 🚫 **不动别人的在途文件**：短剧仓可能有他人在改（supervisor/用户手改）；`git status` 里**陌生的未提交改动一律不 clean/stash/reset**。
- ✅ **每轮必须有「看得见的进展」**；真的做不了 → **如实写 `BLOCKERS.md`** 并说明下一步与所需资源。
- ✅ **验收式陈述**：说"生成了"必须给 **路径 + 字节 + 时长**；说"对齐了"必须给**回读证据**（`sound_caption` / `qwen3_asr`）。🚫 不凭印象下结论。
- ⏱️ **长任务**：优先 MCP 的**异步**（`wait=False` + `comfyui_get_result`）；**单条别超过本轮预算**（视频 5–15 min/条）。
- 🖥️ **GPU = RTX 4090 · 16 GB** ⇒ `video_minimax_h3_i2v/r2v/t2v` 的 **`megapixels` 必须 ≤ 0.6**（≈1056×608；调到 0.92/720p **必 OOM**）；**要 1080p 请生成后用 `video_upscale_seedvr2` 超分**（帧数/音轨原样保留）。R2V 双参考图更吃显存，建议 0.4。
- 📖 **§4 与本节同级、同为硬约束**：**prompt 三条禁令**（禁元信息 / 禁否定式 / 台词须匹配时长）· **定妆照 = 外形唯一权威** · **音频分层与电平纪律** · **拼接音画钉长** —— **违反即出废片**，详见 §4 与 `run/video/STEM_FEST_PLAYBOOK.md`。
- 🔒 **凭据**：`C:\Users\Administrator\.cline`（含 MCP 配置/密钥）**只读使用，绝不复制进任何仓 / 日志 / 报告**。
- 🚫 **不改** `WATCH_VIDEO_TASK.md`（只读）与 loop / 注册脚本（由 supervisor 写）。

---

## 4. 从 stem_fest 继承的实战经验（★★★ 动手前必读 · 2026-10-11 并入）

> **来源**：`E:\code\stem_fest`（《如愿·看见》科技节短片 · **126 镜已全片交付**）—— 与本线**同一台机、同一套 ComfyUI + 同一批 MCP 工具**，
> 它的 README/storyboard 是**踩满坑后固化**下来的操作规程。
> 📖 **本节是精简版；全部命令块、实测数据、长篇推导 → `run/video/STEM_FEST_PLAYBOOK.md`（强烈建议首次动手前通读一遍）**。
> ⚠️ **只照抄「参数 / 配方 / 判据 / 纪律」，不照搬它的剧情与视觉风格**（差异见 §4.9 与 playbook §10）。

### 4.1 分镜脚本表格 = 唯一权威（先读表，再动手）

- 本仓表 = `SCENES/<NN>_<标题>.md` 的 `## 逐镜表`（**7 列固定**：镜号/时长/画面/运镜/景别/台词·音效/参考图提示）+ `ASSETS/SHOT_SPECS/<NN>_*`（T2I/I2V 规格）。
- **纪律：一切生成任务从表里解析，别口述、别手拼 prompt**（stem_fest 三个生产脚本都是「解析表 → 生成任务」）。

| 口径 | 要点 |
|:--|:--|
| **时长量化** | 整数秒 **2–10**；H3 **帧数＝`17k+5`** ⇒ 实际播放：2s→2.33 / 3s→3.04 / 4s→4.46 / 5s→5.17 / **6s→6.58** / 7s→7.29 / 8s→8.00 / 9s→9.42 / 10s→10.13（**写 6s 比 5s 实际贵 1.41s**，别随手写 6s） |
| **时长公式** | `need = 净字 ÷ 语速 + 0.8s(起势气口) + 动作余量 + 换人×0.5s + 停顿 0.4s`；**无台词镜** `need = 2.5s + 0.4s×动作数`（≤6s） |
| ★★ **台词长度必须匹配时长** | 差值应落 `need +0.2~0.8s`。**台词太短** ⇒ H3 用「口型空转／自己补话」填满（乱音、胡说，换 seed/改 prompt 无效）；**太长** ⇒ 挤成乱音。**处置优先序**：① 调台词长度/镜头时长 → ② 改正向音景/换 seed → ③ **最后**才后期掐音 |
| **景别写「范围」** | 只写「全景／中景」**名词** ⇒ H3 贴近拍衣服、**脸出画只剩躯干**；须写「全景＝人物全身 + 环境」这类范围定义 |
| **站位三要素** | ① 左→右顺序 ② 相对关系（前/后/旁边/**对面**、谁站中间、从哪侧入画）③ 姿态/朝向（蹲/站/坐、面向哪）。只写①是「站位错乱／多人／缺人」的总根源；座位必写「面对面＋中间隔桌板」，手部动作必写「**谁的**双手」，人数要**逐个点名不留「等」** |
| **参考图按人数** | 画面该有几人，参考图就须含**几张脸**（缺脸会消失/背景空荡）；纯场景走 T2V；🚫 场景图别用空场景（人物像贴上去） |
| **改表必校验** | 改时长/台词/参考图 ⇒ 重跑**时长审计 + 表结构一致性**闸门，零漂移才开跑 |

### 4.2 资产管理（定妆照 / 命名 / 合影 / seed / 台账）

| 规矩 | 要点 |
|:--|:--|
| ★★ **定妆照 = 外形的唯一权威** | prompt **只写客观可见的稳定特征**（性别/发型发色/服装/配饰）；🚫 **禁写体型/脸型/胖瘦/年龄感**（写「圆脸、偏胖」→ 生成结果真的变胖变圆；写「83 岁」→ 画苍老，应写「精神矍铄、面容紧致」）；性格/印象描述**不可**当外形依据 |
| **顺序：定妆照 > 分镜表** | 服装/外观冲突时**以定妆照为准**（本仓 `ASSETS/CHARACTERS/<角色>/定妆规格.md`） |
| **命名全 ASCII（小写+下划线）** | 角色 `<slug>_hero_v01.png`（**一人一张**，其所有镜头都引用它）；场景/道具 `<slug>_<view>_v<NN>.png`（view=wide/medium/detail/hero）。⚠️ 中文/空格名会被 ComfyUI 上传改写成随机 `mcp_ref_<hex>.png`，无法辨认 |
| ★★ **合影＝程序拼版，绝不用图生图** | `image_edit_longcat` 转过的合影**会身份失真** ⇒ 正解＝**裁人 → 并排拼进一张宽图 → 直接入库** `_group/<slug>_hero_v01.png`；**站位由拼版顺序物理决定**，prompt 里的站位段必须与之**一致**（不一致时 H3 二选一） |
| **seed 固定可复现** | 同角色/同场景固定 seed；候选图用「基 seed + 偏移」；**seed 记入台账** |
| **上传不覆盖同名** | 换图**先删** `E:\code\ComfyUI\input\<名>.png` 再上传（否则存成 `名 (1).png`，出现「改了没用」） |
| **结构随仓走、大文件本地存** | 图/音/视频**不入 git**；`.md`/`.gitkeep`/`manifest.json`/脚本入库（与短剧仓 `.gitignore` 同口径） |

### 4.3 MiniMax H3 出视频（参数照抄）

| 参数 | **必须用** | 说明 |
|:--|:--|:--|
| `steps` | **4 / 10 / 20**（按镜型） | 4＝静态·单人·对话；**10＝角色镜默认**；20＝**环境剧变镜**（航拍跟拍/画面持续剧变）。耗时(1056×608)：4步≈3.4min / 10步≈9.5min / 20步≈18–26min。<br>⚠️ **提步数 ≠ 提画质**：曾把 65 镜从 10 提到 20 全量重跑，被判**无提升、机时 +36%** 并全部回退 ⇒ H3 在 10 步已基本收敛，**别默认堆 20** |
| `megapixels` | **0.6** | →1056×608；**0.92(720p) 必 OOM**；R2V 双参考图建议 **0.4**；要 1080p 用 `video_upscale_seedvr2` 超分（**帧数/音轨原样保留**，可直接替换） |
| `aspect_ratio` | `"16:9 (Widescreen)"` | |
| `duration` | 照抄表内时长 | 受 `17k+5` 量化（见 4.1） |
| `ref_image_1 / 2` | 角色/合影 → `<Picture 1>`；场景图 → `<Picture 2>` | R2V ≤2 图；**按「在场人数」给图**（缺脸会消失/背景空） |
| `prompt` | `CUT 1:` + **景别** + 动作 + `Audio:`（**只放 L1 台词原文**） | 一镜一个主景别；环境声**不写**在这（见 4.5） |

- **路由**：有角色 → `video_minimax_h3_i2v`（首帧图）；多角色锁定 → `video_minimax_h3_r2v`；无角色 → `t2v`；屏幕/UI 动态 → 降级备选。
- **分镜帧前置**：`image_edit_longcat` 输出**脸高 ≥250px**（小人脸进 H3 会漂）。
- **验证「这镜到底几步」** ⇒ 读 mp4 **内嵌元数据**（可复算，别用画面统计量猜）：`ffprobe -v quiet -print_format json -show_entries format_tags <file>` → `format_tags.prompt` 里的 `BasicScheduler.inputs.steps`。

### 4.4 prompt 三条禁令（前两条**直接出废片**）

1. ★★★ **禁写「元信息 / 对模型说的话」** —— 比喻式内心状态（像在…／仿佛…）、镜头用意（暗示…／表达…／观众要读到…）、镜头编号指代（本镜／该镜）会被 H3 **当成台词、原样渲染成画面字幕**（⚠️ **提 steps 无效**，是语义层问题）。修法＝**改写成可见的物理表现**（「像在消化一件很难接受的事」→「面无表情地沉默了几秒，喉结动了一下」）。改完跑 hazard 扫描闸门，**非 0 退出即禁止开跑**。
2. ★★★ **无台词镜禁写否定式** ⇒ 一律写**正向音景**（只说「有什么声音」，音景本身**不含可读词句**）；⛔ 别写「本镜不要生成任何语音…」（它**本身会被渲染成字幕**）。否则 H3 会幻觉出人声。
3. ★★★ **台词长度必须匹配镜头时长**（见 4.1）。

> 另：**参考图里的文字/水印**（人名标签、水印）也会被画进画面 ⇒ 素材先清干净。

### 4.5 音频六层分工（**H3 只出 L1 台词**，其余全部后期铺）

| 层 | 谁做 |
|:--|:--|
| **L1 台词**（有原文、要对口型） | ✅ **H3**（**只此一项**） |
| **L2 环境声**（风/雨/街/空调/键盘底噪） | `stable_audio_3_sfx`（⭐1–10s）· `woosh_sfx` · 长氛围 `ace_step_t2audio` |
| **L2b 点状 foley**（脚步/按键/轻响/心跳） | `stable_audio_3_sfx` ⭐ |
| **L3 群杂人声**（听不清的 walla） | `ace_step_t2audio`（音效模型只会糊状人声，念不出词） |
| **L3b 有词句的播报/旁白** | `qwen3_tts`（**本线现行主用**） |
| **L4 给已拍画面配 foley** | `woosh_v2a`（≤8s，按画面内容） |
| **跨镜 BGM** | 现成音源 / `ace_step_t2audio`，**后期整体铺**（`-c:v copy` 只换音轨） |

- **实测**：H3 **前后段 ≈ −50 dB（生不出环境声）**，且**听不进「多人说话」语义** ⇒ 环境声/群杂别指望 H3。
- **脚本纪律**：`音效：` 列**禁写「讨论声/人声/说话声」**（会被 H3 当台词）⇒ 用 **`（后期）`** 后缀，脚本拼 prompt 前用 `strip_late_audio()` **自动剔除整句**。
- ⚠️ 本线 `H3 Audio` 与 `qwen3_tts` 旁白**并存** ⇒ **同一句台词不要两边都放**（否则双份人声）。
- **电平纪律（违反必削波）**：BGM 母带与成片音轨直接相加必爆 ⇒ ① BGM 降 level ② `sidechaincompress` 用**成片音轨自己**当侧链做闪避 ③ 总线 `alimiter` 守 −1 dBFS；母带目标 ≈ **−23 LUFS**。
- ⚠️ **判收口径**：`sound_caption` **不可靠**（曾把稻田蝉鸣读成 *vacuum cleaner*）⇒ 用**客观画像**（频段/静音/crest/调制）+ 同族对比。

### 4.6 验收判据（**数值化**；报 `success` ≠ 产出成功）

- **规格**：`ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,duration,nb_frames <file>`。
- **质量体检**（PS 里用 `cmd /c "ffmpeg … 2>&1"` 包一层，否则 ffmpeg 走 stderr 抛 `NativeCommandError`）：`blackdetect=d=0.2:pix_th=0.10`（黑帧）/ `freezedetect=n=-60dB:d=0.5`（静帧）/ `silencedetect=n=-50dB:d=0.4`（静音）/ `scdet=threshold=10`（硬切）/ `ebur128=peak=true`（响度）。
- **画面「有没有某物 + 占多大」** → `image_segmentation_sam3`（**可直接喂 .mp4**，每帧 `mask_coverage`，**0＝没检出**）；**台词逐字** → `qwen3_asr`（**可直接喂 .mp4**）；**人脸** → `face_feature`（⚠️ **绝对余弦阈值失真**，用**相对排名 + `face_px_h≥250`**）。
- **看画面**：**基模自带视觉 —— 第一步就是 `read_files` 读图**（别先写像素脚本/找外部 VLM）；⚠️ 额度 ≈**7 张/会话**（超出**静默丢弃**、不报错）、不可复现、读不准低对比度小字与**任何数值** ⇒ 拼**联系表**（1 张 ≈6 镜×4 帧）、大图缩 ≤1024px；判「崩坏/黑帧/过曝」**必须读全帧**（别把裁剪条带当全帧）。
- ★ **出片即停**：渲完**先报路径（文件名+规格）等验收**，🚫 不自动跑整套自查链 / 不写长台账（除非被点名要）。

### 4.7 拼接的音画漂移（**成片级铁律**）

- **根因**：每个 H3 片段**音轨解码长度比画面长 0~32 ms**（AAC 1024 采样/颗取整），126 段合计 **+2631 ms** ⇒ 拼完成片人声越来越滞后（**单镜产物看不出毛病，只有拼成片才发作**）。
- **铁律**：**`帧数 ÷ 24` 是画面的权威时间轴**，音频段必须被**钉到它**：
  `aresample=32000,aformat=channel_layouts=stereo,apad,atrim=0:<本镜时长>,asetpts=N/SR/TB`
  —— 任何 concat 变体都躲不掉（5 种接法全实测失败）；`-shortest` **更糟（砍的是视频）**。
- **闸门**：拼接后 `|音轨长度 − 画面长度| < 0.15s` **且**逐镜测**内容偏移**（时长≈0 只是**必要非充分**；旧成片 +2.631s 会被当场拦下）。
- **顺序**：**先验母版同步，再叠 BGM/音效**；🚫 别在已叠音效的片上测偏移（会报**假峰**）。章节表 / 音频钉长 / 字幕段长**必须同源**。

### 4.8 跑批纪律（照抄）

- **启批前先 `--dry`**（核镜数/时长/参考图是否都在）；**跑完核「进程已退出 + 队列清零」**（查 `/queue`、`/history`）。
- 长任务**后台跑**（`Start-Process`）；单条 3–26 min、整幕数小时 ⇒ 前台 30s 必超时。
- **清队列姿势**：删排队 `POST /queue {"delete":[id]}`；**中断正在执行要先 `POST /interrupt` 再删**（只发 delete 删不掉 running 那个）；清历史 `POST /history`。
- **跑批期间别调本地视觉模型**（常驻显存会把 H3 挤爆）。脚本**幂等可续跑**、每幕独立脚本（互不引用）。

### 4.9 与 stem_fest 的差异（别照搬错）

- stem_fest = **超写实真人质感·校园短片**；本仓 = **42 章 · 半写实半水墨科幻短剧** ⇒ **风格后缀/视觉规范以短剧仓为准**（`ASSETS/视觉总纲.md` + `半写实半水墨视觉规范.md` + `AI不拟人化视觉规范.md`），**不套用 stem_fest 的 STYLE**。
- **短剧仓既有约定优先**：命名 `EP{NN}_SHOT-{MM}`、`SCENES/` 表格式、`SHOT_SPECS` 规格、验收标准（短剧 README §十四）。

## 5. 产出、命名与体积

- **本线记录产物** → `doc/personal-watch/run/video/`：`PLAN.md`（总计划+逐章状态）· `PIPELINE.md`（SOP）· `STEM_FEST_PLAYBOOK.md`（**`stem_fest` 经验长文版**·§4 的展开）· `BLOCKERS.md` · `logs/`（**不入库**）。
- **成片与素材** → 短剧仓既定目录（`OUTPUT/<章>/videos/`、`OUTPUT/全片/`、`scripts/`）。
- **体积红线**：单文件 **≥5 MB 一律不 `git add`**（视频/音频/大图/模型）；靠 `manifest.json` / 清单**间接入库**。提交前自检：`git check-ignore -v <file>`（应命中项目 `.gitignore`）。
- 大文件需外送 → **报运维**（不在本线范围）。

---

## 6. 记忆、心跳与判活

- `MEMORY_VIDEO.md` 顶部：**`WAITING:` 行（只出现一次）** + 进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞` / `ERROR_COUNT`）+ 本唤醒流水（旧的滚动归档到 `daily-memories-video/`）。
- `daily-memories-video/<YYYY-MM-DD>.md`：逐轮流水（不进 prompt）。
- **判活**：本线是**慢线**（每小时唤醒）⇒ **不看「提交频率」**，看 **loop 存活标记 `run/video/logs/watch_video_loop.hb`**（每轮刷新）+ loop 日志 `run/video/logs/watch_video_loop.log`。
- `WAITING` 语义：`1` = 常态（无紧急待办）；`0` = 有近期待办。**本线 loop 按小时唤醒，与 `WAITING` 无关**（字段仅供人读）。

---

## 7. 关键文档索引（**先读再干**）

- **短剧项目总纲**：`README.md`（**§一 结构 · §二 角色 · §十三 ComfyUI API 完全手册**）。
- **踩坑史（必读）**：`LESSONS_LEARNED.md` —— 角色一致性靠**定妆照 + LongCat Image Edit**；**路径别猜，先 list**（AI 助手误指目录的教训）。
- **工作清单**：`ASSETS/HIGH_PRIORITY_TODO.md`（策划已完成，**已进入「图像与视频生成阶段」**）。
- **ComfyUI 实战**：`docs/comfyui_guide.md`（API 批量生成、history 解析、超时/断点续传、排错清单）。
- **视觉/音频规范**：`ASSETS/半写实半水墨视觉规范.md` · `ASSETS/AI不拟人化视觉规范.md` · `ASSETS/配乐提示词规格.md`。
- **MCP 工具说明**：`mcp_server/comfyui_tools.md`（及 `E:\code\stem_fest\mcp_server\`）。
- **`stem_fest` 实战经验（本任务书 §4 的出处 / 展开版 · ★ 遇到配方/判据问题先查这里）**：
  - `run/video/STEM_FEST_PLAYBOOK.md`（**本仓** · 已抽取的 11 节经验，含全部命令块/实测数据）
  - `E:\code\stem_fest\README.md`（§0 读图 · §0.5 出片即停 · §4 照抄参数 · §4.4 音频六层 · §4.5 能力地图 · §6 已知坑 · §7 生产流程）
  - `E:\code\stem_fest\storyboard.md`（分镜表范式：时长/运镜/景别/参考图/站位）
  - `E:\code\stem_fest\mcp_server\comfyui_tools.md`（工具参数/约束/实测数据权威）
  - `E:\code\stem_fest\ASSETS\README.md`（素材台账范式：定妆照/seed/命名/看图验收）

---

## 8. 本线文件与启动（supervisor / 用户）

| 文件 | 作用 |
|:--|:--|
| `run/WATCH_VIDEO_TASK.md` | **本任务书**（只读 · = 每轮 prompt） |
| `run/watch_video_loop.ps1` | **Win11 loop**：每小时唤醒 → `cline` 读本任务书 → git 同步两个仓 |
| `run/register_watch_video_task.ps1` | **注册计划任务**（开机自启，镜像既有 `ComfyUI` 任务） |
| `run/MEMORY_VIDEO.md` · `run/daily-memories-video/` | 运行时记忆 / 日流水 |
| `run/video/` | 本线记录产物（`PLAN.md` 等） |

**启动（本机 PowerShell）**：
```powershell
# 1) 注册计划任务（开机 +30s 自动拉起 loop；需管理员）
powershell -ExecutionPolicy Bypass -File "D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\register_watch_video_task.ps1"
# 2) 立即试跑一次（不等重启）
Start-ScheduledTask -TaskName 'WatchVideoLoop'
# 3) 手动前台试跑（调试用）
powershell -ExecutionPolicy Bypass -File "D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\watch_video_loop.ps1"
```

**停止**：`Stop-ScheduledTask -TaskName 'WatchVideoLoop'`（并 `Unregister-ScheduledTask -TaskName 'WatchVideoLoop'` 可彻底移除）；手动跑的用 `Get-Process powershell | ? { $_.Path }` 自查后 `Stop-Process`。
**判活**：`run/video/logs/watch_video_loop.hb`（mtime 每小时刷）+ 日志。

> ⚠️ **改 loop / 任务书后须重启计划任务才生效**（脚本不会热重载）。
> 🔤 **`.ps1` 必须存成「UTF-8 带 BOM」** —— 本机是 **Windows PowerShell 5.1 + GBK 默认编码**；**无 BOM 的 .ps1 会把中文注释读成乱码并直接报语法错**（本线立线时已踩过一次）。自检/补 BOM：`$f='…\watch_video_loop.ps1'; (Get-Content $f -Raw) | Set-Content -Encoding utf8 $f`（PS 5.1 的 `utf8` = 带 BOM）。
> 🧪 **安全自检（不调 cline、不烧 token）**：`powershell -ExecutionPolicy Bypass -File "…\watch_video_loop.ps1" -Once -DryRun`（只走横幅/日志/心跳/git 同步）。
> ⚙️ **可调参数**（loop 顶部 `param()`）：`-IntervalSec`(默认 3600) · `-ClineTimeout`(默认 3300) · `-Model`(默认空=用 cline 已配模型) · `-Thinking`(默认 medium) · `-Once`/`-DryRun`(调试)。**🚫 无重试参数（已废除）。**
> ⏰ **节律 = 每小时（对齐整点）· 用户 2026-10-11 明确确认保留**，☑️ **已知代价并接受**：实测每轮 ≈1.62M input tokens ⇒ **≈39M input/天（24 轮）**。**🚫 后续 operator/agent 不要"顺手"改成低频**（要改须先问用户）。
> 🧵 **prompt 传递方式（本线特有 · 2026-10-11 实测踩坑）**：Windows 上**不能把任务书全文当命令行参数** —— 经 `cline.cmd`（批处理）会撞 **cmd.exe ~8KB 上限**（实测报「**命令行太长**」，cline 秒退 exit 1）。⇒ loop 改为 ① 直调 **`node.exe` + cline JS 入口**（绕过 cmd）② 只传**短指针 prompt**（含任务书绝对路径）。**因此 agent 每轮第一步必须自己读任务书全文**。
> 🚫 **失败处理 = 不重试（2026-10-11 用户明令）**：已知失败**全是确定性/配置性**的（命令行过长 · cline/node 路径错 · 未登录/401 · 模型名不存在 · provider 配置错 · 配置文件/目录不可读……）—— **重试一次也解决不了，只会烧 token**（实测单轮 ≈1.62M input tokens）。⇒ **失败只记日志 + 退回整点节律，由人处理**。每轮用量仍记 `[usage] …`。
> 🧑💻 **运行身份（2026-10-11 实测 · 关键）**：**必须用「当前用户 S4U」运行**（`register… -RunAsCurrentUser`），🚫 **不要用 SYSTEM** —— SYSTEM 下 `py -3.10` 报 **`No installed Python found!`**（Python 按**用户**注册）⇒ **MCP `comfyui-drama` / `web-search` 全部加载失败**（cline 日志 `[mcp] Failed to load …`），agent 只能退化成手拼 HTTP API。切到 S4U 后两个 MCP 均正常拉起。


