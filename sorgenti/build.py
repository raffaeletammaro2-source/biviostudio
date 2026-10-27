# -*- coding: utf-8 -*-
import re, json, os, html, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from services import SERVICES, SERVICE_BY_SLUG, ORDER, PHASES
from articles1 import ARTICLES_1
from articles2 import ARTICLES_2

B = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("BIVIO_OUT", os.path.dirname(B))
BASE = "https://www.biviostudio.it/"
SRC = open(os.path.join(B, "source_home.html"), encoding="utf-8").read()
ARTICLES = sorted(ARTICLES_1 + ARTICLES_2, key=lambda a: a["date"], reverse=True)
ART_BY_SLUG = {a["slug"]: a for a in ARTICLES}
MESI = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
def itdate(d): y,m,g = d.split("-"); return f"{int(g)} {MESI[int(m)-1]} {y}"
E = lambda s: html.escape(s, quote=True)

# ---------- estrazione dalla home originale
css_base = re.search(r"<style>(.*?)</style>", SRC, re.S).group(1)
def between(a, b):
    i = SRC.index(a); j = SRC.index(b, i)
    return SRC[i:j]
DEFS = between("<!-- Monogramma riutilizzabile -->", "<!-- NAV -->")
HERO = between("<!-- HERO -->", "<!-- IL BIVIO -->")
BIVIO = between("<!-- IL BIVIO -->", "<!-- METODO -->")
METODO = between("<!-- METODO -->", "<!-- SERVIZI -->")
PERCHI = between("<!-- PER CHI -->", "<!-- COME FUNZIONA -->")
COME = between("<!-- COME FUNZIONA -->", "<!-- FORM -->")
FORMSEC = between("<!-- FORM -->", "<!-- FAQ -->")
FAQ = between("<!-- FAQ -->", "<!-- CTA FINALE -->")
FINAL = between("<!-- CTA FINALE -->", "<footer>")

os.makedirs(OUT + "/assets", exist_ok=True)
os.makedirs(OUT + "/servizi", exist_ok=True)
os.makedirs(OUT + "/blog", exist_ok=True)
open(OUT + "/assets/bivio.css", "w", encoding="utf-8").write(css_base + open(os.path.join(B, "extra.css"), encoding="utf-8").read())
shutil.copy(os.path.join(B, "bivio.js"), OUT + "/assets/bivio.js")

# ---------- forme di fase
def shape(ph, size=34, cls="sh"):
    c = PHASES[ph]["color"]
    if ph == "struttura":
        inner = f'<path d="M34 34H0A34 34 0 0 1 34 0Z" fill="{c}"/>'
    elif ph == "community":
        inner = f'<circle cx="17" cy="17" r="17" fill="{c}"/>'
    elif ph == "performance":
        inner = f'<rect width="34" height="34" rx="6" fill="{c}"/>'
    else:
        inner = f'<rect width="34" height="34" rx="6" fill="#14161B"/><path d="M8 26 17 8l9 18" stroke="#FF5B1F" stroke-width="3.5" fill="none" stroke-linejoin="round"/>'
    return f'<svg class="{cls}" viewBox="0 0 34 34" width="{size}" height="{size}" aria-hidden="true">{inner}</svg>'

def cat_style(ph):
    p = PHASES[ph]
    if ph == "affiancamento": return "background:#14161B;color:#fff"
    if ph == "performance": return f"background:{p['soft']};color:#7A5200"
    return f"background:{p['soft']};color:{p['ink']}"

TICK = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#FF5B1F"/><path d="M5.5 10.5l3 3 6-6.5" stroke="#fff" stroke-width="2.2" fill="none"/></svg>'

# ---------- partial: head, nav, footer
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Sora:wght@300;400;600;700;800&display=swap">'
ORG_ID = BASE + "#organization"
ORG = {
  "@type": ["Organization", "ProfessionalService"], "@id": ORG_ID, "name": "bivio.studio",
  "alternateName": "Bivio Studio", "url": BASE,
  "description": "Growth Marketing Agency che aiuta PMI ed e-commerce a crescere con un metodo in tre fasi: struttura dei processi, community e performance marketing.",
  "slogan": "Prima il sistema, poi la crescita.",
  "telephone": "+39 081 18522008", "email": "info@biviostudio.it",
  "address": {"@type": "PostalAddress", "addressCountry": "IT"},
  "areaServed": {"@type": "Country", "name": "Italia"},
  "knowsAbout": ["Growth marketing", "Performance marketing", "Meta Ads", "Google Ads", "Gestione social media", "Content creation", "Video editing", "E-commerce", "Sviluppo siti web", "Automazione dei processi", "Intelligenza artificiale", "CRM", "Data analytics", "Formazione marketing"],
}

