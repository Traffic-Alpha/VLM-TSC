'''
Author: WANG Maonan
Date: 2025-06-25 16:45:03
LastEditors: WANG Maonan
Description: 使用随机策略收集信息
LastEditTime: 2025-07-16 20:52:04
'''
import os
import random

from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.utils.format_dict import save_str_to_json

from utils.env_utils.make_env import make_env
from CONFIG import SCENARIO_CONFIGS
 
def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))

# 读取场景配置
SCENARIO_IDX = "Hongkong_YMT_NORMAL" # 可视化场景, SouthKorea_Songdo, Hongkong_YMT
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
    trip_info = path_convert(f"../exp_dataset/{SCENARIO_NAME}/tripinfo_random.out.xml")
    
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
        action = random.randint(0, PHASE_NUMBER-1)
        states, rewards, truncated, dones, infos = tsc_env.step(action=action)
    
    # 存储全局信息
    global_infos = {
        "scenario_name": SCENARIO_NAME,
        "tls_id": JUNCTION_NAME,
        "can_perform_action": {**tsc_env.can_perform_action_infos}
    }
    save_str_to_json(global_infos, os.path.join(base_path, "global.json"))
        
    tsc_env.close()