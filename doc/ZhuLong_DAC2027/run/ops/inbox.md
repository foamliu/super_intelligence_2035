# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 144 -->

## RUN_ID 144 — 协助 post-train 从 36.15 启动 PyAether 评测（serve minicpm5-2b + 隧道 + 起跑）

> **用户令 2026-11-14**：post-train 的 `EDA-Eval-PyAether-v20260311_fixed.jsonl` 评测
> **不应在 .17 本地启动**（那样没有 RAG、没有沙盒 MCP，测出来不是真实分数）。
> 必须像 zhulong 一样**从 36.15 启动**。本块负责把链路打通并起跑。
> 只做 zhulong 熟悉的动作；不改 post-train 的评测代码/判据。

```bash
set -u
echo "=== RUN_ID 144 | post-train eval bootstrap on 36.15 | $(date '+%F %T') | host=$(hostname) ==="
echo "  预期本机 = 10.251.36.15（若 hostname 不符请停止并报告）"
hostname -I 2>/dev/null | sed 's/^/  local IPs: /'

BASE_DIR=/nasdata/app.e0031982/code/eda_fastmcp
GR=$(git rev-parse --show-toplevel 2>/dev/null || echo /nasdata/app.e0031982/code/super_intelligence_2035)
cd "$GR" || exit 1
git pull --rebase --autostash origin main >/dev/null 2>&1 || true

echo
echo "[1] 既有基础设施现状（RAG / 沙盒 MCP / GPU）"
echo "  --- RAG 服务（9006）---"
(curl -s -o /dev/null -w '  RAG:9006 http=%{http_code}\n' --max-time 5 http://127.0.0.1:9006/ ) 2>/dev/null || echo "  RAG:9006 不可达"
echo "  --- 沙盒 MCP（18891）---"
(curl -s -o /dev/null -w '  MCP:18891 http=%{http_code}\n' --max-time 5 http://127.0.0.1:18891/mcp ) 2>/dev/null || echo "  MCP:18891 不可达"
echo "  --- 沙盒端口 8650-8654 ---"
for p in 8650 8651 8652 8654; do
  if (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null; then echo "  $p OPEN"; exec 3<&- 3>&-; else echo "  $p CLOSED"; fi
done
echo "  --- GPU（36.15 是否有卡可 serve 2B）---"
nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null | sed 's/^/  /' || echo "  无 nvidia-smi"

echo
echo "[2] 是否已有 minicpm5-2b serve 在跑"
ps -eo pid,etime,args 2>/dev/null | grep -iE 'vllm|sglang|api_server' | grep -v grep | cut -c1-170 | head -8 || echo "  (无 serve 进程)"

echo
echo "[3] .17 隧道现状（post-train 在 .17，需要把模型调用打通）"
echo "  --- 现有隧道/端口转发 ---"
ps -eo pid,etime,args 2>/dev/null | grep -E 'ssh .*-[LR]|ssh -[LR]|autossh' | grep -v grep | cut -c1-170 | head -10 || echo "  (无 ssh 隧道)"
echo "  --- 到 .17 的连通性 ---"
ping -c 1 -W 2 10.252.32.17 >/dev/null 2>&1 && echo "  10.252.32.17 ping OK" || echo "  10.252.32.17 ping FAIL"

echo
echo "[4] post-train 的 SFT ckpt（用于 serve）"
ls -dt /nasdata/app.e0031982/*/sft* /nasdata/app.e0031982/**/global_step_105 2>/dev/null | head -6 | sed 's/^/  /' || echo "  (未找到 sft ckpt 目录，请人工确认路径)"
find /nasdata/app.e0031982 -maxdepth 4 -type d -name 'global_step_*' 2>/dev/null | head -8 | sed 's/^/  /'

echo
echo "[5] zhulong 自己的评测启动方式（供 post-train 复用）"
echo "  BASE_DIR=$BASE_DIR"
ls -la "$BASE_DIR" 2>/dev/null | head -12 | sed 's/^/  /' || echo "  BASE_DIR 不存在"
echo "  --- eda_fastmcp 里的启动脚本 ---"
find "$BASE_DIR" -maxdepth 2 -name '*.sh' 2>/dev/null | head -12 | sed 's/^/  /'
echo "  --- 环境变量口径（RAG/沙盒）---"
grep -rhoE 'RAG_RECALL_URL=[^ ]*|PROXY_PORTS=[^ ]*|SANDBOX_ENDPOINTS=[^ ]*' "$BASE_DIR" 2>/dev/null | sort -u | head -10 | sed 's/^/  /'

echo
echo "[6] 结论与待办（人工据此决定下一步）"
echo "  请据 [1]-[5] 判断:"
echo "   a) RAG(9006) 与 MCP(18891) 是否就绪 — 不就绪则先拉起"
echo "   b) 36.15 GPU 是否可 serve minicpm5-2b — 决定 serve 命令与端口"
echo "   c) .17 -> 36.15 的隧道方向 — post-train 在 .17 调用 36.15 的模型端点"
echo "   d) post-train 侧需要改的是 BASE_URL（指向隧道），不改评测代码"

echo
echo "=== DONE 144 ==="
```


