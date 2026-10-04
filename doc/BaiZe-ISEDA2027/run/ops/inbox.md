# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 29 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> 危险模式会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **两条纪律**（前两批的教训）：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② **绝不整树 `du`** —— `/nas_train` 有 175 TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`（每条带 `timeout`）**。
>
> ## 🚨🚨 **中继的真实行为（2026-10-02 实测，务必遵守）**
> `ops_relay.sh:46` 的 `inbox_cmd_block()` 是：
> ```bash
> awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"
> ```
> **→ 它只执行文件里<u>第一个</u> ```bash 块**，后面的块**永远不会被执行**。
>
> **我们已因此踩了一次坑**：RUN_ID 从 3 加到 4 时，中继**又把 RUN_ID 3 的磁盘勘察跑了一遍**，
> 新写的命令被静默忽略（outbox 里 RUN_ID 4 记录的命令文本就是 RUN_ID 3 的）。
>
> ### ✅ 下发新命令的铁律
> 1. **把要执行的块放在文件的<u>最前面</u>**（任何 `## RUN_ID N` 标题之前的位置无所谓，关键是**第一个 ```bash**）。
> 2. **把旧块降级为 ```text**（或删掉）—— 否则它一直霸占"第一个块"。
> 3. **每次 `RUN_ID` 都要 +1**（中继靠"变大"触发）。
>
> > 🔧 **根治方案（待中继重启时再改，勿改运行中的脚本）**：
> > 把 `inbox_cmd_block()` 改成按最新 RUN_ID 取块，例如
> > `awk -v rid="$rid" '/^## RUN_ID /{cur=$3} /^```bash/{if(cur==rid){f=1;next}} /^```/{if(f)exit} f' "$INBOX"`。

---

## RUN_ID 29 — ✂️ **注释 `.29` 的 `~/.bashrc` 里的 `OPENAI_API_KEY`（已获批准）**（**本块最新，优先执行**）

**用户决定（2026-10-04）**：**只注释 `OPENAI_API_KEY`（原值保留为注记）**；**`https_proxy` 不动**（实测 GitHub 没它就 FAIL）；同时已把 harness 的 driver 改成读 `secrets.json`。

**RUN_ID 28 事实基础**：
- 该变量在 **`~/.bashrc:170`**（`export OPENAI_API_KEY=…`，连同 `API_TYPE`:169 / `OPENAI_API_URL`:171）；`/etc/profile.d`、`/etc/environment` **均无**
- 它是**已吊销**的 key → 会**覆盖** `secrets.json` 里的有效 key（V0/V1/V2 全 Forbidden 的一半原因）
- **`.12` 是范本**：它的 `.bashrc:143` 就注释着 `# disabled: proxy DNS cannot resolve internal agi-gateway.cxmt.com`

**本块动作**：备份 `.bashrc` → 用 `sed` 把 `export OPENAI_API_KEY=` 行**原地注释**（**原值保留**，不删）→ 语法自检 → 确认 `https_proxy`/`API_TYPE`/`OPENAI_API_URL` **未被动** → 确认两条 loop 仍在跑（**本次不动进程**）。

> ⚠️ 注：改 `.bashrc` **不影响已在运行的 loop**（进程 env 在启动时已固化），属"防未来"；loop 侧的 V3 配方（剥 proxy + 显式 `-k`）**保持不变**。

```bash
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
B="$HOME/.bashrc"; TS=$(date +%Y%m%d-%H%M%S)

echo; echo "=== 1. 备份 .bashrc ==="
cp -a "$B" "$B.bak.$TS" && echo "   backed up -> $B.bak.$TS"
echo "   改前 165-175 行（masked）:"
sed -n '165,175p' "$B" | sed -E 's/(=|")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g' | cut -c1-130

echo; echo "=== 2. 原地注释 export OPENAI_API_KEY（原值保留）==="
sed -i -E 's|^([[:space:]]*)export[[:space:]]+OPENAI_API_KEY=|\1# [2026-10-04 ops] export OPENAI_API_KEY=|' "$B"
echo "   改后 165-175 行（masked）:"
sed -n '165,175p' "$B" | sed -E 's/(=|")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g' | cut -c1-130

echo; echo "=== 3. 自检 ==="
bash -n "$B" && echo "   bash -n : OK"
echo -n "   已注释的 OPENAI_API_KEY 行数 = "; grep -c '^[[:space:]]*#[[:space:]]*\[2026-10-04 ops\][[:space:]]*export OPENAI_API_KEY=' "$B"
echo -n "   仍生效的 OPENAI_API_KEY 行数 = "; grep -c '^[[:space:]]*export[[:space:]]+OPENAI_API_KEY=' "$B"

echo; echo "=== 4. 确认其余未被动（masked）==="
grep -nE '^[[:space:]]*(export[[:space:]]+)?(https_proxy|http_proxy|API_TYPE|OPENAI_API_URL)' "$B" | sed -E 's/(=|")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g' | cut -c1-135

echo; echo "=== 5. 两条 loop 仍在跑（本次不动进程）==="
pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-92
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 28**（rc 探查，**✅ 已执行 08:06:30**）为 ```text。

## RUN_ID 28 — 🔍 **查清那两个变量在哪设的 + 去掉各自会有什么后果**（✅ 已执行，本块不再运行）

**用户提问（2026-10-04）**：`OPENAI_API_KEY` / `*_proxy` 是不是在 `.29` 的 `~/.bashrc` 里设的？要不要注释掉？

**先搞清事实再动手**（🚫 本块**只读**，不改任何 rc 文件）：
1. **在哪设的**：`~/.bashrc` / `~/.bash_profile` / `~/.profile` / `~/.bash_aliases` / `/etc/profile.d/*` / `/etc/environment`（**值只打 masked**）
2. **`.12` 对照**：为什么 `.12` 没这些变量（它的 rc 里有什么）
3. **去掉 proxy 的后果**：`git ls-remote github` 在没有 proxy 时通不通（**决定能不能注释掉**）
4. **gateway 域名是否适合放进 `no_proxy`**（比全局删 proxy 更精准的解法）

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'

echo; echo "=== 1. [.29] rc 文件里的相关设置（masked）==="
for f in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile" "$HOME/.bash_aliases" "$HOME/.bash_login"; do
  [ -f "$f" ] || continue
  echo "-- $f (mtime $(stat -c %y "$f" | cut -c1-19)) --"
  grep -inE 'proxy|OPENAI|API_TYPE|ANTHROPIC|no_proxy' "$f" 2>/dev/null \
    | sed -E 's/(=|")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g' | cut -c1-150 | head -12
done

echo; echo "=== 2. [.29] 系统级 /etc/profile.d 与 /etc/environment ==="
grep -rinE 'proxy|OPENAI|API_TYPE' /etc/profile.d/ /etc/environment /etc/profile 2>/dev/null \
  | sed -E 's/(=|")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g' | cut -c1-140 | head -12

echo; echo "=== 3. [.29] proxy 是否在外网可达上必需（关键！）==="
echo -n "   github WITHOUT proxy : "; timeout 25 env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
  git ls-remote --heads https://github.com/openai/openai-python.git HEAD >/dev/null 2>&1 && echo OK || echo FAIL
echo -n "   github WITH proxy    : "; timeout 25 git ls-remote --heads https://github.com/openai/openai-python.git HEAD >/dev/null 2>&1 && echo OK || echo FAIL
echo -n "   gateway WITHOUT proxy: "; timeout 15 env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY curl -s -o /dev/null -w '%{http_code}' http://agi-gateway.cxmt.com/v1/models; echo
echo -n "   gateway WITH proxy   : "; timeout 15 curl -s -o /dev/null -w '%{http_code}' http://agi-gateway.cxmt.com/v1/models; echo
echo "   no_proxy 现值: [${no_proxy:-<empty>}] / [${NO_PROXY:-<empty>}]"
echo "   https_proxy 现值: $(echo "${https_proxy:-<empty>}" | cut -c1-20)"

echo; echo "=== 4. [.12] 对照：它的 rc 里有什么 ==="
timeout 30 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 '
for f in $HOME/.bashrc $HOME/.bash_profile $HOME/.profile; do
  [ -f "$f" ] || continue
  echo "-- $f --"; grep -inE "proxy|OPENAI|API_TYPE|no_proxy" "$f" 2>/dev/null | sed -E "s/(=|\")[A-Za-z0-9_]{6}[A-Za-z0-9_.-]*/\1<MASKED>/g" | cut -c1-130 | head -8
done
echo "   .12 env: https_proxy=[${https_proxy:-<empty>}] OPENAI_API_KEY len=${#OPENAI_API_KEY}"' 2>&1 | cut -c1-155

echo; echo "=== 5. 当前 loop 状态（不动）==="
pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-90
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 27**（最终修复，**✅ 已执行 08:01:13**，**两线已复工**）为 ```text。

## RUN_ID 27 — ✅ **应用 V3 配方（`-k` 显式传 key）+ 重启两条 loop**（✅ 已执行，两线复工）

**RUN_ID 26 四路矩阵（2026-10-04 07:58:23）—— 定论**：
| 组 | env | 结果 |
|:--|:--|:--|
| V0 | 原样 | Forbidden |
| V1 | 剥 `KEY+URL+TYPE` | Forbidden |
| V2 | 剥 `proxy+KEY+URL+TYPE` | Forbidden |
| **V3** | V2 **+ `-k <有效key>`** | **OK** ✅ |

⇒ **`.29` 的 cline 必须显式 `-k`**（key 请 curl 200；`.12` 不带 `-k` 也能跑，但 `.29` 不行）。
📌 已把两条 loop 的 cline 调用行改成：`env -u <所有 *_proxy> -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE cline … -k "$CLINE_KEY" …`，`CLINE_KEY` 在脚本启动时用 `sed` 从 `secrets.json` 现读（**不落仓库**）。

**本块**：先跑一次 V3 前置校验（**不 OK 就不重启**）→ checkout 新脚本 → 重启 → 校验 `error:.*Forbidden == 0`。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
WK=/nas_train/app.e0031982/code/super_intelligence_2035; RUN=$WK/doc/BaiZe-ISEDA2027/run
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" | head -1)"
P="-u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY"

echo; echo "=== 1. 前置：V3 复核（必须 OK 才重启）==="
V3=$(env $P -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE timeout 90 "$C" -c /tmp -m "$M" -k "$_k" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -2 | tr -d '\r' | tr '\n' ' ')
echo "   V3 => ${V3:0:130}"

echo; echo "=== 2. 条件重启 ==="
if echo "$V3" | grep -q 'Forbidden'; then
  echo "   !!! V3 仍失败 → 不重启，保留现状待运维"
else
  git -C "$WK" fetch origin --quiet 2>/dev/null
  git -C "$WK" checkout origin/main -- doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh && echo "   checked out"
  grep -c 'CLINE_KEY' "$RUN/baize_pretrain_loop.sh" "$RUN/baize_harness_loop.sh"
  pkill -f 'baize_pretrain_loop.sh'; pkill -f 'baize_harness_loop.sh'; sleep 5
  cd "$RUN"
  setsid bash baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
  sleep 3
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 30
  echo "   -- 进程 --"; pgrep -af 'bash baize_(pretrain|harness)_loop\.sh|bun.*cline' | cut -c1-102
  echo "   -- 真实报错数（应为 0）--"; grep -c 'error:.*Forbidden' /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null
  echo "   -- pretrain 日志尾 --"; tail -c 320 /tmp/baize_pretrain_loop.log | tr -d '\r' | tail -3 | cut -c1-135
  echo "   -- harness 日志尾 --"; tail -c 320 /tmp/baize_harness_loop.log | tr -d '\r' | tail -3 | cut -c1-135
fi

echo; echo "=== 3. GPU（P-9）==="; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -2
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 26**（4 路矩阵，**✅ 已执行 07:58:23**，**结果：V3 = OK**）为 ```text。

