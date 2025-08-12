'''
Author: WANG Maonan
Date: 2025-06-30 22:04:19
LastEditors: WANG Maonan
Description: Simple Network for the Junction
LastEditTime: 2025-08-11 18:25:00
'''
import torch
import torch.nn as nn
import gymnasium as gym
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class IntersectionNet(BaseFeaturesExtractor):
    def __init__(
            self, observation_space: gym.Space, 
            features_dim:int, 
            embed_dim=32,
            lstm_hidden_dim=64,
            num_lstm_layers=1,
            bidirectional=True,
        ):
        """十字路口信息处理网络
        参数:
            embed_dim: 特征嵌入维度 (默认32)
            lstm_hidden_dim: LSTM 隐藏层维度 (默认64)
            num_lstm_layers: LSTM 层数 (默认1)
            bidirectional: 是否使用双向 LSTM (默认True)
        """
        super().__init__(observation_space, features_dim)
        movement_dim = observation_space.shape[-1] # 每个 movement 的特征
        
        # 特征嵌入层 (处理每个 movement 的特征)
        self.embed = nn.Sequential(
            nn.Linear(movement_dim, embed_dim),
            nn.ReLU(),
            nn.LayerNorm(embed_dim)
        )
        
        # 时间序列处理
        self.lstm = nn.LSTM(
            input_size=embed_dim,
            hidden_size=lstm_hidden_dim,
            num_layers=num_lstm_layers,
            bidirectional=bidirectional,
            batch_first=True
        )
        
        # 计算最终输出维度（双向 LSTM*2）
        self.lstm_output_dim = lstm_hidden_dim * 2 if bidirectional else lstm_hidden_dim

        # 特征输出层
        self.output_proj = nn.Linear(self.lstm_output_dim, features_dim)
        
    def forward(self, x):
        """
        输入:
            x: 形状 [bs, T, M, F] = [batch_size, 时序数, Movement数, 特征维度]
        输出:
            十字路口的特征表示 [bs, features_dim]
        """
        bs, T, M, F = x.shape
        
        # 1. 特征嵌入: 处理每个 Movement 的特征
        x_flat = x.reshape(-1, F)
        embedded = self.embed(x_flat)  # [bs*T*M, embed_dim]
        embedded = embedded.reshape(bs, T, M, -1)  # [bs, T, M, embed_dim]
        
        # 2. Movement维度最大池化
        movement_pooled, _ = torch.max(embedded, dim=2)  # [bs, T, embed_dim]
        
        # 3. 时序处理
        lstm_out, _ = self.lstm(movement_pooled)  # [bs, T, lstm_hidden_dim * 2（双向）]
        
        # 4. 时间维度最大池化
        time_pooled, _ = torch.max(lstm_out, dim=1)  # [bs, lstm_hidden_dim * 2]
        
        # 5. 调整输出维度（如果 LSTM 输出维度不等于 features_dim）
        output = self.output_proj(time_pooled)  # [bs, features_dim]
        
        return output