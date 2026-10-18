#!/usr/bin/env python3
# news 线临时诊断：挖出 i=2（评论输入组件 Oe）的 state hook 与 props.onSubmit 形状
import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

JS = r"""
(() => {
  const ta = document.querySelector('.comment-textarea');
  const key = Object.keys(ta).find((k) => k.startsWith('__reactInternalInstance$'));
  let f = ta[key];
  for (let i = 0; i < 2 && f; i++) f = f.return;
  const name = (f.type && (f.type.displayName || f.type.name)) || String(f.type).slice(0, 30);
  const hooks = [];
  let h = f.memoizedState;
  for (let i = 0; i < 10 && h; i++) {
    const v = h.memoizedState;
    let s;
    if (v === null) s = 'null';
    else if (typeof v === 'function') s = 'fn:' + String(v).slice(0, 80);
    else if (typeof v === 'object' && v && 'current' in v) s = 'ref:' + String(v.current && v.current.className).slice(0, 40);
    else s = typeof v === 'object' ? 'obj:' + Object.keys(v).slice(0, 8).join(',') : String(v).slice(0, 80);
    hooks.push({i, v: s});
    h = h.next;
  }
  const p = f.memoizedProps || {};
  return JSON.stringify({ name, hooks, onSubmitType: typeof p.onSubmit, onSubmitLen: p.onSubmit ? String(p.onSubmit).length : 0, props: Object.keys(p) });
})()
"""

ws = cdp.session(sys.argv[1])
try:
    r = ws.call("Runtime.evaluate", {"expression": JS, "returnByValue": True})
    print(json.dumps(r, ensure_ascii=False)[:1500])
finally:
    ws.close()
