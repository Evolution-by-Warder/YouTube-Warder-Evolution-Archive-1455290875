"""One-time read-only extraction of the pinned public infobar preview archive."""
import base64, hashlib, io, json, pathlib, urllib.request, zipfile
from PIL import Image, ImageOps, ImageDraw
URL="https://raw.githubusercontent.com/Evolution-by-Warder/FullHDGlass-Warder-Evolution/08b5e6fe2870d8d6908b780c7a31ac18046da009/assets/warder/downloads/ui/icon-set-previews/warder-infobar-types.zip"
SHA="7cce388af950491a02106926d679a8254bc62313eaaccdd6fcf37b8ef585c22c"
out=pathlib.Path("infobar-review")
out.mkdir(exist_ok=True)
with urllib.request.urlopen(URL,timeout=45) as r: raw=r.read(4_000_000)
assert len(raw)==2584364
assert hashlib.sha256(raw).hexdigest()==SHA
rows=[]
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    assert z.testzip() is None
    assert sum(i.file_size for i in z.infolist())<100_000_000
    for n in sorted(z.namelist()):
        if not n.lower().endswith((".png",".jpg",".jpeg",".webp")):continue
        with Image.open(io.BytesIO(z.read(n))) as im:
            im.load()
            if im.width<100 or im.height<40:continue
            idx=len(rows)+1
            rgb=im.convert("RGBA")
            bg=Image.new("RGBA",rgb.size,(5,12,23,255));bg.alpha_composite(rgb);rgb=bg.convert("RGB")
            rgb.thumbnail((1920,1080),Image.Resampling.LANCZOS)
            full=out/f"{idx:03d}-full.webp";rgb.save(full,"WEBP",quality=91,method=4)
            small=rgb.copy();small.thumbnail((560,315),Image.Resampling.LANCZOS)
            thumb=out/f"{idx:03d}-thumb.webp";small.save(thumb,"WEBP",quality=84,method=4)
            rows.append({"id":idx,"source":n,"original_size":list(im.size),"full_size":list(rgb.size),"thumb_size":list(small.size),"full":full.name,"thumb":thumb.name})
assert rows and len(rows)<=200
(out/"inventory.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print("PREVIEW_INVENTORY "+json.dumps(rows,ensure_ascii=False),flush=True)
for offset in range(0,len(rows),24):
    batch=rows[offset:offset+24]; sheet=Image.new("RGB",(1000,((len(batch)+2)//3)*205),(10,18,30));draw=ImageDraw.Draw(sheet)
    for j,row in enumerate(batch):
        x=j%3*333;y=j//3*205
        with Image.open(out/row["thumb"]) as im:
            im.thumbnail((317,173));sheet.paste(im,(x+(333-im.width)//2,y+3))
        draw.text((x+9,y+179),str(row["id"])+" "+pathlib.PurePosixPath(row["source"]).name[:42],fill=(225,238,252))
    sheet.save(out/f"contact-{offset//24+1}.jpg",quality=91)
# Public asset data only; chunks fit the log transport without truncating individual lines.
for row in rows:
    for kind in ("full","thumb"):
        b=(out/row[kind]).read_bytes()
        encoded=base64.b64encode(b).decode("ascii")
        for p in range(0,len(encoded),12000):
            print("PREVIEW_B64 %03d %s %04d %s"%(row["id"],kind,p//12000,encoded[p:p+12000]),flush=True)
print("PREVIEW_COMPLETE "+str(len(rows)),flush=True)
