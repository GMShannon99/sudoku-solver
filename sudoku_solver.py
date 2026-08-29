"""
Sudoku Solver
=============
 
Overview of the approach used in this file:
 
1. TRACKING SETS: for every row, column, and 3x3 box, keep a set of the
   digits (1-9) that are still missing from it. These start as {1..9}
   and shrink as digits get placed on the board.
 
2. CANDIDATES: for any empty cell, the digits that could legally go
   there are exactly the digits still missing from its row AND its
   column AND its box, all at once. So a cell's candidate list is the
   set intersection of those three tracking sets.
 
3. NAKED SINGLES: if a cell's candidate list ever narrows down to
   exactly one digit, that digit MUST go there -- it's the only value
   that satisfies all three constraints simultaneously. Placing it may
   shrink other cells' candidate lists too, so we keep sweeping the
   grid until a full pass places nothing new.
 
4. BACKTRACKING: naked singles alone can't crack every puzzle -- some
   puzzles never produce a single-candidate cell just from deduction.
   When that happens, we pick the emptiest-looking cell (fewest
   candidates -- the "Minimum Remaining Values" or MRV heuristic),
   guess one of its candidates, and recurse. If a guess ever leads to
   a cell with ZERO candidates (a contradiction), we undo it and try
   the next candidate. This is recursive: each guess spawns a "what if"
   branch, and a failed branch pops back out to try the next option.
"""
 
# A famous "world's hardest sudoku"-style puzzle (only 21 givens).
# Naked singles alone will NOT fully solve this one -- every empty cell
# still has 2+ candidates after propagation stalls out. That's exactly
# the case backtracking exists to handle.
sample_puzzle = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0],
]
 
# The full set of legal Sudoku digits. Used as the starting point for
# every row/column/box tracking set, before any digits get removed.
ALL_DIGITS = set(range(1, 10))
 
 
def display_grid(grid):
    """
    Prints the grid to the console as a 9x9 text grid, with '.' for
    empty cells and '|' / '-' dividers marking the 3x3 box boundaries.
 
    Read-only: never modifies grid. Kept deliberately separate from all
    solving logic below, so display concerns never tangle with solving
    concerns.
    """
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row_str = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str += "| "
            val = grid[r][c]
            row_str += (str(val) if val != 0 else ".") + " "
        print(row_str)
 
 
