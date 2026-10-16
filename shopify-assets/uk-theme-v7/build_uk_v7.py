"""BeeBlend UK v7: the beeblend.in look exactly as v4 (forest, gold, paper, Young Serif + Figtree, same layout and UK data),
with v5's honesty fixes, the Pure Honey Collection 'coming soon', and conversion add-ons that use only real store facts:
free-UK-delivery progress (store's own £50 free Standard rate), delivery estimate from the shipping policy,
buy-box reassurance, payment icons, service-promise strip, and calmer premium motion."""
import json, re, os, shutil, subprocess
B = os.path.dirname(os.path.abspath(__file__))
subprocess.run(['python3', B + '/build_uk_v4.py'], check=True, stdout=subprocess.DEVNULL)
SRC = B + '/uktheme4'; OUT = B + '/uktheme7'; X6 = B + '/ukextra6'; X7 = B + '/ukextra7'
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(SRC, OUT)
def load(p):
    s = open(p).read(); s = re.sub(r'^\s*/\*.*?\*/', '', s, flags=re.S); return json.loads(s)
def save(p, d):
    with open(p, 'w') as f: json.dump(d, f, ensure_ascii=False, indent=1)
def copytree_into(src):
    for r, _, files in os.walk(src):
        for f in files:
            a = os.path.join(r, f); rel = os.path.relpath(a, src)
            os.makedirs(os.path.dirname(OUT + '/' + rel), exist_ok=True); shutil.copy(a, OUT + '/' + rel)
copytree_into(X6); copytree_into(X7)

# ---------- 1. honesty fixes carried from v5 (no invented scores, no sample reviews, one FAQPage per page) ----------
p = OUT + '/sections/bb-faq.liquid'; s = open(p).read()
s = s.replace('<script type="application/ld+json">', '{%- if section.settings.schema -%}\n<script type="application/ld+json">', 1)
s = s.replace('</script>\n{% schema %}', '</script>\n{%- endif -%}\n{% schema %}', 1)
s = s.replace('{ "type": "checkbox", "id": "open_first", "label": "Open first question", "default": true },', '{ "type": "checkbox", "id": "open_first", "label": "Open first question", "default": true },\n    { "type": "checkbox", "id": "schema", "label": "Add these questions to Google (use on one FAQ per page)", "default": true },', 1)
assert 'section.settings.schema' in s and '"id": "schema"' in s; open(p, 'w').write(s)
ASSURE = {"b1": {"type": "badge", "settings": {"icon": "leaf", "title": "100% natural"}},
          "b2": {"type": "badge", "settings": {"icon": "drop", "title": "No preservatives"}},
          "b3": {"type": "badge", "settings": {"icon": "hex", "title": "Ethically harvested"}},
          "b4": {"type": "badge", "settings": {"icon": "shield", "title": "Secure checkout"}}}
CONF = {"type": "custom_liquid", "settings": {"custom_liquid": "{% render 'uk-buy-confidence' %}"}}
for f in sorted(os.listdir(OUT + '/templates')):
    if not f.endswith('.json'): continue
    p = OUT + '/templates/' + f; d = load(p); S = d['sections']; changed = False; faq_seen = 0
    for k in list(d['order']):
        sec = S[k]
        if sec['type'] == 'uk-taste-profile':
            d['order'].remove(k); del S[k]; changed = True; continue
        if sec['type'] == 'bb-product-assurance':
            sec['blocks'] = ASSURE; sec['block_order'] = list(ASSURE); changed = True
        if sec['type'] == 'bb-faq':
            faq_seen += 1; sec['settings']['schema'] = faq_seen == 1; changed = True
        if sec['type'] == 'main-product' and 'buy_buttons' in sec.get('block_order', []) and 'uk_confidence' not in sec['blocks']:
            sec['blocks']['uk_confidence'] = CONF
            bo = sec['block_order']; bo.insert(bo.index('buy_buttons') + 1, 'uk_confidence'); changed = True
        for b in (sec.get('blocks') or {}).values():
            st = b.get('settings', {})
            if st.get('review_data') == 'sample_data': del st['review_data']; changed = True
            if st.get('show_sample_reviews') is True: st['show_sample_reviews'] = False; changed = True
    if changed: save(p, d)

