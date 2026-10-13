import json,re,os,shutil
B=os.path.dirname(os.path.abspath(__file__))
SRC=B+'/theme'; CUR=B+'/ukcur'; OUT=B+'/uktheme'
shutil.rmtree(OUT,ignore_errors=True); shutil.copytree(SRC,OUT)
def load(p):
    s=open(p).read(); s=re.sub(r'^\s*/\*.*?\*/','',s,flags=re.S); return json.loads(s)
def save(rel,d):
    with open(OUT+'/'+rel,'w') as f: json.dump(d,f,ensure_ascii=False,indent=1)
def T(rel): return load(OUT+'/'+rel)

# ---------- UK facts ----------
IG='https://www.instagram.com/beeblenduk/'; TT='https://www.tiktok.com/@beeblend'
GLOBAL={"include_schema":True,"logo":"shopify://shop_images/beeblend-logo.svg","instagram":IG,"facebook":"","youtube":"","phone":"+44 7767967707","email":"support@beeblend.co.uk"}
DELIVERY="<p>Orders are processed within 1–2 business days (Monday–Friday). UK Standard Delivery takes 3–5 business days and is free on orders over £40 (otherwise £3.99). UK Express Delivery takes 1–2 business days (£6.99). You'll get tracking details by email once your order ships. See <a href=\"/pages/shipping-delivery\">shipping &amp; delivery</a>.</p>"
DAMAGED="<p>Email support@beeblend.co.uk within 48 hours of delivery with your order number and a photo, and we'll put it right quickly.</p>"
GUIDE='<a href="/pages/which-honey-should-i-choose">which honey should I choose?</a>'
TRUST=[("drop","Raw & unheated"),("pin","Single-origin"),("leaf","No added sugar or syrups"),("truck","Free UK delivery over £40"),("shield","Secure checkout")]
def trust_section():
    bl={f"t{i+1}":{"type":"item","settings":{"icon":ic,"text":tx}} for i,(ic,tx) in enumerate(TRUST)}
    return {"type":"bb-trust-bar","blocks":bl,"block_order":list(bl),"settings":{}}
def faq(items,heading="Questions, answered",bg="paper"):
    bl={f"q{i+1}":{"type":"qa","settings":{"q":q,"a":a}} for i,(q,a) in enumerate(items)}
    return {"type":"bb-faq","blocks":bl,"block_order":list(bl),"settings":{"heading":heading,"open_first":True,"bg":bg}}

# ---------- layout / config: keep the UK store's own versions ----------
for rel in ['layout/theme.liquid','snippets/meta-tags.liquid','config/settings_data.json','sections/footer-group.json']:
    shutil.copy(CUR+'/'+rel, OUT+'/'+rel)
hg=T('sections/header-group.json'); ukhg=load(CUR+'/sections/header-group.json')
for k,v in ukhg['sections'].items(): hg['sections'][k]=v  # UK announcement bar + header settings
save('sections/header-group.json',hg)

