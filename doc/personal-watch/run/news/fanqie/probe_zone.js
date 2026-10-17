(() => {
  // probe_zone.js — 番茄作家专区登录态探针（在目标标签页上执行）
  const txt = document.body.innerText || '';
  const has = (s) => txt.includes(s);
  return JSON.stringify({
    url: location.href,
    title: document.title,
    loginShown: has('请登录') || has('立即登录'),
    hasMyWorks: has('我的作品') || has('作品管理') || has('前往工作台'),
    head: txt.slice(0, 160),
    cookieNames: document.cookie.split('; ').map((c) => c.split('=')[0]).join(',')
  }, null, 1);
})()
