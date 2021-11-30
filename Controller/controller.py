from time import sleep

import numpy
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
        self.view.add_topic_type(self.model.global_cfg["base_data_type"].keys())
        self.Timer.start(50)
        self.Timer.timeout.connect(self.monitor_timer)

        self.index = 0
        self.signal_connect()
        send_log_msg(NORMAL, "欢迎来到 Xiaoqiang Studio~")
        self.model.start()

    def run(self):
        apply_stylesheet(self.app, theme=self.model.global_cfg['theme'])
        self.view.show()
        self.model.quit()
        self.app.exec_()
        self.model.save_global_cfg_when_close()


    def signal_connect(self):
        self.view.ui.pushButton.clicked.connect(self.button_clicked)
        self.view.ui.button_add_topic.clicked.connect(self.add_topic)
        self.view.ui.menu_theme.triggered.connect(self.change_theme)
        self.view.ui.tree_widget_for_display.itemChanged.connect(self.display_setting_changed)
        self.view.ui.tree_widget_for_display.clicked.connect(self.display_clicked)

    def display_clicked(self, item):
        print(item)

    def display_setting_changed(self, item, col):
        print(item, col)

    def add_topic(self):
        need_topic = self.view.get_sub_topic_text()
        if need_topic == "":
            send_log_msg(ERROR, "请填写需要订阅的话题")
        else:
            data_type = self.view.get_data_type_text()
            fun_name = data_type + "_callback"
            callback_fun = getattr(self, fun_name, None)
            self.model.sub(need_topic, callback_fun)
            send_log_msg(NORMAL, "已订阅Topic: %s"%need_topic)
            self.view.add_tree_widget(
                    self.model.global_cfg['base_data_type'][data_type],
                    data_type,
                    need_topic)

    def point_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的point msg"%topic)
        self.view.canvas.draw_point_cloud("point_cloud", numpy.array(msg["points"]))
        print(msg.keys())

    def image_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的image msg"%topic)

    def bbox_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的bbox msg"%topic)

    def change_theme(self, theme):
        curr_theme = theme.text() + ".xml"
        self.model.global_cfg["theme"] = curr_theme
        apply_stylesheet(self.app, theme=curr_theme)

    index = 0
    def button_clicked(self):
        curr_bin_path = osp.join("data/point_cloud", str(self.index).zfill(6) + ".bin")
        print(curr_bin_path)
        curr_points = read_bin(curr_bin_path)[0]
        self.model.pub("points", {"points":curr_points.tolist()})
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