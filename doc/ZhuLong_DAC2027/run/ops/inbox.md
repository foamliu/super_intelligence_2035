# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 142 -->
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