def head(title, desc, path, root, ld, ogtype="website"):
    url = BASE + path
    lds = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f"""<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="bivio.studio">
<meta property="og:locale" content="it_IT">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14161B">
{FONTS}
<link rel="stylesheet" href="{root}assets/bivio.css">
{lds}
"""

def svc_url(root, slug): return f"{root}servizi/{slug}.html"
def art_url(root, slug): return f"{root}blog/{slug}.html"
def home_url(root): return f"{root}index.html" if root else "index.html"

def nav(root, cur=""):
    hu = home_url(root)
    anchor = (lambda a: f"#{a}") if not root else (lambda a: f"{hu}#{a}")
    cols = ""
    for ph in PHASES:
        links = "".join(f'<a href="{svc_url(root, s)}">{E(SERVICE_BY_SLUG[s]["name"])}</a>' for s in ORDER if SERVICE_BY_SLUG[s]["phase"] == ph)
        cols += f'<div class="dd-col"><h4><i style="background:{PHASES[ph]["color"]}"></i>{PHASES[ph]["short"]}</h4>{links}</div>'
    mcols = ""
    for ph in PHASES:
        links = "".join(f'<a href="{svc_url(root, s)}">{E(SERVICE_BY_SLUG[s]["name"])}</a>' for s in ORDER if SERVICE_BY_SLUG[s]["phase"] == ph)
        mcols += f'<h4>{PHASES[ph]["short"]}</h4>{links}'
    ac = lambda k: ' aria-current="page"' if cur == k else ""
    return f"""<header class="nav">
  <div class="wrap">
    <a class="brand" href="{hu if root else '#top'}" aria-label="bivio.studio, home">
      <svg><use href="#mono"/></svg>
      <span><span class="wm"><b>bivio</b>.studio</span><span class="pay">GROWTH &amp; PERFORMANCE MARKETING</span></span>
    </a>
    <nav aria-label="Principale">
      <ul class="menu">
        <li class="dd{' cur' if cur=='servizi' else ''}"><button type="button" aria-expanded="false" aria-haspopup="true">I servizi <svg viewBox="0 0 10 10"><path d="M1 3l4 4 4-4" stroke="currentColor" stroke-width="1.6" fill="none"/></svg></button>
          <div class="dd-panel">{cols}<div class="dd-all"><span>L'ecosistema completo del digital marketing, in un'unica regia.</span><a href="{root}servizi/index.html">Tutti i servizi →</a></div></div></li>
        <li><a href="{anchor('metodo')}">Metodo</a></li>
        <li><a href="{anchor('perchi')}">Per chi</a></li>
        <li><a href="{root}blog/index.html"{ac('blog')}>Blog</a></li>
        <li><a href="{anchor('faq')}">FAQ</a></li>
      </ul>
    </nav>
    <div class="nav-r">
      <a class="btn sm" href="#consulenza">Consulenza<span class="long">&nbsp;gratuita</span> <span class="arr">→</span></a>
      <button type="button" class="burger" aria-label="Apri il menu" aria-expanded="false" aria-controls="mnav"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    </div>
  </div>
</header>
<div class="mnav" id="mnav" hidden>
  <div class="big"><a href="{hu}">Home</a><a href="{root}servizi/index.html">I servizi</a><a href="{root}blog/index.html">Blog</a><a href="{anchor('metodo')}">Metodo</a><a href="{anchor('faq')}">FAQ</a></div>
  {mcols}
</div>
"""

