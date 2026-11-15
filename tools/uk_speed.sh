set -x
mkdir -p out
python - <<'P'
import json,re
from playwright.sync_api import sync_playwright
R={}
def test(p,name,base,q,dev):
    ctx=dict(viewport={'width':1440,'height':900}) if dev=='desktop' else p.devices['iPhone 13']
    b=p.chromium.launch(); c=b.new_context(**ctx); pg=c.new_page()
    errs=[]; pg.on('console',lambda m: errs.append(m.text[:160]) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)[:160]))
    r={}
    pg.goto(base+'/'+q,wait_until='load',timeout=90000); pg.wait_for_timeout(3000)
    r['hero_before']=pg.evaluate("(()=>{const v=document.querySelector('.bb-hero video');return v?{src:v.currentSrc||v.getAttribute('src')||'',paused:v.paused}:null})()")
    try:
        btn=pg.locator('button:has-text("Accept")').first
        if btn.is_visible(): btn.click()
    except Exception: pass
    pg.mouse.move(400,400); pg.mouse.wheel(0,300); pg.wait_for_timeout(5000)
    r['hero_after']=pg.evaluate("(()=>{const v=document.querySelector('.bb-hero video');return v?{src:(v.currentSrc||'').slice(-60),paused:v.paused,ready:v.readyState,time:v.currentTime,playing:v.classList.contains('is-playing')}:null})()")
    for y in range(0,9000,600): pg.mouse.wheel(0,600); pg.wait_for_timeout(200)
    r['bee_videos']=pg.evaluate("[...document.querySelectorAll('video')].map(v=>({cls:v.className.slice(0,40),src:(v.currentSrc||'').slice(-50),paused:v.paused,ready:v.readyState}))")
    h=pg.content()
    r['h1']=pg.evaluate("[...document.querySelectorAll('h1')].map(e=>e.innerText.trim().slice(0,60))")
    r['imgs_no_alt']=pg.evaluate("[...document.querySelectorAll('img:not([alt])')].map(i=>i.src.slice(-70))")
    r['liquid_err']=len(re.findall(r'Liquid (syntax )?error',h,re.I))
    r['theme']=pg.evaluate("window.Shopify&&Shopify.theme&&Shopify.theme.id")
    r['footer_logo']=pg.evaluate("(()=>{const i=document.querySelector('footer img');return i?i.outerHTML.slice(0,220):null})()")
    prod=pg.evaluate("(()=>{const a=[...document.querySelectorAll('a[href*=\"/products/\"]')][0];return a?a.getAttribute('href').split('?')[0]:null})()")
    r['product']=prod
    if dev=='mobile':
        pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(500)
        try: pg.locator('summary.header__icon--menu').first.click(); pg.wait_for_timeout(800); r['menu_open']=pg.evaluate("!!document.querySelector('menu-drawer details[open], .menu-drawer-container[open]')")
        except Exception as e: r['menu_open']='ERR '+str(e)[:80]
    if prod:
        pg.goto(base+prod+q,wait_until='load',timeout=90000); pg.wait_for_timeout(2500)
        r['prod_h1']=pg.evaluate("[...document.querySelectorAll('h1')].map(e=>e.innerText.trim().slice(0,60))")
        r['prod_theme']=pg.evaluate("window.Shopify&&Shopify.theme&&Shopify.theme.id")
        try:
            pg.locator('form[action*="/cart/add"] [type=submit]').first.click(); pg.wait_for_timeout(3500)
            r['cart_count']=pg.evaluate("fetch('/cart.js').then(r=>r.json()).then(j=>j.item_count)")
        except Exception as e: r['cart_count']='ERR '+str(e)[:100]
    pg.goto(base+'/collections/all'+q,wait_until='load',timeout=90000); pg.wait_for_timeout(2000)
    r['coll_h1']=pg.evaluate("[...document.querySelectorAll('h1')].map(e=>e.innerText.trim().slice(0,60))")
    r['coll_products']=pg.evaluate("document.querySelectorAll('a[href*=\"/products/\"]').length")
    r['console_errors']=sorted(set(errs))[:15]
    b.close(); return r
with sync_playwright() as p:
    for name,base,q in (('draft','https://beeblend.co.uk','?preview_theme_id=200711209347'),('live','https://beeblend.co.uk','')):
        for dev in ('desktop','mobile'):
            try: R[f'{name}_{dev}']=test(p,name,base,q,dev)
            except Exception as e: R[f'{name}_{dev}']='FAIL '+str(e)[:300]
json.dump(R,open('out/func.json','w'),indent=1)
P
