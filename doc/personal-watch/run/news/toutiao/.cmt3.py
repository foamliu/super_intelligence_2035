#!/usr/bin/env python3
# .cmt3.py <tabId> <url> <text> — 引流评论（2026-10-22 18:0x 实测口径：comment-textarea 在文章页底部，先 scrollIntoView 再校验 activeElement）
import json, sys, time
sys.path.insert(0, '/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/fanqie')
import cdp
tid, url, text = sys.argv[1], sys.argv[2], sys.argv[3]
assert len(text) <= 40, len(text)
ws = cdp.session(tid)
def ev(e):
    r = ws.call('Runtime.evaluate', {'expression': e, 'returnByValue': True, 'awaitPromise': True})['result']
    return r.get('value')
def click(x, y):
    for k in ('mouseMoved', 'mousePressed', 'mouseReleased'):
        p = {'type': k, 'x': x, 'y': y}
        if k != 'mouseMoved': p.update(button='left', clickCount=1)
        ws.call('Input.dispatchMouseEvent', p); time.sleep(0.12)
BOX = "(()=>{const b=document.querySelector('div.comment-textarea');b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),h:Math.round(r.height)})})()"
STATE = "(()=>{const t=document.querySelector('div.comment-textarea');const b=[...document.querySelectorAll('button.submit-btn')].filter(x=>x.offsetParent)[0];if(!t||!b)return null;const r=b.getBoundingClientRect();const c=document.body.innerText.match(/评论 (\\d+)/);return JSON.stringify({len:t.innerText.length,cls:b.className,bx:Math.round(r.x+r.width/2),by:Math.round(r.y+r.height/2),cnt:c?c[1]:null})})()"
try:
    ws.call('Emulation.setFocusEmulationEnabled', {'enabled': True})
    ws.call('Page.enable')
    if ev('location.href').rstrip('/') != url.rstrip('/'):
        ws.call('Page.navigate', {'url': url}); time.sleep(9)
    ev('window.focus(); 1')
    time.sleep(0.6)
    box = json.loads(ev(BOX)); time.sleep(0.8)
    foc = ''
    for dy in (0, -3, 3):
        click(box['x'], box['y'] + dy); time.sleep(0.7)
        foc = ev("document.activeElement.tagName+'.'+String(document.activeElement.className).slice(0,25)")
        if 'comment-textarea' in foc: break
        box = json.loads(ev(BOX)); time.sleep(0.5)
    print('FOCUS', foc, 'BOX', box, flush=True)
    if 'comment-textarea' not in foc:
        print('ABORT_NO_FOCUS'); sys.exit(3)
    for ch in text:
        ws.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'text': ch, 'unmodifiedText': ch, 'key': ch})
        ws.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': ch})
        time.sleep(0.03)
    time.sleep(0.6)
    st = json.loads(ev(STATE)); print('TYPED', st, flush=True)
    if st['len'] != len(text) or 'disable' in st['cls']:
        print('ABORT_NOT_READY'); sys.exit(2)
    click(st['bx'], st['by']); time.sleep(4)
    r = json.loads(ev(STATE)); print('AFTER', r, flush=True)
    ok = (r['len'] == 0)
    print('OK' if ok else 'UNVERIFIED')
    sys.exit(0 if ok else 5)
finally:
    ws.close()
