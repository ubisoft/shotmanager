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
Example of use of the gpu package applued to the dopesheet region
"""


from .dopesheet_gpu_sample_widget import DopesheetGpuSampleWidget

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

from shotmanager.utils.utils_ogl import get_region_at_xy


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


# wkip really used???
def initialize_gDopesheetGpuSampleInfos():
    return {
        "prev_mouse_x": 0,
        "prev_mouse_y": 0,
        "frame_under_mouse": -1,
        "active_clip_index": -1,
        "active_clip_region": None,
        "clips": list(),
    }


##############################################################################################################
##############################################################################################################


class UAS_Gpu_DopesheetGpuSample(Operator):
    bl_idname = "uas_gpu.dopesheet_gpu_sample"
    bl_label = "Draw gpu sample in timeline"
    bl_options = {"REGISTER", "INTERNAL"}
    # bl_options = {"UNDO"}
    # !!! Important note: Do not set undo here: it doesn't work and it will be in conflic with the
    # calls to bpy.ops.ed.undo_push in the code !!!

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

        self.target_area = None
        self.target_area_index = -1

        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.prev_click = 0

        # self.active_clip = None
        # self.active_clip_region = None

        self.widgets = []

    def init_widgets(self, context, widgets):
        self.widgets = widgets
        for widget in self.widgets:
            widget.init(context)

    def __del__(self):
        # config.gRedrawShotStack = False
        pass

    ###################################
    # invoke
    ###################################

    def invoke(self, context, event):
        _logger.debug_ext("Invoke op dopesheet_gpu_sample", col="PURPLE")

        # if ignoreWidget(context):
        #     _logger.debug_ext("Canceled op uas_gpu.dopesheet_gpu_sample", col="PURPLE")
        #     context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample = False
        #     return {"CANCELLED"}

        # context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample = True

        props = config.getAddonProps(context.scene)
        # # config.gRedrawShotStack = False

        self.target_area_index = props.getTargetDopesheetIndex(context, only_valid=True)
        self.target_area = props.getValidTargetDopesheet(context)

        # if self.target_area is None:
        #     _logger.debug_ext("Canceled op uas_gpu.dopesheet_gpu_sample area", col="PURPLE")
        #     return {"CANCELLED"}
        # else:
        #     self.init_widgets(context, [DopesheetGpuSampleWidget(target_area=self.target_area)])
        self.init_widgets(context, [DopesheetGpuSampleWidget(target_area=self.target_area)])

        args = (self, context, self.widgets)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        # # if config.gShotsStackInfos is None:
        # #     config.gShotsStackInfos = initialize_gDopesheetGpuSampleInfos()

        # redraw all
        for area in context.screen.areas:
            area.tag_redraw()
        # context.scene.frame_current = context.scene.frame_current

        return {"RUNNING_MODAL"}

    ###################################
    # register handles
    ###################################

    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            self.draw_callback_px, args, "WINDOW", "POST_PIXEL"
        )

    def unregister_handlers(self, context):
        bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None
        self.draw_event = None

    def handle_widget_events(self, context, event):
        """handle event for dopesheet_gpu_sample operator"""
        # _logger.debug_ext(" handle_widget_events", col="PURPLE", tag="SHOTSTACK_EVENT")

        event_handled = False
        region, area = get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # get only events in the target area
        # wkip: mouse release out of the region have to be taken into account

        # events canceling the action
        # for widget in self.widgets:
        ##     if widget.manipulated_clip:  # removed
        #         if (
        #             (event.type == "LEFTMOUSE" and event.value == "RELEASE")
        #             or (event.type == "RIGHTMOUSE" and event.value == "RELEASE")
        #             or (event.type == "ESC" and event.value == "RELEASE")
        #         ):
        #             widget.cancelAction(context)
        #             event_handled = True

        # events doing the action
        if not event_handled:
            if self.target_area is not None and area == self.target_area:
                if region:
                    # if ignoreWidget(bpy.context):
                    #     return False
                    # else:
                    for widget in self.widgets:
                        if widget.handle_event(context, event, region):
                            event_handled = True
                            break

        return event_handled

    ###################################
    # modal
    ###################################

    def modal(self, context, event):
        # props = config.getAddonProps(context.scene)
        # prefs = config.getAddonPrefs()

        event_handled = False
        # _logger.debug_ext(f"uas_shot_manager.dopesheet_gpu_sample  Modal", col="PURPLE")

        # if event.type not in ["TIMER", "MOUSEMOVE"]:
        #     print(f"Modal, event type: {event.type}")

        # if config.gShotsStackInfos is None:
        #     config.gShotsStackInfos = initialize_gDopesheetGpuSampleInfos()

        if not context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample:
            _logger.debug_ext("dopesheet_gpu_sample In Modal - for Cancel", col="PURPLE")
            self.unregister_handlers(context)

            # redraw all
            for area in context.screen.areas:
                area.tag_redraw()
            # context.scene.frame_current = context.scene.frame_current

            # context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample = False
            # return {"CANCELLED"}
            return {"FINISHED"}

        # temp to remove
        return {"PASS_THROUGH"}

        # _logger.debug_ext(f"    context.area: {context.area}, self.target_area: {self.target_area}", col="YELLOW")
        if context.area:
            # _logger.debug_ext("    context.area", col="YELLOW")
            # if ignoreWidget(context):
            #     _logger.debug_ext("         ignore widget in dopesheet_gpu_sample", col="PURPLE")

            #     #  self.unregister_handlers(context)
            #     # for area in context.screen.areas:
            #     #     #    if area.type == "DOPESHEET_EDITOR" and area == self.target_area:
            #     #     area.tag_redraw()
            #     #     print("Ignioring...")
            #     return {"PASS_THROUGH"}

            event_handled = self.handle_widget_events(context, event)
            if event_handled:
                config.gRedrawShotStack = True
            #   return {"RUNNING_MODAL"}

        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        config.gMouseScreenPos[0] = event.mouse_x
        config.gMouseScreenPos[1] = event.mouse_y

        debug_forceRedraw = config.gShotsStack_forceRedraw_debug

        if config.gRedrawShotStack or event_handled or debug_forceRedraw:
            for area in context.screen.areas:
                area.tag_redraw()
            config.gRedrawShotStack = False
            config.gRedrawShotStack_preDrawOnly = False

        if event_handled:
            return {"RUNNING_MODAL"}

        # if debug_forceRedraw:
        #     return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self.unregister_handlers(context)

    def draw_callback_px(self, op, context, widgets):
        """Draw handler to paint onto the screen"""
        # print(
        #     f"*** context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample: {context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample}"
        # )
        # if not context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample:
        #     return

        # if ignoreWidget(context):
        #     return

        for widget in widgets:
            widget.draw(preDrawOnly=False)


_classes = (UAS_Gpu_DopesheetGpuSample,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    def _update_UAS_shot_manager__display_dopesheet_gpu_sample(self, context):
        if context.window_manager.UAS_shot_manager_display_dopesheet_gpu_sample:
            bpy.ops.uas_gpu.dopesheet_gpu_sample("INVOKE_DEFAULT")

    bpy.types.WindowManager.UAS_shot_manager_display_dopesheet_gpu_sample = BoolProperty(
        name="Show Dopesheet Gpu Sample",
        description="Toggle the display of the dopesheet gpu sample in the Dopesheet editor",
        update=_update_UAS_shot_manager__display_dopesheet_gpu_sample,
        default=False,
    )


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
