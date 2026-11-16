#!/usr/bin/env node
/* hr_id_by_name.js — 只读：按姓名精确匹配返回 data-id。 */
const http = require('http'), WS = require('ws'); const BASE = 'http://127.0.0.1:9222';
const get = p => new Promise((res, rej) => http.get(BASE + p, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } }); }).on('error', rej));
function connect(u) { const ws = new WS(u, { perMessageDeflate: false }); let id = 0; const p = new Map();
  ws.on('message', raw => { let m; try { m = JSON.parse(raw.toString()); } catch (e) { return; } if (m.id && p.has(m.id)) { const { res, rej } = p.get(m.id); p.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } });
  const ready = new Promise((r, j) => { ws.on('open', r); ws.on('error', j); });
  const send = (me, pa) => new Promise((r, j) => { const i = ++id; p.set(i, { res: r, rej: j }); ws.send(JSON.stringify({ id: i, method: me, params: pa || {} })); });
  return { ws, ready, send }; }
(async () => {
  const names = process.argv.slice(2);
  const lst = await get('/json/list');
  const t = lst.filter(x => x.type === 'page').find(x => (x.url || '').includes('chat/index'));
  if (!t) { console.error('no target'); process.exit(2); }
  const c = connect(t.webSocketDebuggerUrl); await c.ready;
  const ev = e => c.send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  const out = (await ev(`(function(){
    var res={};var w=document.querySelectorAll('.geek-item-wrap');
    for(var i=0;i<w.length;i++){var n=((w[i].querySelector('.geek-name')||{}).innerText||'').trim();var g=w[i].querySelector('.geek-item');if(n)res[n]=g?g.getAttribute('data-id'):null;}
    var want=${JSON.stringify(names)};var o={};want.forEach(function(n){o[n]=res[n]||null;});return JSON.stringify(o);
  })()`)).result.value;
  console.log(out); c.ws.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
