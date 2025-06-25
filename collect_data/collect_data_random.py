'''
Author: WANG Maonan
Date: 2025-06-25 16:45:03
LastEditors: WANG Maonan
Description: 使用随机策略收集信息
LastEditTime: 2025-06-25 18:08:47
'''
import os
import cv2
import random

from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.utils.format_dict import save_str_to_json

from utils.tsc_env3d import TSCEnvironment3D
from utils.tsc_wrapper import TSCEnvWrapper
from utils.save_vector import save_numpy_array

from CONFIG import SCENARIO_CONFIGS
from collect_data.parse_state import TrafficState2DICT # 将环境信息转换为 JSON
 
def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))

# 读取场景配置
SCENARIO_NAME = "Hongkong_YMT" # 可视化场景, SouthKorea_Songdo, Hongkong_YMT
config = SCENARIO_CONFIGS.get(SCENARIO_NAME) # 获取特定场景的配置
SUMOCFG = config["SUMOCFG"]
NETFILE = config["NETFILE"]
JUNCTION_NAME = config["JUNCTION_NAME"]
CENTER_COORDINATES = config["CENTER_COORDINATES"]
PHASE_NUMBER = config["PHASE_NUMBER"] # 绿灯相位数量

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

def make_env(
        tls_id:str, 
        sumo_cfg:str, net_file:str,
        scenario_glb_dir:str, 
        num_seconds:int, use_gui:bool,
        aircraft_inits=None,
        preset:str="1080P", resolution:float=1,
    ):
    tsc_env = TSCEnvironment3D(
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        scenario_glb_dir=scenario_glb_dir,
        preset=preset, resolution=resolution,
        num_seconds=num_seconds,
        tls_ids=[tls_id],
        tls_action_type='choose_next_phase',
        use_gui=use_gui,
        aircraft_inits=aircraft_inits,
        modify_states_func=None
    )
    tsc_env = TSCEnvWrapper(tsc_env, tls_id=tls_id)

    return tsc_env

if __name__ == '__main__':
    
    tls_id = JUNCTION_NAME
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}.sumocfg")
    net_file = path_convert(f"../exp_networks/{SCENARIO_NAME}/env/{NETFILE}.net.xml")
    scenario_glb_dir = path_convert(f"../exp_networks/{SCENARIO_NAME}/3d_assets/")
    
    # Init Env
    tsc_env = make_env(
        tls_id=tls_id,
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        scenario_glb_dir=scenario_glb_dir,
        num_seconds=300,
        use_gui=True,
        aircraft_inits=aircraft_inits,
        preset="480P",
        resolution=1,
    )

    # Interact with Environment
    dones = False
    step_idx = 0
    rl_state, pixel, veh_3d_elements, infos = tsc_env.reset()
    traffic_state_to_dict = TrafficState2DICT(tls_id, infos) # 特征转换器

    while not dones:
        action = random.randint(0, PHASE_NUMBER-1)
        states, rewards, truncated, dones, infos = tsc_env.step(action=action)
        rl_state, camera_data, veh_3d_elements = states['rl_state'], states['pixel'], states['veh_3d_elements']

        # info 包含环境完整的信息, 用于转换为 json
        direction_infos = traffic_state_to_dict(infos)

        # #################
        # 存储每一个时刻的数据
        # #################
        base_path = path_convert(f"../exp_dataset/{SCENARIO_NAME}/{step_idx}")
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        # -> 存储 Vector
        save_numpy_array(array=rl_state, file_path=os.path.join(base_path, "state_vector.json"))

        # -> 存储车辆数据
        save_str_to_json(veh_3d_elements, os.path.join(base_path, "3d_vehs.json"))

        # -> 存储传感器数据 (图片)
        for element_id, cameras in camera_data.items():
            # Iterate over each camera type
            for camera_type, image_array in cameras.items():
                # Save the numpy array as an image
                image_path = os.path.join(base_path, f"{element_id}_{camera_type}.png")
                cv2.imwrite(image_path, convert_rgb_to_bgr(image_array))

        # -> 存储每个方向的 JSON 数据
        for direction_idx, direction_info in direction_infos.items():
            json_path = os.path.join(base_path, f"{direction_idx}.json")
            save_str_to_json(direction_info, json_path)

        step_idx += 1
        
    tsc_env.close()