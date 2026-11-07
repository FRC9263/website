"""Build the one-page sponsor pack PDF (public/sponsor-pack.pdf).

All text comes from data/site.yaml and data/sponsors.yaml (the `pitch:` block),
so the PDF always matches the Sponsors page. Called from build.py.
"""
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Frame, KeepInFrame, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

# Team colours (same as static/css/site.css)
GREEN = HexColor("#2f7d66")
GREEN_DEEP = HexColor("#1b4a40")
GOLD = HexColor("#e9c441")
INK = HexColor("#17221e")
MUTED = HexColor("#55615c")
MIST = HexColor("#eef3f0")

W, H = letter
M = 0.6 * inch  # page margin


def _styles():
    base = dict(fontName="Helvetica", textColor=INK, fontSize=10.5, leading=14.5)
    return {
        "title": ParagraphStyle("title", **{**base, "fontName": "Helvetica-Bold", "fontSize": 26, "leading": 29}),
        "intro": ParagraphStyle("intro", **{**base, "fontSize": 12, "leading": 16.5}),
        "h": ParagraphStyle("h", **{**base, "fontName": "Helvetica-Bold", "fontSize": 13, "leading": 16,
                                    "textColor": GREEN_DEEP, "spaceBefore": 6, "spaceAfter": 4}),
        "body": ParagraphStyle("body", **base),
        "bullet": ParagraphStyle("bullet", **{**base, "leftIndent": 12, "bulletIndent": 0, "spaceAfter": 2}),
        "small": ParagraphStyle("small", **{**base, "fontSize": 9.5, "leading": 13, "textColor": MUTED}),
        "lvl_name": ParagraphStyle("lvl_name", **{**base, "fontName": "Helvetica-Bold", "fontSize": 13}),
        "lvl_amt": ParagraphStyle("lvl_amt", **{**base, "fontName": "Helvetica-Bold", "textColor": GREEN_DEEP}),
    }


def _bullets(items, st):
    return [Paragraph(escape(str(i)), st["bullet"], bulletText="•") for i in items]


