'''
Author: WANG Maonan
Date: 2025-07-10 20:25:52
LastEditors: WANG Maonan
Description: ENV + Wrapper
LastEditTime: 2025-07-17 16:04:37
'''
import os
from loguru import logger 
from utils.env_utils.tsc_env3d import TSCEnvironment3D
from utils.env_utils.tsc_wrapper import TSCEnvWrapper

def ensure_directory_exists(file_path):
    """确保文件所在的目录存在，如果不存在则创建
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):  # 检查目录是否存在
        os.makedirs(directory, exist_ok=True)  # 创建目录（包括父目录）
        logger.info(f"SIM: 目录已创建: {directory}")
    else:
        logger.info(f"SIM: 目录已存在: {directory}")
        
def make_env(
        tls_id:str, 
        sumo_cfg:str, net_file:str,
        scenario_glb_dir:str, 
        movement_num:int, phase_num:int,
        num_seconds:int, use_gui:bool,
        trip_info:str,
        accident_config,
        special_vehicle_config,
        aircraft_inits=None,
        preset:str="1080P", resolution:float=1,
        base_path:str = None,
    ):
    ensure_directory_exists(trip_info)
    tsc_env = TSCEnvironment3D(
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        scenario_glb_dir=scenario_glb_dir,
        preset=preset, resolution=resolution,
        num_seconds=num_seconds,
        tls_ids=[tls_id],
        tls_action_type='choose_next_phase',
        trip_info=trip_info,
        use_gui=use_gui,
        aircraft_inits=aircraft_inits,
        accident_config=accident_config,
        special_vehicle_config=special_vehicle_config
    )
    tsc_env = TSCEnvWrapper(
        tsc_env, tls_id=tls_id, 
        movement_num=movement_num,
        phase_num=phase_num,
        base_path=base_path,
    )

    return tsc_env