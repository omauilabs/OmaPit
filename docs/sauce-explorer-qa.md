# Sauce Explorer browser QA

Status: passed for this browser feature, 2026-10-04. This does not clear the separate Cut Explorer mesh fidelity issue.

## Evidence

- `sauce-explorer-desktop.png`: normal desktop browser viewport, three-column regional library, blend editor and dinner planner.
- `sauce-explorer-mobile.png`: mobile viewport request 390 × 844, observed document content width 375 px with scrollbar. Four Plan views fit one row.
- `sauce-explorer-mobile-mixer.png`: ingredient parts and scaled amounts fit on mobile.
- `sauce-explorer-mobile-dinner.png`: weight/unit pair spans full width; dinner fields and breakdown fit. Document scroll width = client width = 375 px; no horizontal page overflow.

## Exercised

- Open Plan → Sauces; reload directly at #sauces.
- Increase guests from 8 to 12; table allocation rises from 237 to 355 mL.
- Set two finishing coats on 5 lb raw pork at 55% edible cooked yield; glaze adds 150 mL. With 15% reserve, exact batch is approximately 580 mL and the headline rounds to 600 mL.
- Select Alabama white; editor, description, pairings, method and source change together.
- Change mayonnaise parts from 65 to 55; normalized percentage becomes 61.1%, and amounts recalculate.
- Save a uniquely named QA blend, reload the page, load it, and observe the edited recipe. Delete only the QA blend afterwards.
- Add a second food without increasing the guest table allocation; add honey to the blend.
- Open text export and inspect ingredients, two food assumptions, quantities, method, source and handling note in the existing export dialog.
- Enter zero guests: Save blend is disabled. Restore valid guests.
- Search for a nonexistent style: explicit empty state. Clear search, filter to Mustard, select Carolina gold, then restore all families.
- With no cut draft: clear explanation. Create a temporary 4 lb Brisket draft through Cut Explorer, import into Sauce Explorer, observe second food at 4 lb/raw/beef and a review-yield message. Clear only that temporary draft through New meal afterwards.
- Inspect mobile library, mixer and dinner inputs. Fix contextual nav overlap and nested weight field crowding, then recapture.
- Browser error/warning log: empty at final inspection.

## Build and calculations

Production build passes. Existing lazy Three.js chunk remains over 500 kB; no new chunk warning from Sauce Explorer. Six sauce tests and seven existing cut/packaging tests pass, 13 total. Final subsequent CSS-only change was rebuilt and visually checked.

## Scope limits

Kitchen taste, consumption and yield are untested. Planner defaults are editable estimates. Saved blends are local to this browser; dinner fields are transient. This is the web companion implementation; no native Quickshell or hardware claims. Existing active cook was preserved.