def footer(root):
    hu = home_url(root)
    links = "".join(f'<a href="{svc_url(root, s)}">{E(SERVICE_BY_SLUG[s]["name"])}</a>' for s in ORDER)
    return f"""<footer>
  <div class="wrap">
    <div>
      <a class="brand" href="{hu}"><svg><use href="#mono"/></svg><span><span class="wm"><b>bivio</b>.studio</span><span class="pay" style="display:block">GROWTH &amp; PERFORMANCE MARKETING</span></span></a>
      <p class="claim">Prima il sistema,<br>poi la crescita.</p>
      <div class="bars"><i style="background:var(--o)"></i><i style="background:var(--v)"></i><i style="background:var(--a)"></i></div>
    </div>
    <div>
      <h4>I servizi</h4>
      <div class="fl svc-links">{links}</div>
    </div>
    <div>
      <h4>Esplora</h4>
      <div class="fl"><a href="{root}servizi/index.html">Tutti i servizi</a><a href="{hu}#metodo">Il metodo</a><a href="{hu}#perchi">Per chi lavoriamo</a><a href="{root}blog/index.html">Blog</a><a href="#consulenza">Consulenza gratuita</a></div>
    </div>
    <div>
      <h4>Contatti</h4>
      <div class="fl"><span>081 185 22008</span><span>info@biviostudio.it</span><span>Operiamo in tutta Italia, in presenza e da remoto</span></div>
    </div>
    <div class="legal"><span>© 2026 bivio.studio · P.IVA da inserire</span><span>Privacy policy · Cookie policy</span></div>
  </div>
</footer>
<div class="mbar" id="mbar"><a class="btn" href="#consulenza">Prenota la consulenza gratuita <span class="arr">→</span></a></div>
<script src="{root}assets/bivio.js"></script>
"""

# ---------- partial: modulo con servizi aggiornati
def form_section(preselect=None, title=None, lead=None):
    f = FORMSEC
    pre = E(SERVICE_BY_SLUG[preselect]["form"]) if preselect else ""
    # Netlify Forms: nome del modulo, attributo data-netlify, honeypot anti-spam e campi nascosti
    f = f.replace('<form id="lead" novalidate>',
        f'<form id="lead" name="consulenza" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" novalidate data-pre="{pre}">\n'
        '        <input type="hidden" name="form-name" value="consulenza">\n'
        '        <input type="hidden" name="pagina" id="f-pagina" value="">\n'
        '        <input type="hidden" name="inviato_il" id="f-data" value="">\n'
        '        <p hidden><label>Non compilare questo campo: <input name="bot-field" id="f-bot"></label></p>')
    if title:
        f = f.replace('<h2 class="h2" style="margin-top:16px">Prenota la tua analisi di crescita.</h2>', f'<h2 class="h2" style="margin-top:16px">{title}</h2>')
    if lead:
        f = f.replace('<p class="lead">Più informazioni ci dai, più la call sarà concreta. Arriviamo preparati, con le prime ipotesi già pronte.</p>', f'<p class="lead">{lead}</p>')
    return f

# ---------- partial: ecosistema
def ecosystem(root):
    out = '<div class="eco">'
    for ph, p in PHASES.items():
        items = [SERVICE_BY_SLUG[s] for s in ORDER if SERVICE_BY_SLUG[s]["phase"] == ph]
        cards = ""
        for s in items:
            tags = "".join(f'<span class="tg">{E(t)}</span>' for t in s["tags"])
            cards += f'''<a class="eco-card reveal" data-ph="{ph}" style="--pc:{p['color']}" href="{svc_url(root, s['slug'])}">
  {shape(ph)}
  <div><h3>{E(s['name'])}</h3><p>{E(s['card'])}</p></div>
  <div class="tgs">{tags}</div>
  <div class="go">Scopri il servizio <span>→</span></div>
</a>'''
        out += f'''<div class="eco-group">
  <div class="eco-head reveal"><div class="ph" style="color:{p['ink'] if ph!='performance' else '#9A6700'}"><i style="background:{p['color']}"></i>{p['label']}</div><h3>{p['short']}</h3><p>{p['desc']}</p><span class="cnt">{len(items)} {'servizio' if len(items)==1 else 'servizi'}</span></div>
  <div class="eco-grid" style="--n:{len(items)}">{cards}</div>
</div>'''
    return out + '</div>'

def post_card(root, a):
    s = SERVICE_BY_SLUG[a["service"]]
    return f'''<a class="post reveal" data-cat="{s['slug']}" href="{art_url(root, a['slug'])}">
  <span class="cat" style="{cat_style(s['phase'])}">{E(s['name'])}</span>
  <h3>{E(a['title'])}</h3>
  <p>{E(a['desc'])}</p>
  <div class="meta"><span>{itdate(a['date'])} · {a['read']} min</span><b>Leggi →</b></div>
</a>'''

def faq_html(faqs):
    return "".join(f'<details class="reveal"><summary>{E(q)}<span class="pm"></span></summary><p>{E(a)}</p></details>' for q, a in faqs)
