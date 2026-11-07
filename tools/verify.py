import urllib.request,re,json
U={'/collections/jar':'one flower and one region at a time','/collections/gifts':'A good gift becomes part','/collections/sachet':'without choosing a full jar','/collections/jar?x=2':'We keep our own hives','/collections/gifts?x=2':'Our pick for a gift'}
out={}
for p,s in U.items():
    try:
        r=urllib.request.urlopen(urllib.request.Request('https://beeblend.in'+p,headers={'User-Agent':'Mozilla/5.0'}),timeout=40); h=r.read().decode('utf-8','replace')
        i=h.lower().find(s.lower()[:20]); out[p]={'ctx':h[max(0,i-300):i+500] if i>=0 else '', 'status':r.status,'found':s.lower() in h.lower(),'title':re.search(r'<title>(.*?)</title>',h,re.S).group(1).strip()[:90]}
    except Exception as e: out[p]={'err':str(e)}
json.dump(out,open('verify.json','w'),ensure_ascii=False,indent=1)
