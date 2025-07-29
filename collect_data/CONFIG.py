'''
Author: WANG Maonan
Date: 2025-06-25 16:50:28
LastEditors: WANG Maonan
Description: 场景信息 (netrwork+route+event) 三个部分组成一个场景
-> Note: 需要提前在 route 中定义好对应的车辆类型
LastEditTime: 2025-07-29 16:02:03
'''
SCENARIO_CONFIGS = {
    # ===> Beijing_Beishahe
    "Beijing_Beishahe_Test": {
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
    
    # ===> Beijing_Changjianglu
    "Beijing_Changjianglu_Test": {
        "SCENARIO_NAME": "Beijing_Changjianglu",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (933, 175, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": None,
        # ================== 特殊车辆配置 ==================
        "SPECIAL_VEHICLES": None
    },
    # 包含特殊事件
    "Beijing_Changjianglu_Event": {
        "SCENARIO_NAME": "Beijing_Changjianglu",
        "SUMOCFG": "easy_fluctuating_commuter.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (933, 175, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": [
            {
                "id": "accident_01",  # 事故唯一标识符
                "depart_time": 100,    # 事故发生的仿真时间（秒）
                "edge_id": "832511541#0.628",  # 事故 Edge ID
                "lane_index": 2,          # 发生事故的 lane index
                "position": 283,    # 在车道上的位置（米）, 车道长度-1
                "duration": 50,   # 事故持续时间（秒），0=永久
            }, # 事故一
        ],
        "SPECIAL_VEHICLES": [
            {
                "id": "ambulance_01", # 车辆唯一ID
                "type": "emergency",  # 车辆类型
                "depart_time": 200, # 出发时间(秒)
                "route": ["832511541#0.628", "606446493#4"],
            },
            {
                "id": "fire_01",
                "type": "fire_engine",
                "depart_time": 300,
                "route": ["606446495#0.451", "606446495#5"],
            },
        ]
    },

    # ===> Beijing_Gaojiaoyuan
    "Beijing_Gaojiaoyuan_Test": {
        "SCENARIO_NAME": "Beijing_Gaojiaoyuan",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (944, 438, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> Beijing_Pinganli
    "Beijing_Pinganli_Test": {
        "SCENARIO_NAME": "Beijing_Pinganli",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (1435, 960, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> Beijing_Yongrunlu
    "Beijing_Yongrunlu_Test": {
        "SCENARIO_NAME": "Beijing_Yongrunlu",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (395, 895, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> Chengdu_Chenghannanlu
    "Chengdu_Chenghannanlu_Test": {
        "SCENARIO_NAME": "Chengdu_Chenghannanlu",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (420, 62, 50),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> Chengdu_Guanghua
    "Chengdu_Guanghua_Test": {
        "SCENARIO_NAME": "Chengdu_Guanghua",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (488, 322, 50),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },
    
    # ===> Tianjin_zhijingdao
    "Tianjin_zhijingdao_Test": {
        "SCENARIO_NAME": "Tianjin_zhijingdao",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (1733, 1170, 50),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None,
    },

    # ===> Beijing Beihuan
    "Beijing_Beihuan_Test": {
        "SCENARIO_NAME": "Beijing_Beihuan",
        "SUMOCFG": "easy_high_density.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 600,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (835, 360, 50),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> Hongkong_YMT
    "Hongkong_YMT_Test": {
        "SCENARIO_NAME": "Hongkong_YMT", # 场景所在文件夹
        "SUMOCFG": "easy.sumocfg", # sumocfg 中包含 route & network 的组合
        "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "J1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3, # Phase 数量
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (172, 201, 60),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:0, 3:1},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> France_Massy
    "France_Massy_Test": {
        "SCENARIO_NAME": "France_Massy",
        "SUMOCFG": "easy.sumocfg",
        "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (173, 244, 60),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },

    # ===> SouthKorea_Songdo
    "SouthKorea_Songdo_Test": {
        "SCENARIO_NAME": "SouthKorea_Songdo",
        "SUMOCFG": "easy.sumocfg",
        "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "J2",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4,
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (900, 1641, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:3, 2:1, 3:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
        },

    # ===>
    "Building_EVENETS": {
        # ================== 基础场景参数 ==================
        "SCENARIO_NAME": "Buildings", # 场景所在文件夹
        "SUMOCFG": "easy.sumocfg", # sumocfg 中包含 route & network 的组合
        "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "J0",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4, # Phase 数量
        "MOVEMENT_NUMBER": 12, 
        "CENTER_COORDINATES": (39.84, -14.45, 60),
        "SENSOR_INDEX_2_PHASE_INDEX": None,
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },
    # "Building_EVENETS": {
    #     # ================== 基础场景参数 ==================
    #     "SCENARIO_NAME": "Buildings", # 场景所在文件夹
    #     "SUMOCFG": "easy.sumocfg", # sumocfg 中包含 route & network 的组合
    #     "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
    #     "JUNCTION_NAME": "J0",
    #     "NUM_SECONDS": 500,
    #     "PHASE_NUMBER": 4, # Phase 数量
    #     "MOVEMENT_NUMBER": 12, 
    #     "CENTER_COORDINATES": (39.84, -14.45, 60),
    #     "SENSOR_INDEX_2_PHASE_INDEX": None,
    #     # ==================== 事故配置 ====================
    #     "ACCIDENTS": [
    #         {
    #             "id": "accident_01",  # 事故唯一标识符
    #             "depart_time": 20,          # 事故发生的仿真时间（秒）
    #             "edge_id": "-E0",  # 事故 Edge ID
    #             "lane_index": 0,          # 发生事故的 lane index
    #             "position": 160,    # 在车道上的位置（米）, 车道长度-1
    #             "duration": 50,   # 事故持续时间（秒），0=永久
    #         }, # 事故一
    #         {
    #             "id": "accident_02",  # 事故唯一标识符
    #             "depart_time": 100,          # 事故发生的仿真时间（秒）
    #             "edge_id": "-E0",  # 事故 Edge ID
    #             "lane_index": 1,          # 发生事故的 lane index
    #             "position": 160,    # 在车道上的位置（米）
    #             "duration": 20,   # 事故持续时间（秒），0=永久
    #         }, # 事故二
    #         {
    #             "id": "accident_03",  # 事故唯一标识符
    #             "depart_time": 100,          # 事故发生的仿真时间（秒）
    #             "edge_id": "-E0",  # 事故 Edge ID
    #             "lane_index": 2,          # 发生事故的 lane index
    #             "position": 160,    # 在车道上的位置（米）
    #             "duration": 20,   # 事故持续时间（秒），0=永久
    #         }, # 事故三
    #     ],
    #     # ================== 特殊车辆配置 ==================
    #     "SPECIAL_VEHICLES": [
    #         {
    #             "id": "ambulance_01", # 车辆唯一ID
    #             "type": "emergency",  # 车辆类型
    #             "depart_time": 10, # 出发时间(秒)
    #             "route": ["E1", "E0"],  # 行驶路线
    #         },
    #         {
    #             "id": "fire_01",
    #             "type": "fire_engine",
    #             "depart_time": 20,
    #             "route": ["E1", "E0"],
    #         },
    #         {
    #             "id": "police_01",
    #             "type": "police",
    #             "depart_time": 30,
    #             "route": ["E1", "E0"],
    #         },
    #     ]
    # },
    
    # ===> 
    "Hongkong_YMT_EVENETS": {
        # ================== 基础场景参数 ==================
        "SCENARIO_NAME": "Hongkong_YMT", # 场景所在文件夹
        "SUMOCFG": "easy.sumocfg", # sumocfg 中包含 route & network 的组合
        "NETFILE": "./networks/easy.net.xml", # 需要 network 加载地图信息
        "JUNCTION_NAME": "J1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 4, # Phase 数量
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
                "id": "fire_01",
                "type": "fire_engine",
                "depart_time": 20,
                "route": ["960661806#0", "102640426#0"],
            },
            {
                "id": "police_01",
                "type": "police",
                "depart_time": 30,
                "route": ["960661806#0", "102640426#0"],
            },
        ]
    },
}