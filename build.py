#!/usr/bin/env python3
"""
Build the English and Chinese versions of wdanyi.com from _src/.

Source of truth is _src/*.html, where every translatable element carries
data-en / data-cn. This script emits two real, statically-rendered sites:

    en/<page>.html   lang="en"     — element text taken from the source as-is
    zh/<page>.html   lang="zh-Hans" — element text taken from data-cn

plus redirect stubs at the old root URLs, sitemap.xml and robots.txt.

Why not keep swapping text in JavaScript, as the site used to?
  - Search engines never saw the Chinese text (attribute values are not
    indexed as content), so half the site was invisible.
  - There was no way to send someone a Chinese-language link.
  - <title> and meta description could not vary by language.
  - The page rendered English and then flipped, and localStorage pinned
    returning visitors to whichever language they last used.
  - applyLang() assigned textContent, which silently deleted the <em>
    markup inside seven journal/book titles the moment you switched.

Usage:  python build.py
"""

import os
import re
import shutil
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src")
SITE = "https://www.wdanyi.com"
GA_ID = "G-XD2RVWDXLJ"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

# Assets live at the site root; generated pages sit one directory down.
ASSET_RE = re.compile(
    r'((?:href|src|data-src)=")('
    r'style\.css|main\.js|favicon\.svg|favicon-32\.png|apple-touch-icon\.png|img/'
    r')'
)

PAGES = {
    "index": dict(
        og_type="website",
        en_title="Ewen Wang — Artist",
        zh_title="王志（王丹一）— 艺术家",
        en_desc="Ewen Wang (王志 / 王丹一) — artist working across ink, oil, "
                "printmaking and mineral pigment. Selected works, biography and CV.",
        zh_desc="王志（号王丹一），1957年生。创作跨越水墨、油画、版画与岩彩。作品、简介与艺术简历。",
    ),
    "works": dict(
        og_type="website",
        en_title="Works — Ewen Wang",
        zh_title="作品 — 王志",
        en_desc="Works by Ewen Wang — ink landscapes, oil painting, printmaking, "
                "mineral pigment, sketch and calligraphy.",
        zh_desc="王志作品 — 水墨山水、油画、版画、岩彩、速写与书法。",
    ),
    "about": dict(
        og_type="profile",
        en_title="About — Ewen Wang",
        zh_title="简介 — 王志",
        en_desc="Biography, exhibitions, press and academic papers of Ewen Wang (王志).",
        zh_desc="王志的人物简介、参展经历、媒体报道与学术论文。",
    ),
    "cv": dict(
        og_type="profile",
        en_title="CV — Ewen Wang",
        zh_title="艺术简历 — 王志",
        en_desc="Curriculum vitae of Ewen Wang (王志) — education, exhibitions, "
                "collections and publications.",
        zh_desc="王志艺术简历 — 教育经历、参展、收藏与著述。",
    ),
    "statement": dict(
        og_type="article",
        en_title="Artist's Statement — Ewen Wang",
        zh_title="艺术自述 — 王志",
        en_desc="Ewen Wang (王志) in his own words.",
        zh_desc="王志的艺术自述。",
    ),
    "contact": dict(
        og_type="website",
        en_title="Contact — Ewen Wang",
        zh_title="联系 — 王志",
        en_desc="Enquiries about available works, exhibitions, press and licensing.",
        zh_desc="作品询价、展览合作、媒体采访与版权授权。",
    ),
}

JSONLD = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Ewen Wang",
    "alternateName": ["王志", "王丹一", "Danyi Wang"],
    "birthDate": "1957",
    "url": "https://www.wdanyi.com/en/",
    "image": "https://www.wdanyi.com/img/og-card.jpg",
    "jobTitle": "Artist",
    "knowsAbout": ["Ink wash painting", "Oil painting", "Printmaking",
                   "Mineral pigment painting", "Chinese calligraphy"]
  }
  </script>
