"""
Sudoku GUI
==========
 
Two screens, shown one after another in the same window:
 
1. PuzzleEntryGUI -- a blank 9x9 grid. Type your puzzle's clues
   directly into the squares you want filled; leave every other
   square blank (no need to type 0 anywhere). Each digit is validated
   against its row/column/box, same as guessing on screen 2. A "Use
   Sample Puzzle" button skips straight to the built-in sample_puzzle
   instead, a "Paste Puzzle" button loads a single saved-puzzle record
   (see Sudoku_Save.txt below) off the system clipboard and jumps
   straight to the solving screen with it, a "Generate Puzzle" button
   creates a brand-new randomly generated puzzle at a chosen
   difficulty, and a "Create New" button clears the grid so you can
   start typing a fresh puzzle.

2. SudokuGUI -- the solving screen. Whatever puzzle came out of
   screen 1 appears here with those clues locked (shown in a
   different color) and every other cell open for your own guesses.
   To the right of each row and below each column, this displays the
   digits still missing from that row/column -- a live version of the
   row/column tracking sets from sudoku_solver.py's build_tracking_sets().
   A "Solve" button runs the full solver (naked singles + backtracking)
   and fills in everything beyond what you've entered. A "Reset"
   button clears your guesses back to the original puzzle's clues. A
   "Save to File" button appends the current grid to Sudoku_Save.txt as
   a record "Paste Puzzle" (above) can later load back in. Ctrl+Z undoes
   your most recent guess, one step at a time, while this screen is showing.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from sudoku_solver import (
    sample_puzzle,
    build_tracking_sets,
    solve,
    box_index,
    generate_puzzle,
    rate_difficulty,
)

__version__ = "1.4.0"
HELP_LAST_UPDATED = "September 2, 2026"

SAVE_FILE_NAME = "Sudoku_Save.txt"

# Caps how many backtracking guesses PuzzleEntryGUI._on_paste's
# validate-by-solving check will spend on a pasted puzzle before giving
# up and treating it as invalid -- see solve()'s max_iterations for why
# this exists (a corrupted/untrusted grid's contradiction can otherwise
# take an impractically long time to prove). 50,000 is roughly 27x what
# this app's own hardest reference puzzle (sample_puzzle, ~1,850
# guesses) has ever needed, so a genuinely valid puzzle is never at
# realistic risk of a false rejection.
PASTE_VALIDATION_MAX_ITERATIONS = 50_000

ENTRY_HINT_TEXT = "Type a digit into any square you want filled."

HELP_TEXT = f"""\
Version {__version__} -- Last updated: {HELP_LAST_UPDATED}

Author: Gil Shannon
Email: gmshannon99@gmail.com
Note: Any comments, questions, or bug reports can be sent to the email
above.

This project is open source. View the code on GitHub:
https://github.com/GMShannon99/sudoku-solver

HOW THIS APP WORKS

STARTING FROM A BLANK GRID
When the grid is blank -- either the first time the app opens, or
right after clicking "New/Clear" -- you're on the puzzle entry
screen. Type a digit into every square you want as a starting
clue and leave every other square blank (no need to type 0
anywhere). Every digit you type is checked against that cell's
row, column, and 3x3 box, exactly like the checks used later on
the solving screen -- a digit that's already used elsewhere in
that row, column, or box is rejected with a beep. Then either:
  * Click "Start Solving" to lock in whatever you typed as the
    puzzle's givens and move to the solving screen (this is the
    point where the game switches into guessing mode), or
  * Click "Use Sample Puzzle" to skip straight to the built-in
    sample puzzle instead, ignoring anything you typed, or
  * Click "Paste Puzzle" to load a puzzle you previously saved to
    Sudoku_Save.txt off the system clipboard -- see PASTING A
    SAVED PUZZLE below, or
  * Pick a difficulty (Easy, Moderate, or Hard) and click
    "Generate Puzzle" to create a brand new puzzle instead of
    typing or pasting one -- see GENERATING A NEW PUZZLE below, or
  * Click "Create New" to clear every square on this entry
    screen and start manually typing a brand new puzzle to be
    solved.

GENERATING A NEW PUZZLE
On the puzzle entry screen, next to "Use Sample Puzzle," a set of
difficulty radio buttons (Easy, Moderate, Hard) and a "Generate
Puzzle" button let you create a brand-new, randomly generated
puzzle instead of typing or pasting one in. Pick whichever
difficulty you want first, then click "Generate Puzzle" -- if you
click it without picking a difficulty, it defaults to Moderate
and generates anyway rather than making you choose. Every
generated puzzle is guaranteed to have exactly one valid
solution, the same guarantee a hand-typed or pasted puzzle only
gets once you've confirmed it yourself. Generating can take a
moment, since finding a puzzle at the right difficulty may need
several internal attempts -- a "Generating puzzle..." message
lets you know it's working. Once generation finishes, you're
taken straight to the solving screen with the new puzzle loaded,
same as clicking "Use Sample Puzzle."

PASTING A SAVED PUZZLE
"Paste Puzzle" loads a puzzle you saved earlier with "Save to File"
(see SAVING YOUR PUZZLE TO A FILE below). Open Sudoku_Save.txt,
copy exactly ONE line/record, then click "Paste Puzzle" on this
entry screen. If the clipboard holds a valid record, you're taken
straight to the solving screen with that puzzle loaded and ready
to solve -- its saved difficulty level (Easy/Moderate/Hard) comes
along with it, so the solving screen's difficulty label is correct
immediately, without needing to re-solve the puzzle first. If the
clipboard doesn't hold a single valid record (wrong length, stray
characters, more than one line copied, etc.), an error message
explains this and nothing on screen changes.

SELECTING A CELL
Click on any empty (white) cell to select it. The cell turns
yellow to show it's selected, and a set of candidate-digit
buttons appears in the lower-right corner of the window.

CANDIDATE BUTTONS
The candidate buttons show every digit that could legally go in
the cell you just selected -- that is, every digit 1-9 that
isn't already used elsewhere in that cell's row, column, or 3x3
box. Click one of these buttons to fill the selected cell with
that digit.

