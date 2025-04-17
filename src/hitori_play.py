import random
from collections import deque
from typing import List, Tuple


import signal
import sys

def handle_suspend(signum, frame):
    print("\n⚠️  Suspended with Ctrl+Z. Exiting cleanly...")
    sys.exit(0)

signal.signal(signal.SIGTSTP, handle_suspend)



GameState = {
    "LOST": -1,
    "IN_PROGRESS": 0,
    "WON": 1,
}

def check_rule1(board: List[List[int]]) -> bool:
    size = len(board)
    for i in range(size):
        row_seen = set()
        col_seen = set()
        for j in range(size):
            row_val = board[i][j]
            col_val = board[j][i]
            if row_val != 0:
                if row_val in row_seen:
                    return False
                row_seen.add(row_val)
            if col_val != 0:
                if col_val in col_seen:
                    return False
                col_seen.add(col_val)
    return True

def check_rule2(mask: List[List[bool]]) -> bool:
    size = len(mask)
    for x in range(size):
        for y in range(size):
            if mask[x][y]:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        if mask[nx][ny]:
                            return False
    return True

def check_rule3(board: List[List[int]]) -> bool:
    size = len(board)
    visited = [[False] * size for _ in range(size)]

    for x in range(size):
        for y in range(size):
            if board[x][y] != 0:
                start = (x, y)
                break
        else:
            continue
        break
    else:
        return False

    queue = deque([start])
    visited[start[0]][start[1]] = True

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                if not visited[nx][ny] and board[nx][ny] != 0:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    for x in range(size):
        for y in range(size):
            if board[x][y] != 0 and not visited[x][y]:
                return False
    return True

