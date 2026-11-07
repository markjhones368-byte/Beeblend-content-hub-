import urllib.request,re,json
U={'/pages/raw-honey':'What makes honey','/pages/pure-honey':'Why "pure" on the label','/pages/honey-sachets-wholesale':'How to order honey sachets wholesale','/blogs/news/litchi-shahad':'लीची शहद','/blogs/news/5-reasons-why-raw-honey-is-better-than-processed-honey':'Raw vs Processed Honey','/collections/hampers':'noindex','/collections/jar':'Single-Origin Honey Jars'}
out={}
for p,s in U.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request('https://beeblend.in'+p,headers={'User-Agent':'Mozilla/5.0'}),timeout=40); h=r.read().decode('utf-8','replace')
        i=h.lower().find(s.lower()[:20]); out[p]={'final':r.geturl(), 'status':r.status,'found':s.lower() in h.lower(),'title':re.search(r'<title>(.*?)</title>',h,re.S).group(1).strip()[:90]}
    except Exception as e: out[p]={'err':str(e)}
json.dump(out,open('verify.json','w'),ensure_ascii=False,indent=1)
