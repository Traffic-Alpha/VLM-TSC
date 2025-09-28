'''
Author: WANG Maonan
Date: 2025-06-25 18:21:04
LastEditors: WANG Maonan
Description: Render Junction Scenarios
LastEditTime: 2025-09-28 16:41:06
'''
import os
import sys
import time
import argparse

def parse_args():
    """解析 Blender 传递的参数"""
    # 提取 '--' 之后的参数
    argv = sys.argv
    if "--" not in argv:
        return {}
    args = argv[argv.index("--") + 1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--tshub", type=str, required=True, help="TransSimHub 根目录") # 加载 tshub 3d render lib
    parser.add_argument("--scenario", type=str, required=True, help="场景数据路径")
    parser.add_argument("--resolution", type=int, default=480, help="图像分辨率")
    parser.add_argument("--start", type=int, default=266, help="起始时间步")
    parser.add_argument("--end", type=int, default=266, help="结束时间步")
    parser.add_argument("--models", type=str, default="high_poly", choices=["high_poly", "low_poly"], help="车辆模型精度")
    
    return parser.parse_args(args)

def main():
    args = parse_args()

    # 动态设置模型路径
    models_base_path = os.path.join(
        args.tshub, 
        "tshub/tshub_env3d/_assets_3d/",
        f"vehicles_{args.models}/"  # 根据参数选择high_poly或low_poly
    )
    # 添加tshub到系统路径
    sys.path.insert(0, os.path.join(args.tshub, "tshub/tshub_env3d/"))
    
    # 动态导入（确保路径设置后再导入）
    from vis3d_blender_render import TimestepRenderer, VehicleManager

    try:
        # 初始化管理器
        vehicle_mgr = VehicleManager(models_base_path) # 加载特定的车辆模型
        renderer = TimestepRenderer(
            resolution=args.resolution,
            render_mask=False, 
            render_depth=False
        ) # 渲染场景的每一个时刻

        # 初始化计时变量
        total_start_time = time.time()
        timestep_times = []

        # 遍历所有时刻
        for timestep in range(args.start, args.end + 1):
            scenario_timestep_path = os.path.join(args.scenario, str(timestep)) # 存储的文件夹
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