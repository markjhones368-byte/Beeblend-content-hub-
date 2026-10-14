"""BeeBlend UK redesign v4: the beeblend.in design, carrying the UK store's own content, plus an extra animation layer."""
import json, re, os, shutil
B = os.path.dirname(os.path.abspath(__file__))
IN = B + '/theme'; UK = B + '/ukfull'; X3 = B + '/ukextra'; X4 = B + '/ukextra4'; OUT = B + '/uktheme4'
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(IN, OUT)
def load(p):
    s = open(p).read(); s = re.sub(r'^\s*/\*.*?\*/', '', s, flags=re.S); return json.loads(s)
def save(rel, d):
    with open(OUT + '/' + rel, 'w') as f: json.dump(d, f, ensure_ascii=False, indent=1)
IG = 'https://www.instagram.com/beeblenduk/'; TT = 'https://www.tiktok.com/@beeblend?_t=ZN-90ZZW4Fjk7a&_r=1'

# ---------- 1. the UK store's own layout, settings, header and footer ----------
for rel in ['layout/theme.liquid', 'snippets/meta-tags.liquid', 'config/settings_data.json', 'sections/footer-group.json']:
    shutil.copy(UK + '/' + rel, OUT + '/' + rel)
hg = load(UK + '/sections/header-group.json')
hg['sections']['bb_motion'] = {"type": "bb-global", "settings": {"include_schema": False}}
hg['order'].append('bb_motion'); save('sections/header-group.json', hg)
for rel in ['templates/collection.sachet.json', 'templates/page.socials.json', 'templates/page.why-beeblend.json']:
    if os.path.exists(OUT + '/' + rel): os.remove(OUT + '/' + rel)
for f in os.listdir(UK + '/templates'):
    if f.endswith('.json') or f.endswith('.liquid'): shutil.copy(UK + '/templates/' + f, OUT + '/templates/' + f)
for f in os.listdir(UK + '/templates/customers'): shutil.copy(UK + '/templates/customers/' + f, OUT + '/templates/customers/' + f)

# ---------- 2. section tweaks for the UK + animation layer ----------
p = OUT + '/sections/bb-global.liquid'; s = open(p).read()
s = s.replace('"areaServed":"IN","availableLanguage":["English","Hindi","Gujarati"]', '"areaServed":"GB","availableLanguage":["English"]')
s = s.replace('"default": "https://www.instagram.com/beeblendindia/"', '"default": "' + IG + '"').replace('"default": "+91-7984373799"', '"default": "+44 7767967707"').replace('"default": "info@beeblend.in"', '"default": "support@beeblend.co.uk"')
s = s.replace("{{ 'bb-motion.css' | asset_url | stylesheet_tag }}", "{{ 'bb-motion.css' | asset_url | stylesheet_tag }}\n{{ 'uk-skin.css' | asset_url | stylesheet_tag }}\n<script>document.documentElement.classList.add('uk-js');</script>\n<script src=\"{{ 'uk-motion.js' | asset_url }}\" defer></script>", 1)
assert 'uk-motion.js' in s; open(p, 'w').write(s)
p = OUT + '/sections/bb-product-assurance.liquid'; s = open(p).read()
s = s.replace('"title": "Ships across India", "text": "Edit delivery time"', '"title": "Fast UK delivery", "text": "Edit delivery time"').replace('"text": "UPI, cards, COD"', '"text": "Cards, Apple Pay, Google Pay"'); open(p, 'w').write(s)
p = OUT + '/sections/bb-trust-bar.liquid'; s = open(p).read(); s = s.replace('"Ships across India"', '"Fast UK delivery"'); open(p, 'w').write(s)
# social: TikTok card (the UK's channel) and UK defaults
shutil.copy(B + '/uktheme/sections/bb-social.liquid', OUT + '/sections/bb-social.liquid')
# reasons: optional link per card, and no empty grid when there are no cards
p = OUT + '/sections/bb-reasons.liquid'; s = open(p).read()
s = s.replace('    <div class="bb-rs">\n', '    {%- if section.blocks.size > 0 -%}\n    <div class="bb-rs">\n', 1)
s = s.replace('''          <p>{{ block.settings.text }}</p>
        </article>
      {%- endfor -%}
    </div>''', '''          <p>{{ block.settings.text }}</p>
          {%- if block.settings.link_label != blank -%}<a class="bb-rs__link" href="{{ block.settings.link }}">{{ block.settings.link_label }} <span aria-hidden="true">&rarr;</span></a>{%- endif -%}
        </article>
      {%- endfor -%}
    </div>
    {%- endif -%}''', 1)
