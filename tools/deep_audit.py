"""Deep SEO audit for beeblend.in + public competitor footprint + Google autocomplete (India). Runs on GitHub Actions."""
import json, re, time, urllib.request, urllib.parse, html as H, concurrent.futures as cf
UA={'User-Agent':'Mozilla/5.0 (compatible; BeeBlendAudit/2.0)'}
def get(u,t=40,binary=False):
    for i in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r:
                b=r.read(); return r.status,(b if binary else b.decode('utf-8','replace')),r.geturl(),dict(r.headers)
        except urllib.error.HTTPError as e: return e.code,'',u,{}
        except Exception as e: err=str(e); time.sleep(1)
    return 0,err,u,{}
def locs(x): return [H.unescape(u) for u in re.findall(r'<loc>(.*?)</loc>',x)]
def sitemap_urls(base):
    st,x,_,_=get(base+'/sitemap.xml'); out=[]
    subs=locs(x) if 'sitemapindex' in x else []
    if not subs: return locs(x)
    for s in subs:
        st,y,_,_=get(s); out+=locs(y)
    return out
out={}
# ---------- 1. beeblend full crawl ----------
B='https://beeblend.in'
urls=[u for u in sitemap_urls(B) if 'beeblend.in' in u and not re.search(r'\.(md|xml)$',u)]
pages={}; links={}; imgs_noalt=[]
def crawl(u):
    st,h,fin,hd=get(u)
    d={'status':st,'final':fin}
    if st!=200: return u,d,[],[]
    g=lambda rx:(re.search(rx,h,re.I|re.S) or [None,None])[1]
    d['title']=' '.join(H.unescape(g(r'<title>(.*?)</title>') or '').split())
    d['desc']=H.unescape(g(r'<meta\s+name="description"\s+content="(.*?)"') or '')
    d['canonical']=g(r'<link\s+rel="canonical"\s+href="(.*?)"')
    d['robots']=g(r'<meta\s+name="robots"\s+content="(.*?)"')
    d['h1']=[' '.join(re.sub('<[^>]+>','',x).split())[:90] for x in re.findall(r'<h1[^>]*>(.*?)</h1>',h,re.I|re.S)]
    types=[]
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',h,re.I|re.S):
        try: j=json.loads(blk)
        except Exception: types.append('PARSE_ERROR'); continue
        for it in (j.get('@graph',[j]) if isinstance(j,dict) else j):
            if isinstance(it,dict): types.append(it.get('@type') if isinstance(it.get('@type'),str) else str(it.get('@type')))
    d['ld']=types
    imgs=re.findall(r'<img\b[^>]*>',h,re.I)
    na=[]
    for i in imgs:
        a=re.search(r'\balt="([^"]*)"',i); src=re.search(r'\bsrc="([^"]+)"',i)
        if (not a or not a.group(1).strip()) and src: na.append(src.group(1).split('?')[0].split('/')[-1])
    d['imgs']=len(imgs); d['noalt']=len(na)
    body=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S|re.I)
    main=re.search(r'<main.*?</main>',body,re.S|re.I); txt=re.sub('<[^>]+>',' ',main.group(0) if main else body)
    d['words_main']=len(txt.split())
    d['kb']=len(h)//1024
    hrefs=set()
    for m in re.findall(r'href="(/[^"#?]*)',h):
        if not re.match(r'/(cdn|cart|account|checkouts|search|apps|services|tools|policies|wpm|\.well-known)',m): hrefs.add(m)
    return u,d,sorted(hrefs),na
with cf.ThreadPoolExecutor(6) as ex:
    for u,d,hr,na in ex.map(crawl,urls):
        pages[u]=d
        for x in hr: links.setdefault(x,set()).add(u)
        for n in na: imgs_noalt.append((u,n))
# broken internal links
def chk(p):
    st,_,fin,_=get(B+p,t=25); return p,st,fin
broken=[]; redirects=[]
with cf.ThreadPoolExecutor(8) as ex:
    for p,st,fin in ex.map(chk,sorted(links)):
        if st!=200: broken.append({'path':p,'status':st,'linked_from':sorted(links[p])[:5]})
        elif urllib.parse.urlparse(fin).path.rstrip('/')!=p.rstrip('/'): redirects.append({'path':p,'to':fin,'linked_from':sorted(links[p])[:3]})
