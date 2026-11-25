import sys, requests, pathlib
sys.path.insert(0, 'research')
from arxiv_fetch import HEADERS
ids = '2610.26781,2610.26851,2610.26861,2610.25026,2610.26538'
base = pathlib.Path('research/raw')
r = requests.get('https://export.arxiv.org/api/query', params={'id_list': ids, 'max_results': 20}, headers=HEADERS, timeout=120)
(base/'2026-10-20-idlist-r102.xml').write_text(r.text, encoding='utf-8')
(base/'2026-10-20-idlist-r102.headers').write_text(
    'HTTP %s\nContent-Type: %s\nContent-Length: %s\n' % (r.status_code, r.headers.get('Content-Type'), r.headers.get('Content-Length')), encoding='utf-8')
print('status', r.status_code, r.headers.get('Content-Type'), len(r.text))