## RUN_ID 26 — 🎯 **锁定唯一残留变量：`OPENAI_API_URL` + `API_TYPE`（4 路矩阵）**（✅ 已执行 → **V3 是解**，见 RUN_ID 27）

**已排除（2026-10-04 07:56）**：
- ❌ **cline 版本**：`.29`/`.12` 都是 **CLI 3.0.51**，安装日期同为 **2026-09-08**（globalState 里的 4.1.21/4.0.8 是 **VSCode 扩展**版本，与 CLI 无关）→ "10-03 自动升级"**否证**
- ❌ **看门 | key**：`.29` secrets key → `curl` = **200**
- ❌ **`-c /tmp` / 模型名**：`.12` 用**完全相同的命令**跑通了（`[thinking] … → OK`）
- ✅ **`.12` 与 `.29` 的唯一环境差异 = `.29` 多出 `OPENAI_API_URL=http://agi-gateway.cxmt.com/v1` 与 `API_TYPE=openai`**
- 📌 **旁证**：唯一在 `.29` 上成功过的那次 smoke（RUN_ID 14 §3）**恰好也 unset 了这两个变量**；我后续几轮都漏了

**4 路矩阵**（每组都只改 env，不改文件）：
| 组 | env | 期望 |
|:--|:--|:--|
| V0 | 原样 | Forbidden（基线） |
| V1 | 剥 `OPENAI_API_KEY`+`OPENAI_API_URL`+`API_TYPE`（**不剥 proxy**） | 看 URL/TYPE 是否单独致命 |
| V2 | 剥 proxy + 剥三者（=RUN_ID 14 的配方，**不带 -k**） | 若 OK → **修法 = 在 cline 调用行补 `-u OPENAI_API_URL -u API_TYPE`** |
| V3 | 剥三者 + `-k <secrets>`（=RUN_ID 14 原样） | 若 OK 而 V2 不 → 需要显式 `-k` |

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" | head -1)"
P="-u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY"
SM="reply with exactly OK"
run() { L="$1"; shift; printf '   %-30s => ' "$L"; env "$@" timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "$SM" 2>&1 | head -2 | tr -d '\r' | tr '\n' ' ' | cut -c1-135; echo; }

echo; echo "=== 1. 4 路矩阵 ==="
run "V0 原样"
run "V1 剥KEY+URL+TYPE"        -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE
run "V2 剥proxy+KEY+URL+TYPE"  $P -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE
printf '   %-30s => ' "V3 同V2 + -k"; env $P -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE timeout 90 "$C" -c /tmp -m "$M" -k "$_k" --auto-approve true -t 45 "$SM" 2>&1 | head -2 | tr -d '\r' | tr '\n' ' ' | cut -c1-135; echo

echo; echo "=== 2. 现状（不动 loop）==="
pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-90
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 25**（cline 升级假说，**✅ 已执行 07:56:56**，**结果：版本相同 3.0.51 → 否证**）为 ```text。

## RUN_ID 25 — 🔎 **最后一击：cline 是否在 10-03 22:10 前后被自动升级**（✅ 已执行，❌ 否证，见 RUN_ID 26）

**RUN_ID 24 唯一实质差异（2026-10-04 07:54:35）**：
| 项 | `.29` | `.12` |
|:--|:--|:--|
| **clineVersion** | **4.1.21**（较新） | **4.0.8**（较旧） |
| actModeOpenAiModelId | `deepseek-v4-flash` | `deepseek-v4-pro-fp4` |
| provider / openAiBaseUrl | `openai` / 网关 | `openai` / 网关（**一致**） |

⇒ **假说：`.29` 的 cline 在 10-03 22:10 前后被自动升级到 4.1.21，新版与我们的网关配置不兼容** → 这正好是停摆起点。

**本块要证/否证的**：
1. **`.29` cline 安装目录的 mtime** —— 若 ≈ `2026-10-03 22:xx` → **升级坐实**
2. **`.12` 上把同一 smoke 跑通**（上次因 ssh 的 PATH 缺 `bun` 而无效，本次显式加 `$HOME/.bun/bin`）
3. 两机 `--version` 并排

🚫 **只读**：不安装、不降级、不重启任何 loop。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'

echo; echo "=== 1. [.29] cline 安装痕迹（找自动升级时间）==="
ls -l --time-style=long-iso "$HOME/.bun/bin/cline" 2>/dev/null
readlink -f "$HOME/.bun/bin/cline" 2>/dev/null | sed 's/^/   -> /'
find "$HOME/.bun" -maxdepth 7 -name 'package.json' -path '*cline*' -printf '   %TY-%Tm-%Td %TH:%TM  %p\n' 2>/dev/null | head -6
find "$HOME/.bun/install/global" -maxdepth 3 -printf '   %TY-%Tm-%Td %TH:%TM  %p\n' 2>/dev/null | head -8
echo -n "   .29 cline --version: "; "$HOME/.bun/bin/cline" --version 2>&1 | head -1

echo; echo "=== 2. [.12] 对照 ==="
timeout 35 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 '
ls -l --time-style=long-iso $HOME/.bun/bin/cline 2>/dev/null | sed "s/^/   /"
find $HOME/.bun -maxdepth 7 -name package.json -path "*cline*" -printf "   %TY-%Tm-%Td %TH:%TM  %p\n" 2>/dev/null | head -6
export PATH=$HOME/.bun/bin:$PATH
echo -n "   .12 cline --version: "; cline --version 2>&1 | head -1' 2>&1 | cut -c1-165

echo; echo "=== 3. [.12] 同一 smoke（显式补 PATH）—— 预期 OK ==="
timeout 70 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 '
export PATH=$HOME/.bun/bin:$PATH; cd /tmp
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_KEY \
  timeout 50 cline -c /tmp -m deepseek-v4-pro-fp4 --auto-approve true -t 35 "reply with exactly OK" 2>&1 | head -3' 2>&1 | cut -c1-155

echo; echo "=== 4. 现状（不动）==="
pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-90
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 24**（对撞测试，**✅ 已执行 07:54:35**）为 ```text。

## RUN_ID 24 — 🔬 **对撞：同一 key 下 `.12` 的 cline 能跑、`.29` 不能 —— 差在哪**（✅ 已执行，本块不再运行）

**现状（2026-10-04 07:52）**：
- ❌ `.29`：**任何 env 组合**（剥/不剥 proxy、剥/放 OPENAI_API_KEY、v1/v2/v3）→ cline 一律 **3 秒内 `error: Forbidden`**
- ✅ **同一把 key** → `curl /v1/chat/completions` = **200**
- ✅ **`.12` 的 vision/data 一直在正常干活**（clog mtime 07:46）
- ⇒ **问题已从「key/proxy」转移到「`.29` 上的 cline 客户端本身」**（本地配置 / 版本 / data-dir）

**本块四连测（全只读，绝不重启任何 loop）**：
| # | 测什么 | 判定 |
|:--|:--|:--|
| 1 | 两机 cline **版本** | 版本不同 → 升级/回滚 |
| 2 | 两机 `globalState.json` **全量键值对比** | 找出唯一差异 |
| 3 | **在 `.12` 上跑同一 smoke**（经 ssh） | 若 OK → 坐实"host-local" |
| 4 | 在 `.29` 用 **全新 `--data-dir`** 跑 smoke | 若 OK → **`.29` 的 `~/.cline/data` 坏了**（可隔离修复） |

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" | head -1)"
P="-u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY"
SM="reply with exactly OK"

echo; echo "=== 1. 两机 cline 版本 ==="
echo -n "   .29: "; "$C" --version 2>&1 | head -1
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 "echo -n '   .12: '; /home/app.e0031982/.bun/bin/cline --version 2>&1 | head -1" 2>&1 | tail -1

echo; echo "=== 2. globalState.json 键值对比（只打非敏感项）==="
sed -n '1,400p' "$HOME/.cline/data/globalState.json" 2>/dev/null | tr ',' '\n' | grep -iE 'provider|model|baseurl|version|telemetry|proxy|auth' | head -20 | sed 's/^/   .29 /'
echo "   -- .12 --"
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 "sed -n '1,400p' \$HOME/.cline/data/globalState.json 2>/dev/null | tr ',' '\n' | grep -iE 'provider|model|baseurl|version|telemetry|proxy|auth' | head -20 | sed 's/^/   .12 /'" 2>&1 | head -22

echo; echo "=== 3. 在 .12 上跑同一 smoke（判定 host-local）==="
timeout 60 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 "cd /tmp && env $P -u OPENAI_API_KEY timeout 45 /home/app.e0031982/.bun/bin/cline -c /tmp -m $M --auto-approve true -t 30 '$SM' 2>&1 | head -3 | cut -c1-140" 2>&1 | cut -c1-150

echo; echo "=== 4. 在 .29 用【全新 --data-dir】跑 smoke（判定本地配置是否坏了）==="
rm -rf /tmp/_cd_probe 2>/dev/null
env $P -u OPENAI_API_KEY timeout 90 "$C" --data-dir /tmp/_cd_probe -c /tmp -m "$M" --auto-approve true -t 45 "$SM" 2>&1 | head -3 | cut -c1-150

echo; echo "=== 5. 当前 loop 状态（不动）==="
pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-95
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 23**（正确复测，**✅ 已执行 07:52:08**，**结果：T1/T2/T3 全 Forbidden → 未重启**）为 ```text。

## RUN_ID 23 — 🎯 **正确复测（带 proxy 剥离）+ 通过则自动重启**（✅ 已执行，⚠️ 全挂、未重启，见 RUN_ID 24）

**RUN_ID 22 关键结论（2026-10-04 07:49:40）**：
- 🔑 **key 是有效的**：`.29` secrets key → **curl 200** ✅；`.12` key → **200** ✅，且 `.12` 一直在干活
- ❌ `.env` 里那些 `*_API_KEY`（len=72, `02_0…`）→ **403**（无效，不用了）
- 🩹 **我的 RUN_ID 20 测试有缺陷**：A/B/C 三组**都漏了剥 proxy**（`via-proxy -> 503` 早就测出来了）→ 结论无效
- ✅ **07:28 那版（`-u <所有 *_proxy>` + `-u OPENAI_API_KEY`）是能跑的**（pretrain 因此产出 `beea3f1`）；我在"修 driver"时把它改坏了
- 📌 已把两条 loop 回退为 **v1**（proxy 全剥 + `-u OPENAI_API_KEY`）

**本块 = 一次把事做实**：
| 组 | 环境 | 预期 |
|:--|:--|:--|
| **T1** | 剥 proxy + `-u OPENAI_API_KEY`（=v1） | **OK** → 自动重启两条 loop |
| **T2** | 剥 proxy + `OPENAI_API_KEY=<有效>` | 若也 OK → 将来可用它救 driver |
| **T3** | 剥 proxy + `OPENAI_API_KEY=<stale>` | 预期 Forbidden（坐实 stale env key 有毒） |

> 仅当 **T1 通过**才重启；T1 若仍 Forbidden → **不动 loop**，只报告。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
WK=/nas_train/app.e0031982/code/super_intelligence_2035; RUN=$WK/doc/BaiZe-ISEDA2027/run
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" | head -1)"
P="-u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY"

echo; echo "=== 1. T1 剥proxy + 剥OPENAI_API_KEY（=v1）==="
T1=$(env $P -u OPENAI_API_KEY timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -3 | tr -d '\r' | tr '\n' ' ')
echo "   T1 => ${T1:0:150}"

echo; echo "=== 2. T2 剥proxy + OPENAI_API_KEY=有效(secrets) ==="
env $P OPENAI_API_KEY="$_k" timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -3 | cut -c1-150

echo; echo "=== 3. T3 剥proxy + OPENAI_API_KEY=stale(env) ==="
env $P OPENAI_API_KEY="$OPENAI_API_KEY" timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -3 | cut -c1-150

echo; echo "=== 4. 条件重启 ==="
if echo "$T1" | grep -q 'Forbidden'; then
  echo "   !!! T1 仍 Forbidden → 不重启，保留现状待运维决策"
else
  echo "   T1 通过 → checkout v1 脚本并重启两条 loop"
  git -C "$WK" fetch origin --quiet 2>/dev/null
  git -C "$WK" checkout origin/main -- doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh && echo "   checked out"
  pkill -f 'baize_pretrain_loop.sh'; pkill -f 'baize_harness_loop.sh'; sleep 5
  cd "$RUN"
  setsid bash baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
  sleep 3
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 25
  echo "   -- 校验 --"; pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-100
  echo "   -- 真实报错数（应为 0）--"; grep -c 'error:.*Forbidden' /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null
  echo "   -- pretrain 日志尾 --"; tail -c 300 /tmp/baize_pretrain_loop.log | tr -d '\r' | tail -3 | cut -c1-135
  echo "   -- harness 日志尾 --"; tail -c 300 /tmp/baize_harness_loop.log | tr -d '\r' | tail -3 | cut -c1-135
fi

echo; echo "=== 5. GPU（P-9）==="; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -2
echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 22**（读 .env + 筛 key，**✅ 已执行 07:49:48**）为 ```text。

