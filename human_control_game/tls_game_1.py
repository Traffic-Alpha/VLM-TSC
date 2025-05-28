'''
Author: Maonan Wang
Date: 2025-03-31 18:17:33
LastEditTime: 2025-04-01 10:48:17
LastEditors: Maonan Wang
Description: 
FilePath: /VLM-TSC/human_control_game/tls_game_1.py
'''
import pygame
import traceback
import multiprocessing
from multiprocessing import Queue

from utils.game_env import TSCEnvironmentGame3D
from utils.game_wrapper import TSCGameEnvWrapper
from tshub.utils.get_abs_path import get_abs_path
path_convert = get_abs_path(__file__)


def make_env(
        tls_id: str,
        sumo_cfg: str,
        network_file: str,
        scenario_glb_dir: str,
        trip_info:str, summary:str, statistic_output:str,
        num_seconds: int, use_gui: bool,
        preset: str = "1080P", resolution: float = 1,
):
    tsc_game_env = TSCEnvironmentGame3D(
        sumo_cfg=sumo_cfg,
        net_file=network_file,
        scenario_glb_dir=scenario_glb_dir,
        trip_info=trip_info,
        summary=summary,
        statistic_output=statistic_output,
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
HEIGHT = 400

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
    # 定义缩放比例，这里将图像缩小为原来的 1/4
    scale_factor = 4
    scaled_width = 1280 // scale_factor
    scaled_height = 720 // scale_factor

    for i, data in enumerate(camera_data):
        x = (i % 2) * (WIDTH // 2)
        y = (i // 2) * (HEIGHT // 2)
        # 缩小图像
        scaled_data = data[::scale_factor, ::scale_factor]
        for row in range(scaled_height):
            for col in range(scaled_width):
                color = tuple(scaled_data[row, col])
                pygame.draw.rect(screen, color, (x + col, y + row, 1, 1))


# 绘制交通阶段选项
def draw_traffic_phases(selected_phase):
    print(f"选择的信号灯为 {selected_phase}")
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


# 进程函数，用于运行环境操作
def env_process(
        queue_in, queue_out, 
        tls_id, 
        sumo_cfg, network_file, scenario_glb_dir, 
        trip_info, summary, statistic_output,
        num_seconds, use_gui, preset, resolution
    ):
    tsc_game_env = make_env(
        tls_id=tls_id,
        sumo_cfg=sumo_cfg,
        network_file=network_file,
        scenario_glb_dir=scenario_glb_dir,
        trip_info=trip_info,
        summary=summary,
        statistic_output=statistic_output,
        num_seconds=num_seconds,
        use_gui=use_gui,
        preset=preset,
        resolution=resolution,
    ) # 新建环境
    tls_pixel_state = tsc_game_env.reset() # 初始化环境
    queue_out.put(tls_pixel_state) # 传入数据

    while True:
        action = queue_in.get() # 根据队列里面的数据判断执行的 action
        if action is None:
            break
        tls_pixel_states, rewards, truncated, dones, infos = tsc_game_env.step(int(action))
        
        for tls_pixel_state in tls_pixel_states:
            queue_out.put(tls_pixel_state)
        
        if dones:
            tsc_game_env.close()


if __name__ == '__main__':
    try:
        # 主环境交互, 获得传感器数据
        tls_id = 'htddj_gsndj'
        sumo_cfg = path_convert("../map/single_junction.sumocfg")
        network_file = path_convert("../map/single_junction.net.xml")
        scenario_glb_dir = path_convert(f"../map/3d_assets")
        trip_info = path_convert("./sumo_output/tripinfo.out.xml")
        summary = path_convert("./sumo_output/summary.out.xml")
        statistic_output = path_convert("./sumo_output/statistic.out.xml")

        # 创建队列用于进程间通信
        queue_in = Queue() # 存储 action
        queue_out = Queue() # 存储环境返回的 pixel

        # 启动进程
        p = multiprocessing.Process(
            target=env_process,
            args=(
                queue_in, queue_out, 
                tls_id, sumo_cfg, network_file, scenario_glb_dir, 
                trip_info, summary, statistic_output,
                300, True, "720P", 1
            )
        )
        p.start()

        # 获取初始状态
        screen.fill(BLACK)
        tls_pixel_state = queue_out.get()
        print("环境初始化成功，进入主循环")

        # 主循环
        running = True
        selected_phase = 0  # 初始化选择的相位
        while running:
            # 检测 event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False # 结束仿真
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos  # 判断鼠标的位置, 从而判断选择的哪一个 traffic phase
                    for i, (phase, _) in enumerate(traffic_phases.items()):
                        if 20 <= x <= 200 and 20 + i * 40 <= y <= 20 + (i + 1) * 40:  # 判断选择的哪一个 traffic phase
                            print(f"选择了 Phase {phase}")
                            selected_phase = phase  # 选择的相位
                            queue_in.put(selected_phase)

            # 检查是否有 step 结果
            if not queue_out.empty():
                tls_pixel_state = queue_out.get()

            draw_camera_data(camera_data=tls_pixel_state['junction_front_all']) # 更新摄像头数据
            draw_traffic_phases(selected_phase=selected_phase)  # 绘制选择的信号灯
            pygame.display.flip()

        # 停止进程
        queue_in.put(None)
        p.join()

    except Exception as e:
        print(f"程序出现异常: {e}")
        traceback.print_exc()

    # 退出 Pygame
    pygame.quit()
    