#!/usr/bin/env python3
"""微头条正文写入（稳定路径）：经 React fiber 取包装组件的 stateNode.editor（ProseMirror Editor），
用 Schema 重建段落后 view.dispatch —— 绕开「键盘事件被编辑器吞掉 / 只落单段」的坑。

背景（2026-10-23 第 132 轮实测）：
  · 本页 ProseMirror 用 `syl-placeholder` widget，Enter 键事件（rawKeyDown/char/keyUp 各种组合）
    均**不产生新段落**；逐字 keyDown 也被吞；仅 `Input.insertText` 能落字但**不换段**。
  · 包装组件 props.getEditor 是「全局登记器」，不是 EditorView 取用口 ⇒ view 从 `stateNode.editor.view` 取。
  · getEditor(editor) 返回**类 thenable 对象**，`JSON.parse` 会抛 TypeError ⇒ 判据走 `window.__fillRes`。

用法: fill_pm.py <tabId> <paras.json>
判据: docParas / domParas / 逐段长度 / 总字数 / domOk+contentOk 与输入 JSON 完全一致。
"""
import sys, time, json
sys.path.insert(0, 'news/fanqie')
import cdp

JS = r"""(()=>{
  const paras = window.__paras;
  if(!Array.isArray(paras)||!paras.length) return 'NO_PARAS';
  const root=document.querySelector('div.syl-editor')||document.querySelector('div.ProseMirror');
  if(!root) return 'NO_EDITOR';
  const key=Object.keys(root).find(k=>k.startsWith('__reactInternalInstance'));
  if(!key) return 'NO_FIBER';
  let f=root[key], editor=null, get_=null;
  while(f){
    const sn=f.stateNode;
    if(sn && typeof sn==='object' && !sn.nodeType && sn.editor && sn.editor.view && sn.editor.view.state) editor=sn.editor;
    const mp=f.memoizedProps;
    if(!get_ && mp && typeof mp.getEditor==='function' && String(mp.getEditor).indexOf('domParser')>=0) get_=mp.getEditor;
    if(editor) break;
    f=f.return;
  }
  if(!editor) return 'NO_EDITOR_OBJ';
  const view=editor.view;
  // 视图本身含循环引用 + 类 thenable（序列化会抛），且会污染后续 evaluate ⇒ 不挂到 window
  // 注意：包装组件的 getEditor(editor) 在本页返回类 thenable，写进 window 后任何序列化都会抛 ⇒ 不调用
  const schema=view.state.schema;
  const nodes=paras.map(t=>schema.nodes.paragraph.create(null, t?schema.text(t):null));
  const doc=schema.nodes.doc.create(null, nodes);
  const tr=view.state.tr.replaceWith(0, view.state.doc.content.size, doc.content);
  try { view.dispatch(tr); } catch(e){ view.updateState(view.state.apply(tr)); }
  try { view.focus(); } catch(e){}
  const ps=[...document.querySelectorAll('div.ProseMirror > p')].map(p=>p.innerText);
  const domOk = ps.length===paras.length && ps.every((x,i)=>x===paras[i]);
  const contentOk = view.state.doc.textContent===paras.join('');
  window.__fillRes = {docParas:view.state.doc.childCount, domParas:ps.length, lens:ps.map(x=>x.length),
                      total:ps.join('').length, domOk, contentOk};
  return 'DONE';
})()"""


def fill(tid, paras, settle=0.6):
    ws = cdp.session(tid)
    try:
        expr = ('window.__fillRes=null;window.__paras=' + json.dumps(paras, ensure_ascii=False) + ';' +
                JS + ';1')
        r = ws.call('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': False})
        if r.get('exceptionDetails'):
            return {'error': json.dumps(r['exceptionDetails'], ensure_ascii=False)[:500]}
        time.sleep(settle)
        r2 = ws.call('Runtime.evaluate', {'expression': 'JSON.stringify(window.__fillRes)',
                                          'returnByValue': True})
    finally:
        ws.close()
    v = (r2.get('result') or {}).get('value')
    return json.loads(v) if v else {'error': 'no __fillRes'}


def check(res, paras):
    want = {'domParas': len(paras), 'total': sum(len(p) for p in paras)}
    ok = bool(res) and not res.get('error') and res.get('domOk') and res.get('contentOk') \
        and res.get('domParas') == want['domParas'] and res.get('total') == want['total'] \
        and res.get('docParas') == want['domParas']
    return ok, want


if __name__ == '__main__':
    tid, path = sys.argv[1], sys.argv[2]
    paras = json.load(open(path, encoding='utf-8'))
    res = fill(tid, paras)
    ok, want = check(res, paras)
    print('FILL', json.dumps(res, ensure_ascii=False))
    print('WANT', want)
    print('OK' if ok else 'FAIL')
    sys.exit(0 if ok else 1)
