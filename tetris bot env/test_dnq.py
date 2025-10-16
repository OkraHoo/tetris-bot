import os
import time
import pygame
pygame.init()
from stable_baselines3 import DQN
from tetris_env import TetrisEnv

MODEL_PATH = "dqn_tetris.zip"  # SB3 appends .zip when saving; adjust if you saved differently

if not os.path.exists(MODEL_PATH):
    print(f"Model file '{MODEL_PATH}' not found. Please train and save a model as '{MODEL_PATH}' or adjust the path.")
    exit(1)

model = DQN.load(MODEL_PATH)
env = TetrisEnv(render_mode="human")

obs, _ = env.reset()
done = False

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(int(action))
        env.render()

        if terminated or truncated:
            print("Game Over, Score:", info.get("score", 0))
            obs, _ = env.reset()
            time.sleep(0.1)
except KeyboardInterrupt:
    env.close()
    print("Exited cleanly.")