s = s.replace("  #bb-rs-{{ section.id }} .bb-rs__cta{", "  #bb-rs-{{ section.id }} .bb-rs__link{margin-top:auto;padding-top:.6rem;font-weight:600;font-size:1.5rem;color:var(--bb-forest);text-decoration:none;border-bottom:1.5px solid var(--bb-gold);align-self:flex-start}\n  #bb-rs-{{ section.id }} .bb-rs__cta{", 1)
s = re.sub(r'(\{ "type": "textarea", "id": "text", "label": "[^"]*"[^}]*\})(\s*\]\s*\}\s*\],\s*"presets")', r'\1,\n      { "type": "text", "id": "link_label", "label": "Link label" },\n      { "type": "url", "id": "link", "label": "Link" }\2', s, count=1)
assert 'link_label' in s and 'bb-rs__link' in s
open(p, 'w').write(s)
for f in ['uk-flavour-journey.liquid', 'uk-taste-profile.liquid']:
    s = open(X3 + '/sections/' + f).read()
    s = s.replace('    <h2>{{ section.settings.heading }}</h2>\n    {%- if section.settings.text != blank -%}<p>', '    <div class="bb-head" style="margin:0"><h2>{{ section.settings.heading }}</h2></div>\n    {%- if section.settings.text != blank -%}<p>')
    s = s.replace("#{{ sid }} .ukj__head h2{font-size:clamp(3.8rem,6vw,7.8rem);max-width:12ch}", "#{{ sid }} .ukj__head h2{font-size:clamp(3rem,4.4vw,4.8rem);max-width:16ch}")
    s = s.replace("#{{ sid }} .ukj__head{padding-top:clamp(7.2rem,10vw,12rem);padding-bottom:clamp(3.2rem,4vw,5.6rem);display:grid;gap:1.6rem}", "#{{ sid }} .ukj__head{padding-top:clamp(4.8rem,8vw,9.6rem);padding-bottom:clamp(3.2rem,4vw,4.8rem);display:grid;gap:1.6rem;max-width:132rem;margin:0 auto}")
    s = s.replace("#{{ sid }} .ukj__head p{max-width:46ch;font-size:1.8rem;color:#5E584D}", "#{{ sid }} .ukj__head p{max-width:52ch;font-size:1.7rem;color:#6B655B}")
    s = s.replace('<div>\n      <h2>{{ section.settings.heading }}</h2>', '<div class="bb-head" style="margin:0">\n      <h2>{{ section.settings.heading }}</h2>')
    s = s.replace("#{{ sid }} h2{font-size:clamp(3.6rem,5vw,6.4rem)}", "#{{ sid }} h2{font-size:clamp(3rem,4.4vw,4.8rem)}")
    open(OUT + '/sections/' + f, 'w').write(s)
for f in ['uk-skin.css', 'uk-motion.js']:
    shutil.copy(X4 + '/assets/' + f, OUT + '/assets/' + f)

# ---------- 3. content helpers ----------
PROPER = ['BeeBlend', 'Kashmiri', 'Acacia', 'Lychee', 'Himalayan', 'Multi-Flora', 'Fennel', 'Sesame', 'Mustard', 'Golden Nut', 'Wild', 'Yellow', 'Black', 'UK', 'Honey Guide', 'Honey Pairing Guide', 'Brie', 'Camembert', 'Cheddar', 'Mediterranean', 'Kashmir', 'FAQs']
HONEY_WORDS = ['Lychee', 'Acacia', 'Fennel', 'Sesame', 'Himalayan', 'Mustard', 'Golden Nut', 'Multi-Flora']
def clean(h):
    if not h: return h
    t = re.sub(r'(?i)<em>\s*b?ee\s*</em>', ' ', h)
    t = re.sub(r'(?i)\bbee\s*blend\b', 'BeeBlend', t)
    t = re.sub(r'(?<![\w-])[Bb][Ee][Ee](?![\w-])', ' ', t)
    t = re.sub(r'<[^>]+>', '', t).replace('Bees,Perfected', 'Bees, Perfected')
    t = re.sub(r'\s+', ' ', t).strip(' -–—')
    L = [c for c in t if c.isalpha()]
    if L and sum(c.isupper() for c in L) / len(L) > 0.5:
        t = t.lower(); t = t[0].upper() + t[1:]
        for w in PROPER: t = re.sub(r'(?i)\b' + re.escape(w) + r'\b', w, t)
        for w in HONEY_WORDS: t = re.sub(r'(?i)\b(' + re.escape(w) + r') honey\b', r'\1 Honey', t)
        t = re.sub(r'\bi\b', 'I', t)
    return t
