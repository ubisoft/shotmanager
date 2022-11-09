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
Workspace info: display info in bgl on workspace areas
Code initially coming from https://blender.stackexchange.com/questions/61699/how-to-draw-geometry-in-3d-view-window-with-bgl
"""

import math

import bpy
import blf

from mathutils import Vector
from shotmanager.utils import utils
from shotmanager.utils import utils_editors_dopesheet
from shotmanager.utils.utils_editors_dopesheet import getLaneHeight
from shotmanager.config import config

from shotmanager.gpu.gpu_2d.class_Mesh2D import build_rectangle_mesh


def toggle_workspace_info_display(context):
    # print("  toggle_workspace_info_display:  self.UAS_shot_manager_display_overlay_tools: ", self.UAS_shot_manager_display_overlay_tools)
    if (
        context.window_manager.UAS_shot_manager_identify_3dViews
        or context.window_manager.UAS_shot_manager_identify_dopesheets
    ):
        bpy.ops.shot_manager.workspace_info("INVOKE_DEFAULT")
        return
    else:
        return


def draw_typo_2d(color, text, position, font_size):
    font_id = 0
    dpi = 72
    z_detph = 0

    blf.position(font_id, position.x, position.y, z_detph)
    blf.color(font_id, color[0], color[1], color[2], color[3])
    blf.size(font_id, font_size, dpi)
    blf.draw(font_id, text)


# def draw_callback__user_info(self, context, callingArea, targetViewportIndex):
#     """Infos on user areas
#     """
#     if context.window_manager.UAS_shot_manager_identify_3dViews:
#         draw_callback__viewport_info(self, context, callingArea, targetViewportIndex)
#     if context.window_manager.UAS_shot_manager_identify_dopesheets:
#         draw_callback__dopesheet_info(self, context, callingArea, targetViewportIndex)


###################
# dopesheet and timeline
###################


