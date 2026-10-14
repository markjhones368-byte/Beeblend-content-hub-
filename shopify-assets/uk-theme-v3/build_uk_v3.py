"""BeeBlend UK redesign, v3.
Base = the live UK theme (all content, templates and SEO as they are).
Adds the premium section library and re-dresses every page's existing content in it.
"""
import json, re, os, shutil
B = os.path.dirname(os.path.abspath(__file__))
UK = B + '/ukfull'; IN = B + '/theme'; EXTRA = B + '/ukextra'; OUT = B + '/uktheme3'
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(UK, OUT)

def load(p):
    s = open(p).read(); s = re.sub(r'^\s*/\*.*?\*/', '', s, flags=re.S); return json.loads(s)
def save(rel, d):
    with open(OUT + '/' + rel, 'w') as f: json.dump(d, f, ensure_ascii=False, indent=1)

# ---------- 1. premium section library ----------
for sub, pref in [('sections', 'bb-'), ('snippets', 'bb-'), ('assets', 'bb-')]:
    for f in os.listdir(IN + '/' + sub):
        if f.startswith(pref): shutil.copy(f'{IN}/{sub}/{f}', f'{OUT}/{sub}/{f}')
for root_, _, files in os.walk(EXTRA):
    for f in files:
        src = os.path.join(root_, f); rel = os.path.relpath(src, EXTRA)
        os.makedirs(os.path.dirname(OUT + '/' + rel), exist_ok=True); shutil.copy(src, OUT + '/' + rel)

IG = 'https://www.instagram.com/beeblenduk/'
p = OUT + '/sections/bb-global.liquid'; s = open(p).read()
s = s.replace('"areaServed":"IN","availableLanguage":["English","Hindi","Gujarati"]', '"areaServed":"GB","availableLanguage":["English"]')
s = s.replace('"default": "https://www.instagram.com/beeblendindia/"', '"default": "' + IG + '"').replace('"default": "+91-7984373799"', '"default": "+44 7767967707"').replace('"default": "info@beeblend.in"', '"default": "support@beeblend.co.uk"')
s = s.replace("family=Figtree:wght@400;500;600;700&family=Young+Serif", "family=Figtree:wght@400;500;600;700&family=Fraunces:opsz,wght,SOFT,WONK@9..144,400..800,0..100,0..1", 1)
s = s.replace("{{ 'bb-motion.css' | asset_url | stylesheet_tag }}", "{{ 'bb-motion.css' | asset_url | stylesheet_tag }}\n{{ 'uk-skin.css' | asset_url | stylesheet_tag }}\n<script>document.documentElement.classList.add('uk-js');</script>\n<script src=\"{{ 'uk-motion.js' | asset_url }}\" defer></script>", 1)
assert 'uk-skin.css' in s and 'Fraunces' in s
open(p, 'w').write(s)
p = OUT + '/sections/bb-product-assurance.liquid'; s = open(p).read()
s = s.replace('"title": "Ships across India", "text": "Edit delivery time"', '"title": "Free UK delivery", "text": "On orders over £40"').replace('"text": "UPI, cards, COD"', '"text": "Cards, Apple Pay, Google Pay"'); open(p, 'w').write(s)
p = OUT + '/sections/bb-trust-bar.liquid'; s = open(p).read(); s = s.replace('"Ships across India"', '"Free UK delivery over £40"'); open(p, 'w').write(s)
p = OUT + '/sections/bb-social.liquid'; s = open(p).read()
s = s.replace('"default": "https://www.instagram.com/beeblendindia/"', '"default": "' + IG + '"').replace('"label": "Instagram handle", "default": "@beeblendindia"', '"label": "Instagram handle", "default": "@beeblenduk"').replace('"default": "BeeBlend India"', '"default": "BeeBlend"').replace('"label": "YouTube handle", "default": "@beeblendindia"', '"label": "YouTube handle"')
open(p, 'w').write(s)

