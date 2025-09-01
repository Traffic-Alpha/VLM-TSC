###
 # @Author: WANG Maonan
 # @Date: 2025-08-14 16:59:25
 # @LastEditors: WANG Maonan
 # @Description: 渲染多个场景
 # @LastEditTime: 2025-08-29 18:16:46
### 
#!/bin/bash

# 定义场景路径数组
SCENARIOS=(
    "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/SouthKorea_Songdo_easy_random_perturbation_barrier"
    "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/SouthKorea_Songdo_easy_random_perturbation_branch"
    "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/SouthKorea_Songdo_easy_random_perturbation_crashed"
    "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/SouthKorea_Songdo_easy_random_perturbation_pedestrain"
)

# 遍历所有场景并执行render.sh
for scenario in "${SCENARIOS[@]}"; do
    echo "正在处理场景: $scenario"
    ./render.sh --scenario "$scenario"
    
    # 检查上一个命令的退出状态
    if [ $? -ne 0 ]; then
        echo "错误: 处理场景 $scenario 时失败"
        exit 1
    fi
    
    echo "场景 $scenario 处理完成"
    echo "----------------------------------------"
done

echo "所有场景处理完成！"