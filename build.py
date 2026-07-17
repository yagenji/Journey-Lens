#!/usr/bin/env python3
# JOURNEY LENS — static story page generator (/id/index.html)
import json, re, os, shutil, html

import glob
SRC_HTML = "index.html"     # repo root homepage (template source)
OUT      = "."              # repo root (in-place)
DOMAIN   = "https://journey.yagenji.com"

PWA_HEAD = (
'<link rel="apple-touch-icon" href="/icons/icon-180.png">\n'
'<meta name="theme-color" content="#13150F">\n'
'<meta name="apple-mobile-web-app-capable" content="yes">\n'
'<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
'<meta name="apple-mobile-web-app-title" content="JOURNEY LENS">\n'
'<link rel="manifest" href="/manifest.json">\n'
'<link rel="alternate" type="application/rss+xml" title="JOURNEY LENS" href="/rss.xml">'
)
SW_REG = "<script>if('serviceWorker'in navigator){addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}</script>"

src = open(SRC_HTML, encoding="utf-8").read()

# --- combine per-story files (content/stories/*.json) via content/order.json ---
_od = json.load(open("content/order.json", encoding="utf-8"))
_raw = _od.get("countryOrder", [])
_newdays = _od.get("newDays", 30)
_order = [(x.get("name") if isinstance(x, dict) else x) for x in _raw]
_oidx = {k: i for i, k in enumerate(_order)}
def _tail_int(x):
    m = re.search(r"(\d+)$", x or ""); return int(m.group(1)) if m else 0
def _wkey(c):
    o = c.get("order"); eff = float(o) if o not in (None, "") else _tail_int(c.get("id")); return (eff, c.get("id") or "")
def _ckey(c):
    jp = c.get("jp"); return (_oidx.get(jp, len(_order) + 1), jp or "")