"""


def head_for(slug, lang):
    """Regenerate the whole <head> so both languages stay in step."""
    meta = PAGES[slug]
    is_en = lang == "en"
    title = meta["en_title"] if is_en else meta["zh_title"]
    desc = meta["en_desc"] if is_en else meta["zh_desc"]
    page = f"{slug}.html"
    url = f"{SITE}/{lang}/{page}"
    en_url = f"{SITE}/en/{page}"
    zh_url = f"{SITE}/zh/{page}"
    locale = "en_US" if is_en else "zh_CN"
    alt_locale = "zh_CN" if is_en else "en_US"

    parts = [
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f'  <meta name="description" content="{desc}">',
        f'  <title>{title}</title>',
        f'  <link rel="canonical" href="{url}">',
        '',
        '  <!-- Both languages are real pages; tell search engines how they pair up. -->',
        f'  <link rel="alternate" hreflang="en" href="{en_url}">',
        f'  <link rel="alternate" hreflang="zh-Hans" href="{zh_url}">',
        f'  <link rel="alternate" hreflang="x-default" href="{en_url}">',
        '',
        f'  <meta property="og:type" content="{meta["og_type"]}">',
        '  <meta property="og:site_name" content="Ewen Wang">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:title" content="{title}">',
        f'  <meta property="og:description" content="{desc}">',
        f'  <meta property="og:image" content="{SITE}/img/og-card.jpg">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        f'  <meta property="og:locale" content="{locale}">',
        f'  <meta property="og:locale:alternate" content="{alt_locale}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{title}">',
        f'  <meta name="twitter:description" content="{desc}">',
        f'  <meta name="twitter:image" content="{SITE}/img/og-card.jpg">',
        '',
        '  <link rel="icon" href="../favicon.svg" type="image/svg+xml">',
        '  <link rel="alternate icon" href="../favicon-32.png" sizes="32x32">',
        '  <link rel="apple-touch-icon" href="../apple-touch-icon.png">',
        '  <link rel="stylesheet" href="../style.css">',
        '',
        f'  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>',
        '  <script>',
        '    window.dataLayer = window.dataLayer || [];',
        '    function gtag(){dataLayer.push(arguments);}',
        "    gtag('js', new Date());",
        f"    gtag('config', '{GA_ID}');",
        '  </script>',
    ]
    if slug == "index" and is_en:
        parts.append(JSONLD.rstrip("\n"))
    return "\n".join(parts)


class Localiser(HTMLParser):
    """Emit one language of the source.

    English keeps each element's existing inner HTML — the source renders
    English by default, so inline <em> markup survives. Chinese replaces
    inner content with the data-cn value. Elements with no data-cn (years,
    proper names, the email address) are left alone in both.
    """

    def __init__(self, lang, slug):
        super().__init__(convert_charrefs=False)
        self.lang = lang
        self.slug = slug
        self.out = []
        self.skip_depth = 0      # >0 while inside an element we are replacing
        self.skip_tag = None
        self.skip_close = True   # False when the element itself was replaced

    def emit(self, s):
        if self.skip_depth == 0:
            self.out.append(s)

    def handle_decl(self, decl):
        self.emit(f"<!{decl}>")

    def handle_comment(self, data):
        self.emit(f"<!--{data}-->")

    def handle_entityref(self, name):
        self.emit(f"&{name};")

    def handle_charref(self, name):
        self.emit(f"&#{name};")

    def handle_data(self, data):
        self.emit(data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_starttag(self, tag, attrs, self_closing=False):
        raw = self.get_starttag_text()
        d = dict(attrs)

        # Track nesting so a replaced element's children are dropped wholesale.
        if self.skip_depth > 0:
            if tag == self.skip_tag and not self_closing and tag not in VOID:
                self.skip_depth += 1
            return

        # The language switch becomes a real link between the two trees.
        if tag == "button" and "lang-toggle" in (d.get("class") or ""):
            page = f"{self.slug}.html"
            if self.lang == "en":
                link = (f'<a class="lang-toggle" href="../zh/{page}" '
                        f'lang="zh-Hans" hreflang="zh-Hans">中文</a>')
            else:
                link = (f'<a class="lang-toggle" href="../en/{page}" '
                        f'lang="en" hreflang="en">EN</a>')
            self.out.append(link)
            self.skip_tag, self.skip_depth, self.skip_close = tag, 1, False
            return

        # Strip the data-en / data-cn scaffolding from the output.
        clean = re.sub(r'\s+data-(?:en|cn)="[^"]*"', "", raw)
        clean = ASSET_RE.sub(r"\1../\2", clean)
        self.out.append(clean)

        if self.lang == "zh" and "data-cn" in d and tag not in VOID and not self_closing:
            self.out.append(d["data-cn"])
            self.skip_tag, self.skip_depth, self.skip_close = tag, 1, True

    def handle_endtag(self, tag):
        if self.skip_depth > 0:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    if self.skip_close:
                        self.out.append(f"</{tag}>")
                    self.skip_tag, self.skip_close = None, True
            return
        self.out.append(f"</{tag}>")

    def result(self):
        return "".join(self.out)


# The Chinese statement has no English counterpart yet. Rather than serve a
# wall of Chinese under lang="en", say so and mark the language properly.
EN_STATEMENT_NOTE = """
        <p class="prose-en-note" lang="en">
          The text below is the artist's own account of his development,
          written in Chinese. An English artist's statement is in preparation.
          <a href="../zh/statement.html">Read it in Chinese →</a>
        </p>
