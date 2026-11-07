"""Competitor SEO deep-dive (public data only) + Google India autocomplete expansion. Runs on GitHub Actions."""
import json, re, time, urllib.request, urllib.parse, html as H, concurrent.futures as cf, collections
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
def get(u,t=40):
    err=''
    for i in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r:
                return r.status,r.read().decode('utf-8','replace'),r.geturl()
        except urllib.error.HTTPError as e: return e.code,'',u
        except Exception as e: err=str(e); time.sleep(1)
    return 0,err,u
def locs(x): return [H.unescape(u) for u in re.findall(r'<loc>(.*?)</loc>',x)]
def sitemap_urls(base):
    st,x,_=get(base+'/sitemap.xml')
    if 'sitemapindex' not in x: return locs(x)
    out=[]
    for s in locs(x):
        if re.search(r'image|video',s): continue
        out+=locs(get(s)[1])
    return out
def ldjson(h):
    items=[]
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',h,re.I|re.S):
        try: j=json.loads(blk.strip())
        except Exception: continue
        stack=[j]
        while stack:
            it=stack.pop()
            if isinstance(it,list): stack+=it
            elif isinstance(it,dict):
                items.append(it)
                for k,v in it.items():
                    if isinstance(v,(dict,list)): stack.append(v)
    return items
def page(u):
    st,h,fin=get(u)
    d={'url':u,'status':st}
    if st!=200: return d
    g=lambda rx:(re.search(rx,h,re.I|re.S) or [None,None])[1]
    d['title']=' '.join(H.unescape(g(r'<title[^>]*>(.*?)</title>') or '').split())
    d['desc']=' '.join(H.unescape(g(r'<meta\s+name="description"\s+content="(.*?)"') or g(r'<meta\s+content="(.*?)"\s+name="description"') or '').split())
    d['h1']=[' '.join(H.unescape(re.sub('<[^>]+>','',x)).split())[:120] for x in re.findall(r'<h1[^>]*>(.*?)</h1>',h,re.I|re.S)][:3]
    d['h2']=[' '.join(H.unescape(re.sub('<[^>]+>','',x)).split())[:90] for x in re.findall(r'<h2[^>]*>(.*?)</h2>',h,re.I|re.S)][:25]
    items=ldjson(h)
    d['ld']=sorted(set(str(i.get('@type')) for i in items if i.get('@type')))
    ar=[i for i in items if str(i.get('@type'))=='AggregateRating' or 'ratingValue' in i]
    if ar: d['rating']=ar[0].get('ratingValue'); d['reviews']=ar[0].get('reviewCount') or ar[0].get('ratingCount')
    m=re.search(r'data-number-of-reviews="(\d+)"',h) or re.search(r'"reviewCount"\s*:\s*"?(\d+)',h)
    if m and not d.get('reviews'): d['reviews']=m.group(1)
    imgs=re.findall(r'<img\b[^>]*>',h,re.I)
    d['imgs']=len(imgs); d['imgs_alt']=sum(1 for i in imgs if re.search(r'\balt="[^"]{3,}"',i))
    body=re.sub(r'<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>','',h,flags=re.S|re.I)
    main=re.search(r'<main.*?</main>',body,re.S|re.I); txt=' '.join(H.unescape(re.sub('<[^>]+>',' ',main.group(0) if main else body)).split())
    d['words']=len(txt.split())
    low=txt.lower()
    d['signals']={k:bool(re.search(v,low)) for k,v in {
        'nmr':r'\bnmr\b','lab_test':r'lab[- ]test|test report|tested','fssai':r'fssai','organic_cert':r'certified organic|ecocert|npop|india organic',
        'cod':r'cash on delivery|\bcod\b','free_ship':r'free (shipping|delivery)','faq':r'faq|frequently asked','origin':r'sourced from|harvested|beekeeper|apiar',
        'health_claims':r'immunit|cure|diabet|weight loss|boost'}.items()}
    d['kb']=len(h)//1024
    return d
