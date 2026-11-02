# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 239 | TARGET: 29 -->
## RUN_ID 239 — 更正：zhulong agent 在 **36.15** 这台机器上（不在 .29/.12）；本块只探测 .29 能否直达该机

> 用户更正：zhulong 的 work copy 在 36.15，Tab-3 HTML 应在那边。故本块不再扫本机，只测连通性（只读）。

```bash
set -u
echo "=== RUN_ID 239 | reachability to zhulong host 36.15 | $(date '+%F %T') | host=$(hostname) ==="

echo
echo "[1] 解析/连通性候选（10.239.36.15 / 172.19.36.15 / 36.15）"
for h in 10.239.36.15 172.19.36.15 36.15; do
  ip=$(getent hosts "$h" 2>/dev/null | awk '{print $1}' | head -1)
  echo "    $h -> ${ip:-未解析}"
  if [ -n "$ip" ]; then
    timeout 3 bash -c "echo > /dev/tcp/$ip/22" 2>/dev/null && echo "      TCP:22 OPEN" || echo "      TCP:22 closed/timeout"
    timeout 6 ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=4 "$ip" 'echo "      ssh OK host=$(hostname)"' 2>&1 | head -2 | sed 's/^/      /'
  fi
done

echo
echo "[2] 本机 .29 的 zhulong 工作副本（对照：应当没有那个 HTML）"
R=/nas_train/app.e0031982/code/super_intelligence_2035
cd "$R" 2>/dev/null && {
  timeout 15 find doc/ZhuLong_DAC2027 -maxdepth 2 \( -iname '*tab*' -a \( -name '*.html' -o -name '*.htm' \) \) 2>/dev/null | head -5 | sed 's/^/    /'
  echo "    .29 顶层 html 数=$(ls -1 doc/ZhuLong_DAC2027/*.html 2>/dev/null | wc -l)"
} || echo "    repo 不存在"

echo "=== DONE 239 ==="
```
