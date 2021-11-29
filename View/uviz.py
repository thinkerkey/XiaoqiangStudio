import os
import numpy as np
import math
import yaml
try:
    from yaml import CLoader as Loader
except:
    from yaml import Loader as Loader

import vispy.scene
import vispy.app
import trimesh

from vispy.util.profiler import Profiler

from vispy import scene
from vispy.scene import visuals, SceneCanvas
from vispy.color import Color

import vispy.io as vispy_file
from vispy.gloo.util import _screenshot

from vispy.scene.visuals import Polygon
from vispy.visuals import transforms
from vispy.io import load_data_file, read_png
from .box_marker import BoxMarkers
from scipy.spatial.transform import Rotation

from matplotlib import pyplot as plt
from Utils.common_utils import *



class Canvas(scene.SceneCanvas):
    """Class that creates and handles a visualizer for a pointcloud"""
    # view相当于是面板，下面可以有好多vis
    # 设计api

    def __init__(self, data_frame, **kwargs):
        scene.SceneCanvas.__init__(self, keys='interactive')
        self.unfreeze()

        if self.draw_img:
            grid = self.central_widget.add_grid(spacing=0, bgcolor='black',
                                        border_color='k')
            self.img_view = grid.add_view(row=0, col=0, margin=10,
                                        border_color=(0, 0, 0))
            #  self.img_view.stretch = [0.66, 1.0]
            self.view = grid.add_view(row=0, col=1, margin=10,
                                        border_color=(0, 0, 0))

            self.view.camera = 'turntable' # arcball
            self.img_view.camera = scene.PanZoomCamera(aspect=1)
            self.img_view.camera.flip = (0, 1, 0)
            self.img_view.camera.set_range() #FIXME: do not work
        else:
            self.view = self.central_widget.add_view()
            self.view.camera = 'turntable' # arcball



        self.color_map = {}
        self.load_color_map()

        self.boxes = None
        self.boxes2 = None
        self.traj = None
        self.data_frame = data_frame
        self.init_cloud_vis()

        if self.draw_box:
            self.init_box_vis()
            self.init_box_line_vis()
        if self.draw_obj_vel:
            self.init_obj_vel_vis()
        if self.draw_car_model:
            self.init_veh_model(self.view)
        else:
            # add xyz-axiz
            visuals.XYZAxis(parent=self.view.scene)
        if self.draw_img:
            self.init_image_vis()

        self.timer = vispy.app.Timer('auto', connect=self.do_update_local, start=False)
        self.show()

    def init_image_vis(self):
        self.image_vis = scene.visuals.Image(method = 'auto')
        self.img_view.add(self.image_vis)

    def init_cloud_vis(self):
        self.pointcloud_vis = visuals.Markers(parent=self.view.scene)
        self.pointcloud_vis.set_gl_state('translucent', depth_test=False)
        self.view.add(self.pointcloud_vis)

    def init_cloud_vis2(self):
        self.pointcloud_vis2 = visuals.Markers(parent=self.view.scene)
        self.pointcloud_vis2.set_gl_state('translucent', depth_test=False)
        self.view2.add(self.pointcloud_vis2)

    def init_box_vis(self):
        self.boxes_vis = BoxMarkers(width=0.01, height=0.01, depth=0.01)
        self.boxes_vis.transform = transforms.MatrixTransform()
        self.view.add(self.boxes_vis)

    def init_box_vis2(self):
        self.boxes_vis2 = BoxMarkers(width=0.01, height=0.01, depth=0.01)
        self.boxes_vis2.transform = transforms.MatrixTransform()
        self.view2.add(self.boxes_vis2)

    def init_obj_vel_vis(self):
        self.obj_vel_vis = visuals.Arrow(arrow_type='stealth', antialias=True,
                width=2)
        self.view.add(self.obj_vel_vis)

    def init_obj_vel_vis2(self):
        self.obj_vel_vis2 = visuals.Arrow(arrow_type='stealth', antialias=True,
                width=2)
        self.view2.add(self.obj_vel_vis2)

    def init_box_line_vis(self):
        self.box_line_vis = visuals.Line(antialias=True)
        self.view.add(self.box_line_vis)

    def init_box_line_vis2(self):
        self.box_line_vis2 = visuals.Line(antialias=True)
        self.view2.add(self.box_line_vis2)

    def init_traj_view(self):
        test = np.array([[0.0, 0.0], [0.0, 0.1]])
        self.traj_vis = visuals.Line(test, width=100, color=white)
        self.view.add(self.traj_vis)

    def init_railing_view(self):
        railing_path = 'data/railing.obj'
        self.railing_mesh = trimesh.load(railing_path, force='mesh')
        rot = Rotation.from_euler('xyz', [-90., 0., 0.], degrees=True).as_matrix()
        self.railing_mesh.vertices = np.dot(self.railing_mesh.vertices, rot)
        maxx = np.max(self.railing_mesh.vertices, axis=0)
        minn = np.min(self.railing_mesh.vertices, axis=0)
        self.railing_actual_len = maxx[0] - minn[0]
        self.railing_vis = visuals.Mesh(shading='smooth', color=white)
        self.view.add(self.railing_vis)

    def init_veh_model(self, view):
        #  stl_path = 'data/beetle.stl'
        stl_path = 'data/toyota.stl'
        car_mesh = trimesh.load(stl_path)
        mesh_vis = visuals.Mesh(vertices=car_mesh.vertices, faces=car_mesh.faces,
                shading='smooth',
                color=self.color_map['car_model'])
        # The size of model from internet is not the actual size of a car
        # and the face direction need adjust
        mesh_vis.transform = transforms.MatrixTransform()
        mesh_vis.transform.scale((0.035, 0.035, 0.035))
        mesh_vis.transform.rotate(-90, (0, 0, 1))
        view.add(mesh_vis)

    @property
    def visuals(self):
        """List of all 3D visuals on this canvas."""
        return [v for v in self.view.children[0].children if isinstance(v, scene.visuals.VisualNode)]

    def load_color_map(self):
        with open('config/color.yml', 'r') as c:
            color_map = yaml.load(c, Loader=Loader)

        for ke in color_map:
            self.color_map[ke] = Color(color_map[ke])

    def do_update_local(self, event):
        # TODO: time comsuming
        self.load_color_map()

        self.points, self.colors = self.data_frame.get_points(self.frame_idx)

        if self.colors is not None:
            face_color = edge_color = self.colors
        else:
            face_color = edge_color = Color(self.color_map['cloud'])

        range_data = np.linalg.norm(self.points2[:, :2], 2, axis=1)
        viridis_range = ((range_data - range_data.min()) /
                        (range_data.max() - range_data.min()) *
                        255).astype(np.uint8)
        viridis_map = self.get_mpl_colormap("GnBu")
        viridis_colors = viridis_map[viridis_range]
        face_color = edge_color = viridis_colors[..., ::-1]

        self.pointcloud_vis.set_data(self.points,
                edge_color=edge_color,
                face_color=face_color,
                size=1)


        if self.draw_box:
            self.boxes = self.data_frame.get_boxes(self.frame_idx)
            self.add_box()
            self.add_box_line(self.boxes, self.box_line_vis)

            if self.draw_obj_vel:
                self.add_obj_vel()

        if self.draw_traj:
            self.traj = self.data_frame.get_traj(self.frame_idx)
            self.add_traj()

        if self.draw_railing:
            self.railing_pos = self.data_frame.get_railing(self.frame_idx)
            self.add_railing()

        if self.draw_img:
            self.img_data = read_png(load_data_file(self.data_frame.get_img(self.frame_idx)))
            self.add_img()

        self.frame_idx += self.offset
        if self.frame_idx >= self.total:
            self.frame_idx = 0
        elif self.frame_idx < 0:
            self.frame_idx = self.total - 1

    def clear_box(self):
        for v in self.visuals:
            if isinstance(v, BoxMarkers):
                v.parent = None

    def add_img(self):
        self.image_vis.set_data(self.img_data)

    def add_railing(self):
        start_pos, end_pos = self.railing_pos[0], self.railing_pos[-1]

        mesh = self.railing_mesh
        seg_len = np.linalg.norm(end_pos - start_pos)
        num = math.ceil(seg_len / self.railing_actual_len)

        theta = math.atan2(end_pos[1]-start_pos[1], end_pos[0]-start_pos[0])
        rot = Rotation.from_euler('xyz', [0., 0., theta]).as_matrix()

        # rotate & copy
        vertices = np.dot(mesh.vertices, rot)
        vertices = np.tile(vertices, (num, 1))
        # translate
        fa = np.linspace(start_pos, end_pos, num=num)
        new_x = np.repeat(fa[:, 0], mesh.vertices.shape[0])
        new_y = np.repeat(fa[:, 1], mesh.vertices.shape[0])
        vertices[:, 0] = vertices[:, 0] + new_x
        vertices[:, 1] = vertices[:, 1] + new_y

        faces = np.tile(mesh.faces, (num, 1))
        face_num = np.max(mesh.faces) + 1
        fa = np.repeat(np.arange(num), mesh.faces.shape[0])
        fa_id = fa * face_num
        fa_id = fa_id.reshape(-1, 1)
        fa_id = np.repeat(fa_id, 3, axis=1)
        faces += fa_id
        self.railing_vis.set_data(vertices=vertices,
                faces=faces)

    def add_traj(self):
        self.traj_vis.set_data(self.traj, width=100)

    def prepare_box_data(self, boxes, enlarge_ratio=1.0):
        pos = []
        width = []
        height = []
        depth = []
        theta = []
        for b in boxes:
            pos.append([b.x, b.y, b.z])
            width.append([b.width])
            height.append([b.length])
            depth.append([b.height])
            theta.append([b.dir])

        pos = np.array(pos)
        # enlarge box a little bit
        width = np.array(width) * enlarge_ratio
        height = np.array(height) * enlarge_ratio
        depth = np.array(depth) * enlarge_ratio
        theta = np.array(theta)
        return pos, width, height, depth, theta

    def prepare_box_color(self, boxes, lightness_ratio=1.0, opacity=1.0):
        fc = []
        for b in boxes:
            rgba = self.color_map[self.label_map[b.kind]].rgba
            if lightness_ratio != 1.0:
                rgba[:3] = scale_lightness(rgba[:3], lightness_ratio)
            fc.append(rgba)
        fc = np.array(fc)
        ec = np.copy(fc)
        fc[..., 3] = opacity
        return fc, ec

    def add_box(self):
        pos, width, height, depth, theta = self.prepare_box_data(self.boxes)
        if pos.shape[0] < 1: return

        fc, ec = self.prepare_box_color(self.boxes, opacity = 0.8)
        self.boxes_vis.set_data(pos, width=width, height=height, depth=depth, face_color=fc,
            edge_color=ec, rotation=theta)

    def add_box2(self):
        pos, width, height, depth, theta = self.prepare_box_data(self.boxes2)
        if pos.shape[0] < 1: return

        fc, ec = self.prepare_box_color(self.boxes2, opacity = 0.8)
        self.boxes_vis2.set_data(pos, width=width, height=height, depth=depth, face_color=fc,
            edge_color=ec, rotation=theta)

    def create_box_vertex(self, pos, width, length, height, rotation):

        rotation_mat = []
        for theta in rotation:
            rotation_mat.append(Rotation.from_euler('xyz', [0., 0., theta]).as_matrix())

        box_vertex = np.array([[-0.5, -0.5, -0.5],
                               [-0.5, -0.5, 0.5],
                               [0.5, -0.5, -0.5],
                               [0.5, -0.5, 0.5],
                               [0.5, 0.5, -0.5],
                               [0.5, 0.5, 0.5],
                               [-0.5, 0.5, -0.5],
                               [-0.5, 0.5, 0.5]])
        nb_v = box_vertex.shape[0]

        scale = np.hstack((width, length, height))

        vertices = np.zeros((nb_v * pos.shape[0], 3))
        p_idx = []
        for i in range(pos.shape[0]):
            idx_v_start  = nb_v*i
            idx_v_end    = nb_v*(i+1)

            vertices[idx_v_start:idx_v_end] = box_vertex*scale[i]
            vertices[idx_v_start:idx_v_end] = \
                np.dot(vertices[idx_v_start:idx_v_end], rotation_mat[i])
            vertices[idx_v_start:idx_v_end] += pos[i]

            for j in range(nb_v):
                p_idx.append((j + idx_v_start, (2 + j) % nb_v + idx_v_start))
            for j in range(int(nb_v / 2)):
                p_idx.append((2 * j + idx_v_start, 2 *j + 1 + idx_v_start))
        return vertices, np.array(p_idx)

    def add_box_line(self, boxes, box_line_vis):
        pos, width, height, depth, theta = self.prepare_box_data(boxes)

        if pos.shape[0] < 1: return

        fc, _ = self.prepare_box_color(boxes, lightness_ratio = 1.0)
        fc = np.tile(fc, 8).reshape(-1, 4)

        vertex_point, p_idx = self.create_box_vertex(pos,
                width, height, depth, theta)

        box_line_vis.set_data(pos=vertex_point, connect=p_idx, color=fc, width=1)

    def add_obj_vel(self):
        pos = []
        pos_pair = []
        arrow = []
        for i, b in enumerate(self.boxes):
            theta = np.pi * 0.5 - b.dir
            vel = b.vel * 0.5
            x = b.x + vel * math.cos(theta)
            y = b.y + vel * math.sin(theta)
            pos.append([b.x, b.y, b.z])
            pos.append([x, y, b.z])
            pos_pair.append((2 * i, 2 * i + 1))

            arrow.append([b.x, b.y, b.z, x, y, b.z])

        pos = np.array(pos)
        arrow = np.array(arrow)

        self.obj_vel_vis.set_data(pos, connect='segments', arrows=arrow, width=4)


    def get_mpl_colormap(self, cmap_name):
        cmap = plt.get_cmap(cmap_name)

        # Initialize the matplotlib color map
        sm = plt.cm.ScalarMappable(cmap=cmap)
        # Obtain linear color range
        color_range = sm.to_rgba(np.linspace(0, 1, 256), bytes=True)[:, 2::-1]
        return color_range.reshape(256, 3).astype(np.float32) / 255.0

    def destroy(self):
        # destroy the visualization
        self.close()
        vispy.app.quit()

    def run(self):
        vispy.app.run()
