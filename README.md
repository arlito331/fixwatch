# LogPothole

**LogPothole** lets government road crews report specific potholes — a photo plus an exact location — and track them to repair. Every report is a **red dot** on the map until it's fixed, then it turns **green**.

Formerly **FixWatch** (post-repair durability tracker). The pivot inverts the lifecycle: records are now born *reported* (red) and become *fixed* (green), instead of being logged only after repair. Everything FixWatch tracked — photo timelines, "days holding", timelapse and video export — still works on fixed potholes.

Part of the PowerFix tool family: [PotholeWatch](https://github.com/arlito331/potholewatch) (reactive incident monitor) · [Case Study Generator](https://github.com/arlito331/powerfix-case-study) (ROI PDFs) · [PotholeRadar](https://github.com/arlito331/potholeradar) (proactive area scanner) · **LogPothole** (report → fix tracker).

## How a pothole gets reported and fixed

1. **Report** (staff-only): search an address, click the map, drag the pin, or use GPS; attach "before" photos; add notes. The pothole appears as a red dot.
2. **Fix** — a red dot turns green either way:
   - the manual **"Mark fixed"** toggle (with a fix date), or
   - **uploading an "after" photo** — any upload on an open pothole marks it fixed, no AI verification for now.
3. **Prove it holds**: fixed potholes keep the FixWatch photo timeline ("Day 0", "Day 20", …), live "days holding" math, timelapse playback, and client-side video export.

A fixed pothole can be **reopened** if the repair fails.

## Ruta crítica

The map list doubles as the critical-path backlog: open potholes first (oldest report on top), then fixed ones (longest holding on top). An actual routing feature over this ordering is planned. Also planned, not built: pothole size / material-volume estimation.

## How it works

- `index.html` (GitHub Pages) is the whole app — a **Map · Ruta Crítica** tab and a **Report a Pothole** tab. No build step, no backend.
- Data lives in `data/fixes.json`, a flat JSON array. The browser reads it via `raw.githubusercontent.com` and writes through GitHub's Contents API.
- Core record: `{lat, lng, report_date, status: "reported" | "fixed", fix_date, photos}`. Records without a `status` (pre-pivot FixWatch data) are treated as `fixed`.
- Reporting is **government-staff-only for now**: writing requires the staff access code (a GitHub token with `repo` scope) pasted once via the gear icon, stored only in the browser's localStorage.
- "Days open" / "days holding" are never stored — recomputed on every page load.

## Running locally

```bash
python3 -m http.server 8000
```

Or just open `index.html` in a browser.

## Roadmap (not built yet)

- Routing over the ruta crítica (ordered repair route for a crew day)
- Pothole size / material-volume estimation from report photos
- AI verification of "after" photos (currently any upload marks a pothole fixed)
- Public (non-staff) reporting with moderation