def draw_callback__dopesheet_lane_numbers(self, context, callingArea, displayLaneIndices=True):
    opacity = 0.4
    color_even_lane = (0, 0.4, 0.9, opacity)
    color_odd_lane = (0.4, 0.9, 0.9, opacity)
    font_size = getLaneHeight()  # 12
    rect_width = 50

    blf.color(0, 0.9, 0.9, 0.9, 0.9)
    blf.size(0, font_size, 72)
    offset_y = 100

    rangeLanes = utils_editors_dopesheet.getDisplayedLanesRange(context.region)

    if displayLaneIndices:
        # for laneInd in range(0, rangeLanes[2]):
        drawSingleForDebug = False
        if drawSingleForDebug:
            laneInd = 1
            txtStr = f"{laneInd}"
            # vLaneYPos = utils_editors_dopesheet.getLaneToValue(laneInd + rangeLanes[0])
            vLaneYPos = utils_editors_dopesheet.getLaneToValue(laneInd)

            # here we use posX_inView rather than 0 otherwise view_to_region return 12000 for x and then also for y
            # and in this case pxLaneYPos is not usable anymore and the text disappears
            posX_inView = context.region.view2d.region_to_view(0, 0)[0]

            pxLaneXPos = context.region.view2d.view_to_region(posX_inView, vLaneYPos)[0]
            pxLaneYPos = context.region.view2d.view_to_region(posX_inView, vLaneYPos)[1]
            #   pxLaneYPos = context.region.view2d.view_to_region(0, -vLaneYPos)[1]
            txtStr = f"Lane ind: {laneInd}, vLaneYPos in View: {vLaneYPos}, pxLaneYPos in region: X:{pxLaneXPos} Y:{pxLaneYPos}"

            textPosY = 140
            textPosY = pxLaneYPos - getLaneHeight()

            # rect #################
            rect = build_rectangle_mesh((10, textPosY), rect_width, getLaneHeight())
            rect.color = color_even_lane
            rect.draw(None)

            # lane text ############

            blf.position(
                0,
                10,
                textPosY + getLaneHeight() / 5,
                0,
            )
            # blf.position(0, 10, vLaneYPos, 0)
            blf.draw(0, txtStr)

        else:
            # for laneInd in range(0, rangeLanes[2]):
            for laneInd in range(math.ceil(rangeLanes[0]), math.ceil(rangeLanes[1])):
                txtStr = f"{laneInd + math.ceil(rangeLanes[0])}"
                txtStr = f"{laneInd}"
                vLaneYPos = utils_editors_dopesheet.getLaneToValue(laneInd)
                # vLaneYPos = utils_editors_dopesheet.getLaneToValue(laneInd + math.ceil(rangeLanes[0]))

                # here we use posX_inView rather than 0 otherwise view_to_region return 12000 for x and then also for y
                # and in this case pxLaneYPos is not usable anymore and the text disappears
                posX_inView = context.region.view2d.region_to_view(0, 0)[0]
                pxLaneYPos = context.region.view2d.view_to_region(posX_inView, vLaneYPos)[1]
                # txtStr = f"Lane ind: {laneInd}, vLaneYPos in View: {vLaneYPos}, pxLaneYPos in region: {pxLaneYPos}"
                txtStr = f"{laneInd}"
                #  txtStr = f"Lane ind: {laneInd}, vLaneYPos in View: {vLaneYPos}, pxLaneYPos in region:{pxLaneYPos}"

                textPosX = 10
                if 0 != laneInd % 2:
                    textPosX += 10

                textPosY = 140
                textPosY = pxLaneYPos  # - getLaneHeight()
                # rect #################
                rect = build_rectangle_mesh((textPosX, textPosY), rect_width, getLaneHeight())
                rect.color = color_even_lane if 0 != laneInd % 2 else color_odd_lane
                rect.draw(None)

                # lane text ############

                blf.position(
                    0,
                    textPosX,
                    textPosY + getLaneHeight() / 5,
                    0,
                )
                # blf.position(0, 10, vLaneYPos, 0)
                blf.draw(0, txtStr)
        # for laneInd in range(0, rangeLanes[2]):
        #     txtStr = f"{laneInd + math.ceil(rangeLanes[0])}"
        #     vLaneYPos = utils_editors_dopesheet.getLaneToValue(laneInd + rangeLanes[0])

        #     pxLaneYPos = context.region.view2d.view_to_region(0, -vLaneYPos)[1]
        #     pxLaneYPos = context.region.view2d.view_to_region(0, -vLaneYPos)[1]
        #     txtStr = f"{vLaneYPos}"

        #     blf.position(
        #         0,
        #         10,
        #         pxLaneYPos,
        #         0,
        #     )
        #     # blf.position(0, 10, vLaneYPos, 0)
        #     blf.draw(0, txtStr)

    txtStr = f"Range Lanes: [{rangeLanes[0]:03.2f}, {rangeLanes[1]:03.2f}], num full lanes: {rangeLanes[2]:03.2f}"
    blf.size(0, 12, 72)
    blf.position(0, 60, offset_y, 0)
    blf.draw(0, txtStr)


def draw_callback__dopesheet_mouse_pos(self, context, callingArea):
    blf.color(0, 0.9, 0.9, 0.9, 0.9)
    blf.size(0, 12, 72)
    offset_y = 80

    rMouse_x = config.gMouseScreenPos[0] - context.region.x
    rMouse_y = config.gMouseScreenPos[1] - context.region.y

    ruMouse_x = int(context.region.view2d.region_to_view(rMouse_x, 0)[0])
    # y in region values unit
    ruMouse_y = int(context.region.view2d.region_to_view(0, rMouse_y)[1])
    # y in lanes
    #  ruMouse_y = -1.0 * ruMouse_y // utils_editors.getLaneHeight()

    # y in lanes
    ruMouse_y_in_Lanes = utils_editors_dopesheet.getLaneIndexUnderLocationY(context.region, rMouse_y)

    txtStr = f"Mouse pos: Screen: x: {config.gMouseScreenPos[0]}, y: {config.gMouseScreenPos[1]},  - in Region px: rX: {rMouse_x}, rY: {rMouse_y},"
    txtStr += f"- in Region units: ruX: {ruMouse_x} fr., ruY: {ruMouse_y} values,    rY: {ruMouse_y_in_Lanes} lanes"

    blf.position(0, 60, offset_y, 0)
    blf.draw(0, txtStr)


