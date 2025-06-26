'''
Author: WANG Maonan
Date: 2025-06-25 18:06:42
LastEditors: WANG Maonan
Description: 将特征向量存储在文件中
LastEditTime: 2025-06-26 15:32:26
'''
import numpy as np
from numpy.typing import NDArray
from typing import Optional

def save_states(states: NDArray[np.float32], filename: str) -> None:
    """Save a NumPy array to a .npy file.

    Args:
        states (NDArray[np.float32]): The NumPy array to save, with dtype=np.float32.
        filename (str): The path to the output .npy file.
    """
    np.save(filename, states)


def load_states(filename: str) -> NDArray[np.float32]:
    """Load a NumPy array from a .npy file.

    Args:
        filename (str): The path to the input .npy file.

    Returns:
        NDArray[np.float32]: The loaded NumPy array with dtype=np.float32.
    """
    return np.load(filename)