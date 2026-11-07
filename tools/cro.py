import asyncio, json, re
from playwright.async_api import async_playwright
P={'BeeBlend':'https://beeblend.in/products/lychee-honey','HoneyVeda':'https://honeyveda.in/products/lychee-honey','Indigenous Honey':'https://indigenoushoney.com/products/indigenous-honey-raw-pure-litchi-honey',
'Two Brothers':'https://twobrothersindiashop.com/products/acacia-honey-raw','Organic India':'https://organicindia.com/products/multi-floral-honey','BeeBlend home':'https://beeblend.in/'}
SIG={'GoKwik checkout':r'gokwik','Shiprocket/Fastrr checkout':r'fastrr|shiprocket','Razorpay Magic checkout':r'magic-checkout|razorpay','Simpl pay-later':r'getsimpl|simpl\.','COD mentioned':r'cash on delivery|\bcod\b','WhatsApp button':r'wa\.me|api\.whatsapp|whatsapp','Judge.me':r'judge\.me|judgeme','Fera reviews':r'fera\.ai','Loox':r'loox','Subscriptions (Appstle/Recharge/Seal/Loop)':r'appstle|rechargepayments|sealsubscriptions|loopwork|subscribe & save|subscribe and save','Bundles app (Kaching/Fast Bundle/Bundler/Rebuy)':r'kaching|fastbundle|fast-bundle|bundler|rebuy','Frequently bought together':r'frequently bought','Loyalty (Nector/Smile/Growave/Flits)':r'nector|smile\.io|growave|flits','Klip':r'klip','Free shipping message':r'free (shipping|delivery)','Buy-more-save tiers':r'buy \d|pack of \d|save \d+%|combo'}
async def main():
    out={}
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(**p.devices['iPhone 13'])
        for n,u in P.items():
            pg=await ctx.new_page(); d={'url':u}
            try:
                await pg.goto(u,wait_until='domcontentloaded',timeout=60000); await pg.wait_for_timeout(6000)
                fn=re.sub(r'\W+','_',n.lower())
                await pg.screenshot(path=f'm_{fn}_fold.jpg',type='jpeg',quality=70)
                await pg.screenshot(path=f'm_{fn}_full.jpg',type='jpeg',quality=45,full_page=True)
                h=(await pg.content()).lower(); t=await pg.inner_text('body')
                d['signals']={k:bool(re.search(v,h)) for k,v in SIG.items()}
                d['top_text']=' '.join(t.split())[:1400]
                d['height']=await pg.evaluate('document.body.scrollHeight')
                d['reqs']=await pg.evaluate('performance.getEntriesByType("resource").length')
                d['bytes_kb']=await pg.evaluate('Math.round(performance.getEntriesByType("resource").reduce((a,r)=>a+(r.transferSize||0),0)/1024)')
                d['lcp_ms']=await pg.evaluate('new Promise(r=>{new PerformanceObserver(l=>{const e=l.getEntries();r(Math.round(e[e.length-1].startTime))}).observe({type:"largest-contentful-paint",buffered:true});setTimeout(()=>r(null),3000)})')
            except Exception as e: d['err']=str(e)[:200]
            out[n]=d; await pg.close()
        await b.close()
    json.dump(out,open('cro.json','w'),indent=1)
asyncio.run(main())