# ---------- 2. Pure Honey Collection coming-soon, in the beeblend.in palette ----------
p = OUT + '/sections/uk-coming-soon.liquid'; s = open(p).read()
for a, b in [('#16130F', '#1F3A2E'), ('#F8F3E8', '#FBF4E4'), ('#EFE6D3', '#FFF8E8'), ('#1C1814', '#24211C'), ('#B8914D', '#C9921B'),
             ('#D4B57A', '#E2B341'), ('#9C7A3C', '#A87A12'), ('#E6CC93', '#F4DE9A'), ('#EFE7D6', '#F2E8D2'), ('#EFE3C6', '#F6E7C1'),
             ('rgba(184,145,77,', 'rgba(201,146,27,'), ("'Jost'", "'Figtree'"), ('"label": "Charcoal"', '"label": "Forest green"'), ('"label": "Ivory"', '"label": "Cream"')]:
    s = s.replace(a, b)
s = s.replace("#{{ sid }} .ukcs__row button{min-height:5.4rem;padding:0 3rem;border:0;border-radius:999px;background:#C9921B;color:#1F3A2E;font:500",
              "#{{ sid }} .ukcs__row button{min-height:5.4rem;padding:0 3rem;border:0;border-radius:999px;background:#C9921B;color:#1d1606;font:600")
s = s.replace("#{{ sid }} .ukcs__form{margin-top:3.2rem;max-width:48rem}", "#{{ sid }} .ukcs__form,#{{ sid }} .ukcs__points+form{margin-top:3.2rem;max-width:48rem;display:block}")
s = s.replace('#{{ sid }} .ukcs__form label{', '#{{ sid }} form label{')
open(p, 'w').write(s)
GIFT_IMG = 'shopify://shop_images/pure-honey-collection-gift-box.jpg'
CS_TEXT = "<p>Our honey sachet tasting box: 24 tear-open 10g sachets, four each of six raw honeys, so you can taste them side by side. Perfect for gifting, travel and the office.</p>"
CS_POINTS = "Himalayan Multi, Fennel, Kashmiri Acacia, Mustard, Lychee and Ayurveda Blend\n24 sachets × 10g (240g in total)\nGift-ready box"
def coming_soon(h1=False, bg='ivory'):
    return {"type": "uk-coming-soon", "settings": {"image": GIFT_IMG, "badge": "Coming soon", "eyebrow": "Coming soon", "heading": "The Pure Honey Collection",
            "heading_tag": "h1" if h1 else "h2", "text": CS_TEXT, "points": CS_POINTS, "show_form": True, "bg": bg}}

# ---------- 3. service promises (real facts from delivery rates and policies) ----------
def promises(bg='#FFFCF5', compact=False):
    items = [("truck", "Free UK delivery", "On orders over £50", "/policies/shipping-policy"),
             ("clock", "Dispatched in 1–3 days", "Tracked, with UK delivery in 3–5 working days", ""),
             ("box", "Packed with care", "Glass jars wrapped for safe delivery", ""),
             ("lock", "Secure checkout", "Pay safely with the methods you trust", "")]
    blocks = {f"p{i+1}": {"type": "item", "settings": {"icon": ic, "title": t, "text": tx, **({"link": l} if l else {})}} for i, (ic, t, tx, l) in enumerate(items)}
    return {"type": "uk-service-strip", "blocks": blocks, "block_order": list(blocks), "settings": {"bg": bg, "compact": compact}}

save(OUT + '/templates/collection.sachet.json', {"sections": {
    "coming": coming_soon(h1=True),
    "promise": promises(compact=True),
    "jars": {"type": "bb-product-grid", "settings": {"heading": "Our raw honey jars", "text": "Available now, in 160g and 250g.", "collection": "jar", "limit": 8, "columns": 4, "quick_add": True, "show_sold_out": True, "center": False, "button_label": "Shop all honey", "bg": "white"}}},
    "order": ["coming", "promise", "jars"]})
p = OUT + '/templates/page.gifting.json'; d = load(p)
d['sections']['phc_coming'] = coming_soon(bg='charcoal'); d['order'].insert(1, 'phc_coming'); save(p, d)

p = OUT + '/templates/index.json'; d = load(p)
cc = d['sections'].get('collection_list_YR74Ua')
for b in (cc or {}).get('blocks', {}).values():
    if b['settings'].get('collection') == 'sachet':
        b['settings'].update({"label": "Pure Honey Collection", "sub": "Coming soon", "image": GIFT_IMG})