def plain(t): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', t or '')).strip()
def rt(t):
    t = (t or '').strip()
    if not t: return ''
    return t if re.match(r'^<(p|ul|ol|h[1-6])[\s>]', t) else '<p>' + t + '</p>'
TEXTURE = ('bg', 'drops', 'pattern', 'honeycomb', 'screenshot', 'background')
def photo(img): return bool(img) and not any(k in img.lower() for k in TEXTURE)
def blocks(s, typ=None):
    return [s['blocks'][k] for k in s.get('block_order', []) if not s['blocks'][k].get('disabled') and (typ is None or s['blocks'][k]['type'] == typ)]
def first(s, typ, key):
    for b in blocks(s, typ):
        if b['settings'].get(key): return b['settings'][key]
    return ''
def buttons(s):
    res = []
    for b in blocks(s):
        st = b['settings']
        if b['type'] == 'button' and st.get('button_label'):
            res.append((clean(st['button_label']), st.get('button_link', '')))
        if b['type'] == 'buttons':
            for i in (1, 2):
                if st.get(f'button_label_{i}'): res.append((clean(st[f'button_label_{i}']), st.get(f'button_link_{i}', '')))
    return [(a, (l or '').rstrip('\\')) for a, l in res]
ICONS = ['leaf', 'drop', 'pin', 'hex', 'gift', 'shield', 'truck', 'leaf', 'drop']
BG = ['paper', 'white']

def steps_from(html):
    parts = re.findall(r'<h[23][^>]*>(.*?)</h[23]>\s*(.*?)(?=<h[23]|$)', html or '', flags=re.S)
    return [(clean(plain(a)), plain(b)) for a, b in parts if plain(a)]

