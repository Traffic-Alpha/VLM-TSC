'''
Author: WANG Maonan
Date: 2025-06-30 21:57:14
LastEditors: WANG Maonan
Description: Plot Reward Curve
LastEditTime: 2025-06-30 21:58:18
'''
from tshub.utils.plot_reward_curves import plot_reward_curve
from tshub.utils.get_abs_path import get_abs_path
path_convert = get_abs_path(__file__)


if __name__ == '__main__':
    SCENARIO_IDX = "Hongkong_YMT_NORMAL"
    log_files = [
        path_convert(f'./{SCENARIO_IDX}_log/{i}.monitor.csv')
        for i in range(10)
    ]
    output_file = path_convert(f'./reward_curve.png')
    plot_reward_curve(log_files, output_file=output_file, window_size=1, fill_outliers=False)