## RUN_ID 22 — 🔑 **读 `eda_fastmcp/.env` 的候选 key + 逐个打网关筛出可用的**（✅ 已执行，本块不再运行）

**背景（用户 2026-10-04 提供）**：`/nas_train/app.e0031982/code/eda_fastmcp/.env` 里还有几把 key（**GLM-5.2 / deepseek-v4-flash / kimi-k2.6 / 豆包**）→ 若其中一把能过网关，即可替换 `.29` 的失效 key。
**RUN_ID 20 遗留**：三路 smoke（env=valid / unset / env=stale）**全 Forbidden** → 当前那把 `02_088…` 疑似**也失效了**。

🚫 **本块只读**；⚠️ **key 一律只打 `len` + `prefix4`，绝不输出完整值**。
> 📌 同时顺带完成 RUN_ID 21 的判定（`.29` vs `.12` 的 key/存活/mtime）。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
GW=http://agi-gateway.cxmt.com/v1; E=/nas_train/app.e0031982/code/eda_fastmcp/.env

echo; echo "=== 1. .env 存在性 + 变量名（值仅 len/prefix4）==="
if [ -f "$E" ]; then
  ls -l "$E" | cut -c1-100
  while IFS='=' read -r k v; do
    case "$k" in ''|'#'*) continue;; esac
    v="${v%\"}"; v="${v#\"}"; v="${v%\'}"; v="${v#\'}"
    printf '   %-30s len=%-4s prefix4=%s\n' "$k" "${#v}" "${v:0:4}"
  done < "$E"
else
  echo "   !!! 不存在：$E"; ls -l /nas_train/app.e0031982/code/ 2>/dev/null | head -15
fi

echo; echo "=== 2. 每个 key × 2 个模型 → http code（200=可用）==="
while IFS='=' read -r k v; do
  case "$k" in ''|'#'*) continue;; esac
  v="${v%\"}"; v="${v#\"}"; v="${v%\'}"; v="${v#\'}"
  [ "${#v}" -lt 16 ] && continue
  for M in deepseek-v4-flash deepseek-v4-pro-fp4; do
    code=$(timeout 20 curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $v" -H 'Content-Type: application/json' \
      -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":3}" "$GW/chat/completions" 2>/dev/null)
    printf '   %-30s %-22s -> %s\n' "$k" "$M" "$code"
  done
done < "$E"

echo; echo "=== 3. 顺带：.29 当前 key 是否也失效 ==="
sk="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" | head -1)"
echo "   .29 secrets: len=${#sk} prefix4=${sk:0:4} mtime=$(stat -c %y "$HOME/.cline/data/secrets.json" | cut -c1-19)"
echo -n "   .29 curl -> "; timeout 20 curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $sk" -H 'Content-Type: application/json' -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"hi"}],"max_tokens":3}' "$GW/chat/completions"

echo; echo "=== 4. 对照 .12：key 状态 + 是否仍在干活 ==="
timeout 30 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 '
S="$HOME/.cline/data/secrets.json"
k="$(sed -n "s/.*\"openAiApiKey\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$S" | head -1)"
echo "   .12 secrets: len=${#k} prefix4=${k:0:4} mtime=$(stat -c %y "$S" | cut -c1-19)"
printf "   .12 curl -> "; timeout 20 curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $k" -H "Content-Type: application/json" -d "{\"model\":\"deepseek-v4-pro-fp4\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":3}" http://agi-gateway.cxmt.com/v1/chat/completions
echo "   -- .12 loops --"; pgrep -af "baize_.*_loop\.sh" | cut -c1-90
echo "   -- .12 vision log mtime --"; stat -c %y /tmp/baize_vision_loop.log 2>/dev/null | cut -c1-19
' 2>&1 | cut -c1-165 || echo "ssh .12 FAILED"

echo; echo "=== 5. GPU（P-9 应仍在跑）==="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -2

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 21**（key 是否再轮换，**未推送**）为 ```text —— 其内容已并入本块第 3/4 节。

## RUN_ID 21 — 🔴 **决定性判定：key 是不是【又被轮换】了？**（⛔ 未执行，已并入 RUN_ID 22）

**RUN_ID 20 的意外结果（2026-10-04 07:44:05）**：**三路 smoke 全 `Forbidden`** —— 连 **B（unset）** 也失败，而 **07:29 时同一招是 OK 的**（RUN_ID 15 §3 明确 OK）。
⇒ **不是 env 变体的问题**；**key 本身在 07:29→07:44 之间再次失效**（或网关开始拒绝）。
🔎 **高度怀疑**：我在 07:15 建议"尽快轮换 key" → **若你已轮换，则 `.12` 那把（`02_088`，我复制到 `.29` 的）也已作废** → 完美解释"三路全挂"。

**本块 = 一锤定音**（只读，不动任何 loop）：
| 测点 | 含义 |
|:--|:--|
| `.29` secrets key → curl | 若 403 → 该 key 死了 |
| **`.12` secrets key → curl** | 若也 403 → **key 被全局轮换**（两机都失效）；若 200 → 只有 `.29` 有问题 |
| **`.12` 的 vision/data 是否仍在干活** | 若也停了 → 全局面（`02_088` 死）；若还在跑 → 只有 `.29` 异常 |
| 两机 secrets.json 的 **mtime** | 若 `.12` 的 mtime 变成今天 → **刚被轮换过** |

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
GW=http://agi-gateway.cxmt.com/v1
S="$HOME/.cline/data/secrets.json"
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$S" | head -1)"

echo; echo "=== 1. [.29] secrets.json + curl（用当前 key）==="
echo "   mtime=$(stat -c %y "$S" | cut -c1-19)  len=${#_k} prefix6=${_k:0:6}"
timeout 20 curl -s -o /tmp/_a.json -w '   curl code=%{http_code}\n' -H "Authorization: Bearer $_k" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"hi"}],"max_tokens":3}' "$GW/chat/completions"
head -c 200 /tmp/_a.json 2>/dev/null; echo
echo "   [.29] env 里的 key: len=${#OPENAI_API_KEY} prefix6=${OPENAI_API_KEY:0:6}"

echo; echo "=== 2. [.12] secrets.json + curl + 是否仍在干活 ==="
timeout 35 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 '
GW=http://agi-gateway.cxmt.com/v1; S="$HOME/.cline/data/secrets.json"
k="$(sed -n "s/.*\"openAiApiKey\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" "$S" | head -1)"
echo "   mtime=$(stat -c %y "$S" | cut -c1-19)  len=${#k} prefix6=${k:0:6}"
timeout 20 curl -s -o /dev/null -w "   curl code=%{http_code}\n" -H "Authorization: Bearer $k" -H "Content-Type: application/json" -d "{\"model\":\"deepseek-v4-pro-fp4\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":3}" "$GW/chat/completions"
echo "-- loops --"; pgrep -af "baize_.*_loop\.sh" | cut -c1-95
echo "-- logs mtime --"; for f in /tmp/baize_vision_loop.log /tmp/baize_data_loop.log; do printf "   %s %s\n" "$(stat -c %y $f 2>/dev/null | cut -c1-19)" "$f"; done
echo "-- vision log tail --"; tail -c 250 /tmp/baize_vision_loop.log 2>/dev/null | tr -d "\r" | tail -2 | cut -c1-120
' 2>&1 | cut -c1-168 || echo "ssh .12 FAILED"

echo; echo "=== 3. 现有 loop 状态（不动它们）==="
pgrep -af "bash baize_(pretrain|harness)_loop\.sh" | cut -c1-95
echo "-- GPU（P-9 应仍在跑）--"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -2

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 20**（三路 smoke，**✅ 已执行 07:44:14**，**结果：A/B/C 全 Forbidden**）为 ```text。

## RUN_ID 20 — 🔬 **判定：cline 在「env=有效 key」下能否跑（vs「彻底 unset」）**（✅ 已执行，⚠️ 三路全挂，见 RUN_ID 21）

**已知事实**：
- ✅ **07:28 那版**（启动时 `env -u OPENAI_API_KEY` + cline 行也 `-u OPENAI_API_KEY`）= **彻底没有该变量** → **clinely 正常工作**（pretrain 因此产出 `beea3f1`「P-5b 完成 + P-9.1 启动」）
- ❌ **07:39 / 07:42 两版**（脚本注入 key）→ 重启后 **3 秒即 `error: Forbidden`**
- ⚠️ 我上一轮的校验方法**无效**：`/proc/<pid>/environ` 是 **exec 时的初始环境**，脚本里的 `export`/`unset` 不会反映进去 → 无法用它判断注入是否生效
- ✅ 但 `sed` 提取本身没问题：本块第 1 节会再验一次（应 `len=72 prefix6=02_088`）

**本块 = 三路 smoke 对照**（只读，不改任何文件）：
| 组 | 环境 | 判定 |
|:--|:--|:--|
| **A** | `OPENAI_API_KEY=<有效>` | 若 OK → 「注入有效 key」可行，问题在脚本没生效 |
| **B** | `OPENAI_API_KEY` 被 unset | 若 OK（预期）→ **以 unset 为准** |
| **C** | `OPENAI_API_KEY=<stale 01_549…>` | 若 Forbidden → 坐实 stale env key 会毒化 cline |

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" 2>/dev/null | head -1)"

echo; echo "=== 1. key 提取自检（masked）==="
echo "   valid(sed): len=${#_k} prefix6=${_k:0:6}"
echo "   stale(env): len=${#OPENAI_API_KEY} prefix6=${OPENAI_API_KEY:0:6}"

try() { L="$1"; shift; printf '   [%s] => ' "$L"; env "$@" timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -3 | tr -d '\r' | tr '\n' ' ' | cut -c1-150; echo; }

echo; echo "=== 2. 三路 smoke ==="
try "A env=valid"  OPENAI_API_KEY="$_k"
try "B unset"      -u OPENAI_API_KEY
try "C env=stale"  OPENAI_API_KEY="${OPENAI_API_KEY}"

echo; echo "=== 3. 顺便：harness 的 driver 会不会因 unset 而不可用 ==="
echo "   run_harness.py 读 key 的行："
grep -n 'OPENAI_API_KEY' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/run_harness.py 2>/dev/null | head -4 | cut -c1-140

