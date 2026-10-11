"""Checks for the all.about.python static site.

Runs under pytest alongside the rest of the suite:

    pytest                      # everything
    pytest tests/test_site.py   # just the site

The static checks (markup, ids, links, language) need nothing but Python and
always run. The browser checks (colour contrast, horizontal overflow, the
JavaScript behaviours) need Firefox and geckodriver, and are skipped
automatically when either is missing, so this file is safe in CI.

The site directory is found automatically as a sibling `web/` or `site/`
folder; override it with the SITE_DIR environment variable.
"""

import base64
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser

import pytest

PAGES = ["index", "history", "faq", "projects", "reference"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


def _find_site():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.environ.get("SITE_DIR"),
                 os.path.join(here, "..", "web"),
                 os.path.join(here, "..", "site"),
                 os.path.join(here, "..")):
        if cand and os.path.isfile(os.path.join(cand, "index.html")):
            return os.path.abspath(cand)
    return None


SITE = _find_site()

if SITE is None:
    pytest.skip("site directory not found; set SITE_DIR",
                allow_module_level=True)


# --------------------------------------------------------------- parsing ---

class _Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.refs = [], [], [], []
        self.imgs_without_alt = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        for key in ("href", "src"):
            if key in d:
                self.refs.append(d[key])
        if tag == "img" and "alt" not in d:
            self.imgs_without_alt += 1
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                still_open = [t for t, _ in self.stack[i + 1:]]
                self.errors.append(
                    f"</{tag}> at line {self.getpos()[0]} closed while "
                    f"{still_open} were still open")
                del self.stack[i:]
                return
        self.errors.append(f"</{tag}> at line {self.getpos()[0]} never opened")


def _parse(page):
    src = open(os.path.join(SITE, page + ".html"), encoding="utf-8").read()
    doc = _Doc()
    doc.feed(src)
    doc.close()
    return src, doc


_PARSED = {p: _parse(p) for p in PAGES}
_IDS = {p + ".html": set(_PARSED[p][1].ids) for p in PAGES}


# ---------------------------------------------------------------- static ---

@pytest.mark.parametrize("page", PAGES)
def test_markup_is_wellformed(page):
    _, doc = _PARSED[page]
    assert not doc.errors, f"{page}.html: " + "; ".join(doc.errors[:5])
    unclosed = [f"<{t}> opened line {n}" for t, n in doc.stack]
    assert not unclosed, f"{page}.html never closed: " + "; ".join(unclosed[:5])


@pytest.mark.parametrize("page", PAGES)
def test_ids_are_unique(page):
    _, doc = _PARSED[page]
    dupes = {i for i in doc.ids if doc.ids.count(i) > 1}
    assert not dupes, f"{page}.html has duplicate ids: {sorted(dupes)}"


@pytest.mark.parametrize("page", PAGES)
def test_required_head_elements(page):
    src, _ = _PARSED[page]
    for needle, label in [('<html lang="en"', "lang attribute"),
                          ('name="viewport"', "viewport meta"),
                          ('name="description"', "meta description"),
                          ('class="skip"', "skip link")]:
        assert needle in src, f"{page}.html is missing its {label}"


@pytest.mark.parametrize("page", PAGES)
def test_images_have_alt_text(page):
    _, doc = _PARSED[page]
    assert doc.imgs_without_alt == 0, \
        f"{page}.html has {doc.imgs_without_alt} <img> without alt"


@pytest.mark.parametrize("page", PAGES)
def test_links_and_assets_resolve(page):
    _, doc = _PARSED[page]
    broken = []
    for ref in doc.refs:
        if ref.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        if ref.startswith("#"):
            if ref[1:] not in _IDS[page + ".html"]:
                broken.append(f"anchor {ref}")
            continue
        path, _, frag = ref.partition("#")
        if not os.path.exists(os.path.join(SITE, path)):
            broken.append(f"missing file {ref}")
        elif frag and path.endswith(".html") and frag not in _IDS.get(path, set()):
            broken.append(f"cross-page anchor {ref}")
    assert not broken, f"{page}.html: " + "; ".join(broken)


@pytest.mark.parametrize("page", PAGES)
def test_text_is_english_only(page):
    """The site was rebuilt in English; no Cyrillic should survive."""
    src, _ = _PARSED[page]
    found = re.findall(r"[Ѐ-ӿ]+", src)
    assert not found, f"{page}.html contains Cyrillic: {found[:5]}"


# -------------------------------------------------------------- fixtures ---

def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def origin():
    """Serve the site on a throwaway port for the duration of the session."""
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            urllib.request.urlopen(url + "/index.html", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    else:
        proc.terminate()
        pytest.skip("could not start the local web server")
    yield url
    proc.terminate()


class _Browser:
    def __init__(self, base, sid):
        self.base, self.sid = base, sid

    def _rq(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=180).read().decode())

    def get(self, url, settle=1.4):
        self._rq("POST", f"/session/{self.sid}/url", {"url": url})
        time.sleep(settle)

    def size(self, w, h):
        self._rq("POST", f"/session/{self.sid}/window/rect",
                 {"width": w, "height": h, "x": 0, "y": 0})
        time.sleep(0.3)

    def js(self, script, *args):
        return self._rq("POST", f"/session/{self.sid}/execute/sync",
                        {"script": script, "args": list(args)})["value"]

    def screenshot(self, path):
        png = self._rq("GET", f"/session/{self.sid}/screenshot")["value"]
        open(path, "wb").write(base64.b64decode(png))