class HitoriGame:
    def __init__(self, board_size: int, seed: int = None):
        self.board_size = board_size
        self.seed = seed or random.randint(0, 9999999)
        random.seed(self.seed)

        self.solution_board = [[0] * board_size for _ in range(board_size)]
        self.solution_painted_mask = [[False] * board_size for _ in range(board_size)]
        self.player_painted_mask = [[False] * board_size for _ in range(board_size)]
        self.state = [[0] * board_size for _ in range(board_size)]

        self._generate_solution_board()
        self._initialize_player_board()
        self.status = GameState["IN_PROGRESS"]


    def _generate_solution_board(self):
        while True:
            # Step 1: initialize masks
            board = [[0] * self.board_size for _ in range(self.board_size)]
            painted = [[False] * self.board_size for _ in range(self.board_size)]

            # Step 2: randomly select non-adjacent painted cells
            num_painted = random.randint(13, 18) if self.board_size == 8 else max(1, self.board_size)
            attempts = 0
            while num_painted > 0 and attempts < 500:
                x = random.randint(0, self.board_size - 1)
                y = random.randint(0, self.board_size - 1)

                if painted[x][y]: continue
                # Check neighbors
                adjacent = False
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                        if painted[nx][ny]:
                            adjacent = True
                            break
                if adjacent: 
                    attempts += 1
                    continue

                painted[x][y] = True
                num_painted -= 1

            # Step 3: Create accumulators
            horiz_accum = [[False] * (self.board_size + 2) for _ in range(self.board_size)]
            vert_accum = [False] * (self.board_size + 2)

            success = True
            for x in range(self.board_size):
                vert_accum = [False] * (self.board_size + 2)
                total_choices = self.board_size + 1
                for y in range(self.board_size):
                    if painted[x][y]:
                        continue
                    attempts = 0
                    while attempts < 1000:
                        i = random.randint(1, self.board_size)
                        if not vert_accum[i] and not horiz_accum[y][i]:
                            board[x][y] = i
                            vert_accum[i] = True
                            horiz_accum[y][i] = True
                            break
                        attempts += 1
                    else:
                        success = False
                        break
                if not success:
                    break
            if not success:
                continue

            # Step 4: Fill painted cells with duplicates
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if painted[x][y]:
                        candidates = [board[x][j] for j in range(self.board_size) if not painted[x][j] and board[x][j] != 0]
                        candidates += [board[i][y] for i in range(self.board_size) if not painted[i][y] and board[i][y] != 0]
                        if not candidates:
                            success = False
                            break
                        board[x][y] = random.choice(candidates)
                if not success:
                    break
            if not success:
                continue

            # Step 5: Build visible board
            visible = [[0 if painted[x][y] else board[x][y] for y in range(self.board_size)] for x in range(self.board_size)]
            if check_rule2(painted) and check_rule3(visible):
                # Finalize
                self.solution_board = board
                self.solution_painted_mask = painted
                return


    def _initialize_player_board(self):
        for x in range(self.board_size):
            for y in range(self.board_size):
                self.state[x][y] = self.solution_board[x][y]

    def print_solution_with_paint(self):
        print("Full Solution (with painted cells shown as X):")
        for y in range(self.board_size):
            row = []
            for x in range(self.board_size):
                if self.solution_painted_mask[x][y]:
                    row.append("X")
                else:
                    row.append(str(self.solution_board[x][y]))
            print(" ".join(row))
        print()

        solution_visible_board = [[
            0 if self.solution_painted_mask[x][y] else self.solution_board[x][y]
            for y in range(self.board_size)
        ] for x in range(self.board_size)]

        print("Checking solution board rules:")
        print(f"Rule 1 (no duplicates): {check_rule1(solution_visible_board)}")
        print(f"Rule 2 (no adjacent painted): {check_rule2(self.solution_painted_mask)}")
        print(f"Rule 3 (connected unpainted): {check_rule3(solution_visible_board)}\n")

    def print_state(self):
        print("Current Game Board:")
        for y in range(self.board_size):
            row = []
            for x in range(self.board_size):
                row.append("X" if self.player_painted_mask[x][y] else str(self.state[x][y]))
            print(" ".join(row))
        print(f"Status: {self.status}  (−1 = lost, 0 = in progress, 1 = won)\n")

    def check_loss(self) -> Tuple[bool, List[int]]:
        """
        Check if player violates Rule 2 or Rule 3.
        Returns (True, [rule_numbers]) if any violated.
        """
        broken = []
        if not check_rule2(self.player_painted_mask):
            broken.append(2)
        if not check_rule3(self.state):
            broken.append(3)
        return (len(broken) > 0, broken)

        
    def check_win(self) -> bool:
        """Return True if the player satisfies all 3 rules."""
        return (
            check_rule1(self.state)
            and check_rule2(self.player_painted_mask)
            and check_rule3(self.state)
        )

    def move(self, x: int, y: int) -> Tuple[List[List[int]], int]:
        if self.status != GameState["IN_PROGRESS"]:
            print("Game is already over.")
            return self.state, self.status

        if self.player_painted_mask[x][y]:
            print("Cell already painted.")
            return self.state, self.status

        self.state[x][y] = 0
        self.player_painted_mask[x][y] = True

        lost, broken_rules = self.check_loss()
        if lost:
            self.status = GameState["LOST"]
            print(f"You broke Rule(s): {', '.join(map(str, broken_rules))}")
        elif self.check_win():
            self.status = GameState["WON"]

        return self.state, self.status

    def run(self):
        self.print_solution_with_paint()

        self.print_state()


        while self.status == GameState["IN_PROGRESS"]:
            try:
                x, y = map(int, input("Enter coordinates to paint (x y, 0-indexed): ").split())
                self.move(x, y)
                self.print_state()
            except Exception as e:
                print("Invalid input:", e)

        if self.status == GameState["WON"]:
            print("You won!")
        elif self.status == GameState["LOST"]:
            print("You lost!")


# Main
if __name__ == "__main__":
    size = 4 #int(input("Enter board size (e.g., 4, 5, 6): "))
    game = HitoriGame(board_size=size)
    game.run()