# ---------- section code tweaks for the UK ----------
p=OUT+'/sections/bb-global.liquid'; s=open(p).read()
s=s.replace('"areaServed":"IN","availableLanguage":["English","Hindi","Gujarati"]','"areaServed":"GB","availableLanguage":["English"]')
s=s.replace('"default": "https://www.instagram.com/beeblendindia/"','"default": "'+IG+'"').replace('"default": "+91-7984373799"','"default": "+44 7767967707"').replace('"default": "info@beeblend.in"','"default": "support@beeblend.co.uk"')
open(p,'w').write(s)
p=OUT+'/sections/bb-product-assurance.liquid'; s=open(p).read()
s=s.replace('"title": "Ships across India", "text": "Edit delivery time"','"title": "Free UK delivery", "text": "On orders over £40"').replace('"text": "UPI, cards, COD"','"text": "Cards, Apple Pay, Google Pay"')
open(p,'w').write(s)
p=OUT+'/sections/bb-trust-bar.liquid'; s=open(p).read(); s=s.replace('"Ships across India"','"Free UK delivery over £40"'); open(p,'w').write(s)
# TikTok card for the social section
p=OUT+'/sections/bb-social.liquid'; s=open(p).read()
s=s.replace('grid-template-columns:repeat(3,minmax(0,1fr));gap:1.6rem;margin-bottom','grid-template-columns:repeat({{ n_links | at_least: 1 }},minmax(0,1fr));gap:1.6rem;margin-bottom')
s=s.replace("{{ 'bb-premium.css' | asset_url | stylesheet_tag }}","{{ 'bb-premium.css' | asset_url | stylesheet_tag }}\n{%- liquid\n  assign n_links = 0\n  if section.settings.instagram != blank\n    assign n_links = n_links | plus: 1\n  endif\n  if section.settings.tiktok != blank\n    assign n_links = n_links | plus: 1\n  endif\n  if section.settings.youtube != blank\n    assign n_links = n_links | plus: 1\n  endif\n  if section.settings.facebook != blank\n    assign n_links = n_links | plus: 1\n  endif\n-%}",1)
s=s.replace("  #bb-soc-{{ section.id }} .bb-soc__link--fb{","  #bb-soc-{{ section.id }} .bb-soc__link--tt{--brand:#111;--glow:rgba(0,0,0,.3)}\n  #bb-soc-{{ section.id }} .bb-soc__link--fb{",1)
s=s.replace("    #bb-soc-{{ section.id }} .bb-soc__link--fb:hover .bb-logo__mark{fill:#1877F2}","    #bb-soc-{{ section.id }} .bb-soc__link--fb:hover .bb-logo__mark{fill:#1877F2}\n    #bb-soc-{{ section.id }} .bb-soc__link--tt:hover .bb-logo__fill{fill:#fff}",1)
TTLOGO='{%- capture tt_logo -%}<svg class="bb-logo bb-logo--tt" viewBox="0 0 24 24" aria-hidden="true"><path class="bb-logo__fill" fill="#111" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>{%- endcapture -%}\n'
s=s.replace('{%- capture fb_logo -%}',TTLOGO+'{%- capture fb_logo -%}',1)
TTCARD='''      {%- if section.settings.tiktok != blank -%}
        <a class="bb-soc__link bb-soc__link--tt bb-card" href="{{ section.settings.tiktok }}" target="_blank" rel="noopener" aria-label="BeeBlend on TikTok">{{ tt_logo }}<div><div class="bb-soc__name">TikTok</div><div class="bb-soc__handle">{{ section.settings.tiktok_handle }}</div></div><div class="bb-soc__cta"><span>Recipes and honey moments</span><i aria-hidden="true">&rarr;</i></div></a>
      {%- endif -%}
      {%- if section.settings.youtube != blank -%}'''
s=s.replace('      {%- if section.settings.youtube != blank -%}',TTCARD,1)
s=s.replace('{ "type": "text", "id": "youtube", "label": "YouTube URL" },','{ "type": "text", "id": "tiktok", "label": "TikTok URL" },\n    { "type": "text", "id": "tiktok_handle", "label": "TikTok handle", "default": "@beeblend" },\n    { "type": "text", "id": "youtube", "label": "YouTube URL" },',1)
s=s.replace('"default": "https://www.instagram.com/beeblendindia/"','"default": "'+IG+'"').replace('"label": "Instagram handle", "default": "@beeblendindia"','"label": "Instagram handle", "default": "@beeblenduk"').replace('"default": "BeeBlend India"','"default": "BeeBlend"').replace('"label": "YouTube handle", "default": "@beeblendindia"','"label": "YouTube handle"')
open(p,'w').write(s)

# ---------- drop India-only templates; bring over UK-only page templates ----------
for rel in ['templates/collection.sachet.json','templates/page.socials.json','templates/page.why-beeblend.json']:
    os.remove(OUT+'/'+rel)
for rel in ['templates/page.privacy-policy.json','templates/page.shipping-delivery.json','templates/page.returns-refunds.json','templates/page.terms-conditions.json','templates/page.honey-guide.json','templates/page.honey-pairing-guide.json']:
    shutil.copy(CUR+'/'+rel, OUT+'/'+rel)