def conv(k, s, ctx):
    typ = s['type']; st = s.get('settings', {})
    if s.get('disabled'): return None
    if typ == 'main-page' and ctx['hero']: return None
    if typ in ('image-banner', 'rich-text') and ctx['first'] and not ctx['hero']:
        ctx['hero'] = True; ctx['first'] = False
        img = st.get('image') or st.get('bg_image') or ''
        h = clean(first(s, 'heading', 'heading')) or ctx['title']; tx = first(s, 'text', 'text'); btn = buttons(s)
        o = {"type": "bb-page-hero", "settings": {"heading": h, "crumbs": True, "bg": "paper", "fit": "cover"}}
        if tx and len(plain(tx)) <= 500: o['settings']['text'] = plain(tx)
        if photo(img): o['settings']['image'] = img
        if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
        out = [(k, o)]
        if tx and len(plain(tx)) > 500:
            out.append((k + '_text', {"type": "rich-text", "blocks": {"t": {"type": "text", "settings": {"text": rt(tx)}}}, "block_order": ["t"], "settings": {"desktop_content_position": "center", "content_alignment": "left", "color_scheme": "scheme-e7d033a6-032f-4c6f-85fe-a72fe5872837", "full_width": True, "padding_top": 40, "padding_bottom": 64}}))
        return out
    if not typ.startswith('main-') and typ not in ('apps', 'featured-blog', 'contact-form'): ctx['n'] += 1
    ctx['first'] = False
    bg = BG[ctx['n'] % 2]
    if typ == 'main-collection-banner':
        return [(k, {"type": "bb-page-hero", "settings": {"use_collection_image": True, "fit": "contain", "crumbs": True, "bg": "paper"}})]
    if typ == 'video-section':
        return [(k, {"type": "bb-hero", "settings": {"video": st.get('video'), "image": "shopify://shop_images/honey_drizzle_1.jpg", "heading": clean(st.get('text_name', '')), "subheading": st.get('subtitle', ''), "btn1_label": st.get('button_text', ''), "btn1_link": st.get('button_url', ''), "btn2_label": clean(st.get('button_text1', '')), "btn2_link": "shopify://pages/which-honey-should-i-choose", "eyebrow": "Rare honeys · Distinctive flavours", "show_cue": True}})]
    if typ == 'image-banner':
        img = st.get('image') or ''; btn = buttons(s)
        o = {"type": "bb-gifting-banner", "settings": {"heading": clean(first(s, 'heading', 'heading')), "text": plain(first(s, 'text', 'text')), "tint": "#EADBBE"}}
        if photo(img): o['settings']['image'] = img
        else: o['settings']['trio'] = ["kashmiri-acacia-honey", "golden-nut-honey", "lychee-honey"]
        if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
        return [(k, o)]
    if typ == 'rich-text':
        h = clean(first(s, 'heading', 'heading')); tx = first(s, 'text', 'text'); btn = buttons(s)
        long_text = len(plain(tx)) > 600 or (tx or '').count('<h') >= 2 or (tx or '').count('<li') >= 3
        if long_text:
            return [(k, s)]          # long policy/article text keeps its own section, styled by the beeblend.in skin
        o = {"type": "bb-reasons", "settings": {"heading": h or ' ', "text": plain(tx), "center": True, "bg": bg}}
        if not h: o['settings']['heading'] = clean(btn[0][0]) if btn else 'BeeBlend'
        if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
        return [(k, o)]
    if typ == 'image-with-text':
        img = st.get('image') or ''; btn = buttons(s)
        h = clean(first(s, 'heading', 'heading')); tx = first(s, 'text', 'text'); cap = first(s, 'caption', 'caption')
        stp = steps_from(tx)
        if len(stp) >= 2 and not h:
            bl = {f"s{i+1}": {"type": "step", "settings": {"title": a, "text": b}} for i, (a, b) in enumerate(stp[:5])}
            o = {"type": "bb-story-steps", "blocks": bl, "block_order": list(bl), "settings": {"illustration": "hive_to_jar", "heading": "From hive to jar", "text": ""}}
            if photo(img): o['settings'].update({"illustration": "image", "image": img})
            if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
            return [(k, o)]
        text = rt(tx)
        if cap: text = '<p><strong>' + clean(cap) + '</strong></p>' + text
        o = {"type": "bb-text-image", "settings": {"heading": h or clean(cap) or ' ', "text": text, "image_right": st.get('layout', 'image_first') != 'image_first', "bg": bg, "tint": "#EADBBE"}}
        if img: o['settings']['image'] = img
        if btn: o['settings']['btn_label'], o['settings']['btn_link'] = btn[0]
        return [(k, o)]
    if typ == 'multicolumn':
        bl = {}
        for i, b in enumerate(blocks(s, 'column')):
            bs = b['settings']; c = {"icon": ICONS[i % len(ICONS)], "title": clean(plain(bs.get('title', ''))), "text": plain(bs.get('text', ''))}
            if bs.get('link_label') and bs.get('link'): c['link_label'] = clean(bs['link_label']); c['link'] = bs['link']
            elif bs.get('link_label'): c['link_label'] = clean(bs['link_label']); c['link'] = ctx.get('fallback_link', 'shopify://collections/all')
            bl[f"r{i+1}"] = {"type": "reason", "settings": c}
        o = {"type": "bb-reasons", "blocks": bl, "block_order": list(bl), "settings": {"heading": clean(plain(st.get('title', ''))) or ' ', "center": False, "bg": bg}}
        if st.get('button_label'): o['settings']['btn_label'], o['settings']['btn_link'] = clean(st['button_label']), st.get('button_link', '')
        return [(k, o)]
    if typ == 'collapsible-content':
        bl = {f"q{i+1}": {"type": "qa", "settings": {"q": clean(b['settings'].get('heading', '')) or 'Question', "a": rt(b['settings'].get('row_content', ''))}} for i, b in enumerate(blocks(s, 'collapsible_row'))}
        return [(k, {"type": "bb-faq", "blocks": bl, "block_order": list(bl), "settings": {"heading": clean(st.get('heading', '')) or 'Questions, answered', "open_first": True, "bg": bg}})]
    if typ == 'text-scrolling':
        items = [clean(x.strip()).replace('NoPreservatives', 'No Preservatives') for x in re.split(r'[•·|]', st.get('text_name', '')) if x.strip()]
        icons = ['hex', 'leaf', 'drop', 'pin', 'shield', 'gift']
        bl = {f"t{i+1}": {"type": "item", "settings": {"icon": icons[i % len(icons)], "text": t}} for i, t in enumerate(items)}
        return [(k, {"type": "bb-trust-bar", "blocks": bl, "block_order": list(bl), "settings": {}})]
    if typ == 'collection-list':
        bl = {f"c{i+1}": {"type": "card", "settings": {"collection": b['settings']['collection']}} for i, b in enumerate(blocks(s, 'featured_collection')) if b['settings'].get('collection')}
        return [(k, {"type": "bb-collection-cards", "blocks": bl, "block_order": list(bl), "settings": {"heading": clean(plain(st.get('title', ''))) or 'Our collections', "center": False, "fit": "contain", "bg": bg}})]
    if typ == 'featured-collection':
        return [(k, {"type": "bb-product-grid", "settings": {"heading": clean(st.get('title', '')), "collection": st.get('collection', 'all'), "limit": int(st.get('products_to_show', 4)), "columns": 4, "quick_add": True, "show_sold_out": True, "center": False, "button_label": "View all", "bg": "white"}})]
    if typ == 'logo-grid':
        bl = {}
        for i, b in enumerate(blocks(s)):
            img = b['settings'].get('logo_img', '')
            if img and 'logo' not in img.lower(): bl[f"p{i+1}"] = {"type": "photo", "settings": {"image": img, "link": b['settings'].get('logo_link') or IG}}
        return [(k, {"type": "bb-social", "blocks": bl, "block_order": list(bl), "settings": {"heading": clean(st.get('test_heading', '')) or 'Where to find us', "text": "", "instagram": IG, "instagram_handle": "@beeblenduk", "tiktok": TT, "tiktok_handle": "@beeblend", "feed_heading": "From our feed", "bg": "white"}})]
    if typ == 'testimonials':
        return None
    return [(k, s)]

