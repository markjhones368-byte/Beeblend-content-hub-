set -x
npm i -g lighthouse@12.6.1 >/dev/null 2>&1
export CHROME_PATH=$(python -c "import glob,os;print(sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome')))[-1])")
mkdir -p out
DRAFT="https://eptqzg-e5.myshopify.com/?preview_theme_id=200711209347&_fd=0&pb=0"
LIVE="https://beeblend.co.uk/"
curl -sL -A "Mozilla/5.0 Chrome/124" "$DRAFT" -o out/draft.html
curl -sL -A "Mozilla/5.0 Chrome/124" "$LIVE" -o out/live.html
run(){ timeout 170 lighthouse "$2" --quiet --max-wait-for-load=40000 --chrome-flags="--headless=new --no-sandbox" $3 --output=json --output-path=out/$1.json || true; }
for i in 1 2 3; do run draft_desktop_$i "$DRAFT" "--preset=desktop"; done
run live_desktop_1 "$LIVE" "--preset=desktop"
run draft_mobile_1 "$DRAFT" ""
python - <<'P'
import json,glob,os,re
S={}
for f in sorted(glob.glob('out/*.json')):
    n=os.path.basename(f)
    try: j=json.load(open(f)); a=j['audits']; c=j['categories']
    except Exception as e: S[n]='ERR'; continue
    r={k:round(v['score']*100) for k,v in c.items() if v.get('score') is not None}
    for m in ['largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index','total-byte-weight','dom-size','bootup-time','mainthread-work-breakdown']: r[m]=a[m].get('displayValue')
    # all scored perf-related audits that fail (GTmetrix Structure = these)
    r['perf_fail']=sorted([(round(v['score']*100),k,v.get('displayValue','')) for k,v in a.items() if v.get('score') is not None and v['score']<0.9 and v.get('scoreDisplayMode') in ('binary','numeric','metricSavings')])[:30]
    for cat in ['seo','accessibility','best-practices']:
        if cat in c: r[cat+'_fail']=[k for k in [x['id'] for x in c[cat]['auditRefs']] if a.get(k,{}).get('score') is not None and a[k]['score']<1]
    if 'image-alt' in a: r['img_alt_items']=[i.get('node',{}).get('snippet','')[:160] for i in (a['image-alt'].get('details') or {}).get('items',[])]
    S[n]=r
for n in ['draft.html','live.html']:
    h=open('out/'+n,encoding='utf-8',errors='replace').read()
    S[n]={'kb':len(h)//1024,'h1':[' '.join(re.sub('<[^>]+>',' ',x).split())[:70] for x in re.findall(r'<h1[^>]*>(.*?)</h1>',h,re.S)],
      'liquid_errors':re.findall(r'Liquid (?:syntax )?error[^<]{0,160}',h)[:5],'font_import':'@import' in h and 'fonts.googleapis.com/css2?family=Figtree' in h,
      'imgs_no_alt':[i[:150] for i in re.findall(r'<img\b[^>]*>',h) if not re.search(r'\balt=',i)][:6],
      'video_autoplay':len(re.findall(r'<video[^>]*autoplay',h)),'preview':'200711209347' in h,
      'title':(re.search(r'<title>(.*?)</title>',h,re.S) or [0,''])[1].strip(),'desc':(re.search(r'name="description" content="([^"]*)"',h) or [0,''])[1]}
json.dump(S,open('out/uk_summary.json','w'),indent=1)
P