# ---------- homepage ----------
d=T('templates/index.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL)
S['hero']['settings'].update({"video":"shopify://files/videos/video-bg.mp4","image":"shopify://shop_images/honey_drizzle_1.jpg","heading":"Raw honey that tastes of where it's from","subheading":"Rare, single-origin raw honeys from Kashmir, the Himalayas and beyond. Unheated, nothing added, delivered across the UK.","btn1_label":"Shop raw honey","btn1_link":"shopify://collections/jar","btn2_label":"Find your honey","btn2_link":"shopify://pages/which-honey-should-i-choose"})
S['trust']=trust_section()
S['hero_product']={"type":"bb-feature-product","settings":{"product":"golden-nut-honey","layout":"spotlight","image":"shopify://shop_images/Golden_Nut_Honey_with_premium_nuts_and_dried_fruit.png","asset":"","badge":"Gift favourite","eyebrow":"Golden Nut Infusion","heading":"Raw honey, slow-infused with almonds, cashews and dates.","text":"Our most indulgent jar: creamy, nutty and naturally sweet, with real nut pieces in every spoonful. Made for toast, porridge, cheese boards, and for giving.","stat1_num":"","stat1_label":"","stat2_num":"160g","stat2_label":"or 250g","stat3_num":"No","stat3_label":"added sugar","spec_extra":"Contains tree nuts","btn_label":"Add to cart","link_label":"See the jar","note":"Raw honey · No added sugar · Free UK delivery over £40","bg":"paper"}}
S['bestsellers']['settings'].update({"heading":"Best-selling raw honey","text":"Seven single-origin honeys in 160g and 250g jars. Pick a size and add to cart straight from here.","button_label":"Shop all raw honey"})
S['reviews'].pop('disabled',None)
jm=S['reviews']['blocks']['jm']['settings']; jm.update({"show_sample_reviews":False,"reviews_selection":"all"})
S['reviews']['settings'].update({"heading":"What our customers say"})
S['gifting']['settings'].update({"text":"Honey hampers for Christmas, birthdays, weddings and corporate gifting, packed and ready to give.","btn_link":"shopify://pages/gifting"})
S['social']['settings'].update({"text":"Recipes, behind-the-scenes and first looks at new honeys.","instagram":IG,"instagram_handle":"@beeblenduk","tiktok":TT,"tiktok_handle":"@beeblend","youtube":"","youtube_handle":"","facebook":"","facebook_handle":""})
S['guides']['settings'].update({"blog":"recipes","heading":"Recipes from the BeeBlend kitchen"})
S['faq']=faq([
 ("My honey has gone thick and grainy. Is it spoiled?","<p>No. Raw honey naturally crystallises over time, especially in cooler weather. It's a sign it hasn't been heated. Stand the closed jar in warm (not boiling) water and stir to make it runny again.</p>"),
 ("What does single-origin mean?","<p>Each jar comes from one region and one main flower source, so every honey has its own colour, aroma and taste.</p>"),
 ("Is BeeBlend honey pure and raw?","<p>Yes. Every jar is pure honey with nothing added: no sugar, syrups or preservatives. It's extracted and gently filtered but never heated, which is why it crystallises naturally.</p>"),
 ("Which honey should I buy first?","<p>For tea and everyday use, start with <a href=\"/products/kashmiri-acacia-honey\">Kashmiri Acacia</a> or <a href=\"/products/himalayan-multifloral-honey\">Himalayan Multi-Flora</a>. For cooking, try <a href=\"/products/sesame-honey\">Black Sesame</a>. Still unsure? Read "+GUIDE+"</p>"),
 ("How should I store it?","<p>Keep the lid tight and store at room temperature, away from direct sunlight. No need to refrigerate.</p>"),
 ("How fast is UK delivery?",DELIVERY),
 ("Do you ship outside the UK?","<p>Yes. International delivery takes 7–14 business days, with shipping calculated at checkout. Customs duties and taxes are paid by the recipient.</p>"),
 ("Can I order for gifting or in bulk?","<p>Yes. Visit our <a href=\"/pages/gifting\">gifting page</a> or <a href=\"/pages/contact\">contact us</a> for corporate and bulk orders.</p>")],"Raw honey questions, answered")
save('templates/index.json',d)

# ---------- product ----------
d=T('templates/product.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL,include_schema=False)
S['main']['blocks']['ship_note']['settings']['text']="✓ Dispatched in 1–2 business days  ·  ✓ Free UK delivery over £40  ·  ✓ Secure checkout"
S['assure']['blocks']['b4']['settings'].update({"title":"Free UK delivery","text":"On orders over £40"})
S['faq']=faq([
 ("Is BeeBlend honey 100% pure?","<p>Yes. Our raw honeys are 100% honey, with no added sugar, artificial preservatives, colours or flavours. Golden Nut Infusion also contains almonds, cashews and dates.</p>"),
 ("Is it raw?","<p>Yes. It's unheated and minimally handled to keep its natural taste and aroma.</p>"),
 ("My honey has gone thick and grainy. Is it spoiled?","<p>No. Raw honey naturally crystallises over time, especially in cooler weather. Stand the closed jar in warm (not boiling) water and stir to make it runny again.</p>"),
 ("Can I use it instead of sugar?","<p>Yes. Use it in tea, porridge, yoghurt, dressings, baking and cooking. Honey is sweeter than sugar, so you'll need a little less.</p>"),
 ("How fast is UK delivery?",DELIVERY),
 ("What if my jar arrives damaged?",DAMAGED),
 ("Is honey suitable for babies?","<p>No. Honey is not suitable for infants under 12 months.</p>")])
save('templates/product.json',d)

# ---------- collection ----------
d=T('templates/collection.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL,include_schema=False)
S['trust']=trust_section()
S['faq']=faq([
 ("What does single-origin honey mean?","<p>Each jar comes from one region and one main flower source, so every honey has its own colour, aroma and taste.</p>"),
 ("Which honey should I start with?","<p>For everyday use, try Lychee Blossom or Kashmiri Acacia: both are light and smooth. For gifting, Golden Nut Infusion is our most indulgent jar. Or read "+GUIDE+"</p>"),
 ("My honey has gone thick and grainy. Is it spoiled?","<p>No. Raw honey naturally crystallises over time, especially in cooler weather. Stand the closed jar in warm (not boiling) water and stir to make it runny again.</p>"),
 ("How fast is UK delivery?",DELIVERY)],bg="white")
save('templates/collection.json',d)

# ---------- contact ----------
d=T('templates/page.contact.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL,include_schema=False)
S['hero']['settings'].update({"text":"Order questions, gifting and bulk enquiries, or help choosing a honey. We're happy to help."})
S['form']['blocks']={"o1":{"type":"office","settings":{"title":"BeeBlend UK","address":"<p>BeeBlend Ltd<br/>5 Kew Road, Richmond, London, TW9 2PR</p>","phone":"+44 7767967707","email":"support@beeblend.co.uk"}}}
S['form']['block_order']=["o1"]
S['faq']=faq([
 ("How fast is UK delivery?",DELIVERY),
 ("What if my jar arrives damaged?",DAMAGED),
 ("Do you ship outside the UK?","<p>Yes. International delivery takes 7–14 business days, with shipping calculated at checkout. Customs duties and taxes are paid by the recipient.</p>"),
 ("Can I return an order?","<p>We accept unopened, unused items within 14 days of delivery. See our <a href=\"/pages/returns-refunds\">returns &amp; refunds policy</a>.</p>"),
 ("Can I order in bulk?","<p>Yes. Use the form above with your quantity and we'll get back to you with pricing.</p>")])
save('templates/page.contact.json',d)

# ---------- gifting ----------
d=T('templates/page.gifting.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL,include_schema=False)
S['hero']['settings']['text']="Christmas hampers, corporate gifts and personalised sets, packed beautifully and delivered across the UK."
S['cards']['blocks']['c2']['settings']['sub']="Christmas, birthdays, weddings and more"
S['steps']['blocks']['s3']['settings']['text']="To one address or many, across the UK."
S.pop('hero_product',None); d['order']=[k for k in d['order'] if k!='hero_product']
S['faq']=faq([
 ("Do you offer bulk or corporate pricing?","<p>Yes. Send us your quantity and budget through our <a href=\"/pages/contact\">contact page</a> and we'll share options and pricing.</p>"),
 ("Can you personalise the packaging?","<p>Yes, personalised gift sets are available. Tell us what you'd like printed when you get in touch.</p>"),
 ("Can you deliver to multiple addresses?","<p>Yes. Share the address list with us and we'll handle the rest.</p>"),
 ("When should I order for Christmas?","<p>For corporate and bulk orders, get in touch three to four weeks ahead so there's time to pack and dispatch. Individual orders are processed within 1–2 business days.</p>"),
 ("How fast is UK delivery?",DELIVERY)],"Gifting questions",bg="white")
save('templates/page.gifting.json',d)

# ---------- about ----------
d=T('templates/page.about-us.json'); S=d['sections']
S['bb_global']['settings']=dict(GLOBAL,include_schema=False)
S['hero']['settings']['text']="Most honey is blended from many sources and heated so it pours forever and tastes the same. Ours isn't. Every BeeBlend honey comes from a single region, stays separate from hive to jar, and is never heated. So a spoon of Kashmiri Acacia tastes nothing like Himalayan Multi-Flora. That's the whole point."
S['trust']=trust_section()
save('templates/page.about-us.json',d)

# ---------- health ----------
d=T('templates/page.health-benefits.json'); S=d['sections']
S['bb_global']={"type":"bb-global","settings":dict(GLOBAL,include_schema=False)}
S['hero']={"type":"bb-page-hero","settings":{"eyebrow":"Honey & everyday life","heading":"Why people choose raw honey","text":"Honey is a natural sweetener made by bees from flower nectar. Here's what makes raw, single-origin honey different, and how to enjoy it every day.","crumbs":True,"bg":"paper","image":"shopify://shop_images/honey_drizzle_1.jpg","fit":"cover"}}
S.pop('image_banner_ATFrQC',None)
S['faq']=faq([
 ("Is honey healthier than sugar?","<p>Honey is still a sugar and should be enjoyed in moderation. People choose it because it's a single, natural ingredient with its own flavour, and because it's sweeter than sugar, so a little goes a long way.</p>"),
 ("What does raw mean?","<p>Raw honey is extracted and gently filtered but not heated, so it keeps its natural aroma and pollen. It crystallises over time, which is normal.</p>"),
 ("Is honey suitable for everyone?","<p>Honey is not suitable for infants under 12 months. If you have diabetes or another medical condition, check with your doctor before adding honey to your diet. Golden Nut Infusion contains tree nuts.</p>"),
 ("How do I use honey every day?","<p>Stir it into tea or warm water once it has cooled slightly, drizzle it over porridge and yoghurt, or use it in dressings and baking. See our "+'<a href="/pages/honey-pairing-guide">honey pairing guide</a>'+".</p>")],"Good to know")
d['order']=['bb_global','hero','multicolumn_8GhCWm','faq']
S.pop('main',None)
save('templates/page.health-benefits.json',d)


# ---------- v2: premium UK layer (honey picker hero, marquee, flavour journey, taste profile) ----------
for root_,_,files in os.walk(B+'/ukextra'):
    for f in files:
        src=os.path.join(root_,f); rel=os.path.relpath(src,B+'/ukextra')
        os.makedirs(os.path.dirname(OUT+'/'+rel),exist_ok=True); shutil.copy(src,OUT+'/'+rel)
p=OUT+'/sections/bb-global.liquid'; s=open(p).read()
s=s.replace("family=Figtree:wght@400;500;600;700&family=Young+Serif","family=Figtree:wght@400;500;600;700&family=Fraunces:opsz,wght,SOFT,WONK@9..144,400..800,0..100,0..1&family=Young+Serif",1)
s=s.replace("{{ 'bb-motion.css' | asset_url | stylesheet_tag }}","{{ 'bb-motion.css' | asset_url | stylesheet_tag }}\n{{ 'uk-skin.css' | asset_url | stylesheet_tag }}",1)
assert 'uk-skin.css' in s and 'Fraunces' in s
open(p,'w').write(s)
HONEYS=[
 ("kashmiri-acacia-honey","Kashmiri Acacia","#F4DE9A","dark","Light and floral","Kashmir valley","Light, clean and delicately sweet, with a hint of vanilla. It sweetens tea without changing its taste.","Tea, Lemon water, Yoghurt, Soft cheese"),
 ("mustard-honey","Yellow Mustard","#EFC650","dark","Mild, turns creamy","From mustard blossom","Mild and floral with a gentle warmth. It turns naturally thick and creamy, a sign it hasn't been heated.","Toast, Dressings, Mature cheddar, Glazes"),
 ("lychee-honey","Lychee Blossom","#E3B04B","dark","Fragrant and fruity","From lychee blossom","Fragrant and fruity, with soft rose-like notes. One of the most aromatic honeys we make.","Strawberries, Pancakes, Iced tea, Goat cheese"),
 ("himalayan-multifloral-honey","Himalayan Multi-Flora","#CF8E2A","dark","Wildflower, gently spiced","High-altitude Himalayan regions","Wildflower sweetness with herbal, gently spiced notes and a clean finish. Our everyday honey.","Porridge, Everyday tea, Baking, Granola"),
 ("fennel-honey","Wild Fennel","#B06E1E","light","Soft aniseed warmth","Mediterranean region","A soft aniseed aroma and warm herbal sweetness. Distinctive without being overpowering.","Herbal tea, Ricotta, Roast roots, Vinaigrettes"),
 ("golden-nut-honey","Golden Nut","#A8742F","light","With almonds, cashews and dates","Raw honey, almonds, cashews and dates","Raw honey slow-infused with almonds, cashews and dates. Creamy, nutty and rich. Contains tree nuts.","Toast, Ice cream, Porridge, Cheese boards"),
 ("sesame-honey","Black Sesame","#7E4614","light","Toasted and nutty","From sesame blossom","Toasted, nutty and caramel-deep, with a savoury edge that holds up in cooking.","Salmon glaze, Noodles, Aged cheese, Stir-fries"),
]
d=T('templates/index.json'); S=d['sections']
hb={f"h{i+1}":{"type":"honey","settings":{"product":h,"name":nm,"note":note,"colour":c,"ink":ink}} for i,(h,nm,c,ink,note,o,notes,pairs) in enumerate(HONEYS)}
S['hero']={"type":"uk-hero","blocks":hb,"block_order":list(hb),"settings":{"heading":"Raw honey that tastes of where it's from","text":"Seven single-origin honeys, raw and never heated, delivered across the UK. Pick one to meet it.","btn1_label":"Shop raw honey","btn1_link":"shopify://collections/jar","btn2_label":"Help me choose","btn2_link":"shopify://pages/which-honey-should-i-choose"}}
mk=["Free UK delivery over £40","Raw and never heated","One flower, one region","Dispatched in 1–2 working days","Nothing added, ever"]
mb={f"m{i+1}":{"type":"item","settings":{"text":t}} for i,t in enumerate(mk)}
S['marquee']={"type":"uk-marquee","blocks":mb,"block_order":list(mb),"settings":{"bg":"#1F3A2E","fg":"#FFF8E8","accent":"#F2C14E","speed":45}}
jb={f"j{i+1}":{"type":"honey","settings":{"product":h,"name":nm,"colour":c,"ink":ink,"origin":o,"notes":notes,"pairs":pairs}} for i,(h,nm,c,ink,note,o,notes,pairs) in enumerate(HONEYS)}
S['journey']={"type":"uk-flavour-journey","blocks":jb,"block_order":list(jb),"settings":{"heading":"Seven honeys, from light to dark","text":"Every honey takes its colour and taste from the flowers the bees visited. Start with pale Kashmiri Acacia and finish with deep Black Sesame."}}
for k in ['trust','spectrum','hero_product','story']: S.pop(k,None)
d['order']=['bb_global','hero','bestsellers','marquee','journey','compare','reels','reviews','gifting','social','guides','faq']
save('templates/index.json',d)
d=T('templates/product.json')
d['sections']['taste']={"type":"uk-taste-profile","settings":{"heading":"How it tastes"}}
o=d['order']; o.insert(o.index('main')+1,'taste')
save('templates/product.json',d)

# ---------- final scrub ----------
bad=re.compile(r'(?i)india|indian|₹|\+91|beeblend\.in\b|beeblendindia|diwali|rakhi|pure-honey-collection|/blogs/news|info@beeblend\.in')
for root,_,files in os.walk(OUT+'/templates'):
    for f in files:
        t=open(os.path.join(root,f)).read()
        for m in bad.finditer(t): print('LEFTOVER',f,t[max(0,m.start()-50):m.end()+30].replace('\n',' '))
print('done')
