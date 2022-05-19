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


import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from shotmanager.utils import utils
from shotmanager.overlay_tools.workspace_info.workspace_info import draw_typo_2d

from shotmanager.utils.utils import clamp, gamma_color, color_is_dark

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

LANE_HEIGHT = 18


def get_lane_origin_y(lane):
    return -LANE_HEIGHT * lane - 39  # an offset to put it under timeline ruler.

def draw_shots_stack(context):
    ## with dico
    # print(f" suis dans draw_shots_stack: config.gShotsStackInfos: {config.gShotsStackInfos}")

    # _logger.debug_colored("Here 80 - config.gShotsStackInfos Clips len: " + str(len(config.gShotsStackInfos["clips"])))

    if config.gShotsStackInfos is not None:
        # _logger.debug_ext("Redraw in draw_shots_stack", col="PURPLE")
        #    _logger.debug_colored("Here 82")
        for i, clip in enumerate(config.gShotsStackInfos["clips"]):
            # _logger.debug_ext(
            #     f"highlight Shot handle over loop, clip {i}{config.gShotsStackInfos['active_clip_index']} region: {config.gShotsStackInfos['active_clip_region']}",
            #     col="BLUE",
            # )

            clip.highlight = i == config.gShotsStackInfos["active_clip_index"]
            clip.active_region = config.gShotsStackInfos["active_clip_region"]
            clip.active_clip_over = config.gShotsStackInfos["active_clip_over"]
            clip.draw(context)
            # try:
            #     clip.draw(context)
            # except Exception as e:
            #     # wkip wkip
            #     pass
        #    _logger.debug_colored("Here 84")
        if config.gShotsStackInfos["frame_under_mouse"] != -1:
            blf.color(0, 0.99, 0.99, 0.99, 1)
            blf.size(0, 11, 72)
            blf.position(
                0, config.gShotsStackInfos["prev_mouse_x"] + 4, config.gShotsStackInfos["prev_mouse_y"] + 10, 0
            )
            blf.draw(0, str(config.gShotsStackInfos["frame_under_mouse"]))

        if config.devDebug:
            blf.color(0, 0.99, 0.1, 0.1, 1)
            blf.size(0, 35, 72)
            blf.position(0, 100, 100, 0)
            # blf.draw(0, "Toto")
        #  blf.draw(0, f"Last: {config.devDebug_lastRedrawTime}")


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
            (
                transformed_vertices[0][0],
                transformed_vertices[0][1],
            ),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[0][1],
            ),
            (
                transformed_vertices[0][0] + transformed_vertices[3][1] - transformed_vertices[0][1],
                transformed_vertices[3][1],
            ),
            (
                transformed_vertices[0][0],
                transformed_vertices[3][1],
            ),
        )

        batch = batch_for_shader(
            self._shader,
            "TRI_FAN",
            {
                "pos": verticesSquare,
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
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

    bl2 = region.view2d.view_to_region(0, 0)
    tr2 = region.view2d.view_to_region(1, 1)

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


## !!! not in the class !!!
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
