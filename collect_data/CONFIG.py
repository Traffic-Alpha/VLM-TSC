'''
Author: WANG Maonan
Date: 2025-06-25 16:50:28
LastEditors: WANG Maonan
Description: 场景信息 (netrwork+route+event) 三个部分组成一个场景
-> Note: 需要提前在 route 中定义好对应的车辆类型
LastEditTime: 2025-07-17 15:54:14
'''
SCENARIO_CONFIGS = {
    "Beijing_Beishahe_Normal": {
        "SCENARIO_NAME": "Beijing_Beishahe",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 800,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (450, 400, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": [
            {
                "id": "accident_01",  # 事故唯一标识符
                "depart_time": 20,    # 事故发生的仿真时间（秒）
                "edge_id": "741602130.216",  # 事故 Edge ID
                "lane_index": 2,          # 发生事故的 lane index
                "position": 167,    # 在车道上的位置（米）, 车道长度-1
                "duration": 50,   # 事故持续时间（秒），0=永久
            }, # 事故一
        ],
        # ================== 特殊车辆配置 ==================
        "SPECIAL_VEHICLES": None
    },
    
    "Hongkong_YMT_NORMAL": {
        # ================== 基础场景参数 ==================
        "SCENARIO_NAME": "Hongkong_YMT", # 场景所在文件夹
        "SUMOCFG": "ymt_normal.sumocfg", # sumocfg 中包含 route & network 的组合
        "NETFILE": "./env_normal/YMT.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "J1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3, # Phase 数量
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (172, 201, 60),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:0, 3:1},
        # ==================== 事故配置 ====================
        "ACCIDENTS": [
            {
                "id": "accident_01",  # 事故唯一标识符
                "depart_time": 20,          # 事故发生的仿真时间（秒）
                "edge_id": "30658263#0",  # 事故 Edge ID
                "lane_index": 0,          # 发生事故的 lane index
                "position": 99,    # 在车道上的位置（米）, 车道长度-1
                "duration": 50,   # 事故持续时间（秒），0=永久
            }, # 事故一
            {
                "id": "accident_02",  # 事故唯一标识符
                "depart_time": 100,          # 事故发生的仿真时间（秒）
                "edge_id": "30658263#0",  # 事故 Edge ID
                "lane_index": 1,          # 发生事故的 lane index
                "position": 99,    # 在车道上的位置（米）
                "duration": 20,   # 事故持续时间（秒），0=永久
            }, # 事故二
            {
                "id": "accident_03",  # 事故唯一标识符
                "depart_time": 100,          # 事故发生的仿真时间（秒）
                "edge_id": "30658263#0",  # 事故 Edge ID
                "lane_index": 2,          # 发生事故的 lane index
                "position": 99,    # 在车道上的位置（米）
                "duration": 20,   # 事故持续时间（秒），0=永久
            }, # 事故三
        ],
        # ================== 特殊车辆配置 ==================
        "SPECIAL_VEHICLES": [
            {
                "id": "ambulance_01", # 车辆唯一ID
                "type": "emergency",  # 车辆类型
                "depart_time": 10, # 出发时间(秒)
                "route": ["960661806#0", "102640426#0"],  # 行驶路线
            },
            {
                "id": "police_01",
                "type": "police",
                "depart_time": 100,
                "route": ["102454134#0", "102640432#0"],
            },
        ]
    },
    "SouthKorea_Songdo": {
        "SCENARIO_NAME": "SouthKorea_Songdo",
        "SUMOCFG": "songdo_eval",
        "JUNCTION_NAME": "J2",
        "PHASE_NUMBER": 4,
        "CENTER_COORDINATES": (900, 1641, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0}
    },
    "France_Massy": {
        "SCENARIO_NAME": "France_Massy",
        "SUMOCFG": "massy_eval",
        "JUNCTION_NAME": "INT1",
        "PHASE_NUMBER": 3,
        "CENTER_COORDINATES": (173, 244, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0}
    }
}