def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i+1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

def page(headpart, body, full=True):
    if not full:
        return headpart + body
    return f'<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n{headpart}</head>\n<body>\n{body}</body>\n</html>\n'

def write(path, txt):
    open(os.path.join(OUT, path), "w", encoding="utf-8").write(txt)

# ======================================================= HOME
home_faq = [
  ("La consulenza è davvero gratuita?", "Sì. La call di analisi non ha costi e non ti impegna a nulla. Alla fine ti diciamo da dove partire: se vuoi proseguire con noi, prepariamo una proposta su misura."),
  ("Gestite solo i social?", "No. I social sono un tassello dell'ecosistema digitale. Prima sistemiamo processi e strumenti, poi costruiamo la comunicazione, infine accendiamo le campagne di performance."),
  ("Ho già fatto ads e non hanno funzionato. Perché dovrebbe andare diversamente?", "Spesso il limite non sono le ads, ma quello che succede dopo il click: richieste perse, nessun CRM, nessun tracciamento. Il nostro metodo parte proprio da lì, così ogni euro investito ha un ritorno misurabile."),
  ("Cosa può fare l'intelligenza artificiale per la mia azienda?", "Può occuparsi delle attività ripetitive che oggi richiedono una persona: rispondere ai clienti su sito e WhatsApp, qualificare i contatti, preparare contenuti e report. Integriamo gli strumenti nei tuoi processi e formiamo il team a usarli."),
  ("Lavorate in tutta Italia?", "Sì. Seguiamo aziende su tutto il territorio italiano, con incontri in presenza quando servono e lavoro da remoto per tutto il resto."),
  ("Posso attivare un solo servizio?", "Sì, ogni servizio si può attivare singolarmente. Durante la consulenza ti diciamo con trasparenza se ha senso partire da lì o da un'altra fase."),
  ("Come misurate i risultati?", "Fissiamo obiettivi chiari all'inizio e li monitoriamo con report leggibili: costo per lead, costo di acquisizione cliente, vendite generate e ritorno sull'investimento."),
]
faq_home = re.sub(r'<div class="faq">.*?</div>\s*</div>\s*</section>', '<div class="faq">' + faq_html(home_faq) + '</div>\n  </div>\n</section>', FAQ, flags=re.S)

servizi_home = f'''<!-- SERVIZI -->
<section class="s" id="servizi">
  <div class="wrap">
    <div class="s-head reveal">
      <div class="eyebrow">I servizi</div>
      <h2 class="h2">L'ecosistema del digital marketing, <span class="o">in un'unica regia.</span></h2>
      <p class="lead">Dieci servizi organizzati sulle tre fasi del metodo. Ognuno funziona da solo, ma rende di più quando lavora insieme agli altri: i dati del CRM migliorano le campagne, i contenuti alimentano le ads, le automazioni liberano tempo per vendere.</p>
    </div>
    {ecosystem("")}
    <div class="eco-cta reveal" style="margin-top:30px"><p class="lead" style="font-size:16px;color:var(--muted)">Non sai da quale servizio partire? È esattamente quello che scopriamo nella consulenza.</p><a class="btn magnet" href="#consulenza">Trova il punto di partenza <span class="arr">→</span></a></div>
  </div>
</section>

'''
blog_home = f'''<section class="s" id="blog" style="padding-top:0">
  <div class="wrap">
    <div class="s-head reveal">
      <div class="eyebrow">Dal blog</div>
      <h2 class="h2">Guide pratiche per far crescere la tua azienda.</h2>
    </div>
    <div class="posts">{"".join(post_card("", a) for a in ARTICLES[:3])}</div>
    <div class="eco-cta" style="margin-top:22px"><span></span><a class="btn dark" href="blog/index.html">Tutti gli articoli <span class="arr">→</span></a></div>
  </div>
</section>

'''
hero_home = HERO
marq = '<span>' + '</span><span>'.join(SERVICE_BY_SLUG[s]["name"] for s in ORDER) + '</span>'
hero_home = re.sub(r'<div class="track">.*?</div>', f'<div class="track">\n    {marq}\n    {marq}\n  </div>', hero_home, flags=re.S)
# nel marquee niente link: aria-hidden

