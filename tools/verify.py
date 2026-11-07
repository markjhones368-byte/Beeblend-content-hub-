import urllib.request,re,json
U={'/blogs/news/multiflora-vs-monofloral-honey':'Multiflora honey meaning in Hindi','/blogs/news/sarson-ke-phool-ka-shahad':'सरसों का शहद','/collections/jar':'Compare our raw honey jars',
'/collections/sachet':'Wholesale honey sachets','/collections/gifts':'Honey gift ideas by occasion','/blogs/recipes/5-ways-to-sweeten-your-morning-with-beeblend-honey':'Keep reading',
'/blogs/recipes/desserts-reimagined-drizzling-honey-over-cakes-ice-cream':'Golden Turmeric Honey Blend','/products/fennel-honey':'Fennel Flower Honey (Saunf)','/products/lychee-honey':'Fresh lychees and a wooden honey dipper'}
out={}
for p,s in U.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request('https://beeblend.in'+p,headers={'User-Agent':'Mozilla/5.0'}),timeout=40); h=r.read().decode('utf-8','replace')
        out[p]={'status':r.status,'found':s.lower() in h.lower(),'title':re.search(r'<title>(.*?)</title>',h,re.S).group(1).strip()[:90]}
    except Exception as e: out[p]={'err':str(e)}
json.dump(out,open('verify.json','w'),ensure_ascii=False,indent=1)
