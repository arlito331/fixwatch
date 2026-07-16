# FixWatch

**FixWatch** tracks potholes that have been repaired with **PowerPatch** — proof that a fix is holding, not just that it was made.

Part of the PowerFix tool family: [PotholeWatch](https://github.com/arlito331/potholewatch) (reactive incident monitor) · [Case Study Generator](https://github.com/arlito331/powerfix-case-study) (ROI PDFs) · [PotholeRadar](https://github.com/arlito331/potholeradar) (proactive area scanner) · **FixWatch** (post-repair durability tracker).

## What it tracks

Two things, deliberately kept minimal:

1. **Exact location** — search a place, click the map, drag the pin, or paste coordinates.
2. **Date fixed with PowerPatch** — used to compute "days holding" live, client-side, every time the page loads.

Optional label/notes can be attached to a fix, but the core record is just `{lat, lng, fix_date}`.

## How it works

- `index.html` (GitHub Pages) is the whole app — a **Fixed Map** tab (all logged fixes, sorted by days holding, longest first) and a **Log a Fix** tab (map picker + date + notes).
- Data lives in `data/fixes.json`, a flat JSON array. There's no backend — the browser reads it via `raw.githubusercontent.com` and writes new entries directly through GitHub's Contents API.
- Click the gear icon once and paste a GitHub personal access token with **`repo`** scope (stored only in your browser's localStorage — never sent anywhere except `api.github.com`). That's the only auth this app needs; logging a fix requires no server-side secrets, so there's no GitHub Actions workflow involved.
- "Days holding" is never stored — it's recomputed from `fix_date` vs. today on every page load, so it's always current.

## Running locally

No build step, no dependencies. Just open `index.html` in a browser, or serve the folder statically:

```bash
python3 -m http.server 8000
```

## Roadmap (not built yet)

- Photo attachment per fix (before/after or just "still holding" proof shots)
- Linking a fix back to the PotholeRadar finding or PotholeWatch incident it originated from
- Filtering the Fixed Map by territory/country
- Surfacing durability stats (e.g. "average days holding") in the Case Study Generator's PDFs