def draw_callback__dopesheet_size(self, context, callingArea):
    blf.color(0, 0.9, 0.9, 0.9, 0.9)

    # blf.size(0, round(self.font_size * get_prefs_ui_scale()), 72)
    blf.size(0, 12, 72)
    # textPos_y = self.origin.y + 6 * get_prefs_ui_scale()
    # textPos_y = self.origin.y + utils_editors_dopesheet.getLaneHeight() * 0.2
    # blf.position(0, *context.region.view2d.view_to_region(self.origin.x + 1.4, textPos_y), 0)

    offset_y = 20
    # in view units
    areaBoxSize = utils_editors_dopesheet.getRegionFrameRange(context, callingArea, inViewUnits=True)
    widthStr = f"Width range: {(areaBoxSize[0]):03.2f} fr, {(areaBoxSize[2]):03.2f} fr, width: {(areaBoxSize[2] - areaBoxSize[0]):03.2f} fr"

    rHeightRangeMin = areaBoxSize[1]
    rHeightRangeMax = areaBoxSize[3]
    rHeight = rHeightRangeMax - rHeightRangeMin

    ruHeightRangeMin = rHeightRangeMin // getLaneHeight()
    ruHeightRangeMax = rHeightRangeMax // getLaneHeight()
    ruHeight = rHeight / getLaneHeight()

    heightStr = f"Height range: {rHeightRangeMin:03.2f}, {rHeightRangeMax:03.2f}, height: {rHeight:03.2f},  range in lanes: {ruHeightRangeMin:03.2f}, {ruHeightRangeMax:03.2f}, num lanes: {ruHeight:03.2f}"

    blf.position(0, 60, offset_y, 0)
    blf.draw(0, widthStr)
    blf.position(0, 60, offset_y * 2, 0)
    blf.draw(0, heightStr)

    # in screen units
    # This defines the dopesheet content region size in pixels (without the left panel listing the channels)
    # Bottom left is the origin, so at [0, 0]
    areaBoxSize = utils_editors_dopesheet.getRegionFrameRange(context, callingArea, inViewUnits=False)
    # widthStr = f"Width range: {(areaBoxSize[0]):03.2f} px, {(areaBoxSize[2]):03.2f} px"
    # heightStr = f"Height range: {(areaBoxSize[1]):03.2f} px, {(areaBoxSize[3]):03.2f} px"
    txtStr = f"Region box (in pixels, origin: bottom left): B Lft: [{(areaBoxSize[0]):03.1f}, {(areaBoxSize[1]):03.1f}], T Rght: [{(areaBoxSize[2]):03.1f}, {(areaBoxSize[3]):03.1f}]"

    blf.position(0, 60, offset_y * 3, 0)
    blf.draw(0, txtStr)
    # blf.position(0, 60, offset_y * 4, 0)
    # blf.draw(0, heightStr)


def draw_callback__dopesheet_info(self, context, callingArea, targetDopesheetIndex):
    """Infos on dopesheet areas"""
    if not context.window_manager.UAS_shot_manager_identify_dopesheets:
        return

    dopesheets = utils.getDopesheets(context)

    contextDopesheetsInd = -1
    for i, screen_area in enumerate(dopesheets):
        if context.area == dopesheets[i]:
            contextDopesheetsInd = i
            break

    if len(dopesheets):
        position = Vector([70, 40])
        size = 30
        if targetDopesheetIndex == contextDopesheetsInd:
            color = (0.1, 0.95, 0.1, 1.0)
        else:
            color = (0.95, 0.95, 0.95, 1.0)

        areaIndStr = "?" if -1 == contextDopesheetsInd else contextDopesheetsInd
        draw_typo_2d(color, f"Dopesheet: {areaIndStr}", position, size)


###################
# 3d viewport
###################


def draw_callback__viewport_info(self, context, callingArea, targetViewportIndex):
    """Infos on viewport areas"""
    if not context.window_manager.UAS_shot_manager_identify_3dViews:
        return

    viewports = utils.getAreasByType(context, "VIEW_3D")

    contextViewportInd = -1
    for i, screen_area in enumerate(viewports):
        if context.area == viewports[i]:
            contextViewportInd = i
            break

    if len(viewports):
        if targetViewportIndex == contextViewportInd:
            color = (0.1, 0.95, 0.1, 1.0)
            posY = 200
        else:
            color = (0.95, 0.95, 0.95, 1.0)
            posY = 115

        size = 50
        posY -= 55
        position = Vector([70, posY])
        areaIndStr = "?" if -1 == contextViewportInd else contextViewportInd
        draw_typo_2d(color, f"3D View: {areaIndStr}", position, size)

        if targetViewportIndex == contextViewportInd:
            size = 20
            posY -= 28
            message = "Current Shot Manager Target"
            position = Vector([70, posY])
            draw_typo_2d(color, f"{message}", position, size)

            size = 14
            posY -= 22
            message = "Shot Manager is using this viewport to set the camera of the current shot"
            position = Vector([70, posY])
            draw_typo_2d(color, f"{message}", position, size)
            posY -= 18
            message = "and control several overlays settings."
            position = Vector([70, posY])
            draw_typo_2d(color, f"{message}", position, size)
            posY -= 18
            message = "The target viewport can be changed from the Shot Manager panel."
            position = Vector([70, posY])
            draw_typo_2d(color, f"{message}", position, size)


