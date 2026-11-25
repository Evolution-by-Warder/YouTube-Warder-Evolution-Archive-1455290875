from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.href=[]; self.src=[]; self.lang=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if 'href' in a: self.href.append(a['href'].split('?',1)[0] if a['href'].startswith(('portal.css?','portal-orbit.css?','portal-art/skull.png?')) else a['href'])
        if 'src' in a: self.src.append(a['src'].split('?',1)[0] if a['src'].startswith(('portal.js?','portal-orbit.js?','portal-art/skull.png?')) else a['src'])
        if 'lang' in a: self.lang.append(a['lang'])
class WebsitePortalTests(unittest.TestCase):
    def test_portal_assets_links_and_products(self):
        docs=ROOT/'docs'; p=Parser(); p.feed((docs/'index.html').read_text())
        self.assertEqual(len(p.ids),len(set(p.ids)))
        self.assertTrue({'glass','picon','radio','youtube','gsu','products','about','main'}<=set(p.ids))
        self.assertTrue({'en','sk'}<=set(p.lang))
        for href in p.href+p.src:
            if href.startswith('#'): self.assertIn(href[1:],p.ids)
            elif not href.startswith('https://'): self.assertTrue((docs/href).is_file(),href)
        for name in ["FullHDGlass-Warder-Evolution","PiconHub-Warder-Evolution","Radio-Warder-Evolution","YouTube-Warder-Evolution","GSU-Warder-Evolution"]:
            self.assertIn('https://github.com/Evolution-by-Warder/'+name+'/releases/latest',p.href)
        self.assertEqual(sum(x.endswith('_all.ipk') for x in p.href),5)
        self.assertNotIn('privacy.html',p.href); self.assertNotIn('terms.html',p.href)
        self.assertEqual((docs/'CNAME').read_text().strip(),'warder-evolution.eu')
        for name in ('youtube.html','privacy.html','terms.html'): self.assertTrue((docs/name).is_file())
        self.assertIn('privacy.html',(docs/'youtube.html').read_text())
        self.assertIn('terms.html',(docs/'youtube.html').read_text())
    def test_no_external_scripts(self):
        p=Parser(); p.feed((ROOT/'docs/index.html').read_text()); self.assertIn('portal.js',p.src)
        self.assertTrue(all(not x.endswith('.js') or x in ('portal.js','portal-orbit.js') for x in p.src))

    def test_individual_product_pages(self):
        docs=ROOT/'docs'
        names={'fullhdglass.html':'FullHDGlass','piconhub.html':'PiconHub','radio.html':'Radio','youtube-warder.html':'YouTube','gsu.html':'GSU'}
        home=Parser(); home.feed((docs/'index.html').read_text())
        for filename,name in names.items():
            self.assertIn(filename,home.href)
            source=(docs/filename).read_text()
            p=Parser();p.feed(source)
            self.assertEqual(len(p.ids),len(set(p.ids)))
            self.assertTrue({'main','features','download'}<=set(p.ids))
            self.assertTrue({'en','sk'}<=set(p.lang))
            self.assertIn('portal.js',p.src)
            self.assertEqual(source.count('class="feature-card"'),8,filename)
            self.assertEqual(source.count('class="family-card"'),4,filename)
            self.assertIn('index.html#products',p.href)
            self.assertTrue(any(x.endswith('_all.ipk') for x in p.href))
            self.assertTrue(any(x.endswith('/releases/latest') for x in p.href))
            self.assertNotIn('privacy.html',p.href)
            self.assertNotIn('terms.html',p.href)
            for href in p.href+p.src:
                if href.startswith('#'):self.assertIn(href[1:],p.ids,filename)
                elif not href.startswith('https://'):self.assertTrue((docs/href.split('#')[0]).is_file(),href)

    def test_marketing_pages_no_technical_gallery_archives(self):
        docs=ROOT/'docs'
        for filename in ('index.html','fullhdglass.html','piconhub.html','radio.html','youtube-warder.html','gsu.html'):
            source=(docs/filename).read_text()
            p=Parser();p.feed(source)
            self.assertFalse(any(h.lower().split('?')[0].endswith(('.zip','.rar','.7z')) for h in p.href),filename)
            self.assertNotIn('portal-art/gallery/',source)
            self.assertNotIn('weather-wind-help.png',source)
            self.assertNotIn('weather-uv-help.png',source)

    def test_real_receiver_galleries(self):
        import json,hashlib
        docs=ROOT/'docs'
        data=json.loads((docs/'screenshots/provenance.json').read_text())
        pages={'glass':'fullhdglass.html','picon':'piconhub.html','gsu':'gsu.html','radio':'radio.html','youtube':'youtube-warder.html'}
        self.assertEqual({k:len(v) for k,v in data['products'].items()},{'glass':12,'picon':3,'gsu':7,'radio':10,'youtube':8})
        for key,items in data['products'].items():
            source=(docs/pages[key]).read_text()
            self.assertIn('id="screenshots"',source)
            self.assertEqual(source.count('class="shot-zoom"'),len(items))
            for item in items:
                self.assertEqual((item['width'],item['height']),(1920,1080))
                self.assertTrue(item['en'] and item['sk'])
                for kind in ('full','thumb'):
                    b=(docs/item[kind]).read_bytes()
                    self.assertEqual(b[:4],b'RIFF')
                    self.assertEqual(b[8:12],b'WEBP')
                    self.assertEqual(hashlib.sha1(('blob %d\0'%len(b)).encode()+b).hexdigest(),item[kind+'_git_blob'])
                    self.assertIn(item[kind],source)

    def test_fullhdglass_infobar_gallery(self):
        import json,hashlib
        docs=ROOT/'docs'
        data=json.loads((docs/'screenshots/infobars/provenance.json').read_text())
        items=data['items']
        self.assertEqual(len(items),78)
        self.assertEqual([r['type'] for r in items],list(range(1,66))+list(range(70,78))+[87,88,89,98,99])
        self.assertEqual(next(r for r in items if r['type']==38)['source'],'37.jpg')
        self.assertEqual(next(r for r in items if r['type']==37)['source'],'follow-up/38.jpg')
        self.assertIsNone(data['missing_type'])
        page=(docs/'fullhdglass-infobars.html').read_text()
        p=Parser();p.feed(page)
        self.assertEqual(len(p.ids),len(set(p.ids)))
        self.assertEqual(page.count('class="shot-zoom"'),78)
        self.assertIn('fullhdglass-infobars.html',(docs/'fullhdglass.html').read_text())
        self.assertFalse(any(h.lower().endswith('.zip') for h in p.href))
        for item in items:
            self.assertEqual((item['width'],item['height']),(1920,1080))
            self.assertIn('Infobar type '+str(item['type']),page)
            self.assertIn('Infobar typu '+str(item['type']),page)
            for kind in ('full','thumb'):
                b=(docs/item[kind]).read_bytes()
                self.assertEqual(b[:4],b'RIFF')
                self.assertEqual(b[8:12],b'WEBP')
                self.assertEqual(hashlib.sha1(('blob %d\0'%len(b)).encode()+b).hexdigest(),item[kind+'_git_blob'])
                self.assertIn(item[kind],p.href if kind=='full' else p.src)

    def test_infobar_collection_card_order(self):
        import re
        source=(ROOT/"docs/fullhdglass.html").read_text()
        grid=source.split('id="screenshots"',1)[1].split("</section>",1)[0]
        links=re.findall(r'<figure[^>]*><a href="([^"]+)"',grid)
        self.assertEqual(links,["screenshots/glass/01-full.webp","fullhdglass-infobars.html","screenshots/glass/02-full.webp","fullhdglass-channel-selection.html","screenshots/glass/03-full.webp","screenshots/glass/04-full.webp","screenshots/glass/05-full.webp"]+["screenshots/glass/%02d-full.webp"%n for n in range(6,13)])
        self.assertIn('src="screenshots/infobars/37-full.webp"',grid)
        self.assertEqual(grid.count('href="fullhdglass-infobars.html"'),1)
        self.assertIn("Pozrite si 78 typov infobarov",grid)

    def test_channel_selection_gallery(self):
        import json,hashlib
        docs=ROOT/"docs"
        data=json.loads((docs/"screenshots/channel-selection/provenance.json").read_text())
        self.assertEqual(data["source_count"],48)
        self.assertEqual(data["duplicates"],{"41.jpg":"40.jpg"})
        items=data["items"]
        self.assertEqual(len(items),47)
        self.assertEqual(len({x["full_git_blob"] for x in items}),47)
        self.assertEqual([x["source"] for x in items], [str(n)+".jpg" for n in range(1,41)]+["follow-up/43.jpg","42.jpg","43.jpg","follow-up/46.jpg","44.jpg","45.jpg","46.jpg"])
        self.assertEqual([x["sk"] for x in items[39:45]],["s PIG","s PIG 2","s PIG 3","s PIG 4","s PIG 5","s PIG 6"])
        self.assertEqual([x["full"] for x in items],["screenshots/channel-selection/%02d-full.webp"%n for n in range(1,48)])
        self.assertIn("Pozrite si 47 variantov výberu kanálov",(docs/"fullhdglass.html").read_text())
        page=(docs/"fullhdglass-channel-selection.html").read_text()
        p=Parser();p.feed(page)
        self.assertEqual(len(p.ids),len(set(p.ids)))
        self.assertEqual(page.count('class="shot-zoom"'),47)
        self.assertFalse(any(h.lower().endswith(".zip") for h in p.href))
        for item in items:
            self.assertTrue(item["sk"] and item["en"])
            self.assertEqual(item["original_size"],[1920,1080])
            left,top,right,bottom=item["crop"]
            self.assertTrue(0<=left<right<=1920 and 0<=top<bottom<=1080)
            self.assertEqual((item["width"],item["height"]),(right-left,bottom-top))
            self.assertTrue(400<=item["width"]<=440 and 175<=item["height"]<=200)
            self.assertEqual(item["full_git_blob"],item["thumb_git_blob"])
            self.assertIn('src="%s" width="%s" height="%s"'%(item["thumb"],item["width"],item["height"]),page)
            for kind in ("full","thumb"):
                b=(docs/item[kind]).read_bytes()
                self.assertEqual(b[:4],b"RIFF")
                self.assertEqual(b[8:12],b"WEBP")
                self.assertEqual(hashlib.sha1(("blob %d\0"%len(b)).encode()+b).hexdigest(),item[kind+"_git_blob"])
                self.assertIn(item[kind],p.href if kind=="full" else p.src)
        self.assertNotIn("V dodanej kolekcii nie je samostatný záber typu 37.",(docs/"fullhdglass-infobars.html").read_text())

    def test_channel_selection_card_uses_clean_pig_crop(self):
        docs=ROOT/"docs"
        source=(docs/"fullhdglass.html").read_text()
        self.assertIn('src="screenshots/channel-selection/card-preview-pig.webp" width="428" height="185"',source)
        self.assertEqual((docs/"screenshots/channel-selection/card-preview-pig.webp").read_bytes(),(docs/"screenshots/channel-selection/40-full.webp").read_bytes())

    def test_homepage_product_card_links(self):
        import re
        docs=ROOT/"docs"
        source=(docs/"index.html").read_text()
        cards=re.findall(r'<article class="product [^"]+" id="([^"]+)"[^>]*>(.*?)</article>',source,re.S)
        expected={"glass":"fullhdglass.html","picon":"piconhub.html","radio":"radio.html","youtube":"youtube-warder.html","gsu":"gsu.html"}
        self.assertEqual(len(cards),5)
        self.assertEqual({key for key,_ in cards},set(expected))
        for key,card in cards:
            self.assertIn('<h3><a class="product-card-link" href="'+expected[key]+'">',card)
            self.assertIn('class="btn primary" href="'+expected[key]+'"',card)
            self.assertEqual(card.count('class="product-card-link"'),1)
            p=Parser();p.feed(card)
            self.assertEqual(len(p.href),5)
            self.assertEqual(sum(h.endswith(".ipk") for h in p.href),1)
            self.assertEqual(sum(h.endswith("/releases/latest") for h in p.href),1)
        css=(docs/"portal.css").read_text()
        self.assertIn(".product-card-link::after",css)
        self.assertIn("a:not(.product-card-link)",css)

    def test_dvb_radio_rds_caption(self):
        import json
        docs=ROOT/"docs"
        item=next(x for x in json.loads((docs/"screenshots/provenance.json").read_text())["products"]["glass"] if x["full"]=="screenshots/glass/11-full.webp")
        self.assertEqual(item["sk"],"Režim rádia – DVB-S s RDS/RT+")
        self.assertEqual(item["en"],"Radio mode – DVB-S with RDS/RT+")
        page=(docs/"fullhdglass.html").read_text()
        self.assertIn('data-caption-sk="'+item["sk"]+'"',page)
        self.assertIn('data-caption-en="'+item["en"]+'"',page)

    def test_four_language_marketing_portal(self):
        import re
        docs=ROOT/"docs"
        langs=("sk","en","de","ru")
        pages=("index.html","fullhdglass.html","piconhub.html","radio.html","youtube-warder.html","gsu.html","fullhdglass-infobars.html","fullhdglass-channel-selection.html")
        for filename in pages:
            source=(docs/filename).read_text()
            self.assertIn('<html lang="sk" data-language="sk">',source)
            self.assertEqual(re.findall(r'<button data-lang="([^"]+)"',source),list(langs))
            counts=[source.count('class="'+lang+'" lang="'+lang+'"') for lang in langs]
            self.assertGreater(counts[0],0)
            self.assertEqual(len(set(counts)),1,filename)
            for lang in langs:
                self.assertIn('data-text-'+lang+'=',source)
                self.assertIn('data-content-'+lang+'=',source)
            for anchor in re.findall(r'<a [^>]*data-caption-en="[^"]+"[^>]*>',source):
                for lang in langs:
                    self.assertRegex(anchor,r'data-caption-'+lang+r'="[^"]+"')
        home=(docs/"index.html").read_text()
        for key,filename in (("glass","fullhdglass.html"),("picon","piconhub.html"),("radio","radio.html"),("youtube","youtube-warder.html"),("gsu","gsu.html")):
            card=re.search(r'<article class="product [^"]+" id="'+key+r'"[^>]*>(.*?)</article>',home,re.S).group(1)
            detail=(docs/filename).read_text()
            if key in ("glass","radio"):
                self.assertIn("podporuje 21 jazykov",card)
                self.assertIn("podporuje 21 jazykov",detail)
            else:
                self.assertIn("Pripravuje sa rozšírenie jazykovej podpory na 21 jazykov.",card)
                self.assertIn("Pripravuje sa rozšírenie jazykovej podpory na 21 jazykov.",detail)
        script=(docs/"portal.js").read_text()
        self.assertIn('let initial="sk"',script)
        self.assertNotIn("navigator.language",script)

    def test_language_cache_safety(self):
        import re
        docs=ROOT/"docs"
        for filename in ("index.html","fullhdglass.html","piconhub.html","radio.html","youtube-warder.html","gsu.html","fullhdglass-infobars.html","fullhdglass-channel-selection.html"):
            page=(docs/filename).read_text()
            self.assertIn('href="portal.css?v=20261125-skull1"',page)
            self.assertIn('src="portal.js?v=20261125-langfix2"',page)
            self.assertIn('id="warder-language-guard"',page)
            for lang in ("en","de","ru"):
                tags=re.findall(r'<span class="'+lang+r'" lang="'+lang+r'"[^>]*>',page)
                self.assertTrue(tags,filename)
                self.assertTrue(all(" hidden>" in tag for tag in tags),filename)
            self.assertNotIn('<span class="sk" lang="sk" hidden>',page)
        self.assertIn('el.hidden=el.getAttribute("lang")!==lang',(docs/"portal.js").read_text())

    def test_compatibility_distinguishes_images_from_receivers(self):
        import re
        docs=ROOT/"docs"
        for filename in ("fullhdglass.html","piconhub.html","radio.html","youtube-warder.html","gsu.html"):
            source=(docs/filename).read_text()
            match=re.search(r'<h3><span class="sk" lang="sk">Kompatibilita</span>.*?</h3><p>(.*?)</p>',source,re.S)
            self.assertIsNotNone(match,filename)
            paragraph=match.group(1)
            for lang,word in (("sk","image"),("en","images"),("de","Images"),("ru","образ")):
                span=re.search(r'<span class="'+lang+r'" lang="'+lang+r'"(?: hidden)?>(.*?)</span>',paragraph,re.S)
                self.assertIsNotNone(span,filename)
                text=span.group(1)
                for token in ("Enigma2","OpenATV","OpenPLi",word):
                    self.assertIn(token,text,filename)
            self.assertNotIn("prijímače OpenATV",paragraph)
            self.assertNotIn("OpenATV and OpenPLi receivers",paragraph)
            if filename=="fullhdglass.html":
                self.assertIn("MIPS/MIPSEL",paragraph)
                self.assertIn("ARM/AArch64",paragraph)

    def test_restored_skull_source(self):
        import struct,zlib,re
        docs=ROOT/"docs"
        b=(docs/"portal-art/skull.png").read_bytes()
        self.assertEqual(b[:8],b"\x89PNG\r\n\x1a\n")
        w,h,depth,color=struct.unpack(">IIBB",b[16:26])
        self.assertEqual((w,h,depth,color),(425,445,8,6))
        pos=8; packed=[]
        while pos<len(b):
            n=struct.unpack(">I",b[pos:pos+4])[0]
            if b[pos+4:pos+8]==b"IDAT": packed.append(b[pos+8:pos+8+n])
            pos+=12+n
        raw=zlib.decompress(b"".join(packed)); stride=w*4+1
        self.assertEqual(len(raw),stride*h)
        self.assertTrue(all(raw[y*stride]==0 for y in range(h)))
        alpha=lambda x,y:raw[y*stride+1+x*4+3]
        self.assertTrue(all(alpha(x,y)==0 for x in (0,w-1) for y in range(h)))
        self.assertGreater(alpha(25,226),100)
        self.assertGreater(alpha(399,226),100)
        self.assertNotIn("mask-image",re.search(r"\.skull\{([^}]+)\}",(docs/"portal.css").read_text()).group(1))
        self.assertIn('class="skull" src="portal-art/skull.png?v=20261125-skull1" alt="" width="425" height="445"',(docs/"index.html").read_text())

    def test_product_orbit_sources(self):
        docs=ROOT/'docs'
        page=(docs/'index.html').read_text()
        css=(docs/'portal-orbit.css').read_text()
        js=(docs/'portal-orbit.js').read_text()
        self.assertIn('class="planet-track" hidden',page)
        self.assertEqual(page.count('data-planet-icon='),5)
        self.assertIn('catalog.querySelectorAll(":scope > .product")',js)
        self.assertIn('i*2*Math.PI/cards.length',js)
        self.assertIn('linear infinite reverse',css)
        self.assertIn('prefers-reduced-motion:reduce',css)
        self.assertIn('portal-orbit.js',(docs/'WEBSITE-ORBIT.md').read_text())
