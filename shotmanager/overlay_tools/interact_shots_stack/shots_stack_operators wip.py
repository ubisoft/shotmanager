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

from .shots_stack_bgl import BL_UI_ShotClip, draw_shots_stack

import bpy
from bpy.types import Operator

from shotmanager.config import config
from shotmanager.utils import utils
from shotmanager.utils.utils import gamma_color
from shotmanager.utils.utils_ogl import get_region_at_xy


from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def ignoreWidget(context):
    prefs = bpy.context.preferences.addons["shotmanager"].preferences

    # if not len(props.get_shots()):
    #     return True
    if not context.window_manager.UAS_shot_manager_display_overlay_tools:
        return True
    if (context.screen.is_animation_playing and not context.screen.is_scrubbing) and (
        context.window_manager.UAS_shot_manager_use_best_perfs and prefs.best_play_perfs_turnOff_interactiveShotsStack
    ):
        return True
    return False


def initialize_gShotsStackInfos():
    return {
        "prev_mouse_x": 0,
        "prev_mouse_y": 0,
        "frame_under_mouse": -1,
        "active_clip_index": -1,
        "active_clip_region": None,
        "clips": list(),
    }


def display_state_changed_intShStack(context):
    # wkipwkipwkip could be removed, not used as such
    print("display_state_changed_intShStack - to remove")
    prefs = context.preferences.addons["shotmanager"].preferences
    # if (
    #     context.window_manager.UAS_shot_manager_display_overlay_tools
    #     and prefs.toggle_overlays_turnOn_interactiveShotsStack
    # ):
    bpy.ops.uas_shot_manager.interactive_shots_stack("INVOKE_DEFAULT")