def build(root: Path, out: Path, site: dict, sponsors: dict):
    pitch = sponsors.get("pitch") or {}
    st = _styles()
    target = out / "sponsor-pack.pdf"

    from reportlab.pdfgen.canvas import Canvas
    c = Canvas(str(target), pagesize=letter, invariant=1)  # same input -> same bytes, no daily churn
    c.setTitle(f"Sponsor Team {site['team_number']} - {site['name']}")
    c.setAuthor(f"FRC Team {site['team_number']}")

    # ---- Header band: green, logo, team name, green|gold seam ----
    band_h = 1.15 * inch
    c.setFillColor(GREEN_DEEP)
    c.rect(0, H - band_h, W, band_h, stroke=0, fill=1)
    logo = root / "static" / "img" / "logo.png"
    if logo.exists():
        c.drawImage(ImageReader(str(logo)), M, H - band_h + 0.15 * inch, 0.85 * inch, 0.85 * inch, mask="auto")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(M + 1.05 * inch, H - 0.62 * inch, site["name"])
    c.setFillColor(GOLD)
    c.drawString(M + 1.05 * inch + c.stringWidth(site["name"] + " ", "Helvetica-Bold", 24), H - 0.62 * inch,
                 str(site["team_number"]))
    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    c.drawString(M + 1.05 * inch, H - 0.9 * inch,
                 f"FIRST Robotics Competition  ·  {site['school']}, {site['city']}")
    c.setFillColor(GREEN)
    c.rect(0, H - band_h - 6, W / 2, 6, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(W / 2, H - band_h - 6, W / 2, 6, stroke=0, fill=1)

    # ---- Footer: contact strip ----
    foot_h = 0.75 * inch
    c.setFillColor(INK)
    c.rect(0, 0, W, foot_h, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M, 0.43 * inch, "Talk to us:")
    c.setFillColor(white)
    c.setFont("Helvetica", 11.5)
    contact = f"{site['email']}   ·   frc9263.ca/sponsors   ·   Instagram @frc{site['team_number']}"
    c.drawString(M + 0.95 * inch, 0.43 * inch, contact)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(HexColor("#9fb0a8"))
    c.drawString(M, 0.2 * inch, "Results and awards: thebluealliance.com/team/"
                 f"{site['team_number']}  ·  frc-events.firstinspires.org/team/{site['team_number']}")

    # ---- Body ----
    top = H - band_h - 6 - 0.3 * inch
    bottom = foot_h + 0.25 * inch
    full_w = W - 2 * M

    story = [Paragraph(escape(pitch.get("heading", f"Sponsor Team {site['team_number']}")), st["title"]),
             Spacer(1, 6),
             Paragraph(escape(" ".join(str(pitch.get("intro", "")).split())), st["intro"]),
             Spacer(1, 10)]

    # Team photo (already public on the home page), full width, cropped to a strip
    photo = root / "static" / "img" / site.get("hero_photo", "team-photo.jpg")
    if photo.exists():
        story.append(_PhotoStrip(str(photo), full_w, (2.2 if pitch.get("show_levels") else 3.0) * inch))
        story.append(Spacer(1, 12))

    # Two columns: where the money goes | track record
    left = [Paragraph("Where your support goes", st["h"])] + _bullets(pitch.get("uses", []), st)
    right = [Paragraph("Our track record", st["h"])] + _bullets(pitch.get("highlights", []), st)
    cols = Table([[left, right]], colWidths=[full_w * 0.55, full_w * 0.45], hAlign="LEFT")
    cols.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (1, 0), (1, 0), MIST),
        ("LINEABOVE", (1, 0), (1, 0), 4, GOLD),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 12),
        ("TOPPADDING", (1, 0), (1, 0), 8), ("BOTTOMPADDING", (1, 0), (1, 0), 10),
    ]))
    story += [cols, Spacer(1, 8)]

    if pitch.get("in_kind"):
        story.append(Paragraph(escape(" ".join(str(pitch["in_kind"]).split())), st["body"]))
        story.append(Spacer(1, 6))

    # Levels: only when switched on in sponsors.yaml (same rule as the web page)
    levels = pitch.get("levels") or []
    if pitch.get("show_levels") and levels:
        story.append(Paragraph("Sponsorship levels", st["h"]))
        cells = []
        for lv in levels:
            cell = [Paragraph(escape(lv["name"]), st["lvl_name"]),
                    Paragraph(escape(lv.get("amount") or "Ask us"), st["lvl_amt"]), Spacer(1, 3)]
            cell += _bullets(lv.get("perks", []), st)
            cells.append(cell)
        lt = Table([cells], colWidths=[full_w / len(cells)] * len(cells), hAlign="LEFT")
        lt.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), MIST),
            ("LINEABOVE", (0, 0), (-1, 0), 4, GREEN),
            ("LINEAFTER", (0, 0), (-2, 0), 4, white),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story += [lt, Spacer(1, 8)]

    # Current sponsors
    names = [s["name"] for t in sponsors.get("tiers", []) for s in t.get("sponsors", [])]
    if names:
        story.append(Paragraph(f"Thank you to our {sponsors.get('season', '')} sponsors", st["h"]))
        story.append(Paragraph(escape("  ·  ".join(names)), st["small"]))

    # Shrink to fit if the text grows, so it always stays one page
    frame = Frame(M, bottom, full_w, top - bottom, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame.addFromList([KeepInFrame(full_w, top - bottom, story, mode="shrink")], c)

    c.showPage()
    c.save()
    print("  wrote", target.relative_to(root))


from reportlab.platypus import Flowable  # noqa: E402


class _PhotoStrip(Flowable):
    """Photo scaled to the full width and cropped top/bottom to a fixed height."""

    def __init__(self, path, width, height):
        super().__init__()
        self.img = ImageReader(path)
        self.width, self.height = width, height

    def draw(self):
        iw, ih = self.img.getSize()
        draw_h = self.width * ih / iw
        c = self.canv
        c.saveState()
        p = c.beginPath()
        p.rect(0, 0, self.width, self.height)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(self.img, 0, (self.height - draw_h) / 2, self.width, draw_h)
        c.restoreState()
