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
        # grid = self.canvas.central_widget.add_grid(spacing=0, bgcolor='black',
        #                                   border_color='k')
        # self.canvas_view = grid.add_view(row=0, col=1, margin=10,
        #                                         border_color=(0, 0, 0))

        self.canvas_view  = self.canvas.central_widget.add_view()


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

    def set_point_cloud(self, points):
        self.pointcloud_vis = visuals.Markers()
        self.pointcloud_vis.set_gl_state('translucent', depth_test=False)
        self.pointcloud_vis.set_data(points, edge_color=None, face_color=(1, 1, 1, 1), size = 2)
        self.canvas_view.add(self.pointcloud_vis)
        self.canvas_view.camera = 'turntable'  # or try 'arcball'

        # add a colored 3D axis for orientation
        axis = visuals.XYZAxis(parent=self.canvas_view.scene)


    def show(self):
        self.ui.show()





if __name__ == "__main__":
    from qt_material import apply_stylesheet

    app = QApplication([])
    apply_stylesheet(app, theme='dark_teal.xml')
    obj = View()
    obj.show()
    app.exec_()

