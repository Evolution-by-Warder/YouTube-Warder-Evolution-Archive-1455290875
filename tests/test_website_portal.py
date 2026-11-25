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

    def test_receiver_gallery_payload_when_present(self):
        import json,base64
        docs=ROOT/'docs'
        for name in ('fullhdglass.html','piconhub.html','radio.html','youtube-warder.html','gsu.html'):
            self.assertIn('receiver-gallery.js',(docs/name).read_text())
        path=docs/'warder-product-screenshots.json'
        if not path.is_file():return
        data=json.loads(path.read_text())
        self.assertEqual(data['schema'],1)
        self.assertEqual(set(data['products']),{'glass','picon','radio','youtube','gsu'})
        self.assertGreaterEqual(sum(len(x) for x in data['products'].values()),31)
        for items in list(data['products'].values())+[data.get('variants',[])]:
            for item in items:
                self.assertTrue(item['en'] and item['sk'])
                for field in ('full','thumb'):
                    prefix,encoded=item[field].split(',',1)
                    self.assertIn(prefix,('data:image/webp;base64','data:image/png;base64','data:image/jpeg;base64'))
                    self.assertTrue(base64.b64decode(encoded,validate=True))
                self.assertGreater(item['width'],0)
                self.assertGreater(item['height'],0)