home_ld = [
  {"@context": "https://schema.org", **ORG,
   "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Servizi di digital marketing", "itemListElement": [
     {"@type": "Offer", "itemOffered": {"@type": "Service", "name": SERVICE_BY_SLUG[s]["h1"], "url": BASE + f"servizi/{s}.html"}} for s in ORDER]}},
  {"@context": "https://schema.org", "@type": "WebSite", "name": "bivio.studio", "url": BASE, "inLanguage": "it-IT", "publisher": {"@id": ORG_ID}},
  faq_ld(home_faq),
]
home_title = "bivio.studio | Growth Marketing Agency per PMI ed e-commerce"
home_desc = "Growth Marketing Agency per PMI ed e-commerce in tutta Italia. Processi, CRM e AI, social e contenuti, Meta e Google Ads, e-commerce e siti web. Consulenza gratuita."
home_body = DEFS + nav("") + hero_home + BIVIO + METODO + servizi_home + PERCHI + COME + form_section() + faq_home + blog_home + FINAL + footer("")
home_head = head(home_title, home_desc, "", "", home_ld)
write("index.html", page(home_head, home_body))
# versione per l'artifact (senza scheletro html/head/body)
if os.environ.get("BIVIO_ARTIFACT"): open(os.environ["BIVIO_ARTIFACT"], "w", encoding="utf-8").write(page(home_head.replace("<title>bivio.studio | Growth Marketing Agency per PMI ed e-commerce</title>", "<title>bivio.studio</title>"), home_body, full=False))