echo; echo "=== 4. 当前两条 loop 的日志尾（现状）==="
tail -c 300 /tmp/baize_pretrain_loop.log 2>/dev/null | tr -d '\r' | tail -3 | cut -c1-130
tail -c 300 /tmp/baize_harness_loop.log  2>/dev/null | tr -d '\r' | tail -3 | cut -c1-130

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 19**（v3 sed 注入，**✅ 已执行 07:42:54**，**结果：仍 Forbidden**）为 ```text。

## RUN_ID 19 — 🔧 **修复第三版：改纯 shell 的 sed 取 key + 重启**（✅ 已执行，⚠️ 仍 Forbidden，见 RUN_ID 20）

**RUN_ID 18 暴露的回归（2026-10-04 07:40）**：
- ❌ 我 v2 用 `python3 -c ...` 注入 key，但 **relay 拉起的 non-interactive shell 里 `python3` 不在 PATH** → 取不到 → **没覆盖** → loop 继承了父进程那把 **stale `01_549…`** → 重启后立刻又 `error: Forbidden`（pretrain/harness 各 1 次）
- ✅ v3：改用 **纯 shell `sed`** 从 secrets.json 提取（不依赖 python），并加 **兜底 `unset`**（读不到就退回 secrets.json，绝不撞 stale key）
- 📌 本块**先验证 sed 能取到 key**（只打 len/prefix6），**取不到就中止、不动 loop**

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
WK=/nas_train/app.e0031982/code/super_intelligence_2035; RUN=$WK/doc/BaiZe-ISEDA2027/run

echo; echo "=== 1. 先验证 sed 提取（只打 masked）==="
_k="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" 2>/dev/null | head -1)"
echo "   extracted: len=${#_k} prefix6=${_k:0:6}  (期望 len=72 prefix6=02_088)"
[ -n "$_k" ] || { echo "   !!! sed 取不到 → 中止，不改动任何 loop"; echo DONE; exit 0; }
unset _k

echo; echo "=== 2. checkout v3 脚本 ==="
git -C "$WK" fetch origin --quiet 2>/dev/null
git -C "$WK" checkout origin/main -- doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh && echo "   checked out"
grep -n 'openAiApiKey' "$RUN/baize_pretrain_loop.sh" "$RUN/baize_harness_loop.sh" | cut -c1-120

echo; echo "=== 3. 停 + 重启（🚫 不碰 GPU 上的 P-9）==="
pkill -f 'baize_pretrain_loop.sh'; pkill -f 'baize_harness_loop.sh'; sleep 5
pgrep -af 'baize_(pretrain|harness)_loop\.sh' | cut -c1-100 || echo "   已停止"
cd "$RUN"
setsid bash baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
sleep 3
setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
sleep 25

echo; echo "=== 4. 校验（重点：loop 环境里的 key 前缀必须是 02_088）==="
for n in pretrain harness; do
  P=$(pgrep -f "bash baize_${n}_loop.sh" | head -1); printf '   %-9s pid=%-9s ' "$n" "${P:-none}"
  [ -n "$P" ] && tr '\0' '\n' < "/proc/$P/environ" 2>/dev/null | grep '^OPENAI_API_KEY=' | sed 's/=\(.\{6\}\).*/key= \1...(masked)/' || echo "(no pid!)"
done
echo "-- 进程 --"; pgrep -af 'bash baize_(pretrain|harness)_loop\.sh' | cut -c1-105
echo "-- 真实报错数（应为 0）--"; grep -c 'error:.*Forbidden' /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null
echo "-- pretrain 日志尾 --"; tail -c 400 /tmp/baize_pretrain_loop.log 2>/dev/null | tr -d '\r' | tail -4 | cut -c1-140
echo "-- GPU（P-9 应仍在跑）--"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -3

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 18**（v2 注入，**✅ 已执行 07:40:10**，**结果=回归**）为 ```text。

## RUN_ID 18 — 🔧 **修复第二版：loop 自己注入有效 key（而非 unset）+ 重启**（✅ 已执行，⚠️ 该版有回归，见 RUN_ID 19）

**为何要改（RUN_ID 17 发现，2026-10-04 07:37）**：
- ⚠️ 我上一版补丁把 `OPENAI_API_KEY` **unset** 掉 → **`run_harness.py:105-108`**（`self.api_key=os.environ.get("OPENAI_API_KEY","")` / `available()` 要求非空）会让 **harness 自己的 driver 变 `available()==False`** → 我在修 bug 时引入了新 bug
- ✅ 正确做法：**把有效 key 注入 loop 环境**（从 `~/.cline/data/secrets.json` 现读，不落仓库）→ cline 与所有子进程（含 `ClineDriver`）都拿到它
- 📌 脚本已改：两条 loop 顶部新增 `export OPENAI_API_KEY="$(...secrets.json...)"`；cline 调用行只保留 proxy 屏蔽
- ℹ️ 另注：RUN_ID 16 的「harness Forbidden=16」经 RUN_ID 17 判定为**假阳性**（agent 推理文本在讨论该词），**精确探针应为 `grep -c 'error:.*Forbidden'`**

**本块动作**：checkout 新脚本 → 停两条 loop（**🚫 不动 GPU 上的 P-9 进程**）→ 重启 → 校验（含 loop 环境里 key 是否已注入，仅打 masked 前缀）。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
WK=/nas_train/app.e0031982/code/super_intelligence_2035; RUN=$WK/doc/BaiZe-ISEDA2027/run

echo; echo "=== 1. checkout 最新 loop 脚本 ==="
git -C "$WK" fetch origin --quiet 2>/dev/null
git -C "$WK" checkout origin/main -- doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh && echo "   checked out"
grep -n 'export OPENAI_API_KEY' "$RUN/baize_pretrain_loop.sh" "$RUN/baize_harness_loop.sh" | cut -c1-115

echo; echo "=== 2. 停两条 loop（🚫 不碰 GPU 上的 P-9）==="
ps -eo pid=,etimes=,args= 2>/dev/null | grep -E 'baize_(pretrain|harness)_loop\.sh' | grep -v grep | cut -c1-105
pkill -f 'baize_pretrain_loop.sh'; pkill -f 'baize_harness_loop.sh'; sleep 5
pgrep -af 'baize_(pretrain|harness)_loop\.sh' | cut -c1-105 || echo "   已停止"

echo; echo "=== 3. 重启（由脚本自身注入 key）==="
cd "$RUN"
setsid bash baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
sleep 3
setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
sleep 20

echo; echo "=== 4. 校验 ==="
for n in pretrain harness; do
  P=$(pgrep -f "baize_${n}_loop.sh" | head -1); printf '   %-9s pid=%-9s ' "$n" "${P:-none}"
  [ -n "$P" ] && tr '\0' '\n' < "/proc/$P/environ" 2>/dev/null | grep '^OPENAI_API_KEY=' | sed 's/=\(.\{6\}\).*/key= \1...(masked)/' || echo "(no key in env!)"
done
echo "   secrets.json: $(python3 -c "import json,os;k=json.load(open(os.path.expanduser('~/.cline/data/secrets.json')))['openAiApiKey'];print('len',len(k),'prefix6',k[:6])" 2>/dev/null)"
echo "-- 进程 --"; pgrep -af 'baize_(pretrain|harness)_loop\.sh|bun.*cline' | cut -c1-118
echo "-- 真实报错数（应为 0）--"; grep -c 'error:.*Forbidden' /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null
echo "-- pretrain 日志尾 --"; tail -c 400 /tmp/baize_pretrain_loop.log 2>/dev/null | tr -d '\r' | tail -3 | cut -c1-140
echo "-- GPU（P-9 应仍在跑）--"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 17**（Forbidden 定性，**✅ 已执行 07:37:28**）为 ```text。

## RUN_ID 17 — 🔎 **harness 日志里的 16 次 `Forbidden` 是 loop 自身还是 agent 内部嵌套调用？**（✅ 已执行，本块不再运行）

**RUN_ID 16 复查（2026-10-04 07:36:21）**：
- ✅ **pretrain 完全正常**：`Forbidden=0`；日志显示 **"P-5b completion recorded in report, P-9.1 running"**；**GPU 8 卡已重新忙起来**（22–84% util / ~39GB）→ 不再是空转
- ✅ harness loop + 一个 `bun cline` **正跑在 `harness_work/workdirs/django__django-…` 里**（= 步3 真实端到端）
- ⚠️ **harness 日志 `Forbidden=16`（修复后新日志）** → 本块判定其性质：
  - **(A) loop 自身调用失败** → 说明修复没兜住，必须再修
  - **(B) agent 自己嵌套调 cline**（如 `run_harness.py` 的 `ClineDriver` 用 `os.environ["OPENAI_API_KEY"]`，而我把该变量 unset 了 → 传空 key → 403）→ 属**我引入的副作用**，需把"unset"改成"**设为有效 key**"

🚫 **纯只读**。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
echo; echo "=== 1. harness 日志 Forbidden 上下文（前 3 处，看是否紧跟 [loop] wake up）==="
grep -n -B4 -A2 'Forbidden' /tmp/baize_harness_loop.log 2>/dev/null | head -34 | cut -c1-165

echo; echo "=== 2. harness 最近的 [loop] 行（应只有重启后的 1 次 wake up）==="
grep -n '\[loop\]' /tmp/baize_harness_loop.log 2>/dev/null | tail -8 | cut -c1-140
echo "-- Forbidden 计数（同一次运行内）--"; grep -c Forbidden /tmp/baize_harness_loop.log 2>/dev/null

echo; echo "=== 3. pretrain 对照（应为 0）==="
grep -c Forbidden /tmp/baize_pretrain_loop.log 2>/dev/null

echo; echo "=== 4. GPU 上跑的是什么 + 进程 ==="
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null | head -10 | cut -c1-80
ps -eo pid=,etimes=,args= 2>/dev/null | grep -E 'torchrun|pretrain_launcher' | grep -v grep | cut -c1-120

echo; echo "=== 5. harness 的 driver 代码里怎么取 key（举证）==="
grep -n 'OPENAI_API_KEY\|"-k"\|api_key' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/run_harness.py 2>/dev/null | head -8 | cut -c1-150

echo; echo "=== 6. pretrain 是否已回写 MEMORY ==="
ls -l --time-style=+%m-%d_%H:%M /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md 2>/dev/null | cut -c1-110

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 16**（复工复查，**✅ 已执行 07:36:21**）为 ```text。

## RUN_ID 16 — 🩺 **复工确认：两条线是否真在产出**（✅ 已执行，本块不再运行）

**RUN_ID 15 修复已执行（2026-10-04 07:29:03）**：`.29` 换上新 key + 两条 loop 已重启 → `Forbidden=0` ✅。
**本块在 ~7 分钟后复查**：① 进程/会话是否仍在 ② **`Forbidden` 是否仍为 0**（防复发）③ 两线产物 mtime 是否在动 ④ GPU 状态。

🚫 **纯只读**。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T'
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo; echo "=== 1. loop + cline 进程 ==="
ps -eo pid=,etimes=,args= 2>/dev/null | grep -E 'baize_(pretrain|harness)_loop\.sh|bun.*cline' | grep -v grep | cut -c1-115

echo; echo "=== 2. Forbidden 计数（应为 0）==="
grep -c Forbidden /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null

echo; echo "=== 3. 日志尾（看是否在正常推理 / 有无新报错）==="
echo "-- pretrain(loop) --"; tail -c 1500 /tmp/baize_pretrain_loop.log 2>/dev/null | tr -d '\r' | tail -c 500 | cut -c1-150
echo "-- harness(loop) --";  tail -c 1500 /tmp/baize_harness_loop.log  2>/dev/null | tr -d '\r' | tail -c 500 | cut -c1-150
echo "-- pretrain(P5B 训练日志最后 3 行) --"; tail -3 /tmp/baize_p5b.log 2>/dev/null | cut -c1-150

