#!/usr/bin/env python3
# .tt_comment.py <tabId> <text> [url] — 头条文章/微头条「引流评论」一键发布（零依赖 · 复用 fanqie/cdp.py）
#
# 背景（2026-10-20 12:0x–12:5x 轮实测 · SPEC §5.1 口径补充）：
#   ① 输入框 = `div.comment-textarea`，提交按钮 = `button.submit-btn`（无文字时带 `disable`）；
#   ② **直接点输入框「中心点」经常不聚焦**（`elementFromPoint` 落在父级 `div.ttp-comment-input`，焦点留给 BODY）；
#      ⇒ 必须**校验 document.activeElement**，未聚焦就按 高度/2 逐档试探点击，最多 4 个点；
#   ③ 页面首次加载的 1–2 秒内点击会被吞掉 ⇒ 打开后至少等 3.5 s（本脚本默认 wait=4.0）；
#   ④ 文本只能用真实按键（keyDown with text + keyUp）逐字输入，JS 赋值 / insertText 不激活提交按钮；
#   ⑤ 成功判据（SPEC §5.1 三取二）：输入框清空 / 列表顶部出现本号评论 / 评论计数 +1 —— 本脚本回读前两条。
import json
import sys
import time

sys.path.insert(0, '/home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/fanqie')
import cdp  # noqa: E402

# 先 scrollIntoView 把评论框滚到视口中间（实测：框在视口外时鼠标坐标全错、点击必然落空）
BOX_JS = """(async()=>{const b=document.querySelector('div.comment-textarea');if(!b)return null;
b.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,700));
const r=b.getBoundingClientRect();return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),h:Math.round(r.height)})})()"""
FOCUS_JS = "(()=>{const a=document.activeElement;return (a.tagName+'.'+String(a.className)).slice(0,40)})()"
STATE_JS = """(()=>{const ta=document.querySelector('div.comment-textarea');
const b=[...document.querySelectorAll('button.submit-btn')].filter(x=>x.offsetParent)[0];
if(!ta||!b)return null;const r=b.getBoundingClientRect();
return JSON.stringify({len:ta.innerText.length,cls:b.className,bx:Math.round(r.x+r.width/2),by:Math.round(r.y+r.height/2)})})()"""


def main(argv):
    if len(argv) < 2:
        print('usage: .tt_comment.py <tabId> <text> [url]')
        return 9
    tid, text = argv[0], argv[1]
    if len(text) > 40:
        print('ABORT_TEXT_TOO_LONG %d (SPEC §5 硬限 ≤40 字)' % len(text))
        return 4
    if len(argv) > 2:
        cdp.cmd_goto([tid, argv[2]])
        time.sleep(4.0)
    ws = cdp.session(tid)

    def ev(expr):
        return ws.call('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})['result'].get('value')

    def click(x, y):
        for kind in ('mouseMoved', 'mousePressed', 'mouseReleased'):
            p = {'type': kind, 'x': x, 'y': y}
            if kind != 'mouseMoved':
                p.update(button='left', clickCount=1)
            ws.call('Input.dispatchMouseEvent', p)
            time.sleep(0.1)

    try:
        raw = ev(BOX_JS)
        if not raw:
            print('NO_TEXTAREA')
            return 1
        box = json.loads(raw)
        ys = [box['y'], box['y'] - box['h'] // 2 + 3, box['y'] + box['h'] // 2 - 3, box['y'] - 3]
        focused = None
        for y in ys:
            click(box['x'], y)
            time.sleep(0.6)
            focused = ev(FOCUS_JS)
            if 'comment-textarea' in focused:
                break
            # 未聚焦：重新取框（长页面里滚动位置可能在两次点击之间变化）
            raw = ev(BOX_JS)
            if raw:
                nb = json.loads(raw)
                box = nb
                ys = [nb['y'], nb['y'] - nb['h'] // 2 + 3, nb['y'] + nb['h'] // 2 - 3, nb['y'] - 3]
        print('FOCUS', focused)
        if 'comment-textarea' not in focused:
            print('ABORT_NO_FOCUS')
            return 3

        for ch in text:
            ws.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'text': ch, 'unmodifiedText': ch, 'key': ch})
            ws.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': ch})
            time.sleep(0.03)
        time.sleep(0.5)
        st = json.loads(ev(STATE_JS))
        print('TYPED', st)
        if st['len'] != len(text) or 'disable' in st['cls']:
            print('ABORT_NOT_READY')
            return 2

        click(st['bx'], st['by'])
        time.sleep(3.5)
        tag = text[:10]
        raw = ev("(()=>{const t=document.body.innerText;const k='%s';const i=t.lastIndexOf(k);"
                 "return JSON.stringify({hits:t.split(k).length-1,seg:t.slice(Math.max(0,i-70),i+30)})})()" % tag)
        res = json.loads(raw)
        fresh = '刚刚' in res['seg'] or '秒前' in res['seg'] or '1分钟前' in res['seg']
        print('AFTER', 'OK' if (res['hits'] >= 1 and fresh) else 'UNVERIFIED', res['hits'], repr(res['seg'][-30:]))
        return 0 if (res['hits'] >= 1 and fresh) else 5
    finally:
        ws.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
