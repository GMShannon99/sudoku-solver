# Sudoku Solver

A Sudoku puzzle solver with a graphical interface, built in Python using tkinter. Type in your own puzzle, load the built-in sample, generate a brand-new one at your chosen difficulty, or paste one back in from a saved file — then either solve it step by step yourself with candidate hints and undo, or let the solver finish it for you with one click.

## Current version

**v1.4.0** (from `__version__` in `sudoku_gui.py`)

## Features

- **Puzzle entry screen** — start from a blank 9x9 grid and type in your own clues, or use one of the buttons below to load a puzzle instead.
- **Use Sample Puzzle** — loads the built-in "world's hardest sudoku"-style sample puzzle.
- **Generate Puzzle** — creates a brand-new, randomly generated puzzle at a difficulty you select (Easy, Moderate, or Hard) via radio buttons next to the button. Guaranteed to have exactly one valid solution; if you click it without picking a difficulty, it defaults to Moderate rather than blocking you.
- **Paste Puzzle** — loads a puzzle record copied to the clipboard from `Sudoku_Save.txt` (see [Saved puzzle file format](#saved-puzzle-file-format) below). The pasted puzzle is independently validated by actually solving it before being accepted — an unsolvable or corrupted paste is rejected with an on-screen error rather than being loaded. Any trailing difficulty character in the pasted text is optional and ignored; only the 81 grid digits are used.
- **Click-to-see-candidates** — click any empty cell to highlight it yellow and show clickable buttons for every digit that's legally still valid there (missing from that cell's row, column, and box). Click a button to fill the cell.
- **Live row/column missing-digit labels** — the digits still missing from each row are shown to the right of it, and the digits still missing from each column are shown below it, updating as you type. A completed row or column shows a checkmark.
- **Auto-complete detection** — if you fill in every remaining cell yourself, the app automatically checks the result: if it matches the puzzle's correct solution, the cells lock (shown in blue) and the iteration count is shown, exactly as if you'd clicked Solve; if the grid is full but doesn't match, that means a *different* valid solution also exists, and a "Multiple Solutions" message is shown instead.
- **Ctrl+Z undo** — while on the solving screen, pressing Ctrl+Z undoes your most recent cell entry, one step at a time. This is separate from Save/Reset below (it tracks every entry automatically), and only works on the solving screen — it has no effect on the puzzle entry screen.
- **Save / Reset backup snapshots** — Save takes an in-memory snapshot of the current grid onto a backup stack (you can save multiple times); Reset restores the most recently saved backup, or clears back to the puzzle's original clues if nothing has been saved. Lost when the app closes.
- **Save to File** — appends the puzzle's *original given clues* (never your guesses or the solved values, regardless of solving progress) as a new record to `Sudoku_Save.txt` in the app's folder. Each save adds another record rather than overwriting the file — see [Saved puzzle file format](#saved-puzzle-file-format) below.
- **Solve button** — runs the full solver (naked singles propagation plus MRV-guided backtracking) and fills in every remaining cell.
- **Difficulty rating** — shown above the puzzle once solving starts, based on how many backtracking guesses the solver needed for the puzzle's original clues: 0 guesses = Easy, 1–39 = Moderate, 40+ = Hard.
- **Help window** — a separate window explaining every control on both the entry screen and the solving screen, including an author/contact section (name, email, and a note that bug reports or questions can be sent there), a link to this GitHub repo noting the project is open source, and a "Version X — Last updated: \<date>" line.
- **New/Clear button** — asks for confirmation, then discards the current puzzle, all saved backups, and undo history, and returns you to the puzzle entry screen to start over.
- **Input validation** — any digit you type or click in is checked against its row, column, and 3x3 box; an invalid digit is rejected (the cell stays blank) with an audible beep.

> Note: earlier versions showed "By Gil Shannon" in the window title bars. That credit now lives in the Help window's author/contact section instead — the title bars just show the screen name and version.

## Saved puzzle file format

"Save to File" and "Paste Puzzle" (above) share a simple text record format, one puzzle per line, appended to `Sudoku_Save.txt` in the same folder as the running script or `.exe`:

- **81 characters** — the grid itself, row by row, 9 characters per row. Each character is the digit `1`–`9` for a given clue, or `0` for an empty cell. Only the puzzle's *original* clues are ever written — never guesses or solver-filled values.
- **1 optional trailing character** — a difficulty letter (`E`/`M`/`H` for Easy/Moderate/Hard) written by "Save to File" for reference. This character is purely informational: "Paste Puzzle" never trusts it and ignores it entirely, since every pasted puzzle is independently re-validated and re-rated by actually solving it. A line of exactly 81 characters (no trailing character at all) is equally valid.

Each click of "Save to File" appends a new line rather than overwriting the file, so puzzles saved across different sessions all accumulate in the same file. To load one back in, copy a single line from `Sudoku_Save.txt` onto the clipboard and click "Paste Puzzle" on the entry screen.

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

This generates `sudoku_gui.spec`, which is checked into the repo. For any rebuild after the first, prefer running PyInstaller against that existing spec file instead, so the build config stays consistent:

```
pyinstaller sudoku_gui.spec --noconfirm
```

Re-run after any code change to produce an updated `.exe`. Note that `venv\Scripts\activate` needs to be re-run every time you open a new terminal session for this project.

## Project structure

- `sudoku_gui.py` — the tkinter GUI (puzzle entry screen and solving screen).
- `sudoku_solver.py` — the solving logic (tracking sets, candidates, naked singles, backtracking, puzzle generation, uniqueness checking) plus a terminal-based entry point.
- `sudoku_gui.spec` — PyInstaller build spec for `sudoku_gui.py`.
- `dist/` — the built executable.
- `build/` — PyInstaller's intermediate build files.
- `Sudoku_Save.txt` — created at runtime (not checked into git) the first time "Save to File" is used; see [Saved puzzle file format](#saved-puzzle-file-format) above.

## Versioning

Version numbers are bumped manually, following semantic versioning (MAJOR.MINOR.PATCH). Each version bump should ideally correspond to a git commit describing the change.