echo; echo "=== 4. 两线产物 mtime（判断是否已在写文件）==="
ls -l --time-style=+%m-%d_%H:%M "$R/MEMORY_PRETRAIN_2B.md" "$R/MEMORY_HARNESS.md" 2>/dev/null | cut -c1-110
echo "-- cline sessions 最近 3 个 --"; ls -lt --time-style=+%m-%d_%H:%M ~/.cline/data/sessions 2>/dev/null | head -4 | cut -c1-115

echo; echo "=== 5. GPU ==="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 15**（修复块，**✅ 已执行 07:29:03**）为 ```text。

## RUN_ID 15 — ✅ **执行修复：把 `.12` 的有效 key 写到 `.29` + 重启两条 loop**（✅ 已执行，本块不再运行）

**RUN_ID 14 一锤定音（2026-10-04 07:26）**：
- ✅ **`.12` 的 secrets key → `chat/completions` = 200**；用它跑 cline smoke **返回 OK**
- ❌ **`.29` 的两个 key 都 403**（env `01_549…` 与 secrets `02_088…`）；两者 prefix6 相同但**内容不同** → **`.29` 持有的是已被吊销的旧 key**
- ✅ `.12` / `.29` 的 `globalState`（provider / modelId / openAiBaseUrl）**完全一致** → 配置无差异
- ⏱ 与"10-03 22:12 后开始全程 Forbidden"**时间线吻合**

**本块动作（破坏性，已获批准）**：
1. **备份** `.29` 的 `~/.cline/data/secrets.json`
2. 从 `.12` 取有效 key，**经 stdin 管道**写入 `.29`（🚫 **key 明文绝不落入命令文本/outbox**）
3. 先用**新 secrets**（不带 `-k`）跑 smoke 验证
4. `pkill` 两条 loop → 用**已打好补丁的脚本**（`-u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE -u *_PROXY`）重启
5. 校验：进程在 + 日志**不再出现 Forbidden**

🚫 **红线**：不动 vision/data；不改任何其它文件；key 只以 `len/prefix6` 形式回显。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T %Z'
WK=/nas_train/app.e0031982/code/super_intelligence_2035; RUN=$WK/doc/BaiZe-ISEDA2027/run
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; GW=http://agi-gateway.cxmt.com/v1
S=~/.cline/data/secrets.json; TS=$(date +%Y%m%d-%H%M%S); cd /tmp

echo; echo "=== 1. 备份 .29 的 secrets.json ==="
cp -a "$S" "$S.bak.$TS" && echo "   backed up -> $S.bak.$TS"
python3 -c "import json,pathlib;k=json.load(open(str(pathlib.Path.home())+'/.cline/data/secrets.json'))['openAiApiKey'];print('   old: len=',len(k),'prefix6=',k[:6])"

echo; echo "=== 2. 从 .12 取有效 key 并写入（管道传递，不回显明文）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 \
  'python3 -c "import json,pathlib;print(json.load(open(str(pathlib.Path.home())+\"/.cline/data/secrets.json\"))[\"openAiApiKey\"])"' \
  | tr -d '\r\n' | python3 -c "import json,sys,os;k=sys.stdin.read().strip();\
assert len(k)>32,'ABORT: fetched key too short -> nothing written';json.dump({'openAiApiKey':k},open(os.path.expanduser('~/.cline/data/secrets.json'),'w'));print('   new: len=',len(k),'prefix6=',k[:6])" \
  || { echo "!!! 写入失败 → 中止"; echo DONE; exit 0; }

echo; echo "=== 3. 用【新 secrets、不带 -k】跑 cline smoke（仿 .12 环境）==="
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
  timeout 90 "$C" -c /tmp -m "$M" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -4 | cut -c1-150

echo; echo "=== 4. 取最新 loop 脚本（只 checkout 这两个文件）==="
git -C "$WK" fetch origin --quiet 2>/dev/null
git -C "$WK" checkout origin/main -- doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh && echo "   checked out"
grep -n 'OPENAI_API_KEY' "$RUN/baize_pretrain_loop.sh" "$RUN/baize_harness_loop.sh" | cut -c1-110

echo; echo "=== 5. 停旧 loop ==="
ps -eo pid=,etimes=,args= 2>/dev/null | grep -E 'baize_(pretrain|harness)_loop\.sh' | grep -v grep | cut -c1-105
pkill -f 'baize_pretrain_loop.sh'; pkill -f 'baize_harness_loop.sh'; sleep 5
pgrep -af 'baize_(pretrain|harness)_loop\.sh' | cut -c1-105 || echo "   已全部停止"

echo; echo "=== 6. 重启（无 proxy / 无 stale OPENAI_*）==="
cd "$RUN"
setsid env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
  bash baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
sleep 2
setsid env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
  bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
sleep 28

echo; echo "=== 7. 校验 ==="
pgrep -af 'baize_(pretrain|harness)_loop\.sh' | cut -c1-130
echo "-- pretrain log --"; tail -6 /tmp/baize_pretrain_loop.log | cut -c1-150
echo "-- harness log --";  tail -6 /tmp/baize_harness_loop.log  | cut -c1-150
echo "-- Forbidden 计数（新日志，应为 0）--"; grep -c Forbidden /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log 2>/dev/null

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 14**（key 对钥匙，**✅ 已执行 07:26:10**）为 ```text。

## RUN_ID 14 — 🎯 **钥匙对钥匙：3 个 key 分别 curl + 用 `.12` 的 key 跑 smoke**（✅ 已执行，本块不再运行）

**RUN_ID 13 决定性证据（2026-10-04 07:23）**：
- 🔴 **`curl /v1/chat/completions`（带 `$OPENAI_API_KEY`）→ `http=403`**（`/v1/models` 200，但该端点不校验）
- 🔴 `.29` cline `-k $OPENAI_API_KEY` → 仍 `Forbidden`
- ⏱ **时间线吻合**：harness 在 **10-03 22:12** 用 `-k $OPENAI_API_KEY` 的 smoke **成功** → 说明**该 key 在当时有效，22:12 之后被轮换/吊销**
- 📌 `.29` `globalState.json` 正常：`openAiBaseUrl=http://agi-gateway.cxmt.com/v1`、`planModeOpenAiModelId=deepseek-v4-pro-fp4`

**本块 = 一锤定音**：把 ①`.29` env key ②`.29` secrets key ③**`.12` 的 secrets key** 三个分别打网关；
再用 **`.12` 的 key** 跑 cline smoke（不改任何文件）。若第 ③ 个能过 → **修法 = 把 `.29` 的 cline 指向有效 key**。

🚫 **纯只读**：不写文件 / 不 kill / 不重启。
> ⚠️ **严禁打印 key 明文** —— 只打 `len` 和 `prefix6`。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T %Z'
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; GW=http://agi-gateway.cxmt.com/v1; cd /tmp

echo; echo "=== 1. 取三个 key（只显示 len + prefix6）==="
K12=$(timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'python3 -c "import json,pathlib;print(json.load(open(str(pathlib.Path.home())+\"/.cline/data/secrets.json\"))[\"openAiApiKey\"])"' 2>/dev/null | tr -d '\r\n')
K29S=$(python3 -c "import json,pathlib;print(json.load(open(str(pathlib.Path.home())+'/.cline/data/secrets.json'))['openAiApiKey'])" 2>/dev/null | tr -d '\r\n')
K29E="${OPENAI_API_KEY:-}"
for kv in ".12 secrets:$K12" ".29 secrets:$K29S" ".29 env:$K29E"; do
  n="${kv%%:*}"; k="${kv#*:}"
  printf '   %-12s len=%-4s prefix6=%s\n' "$n" "${#k}" "${k:0:6}"
done
echo "   .29 secrets == .12 secrets ?  $([ "$K29S" = "$K12" ] && echo YES || echo NO)"

echo; echo "=== 2. 三个 key 分别打 chat/completions ==="
for kv in "env:$K29E" "sec29:$K29S" "sec12:$K12"; do
  n="${kv%%:*}"; k="${kv#*:}"
  code=$(timeout 20 curl -s -o /tmp/_cc.json -w '%{http_code}' -H "Authorization: Bearer $k" -H 'Content-Type: application/json' \
    -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"hi"}],"max_tokens":3}' "$GW/chat/completions")
  printf '   %-7s -> %s   ' "$n" "$code"; head -c 120 /tmp/_cc.json | tr -d '\n'; echo
done

echo; echo "=== 3. 用【.12 的 key】跑 cline smoke（仿 .12 环境）==="
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
  timeout 90 "$C" -c /tmp -m "$M" -k "$K12" --auto-approve true -t 45 "reply with exactly OK" 2>&1 | head -6 | cut -c1-170

