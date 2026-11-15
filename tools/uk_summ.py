import json,glob,re,os
S={}
for f in sorted(glob.glob('out/lh_*.json')):
    try: j=json.load(open(f))
    except Exception as e: S[f]=str(e); continue
    a=j['audits']; c=j['categories']
    r={k:round(v['score']*100) if v.get('score') is not None else None for k,v in c.items()}
    for m in ['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','interactive']:
        r[m]=a[m].get('displayValue')
    try: r['lcp_el']=a['largest-contentful-paint-element']['details']['items'][0]['items'][0]['node'].get('snippet')
    except Exception: r['lcp_el']=None
    r['bytes']=a['total-byte-weight'].get('displayValue')
    r['biggest']=[(i['url'][-90:],round(i['totalBytes']/1024)) for i in a['total-byte-weight']['details']['items'][:12]]
    tp=a.get('third-party-summary',{}).get('details',{}).get('items',[])
    r['third_party']=[(i.get('entity') if isinstance(i.get('entity'),str) else (i.get('entity') or {}).get('text'),round(i.get('blockingTime',0)),round(i.get('transferSize',0)/1024)) for i in tp][:15]
    bt=a.get('bootup-time',{}).get('details',{}).get('items',[])
    r['js_bootup']=[(i['url'][-80:],round(i.get('total',0)),round(i.get('scripting',0))) for i in bt[:12]]
    r['dom']=a.get('dom-size',{}).get('displayValue')
    if 'seo' in c:
        for cat in ['seo','accessibility','best-practices']:
            ids=[x['id'] for x in c[cat]['auditRefs']]
            r[cat+'_fail']=[k for k in ids if a.get(k,{}).get('score') is not None and a[k]['score']<1]
    S[os.path.basename(f)]=r
h=open('out/home.html',encoding='utf-8',errors='replace').read()
S['html']={'kb':len(h)//1024,
 'videos':[v[:600] for v in re.findall(r'<video[^>]*>.*?</video>',h,re.S)[:6]],
 'video_src':sorted(set(re.findall(r'(?:src|data-src)="([^"]+\.(?:mp4|webm|m3u8)[^"]*)"',h))),
 'gtag_ids':re.findall(r'(?:id=|config\W+)((?:G|AW|GT|GTM)-[A-Z0-9]+)',h),
 'fb_init':re.findall(r"fbq\('init',\s*'(\d+)'",h),
 'script_hosts':sorted(set(re.findall(r'<script[^>]+src="(?:https?:)?//([^/"]+)',h))),
 'app_blocks':sorted(set(re.findall(r'/extensions/[^/]+/([a-z0-9-]+)/',h))),
 'webmcp':re.findall(r'[^"\'\s]*webmcp[^"\'\s]*',h)[:5],
 'product_js':re.findall(r'[\w-]+-honey\.js[^"\'\s]*',h)[:10],
 'preload':re.findall(r'<link[^>]+rel="preload"[^>]*>',h)[:10],
 'title':(re.search(r'<title>(.*?)</title>',h,re.S).group(1).strip() if '<title>' in h else '')}
S['robots']=open('out/robots.txt').read()[:600]
json.dump(S,open('out/uk_summary.json','w'),indent=1)
