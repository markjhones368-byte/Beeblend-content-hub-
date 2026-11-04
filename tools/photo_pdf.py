"""Collect every photo from the BeeBlend websites and build one PDF (runs on GitHub Actions)."""
import io, json, re, sys, time, urllib.request
from urllib.parse import urljoin, urlparse
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

UA = {'User-Agent': 'Mozilla/5.0 (BeeBlend photo export)'}
SITES = [('beeblend.co.uk', 'United Kingdom'), ('beeblend.in', 'India')]
PAGES = ['/', '/pages/about-us', '/pages/gifting', '/collections/all', '/collections/jar', '/collections/sachet', '/pages/contact']
def get(url, binary=False, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                d = r.read(); return d if binary else d.decode('utf-8', 'replace')
        except Exception as e:
            err = e; time.sleep(1.5)
    print('FAIL', url, err); return None
def key(u):
    p = urlparse(u).path.split('/')[-1]
    p = re.sub(r'_(\d+x\d*|x\d+|\d+x)(?=\.)', '', p)          # drop size suffixes like _2000x
    return p.lower()
def clean(u):
    u = u.split('?')[0]
    if u.startswith('//'): u = 'https:' + u
    return u

collected = []   # (site, section, title, url, alt)
for host, label in SITES:
    base = 'https://' + host
    seen = set()
    # 1. product photos
    page = 1
    while True:
        txt = get(f'{base}/products.json?limit=250&page={page}')
        if not txt: break
        prods = json.loads(txt).get('products', [])
        if not prods: break
        for p in prods:
            for im in p.get('images', []):
                u = clean(im['src']); k = key(u)
                if k in seen: continue
                seen.add(k); collected.append((label, 'Products', p['title'], u, im.get('alt') or ''))
        page += 1
    # 2. other photos used on the website
    for path in PAGES:
        html = get(base + path)
        if not html: continue
        for m in re.finditer(r'(?:https?:)?//[^"\'\s>]+?/(?:cdn/shop|s/files)/[^"\'\s>]+?\.(?:jpe?g|png|webp)(?:\?[^"\'\s>]*)?', html, re.I):
            u = clean(m.group(0).replace('&amp;', '&'))
            if '/t/' in u and '/assets/' in u and not re.search(r'(poster|phc|ritual|beekeeper)', u): continue
            k = key(u)
            if k in seen or re.search(r'(logo|icon|favicon|payment|badge|sprite|placeholder|thumbnail\.0)', k): continue
            seen.add(k); collected.append((label, 'Website photos', path, u, ''))
print('found', len(collected), 'photos')

# download + shrink for the PDF
imgs = []
for site, sec, title, u, alt in collected:
    q = u + ('&' if '?' in u else '?') + 'width=1800'
    data = get(q, binary=True) or get(u, binary=True)
    if not data: continue
    try:
        im = Image.open(io.BytesIO(data)); im.load()
    except Exception as e:
        print('BAD IMAGE', u, e); continue
    if min(im.size) < 220: continue                      # skip tiny UI images
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[-1]); im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((1800, 1800))
    imgs.append((site, sec, title, u.split('/')[-1], alt, im))
print('downloaded', len(imgs))

W, H = A4; M = 36
c = canvas.Canvas('BeeBlend-website-photos.pdf', pagesize=A4)
c.setTitle('BeeBlend website photos'); c.setAuthor('BeeBlend')
forest, gold, ink, muted = HexColor('#1F3A2E'), HexColor('#C9921B'), HexColor('#24211C'), HexColor('#6B655B')
# cover
c.setFillColor(forest); c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(gold); c.setFont('Helvetica-Bold', 11); c.drawString(M, H - 140, 'BEEBLEND')
c.setFillColor(HexColor('#FFF8E8')); c.setFont('Times-Bold', 40); c.drawString(M, H - 190, 'Website photos')
c.setFont('Helvetica', 12); c.setFillColor(HexColor('#C9D3CB'))
counts = {}
for s, sec, *_ in imgs: counts[(s, sec)] = counts.get((s, sec), 0) + 1
y = H - 230
for (s, sec), n in counts.items():
    c.drawString(M, y, f'{s} · {sec}: {n}'); y -= 18
c.drawString(M, y - 10, 'Collected from beeblend.co.uk and beeblend.in on ' + time.strftime('%d %B %Y'))
c.showPage()

def header(site, sec, title):
    c.setFillColor(gold); c.setFont('Helvetica-Bold', 9); c.drawString(M, H - M, f'{site.upper()}  ·  {sec.upper()}')
    c.setFillColor(ink); c.setFont('Times-Bold', 16); c.drawString(M, H - M - 22, title[:80])
# two photos per page, each with caption
slot_h = (H - 2 * M - 60) / 2
last = None; slot = 0
for site, sec, title, fname, alt, im in imgs:
    grp = (site, sec, title if sec == 'Products' else '')
    if grp != last or slot == 2:
        if last is not None: c.showPage()
        header(site, sec, title if sec == 'Products' else 'Photos used on the website'); slot = 0; last = grp
    top = H - M - 44 - slot * slot_h
    bw, bh = W - 2 * M, slot_h - 40
    r = min(bw / im.width, bh / im.height); iw, ih = im.width * r, im.height * r
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=85, optimize=True); buf.seek(0)
    c.drawImage(ImageReader(buf), M + (bw - iw) / 2, top - ih, iw, ih)
    c.setFillColor(muted); c.setFont('Helvetica', 8)
    cap = fname + (f'  ·  {alt}' if alt else '') + (f'  ·  page {title}' if sec != 'Products' else '')
    c.drawString(M, top - ih - 12, cap[:120])
    slot += 1
c.showPage(); c.save()
print('pdf done')
