
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QSplitter
from PySide2.QtCore import QTimer, Qt
import vispy.scene
from vispy.scene import visuals
import numpy as np

class View():
    '''
        mvc模式中的视图部分，本身不包含任何逻辑，仅作界面显示使用
    '''
    def __init__(self):
        self.ui = QUiLoader().load('main.ui')
        self.canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()
        self.ui.groupbox_vis3d.layout().addWidget(self.canvas.native)
        self.spliter_dict = {}
        self.set_qspilter("main_form",
                            Qt.Horizontal,
                            [self.ui.groupbox_displays,
                                self.ui.groupbox_mainwindow,
                                self.ui.tabwidget_setting],
                            [2, 4, 2],
                            self.ui.centralwidget.layout())
        self.set_qspilter("main_win",
                            Qt.Vertical,
                            [self.ui.groupbox_vis3d,
                                self.ui.tabwidget_main],
                            [4, 2],
                            self.ui.groupbox_mainwindow.layout())
        self.signal_connect()

    def set_qspilter(self, spliter_name,
                            spliter_dir,
                            widget_list,
                            factor_list,
                            layout_set):
        # Qt.Horizontal or v
        self.spliter_dict[spliter_name] = QSplitter(spliter_dir)

        for w in widget_list:
            self.spliter_dict[spliter_name].addWidget(w)

        for i, f in enumerate(factor_list):
            self.spliter_dict[spliter_name].setStretchFactor(i, f)
        layout_set.addWidget(self.spliter_dict[spliter_name])

    def signal_connect(self):
        self.ui.pushButton.clicked.connect(self.button_clicked)

    def button_clicked(self):
        self.radomeshowVispy()

    def radomeshowVispy(self):
        pos = np.random.normal(size=(100000, 3), scale=0.2)
        centers = np.random.normal(size=(50, 3))
        indexes = np.random.normal(size=100000, loc=centers.shape[0] / 2.,
                                   scale=centers.shape[0] / 3.)
        indexes = np.clip(indexes, 0, centers.shape[0] - 1).astype(int)
        scales = 10 ** (np.linspace(-2, 0.5, centers.shape[0]))[indexes][:, np.newaxis]
        pos *= scales
        pos += centers[indexes]

        # create scatter object and fill in the data
        scatter = visuals.Markers()
        scatter.set_data(pos, edge_color=None, face_color=(1, 1, 1, .5), size=5)

        self.view.add(scatter)

        self.view.camera = 'turntable'  # or try 'arcball'

        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=self.view.scene)


    def show(self):
        self.ui.show()





if __name__ == "__main__":
    app = QApplication([])
    obj = View()
    obj.show()
    app.exec_()

