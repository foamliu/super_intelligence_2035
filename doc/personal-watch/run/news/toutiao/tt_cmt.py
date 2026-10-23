#!/usr/bin/env python3
"""头条公开页 w/<id> 发评论（逐键路径）。

已验证的 3 个坑（2026-10-23 19:4x 实测）：
 1) `Input.insertText` 能写进 div.comment-textarea，但 **不触发** 头条的输入监听
    ⇒ `button.submit-btn` 一直是 `submit-btn disable`（opacity .3），点了没反应。
    ⇒ 必须走 **逐字符 keyDown/keyUp**（带 text/unmodifiedText）。
 2) 逐键之前若用 insertText 写了一个字符，它会留在框里（本轮误留一个 `a`），
    发前必须 Ctrl+A + Backspace 清空并复核 len==0。
 3) 中间隔 ≥4s 页面才把新评论渲染进 `.ttp-comment-item`；刚点完读 items 数是 0，
    要 **重新导航** 再读才是真数。

用法：
  python3 /tmp/tt_cmt.py <标签id> <页面URL> <评论文本> <截图标签> [--dry]
"""
import sys, json, time
sys.path.insert(0, '/tmp')
from ttx import T

SHOT = '/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/toutiao/shots/'
TA = '"%s"' % '.comment-textarea'

def state(t):
    return t.ev(r'''(()=>{const ta=document.querySelector(%s);const b=document.querySelector('.ttp-comment-input button.submit-btn');const t2=document.body.innerText.replace(/\s+/g,' ');return JSON.stringify({len:ta?(ta.innerText||'').length:-1,txt:ta?(ta.innerText||'').trim():'',cls:b?b.className:'NF',op:b?getComputedStyle(b).opacity:'-',items:document.querySelectorAll('.ttp-comment-item').length,cmt:(t2.match(/评论\s*\d+/)||[])[0]})})()''' % TA)

def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    tid, url, text, tag = sys.argv[1:5]
    dry = '--dry' in sys.argv
    t = T(tid)
    t.ws.call('Page.bringToFront', {})
    t.ws.call('Page.navigate', {'url': url}); time.sleep(6)
    t.ws.call('Emulation.setFocusEmulationEnabled', {'enabled': True}); time.sleep(0.4)
    print('BEFORE', state(t))
    # 1) 清空残留
    r = json.loads(t.ev(r'''(()=>{const ta=document.querySelector(%s);ta.scrollIntoView({block:'center'});const q=ta.getBoundingClientRect();return JSON.stringify({x:Math.round(q.x+30),y:Math.round(q.y+q.height/2)})})()''' % TA))
    t.click(r['x'], r['y']); time.sleep(0.3)
    for tpe in ('keyDown', 'keyUp'):
        t.ws.call('Input.dispatchKeyEvent', {'type': tpe, 'key': 'a', 'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'nativeVirtualKeyCode': 65, 'modifiers': 2}); time.sleep(0.08)
    t.ws.call('Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'Backspace', 'code': 'Backspace', 'windowsVirtualKeyCode': 8, 'nativeVirtualKeyCode': 8})
    t.ws.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Backspace', 'code': 'Backspace', 'windowsVirtualKeyCode': 8, 'nativeVirtualKeyCode': 8})
    time.sleep(0.6)
    # 2) 逐键输入
    for ch in text:
        t.ws.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'text': ch, 'unmodifiedText': ch, 'key': ch})
        t.ws.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': ch})
        time.sleep(0.03)
    time.sleep(0.9)
    st = json.loads(state(t))
    print('FILLED', st)
    t.shot(SHOT + tag + '-filled.png')
    if dry:
        t.close(); return
    assert st['len'] == len(text), 'fill mismatch'
    assert 'disable' not in st['cls'], 'submit still disabled - keyboard path failed'
    # 3) 点提交
    b = json.loads(t.ev(r'''(()=>{const b=document.querySelector('.ttp-comment-input button.submit-btn');b.scrollIntoView({block:'center'});const q=b.getBoundingClientRect();return JSON.stringify({x:Math.round(q.x+q.width/2),y:Math.round(q.y+q.height/2)})})()'''))
    t.click(b['x'], b['y']); time.sleep(5)
    print('AFTER', state(t))
    # 4) 重新导航复核
    t.ws.call('Page.navigate', {'url': url}); time.sleep(6)
    fin = json.loads(state(t))
    fin['mine'] = bool(t.ev('document.body.innerText.indexOf(%s) >= 0' % json.dumps(text[:10], ensure_ascii=False)))
    print('RECHECK', json.dumps(fin, ensure_ascii=False))
    t.shot(SHOT + tag + '-after.png')
    t.close()

main()
