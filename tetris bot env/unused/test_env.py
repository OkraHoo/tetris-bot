import numpy as np
import random
import pygame
import gymnasium as gym
from gymnasium import spaces
from pieces import TETROMINOS

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 20

ACTIONS = {
    0: "left",
    1: "right",
    2: "rotate",
    3: "drop"
}

COLORS = {
    0: (30, 30, 30),
    1: (0, 255, 255),
    2: (255, 255, 0),
    3: (128, 0, 128),
    4: (0, 255, 0),
    5: (255, 0, 0),
    6: (0, 0, 255),
    7: (255, 165, 0)
}

class TetrisEnv(gym.Env):   # ✅ 改為 Gym 介面
    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
        self.score = 0
        self.done = False
        self.screen = None
        self.clock = None

        # ✅ Gym 要求的空間定義
        self.action_space = spaces.Discrete(len(ACTIONS))
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(BOARD_HEIGHT, BOARD_WIDTH), dtype=np.int8
        )

        self.spawn_piece()

    def spawn_piece(self):
        self.current = random.choice(list(TETROMINOS.keys()))
        self.shape = np.array(TETROMINOS[self.current][0])
        self.x, self.y = 3, 0
        self.color_id = list(TETROMINOS.keys()).index(self.current) + 1

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board.fill(0)
        self.score = 0
        self.done = False
        self.spawn_piece()
        obs = self.board.copy()
        return obs, {}

    def valid(self, shape, x, y):
        for (r, c), val in np.ndenumerate(shape):
            if val:
                br, bc = y + r, x + c
                if br >= BOARD_HEIGHT or bc < 0 or bc >= BOARD_WIDTH:
                    return False
                if self.board[br, bc]:
                    return False
        return True

    def place(self):
        for (r, c), val in np.ndenumerate(self.shape):
            if val:
                self.board[self.y + r, self.x + c] = 1
        lines_cleared = self.clear_lines()
        reward = 1 + lines_cleared * 10
        self.score += reward
        self.spawn_piece()
        return reward

    def clear_lines(self):
        full_lines = [i for i in range(BOARD_HEIGHT) if all(self.board[i])]
        for i in full_lines:
            self.board[1:i+1] = self.board[0:i]
            self.board[0] = 0
        return len(full_lines)

    def step(self, action):
        if self.done:
            return self.board.copy(), 0, True, False, {}

        if action == 0 and self.valid(self.shape, self.x - 1, self.y):
            self.x -= 1
        elif action == 1 and self.valid(self.shape, self.x + 1, self.y):
            self.x += 1
        elif action == 2:
            new_shape = np.rot90(self.shape)
            if self.valid(new_shape, self.x, self.y):
                self.shape = new_shape
        elif action == 3:
            while self.valid(self.shape, self.x, self.y + 1):
                self.y += 1
            reward = self.place()
            if not self.valid(self.shape, self.x, self.y):
                self.done = True
            return self.board.copy(), reward, self.done, False, {"score": self.score}

        # 自動下降
        if self.valid(self.shape, self.x, self.y + 1):
            self.y += 1
            reward = 0
        else:
            reward = self.place()
            if not self.valid(self.shape, self.x, self.y):
                self.done = True

        return self.board.copy(), reward, self.done, False, {"score": self.score}

    def render(self):
        if self.render_mode != "human":
            return
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE))
            self.clock = pygame.time.Clock()

        self.screen.fill((0, 0, 0))
        board_copy = self.board.copy()

        for (r, c), val in np.ndenumerate(self.shape):
            if val:
                br, bc = self.y + r, self.x + c
                if 0 <= br < BOARD_HEIGHT and 0 <= bc < BOARD_WIDTH:
                    board_copy[br, bc] = 1

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                color = COLORS[board_copy[r, c]]
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen:
            pygame.quit()
            self.screen = None