def convert(rel, title, product=False):
    d = load(OUT + '/' + rel)
    ctx = {'first': True, 'hero': False, 'n': 0, 'title': title}
    new, order = {}, []
    if product:
        new['crumbs'] = {"type": "bb-breadcrumbs", "settings": {}}; order.append('crumbs')
    for k in d['order']:
        s = d['sections'][k]
        if s.get('disabled'): continue
        if s['type'] == 'main-product': ctx['first'] = False
        res = conv(k, s, ctx)
        if not res: continue
        for kk, v in res: new[kk] = v; order.append(kk)
        if product and s['type'] == 'main-product':
            new['taste'] = {"type": "uk-taste-profile", "settings": {"heading": "How it tastes"}}; order.append('taste')
            new['assure'] = {"type": "bb-product-assurance", "blocks": {
                "b1": {"type": "badge", "settings": {"icon": "drop", "title": "Raw honey", "text": "Cold-extracted, never blended"}},
                "b2": {"type": "badge", "settings": {"icon": "pin", "title": "Single-origin", "text": "Distinctive floral sources"}},
                "b3": {"type": "badge", "settings": {"icon": "leaf", "title": "100% natural", "text": "No preservatives"}},
                "b4": {"type": "badge", "settings": {"icon": "shield", "title": "Secure checkout", "text": "Cards, Apple Pay, Google Pay"}}},
                "block_order": ["b1", "b2", "b3", "b4"], "settings": {}}; order.append('assure')
    if product:
        new['sticky'] = {"type": "bb-sticky-atc", "settings": {}}; order.append('sticky')
    d['sections'] = new; d['order'] = order; save(rel, d)