d['sections']['uk_promise'] = promises()
d['order'].insert(d['order'].index('text_scrolling_khjh3U') + 1, 'uk_promise')
save(p, d)
for f in ('collection.json', 'collection.honey-jars.json', 'list-collections.json'):
    p = OUT + '/templates/' + f
    if not os.path.exists(p): continue
    d = load(p); d['sections']['uk_promise'] = promises(compact=True)
    i = next((i for i, k in enumerate(d['order']) if d['sections'][k]['type'] in ('main-product-grid', 'bb-product-grid', 'main-collection-product-grid', 'main-list-collections')), 1)
    d['order'].insert(i + 1, 'uk_promise'); save(p, d)

# ---------- 4. cart: free-delivery progress, empty-cart shelf, footer payment icons, announcement ----------
p = OUT + '/snippets/cart-drawer.liquid'; s = open(p).read()
s = s.replace('      <cart-drawer-items', "      {%- render 'uk-free-delivery' -%}\n      <cart-drawer-items", 1)
assert "uk-free-delivery" in s; open(p, 'w').write(s)
p = OUT + '/sections/main-cart-footer.liquid'; s = open(p).read()
s = s.replace('<div class="js-contents" {{ block.shopify_attributes }}>', "<div class=\"js-contents\" {{ block.shopify_attributes }}>\n                {%- render 'uk-free-delivery' -%}", 1)
assert "uk-free-delivery" in s; open(p, 'w').write(s)

p = OUT + '/config/settings_schema.json'; d = json.load(open(p))
d.append({"name": "BeeBlend UK", "settings": [
    {"type": "checkbox", "id": "uk_free_delivery_bar", "label": "Show free UK delivery messages", "default": True,
     "info": "Keep this in step with your Shipping and delivery settings (UK Standard is free from £50)."},
    {"type": "number", "id": "uk_free_delivery_threshold", "label": "Free UK delivery from (£)", "default": 50}]})
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)

p = OUT + '/config/settings_data.json'; d = load(p)
for st in [d.get('current')] + [v for v in d.get('presets', {}).values()]:
    if isinstance(st, dict) and st.get('cart_drawer_collection', None) == '': st['cart_drawer_collection'] = 'jar'
save(p, d)

p = OUT + '/sections/footer-group.json'; d = load(p)
for v in d['sections'].values():
    if v['type'] == 'footer': v['settings']['payment_enable'] = True
save(p, d)
p = OUT + '/sections/header-group.json'; d = load(p)
ab = d['sections']['announcement-bar']
ab['blocks']['uk-free-delivery'] = {"type": "announcement", "settings": {"text": "Free UK delivery on orders over £50", "link": "shopify://collections/all"}}
ab.setdefault('block_order', list(ab['blocks'])[:-1]); ab['block_order'].append('uk-free-delivery')
ab['settings']['auto_rotate'] = True; ab['settings']['change_slides_speed'] = 5
save(p, d)

# ---------- 5. calmer premium motion: drop pollen, ripple, magnetic pull; softer tilt; header shadow on scroll ----------
p = OUT + '/assets/uk-motion.js'; s = open(p).read()
s = s.replace('reveals(); tilt(); magnetic(); pollen(); journeyFocus(); drift();', 'reveals(); tilt(); journeyFocus(); drift();')
s = s.replace("setTimeout(function () { tilt(); magnetic(); }, 300)", "setTimeout(function () { tilt(); }, 300)")
s = s.replace("((0.5 - y) * 7).toFixed(2)", "((0.5 - y) * 3).toFixed(2)").replace("((x - 0.5) * 9).toFixed(2)", "((x - 0.5) * 4).toFixed(2)")
a = s.index('  /* 7. Tap ripple on buttons */'); b = s.index('  /* 8. Phones:')
s = s[:a] + s[b:]
s = s.replace("      if (drifters.length) driftTick();", "      document.documentElement.classList.toggle('uk-scrolled', window.scrollY > 24);\n      if (drifters.length) driftTick();")
assert 'pollen();' not in s and 'uk-scrolled' in s; open(p, 'w').write(s)

with open(OUT + '/assets/uk-skin.css', 'a') as f:
    f.write(open(B + '/uk-premium-v7.css').read())
print('built v7', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
