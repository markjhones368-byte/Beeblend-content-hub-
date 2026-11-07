import json, re, time, urllib.request, urllib.parse
from html.parser import HTMLParser
UA={'User-Agent':'Mozilla/5.0 (compatible; BeeBlendSEOAudit/1.0)'}
def get(u,t=60):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r: return r.status, r.read().decode('utf-8','replace'), r.geturl()
    except urllib.error.HTTPError as e: return e.code, '', u
    except Exception as e: return 0, str(e), u
B='https://beeblend.in'
pages=['/','/collections/jar','/collections/sachet','/collections/all','/collections/gifts','/collections/frontpage','/collections/honeycomb','/collections/candles','/pages/about-us','/pages/why-beeblend','/pages/health-benefits','/pages/gifting','/blogs/news','/blogs/news/which-honey-is-best-india','/blogs/news/how-to-identify-pure-honey-at-home','/blogs/news/asli-shahad-ki-pehchan']
for h in ['lychee-honey','fennel-honey','himalayan-multifloral-honey','sesame-honey','mustard-honey','golden-nut-honey','kashmiri-acacia-honey','pure-honey-collection']: pages.append('/products/'+h)
out={'pages':{}}
for p in pages:
    st,html,final=get(B+p)
    d={'status':st,'final':final}
    if html and st==200:
        g=lambda rx: (re.search(rx,html,re.I|re.S) or [None,None])[1]
        d['title']=(g(r'<title>(.*?)</title>') or '').strip()
        d['desc']=g(r'<meta\s+name="description"\s+content="(.*?)"')
        d['canonical']=g(r'<link\s+rel="canonical"\s+href="(.*?)"')
        d['robots']=g(r'<meta\s+name="robots"\s+content="(.*?)"')
        d['h1']=[re.sub('<[^>]+>','',x).strip()[:80] for x in re.findall(r'<h1[^>]*>(.*?)</h1>',html,re.I|re.S)]
        lds=[]
        for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',html,re.I|re.S):
            try:
                j=json.loads(blk)
            except Exception as e:
                lds.append({'PARSE_ERROR':str(e)[:80],'snippet':blk.strip()[:120]}); continue
            items=j.get('@graph',[j]) if isinstance(j,dict) else j
            for it in items if isinstance(items,list) else [items]:
                if not isinstance(it,dict): continue
                t=it.get('@type'); e={'type':t}
                if t in ('Product','ProductGroup'):
                    e.update({k:it.get(k) is not None for k in ('brand','aggregateRating','review','gtin','sku','image','description')})
                    off=it.get('offers') or it.get('hasVariant')
                    e['offers']=json.dumps(off)[:300] if off else None
                if t=='FAQPage': e['n']=len(it.get('mainEntity',[]))
                if t=='BreadcrumbList': e['n']=len(it.get('itemListElement',[]))
                lds.append(e)
        d['jsonld']=lds
        imgs=re.findall(r'<img\b[^>]*>',html,re.I)
        d['imgs']=len(imgs); d['img_no_alt']=sum(1 for i in imgs if not re.search(r'\balt="[^"]+',i))
        text=re.sub(r'<script.*?</script>|<style.*?</style>','',html,flags=re.S|re.I)
        d['words']=len(re.sub('<[^>]+>',' ',text).split())
        d['html_kb']=len(html)//1024
        d['hreflang']=re.findall(r'hreflang="([^"]+)"',html)[:6]
    out['pages'][p]=d
st,rb,_=get(B+'/robots.txt'); out['robots_txt']=rb[:3000]
st,sm,_=get(B+'/sitemap.xml'); subs=re.findall(r'<loc>(.*?)</loc>',sm); out['sitemaps']={}
allurls=[]
for s in subs:
    s=s.replace('&amp;','&'); st,x,_=get(s); u=re.findall(r'<loc>(.*?)</loc>',x); out['sitemaps'][s]=len(u); allurls+=u
out['sitemap_urls']=[u for u in allurls if not re.search(r'cdn\.shopify|/files/',u)]
psi={}
for p in ['/','/products/kashmiri-acacia-honey']:
    for strat in ['mobile']:
        q=urllib.parse.urlencode({'url':B+p,'strategy':strat,'category':['performance','seo']},doseq=True)
        st,x,_=get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?'+q,t=120)
        try:
            j=json.loads(x); lr=j['lighthouseResult']
            r={'perf':lr['categories']['performance']['score'],'seo':lr['categories']['seo']['score']}
            for k in ['largest-contentful-paint','first-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','total-byte-weight']:
                r[k]=lr['audits'][k]['displayValue']
            fe=j.get('loadingExperience',{}).get('metrics',{})
            r['field']={k:(v.get('percentile'),v.get('category')) for k,v in fe.items()}
            r['seo_fails']=[a['title'] for a in lr['audits'].values() if a.get('score')==0 and a['id'] in [x['id'] for x in lr['categories']['seo']['auditRefs']]]
            r['opps']=sorted([(a['title'],a.get('details',{}).get('overallSavingsMs',0)) for a in lr['audits'].values() if a.get('details',{}).get('type')=='opportunity' and a.get('details',{}).get('overallSavingsMs',0)>300],key=lambda z:-z[1])[:8]
        except Exception as e: r={'error':str(e)[:200],'raw':x[:300]}
        psi[p+' '+strat]=r
out['psi']=psi
json.dump(out,open('seo-audit.json','w'),indent=1,ensure_ascii=False); print('done')
