# Sudoku Solver

A Sudoku puzzle solver with a graphical interface, built in Python using tkinter. Type in your own puzzle (or load the built-in sample) and either solve it step by step yourself with candidate hints, or let the solver finish it for you with one click.

## Current version

**v1.2.2** (from `__version__` in `sudoku_gui.py`)

## Features

- **Puzzle entry screen** — start from a blank 9x9 grid and type in your own clues, or click "Use Sample Puzzle" to load the built-in sample puzzle instead.
- **Click-to-see-candidates** — click any empty cell to highlight it yellow and show clickable buttons for every digit that's legally still valid there (missing from that cell's row, column, and box). Click a button to fill the cell.
- **Live row/column missing-digit labels** — the digits still missing from each row are shown to the right of it, and the digits still missing from each column are shown below it, updating as you type. A completed row shows "done"; a completed column shows a checkmark.
- **Save / Reset backup snapshots** — Save takes a snapshot of the current grid onto a backup stack (you can save multiple times); Reset restores the most recently saved backup, or clears back to the puzzle's original clues if nothing has been saved.
- **Solve button** — runs the full solver (naked singles propagation plus MRV-guided backtracking) and fills in every remaining cell.
- **Help window** — a separate window explaining every control on both the entry screen and the solving screen.
- **New/Clear button** — asks for confirmation, then discards the current puzzle and all backups and returns you to the puzzle entry screen to start over.
- **Difficulty rating** — shown above the puzzle once solving starts, based on how many backtracking guesses the solver needed: 0 guesses = Easy, 1–39 = Moderate, 40+ = Hard.
- **Input validation** — any digit you type or click in is checked against its row, column, and 3x3 box; an invalid digit is rejected (the cell stays blank) with an audible beep.

## How to run it

### Running from source

Requires Python 3. `sudoku_gui.py` depends on `sudoku_solver.py` being in the same folder.

```
python sudoku_gui.py
```

### Running the prebuilt executable

Just double-click `sudoku_gui.exe` in the `dist` folder. No Python installation required.

## How to build the .exe yourself

```
python -m venv venv
venv\Scripts\activate
pip install pyinstaller
pyinstaller --onefile --windowed sudoku_gui.py
```

Re-run the `pyinstaller` command after any code change to produce an updated `.exe`. Note that `venv\Scripts\activate` needs to be re-run every time you open a new terminal session for this project.

## Project structure

- `sudoku_gui.py` — the tkinter GUI (puzzle entry screen and solving screen).
- `sudoku_solver.py` — the solving logic (tracking sets, candidates, naked singles, backtracking) plus a terminal-based entry point.
- `sudoku_gui.spec` — PyInstaller build spec for `sudoku_gui.py`.
- `dist/` — the built executable.
- `build/` — PyInstaller's intermediate build files.

## Versioning

Version numbers are bumped manually, following semantic versioning (MAJOR.MINOR.PATCH). Each version bump should ideally correspond to a git commit describing the change.
