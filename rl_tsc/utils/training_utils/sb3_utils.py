'''
@Author: WANG Maonan
@Date: 2023-09-08 17:39:53
@Description: Stable Baseline3 Utils
LastEditTime: 2025-09-08 17:14:22
'''
import os
import numpy as np
from typing import Callable
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback

class VecNormalizeCallback(BaseCallback):
    """保存环境标准化之后的值
    """
    def __init__(self, save_freq: int, save_path: str, name_prefix: str = "vec_normalize", verbose: int = 0):
        super(VecNormalizeCallback, self).__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.save_freq == 0:
            path = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps.pkl")
            self.model.get_vec_normalize_env().save(path)
            if self.verbose > 1:
                print(f"Saving VecNormalize to {path}")
        return True


class CustomEvalCallback(EvalCallback):
    """
    扩展EvalCallback，同时保存最优模型和环境信息
    """
    def __init__(self, *args, **kwargs):
        # 保存环境信息的路径
        self.env_save_path = kwargs.pop('env_save_path', './logs/')
        super(CustomEvalCallback, self).__init__(*args, **kwargs)
        
        # 创建保存目录
        if self.env_save_path is not None:
            os.makedirs(self.env_save_path, exist_ok=True)

    def _on_step(self) -> bool:
        continue_training = super()._on_step()
        
        if continue_training and self.best_mean_reward != -np.inf:
            # 保存环境信息
            self._save_env_info()
            
        return continue_training

    def _save_env_info(self):
        """保存环境信息"""
        try:
            # 保存VecNormalize环境
            if hasattr(self.model.get_vec_normalize_env(), 'save'):
                env_path = os.path.join(self.env_save_path, "best_vec_normalize.pkl")
                self.model.get_vec_normalize_env().save(env_path)
                if self.verbose > 0:
                    print(f"Saving best VecNormalize to {env_path}")
                
        except Exception as e:
            print(f"Error saving environment info: {e}")


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: Initial learning rate.
    :return: schedule that computes
      current learning rate depending on remaining progress
    """
    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining:
        :return: current learning rate
        """
        return progress_remaining * initial_value

    return func