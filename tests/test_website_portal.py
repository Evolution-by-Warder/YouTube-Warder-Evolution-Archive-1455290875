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
        if 'href' in a: self.href.append(a['href'])
        if 'src' in a: self.src.append(a['src'])
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
        self.assertTrue(all(not x.endswith('.js') or x=='portal.js' for x in p.src))

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
