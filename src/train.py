from stable_baselines3 import PPO
from hitori_rl_env import HitoriEnv

env = HitoriEnv(board_size=4)
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)

# Save model
model.save("ppo_hitori")