@pytest.fixture(scope="session")
def browser():
    if not shutil.which("geckodriver"):
        pytest.skip("geckodriver not installed")
    if not (shutil.which("firefox") or shutil.which("firefox-bin")):
        pytest.skip("firefox not installed")

    port = _free_port()
    proc = subprocess.Popen(["geckodriver", "--port", str(port)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            urllib.request.urlopen(base + "/status", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    else:
        proc.terminate()
        pytest.skip("geckodriver did not start")

    caps = {"capabilities": {"alwaysMatch": {
        "browserName": "firefox",
        "moz:firefoxOptions": {"args": ["-headless", "--width=1440",
                                        "--height=1400"]}}}}
    req = urllib.request.Request(base + "/session",
                                 data=json.dumps(caps).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    sid = json.loads(urllib.request.urlopen(req, timeout=180).read()
                     .decode())["value"]["sessionId"]
    drv = _Browser(base, sid)
    yield drv
    try:
        drv._rq("DELETE", f"/session/{sid}")
    finally:
        proc.terminate()


# ------------------------------------------------------------------ live ---

_CONTRAST_JS = r"""
// Firefox resolves color-mix() to `color(srgb r g b / a)` with 0-1 channels,
// so a naive number-scrape would read those as near-black. Handle both forms.
function parse(c){
  c=(c||'').trim();
  if(c==='transparent'||c==='') return {r:0,g:0,b:0,a:0};
  let m=c.match(/^color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\s*\)$/);
  if(m) return {r:+m[1]*255,g:+m[2]*255,b:+m[3]*255,a:m[4]===undefined?1:+m[4]};
  const n=(c.match(/[\d.]+/g)||[0,0,0]).map(Number);
  return {r:n[0],g:n[1],b:n[2],a:n.length>3?n[3]:1};}
function over(f,b){const a=f.a;return {r:f.r*a+b.r*(1-a),g:f.g*a+b.g*(1-a),
  b:f.b*a+b.b*(1-a),a:1};}
function lum(c){const f=v=>{v/=255;return v<=0.04045?v/12.92:
  Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}
function ratio(a,b){const L1=lum(a),L2=lum(b);
  return (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);}
function bgOf(el){let n=el,acc=null;
  while(n){const c=parse(getComputedStyle(n).backgroundColor);
    if(c.a>0){acc=acc?over(acc,c):c; if(acc.a>=1||c.a>=1) return acc;}
    n=n.parentElement;}
  return acc||{r:255,g:255,b:255,a:1};}
const out=[];
document.querySelectorAll('body *').forEach(el=>{
  if(el.closest('[hidden]')) return;
  const cs=getComputedStyle(el);
  if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0) return;
  const own=[...el.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim())
    .map(n=>n.textContent.trim()).join(' ');
  if(!own) return;
  const r=el.getBoundingClientRect(); if(r.width===0||r.height===0) return;
  const fg=parse(cs.color), bg=bgOf(el);
  const cr=ratio(over(fg,bg),bg);
  const px=parseFloat(cs.fontSize);
  const bold=(parseInt(cs.fontWeight,10)||400)>=700;
  const need=(px>=24||(px>=18.66&&bold))?3.0:4.5;
  if(cr<need) out.push({text:own.slice(0,40),
    ratio:Math.round(cr*100)/100, need:need});
});
return out;
"""

_OVERFLOW_JS = """
const de=document.documentElement;
function clipped(el){let n=el.parentElement;
  while(n && n!==document.body){
    if(/auto|scroll|hidden/.test(getComputedStyle(n).overflowX)) return true;
    n=n.parentElement;}
  return false;}
const wide=[...document.querySelectorAll('body *')].filter(el=>{
  const r=el.getBoundingClientRect();
  if(r.width===0||clipped(el)) return false;
  return r.right>de.clientWidth+1||r.left<-1;
}).slice(0,5).map(el=>el.tagName.toLowerCase()+'.'+
  (typeof el.className==='string'?el.className.trim().split(/\\s+/).join('.'):''));
return {scrollW:de.scrollWidth, clientW:de.clientWidth, offenders:wide};
"""

_BUTTON_JS = r"""
function parse(c){const m=(c.match(/[\d.]+/g)||[0,0,0]).map(Number);
  return {r:m[0],g:m[1],b:m[2],a:m.length>3?m[3]:1};}
function lum(c){const f=v=>{v/=255;return v<=0.04045?v/12.92:
  Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);}
function bgOf(el){let n=el;while(n){const c=parse(getComputedStyle(n).backgroundColor);
  if(c.a>0)return c;n=n.parentElement;}return{r:255,g:255,b:255,a:1};}
return [...document.querySelectorAll('.btn')].map(b=>{
  const cs=getComputedStyle(b),fg=parse(cs.color),bg=bgOf(b);
  const L1=lum(fg),L2=lum(bg);
  return {t:b.textContent.trim().slice(0,26),
          r:Math.round(((Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05))*100)/100};});
"""


@pytest.mark.parametrize("page", PAGES)
def test_text_contrast_meets_wcag_aa(browser, origin, page):
    browser.size(1440, 1400)
    browser.get(f"{origin}/{page}.html")
    if page == "faq":
        browser.js("document.querySelectorAll('.qa').forEach(d=>d.open=true);")
        time.sleep(0.6)
    bad = browser.js(_CONTRAST_JS)
    detail = "; ".join(f"{b['ratio']}:1 (needs {b['need']}) “{b['text']}”"
                       for b in bad[:6])
    assert not bad, f"{page}.html has {len(bad)} low-contrast elements: {detail}"


@pytest.mark.parametrize("width,label", [(360, "phone"), (768, "tablet"),
                                         (1440, "desktop")])
@pytest.mark.parametrize("page", PAGES)
def test_no_horizontal_overflow(browser, origin, page, width, label):
    browser.size(width, 1200)
    browser.get(f"{origin}/{page}.html")
    r = browser.js(_OVERFLOW_JS)
    assert r["scrollW"] <= r["clientW"] + 1, (
        f"{page}.html scrolls sideways at {width}px ({label}): "
        f"{r['scrollW']} > {r['clientW']}, offenders {r['offenders']}")


@pytest.mark.parametrize("page", PAGES)
def test_buttons_are_legible(browser, origin, page):
    browser.size(1440, 1400)
    browser.get(f"{origin}/{page}.html")
    bad = [b for b in browser.js(_BUTTON_JS) if b["r"] < 4.5]
    assert not bad, f"{page}.html: " + "; ".join(
        f"“{b['t']}” at {b['r']}:1" for b in bad)


def test_faq_expand_and_collapse_all(browser, origin):
    browser.size(1440, 1400)
    browser.get(f"{origin}/faq.html")
    total = browser.js("return document.querySelectorAll('.qa').length;")
    browser.js("document.querySelector(\"[data-action='expand']\").click();")
    time.sleep(0.6)
    assert browser.js("return document.querySelectorAll('.qa[open]').length;") == total
    browser.js("document.querySelector(\"[data-action='collapse']\").click();")
    time.sleep(0.6)
    assert browser.js("return document.querySelectorAll('.qa[open]').length;") == 0


def test_faq_deep_link_opens_question(browser, origin):
    browser.get(f"{origin}/faq.html#q-decorators")
    assert browser.js(
        "const e=document.getElementById('q-decorators');return !!(e && e.open);")


def test_project_details_fold(browser, origin):
    browser.get(f"{origin}/projects.html")
    state = browser.js("""return {
        folds: document.querySelectorAll('.fold').length,
        open:  document.querySelectorAll('.fold[open]').length,
        height: document.body.scrollHeight};""")
    assert state["folds"] == 12, f"expected 12 folds, found {state['folds']}"
    assert state["open"] == 0, "folds should start collapsed"
    expanded = browser.js("""document.querySelectorAll('.fold')
        .forEach(f=>f.open=true); return document.body.scrollHeight;""")
    assert expanded > state["height"], "expanding the folds did not grow the page"


def test_copy_buttons_are_added(browser, origin):
    browser.get(f"{origin}/faq.html")
    assert browser.js("return document.querySelectorAll('.snippet .copy').length;") > 0


def test_nav_link_reacts_to_hover(browser, origin):
    browser.size(1440, 1400)
    browser.get(f"{origin}/index.html")
    before = browser.js("""const a=document.querySelector('.nav a:not([aria-current])');
        const c=getComputedStyle(a);return [c.color,c.backgroundColor];""")
    box = browser.js("""const a=document.querySelector('.nav a:not([aria-current])');
        const r=a.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];""")
    browser._rq("POST", f"/session/{browser.sid}/actions", {"actions": [{
        "type": "pointer", "id": "mouse",
        "parameters": {"pointerType": "mouse"},
        "actions": [{"type": "pointerMove", "x": int(box[0]), "y": int(box[1])},
                    {"type": "pause", "duration": 400}]}]})
    time.sleep(0.4)
    after = browser.js("""const a=document.querySelector('.nav a:not([aria-current])');
        const c=getComputedStyle(a);return [c.color,c.backgroundColor];""")
    assert after != before, f"nav hover changed nothing: {before}"


def test_mobile_menu_opens(browser, origin):
    browser.size(390, 900)
    browser.get(f"{origin}/index.html")
    assert browser.js("""const t=document.querySelector('.nav-toggle');
        return !!(t && !t.hidden && getComputedStyle(t).display!=='none');"""), \
        "menu button is not visible at 390px"
    browser.js("document.querySelector('.nav-toggle').click();")
    time.sleep(0.5)
    assert browser.js("""const n=document.getElementById('nav');
        return getComputedStyle(n).display!=='none' && n.dataset.open==='true';"""), \
        "menu button did not open the navigation"