"""


def localise(slug, lang):
    src = open(os.path.join(SRC, f"{slug}.html"), encoding="utf-8").read()

    p = Localiser(lang, slug)
    p.feed(src)
    out = p.result()

    # Document language.
    out = re.sub(r'<html[^>]*>',
                 f'<html lang="{"en" if lang == "en" else "zh-Hans"}">',
                 out, count=1)

    # Swap in the regenerated head.
    out = re.sub(r"<head>.*?</head>",
                 "<head>\n" + head_for(slug, lang) + "\n</head>",
                 out, count=1, flags=re.S)

    # main.js sits at the site root.
    out = out.replace('<script src="main.js">', '<script src="../main.js">')

    if slug == "statement" and lang == "en":
        out = out.replace('<div class="prose">',
                          '<div class="prose" lang="zh-Hans">' + EN_STATEMENT_NOTE,
                          1)

    return out


REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="canonical" href="{target}">
  <meta name="robots" content="noindex, follow">
  <meta http-equiv="refresh" content="0; url={target_rel}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <script>
    // Send Chinese-language browsers to the Chinese tree; everyone else to English.
    // The visitor can still switch by hand once they land.
    (function () {{
      var l = (navigator.language || '').toLowerCase();
      var zh = l.indexOf('zh') === 0 && l.indexOf('zh-hant') !== 0 &&
               l.indexOf('zh-tw') !== 0 && l.indexOf('zh-hk') !== 0;
      location.replace((zh ? 'zh/' : 'en/') + '{page}');
    }})();
  </script>
</head>
<body>
  <p style="font-family:system-ui,sans-serif;padding:2rem">
    <a href="{target_rel}">Continue to {title}</a> ·
    <a href="zh/{page}">中文</a>
  </p>
</body>
</html>
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    for lang in ("en", "zh"):
        d = os.path.join(ROOT, lang)
        if os.path.isdir(d):
            shutil.rmtree(d)

    for slug in PAGES:
        for lang in ("en", "zh"):
            write(os.path.join(ROOT, lang, f"{slug}.html"), localise(slug, lang))
        # Old root URLs are indexed; keep them alive as redirects.
        write(os.path.join(ROOT, f"{slug}.html"),
              REDIRECT.format(title=PAGES[slug]["en_title"],
                              target=f"{SITE}/en/{slug}.html",
                              target_rel=f"en/{slug}.html",
                              page=f"{slug}.html"))
        print(f"  {slug:10s} -> en/ zh/ + root redirect")

    # /en/ and /zh/ resolve to their index.html automatically.

    urls = []
    for slug in PAGES:
        for lang in ("en", "zh"):
            urls.append(
                f"  <url>\n"
                f"    <loc>{SITE}/{lang}/{slug}.html</loc>\n"
                f"    <xhtml:link rel=\"alternate\" hreflang=\"en\" href=\"{SITE}/en/{slug}.html\"/>\n"
                f"    <xhtml:link rel=\"alternate\" hreflang=\"zh-Hans\" href=\"{SITE}/zh/{slug}.html\"/>\n"
                f"    <lastmod>2026-07-26</lastmod>\n"
                f"  </url>"
            )
    write(os.path.join(ROOT, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
          '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")

    write(os.path.join(ROOT, "robots.txt"),
          "User-agent: *\n"
          "Allow: /\n\n"
          "# Retired press feature — kept for reference, not for indexing.\n"
          "Disallow: /press-chuangrong-2025.html\n\n"
          f"Sitemap: {SITE}/sitemap.xml\n")

    print("  sitemap.xml, robots.txt")
    print("done.")


if __name__ == "__main__":
    main()
