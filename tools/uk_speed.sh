set -x
npm i -g lighthouse@12.6.1 >/dev/null 2>&1
export CHROME_PATH=$(python -c "import glob,os;print(sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome')))[-1])")
mkdir -p out
DRAFT="https://eptqzg-e5.myshopify.com/?preview_theme_id=200711209347&_fd=0&pb=0"
APPS='--blocked-url-patterns=*sealsubscriptions* --blocked-url-patterns=*bitbybit* --blocked-url-patterns=*accounts.google.com/gsi* --blocked-url-patterns=*notify-me.io* --blocked-url-patterns=*klip*'
TAGS='--blocked-url-patterns=*googletagmanager* --blocked-url-patterns=*connect.facebook.net* --blocked-url-patterns=*doubleclick* --blocked-url-patterns=*google-analytics*'
run(){ timeout 150 lighthouse "$DRAFT" --quiet --max-wait-for-load=40000 --chrome-flags="--headless=new --no-sandbox" $3 --output=json --output-path=out/$1_$2.json --only-categories=performance || true; }
for i in 1 2; do
 run A_draft desktop_$i "--preset=desktop"
 run C_noapps desktop_$i "--preset=desktop $APPS"
 run D_noapps_notags desktop_$i "--preset=desktop $APPS $TAGS"
 run A_draft mobile_$i ""
 run C_noapps mobile_$i "$APPS"
 run D_noapps_notags mobile_$i "$APPS $TAGS"
done
python - <<'P'
import json,glob,os
S={}
for f in sorted(glob.glob('out/*.json')):
    try: j=json.load(open(f)); a=j['audits']
    except Exception as e: S[os.path.basename(f)]='ERR'; continue
    S[os.path.basename(f)]={'perf':round(j['categories']['performance']['score']*100),'lcp':a['largest-contentful-paint']['displayValue'],'tbt':a['total-blocking-time']['displayValue'],'si':a['speed-index']['displayValue'],'cls':a['cumulative-layout-shift']['displayValue'],'bytes':a['total-byte-weight']['displayValue'],'reqs':len(a['network-requests']['details']['items'])}
json.dump(S,open('out/uk_summary.json','w'),indent=1)
P
