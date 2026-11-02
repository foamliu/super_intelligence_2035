# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 141 -->
## RUN_ID 141 — 在 36.15 找「Tab-3 美观改进」中文 HTML；找到且未入库 ⇒ 直接 commit+push 入库

> 用户令 2026-11-02：「ZhuLong_DAC2027 目录下有个 Tab-3 美观改进中文 HTML，有的话提交入库，并按此执行」。本块负责"定位 + 入库"；按 HTML 改 Tab-3 由 agent 下轮按 `ZHULONG_TASK.md` 新运维令执行。

```bash
set -u
echo "=== RUN_ID 141 | locate+commit Tab-3 beautify html | $(date '+%F %T') | host=$(hostname) ==="
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo /nasdata/app.e0031982/code/super_intelligence_2035)" || exit 1
echo "  repo=$(pwd)  HEAD=$(git rev-parse --short HEAD)"

echo
echo "[1] doc/ZhuLong_DAC2027 顶层 html"
timeout 20 ls -lh --time-style='+%F %T' doc/ZhuLong_DAC2027/*.html 2>/dev/null | awk '{print "    "$6,$7,$5,$8}' || echo "    (none)"

echo
echo "[2] 名字含 tab 的 html/htm（maxdepth 3）"
timeout 25 find doc/ZhuLong_DAC2027 -maxdepth 3 \( -iname '*tab*' -a \( -name '*.html' -o -name '*.htm' \) \) -printf '%TY-%Tm-%Td %TH:%TM %8s %p\n' 2>/dev/null | sed 's/^/    /' || true

echo
echo "[3] git status（zhulong 树，只看 html/htm；? = 未跟踪）"
timeout 20 git status --porcelain -- doc/ZhuLong_DAC2027 2>/dev/null | grep -iE '\.html?$' | head -10 | sed 's/^/    /' || echo "    (无 html 变更)"

echo
echo "[4] 全部 html 里命中「美观/Tab-3/表 3/改进」的（最多 10 条）"
for f in $(timeout 25 find doc/ZhuLong_DAC2027 -maxdepth 3 -name '*.html' 2>/dev/null | head -60); do
  if timeout 5 grep -qiE '美观|Tab-?3|表 ?3|改进建议|排版' "$f" 2>/dev/null; then
    echo "    HIT $f ($(stat -c %s "$f")B)"
  fi
done

echo
echo "[5] 选定候选 → 打印结构 → 入库（commit+push）"
CAND=$(timeout 25 find doc/ZhuLong_DAC2027 -maxdepth 3 \( -iname '*tab*' -a \( -name '*.html' -o -name '*.htm' \) \) 2>/dev/null | head -1)
if [ -z "${CAND:-}" ]; then
  echo "    ❌ 未找到文件名含 tab 的 html —— 不做任何提交"
else
  echo "    candidate = $CAND  ($(stat -c %s "$CAND")B)"
  echo "    title: $(grep -oiE '<title>[^<]*' "$CAND" 2>/dev/null | head -1 | sed 's/<title>//I')"
  echo "    headings: $(grep -cE '<h[1-4]' "$CAND" 2>/dev/null)"
  grep -oE '<h[1-4][^>]*>[^<]{2,80}' "$CAND" 2>/dev/null | sed -E 's/<h[1-4][^>]*>//' | head -12 | sed 's/^/      - /'
  if git ls-files --error-unmatch "$CAND" >/dev/null 2>&1; then
    echo "    已在库内（tracked），无需提交"
  else
    git add -- "$CAND"
    git -c user.email=ops@local -c user.name=ops commit -m "zhulong paper: 入库 Tab-3 美观改进建议 HTML（用户令 2026-11-02）" -m "file: $CAND" >/dev/null 2>&1 || echo "    commit 失败/无变更"
    timeout 60 git push origin main 2>&1 | tail -2 | sed 's/^/    /'
    echo "    after: $(git log -1 --pretty='%h %s' | cut -c1-100)"
  fi
fi

echo
echo "[6] 确认该文件现在是否被跟踪"
timeout 10 git ls-files doc/ZhuLong_DAC2027 2>/dev/null | grep -iE '\.html?$' | head -8 | sed 's/^/    tracked: /'

echo "=== DONE 141 ==="
```
