#!/bin/bash
# recruit/check_pii.sh — 入库前「值级」PII / 凭据自检
#
# 背景：2026-10-11 supervisor 拍板「**接受姓名级入库**」（见 recruit/README.md「数据边界」）。
#   姓名/学校/期望/分级/沟通摘要是**允许**入库的；本脚本只查**绝不允许**的
#   **值级**凭据与直接标识符（cookie 值 / securityId·geekId 值 / 手机号 / 邮箱 / 身份证 / 私钥 / Basic 认证）。
#   ⇒ 只匹配「赋值形态」与「强特征」，**不会**命中规则文本里的字段名（如「不许写 securityId」）。
#
# 用法：
#   bash recruit/check_pii.sh                              # 扫本目录（recruit/）
#   bash recruit/check_pii.sh recruit/hr                   # 扫指定路径
#   bash recruit/check_pii.sh $(git diff --cached --name-only)   # 只扫已暂存文件（推荐做 pre-commit）
# 退出码：0 = 未命中；1 = 命中（**请人工复核后再提交**）
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -gt 0 ]; then TARGETS=("$@"); else TARGETS=("$DIR"); fi

# 只匹配「值级」形态（避免误伤规则文本）
PATTERNS=(
  "(wt2|wbg|zp_at|bst)['\"]?[[:space:]]*[=:][[:space:]]*['\"]?[A-Za-z0-9%_/+.-]{20,}"
  "(securityId|geekId)['\"]?[[:space:]]*[=:][[:space:]]*['\"]?[A-Za-z0-9_-]{12,}"
  "(^|[^0-9])1[3-9][0-9]{9}([^0-9]|$)"
  "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}"
  "[0-9]{17}[0-9Xx]"
  "-----BEGIN [A-Z ]*PRIVATE KEY-----"
  "Basic [A-Za-z0-9+/]{20,}={0,2}"
)

# 已知良性（git remote / 文档里的示例域）—— 排除，避免误报
EXCLUDE='(git@|@github[.]|@gitlab[.]|ssh://|https://[^ ]*@|noreply@)'

total=0
for p in "${PATTERNS[@]}"; do
  out="$(grep -rInE --exclude-dir=.git --exclude='check_pii.sh' --exclude='README.md' \
            -e "$p" "${TARGETS[@]}" 2>/dev/null | grep -vE "$EXCLUDE" || true)"
  n="$(printf '%s' "$out" | grep -c . || true)"
  if [ "${n:-0}" -gt 0 ]; then
    total=$((total + n))
    echo "🚫 命中 [$p] × $n —— 仅列位置（**不打印内容**，防二次泄露）："
    printf '%s\n' "$out" | head -8 | sed -E 's/^([^:]*:[0-9]+):.*$/\1/' | sed 's/^/    /'
  fi
done

if [ "$total" -gt 0 ]; then
  echo "==> ❌ 共命中 $total 处值级 PII/凭据：请人工复核；确认无凭据后再提交。"
  exit 1
fi
echo "==> ✅ 未命中值级 PII/凭据（姓名级数据不在此列，属允许入库）。"
exit 0
