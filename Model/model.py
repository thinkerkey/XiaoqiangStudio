from Utils.common_utils import *



class Model():
    def __init__(self, cfg_path = "config/global_config.json") -> None:
        self.global_cfg_path = cfg_path
        self.global_cfg = parse_json(self.global_cfg_path)

    def save_global_cfg_when_close(self):
        write_json(self.global_cfg, self.global_cfg_path)