# ======================================================= PAGINE SERVIZIO
R = "../"
for s in SERVICES:
    p = PHASES[s["phase"]]
    path = f"servizi/{s['slug']}.html"
    pains = "".join(f'<li><i>!</i><span>{E(x)}</span></li>' for x in s["pains"])
    pains_title = s.get("pains_title", "Ti suona familiare?")
    pains_after = s.get("pains_after", "Sono segnali comuni, e quasi sempre hanno una causa precisa nei processi o negli strumenti. In consulenza la individuiamo insieme.")
    dl = "".join(f'<div class="dl reveal">{shape(s["phase"], 30)}<h3>{E(t)}</h3><p>{E(d)}</p></div>' for t, d in s["deliver"])
    steps = "".join(f'<div class="st reveal"><div class="n">{i+1:02d}</div><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, (t, d) in enumerate(s["steps"]))
    perchi = "".join(f'<li>{TICK}<span>{E(x)}</span></li>' for x in s["perchi"])
    rel = "".join(f'<a href="{svc_url(R, r)}">{E(SERVICE_BY_SLUG[r]["name"])} <small>{PHASES[SERVICE_BY_SLUG[r]["phase"]]["short"]} →</small></a>' for r in s["related"])
    posts = "".join(post_card(R, ART_BY_SLUG[a]) for a in s["articles"])
    pc = p["color"] if s["phase"] != "affiancamento" else "#FF5B1F"
    big_shape = shape(s["phase"], 360, "ph-shape")
    body = DEFS + nav(R, "servizi") + f'''<section class="phero" id="top">
  {big_shape}
  <div class="wrap">
    <nav class="crumbs" aria-label="Percorso"><a href="{home_url(R)}">Home</a><span aria-hidden="true">/</span><a href="{R}servizi/index.html">Servizi</a><span aria-hidden="true">/</span><span>{E(s['name'])}</span></nav>
    <div>
      <div class="eyebrow" style="color:{pc if s['phase']!='struttura' else '#A996FF'}">{p['label']}</div>
      <h1>{E(s['h1'])}</h1>
      <p class="sub">{E(s['sub'])}</p>
      <div class="ctas"><a class="btn magnet" href="#consulenza">Richiedi la consulenza gratuita <span class="arr">→</span></a><a class="btn ghost" href="#cosa-facciamo">Cosa facciamo</a></div>
    </div>
    <aside class="inbreve"><div class="lbl">In breve</div><p>{E(s['inbreve'])}</p></aside>
  </div>
</section>

<section class="s" id="problemi">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Il problema</div><h2 class="h2">{E(pains_title)}</h2></div>
    <ul class="pain-list">{pains}</ul>
    <div class="pain-after reveal"><p>{E(pains_after)}</p><a class="btn" href="#consulenza">Analizziamolo insieme <span class="arr">→</span></a></div>
  </div>
</section>

<section class="s" id="cosa-facciamo" style="padding-top:0">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Cosa facciamo</div><h2 class="h2">Il servizio {E(s['name'])}, nel dettaglio.</h2></div>
    <div class="dl-grid">{dl}</div>
  </div>
</section>

<section class="s metodo" id="come" style="--pc:{pc}">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Come lavoriamo</div><h2 class="h2">Quattro passaggi, dal primo incontro ai risultati.</h2></div>
    <div class="steps4" style="--pc:{pc}">{steps}</div>
  </div>
</section>

<section class="s">
  <div class="wrap split">
    <div class="sbox reveal"><h3>Per chi è questo servizio</h3><ul class="ticks">{perchi}</ul></div>
    <div class="sbox reveal rel"><h3>Funziona ancora meglio con</h3>{rel}<a href="{R}servizi/index.html">Tutto l'ecosistema <small>10 servizi →</small></a></div>
  </div>
</section>

<section class="s" id="faq" style="padding-top:0">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Domande frequenti</div><h2 class="h2">{E(s['name'])}: le domande più comuni.</h2></div>
    <div class="faq">{faq_html(s['faq'])}</div>
  </div>
</section>

<section class="s" style="padding-top:0">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Approfondimenti</div><h2 class="h2">Dal blog.</h2></div>
    <div class="posts two">{posts}</div>
  </div>
</section>

''' + form_section(s["slug"], "Richiedi la consulenza gratuita.", f"Ci occupiamo di {s['name'].lower()} dentro un percorso di crescita completo. Raccontaci la tua situazione: arriviamo alla call con le prime ipotesi già pronte.") + footer(R)
    ld = [
      {"@context": "https://schema.org", "@type": "Service", "name": s["h1"], "serviceType": s["name"], "description": s["desc"],
       "url": BASE + path, "provider": {"@id": ORG_ID, "@type": "ProfessionalService", "name": "bivio.studio", "url": BASE},
       "areaServed": {"@type": "Country", "name": "Italia"}, "inLanguage": "it-IT",
       "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"], "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t, "description": d}} for t, d in s["deliver"]]}},
      faq_ld(s["faq"]),
      crumbs_ld([("Home", ""), ("Servizi", "servizi/index.html"), (s["name"], path)]),
    ]
    write(path, page(head(s["title"], s["desc"], path, R, ld), body))

# ======================================================= HUB SERVIZI
hub_path = "servizi/index.html"
hub_body = DEFS + nav(R, "servizi") + f'''<section class="phero" id="top">
  <div class="wrap">
    <nav class="crumbs" aria-label="Percorso"><a href="{home_url(R)}">Home</a><span aria-hidden="true">/</span><span>Servizi</span></nav>
    <div>
      <div class="eyebrow">I servizi</div>
      <h1>L'ecosistema del digital marketing per PMI ed e-commerce</h1>
      <p class="sub">Dieci servizi, una sola regia. Li organizziamo sulle tre fasi del nostro metodo, perché la crescita regge solo quando struttura, comunicazione e campagne lavorano insieme.</p>
      <div class="ctas"><a class="btn magnet" href="#consulenza">Prenota la consulenza gratuita <span class="arr">→</span></a></div>
    </div>
    <aside class="inbreve"><div class="lbl">In breve</div><p>bivio.studio è una Growth Marketing Agency che opera in tutta Italia. Offre servizi di automazione dei processi e AI, CRM, siti web, data analytics, gestione social media, content creation e video, Meta Ads, Google Ads, e-commerce e formazione per team marketing interni, a PMI ed e-commerce.</p></aside>
  </div>
</section>
<section class="s">
  <div class="wrap">
    {ecosystem(R)}
  </div>
</section>
''' + form_section(None, "Non sai da dove partire?", "Raccontaci la tua azienda e i tuoi obiettivi. Nella consulenza gratuita ti indichiamo quali servizi servono davvero, e in quale ordine.") + footer(R)
hub_ld = [
  {"@context": "https://schema.org", "@type": "ItemList", "name": "Servizi di digital marketing di bivio.studio", "itemListElement": [
     {"@type": "ListItem", "position": i+1, "url": BASE + f"servizi/{s}.html", "name": SERVICE_BY_SLUG[s]["h1"]} for i, s in enumerate(ORDER)]},
  crumbs_ld([("Home", ""), ("Servizi", hub_path)]),
]
write(hub_path, page(head("Servizi di digital marketing per PMI ed e-commerce | bivio.studio", "Automazioni e AI, CRM, siti web, data analytics, social media, content creation, Meta Ads, Google Ads, e-commerce e formazione: tutti i servizi di bivio.studio.", hub_path, R, hub_ld), hub_body))

# ======================================================= BLOG INDEX
blog_path = "blog/index.html"
filt = '<button type="button" data-cat="all" aria-pressed="true">Tutti</button>' + "".join(f'<button type="button" data-cat="{s}" aria-pressed="false">{E(SERVICE_BY_SLUG[s]["name"])}</button>' for s in ORDER)
blog_body = DEFS + nav(R, "blog") + f'''<section class="phero" id="top">
  <div class="wrap">
    <nav class="crumbs" aria-label="Percorso"><a href="{home_url(R)}">Home</a><span aria-hidden="true">/</span><span>Blog</span></nav>
    <div>
      <div class="eyebrow">Blog</div>
      <h1>Guide di marketing digitale per PMI ed e-commerce</h1>
      <p class="sub">Articoli pratici su social, contenuti, ads, e-commerce, siti web, CRM, automazioni, dati e AI. Scritti per chi deve prendere decisioni, non per chi deve riempire un calendario.</p>
    </div>
    <aside class="inbreve"><div class="lbl">Come leggerli</div><p>Ogni articolo si apre con un riepilogo dei punti chiave e si chiude con le domande frequenti. Filtra per servizio per trovare le guide sul tema che ti interessa.</p></aside>
  </div>
</section>
<section class="s">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filtra per servizio">{filt}</div>
    <div class="posts">{"".join(post_card(R, a) for a in ARTICLES)}</div>
  </div>
</section>
''' + form_section(None) + footer(R)
blog_ld = [
  {"@context": "https://schema.org", "@type": "Blog", "name": "Blog bivio.studio", "url": BASE + blog_path, "inLanguage": "it-IT", "publisher": {"@id": ORG_ID},
   "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": BASE + f"blog/{a['slug']}.html", "datePublished": a["date"]} for a in ARTICLES]},
  crumbs_ld([("Home", ""), ("Blog", blog_path)]),
]
write(blog_path, page(head("Blog di marketing digitale per PMI | bivio.studio", "Guide pratiche su social media, contenuti, Meta e Google Ads, e-commerce, siti web, CRM, automazioni, data analytics e AI per PMI ed e-commerce.", blog_path, R, blog_ld), blog_body))

