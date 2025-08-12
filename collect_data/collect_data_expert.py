'''
Author: WANG Maonan
Date: 2025-07-10 17:41:22
LastEditors: WANG Maonan
Description: 专家策略, rl+rule
+ Command Example: MAP=France_Massy SCENE=easy_random_perturbation_barrier python collect_data_expert.py
LastEditTime: 2025-08-12 11:51:51
'''
import os
import torch
import hydra
from omegaconf import DictConfig, OmegaConf
from stable_baselines3 import PPO

from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.utils.format_dict import save_str_to_json

from utils.env_utils.make_env import make_env
from utils.rl_utils.simple_int import IntersectionNet

from parse_infos.get_expert_action import ExpertTrafficSignalController # 专家决策器

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
    JUNCTION_NAME = cfg.JUNCTION_NAME # tls id
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

    # configs for sim
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}")
    net_file = path_convert(f"../exp_networks/{SCENARIO_NAME}/{NETFILE}")
    scenario_glb_dir = path_convert(f"../exp_networks/{SCENARIO_NAME}/3d_assets/")
    base_path = base_path = path_convert(f"../exp_dataset/{SCENARIO_IDX}/") # 存储路径
    trip_info = path_convert(f"../exp_dataset/{SCENARIO_IDX}/tripinfo_fix.out.xml")

    # Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _none_event = '_'.join(SCENARIO_IDX.split('_')[:-1] + ['none'])
    model_path = path_convert(f"../rl_tsc/{_none_event}_models/last_rl_model.zip")
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
        resolution=1,
        base_path=base_path,
    )

    # Interact with Environment
    dones = False
    # 初始化环境
    rl_state, infos = tsc_env.reset()
    
    # 初始化专家决策
    expert_decision = ExpertTrafficSignalController(tls_id=JUNCTION_NAME, raw_infos=infos) 
    
    while not dones:
        decision = expert_decision.decide(infos['state']['vehicle'])
        if decision is None: # 如果不是特殊情况, 则使用 RL 的决策
            decision, _ = model.predict(rl_state, deterministic=True)
            decision = decision.item()
        else:
            print(f"--> 使用专家决策特殊情况 {decision}")

        rl_state, rewards, truncated, dones, infos = tsc_env.step(action=decision)

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