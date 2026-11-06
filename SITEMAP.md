# frc9263.ca — Site Map

Team 9263 ALD Lions · Aldershot School, Burlington ON · Rookie 2023

**How the site works:** Python builds the pages and Cloudflare hosts them. Students edit content as simple text files (`content/`, `data/`); everything marked **AUTO** refreshes on a schedule with no human involved.

---

## 1. Pages

| # | Page | URL | What's on it | Source | Updates |
|---|------|-----|--------------|--------|---------|
| 1 | Home | `/` | Hero photo + tagline, next event countdown, last result, 3 latest news items, sponsor logo strip | Mix | AUTO + manual |
| 2 | About | `/about` | Who we are, history (2023 rookie → 2025 Waterloo win), mission, the school | `content/about.md` | Once a year |
| 3 | Team | `/team` | Captains, sub-teams, members, mentors, teacher | `data/members.yaml` | Each September |
| 4 | Robots | `/robots` + `/robots/2026` | One page per season: robot name, game, photo, what it does, results | `content/robots/*.md` + TBA | Each season |
| 5 | Events | `/events` | Upcoming events + past results (rank, record, playoffs, awards) | TBA API | AUTO (hourly in season) |
| 6 | Awards | `/awards` | Award history + blue banners (2025 Waterloo) | TBA API | AUTO |
| 7 | Team News | `/news` | Our own posts: build updates, event recaps, outreach | `content/news/*.md` | Whenever |
| 8 | FRC & Robotics News | `/feed` | Headlines + link only (no copied articles): FIRST, FIRST Canada, world robotics | RSS feeds | AUTO (daily) |
| 9 | Sponsors | `/sponsors` | Current sponsors by tier, thank-you | `data/sponsors.yaml` | When it changes |
| 10 | Sponsor Us | `/sponsor-us` | Why sponsor, tiers + what each gets, contact, downloadable package | `content/sponsor-us.md` | Once a year |
| 11 | Media | `/media` | Photo albums, match videos | Manual + TBA media | Per event |
| 12 | Join / Contact | `/join` | How Aldershot students join, contact email (team Gmail) | `content/join.md` | Once a year |
| 13 | Stats | `/stats` | Our season EPA, trend, how we compare in Ontario | Statbotics | AUTO |
| — | Predictions | `predict.frc9263.ca` | Play-money match predictions, leaderboard, booth big-screen mode | Statbotics + TBA | Live at events |

Footer on every page: social links, GitHub, contact, "Data from The Blue Alliance / Statbotics / FIRST" (FIRST asks for a link back if their API data is shown).

---

## 2. Auto-update feeds

| Feed | Used for | Key needed | Status |
|------|----------|------------|--------|
| The Blue Alliance API v3 | Events, results, awards, media | Yes — `X-TBA-Auth-Key` | Verified |
| Statbotics API | EPA, win probabilities, stats page, predictions odds | No | Verified |
| FRC Events API (official) | Backup for results | Yes — username + token | Verified; no commercial use |
| FIRST FRC blog | `/feed` | — | **Feed URL not confirmed — test** |
| FIRST Robotics Canada news | `/feed` | — | **Feed URL not confirmed — test** |
| IEEE Spectrum Robotics | `/feed` | — | `feeds.feedburner.com/IeeeSpectrumRoboticsChannel` |
| The Robot Report | `/feed` | — | `therobotreport.com/feed` |

---

## 3. Content files (what students edit)

```
content/
  about.md
  join.md
  sponsor-us.md
  news/2026-11-01-overtime-sunday.md   ← one file per post
  robots/2026.md                       ← one file per season
data/
  members.yaml      ← name, role, sub-team, grad year
  sponsors.yaml     ← name, tier, logo file, link
  seasons.yaml      ← year, game name, robot name
static/
  img/ logos/ docs/
```

Rule: if it's text a student writes, it's a Markdown or YAML file. No one needs to touch Python to update the site.

---

## 4. Ideas taken from other teams

- **Menu layout** — Team 254: The Team / Robots / Media / Resources / Sponsors / Sponsor Us / Blog.
- **Separate event site** — 254 runs its event on its own site → our `predict.` subsite.
- **Sponsor tiers with listed benefits** — common pattern (logo on site → robot sticker → pit banner → social shoutout).
- **URL on everything** — AdamBots: shirts, pit posters, buttons, robot. Add a QR code to the booth.
- **Blue banners in CSS** — `banners.css` library.
- **Static site on Cloudflare Pages** — WAFFLES 4476 runs its wiki this way.

---

## 5. Build order

1. Skeleton: Home, About, Team, Sponsors, Join (manual content only) → live on frc9263.ca
2. Events + Awards from TBA (scheduled rebuild)
3. `/feed` news page
4. Robots, Media, Stats
5. Predictions subsite

---

## 6. Open questions (not verified — check before building)

- **Members page and minors:** first name + last initial only? Photos need school consent? → ask the teacher.
- **Predictions needs a live backend** (logins, points, leaderboard). The static Pages build can't hold that on its own — pick: Cloudflare Workers + D1, or a small VPS.
- **"Predictions," not "betting"** on a school team site, play money only, nicknames only.
- **Handover:** second owner on the Cloudflare account and the GitHub org (teacher), before Nikita graduates.
- **Team photos/logo files:** who has the originals?
