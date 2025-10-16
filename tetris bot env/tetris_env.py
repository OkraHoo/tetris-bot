import numpy as np
import random
import pygame
import gymnasium as gym
from gymnasium import spaces
from pieces import TETROMINOS

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30  # 每格像素大小

ACTIONS = {
    0: "left",
    1: "right",
    2: "rotate",
    3: "drop"
}

COLORS = {
    0: (30, 30, 30),   # 背景
    1: (0, 255, 255),  # I
    2: (255, 255, 0),  # O
    3: (128, 0, 128),  # T
    4: (0, 255, 0),    # S
    5: (255, 0, 0),    # Z
    6: (0, 0, 255),    # J
    7: (255, 165, 0)   # L
}


class TetrisEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=np.int8)
        self.score = 0
        self.done = False
        self.screen = None
        self.clock = None

        # Gym spaces
        self.action_space = spaces.Discrete(len(ACTIONS))
        # observation contains color ids 0..7
        self.observation_space = spaces.Box(low=0, high=7, shape=(BOARD_HEIGHT, BOARD_WIDTH), dtype=np.int8)

        self.spawn_piece()

    def spawn_piece(self):
        self.current = random.choice(list(TETROMINOS.keys()))
        self.shape = np.array(TETROMINOS[self.current][0], dtype=np.int8)
        self.x, self.y = 3, 0
        self.color_id = list(TETROMINOS.keys()).index(self.current) + 1

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board.fill(0)
        self.score = 0
        self.done = False
        self.spawn_piece()
        return self.board.copy(), {}

    def get_observation(self):
        return np.copy(self.board)

    def valid(self, shape, x, y):
        for (r, c), val in np.ndenumerate(shape):
            if val:
                br, bc = y + r, x + c
                if br >= BOARD_HEIGHT or bc < 0 or bc >= BOARD_WIDTH:
                    return False
                if br >= 0 and self.board[br, bc]:
                    return False
        return True

    def place(self):
        # 放置方塊到棋盤
        for (r, c), val in np.ndenumerate(self.shape):
            if val:
                self.board[self.y + r, self.x + c] = self.color_id

        # 清理消行，但不在這裡計算 reward
        lines_cleared = self.clear_lines()
        
        # 生成新方塊
        self.spawn_piece()
        
        # 統一呼叫 reward 計算
        reward = self.get_reward(lines_cleared)
        
        # 累加分數
        self.score += reward
        return reward


    def clear_lines(self):
        full_lines = [i for i in range(BOARD_HEIGHT) if all(self.board[i])]
        for i in full_lines:
            # 上方行下移
            self.board[1:i+1] = self.board[0:i]
            self.board[0] = 0
        return len(full_lines)

    def step(self, action):
        if self.done:
            return self.board.copy(), 0, True, False, {}

        # 移動或旋轉
        if action == 0 and self.valid(self.shape, self.x - 1, self.y):
            self.x -= 1
        elif action == 1 and self.valid(self.shape, self.x + 1, self.y):
            self.x += 1
        elif action == 2:
            new_shape = np.rot90(self.shape)
            if self.valid(new_shape, self.x, self.y):
                self.shape = new_shape
        elif action == 3:  # drop
            while self.valid(self.shape, self.x, self.y + 1):
                self.y += 1
            reward = self.place()
            if not self.valid(self.shape, self.x, self.y):
                self.done = True
            return self.board.copy(), reward, self.done, False, {"score": self.score}

        # 自動下降一步
        if self.valid(self.shape, self.x, self.y + 1):
            self.y += 1
            reward = 0
        else:
            # 放置方塊並計算集中 reward
            self.place()
            lines_cleared = self.clear_lines()
            reward = self.get_reward(lines_cleared)  # <- 統一呼叫集中 reward
            if not self.valid(self.shape, self.x, self.y):
                self.done = True

        terminated = bool(self.done)
        truncated = False
        return self.board.copy(), reward, terminated, truncated, {"score": self.score}

    def render(self):
        if self.render_mode != "human":
            return
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE))
            pygame.display.set_caption("Tetris AI Debug")
            self.clock = pygame.time.Clock()

        self.screen.fill((0, 0, 0))
        board_copy = np.copy(self.board)

        # 畫目前方塊
        for (r, c), val in np.ndenumerate(self.shape):
            if val:
                br, bc = self.y + r, self.x + c
                if 0 <= br < BOARD_HEIGHT and 0 <= bc < BOARD_WIDTH:
                    board_copy[br, bc] = self.color_id

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                color = COLORS[int(board_copy[r, c])]
                rect = pygame.Rect(c * BLOCK_SIZE, r * BLOCK_SIZE,
                                   BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                pygame.draw.rect(self.screen, color, rect)

        pygame.display.flip()
        if self.clock:
            self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen:
            pygame.quit()
            self.screen = None
    def count_holes(self):
        holes = 0
        for c in range(BOARD_WIDTH):
            block_found = False
            for r in range(BOARD_HEIGHT):
                if self.board[r, c]:
                    block_found = True
                elif block_found:
                    holes += 1
        return holes

    def aggregate_height(self):
        height = 0
        for c in range(BOARD_WIDTH):
            for r in range(BOARD_HEIGHT):
                if self.board[r, c]:
                    height += (BOARD_HEIGHT - r)
                    break
        return height

    def bumpiness(self):
        heights = []
        for c in range(BOARD_WIDTH):
            for r in range(BOARD_HEIGHT):
                if self.board[r, c]:
                    heights.append(BOARD_HEIGHT - r)
                    break
            else:
                heights.append(0)
        bump = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
        return bump
    
    def get_reward(self, lines_cleared):
        reward = 0
        # 1️⃣ 消除行數獎勵
        reward += lines_cleared * 10
        # 2️⃣ 遊戲結束懲罰
        if not self.valid(self.shape, self.x, self.y):
            reward -= 20  # 堆太高導致遊戲結束
        # 3️⃣ 空洞懲罰
        reward -= self.count_holes() * 0.5
        # 4️⃣ 堆疊高度懲罰
        reward -= self.aggregate_height() * 0.1
        # 5️⃣ 表面凹凸懲罰
        reward -= self.bumpiness() * 0.2
        # 6️⃣ 可選：每一步小懲罰，避免 AI 無腦拖延
        # reward -= 0.01
        return reward
    
