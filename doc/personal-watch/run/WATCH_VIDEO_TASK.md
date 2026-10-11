# WATCH_VIDEO_TASK.md — 观察哨 · **video agent** 任务书

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_VIDEO.md` / `daily-memories-video/`；本线产物写 `video/`；**主战场 = 短剧项目仓**（见 §1）。
> ⚠️ **本文件 = 每轮「必读」的指令文件**：loop 只把**绝对路径**交给 cline，**agent 必须先用工具读全文**再干活（Windows 命令行长度限制所致，见 §7）→ 保持精简（目标 ≤ 32KB，红线 40KB）；历史轮次归档到 `daily-memories-video/`，不进 prompt。
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
- **成片与素材**（入短剧仓）：按项目既有约定（`OUTPUT/`、`ASSETS/`、`scripts/`）；**大文件（视频/音频/模型）不入 git**（遵项目 `.gitignore` + 本线体积纪律，见 §4）。

**④ 验收（硬）**：每个「已生成」的产物都要**亲眼核验存在**：文件存在 + **字节数 > 0** + 用 `ffprobe/ffmpeg` 读**时长/分辨率**（视频）或 `sound_caption` / `qwen3_asr` 回读（音频）。🚫 **不许把「提交成功」当「产出成功」**。

**⑤ 优先级**：本批 = **P0**；本线暂**无其他批次**，全部精力投入「完成成片」。

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
5. **干活**（**要产出**）：写脚本 / 跑 ComfyUI 任务 / 合成 / 核验。**每完成一条就核验一条**（§运维指令区④）。
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
- 🔒 **凭据**：`C:\Users\Administrator\.cline`（含 MCP 配置/密钥）**只读使用，绝不复制进任何仓 / 日志 / 报告**。
- 🚫 **不改** `WATCH_VIDEO_TASK.md`（只读）与 loop / 注册脚本（由 supervisor 写）。

---

## 4. 产出、命名与体积

- **本线记录产物** → `doc/personal-watch/run/video/`：`PLAN.md`（总计划+逐章状态）· `PIPELINE.md`（SOP）· `BLOCKERS.md` · `logs/`（**不入库**）。
- **成片与素材** → 短剧仓既定目录（`OUTPUT/<章>/videos/`、`OUTPUT/全片/`、`scripts/`）。
- **体积红线**：单文件 **≥5 MB 一律不 `git add`**（视频/音频/大图/模型）；靠 `manifest.json` / 清单**间接入库**。提交前自检：`git check-ignore -v <file>`（应命中项目 `.gitignore`）。
- 大文件需外送 → **报运维**（不在本线范围）。

---

## 5. 记忆、心跳与判活

- `MEMORY_VIDEO.md` 顶部：**`WAITING:` 行（只出现一次）** + 进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞` / `ERROR_COUNT`）+ 本唤醒流水（旧的滚动归档到 `daily-memories-video/`）。
- `daily-memories-video/<YYYY-MM-DD>.md`：逐轮流水（不进 prompt）。
- **判活**：本线是**慢线**（每小时唤醒）⇒ **不看「提交频率」**，看 **loop 存活标记 `run/video/logs/watch_video_loop.hb`**（每轮刷新）+ loop 日志 `run/video/logs/watch_video_loop.log`。
- `WAITING` 语义：`1` = 常态（无紧急待办）；`0` = 有近期待办。**本线 loop 按小时唤醒，与 `WAITING` 无关**（字段仅供人读）。

---

## 6. 关键文档索引（**先读再干**）

- **短剧项目总纲**：`README.md`（**§一 结构 · §二 角色 · §十三 ComfyUI API 完全手册**）。
- **踩坑史（必读）**：`LESSONS_LEARNED.md` —— 角色一致性靠**定妆照 + LongCat Image Edit**；**路径别猜，先 list**（AI 助手误指目录的教训）。
- **工作清单**：`ASSETS/HIGH_PRIORITY_TODO.md`（策划已完成，**已进入「图像与视频生成阶段」**）。
- **ComfyUI 实战**：`docs/comfyui_guide.md`（API 批量生成、history 解析、超时/断点续传、排错清单）。
- **视觉/音频规范**：`ASSETS/半写实半水墨视觉规范.md` · `ASSETS/AI不拟人化视觉规范.md` · `ASSETS/配乐提示词规格.md`。
- **MCP 工具说明**：`mcp_server/comfyui_tools.md`（及 `E:\code\stem_fest\mcp_server\`）。

---

## 7. 本线文件与启动（supervisor / 用户）

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
> ⚙️ **可调参数**（loop 顶部 `param()`）：`-IntervalSec`(默认 3600) · `-ClineTimeout`(默认 3300) · `-Model`(默认空=用 cline 已配模型) · `-Thinking`(默认 medium) · `-RetrySec`(默认 600) · `-MaxRetry`(默认 2) · `-FastFailSec`(默认 60)。
> ⏰ **节律 = 每小时（对齐整点）· 用户 2026-10-11 明确确认保留**，☑️ **已知代价并接受**：实测每轮 ≈1.62M input tokens ⇒ **≈39M input/天（24 轮）**。**🚫 后续 operator/agent 不要"顺手"改成低频**（要改须先问用户）。
> 🧵 **prompt 传递方式（本线特有 · 2026-10-11 实测踩坑）**：Windows 上**不能把任务书全文当命令行参数** —— 经 `cline.cmd`（批处理）会撞 **cmd.exe ~8KB 上限**（实测报「**命令行太长**」，cline 秒退 exit 1）。⇒ loop 改为 ① 直调 **`node.exe` + cline JS 入口**（绕过 cmd）② 只传**短指针 prompt**（含任务书绝对路径）。**因此 agent 每轮第一步必须自己读任务书全文**。
> 🔁 **失败处理（2026-10-11 修订 · 省 token）**：**只对「启动类失败」重试** —— 判据 = `exit≠0` **且本轮耗时 < `-FastFailSec`(默认 60s)**（秒退 ⇒ 几乎不耗 token），最多 `-MaxRetry`(默认 2) 次；**「运行类失败」（真跑了一阵子）一律不自动重试**，直接退回整点节律。⚠️ **实测单轮 ≈ 1.62M input tokens**（首轮 S1：`in 1,621,718 / out 32,874 / cacheRead 1,528,320`，5m35s）⇒ **盲目重试 = 纯烧钱**。每轮用量会写进 loop 日志 `[usage] …`。想更省可 `-MaxRetry 0` 关掉重试。
> 🧑💻 **运行身份（2026-10-11 实测 · 关键）**：**必须用「当前用户 S4U」运行**（`register… -RunAsCurrentUser`），🚫 **不要用 SYSTEM** —— SYSTEM 下 `py -3.10` 报 **`No installed Python found!`**（Python 按**用户**注册）⇒ **MCP `comfyui-drama` / `web-search` 全部加载失败**（cline 日志 `[mcp] Failed to load …`），agent 只能退化成手拼 HTTP API。切到 S4U 后两个 MCP 均正常拉起。


