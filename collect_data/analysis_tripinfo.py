'''
Author: WANG Maonan
Date: 2025-07-16 20:56:26
LastEditors: WANG Maonan
Description: 分析 Tripinfo 文件
LastEditTime: 2025-07-16 21:15:25
'''
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.analysis_output.tripinfo_analysis import TripInfoAnalysis

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level="INFO")

METHOD = 'expert' # random, fix, rl, expert
SCENARIO_NAME = 'Hongkong_YMT' # Hongkong_YMT, SouthKorea_Songdo, France_Massy

tripinfo_file = current_file_path(f"../exp_dataset/{SCENARIO_NAME}/tripinfo_{METHOD}.out.xml")
tripinfo_parser = TripInfoAnalysis(tripinfo_file)

# 所有车辆一起分析
stats = tripinfo_parser.calculate_multiple_stats(metrics=['duration', 'waitingTime', 'fuel_abs'])
TripInfoAnalysis.print_stats_as_table(stats)

# 按照车辆类型分析
print('-'*10)
vehicle_stats = tripinfo_parser.statistics_by_vehicle_type(metrics=['duration', 'waitingTime'])
print("==> Travel Time: -----------")
print(vehicle_stats['duration'])
print("==> Waiting Time: -----------")
print(vehicle_stats['waitingTime'])