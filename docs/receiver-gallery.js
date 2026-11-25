/* Owner-supplied real receiver screenshots. No third-party scripts or archive downloads. */
(()=>{"use strict";
const keys={"detail-glass":"glass","detail-picon":"picon","detail-radio":"radio","detail-youtube":"youtube","detail-gsu":"gsu"};
const key=Object.keys(keys).find(k=>document.body.classList.contains(k));
if(!key)return;
const language=()=>document.documentElement.lang==="sk"?"sk":"en";
const bi=(en,sk)=>{const f=document.createDocumentFragment();for(const [lang,text] of [["en",en],["sk",sk]]){const s=document.createElement("span");s.className=lang;s.lang=lang;s.textContent=text;f.append(s)}return f};
const el=(name,cls,text)=>{const x=document.createElement(name);if(cls)x.className=cls;if(text)x.textContent=text;return x};
const imageData=s=>typeof s==="string"&&/^data:image\/(webp|png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(s);
const valid=x=>x&&typeof x.en==="string"&&typeof x.sk==="string"&&imageData(x.full)&&imageData(x.thumb)&&Number.isInteger(x.width)&&Number.isInteger(x.height)&&x.width>0&&x.height>0;
function render(items,id,titleEn,titleSk,subtitleEn,subtitleSk,compact=false){
items=items.filter(valid);if(!items.length)return;
const section=el("section","shell detail-section receiver-gallery"+(compact?" compact-variants":""));section.id=id;
const heading=el("div","section-heading"),wrap=el("div"),eyebrow=el("div","eyebrow"),h=el("h2"),p=el("p");eyebrow.append(bi("VISUAL EXPERIENCE","VIZUÁLNY ZÁŽITOK"));h.append(bi(titleEn,titleSk));p.append(bi(subtitleEn,subtitleSk));wrap.append(eyebrow,h);heading.append(wrap,p);section.append(heading);
const grid=el("div","receiver-gallery-grid");section.append(grid);
const links=[];
items.forEach((item,index)=>{const fig=el("figure","receiver-gallery-item"),link=el("a","receiver-gallery-link"),img=el("img"),zoom=el("span","receiver-gallery-zoom","⤢"),caption=el("figcaption");link.href=item.full;link.setAttribute("aria-label",item[language()]);img.src=item.thumb;img.alt=item[language()];img.loading=index<2?"eager":"lazy";img.width=item.width;img.height=item.height;zoom.setAttribute("aria-hidden","true");caption.append(bi(item.en,item.sk));link.append(img,zoom);fig.append(link,caption);grid.append(fig);links.push(link);
if(typeof HTMLDialogElement!=="undefined")link.addEventListener("click",ev=>{if(ev.button!==0||ev.ctrlKey||ev.metaKey||ev.shiftKey||ev.altKey)return;ev.preventDefault();let current=index;const dialog=el("dialog","screenshot-dialog"),bar=el("div","screenshot-controls"),label=el("span","screenshot-caption"),full=el("img");const sk=language()==="sk";dialog.setAttribute("aria-label",sk?"Galéria snímok":"Screenshot gallery");label.setAttribute("aria-live","polite");
const button=(text,aria)=>{const b=el("button","",text);b.type="button";b.setAttribute("aria-label",aria);return b};
const prev=button("←",sk?"Predchádzajúca snímka":"Previous screenshot"),next=button("→",sk?"Nasledujúca snímka":"Next screenshot"),close=button("×",sk?"Zavrieť":"Close");bar.append(prev,label,next,close);dialog.append(bar,full);document.body.append(dialog);
function show(){const x=items[current];full.src=x.full;full.alt=sk?x.sk:x.en;label.textContent=(current+1)+" / "+items.length+" — "+full.alt;prev.disabled=current===0;next.disabled=current===items.length-1}
function step(n){current=Math.max(0,Math.min(items.length-1,current+n));show()}
prev.onclick=()=>step(-1);next.onclick=()=>step(1);close.onclick=()=>dialog.close();dialog.addEventListener("keydown",e=>{if(e.key==="ArrowLeft"||e.key==="ArrowRight"){e.preventDefault();step(e.key==="ArrowLeft"?-1:1)}});dialog.addEventListener("close",()=>{dialog.remove();link.focus()});show();dialog.showModal();close.focus()});
});
const release=document.querySelector(".release-section");if(!release)return;release.before(section);
const nav=document.querySelector(".nav-links"),download=nav?.querySelector('a[href="#download"]');
if(nav&&download&&id==="screenshots"){const anchor=el("a");anchor.href="#screenshots";anchor.append(bi("Gallery","Galéria"));nav.insertBefore(anchor,download)}
}
fetch("warder-product-screenshots.json",{cache:"default"}).then(response=>{if(!response.ok)throw Error("Screenshot data unavailable");return response.json()}).then(data=>{if(data.schema!==1||!data.products)return;const items=data.products[keys[key]];if(Array.isArray(items))render(items,"screenshots","See it in action.","Pozrite si ho v akcii.","Real screenshots captured directly on a receiver.","Skutočné snímky priamo z prijímača.");if(keys[key]==="glass"&&Array.isArray(data.variants))render(data.variants,"interface-variants","Make it your own.","Vyberte si vlastný štýl.","Original previews of available interface variants.","Pôvodné náhľady možných prevedení prostredia.",true)}).catch(()=>{/* No empty galleries are shown. */});
})();
