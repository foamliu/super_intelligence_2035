import socket, urllib.request, urllib.parse, time, xml.etree.ElementTree as ET
GOOD_IP="151.101.67.42"; HOST="export.arxiv.org"
_o=socket.getaddrinfo
def _g(h,p,*a,**k):
    return _o(GOOD_IP,p,*a,**k) if h==HOST else _o(h,p,*a,**k)
socket.getaddrinfo=_g
NS={'a':'http://www.w3.org/2005/Atom','x':'http://arxiv.org/schemas/atom','o':'http://a9.com/-/spec/opensearch/1.1/'}
def q(name, params):
    url='https://%s/api/query?%s'%(HOST, urllib.parse.urlencode(params))
    req=urllib.request.Request(url, headers={'User-Agent':'research-watch/1.0 (mailto:foamliu@yeah.net)'})
    t0=time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        raw=r.read(); st=r.status; ct=r.headers.get('Content-Type')
    root=ET.fromstring(raw)
    tot=root.find('o:totalResults',NS)
    ents=root.findall('a:entry',NS)
    print('---', name, 'status=%s ct=%s total=%s n_entries=%d %.2fs'%(st,ct,tot.text if tot is not None else None,len(ents),time.time()-t0))
    for e in ents[:5]:
        print('   ', e.find('a:id',NS).text.split('/abs/')[-1], e.find('a:published',NS).text, e.find('a:updated',NS).text, e.find('x:primary_category',NS).attrib['term'], ' '.join(e.find('a:title',NS).text.split())[:70])
q('lastUpdatedDate cs.CL', {'search_query':'cat:cs.CL','start':0,'max_results':5,'sortBy':'lastUpdatedDate','sortOrder':'descending'})
time.sleep(3.2)
q('submittedDate 20261028-20261031', {'search_query':'cat:cs.CL AND submittedDate:[202610280000 TO 202610312359]','start':0,'max_results':5,'sortBy':'submittedDate','sortOrder':'descending'})
time.sleep(3.2)
q('all recent submitted', {'search_query':'submittedDate:[202610280000 TO 202610312359]','start':0,'max_results':5,'sortBy':'submittedDate','sortOrder':'descending'})