###################
# Advanced infos and debug - common to all editors
###################


def draw_callback__area_advanced_info(self, context, callingArea, targetViewportIndex):
    """Advanced and debug infos on all areas
    context.area is the calling area, from where the initial message was sent (= the current area)
    """
    # return
    # bgl.glClearStencil(0)
    # bgl.glClear(0)
    # bgl.glClearStencil(1)
    # bgl.glClear(1)
    # bgl.glClearStencil(2)
    # bgl.glClear(2)

    # get all areas ######
    # context.area is the calling area, from where the initial message was sent (= the current area)
    areasList = list()
    for screen_area in context.screen.areas:
        #     if screen_area.type == "VIEW_3D":
        areasList.append(screen_area)

    contextArea = context.area
    contextAreaInd = -1
    for i, area in enumerate(context.screen.areas):
        if area == context.area:
            contextAreaInd = i
            break

    # get calling area ######
    callingAreaType = callingArea.type
    callingAreaInd = -1
    for i, area in enumerate(context.screen.areas):
        if area == callingArea:
            callingAreaInd = i
            break

    # get dopesheets ######
    contextViewportInd = -1
    dopesheets = utils.getAreasByType(context, "DOPESHEET_EDITOR")
    for i, dopesh in enumerate(dopesheets):
        if dopesh == context.area:
            contextViewportInd = i
            break

    # get viewports ######
    contextViewportInd = -1
    viewports = utils.getAreasByType(context, "VIEW_3D")
    for i, viewport in enumerate(viewports):
        if viewport == context.area:
            contextViewportInd = i
            break

    # get calling viewport ######
    callingViewportInd = -1
    for i, viewport in enumerate(viewports):
        if viewport == callingArea:
            callingViewportInd = i
            break

    ##########################
    # Display ################
    size = 14
    color = (1.0, 0.6, 0.6, 1.0)
    y_offset = -18
    position = Vector([60, 170])

    if len(viewports):
        if contextViewportInd == targetViewportIndex:
            color = (0.0, 1.0, 0.0, 1.0)
        elif contextViewportInd == callingViewportInd:
            color = (1.0, 1.0, 0.0, 1.0)

    # type (VIEW_3D, Dopesheet...) ###
    message = f"{contextArea.type}"
    if "VIEW_3D" == contextArea.type:
        message += f":  {contextViewportInd}"
    elif "DOPESHEET_EDITOR" == contextArea.type:
        message += f" in mode {contextArea.spaces[0].mode}"

    position.y += y_offset
    draw_typo_2d(color, f"{message}", position, size + 2)

    if len(viewports):
        if "VIEW_3D" == contextArea.type:
            position.y += y_offset
            draw_typo_2d(
                color,
                f"Viewport index: {contextViewportInd}, Num viewports: {len(viewports)}, Calling viewport: {callingViewportInd}",
                position,
                size,
            )

            position.y += y_offset
            message = f"Shot Manager target viewport: {targetViewportIndex}"
            draw_typo_2d(color, f"{message}", position, size)

    position.y += y_offset - 10
    message = f"Context area index: {contextAreaInd}, Tolal number of areas: {len(context.screen.areas)}"
    draw_typo_2d(color, f"{message}", position, size)

    position.y += y_offset - 10
    message = f"Calling area index: {callingAreaInd}, type: {callingAreaType}"
    draw_typo_2d(color, f"{message}", position, size)

    position.y += -10

    if len(dopesheets):
        if "DOPESHEET_EDITOR" == contextArea.type:
            draw_callback__dopesheet_size(self, context, contextArea)
            draw_callback__dopesheet_mouse_pos(self, context, contextArea)


