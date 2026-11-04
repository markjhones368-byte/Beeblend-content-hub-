"""Download every photo from the BeeBlend websites at original resolution, one file each (runs on GitHub Actions)."""
import json, os, re, time, urllib.request
from urllib.parse import urlparse
UA = {'User-Agent': 'Mozilla/5.0 (BeeBlend photo export)'}
SITES = [('beeblend.co.uk', 'UK'), ('beeblend.in', 'India')]
PAGES = ['/', '/pages/about-us', '/pages/gifting', '/collections/all', '/collections/jar', '/collections/sachet', '/pages/contact']
def get(url, binary=False):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = r.read(); return d if binary else d.decode('utf-8', 'replace')
        except Exception as e:
            err = e; time.sleep(2)
    print('FAIL', url, err); return None
def key(u):
    p = urlparse(u).path.split('/')[-1]
    return re.sub(r'_(\d+x\d*|x\d+|\d+x)(?=\.)', '', p).lower()
def clean(u):
    u = u.split('?')[0]; return 'https:' + u if u.startswith('//') else u
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]
out = 'photos'; n = 0; index = []
for host, label in SITES:
    base = 'https://' + host; seen = set(); items = []
    page = 1
    while True:
        txt = get(f'{base}/products.json?limit=250&page={page}')
        prods = json.loads(txt).get('products', []) if txt else []
        if not prods: break
        for p in prods:
            for i, im in enumerate(p.get('images', []), 1):
                u = clean(im['src']); k = key(u)
                if k in seen: continue
                seen.add(k); items.append((f'{label}/Products/{slug(p["handle"])}', f'{slug(p["handle"])}-{i:02d}', u))
        page += 1
    for path in PAGES:
        html = get(base + path)
        if not html: continue
        for m in re.finditer(r'(?:https?:)?//[^"\'\s>]+?/(?:cdn/shop|s/files)/[^"\'\s>]+?\.(?:jpe?g|png|webp)(?:\?[^"\'\s>]*)?', html, re.I):
            u = clean(m.group(0).replace('&amp;', '&'))
            if '/t/' in u and '/assets/' in u and not re.search(r'(poster|phc|ritual|beekeeper)', u): continue
            k = key(u)
            if k in seen or re.search(r'(logo|icon|favicon|payment|badge|sprite|placeholder|thumbnail\.0)', k): continue
            seen.add(k); items.append((f'{label}/Website photos', os.path.splitext(k)[0], u))
    for folder, name, u in items:
        data = get(u, binary=True)
        if not data or len(data) < 15000: continue           # skip failures and tiny UI images
        ext = os.path.splitext(urlparse(u).path)[1].lower() or '.jpg'
        os.makedirs(f'{out}/{folder}', exist_ok=True)
        fn = f'{out}/{folder}/{name}{ext}'
        open(fn, 'wb').write(data); n += 1; index.append(f'{fn}\t{len(data)//1024} KB\t{u}')
open(f'{out}/index.txt', 'w').write('\n'.join(index))
print('saved', n, 'photos')
