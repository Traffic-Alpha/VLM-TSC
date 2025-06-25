'''
Author: WANG Maonan
Date: 2025-06-25 18:06:42
LastEditors: WANG Maonan
Description: 将特征向量存储在文件中
LastEditTime: 2025-06-25 18:09:43
'''
import json
import numpy as np
from typing import Union, Optional
from pathlib import Path

def save_numpy_array(
    array: np.ndarray,
    file_path: Union[str, Path],
    metadata: Optional[dict] = None,
) -> None:
    """
    将 NumPy 数组保存为 JSON 文件
    
    Args:
        array: 要保存的 NumPy 数组
        file_path: 保存路径 (包括 .json 扩展名)
        metadata: 可选的元数据字典 (如描述、作者等)
    """
    data = {
        "array_data": array.tolist(),  # 转换为 Python 列表
        "dtype": str(array.dtype),    # 保存数据类型
        "shape": list(array.shape),   # 保存数组形状
    }
    
    # 添加元数据 (如果有)
    if metadata:
        data["metadata"] = metadata
    
    # 写入 JSON 文件
    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_numpy_array(file_path: Union[str, Path]) -> np.ndarray:
    """
    从 JSON 文件加载 NumPy 数组
    
    Args:
        file_path: JSON 文件路径
        
    Returns:
        重建的 NumPy 数组
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # 重建 NumPy 数组
    array = np.array(data["array_data"], dtype=data["dtype"])
    return array