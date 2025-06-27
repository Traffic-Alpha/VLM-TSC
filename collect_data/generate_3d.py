'''
Author: WANG Maonan
Date: 2025-06-25 18:21:04
LastEditors: WANG Maonan
Description: 精细化场景渲染
LastEditTime: 2025-06-26 18:23:11
'''
import os
import sys
import time

tshub_path = "/home/tshub/Code_Project/2_Traffic/TransSimHub/"
sys.path.insert(0, tshub_path + "tshub/tshub_env3d/")

from vis3d_blender_render import TimestepRenderer, VehicleManager

# 配置文件路径
START_TIMESTEP = 0 # 开始渲染的时间
END_TIMESTEP = 68 # 结束渲染的时间
MODELS_BASE_PATH = "/home/tshub/Code_Project/3_blender/3d_models/" # 需要渲染的模型
SCENARIO_PATH = "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/Hongkong_YMT/" # 场景所在的环境

def main():
    """主执行函数"""
    try:
        # 初始化管理器
        vehicle_mgr = VehicleManager(MODELS_BASE_PATH)
        renderer = TimestepRenderer(
            resolution=480, 
            render_mask=False, 
            render_depth=False
        )

        # 初始化计时变量
        total_start_time = time.time()
        timestep_times = []

        # 遍历所有时刻
        for timestep in range(START_TIMESTEP, END_TIMESTEP + 1):
            scenario_timestep_path = os.path.join(SCENARIO_PATH, str(timestep)) # 存储的文件夹
            json_path = os.path.join(scenario_timestep_path, "3d_vehs.json")
            
            if not os.path.exists(json_path):
                print(f"⚠️ 时刻 {timestep} 的JSON文件不存在，跳过")
                continue
            
            print(f"\n🕒 正在处理时刻 {timestep}...")
            timestep_start = time.time()
            
            # 加载车辆
            vehicles = vehicle_mgr.load_vehicles(json_path)
            if not vehicles:
                print(f"⚠️ 时刻 {timestep} 未加载任何车辆")
            
            # 渲染
            renderer.render_timestep(scenario_timestep_path)

            # 计算并记录当前timestep耗时
            timestep_elapsed = time.time() - timestep_start
            timestep_times.append(timestep_elapsed)
            print(f"✅ 完成时刻 {timestep} 的渲染 (耗时: {timestep_elapsed:.2f}秒)")
        
        # 计算总耗时和统计信息
        total_elapsed = time.time() - total_start_time
        avg_time = sum(timestep_times) / len(timestep_times) if timestep_times else 0
        min_time = min(timestep_times) if timestep_times else 0
        max_time = max(timestep_times) if timestep_times else 0
        
        print("\n🎉 所有时刻渲染完成!")
        print(f"📊 渲染统计:")
        print(f"  - 总timestep数: {len(timestep_times)}")
        print(f"  - 总耗时: {total_elapsed/60:.2f}分钟")
        print(f"  - 平均每个timestep耗时: {avg_time/60:.2f}分钟")
        print(f"  - 最快timestep耗时: {min_time/60:.2f}分钟")
        print(f"  - 最慢timestep耗时: {max_time/60:.2f}分钟")
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
# blender /home/tshub/Code_Project/2_Traffic/sim_envs/Hongkong_YMT/blender/HK_YMT.blend --background --python /home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/collect_data/generate_3d.py