
import libsumo as traci
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from tshub.sumo_tools.generate_detectors import generate_detector
from tshub.sumo_tools.additional_files.traffic_light_additions import generate_traffic_lights_additions

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'))

# 开启仿真 --> 指定 net 文件
netfile_path = current_file_path("./env/map.net.xml")
traci.start(["sumo", "-n", netfile_path])

# 指定要生成的路口 id 和探测器保存的位置
g_detectors = generate_detector(traci)
g_detectors.generate_multiple_detectors(
    tls_list=['INT1'], 
    result_folder=current_file_path("./add/"),
    detectors_dict={'e2':{'detector_length':45}}
)

from tshub.sumo_tools.additional_files.traffic_light_additions import generate_traffic_lights_additions
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'))

# 指定 net 文件
sumo_net = current_file_path("./env/map.net.xml")

generate_traffic_lights_additions(
    network_file=sumo_net,
    output_file=current_file_path('./add/tls.add.xml')
)