class ShotManager_WorkspaceInfo(bpy.types.Operator):
    bl_idname = "shot_manager.workspace_info"
    bl_label = "Simple Modal View3D Operator"

    def __init__(self):
        print("Initialize ShotManager_WorkspaceInfo")
        # self.draw_handle = None
        # self.draw_event = None
        self._handle_draw_onView3D = None
        self._handle_draw_onDopeSheet = None

    def register_handlers(self, args, context):
        # self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
        #     self.draw, args, "WINDOW", "POST_PIXEL"
        # )
        # self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        pass

    def unregister_handlers(self, context):

        print("unregister_handlers ShotManager_WorkspaceInfo")
        # context.window_manager.event_timer_remove(self.draw_event)
        # bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")

        if self._handle_draw_onView3D is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw_onView3D, "WINDOW")
            self._handle_draw_onView3D = None

        if self._handle_draw_onDopeSheet is not None:
            bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self._handle_draw_onDopeSheet, "WINDOW")
            self._handle_draw_onDopeSheet = None

        # redraw all
        for area in context.screen.areas:
            area.tag_redraw()

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)

        # callingAreaType = context.area.type
        # callingAreaIndex = utils.getAreaIndex(context, context.area, "VIEW_3D")

        targetViewportIndex = props.getTargetViewportIndex(context)
        targetDopesheetIndex = props.getTargetDopesheetIndex(context)

        if config.devDebug:
            # the arguments we pass the the callback
            # message = f"Calling area index: {callingAreaIndex}, type: {callingAreaType}"
            # message2 = f"target: {targetViewportIndex}"
            args = (self, context, context.area, targetViewportIndex)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            #   self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, "WINDOW", "POST_VIEW")
            # self._handle_draw_onView3D = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, "WINDOW", "POST_PIXEL")

            # see types of spaces here: https://docs.blender.org/api/current/bpy.types.Space.html#bpy.types.Space
            self._handle_draw_onView3D = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback__area_advanced_info, args, "WINDOW", "POST_PIXEL"
            )
            self._handle_draw_onDopeSheet = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
                draw_callback__area_advanced_info, args, "WINDOW", "POST_PIXEL"
            )

            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        else:
            # the arguments we pass the the callback
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            #   self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, args, "WINDOW", "POST_VIEW")
            # self._handle_draw_onView3D = bpy.types.SpaceView3D.draw_handler_add(draw_callback_2d, args, "WINDOW", "POST_PIXEL")

            args = (self, context, context.area, targetViewportIndex)
            self._handle_draw_onView3D = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback__viewport_info, args, "WINDOW", "POST_PIXEL"
            )

            args = (self, context, context.area, targetDopesheetIndex)
            self._handle_draw_onDopeSheet = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
                draw_callback__dopesheet_info, args, "WINDOW", "POST_PIXEL"
            )

            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
            # else:
            #     self.report({"WARNING"}, "View3D not found, cannot run operator")
            #     return {"CANCELLED"}

    def modal(self, context, event):
        #    context.area.tag_redraw()

        # code for press and release but

        # if event.type == "LEFTMOUSE":
        #     if event.value == "PRESS":
        #         print("LMB Pressed")

        #     elif event.value == "RELEASE":
        #         print("LMB Released")
        #         # print("Modal ShotManager_WorkspaceInfo")
        #         context.window_manager.UAS_shot_manager_identify_3dViews = False
        #         bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw_onView3D, "WINDOW")
        #         return {"FINISHED"}

        if (
            not context.window_manager.UAS_shot_manager_identify_3dViews
            and not context.window_manager.UAS_shot_manager_identify_dopesheets
        ):
            # or event.type in {"RIGHTMOUSE", "ESC"}
            #   bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, "WINDOW")

            self.unregister_handlers(context)

            return {"CANCELLED"}

        return {"PASS_THROUGH"}
        # return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(ShotManager_WorkspaceInfo)


def unregister():
    try:
        self.unregister_handlers(bpy.context)
    except Exception:
        if config.devDebug:
            print("Cannot remove SpaceView3D.draw_handler")

    bpy.utils.unregister_class(ShotManager_WorkspaceInfo)


# if __name__ == "__main__":
#     register()
