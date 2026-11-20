#!/usr/bin/env node
/* hr_unread_toggle.js — 只读意图：切换左侧「未读」筛选开关后导出列表（不点会话、不发消息）。
 * 用法：node ~/hr_unread_toggle.js [on|off|dump]  默认 dump（只导出状态）
 */
const http = require('http'), WS = require('ws'); const BASE = 'http://127.0.0.1:9222';
const get = p => new Promise((res, rej) => http.get(BASE + p, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej));
const sleep = ms => new Promise(r => setTimeout(r, ms));
function connect(u) { const ws = new WS(u, { perMessageDeflate: false }); let id = 0; const p = new Map();
  ws.on('message', raw => { let m; try { m = JSON.parse(raw.toString()); } catch (e) { return; } if (m.id && p.has(m.id)) { const { res, rej } = p.get(m.id); p.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } });
  const ready = new Promise((r, j) => { ws.on('open', r); ws.on('error', j); });
  const send = (me, pa) => new Promise((r, j) => { const i = ++id; p.set(i, { res: r, rej: j }); ws.send(JSON.stringify({ id: i, method: me, params: pa || {} })); });
  return { ws, ready, send }; }
(async () => {
  const mode = process.argv[2] || 'dump';
  const lst = await get('/json/list');
  const t = lst.filter(x => x.type === 'page').find(x => (x.url || '').includes('chat/index'));
  if (!t) { console.error('no target'); process.exit(2); }
  const c = connect(t.webSocketDebuggerUrl); await c.ready;
  const ev = e => c.send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  const state = async () => (await ev(`(function(){
    var box=document.querySelector('.chat-message-filter-left');var el=box?[].slice.call(box.querySelectorAll('span')).filter(function(e){return (e.innerText||'').trim()==='未读';})[0]:null;
    return JSON.stringify({isActive: el? /active/.test(el.className||'') : null, cls: el?el.className:null,
      n: document.querySelectorAll('.geek-item-wrap').length});
  })()`)).result.value;
  console.log('BEFORE', await state());
  if (mode !== 'dump') {
    const want = mode === 'on' ? '未读' : '全部';
    const r = (await ev(`(function(){
      var box=document.querySelector('.chat-message-filter-left');
      if(!box) return 'nf-box';
      var el=[].slice.call(box.querySelectorAll('span')).filter(function(e){return (e.innerText||'').trim()===${JSON.stringify(want)};})[0];
      if(!el) return 'nf:'+box.innerText;
      el.click(); return 'clicked:'+el.innerText.trim();
    })()`)).result.value;
    console.log('TOGGLE', r);
    await sleep(2000);
    console.log('AFTER', await state());
    const names = (await ev(`(function(){var w=document.querySelectorAll('.geek-item-wrap');var a=[];for(var i=0;i<w.length;i++){var nm=(w[i].querySelector('.geek-name')||{}).innerText||'';var tm=(w[i].querySelector('.time,.geek-item__time')||{}).innerText||'';a.push(nm.trim()+' ~ '+tm.trim());}return a.join('\\n');})()`)).result.value;
    console.log(names);
  }
  c.ws.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