echo; echo "=== 4. [.12] globalState 对照（修正版）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'python3 -c "import json,pathlib;d=json.load(open(str(pathlib.Path.home())+\"/.cline/data/globalState.json\"));[print(\"   \",k,\"=\",repr(d.get(k))) for k in (\"actModeApiProvider\",\"planModeApiProvider\",\"actModeOpenAiModelId\",\"planModeOpenAiModelId\",\"openAiBaseUrl\")]"' 2>&1 | cut -c1-180

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 13**（globalState 对照，**✅ 已执行 07:23:51**）为 ```text。

## RUN_ID 13 — 🎯 **对 `.29` vs `.12` 的 `globalState.json` 字段 + 直连网关验证**（✅ 已执行，本块不再运行）

**RUN_ID 12 结论（2026-10-04 07:21）—— 已排除的假设**：
- ❌ **不是 proxy**（`env -u *_PROXY` 仍 Forbidden；虽然 `via-proxy -> 503` / `no-proxy -> 200`）
- ❌ **不是 `OPENAI_API_URL`/`API_TYPE`/`OPENAI_API_KEY`**（"完全模仿 .12"的 NO_ALL 变体仍 Forbidden）
- ✅ `-k` 确为 API key（`-k, --key <api-key>`）
- 🔑 **两个 host 的 `secrets.json` 都是 96 B、同一个 key**；但 **`globalState.json` 不同**：
  `.29` = 2765 B / **mtime 2026-09-29 19:31**（被人改过）vs `.12` = 3122 B / **2026-09-08 11:26**
- 🎯 **本块要判定**：`.29` 的 **`openAiBaseUrl` / `actModeApiProvider` / `actModeOpenAiModelId`** 是否被改坏（→ 这个假设能解释"为什么 unset 环境变量没用"）

🚫 **纯只读** —— 不 kill / 不重启 / **不改文件**；
> ⚠️ **严禁打印任何 key 明文**（RUN_ID 11 已泄一次：`OPENAI_API_KEY` 明文进了 outbox，**请尽快轮换**）。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T %Z'
C=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; cd /tmp

echo; echo "=== 1. [.29] globalState.json 关键字段（无 key）==="
python3 -c "import json,pathlib;d=json.load(open(pathlib.Path.home()/'.cline/data/globalState.json'));[print('   ',k,'=',repr(d.get(k))) for k in ('actModeApiProvider','planModeApiProvider','actModeOpenAiModelId','planModeOpenAiModelId','openAiBaseUrl')]" 2>&1 | cut -c1-180

echo; echo "=== 2. [.12] 同样字段（对照）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'echo "   HOME=$HOME"; hostname; python3 -c "import json,pathlib;d=json.load(open(pathlib.Path.home()+\"/.cline/data/globalState.json\"));[print(\"   \",k,\"=\",repr(d.get(k))) for k in (\"actModeApiProvider\",\"planModeApiProvider\",\"actModeOpenAiModelId\",\"planModeOpenAiModelId\",\"openAiBaseUrl\")]"' 2>&1 | cut -c1-180 || echo "ssh .12 FAILED"

echo; echo "=== 3. [.29] cline 是否支持显式 base-url / 其它 key 参数 ==="
"$C" --help 2>&1 | grep -inE 'base|url|key|provider' | head -12 | cut -c1-150

echo; echo "=== 4. [.29] 直连网关：models（带 key）==="
timeout 20 curl -s -o /tmp/_m2.json -w '   models  http=%{http_code}\n' -H "Authorization: Bearer $OPENAI_API_KEY" http://agi-gateway.cxmt.com/v1/models; head -c 300 /tmp/_m2.json; echo

echo; echo "=== 5. [.29] 直连网关：chat/completions（关键！）==="
timeout 30 curl -s -o /tmp/_c.json -w '   chat    http=%{http_code}\n' -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' http://agi-gateway.cxmt.com/v1/chat/completions; head -c 300 /tmp/_c.json; echo

echo; echo "=== 6. [.29] 用 -k 显式传 key 再 smoke 一次（对照 RUN_ID 10 的结论）==="
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
  timeout 90 "$C" -c /tmp -m "$M" -k "$OPENAI_API_KEY" --auto-approve true -t 45 "reply OK" 2>&1 | head -5 | cut -c1-170

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 12**（env 矩阵，**✅ 已执行 07:21:35**）为 ```text。

## RUN_ID 12 — 🎯 **env 矩阵 smoke：找出让 cline 变绿的组合**（✅ 已执行，本块不再运行）

**RUN_ID 11 结论（2026-10-04 07:18）**：
- ✅ **`no-proxy -> 200`** vs **`via-proxy -> 503`** → **代理确实打不通内网网关**（但只去 proxy **没修好** cline，仍 Forbidden）
- 🔑 **`.12` 的差异 = 它的(非交互)环境里【没有 proxy、也没有 `OPENAI_*`/`API_TYPE`】** → cline 走自己的 secrets/config 就能用
- ❌ `.29` 有：`OPENAI_API_KEY=01_549…` · `API_TYPE=openai` · `OPENAI_API_URL=http://agi-gateway.cxmt.com/v1` · `https_proxy=…`
- 📌 **所以本块要判定**：是 `OPENAI_API_URL`/`API_TYPE` 让 cline 选错 provider，还是别的（本矩阵会直接给出答案）

🚫 **纯只读** —— 不 kill / 不重启 / 不写文件；只在 `/tmp` 做 smoke。
> ⚠️ **请务必不要打印任何 key 明文**（RUN_ID 11 的脱敏 sed 失效了，`OPENAI_API_KEY` 已被明文写入 `outbox.md`）。

```text
echo "=== 0. HOST/TIME ==="; hostname; date '+%F %T %Z'
CLINE=/home/app.e0031982/.bun/bin/cline; M=deepseek-v4-pro-fp4; T='reply with exactly OK'; cd /tmp
"$CLINE" --version 2>&1 | head -2

echo; echo "=== 1. cline 的 -k 到底是什么 ==="
"$CLINE" --help 2>&1 | grep -inE -- '-k|api.?key' | head -8 | cut -c1-150

echo; echo "=== 2. ~/.cline/data 清单（只看文件名/mtime，不打印内容）==="
ls -la ~/.cline/data/ 2>/dev/null | cut -c1-130

echo; echo "=== 3. 🔬 smoke 矩阵（每条 head -4，只看是否 Forbidden）==="
try() { L="$1"; shift; printf '%-14s => ' "$L"; env "$@" timeout 90 "$CLINE" -c /tmp -m "$M" --auto-approve true -t 45 "$T" 2>&1 | head -4 | tr '\n' ' ' | cut -c1-165; echo; }
try "ALL"            
try "NO_PROXY"       -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY
try "NO_OPENAI"      -u OPENAI_API_URL -u API_TYPE
try "NO_BOTH"        -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_URL -u API_TYPE
try "NO_ALL(仿.12)"  -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u OPENAI_API_URL -u API_TYPE -u OPENAI_API_KEY

echo; echo "=== 4. 若上面全 Forbidden → 看 cline 自己的 provider 配置文件名 ==="
for f in ~/.cline/data/settings.json ~/.cline/data/globalState.json ~/.cline/data/secrets.json; do
  [ -f "$f" ] && { printf '%s : %s bytes, mtime %s\n' "$f" "$(stat -c%s "$f")" "$(stat -c%y "$f" | cut -c1-19)"; python3 -c "import json,sys;d=json.load(open('$f'));print('   keys:',[k for k in d][:14])" 2>/dev/null; }
done

echo; echo "=== 5. 对照 .12：它的 ~/.cline/data 清单 ==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'ls -la ~/.cline/data/ 2>/dev/null | cut -c1-130; echo "-- whoami/host --"; hostname' 2>&1 | cut -c1-140 || echo "ssh .12 FAILED"

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 11**（proxy 验证，**✅ 已执行 07:18:00**）为 ```text。

## RUN_ID 11 — 🎯 **验证 `Forbidden` 是否由 `https_proxy` 引起**（✅ 已执行，本块不再运行）

**RUN_ID 10 已排除的假设（2026-10-04 07:15）**：
- ❌ **不是 key**：`.29` smoke **带 `-k $OPENAI_API_KEY` 依然 `Forbidden`**；且 `.12` 的 secrets key 与之**完全相同**（`02_088…len72`）
- ❌ **不是模型名**：`.12` 用的是**同一个** `MODEL="deepseek-v4-pro-fp4"`，却工作正常
- ✅ **`.29` 独有的一张牌 = `https_proxy`（len25, `http://1…`）**，而网关是**内网** `OPENAI_API_URL=http://a…`（len30）
- 📌 Forbidden 计数：pretrain 日志 **18** 次、harness 日志 **37** 次；`.29` 最后一次正常 cline 是 **10-03 22:12**（harness smoke 成功）

**本块要判定的**：`.29` 的 cline 是否把**内网网关**的请求也塞进了外网代理 → 网关 `Forbidden`。
**第 4 节 = 直接试修法**（`env -u *_PROXY` 后再 smoke）；若通过 → 修法 = **以不带 proxy 的环境重启两条 loop**。

🚫 **纯只读** —— 不 kill / 不重启 / 不写文件（只在 `/tmp` 做 smoke）。

```text
echo "=== 0. HOST / TIME / CLINE VERSION ==="; hostname; date '+%F %T %Z'
CLINE=/home/app.e0031982/.bun/bin/cline
"$CLINE" --version 2>&1 | head -3

echo; echo "=== 1. [.29] proxy / openai 相关 env（key 已脱敏）==="
env | grep -iE 'proxy|openai|api_type' | sed 's/\(key=[^ ]\{0,8\}\)[^ ]*/\1.../' | cut -c1-160

echo; echo "=== 2. [.12] 同一组 env + cline 版本（对照）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'echo "-- cline --"; /home/app.e0031982/.bun/bin/cline --version 2>&1 | head -2; echo "-- env --"; env | grep -iE "proxy|openai|api_type" | sed "s/\(key=[^ ]\{0,8\}\)[^ ]*/\1.../" | cut -c1-160' 2>&1 | cut -c1-170 || echo "ssh .12 FAILED"

echo; echo "=== 3. [.29] cline smoke 完整错误（head 40，找 'Interesting:' 真解释）==="
cd /tmp && timeout 120 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 --auto-approve true -t 60 "reply with exactly OK" 2>&1 | head -40 | cut -c1-190

echo; echo "=== 4. [.29] ⭐ smoke【剥掉全部 proxy 环境变量】—— 期待变绿 ==="
cd /tmp && env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY -u all_proxy -u ALL_PROXY -u no_proxy -u NO_PROXY \
  timeout 120 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 --auto-approve true -t 60 "reply with exactly OK" 2>&1 | head -20 | cut -c1-190

echo; echo "=== 5. [.29] 链路对照：直连 vs 走代理 ==="
timeout 20 curl -s -o /dev/null -w 'no-proxy  -> %{http_code}\n' "${OPENAI_API_URL:-http://agi-gateway.cxmt.com/v1}/models" 2>&1
timeout 20 curl -s -o /dev/null -w 'via-proxy -> %{http_code}\n' -x "${https_proxy:-${http_proxy}}" "${OPENAI_API_URL:-http://agi-gateway.cxmt.com/v1}/models" 2>&1
echo "-- no_proxy 当前值: [${no_proxy:-<empty>}] --"

echo; echo "=== 6. 首个 Forbidden 的上下文（含时间戳）==="
grep -n -B4 -A1 'Forbidden' /tmp/baize_pretrain_loop.log 2>/dev/null | head -24 | cut -c1-175

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 10**（Forbidden 根因探查，**✅ 已执行 07:15:37 exit=0**）为 ```text。

## RUN_ID 10 — 🔍 **定位 `Forbidden` 根因**（✅ 已执行，本块不再运行）

**RUN_ID 9 已定位（2026-10-04 07:13）**：
- ✅ 两条 `.29` loop **进程都活着**（`baize_pretrain_loop.sh` / `baize_harness_loop.sh`）
- ✅ **P-5b 已于 10-04 01:37 跑完**（`successfully saved checkpoint from iteration 4771`）→ **8 卡全空闲（0% / 0 MiB）已 ~5.6h**
- 🔴 **根因候选**：`/tmp/baize_*_loop.log` 每个 30min 周期都是 **`error: Forbidden`**，而 **`cline returned (exit 0)`** → loop 分辨不出失败 → **静默空转 ~9h**。**不是 token 额度，是 `Forbidden`（鉴权 / 模型名 / 网关）**
- ✅ `.12` 正常（vision/data loop 活着且干活）→ **问题只在 `.29`**

**本块目标**：判定 `Forbidden` 属于哪一种，并验证 `-k $OPENAI_API_KEY` 能否修好：
① **key 不对**（`~/.cline/data/secrets.json` 里的 stale key）② **模型名不对**（`MODEL=` 变量已失效）③ **网关/base-url 不对**（cline 没用内网网关）。

🚫 **纯只读** —— 不 kill / 不重启 / **不写任何文件**；smoke 测试只往 `/tmp` 落地（可接受）。

```text
echo "=== 0. HOST / TIME / CLINE ==="; hostname; date '+%F %T %Z'
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
CLINE=$(command -v cline 2>/dev/null || echo "$HOME/.bun/bin/cline"); echo "CLINE=$CLINE"

echo; echo "=== 1. 两条 loop 的 cline 调用行 + 关键变量 ==="
for f in baize_pretrain_loop.sh baize_harness_loop.sh; do
  echo "-- $f"; grep -nE 'cline |^MODEL=|^CLINE_TIMEOUT=|^SLEEP_|^PUSH_' "$RUN/$f" 2>/dev/null | cut -c1-190
done

echo; echo "=== 2. Forbidden 时间线（总数 / 首次 / 最近）+ 最后一次正常周期 ==="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log; do
  echo "-- $f : Forbidden 总数=$(grep -c 'Forbidden' "$f" 2>/dev/null)"
  grep -n 'Forbidden' "$f" 2>/dev/null | head -1 | cut -c1-120
done
grep -nE 'Forbidden|wake up|push OK|nothing to commit' /tmp/baize_pretrain_loop.log 2>/dev/null | tail -14 | cut -c1-130

echo; echo "=== 3. secrets.json（脱敏）==="
python3 -c "import json,pathlib;p=pathlib.Path.home()/'.cline/data/secrets.json';print('exists',p.exists(),'mtime',__import__('datetime').datetime.fromtimestamp(p.stat().st_mtime).isoformat() if p.exists() else '');d=json.loads(p.read_text()) if p.exists() else {};[print(' ',k,'=',(str(v)[:6]+'...len'+str(len(str(v)))) if any(t in k.lower() for t in ('key','token','secret')) else v) for k,v in d.items()]" 2>&1 | cut -c1-200

echo; echo "=== 4. 环境变量凭据（脱敏：只看名字/length/前 8 位）==="
python3 -c "import os;[print(' ',k,'len',len(v),'prefix',v[:8]) for k,v in sorted(os.environ.items()) if any(t in k.upper() for t in ('KEY','TOKEN','API','PROXY'))]" 2>&1 | cut -c1-160

echo; echo "=== 5. cline smoke ——【不带 -k】（复现 loop 的失败）==="
cd /tmp && timeout 150 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 --auto-approve true -t 60 "reply with exactly OK" 2>&1 | tail -6 | cut -c1-170

echo; echo "=== 6. cline smoke ——【带 -k \$OPENAI_API_KEY】==="
cd /tmp && timeout 150 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 -k "$OPENAI_API_KEY" --auto-approve true -t 60 "reply with exactly OK" 2>&1 | tail -6 | cut -c1-170

echo; echo "=== 7. 对照：.12 用的是哪个 MODEL（为什么它没 Forbidden）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'grep -nE "^MODEL=|cline " /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_vision_loop.sh | cut -c1-190; echo "-- .12 secrets --"; python3 -c "import json,pathlib;p=pathlib.Path.home()/\".cline/data/secrets.json\";d=json.loads(p.read_text()) if p.exists() else {};[print(k,len(str(v)),str(v)[:6]) for k,v in d.items() if \"key\" in k.lower()]"' 2>&1 | cut -c1-170 || echo "ssh .12 FAILED"

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 9**（`.29` 静默探查，**✅ 已执行 07:13:17 exit=0**）为 ```text —— 它不再霸占「第一个块」。

## RUN_ID 9 — 🔍 **只读探查：`.29` 的 pretrain / harness 为何静默 ~9 小时**（✅ 已执行，本块不再运行）

**背景**：`MEMORY_PRETRAIN_2B.md` 最后更新停在 **10-03 22:05**（第 54 次巡检，P-5b **90.97%**，final ETA 10-04 ~01:36）；`MEMORY_HARNESS.md` 停在 **10-03 22:43**。
**10-04 全天只有 vision / data 在写文件**（07:06 仍在写）→ 而 pretrain/harness **零文件变更**。
**怀疑**：**pretrain/vision/data/harness 四条线共用同一 cline key** → vision+data 整夜抢占 → **pretrain/harness 被 Token 额度饿死**（已知坑：cline 额度耗尽**仍返回 `exit 0`**，loop 分辨不出，只睡 30min 再试 = **静默变慢而非崩溃**）。
**要回答的 4 个问题**：① loop 进程还在不在？② 日志里有没有「额度已用完」？③ **P-5b 到底跑完没有 / GPU 是否在空转**？④ `.12` 侧是否正常（做对照）。

**约束**：🚫 **纯只读** —— 不 kill / 不重启 / 不 `rm` / 不改任何文件；长输出 `cut -c1-140`；**不整树 `du`**。

```text
echo "=== 0. HOST / TIME ==="; hostname; date '+%F %T %Z'

echo; echo "=== 1. [.29] LOOPS ==="
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"

echo; echo "=== 2. [.29] LOOP LOGS (tail 18 + Token额度 命中数) ==="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log; do
  echo "-- $f  mtime=$(stat -c %y "$f" 2>/dev/null | cut -c1-19)  size=$(stat -c %s "$f" 2>/dev/null)"
  printf '   Token额度相关行数 = '; grep -c '额度\|quota\|Token\|Forbidden' "$f" 2>/dev/null || echo 0
  tail -n 18 "$f" 2>/dev/null | cut -c1-160
  echo
done

echo "=== 3. [.29] /tmp 最近改动的日志（判断最后一次唤醒时间）==="
ls -lt --time-style=long-iso /tmp/*.log 2>/dev/null | head -12

echo; echo "=== 4. [.29] 训练进程 + GPU（P-5b 是否还在跑）==="
pgrep -af 'pretrain_launcher|torchrun|p5b' | cut -c1-140 | head -10 || echo "(NO torchrun => 训练已结束)"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null || echo "(nvidia-smi failed)"
echo "-- /tmp/baize_p5b.log tail 10 --"; tail -n 10 /tmp/baize_p5b.log 2>/dev/null | cut -c1-160 || echo "(no p5b log)"

echo; echo "=== 5. [.29] P-5b ckpt（看 final @4771 是否落盘）==="
CK=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments
ls -1 "$CK" 2>/dev/null | head -15
for d in "$CK"/p5b "$CK"/p5b_*; do [ -d "$d" ] && { echo "-- $d"; ls -1t "$d" 2>/dev/null | head -8; }; done
echo "-- 含 4771 的路径 --"; find "$CK" -maxdepth 2 -name '*4771*' 2>/dev/null | head -5

echo; echo "=== 6. [.12] 远端（ssh）loops + GPU —— 做对照 ==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'hostname; echo "-- loops --"; pgrep -af "baize_.*_loop\.sh" | cut -c1-140; echo "-- gpu --"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader' 2>&1 | cut -c1-160 || echo "ssh 10.239.2.12 FAILED"

echo; echo "=== 7. 共享工作副本 git 状态 ==="
git -C /nas_train/app.e0031982/code/super_intelligence_2035 log --oneline -3 2>/dev/null
git -C /nas_train/app.e0031982/code/super_intelligence_2035 status -sb 2>/dev/null | head -6

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 8**（清 relay 副本）为 ```text —— 它现在**不再**霸占「第一个块」。

## RUN_ID 8 — 🧹 **清 ops_relay 重复副本**（⚠️ **已被 RUN_ID 9 接管，本块不再执行**）

**背景**：`.29` 上又见 **2 个 `ops_relay.sh`**（`2489749` etimes≈42.8h + `2315903` etimes≈0）。
**目标**：只保留「运行最久」的那个；**若清理有任何不确定，就不杀、只报告**。
**底线**：**执行完必须仍有 ≥1 个 relay 存活**（否则假期无法通讯）。

```text
echo "=========== 0. 时间 ==========="
hostname; date '+%F %T %Z'
echo

echo "=========== 1. 现有 relay 清单（pid / ppid / etimes） ==========="
ps -eo pid=,ppid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-150
echo

echo "=========== 2. 定位【执行本命令的】relay（沿祖先进程回溯） ==========="
SELF=""
p=$$
for i in 1 2 3 4 5 6 7 8 9 10; do
  [ -z "$p" ] && break; [ "$p" = "0" ] && break; [ "$p" = "1" ] && break
  c=$(ps -o args= -p "$p" 2>/dev/null)
  case "$c" in *ops_relay.sh*) SELF="$p"; break;; esac
  p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
done
echo "SELF = ${SELF:-<not found>}"

echo "=========== 3. KEEP = 运行最久者（etimes 最大） ==========="
KEEP=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | sort -k2 -nr | awk 'NR==1{print $1}')
echo "KEEP = ${KEEP:-<none>}"

echo "=========== 4. 清理（**只杀** 既非 KEEP 也非 SELF 的副本） ==========="
COUNT=$(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | wc -l)
echo "relay count before = $COUNT"
if [ -z "$KEEP" ]; then
  echo "!!! 未找到任何 relay → 不杀任何进程（fail-safe）"
elif [ "$COUNT" -le 1 ]; then
  echo "只有 1 个 → 无需清理"
else
  for pid in $(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | awk '{print $1}'); do
    if [ "$pid" = "$KEEP" ]; then echo "keep   pid=$pid (longest-running)"; continue; fi
    if [ -n "$SELF" ] && [ "$pid" = "$SELF" ]; then echo "keep   pid=$pid (=== SELF，延后处理)"; continue; fi
    echo "kill   pid=$pid (duplicate)"
    kill -TERM "$pid" 2>/dev/null
  done
fi
sleep 3

echo "=========== 5. 若 SELF 是副本 → **延后 90s 自行退出**（先让 outbox 写完并 push） ==========="
if [ -n "$SELF" ] && [ "$SELF" != "$KEEP" ]; then
  echo "SELF=$SELF ≠ KEEP=$KEEP → 本进程为副本，90s 后自行退出（setsid 脱离，保证 outbox 先落地）"
  setsid sh -c "sleep 90; kill -TERM $SELF" >/dev/null 2>&1 < /dev/null &
else
  echo "SELF == KEEP（或未定位）→ 无需自退"
fi

echo "=========== 6. 收尾核对（**必须 ≥1 存活**） ==========="
sleep 2
REMAIN=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-150)
echo "$REMAIN"
n=$(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | wc -l)
echo "relay count after = $n"
if [ "$n" -ge 1 ]; then echo "OK: 至少 1 个存活（通讯可用）"; else echo "!!! 警告：0 个存活 —— 需人工重启 relay（勿删本目录）"; fi
echo
echo "=========== DONE ==========="
```

---

## RUN_ID 7（**已被 RUN_ID 8 接管，本块不再执行**）— 只读诊断

**背景（运维 2026-10-03 10:57）**：`09:00` 之后**没有 agent 的提交**（只有运维自己的），而各线 `WAITING=1` 预期约每 50 分钟一轮。
→ 疑因：某线 cline 会话较长（data 可能在 `rm -rf` 8.1T）、或 `git pull --rebase` 撞上运维的密集推送而跳过 push 周期。
**本块只读，不改任何东西、不 kill 任何进程。**

```text
echo "=========== 0. 时间（host / date） ==========="
hostname; date '+%F %T %Z'
echo

echo "=========== 1. loop / relay 进程（预期 4 loop + 1 relay） ==========="
ps -eo pid=,etimes=,stat=,args= 2>/dev/null | grep -E 'baize_.*_loop\.sh|ops_relay\.sh' | grep -v grep | cut -c1-150
echo

echo "=========== 2. 共享工作副本：未提交 / 未推送 / 最近提交 ==========="
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null || { echo "REPO MISSING"; exit 0; }
git status -sb 2>&1 | head -25
echo "-- 最近 6 条本地提交 --"
git --no-pager log --oneline -6 2>&1 | cut -c1-120
echo "-- 与远端 leading/behind（L=ahead R=behind，fetch 由 relay 自己做过） --"
git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "(no origin/main ref)"
echo

echo "=========== 3. 各 loop 日志尾部（是否在跑 / 报错） ==========="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_vision_loop.log /tmp/baize_data_loop.log /tmp/baize_harness_loop.log; do
  if [ -f "$f" ]; then
    printf '== %s (mtime %s)\n' "$f" "$(date -r "$f" '+%F %T' 2>/dev/null)"
    tail -4 "$f" | cut -c1-160
  else
    printf '== %s : (no log)\n' "$f"
  fi
done
echo "-- ops relay 日志 --"
tail -6 /tmp/ops_relay.log 2>/dev/null | cut -c1-160 || echo "(no /tmp/ops_relay.log)"
echo

echo "=========== 4. GPU 占用（谁在跑） ==========="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | cut -c1-60 || echo "(no nvidia-smi)"
echo

echo "=========== 5. 关键训练日志 ==========="
for f in /tmp/r10_denseM.log /tmp/baize_p5b_train.log; do
  [ -f "$f" ] && { printf '== %s (mtime %s)\n' "$f" "$(date -r "$f" '+%F %T')"; tail -3 "$f" | cut -c1-160; }
done
echo "-- R10③ 是否 DONE（预期 0→1） --"
grep -c 'denseM ALL DONE' /tmp/r10_denseM.log 2>/dev/null || echo 0
echo

echo "=========== 6. 磁盘 + GPIC / laion2B ==========="
df -hT /nas_train 2>/dev/null | tail -1
echo "-- gpic train tar 数（预期 ≥1131/8000） --"
ls -1 /nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar 2>/dev/null | wc -l
echo "-- laion2B-en-aesthetic 是否已删 --"
if [ -d /nas_train/app.e0031982/datasets/laion2B-en-aesthetic ]; then echo "STILL EXISTS"; else echo "GONE (deleted)"; fi
echo

echo "=========== DONE ==========="
```

---

## RUN_ID 6（**已被 RUN_ID 7 接管，本块不再执行**）— 清重复 relay + 勘查既有 harness 研究线

**目标**：① 清掉重复的 `ops_relay.sh`；② **只读**勘查 `/nas_train/app.e0031982/harness/` 里那条**既有的** harness 研究线（运维指示：**可以合并**）。

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 当前 relay / loop 进程 ==========="
pgrep -af 'ops_relay.sh|baize_.*_loop\.sh' | cut -c1-140
echo

echo "=========== 2. 清重复的 ops_relay.sh（保留【启动最早】的那个） ==========="
echo "⚠️ 用 etimes(已运行秒数) 排序取最早，不用 PID 数字 —— PID 会回绕，数字小不代表更早"
echo "   证据：两次独立观测（RUN_ID 2 与 5）都看到【2 个】relay，其中 2489749 跨两次存活，"
echo "         另一个从 1276654 变成 2228582 → 2489749 是更早/更稳的那个。"
ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-140
KEEP=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | sort -k2 -nr | awk 'NR==1{print $1}')
RELAYS=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | awk '{print $1}')
echo "keep (longest-running) = $KEEP ; all = $(echo $RELAYS | tr '\n' ' ')"
for p in $RELAYS; do
  if [ "$p" != "$KEEP" ]; then
    echo "killing duplicate relay pid=$p"
    kill "$p" 2>/dev/null
  fi