# ======================================================= ARTICOLI
def slugify(t):
    t = t.lower()
    for a, b in [("à","a"),("è","e"),("é","e"),("ì","i"),("ò","o"),("ù","u"),("'"," ")]: t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]

for a in ARTICLES:
    s = SERVICE_BY_SLUG[a["service"]]
    p = PHASES[s["phase"]]
    path = f"blog/{a['slug']}.html"
    heads = []
    def add_id(m):
        t = re.sub("<.*?>", "", m.group(1)); i = slugify(t); heads.append((i, t)); return f'<h2 id="{i}">{m.group(1)}</h2>'
    bodyhtml = re.sub(r"<h2>(.*?)</h2>", add_id, a["body"])
    heads.append(("domande-frequenti", "Domande frequenti"))
    toc = "".join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t in heads)
    summ = "".join(f"<li>{E(x)}</li>" for x in a["summary"])
    faqs = "".join(f'<h3>{E(q)}</h3><p>{E(an)}</p>' for q, an in a["faq"])
    # correlati: l'altro articolo dello stesso servizio + 1 per servizio collegato
    rel = [x for x in s["articles"] if x != a["slug"]] + [SERVICE_BY_SLUG[r]["articles"][0] for r in s["related"][:2]]
    relcards = "".join(post_card(R, ART_BY_SLUG[x]) for x in rel)
    body = DEFS + '<div class="read-prog" aria-hidden="true"></div>' + nav(R, "blog") + f'''<section class="phero art-head" id="top">
  <div class="wrap">
    <nav class="crumbs" aria-label="Percorso"><a href="{home_url(R)}">Home</a><span aria-hidden="true">/</span><a href="{R}blog/index.html">Blog</a><span aria-hidden="true">/</span><a href="{svc_url(R, s['slug'])}">{E(s['name'])}</a></nav>
    <div>
      <a class="art-cat" style="{cat_style(s['phase'])}" href="{svc_url(R, s['slug'])}">{E(s['name'])}</a>
      <h1>{E(a['title'])}</h1>
      <div class="art-meta"><span>Di <b>Redazione bivio.studio</b></span><span>Pubblicato il <b><time datetime="{a['date']}">{itdate(a['date'])}</time></b></span><span>Lettura <b>{a['read']} minuti</b></span></div>
    </div>
  </div>
</section>
<section class="s" style="padding-top:56px">
  <div class="wrap art">
    <aside class="toc" aria-label="Indice">
      <div class="lbl">In questo articolo</div>
      <ol>{toc}</ol>
      <div class="side-cta"><b>{E(s['name'])}</b><p>Vuoi applicarlo alla tua azienda? Ne parliamo in una call gratuita.</p><a class="btn sm" href="#consulenza">Prenota <span class="arr">→</span></a></div>
    </aside>
    <article class="art-body">
      <div class="inbreve"><div class="lbl">In breve</div><ul>{summ}</ul></div>
      <details class="toc-m"><summary>Indice dell'articolo</summary><ol>{toc}</ol></details>
      <div class="prose">
        {bodyhtml}
        <div class="art-cta"><span class="q" aria-hidden="true"></span><h3>Vuoi un piano su misura per la tua azienda?</h3><p>Con il servizio {E(s['name'])} mettiamo in pratica quello che hai letto, dentro un percorso di crescita completo.</p><div class="row-b"><a class="btn" href="#consulenza">Prenota la consulenza gratuita <span class="arr">→</span></a><a class="btn ghost" href="{svc_url(R, s['slug'])}">Scopri il servizio</a></div></div>
        <h2 id="domande-frequenti">Domande frequenti</h2>
        {faqs}
      </div>
    </article>
  </div>
</section>
<section class="s" style="padding-top:0">
  <div class="wrap">
    <div class="s-head reveal"><div class="eyebrow">Continua a leggere</div><h2 class="h2">Articoli correlati.</h2></div>
    <div class="posts">{relcards}</div>
  </div>
</section>
''' + form_section(a["service"]) + footer(R)
    words = len(re.sub("<.*?>", " ", a["body"]).split())
    ld = [
      {"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"], "description": a["desc"],
       "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "it-IT", "wordCount": words,
       "mainEntityOfPage": BASE + path, "url": BASE + path,
       "author": {"@type": "Organization", "name": "Redazione bivio.studio", "url": BASE},
       "publisher": {"@id": ORG_ID, "@type": "Organization", "name": "bivio.studio", "url": BASE},
       "about": {"@type": "Service", "name": s["name"], "url": BASE + f"servizi/{s['slug']}.html"},
       "abstract": " ".join(a["summary"])},
      faq_ld(a["faq"]),
      crumbs_ld([("Home", ""), ("Blog", "blog/index.html"), (s["name"], f"servizi/{s['slug']}.html"), (a["title"], path)]),
    ]
    write(path, page(head(a["seo"], a["desc"], path, R, ld, "article"), body))

