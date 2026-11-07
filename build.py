"""Build the FRC 9263 website.

Reads content/ (Markdown), data/ (YAML), templates/ (HTML) and static/,
and writes the finished site into public/ — the folder Cloudflare serves.

Run:  python build.py              (also fetches the news feeds)
      python build.py --no-fetch   (use the saved feeds, no internet)
"""
import hashlib
import shutil
import sys
from datetime import date
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

import feeds
import sponsor_pdf

ROOT = Path(__file__).parent
OUT = ROOT / "public"


def load_yaml(name):
    with open(ROOT / "data" / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_md(name):
    """Return (front matter dict, HTML body) for content/<name>.md."""
    text = (ROOT / "content" / f"{name}.md").read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        _, fm, text = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    return meta, markdown.markdown(text, extensions=["extra", "toc"])


def write(path, html):
    """path like '' (home), 'about', 'team' -> public/<path>/index.html"""
    target = OUT / path / "index.html" if path else OUT / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print("  wrote", target.relative_to(ROOT))


def main():
    # Start clean so deleted pages don't linger
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
    )
    site = load_yaml("site")
    # Changes whenever site.css changes, so browsers fetch the new CSS instead of a cached copy
    css_version = hashlib.md5((ROOT / "static/css/site.css").read_bytes()).hexdigest()[:8]
    common = {"site": site, "year": date.today().year, "css_version": css_version}

    def render(template, path, **ctx):
        html = env.get_template(template).render(**common, path=path, **ctx)
        write(path, html)

    news = feeds.load(fetch="--no-fetch" not in sys.argv)
    render("home.html", "", sponsors=load_yaml("sponsors"), news=news)

    for page in ["about", "join"]:
        meta, body = load_md(page)
        render("page.html", page, meta=meta, body=body)

    render("team.html", "team", team=load_yaml("members"))
    render("sponsors.html", "sponsors", sponsors=load_yaml("sponsors"))
    sponsor_pdf.build(ROOT, OUT, site, load_yaml("sponsors"))   # public/sponsor-pack.pdf

    # 404 page sits at public/404.html (Cloudflare serves it for unknown URLs)
    (OUT / "404.html").write_text(
        env.get_template("404.html").render(**common, path="404"), encoding="utf-8"
    )
    print("  wrote public/404.html")
    print("Done.")


if __name__ == "__main__":
    main()
