"""BeeBlend UK v5 'Luxury': v4 (beeblend.in layout + UK content) re-art-directed to the master brief:
charcoal + refined gold + honey amber + ivory, Cormorant Garamond + Figtree, restrained motion, no invented data."""
import json, re, os, shutil, subprocess
B = os.path.dirname(os.path.abspath(__file__))
subprocess.run(['python3', B + '/build_uk_v4.py'], check=True, stdout=subprocess.DEVNULL)
SRC = B + '/uktheme4'; OUT = B + '/uktheme5'; X5 = B + '/ukextra5'
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(SRC, OUT)
def load(p):
    s = open(p).read(); s = re.sub(r'^\s*/\*.*?\*/', '', s, flags=re.S); return json.loads(s)
def save(p, d):
    with open(p, 'w') as f: json.dump(d, f, ensure_ascii=False, indent=1)

# ---------- 1. palette + typography swap in the premium layer ----------
SWAP = [('#1F3A2E', '#16130F'), ('#1f3a2e', '#16130F'), ('#2C5140', '#2B251D'), ('rgba(31,58,46,', 'rgba(22,19,15,'),
        ('#C9921B', '#B8914D'), ('#c9921b', '#B8914D'), ('#b6820f', '#A47E3D'), ('#E5EBE3', '#EFE7D6'), ('#F6E7C1', '#EFE3C6'),
        ('#FFFCF5', '#F8F3E8'), ("'Young Serif'", "'Cormorant Garamond'"), ('Young+Serif', 'Cormorant+Garamond:wght@500;600;700')]
for d in ('assets', 'sections', 'snippets'):
    for f in os.listdir(OUT + '/' + d):
        if not (f.startswith('bb-') or f.startswith('uk-')): continue
        p = f'{OUT}/{d}/{f}'
        if f.endswith(('.webp', '.png', '.jpg', '.woff2', '.gif')): continue
        s = open(p).read(); o = s
        for a, b in SWAP: s = s.replace(a, b)
        if f == 'bb-global.css':
            s = s.replace("font-family:'Cormorant Garamond',Georgia,serif!important;text-transform:none!important;letter-spacing:-.01em!important;font-weight:400!important", "font-family:'Cormorant Garamond',Georgia,serif!important;text-transform:none!important;letter-spacing:0!important;font-weight:600!important")
        if s != o: open(p, 'w').write(s)

# ---------- 2. new skin + motion (replaces v4's) ----------
for f in os.listdir(X5 + '/assets'): shutil.copy(X5 + '/assets/' + f, OUT + '/assets/' + f)

# ---------- 3. FAQ schema: one FAQPage per page ----------
p = OUT + '/sections/bb-faq.liquid'; s = open(p).read()
s = s.replace('<script type="application/ld+json">', '{%- if section.settings.schema -%}\n<script type="application/ld+json">', 1)
s = s.replace('</script>\n{% schema %}', '</script>\n{%- endif -%}\n{% schema %}', 1)
s = s.replace('{ "type": "checkbox", "id": "open_first", "label": "Open first question", "default": true },', '{ "type": "checkbox", "id": "open_first", "label": "Open first question", "default": true },\n    { "type": "checkbox", "id": "schema", "label": "Add these questions to Google (use on one FAQ per page)", "default": true },', 1)
assert 'section.settings.schema' in s and '"id": "schema"' in s; open(p, 'w').write(s)

# ---------- 4. templates: rhythm, no invented data, real reviews only ----------
ASSURE = {"b1": {"type": "badge", "settings": {"icon": "leaf", "title": "100% natural"}},
          "b2": {"type": "badge", "settings": {"icon": "drop", "title": "No preservatives"}},
          "b3": {"type": "badge", "settings": {"icon": "hex", "title": "Ethically harvested"}},
          "b4": {"type": "badge", "settings": {"icon": "shield", "title": "Secure checkout"}}}
for f in sorted(os.listdir(OUT + '/templates')):
    if not f.endswith('.json'): continue
    p = OUT + '/templates/' + f; d = load(p); S = d['sections']; changed = False
    faq_seen = 0
    for k in list(d['order']):
        sec = S[k]
        if sec['type'] == 'uk-taste-profile':       # scores were our own reading, not store data
            d['order'].remove(k); del S[k]; changed = True; continue
        if sec['type'] == 'bb-product-assurance':
            sec['blocks'] = ASSURE; sec['block_order'] = list(ASSURE); changed = True
        if sec['type'] == 'bb-faq':
            faq_seen += 1; sec['settings']['schema'] = faq_seen == 1; changed = True
        for b in (sec.get('blocks') or {}).values():
            st = b.get('settings', {})
            if st.get('review_data') == 'sample_data': del st['review_data']; changed = True
            if st.get('show_sample_reviews') is True: st['show_sample_reviews'] = False; changed = True
    if changed: save(p, d)

d = load(OUT + '/templates/index.json'); S = d['sections']
BG = {'featured_collection_MQcrBh': 'paper', 'image_with_text_tYq3R8': 'sage', 'image_with_text_8hbt9B': 'paper',
      'collection_list_YR74Ua': 'sage', 'logo_grid_kVhfhk': 'white', 'image_with_text_dDHrjn': 'paper'}
for k, v in BG.items():
    if k in S: S[k]['settings']['bg'] = v
save(OUT + '/templates/index.json', d)

# ---------- 5. journey: stacked cards by default (no JS, phones); sticky story only on desktop with JS ----------
p = OUT + '/sections/uk-flavour-journey.liquid'; s = open(p).read()
a = s.index('  @media(min-width:990px){\n    #{{ sid }} .ukj__scroller'); b = s.index('  /* Mobile and tablet: swipeable cards */')
desk = s[a:b].replace('\n    #{{ sid }}', '\n    .uk-js #{{ sid }}').replace(',#{{ sid }}', ',.uk-js #{{ sid }}')
desk = desk.replace('  @media(min-width:990px){\n', '  @media(min-width:990px){\n    .uk-js #{{ sid }} .ukj__marks,.uk-js #{{ sid }} .ukj__fill{display:block}\n    .uk-js #{{ sid }} .ukj__ghost{display:block}\n    .uk-js #{{ sid }} .ukj__item{border-radius:0;padding-top:0;padding-bottom:0}\n    .uk-js #{{ sid }} .ukj__media .uk-disc{width:min(100%,52rem)}\n', 1)
c = s.index('  @media (prefers-reduced-motion: reduce){', b)
stack = """  /* Default: honey cards stacked one under another (phones, tablets, and whenever JavaScript is off) */
  #{{ sid }} .ukj__marks,#{{ sid }} .ukj__fill,#{{ sid }} .ukj__ghost{display:none}
  #{{ sid }} .ukj__items{display:grid;gap:1.6rem;max-width:132rem;margin:0 auto;padding:0 1.6rem 6.4rem}
  @media(min-width:750px){#{{ sid }} .ukj__items{grid-template-columns:1fr 1fr;padding:0 3.2rem 8rem}}
  #{{ sid }} .ukj__item{display:flex;flex-direction:column-reverse;gap:2.4rem;padding:3.2rem 2.4rem;border-radius:2.4rem;background:var(--ic);position:relative;overflow:hidden}
  #{{ sid }} .ukj__media .uk-disc{width:min(72%,30rem)}
"""
s = s[:a] + stack + desk + s[c:]
open(p, 'w').write(s)

print('built v5', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
