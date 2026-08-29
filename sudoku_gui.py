"""
Sudoku GUI
==========
 
Two screens, shown one after another in the same window:
 
1. PuzzleEntryGUI -- a blank 9x9 grid. Type your puzzle's clues
   directly into the squares you want filled; leave every other
   square blank (no need to type 0 anywhere). A "Use Sample Puzzle"
   button skips straight to the built-in sample_puzzle instead.
 
2. SudokuGUI -- the solving screen. Whatever puzzle came out of
   screen 1 appears here with those clues locked (shown in a
   different color) and every other cell open for your own guesses.
   To the right of each row and below each column, this displays the
   digits still missing from that row/column -- a live version of the
   row/column tracking sets from sudoku_solver.py's build_tracking_sets().
   A "Solve" button runs the full solver (naked singles + backtracking)
   and fills in everything beyond what you've entered. A "Reset"
   button clears your guesses back to the original puzzle's clues.
"""
 
import tkinter as tk
 
from sudoku_solver import sample_puzzle, build_tracking_sets, solve
 
 
class SudokuGUI:
    def __init__(self, root, puzzle):
        self.root = root
        self.puzzle = puzzle  # the original puzzle, used for Reset and for
                               # knowing which cells are locked "givens"
        self.given_cells = {
            (r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0
        }
        self.entries = {}
        self.row_labels = []
        self.col_labels = []
 
        self._build_grid()
        self._build_side_labels()
        self._build_buttons()
        self._update_candidates()
 
    def _build_grid(self):
        """Creates the 9x9 grid of Entry widgets, PLUS a 10th column
        (for row-missing labels) and a 10th row (for column-missing
        labels), all inside the SAME frame using the SAME grid layout
        manager. This is what forces the labels to line up exactly
        with their row/column -- putting them in a separate frame (as
        an earlier version of this file did) left their spacing
        unrelated to the grid's spacing, so they drifted out of line."""
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=0, column=0, padx=10, pady=10)
 
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
        button_frame.grid(row=1, column=0, pady=10)
 
        tk.Button(button_frame, text="Solve", command=self._on_solve).grid(
            row=0, column=0, padx=5
        )
        tk.Button(button_frame, text="Reset", command=self._on_reset).grid(
            row=0, column=1, padx=5
        )
 
        self.status_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.status_label.grid(row=2, column=0)
 
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
        """Runs on every keystroke in an editable cell: keeps only the
        most recently typed valid digit (so typing a second character
        replaces rather than appends), then refreshes the candidate
        display for the whole board."""
        entry = self.entries[(row, col)]
        text = entry.get()
 
        if len(text) > 1:
            text = text[-1]
        if text and text not in "123456789":
            text = ""
 
        entry.delete(0, tk.END)
        if text:
            entry.insert(0, text)
 
        self._update_candidates()
 
    def _update_candidates(self):
        """Recomputes row/column missing-digit sets from the CURRENT
        grid (givens + whatever guesses are typed in so far) and
        refreshes every side label. A row/column showing nothing means
        it's fully and correctly filled."""
        grid = self._read_grid()
        row_missing, col_missing, _ = build_tracking_sets(grid)
 
        for r in range(9):
            digits = "".join(str(d) for d in sorted(row_missing[r]))
            self.row_labels[r].config(text=digits if digits else "done")
 
        for c in range(9):
            digits = "\n".join(str(d) for d in sorted(col_missing[c]))
            self.col_labels[c].config(text=digits if digits else "\u2713")
 
    def _on_solve(self):
        """Runs the full solver on the current grid (givens + any
        guesses typed in) and fills every remaining cell with the
        result. Guessed cells that turn out inconsistent with the
        given puzzle will simply be overwritten by the solver."""
        grid = self._read_grid()
 
        if solve(grid):
            for (r, c), entry in self.entries.items():
                if (r, c) not in self.given_cells:
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(grid[r][c]))
                    entry.config(state="disabled", disabledforeground="blue")
            self.status_label.config(text="Solved!", fg="green")
        else:
            self.status_label.config(
                text="No solution exists for the current entries.", fg="red"
            )
 
        self._update_candidates()
 
    def _on_reset(self):
        """Clears every guessed cell back to empty, leaving only the
        original puzzle givens."""
        for (r, c), entry in self.entries.items():
            if (r, c) not in self.given_cells:
                entry.config(state="normal")
                entry.delete(0, tk.END)
 
        self.status_label.config(text="")
        self._update_candidates()
 
 
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
 
        self._build_grid()
        self._build_buttons()
 
    def _build_grid(self):
        """Same 9x9 layout and 3x3 box-divider spacing as SudokuGUI's
        grid, but every cell is editable from the start -- nothing is
        locked, since there are no "givens" yet."""
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=0, column=0, padx=10, pady=10)
 
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
        button_frame.grid(row=1, column=0, pady=10)
 
        tk.Button(button_frame, text="Start Solving", command=self._on_start).grid(
            row=0, column=0, padx=5
        )
        tk.Button(
            button_frame, text="Use Sample Puzzle", command=self._on_sample
        ).grid(row=0, column=1, padx=5)
 
        self.hint_label = tk.Label(
            self.root,
            text="Type a digit into any square you want filled -- leave the rest blank.",
            font=("Arial", 10),
        )
        self.hint_label.grid(row=2, column=0)
 
    def _on_cell_edit(self, row, col):
        """Same single-digit-only enforcement as the main solving grid:
        keeps only the most recently typed valid digit 1-9. No 0's are
        ever allowed to sit in a cell here -- blank IS the "no clue"
        state, exactly as requested."""
        entry = self.entries[(row, col)]
        text = entry.get()
 
        if len(text) > 1:
            text = text[-1]
        if text and text not in "123456789":
            text = ""
 
        entry.delete(0, tk.END)
        if text:
            entry.insert(0, text)
 
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
        self.result = self._read_grid()
        self.root.quit()  # ends THIS mainloop() call; window stays open
 
    def _on_sample(self):
        # A shallow copy per row, so editing this grid later never
        # touches the original sample_puzzle constant.
        self.result = [row[:] for row in sample_puzzle]
        self.root.quit()
 
    def on_window_closed(self):
        """Called if the person closes the window directly (the X
        button) instead of clicking a button. Leaves result as None so
        main() knows to exit quietly rather than launch the solver."""
        self.result = None
        self.root.quit()
 
 
def main():
    root = tk.Tk()
    root.title("Enter Your Puzzle")
 
    entry_screen = PuzzleEntryGUI(root)
    # Override the window's own close button so it stops the mainloop
    # cleanly (via quit()) instead of destroying the window outright --
    # this lets us safely check entry_screen.result afterward.
    root.protocol("WM_DELETE_WINDOW", entry_screen.on_window_closed)
    root.mainloop()
 
    puzzle = entry_screen.result
    if puzzle is None:
        root.destroy()
        return
 
    # Clear the entry screen's widgets and rebuild the same window as
    # the main solving grid -- reusing one window keeps this feeling
    # like a single continuous app rather than two separate popups.
    for widget in root.winfo_children():
        widget.destroy()
 
    root.title("Sudoku Solver")
    SudokuGUI(root, puzzle)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()