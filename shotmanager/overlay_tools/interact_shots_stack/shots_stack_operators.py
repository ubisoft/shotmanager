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

from .shots_stack_bgl import ShotClip, draw_shots_stack

import bpy

from shotmanager.config import config
from shotmanager.utils import utils
from shotmanager.utils.utils_ogl import get_region_at_xy


import logging

_logger = logging.getLogger(__name__)


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
        self.target_area = None

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.prev_click = 0

        self.active_clip = None
        self.active_clip_region = None

        self.frame_under_mouse = None

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            self.draw, (context,), "WINDOW", "POST_PIXEL"
        )
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

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

        props = context.scene.UAS_shot_manager_props

        # target_area_index = 1
        # self.target_area = utils.getAreaFromIndex(context, target_area_index, "DOPESHEET_EDITOR")
        self.target_area = props.getValidTargetDopesheet(context)

        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)
        self.context = context
        self.sm_props = context.scene.UAS_shot_manager_props
        self.build_clips()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences

        if (
            not context.window_manager.UAS_shot_manager_display_overlay_tools
            or not prefs.toggle_overlays_turnOn_interactiveShotsStack
        ):
            self.unregister_handlers(context)
            # context.window_manager.UAS_shot_manager_display_overlay_tools = False
            return {"CANCELLED"}

        if self.ignoreWidget(context):
            return {"PASS_THROUGH"}

        for area in context.screen.areas:
            if area.type == "DOPESHEET_EDITOR":
                try:
                    area.tag_redraw()
                except Exception as e:
                    print("*** Paf in DopeSheet Modal Shots Stack")
                    self.unregister_handlers(context)
                    context.window_manager.UAS_shot_manager_display_overlay_tools = False
                    return {"CANCELLED"}

        if config.devDebug:
            # print("wkip modal redrawing of the Interactive Shots Stack")
            pass
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
                self.sm_props.getShotsList(ignoreDisabled=not props.interactShotsStack_displayDisabledShots),
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
                self.sm_props.getShotsList(ignoreDisabled=not props.interactShotsStack_displayDisabledShots)
            ):
                self.clips.append(ShotClip(self.context, shot, i, self.sm_props))

    def draw(self, context):

        # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
        #     context.window_manager.event_timer_remove(self.draw_event)
        #     bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

        #     self.draw_handle = None
        #     self.draw_event = None
        #     return

        # !!! warning: Blender Timeline editor has a problem of refresh so even if the display is not done it may appear in the editor
        try:
            if self.ignoreWidget(context):
                return False

            if self.target_area is not None and self.context.area != self.target_area:
                return False

            draw_shots_stack(context, self)
            # for clip in self.clips:
            #     clip.draw(context)
            #     # try:
            #     #     clip.draw(context)
            #     # except Exception as e:
            #     #     # wkip wkip
            #     #     pass
            # if self.frame_under_mouse is not None:
            #     blf.color(0, 0.99, 0.99, 0.99, 1)
            #     blf.size(0, 11, 72)
            #     blf.position(0, self.prev_mouse_x + 4, self.prev_mouse_y + 10, 0)
            #     blf.draw(0, str(self.frame_under_mouse))

        except Exception as ex:
            _logger.error(f"*** Crash in ogl context - Draw clips loop: error: {ex} ***")
            self.unregister_handlers(context)
            context.window_manager.UAS_shot_manager_display_overlay_tools = False
            # context.window_manager.UAS_shot_manager_display_overlay_tools = True


_classes = (UAS_ShotManager_InteractiveShotsStack,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

