'''
Author: WANG Maonan
Date: 2025-07-17 13:01:58
LastEditors: WANG Maonan
Description: 车辆 Route 生成
LastEditTime: 2025-07-17 15:32:43
'''
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.generate_routes import generate_route

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level='WARNING', terminal_log_level='INFO')

# 开启仿真 --> 指定 net 文件
sumo_net = current_file_path("./networks/normal.net.xml")

traffic_flow_configs = {
    # 1. 稳定低密度车流 (Stable Low-Density Flow)
    "low_density": {
        '741602130.216': [8, 8, 8, 8, 8],  # 稳定8辆/分钟
        '657921289.337': [7, 7, 7, 7, 7],  # 稳定7辆/分钟
        '657921284.293': [6, 6, 6, 6, 6]   # 稳定6辆/分钟
    },
    
    # 2. 波动通勤车流 (Fluctuating Commuter Flow)
    "fluctuating_commuter": {
        '741602130.216': [5, 20, 5, 18, 4],  # 高峰低谷交替
        '657921289.337': [4, 22, 6, 15, 3],  # 强波动性
        '657921284.293': [7, 18, 5, 12, 6]   # 中等波动
    },
    
    # 3. 饱和高密度车流 (Saturated High-Density Flow)
    "high_density": {
        '741602130.216': [25, 25, 25, 25, 25],  # 车道近饱和
        '657921289.337': [22, 22, 22, 22, 22],  # 稳定高负载
        '657921284.293': [20, 20, 20, 20, 20]   # 持续高压
    },
    
    # 4. 随机扰动车流 (Random Perturbation Flow)
    "random_perturbation": {
        '741602130.216': [15, 3, 25, 5, 10], 
        '657921289.337': [18, 2, 30, 8, 12], 
        '657921284.293': [12, 10, 5, 20, 15]
    },
    
    # 5. 递增需求车流 (Increasing Demand Flow)
    "increasing_demand": {
        '741602130.216': [5, 10, 15, 20, 25],  # 线性增长
        '657921289.337': [8, 8, 15, 22, 30],  # 阶梯式增长
        '657921284.293': [10, 15, 25, 30, 35]  # 加速增长
    },
}

for config_id, config_info in traffic_flow_configs.items():
    generate_route(
        sumo_net=sumo_net,
        interval=[2,2,2,2,2], # 共有 10 min
        edge_flow_per_minute=config_info,
        edge_turndef={},
        veh_type={
            'background': {'color':'220,220,220', 'length': 5, 'probability':1},
        },
        output_trip=current_file_path('./testflow.trip.xml'),
        output_turndef=current_file_path('./testflow.turndefs.xml'),
        output_route=current_file_path(f'./routes/{config_id}.rou.xml'),
        interpolate_flow=False,
        interpolate_turndef=False,
    )