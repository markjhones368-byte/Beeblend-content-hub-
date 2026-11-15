set -x
mkdir -p out
python - <<'P'
from playwright.sync_api import sync_playwright
U="https://beeblend.co.uk/?preview_theme_id=200711209347"
L="https://beeblend.co.uk/"
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,url in (('draft',U),('live',L)):
        for dev,ctx in (('desktop',dict(viewport={'width':1440,'height':900},device_scale_factor=1)),('mobile',p.devices['iPhone 13'])):
            c=b.new_context(**ctx); pg=c.new_page()
            pg.goto(url,wait_until='load',timeout=90000); pg.wait_for_timeout(4000)
            pg.screenshot(path=f'out/{name}_{dev}_top.png')
            if name=='draft':
                for y in range(0,20000,700): pg.mouse.wheel(0,700); pg.wait_for_timeout(250)
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(1500)
                pg.screenshot(path=f'out/{name}_{dev}_full.png',full_page=True)
            c.close()
    b.close()
P
ls -la out