class UAS_ShotManager_InteractiveShotsStack(Operator):
    bl_idname = "uas_shot_manager.interactive_shots_stack"
    bl_label = "Draw Interactive Shots Stack in timeline"
    bl_options = {"INTERNAL"}
    # bl_options = {"UNDO"}
    # !!! Important note: Do not set undo here: it doesn't work and it will be in conflic with the
    # calls to bpy.ops.ed.undo_push in the code !!!

    def __init__(self):
        self.asset_browser = None
        self.compact_display = False

        self.draw_handle = None
        self.draw_event = None

        self.target_area = None
        self.target_area_index = -1

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.prev_click = 0

        self.active_clip = None
        self.active_clip_region = None

        config.gShotsStackInfos = None

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            draw_callback_px, args, "WINDOW", "POST_PIXEL"
        )
        self.draw_event = context.window_manager.event_timer_add(0.2, window=context.window)

    def unregister_handlers(self, context):
        # context.window_manager.UAS_shot_manager_display_overlay_tools = False

        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

        self.draw_handle = None
        self.draw_event = None

    def invoke(self, context, event):
        _logger.debug_ext("Invoke interactive_shots_stack", col="PURPLE")

        if ignoreWidget(context):
            return {"CANCELLED"}

        props = context.scene.UAS_shot_manager_props

        # target_area_index = 1
        # self.target_area = utils.getAreaFromIndex(context, target_area_index, "DOPESHEET_EDITOR")
        self.target_area_index = props.getTargetDopesheetIndex(context, only_valid=True)
        self.target_area = props.getValidTargetDopesheet(context)

        args = (context, self.target_area)
        self.register_handlers(args, context)

        self.build_clips()
        context.window_manager.modal_handler_add(self)

        if config.gShotsStackInfos is None:
            config.gShotsStackInfos = initialize_gShotsStackInfos()

        # redraw all
        for area in context.screen.areas:
            area.tag_redraw()
        context.scene.frame_current = context.scene.frame_current

        return {"RUNNING_MODAL"}

    ###################################
    # modal
    ###################################

    def modal(self, context, event):
        newRedrawTime = -1
        config.devDebug_lastRedrawTime = newRedrawTime
        newRedrawTime = 0

        # print(f"Modal, event type: {event.type}")

        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        # if config.gShotsStackInfos is None:
        #     config.gShotsStackInfos = initialize_gShotsStackInfos()

        if (
            not context.window_manager.UAS_shot_manager_display_overlay_tools
            or not prefs.toggle_overlays_turnOn_interactiveShotsStack
            or not len(props.get_shots())
            or self.target_area_index != props.getTargetDopesheetIndex(context, only_valid=True)
        ):
            self.unregister_handlers(context)
            # context.window_manager.UAS_shot_manager_display_overlay_tools = False
            # return {"CANCELLED"}
            return {"FINISHED"}

        if ignoreWidget(context):
            #  self.unregister_handlers(context)
            # for area in context.screen.areas:
            #     #    if area.type == "DOPESHEET_EDITOR" and area == self.target_area:
            #     area.tag_redraw()
            #     print("Ignioring...")
            return {"PASS_THROUGH"}

        # self.build_clips()  # Assume that when the mouse got out of the region shots may be edited
        # self.active_clip = None
        for area in context.screen.areas:
            if area.type == "DOPESHEET_EDITOR" and area == self.target_area:
                # _logger.debug_ext("Redraw", col="PURPLE")
                try:
                    # if True:
                    #  self.build_clips()  # Assume that when the mouse got out of the region shots may be edited
                    #  self.active_clip = None
                    area.tag_redraw()
                # print("Redraw")
                except Exception as e:
                    print("*** Paf in DopeSheet Modal Shots Stack")
                    self.unregister_handlers(context)
                    context.window_manager.UAS_shot_manager_display_overlay_tools = False
                    return {"CANCELLED"}

        # # if context.area != self.target_area:
        # #     return {"PASS_THROUGH"}

        # # context.area.tag_redraw()

        if config.devDebug:
            # print("wkip modal redrawing of the Interactive Shots Stack")
            pass
        # TODO: wkip here investigate for optimization cause this forced refresh is really greedy !!!

        # for area in context.screen.areas:
        #     if area.type == "DOPESHEET_EDITOR":
        #         area.tag_redraw()

        # if not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction:
        #     return {"PASS_THROUGH"}

        event_handled = False
        region, area = get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # don't get events when out of area
        if self.target_area is not None and area != self.target_area:
            #    _logger.debug_ext("in region Area", col="YELLOW")
            return {"PASS_THROUGH"}

        # _logger.debug_ext("in region Area", col="PURPLE")

        if region:
            #    _logger.debug_ext("in region Area 02", col="RED")
            # wkip
            # if 0 == len(config.gShotsStackInfos["clips"]):
            #     self.build_clips()

            if not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction:
                return {"PASS_THROUGH"}

            mouse_x, mouse_y = region.view2d.region_to_view(event.mouse_x - region.x, event.mouse_y - region.y)
            if event.type == "LEFTMOUSE":
                if event.value == "PRESS":
                    # bpy.ops.ed.undo_push(message=f"Set Shot Start...")
                    for i, clip in enumerate(config.gShotsStackInfos["clips"]):
                        active_clip_region = clip.get_handle(mouse_x, mouse_y)
                        if active_clip_region is not None:
                            _logger.debug_ext(f"highlight Shot", col="RED")
                            clip.highlight = True
                            config.gShotsStackInfos["active_clip_index"] = i
                            config.gShotsStackInfos["active_clip_region"] = active_clip_region
                            self.active_clip = clip
                            self.active_clip_region = active_clip_region
                            props.setSelectedShotByIndex(self.active_clip.shot_index)
                            event_handled = True
                            continue
                        else:
                            clip.highlight = False

                    counter = time.perf_counter()
                    if self.active_clip and counter - self.prev_click < 0.3:  # Double click.
                        props.setCurrentShotByIndex(self.active_clip.shot_index, changeTime=False)
                        mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        context.scene.frame_current = mouse_frame
                        event_handled = True

                    self.prev_click = counter
                elif event.value == "RELEASE":
                    bpy.ops.ed.undo_push(message=f"Change Shot...")
                    config.gShotsStackInfos["active_clip_index"] = -1
                    config.gShotsStackInfos["active_clip_region"] = None

            elif event.type == "MOUSEMOVE":
                _logger.debug_ext(f"I move", col="BLUE", tag="SHOTSTACK_EVENT")

                # mouse over handles?
                config.gShotsStackInfos["active_clip_over"] = False
                for i, clip in enumerate(config.gShotsStackInfos["clips"]):
                    active_clip_region = clip.get_handle(mouse_x, mouse_y)
                    if active_clip_region is not None:
                        _logger.debug_ext(
                            f"highlight Shot handle over, clip {i} region: {active_clip_region}", col="BLUE"
                        )
                        clip.highlight = True
                        config.gShotsStackInfos["active_clip_index"] = i
                        config.gShotsStackInfos["active_clip_region"] = active_clip_region
                        config.gShotsStackInfos["active_clip_over"] = True
                    # else:
                    #     config.gShotsStackInfos["active_clip_index"] = -1
                    #     config.gShotsStackInfos["active_clip_region"] = None
                    # clip.highlight = False

                if event.value == "PRESS":
                    _logger.debug_ext(f"   key pressed", col="BLUE", tag="SHOTSTACK_EVENT")
                    if self.active_clip:
                        mouse_frame = int(region.view2d.region_to_view(event.mouse_x - region.x, 0)[0])
                        prev_mouse_frame = int(region.view2d.region_to_view(self.prev_mouse_x, 0)[0])
                        self.active_clip.handle_mouse_interaction(
                            self.active_clip_region, mouse_frame - prev_mouse_frame
                        )
                        self.active_clip.update()
                        if self.active_clip_region != 0:
                            # self.frame_under_mouse = mouse_frame
                            config.gShotsStackInfos["frame_under_mouse"] = mouse_frame
                        event_handled = True
                elif event.value == "RELEASE":
                    _logger.debug_ext(f"   key released", col="BLUE", tag="SHOTSTACK_EVENT")
                    if self.active_clip:
                        self.active_clip.highlight = False
                        self.active_clip = None
                        # self.frame_under_mouse = None
                        config.gShotsStackInfos["frame_under_mouse"] = -1
                        event_handled = True

            self.prev_mouse_x = event.mouse_x - region.x
            self.prev_mouse_y = event.mouse_y - region.y

            # if config.gShotsStackInfos["frame_under_mouse"] != -1:
            #     print(
            #         "Type of config.gShotsStackInfos frame_under_mouse: "
            #         + str(type(config.gShotsStackInfos["frame_under_mouse"]))
            #     )
            config.gShotsStackInfos["prev_mouse_x"] = self.prev_mouse_x
            config.gShotsStackInfos["prev_mouse_y"] = self.prev_mouse_y
        else:
            _logger.debug(
                "Should I be here ? - config.gShotsStackInfos Clips len: "
                + str(len(config.gShotsStackInfos["clips"]), col="RED")
            )
            # self.build_clips()  # Assume that when the mouse got out of the region shots may be edited
            # self.active_clip = None

        if event_handled:
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def build_clips(self):
        props = bpy.context.scene.UAS_shot_manager_props

        if config.gShotsStackInfos is None:
            config.gShotsStackInfos = initialize_gShotsStackInfos()
        else:
            config.gShotsStackInfos["clips"].clear()

        currentShotIndex = props.getCurrentShotIndex()
        selectedShotIndex = props.getSelectedShotIndex()

        shots = props.get_shots()

        if props.interactShotsStack_displayInCompactMode:
            # shots = sorted(
            #     props.getShotsList(ignoreDisabled=not props.interactShotsStack_displayDisabledShots),
            #     key=lambda s: s.start,
            # )
            shots = sorted(
                shots,
                key=lambda s: s.start,
            )
            shots_from_lane = defaultdict(list)
            for i, shot in enumerate(shots):
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                lane = 0
                if i > 0:
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
                            lane = 1
                shots_from_lane[lane].append(shot)

                s = BL_UI_ShotClip(lane, i)
                s.shot_color = gamma_color(shot.color)
                s.update()
                config.gShotsStackInfos["clips"].append(s)
        else:
            numShots = -1
            for i, shot in enumerate(shots):
                if not props.interactShotsStack_displayDisabledShots and not shot.enabled:
                    continue
                numShots += 1
                # print(f"   i: {i}")
                s = BL_UI_ShotClip(numShots, i)
                s.shot_color = gamma_color(shot.color)
                s.update()
                config.gShotsStackInfos["clips"].append(s)


