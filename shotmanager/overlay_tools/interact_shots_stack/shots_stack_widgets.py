# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
UI in BGL for the Interactive Shots Stack overlay tool
"""

from collections import defaultdict

import bpy
import bgl
import blf
import gpu
from mathutils import Vector

from shotmanager.utils.utils import gamma_color, color_is_dark

from .shots_stack_bgl import Image2D, Mesh2D, build_rectangle_mesh, get_lane_origin_y

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
LANE_HEIGHT = 18


class BL_UI_ShotClip:
    def __init__(self, context, lane, shot_index):
        """
        shot_index is the index of the shot in the whole take list
        """
        self.context = context

        self.height = LANE_HEIGHT
        self.width = 0
        self.lane = lane

        self._highlight = False
        self._active_region = None
        self._active_clip_over = False

        self.clip_mesh = None
        self.contour_mesh = None
        self.contourCurrent_mesh = None
        self.camIcon = None
        self.start_interaction_mesh = None
        self.end_interaction_mesh = None
        self.origin = None

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)

        self._shot_index = shot_index
        self._name_color_light = (0.9, 0.9, 0.9, 1)
        self._name_color_dark = (0.12, 0.12, 0.12, 1)
        self._name_color_disabled = (0.6, 0.6, 0.6, 1)

        self._shot_color = (0.8, 0.3, 0.3, 1.0)
        self._shot_color_disabled = (0.1, 0.1, 0.1, 0.5)

        # self.color_selectedShot_border = (0.9, 0.9, 0.2, 0.99)
        #    self.color_selectedShot_border = (0.2, 0.2, 0.2, 0.99)  # dark gray
        self.color_selectedShot_border = (0.95, 0.95, 0.95, 0.9)  # white

        # self.update()

    def update(self):
        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        self.width = shot.end - shot.start + 1
        self.origin = Vector([shot.start, get_lane_origin_y(self.lane)])
        self.clip_mesh = build_rectangle_mesh(self.origin, self.width, self.height)
        self.start_interaction_mesh = build_rectangle_mesh(self.origin, 1, self.height)
        self.end_interaction_mesh = build_rectangle_mesh(self.origin + Vector([self.width - 1, 0]), 1, self.height)
        self.contour_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        self.contourCurrent_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        # self.contourCurrent_mesh = build_rectangle_mesh(
        #     Vector([self.origin.x - 1, self.origin.y - 1]), self.width + 2, self.height + 2, True
        # )
        self.camIcon = Image2D(self.origin, self.width, self.height)

    @property
    def shot_index(self):
        return self._shot_index

    @shot_index.setter
    def shot_index(self, value):
        self._shot_index = value

    @property
    def shot_color(self):
        return self._shot_color

    @shot_color.setter
    def shot_color(self, value):
        self._shot_color = (value[0], value[1], value[2], 0.5)

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value: bool):
        self._highlight = value

    @property
    def active_region(self):
        return self._active_region

    @active_region.setter
    def active_region(self, value):
        self._active_region = value

    @property
    def active_clip_over(self):
        return self._active_clip_over

    @active_clip_over.setter
    def active_clip_over(self, value: bool):
        self._active_clip_over = value

    def draw(self):
        context = self.context
        props = context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        bgl.glEnable(bgl.GL_BLEND)
        UNIFORM_SHADER_2D.bind()

        self.shot_color = shot.color
        color = gamma_color(self.shot_color)

        if not shot.enabled:
            color = self._shot_color_disabled
            # color = (0.15, 0.15, 0.15, 0.5)

        if self.highlight:
            _logger.debug_ext(f"highlight Shot in draw", col="RED", tag="SHOTSTACK_EVENT")
            color = (0.9, 0.9, 0.9, 0.5)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        self.clip_mesh.draw(UNIFORM_SHADER_2D, context.region)

        # handles highlight
        if self.active_clip_over and self.highlight and 0 != self.active_region:
            # left handle
            if -1 == self.active_region:
                self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
                color = (0.9, 0.0, 0.0, 0.5)
                UNIFORM_SHADER_2D.uniform_float("color", color)
                self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
            # right handle
            elif 1 == self.active_region:
                self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
                color = (0.9, 0.0, 0.0, 0.5)
                UNIFORM_SHADER_2D.uniform_float("color", color)
                self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
        else:
            self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
            self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)

        # current_shot = props.getCurrentShot()
        # selected_shot = props.getSelectedShot()
        current_shot_ind = props.getCurrentShotIndex()
        selected_shot_ind = props.getSelectedShotIndex()

        # current shot
        # if current_shot != -1 and self.name == current_shot.name:
        if self.shot_index == current_shot_ind:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_currentShot_border)
            self.contourCurrent_mesh.linewidth = 4 if current_shot_ind == selected_shot_ind else 2
            self.contourCurrent_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # selected shot
        # if current_shot != -1 and self.name == selected_shot.name:
        if self.shot_index == selected_shot_ind:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_selectedShot_border)
            self.contour_mesh.linewidth = 1 if current_shot_ind == selected_shot_ind else 2
            self.contour_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # draw a camera icon on the current shot
        # TODO finish and clean
        #   self.camIcon.draw(context.region)

        bgl.glDisable(bgl.GL_BLEND)

        if shot.enabled:
            if color_is_dark(color, 0.4):
                blf.color(0, *self._name_color_light)
            else:
                blf.color(0, *self._name_color_dark)
        else:
            blf.color(0, *self._name_color_disabled)

        blf.size(0, 11, 72)
        blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.3, self.origin.y + 5), 0)
        blf.draw(0, shot.name)

    def get_handle(self, x, y):
        """
        Return the handle of the clip the mouse is on: -1 for start, 0 for move, 1 for end. None otherwise
        :param x:
        :param y:
        :return:
        """
        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        if shot.start <= x < shot.end + 1 and self.origin.y <= y < self.origin.y + self.height:
            # Test order is important for the case of start and end are the same. We want to prioritize moving the end.
            if shot.end <= x < shot.end + 1:
                return 1
            elif shot.start <= x < shot.start + 1:
                return -1
            else:
                return 0

        return None

    ### #TODO: wkip undo doesn't work here !!!
    def handle_mouse_interaction(self, region, mouse_disp):
        """
        region: if region == -1:    left clip handle (start)
                if region == 1:     right lip handle (end)
        """
        # from shotmanager.properties.shot import UAS_ShotManager_Shot

        #  bpy.ops.ed.undo_push(message=f"Set Shot Start...")

        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]
        # !! we have to be sure we work on the selected shot !!!
        if region == 1:
            shot.end += mouse_disp
        elif region == -1:
            shot.start += mouse_disp
            # bpy.ops.uas_shot_manager.set_shot_start(newStart=self.start + mouse_disp)
        else:
            # Very important, don't use properties for changing both start and ends. Depending of the amount of displacement duration can change.
            if mouse_disp > 0:
                shot.end += mouse_disp
                shot.start += mouse_disp
            else:
                shot.start += mouse_disp
                shot.end += mouse_disp


class BL_UI_ShotStack:
    def __init__(self, target_area=None):
        self.context = None
        self.target_area = target_area

        self.ui_shots = list()

        self.debug_mesh = None

    def init(self, context):
        self.context = context

        height = 20
        lane = 3
        startframe = 120
        numFrames = 15
        origin = Vector([startframe, get_lane_origin_y(lane)])
        self.debug_mesh = build_rectangle_mesh(origin, numFrames, height)

    def draw_shots(self):
        props = self.context.scene.UAS_shot_manager_props
        shots = props.get_shots()

        # create an array of tupples (ind, shot) to keep the association between the shot and its position
        shotTupples = []
        for i, shot in enumerate(shots):
            shotTupples.append((i, shot))

        self.ui_shots.clear()

        if props.interactShotsStack_displayInCompactMode:
            shotTupplesSorted = sorted(
                shotTupples,
                key=lambda shotTupple: shotTupple[1].start,
            )
            #  print(f"Tupples sorted: {shotTupplesSorted}")
            shots_from_lane = defaultdict(list)

            for ind, shotTupple in enumerate(shotTupplesSorted):
                shot = shotTupple[1]
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                lane = 0
                if ind > 0:
                    for ln, shots_in_lane in shots_from_lane.items():
                        for s in shots_in_lane:
                            if s.start <= shot.start <= s.end:
                                break
                        else:
                            lane = ln
                            break
                    else:
                        if len(shots_from_lane):
                            lane = max(shots_from_lane) + 1  # No free lane, make a new one.
                        else:
                            lane = ln
                            pass
                shots_from_lane[lane].append(shot)

                s = BL_UI_ShotClip(self.context, lane, shotTupple[0])
                s.shot_color = gamma_color(shot.color)
                s.update()
                self.ui_shots.append(s)
                s.draw()
        else:
            shots = props.get_shots()
            numShots = -1
            for i, shot in enumerate(shots):
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                numShots += 1
                s = BL_UI_ShotClip(self.context, numShots, i)
                s.shot_color = gamma_color(shot.color)
                s.update()
                self.ui_shots.append(s)
                s.draw()

    def draw(self):
        if self.target_area is not None and self.context.area != self.target_area:
            return

        # Debug - red rectangle ####################
        drawDebugRect = False
        if drawDebugRect:
            print("ogl draw shot stack")
            bgl.glEnable(bgl.GL_BLEND)
            UNIFORM_SHADER_2D.bind()
            color = (0.9, 0.0, 0.0, 0.9)
            UNIFORM_SHADER_2D.uniform_float("color", color)
            self.debug_mesh.draw(UNIFORM_SHADER_2D, self.context.region)

            return

        self.draw_shots()

    def handle_event(self, event):
        """handle event for BL_UI_ShotStack"""
        _logger.debug_ext("*** handle event for BL_UI_ShotStack", col="GREEN", tag="SHOTSTACK_EVENT")
