'''
Author: WANG Maonan
Date: 2025-06-25 16:50:28
LastEditors: WANG Maonan
Description: 场景信息, 这里和 collect data 里面的 config 是一样的
LastEditTime: 2025-07-29 15:18:51
'''
SCENARIO_CONFIGS = {
    "Beijing_Changjianglu_Test": {
        "SCENARIO_NAME": "Beijing_Changjianglu",
        "SUMOCFG": "easy_fluctuating_commuter.sumocfg",
        "NETFILE": "./networks/easy.net.xml",
        "JUNCTION_NAME": "INT1",
        "NUM_SECONDS": 500,
        "PHASE_NUMBER": 3,
        "MOVEMENT_NUMBER": 6, 
        "CENTER_COORDINATES": (933, 175, 100),
        "SENSOR_INDEX_2_PHASE_INDEX": {0:2, 1:1, 2:0},
        "ACCIDENTS": None,
        "SPECIAL_VEHICLES": None
    },
}