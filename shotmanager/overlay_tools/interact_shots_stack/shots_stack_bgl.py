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

import math

import bpy
import bgl
import gpu

from mathutils import Vector

from shotmanager.utils import utils
from shotmanager.utils import utils_editors_dopesheet
from shotmanager.overlay_tools.workspace_info.workspace_info import draw_typo_2d

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

# deprecated - use getPrefsUIScale


def get_prefs_ui_scale():
    # ui_scale has a very weird behavior, especially between 0.79 and 0.8. We try to compensate it as
    # much as possible
    factor = 0
    if bpy.context.preferences.view.ui_scale >= 1.1:
        factor = 0.2
    if bpy.context.preferences.view.ui_scale >= 1.0:
        factor = 0.0
    elif bpy.context.preferences.view.ui_scale >= 0.89:
        factor = 1.6
    elif bpy.context.preferences.view.ui_scale >= 0.79:
        factor = 0.0
    elif bpy.context.preferences.view.ui_scale >= 0.69:
        factor = 0.1
    else:
        factor = 0.15

    return bpy.context.preferences.view.ui_scale + abs(bpy.context.preferences.view.ui_scale - 1) * factor


# deprecated - use -
def get_lane_origin_y(lane):
    """Return the offset to put under the timeline ruler"""
    RULER_HEIGHT = 52
    RULER_HEIGHT = 40
    return math.floor(
        -1.0 * utils_editors_dopesheet.getLaneHeight() * lane - (RULER_HEIGHT * bpy.context.preferences.view.ui_scale)
    )


##############################################################################################################
##############################################################################################################


def drawAreaInfo(context, pos_y=90):
    """Draw the information about the area
    Calling area is given by context.area
    Args:

    See: https://blender.stackexchange.com/questions/55418/dopesheet-grapheditor-how-to-detect-change-with-api-displayed-frame-range

    """
    # # if not context.window_manager.UAS_shot_manager_identify_dopesheets:
    # #     return

    # dopesheets = utils.getDopesheets(context)

    # contextDopesheetsInd = -1
    # for i, screen_area in enumerate(dopesheets):
    #     if context.area == dopesheets[i]:
    #         contextDopesheetsInd = i
    #         break

    size = 20
    color = (0.95, 0.95, 0.95, 1.0)
    position = Vector([70, pos_y])
    position2 = Vector([70, pos_y - size - 5])
    position3 = Vector([70, pos_y - 2 * size - 5])
    # for i, area in enumerate(context.screen.areas):
    # if area.type == area_type:
    #     areasList.append(area)
    # draw_typo_2d(color, f"Area {i}: {area.type}", position, size)

    region = context.area.regions[-1]
    # print(f"SCREEN: {context.screen.name}")

    h = region.height  # screen
    w = region.width  #
    bl = region.view2d.region_to_view(0, 0)
    tr = region.view2d.region_to_view(w, h)
    # tr = region.view2d.region_to_view(1, 1)

    # bl2 = region.view2d.view_to_region(0, 0)
    # tr2 = region.view2d.view_to_region(1, 1)

    draw_typo_2d(color, f"Area {'x'}: width:{context.area.width}, region w: {region.width}", position, size)
    # draw_typo_2d(color, f"screen: {context.screen.name}", position2, size)
    draw_typo_2d(color, f"region top right: {tr}, bottom left: {bl}", position2, size)
    draw_typo_2d(color, f"Number of frames displayed: {tr[0]}", position3, size)


#  draw_typo_2d(color, f"region top right: {tr2}, bottom left: {bl2}", position3, size)

# if len(dopesheets):
# if targetDopesheetIndex == contextDopesheetsInd:
#     color = (0.1, 0.95, 0.1, 1.0)
# else:

# areaIndStr = "?" if -1 == contextDopesheetsInd else contextDopesheetsInd
# draw_typo_2d(color, f"Dopesheet: {areaIndStr}", position, size)


# !!! not in the class !!!
def draw_callback_modal_overlay(context, callingArea, targetAreaType="ALL", targetAreaIndex=-1, color=1):
    """Everything in this function should be accessible globally
    There can be only one registrer draw handler at at time
    Args:
        targetAreaType: can be DOPESHEET, VIEWPORT
        targetAreaIndex: index of the target in the list of the areas of the specified type
    """
    print("ogl")
    # if target_area is not None and context.area != target_area:
    #     return False

    # debug:
    targetAreaType = "ALL"

    okForDrawing = False
    if "ALL" == targetAreaType:
        okForDrawing = True

    elif "DOPESHEET" == targetAreaType:
        dopesheets = utils.getDopesheets(context)

        _contextDopesheetsInd = -1
        for i, screen_area in enumerate(dopesheets):
            if context.area == dopesheets[i]:
                _contextDopesheetsInd = i
                break

        if len(dopesheets):
            okForDrawing = targetAreaIndex == _contextDopesheetsInd

    if 1 == color:
        drawAreaInfo(context)
    else:
        drawAreaInfo(context, pos_y=60)
    # targetAreaType, targetAreaIndex

    if okForDrawing:
        print("ogl2")
        bgl.glEnable(bgl.GL_BLEND)
        UNIFORM_SHADER_2D.bind()
        color = (0.9, 0.0, 0.0, 0.9)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        config.tmpTimelineModalRect.draw(UNIFORM_SHADER_2D, context.region)