TYPING DIRECTLY
You don't have to use the candidate buttons -- you can also just
type a digit straight into a cell. It's checked with the exact
same rule as the candidate buttons (must be missing from the
cell's row, column, and box). If you type a digit that would
break that rule, it's rejected: the cell stays blank and the
computer beeps to let you know.

ROW NUMBERS (RIGHT SIDE)
The numbers shown to the right of each row list every digit
still missing from that row. As you fill in cells, digits drop
out of this list. A row that's completely and correctly filled
shows a checkmark.

COLUMN NUMBERS (BELOW EACH COLUMN)
The numbers shown below each column work the same way, but for
that column: every digit still missing from it, updating live as
you play. A fully and correctly filled column shows a checkmark.

GIVEN CLUES VS. YOUR ENTRIES
The puzzle's starting clues are shown in gray and cannot be
changed -- these are the numbers the puzzle began with. Every
other cell is yours to fill in and stays editable until the
puzzle is solved.

UNDO (CTRL+Z)
While on the solving screen, pressing Ctrl+Z undoes your most
recent entry, one step at a time -- each press steps back one more
guess, however many you've made. It has no effect once there's
nothing left to undo (no error, nothing happens), and it only
works on the solving screen: it has no effect back on the puzzle
entry screen. This is separate from Save/Reset below -- Ctrl+Z
tracks every entry automatically as you make it, while Save/Reset
are manual snapshots you take yourself.

SAVING YOUR PUZZLE TO A FILE
"Save to File" appends the current grid (givens plus whatever
you've typed in so far) as a new record to a file named
Sudoku_Save.txt, created in the same folder as the app itself.
Every click adds ANOTHER record -- it never overwrites what's
already in the file, so saves from different sessions all pile up
as separate lines. Each record is 82 characters: 81 characters for
the grid itself (row by row, 9 characters per row, each one either
the digit 1-9 for a filled cell or 0 for an empty cell), followed
by one final letter giving the puzzle's difficulty -- E for Easy,
M for Moderate, or H for Hard. See PASTING A SAVED PUZZLE above for
how to load a record back in.

THE BUTTONS
  Save         -- Takes a snapshot backup of the grid exactly as it
                  looks right now (givens plus whatever you've typed
                  in so far). You can save as many times as you like;
                  each Save adds another backup. This is an in-memory
                  backup only -- it's lost when the app closes; see
                  Save to File below for a backup that persists.
  Save to File -- Appends the current grid to Sudoku_Save.txt as a
                  new record -- see SAVING YOUR PUZZLE TO A FILE above.
  Solve        -- Runs the full solver and fills in every remaining
                  empty cell to complete the puzzle.
  Reset        -- Restores the most recently saved backup. If you've
                  never clicked Save, this instead clears the grid
                  back to the original puzzle's clues.
  Help         -- Opens this help window.
  New/Clear    -- After asking you to confirm, discards the current
                  puzzle and every saved backup and takes you back to
                  the blank puzzle entry screen described above, so
                  you can start over with a brand new puzzle.
"""


def _app_directory():
    """
    Directory Sudoku_Save.txt is read from and appended to: the folder
    containing the running script, OR -- when PyInstaller has packaged
    this into a onefile .exe -- the folder containing that .exe itself.
    sys.frozen is the flag PyInstaller sets on a packaged build; without
    checking it, __file__ inside a frozen build would resolve to
    PyInstaller's internal temp extraction folder instead of wherever
    the person actually put the .exe, which isn't what "the same folder
    as the running script/exe" means from the person's point of view.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _parse_save_record(text):
    """
    Validates and parses a single pasted puzzle record: 81 grid digits
    (0-9, row by row, 9 per row), OPTIONALLY followed by one more
    character in position 82. A single trailing newline (as every line
    in Sudoku_Save.txt has) is tolerated; more than one line of actual
    content is rejected.

    That optional 82nd character -- the difficulty letter
    SudokuGUI._on_save_to_file writes (E/M/H) -- is NOT validated here
    at all, and its value is completely ignored: it's purely
    informational, since PuzzleEntryGUI._on_paste independently
    re-validates and re-rates every pasted puzzle by actually solving
    it. Any character in that position is accepted, including a space
    or something else entirely, and a record with no 82nd character at
    all (exactly 81 characters) is equally valid.

    Rejected only if:
      * the length isn't exactly 81 or 82 characters, or
      * any of the first 81 characters isn't a digit 0-9.

    Note this deliberately does NOT call .strip() on the chosen line:
    stripping happens to be harmless now that position 82 isn't
    validated, but avoiding it keeps length-checking exact rather than
    dependent on whatever whitespace .strip() would remove.

    Returns the parsed 9x9 grid on success, or None if text isn't
    exactly one valid record.
    """
    if not text:
        return None

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        return None
    record = lines[0]

    if len(record) not in (81, 82):
        return None

    grid_digits = record[:81]
    if not grid_digits.isdigit():
        return None

    grid = [[0] * 9 for _ in range(9)]
    for i, ch in enumerate(grid_digits):
        grid[i // 9][i % 9] = int(ch)
    return grid


def _clear_window(root):
    """
    Destroys every widget currently in root. Must be called before
    building either screen's widgets on top of it -- otherwise the old
    screen's Label/Button widgets stay alive in the same grid cells as
    the new screen's, producing overlapping title text and leftover
    buttons whose callbacks still fire (and, in PuzzleEntryGUI's case,
    can end the whole app via its "Start Solving" button's quit()).
    """
    for widget in root.winfo_children():
        widget.destroy()


def _show_help_window(root):
    """
    Opens a separate, non-modal Toplevel window with a plain-language
    explanation of how the app works. Toplevel (rather than reusing
    root) means this window has its own lifecycle -- closing it via
    its Close button or its own X button just destroys that window,
    leaving the screen that opened it completely untouched and still
    interactive. Shared by both PuzzleEntryGUI and SudokuGUI's Help
    buttons so the two screens can't drift out of sync with each other.
    """
    doc_window = tk.Toplevel(root)
    doc_window.title("How This App Works")
    doc_window.geometry("560x600")
    doc_window.config(bg="black")

    text_widget = tk.Text(
        doc_window,
        wrap="word",
        font=("Arial", 11),
        padx=12,
        pady=12,
        bg="black",
        fg="white",
        insertbackground="white",
    )
    text_widget.grid(row=0, column=0, sticky="nsew")
    doc_window.grid_rowconfigure(0, weight=1)
    doc_window.grid_columnconfigure(0, weight=1)

    scrollbar = tk.Scrollbar(doc_window, command=text_widget.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.insert("1.0", HELP_TEXT)
    text_widget.config(state="disabled")

    tk.Button(
        doc_window,
        text="Close",
        command=doc_window.destroy,
        bg="white",
        fg="black",
        activebackground="#dddddd",
        activeforeground="black",
    ).grid(row=1, column=0, columnspan=2, pady=8)


class SudokuGUI:
    def __init__(self, root, puzzle, reiteration_count=0, solution=None):
        self.root = root
        self.puzzle = puzzle  # the original puzzle, used for Reset and for
                               # knowing which cells are locked "givens"
        self.reiteration_count = reiteration_count  # backtracking guesses
                                                      # the solver needed for
                                                      # the ORIGINAL puzzle,
                                                      # computed silently
                                                      # back on the entry
                                                      # screen (see
                                                      # PuzzleEntryGUI._on_start
                                                      # / _on_sample)
        self.solution = solution  # the solver's fully-solved grid for this
                                   # puzzle, computed silently on the entry
                                   # screen alongside reiteration_count above.
                                   # Compared against whatever grid the person
                                   # manually fills in -- see _on_cell_edit --
                                   # to detect puzzles with multiple solutions.
        self.given_cells = {
            (r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0
        }
        self.entries = {}
        self.row_labels = []
        self.col_labels = []
        self.backup_stack = []  # each entry: a full 9x9 grid snapshot,
                                 # saved via the Save button, most recent last
        self.undo_stack = []  # each entry: a full 9x9 grid snapshot taken
                               # from just BEFORE a successful guess -- see
                               # _push_undo_snapshot/_on_undo. Deliberately
                               # separate from backup_stack above: this one
                               # is filled automatically on every guess,
                               # rather than only when Save is clicked.
        self.last_known_grid = None  # the grid as of the last successful
                                      # guess (or, before any guesses, the
                                      # grid _build_grid() just built) --
                                      # see _push_undo_snapshot
        self.selected_cell = None  # (row, col) of the cell currently
                                    # highlighted for candidate-picking, or
                                    # None if nothing is selected
        self.candidate_buttons = []  # the small digit Button widgets
                                      # currently shown for selected_cell
        self.default_entry_bg = None  # captured from the first editable
                                       # Entry, used to un-highlight cells

        self._build_difficulty_label()
        self._build_title()
        self._build_grid()
        self.last_known_grid = self._read_grid()
        self._build_side_labels()
        self._build_buttons()
        self._build_candidate_area()
        self._update_candidates()
        self._bind_undo()

    def _build_difficulty_label(self):
        """Displays a small-font "Difficulty Level: ..." line directly
        above the main title, derived from self.reiteration_count (the
        backtracking-guess count computed for this puzzle back on the
        entry screen -- see PuzzleEntryGUI._on_start / _on_sample). More
        backtracking guesses means the naked-singles pass alone couldn't
        crack it, so a higher count is treated as a harder puzzle:
          0 guesses      -> Easy
          1-39 guesses   -> Moderate
          40+ guesses    -> Hard
        (see sudoku_solver.rate_difficulty, the single source of truth
        for these thresholds -- generate_puzzle() uses the exact same
        function to rate a generated puzzle's difficulty). Lives
        directly in root's grid (same as title_label) so it gets torn
        down along with everything else on New/Clear's _clear_window()
        call, and recomputed fresh the next time a puzzle is started."""
        difficulty = rate_difficulty(self.reiteration_count)

        difficulty_label = tk.Label(
            self.root, text=f"Difficulty Level: {difficulty}", font=("Arial", 10)
        )
        difficulty_label.grid(row=0, column=0, pady=(10, 0))

    def _build_title(self):
        """Displays the puzzle name, directly below the
        difficulty label at the top of the window, above the grid."""
        title_label = tk.Label(
            self.root, text=f"Sudoku Solver v{__version__}", font=("Arial", 14, "bold")
        )
        title_label.grid(row=1, column=0, pady=(0, 0))
 
    def _build_grid(self):
        """Creates the 9x9 grid of Entry widgets, PLUS a 10th column
        (for row-missing labels) and a 10th row (for column-missing
        labels), all inside the SAME frame using the SAME grid layout
        manager. This is what forces the labels to line up exactly
        with their row/column -- putting them in a separate frame (as
        an earlier version of this file did) left their spacing
        unrelated to the grid's spacing, so they drifted out of line."""
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=2, column=0, padx=10, pady=10)

        for r in range(9):
            for c in range(9):
                # Extra spacing every 3rd row/column visually separates
                # the 3x3 boxes, same idea as the "-" and "|" dividers
                # used in the terminal version's display_grid().
                padx = (8 if c % 3 == 0 and c != 0 else 1, 1)
                pady = (8 if r % 3 == 0 and r != 0 else 1, 1)
 
                entry = tk.Entry(
                    self.grid_frame, width=2, font=("Arial", 18), justify="center"
                )
                entry.grid(row=r, column=c, padx=padx, pady=pady)
 
                val = self.puzzle[r][c]
                if val != 0:
                    # Given cell: pre-filled, locked, visually distinct.
                    entry.insert(0, str(val))
                    entry.config(
                        state="disabled",
                        disabledforeground="black",
                        disabledbackground="#dddddd",
                    )
                else:
                    # Empty cell: editable. Recompute candidates on every
                    # keystroke so the side labels stay live.
                    entry.bind(
                        "<KeyRelease>",
                        lambda event, row=r, col=c: self._on_cell_edit(row, col),
                    )
                    # Click-to-see-candidates: <Button-1> fires on every
                    # click regardless of whether the cell already has
                    # focus, unlike <FocusIn> (which only fires the first
                    # time), so re-clicking an already-focused cell still
                    # re-shows its candidates.
                    entry.bind(
                        "<Button-1>",
                        lambda event, row=r, col=c: self._on_cell_click(row, col),
                    )
                    if self.default_entry_bg is None:
                        self.default_entry_bg = entry.cget("bg")
 
                self.entries[(r, c)] = entry
 
    def _build_side_labels(self):
        """Creates the row-missing labels in column 9 (immediately to
        the right of the grid) and the column-missing labels in row 9
        (immediately below the grid) -- all still inside grid_frame,
        using the SAME padx/pady rules as the matching row/column of
        entry cells, so every label sits vertically or horizontally
        centered on exactly the row/column it describes."""
        self.row_labels = []
        for r in range(9):
            pady = (8 if r % 3 == 0 and r != 0 else 1, 1)
            lbl = tk.Label(
                self.grid_frame, text="", font=("Arial", 12), anchor="w", width=10
            )
            lbl.grid(row=r, column=9, padx=(12, 0), pady=pady, sticky="w")
            self.row_labels.append(lbl)
 
        self.col_labels = []
        for c in range(9):
            padx = (8 if c % 3 == 0 and c != 0 else 1, 1)
            lbl = tk.Label(self.grid_frame, text="", font=("Arial", 10), justify="center")
            lbl.grid(row=9, column=c, padx=padx, pady=(12, 0))
            self.col_labels.append(lbl)
 
    def _build_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=0, pady=10)

        tk.Button(button_frame, text="Save", command=self._on_save).grid(
            row=0, column=0, padx=5
        )
        tk.Button(
            button_frame, text="Save to File", command=self._on_save_to_file
        ).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Solve", command=self._on_solve).grid(
            row=0, column=2, padx=5
        )
        tk.Button(button_frame, text="Reset", command=self._on_reset).grid(
            row=0, column=3, padx=5
        )
        tk.Button(button_frame, text="Help", command=self._on_help).grid(
            row=0, column=4, padx=5
        )
        tk.Button(
            button_frame, text="New/Clear", command=self._on_new_clear
        ).grid(row=0, column=5, padx=5)

        self.status_label = tk.Label(
            self.root, text=ENTRY_HINT_TEXT, font=("Arial", 10)
        )
        self.status_label.grid(row=4, column=0)

        self.backup_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.backup_label.grid(row=5, column=0)

    def _build_candidate_area(self):
        """
        A scratch area in the lower right of the WINDOW (not the grid)
        for "click a cell, see its candidates" mode: candidate-digit
        buttons for whichever cell is currently selected get drawn here.
        It lives in its own column of root's grid, spanning the same
        rows as the grid/buttons/status/backup area and bottom-aligned,
        so it never overlaps the row/column missing-digit labels (those
        live inside grid_frame itself, in grid_frame's own column 9 /
        row 9).
        """
        self.candidate_frame = tk.Frame(self.root)
        self.candidate_frame.grid(
            row=2, column=1, rowspan=4, sticky="se", padx=10, pady=10
        )

        # A persistent label (NOT one of self.candidate_buttons, so
        # _clear_candidate_buttons() never touches it) for "Reiterations:
        # N", shown once the puzzle is complete. Row 3 sits below the
        # candidate buttons' own rows (at most 3 rows for 9 digits, i//3
        # of 0-2), so it never overlaps them.
        self.reiteration_label = tk.Label(
            self.candidate_frame, text="", font=("Arial", 10, "italic")
        )
        self.reiteration_label.grid(row=3, column=0, columnspan=3, pady=(8, 0))

        # Same idea as reiteration_label, one row below it -- the two
        # are mutually exclusive (a fully-filled grid either matches
        # self.solution or it doesn't) but kept as separate widgets/rows
        # so they never fight over the same space.
        self.multiple_solutions_label = tk.Label(
            self.candidate_frame, text="", font=("Arial", 10, "italic"), fg="red"
        )
        self.multiple_solutions_label.grid(row=4, column=0, columnspan=3, pady=(4, 0))

    def _read_grid(self):
        """Reads the current state of every Entry widget into a plain
        9x9 list-of-lists grid, exactly the format sudoku_solver.py's
        functions expect. Any cell that isn't a single valid digit
        1-9 is treated as empty (0)."""
        grid = [[0] * 9 for _ in range(9)]
        for (r, c), entry in self.entries.items():
            text = entry.get().strip()
            if len(text) == 1 and text in "123456789":
                grid[r][c] = int(text)
        return grid
 
    def _on_cell_edit(self, row, col):
        """
        Runs on every keystroke in an editable cell. First narrows
        whatever was typed down to a single candidate digit (same as
        before), then VALIDATES that digit before allowing it to stay:
        it must not already be used anywhere else in this cell's row,
        column, or 3x3 box. An invalid digit is rejected outright --
        the cell is left blank and the system beeps -- rather than
        being accepted and left for the person to notice later.
 
        Note this is deliberately stricter than just "matches a
        candidate digit for this cell": it directly checks the row,
        column, and box conditions the person described, which in
        practice is the same check build_candidates() already performs
        (a digit is only ever a candidate if it clears all three).
        """
        entry = self.entries[(row, col)]
        text = entry.get()

        if len(text) > 1:
            text = text[-1]
        if text and text not in "123456789":
            text = ""

        # A leftover red status message (e.g. "No solution exists...")
        # shouldn't linger once the person starts typing again.
        self.status_label.config(text=ENTRY_HINT_TEXT, fg="black")

        if text:
            digit = int(text)

            # Validate against the REST of the grid, with this cell
            # treated as empty -- we're deciding whether to place a
            # NEW digit here, so this cell's own old value (if any)
            # shouldn't count against the new one. Same candidate
            # computation used by the click-a-candidate-button path, so
            # the two can't drift out of sync with each other.
            if digit not in self._valid_candidates(row, col):
                self.root.bell()  # audible beep on rejection
                text = ""  # reject -- leave the cell blank

        entry.delete(0, tk.END)
        if text:
            entry.insert(0, text)
            # A digit actually landed -- same end state as picking it
            # from the candidate buttons: drop the highlight and clear
            # whatever candidate buttons were on screen.
            self._clear_selection()
            self._push_undo_snapshot()

        self._update_candidates()
        self._check_grid_completion()

    def _valid_candidates(self, row, col):
        """
        The single source of truth for "what digits could legally go in
        this specific empty cell right now": digits missing from its
        row AND its column AND its box, with the cell itself treated as
        empty. Both _on_cell_edit() (typing) and the candidate buttons
        built by _show_candidates() (clicking) call this, so the two
        input paths can never disagree about what's valid.
        """
        grid = self._read_grid()
        grid[row][col] = 0
        row_missing, col_missing, box_missing = build_tracking_sets(grid)
        box = box_index(row, col)
        return sorted(row_missing[row] & col_missing[col] & box_missing[box])

    def _on_cell_click(self, row, col):
        """
        Click handler for editable cells only (given cells never get
        this binding -- see _build_grid). Selects this cell: highlights
        it yellow and shows its candidate buttons. Clicking a different
        cell than the one already selected clears the old selection
        first, so only one cell is ever highlighted/showing candidates
        at a time; re-clicking the same cell is a no-op.
        """
        if self.selected_cell == (row, col):
            return

        self._clear_selection()
        self.selected_cell = (row, col)
        self.entries[(row, col)].config(bg="yellow")
        self._show_candidates(row, col)

    def _show_candidates(self, row, col):
        """Destroys any previously-shown candidate buttons and draws a
        fresh small Button per valid candidate digit for (row, col) in
        the lower-right candidate_frame."""
        self._clear_candidate_buttons()
        for i, digit in enumerate(self._valid_candidates(row, col)):
            btn = tk.Button(
                self.candidate_frame,
                text=str(digit),
                width=2,
                font=("Arial", 12),
                bg="yellow",
                activebackground="yellow",
                command=lambda d=digit: self._on_candidate_click(d),
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.candidate_buttons.append(btn)

    def _on_candidate_click(self, digit):
        """
        Fills the selected cell with the clicked candidate digit --
        same as if it had been typed -- then converges on the same end
        state typing does: highlight removed, candidate buttons
        cleared, side labels refreshed via _update_candidates().
        """
        if self.selected_cell is None:
            return

        row, col = self.selected_cell
        entry = self.entries[(row, col)]
        entry.delete(0, tk.END)
        entry.insert(0, str(digit))

        self._clear_selection()
        self._push_undo_snapshot()
        self._update_candidates()
        self._check_grid_completion()

    def _clear_selection(self):
        """Un-highlights the currently selected cell (if any) and
        clears its candidate buttons. Safe to call when nothing is
        selected."""
        if self.selected_cell is not None:
            self.entries[self.selected_cell].config(bg=self.default_entry_bg)
            self.selected_cell = None
        self._clear_candidate_buttons()

    def _clear_candidate_buttons(self):
        """Destroys every candidate Button currently on screen, so they
        never pile up when a different cell gets selected."""
        for btn in self.candidate_buttons:
            btn.destroy()
        self.candidate_buttons = []

    def _show_reiteration_count(self):
        """Displays 'Reiterations: N' using the backtracking-guess count
        computed for the original puzzle (see self.reiteration_count).
        Called whenever the puzzle becomes fully solved -- via the Solve
        button or by the person manually filling the last empty cell."""
        self.reiteration_label.config(text=f"Reiterations: {self.reiteration_count}")

    def _clear_reiteration_count(self):
        """Hides the 'Reiterations: N' message. Called whenever Save,
        Reset, Help, or New/Clear is clicked, so the message never lingers
        past the moment that prompted it."""
        self.reiteration_label.config(text="")

    def _update_candidates(self):
        """Recomputes row/column missing-digit sets from the CURRENT
        grid (givens + whatever guesses are typed in so far) and
        refreshes every side label. A row/column showing nothing means
        it's fully and correctly filled."""
        grid = self._read_grid()
        row_missing, col_missing, _ = build_tracking_sets(grid)
 
        for r in range(9):
            digits = "".join(str(d) for d in sorted(row_missing[r]))
            self.row_labels[r].config(text=digits if digits else "✓")
 
        for c in range(9):
            digits = "\n".join(str(d) for d in sorted(col_missing[c]))
            self.col_labels[c].config(text=digits if digits else "\u2713")

    def _check_grid_completion(self):
        """
        Re-checks fullness fresh every time this is called -- from
        BOTH cell-fill paths, typing (_on_cell_edit) and clicking a
        candidate button (_on_candidate_click) -- so a stale "Multiple
        Solutions" message never lingers once the grid stops being
        fully filled, and so filling the last cell either way is
        actually detected.

        Validation upstream of both call sites already guarantees any
        filled grid is a legally completed one (every digit that
        landed passed the row/column/box check) -- but a legal
        completion isn't necessarily THE solution the solver found for
        this puzzle. Compare against it: a match means this is the
        puzzle's (unique) solution, so run the exact same logic the
        Solve button runs. A mismatch means the puzzle has more than
        one valid solution.
        """
        self._clear_multiple_solutions_message()
        grid = self._read_grid()
        if all(grid[r][c] != 0 for r in range(9) for c in range(9)):
            if grid == self.solution:
                self._on_solve()
            else:
                self._show_multiple_solutions_message()

    def _show_multiple_solutions_message(self):
        """Displays 'Multiple Solutions' in the lower-right corner
        (candidate_frame, next to reiteration_label). Shown when the
        grid becomes fully filled with a legally completed grid (every
        digit already passed the row/column/box check on entry) that
        nonetheless doesn't match self.solution -- the solver's own
        solution for this puzzle -- which means the puzzle admits more
        than one valid completion."""
        self.multiple_solutions_label.config(text="Multiple Solutions")

    def _clear_multiple_solutions_message(self):
        """Hides the 'Multiple Solutions' message. Called whenever any
        other button is pressed, so it never lingers past the moment
        that prompted it -- same pattern as _clear_reiteration_count()."""
        self.multiple_solutions_label.config(text="")
 
    def _on_save(self):
        """
        Saves a snapshot of the current grid (givens + guesses so far)
        onto the backup stack, then updates the on-screen message to
        show how many backups now exist. Each save is independent --
        saving again later adds ANOTHER snapshot on top, it doesn't
        replace the previous one.
        """
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()
        grid = self._read_grid()
        self.backup_stack.append(grid)
        self._update_backup_label()

    def _on_save_to_file(self):
        """
        Appends the puzzle's ORIGINAL GIVEN CLUES -- self.puzzle, as
        passed into this screen's constructor -- as one new record to
        Sudoku_Save.txt, in the same folder as the running script/exe
        (see _app_directory()). Deliberately reads self.puzzle here,
        NOT self._read_grid(): self.puzzle never changes after this
        screen is built (see __init__), so it always holds exactly the
        givens with every other cell at 0, regardless of whatever the
        person has since typed in or the Solve button has filled in --
        _read_grid() would capture that live solving progress instead,
        which isn't what a saved puzzle record should represent.

        Each record is 82 characters: 81 grid characters (row by row,
        '1'-'9' for a given clue or '0' for every other cell), followed
        by one difficulty letter -- E/M/H for Easy/Moderate/Hard, reusing
        self.reiteration_count's already-computed rating (the same
        value _build_difficulty_label() displays) rather than
        recalculating it. Appending -- never overwriting -- means
        multiple saves accumulate as separate lines; PuzzleEntryGUI's
        "Paste Puzzle" (_on_paste) expects to load exactly one such
        line at a time off the clipboard.
        """
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()

        record = "".join(str(self.puzzle[r][c]) for r in range(9) for c in range(9))
        record += rate_difficulty(self.reiteration_count)[0]  # E/M/H

        path = os.path.join(_app_directory(), SAVE_FILE_NAME)
        try:
            with open(path, "a", encoding="utf-8") as save_file:
                save_file.write(record + "\n")
        except OSError as err:
            self.status_label.config(text=f"Could not save to file: {err}", fg="red")
            return

        self.status_label.config(text=f"Saved to {SAVE_FILE_NAME}.", fg="green")

    def _update_backup_label(self):
        """Refreshes the '<N> screen backup(s)' message to match
        however many snapshots are currently on the stack."""
        count = len(self.backup_stack)
        if count == 0:
            self.backup_label.config(text="")
        elif count == 1:
            self.backup_label.config(text="1 screen backup")
        else:
            self.backup_label.config(text=f"{count} screen backups")
 
    def _apply_grid_to_entries(self, grid):
        """Writes a full 9x9 grid into the on-screen entry cells,
        leaving the locked given cells untouched (they never change
        after the puzzle is loaded) and only updating the editable
        guess cells."""
        for (r, c), entry in self.entries.items():
            if (r, c) not in self.given_cells:
                entry.config(state="normal")
                entry.delete(0, tk.END)
                val = grid[r][c]
                if val != 0:
                    entry.insert(0, str(val))

    def _bind_undo(self):
        """Binds Ctrl+Z to _on_undo on root. Bound fresh every time a
        SudokuGUI is constructed (see __init__) so it's only ever active
        while THIS screen is the one showing -- _on_new_clear() unbinds
        it again before tearing this screen down, so Ctrl+Z has no
        effect back on PuzzleEntryGUI."""
        self.root.bind("<Control-z>", self._on_undo)

    def _unbind_undo(self):
        """Removes the Ctrl+Z binding _bind_undo() set up. Called from
        _on_new_clear() before switching back to PuzzleEntryGUI."""
        self.root.unbind("<Control-z>")

    def _push_undo_snapshot(self):
        """
        Called whenever a guessed (non-given) cell is successfully
        filled with a valid digit -- by typing (_on_cell_edit) or by
        clicking a candidate button (_on_candidate_click). Pushes
        self.last_known_grid -- the grid as it looked just BEFORE this
        fill, captured after the previous successful fill (or, for the
        very first fill, right after this screen was built) -- onto
        undo_stack, then advances last_known_grid to the grid as it
        looks now, ready to be pushed by the NEXT fill.
        """
        self.undo_stack.append(self.last_known_grid)
        self.last_known_grid = self._read_grid()

    def _on_undo(self, event=None):
        """
        Ctrl+Z handler (see _bind_undo). Pops the most recent snapshot
        off undo_stack and restores the grid to it via
        _apply_grid_to_entries -- the same restore logic Reset uses. A
        no-op if there's nothing left to undo: no error, no popup,
        Ctrl+Z simply has no effect.
        """
        if not self.undo_stack:
            return

        grid = self.undo_stack.pop()
        self._clear_selection()
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()
        self._apply_grid_to_entries(grid)
        self.last_known_grid = grid
        self._update_candidates()
        self.status_label.config(text="Undid last entry.", fg="blue")

    def _on_solve(self):
        """Runs the full solver on the current grid (givens + any
        guesses typed in) and fills every remaining cell with the
        result. Guessed cells that turn out inconsistent with the
        given puzzle will simply be overwritten by the solver."""
        self._clear_selection()
        self._clear_multiple_solutions_message()
        grid = self._read_grid()

        solved, _ = solve(grid)
        if solved:
            for (r, c), entry in self.entries.items():
                if (r, c) not in self.given_cells:
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(grid[r][c]))
                    entry.config(state="disabled", disabledforeground="blue")
            self.status_label.config(text="Solved!", fg="green")
            self._show_reiteration_count()
            # The solved grid didn't arrive via the tracked "guess"
            # path _push_undo_snapshot() watches, so the undo history
            # built up before this Solve no longer applies to what's on
            # screen now -- clear it rather than leave it pointing at a
            # stale sequence of prior grids.
            self.undo_stack = []
            self.last_known_grid = self._read_grid()
        else:
            self.status_label.config(
                text="No solution exists for the current entries.", fg="red"
            )

        self._update_candidates()

    def _on_reset(self):
        """
        Restores the grid to the MOST RECENTLY saved backup, removing
        that backup from the stack and decrementing the on-screen
        backup count by 1. If no backups have been saved yet, there's
        nothing to restore TO, so this falls back to the original
        behavior: clearing every guess back to just the puzzle's
        original givens.
        """
        self._clear_selection()
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()
        if self.backup_stack:
            grid = self.backup_stack.pop()
            self._apply_grid_to_entries(grid)
            self._update_backup_label()
            self.status_label.config(text="Restored last saved backup.", fg="blue")
        else:
            # Nothing saved -- fall back to clearing to the puzzle's
            # original givens, same as this button did before backups
            # existed.
            for (r, c), entry in self.entries.items():
                if (r, c) not in self.given_cells:
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
            self.status_label.config(
                text="No backups saved -- cleared to puzzle.", fg="red"
            )

        # Same reasoning as _on_solve(): the grid just changed via a
        # path _push_undo_snapshot() doesn't watch, so any undo history
        # from before this Reset no longer applies.
        self.undo_stack = []
        self.last_known_grid = self._read_grid()
        self._update_candidates()

    def _on_help(self):
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()
        _show_help_window(self.root)

    def _on_new_clear(self):
        """
        Handles the "New/Clear" button. Since this throws away the
        current puzzle AND every saved backup, it first asks for
        confirmation; only a "Yes" answer proceeds. Once confirmed, it
        tears down this solving screen and rebuilds the blank
        PuzzleEntryGUI screen in the same window -- the exact same
        transition main() drives the first time the app starts (see
        _run_puzzle_entry_screen()).
        """
        self._clear_reiteration_count()
        self._clear_multiple_solutions_message()
        confirmed = messagebox.askyesno(
            "Start a New Puzzle?",
            "This will discard the current puzzle and all saved "
            "backups. Are you sure you want to continue?",
        )
        if not confirmed:
            return

        # Ctrl+Z must have no effect once we're off this screen -- see
        # _bind_undo/_unbind_undo.
        self._unbind_undo()

        puzzle, reiteration_count, solution = _run_puzzle_entry_screen(self.root)
        if puzzle is None:
            self.root.destroy()
            return

        _clear_window(self.root)
        self.root.title("Sudoku Solver")
        SudokuGUI(self.root, puzzle, reiteration_count, solution)


class PuzzleEntryGUI:
    """
    A full-window screen that looks and behaves like the main solving
    grid (SudokuGUI above), but every cell starts blank and editable --
    there's no "given vs. guess" distinction yet, because the puzzle
    itself hasn't been defined. The person types their clues directly
    into the squares they want filled and leaves the rest blank (no
    need to type 0 anywhere).
 
    This mirrors the terminal version's get_puzzle_from_terminal() in
    purpose -- get a validated starting puzzle, with a shortcut to
    skip straight to sample_puzzle -- just via clicking into a grid
    instead of typing text rows.
    """
 
    def __init__(self, root):
        self.root = root
        self.entries = {}
        self.result = None  # set once the person clicks a button below
        self.reiteration_count = 0  # backtracking guesses the solver
                                     # needed for self.result, computed
                                     # silently in _on_start/_on_sample
        self.solution = None  # the solver's fully-solved grid for
                               # self.result, also computed silently in
                               # _on_start/_on_sample -- SudokuGUI compares
                               # against this to detect multiple solutions
        self.difficulty_var = tk.StringVar(value="")  # "" until the
                                                        # person picks a
                                                        # Generate Puzzle
                                                        # radio button --
                                                        # see _on_generate

        self._build_title()
        self._build_grid()
        self._build_buttons()
 
    def _build_title(self):
        """Displays the puzzle name, at the top
        of the window above the grid."""
        self.title_label = tk.Label(
            self.root,
            text=f"Enter Your Puzzle v{__version__}",
            font=("Arial", 14, "bold"),
        )
        self.title_label.grid(row=0, column=0, pady=(10, 0))
 
    def _build_grid(self):
        """Same 9x9 layout and 3x3 box-divider spacing as SudokuGUI's
        grid, but every cell is editable from the start -- nothing is
        locked, since there are no "givens" yet."""
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=1, column=0, padx=10, pady=10)
 
        for r in range(9):
            for c in range(9):
                padx = (8 if c % 3 == 0 and c != 0 else 1, 1)
                pady = (8 if r % 3 == 0 and r != 0 else 1, 1)
 
                entry = tk.Entry(
                    self.grid_frame, width=2, font=("Arial", 18), justify="center"
                )
                entry.grid(row=r, column=c, padx=padx, pady=pady)
                entry.bind(
                    "<KeyRelease>",
                    lambda event, row=r, col=c: self._on_cell_edit(row, col),
                )
                self.entries[(r, c)] = entry
 
    def _build_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=2, column=0, pady=10)
 
        tk.Button(button_frame, text="Start Solving", command=self._on_start).grid(
            row=0, column=0, padx=5
        )
        tk.Button(
            button_frame, text="Use Sample Puzzle", command=self._on_sample
        ).grid(row=0, column=1, padx=5)
        tk.Button(
            button_frame, text="Paste Puzzle", command=self._on_paste
        ).grid(row=0, column=2, padx=5)
        tk.Button(
            button_frame, text="Create New", command=self._on_create_new
        ).grid(row=0, column=3, padx=5)
        tk.Button(
            button_frame, text="Generate Puzzle", command=self._on_generate
        ).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Help", command=self._on_help).grid(
            row=0, column=5, padx=5
        )

        # Difficulty picker for "Generate Puzzle" above -- deliberately
        # starts with NO radio button selected (difficulty_var's default
        # is ""); _on_generate treats an empty selection as "Moderate"
        # rather than blocking the click, so picking one is optional.
        difficulty_frame = tk.Frame(self.root)
        difficulty_frame.grid(row=3, column=0)
        tk.Label(
            difficulty_frame, text="Generate difficulty:", font=("Arial", 10)
        ).grid(row=0, column=0, padx=(0, 5))
        for i, level in enumerate(("Easy", "Moderate", "Hard")):
            tk.Radiobutton(
                difficulty_frame,
                text=level,
                variable=self.difficulty_var,
                value=level,
            ).grid(row=0, column=i + 1, padx=3)

        self.hint_label = tk.Label(
            self.root,
            text=ENTRY_HINT_TEXT,
            font=("Arial", 10),
        )
        self.hint_label.grid(row=4, column=0)

    def _on_cell_edit(self, row, col):
        """
        Narrows whatever was typed down to a single digit 1-9 (no 0's
        are ever allowed to sit in a cell here -- blank IS the "no
        clue" state), then VALIDATES that digit with the exact same
        row/column/box rule the solving screen's candidate buttons use
        (see SudokuGUI._valid_candidates): it must not already be
        used elsewhere in this cell's row, column, or 3x3 box among
        the OTHER clues typed so far. An invalid digit is rejected --
        the cell stays blank and the computer beeps -- so the puzzle
        you hand off to "Start Solving" can never start out broken.
        """
        self._clear_paste_error()

        entry = self.entries[(row, col)]
        text = entry.get()

        if len(text) > 1:
            text = text[-1]
        if text and text not in "123456789":
            text = ""

        if text:
            digit = int(text)
            if digit not in self._valid_candidates(row, col):
                self.root.bell()
                text = ""

        entry.delete(0, tk.END)
        if text:
            entry.insert(0, text)

    def _clear_paste_error(self):
        """
        Resets hint_label back to its normal ENTRY_HINT_TEXT/black
        state, clearing any lingering red "Pasted puzzle is not valid."
        message left by a previous failed Paste Puzzle attempt (see
        _on_paste). Called at the start of every button handler on this
        screen and on every keystroke (_on_cell_edit), so the error
        message never lingers past the moment it stopped being relevant.
        """
        self.hint_label.config(text=ENTRY_HINT_TEXT, fg="black")

    def _valid_candidates(self, row, col):
        """Same computation as SudokuGUI._valid_candidates: digits
        missing from this cell's row AND column AND box, treating the
        cell itself as empty."""
        grid = self._read_grid()
        grid[row][col] = 0
        row_missing, col_missing, box_missing = build_tracking_sets(grid)
        box = box_index(row, col)
        return sorted(row_missing[row] & col_missing[col] & box_missing[box])

    def _read_grid(self):
        """Reads the current state of every cell into a plain 9x9 grid.
        A blank cell becomes 0 (the "no clue" placeholder every solving
        function in sudoku_solver.py expects) -- the person never has
        to type 0 themselves."""
        grid = [[0] * 9 for _ in range(9)]
        for (r, c), entry in self.entries.items():
            text = entry.get().strip()
            if len(text) == 1 and text in "123456789":
                grid[r][c] = int(text)
        return grid
 
    def _on_start(self):
        self._clear_paste_error()
        grid = self._read_grid()
        filled_count = sum(1 for row in grid for value in row if value != 0)
        if filled_count <= 5:
            messagebox.showwarning(
                "Not Enough Clues", "Must enter more squares before starting."
            )
            return  # stay on this screen so more clues can be added

        self.result = grid
        # Background/silent: solve a COPY so this never touches what's
        # displayed -- used to count how many backtracking guesses (not
        # naked-singles steps) the ORIGINAL puzzle needs, AND to keep the
        # fully-solved grid itself, both for later use once SudokuGUI's
        # puzzle becomes solved.
        solution_grid = [row[:] for row in grid]
        _, self.reiteration_count = solve(solution_grid)
        self.solution = solution_grid
        self.root.quit()  # ends THIS mainloop() call; window stays open

    def _on_sample(self):
        self._clear_paste_error()
        # A shallow copy per row, so editing this grid later never
        # touches the original sample_puzzle constant.
        self.result = [row[:] for row in sample_puzzle]
        # Same silent background count/solution as _on_start, on its own
        # copy -- the "Must enter more squares" check above doesn't apply
        # here since sample_puzzle is always a valid, complete-enough
        # puzzle.
        solution_grid = [row[:] for row in self.result]
        _, self.reiteration_count = solve(solution_grid)
        self.solution = solution_grid
        self.root.quit()

    def _on_generate(self):
        """
        Reads the selected difficulty radio button -- defaulting to
        "Moderate" if none is picked, rather than blocking the click --
        and generates a brand-new puzzle at that difficulty via
        sudoku_solver.generate_puzzle(), then proceeds exactly like
        _on_sample() above: sets self.result and moves on to the
        solving screen. The minimum-clues check _on_start() does isn't
        needed here since a generated puzzle always has enough clues
        by construction.

        generate_puzzle() already computes both the backtracking-guess
        count AND the fully-solved grid for whatever puzzle it returns,
        so those are reused directly here instead of calling solve()
        again on the result.

        Shows a brief "Generating puzzle..." message first and forces
        it to actually paint (via update_idletasks) before the
        generation call blocks the UI -- generation can take a moment,
        since landing on the requested difficulty may take several
        internal attempts (see generate_puzzle's docstring).
        """
        self._clear_paste_error()
        target_difficulty = self.difficulty_var.get() or "Moderate"

        self.hint_label.config(text="Generating puzzle...", fg="black")
        self.root.update_idletasks()

        puzzle, reiteration_count, _actual_difficulty, solution = generate_puzzle(
            target_difficulty
        )

        self.result = puzzle
        self.reiteration_count = reiteration_count
        self.solution = solution
        self.root.quit()

    def _on_paste(self):
        """
        Reads the system clipboard and validates it STRUCTURALLY (see
        _parse_save_record): 81 grid digits (0-9, row by row), with an
        OPTIONAL 82nd character that's accepted no matter what it is --
        length must be exactly 81 or 82 characters, and only the first
        81 characters are actually checked. Anything else (wrong
        length, a non-digit among the first 81 characters, more than
        one line) is rejected immediately with an error dialog and
        nothing on screen changes.

        That optional 82nd character is documentation only, and never
        validated -- deliberately NOT trusted as the puzzle's actual
        difficulty. Once the record parses, this independently
        re-validates the puzzle itself by actually running solve() on
        it:
          * If solve() finds no solution (the puzzle is corrupted,
            contradictory, or was hand-edited into an invalid state),
            nothing is loaded into the grid and nothing proceeds to the
            solving screen -- instead, hint_label shows a red "Pasted
            puzzle is not valid." message (see _clear_paste_error for
            how that gets cleared again).
          * If solve() succeeds, its REAL results -- the actual
            reiteration_count, not whatever the file's trailing
            character claimed -- are what SudokuGUI's difficulty label
            ends up showing, exactly as if the puzzle had been typed in
            by hand and sent through "Start Solving".
        solve() can take a moment on a hard puzzle, so hint_label shows
        "Validating pasted puzzle..." while this runs. It's also called
        with a max_iterations cap (see sudoku_solver.solve): a
        corrupted or hand-edited grid can hide a contradiction that
        only surfaces after backtracking has exhausted a huge chunk of
        the search space, which -- unlike solving a genuinely hard but
        valid puzzle -- can take an impractically long time (this app's
        own "world's hardest sudoku"-style sample_puzzle needs under
        2,000 guesses; a contrived corrupted grid was measured taking
        tens of thousands of guesses and multiple seconds per 10,000,
        with no guarantee of ever finishing). PASTE_VALIDATION_MAX_ITERATIONS
        is set generously above any puzzle this solver has ever
        actually needed, so a real valid puzzle is never at risk of a
        false rejection, while a corrupted one can't freeze the app.
        """
        self._clear_paste_error()

        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            clipboard_text = None

        grid = _parse_save_record(clipboard_text)
        if grid is None:
            messagebox.showerror(
                "Could Not Read Puzzle",
                "The clipboard doesn't contain a valid saved puzzle "
                "record. Copy a single line of 81 grid digits (0-9), "
                "optionally followed by one more character, and try "
                "again.",
            )
            return

        self.hint_label.config(text="Validating pasted puzzle...", fg="black")
        self.root.update_idletasks()

        solution_grid = [row[:] for row in grid]
        solved, reiteration_count = solve(
            solution_grid, max_iterations=PASTE_VALIDATION_MAX_ITERATIONS
        )
        if not solved:
            self.hint_label.config(text="Pasted puzzle is not valid.", fg="red")
            return

        for (r, c), entry in self.entries.items():
            entry.delete(0, tk.END)
            if grid[r][c] != 0:
                entry.insert(0, str(grid[r][c]))

        self.result = grid
        self.solution = solution_grid
        self.reiteration_count = reiteration_count
        self.root.quit()

    def _on_create_new(self):
        """
        Clears every square on THIS entry screen back to blank, so the
        person can manually type a brand new puzzle to be solved
        without closing and reopening the app. Doesn't move to the
        solving screen -- that only happens via "Start Solving". Also
        relabels the title bar at the top of the screen to make clear
        the grid is now in manual entry mode.
        """
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self._clear_paste_error()
        self.title_label.config(text="Sudoku - Manual Enter Mode")

    def _on_help(self):
        self._clear_paste_error()
        _show_help_window(self.root)

    def on_window_closed(self):
        """Called if the person closes the window directly (the X
        button) instead of clicking a button. Leaves result as None so
        main() knows to exit quietly rather than launch the solver."""
        self.result = None
        self.root.quit()
 
 
