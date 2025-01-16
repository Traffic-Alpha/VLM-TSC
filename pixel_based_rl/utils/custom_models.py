'''
Author: Maonan Wang
Date: 2025-01-16 14:24:41
LastEditTime: 2025-01-16 15:51:51
LastEditors: Maonan Wang
Description: ResNet18 for Image Input
FilePath: /VLM-TSC/pixel_based_rl/utils/custom_models.py
'''
import torchvision
import torch.nn as nn
import gymnasium as gym
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomModel(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 16):
        """特征提取网络
        """
        super().__init__(observation_space, features_dim)
        image_num, height, width, channel = observation_space.shape

        self.backbone_model = torchvision.models.resnet18()
        self.backbone_model.conv1 = nn.Conv2d(
            in_channels=image_num*channel, # 只修改了 input channel, 将图片在通道层面合并
            out_channels=64,
            kernel_size=7,
            stride=2, padding=3,
            bias=False
        )
        self.backbone_model.fc = nn.Identity() # 最后一层作为特征输出

        self.image_transfomer = torchvision.transforms.Compose([
            torchvision.transforms.Lambda(lambda x: x/255.0), # 归一化为 0-1
            torchvision.transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
        ])

    def forward(self, observations):
        batch_size, image_nums, height, width, channel = observations.shape

        new_obs = self.image_transfomer(
            observations.view(batch_size*image_nums, channel, height, width)
        ).view(batch_size, image_nums*channel, height, width)
        img_embedding = self.backbone_model(new_obs)
        return img_embedding