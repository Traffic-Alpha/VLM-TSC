'''
Author: Maonan Wang
Date: 2024-12-30 16:00:33
LastEditTime: 2025-07-10 14:13:47
LastEditors: WANG Maonan
Description: Generate Routes for Hongkong YMT
FilePath: /VLM-CloseLoop-TSC/sim_envs/Hongkong_YMT/generate_routes.py
'''
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.generate_routes import generate_route

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level='WARNING', terminal_log_level='INFO')

# 开启仿真 --> 指定 net 文件
sumo_net = current_file_path("./env_normal/YMT.net.xml")

generate_route(
    sumo_net=sumo_net,
    interval=[1,1,1,1,1,1,1], 
    edge_flow_per_minute={
        '102454134#0': [10, 8, 15, 7, 5, 12, 9],
        '1200878753#0': [10, 15, 8, 10, 9, 11, 10],
        '30658263#0': [15, 15, 10, 20, 13, 16, 10], # 带有一个左转车道
        '960661806#0': [6, 1, 1, 2, 5, 6, 5],
    }, # 每分钟每个 edge 有多少车
    edge_turndef={},
    veh_type={
        # 特殊车辆通过 CONFIG 插入
        'background': {'color':'220,220,220', 'length': 5, 'probability':1},
    },
    output_trip=current_file_path('./testflow.trip.xml'),
    output_turndef=current_file_path('./testflow.turndefs.xml'),
    output_route=current_file_path('./env_normal/YMT.rou.xml'),
    interpolate_flow=False,
    interpolate_turndef=False,
)