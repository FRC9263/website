# FRC 9263 ALD Lions — website

Live at **frc9263.ca**. Hosted on Cloudflare (Worker `frc9263-website`, static assets only).

## How it works

```
content/    page text in Markdown   (about.md, join.md)
data/       lists in YAML           (site.yaml, sponsors.yaml, members.yaml)
templates/  page layouts (HTML)
static/     css + images, copied as-is
build.py    turns all of the above into public/
sponsor_pdf.py  builds public/sponsor-pack.pdf from the same sponsor text
public/     the finished site — this is what Cloudflare serves
```

## Update the site

1. Edit a file in `content/` or `data/` (most changes never need anything else).
2. Rebuild:

   ```
   pip install -r requirements.txt
   python build.py
   ```

3. Commit **both** your edit and the changed files in `public/`, then push.
   Cloudflare redeploys automatically.

## Rules

- Never commit API keys or passwords. This repo is public.
- Members are students: first name + last initial only, no photos without school consent.
- Facts on the site (results, awards, sponsors) should come from
  [FRC Events](https://frc-events.firstinspires.org/team/9263) or
  [The Blue Alliance](https://www.thebluealliance.com/team/9263).

See `SITEMAP.md` for the full plan.
