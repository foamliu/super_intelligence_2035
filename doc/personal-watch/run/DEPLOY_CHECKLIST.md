# DEPLOY_CHECKLIST.md — personal-watch worker 部署 / 迁移 / 加固清单

> 面向**运行 worker loop** 的那台机器（当前为阿里云 `iZuf65t80q2n4qgbjqbcp0Z`；拟迁到腾讯云 **2 核 4G**）。
> ⚠️ 该机为 **2 vCPU / 2 GiB**，实测 **CPU 70–80%** —— **资源是首要风险**（详见 §3）。

---

## 0. 🚨 先看这条：重启 = 所有 loop 消失

**`setsid ... &` 只是"脱离进程组"，不是"开机自启"。**

- **实例重启 / 关机再开 → 两条 loop 全部消失**，而 `git log` 看起来就"停了"（这正是 10-04→10-05 静默 27h 的**形态**之一）。
- 重启后**必须手动拉起**（命令见 §4），或**配 systemd**（见 §5）。

---

## 1. 新机 bring-up（Ubuntu 22.04）

```bash
sudo apt update && sudo apt install -y git python3 python3-pip curl jq
# 1) cline CLI（版本与旧机对齐：旧机为 3.0.61）
#    安装方式按你的 npm/官方渠道；装完 `cline --version` 核对
# 2) 克隆仓库（SSH 需部署 key，或改用 HTTPS + PAT）
git clone git@github.com:foamliu/super_intelligence_2035.git ~/super_intelligence_2035
cd ~/super_intelligence_2035 && git config core.autocrlf input   # 保 LF
```

## 2. **cline 配置不在仓库**（必须在新机重建）

| 项 | 位置 | 说明 |
|:--|:--|:--|
| **LLM base URL** | `~/.cline/data/globalState.json` 的 **`openAiBaseUrl`** | ⚠️ **不是** env `CLINE_API_BASE_URL`（那是 Cline 平台自身 API） |
| provider / model / key | `~/.cline/data/settings/providers.json`、`models.json` | 含 `deepseek-flash` 等；**base 必须与模型匹配**（`flash@/v1`=200，`@/cloud/v1`=**403**） |
| MCP | `~/.cline/data/settings/cline_mcp_settings.json` | ⚠️ 历史上**本线从未装上**（news 靠 **CLI 直调** `mcp_web_search_free.py`） |
| 密钥池 | **`doc/keys.txt`（在仓库里！）** | ⚠️ 见 §6 安全 |

**验证**（新机必须真跑一次）：
```bash
cd ~/super_intelligence_2035
curl -s -o /dev/null -w '%{http_code}\n' https://api.deepseek.com/models -H "Authorization: Bearer <key>"   # 200
curl -s -o /dev/null -w '%{http_code}\n' https://www.chinanews.com.cn/scroll-news/2026/1004/news.shtml       # 200（新闻源可达）
git ls-remote --heads origin main >/dev/null && echo GIT_OK                                                 # GitHub 可达
```

## 3. ⚙️ 2 核机器的加固（**针对 CPU 70–80% / 2G 内存**）

| # | 措施 | 为什么 / 怎么做 |
|:--|:--|:--|
| 1 | **加 swap** | 2G 内存跑 `cline`(Node) + python 抓取 + git → **极易 OOM**。`sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`（4G 新机也建议留 1–2G） |
| 2 | **两条 loop 错峰启动** | 2 vCPU 同时跑 news+research 会互相抢 CPU。→ **先起 news，+15 分钟再起 research**；或把 research 的 `SLEEP_LONG` 调大（如 3600） |
| 3 | **抓取脚本降优先级** | N1 逐日抓取是**长时间 CPU+网络**任务 → 在 `fetch_archive.py` 调用处加 `nice -n 19 ionice -c3`，别抢 `cline` 的 CPU |
| 4 | **单轮工作量受限** | 抓取**按天分批**（现有 `PROGRESS.md` 游标已支持）；避免单轮跑数小时占满 CPU |
| 5 | **别在 2 核上并行重任务** | 已知坑：`--stats`/`--index` **不能**与抓取/`--repair` 并发（会写坏 index 行 sha）→ **顺序跑** |
| 6 | **OOM 排查** | `dmesg -T \| grep -i -E 'oom|killed process'`；`journalctl -k --since '2 days ago' \| grep -i oom` |
| 7 | **负载观察** | `uptime`（看 load average 是否 >2）、`free -m`、`ps -eo pid,pcpu,pmem,args --sort=-pcpu \| head` |

> 🔎 **重要**：若 `dmesg` 显示 `Killed process ... (python3|node)`，那么**"静默停摆"的根因就是 OOM**，而不是（或不止是）LLM 额度。

## 4. 启动 / 停止 / 验证

```bash
cd ~/super_intelligence_2035/doc/personal-watch/run && git pull --rebase --autostash

# 启动（先 news）
setsid bash watch_news_loop.sh     > /tmp/watch_news_loop.log     2>&1 < /dev/null &
sleep 900                                                                 # 错峰 15min
setsid bash watch_research_loop.sh > /tmp/watch_research_loop.log 2>&1 < /dev/null &

# 验证
pgrep -af 'watch_(news|research)_loop.sh'     # 各 1 个
tail -5 /tmp/watch_news_loop.log
```
**停止**：`pkill -f 'watch_news_loop.sh'; pkill -f 'watch_research_loop.sh'`

## 5. 可选但推荐：systemd 自启（避免重启后忘记拉起）

```ini
# /etc/systemd/system/watch-news.service
[Unit]
Description=personal-watch news loop
After=network-online.target
[Service]
User=liuyang
WorkingDirectory=/home/liuyang/super_intelligence_2035/doc/personal-watch/run
ExecStart=/bin/bash watch_news_loop.sh
Restart=always
RestartSec=60
StandardOutput=append:/tmp/watch_news_loop.log
StandardError=append:/tmp/watch_news_loop.log
[Install]
WantedBy=multi-user.target
```
`sudo systemctl daemon-reload && sudo systemctl enable --now watch-news`（research 同法，**错峰**可加 `ExecStartPre=/bin/sleep 900`）。

## 6. 🚨 安全：`doc/keys.txt` 已被 git 跟踪

- **事实**：`git ls-files doc/keys.txt` → **被跟踪**（提交 `56fae84`）；**不在 `.gitignore`** → 里面是 **8 个 chat/coding LLM 的 Key（+ASR+文生图）**。
- **风险**：Key 已进**仓库历史**；只要仓库或任何 fork/clone 泄露，等于泄露密钥。
- **建议**：
  1. 把 `doc/keys.txt` 加入 **`.gitignore`** 并 `git rm --cached doc/keys.txt`（**保留本地文件**）；
  2. **轮换**这些 Key（已进历史的按"已泄露"处理）；
  3. 改用**环境变量/本地未跟踪文件**（如 `~/.llm_keys.txt`）供 `llm_rotate.sh` 读取。

## 7. 与其它文档的关系

- **额度/鉴权轮换接入**：见 `LLM_ROTATE_INTEGRATION.md`
- **心跳**：任务书已强制（每轮向 `daily-memories-*/<date>.md` 追加 `[HH:MM] wake | ...`）
- **任务书 / 产出规范**：见 `../README.md`、`../AGENTS.md`、各产物目录的 `README.md`
