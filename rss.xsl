<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title><xsl:value-of select="rss/channel/title"/> · RSS</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="crossorigin"/>
<link rel="stylesheet"><xsl:attribute name="href">https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&amp;family=Hanken+Grotesk:wght@400;500;600;700&amp;family=Zen+Kaku+Gothic+New:wght@400;500;700&amp;family=Shippori+Mincho:wght@500;600&amp;family=Spline+Sans+Mono:wght@400;500&amp;display=swap</xsl:attribute></link>
<style>
:root{--bg:#13150F;--ink:#E6E1D4;--soft:#98948A;--gold:#C99A3A;--line:#2A2C25}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:'Hanken Grotesk',sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:760px;margin:0 auto;padding:clamp(40px,8vh,90px) clamp(18px,5vw,40px) clamp(60px,10vh,120px)}
.kicker{font-family:'Spline Sans Mono',monospace;font-size:.62rem;letter-spacing:.24em;text-transform:uppercase;color:var(--soft);margin:0 0 12px}
h1{font-family:'Shippori Mincho',serif;font-weight:600;font-size:clamp(1.7rem,4vw,2.3rem);letter-spacing:.06em;margin:0 0 10px}
h1 a{border-bottom:1px solid transparent;transition:.2s}
h1 a:hover{border-bottom-color:var(--gold)}
.desc{font-family:'Shippori Mincho',serif;color:var(--soft);margin:0 0 20px;line-height:1.9}
.hint{font-family:'Spline Sans Mono',monospace;font-size:.72rem;letter-spacing:.05em;color:var(--soft);background:rgba(201,154,58,.06);border:1px solid var(--line);border-radius:8px;padding:14px 16px;line-height:1.9;margin:0 0 42px}
.items{list-style:none;padding:0;margin:0}
.items li{padding:22px 0;border-top:1px solid var(--line)}
.ti{font-family:'Shippori Mincho',serif;font-size:1.18rem;color:var(--ink);border-bottom:1px solid transparent;transition:.2s}
.ti:hover{border-bottom-color:var(--gold);color:var(--gold)}
.dt{font-family:'Spline Sans Mono',monospace;font-size:.66rem;letter-spacing:.1em;color:var(--soft);margin:8px 0 0}
.d{font-family:'Shippori Mincho',serif;color:var(--soft);line-height:1.9;margin:10px 0 0}
.back{margin-top:46px}
.back a{font-family:'Spline Sans Mono',monospace;font-size:.72rem;letter-spacing:.1em;color:var(--soft);border-bottom:1px solid transparent}
.back a:hover{color:var(--gold);border-bottom-color:var(--gold)}
</style>
</head>
<body>
<div class="wrap">
<p class="kicker">RSS Feed</p>
<h1><a><xsl:attribute name="href"><xsl:value-of select="rss/channel/link"/></xsl:attribute><xsl:value-of select="rss/channel/title"/></a></h1>
<p class="desc"><xsl:value-of select="rss/channel/description"/></p>
<p class="hint">このページはRSSフィードです。お使いのRSSリーダーにこのURLを登録すると、新しい旅の公開が自動で届きます。</p>
<ul class="items">
<xsl:for-each select="rss/channel/item">
<li>
<a class="ti"><xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute><xsl:value-of select="title"/></a>
<div class="dt"><xsl:value-of select="substring(pubDate,1,16)"/></div>
<p class="d"><xsl:value-of select="description"/></p>
</li>
</xsl:for-each>
</ul>
<p class="back"><a><xsl:attribute name="href"><xsl:value-of select="rss/channel/link"/></xsl:attribute>&#8592; JOURNEY LENS へ</a></p>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
