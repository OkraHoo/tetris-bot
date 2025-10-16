from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from tetris_env import TetrisEnv

# 建立環境
env = TetrisEnv(render_mode=None)
check_env(env)  # ✅ 確認符合 Gym 格式

# 建立 DQN 模型
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=1e-4,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=64,
    train_freq=4,
    target_update_interval=1000,
    gamma=0.99,
    exploration_fraction=0.2,
    exploration_final_eps=0.05,
)

# 開始訓練
model.learn(total_timesteps=100000)

# 儲存模型
model.save("dqn_tetris")
env.close()
