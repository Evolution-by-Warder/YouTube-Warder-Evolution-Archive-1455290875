/* Warder Evolution — orbit engine. Homepage catalog or single-product showroom. */
(()=>{
  "use strict";
  const hero=document.querySelector(".hero-visual");
  const catalog=document.querySelector("#products .products");
  if(!hero)return;
  const single=hero.dataset.orbitMode==="single";
  if(!single&&!catalog)return;
  const track=hero.querySelector(".planet-track"),toggle=hero.querySelector(".orbit-toggle"),count=hero.querySelector(".c2");
  if(!track||!toggle)return;
  const ns="http://www.w3.org/2000/svg";
  const icons={
    display:["M3 4h18v13H3z","M8 21h8M12 17v4","M7 8v5m4-5v5m-4-2.5h4m3-2.5h2a2.5 2.5 0 0 1 0 5h-2z"],
    grid:["M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z"],
    radio:["M12 9v1m0 0L7 21m5-11 5 11M9 17h6","M8.5 6a5 5 0 0 0 0 7m7-7a5 5 0 0 1 0 7M5 3a9 9 0 0 0 0 13M19 3a9 9 0 0 1 0 13"],
    play:["M4 5h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z","M10 8.5l6 3.5-6 3.5z"],
    gear:["M10 2h4l.7 3 2 .9 2.7-1.6 2.8 2.8-1.6 2.7.9 2 3 .7v4l-3 .7-.9 2 1.6 2.7-2.8 2.8-2.7-1.6-2 .9-.7 3h-4l-.7-3-2-.9-2.7 1.6-2.8-2.8 1.6-2.7-.9-2-3-.7v-4l3-.7.9-2-1.6-2.7 2.8-2.8 2.7 1.6 2-.9z","M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0"],
    star:["M12 2l3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z"]
  };
  const labels={sk:["Pozastaviť obeh planét","Spustiť obeh planét"],en:["Pause planetary orbit","Resume planetary orbit"],de:["Planetenumlauf pausieren","Planetenumlauf fortsetzen"],ru:["Приостановить орбиты планет","Возобновить орбиты планет"]};
  function buttonLabel(){
    const paused=hero.classList.contains("orbit-paused");
    const label=(labels[document.documentElement.lang]||labels.sk)[paused?1:0];
    toggle.textContent=paused?"▶":"Ⅱ";
    toggle.setAttribute("aria-label",label);toggle.title=label;
    toggle.setAttribute("aria-pressed",String(paused));
  }
  function makeIcon(key){
    const svg=document.createElementNS(ns,"svg");
    svg.setAttribute("viewBox","0 0 24 24");
    svg.setAttribute("fill","none");svg.setAttribute("stroke","currentColor");
    svg.setAttribute("stroke-width","1.5");svg.setAttribute("stroke-linecap","round");
    svg.setAttribute("stroke-linejoin","round");svg.setAttribute("aria-hidden","true");
    for(const d of (icons[key]||icons.star)){
      const path=document.createElementNS(ns,"path");path.setAttribute("d",d);svg.append(path);
    }
    return svg;
  }
  function rebuild(){
    const cards=single?[{name:hero.dataset.planetName,icon:hero.dataset.planetIcon||"star",accent:hero.dataset.planetColor||"#73dcff"}]:[...catalog.querySelectorAll(":scope > .product")].map(card=>{
      const link=card.querySelector(".product-card-link");if(!link)return null;
      const name=card.dataset.planetName||[...link.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join("").trim()||link.textContent.trim();
      return {name,href:link.getAttribute("href"),icon:card.dataset.planetIcon||"star",accent:card.dataset.planetColor||getComputedStyle(card).getPropertyValue("--accent").trim()||"#73dcff"};
    }).filter(p=>p&&p.href&&p.name);
    hero.classList.add("orbit-rebuilding");
    track.replaceChildren();track.style.setProperty("--planet-count",String(Math.max(1,cards.length)));
    cards.forEach((p,i)=>{
      const angle=-Math.PI/2+i*2*Math.PI/cards.length;
      const slot=document.createElement("div");slot.className="planet-anchor";
      slot.style.setProperty("--x",(50+50*Math.cos(angle)).toFixed(6)+"%");
      slot.style.setProperty("--y",(50+50*Math.sin(angle)).toFixed(6)+"%");
      const counter=document.createElement("div");counter.className="planet-counter";
      const a=document.createElement(single?"span":"a");a.className="planet-link";a.title=p.name;
      if(single){a.setAttribute("role","img")}else{a.href=p.href}
      a.setAttribute("aria-label",p.name);a.style.setProperty("--planet-accent",p.accent);
      const symbol=document.createElement("span");symbol.className="planet-symbol";symbol.setAttribute("aria-hidden","true");symbol.append(makeIcon(p.icon));
      const label=document.createElement("span");label.className="planet-name";label.textContent=p.name;
      a.append(symbol,label);counter.append(a);slot.append(counter);track.append(slot);
    });
    track.hidden=toggle.hidden=!cards.length;
    hero.classList.toggle("orbit-ready",!!cards.length);
    if(count)count.textContent=cards.length?"01 — "+String(cards.length).padStart(2,"0"):"00";
    void track.offsetWidth;
    hero.classList.remove("orbit-rebuilding");
  }
  toggle.addEventListener("click",()=>{hero.classList.toggle("orbit-paused");buttonLabel()});
  new MutationObserver(buttonLabel).observe(document.documentElement,{attributes:true,attributeFilter:["lang"]});
  if(catalog&&!single)new MutationObserver(rebuild).observe(catalog,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["href","data-planet-name","data-planet-icon","data-planet-color"]});
  rebuild();buttonLabel();
})();
