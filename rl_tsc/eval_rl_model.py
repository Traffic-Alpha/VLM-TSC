'''
Author: Maonan Wang
Date: 2025-01-15 17:26:22
Description: 测试 RL 的模型, 可视化 & 输出 tripinfo
+ Command Example: MAP=France_Massy SCENE=easy_high_density_none python eval_rl_model.py
LastEditTime: 2025-08-08 13:20:51
LastEditors: WANG Maonan
'''
import torch
import hydra
from omegaconf import DictConfig, OmegaConf
from loguru import logger
from tshub.utils.get_abs_path import get_abs_path

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize, SubprocVecEnv

from utils.env_utils.make_tsc_env import make_env

path_convert = get_abs_path(__file__)
logger.remove()

@hydra.main(
    config_path=path_convert("../exp_networks/_config/"), # 配置文件所在的文件夹
    config_name="selector"
)
def main(cfg: DictConfig):
    OmegaConf.resolve(cfg) # 解析 cfg
    print(f"Running on map: {cfg.map}")
    print(f"Using scene: {cfg.scene}")
    # 读取场景配置
    SCENARIO_IDX = f"{cfg.map}_{cfg.scene}" # 场景 id
    # base
    SCENARIO_NAME = cfg.SCENARIO_NAME
    JUNCTION_NAME = cfg.JUNCTION_NAME
    NUM_SECONDS = cfg.NUM_SECONDS # 仿真时间
    PHASE_NUMBER = cfg.PHASE_NUMBER # 绿灯相位数量
    MOVEMENT_NUMBER = cfg.MOVEMENT_NUMBER # 有效 movement 的数量
    # networks & sumocfg
    SUMOCFG = cfg.SUMOCFG

    # #########
    # Init Env
    # #########
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}")
    trip_info = path_convert(f"./{SCENARIO_IDX}_tripinfo.out.xml") # 保存 TripInfo 在当前目录下
    base_model_path = path_convert(f'./{SCENARIO_IDX}_models/')
    params = {
        'tls_id':JUNCTION_NAME,
        'num_seconds':NUM_SECONDS,
        'phase_num': PHASE_NUMBER,
        'movement_num': MOVEMENT_NUMBER,
        'sumo_cfg':sumo_cfg,
        'use_gui':True,
        'trip_info': trip_info, # 车辆统计信息
        'log_file':path_convert('./log/'),
    }
    env = SubprocVecEnv([make_env(env_index=f'{i}', **params) for i in range(1)])
    env = VecNormalize.load(load_path=f"{base_model_path}/last_vec_normalize.pkl", venv=env)
    env.training = False # 测试的时候不要更新
    env.norm_reward = False

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
    model = PPO.load(f"{base_model_path}/last_rl_model.zip", env=env, device=device)

    # 使用模型进行测试
    obs = env.reset()
    dones = False # 默认是 False
    total_reward = 0

    while not dones:
        action, _ = model.predict(obs, deterministic=True)
        obs, rewards, dones, infos = env.step(action)
        total_reward += rewards
        
    env.close()
    print(f'累积奖励为, {total_reward}.')

if __name__ == '__main__':
    main()