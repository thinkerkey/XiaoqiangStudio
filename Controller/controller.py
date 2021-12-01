from time import sleep

import numpy
from numpy.__config__ import show
from numpy.lib.type_check import imag
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
        self.view.ui.need_sub_text.returnPressed.connect(self.add_topic)

    def display_clicked(self, item):
        # print(item.parent())
        pass

    def display_setting_changed(self, item, col):
        # print(item, col)
        pass

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
            if  data_type == "image":
                self.view.add_img_view(need_topic)


    def point_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的point msg"%topic)
        # self.view.canvas.draw_point_cloud("point_cloud", msg["points"])
        self.view.set_point_cloud(msg["points"], show=1)
        print(msg.keys())

    def image_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的image msg"%topic)
        # print(np.ndarray(msg['img']))
        # self.view.set_images(np.array(msg['img']), show=1, topic=topic)

    def bbox_callback(self, msg, topic):
        send_log_msg(NORMAL, "收到来自%s的bbox msg"%topic)

    def change_theme(self, theme):
        curr_theme = theme.text() + ".xml"
        self.model.global_cfg["theme"] = curr_theme
        apply_stylesheet(self.app, theme=curr_theme)

    index = 0
    def button_clicked(self):
        from vispy.io import read_png

        curr_index_str = str(self.index).zfill(6)
        curr_bin_path = osp.join("/home/uisee/Workspace/ULab/UTracking/datasets/nuscenes/point_cloud", curr_index_str + ".bin")
        curr_label_path = osp.join("data/bbox_track", curr_index_str + ".txt")
        try:
            curr_text = np.loadtxt(curr_label_path)

            self.view.set_bboxes(curr_text, show = 1, )
        except:
            print("empty")
        curr_image1_path = osp.join("data/image_CAM_FRONT", curr_index_str + ".jpg")
        # curr_image2_path = osp.join("data/image_CAM_BACK", curr_index_str + ".jpg")

        img1 = read_png(curr_image1_path)
        # img2 = read_png(curr_image2_path)
        # print(img1.shape)
        self.view.set_images(img1, show=1, topic="image1")
        # self.view.set_images(img2, show=1, topic="image2")

        curr_points = read_bin(curr_bin_path)[0]
        self.view.set_point_cloud(curr_points, show=1)
        # self.model.pub("points", {"points":curr_points})
        # self.model.pub("image1", {"img":img1})
        # self.model.pub("image2", {"img":img2})
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