# inlinks count per sitemap page
inl={u:len(links.get(urllib.parse.urlparse(u).path or '/',[])) for u in urls}
out['site']={'n_urls':len(urls),'pages':pages,'broken':broken,'redirect_links':redirects,'noalt':imgs_noalt[:400],'inlinks':inl}
st,rb,_,_=get(B+'/robots.txt'); out['site']['robots']=rb[:4000]
# duplicate titles / descriptions
from collections import Counter
tc=Counter(v.get('title') for v in pages.values() if v.get('title')); dc=Counter(v.get('desc') for v in pages.values() if v.get('desc'))
out['site']['dup_titles']=[t for t,c in tc.items() if c>1]; out['site']['dup_desc']=[t for t,c in dc.items() if c>1]
# ---------- 2. PageSpeed (mobile) ----------
psi={}
for p in ['/','/products/kashmiri-acacia-honey','/collections/jar','/blogs/news/which-honey-is-best-india']:
    for attempt in range(3):
        q=urllib.parse.urlencode({'url':B+p,'strategy':'mobile','category':'performance'})
        st,x,_,_=get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?'+q,t=150)
        if st==200 and x:
            try:
                j=json.loads(x); lr=j['lighthouseResult']; a=lr['audits']
                r={'score':lr['categories']['performance']['score']}
                for k in ['largest-contentful-paint','first-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','total-byte-weight','dom-size']:
                    r[k]=a[k].get('displayValue')
                r['field']={k:(v.get('percentile'),v.get('category')) for k,v in j.get('loadingExperience',{}).get('metrics',{}).items()}
                r['field_overall']=j.get('loadingExperience',{}).get('overall_category')
                r['opps']=sorted([(v['title'],v['details'].get('overallSavingsMs',0),v['details'].get('overallSavingsBytes',0)) for v in a.values() if isinstance(v.get('details'),dict) and v['details'].get('type')=='opportunity' and (v['details'].get('overallSavingsMs',0)>200)],key=lambda z:-z[1])[:8]
                r['third_party']=sorted([(i.get('entity') if isinstance(i.get('entity'),str) else (i.get('entity') or {}).get('text'),round(i.get('transferSize',0)/1024),round(i.get('blockingTime',0))) for i in a.get('third-party-summary',{}).get('details',{}).get('items',[])],key=lambda z:-z[1])[:12]
                psi[p]=r; break
            except Exception as e: psi[p]={'error':str(e)[:200]}
        else: psi[p]={'error':f'http {st}','body':x[:200] if isinstance(x,str) else ''}; time.sleep(20)
out['psi']=psi
# ---------- 3. Competitors (public footprint) ----------
comps={'Dabur':'https://www.dabur.com','Organic India':'https://organicindia.com','Two Brothers Organic Farms':'https://twobrothersindiashop.com','Akshayakalpa':'https://akshayakalpa.org','HoneyVeda':'https://honeyveda.in','Indigenous Honey':'https://indigenoushoney.com','Pahadi Amrut':'https://pahadiamrut.com','HoneyTwigs':'https://honeytwigs.com','The Divine Foods':'https://thedivinefoods.com','BeeBlend':'https://beeblend.in'}
cres={}
for name,base in comps.items():
    r={'base':base}
    st,h,fin,hd=get(base); r['home_status']=st; r['home_final']=fin
    if h:
        r['title']=' '.join(H.unescape((re.search(r'<title>(.*?)</title>',h,re.S|re.I) or [None,''])[1]).split())
        r['desc']=H.unescape((re.search(r'<meta\s+name="description"\s+content="(.*?)"',h,re.I) or [None,''])[1])
        r['shopify']='cdn.shopify.com' in h or 'Shopify.theme' in h
        r['ld_home']=list(set(re.findall(r'"@type"\s*:\s*"([A-Za-z]+)"',h)))[:15]
        r['review_apps']=[k for k in ['judge.me','judgeme','yotpo','loox','okendo','stamped','reviews.io','trustpilot','ali-reviews','kudosi','fera'] if k in h.lower()]
    root=fin.split('/',3)[0]+'//'+fin.split('/')[2] if fin.startswith('http') else base
    try:
        su=sitemap_urls(root)
    except Exception as e: su=[]
    r['sitemap_urls']=len(su)
    r['blog_urls']=len([u for u in su if re.search(r'/blogs?/|/blog/|/articles?/|/recipes?/',u)])
    r['product_urls']=len([u for u in su if '/products/' in u or '/product/' in u])
    r['honey_product_urls']=len([u for u in su if ('/products/' in u or '/product/' in u) and 'honey' in u.lower()])
    r['sample_honey_urls']=[u for u in su if 'honey' in u.lower()][:25]
    if r.get('shopify'):
        st,pj,_,_=get(root+'/products.json?limit=250')
        try:
            prods=json.loads(pj).get('products',[])
            hp=[p for p in prods if 'honey' in (p['title']+' '+p.get('product_type','')).lower()]
            r['honey_products']=[{'title':p['title'],'handle':p['handle'],'prices':sorted({v['price'] for v in p['variants']})[:6],'sizes':[v['title'] for v in p['variants']][:6]} for p in hp][:30]
        except Exception: pass
    cres[name]=r
out['competitors']=cres
# ---------- 4. Google autocomplete (India) ----------
seeds=['buy honey online','best honey in india','pure honey','raw honey','organic honey','single origin honey','kashmiri acacia honey','acacia honey','lychee honey','litchi honey','himalayan honey','mustard honey','fennel honey','sesame honey','honey sachets','honey gift box','honey gift','honey for','honey price','honey 1kg','which honey is best','is honey','honey vs','natural honey','forest honey','wild honey','multiflora honey','unprocessed honey','honey brand','shahad','asli shahad','शहद','शुद्ध शहद','सरसों का शहद','लीची शहद','madhu','honey benefits','honey with','corporate gifts honey','diwali gift honey']
ac={}
for s in seeds:
    q=urllib.parse.urlencode({'client':'firefox','hl':'en','gl':'in','q':s})
    st,x,_,_=get('https://suggestqueries.google.com/complete/search?'+q,t=20)
    try: ac[s]=json.loads(x)[1]
    except Exception: ac[s]={'error':st}
    time.sleep(0.4)
out['autocomplete']=ac
json.dump(out,open('deep-audit.json','w'),indent=1,ensure_ascii=False,default=list); print('done', len(urls))