## RUN_ID 143 — zhulong 状态体检（只读）：loop / cline / smoke / 沙盒端口 / git

> 目的：确认 wake#922 之后 zhulong 是否真的在推进 confirmatory smoke。
> 只读，不改任何文件、不起跑、不 kill。

```bash
set -u
echo "=== RUN_ID 143 | zhulong status probe | $(date '+%F %T') | host=$(hostname) ==="
GR=$(git rev-parse --show-toplevel 2>/dev/null || echo /nasdata/app.e0031982/code/super_intelligence_2035)
cd "$GR" || exit 1

echo
echo "[1] zhulong loop 进程"
ps -eo pid,etime,args 2>/dev/null | grep -E 'zhulong_loop\.sh' | grep -v grep | cut -c1-160 || echo "  (无 zhulong_loop)"

echo
echo "[2] cline 进程（是否有 agent 在跑）"
ps -eo pid,etime,pcpu,args 2>/dev/null | grep -E '[c]line ' | grep -v grep | cut -c1-160 | head -10 || echo "  (无 cline)"

echo
echo "[3] 沙盒端口 status（8664/8665/8653/8669）"
for p in 8664 8665 8653 8669; do
  if (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null; then echo "  $p OPEN"; exec 3<&- 3>&-; else echo "  $p CLOSED"; fi
done

echo
echo "[4] 最近的 smoke / subagent 目录（/tmp 与 /nasdata）"
ls -dt /tmp/subagent_smoke* /tmp/*subagent* 2>/dev/null | head -8 || echo "  (无 /tmp subagent 目录)"
ls -dt /nasdata/*/subagent_ablation* /nasdata/*/*subagent* 2>/dev/null | head -8 || echo "  (无 /nasdata subagent 目录)"

echo
echo "[5] 最新 smoke 目录里的关键证据（若有）"
SD=$(ls -dt /tmp/subagent_smoke* 2>/dev/null | head -1)
if [ -n "${SD:-}" ]; then
  echo "  dir=$SD"
  find "$SD" -name '*messages.json' 2>/dev/null | head -3 | while read -r f; do
    echo "    $f  n_msgs=$(python3 -c "import json,sys
try:
  d=json.load(open('$f'));print(len(d) if isinstance(d,list) else len(d.get('messages',[])))
except Exception as e: print('ERR')" 2>/dev/null)"
  done
  grep -m3 -iE 'finishReason|inputTokens|outputTokens' "$SD"/*.log 2>/dev/null | cut -c1-160 | sed 's/^/    /'
else
  echo "  (无 /tmp/subagent_smoke* 目录)"
fi

echo
echo "[6] MEMORY_ZHULONG 头部（WAITING / PHASE）"
head -6 doc/ZhuLong_DAC2027/run/MEMORY_ZHULONG.md 2>/dev/null | cut -c1-200 | sed 's/^/  /'

echo
echo "[7] git 状态（应干净）"
git status --porcelain 2>/dev/null | head -10 | sed 's/^/  /' || true
echo "  HEAD=$(git log -1 --pretty='%h %s' | cut -c1-90)"
echo "  behind/ahead vs origin/main: $(git rev-list --left-right --count origin/main...HEAD 2>/dev/null)"

echo
echo "[8] loop 日志尾部（若存在）"
for f in /tmp/zhulong_loop.log /tmp/zl_loop.log; do
  [ -f "$f" ] && { echo "  --- $f (mtime $(date -r "$f" '+%F %T' 2>/dev/null)) ---"; tail -12 "$f" | cut -c1-170 | sed 's/^/    /'; }
done

echo "=== DONE 143 ==="
```

## RUN_ID 142 — 匿名化后重编译 main.pdf + 验证「PDF 里确实看不到作者/邮箱」+ 提交 main.pdf

