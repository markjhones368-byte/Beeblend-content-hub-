import json,glob,re,os
S={}
for f in sorted(glob.glob('out/*_mobile_*.json')+glob.glob('out/*_desktop_*.json')):
    try: j=json.load(open(f)); a=j['audits']; c=j['categories']
    except Exception as e: S[os.path.basename(f)]='ERR '+str(e)[:80]; continue
    r={k:(round(v['score']*100) if v.get('score') is not None else None) for k,v in c.items()}
    for m in ['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index']: r[m]=a[m].get('displayValue')
    r['bytes']=a['total-byte-weight'].get('displayValue'); r['dom']=a.get('dom-size',{}).get('displayValue')
    r['requests']=len(a.get('network-requests',{}).get('details',{}).get('items',[]))
    if '_1' in f:
        r['biggest']=[(i['url'][-70:],round(i['totalBytes']/1024)) for i in a['total-byte-weight']['details']['items'][:8]]
        r['third_party']=[((i.get('entity') or {}).get('text') if isinstance(i.get('entity'),dict) else i.get('entity'),round(i.get('blockingTime',0)),round(i.get('transferSize',0)/1024)) for i in a.get('third-party-summary',{}).get('details',{}).get('items',[])][:14]
        r['js_bootup']=[(i['url'][-70:],round(i.get('total',0))) for i in a.get('bootup-time',{}).get('details',{}).get('items',[])[:10]]
        for cat in ['seo','accessibility','best-practices']:
            if cat in c: r[cat+'_fail']=[(k,a[k].get('title')) for k in [x['id'] for x in c[cat]['auditRefs']] if a.get(k,{}).get('score') is not None and a[k]['score']<1]
        try: r['lcp_el']=a['largest-contentful-paint-element']['details']['items'][0]['items'][0]['node'].get('snippet')
        except Exception: pass
    S[os.path.basename(f)]=r
for n in ['home.html','draft.html']:
    h=open('out/'+n,encoding='utf-8',errors='replace').read()
    S[n]={'kb':len(h)//1024,'liquid_errors':re.findall(r'Liquid (?:syntax )?error[^<]{0,160}',h)[:5],'hero':(re.search(r'<section class="bb bb-hero".{0,1500}',h,re.S).group(0)[:1500] if 'bb-hero' in h else 'NO HERO'),
     'gtag_ids':re.findall(r'(?:id=|config\W+)((?:G|AW|GT|GTM)-[A-Z0-9]+)',h),'fb_init':re.findall(r"fbq\('init',\s*'(\d+)'",h),
     'script_hosts':sorted(set(re.findall(r'<script[^>]+src="(?:https?:)?//([^/"]+)',h))),'app_ext':sorted(set(re.findall(r'/extensions/[^/]+/([a-z0-9-]+)/',h))),
     'webmcp':re.findall(r'[^"\'\s<>]*webmcp[^"\'\s<>]*',h)[:4]}
css=open('out/bb-premium.orig.css').read() if os.path.exists('out/bb-premium.orig.css') else ''
S['css']={'len':len(css),'imports':css.count('@import')}
if css:
    new=re.sub(r"@import url\('https://fonts\.googleapis\.com/css2\?family=Figtree[^']*'\);",'',css,count=1)
    open('out/bb-premium.css','w').write(new); S['css']['new_len']=len(new)
json.dump(S,open('out/uk_summary.json','w'),indent=1)
