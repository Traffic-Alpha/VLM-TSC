import os
import torch
import matplotlib.pyplot as plt
import numpy as np

from langchain_openai import ChatOpenAI
from stable_baselines3 import PPO


from TSCAssistant.tsc_assistant import TSCAgent

from utils.readConfig import read_config
from utils.make_tsc_env import make_env

from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.tshub_env3d.tshub_env3d import Tshub3DEnvironment
from tshub.tshub_env3d.show_sensor_images import show_sensor_images



path_convert = get_abs_path(__file__)
set_logger(path_convert('./'), terminal_log_level='INFO')


def save_sensor_images(images, scale=1, steps = 1, output_dir='sensor_images'):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set up the figure for displaying images
    fig, axes = plt.subplots(1, len(images), figsize=(scale * 5 * len(images), scale * 5))

    # Handle cases when there is only one image and axes is not iterable
    if len(images) == 1:
        axes = [axes]

    for i, image in enumerate(images):
        if image is not None:
            # Display the image
            axes[i].imshow(image)
            axes[i].axis('off')  # Turn off the axis
            # Save each image to a file
            #plt.imsave(f'{output_dir}/sensor_image_{steps}_{i}.png', image)
            plt.imsave(f'{output_dir}/sensor_image_{i}.png', image)
        else:
            axes[i].axis('off')  # Hide the axis for None images

    # Save the figure displaying the images
    plt.tight_layout()
    plt.savefig(f'{output_dir}/combined_images.png')
    plt.close(fig)

def _process_obs(state):
    tls_id = 'J1'
    phase_num = len(state['tls'][tls_id]['phase2movements']) # phase 的个数
    delta_time = state['tls'][tls_id]['delta_time']
    phase_movements = state['tls'][tls_id]['phase2movements'] # 得到一个 phase 有哪些 movement 组成的
        
    movement_directions = state['tls'][tls_id]['movement_directions']
    movement_ids=state['tls'][tls_id]['movement_ids']
        # 1. 获取每个lane的数据
        # 2. 获取每个pahse对应的lane的标号
        # 3. 获取每个phase的数据
        
    _observation_net_info = list() # 路网的信息
        # phase_movements {0: ['E0--s', '-E1--s'], 1: ['E0--l', '-E1--l'], 2: ['-E3--s', '-E2--s'], 3: ['-E3--l', '-E2--l']}
    for _movement_id, _movement in enumerate(phase_movements): # 按照 movment_id 提取
        for i in range(len(phase_movements[_movement_id])):
            movement_id=movement_ids.index(phase_movements[_movement_id][i])
            flow_mean_speed= state['tls'][tls_id]['last_step_mean_speed'][movement_id] # 上一次
            mean_occupancy = state['tls'][tls_id]['last_step_occupancy'][movement_id]# 占有率
            jam_length_meters = state['tls'][tls_id]['jam_length_meters'][movement_id]# 排队车数量
            jam_length_vehicle= state['tls'][tls_id]['jam_length_vehicle'][movement_id]
            is_now_phase =  state['tls'][tls_id]['this_phase'][movement_id] # now phase id
            if is_now_phase==True:
                is_now_phase=1
            else:
                is_now_phase=0
                #print("obs:",[flow, mean_occupancy, max_occupancy, is_s, num_lane, min_green, is_now_phase, is_next_phase])
            _observation_net_info.append([flow_mean_speed, mean_occupancy, jam_length_meters, jam_length_vehicle, is_now_phase])
        # 不是四岔路, 进行不全
    for _ in range(8 - len(_observation_net_info)):
        _observation_net_info.append([0]*5)
    obs = np.array(_observation_net_info, dtype=np.float32) # 每个 movement 的信息
        
    return obs

if __name__ == '__main__':
    sumo_cfg = path_convert(f"./TSCScenario/SumoNets/train_four_345/env/train_four_345.sumocfg")
    scenario_glb_dir = path_convert(f"./TSCScenario/3d_assets")
    trip_info = path_convert(f'./Result/LLM.tripinfo.xml')

    tshub_env3d = Tshub3DEnvironment(
        sumo_cfg=sumo_cfg,
        scenario_glb_dir=scenario_glb_dir,
        is_aircraft_builder_initialized=False,
        is_map_builder_initialized=False,
        is_vehicle_builder_initialized=True, # 需要打开车辆才可以在仿真中看到车辆
        is_traffic_light_builder_initialized=True, # 需要打开信号灯才会有路口的摄像头
        tls_ids=['J1'],
        use_gui=True, 
        num_seconds=300,
        tls_action_type = 'choose_next_phase',
        collision_action="warn",
        # 下面是用于渲染的参数
        render_mode="offscreen", # 如果设置了 use_render_pipeline, 此时只能是 onscreen
        debuger_print_node=False,
        debugr_spin_camera=True,
        sensor_config={
            'tls': ['junction_front_all']
        } # 需要渲染的图像
    )

    config = read_config()
    openai_proxy = config['OPENAI_PROXY']
    openai_api_key = config['OPENAI_API_KEY']
    chat = ChatOpenAI(
        model=config['OPENAI_API_MODEL'], 
        temperature=0.0,
        openai_api_key=openai_api_key, 
        openai_proxy=openai_proxy
    )
    tsc_agent = TSCAgent(llm=chat, verbose=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = path_convert('./models/last_rl_model.zip')
    model = PPO.load(model_path, device=device)

    for _ in range(10):
        obs = tshub_env3d.reset()
        done = False
        i_steps = 0
        while not done:
            actions = {
                'vehicle': dict(),
                'tls': {'J1': 1},
            }
            obs = _process_obs(state = obs)
            action, _state = model.predict(obs, deterministic=True)
            actions['tls']['J1'] = action
            obs, reward, info, done, sensor_data = tshub_env3d.step(actions = actions)
            i_steps += 1

            show_sensor_images(
                [
                    sensor_data.get('J1_0', {}).get('junction_front_all', None),
                    sensor_data.get('J1_1', {}).get('junction_front_all', None),
                    sensor_data.get('J1_2', {}).get('junction_front_all', None),
                    sensor_data.get('J1_3', {}).get('junction_front_all', None),
                ],
                scale=1,
                images_per_row=4
            ) # 展示路口的摄像头
            save_sensor_images(
                [
                    sensor_data.get('J1_0', {}).get('junction_front_all', None),
                    sensor_data.get('J1_1', {}).get('junction_front_all', None),
                    sensor_data.get('J1_2', {}).get('junction_front_all', None),
                    sensor_data.get('J1_3', {}).get('junction_front_all', None),
                ],
                scale=1, steps = i_steps,
            ) # 展示
    tshub_env3d.close()