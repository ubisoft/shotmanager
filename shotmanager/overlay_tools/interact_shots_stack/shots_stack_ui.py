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
UI for the Interactive Shots Stack overlay tool
"""

import time
from collections import defaultdict

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from shotmanager.config import config
from shotmanager.utils.utils import clamp, gamma_color
from shotmanager.utils.utils_ogl import get_region_at_xy

import logging

_logger = logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


def clamp_to_region(x, y, region):
    l_x, l_y = region.view2d.region_to_view(0, 0)
    h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)


class Image2D:
    def __init__(self, position, width, height):
        import os

        # IMAGE_NAME = "Untitled"
        IMAGE_NAME = os.path.join(os.path.dirname(__file__), "../../icons/ShotMan_EnabledCurrentCam.png")

        # image = bpy.types.Image()
        # # image.file_format = 'PNG'
        # image.filepath = IMAGE_NAME

        # self._image = bpy.data.images[image]
        self._image = bpy.data.images.load(IMAGE_NAME)
        self._shader = gpu.shader.from_builtin("2D_IMAGE")

        x1, y1 = position.x, position.y
        x2, y2 = position.x + width, position.y
        x3, y3 = position.x, position.y + height
        x4, y4 = position.x + width, position.y + height

        self._position = position
        self._vertices = ((x1, y1), (x2, y2), (x4, y4), (x3, y3))
        # print(f"vertices: {self._vertices}")
        # self._vertices = ((100, 100), (200, 100), (200, 200), (100, 200))
        #    self._verticesSquare = ((0, 0), (0, 1), (1, 1), (0, 1))

        # origin is bottom left of the screen
        # self._vertices = ((bottom_left.x, bottom_left.y), (bottom_right.x, bottom_right.y), (top_right.x, top_right.y), (top_left.x, top_left.y))

        if self._image.gl_load():
            raise Exception()

    def draw(self, region=None):
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._image.bindcode)

        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        verticesSquare = (
            (transformed_vertices[0][0], transformed_vertices[0][1],),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[0][1],
            ),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[3][1],
            ),
            (transformed_vertices[0][0], transformed_vertices[3][1],),
        )

        batch = batch_for_shader(
            self._shader, "TRI_FAN", {"pos": verticesSquare, "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),},
        )
        self._shader.bind()
        self._shader.uniform_int("image", 0)
        batch.draw(self._shader)


class Mesh2D:
    def __init__(self, vertices=None, indices=None, texcoords=None):
        self._vertices = list() if vertices is None else vertices
        self._indices = list() if indices is None else indices
        self._texcoords = list() if texcoords is None else texcoords
        self._linewidth = 1

    @property
    def vertices(self):
        return list(self._vertices)

    @property
    def indices(self):
        return list(self._indices)

    @property
    def texcoords(self):
        return list(self._texcoords)

    @property
    def linewidth(self):
        return self._linewidth

    @linewidth.setter
    def linewidth(self, value):
        self._linewidth = max(1, value)

    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        if "TRIS" == draw_types:
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
            batch.draw(shader)
        elif "LINES":
            # draw lines and points fo the caps
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
            bgl.glLineWidth(self._linewidth)
            batch.draw(shader)
            if cap_lines:
                batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices})
                bgl.glPointSize(self._linewidth)
                batch.draw(shader)
        elif "POINTS":
            # wkip here draw points for rounded line caps
            batch = batch_for_shader(shader, "POINTS", {"pos": transformed_vertices})
            bgl.glPointSize(self._linewidth)
            batch.draw(shader)


def build_rectangle_mesh(position, width, height, as_lines=False):
    """

    :param position:
    :param width:
    :param height:
    :param region: if region is specified this will transform the vertices into the region's view. This allow for pan and zoom support
    :return:
    """
    x1, y1 = position.x, position.y
    x2, y2 = position.x + width, position.y
    x3, y3 = position.x, position.y + height
    x4, y4 = position.x + width, position.y + height

    vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
    if as_lines:
        indices = ((0, 1), (0, 2), (2, 3), (1, 3))
    else:
        indices = ((0, 1, 2), (2, 1, 3))

    return Mesh2D(vertices, indices)


LANE_HEIGHT = 18


def get_lane_origin_y(lane):
    return -LANE_HEIGHT * lane - 39  # an offset to put it under timeline ruler.


class ShotClip:
    def __init__(self, context, shot, lane, sm_props):
        self.context = context
        self.shot = shot
        self.height = LANE_HEIGHT
        self.width = 0
        self.lane = lane
        self._highlight = False
        self.clip_mesh = None
        self.contour_mesh = None
        self.contourCurrent_mesh = None
        self.camIcon = None
        self.start_interaction_mesh = None
        self.end_interaction_mesh = None
        self.origin = None
        self.sm_props = sm_props

        self.color_currentShot_border = (0.92, 0.55, 0.18, 0.99)
        self.color_currentShot_border_mix = (0.94, 0.3, 0.1, 0.99)

        # self.color_selectedShot_border = (0.9, 0.9, 0.2, 0.99)
        #    self.color_selectedShot_border = (0.2, 0.2, 0.2, 0.99)  # dark gray
        self.color_selectedShot_border = (0.95, 0.95, 0.95, 0.9)  # white

        self.update()

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value: bool):
        self._highlight = value

    def draw(self, context):
        bgl.glEnable(bgl.GL_BLEND)
        UNIFORM_SHADER_2D.bind()
        color = (self.shot.color[0], self.shot.color[1], self.shot.color[2], 0.5)

        color = gamma_color(color)

        if not self.shot.enabled:
            color = (0.15, 0.15, 0.15, 0.5)

        if self.highlight:
            color = (0.9, 0.9, 0.9, 0.5)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        self.clip_mesh.draw(UNIFORM_SHADER_2D, context.region)

        self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
        self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)

        current_shot = self.sm_props.getCurrentShot()
        selected_shot = self.sm_props.getSelectedShot()

        # current shot
        if current_shot != -1 and self.shot.name == current_shot.name:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_currentShot_border)
            self.contourCurrent_mesh.linewidth = 4 if current_shot == selected_shot else 2
            self.contourCurrent_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # selected shot
        if current_shot != -1 and self.shot.name == selected_shot.name:
            UNIFORM_SHADER_2D.uniform_float("color", self.color_selectedShot_border)
            self.contour_mesh.linewidth = 1 if current_shot == selected_shot else 2
            self.contour_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        # draw a camera icon on the current shot
        # TODO finish and clean
        #   self.camIcon.draw(context.region)

        bgl.glDisable(bgl.GL_BLEND)

        blf.color(0, 0.99, 0.99, 0.99, 1)
        blf.size(0, 11, 72)
        blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.01, self.origin.y + 4), 0)
        blf.draw(0, self.shot.name)

    #   print("here 03")

    def get_region(self, x, y):
        """
        Return the region the mouse is on -1 for start, 0 for move, 1 for end. None else
        :param x:
        :param y:
        :return:
        """
        if self.shot.start <= x < self.shot.end + 1 and self.origin.y <= y < self.origin.y + self.height:
            # Test order is important for the case of start and end are the same. We want to prioritize moving the end.
            if self.shot.end <= x < self.shot.end + 1:
                return 1
            elif self.shot.start <= x < self.shot.start + 1:
                return -1
            else:
                return 0

        return None

    def handle_mouse_interaction(self, region, mouse_disp):
        if region == 1:
            self.shot.end += mouse_disp
        elif region == -1:
            self.shot.start += mouse_disp
        else:
            # Very important, don't use properties for changing both start and ends. Depending of the amount of displacement duration can change.
            if mouse_disp > 0:
                self.shot.end += mouse_disp
                self.shot.start += mouse_disp
            else:
                self.shot.start += mouse_disp
                self.shot.end += mouse_disp

    def update(self):
        self.width = self.shot.end - self.shot.start + 1
        self.origin = Vector([self.shot.start, get_lane_origin_y(self.lane)])
        self.clip_mesh = build_rectangle_mesh(self.origin, self.width, self.height)
        self.start_interaction_mesh = build_rectangle_mesh(self.origin, 1, self.height)
        self.end_interaction_mesh = build_rectangle_mesh(self.origin + Vector([self.width - 1, 0]), 1, self.height)
        self.contour_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        self.contourCurrent_mesh = build_rectangle_mesh(self.origin, self.width, self.height, True)
        # self.contourCurrent_mesh = build_rectangle_mesh(
        #     Vector([self.origin.x - 1, self.origin.y - 1]), self.width + 2, self.height + 2, True
        # )
        self.camIcon = Image2D(self.origin, self.width, self.height)


class UAS_ShotManager_InteractiveShotsStack(bpy.types.Operator):
    bl_idname = "uas_shot_manager.interactive_shots_stack"
    bl_label = "Draw Interactive Shots Stack in timeline"
    bl_options = {"REGISTER", "INTERNAL"}

    def __init__(self):
        self.asset_browser = None
        self.compact_display = False

        self.draw_handle = None
        self.draw_event = None

        self.sm_props = None
        self.clips = list()
        self.context = None

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.prev_click = 0

        self.active_clip = None
        self.active_clip_region = None

        self.frame_under_mouse = None

    def ignoreWidget(self, context):
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        if not context.window_manager.UAS_shot_manager_display_overlay_tools:
            return True

        if (context.screen.is_animation_playing and not context.screen.is_scrubbing) and (
            context.window_manager.UAS_shot_manager_use_best_perfs
            and prefs.best_play_perfs_turnOff_interactiveShotsStack
        ):
            return True
        return False

    def invoke(self, context, event):
        if self.ignoreWidget(context):
            return {"CANCELLED"}

        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            self.draw, (context,), "WINDOW", "POST_PIXEL"
        )
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.context = context
        self.sm_props = context.scene.UAS_shot_manager_props
        self.build_clips()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        for area in context.screen.areas:
            if area.type == "DOPESHEET_EDITOR":
                area.tag_redraw()

        if not context.window_manager.UAS_shot_manager_display_overlay_tools:
            context.window_manager.event_timer_remove(self.draw_event)
            bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")
            return {"CANCELLED"}

        if self.ignoreWidget(context):
            return {"PASS_THROUGH"}

        if config.devDebug:
            print("wkip modal redrawing of the Interactive Shots Stack")
        # TODO: wkip here investigate for optimization cause this forced refresh is really greedy !!!

        # for area in context.screen.areas:
        #     if area.type == "DOPESHEET_EDITOR":
        #         area.tag_redraw()

        if not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction:
            return {"PASS_THROUGH"}

        event_handled = False
        region, area = get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")
        if region:
            mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_x - region.x, event.mouse_y - region.y)
            if event.type == "LEFTMOUSE":
                if event.value == "PRESS":
                    for clip in self.clips:
                        active_clip_region = clip.get_region(mouse_x, mouse_y)
                        if active_clip_region is not None:
                            clip.highlight = True
                            self.active_clip = clip
                            self.active_clip_region = active_clip_region
                            self.sm_props.setSelectedShot(self.active_clip.shot)
                            event_handled = True
                        else:
                            clip.highlight = False

                    counter = time.perf_counter()
                    if self.active_clip and counter - self.prev_click < 0.3:  # Double click.
                        self.sm_props.setCurrentShot(self.active_clip.shot)
                        event_handled = True

                    self.prev_click = counter

            elif event.type == "MOUSEMOVE":
                if event.value == "PRESS":
                    if self.active_clip:
                        mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                        self.active_clip.handle_mouse_interaction(
                            self.active_clip_region, mouse_frame - prev_mouse_frame
                        )
                        self.active_clip.update()
                        if self.active_clip_region != 0:
                            self.frame_under_mouse = mouse_frame
                        event_handled = True
                elif event.value == "RELEASE":
                    if self.active_clip:
                        self.active_clip.highlight = False
                        self.active_clip = None
                        self.frame_under_mouse = None

            self.prev_mouse_x = event.mouse_x - region.x
            self.prev_mouse_y = event.mouse_y - region.y
        else:
            self.build_clips()  # Assume that when the mouse got out of the region shots may be edited
            self.active_clip = None

        if event_handled:
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def build_clips(self):
        props = bpy.context.scene.UAS_shot_manager_props
        self.clips.clear()
        # if self.compact_display:
        if props.interactShotsStack_displayInCompactMode:
            shots = sorted(
                self.sm_props.getShotsList(ignoreDisabled=not props.display_disabledshots_in_interactShotsStack),
                key=lambda s: s.start,
            )
            shots_from_lane = defaultdict(list)
            for i, shot in enumerate(shots):
                lane = 0
                if i > 0:
                    for l, shots_in_lane in shots_from_lane.items():
                        for s in shots_in_lane:
                            if s.start <= shot.start <= s.end:
                                break
                        else:
                            lane = l
                            break
                    else:
                        lane = max(shots_from_lane) + 1  # No free lane, make a new one.
                shots_from_lane[lane].append(shot)

                self.clips.append(ShotClip(self.context, shot, lane, self.sm_props))
        else:
            for i, shot in enumerate(
                self.sm_props.getShotsList(ignoreDisabled=not props.display_disabledshots_in_interactShotsStack)
            ):
                self.clips.append(ShotClip(self.context, shot, i, self.sm_props))

    def draw(self, context):
        # !!! warning: Blender Timeline editor has a problem of refresh so even if the display is not done it may appear in the editor
        if self.ignoreWidget(context):
            return False

        try:
            for clip in self.clips:
                clip.draw(context)
                # try:
                #     clip.draw(context)
                # except Exception as e:
                #     # wkip wkip
                #     pass
            if self.frame_under_mouse is not None:
                blf.color(0, 0.99, 0.99, 0.99, 1)
                blf.size(0, 11, 72)
                blf.position(0, self.prev_mouse_x + 4, self.prev_mouse_y + 10, 0)
                blf.draw(0, str(self.frame_under_mouse))

        except Exception as ex:
            _logger.error(f"*** Crash in ogl context - Draw clips loop: error: {ex} ***")
            context.window_manager.UAS_shot_manager_display_overlay_tools = False
            # context.window_manager.UAS_shot_manager_display_overlay_tools = True


_classes = (UAS_ShotManager_InteractiveShotsStack,)


def register():
    print("       - Registering Interactive Shots Stack Package")
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    print("       - Unegistering Interactive Shots Stack Package")
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
