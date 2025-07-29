'''
Author: Maonan Wang
Date: 2025-01-16 18:51:18
Description: 使用 RL 执行策略并收集信息
LastEditors: WANG Maonan
LastEditTime: 2025-07-29 15:56:33
'''
import os
import torch
from stable_baselines3 import PPO

from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.utils.format_dict import save_str_to_json

from utils.env_utils.make_env import make_env
from utils.rl_utils.simple_int import IntersectionNet

from CONFIG import SCENARIO_CONFIGS
 
def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))

# 读取场景配置
SCENARIO_IDX = "Beijing_Changjianglu_Event" # 可视化场景, SouthKorea_Songdo, Hongkong_YMT
config = SCENARIO_CONFIGS.get(SCENARIO_IDX) # 获取特定场景的配置
SCENARIO_NAME = config["SCENARIO_NAME"]
SUMOCFG = config["SUMOCFG"]
NETFILE = config["NETFILE"]
JUNCTION_NAME = config["JUNCTION_NAME"]
NUM_SECONDS = config["NUM_SECONDS"] # 仿真时间
CENTER_COORDINATES = config["CENTER_COORDINATES"]
PHASE_NUMBER = config["PHASE_NUMBER"] # 绿灯相位数量
MOVEMENT_NUMBER = config["MOVEMENT_NUMBER"] # 有效 movement 的数量
ACCIDENTS = config["ACCIDENTS"] # 定义的事故
SPECIAL_VEHICLES = config["SPECIAL_VEHICLES"] # 定义特殊车辆

# 初始化场景飞行器位置, 获得俯视角图像
aircraft_inits = {
    'a1': {
        "aircraft_type": "drone",
        "action_type": "stationary", # 水平移动
        "position": CENTER_COORDINATES, "speed":3, "heading":(1,1,0), # 初始位置
        "communication_range":100, 
        "if_sumo_visualization":True, "img_file":None,
        "custom_update_cover_radius":None # 使用自定义的计算
    },
}

if __name__ == '__main__':
    tls_id = JUNCTION_NAME
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}")
    net_file = path_convert(f"../exp_networks/{SCENARIO_NAME}/{NETFILE}")
    scenario_glb_dir = path_convert(f"../exp_networks/{SCENARIO_NAME}/3d_assets/")
    base_path = base_path = path_convert(f"../exp_dataset/{SCENARIO_NAME}/") # 存储路径
    trip_info = path_convert(f"../exp_dataset/{SCENARIO_NAME}/tripinfo_rl.out.xml")
    
    # Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = path_convert(f"../rl_tsc/{SCENARIO_IDX}_models/last_rl_model.zip")
    policy_kwargs = dict(
        features_extractor_class=IntersectionNet,
        features_extractor_kwargs=dict(features_dim=32),
    )
    model = PPO.load(
        model_path, 
        device=device,
        custom_objects={"policy_kwargs": policy_kwargs}
    )

    # Init Env
    tsc_env = make_env(
        tls_id=tls_id,
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        scenario_glb_dir=scenario_glb_dir,
        trip_info=trip_info,
        movement_num=MOVEMENT_NUMBER,
        phase_num=PHASE_NUMBER,
        num_seconds=NUM_SECONDS,
        accident_config=ACCIDENTS,
        special_vehicle_config=SPECIAL_VEHICLES,
        use_gui=True,
        aircraft_inits=aircraft_inits,
        preset="480P",
        resolution=1,
        base_path=base_path,
    )

    # Interact with Environment
    dones = False
    rl_state, infos = tsc_env.reset()
    
    while not dones:
        action, _ = model.predict(rl_state, deterministic=True)
        rl_state, rewards, truncated, dones, infos = tsc_env.step(action=action.item())

    # 存储全局信息
    global_infos = {
        "scenario_name": SCENARIO_NAME,
        "tls_id": JUNCTION_NAME,
        "can_perform_action": {**tsc_env.can_perform_action_infos}
    }
    save_str_to_json(global_infos, os.path.join(base_path, "global.json"))

    tsc_env.close()