# ======================================================= SEO files
urls = [("", "1.0", "2026-10-27"), ("servizi/index.html", "0.9", "2026-10-27"), ("blog/index.html", "0.7", ARTICLES[0]["date"])]
urls += [(f"servizi/{s}.html", "0.9", "2026-10-27") for s in ORDER]
urls += [(f"blog/{a['slug']}.html", "0.6", a["date"]) for a in ARTICLES]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod><priority>{p}</priority></url>\n" for u, p, d in urls) + "</urlset>\n"
write("sitemap.xml", sm)
write("robots.txt", f"User-agent: *\nAllow: /\n\n# Crawler dei motori di ricerca e degli assistenti AI ammessi (GEO)\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")
llms = f"# bivio.studio\n\n> Growth Marketing Agency che opera in tutta Italia. Aiuta PMI ed e-commerce a crescere con un metodo in tre fasi: Struttura (processi, CRM, dati, automazioni e AI), Community (social media e contenuti) e Performance (Meta Ads, Google Ads, e-commerce). Offre una consulenza gratuita di analisi.\n\nContatti: tel. 081 185 22008, info@biviostudio.it. Area servita: tutta Italia.\n\n## Servizi\n\n"
llms += "".join(f"- [{SERVICE_BY_SLUG[s]['h1']}]({BASE}servizi/{s}.html): {SERVICE_BY_SLUG[s]['card']}\n" for s in ORDER)
llms += "\n## Blog\n\n" + "".join(f"- [{a['title']}]({BASE}blog/{a['slug']}.html): {a['desc']}\n" for a in ARTICLES)
write("llms.txt", llms)
print("ok", len(SERVICES), "servizi,", len(ARTICLES), "articoli")