def nav_links(base):
    st,h,fin=get(base)
    if st!=200: return []
    host=urllib.parse.urlparse(fin).netloc
    hd=re.search(r'<header.*?</header>',h,re.S|re.I)
    seg=hd.group(0) if hd else h[:60000]
    out=[]
    for m in re.findall(r'href="([^"#?]+)"',seg):
        p=urllib.parse.urlparse(m)
        if p.netloc and host not in p.netloc: continue
        path=p.path
        if re.match(r'^/(collections|products|pages|blogs|blog|our-brand|product)',path) and path not in out: out.append(path)
    # homepage body links (featured products / collections)
    body=collections.Counter(re.findall(r'href="(?:https?://[^/"]*)?(/(?:collections|products|blogs|product)/[^"#?]+)"',h))
    return {'nav':out[:40],'home_most_linked':body.most_common(15)}
COMP={'BeeBlend':'https://beeblend.in','HoneyVeda':'https://honeyveda.in','Indigenous Honey':'https://indigenoushoney.com',
 'Two Brothers Organic Farms':'https://twobrothersindiashop.com','Pahadi Amrut':'https://pahadiamrut.com','Organic India':'https://organicindia.com',
 'The Divine Foods':'https://www.thedivinefoods.com','Akshayakalpa':'https://akshayakalpa.org','Dabur':'https://www.dabur.com'}
out={'comp':{}}
for name,base in COMP.items():
    c={'base':base}
    urls=sitemap_urls(base); c['n_urls']=len(urls)
    honey=[u for u in urls if re.search(r'honey|shahad|madhu',u,re.I)]
    c['honey_urls']=honey[:200]
    blog=[u for u in urls if re.search(r'/blogs?/',u)]
    c['blog_slugs']=[u.rstrip('/').split('/')[-1] for u in blog][:900]
    c['nav']=nav_links(base)
    prods=[u for u in honey if re.search(r'/products?/',u)][:14]
    cols=[u for u in honey if '/collections/' in u and '/products/' not in u][:4]
    posts=[u for u in honey if re.search(r'/blogs?/',u)][:6]
    targets=prods+cols+posts+([base+'/'] )
    with cf.ThreadPoolExecutor(4) as ex: c['pages']=list(ex.map(page,targets))
    out['comp'][name]=c
    print(name,len(urls),len(honey),len(prods),flush=True)
# HoneyTwigs retry variants
ht={}
for u in ['https://honeytwigs.com','https://www.honeytwigs.com','http://honeytwigs.com','https://honeytwigs.in','https://www.honeytwigs.in']:
    st,h,fin=get(u,25); ht[u]={'status':st,'final':fin,'title':' '.join(H.unescape((re.search(r'<title[^>]*>(.*?)</title>',h,re.S|re.I) or [None,''])[1]).split()) if st==200 else ''}
out['honeytwigs']=ht
# Autocomplete expansion
seeds=['kashmiri acacia honey','acacia honey','lychee honey','litchi honey','mustard honey','sarson honey','himalayan honey','himalayan multiflora honey',
 'fennel honey','saunf honey','sesame honey','til honey','raw honey','pure honey','organic honey','natural honey','single origin honey','monofloral honey',
 'raw honey india','honey online','buy honey','buy raw honey','buy pure honey','honey gift','honey gift box','honey hamper','honey sachet','honey sachets',
 'honey brands','best honey','best raw honey','best honey for','crystallised honey','crystallized honey','honey crystallization','honey nmr',
 'unprocessed honey','raw unfiltered honey','honey tasting','honey combo','asli shahad','shahad','sarson ka shahad','शहद','शुद्ध शहद','honey jar','honey 250g',
 'honey 500g','honey for tea','corporate gift','diwali hamper','wedding return gift','healthy gift hamper','almond honey','honey with nuts','dry fruits honey','honey price']
def ac(q):
    u='https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=in&q='+urllib.parse.quote(q)
    st,b,_=get(u,15)
    try: return json.loads(b)[1]
    except Exception: return []
acq=[]
for s in seeds:
    for suf in ['']+[' '+x for x in 'abcdefghijklmnopqrstuvwyz']+[' vs',' for',' in hindi',' price',' online',' near me',' benefits']:
        acq.append(s+suf)
res={}
with cf.ThreadPoolExecutor(3) as ex:
    for q,r in zip(acq,ex.map(lambda q:(time.sleep(0.15),ac(q))[1],acq)): res[q]=r
out['autocomplete']=res
json.dump(out,open('comp-audit.json','w'),ensure_ascii=False)
print('done',sum(len(v) for v in res.values()))
