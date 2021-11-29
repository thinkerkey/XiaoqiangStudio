from Utils.point_cloud_utils import *
from View.view import View
from Model.model import Model
from qt_material import apply_stylesheet
from PySide2.QtWidgets import QApplication
import os.path as osp
from Utils.common_utils import *
from log_sys import *
from PySide2.QtCore import QTimer, Qt

class Controller():
    def __init__(self) -> None:
        self.app = QApplication([])
        self.view = View()
        self.model = Model()
        # for update log info
        self.Timer = QTimer()
        self.view.add_topic_type(self.model.global_cfg["has_sub_topic"].keys())
        self.Timer.start(50)
        self.Timer.timeout.connect(self.monitor_timer)

        self.index = 0
        self.signal_connect()
        send_log_msg(NORMAL, "欢迎使用vis studio~")
        self.model.start()

    def run(self):
        apply_stylesheet(self.app, theme=self.model.global_cfg['theme'])
        self.view.show()
        self.app.exec_()
        self.model.save_global_cfg_when_close()


    def signal_connect(self):
        self.ui.button_add_topic.clicked.connect(self.add_topic)
        self.view.ui.menu_theme.triggered.connect(self.change_theme)


    def add_topic(self):
        pass

    def change_theme(self, theme):
        curr_theme = theme.text() + ".xml"
        self.model.global_cfg["theme"] = curr_theme
        apply_stylesheet(self.app, theme=curr_theme)

    def button_clicked(self):
        curr_bin_path = osp.join("data/point_cloud", str(self.index).zfill(6) + ".bin")
        print(curr_bin_path)
        curr_points = read_bin(curr_bin_path)[0]
        self.view.set_point_cloud(curr_points)
        self.index += 1

    def monitor_timer(self):
        get_msg = ret_log_msg()
        if get_msg != []:
            self.view.display_append_msg_list(get_msg)

    def sigint_handler(self, signum = None, frame = None):
        self.model.save_global_cfg_when_close()




if __name__=="__main__":
    obj = Controller()
    obj.run()