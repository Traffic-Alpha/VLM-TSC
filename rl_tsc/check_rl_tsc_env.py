'''
Author: WANG Maonan
Date: 2025-06-30 20:50:57
LastEditors: WANG Maonan
Description: 测试 TSC ENV 的 state
LastEditTime: 2025-06-30 21:10:28
'''
import numpy as np

from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path

from utils.env_utils.tsc_env import TSCEnvironment
from utils.env_utils.tsc_wrapper import TSCEnvWrapper

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'), file_log_level="INFO", terminal_log_level="INFO")

def make_env(
        tls_id:str, num_seconds:int, movement_num:int,
        sumo_cfg:str, use_gui:bool,
    ):
    tsc_scenario = TSCEnvironment(
        sumo_cfg=sumo_cfg, 
        num_seconds=num_seconds,
        tls_ids=[tls_id], 
        tls_action_type='choose_next_phase',
        use_gui=use_gui,
    )
    tsc_wrapper = TSCEnvWrapper(tsc_scenario, tls_id=tls_id, movement_num=movement_num)
    return tsc_wrapper
    

if __name__ == '__main__':
    sumo_cfg = path_convert("../exp_networks/Hongkong_YMT/ymt_train.sumocfg")
    env = make_env(
        tls_id='J1',
        movement_num=6,
        num_seconds=600,
        sumo_cfg=sumo_cfg,
        use_gui=True
    )

    done = False
    eposide_reward = 0 # 累计奖励
    state = env.reset()
    while not done:
        action = np.random.randint(4) # 随机动作
        states, reward, truncated, done, info = env.step(action)
        eposide_reward += reward # 计算累计奖励
    env.close()

    print(f"累计奖励为, {eposide_reward}.")