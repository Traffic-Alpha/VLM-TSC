'''
Author: WANG Maonan
Date: 2025-07-10 20:25:52
LastEditors: WANG Maonan
Description: ENV + Wrapper
LastEditTime: 2025-07-10 20:25:52
'''
from utils.env_utils.tsc_env3d import TSCEnvironment3D
from utils.env_utils.tsc_wrapper import TSCEnvWrapper

def make_env(
        tls_id:str, 
        sumo_cfg:str, net_file:str,
        scenario_glb_dir:str, 
        movement_num:int, phase_num:int,
        num_seconds:int, use_gui:bool,
        accident_config,
        special_vehicle_config,
        aircraft_inits=None,
        preset:str="1080P", resolution:float=1,
        base_path:str = None,
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