# -*- coding: utf-8 -*-
import logging
import time
from collections import defaultdict

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .ogl_ui import clamp, get_region_at_xy, gamma_color
from .. import properties

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


def clamp_to_region(x, y, region):
    l_x, l_y = region.view2d.region_to_view(0, 0)
    h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)


class Mesh2D:
    def __init__(self, vertices=None, indices=None, texcoords=None):
        self._vertices = list() if vertices is None else vertices
        self._indices = list() if indices is None else indices
        self._texcoords = list() if texcoords is None else texcoords

    @property
    def vertices(self):
        return list(self._vertices)

    @property
    def indices(self):
        return list(self._indices)

    @property
    def texcoords(self):
        return list(self._texcoords)

    def draw(self, shader, region=None, draw_types="TRIS"):
        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=self._indices)
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
        self.start_interaction_mesh = None
        self.end_interaction_mesh = None
        self.origin = None
        self.sm_props = sm_props
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
        if self.highlight:
            color = (0.9, 0.9, 0.9, 0.5)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        self.clip_mesh.draw(UNIFORM_SHADER_2D, context.region)

        self.start_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)
        self.end_interaction_mesh.draw(UNIFORM_SHADER_2D, context.region)

        current_shot = self.sm_props.getCurrentShot()

        if current_shot != -1 and self.shot.name == current_shot.name:
            UNIFORM_SHADER_2D.uniform_float("color", (0.6, 0.6, 0.9, 0.9))
            self.contour_mesh.draw(UNIFORM_SHADER_2D, context.region, "LINES")

        bgl.glDisable(bgl.GL_BLEND)

        blf.color(0, 0.99, 0.99, 0.99, 1)
        blf.size(0, 11, 72)
        blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.01, self.origin.y + 4), 0)
        blf.draw(0, self.shot.name)

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


class UAS_ShotManager_DrawMontageTimeline(bpy.types.Operator):
    bl_idname = "uas_shot_manager.draw_montage_timeline"
    bl_label = "Draw Montage in timeline"
    bl_options = { "REGISTER", "INTERNAL" }
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

    def modal(self, context, event):
        for area in context.screen.areas:
            if area.type == "DOPESHEET_EDITOR":
                area.tag_redraw()

        if not context.window_manager.UAS_shot_manager_toggle_montage_interaction:
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
                    if self.active_clip and counter - self.prev_click < 0.2:  # Double click.
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

        if not context.window_manager.UAS_shot_manager_display_timeline:
            context.window_manager.event_timer_remove(self.draw_event)
            bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            self.draw, (context,), "WINDOW", "POST_PIXEL"
        )
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.context = context
        self.sm_props = context.scene.UAS_shot_manager_props
        self.build_clips()
        return {"RUNNING_MODAL"}

    def build_clips(self):
        self.clips.clear()
        if self.compact_display:
            shots = sorted(self.sm_props.getShotsList(ignoreDisabled=True), key=lambda s: s.start)
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
            for i, shot in enumerate(self.sm_props.getShotsList(ignoreDisabled=True)):
                self.clips.append(ShotClip(self.context, shot, i, self.sm_props))

    def draw(self, context):
        for clip in self.clips:
            try:
                clip.draw(context)
            except Exception as e:
                # wkip wkip
                pass

        if self.frame_under_mouse is not None:
            blf.color(0, 0.99, 0.99, 0.99, 1)
            blf.size(0, 11, 72)
            blf.position(0, self.prev_mouse_x + 4, self.prev_mouse_y + 10, 0)
            blf.draw(0, str(self.frame_under_mouse))


_classes = (UAS_ShotManager_DrawMontageTimeline,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
