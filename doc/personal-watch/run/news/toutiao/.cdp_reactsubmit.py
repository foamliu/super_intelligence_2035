#!/usr/bin/env python3
# news 线临时工具：直接调用评论组件 React props.onSubmit(值) 提交评论
# 为什么存在（2026-10-18 实测）：先 Input.insertText 写入（React 已感知、state=46 字），
# 但此后 Input.dispatchKeyEvent 打不出字、合成 InputEvent 不触发 handler ⇒ submit-btn 永远 .disable；
# 组件 Oe 的 props.onSubmit 才是真正提交通道（内部再走 onSubmitComment）。
# 成功判据：① 输入框清空 ② 评论列表顶部出现本号评论 ③ 评论数 +1
# ⚠️ 2026-10-18 实测补充（必读）
# ① `Input.insertText` 回显 inserted N 之后，React **可能已抢先提交**（输入框清空 + 评论数 +1）；
#    ⇒ 调用本脚本前**必须先读** `.comment-textarea` 的 innerText 长度（>0 才提交），否则会把同一句发两遍。
# ② 评论框被 React 卸载后，ref 指向脱离文档的旧节点 ⇒ insertText「报成功但不落字」；
#    此时换一个未用过的标签页重开该帖（cdp.py goto <tid> <url>），比原地修补快。
# ③ 判据只认 reload 后的 `.ttp-comment-item` / body.innerText，页面乐观预览不可信。
# 用法: python3 news/toutiao/.cdp_reactsubmit.py <targetId>
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

JS = r"""
(async () => {
  const ta = document.querySelector('.comment-textarea');
  if (!ta) return 'no textarea';
  const before = (document.querySelector('button.submit-btn') || {}).className;
  const text = (ta.innerText || '').trim();
  if (!text) return 'empty';
  const key = Object.keys(ta).find((k) => k.startsWith('__reactInternalInstance$'));
  let f = ta[key];
  for (let i = 0; i < 2 && f; i++) f = f.return;
  if (!f || !f.memoizedProps || typeof f.memoizedProps.onSubmit !== 'function') return 'no onSubmit';
  let res;
  try {
    res = await f.memoizedProps.onSubmit(text);
  } catch (e) {
    return JSON.stringify({ err: String(e && e.message) });
  }
  await new Promise((r) => setTimeout(r, 2500));
  const first = [...document.querySelectorAll('.ttp-comment-item')].slice(0, 2).map((n) => n.innerText.replace(/\s+/g, ' ').slice(0, 60));
  return JSON.stringify({ text, before, res: String(res), left: (document.querySelector('.comment-textarea').innerText || '').trim().length, first });
})()
"""

ws = cdp.session(sys.argv[1])
try:
    r = ws.call("Runtime.evaluate", {"expression": JS, "awaitPromise": True, "returnByValue": True}, timeout=60)
    print(json.dumps(r.get("result", {}), ensure_ascii=False)[:1200])
finally:
    ws.close()
