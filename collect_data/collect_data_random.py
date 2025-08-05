'''
Author: WANG Maonan
Date: 2025-06-25 16:45:03
LastEditors: WANG Maonan
Description: 使用随机策略收集信息, 修改不同的配置文件
MAP: Beijing_Beihuan, Beijing_Beishahe

-> MAP=Beijing_Beishahe SCENE=easy_high_density_none python collect_data_random.py
-> MAP=Beijing_Beishahe SCENE=easy_high_density_event python collect_data_random.py

可以使用预设的配置文件, 通过 selector 文件
也可以自己组合文件
LastEditTime: 2025-08-05 13:57:39
'''
import os
import random
import hydra
from omegaconf import DictConfig, OmegaConf

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
    CENTER_COORDINATES = cfg.CENTER_COORDINATES
    PHASE_NUMBER = cfg.PHASE_NUMBER # 绿灯相位数量
    MOVEMENT_NUMBER = cfg.MOVEMENT_NUMBER # 有效 movement 的数量
    # networks & sumocfg
    SUMOCFG = cfg.SUMOCFG
    NETFILE = cfg.NETFILE
    # accidents & sepcial vehicles
    ACCIDENTS = cfg.ACCIDENTS # 定义的事故
    SPECIAL_VEHICLES = cfg.SPECIAL_VEHICLES # 定义特殊车辆

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

    # 初始化仿真参数
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}")
    net_file = path_convert(f"../exp_networks/{SCENARIO_NAME}/{NETFILE}")
    scenario_glb_dir = path_convert(f"../exp_networks/{SCENARIO_NAME}/3d_assets/")
    # 输出文件夹
    base_path = base_path = path_convert(f"../exp_dataset/{SCENARIO_IDX}/") # 存储路径
    trip_info = path_convert(f"../exp_dataset/{SCENARIO_IDX}/tripinfo_random.out.xml")
    
    # Init Env
    tsc_env = make_env(
        tls_id=JUNCTION_NAME,
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
        vehicle_model='high',
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


if __name__ == '__main__':
    main()