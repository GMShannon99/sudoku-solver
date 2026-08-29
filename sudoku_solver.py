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
                place_value(grid, row_missing, col_missing, box_missing, row, col, options[0])
                placed_this_pass += 1
 
        total_placed += placed_this_pass
        if placed_this_pass == 0:
            break  # no progress this pass -- stop, whether solved or stuck
 
    return total_placed, row_missing, col_missing, box_missing
 
 
if __name__ == "__main__":
    print("Starting grid:")
    display_grid(sample_puzzle)
 
    placed, row_missing, col_missing, box_missing = solve_naked_singles(sample_puzzle)
 
    print(f"\nPlaced {placed} cells via naked singles.")
    print("Grid after naked-singles propagation:")
    display_grid(sample_puzzle)
 
    remaining = build_candidates(sample_puzzle, row_missing, col_missing, box_missing)
    if remaining:
        print(f"\n{len(remaining)} cells still unsolved -- candidates:")
        for (row, col), options in remaining.items():
            print(f"  ({row},{col}): {options}")
    else:
        print("\nSolved completely with naked singles alone!")