# Mide los cuadros por segundo al hacer scroll sobre la galería en WebKit (el motor de Safari), activando y quitando piezas.
import json, sys
from playwright.sync_api import sync_playwright
V={'base':'', 'sinMarcador':'.mk,.mk-sm{filter:none!important}', 'sinMascaras':'*{-webkit-mask:none!important;mask:none!important}',
   'sinPedacitos':'.scraps{display:none!important}', 'sinSombraPedacitos':'.scraps{filter:none!important}', 'sinPliegos':'.ply{display:none!important}',
   'sinFiltrosNada':'*{filter:none!important;-webkit-mask:none!important;mask:none!important}', 'sinArrancar':'JS', 'sinFondoFijo':'body::before{display:none!important}'}
JS="""() => new Promise(res => { const g=document.querySelector('.mosaic'), A=g.getBoundingClientRect().top+scrollY-500, B=A+g.offsetHeight+200;
  let t0=performance.now(), last=t0, dts=[], y=A, d=14; scrollTo(0,A);
  function f(t){ dts.push(t-last); last=t; y+=d; if(y>B||y<A) d=-d; scrollTo(0,y); if (t-t0<6000) requestAnimationFrame(f); else {dts.shift(); dts.sort((a,b)=>a-b);
    res({fps:Math.round(1000/(dts.reduce((a,b)=>a+b)/dts.length)), p90:Math.round(dts[Math.floor(dts.length*.9)]), max:Math.round(dts[dts.length-1])}); } }
  requestAnimationFrame(f); })"""
with sync_playwright() as p:
    for eng in (p.webkit,):
        b = eng.launch()
        for name,css in V.items():
            for rep in range(2):
                pg = b.new_page(viewport={"width":1512,"height":945}, device_scale_factor=2, timezone_id="America/Mexico_City")
                if css=='JS': pg.add_init_script("const _si=window.setInterval;window.setInterval=(f,t)=>t===200?0:_si(f,t);")
                pg.goto("http://localhost:8765/index.html"); pg.wait_for_timeout(1500)
                if css and css!='JS': pg.add_style_tag(content=css)
                pg.wait_for_timeout(300)
                print(eng.name, name, rep, pg.evaluate(JS), flush=True); pg.close()
        b.close()