def _run_puzzle_entry_screen(root):
    """
    Clears whatever is currently in the window and shows the blank
    PuzzleEntryGUI screen, then blocks (via a nested mainloop) until
    the person clicks "Start Solving", clicks "Use Sample Puzzle", or
    closes the window. Returns (puzzle, reiteration_count, solution) for
    the puzzle they picked, or (None, 0, None) if they closed the window
    without picking one.

    Pulled out of main() so SudokuGUI's "New/Clear" button can drive
    the exact same entry-screen transition main() uses on first
    startup, without duplicating it.
    """
    _clear_window(root)

    root.title("Enter Your Puzzle")
    entry_screen = PuzzleEntryGUI(root)
    # Override the window's own close button so it stops the mainloop
    # cleanly (via quit()) instead of destroying the window outright --
    # this lets us safely check entry_screen.result afterward.
    root.protocol("WM_DELETE_WINDOW", entry_screen.on_window_closed)
    root.mainloop()

    return entry_screen.result, entry_screen.reiteration_count, entry_screen.solution


def main():
    root = tk.Tk()

    puzzle, reiteration_count, solution = _run_puzzle_entry_screen(root)
    if puzzle is None:
        root.destroy()
        return

    _clear_window(root)
    root.title("Sudoku Solver")
    SudokuGUI(root, puzzle, reiteration_count, solution)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()