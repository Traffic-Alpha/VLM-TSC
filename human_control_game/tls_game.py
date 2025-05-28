'''
Author: Maonan Wang
Date: 2025-03-31 15:47:21
LastEditTime: 2025-03-31 18:17:08
LastEditors: Maonan Wang
Description: 人类控制路口信号灯

假设你是一个 Python 专家，你准备使用 Pygame 制作一个信号灯控制的小游戏。
这个游戏界面由两个部分组成：
1. 4 个方向摄像头的数据，这里是 nunpy array 的格式。
2. 可以选择的 traffic phase,（可以是 2-4 个），每个 phase 由多个 movement 组成，例如 phase-1 是南北直行， phase-2 南北左转，phase-3 东西直行，phase-3 东西左转。
用户每次可以选择不同的 traffic phase 为绿灯，然后 camera 数据会更新。然后等待下一次用户的输入。

请你根据上面的要求，写出完整的 Python 代码。需要注意代码需要 Python 编程的规范。


FilePath: /VLM-TSC/human_control_game/hc_tls.py
'''
import pygame

from utils.game_env import TSCEnvironmentGame3D
from utils.game_wrapper import TSCGameEnvWrapper
from tshub.utils.get_abs_path import get_abs_path
path_convert = get_abs_path(__file__)


def make_env(
        tls_id:str, 
        sumo_cfg:str, 
        network_file:str,
        scenario_glb_dir:str, 
        num_seconds:int, use_gui:bool,
        preset:str="1080P", resolution:float=1,
    ):
    tsc_game_env = TSCEnvironmentGame3D(
        sumo_cfg=sumo_cfg,
        net_file=network_file,
        scenario_glb_dir=scenario_glb_dir,
        preset=preset, resolution=resolution,
        num_seconds=num_seconds,
        tls_ids=[tls_id],
        tls_action_type='choose_next_phase',
        use_gui=use_gui,
        modify_states_func=None
    )
    tsc_game_env = TSCGameEnvWrapper(tsc_game_env, tls_id=tls_id)

    return tsc_game_env


# 初始化 Pygame
pygame.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 定义窗口尺寸
WIDTH = 800
HEIGHT = 600

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("信号灯控制小游戏")

# 定义交通阶段，用箭头描述
traffic_phases = {
    0: "↑↓",
    1: "↖↘",
    2: "←→",
    3: "↗↙"
}

# 绘制摄像头数据
def draw_camera_data(camera_data):
    for i, data in enumerate(camera_data):
        x = (i % 2) * (WIDTH // 2)
        y = (i // 2) * (HEIGHT // 2)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                color = data[row, col]
                pygame.draw.rect(screen, color, (x + col * 2, y + row * 2, 2, 2))


# 绘制交通阶段选项
def draw_traffic_phases(selected_phase):
    y = 20
    # 指定支持特殊字符的字体，这里使用系统默认字体 Arial
    font = pygame.font.SysFont('Arial', 36)
    for phase, description in traffic_phases.items():
        if phase == selected_phase:
            color = GREEN
        else:
            color = RED
        text = font.render(f"Phase {phase}: {description}", True, color)
        screen.blit(text, (20, y))
        y += 40


if __name__ == '__main__':
    # 主环境交互, 获得传感器数据
    tls_id = 'htddj_gsndj'
    sumo_cfg = path_convert("../map/single_junction.sumocfg")
    network_file = path_convert("../map/single_junction.net.xml")
    scenario_glb_dir = path_convert(f"../map/3d_assets")

    tsc_game_env = make_env(
        tls_id=tls_id,
        sumo_cfg=sumo_cfg,
        network_file=network_file,
        scenario_glb_dir=scenario_glb_dir,
        num_seconds=300,
        use_gui=True,
        preset="1080P", 
        resolution=1,
    )
    tls_pixel_state = tsc_game_env.reset()

    # 主循环
    running = True
    selected_phase = 0 # 初始化选择的相位
    while running:
        # 检测 event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos # 判断鼠标的位置, 从而判断选择的哪一个 traffic phase
                for i, (phase, _) in enumerate(traffic_phases.items()):
                    if 20 <= x <= 200 and 20 + i * 40 <= y <= 20 + (i + 1) * 40: # 判断选择的哪一个 traffic phase
                        print(f"选择了 Phase {phase}")
                        selected_phase = phase # 选择的相位

        screen.fill(BLACK)
        tls_pixel_state, rewards, truncated, dones, infos = tsc_game_env.step(int(selected_phase))
        draw_camera_data(camera_data=tls_pixel_state['junction_front_all']) # 更新摄像头数据
        draw_traffic_phases(selected_phase=selected_phase) # 绘制选择的信号灯
        pygame.display.flip()

    # 退出 Pygame
    pygame.quit()