"""BeeBlend UK v6: v5 Luxury + new type pairing (Marcellus / Jost), consumer-friendly readability,
Pure Honey Collection 'coming soon' on the sachets page, gifting page and homepage collection card."""
import json, re, os, shutil, subprocess
B = os.path.dirname(os.path.abspath(__file__))
subprocess.run(['python3', B + '/build_uk_v5.py'], check=True, stdout=subprocess.DEVNULL)
SRC = B + '/uktheme5'; OUT = B + '/uktheme6'; X6 = B + '/ukextra6'
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(SRC, OUT)
def load(p):
    s = open(p).read(); s = re.sub(r'^\s*/\*.*?\*/', '', s, flags=re.S); return json.loads(s)
def save(p, d):
    with open(p, 'w') as f: json.dump(d, f, ensure_ascii=False, indent=1)
for root_, _, files in os.walk(X6):
    for f in files:
        src = os.path.join(root_, f); rel = os.path.relpath(src, X6)
        os.makedirs(os.path.dirname(OUT + '/' + rel), exist_ok=True); shutil.copy(src, OUT + '/' + rel)

# ---------- 1. typography: Marcellus (headings) + Jost (body/UI) ----------
SWAP = [("'Cormorant Garamond'", "'Marcellus'"), ('Cormorant+Garamond:wght@500;600;700', 'Marcellus'),
        ("'Figtree'", "'Jost'"), ('family=Figtree:wght@400;500;600;700', 'family=Jost:wght@400;500;600')]
def fix_weights(css):
    def rule(m):
        r = m.group(0)
        if 'Marcellus' not in r: return r
        r = re.sub(r'font-weight:\s*[5-9]00', 'font-weight:400', r)
        r = re.sub(r"font:\s*[5-9]00(\s)", r"font:400\1", r)
        return r
    return re.sub(r'\{[^{}]*\}', rule, css)
for d in ('assets', 'sections', 'snippets'):
    for f in os.listdir(OUT + '/' + d):
        if not (f.startswith('bb-') or f.startswith('uk-')) or f.endswith(('.webp', '.png', '.jpg', '.woff2', '.gif')): continue
        p = f'{OUT}/{d}/{f}'; s = open(p).read(); o = s
        for a, b in SWAP: s = s.replace(a, b)
        s = fix_weights(s)
        if s != o: open(p, 'w').write(s)

# ---------- 2. readability layer ----------
with open(OUT + '/assets/uk-skin.css', 'a') as f:
    f.write('''
/* ===== v6: consumer-friendly readability with Marcellus + Jost ===== */
body,.bb,.uk{font-family:'Jost',system-ui,sans-serif!important;font-size:1.7rem;line-height:1.7;letter-spacing:.005em}
h1,h2,h3,.h0,.h1,.h2,.h3,.bb h1,.bb h2,.bb h3,.uk h2,.uk h3,.card__heading,.product__title h1,.collection-hero__title{font-family:'Marcellus',Georgia,serif!important;font-weight:400!important;letter-spacing:.005em!important;line-height:1.14!important}
.bb-hero h1{font-size:clamp(4rem,5.4vw,7.2rem)!important;line-height:1.08!important}
.bb-head h2{font-size:clamp(3.2rem,4vw,5rem)!important;line-height:1.12!important}
.bb-head p,.bb-story .bb-head div{color:#5C554A}
.bb-sec--sage .bb-head p,.bb-sec--sage .bb-story .bb-head div{color:#CFC3AE}
.bb-btn,.button,.product-form__submit,.uk-size{font-family:'Jost',sans-serif!important;font-weight:500!important;letter-spacing:.06em!important;font-size:1.55rem!important;min-height:5.2rem}
.bb-card__title,.card__heading a{font-family:'Marcellus',Georgia,serif!important;font-weight:400!important;font-size:2rem!important;line-height:1.2!important}
.bb-card__price,.price-item{font-family:'Jost',sans-serif!important;font-weight:500!important;font-size:1.8rem}
.bb-trust .bb-trust__item{font-family:'Marcellus',Georgia,serif!important;font-weight:400!important;letter-spacing:.04em}
.ukj__item h3{font-size:clamp(3.6rem,4.8vw,6.4rem)!important;line-height:1.05!important}
.section-header .header__menu-item{font-family:'Jost',sans-serif!important;font-size:1.6rem;letter-spacing:.04em}
.bb-faq summary{font-family:'Jost',sans-serif!important;font-weight:500!important;font-size:1.75rem}
.bb-faq__a{font-size:1.65rem;line-height:1.7}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid #B8914D!important;outline-offset:3px}
@media(max-width:749px){
  body,.bb,.uk{font-size:1.65rem}
  .bb-hero h1{font-size:clamp(3.6rem,10.5vw,4.6rem)!important}
  .bb-head h2{font-size:clamp(2.8rem,8.4vw,3.4rem)!important}
  .ukj__item h3{font-size:clamp(3.2rem,10vw,4.2rem)!important}
}
''')

# ---------- 3. Pure Honey Collection: coming soon ----------
GIFT_IMG = 'shopify://shop_images/pure-honey-collection-gift-box.jpg'
CS_TEXT = "<p>Our honey sachet tasting box: 24 tear-open 10g sachets, four each of six raw honeys, so you can taste them side by side. Perfect for gifting, travel and the office.</p>"
CS_POINTS = "Himalayan Multi, Fennel, Kashmiri Acacia, Mustard, Lychee and Ayurveda Blend\n24 sachets × 10g (240g in total)\nGift-ready box"
def coming_soon(h1=False, bg='ivory'):
    return {"type": "uk-coming-soon", "settings": {"image": GIFT_IMG, "badge": "Coming soon", "eyebrow": "Coming soon", "heading": "The Pure Honey Collection",
            "heading_tag": "h1" if h1 else "h2", "text": CS_TEXT, "points": CS_POINTS, "show_form": True, "bg": bg}}
# sachets collection page: coming soon + our jars while you wait
save(OUT + '/templates/collection.sachet.json', {"sections": {
    "coming": coming_soon(h1=True),
    "jars": {"type": "bb-product-grid", "settings": {"heading": "Our raw honey jars", "text": "Available now, in 160g and 250g.", "collection": "jar", "limit": 8, "columns": 4, "quick_add": True, "show_sold_out": True, "center": False, "button_label": "Shop all honey", "bg": "white"}}},
    "order": ["coming", "jars"]})
# gifting page: coming soon right after the page header
p = OUT + '/templates/page.gifting.json'; d = load(p)
d['sections']['phc_coming'] = coming_soon(bg='charcoal')
d['order'].insert(1, 'phc_coming'); save(p, d)
# homepage collection card for sachets
p = OUT + '/templates/index.json'; d = load(p)
cc = d['sections'].get('collection_list_YR74Ua')
if cc:
    for b in cc['blocks'].values():
        if b['settings'].get('collection') == 'sachet':
            b['settings'].update({"label": "Pure Honey Collection", "sub": "Coming soon", "image": GIFT_IMG})
save(p, d)
print('built v6', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