## !!! not in the class !!!
def draw_callback_px(context, target_area):
    # !!! Dev note: This callback function must not use any attribute from the modal operator (not calls to self for example)
    # otherwise it will crash when changing scene or registering the add-on at new !!!

    # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
    #     context.window_manager.event_timer_remove(self.draw_event)
    #     bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

    # !!! warning: Blender Timeline editor has a problem of refresh so even if the display is not done it may appear in the editor

    if target_area is not None and context.area != target_area:
        return False

    # draw_shots_stack(context)
    try:
        # if ignoreWidget(context):
        #     return False
        draw_shots_stack(context)

    except Exception as ex:
        _logger.error(f"*** Crash in ogl context - Draw clips loop: error: {ex} ***")
        # self.unregister_handlers(context)
        # context.window_manager.UAS_shot_manager_display_overlay_tools = False
        # context.window_manager.UAS_shot_manager_display_overlay_tools = True


class UAS_ShotManager_OT_ToggleShotsStackWithOverlayTools(Operator):
    bl_idname = "uas_shot_manager.toggle_shots_stack_with_overlay_tools"
    bl_label = "Toggle Display"
    bl_description = "Toggle Interactive Shots Stack display with overlay tools"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences
        prefs.toggle_overlays_turnOn_interactiveShotsStack = not prefs.toggle_overlays_turnOn_interactiveShotsStack

        # toggle on or off the overlay tools mode
        #  context.window_manager.UAS_shot_manager_display_overlay_tools = prefs.toggle_overlays_turnOn_interactiveShotsStack

        return {"FINISHED"}


class UAS_ShotManager_OT_ToggleShotsStackInteraction(Operator):
    bl_idname = "uas_shot_manager.toggle_shots_stack_interaction"
    bl_label = "Toggle interactions in the Interactive Shots Stack"
    # bl_description = "Toggle Shots Stack Interactions"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction = (
            not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction
        )

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_InteractiveShotsStack,
    UAS_ShotManager_OT_ToggleShotsStackWithOverlayTools,
    UAS_ShotManager_OT_ToggleShotsStackInteraction,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
