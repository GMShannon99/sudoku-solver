# A famous "world's hardest sudoku"-style puzzle (only 21 givens).
# Naked singles alone will NOT fully solve this one -- it's meant to stall
# out, which is exactly what we need to build and test backtracking against.
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
 
ALL_DIGITS = set(range(1, 10))
 
 
def display_grid(grid):
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
    """Box numbering: 0 = top-left, 8 = bottom-right, left-to-right, top-to-bottom."""
    return (row // 3) * 3 + (col // 3)
 
 
def build_tracking_sets(grid):
    """
    Returns three lists of sets:
      row_missing[r]  -> digits not yet placed in row r
      col_missing[c]  -> digits not yet placed in column c
      box_missing[b]  -> digits not yet placed in box b
    Each starts as {1..9} and has placed digits removed.
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
    Returns a dict: {(r, c): sorted list of candidate digits}
    Only includes empty cells. Candidate list = intersection of
    what's missing from that cell's row, column, and box.
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
    """Places val at (row, col) and removes it from the relevant tracking sets."""
    grid[row][col] = val
    row_missing[row].discard(val)
    col_missing[col].discard(val)
    box_missing[box_index(row, col)].discard(val)
 
 
def solve_naked_singles(grid):
    """
    Repeatedly scans for cells with exactly one candidate ("naked singles"),
    placing them and updating the tracking sets, until a full pass places
    nothing new.
 
    Modifies grid in place. Returns (placed_count, row_missing, col_missing,
    box_missing) so the caller can inspect what's left unsolved.
    """
    row_missing, col_missing, box_missing = build_tracking_sets(grid)
    total_placed = 0
 
    while True:
        candidates = build_candidates(grid, row_missing, col_missing, box_missing)
        placed_this_pass = 0
 
        for (row, col), options in candidates.items():
            if len(options) == 1:
                val = options[0]
                b = box_index(row, col)
                # Re-check against the LIVE sets, not just the snapshot the
                # candidates dict was built from. Placing an earlier cell
                # in this same pass may have already used up this digit
                # in a shared row/column/box, making this entry stale.
                if val in row_missing[row] and val in col_missing[col] and val in box_missing[b]:
                    place_value(grid, row_missing, col_missing, box_missing, row, col, val)
                    placed_this_pass += 1
 
        total_placed += placed_this_pass
        if placed_this_pass == 0:
            break  # no progress this pass -- stop, whether solved or stuck
 
    return total_placed, row_missing, col_missing, box_missing
 
 
def solve(grid):
    """
    Solves grid in place using naked-singles propagation followed by
    MRV-guided backtracking. Returns True if solved, False if the grid
    (or the current branch) has no valid solution.
 
    Option B design: no saved/restored tracking-set state. Every recursive
    call rebuilds row/col/box sets and candidates directly from whatever
    the grid looks like at that moment.
 
    Bookkeeping note: naked-singles propagation can fill in several cells
    as a side effect of a single guess. If that guess turns out wrong, all
    of those side-effect placements have to be undone too -- not just the
    guessed cell -- or the grid stays corrupted for the branch above. So
    each call remembers which cells were empty when it started, and wipes
    all of them back to empty before returning False.
    """
    cells_empty_on_entry = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]
 
    solve_naked_singles(grid)
 
    row_missing, col_missing, box_missing = build_tracking_sets(grid)
    candidates = build_candidates(grid, row_missing, col_missing, box_missing)
 
    # Contradiction check: an empty cell with zero valid digits means
    # some guess (this level or higher) was wrong.
    for options in candidates.values():
        if len(options) == 0:
            for row, col in cells_empty_on_entry:
                grid[row][col] = 0  # undo naked-singles fill from this call
            return False
 
    # No empty cells left with candidates -- fully solved.
    if not candidates:
        return True
 
    # MRV heuristic: guess on the cell with the fewest candidates first.
    row, col = min(candidates, key=lambda cell: len(candidates[cell]))
 
    for guess in candidates[(row, col)]:
        grid[row][col] = guess
        if solve(grid):
            return True
        # solve() already cleaned up anything IT filled before returning
        # False, so grid[row][col] is empty again here -- try next guess.
 
    # Every candidate for this cell failed -- undo this call's own
    # naked-singles fill before reporting failure upward.
    for row, col in cells_empty_on_entry:
        grid[row][col] = 0
    return False
 
 
if __name__ == "__main__":
    print("Starting grid:")
    display_grid(sample_puzzle)
 
    if solve(sample_puzzle):
        print("\nSolved!")
        display_grid(sample_puzzle)
    else:
        print("\nNo solution exists for this puzzle.")