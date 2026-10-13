import json,re,os,glob
OUT='uktheme'
def load(p):
    s=open(p).read(); s=re.sub(r'^\s*/\*.*?\*/','',s,flags=re.S); return json.loads(s)
schemas={}
for f in glob.glob(OUT+'/sections/*.liquid'):
    s=open(f).read(); m=re.search(r'{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}',s,re.S)
    schemas[os.path.basename(f)[:-7]]=json.loads(re.sub(r",(\s*[\]}])",r"\1",m.group(1))) if m else {}
UK_PRODUCTS={'lychee-honey','fennel-honey','himalayan-multifloral-honey','sesame-honey','mustard-honey','golden-nut-honey','kashmiri-acacia-honey'}
UK_COLS={'frontpage','gifts','honeycomb','candles','hampers','corporate-gifting','festive-hampers','personalized-gifts','jar','sachet','all'}
UK_PAGES={'contact','about-us','gifting','health-benefits','shipping-delivery','returns-refunds','terms-conditions','privacy-policy','which-honey-should-i-choose','honey-pairing-guide','data-sharing-opt-out'}
errs=[]
def chk_val(where,v):
    for m in re.findall(r'shopify://(products|collections|pages)/([\w-]+)',json.dumps(v)):
        k,h=m
        if (k=='products' and h not in UK_PRODUCTS) or (k=='collections' and h not in UK_COLS) or (k=='pages' and h not in UK_PAGES): errs.append(f'{where}: missing {k}/{h}')
    for h in re.findall(r'href=\\?"(/[^"\\]+)',json.dumps(v)):
        p=h.split('?')[0]
        m=re.match(r'/(products|collections|pages|blogs)/([\w-]+)',p)
        if m:
            k,x=m.groups()
            ok={'products':UK_PRODUCTS,'collections':UK_COLS,'pages':UK_PAGES,'blogs':{'recipes'}}[k]
            if x not in ok: errs.append(f'{where}: bad link {p}')
def chk_settings(where,given,decl):
    ids={x.get('id'):x for x in decl if x.get('id')}
    for k,v in (given or {}).items():
        if k not in ids: errs.append(f'{where}: unknown setting {k}')
        else:
            t=ids[k]['type']
            if t=='product' and v and v not in UK_PRODUCTS: errs.append(f'{where}: product {v} missing in UK')
            if t=='product_list': [errs.append(f'{where}: product {x} missing') for x in v if x not in UK_PRODUCTS]
            if t=='collection' and v and v not in UK_COLS: errs.append(f'{where}: collection {v} missing')
            if t=='blog' and v and v!='recipes': errs.append(f'{where}: blog {v} missing')
            if t=='select' and v not in [o['value'] for o in ids[k].get('options',[])]: errs.append(f'{where}: bad select {k}={v}')
files=glob.glob(OUT+'/templates/*.json')+glob.glob(OUT+'/templates/customers/*.json')+glob.glob(OUT+'/sections/*.json')
for f in files:
    d=load(f); w=os.path.relpath(f,OUT)
    secs=d.get('sections',{})
    for k in d.get('order',[]):
        if k not in secs: errs.append(f'{w}: order key {k} missing')
    for k,s in secs.items():
        t=s['type']; where=f'{w}:{k}({t})'
        if t not in schemas: errs.append(f'{where}: section file missing'); continue
        sc=schemas[t]; chk_settings(where,s.get('settings'),sc.get('settings',[]))
        btypes={b['type']:b for b in sc.get('blocks',[])}
        for bk,b in (s.get('blocks') or {}).items():
            bt=b['type']
            if bt.startswith('shopify://apps/'): continue
            if bt not in btypes and '@app' not in btypes and '@theme' not in btypes: errs.append(f'{where}: block type {bt} unknown'); continue
            if bt in btypes: chk_settings(f'{where}/{bk}',b.get('settings'),btypes[bt].get('settings',[]))
        for bk in s.get('block_order',[]):
            if bk not in (s.get('blocks') or {}): errs.append(f'{where}: block_order {bk} missing')
        chk_val(where,s)
print(len(files),'files checked'); print('\n'.join(sorted(set(errs))) or 'NO ERRORS')
