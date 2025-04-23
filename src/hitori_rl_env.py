import gym
from gym import spaces
import numpy as np
from hitori_play import HitoriGame

class HitoriEnv(gym.Env):
    def __init__(self, board_size=4):
        super(HitoriEnv, self).__init__()
        self.board_size = board_size
        self.action_space = spaces.Discrete(board_size * board_size)
        self.observation_space = spaces.Box(low=0, high=board_size, shape=(board_size, board_size), dtype=np.int32)
        self.game = None
        self.reset()

    def reset(self):
        self.game = HitoriGame(board_size=self.board_size)
        self.game._initialize_player_board()
        self.done = False
        return np.array(self.game.state, dtype=np.int32)

    def step(self, action):
        x, y = divmod(action, self.board_size)
        if self.game.player_painted_mask[x][y]:
            reward = -1  # discouraged invalid move
            return np.array(self.game.state, dtype=np.int32), reward, self.done, {}

        state, status = self.game.move(x, y)

        if status == -1:
            reward = -10  # broke rules
            self.done = True
        elif status == 1:
            reward = 100  # won
            self.done = True
        else:
            reward = 1  # valid move, still in progress

        return np.array(state, dtype=np.int32), reward, self.done, {}

    def render(self, mode='human'):
        self.game.print_state()

    def close(self):
        pass
