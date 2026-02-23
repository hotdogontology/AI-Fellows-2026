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
   - Labeled level boxes (producer at bottom, higher consumers above)
   - Upward arrows for energy flow (producer → primary → secondary → tertiary)
   - Colored population symbols near each level
   - Symbol legend and color legend
5. Try **Load Example** for quick demos, and **Reset** to start over.

## Dynamic population updates (new)

After building a chain:

1. Choose a model (**Balanced**, **Predator Pressure**, or **Bottom-Up**).
2. Choose one level to change.
3. Enter a new value.
4. Click **Apply Change Across Web**.

The app updates all other levels to reflect linked food-web effects.

### Model meanings

- **Balanced**: prey availability and predator pressure are both moderate.
- **Predator Pressure**: top-down effects are stronger.
- **Bottom-Up**: resource/prey effects are stronger.

## How to explain what is happening

- **Energy flow:** Arrows point upward from producer to higher consumers.
- **Population pattern:** Lower levels (especially producers) usually have larger populations. Higher levels have fewer organisms because energy is lost at each transfer.
- **Dynamic update:** Changing one population can affect nearby levels (for example, more primary consumers can reduce producers and support more secondary consumers).
- **Symbol scale:**
  - `■` = grouped individuals (auto-scaled, example: 10/50/100)
  - `•` = 1 individual (used for remainders)

## Included example chains

The app includes at least 3 hardcoded examples:
- Grass → Rabbit → Snake → Hawk
- Phytoplankton → Zooplankton → Small Fish → Tuna
- Oak Tree → Caterpillar → Robin → Fox

## File structure

- `main.py` — entry point (`python main.py`)
- `ui.py` — Tkinter layout and event handlers
- `model.py` — data, examples, validation, and dynamic update models
- `draw.py` — canvas drawing utilities

## Manual acceptance checks

- Launch app window successfully.
- Build chain with valid names/populations and see boxes + arrows + population visuals.
- Verify producer is drawn at the bottom and arrows point upward.
- Reset clears fields and canvas.
- Default populations fill as 1000 / 100 / 10 / 1.
- Invalid numeric input shows friendly errors without crashing.
- Applying dynamic changes updates related levels.

## Optional packaging note (not required)

If your school already uses PyInstaller, you can package this as an executable:

```bash
pyinstaller --onefile --windowed main.py
```

This app does **not** require PyInstaller to run in class.

