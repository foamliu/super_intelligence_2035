(async () => {
  const ta =
    document.querySelector('.comment-textarea textarea') ||
    document.querySelector('.comment-textarea') ||
    document.querySelector('textarea');
  if (!ta) return JSON.stringify({ err: 'no textarea', cand: [...document.querySelectorAll('div[contenteditable],textarea')].map((n) => n.className + '|' + n.tagName).slice(0, 8) });
  ta.focus();
  document.execCommand('insertText', false, '我上个月刚给老机器补了两根DDR5，现在回头看，买的不是内存，是"还没涨到这儿"的那点运气。');
  await new Promise((r) => setTimeout(r, 800));
  return JSON.stringify({ val: ta.value || ta.innerText, cls: ta.className });
})()
