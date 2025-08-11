###
 # @Author: WANG Maonan
 # @Date: 2025-08-11 17:19:12
 # @LastEditors: WANG Maonan
 # @Description: Render Scenarios
 # @Example 渲染单个时间步 ./render.sh --start 250 --end 251 --models high_poly
 # @LastEditTime: 2025-08-11 17:37:59
### 
#!/bin/bash

# 默认参数值
DEFAULT_START=0
DEFAULT_END=100
DEFAULT_MODELS="high_poly"
DEFAULT_BLEND="/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_networks/Hongkong_YMT/env.blend"
DEFAULT_SCENARIO="/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/Hongkong_YMT_easy_high_density_barrier/"
DEFAULT_TSHUB="/home/tshub/Code_Project/2_Traffic/TransSimHub/"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --start)
            START="$2"
            shift 2
            ;;
        --end)
            END="$2"
            shift 2
            ;;
        --models)
            MODELS="$2"
            shift 2
            ;;
        --blend)
            BLEND_FILE="$2"
            shift 2
            ;;
        --scenario)
            SCENARIO_PATH="$2"
            shift 2
            ;;
        --tshub)
            TSHUB_PATH="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 设置默认值（如果用户未提供）
START=${START:-$DEFAULT_START}
END=${END:-$DEFAULT_END}
MODELS=${MODELS:-$DEFAULT_MODELS}
BLEND_FILE=${BLEND_FILE:-$DEFAULT_BLEND}
SCENARIO_PATH=${SCENARIO_PATH:-$DEFAULT_SCENARIO}
TSHUB_PATH=${TSHUB_PATH:-$DEFAULT_TSHUB}

# 打印配置信息
echo "┌──────────────────────────────────────────────┐"
echo "│           Blender 渲染配置参数                 │"
echo "├──────────────────────────────────────────────┤"
echo "│ 起始时间步: $START"
echo "│ 结束时间步: $END"
echo "│ 模型精度:   $MODELS"
echo "│ Blend文件:  $BLEND_FILE"
echo "│ 场景路径:   $SCENARIO_PATH"
echo "│ TransSimHub: $TSHUB_PATH"
echo "└──────────────────────────────────────────────┘"

# 启动Blender渲染
blender "$BLEND_FILE" --background --python render_scene.py -- \
    --tshub "$TSHUB_PATH" \
    --scenario "$SCENARIO_PATH" \
    --start "$START" \
    --end "$END" \
    --models "$MODELS"

# 检查退出状态
if [ $? -eq 0 ]; then
    echo "✅ 渲染成功完成!"
else
    echo "❌ 渲染过程中出错!"
fi