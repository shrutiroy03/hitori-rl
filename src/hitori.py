import random
from collections import deque
from typing import List

class Hitori:
    def __init__(self, board_size: int, seed: int = None, debug: bool = False):
        """
        Initialize a new Hitori puzzle of given board size.
        Optionally seed the random number generator and enable debug mode.
        """
        self.board_size = board_size
        self.seed = seed or random.randint(0, 9999999)
        self.debug = debug
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        random.seed(self.seed)
        self.generate_board()

    def generate_board(self):
        """
        Generates a randomized Hitori board:
        - Places some cells as painted (represented by 0)
        - Fills others with random numbers (1..N)
        - Ensures no adjacent painted cells initially
        - Inserts duplicates in painted cells for solvability
        """
        def in_bounds(x, y):
            return 0 <= x < self.board_size and 0 <= y < self.board_size

        num_cells = self.board_size * self.board_size
        num_painted = random.randint(max(1, num_cells // 8), max(2, num_cells // 5))

        painted = 0
        painted_mask = [[False] * self.board_size for _ in range(self.board_size)]

        while painted < num_painted:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if painted_mask[x][y]:
                continue

            neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            if all(not in_bounds(nx, ny) or not painted_mask[nx][ny] for nx, ny in neighbors):
                painted_mask[x][y] = True
                painted += 1

        for x in range(self.board_size):
            used_in_col = set()
            for y in range(self.board_size):
                if not painted_mask[x][y]:
                    attempts = 0
                    while True:
                        n = random.randint(1, self.board_size)
                        if n not in used_in_col and all(self.board[i][y] != n for i in range(self.board_size)):
                            self.board[x][y] = n
                            used_in_col.add(n)
                            break
                        attempts += 1
                        if attempts > 100:
                            break

        for x in range(self.board_size):
            for y in range(self.board_size):
                if painted_mask[x][y]:
                    row_nums = [self.board[x][j] for j in range(self.board_size) if self.board[x][j] != 0]
                    col_nums = [self.board[i][y] for i in range(self.board_size) if self.board[i][y] != 0]
                    pool = row_nums + col_nums
                    if pool:
                        self.board[x][y] = random.choice(pool)
                    else:
                        self.board[x][y] = 1  # fallback
                    self.board[x][y] = 0  # mark painted

    def check_rule1(self):
        """
        Rule 1: No unpainted number (nonzero) may appear more than once in a row or column.
        """
        for i in range(self.board_size):
            seen_row = set()
            seen_col = set()
            for j in range(self.board_size):
                # Row check
                val = self.board[i][j]
                if val != 0:
                    if val in seen_row:
                        return False
                    seen_row.add(val)
                # Column check
                val = self.board[j][i]
                if val != 0:
                    if val in seen_col:
                        return False
                    seen_col.add(val)
        return True

    def check_rule2(self):
        """
        Rule 2: No painted cell (value 0) may be adjacent to another (up/down/left/right).
        """
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] == 0:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                            if self.board[nx][ny] == 0:
                                return False
        return True

    def check_rule3(self):
        """
        Rule 3: All unpainted (nonzero) cells must form a single connected group.
        Uses flood fill from one unpainted cell and checks if all others are reachable.
        """
        visited = [[False] * self.board_size for _ in range(self.board_size)]

        # Find first unpainted cell
        found = False
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] != 0:
                    start = (x, y)
                    found = True
                    break
            if found:
                break
        if not found:
            return False

        queue = deque([start])
        visited[start[0]][start[1]] = True

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if not visited[nx][ny] and self.board[nx][ny] != 0:
                        visited[nx][ny] = True
                        queue.append((nx, ny))

        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] != 0 and not visited[x][y]:
                    return False
        return True

    def print_board(self):
        """
        Print the board to the terminal, using 'X' for painted cells.
        """
        for y in range(self.board_size):
            row = []
            for x in range(self.board_size):
                row.append("X" if self.board[x][y] == 0 else str(self.board[x][y]))
            print(" ".join(row))
        print()

if __name__ == "__main__":
    size = 4
    game = Hitori(board_size=size, debug=True)
    game.print_board()

    print("Rule 1 (no repeats in rows/cols):", game.check_rule1())
    print("Rule 2 (no adjacent painted):", game.check_rule2())
    print("Rule 3 (connectivity):", game.check_rule3())
