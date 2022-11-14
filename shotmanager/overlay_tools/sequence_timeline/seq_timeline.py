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
Draw an interactive stack of shots in the Timeline editor
"""

import bpy
from bpy.types import Operator


# from shotmanager.utils import utils

from .seq_timeline_widgets import BL_UI_Timeline

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def ignoreWidget(context):
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    if not len(props.get_shots()):
        return True
    if not context.window_manager.UAS_shot_manager_display_overlay_tools:
        return True
    if (context.screen.is_animation_playing and not context.screen.is_scrubbing) and (
        context.window_manager.UAS_shot_manager_use_best_perfs and prefs.best_play_perfs_turnOff_sequenceTimeline
    ):
        return True
    if hasattr(bpy.context.space_data, "overlay"):
        if not prefs.seqTimeline_not_disabled_with_overlays and not context.space_data.overlay.show_overlays:
            return True
    return False


class UAS_ShotManager_sequenceTimeline(Operator):
    bl_idname = "uas_shot_manager.sequence_timeline"
    bl_label = "Display Sequence Timeline"
    bl_description = "Draw the sequence timeline in the 3D viewport"
    bl_options = {"REGISTER", "INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = config.getAddonProps(context.scene)
    #     prefs = config.getAddonPrefs()
    #     val = True
    #     if prefs.seqTimeline_not_disabled_with_overlays and not bpy.context.space_data.overlay.show_overlays:
    #         val = False
    #     return False

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

        # self.target_area = None
        self.target_area_index = -1

        self.widgets = []

    def init_widgets(self, context, widgets, target_area=None):
        self.widgets = widgets
        for widget in self.widgets:
            widget.init(context)

    ###################################
    # invoke
    ###################################

    def invoke(self, context, event):
        _logger.debug_ext("Invoke op uas_shot_manager.sequence_timeline", col="RED")

        if ignoreWidget(context):
            _logger.debug_ext("Canceled op uas_shot_manager.sequence_timeline", col="RED")
            return {"CANCELLED"}

        props = config.getAddonProps(context.scene)

        # get the area index of invocation
        # source_area = context.area
        # source_area_ind = utils.getAreaIndex(context, context.area, "VIEW_3D")
        # expected_target_area_ind = props.getTargetViewportIndex(context, only_valid=False)
        # target_area_ind = props.getTargetViewportIndex(context, only_valid=True)
        target_area = props.getValidTargetViewport(context)
        # print(
        #     f"Invoke Timeline area ind: {source_area_ind}, expected target: {expected_target_area_ind}, valid target: {target_area_ind}"
        # )

        self.target_area_index = props.getTargetViewportIndex(context, only_valid=True)
        # self.target_area = props.getValidTargetViewport(context)

        if target_area is None:
            _logger.debug_ext("Canceled op uas_shot_manager.sequence_timeline area", col="RED")
            return {"CANCELLED"}
        else:
            self.init_widgets(
                context, [BL_UI_Timeline(0, context.area.height - 25, context.area.width, 25, target_area=target_area)]
            )

            args = (self, context, self.widgets)
            self.register_handlers(args, context)

            context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.2, window=context.window)

    def unregister_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None
        self.draw_event = None

    def handle_widget_events(self, event):
        """handle event for sequence_timeline operator"""
        _logger.debug_ext("*-- handle event for sequence_timeline operator", col="GREEN", tag="TIMELINE_EVENT")

        result = False

        # if ignoreWidget(bpy.context):
        #     return False
        # else:
        for widget in self.widgets:
            if widget.handle_event(event):
                result = True

        return result

    ###################################
    # modal
    ###################################

    def modal(self, context, event):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        # _logger.debug_ext(f"uas_shot_manager.sequence_timeline  Modal", col="RED")

        # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
        if (
            not context.window_manager.UAS_shot_manager_display_overlay_tools
            or not prefs.toggle_overlays_turnOn_sequenceTimeline
            #   or not len(props.get_shots())
            or self.target_area_index != props.getTargetViewportIndex(context, only_valid=True)
        ):
            # _logger.debug_ext(f"sequence_timeline In Modal - for Cancel", col="RED")
            self.unregister_handlers(context)
            # return {"CANCELLED"}
            return {"FINISHED"}

        if context.area:
            # _logger.debug_ext(f"    context.area", col="YELLOW")
            if ignoreWidget(context):
                #    _logger.debug_ext(f"         ignore widget in sequence_timeline", col="RED")
                return {"PASS_THROUGH"}

            # print(f"playint: {bpy.context.screen.is_animation_playing}, scrubbing: {bpy.context.screen.is_scrubbing}")
            # if not bpy.context.screen.is_animation_playing or bpy.context.screen.is_scrubbing:
            else:
                if config.devDebug:
                    #         print("wkip modal redrawing of the Sequence Timeline")
                    pass
                # TODO: wkip here investigate for optimization cause this forced refresh is really greedy !!!
                # context.area.tag_redraw ( )

                # # for area in context.screen.areas:
                # #     if area.type == "VIEW_3D":
                # #         area.tag_redraw()
                # region.tag_redraw() #???? faster?

                # context.region.tag_redraw()
                # if not context.window_manager.UAS_shot_manager_toggle_shots_stack_interaction:
                #     return {"PASS_THROUGH"}

            if self.handle_widget_events(event):
                _logger.debug_ext("       handle widget events", col="PURPLE", tag="TIMELINE_EVENT")
                return {"RUNNING_MODAL"}

        #   _logger.debug_ext(f"      Pass Through", col="PURPLE")
        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw_callback_px(self, op, context, widgets):
        """Draw handler to paint onto the screen"""
        # print(
        #     f"*** context.window_manager.UAS_shot_manager_display_overlay_tools: {context.window_manager.UAS_shot_manager_display_overlay_tools}"
        # )
        # if not context.window_manager.UAS_shot_manager_display_overlay_tools:
        #     return

        if ignoreWidget(context):
            return

        # try:
        #     if self is None or self.draw_handle is None:
        #         print("*** draw_handled 11 in ogl context (draw_callback_px)")
        #         return
        # except Exception as e:
        #     # except NameError as e:
        #     # self = None  # or some other default value.
        #     _logger.error(f"*** Crash 11 in ogl context (draw_callback_px) - {e} ***")

        #     context.window_manager.UAS_shot_manager_display_overlay_tools = False
        #     bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        #     self.draw_handle = None
        #     return

        for widget in widgets:
            widget.draw()
        # # try:
        # #     for widget in widgets:
        # #         widget.draw()
        # # except Exception as e:
        # #     _logger.error(f"*** Crash 2 in ogl context (draw_callback_px) - {e} ***")

        # context.window_manager.UAS_shot_manager_display_overlay_tools = False
        # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        # self.draw_handle = None


_classes = (UAS_ShotManager_sequenceTimeline,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    # context.window_manager.UAS_shot_manager_display_overlay_tools = False
    # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
    # self.draw_handle = None

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
