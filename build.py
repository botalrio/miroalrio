import os, re, html as H, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
HERE = os.path.dirname(os.path.abspath(__file__))
import json
tears=json.dumps(json.load(open(os.path.join(HERE,'tears.json'))),separators=(',',':'))
T=[ # cls, label-pos, label html, every(s), step, mode, big, small, aria
 ('s1','left','Hospital atiende a un menor<br>por violencia sexual',3217,1,'count','','cada 54 min','menor','menores'),
 ('s2','left','Desaparece una persona<br>y sigue sin aparecer',2282.7,1,'count','','cada 38 min','persona','personas'),
 ('s3','left','Una niña de 10 a 14<br>años se vuelve madre',3954,1,'count','','cada 66 min','niña','niñas'),
 ('m1','top','Producimos<br>6 toneladas de basura',3.705,6,'count','','cada 4 s','tonelada','toneladas'),
 ('m2','top','Asesinan a<br>una persona',1069.5,1,'count','','cada 18 min','persona','personas'),
 ('m3','top','Una persona<br>se suicida',3570.7,1,'count','','cada 60 min','persona','personas'),
 ('m4','bottom','Perdemos 310 m²<br>de cobertura arbórea',3,313.8,'count','','cada 3 s','m²','m²'),
 ('m5','bottom','Asesinan<br>a una mujer',11265,1,'count','','cada 3 h','mujer','mujeres'),
 ('m6','bottom','Se denuncia la violación<br>de una mujer o niña',1495,1,'count','','cada 25 min','mujer o niña','mujeres o niñas'),
 ('lg','top','Un estudiante abandona el bachillerato',73.3,1,'count','','cada 73 s','estudiante','estudiantes'),
]
tiles=''
for c,pos,lab,ev,st,mode,big,small,u1,un in T:
    tiles+=f'''      <figure class="tile {c} lab-{pos}">
        <figcaption class="mk-sm">{lab.replace('<br>',' <br>')}</figcaption>
        <div class="stack" data-mode="{mode}" data-every="{ev}" data-step="{st}" data-big="{big}" data-small="{small}" data-u1="{u1}" data-un="{un}"><i class="tor c"></i></div>
      </figure>
'''

# Periódico: se arma solo desde el RSS de Substack. El más nuevo va primero; el último lugar siempre es "Ver más".
FEED = 'https://miroalrio.substack.com/feed'
OCULTAR = {'ximena-y-jose'}          # slugs de Substack que NO van en el muro
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
DATA = os.path.join(HERE, 'data', 'posts.json')

def leer_feed():
    req = urllib.request.Request(FEED, headers={'User-Agent': 'Mozilla/5.0 (miroalrio.com build)'})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
    out = []
    for it in root.iter('item'):
        link = (it.findtext('link') or '').strip()
        m = re.search(r'/p/([^/?#]+)', link)
        if not m: continue
        d = parsedate_to_datetime(it.findtext('pubDate'))
        out.append({'slug': m.group(1), 'titulo': (it.findtext('title') or '').strip(),
                    'bajada': (it.findtext('description') or '').strip(), 'iso': d.strftime('%Y-%m-%d'),
                    'fecha': f'{d.day} de {MESES[d.month-1]} de {d.year}'})
    out.sort(key=lambda p: p['iso'], reverse=True)
    return out

try:
    POSTS = leer_feed()
    if not POSTS: raise ValueError('feed vacío')
    json.dump(POSTS, open(DATA, 'w'), ensure_ascii=False, indent=1)
    print('feed ok:', len(POSTS), 'posts')
except Exception as e:                 # si Substack no responde, se usa la última lista buena: el sitio nunca se rompe
    print('feed falló, uso data/posts.json:', e)
    POSTS = json.load(open(DATA))
POSTS = [p for p in POSTS if p['slug'] not in OCULTAR]

SLOTS=15; tor='<i class="tor c"></i>'; posts=''
for p in POSTS[:SLOTS-1]:
    t, d = H.escape(p['titulo']), H.escape(p['bajada'])
    posts+=f'''      <a class="post tap" role="link" tabindex="0" data-href="https://miroalrio.substack.com/p/{p['slug']}"><span class="paper"><span class="mk"><h3 class="jit">{t}</h3><p class="dek">{d}</p></span><time class="mk-sm" datetime="{p['iso']}">{p['fecha']}</time></span>{tor}</a>\n'''
for _ in range(SLOTS-1-len(POSTS[:SLOTS-1])):
    posts+=f'      <div class="post vacia" aria-hidden="true"><span class="paper"></span>{tor}</div>\n'
posts+=f'      <a class="post more tap" role="link" tabindex="0" data-href="https://miroalrio.substack.com/archive"><span class="paper"><span class="mk-sm">VER MÁS</span></span>{tor}</a>\n'
page=open(os.path.join(HERE,'tpl.html')).read().replace('<!--POSTS-->',posts).replace('/*TEARS*/',tears).replace('<!--TILES-->',tiles)
os.makedirs(os.path.join(HERE,'_site'), exist_ok=True)
open(os.path.join(HERE,'_site','index.html'),'w').write(page); print(len(page))
