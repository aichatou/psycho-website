"""Génère le site multi-pages (dist/) à partir de source.html. Usage : python3 build.py"""
import re, json, html, os, shutil, textwrap, datetime
BASE = "https://www.exemple.fr"   # À REMPLACER par le vrai nom de domaine
NAME = "Camille Laurent"; S = re.S
src = open("source.html", encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", src, S).group(1)
secs = dict(re.findall(r'<section id="(\w+)">(.*?)</section>', src, S))
foot = re.search(r"<footer>(.*?)</footer>", src, S).group(1)
ORDER = ["home","about","themes","approach","booking","pricing","blog","faq","contact"]
# id: {langue: (slug, menu, titre, description)}
P = {
"home":{"fr":("","Accueil","Psychothérapeute TCC à Lyon et en visio | Camille Laurent","Psychothérapeute TCC : dépression, burn-out, addictions, deuil. Séances en visio (Europe, Afrique) et en cabinet à Lyon."),
        "en":("","Home","CBT psychotherapist in Lyon and online | Camille Laurent","CBT psychotherapist: depression, burn-out, addiction, grief. Online sessions (Europe, Africa) and in person in Lyon.")},
"about":{"fr":("presentation","Présentation","Présentation | Camille Laurent, psychothérapeute TCC","Ma façon de travailler, le cadre des séances et mon approche de la thérapie cognitive et comportementale."),
         "en":("about","About","About | Camille Laurent, CBT psychotherapist","How I work, the setting of sessions and my approach to cognitive behavioural therapy.")},
"themes":{"fr":("themes","Thèmes","Thèmes : dépression, burn-out, addictions, deuil","Dépression, burn-out, addictions, deuil : comment la TCC peut vous aider et quand consulter un médecin."),
          "en":("topics","Topics","Topics: depression, burn-out, addiction, grief","Depression, burn-out, addiction, grief: how CBT can help and when to see a doctor.")},
"approach":{"fr":("approche","Approche","L’approche TCC en psychothérapie | Camille Laurent","La thérapie cognitive et comportementale expliquée simplement : comprendre, expérimenter, consolider."),
            "en":("approach","Approach","The CBT approach to psychotherapy | Camille Laurent","Cognitive behavioural therapy explained simply: understand, practise, consolidate.")},
"booking":{"fr":("rendez-vous","Rendez-vous","Prendre rendez-vous en visio ou à Lyon","Réservez une séance de psychothérapie en ligne ou en cabinet. Horaires affichés dans votre fuseau horaire."),
           "en":("booking","Book","Book an online or in-person session","Book a psychotherapy session online or in Lyon. Times shown in your own time zone.")},
"pricing":{"fr":("tarifs","Tarifs","Tarifs des séances de psychothérapie","Tarifs en euros et en FCFA : séances individuelles, de couple et de famille."),
           "en":("fees","Fees","Psychotherapy session fees","Fees in euros and CFA francs for individual, couple and family sessions.")},
"blog":{"fr":("blog","Blog","Blog psychothérapie et TCC | Camille Laurent","Articles sur le burn-out, le deuil et la TCC, et proposition d’articles de lecteurs."),
        "en":("blog","Blog","Psychotherapy and CBT blog | Camille Laurent","Articles on burn-out, grief and CBT, and reader article suggestions.")},
"faq":{"fr":("faq","FAQ","FAQ : séances en visio, durée, remboursement","Réponses aux questions fréquentes sur les séances de psychothérapie en visio et en cabinet."),
       "en":("faq","FAQ","FAQ: online sessions, length, reimbursement","Answers to common questions about online and in-person psychotherapy sessions.")},
"contact":{"fr":("contact","Contact","Contact et urgences | Camille Laurent","Contactez Camille Laurent par WhatsApp ou e-mail. Numéros d’urgence en France et en Europe."),
           "en":("contact","Contact","Contact and emergencies | Camille Laurent","Contact Camille Laurent by WhatsApp or email. Emergency numbers for France and Europe.")}}
THEMES = [("depression","depression"),("burn-out","burn-out"),("addictions","addiction"),("deuil","grief")]
T = {"fr":{"book":"Prendre rendez-vous","all":"Tous les thèmes","more":"Lire la suite →","other":"Autres thèmes","sw":"English","swl":"en","loc":"fr_FR"},
     "en":{"book":"Book a session","all":"All topics","more":"Read more →","other":"Other topics","sw":"Français","swl":"fr","loc":"en_GB"}}

def url(l, i, t=None):
    s = P[i][l][0]; u = f"/{l}/" + (s + "/" if s else "")
    return u + THEMES[t][l == "en"] + "/" if t is not None else u
def lang(s, l):
    o, w = ("e", "f") if l == "fr" else ("f", "e")
    s = re.sub(r'<span class="%s">.*?</span>' % o, "", s, flags=S)
    return re.sub(r'<span class="%s">(.*?)</span>' % w, r"\1", s, flags=S)
def links(s, l): return re.sub(r'href="#(\w+)"', lambda m: 'href="%s"' % url(l, m.group(1)), s)
def txt(s): return re.sub(r"<[^>]+>", "", s)
def esc(s): return html.escape(s, quote=True)

def page(l, pid, pair, title, desc, body, ld=(), robots=None):
    o = "en" if l == "fr" else "fr"; cur = pair[l]; alt = pair[o]
    nav = "".join('<a href="%s"%s>%s</a>' % (url(l, i), ' aria-current="page"' if i == pid else "", P[i][l][1]) for i in ORDER)
    heads = "".join('<link rel="alternate" hreflang="%s" href="%s%s">' % (k, BASE, pair[k]) for k in ("fr", "en"))
    heads += '<link rel="alternate" hreflang="x-default" href="%s%s">' % (BASE, pair["fr"])
    ldj = "".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
    rb = '<meta name="robots" content="%s">' % robots if robots else ""
    return f'''<!DOCTYPE html>
<html lang="{l}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{rb}
<link rel="canonical" href="{BASE}{cur}">{heads}
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{BASE}{cur}"><meta property="og:locale" content="{T[l]["loc"]}">
{ldj}<style>{css}</style></head><body>
<header><div class="bar"><a class="logo" href="/{l}/">{NAME}</a>
<a id="lang" class="btn alt" href="{alt}" hreflang="{T[l]["swl"]}" lang="{T[l]["swl"]}">{T[l]["sw"]}</a>
<nav aria-label="Menu">{nav}</nav></div></header>
<main>{body}</main><footer>{lang(foot, l)}</footer></body></html>'''

out = {}; pairs = []
for l in ("fr", "en"):
    ths = []
    for m in re.finditer(r'<div class="card"><h3>(.*?)</h3>\s*(<p>.*?</p>)\s*(<p>.*?</p>)</div>', lang(secs["themes"], l), S):
        ths.append(m.groups())
    for pid in ORDER:
        sec = lang(secs[pid], l); ld = []
        if pid == "home":
            it = iter(range(4))
            sec = re.sub(r'<div class="card"><h3>(.*?)</h3>', lambda m: '<div class="card"><h3><a href="%s">%s</a></h3>' % (url(l, "themes", next(it)), m.group(1)), sec)
            ld = [{"@context": "https://schema.org", "@type": "ProfessionalService", "name": NAME + ", psychothérapeute TCC", "url": BASE + "/" + l + "/", "areaServed": ["Europe", "Africa"], "address": {"@type": "PostalAddress", "addressLocality": "Lyon", "addressCountry": "FR"}, "availableLanguage": ["fr", "en"]}]
        else:
            sec = sec.replace("<h2>", "<h1>", 1).replace("</h2>", "</h1>", 1)
        if pid == "themes":
            sec = sec[:sec.index('<div class="card">')]
            for k, (h, p1, p2) in enumerate(ths):
                sec += '<div class="card"><h3><a href="%s">%s</a></h3>%s<p><a href="%s">%s</a></p></div>' % (url(l, "themes", k), h, p1, url(l, "themes", k), T[l]["more"])
        if pid == "faq":
            qa = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", sec, S)
            ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": txt(q), "acceptedAnswer": {"@type": "Answer", "text": txt(a)}} for q, a in qa]}]
        sec = links(sec, l)
        pair = {k: url(k, pid) for k in ("fr", "en")}; pairs.append(pair) if l == "fr" else None
        _, _, title, desc = P[pid][l]
        out[url(l, pid) + "index.html"] = page(l, pid, pair, title, desc, '<section class="on">%s</section>' % sec, ld)
    for k, (h, p1, p2) in enumerate(ths):
        pair = {c: url(c, "themes", k) for c in ("fr", "en")}; pairs.append(pair) if l == "fr" else None
        others = " · ".join('<a href="%s">%s</a>' % (url(l, "themes", j), ths[j][0]) for j in range(4) if j != k)
        body = '<section class="on"><p><a href="%s">← %s</a></p><h1>%s</h1>%s%s<p><a class="btn" href="%s">%s</a></p><p class="mu">%s : %s</p></section>' % (url(l, "themes"), T[l]["all"], h, p1, p2, url(l, "booking"), T[l]["book"], T[l]["other"], others)
        suffix = " : accompagnement TCC | " if l == "fr" else ": CBT support | "
        out[pair[l] + "index.html"] = page(l, "themes", pair, txt(h) + suffix + NAME, textwrap.shorten(txt(p1), 155, placeholder="…"), body)

today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for pr in pairs:
    for l in ("fr", "en"):
        sm.append("<url><loc>%s%s</loc><lastmod>%s</lastmod>%s<xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"%s%s\"/></url>" % (BASE, pr[l], today, "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (k, BASE, pr[k]) for k in ("fr", "en")), BASE, pr["fr"]))
out["sitemap.xml"] = "\n".join(sm) + "\n</urlset>\n"
out["robots.txt"] = "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE
out["index.html"] = '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>%s</title><link rel="canonical" href="%s/fr/"><meta http-equiv="refresh" content="0;url=/fr/"><link rel="alternate" hreflang="fr" href="%s/fr/"><link rel="alternate" hreflang="en" href="%s/en/"><link rel="alternate" hreflang="x-default" href="%s/fr/"></head><body><a href="/fr/">Français</a> · <a href="/en/">English</a></body></html>' % (NAME, BASE, BASE, BASE, BASE)
out["404.html"] = page("fr", "home", {"fr": "/fr/", "en": "/en/"}, "Page introuvable", "Page introuvable.", '<section class="on"><h1>Page introuvable</h1><p><a class="btn" href="/fr/">Retour à l’accueil</a> <a class="btn alt" href="/en/">Home (English)</a></p></section>', robots="noindex")
shutil.rmtree("dist", ignore_errors=True)
for p, c in out.items():
    f = os.path.join("dist", p.lstrip("/")); os.makedirs(os.path.dirname(f), exist_ok=True); open(f, "w", encoding="utf-8").write(c)
print(len(out), "fichiers générés dans dist/")