def box_index(row, col):
    """
    Converts a (row, col) position into a box number from 0-8.
 
    Boxes are numbered left-to-right, top-to-bottom:
        0 1 2
        3 4 5
        6 7 8
    (box 0 = top-left 3x3 square, box 8 = bottom-right.)
 
    The math: row // 3 tells us which "band" of 3 rows we're in (0, 1,
    or 2), and multiplying by 3 converts that into the box number of
    the leftmost box in that band. col // 3 tells us which box within
    that band (0, 1, or 2), and adding it slides us to the right box.
    Example: row=4, col=7 -> row//3=1, col//3=2 -> box (1*3)+2 = 5.
    """
    return (row // 3) * 3 + (col // 3)
 
 
def build_tracking_sets(grid):
    """
    Builds fresh row/column/box tracking sets by scanning the ENTIRE
    grid from scratch. Nothing is remembered between calls -- every
    call recomputes everything directly from whatever digits currently
    sit in grid.
 
    Returns three lists of 9 sets each:
      row_missing[r]  -> digits (1-9) not yet placed anywhere in row r
      col_missing[c]  -> digits (1-9) not yet placed anywhere in col c
      box_missing[b]  -> digits (1-9) not yet placed anywhere in box b
 
    Each set starts as a full copy of ALL_DIGITS ({1..9}), and any
    digit already sitting in the grid gets removed (discarded) from
    the relevant row/column/box set.
    """
    row_missing = [ALL_DIGITS.copy() for _ in range(9)]
    col_missing = [ALL_DIGITS.copy() for _ in range(9)]
    box_missing = [ALL_DIGITS.copy() for _ in range(9)]
 
    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if val != 0:
                row_missing[r].discard(val)
                col_missing[c].discard(val)
                box_missing[box_index(r, c)].discard(val)
 
    return row_missing, col_missing, box_missing
 
 
def build_candidates(grid, row_missing, col_missing, box_missing):
    """
    Computes the candidate list for every EMPTY cell in the grid.
 
    A cell's candidates are the digits that could legally be placed
    there -- which is exactly the set intersection of what's still
    missing from its row, its column, and its box. (A digit can only
    go in a cell if it isn't already used anywhere in any of those
    three groups.)
 
    Returns a dict: {(row, col): sorted list of candidate digits}.
    Filled-in cells are not included in the returned dict at all.
    """
    candidates = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                b = box_index(r, c)
                options = row_missing[r] & col_missing[c] & box_missing[b]
                candidates[(r, c)] = sorted(options)
    return candidates
 
 
def place_value(grid, row_missing, col_missing, box_missing, row, col, val):
    """
    Places val at (row, col) on the grid, and keeps the tracking sets
    in sync by removing val from that row's, column's, and box's
    missing-digit sets.
 
    This bundling matters: every time a digit gets placed anywhere in
    this file, it MUST go through this function (not a bare
    grid[row][col] = val) so the tracking sets never drift out of sync
    with what's actually on the board.
    """
    grid[row][col] = val
    row_missing[row].discard(val)
    col_missing[col].discard(val)
    box_missing[box_index(row, col)].discard(val)
 
 
def solve_naked_singles(grid):
    """
    Repeatedly sweeps the grid placing "naked singles" -- cells whose
    candidate list has narrowed down to exactly one legal digit -- and
    stops once a full sweep places nothing new.
 
    Modifies grid in place. Returns (total_placed, row_missing,
    col_missing, box_missing): the count of cells placed this call,
    plus the final tracking sets, so a caller can inspect what (if
    anything) is left unsolved without recomputing from scratch.
 
    --- Why this needs to be more careful than "loop and place every
    single-candidate cell" ---
 
    A naive version would build ONE candidates snapshot, then walk
    through it placing every cell that has exactly one candidate. But
    that snapshot can go stale mid-pass: imagine two cells in the SAME
    row that each, independently, still show only one candidate: the
    digit 8. Before either gets placed, that looks like two legitimate
    naked singles. But a Sudoku row can only contain one 8 -- so at
    most one of those placements can actually be correct. If we blindly
    placed both from the stale snapshot, we'd put two 8's in one row,
    silently corrupting the grid without either function complaining
    (discard() doesn't error on removing something already removed).
 
    The fix: after building the snapshot for this pass, re-check EACH
    candidate against the LIVE row_missing/col_missing/box_missing
    sets (which place_value updates immediately as we go) right before
    placing it. If an earlier placement in this same pass already used
    up that digit in a shared row/column/box, the live check catches
    it and we skip that stale entry -- it'll either resolve correctly
    or get re-evaluated safely on the next full pass.
    """
    row_missing, col_missing, box_missing = build_tracking_sets(grid)
    total_placed = 0
 
    while True:
        # Snapshot every empty cell's candidates as they look RIGHT NOW,
        # at the start of this pass.
        candidates = build_candidates(grid, row_missing, col_missing, box_missing)
        placed_this_pass = 0
 
        for (row, col), options in candidates.items():
            if len(options) == 1:
                val = options[0]
                b = box_index(row, col)
                # Live re-check (see docstring above for why this is
                # required, not optional): only place this value if it's
                # STILL actually missing from the row, column, and box
                # at THIS moment -- not just at snapshot time.
                if val in row_missing[row] and val in col_missing[col] and val in box_missing[b]:
                    place_value(grid, row_missing, col_missing, box_missing, row, col, val)
                    placed_this_pass += 1
 
        total_placed += placed_this_pass
 
        # Stopping condition: a full pass that places zero new cells
        # means we've deduced everything pure logic can get us here --
        # either the grid is fully solved, or it's genuinely stuck and
        # needs backtracking (solve() below decides which).
        if placed_this_pass == 0:
            break
 
    return total_placed, row_missing, col_missing, box_missing
 
 
def solve(grid):
    """
    Fully solves grid in place, combining naked-singles propagation
    with MRV-guided recursive backtracking. Returns True if a solution
    was found (grid now holds it), or False if no solution exists for
    the current state of grid.
 
    --- High-level recursive strategy ---
 
    Each call to solve() represents "try to finish solving the puzzle
    from whatever state the grid is currently in." It does three things
    in order:
      1. Push naked-singles deduction as far as it will go (free
         progress, no guessing required).
      2. Check whether that deduction alone finished the puzzle, or hit
         a dead end (a cell with literally zero legal digits).
      3. If neither of those, pick the cell with the fewest remaining
         candidates and try each one in turn, recursively calling
         solve() again to see if that guess leads to a full solution.
 
    Because solve() calls itself, think of it as spawning a "branch" for
    every guess: if the recursive call returns True, that branch worked
    and we're done -- return True immediately, all the way up the call
    chain. If it returns False, that whole branch was a dead end, so we
    undo the guess and try the NEXT candidate for the same cell. If
    every candidate for this cell fails, then the problem isn't this
    cell at all -- it's a wrong guess made further UP the call chain
    (by whoever called this instance of solve()) -- so this call also
    returns False, and the search continues one level up.
 
    --- Why undoing correctly matters here (this is the subtle part) ---
 
    "Undo the guess" isn't as simple as resetting one cell back to 0.
    Step 1 of this function (solve_naked_singles) can fill in SEVERAL
    cells as a side effect of a single guess -- if that guess turns out
    to be wrong, all of those side-effect placements are just as wrong
    as the guess itself, and have to be wiped out too. Leaving them
    behind would corrupt the grid for whichever branch tries next,
    since that branch would be building its candidates on top of digits
    that were never actually valid.
 
    So at the very start of each call, we snapshot which cells were
    empty when we started (cells_empty_on_entry). If this call
    ultimately fails (either immediately, from a contradiction, or
    after every guess at this level has been exhausted), we reset ALL
    of those cells back to empty before returning False. This guarantees
    each call cleans up 100% of what it did -- nothing leaks upward.
 
    This file intentionally does NOT save/restore a snapshot of the
    tracking sets themselves (row_missing/col_missing/box_missing).
    Instead, every call rebuilds those sets from scratch by scanning
    the actual grid values. This is simpler to reason about and avoids
    a whole class of bugs around sets getting out of sync -- the
    trade-off is redoing some scanning work, which is cheap at 9x9 scale.
 
    --- Worked example of the recursion ---
 
    Suppose cell (7,6) has candidates [3, 9] and is currently the
    fewest-candidates cell anywhere on the board:
      1. grid[7][6] = 3          (place the guess)
      2. solve(grid) is called again.
         - Inside that call, naked singles may resolve several more
           cells "for free" as a result of the 3 going in.
         - If that ever produces a cell with 0 candidates: this nested
           call undoes everything IT placed, and returns False.
      3. Back in the outer call: since the recursive call returned
         False, grid[7][6] is now automatically back to 0 (the nested
         call's own cleanup already did that). We move on to the next
         candidate.
      4. grid[7][6] = 9          (try the next guess)
      5. solve(grid) is called again with this new state. If THIS
         branch eventually leads to a fully solved grid, that deepest
         call returns True -- and every call above it, all the way back
         up to the very first solve() call, also returns True without
         undoing anything, since a solution was found.
    """
    # Snapshot of every cell that's currently empty, BEFORE this call
    # does anything. If this call fails, every one of these cells gets
    # reset back to 0 -- this is what makes cleanup complete rather than
    # partial (see docstring above).
    cells_empty_on_entry = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
 
    # Step 1: squeeze out all the free progress pure deduction can give us.
    solve_naked_singles(grid)
 
    # Step 2: look at what's left, freshly recomputed from the grid.
    row_missing, col_missing, box_missing = build_tracking_sets(grid)
    candidates = build_candidates(grid, row_missing, col_missing, box_missing)
 
    # Contradiction check: if ANY empty cell has zero legal digits, some
    # guess -- either the one that led to this call, or one further up
    # the recursion chain -- was wrong. This branch is a dead end.
    for options in candidates.values():
        if len(options) == 0:
            for row, col in cells_empty_on_entry:
                grid[row][col] = 0  # undo this call's naked-singles fill
            return False
 
    # No empty cells remain with candidates -- meaning no empty cells
    # remain at all. The puzzle is fully and correctly solved.
    if not candidates:
        return True
 
    # Step 3: naked singles alone wasn't enough -- time to guess.
    # MRV heuristic: always guess on the cell with the FEWEST remaining
    # candidates. Fewer options means less wasted work if this guess
    # turns out wrong, since we'll detect the contradiction sooner.
    row, col = min(candidates, key=lambda cell: len(candidates[cell]))
 
    for guess in candidates[(row, col)]:
        grid[row][col] = guess
 
        # Recurse: "assuming this guess is correct, can the rest of the
        # puzzle be solved?" This is the branching point -- everything
        # from here down happens inside this nested call.
        if solve(grid):
            return True  # this branch worked -- propagate success upward
 
        # If we reach this line, the recursive call returned False,
        # which means it already reset every cell IT filled (including
        # any naked singles it triggered) back to 0 before returning.
        # So grid[row][col] is already back to 0 here too -- we don't
        # need to reset it ourselves. We just move on and try the next
        # candidate for this same cell.
 
    # Every candidate for this cell led to a dead end. That means the
    # actual mistake lives further up the call chain, not here. Undo
    # this call's own naked-singles fill (so the caller sees a clean
    # slate) and report failure upward.
    for row, col in cells_empty_on_entry:
        grid[row][col] = 0
    return False
 
 
def parse_puzzle_rows(rows):
    """
    Converts a list of 9 raw text rows into a 9x9 grid of integers.
 
    Accepts either format per row:
      "530070000"          (9 characters, no spaces)
      "5 3 0 0 7 0 0 0 0"  (9 characters separated by spaces)
    Blank cells can be written as either '0' or '.'.
 
    Raises ValueError with a clear message if a row doesn't contain
    exactly 9 valid characters, or if there aren't exactly 9 rows.
    This lets the caller catch the error and re-prompt instead of
    crashing the program on bad input.
    """
    if len(rows) != 9:
        raise ValueError(f"Expected 9 rows, got {len(rows)}.")
 
    grid = []
    for row_num, raw_line in enumerate(rows):
        # Strip spaces so both "530070000" and "5 3 0 0 7 0 0 0 0" work.
        cleaned = raw_line.replace(" ", "")
 
        if len(cleaned) != 9:
            raise ValueError(
                f"Row {row_num + 1} has {len(cleaned)} values, expected 9: '{raw_line}'"
            )
 
        row = []
        for ch in cleaned:
            if ch in ("0", "."):
                row.append(0)
            elif ch in "123456789":
                row.append(int(ch))
            else:
                raise ValueError(
                    f"Row {row_num + 1} has an invalid character '{ch}' -- "
                    f"only digits 1-9, '0', and '.' are allowed: '{raw_line}'"
                )
        grid.append(row)
 
    return grid
 
 
def get_puzzle_from_terminal():
    """
    Prompts the person to type in a puzzle, 9 rows at a time, and
    returns a validated 9x9 grid. Keeps re-prompting on bad input
    rather than crashing, and offers a shortcut to load the built-in
    sample_puzzle instead of typing one out.
 
    Returns the parsed grid (a list of 9 lists of 9 ints).
    """
    print("Enter your Sudoku puzzle, one row at a time (9 rows total).")
    print("Use 0 or . for blank cells, e.g.:  530070000  or  5 3 0 0 7 0 0 0 0")
    print("Or just press Enter on the first row to use the built-in sample puzzle.")
    print()
 
    while True:
        rows = []
        first_line = input("Row 1: ")
 
        if first_line.strip() == "":
            print("\nUsing built-in sample puzzle.")
            # A deep-ish copy so edits made while solving never touch
            # the original sample_puzzle constant defined above.
            return [row[:] for row in sample_puzzle]
 
        rows.append(first_line)
        for i in range(2, 10):
            rows.append(input(f"Row {i}: "))
 
        try:
            return parse_puzzle_rows(rows)
        except ValueError as err:
            print(f"\nThat puzzle couldn't be read: {err}")
            print("Let's try again from the top.\n")
 
 
if __name__ == "__main__":
    sample_puzzle_grid = get_puzzle_from_terminal()
 
    print("\nStarting grid:")
    display_grid(sample_puzzle_grid)
 
    if solve(sample_puzzle_grid):
        print("\nSolved!")
        display_grid(sample_puzzle_grid)
    else:
        print("\nNo solution exists for this puzzle.")
        