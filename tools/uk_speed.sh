set -x
mkdir -p out
python - <<'P'
import json
from playwright.sync_api import sync_playwright
R={}
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome')
    for dev in ('desktop','mobile'):
        ctx=dict(viewport={'width':1440,'height':900}) if dev=='desktop' else p.devices['iPhone 13']
        c=b.new_context(**ctx); pg=c.new_page()
        vids=[]; pg.on('response',lambda r: vids.append((r.url[-60:],r.headers.get('content-length'))) if ('.mp4' in r.url or '.webm' in r.url) else None)
        pg.goto('https://beeblend.co.uk/?preview_theme_id=200711209347',wait_until='load',timeout=90000); pg.wait_for_timeout(3000)
        r={'before':pg.evaluate("(()=>{const v=document.querySelector('.bb-hero video');return {sd:v.dataset.sd.slice(-45),hd:v.dataset.hd.slice(-45),src:v.currentSrc}})()"),'video_requests_before':list(vids)}
        pg.mouse.move(300,300); pg.mouse.wheel(0,200); pg.wait_for_timeout(7000)
        r['after']=pg.evaluate("(()=>{const v=document.querySelector('.bb-hero video');return {src:v.currentSrc.slice(-45),paused:v.paused,t:v.currentTime,visible:v.classList.contains('is-playing'),err:v.error&&v.error.code}})()")
        el=pg.locator('.bbk__v').first; el.scroll_into_view_if_needed(); pg.wait_for_timeout(4000)
        r['beekeeper']=pg.evaluate("[...document.querySelectorAll('.bbk__v')].map(v=>({src:v.currentSrc.slice(-35),paused:v.paused,t:Math.round(v.currentTime*10)/10}))")
        r['video_requests']=vids[:10]
        R[dev]=r; c.close()
    b.close()
json.dump(R,open('out/func.json','w'),indent=1)
P
