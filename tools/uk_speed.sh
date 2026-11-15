set -x
mkdir -p out
U="https://beeblend.co.uk/"
python - <<'P'
import json,urllib.request,urllib.parse,re,time,ssl
U="https://beeblend.co.uk/"
R={}
def get(u,t=120,data=None,h=None):
    req=urllib.request.Request(u,data=data,headers=h or {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36'})
    with urllib.request.urlopen(req,timeout=t) as r: return r.status,dict(r.headers),r.read()
# 1. Google PageSpeed Insights (free public API)
for strat in ('mobile','desktop'):
    q='https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url='+urllib.parse.quote(U)+'&strategy='+strat+''.join('&category='+c for c in ('performance','accessibility','best-practices','seo'))
    for attempt in range(3):
        try:
            st,hd,b=get(q,180); j=json.loads(b); lr=j['lighthouseResult']; a=lr['audits']
            le=j.get('loadingExperience',{}); ole=j.get('originLoadingExperience',{})
            R['psi_'+strat]={'scores':{k:round(v['score']*100) for k,v in lr['categories'].items()},
              'lab':{m:a[m]['displayValue'] for m in ('first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','total-byte-weight')},
              'field_url':le.get('overall_category'),'field_origin':ole.get('overall_category'),
              'field_metrics':{k:(v.get('percentile'),v.get('category')) for k,v in (le.get('metrics') or ole.get('metrics') or {}).items()},
              'seo_fail':[k['id'] for k in lr['categories']['seo']['auditRefs'] if a.get(k['id'],{}).get('score') not in (None,1)]}
            break
        except Exception as e: R['psi_'+strat]='ERR '+str(e)[:200]; time.sleep(20)
# 2. W3C HTML validator
try:
    st,hd,b=get('https://validator.w3.org/nu/?out=json&doc='+urllib.parse.quote(U),90)
    msgs=json.loads(b)['messages']; R['w3c']={'errors':sum(1 for m in msgs if m['type']=='error'),'warnings':sum(1 for m in msgs if m.get('subType')=='warning'),'top_errors':sorted(set(m['message'][:90] for m in msgs if m['type']=='error'))[:10]}
except Exception as e: R['w3c']='ERR '+str(e)[:200]
# 3. on-page checks
st,hd,b=get(U); h=b.decode('utf-8','replace')
R['page']={'status':st,'kb':len(b)//1024,'theme_id':(re.search(r'Shopify\.theme\s*=\s*\{[^}]*"id":(\d+)',h) or [0,None])[1],
 'title':(re.search(r'<title>(.*?)</title>',h,re.S) or [0,''])[1].strip(),'desc':(re.search(r'name="description" content="([^"]*)"',h) or [0,''])[1],
 'canonical':(re.search(r'rel="canonical" href="([^"]+)"',h) or [0,''])[1],'h1_count':len(re.findall(r'<h1\b',h)),
 'og':sorted(set(re.findall(r'property="(og:[a-z:_]+)"',h))),'twitter':sorted(set(re.findall(r'name="(twitter:[a-z:_]+)"',h))),
 'hreflang':re.findall(r'hreflang="([^"]+)"',h),'lang':(re.search(r'<html[^>]*lang="([^"]+)"',h) or [0,''])[1],
 'schema_types':sorted(set(re.findall(r'"@type"\s*:\s*"([^"]+)"',h))),'imgs_no_alt':len([i for i in re.findall(r'<img\b[^>]*>',h) if 'alt=' not in i]),
 'viewport':'name="viewport"' in h,'hsts':hd.get('Strict-Transport-Security'),'compression':hd.get('Content-Encoding')}
st,hd,b=get(U+'robots.txt'); R['robots']={'status':st,'sitemap_line':[l for l in b.decode().splitlines() if l.lower().startswith('sitemap')]}
st,hd,b=get(U+'sitemap.xml'); R['sitemap']={'status':st,'children':len(re.findall(rb'<sitemap>',b))}
st,hd,b=get('http://beeblend.co.uk/'); R['http_to_https']=st
try: st,hd,b=get('https://www.beeblend.co.uk/'); R['www']=st
except Exception as e: R['www']=str(e)[:80]
json.dump(R,open('out/func.json','w'),indent=1)
P
