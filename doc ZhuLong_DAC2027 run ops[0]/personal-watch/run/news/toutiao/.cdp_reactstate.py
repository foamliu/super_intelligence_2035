#!/usr/bin/env python3
# news 线临时诊断：从 React fiber 里挖出评论框的 state/props（找出提交函数到底在哪）
# 用法: python3 news/toutiao/.cdp_reactstate.py <targetId>
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

JS = r"""
(() => {
  const ta = document.querySelector('.comment-textarea');
  if (!ta) return 'no textarea';
  const key = Object.keys(ta).find((k) => k.startsWith('__reactInternalInstance$'));
  if (!key) return 'no fiber key: ' + Object.keys(ta).join(',');
  let f = ta[key];
  const out = [];
  for (let i = 0; i < 12 && f; i++) {
    const p = f.memoizedProps || {};
    const s = f.memoizedState;
    out.push({
      i,
      type: typeof f.type === 'string' ? f.type : (f.type && (f.type.displayName || f.type.name)) || String(f.type),
      propKeys: Object.keys(p).slice(0, 25),
      hasSubmit: Object.keys(p).filter((k) => /submit|send|post|comment/i.test(k)),
      stateKind: s && typeof s === 'object' ? Object.keys(s).slice(0, 12) : typeof s,
    });
    f = f.return;
  }
  return JSON.stringify(out);
})()
"""

tid = sys.argv[1]
ws = cdp.session(tid)
try:
    r = ws.call("Runtime.evaluate", {"expression": JS, "returnByValue": True})
    print(r.get("result", {}).get("value"))
finally:
    ws.close()
