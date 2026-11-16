#!/usr/bin/env node
/* hr_ui_probe.js — 只读：导出左侧列表页签栏 + 当前筛选状态 + 列表计数。不点击、不发消息。 */
const http = require('http'), WS = require('ws'); const BASE = 'http://127.0.0.1:9222';
const get = p => new Promise((res, rej) => http.get(BASE + p, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej));
function connect(u) { const ws = new WS(u, { perMessageDeflate: false }); let id = 0; const p = new Map();
  ws.on('message', raw => { let m; try { m = JSON.parse(raw.toString()); } catch (e) { return; } if (m.id && p.has(m.id)) { const { res, rej } = p.get(m.id); p.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } });
  const ready = new Promise((r, j) => { ws.on('open', r); ws.on('error', j); });
  const send = (me, pa) => new Promise((r, j) => { const i = ++id; p.set(i, { res: r, rej: j }); ws.send(JSON.stringify({ id: i, method: me, params: pa || {} })); });
  return { ws, ready, send }; }
(async () => {
  const lst = await get('/json/list');
  const t = lst.filter(x => x.type === 'page').find(x => (x.url || '').includes('chat/index'));
  if (!t) { console.error('no target'); process.exit(2); }
  const c = connect(t.webSocketDebuggerUrl); await c.ready;
  const ev = e => c.send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  const out = (await ev(`(function(){
    var tabs=[].slice.call(document.querySelectorAll('.user-list-tab, .chat-tab, .user-list-filter *, [class*=filter] *')).filter(function(e){return e.children.length===0 && (e.innerText||'').trim()}).slice(0,20);
    var act=[].slice.call(document.querySelectorAll('.active,.selected,.is-active')).map(function(e){return ((e.className||'')+' :: '+(e.innerText||'').replace(/\\n+/g,' / ').slice(0,40))}).slice(0,10);
    return JSON.stringify({href:location.href,n:document.querySelectorAll('.geek-item-wrap').length,
      tabs:tabs.map(function(e){return (e.className||'')+' :: '+(e.innerText||'').replace(/\\n+/g,' / ').slice(0,30)}),active:act},null,1);
  })()`)).result.value;
  console.log(out); c.ws.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