LOCS = [json.load(open(f, encoding="utf-8")) for f in glob.glob("content/stories/*.json")]
# 新しい国（order.json に未登録の jp）は末尾へ自動追加して保存する
_missing = sorted({c.get("jp") for c in LOCS if c.get("jp")} - set(_order))
if _missing:
    _order = _order + _missing
    _oidx = {k: i for i, k in enumerate(_order)}
    json.dump({"countryOrder": _order, "newDays": _newdays}, open("content/order.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
LOCS.sort(key=lambda c: (_ckey(c), _wkey(c)))
json.dump({"locations": LOCS, "newDays": _newdays}, open("content.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------- extract reusable chunks from the source homepage ----------
def between(s, a, b, inc=True):
    i = s.index(a); j = s.index(b, i) + len(b)
    return s[i:j] if inc else s[i+len(a):j-len(b)]

CSS = between(src, "<style>", "</style>", inc=False)
FAVICON = re.search(r'<link rel="icon"[^>]*>', src).group(0)
PRECONNECT = "".join(re.findall(r'<link rel="preconnect"[^>]*>', src))
FONTS = re.search(r'<link href="https://fonts\.googleapis\.com/css2[^>]*>', src).group(0)
NAV = between(src, '<header class="nav"', "</header>")
COLOPHON = between(src, '<footer class="colophon">', "</footer>")
LIGHTBOX = between(src, '<div class="lightbox"', '<p class="lb-cap" id="lbCap"></p>')

# fix nav links to work from a /id/ subpage back to the homepage sections
NAV = ('<header class="nav"' + NAV.split('<header class="nav"',1)[1]) if '<header class="nav"' in NAV else NAV
NAV = NAV.replace('href="#"', 'href="/"') \
         .replace('href="#featured"', 'href="/#featured"') \
         .replace('href="#atlas"', 'href="/#atlas"') \
         .replace('href="#about"', 'href="/#about"')

# extra CSS for the "More from" section (not present in source homepage)
MORE_CSS = (
".cview-more{max-width:1240px;margin:0 auto;padding:clamp(44px,7vh,84px) clamp(18px,5vw,40px) 0;border-top:1px solid var(--line)}\n"
".cview-more-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:22px}\n"
".cview-more .more-en{font-family:var(--latin);font-weight:600;font-size:clamp(1.25rem,3vw,1.7rem);letter-spacing:.01em;color:var(--ink);margin:0}\n"
".cview-more .more-ja{font-family:var(--sans);font-size:.78rem;letter-spacing:.2em;color:var(--ink-soft)}\n"
)

# ---------- helpers mirroring the site JS ----------
def esc(s):
    s = "" if s is None else str(s)
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def vsrc(m): return m.get("videoUrl") or m.get("video") or ""
def ytId(u):
    mm = re.search(r'(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([\w-]{11})', u or "")
    return mm.group(1) if mm else ""
def videoThumb(m):
    if m and m.get("image"): return m["image"]
    i = ytId(vsrc(m or {}))
    return "https://img.youtube.com/vi/%s/hqdefault.jpg" % i if i else ""
def firstPhoto(c):
    for m in (c.get("media") or []):
        if m.get("type")=="photo": return m
    return {}
def entryThumb(c):
    if c.get("heroImage"): return c["heroImage"]
    fp = firstPhoto(c).get("image")
    if fp: return fp
    v = next((m for m in (c.get("media") or []) if m.get("type")=="video"), {})
    return videoThumb(v) or ""
def nameHTML(c):
    out = esc(c.get("jp") or c.get("en"))
    if c.get("placeJa"): out += '<span class="nm-place">'+esc(c["placeJa"])+'</span>'
    return out

SIZE = {"sm":"f-2","md":"f-3","lg":"f-4","full":"f-6"}
SHAPE= {"land":"r-land","port":"r-port","sq":"r-sq","wide":"r-wide"}

def media_figure(m):
    cls = "plate %s %s" % (SIZE.get(m.get("size"),"f-3"), SHAPE.get(m.get("shape"),"r-land"))
    attrs = ' class="%s" tabindex="0" data-cap="%s"' % (cls, esc(m.get("cap") or ""))
    inner = ""
    if m.get("type")=="video":
        src_u = vsrc(m); thumb = videoThumb(m)
        attrs += ' data-video="%s" data-poster="%s"' % (esc(src_u), esc(thumb))
        # all sources here resolve to embeds (YouTube/Vimeo) -> poster + play button
        inner += '<img class="ph" loading="lazy" decoding="async" src="%s" alt="%s">' % (esc(thumb), esc(m.get("cap") or ""))
        inner += '<div class="play"><span></span></div>'
        inner += '<span class="tag">time-lapse</span>'
        if m.get("duration"): inner += '<span class="dur">%s</span>' % esc(m["duration"])
    else:
        inner += '<img class="ph" loading="lazy" decoding="async" src="%s" alt="%s">' % (esc(m.get("image") or ""), esc(m.get("cap") or ""))
    if m.get("cap"): inner += '<figcaption>%s</figcaption>' % esc(m["cap"])
    return "<figure%s>%s</figure>" % (attrs, inner)

def essay_html(c):
    paras = [p for p in re.split(r'\n\n+', c.get("essay") or "") if p!=""]
    parts = []
    if paras: parts.append('<p>'+esc(paras[0])+'</p>')
    if c.get("pullquote"): parts.append('<blockquote class="pullquote">'+esc(c["pullquote"])+'</blockquote>')
    for p in paras[1:]: parts.append('<p>'+esc(p)+'</p>')
    return "".join(parts)

def more_from(c):
    kin = [x for x in LOCS if x.get("continent")==c.get("continent")
           and (x.get("jp") or "")==(c.get("jp") or "") and x["id"]!=c["id"]][:6]
    if not kin: return ""
    cards = ""
    for s in kin:
        place = s.get("placeJa") or s.get("jp") or ""
        cards += ('<a class="jl-card" href="/%s/"><img loading="lazy" decoding="async" src="%s" alt="%s">'
                  '<div class="cap"><p class="jl-place">%s</p><div class="jl-year">%s</div></div></a>'
                  % (esc(s["id"]), esc(entryThumb(s)), esc(place), esc(place), esc(s.get("year") or "")))
    return ('<section class="cview-more"><div class="cview-more-head">'
            '<h2 class="more-en">More from %s</h2>'
            '<span class="more-ja">%sの他の旅</span></div>'
            '<div class="jl-grid">%s</div></section>'
            % (esc(c.get("en")), esc(c.get("jp") or c.get("en")), cards))

def meta_desc(c):
    d = (c.get("standfirst") or "").strip()
    if not d:
        first = re.split(r'\n\n+', c.get("essay") or "")[0].strip()
        d = (first[:110] + "…") if len(first) > 110 else first
    if not d:
        d = "旅をしながら撮りためた、世界の風景・街・人の写真とタイムラプス。"
    return d.replace("\n"," ").strip()

def page(c, prv, nxt):
    hero = entryThumb(c)
    hero_abs = DOMAIN + hero if hero.startswith("/") else hero
    canonical = "%s/%s/" % (DOMAIN, c["id"])
    place = c.get("placeJa") or c.get("jp") or ""
    title_plain = (("%s｜%s" % (c["placeJa"], c.get("jp"))) if c.get("placeJa") else (c.get("jp") or c.get("en")))
    title = title_plain + " — JOURNEY LENS"
    desc = meta_desc(c)
    figures = "".join(media_figure(m) for m in (c.get("media") or []))
    note = ""
    if c.get("noteUrl"):
        note = ('<div class="cview-note"><a href="%s" target="_blank" rel="noopener">'
                '<svg class="note-mark" viewBox="111 111 270 270" fill="currentColor" aria-hidden="true">'
                '<path d="M139.57,142.06c41.19,0,97.6-2.09,138.1-1.04,54.34,1.39,74.76,25.06,75.45,83.53.69,33.06,0,127.73,0,127.73h-58.79c0-82.83.35-96.5,0-122.6-.69-22.97-7.25-33.92-24.9-36.01-18.69-2.09-71.07-.35-71.07-.35v158.96h-58.79v-210.22Z"/>'
                '</svg><span>noteで読む</span><span class="note-arrow">→</span></a></div>' % esc(c["noteUrl"]))
    prev_a = ('<a href="/%s/">← %s</a>' % (esc(prv["id"]), esc(prv.get("jp") or prv.get("en")))) if prv else ""
    next_a = ('<a href="/%s/">%s →</a>' % (esc(nxt["id"]), esc(nxt.get("jp") or nxt.get("en")))) if nxt else ""
    foot_nav = '<nav class="cview-foot">%s<a href="/#atlas">地図へ戻る</a>%s</nav>' % (prev_a, next_a)
    ld = {"@context":"https://schema.org","@graph":[
        {"@type":"Article",
         "headline": title_plain, "description": desc, "image": hero_abs,
         "url": canonical, "inLanguage":"ja",
         "datePublished": c.get("publishedAt",""),
         "author":{"@type":"Person","name":"八源寺 誠"},
         "publisher":{"@type":"Organization","name":"JOURNEY LENS"},
         "isPartOf":{"@type":"WebSite","name":"JOURNEY LENS","url":DOMAIN+"/"}},
        {"@type":"ImageObject",
         "contentUrl": hero_abs,
         "creator":{"@type":"Person","name":"八源寺 誠"},
         "creditText":"JOURNEY LENS / Makoto Yagenji",
         "copyrightNotice":"© JOURNEY LENS",
         "license": DOMAIN+"/#about"}
    ]}
    ld_json = json.dumps(ld, ensure_ascii=False)

    head = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="preload" as="image" href="{esc(hero)}" fetchpriority="high">
<meta property="og:type" content="article">
<meta property="og:site_name" content="JOURNEY LENS">
<meta property="og:title" content="{esc(title_plain)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(hero_abs)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title_plain)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(hero_abs)}">
{FAVICON}
{PWA_HEAD}
{PRECONNECT}
{FONTS}
<link rel="stylesheet" href="/assets/story.css">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
{NAV}
<main id="country-view">
<article class="cview">
<header class="cview-hero" style="background-image:url({esc(hero)})">
<a class="cview-back" href="/#atlas">← 地図へ戻る</a>
<div class="cview-hero-inner"><div class="cview-folio">{esc(c.get("en"))}{(" · "+esc(c["year"])) if c.get("year") else ""}</div>
<h1 class="cview-title">{nameHTML(c)}</h1>
{('<p class="cview-standfirst">'+esc(c["standfirst"])+'</p>') if c.get("standfirst") else ""}</div></header>
<div class="cview-essay">{essay_html(c)}</div>{note}
<div class="cview-gallery"><div class="plates">{figures}</div></div>
{more_from(c)}
{foot_nav}
</article>
</main>
{COLOPHON}
{LIGHTBOX}</div>
<script src="/assets/story.js" defer></script>
{SW_REG}
</body>
</html>
'''
    return head

# ---------- write assets ----------
os.makedirs(OUT+"/assets", exist_ok=True)
open(OUT+"/assets/story.css","w",encoding="utf-8").write(CSS if ".cview-more{" in CSS else CSS + "\n" + MORE_CSS)

STORY_JS = r'''(function(){
  function el(t,c){var e=document.createElement(t);if(c)e.className=c;return e;}
  function ytId(u){var m=(u||'').match(/(?:youtube\.com\/(?:watch\?v=|shorts\/|embed\/)|youtu\.be\/)([\w-]{11})/);return m?m[1]:'';}
  function parseVideo(u){if(!u)return null;var m;
    if(m=u.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/|embed\/)|youtu\.be\/)([\w-]{11})/))return{kind:'embed',embed:'https://www.youtube.com/embed/'+m[1]+'?autoplay=1&rel=0'};
    if(m=u.match(/vimeo\.com\/(?:video\/)?(\d+)/))return{kind:'embed',embed:'https://player.vimeo.com/video/'+m[1]+'?autoplay=1'};
    return{kind:'file',src:u};}
  var lb=document.getElementById('lightbox');
  var lbFigs=[],lbIdx=-1;
  function lbShow(fig){var slot=document.getElementById('lbSlot');slot.innerHTML='';
    if(fig.dataset.video){var info=parseVideo(fig.dataset.video);
      if(info&&info.kind==='embed'){var f=el('iframe');f.src=info.embed;f.allow='autoplay; fullscreen; encrypted-media';f.allowFullscreen=true;slot.appendChild(f);}
      else{var v=el('video');v.controls=true;v.loop=true;v.autoplay=true;v.playsInline=true;v.setAttribute('playsinline','');if(fig.dataset.poster)v.poster=fig.dataset.poster;var s=el('source');s.src=info?info.src:fig.dataset.video;v.appendChild(s);slot.appendChild(v);}
    }else{var im=fig.querySelector('img');var i=el('img');i.src=im.src;i.alt=im.alt;slot.appendChild(i);}
    var cap=document.getElementById('lbCap');if(cap)cap.textContent=fig.dataset.cap||'';}
  function openLb(fig){lbFigs=[].slice.call((fig.closest('.plates')||document).querySelectorAll('.plate'));lbIdx=lbFigs.indexOf(fig);lbShow(fig);if(lb)lb.classList.add('open');}
  function lbNav(d){if(lbFigs.length<2)return;lbIdx=(lbIdx+d+lbFigs.length)%lbFigs.length;lbShow(lbFigs[lbIdx]);}
  function closeLb(){if(lb){lb.classList.remove('open');}var s=document.getElementById('lbSlot');if(s)s.innerHTML='';}
  document.querySelectorAll('.plate').forEach(function(f){
    f.addEventListener('click',function(){openLb(f);});
    f.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openLb(f);}});
  });
  var lc=document.getElementById('lbClose');if(lc)lc.addEventListener('click',closeLb);
  if(lb)lb.addEventListener('click',function(e){if(e.target===lb)closeLb();});
  addEventListener('keydown',function(e){if(!lb||!lb.classList.contains('open'))return;if(e.key==='Escape')closeLb();else if(e.key==='ArrowLeft')lbNav(-1);else if(e.key==='ArrowRight')lbNav(1);});
  var lbTX=null;if(lb){lb.addEventListener('touchstart',function(e){lbTX=e.changedTouches[0].clientX;},{passive:true});lb.addEventListener('touchend',function(e){if(lbTX==null)return;var dx=e.changedTouches[0].clientX-lbTX;lbTX=null;if(Math.abs(dx)>40)lbNav(dx<0?1:-1);},{passive:true});}
  function fade(img){if(img.dataset.ph)return;img.dataset.ph='1';
    if(img.complete&&img.naturalWidth)img.classList.add('on');
    else{img.addEventListener('load',function(){img.classList.add('on');},{once:true});
         img.addEventListener('error',function(){img.classList.add('on');},{once:true});}}
  document.querySelectorAll('img.ph').forEach(fade);
  setTimeout(function(){document.querySelectorAll('img.ph:not(.on)').forEach(function(i){i.classList.add('on');});},2500);
  var nav=document.getElementById('nav');
  if(nav){var onScroll=function(){nav.classList.toggle('solid',scrollY>innerHeight*0.6);};
    addEventListener('scroll',onScroll,{passive:true});onScroll();}
  var tgl=document.getElementById('navToggle'),links=document.getElementById('navLinks');
  if(tgl&&links)tgl.addEventListener('click',function(){var o=links.classList.toggle('open');
    tgl.setAttribute('aria-expanded',o);tgl.textContent=o?'閉じる ×':'メニュー ＋';});
})();'''
open(OUT+"/assets/story.js","w",encoding="utf-8").write(STORY_JS)

# ---------- write story pages ----------
# country-level nav: LOCS is already sorted by countryOrder, so walk distinct
# countries in sequence, land on each country's first story, no wrap at the ends.
_cseq, _cfirst = [], {}
for _c in LOCS:
    _j = _c.get("jp") or ""
    if _j not in _cfirst:
        _cfirst[_j] = _c; _cseq.append(_j)
_cpos = {j: i for i, j in enumerate(_cseq)}
for c in LOCS:
    _pi = _cpos.get(c.get("jp") or "", -1)
    prv = _cfirst[_cseq[_pi-1]] if _pi > 0 else None
    nxt = _cfirst[_cseq[_pi+1]] if (0 <= _pi < len(_cseq)-1) else None
    d = OUT + "/" + c["id"]
    os.makedirs(d, exist_ok=True)
    open(d+"/index.html","w",encoding="utf-8").write(page(c, prv, nxt))

# ---------- sitemap.xml (homepage + all story pages) ----------
urls = ['<url><loc>%s/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>' % DOMAIN]
for c in LOCS:
    lm = c.get("publishedAt","")
    lmt = ("<lastmod>%s</lastmod>" % lm) if lm else ""
    urls.append('<url><loc>%s/%s/</loc>%s<changefreq>monthly</changefreq><priority>0.8</priority></url>' % (DOMAIN, c["id"], lmt))
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
open(OUT+"/sitemap.xml","w",encoding="utf-8").write(sitemap)

# ---------- (manifest / sw / offline / icons are committed static files; not touched) ----------
import datetime as _dt

# ---------- RSS feed (newest first) ----------
_MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
_DOW = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
def rfc822(s):
    try: d = _dt.date.fromisoformat(s)
    except Exception: return ""
    return "%s, %02d %s %04d 00:00:00 +0900" % (_DOW[d.weekday()], d.day, _MON[d.month-1], d.year)
def xesc(s):
    return ("" if s is None else str(s)).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

feed_items = [(i, c) for i, c in enumerate(LOCS) if c.get("publishedAt")]
# publishedAt desc, tie-break by array index desc (later added = newer), matches site "recently added"
feed_items.sort(key=lambda t: (t[1]["publishedAt"], t[0]), reverse=True)
rows = []
for i, c in feed_items:
    place = c.get("placeJa") or ""
    title = (c.get("jp") or c.get("en") or "") + (("｜" + place) if place else "")
    link = "%s/%s/" % (DOMAIN, c["id"])
    desc = (c.get("standfirst") or "").strip()
    rows.append(
        "<item>\n"
        "<title>%s</title>\n"
        "<link>%s</link>\n"
        "<guid isPermaLink=\"true\">%s</guid>\n"
        "<pubDate>%s</pubDate>\n"
        "<description>%s</description>\n"
        "</item>" % (xesc(title), link, link, rfc822(c["publishedAt"]), xesc(desc))
    )
now822 = _dt.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0900")
rss = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<?xml-stylesheet type="text/xsl" href="/rss.xsl"?>\n'
       '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
       '<channel>\n'
       '<title>JOURNEY LENS</title>\n'
       '<link>%s/</link>\n'
       '<atom:link href="%s/rss.xml" rel="self" type="application/rss+xml"/>\n'
       '<description>旅の風景・街・人の写真とタイムラプス。</description>\n'
       '<language>ja</language>\n'
       '<lastBuildDate>%s</lastBuildDate>\n'
       '%s\n'
       '</channel>\n</rss>\n' % (DOMAIN, DOMAIN, now822, "\n".join(rows)))
open(OUT + "/rss.xml", "w", encoding="utf-8").write(rss)

print("PWA + RSS written (", len(rows), "feed items )")
# ---------- remove stale story dirs (deleted stories only) ----------
_valid = set(c["id"] for c in LOCS)
_protected = {"assets","icons","content",".github","uploads","node_modules",".git","_generator"}
for _name in os.listdir(OUT):
    _p = os.path.join(OUT, _name)
    if (not os.path.isdir(_p)) or _name in _protected: continue
    _idx = os.path.join(_p, "index.html")
    if _name not in _valid and os.path.isfile(_idx):
        try:
            if '<article class="cview">' in open(_idx, encoding="utf-8").read():
                shutil.rmtree(_p)
        except Exception:
            pass

print("generated", len(LOCS), "story pages")
print("dirs:", ", ".join(sorted(os.listdir(OUT))[:6]), "...")


# ---------- T2: bake static story cards into index.html (#jlList) for SEO / no-JS ----------
def _jl_thumb(c):
    # 一覧カードのサムネはSPA(jlThumb)/ヒーロー(entryThumb)と統一：heroImage→先頭写真→動画サムネ
    return entryThumb(c)
def _jl_card(c):
    place=esc(c.get("placeJa") or c.get("jp") or "")
    return ('<a class="jl-card" href="/'+esc(c["id"])+'/"><img loading="lazy" decoding="async" src="'
            +esc(_jl_thumb(c))+'" alt="'+place+'"><div class="cap"><p class="jl-place">'+place
            +'</p><div class="jl-year">'+esc(c.get("year") or "")+'</div></div></a>')
_jl_cards="".join(_jl_card(c) for c in LOCS)
_idx=open("index.html",encoding="utf-8").read()
_idx=re.sub(r"<!--JLSTATIC-->.*?<!--/JLSTATIC-->",
            lambda m:"<!--JLSTATIC-->"+_jl_cards+"<!--/JLSTATIC-->", _idx, flags=re.S)
open("index.html","w",encoding="utf-8").write(_idx)
print("baked", len(LOCS), "static story cards into index.html")

# ---------- T3: Atlas/REGION の大陸順を content/settings.json から反映 ----------
_VALID_CONT = {"asia","europe","africa","namerica","samerica","oceania","antarctica"}
_DEFAULT_CONT = ["asia","europe","africa","namerica","samerica","oceania","antarctica"]
def _cont_val(x):
    # CMSの保存形式ゆれに対応: "antarctica" でも {"continent":"antarctica"} でも受ける
    if isinstance(x, str): return x
    if isinstance(x, dict): return x.get("continent") or next(iter(x.values()), None)
    return None
try:
    _st = json.load(open("content/settings.json", encoding="utf-8"))
    _co = [_cont_val(x) for x in (_st.get("continentOrder") or [])]
    _co = [x for x in _co if x in _VALID_CONT]
    _seen = set(); _co = [x for x in _co if not (x in _seen or _seen.add(x))]
    _co = _co + [x for x in _DEFAULT_CONT if x not in _co]
except Exception:
    _co = _DEFAULT_CONT
_arr = "[" + ",".join("'%s'" % x for x in _co) + "]"
_idx = open("index.html", encoding="utf-8").read()
_idx = re.sub(r"const JL_CONT_ORDER=\[[^\]]*\];", "const JL_CONT_ORDER=%s;" % _arr, _idx, count=1)
open("index.html", "w", encoding="utf-8").write(_idx)
print("applied continentOrder:", _co)

# ---------- T4: 「トップに出す国」を content/top_countries.json で維持し index.html へ反映 ----------
# 全ての国(jp)を order.json の並びで列挙。既存のON/OFFは保持し、新しい国は show=True で自動追加。
_existing_jp = {c.get("jp") for c in LOCS if c.get("jp")}
_all_countries = [jp for jp in _order if jp in _existing_jp]
try:
    _tc = json.load(open("content/top_countries.json", encoding="utf-8")).get("countries", [])
except Exception:
    _tc = []
_show_map = {}
for _it in _tc:
    if isinstance(_it, dict) and _it.get("jp"):
        _show_map[_it["jp"]] = bool(_it.get("show", True))
_tc_new = [{"jp": jp, "show": _show_map.get(jp, True)} for jp in _all_countries]
json.dump({"countries": _tc_new}, open("content/top_countries.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
_hidden = [x["jp"] for x in _tc_new if not x["show"]]
_harr = "[" + ",".join(json.dumps(x, ensure_ascii=False) for x in _hidden) + "]"
_idxh = open("index.html", encoding="utf-8").read()
_idxh = re.sub(r"((?:const|let)\s+JL_HIDDEN=)\[[^\]]*\];", lambda m: m.group(1)+_harr+";", _idxh, count=1)
open("index.html", "w", encoding="utf-8").write(_idxh)
print("applied hidden countries:", _hidden)

# ---------- visited-countries map: color assets/world-base.svg by content/visited.json ----------
try:
    _vis = json.load(open("content/visited.json", encoding="utf-8")).get("countries", [])
    _vset = set(str(c).lower() for c in _vis if c)
    _base = open("assets/world-base.svg", encoding="utf-8").read()
    _GOLD = "#D3A24A"
    def _vcol(m):
        code = m.group(1)
        return '<g class="%s country"%s>' % (code, (' fill="%s"' % _GOLD) if code in _vset else "")
    _vmap = re.sub(r'<g class="([a-z]{2}) country">', _vcol, _base)
    open("visited-map.svg", "w", encoding="utf-8").write(_vmap)
    print("visited map:", len(_vset), "countries")
except Exception as _e:
    print("visited map skipped:", _e)