done
sleep 3
echo "-- after（预期只剩 1 个） --"
ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 勘查【既有】harness 研究线（只读，不改动） ==========="
H=/nas_train/app.e0031982/harness
echo "-- 顶层（含日期，用于确认它早于我们） --"
ls -la "$H" 2>/dev/null | cut -c1-140
echo
echo "-- 它的 loop.sh 是否在跑？ --"
pgrep -af 'harness/loop.sh' | cut -c1-140 || echo "(NOT running)"
echo
echo "-- MEMORY.md 顶部 25 行 --"
head -25 "$H/MEMORY.md" 2>/dev/null | cut -c1-170 || echo "(no MEMORY.md)"
echo
echo "-- analyze_harness_sources.md 的章节标题 --"
grep -nE '^#{1,3} ' "$H/analyze_harness_sources.md" 2>/dev/null | head -25 | cut -c1-150 || echo "(none)"
echo
echo "-- report.html 的 title/h1/h2（看它覆盖了什么） --"
grep -oE '<(title|h1|h2)[^>]*>[^<]{0,90}' "$H/report.html" 2>/dev/null | head -18 || echo "(none)"
echo
echo "-- evidence/ --"
ls -la "$H/evidence" 2>/dev/null | head -15 | cut -c1-140
echo "-- mechanisms/ --"
ls -la "$H/mechanisms" 2>/dev/null | head -15 | cut -c1-140
echo
echo "-- daily-memories/ 最近 5 个 --"
ls -1t "$H/daily-memories" 2>/dev/null | head -5
echo

