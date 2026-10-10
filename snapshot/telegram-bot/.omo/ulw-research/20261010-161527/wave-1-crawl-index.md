# Wave 1 — crawl/index

- All sitemap URLs are crawlable 200/index-follow, but all subpages share the home title, description, canonical, and `og:url`.
- 34 non-home URLs therefore signal that the homepage is canonical.
- Four host/protocol variants answer 200 without redirect.
- Database-route misses answer 200 with JavaScript errors; soft-404 risk.
- `robots.txt` blocks `/data/`; this blocks 22 public image URLs observed, mainly homepage popups/events, not the service pages.

## EXPAND

- LEAD: Public `/data/` asset inventory — WHY: scope of blocked visual media determines safe robots fix — ANGLE: inspect each sitemap page and event sources.

