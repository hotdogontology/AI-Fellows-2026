# Food Chain Simulator

A beginner-friendly Python desktop app for classrooms. Students build a 4-level food chain, visualize energy flow, then add populations to compare relative abundance.

## How to run

1. Open a terminal in this folder: `JBrown-FoodWeb-2026`
2. Run:

```bash
python main.py
```

No internet, installs, or external packages are needed.

## What students do

1. Enter four organisms in order:
   - Producer
   - Primary consumer
   - Secondary consumer
   - Tertiary consumer
2. Enter population values for each level, or click **Default Populations**.
3. Click **Build Chain**.
4. Observe:
   - Labeled level boxes
   - Arrows for energy flow (producer → primary → secondary → tertiary)
   - Colored dot grids representing population size
   - Dot scale legend and color legend
5. Try **Load Example** for quick demos, and **Reset** to start over.

## How to explain what is happening

- **Energy flow:** Arrows point upward through trophic levels, showing energy transfer from organisms being eaten to organisms that eat them.
- **Population pattern:** Lower levels (especially producers) usually have larger populations. Higher levels have fewer organisms because energy is lost at each transfer.
- **Scaling:** Dot displays use an automatic scale so large numbers still fit on screen (for example, `1 dot = 10 individuals`).

## Included example chains

The app includes at least 3 hardcoded examples:
- Grass → Rabbit → Snake → Hawk
- Phytoplankton → Zooplankton → Small Fish → Tuna
- Oak Tree → Caterpillar → Robin → Fox

## File structure

- `main.py` — entry point (`python main.py`)
- `ui.py` — Tkinter layout and event handlers
- `model.py` — data, examples, and input validation
- `draw.py` — canvas drawing utilities

## Manual acceptance checks

- Launch app window successfully.
- Build chain with valid names/populations and see boxes + arrows + population visuals.
- Reset clears fields and canvas.
- Default populations fill as 1000 / 100 / 10 / 1.
- Invalid population input shows friendly errors without crashing.

## Optional packaging note (not required)

If your school already uses PyInstaller, you can package this as an executable:

```bash
pyinstaller --onefile --windowed main.py
```

This app does **not** require PyInstaller to run in class.
