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

import time

import bpy
import bgl
import blf
import gpu
from mathutils import Vector

from shotmanager.utils.utils import gamma_color, color_is_dark, lighten_color

from ..shots_stack_bgl import (
    Image2D,
    #    Mesh2D,
    build_rectangle_mesh,
    get_lane_origin_y,
    get_lane_height,
    get_prefs_ui_scale,
)

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class BL_UI_ShotClip:
    def __init__(self, context, shot_index):
        """
        shot_index is the index of the shot in the whole take list
        """
        self.context = context

        self.origin = None
        self.width = 0
        self.font_size = 12

        self._active_region = None
        self._active_clip_over = False
        self._highlight = False
        self._mouseover = False

        # self.prev_mouse_x = 0
        # self.prev_mouse_y = 0
        self.prev_click = 0

        self.clip_mesh = None
        self.contour_mesh = None
        self.contourCurrent_mesh = None
        self.camIcon = None
        self.start_interaction_mesh = None
        self.end_interaction_mesh = None

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)

        self._shot_index = shot_index
        self._name_color_light = (0.9, 0.9, 0.9, 1)
        self._name_color_dark = (0.07, 0.07, 0.07, 1)
        self._name_color_disabled = (0.6, 0.6, 0.6, 1)

        self._shot_color = (0.8, 0.3, 0.3, 1.0)
        self._shot_color_disabled = (0.1, 0.1, 0.1, 0.5)

        # self.color_selectedShot_border = (0.9, 0.9, 0.2, 0.99)
        #    self.color_selectedShot_border = (0.2, 0.2, 0.2, 0.99)  # dark gray
        self.color_selectedShot_border = (0.95, 0.95, 0.95, 0.9)  # white

        # self.update()

    def update(self, lane):
        props = bpy.context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        self.lane = lane
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
    def height(self):
        return get_lane_height()

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
    def mouseover(self):
        return self._mouseover

    @mouseover.setter
    def mouseover(self, value: bool):
        self._mouseover = value

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
            _logger.debug_ext("highlight Shot in draw", col="RED", tag="SHOTSTACK_EVENT")
            color = (0.9, 0.9, 0.9, 0.5)
        # if self.mouseover:
        #     _logger.debug_ext(f"mouseover Shot in draw {shot.name}", col="RED", tag="SHOTSTACK_EVENT")
        #     color = lighten_color(color, 0.3)

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
        ##########################
        # TODO finish and clean
        #   self.camIcon.draw(context.region)

        # draw shot name
        ##########################
        bgl.glDisable(bgl.GL_BLEND)

        if shot.enabled:
            if color_is_dark(color, 0.4):
                blf.color(0, *self._name_color_light)
            else:
                blf.color(0, *self._name_color_dark)
        else:
            blf.color(0, *self._name_color_disabled)

        blf.size(0, self.font_size * get_prefs_ui_scale(), 72)
        blf.position(
            0, *context.region.view2d.view_to_region(self.origin.x + 1.4, self.origin.y + 6 * get_prefs_ui_scale()), 0
        )
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

    def handle_event(self, context, event, region):
        """Return True if the event is handled for BL_UI_ShotStack

        Notes:
            - self.mouseover is not working perfectly since the over color is left on the last
              overed shot when the mouse is out of every shots. This is because when leaving shots
              the event is not returned as being handled.
        """

        ########
        # REMOVED
        ########

        context = self.context
        props = context.scene.UAS_shot_manager_props
        shots = props.get_shots()
        shot = shots[self._shot_index]

        event_handled = False

        # self.mouseover = True

        # if event.type not in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE", "TIMER"]:
        _logger.debug_ext(f"     *** event in BL_UI_Shot: {event.type}", col="GREEN", tag="SHOTSTACK_EVENT")

        mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_x - region.x, event.mouse_y - region.y)
        active_clip_region = self.get_handle(mouse_x, mouse_y)

        # _logger.debug_ext(f"over Shot {shot.name} active_clip_region: {active_clip_region}", col="RED")
        if active_clip_region is not None:

            # mouse over #################
            # NOTE: mouseover works but is not used (= desactivated in draw function) because it has to be associated
            # with a redraw when no events are handle, which is hardware greedy (moreover reactive components are not
            # in the philosophy of Blender)
            self.mouseover = True

            if event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:

                #  _logger.debug_ext(f"over Shot {shot.name}", col="RED")
                #    self.mouseover = True
                self.highlight = True
                # config.gShotsStackInfos["active_clip_index"] = i
                # config.gShotsStackInfos["active_clip_region"] = active_clip_region
                # self.active_clip = clip
                # self.active_clip_region = active_clip_region
                # props = context.scene.UAS_shot_manager_props
                #  props.setSelectedShotByIndex(self.shot_index)

                # event_handled = True
                # else:
                #     self.mouseover = False
                #     pass
                pass

            elif event.type == "LEFTMOUSE":
                if event.value == "PRESS":
                    props.setSelectedShotByIndex(self.shot_index)

                    # double click
                    counter = time.perf_counter()
                    print(f"pref clic: {self.prev_click}")
                    if counter - self.prev_click < 0.3:  # Double click.
                        props.setCurrentShotByIndex(self.shot_index, changeTime=False)
                        mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        context.scene.frame_current = mouse_frame
                        # bpy.ops.uas_shot_manager.set_current_shot(index=self.shot_index)
                    self.prev_click = counter
                    event_handled = True

        else:
            self.highlight = False
            self.mouseover = False
            pass

        return event_handled

    # TODO: wkip undo doesn't work here !!!
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