> 用户令 2026-11-02：「关于 P0 双盲，可以改成匿名」。main.tex 已由运维改为 `[anonymous, sigconf]`（commit `699b17580`，且 18 人网格宏在 anonymous 下跳过）。本块负责**权威编译 + 匿名性实测 + 入库 main.pdf**。

```bash
set -u
echo "=== RUN_ID 142 | anonymous rebuild+verify | $(date '+%F %T') | host=$(hostname) ==="
GR=$(git rev-parse --show-toplevel 2>/dev/null || echo /nasdata/app.e0031982/code/super_intelligence_2035)
cd "$GR" || exit 1
git pull --rebase --autostash origin main >/dev/null 2>&1 || true
P="$GR/doc/ZhuLong_DAC2027/ZhuLong_DAC2027"
cd "$P" || { echo "paper dir 不存在"; exit 1; }

echo "  paper HEAD=$(git rev-parse --short HEAD)"
echo "[0] main.tex 第 1-3 行（应为 anonymous）"
timeout 5 head -3 main.tex | sed 's/^/    /'

echo
echo "[1] 删旧 aux/out 后跑 pdflatex + bibtex（干净构建）"
rm -f main.aux main.out main.toc
timeout 300 pdflatex -interaction=nonstopmode main.tex > /tmp/zl_b1.log 2>&1; echo "    pass1 exit=$?"
timeout 120 bibtex main > /tmp/zl_bib.log 2>&1; echo "    bibtex exit=$?"
timeout 300 pdflatex -interaction=nonstopmode main.tex > /tmp/zl_b2.log 2>&1; echo "    pass2 exit=$?"
timeout 300 pdflatex -interaction=nonstopmode main.tex > /tmp/zl_b3.log 2>&1; echo "    pass3 exit=$?"

echo
echo "[2] 编译健康度"
echo "    errors(^!): $(grep -c '^!' main.log 2>/dev/null || echo 0)"
echo "    undefined:  $(grep -ci 'undefined' main.log 2>/dev/null || echo 0)"
echo "    overfull:   $(grep -c 'Overfull' main.log 2>/dev/null || echo 0)"
grep 'Output written' main.log 2>/dev/null | sed 's/^/    /'
echo "    bibtex warnings: $(grep -c 'Warning' /tmp/zl_bib.log 2>/dev/null || echo 0)"

echo
echo "[3] 匿名性实测（PDF 取文本，查作者/邮箱是否泄漏）"
if command -v mutool >/dev/null 2>&1; then
  timeout 60 mutool draw -F txt -o /tmp/zl_main.txt main.pdf 2>/dev/null
  echo "    mutool pages: $(mutool info main.pdf 2>/dev/null | grep -m1 -i 'Pages')"
else
  echo "    mutool 不可用，改用 pdftotext"
  timeout 60 pdftotext main.pdf /tmp/zl_main.txt 2>/dev/null || echo "    两种工具都不可用"
fi
if [ -s /tmp/zl_main.txt ]; then
  echo "    Anonymous 命中: $(grep -ci 'anonymous' /tmp/zl_main.txt)"
  echo "    泄漏检查（应为 0 行）:"
  grep -inE 'Hongwen|Yiming Zhu|Yang Liu|cxmt|paul\.liu|ChangXin' /tmp/zl_main.txt | head -8 | sed 's/^/      LEAK: /'
  echo "    首页作者区（前 12 行含 Author 的）:"
  grep -inE 'author|anonymous' /tmp/zl_main.txt | head -6 | cut -c1-140 | sed 's/^/      /'
else
  echo "    ⚠️ 无法取文本，请人工看 PDF 首页"
fi

echo
echo "[4] 入库 main.pdf（若与上次不同）"
git add -- main.pdf main.tex 2>/dev/null
if git diff --cached --quiet; then
  echo "    无变化，不提交"
else
  git -c user.email=ops@local -c user.name=ops commit -m "zhulong paper: rebuild main.pdf (anonymous / double-blind)" -m "pages=$(grep -m1 'Output written' main.log | sed 's/.*(\([0-9]*\) pages.*/\1/')" >/dev/null 2>&1
  timeout 60 git push origin main 2>&1 | tail -2 | sed 's/^/    /'
  echo "    after: $(git log -1 --pretty='%h %s' | cut -c1-90)"
fi

echo "=== DONE 142 ==="
```