PAGES = {'page.about-us': 'About us', 'page.honey-guide': 'Which honey should I choose?', 'page.honey-pairing-guide': 'Honey pairing guide', 'page.gifting': 'Gifting', 'page.health-benefits': 'Health benefits', 'page.contact': 'Contact us', 'page.privacy-policy': 'Privacy policy', 'page.shipping-delivery': 'Shipping & delivery', 'page.returns-refunds': 'Returns & refunds', 'page.terms-conditions': 'Terms & conditions', 'blog': 'Recipes', 'collection.honey-jars': 'Honey jars', 'collection': 'Collection'}
for f, t in PAGES.items(): convert(f'templates/{f}.json', t)
for f in sorted(os.listdir(OUT + '/templates')):
    if f.startswith('product.') and f.endswith('.json'): convert('templates/' + f, 'Product', product=True)

# ---------- 4. homepage ----------
d = load(OUT + '/templates/index.json'); S = d['sections']
HONEYS = [
 ("kashmiri-acacia-honey", "Kashmiri Acacia", "#F4DE9A", "dark", "Kashmir", "Delicate, smooth and elegantly sweet, with a mild floral aroma, soft vanilla-like notes and a clean, subtle finish.", "Tea and coffee, Fruit and yoghurt, Soft cheeses"),
 ("mustard-honey", "Yellow Mustard Flower", "#EFC650", "dark", "Mustard-growing regions", "Surprisingly mild and floral, with a gentle warmth and subtle spice that develops on the palate.", "Honey mustard glazes, Mature cheddar, Salad dressings"),
 ("lychee-honey", "Lychee Blossom", "#E3B04B", "dark", "", "Delicate floral notes come first, followed by hints of tropical fruit and a light, lingering sweetness.", "Strawberries and cream, Tea and cold drinks, Soft goat's cheese"),
 ("himalayan-multifloral-honey", "Himalayan Multi-Flora", "#CF8E2A", "dark", "High-altitude Himalayan regions", "Layers of wildflower sweetness, herbal notes and subtle spice, followed by a clean, balanced finish.", "Porridge and granola, Tea and warm drinks, Baking"),
 ("fennel-honey", "Wild Fennel", "#B06E1E", "light", "Mediterranean region", "Delicate anise-like aromatics, followed by warm herbal sweetness and a complex botanical finish.", "Herbal infusions, Ricotta with black pepper, Artisan cheeses"),
 ("golden-nut-honey", "Golden Nut Infusion", "#A8742F", "light", "Raw honey, almonds, cashews and dates", "Creamy, nutty sweetness meets the caramel-like character of dates, with a rich, velvety mouthfeel.", "Toast and croissants, Porridge, Cheese and crackers"),
 ("sesame-honey", "Black Sesame", "#7E4614", "light", "Sesame-growing regions", "Rich and complex, with toasted, nutty notes balanced by caramel-like sweetness and a subtle smoky finish.", "Roasted salmon, Noodles and rice, Aged cheeses"),
]
story = S['image_with_text_bpJ8fC']
jb = {f"j{i+1}": {"type": "honey", "settings": {k2: v for k2, v in {"product": h, "name": nm, "colour": c, "ink": ink, "origin": o, "notes": notes, "pairs": pairs}.items() if v}} for i, (h, nm, c, ink, o, notes, pairs) in enumerate(HONEYS)}
journey = {"type": "uk-flavour-journey", "blocks": jb, "block_order": list(jb), "settings": {"heading": clean(first(story, 'heading', 'heading')), "text": plain(first(story, 'text', 'text'))}}
ctx = {'first': False, 'hero': True, 'n': 0, 'title': 'Home'}
new, order = {}, []
for k in d['order']:
    s = S[k]
    if s.get('disabled') or k == 'text_scrolling_WNLnfY': continue
    if s['type'] == 'apps' and not s.get('blocks'): continue
    if k == 'image_with_text_bpJ8fC': new['journey'] = journey; order.append('journey'); continue
    res = conv(k, s, ctx)
    if not res: continue
    for kk, v in res: new[kk] = v; order.append(kk)
# trust marquee straight under the hero, as on beeblend.in
if 'text_scrolling_khjh3U' in order:
    order.remove('text_scrolling_khjh3U'); order.insert(order.index('video_section_QdfyKG') + 1, 'text_scrolling_khjh3U')
# the "How BeeBlend works" text sits on the forest-green band like beeblend.in's comparison
d['sections'] = new; d['order'] = order; save('templates/index.json', d)
print('built', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