# ---------- 2. global styles: headings move from the decorative all-caps font to Fraunces ----------
p = OUT + '/layout/theme.liquid'; s = open(p).read()
old = """      h1,h2,h3,h4,h5,h6{
          font-family:'valley' !important;
          text-transform:uppercase;
          line-height:1em !important;
      }"""
assert old in s
s = s.replace(old, """      h1,h2,h3,h4,h5,h6{
          font-family:'Fraunces',Georgia,serif !important;
          text-transform:none;
      }""")
open(p, 'w').write(s)
hg = load(OUT + '/sections/header-group.json')
hg['sections']['bb_motion'] = {"type": "bb-global", "settings": {"include_schema": False}}
hg['order'].append('bb_motion'); save('sections/header-group.json', hg)

# ---------- 3. content helpers ----------
PROPER = ['BeeBlend', 'Kashmiri', 'Acacia', 'Lychee', 'Himalayan', 'Multi-Flora', 'Fennel', 'Sesame', 'Mustard', 'Golden Nut', 'Wild', 'Yellow', 'Black', 'UK', 'Honey Guide', 'Honey Pairing Guide', 'Brie', 'Camembert', 'Cheddar', 'Mediterranean', 'Kashmir', 'Himalayas', 'FAQs']
HONEY_WORDS = ['Lychee', 'Acacia', 'Fennel', 'Sesame', 'Himalayan', 'Mustard', 'Golden Nut', 'Multi-Flora']
def clean_heading(h):
    if not h: return h
    t = h
    t = re.sub(r'(?i)<em>\s*b?ee\s*</em>', ' ', t)
    t = re.sub(r'(?i)\bbee\s*blend\b', 'BeeBlend', t)
    t = re.sub(r'(?i)\bbeeblend\b', 'BeeBlend', t)
    t = re.sub(r'(?<![\w-])[Bb][Ee][Ee](?![\w-])', ' ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('Bees,Perfected', 'Bees, Perfected')
    t = re.sub(r'\s+', ' ', t).strip(' -–—')
    letters = [c for c in t if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.5:
        t = t.lower(); t = t[0].upper() + t[1:]
        for w in PROPER:
            t = re.sub(r'(?i)\b' + re.escape(w) + r'\b', w, t)
        for w in HONEY_WORDS:
            t = re.sub(r'(?i)\b(' + re.escape(w) + r') honey\b', r'\1 Honey', t)
        t = re.sub(r'(?i)\bwhich honey should i choose', 'Which honey should I choose', t)
        t = re.sub(r'\bi\b', 'I', t)
    return t
def clean_label(l):
    return clean_heading(l) if l else l

TEXTURE = ('bg', 'drops', 'pattern', 'honeycomb', 'screenshot', 'background')
def is_texture(img):
    return (not img) or any(k in img.lower() for k in TEXTURE)
def is_jar(img):
    n = (img or '').lower()
    return n.endswith('.png') and any(k in n for k in ('honey', 'jar', 'group', 'logo', '34', '05'))
def shape_for(img):
    n = (img or '').lower()
    if is_jar(img): return 'disc'
    if n.endswith('.png') or n.endswith('.svg'): return 'rounded'
    return 'arch'

def blocks(s, typ=None):
    out = []
    for k in s.get('block_order', []):
        b = s['blocks'][k]
        if b.get('disabled'): continue
        if typ is None or b['type'] == typ: out.append(b)
    return out
def first(s, typ, key):
    for b in blocks(s, typ):
        v = b['settings'].get(key)
        if v: return v
    return ''
def buttons(s):
    res = []
    for b in blocks(s):
        st = b['settings']
        if b['type'] == 'button' and st.get('button_label'):
            res.append((clean_label(st['button_label']), st.get('button_link', '')))
            if st.get('button_label_2'): res.append((clean_label(st['button_label_2']), st.get('button_link_2', '')))
        if b['type'] == 'buttons':
            for i in (1, 2):
                if st.get(f'button_label_{i}'): res.append((clean_label(st[f'button_label_{i}']), st.get(f'button_link_{i}', '')))
    return [(a, l.rstrip('\\')) for a, l in res]
def rt(t):
    if not t: return ''
    t = t.strip()
    return t if re.match(r'^<(p|ul|ol|h[1-6])[\s>]', t) else '<p>' + t + '</p>'

RHYTHM = ['#FFFFFF', '#FBF3DC']

# ---------- 4. section converters ----------
def conv(s, ctx):
    typ = s['type']; st = s.get('settings', {})
    if s.get('disabled'): return None
    if typ == 'main-page' and ctx['has_hero']: return None
    if typ in ('image-banner', 'rich-text') and ctx['first'] and not ctx['has_hero']:
        ctx['has_hero'] = True
        img = st.get('image') or ''
        btn = buttons(s)
        heading = clean_heading(first(s, 'heading', 'heading')) or ctx['title']
        text = first(s, 'text', 'text')
        photo = bool(img) and not is_texture(img)
        long_text = len(re.sub('<[^>]+>', '', text or '')) > 500
        hero = {"type": "uk-page-hero", "settings": {"style": "photo" if photo else "colour", "heading": heading, "colour": ctx['colour'], "ink": "dark", "drip": True}}
        if text and not long_text: hero['settings']['text'] = rt(text)
        if photo: hero['settings']['image'] = img
        for i, (a, l) in enumerate(btn[:2]):
            hero['settings'][f'btn{i+1}_label'] = a; hero['settings'][f'btn{i+1}_link'] = l
        out = [hero]
        if text and long_text:
            out.append({"type": "uk-statement", "settings": {"style": "prose", "text": rt(text), "bg": "#FFFFFF", "ink": "dark"}})
        return out
    ctx['first'] = False
    ctx['n'] += 1
    bg = RHYTHM[ctx['n'] % 2]
    if typ == 'image-banner':
        img = st.get('image') or ''
        btn = buttons(s)
        o = {"type": "uk-statement", "settings": {"style": "statement", "heading": clean_heading(first(s, 'heading', 'heading')), "bg": "#1F3A2E", "ink": "light"}}
        tx = first(s, 'text', 'text')
        if tx: o['settings']['text'] = rt(tx)
        if img and not is_texture(img): o['settings']['image'] = img
        for i, (a, l) in enumerate(btn[:2]):
            o['settings'][['btn1_label', 'btn2_label'][i]] = a; o['settings'][['btn1_link', 'btn2_link'][i]] = l
        return [o]
    if typ == 'rich-text':
        h = clean_heading(first(s, 'heading', 'heading')); tx = first(s, 'text', 'text'); btn = buttons(s)
        if not h and not tx and btn:
            o = {"type": "uk-statement", "settings": {"style": "statement", "bg": bg, "ink": "dark"}}
        else:
            long_text = len(re.sub('<[^>]+>', '', tx or '')) > 600 or (tx or '').count('<h') >= 2 or (tx or '').count('<li') >= 3
            o = {"type": "uk-statement", "settings": {"style": "prose" if long_text else "statement", "bg": "#FFFFFF" if long_text else bg, "ink": "dark"}}
            if h: o['settings']['heading'] = h
            if tx: o['settings']['text'] = rt(tx)
        for i, (a, l) in enumerate(btn[:2]):
            o['settings'][['btn1_label', 'btn2_label'][i]] = a; o['settings'][['btn1_link', 'btn2_link'][i]] = l
        return [o]
    if typ == 'image-with-text':
        img = st.get('image') or ''
        btn = buttons(s)
        o = {"type": "uk-split", "settings": {"shape": shape_for(img), "image_side": "left" if st.get('layout', 'image_first') == 'image_first' else 'right', "bg": bg, "ink": "dark"}}
        if img: o['settings']['image'] = img
        cap = first(s, 'caption', 'caption'); h = clean_heading(first(s, 'heading', 'heading')); tx = first(s, 'text', 'text')
        if cap: o['settings']['caption'] = clean_heading(cap)
        if h: o['settings']['heading'] = h
        if tx: o['settings']['text'] = rt(tx)
        if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
        return [o]
    if typ == 'multicolumn':
        cards = {}
        for i, b in enumerate(blocks(s, 'column')):
            bs = b['settings']; c = {"title": clean_heading(re.sub('<[^>]+>', '', bs.get('title', '')))}
            if bs.get('text'): c['text'] = rt(bs['text'])
            if bs.get('link_label'): c['link_label'] = clean_label(bs['link_label'])
            if bs.get('link'): c['link'] = bs['link']
            if bs.get('image') and not is_texture(bs['image']) and not any(k in bs['image'].lower() for k in ('banner_1_bee', 'immune', 'moisturizer', 'coffee-cup', 'honeycomb_1')): c['image'] = bs['image']
            cards[f'c{i+1}'] = {"type": "card", "settings": c}
        return [{"type": "uk-cards", "blocks": cards, "block_order": list(cards), "settings": {"heading": clean_heading(re.sub('<[^>]+>', ' ', st.get('title', ''))).strip(), "columns": "3", "bg": bg}}]
    if typ == 'collapsible-content':
        rows = {}
        for i, b in enumerate(blocks(s, 'collapsible_row')):
            rows[f'r{i+1}'] = {"type": "row", "settings": {"question": clean_heading(b['settings'].get('heading', '')) or 'Question', "answer": rt(b['settings'].get('row_content', ''))}}
        o = {"type": "uk-accordion", "blocks": rows, "block_order": list(rows), "settings": {"heading": clean_heading(st.get('heading', '')) or 'Questions', "open_first": True, "bg": bg}}
        if st.get('caption'): o['settings']['text'] = rt(st['caption'])
        return [o]
    if typ == 'text-scrolling':
        items = [clean_heading(x.strip()) for x in re.split(r'[•·|]', st.get('text_name', '')) if x.strip()]
        items = [i.replace('NoPreservatives', 'No Preservatives').replace('No preservatives', 'No preservatives') for i in items]
        mb = {f"m{i+1}": {"type": "item", "settings": {"text": t}} for i, t in enumerate(items)}
        return [{"type": "uk-marquee", "blocks": mb, "block_order": list(mb), "settings": {"bg": "#1F3A2E", "fg": "#FFF8E8", "accent": "#F2C14E", "speed": 40}}]
    if typ == 'collection-list':
        tb = {}
        for i, b in enumerate(blocks(s, 'featured_collection')):
            if b['settings'].get('collection'): tb[f't{i+1}'] = {"type": "tile", "settings": {"collection": b['settings']['collection']}}
        return [{"type": "uk-collection-tiles", "blocks": tb, "block_order": list(tb), "settings": {"heading": clean_heading(re.sub('<[^>]+>', ' ', st.get('title', ''))).strip() or 'Our collections', "bg": bg}}]
    if typ == 'featured-collection':
        return [{"type": "bb-product-grid", "settings": {"heading": clean_heading(st.get('title', '')), "collection": st.get('collection', 'all'), "limit": int(st.get('products_to_show', 4)), "columns": 4, "quick_add": True, "show_sold_out": True, "center": False, "button_label": "View all", "bg": "white"}}]
    if typ == 'logo-grid':
        ph = {}
        for i, b in enumerate(blocks(s)):
            img = b['settings'].get('logo_img', '')
            if img and 'logo' not in img.lower():
                ph[f'p{i+1}'] = {"type": "photo", "settings": {"image": img, "link": b['settings'].get('logo_link') or IG}}
        return [{"type": "uk-gallery", "blocks": ph, "block_order": list(ph), "settings": {"heading": clean_heading(st.get('test_heading', '')) or 'Where to find us', "link_label": "Follow @beeblenduk on Instagram", "link": IG, "bg": "#FFFFFF"}}]
    if typ == 'testimonials':
        return None
    return [s]   # core Shopify sections stay exactly as they are

def convert_template(rel, title, colour, extra_after_main=None):
    d = load(OUT + '/' + rel)
    ctx = {'first': True, 'has_hero': False, 'n': 0, 'title': title, 'colour': colour}
    new, order = {}, []
    for k in d['order']:
        s = d['sections'][k]
        if s.get('disabled'): continue
        if s['type'].startswith('main-') and s['type'] != 'main-page': ctx['first'] = False
        res = conv(s, ctx)
        if not res: continue
        for i, r in enumerate(res):
            key = k if i == 0 else f'{k}_{i}'
            new[key] = r; order.append(key)
        if extra_after_main and s['type'] == 'main-product':
            new['taste'] = extra_after_main; order.append('taste')
    for i, k in enumerate(order[:-1]):
        if new[k]['type'] == 'uk-page-hero' and new[order[i+1]]['type'] == 'uk-marquee':
            new[k]['settings']['drip'] = False
    d['sections'] = new; d['order'] = order
    save(rel, d)
    return d

PAGES = {
    'templates/page.about-us.json': ('About us', '#F4DE9A'),
    'templates/page.honey-guide.json': ('Which honey should I choose?', '#EFC650'),
    'templates/page.honey-pairing-guide.json': ('Honey pairing guide', '#E3B04B'),
    'templates/page.gifting.json': ('Gifting', '#E3B04B'),
    'templates/page.health-benefits.json': ('Health benefits', '#F4DE9A'),
    'templates/page.contact.json': ('Contact us', '#FBF3DC'),
    'templates/page.privacy-policy.json': ('Privacy policy', '#FBF3DC'),
    'templates/page.shipping-delivery.json': ('Shipping & delivery', '#FBF3DC'),
    'templates/page.returns-refunds.json': ('Returns & refunds', '#FBF3DC'),
    'templates/page.terms-conditions.json': ('Terms & conditions', '#FBF3DC'),
    'templates/blog.json': ('Recipes', '#F4DE9A'),
    'templates/collection.honey-jars.json': ('Honey jars', '#F4DE9A'),
    'templates/collection.json': ('Collection', '#F4DE9A'),
}
for rel, (t, c) in PAGES.items(): convert_template(rel, t, c)
taste = {"type": "uk-taste-profile", "settings": {"heading": "How it tastes"}}
for f in sorted(os.listdir(OUT + '/templates')):
    if f.startswith('product.') and f.endswith('.json'):
        convert_template('templates/' + f, 'Product', '#F4DE9A', dict(taste))

# ---------- 5. homepage: same content, new design ----------
d = load(OUT + '/templates/index.json'); S = d['sections']
def sec(k): return S[k]
vs = sec('video_section_QdfyKG')['settings']
HONEYS = [
 ("kashmiri-acacia-honey", "Kashmiri Acacia", "#F4DE9A", "dark", "Light & Floral", "Kashmir", "Delicate, smooth and elegantly sweet, with a mild floral aroma, soft vanilla-like notes and a clean, subtle finish.", "Tea and coffee, Fruit and yoghurt, Soft cheeses"),
 ("mustard-honey", "Yellow Mustard Flower", "#EFC650", "dark", "Bold & Bright", "Mustard-growing regions", "Surprisingly mild and floral, with a gentle warmth and subtle spice that develops on the palate.", "Honey mustard glazes, Mature cheddar, Salad dressings"),
 ("lychee-honey", "Lychee Blossom", "#E3B04B", "dark", "Exotic Asian Honey", "", "Delicate floral notes come first, followed by hints of tropical fruit and a light, lingering sweetness.", "Strawberries and cream, Tea and cold drinks, Soft goat's cheese"),
 ("himalayan-multifloral-honey", "Himalayan Multi-Flora", "#CF8E2A", "dark", "Mountain Magic", "High-altitude Himalayan regions", "Layers of wildflower sweetness, herbal notes and subtle spice, followed by a clean, balanced finish.", "Porridge and granola, Tea and warm drinks, Baking"),
 ("fennel-honey", "Wild Fennel", "#B06E1E", "light", "Mediterranean Herbal Gold", "Mediterranean region", "Delicate anise-like aromatics, followed by warm herbal sweetness and a complex botanical finish.", "Herbal infusions, Ricotta with black pepper, Artisan cheeses"),
 ("golden-nut-honey", "Golden Nut Infusion", "#A8742F", "light", "Rich & Indulgent", "Raw honey, almonds, cashews and dates", "Creamy, nutty sweetness meets the caramel-like character of dates, with a rich, velvety mouthfeel.", "Toast and croissants, Porridge, Cheese and crackers"),
 ("sesame-honey", "Black Sesame", "#7E4614", "light", "Rich & Nutty", "Sesame-growing regions", "Rich and complex, with toasted, nutty notes balanced by caramel-like sweetness and a subtle smoky finish.", "Roasted salmon, Noodles and rice, Aged cheeses"),
]
hb = {f"h{i+1}": {"type": "honey", "settings": {"product": h, "name": nm, "note": note, "colour": c, "ink": ink}} for i, (h, nm, c, ink, note, o, notes, pairs) in enumerate(HONEYS)}
hero = {"type": "uk-hero", "blocks": hb, "block_order": list(hb), "settings": {"heading": clean_heading(vs['text_name']), "text": vs['subtitle'], "btn1_label": vs['button_text'], "btn1_link": vs['button_url'], "btn2_label": clean_label(vs['button_text1']), "btn2_link": "shopify://pages/which-honey-should-i-choose"}}
story_k = 'image_with_text_bpJ8fC'; st_ = sec(story_k)
jb = {f"j{i+1}": {"type": "honey", "settings": {k: v for k, v in {"product": h, "name": nm, "colour": c, "ink": ink, "origin": o, "notes": notes, "pairs": pairs}.items() if v}} for i, (h, nm, c, ink, note, o, notes, pairs) in enumerate(HONEYS)}
journey = {"type": "uk-flavour-journey", "blocks": jb, "block_order": list(jb), "settings": {"heading": clean_heading(first(st_, 'heading', 'heading')), "text": re.sub('<[^>]+>', '', first(st_, 'text', 'text'))}}
ctx = {'first': False, 'has_hero': True, 'n': 0, 'title': 'Home', 'colour': '#F4DE9A'}
new, order = {}, []
def put(k, v): new[k] = v; order.append(k)
put('hero', hero)
for k in d['order']:
    s = S[k]
    if s.get('disabled') or k == 'video_section_QdfyKG': continue
    if k == 'text_scrolling_WNLnfY': continue                 # empty "Best Sellers Products" label
    if k == story_k: put('journey', journey); continue
    if k == 'text_scrolling_khjh3U':
        mk = conv(s, ctx)[0]; new['marquee'] = mk
        i = order.index('featured_collection_MQcrBh') + 1 if 'featured_collection_MQcrBh' in order else 1
        order.insert(i, 'marquee'); continue
    if s['type'] == 'apps' and not s.get('blocks'): continue  # empty app wrappers
    res = conv(s, ctx)
    if not res: continue
    for i, r in enumerate(res): put(k if i == 0 else f'{k}_{i}', r)
# rhythm on the homepage
if 'image_with_text_dDHrjn' in new: new['image_with_text_dDHrjn']['settings'].update({"bg": "#1F3A2E", "ink": "light"})
if 'image_with_text_8hbt9B' in new: new['image_with_text_8hbt9B']['settings'].update({"bg": "#FBF3DC"})
if 'image_with_text_tYq3R8' in new: new['image_with_text_tYq3R8']['settings'].update({"bg": "#FFFFFF"})
if 'image_with_text_63xW3b' in new: new['image_with_text_63xW3b']['settings'].update({"bg": "#FBF3DC", "shape": "rounded"})
d['sections'] = new; d['order'] = order
save('templates/index.json', d)

# home-new is an unused draft page template; leave it untouched.
print('built', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
