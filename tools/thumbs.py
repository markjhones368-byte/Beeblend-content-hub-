import urllib.request, io, json
from PIL import Image, ImageDraw
urls=json.load(open('tools/thumbs.json'))
tiles=[]
for i,u in enumerate(urls):
    try:
        b=urllib.request.urlopen(urllib.request.Request(u+('&' if '?' in u else '?')+'width=360',headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
        im=Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((360,360))
    except Exception as e: im=Image.new('RGB',(360,360),'grey')
    c=Image.new('RGB',(370,400),'white'); c.paste(im,(5,5)); ImageDraw.Draw(c).text((8,372),str(i),fill='black'); tiles.append(c)
cols=6
for p in range(0,len(tiles),18):
    part=tiles[p:p+18]; rows=(len(part)+cols-1)//cols
    sheet=Image.new('RGB',(370*cols,400*rows),'white')
    for k,t in enumerate(part): sheet.paste(t,((k%cols)*370,(k//cols)*400))
    sheet.save(f'thumbs_{p//18}.jpg',quality=80)
