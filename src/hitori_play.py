import numpy as np
from collections import deque
import random
import sys
import signal

GameState = {
    "LOST": -1,
    "IN_PROGRESS": 0,
    "WON": 1,
}

def handle_suspend(signum, frame):
    print("\n Suspended with Ctrl+Z. Exiting cleanly...")
    sys.exit(0)

signal.signal(signal.SIGTSTP, handle_suspend)

def check_rule1(board: np.ndarray) -> bool:
    for i in range(board.shape[0]):
        row_vals = board[i][board[i] != 0]
        col_vals = board[:, i][board[:, i] != 0]
        if len(np.unique(row_vals)) != len(row_vals):
            return False
        if len(np.unique(col_vals)) != len(col_vals):
            return False
    return True

def check_rule2(mask: np.ndarray) -> bool:
    size = mask.shape[0]
    for x in range(size):
        for y in range(size):
            if mask[x, y]:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size and mask[nx, ny]:
                        return False
    return True

def check_rule3(board: np.ndarray) -> bool:
    size = board.shape[0]
    visited = np.zeros((size, size), dtype=bool)
    starts = np.argwhere(board != 0)
    if starts.size == 0:
        return False
    start = tuple(starts[0])
    queue = deque([start])
    visited[start] = True
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                if not visited[nx, ny] and board[nx, ny] != 0:
                    visited[nx, ny] = True
                    queue.append((nx, ny))
    return np.all((board == 0) | visited)

class HitoriGame:
    def __init__(self, board_size: int, seed: int = None):
        self.board_size = board_size
        self.seed = seed or random.randint(0, 9999999)
        random.seed(self.seed)
        self.solution_board = np.zeros((board_size, board_size), dtype=int)
        self.solution_painted_mask = np.zeros((board_size, board_size), dtype=bool)
        self.player_painted_mask = np.zeros((board_size, board_size), dtype=bool)
        self.state = np.zeros((board_size, board_size), dtype=int)
        self._generate_solution_board()
        self._initialize_player_board()
        self.status = GameState["IN_PROGRESS"]

    def _generate_solution_board(self):
        while True:
            board = np.zeros((self.board_size, self.board_size), dtype=int)
            painted = np.zeros((self.board_size, self.board_size), dtype=bool)
            num_painted = random.randint(13, 18) if self.board_size == 8 else max(1, self.board_size)
            attempts = 0
            while num_painted > 0 and attempts < 500:
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if painted[x, y]: continue
                adjacent = any(
                    0 <= x+dx < self.board_size and 0 <= y+dy < self.board_size and painted[x+dx, y+dy]
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
                )
                if adjacent:
                    attempts += 1
                    continue
                painted[x, y] = True
                num_painted -= 1

            horiz_accum = np.zeros((self.board_size, self.board_size + 2), dtype=bool)
            success = True
            for x in range(self.board_size):
                vert_accum = np.zeros(self.board_size + 2, dtype=bool)
                for y in range(self.board_size):
                    if painted[x, y]:
                        continue
                    for _ in range(1000):
                        i = random.randint(1, self.board_size)
                        if not vert_accum[i] and not horiz_accum[y, i]:
                            board[x, y] = i
                            vert_accum[i] = True
                            horiz_accum[y, i] = True
                            break
                    else:
                        success = False
                        break
                if not success:
                    break
            if not success:
                continue
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if painted[x, y]:
                        candidates = np.concatenate([
                            board[x][~painted[x] & (board[x] != 0)],
                            board[:, y][~painted[:, y] & (board[:, y] != 0)]
                        ])
                        if len(candidates) == 0:
                            success = False
                            break
                        board[x, y] = np.random.choice(candidates)
                if not success:
                    break
            if not success:
                continue
            visible = np.where(painted, 0, board)
            if check_rule2(painted) and check_rule3(visible):
                self.solution_board = board
                self.solution_painted_mask = painted
                return

    def _initialize_player_board(self):
        self.state = self.solution_board.copy()

    def print_solution_with_paint(self):
        print("Full Solution (with painted cells shown as X):")
        for y in range(self.board_size):
            row = ["X" if self.solution_painted_mask[x, y] else str(self.solution_board[x, y]) for x in range(self.board_size)]
            print(" ".join(row))
        visible = np.where(self.solution_painted_mask, 0, self.solution_board)
        print("\nChecking solution board rules:")
        print(f"Rule 1 (no duplicates): {check_rule1(visible)}")
        print(f"Rule 2 (no adjacent painted): {check_rule2(self.solution_painted_mask)}")
        print(f"Rule 3 (connected unpainted): {check_rule3(visible)}\n")

    def print_state(self):
        print("Current Game Board:")
        for y in range(self.board_size):
            row = ["X" if self.player_painted_mask[x, y] else str(self.state[x, y]) for x in range(self.board_size)]
            print(" ".join(row))
        print(f"Status: {self.status}  (−1 = lost, 0 = in progress, 1 = won)\n")

    def check_loss(self):
        broken = []
        if not check_rule2(self.player_painted_mask):
            broken.append(2)
        if not check_rule3(self.state):
            broken.append(3)
        return (len(broken) > 0, broken)

    def check_win(self) -> bool:
        return (
            check_rule1(self.state)
            and check_rule2(self.player_painted_mask)
            and check_rule3(self.state)
        )

    def move(self, x: int, y: int):
        if self.status != GameState["IN_PROGRESS"]:
            print("Game is already over.")
            return self.state, self.status
        if self.player_painted_mask[x, y]:
            print("Cell already painted.")
            return self.state, self.status
        self.state[x, y] = 0
        self.player_painted_mask[x, y] = True
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
        print("You won!" if self.status == GameState["WON"] else "You lost!")

# Main
if __name__ == "__main__":
    size = 4
    game = HitoriGame(board_size=size)
    game.run()