echo "=========== 4. 5 个 harness 的形态（目录 + README 首 3 行） ==========="
for d in cline opencode deepseek-harness codex claude-code; do
  if [ -d "$H/$d" ]; then
    echo "---- $d ----"
    ls "$H/$d" 2>/dev/null | head -14 | tr '\n' ' '; echo
    head -3 "$H/$d/README.md" 2>/dev/null | cut -c1-150
    echo
  else
    echo "---- $d : MISSING ----"
  fi
done

echo "=========== DONE ==========="
```

---

## RUN_ID 5 — 启动 harness 线（✅ **已执行 2026-10-02 22:20, exit=0**）

> ✅ **已生效**：`baize_harness_loop.sh` 已启动（pid 2228938），agent 已接单并读到任务书。
> ⚠️ 围栏已降级为 ```text，**避免霸占"第一个块"**（本文件太长，只认第一个是 relay 的既有行为）。

**目标**：起 `baize_harness_loop.sh`（H-A: SWE-bench 横评 / H-B: harness 源码分析），并校验它接单。

**背景**：运维新建了第 4 条线 ——
任务书 `BAIZE_HARNESS_TASK.md`、loop `baize_harness_loop.sh`、状态 `MEMORY_HARNESS.md`、
产物 `harness/`、日志 `daily-memories-harness/`。**已在 `AGENTS.md` 登记。**

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 前置校验（任务书 / loop / 状态文件） ==========="
for f in BAIZE_HARNESS_TASK.md baize_harness_loop.sh MEMORY_HARNESS.md; do
  if [ -f "$f" ]; then printf '%-28s : OK (%s bytes)\n' "$f" "$(stat -c%s "$f")"; else printf '%-28s : MISSING !!!\n' "$f"; fi
done
echo
echo "-- H-B 的分析对象：harness 源码目录 --"
ls -la /nas_train/app.e0031982/harness/ 2>/dev/null | head -30 || echo "MISSING: /nas_train/app.e0031982/harness/"
echo

echo "=========== 2. 资源摸底（harness 线跑在本机，先看余量 + Docker） ==========="
echo "-- CPU / 内存 --"
nproc; free -g | head -2
echo "-- 磁盘 --"
df -h /nas_train /tmp 2>/dev/null
echo "-- Docker（H-A 的 SWE-bench 评测依赖它） --"
docker info >/dev/null 2>&1 && echo "docker: AVAILABLE" || echo "docker: NOT AVAILABLE (H-A 会因此受阻，如实上报)"
echo "-- 本机已有 loop（预期 3 个：vision/pretrain/data） --"
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 查重（避免起两个） ==========="
if pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  echo "ALREADY RUNNING - skip launch:"
  pgrep -af 'baize_harness_loop.sh' | cut -c1-140
else
  echo "(not running yet — will launch)"
fi
echo

echo "=========== 4. 启动（脱离进程组，防工具超时误杀） ==========="
if ! pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  chmod +x baize_harness_loop.sh
  touch MEMORY_HARNESS.md
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 8
  echo "launched."
else
  echo "skip (already running)."
fi
echo

echo "=========== 5. 验证（应恰好 1 个进程 + 日志出现 [loop] 行） ==========="
pgrep -af 'baize_harness_loop.sh' | cut -c1-140 || echo "!!! NOT RUNNING — 需排查 /tmp/baize_harness_loop.log"
echo "-- log tail --"
tail -8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-160 || echo "(no log yet)"
echo

echo "=========== 6. 全量 loop 一览（预期 4 个） ==========="
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' | cut -c1-140
echo

echo "=========== DONE ==========="
```

---

## RUN_ID 3 — 磁盘空间与占用分布（**已执行，归档**）

> ⚠️ **本块已从 ```bash 降级为 ```text** —— 因为中继**只认第一个 ```bash 块**，
> 留着会让它每次都把这条勘察重跑一遍（实测踩过：RUN_ID 3→4 时中继又跑了这条）。

**目标**：确认 `df -h` 实况；定位 `/nas_train` 175 TB 被什么占用；核对数据准备所需空间与剩余空间。

```text
echo "=========== DF -H (ALL MOUNTS) ==========="
df -h
echo
echo "=========== DF -H (NAS + ROOT, explicit) ==========="
df -h /nas_train /nas_inference /nas_user /nas_env / 2>/dev/null
echo
echo "=========== DF -I (INODES — large-corpus trap) ==========="
df -i /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== TARGETED DU (bounded, timeout 150s each) ==========="
for d in \
  /nas_train/app.e0031982/datasets/baize-vision \
  /nas_train/app.e0031982/datasets/baize-data \
  /nas_train/app.e0031982/datasets/mvp-lab \
  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data \
  /nas_train/app.e0031982/models \
  /nas_inference/app.e0031982/datasets/openbmb ; do
  if [ -e "$d" ]; then
    printf '%-58s : ' "$d"
    timeout 150 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout/fail)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== TOP-LEVEL LISTING (no du, just names) ==========="
echo "-- /nas_train/app.e0031982 --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null | head -40
echo "-- /nas_user/app.e0031982/datasets --"
ls -1 /nas_user/app.e0031982/datasets 2>/dev/null | head -40
echo
echo "=========== BAZE-VISION DETAIL (stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
timeout 60 du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== ANY IN-PROGRESS DOWNLOAD? ==========="
ps -eo pid=,etime=,comm=,args= 2>/dev/null | grep -E 'wget|curl|hf_transfer|datasets|nohup' | grep -v grep | cut -c1-140 | head -10 || echo "(none)"
echo "-- nohup.out tail (if a download is logging) --"
for f in /nas_inference/app.e0031982/datasets/nohup.out /nas_train/app.e0031982/datasets/nohup.out; do
  [ -f "$f" ] && { echo "== $f"; tail -5 "$f" | cut -c1-140; }
done
echo
echo "=========== DONE ==========="
```

---

## RUN_ID 4 — **启动 harness 线**（⛔ **已作废：当时并未生效**）

> ⛔ **本块从未被执行** —— 因为中继只认文件里**第一个** ```bash 块，而它在 RUN_ID 3 的块之后。
> **已由 RUN_ID 5 接管**（见文件最前面）。本块仅作归档，围栏已降级为 ```text。

**目标**：起 `baize_harness_loop.sh`（H-A: SWE-bench 横评 / H-B: harness 源码分析），并校验它接单。

**背景**：运维新建了第 4 条线 ——
任务书 `BAIZE_HARNESS_TASK.md`、loop `baize_harness_loop.sh`、状态 `MEMORY_HARNESS.md`、
产物 `harness/`、日志 `daily-memories-harness/`。**已在 `AGENTS.md` 登记。**

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 前置校验（任务书 / loop / 状态文件） ==========="
for f in BAIZE_HARNESS_TASK.md baize_harness_loop.sh MEMORY_HARNESS.md; do
  if [ -f "$f" ]; then printf '%-28s : OK (%s bytes)\n' "$f" "$(stat -c%s "$f")"; else printf '%-28s : MISSING !!!\n' "$f"; fi
done
echo
echo "-- H-B 的分析对象：harness 源码目录 --"
ls -la /nas_train/app.e0031982/harness/ 2>/dev/null | head -30 || echo "MISSING: /nas_train/app.e0031982/harness/"
echo

echo "=========== 2. 资源摸底（harness 线跑在本机，先看余量 + Docker） ==========="
echo "-- CPU / 内存 --"
nproc; free -g | head -2
echo "-- 磁盘 --"
df -h /nas_train /tmp 2>/dev/null
echo "-- Docker（H-A 的 SWE-bench 评测依赖它） --"
docker info >/dev/null 2>&1 && echo "docker: AVAILABLE" || echo "docker: NOT AVAILABLE (H-A 会因此受阻，如实上报)"
echo "-- 本机已有 loop（预期 3 个：vision/pretrain/data） --"
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 查重（避免起两个） ==========="
if pgrep -af 'baize_harness_loop.sh' | grep -v grep >/dev/null 2>&1; then
  echo "ALREADY RUNNING - skip launch:"
  pgrep -af 'baize_harness_loop.sh' | cut -c1-140
else
  echo "(not running yet — will launch)"
fi
echo

echo "=========== 4. 启动（脱离进程组，防工具超时误杀） ==========="
if ! pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  chmod +x baize_harness_loop.sh
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 8
  echo "launched."
else
  echo "skip (already running)."
fi
echo

echo "=========== 5. 验证（应恰好 1 个进程 + 日志出现 [loop] 行） ==========="
pgrep -af 'baize_harness_loop.sh' | cut -c1-140 || echo "!!! NOT RUNNING — 需排查 /tmp/baize_harness_loop.log"
echo "-- log tail --"
tail -8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-160 || echo "(no log yet)"
echo

echo "=========== 6. 全量 loop 一览（预期 4 个） ==========="
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' | cut -c1-140
echo

echo "=========== DONE ==========="
```
