# GPLv3 License
#
# Copyright (C) 2020 Ubisoft
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
Useful entities for 2D gpu drawings
"""

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

from shotmanager.utils.utils_ogl import clamp_to_region
from shotmanager.utils import utils_editors_dopesheet
from shotmanager.utils.utils import color_to_sRGB, set_color_alpha, alpha_to_linear

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


def draw_tripod(xOrigin, yOrigin, scale=20, thickness=4):
    # tripod size in pixels
    tripodScale = scale
    lineThickness = thickness

    xOri, yOri = xOrigin, yOrigin
    x1, y1 = xOri + tripodScale, yOri
    x2, y2 = xOri, yOri + tripodScale

    vertices = (
        (xOri, yOri),
        (x1, y1),
        (x2, y2),
    )
    xAxisIndices = ((0, 1),)
    yAxisIndices = ((0, 2),)

    # draw lines and points fo the caps
    transformed_vertices = vertices

    bgl.glEnable(bgl.GL_BLEND)

    # X axis ####
    UNIFORM_SHADER_2D.bind()
    UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB((1.0, 0.0, 0.0, 1.0)))
    shader = UNIFORM_SHADER_2D

    batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices}, indices=xAxisIndices)
    bgl.glLineWidth(lineThickness)
    batch.draw(shader)

    # Y axis ####
    UNIFORM_SHADER_2D.bind()
    UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB((0.0, 1.0, 0.0, 1.0)))
    shader = UNIFORM_SHADER_2D

    batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices}, indices=yAxisIndices)
    bgl.glLineWidth(lineThickness)
    batch.draw(shader)
    # cap_lines = True
    # if cap_lines:
    #     batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices})
    #     bgl.glPointSize(lineThickness * 2)
    #     batch.draw(shader)


# 2D objects
############################################


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
        self._indicesLineRect = list()
        self._indicesLineRectClamped = list()

        self._texcoords = list() if texcoords is None else texcoords
        self.lineThickness = 1

        self.color = (0.9, 0.9, 0.0, 0.9)
        self.hasFill = True
        # contour
        self.hasLine = False

    @property
    def vertices(self):
        return list(self._vertices)

    @property
    def indices(self):
        return list(self._indices)

    @property
    def texcoords(self):
        return list(self._texcoords)

    def _drawMesh(
        self, shader, region=None, draw_types="TRIS", cap_lines=False, transformed_vertices=None, vertex_indices=None
    ):
        v_indices = vertex_indices

        bgl.glEnable(bgl.GL_BLEND)

        if shader is None:
            UNIFORM_SHADER_2D.bind()
            UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(self.color))
            shader = UNIFORM_SHADER_2D
        if "TRIS" == draw_types:
            if vertex_indices is None:
                v_indices = self._indices
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=v_indices)
            batch.draw(shader)
        elif "LINES" == draw_types:
            # draw lines and points fo the caps
            # _indicesLineRectClamped _indicesLineRect
            if vertex_indices is None:
                v_indices = self._indicesLineRect
            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=v_indices)
            bgl.glLineWidth(self.lineThickness)
            batch.draw(shader)
            if cap_lines:
                batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices})
                bgl.glPointSize(self.lineThickness)
                batch.draw(shader)
        elif "POINTS" == draw_types:
            # wkip here draw points for rounded line caps
            batch = batch_for_shader(shader, "POINTS", {"pos": transformed_vertices})
            bgl.glPointSize(self.lineThickness)
            batch.draw(shader)

    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        transformed_vertices = self._vertices
        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
            ]

        self._drawMesh(shader, region, draw_types, cap_lines, transformed_vertices)

    def rebuild_rectangle_mesh(self, posX, posY, width, height):
        # all those values are in pixels, in region CS
        # x1 y1 is at the bottom left of the rectangle, x4 y4 is at the top right
        # x1, y1 = posX, posY
        # x2, y2 = posX + width, posY
        # x3, y3 = posX, posY + height
        # x4, y4 = posX + width, posY + height

        vBotLeft = (min(posX, posX + width), min(posY, posY + height))
        vTopLeft = (min(posX, posX + width), max(posY, posY + height))
        vTopRight = (max(posX, posX + width), max(posY, posY + height))
        vBotRight = (max(posX, posX + width), min(posY, posY + height))
        # transformed_vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)

        self._vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)
        #  self._vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
        self._indices = ((0, 3, 1), (1, 3, 2))
        self._indicesLineRect = ((0, 3), (3, 2), (2, 1), (1, 0))
        # here the top line is not drawn
        self._indicesLineRectClamped = ((1, 0), (0, 3), (3, 2))


def build_rectangle_mesh(position, width, height, isLine=False):

    mesh = Mesh2D()
    mesh.rebuild_rectangle_mesh(position[0], position[1], width, height)
    if isLine:
        mesh.hasFill = False
        mesh.hasLine = True

    return mesh


class Object2D:
    """
    The View coordinate system of the region is a screen coordinate system, in pixels.
    Its origin is at the bottom left corner of the region (not of the area!), y axis pointing toward the top.

    The Region coordinate system of the region is a coordinate system depending on the state of the rulers or scroll bars.
    For dopesheets and timelines the X axis units are the frames and the Y axis units are values. For better commodity we
    are rather using lines, a line is 20 values height when the global UI scale factor is 1.0.
    Its origin is at the bottom left corner of the region (not of the area!), y axis pointing toward the top.

    The origin of the object (its position) is at its bottom left, y pointing topward.

    Class properties:

        posXIsInRegionCS:   If True the position on X axis is in the View coordinate system of the region, posX is then in pixels
                            The position X of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the position on X axis is in the Region coordinate system, in frames.
                            The position X of the object will change if the region scale on x is changed (eg: time zoom)

                            Use posXIsInRegionCS = True to display a quad with a constant position on x on the screen
                            Use posXIsInRegionCS = False to display a clip that has to stay as a specific frame (a key for eg)

        posX:               The position on the X axis of the object. Its unit is in pixels if posXIsInRegionCS is True, in frames otherwise


        posYIsInRegionCS:   If True the position on Y axis is in the View coordinate system of the region, posY is then in pixels
                            The position Y of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the position on X axis is in the Region coordinate system, in number of lines.
                            The position Y of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use posYIsInRegionCS = True to display a static quad for example
                            Use posYIsInRegionCS = False to display a clip that has to match a line position

        posY:               The position on the Y axis of the object. Its unit is in pixels if posYIsInRegionCS is True, in lines otherwise


        widthIsInRegionCS:  If True the width is in the View coordinate system of the region, width is then in pixels
                            Width of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the width is in the Region coordinate system, in frames.
                            Width of the object will change if the region scale on x is changed (eg: time zoom)

                            Use widthIsInRegionCS = True to display a quad with a constant width on screen
                            Use widthIsInRegionCS = False to display a clip that has to match a given amount of frames width

        width:              The width of the object. Its unit is in pixels if widthIsInRegionCS is True, in frames otherwise


        heightIsInRegionCS:   If True the height is in the View coordinate system of the region, height is then in pixels
                            Height of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the height is in the Region coordinate system, in number of lines.
                            Height of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use heightIsInRegionCS = True to display a static quad for example
                            Use heightIsInRegionCS = False to display a clip that has to match a line height

        height:             The height of the object. Its unit is in pixels if heightIsInRegionCS is True, in lines otherwise

        alignment:          aligment of the object to its origin
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

        alignmentToRegion: aligment of the object to its parent region
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

    """

    def __init__(
        self,
        posXIsInRegionCS=True,
        posX=30,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
    ):

        self.posXIsInRegionCS = posXIsInRegionCS
        self.posX = posX
        self.posYIsInRegionCS = posYIsInRegionCS
        self.posY = posY

        self.widthIsInRegionCS = widthIsInRegionCS
        self.width = width
        self.heightIsInRegionCS = heightIsInRegionCS
        self.height = height

        self.alignment = alignment
        self.alignmentToRegion = alignmentToRegion


class QuadObject(Object2D, Mesh2D):
    def __init__(
        self,
        posXIsInRegionCS=True,
        posX=30,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
        displayOverRuler=False,
    ):
        Object2D.__init__(
            self,
            posXIsInRegionCS,
            posX,
            posYIsInRegionCS,
            posY,
            widthIsInRegionCS,
            width,
            heightIsInRegionCS,
            height,
            alignment,
            alignmentToRegion,
        )
        Mesh2D.__init__(self)

        self.opacity = 1.0

        # attributes from MESH2D #########
        self.color = (0.9, 0.9, 0.0, 0.9)
        self.hasFill = True
        # contour
        self.hasLine = False
        self.colorLine = (0.9, 0.9, 0.9, 1.0)

        self.displayOverRuler = displayOverRuler

        # bBox is defined by [xMin, YMin, xMax, yMax], in pixels in region CS (so bottom left, compatible with mouse position)
        self._bBox = [0, 0, 1, 1]
        self.isFullyClamped = False

        self.rebuild_rectangle_mesh(0, 0, 1, 1)

    def getEdgeIndices(self, bBox, clamped_bBox):
        """Return the array of indices for the edges to draw"""
        indices = []
        if bBox[0] >= clamped_bBox[0]:
            indices.append((1, 0))
        if bBox[1] >= clamped_bBox[1]:
            indices.append((0, 3))
        if bBox[2] <= clamped_bBox[2]:
            indices.append((3, 2))
        if bBox[3] <= clamped_bBox[3]:
            indices.append((1, 2))
        return indices

    # override Mesh2D
    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):

        # aligment to region ###############
        alignmentsR = self.alignmentToRegion.split("_")
        alignmentR_x = alignmentsR[1]
        alignmentR_y = alignmentsR[0]

        # aligment to pivot ###############
        alignments = self.alignment.split("_")
        alignment_x = alignments[1]
        alignment_y = alignments[0]

        # position ###############
        if self.posXIsInRegionCS:
            # in this case self.posX is in pixels, with origin at the LEFT, X axis rightward
            posX = self.posX
        else:
            # in this case self.posX is in frames, with origin at the LEFT, X axis still rightward
            posX = region.view2d.view_to_region(self.posX, 0, clip=False)[0]

        if self.posYIsInRegionCS:
            # in this case self.posY is in pixels, with origin at the BOTTOM, Y axis upward
            posY = self.posY
        else:
            # in this case self.posY is in lanes, with origin at the TOP, Y axis DOWNWARD
            # the Y axis then has to be changed
            posY_inValues = -1.0 * utils_editors_dopesheet.getLaneToValue(self.posY)
            posY = region.view2d.view_to_region(0, -posY_inValues, clip=False)[1]

        # scale ##################
        if self.widthIsInRegionCS:
            width = self.width
        else:
            if self.posXIsInRegionCS:
                posX_inView = region.view2d.region_to_view(self.posX, 0)[0]
                posX_inRegion = self.posX
            else:
                posX_inView = self.posX
                posX_inRegion = region.view2d.view_to_region(self.posX, 0, clip=False)[0]

            width = region.view2d.view_to_region(posX_inView + self.width, 0, clip=False)[0] - posX_inRegion

        if self.heightIsInRegionCS:
            height = self.height
        else:
            # # height is in number of lanes
            # height_delta_Lane0 = 0
            # if self.posYIsInRegionCS:
            #     # this case may be buggy? Is it used?
            #     # not easy to fix since there is no vertical zoom on dopesheets
            #     posY_inView = region.view2d.region_to_view(0, self.posY)[1]
            #     posY_inRegion = self.posY
            # else:
            #     # convert from lanes to y values
            #     posY_inValues = -1.0 * utils_editors_dopesheet.getLaneToValue(self.posY)
            #     posY_inView = posY_inValues
            #     posY_inRegion = region.view2d.view_to_region(0, posY_inValues, clip=False)[1]

            #     # if posY is 0 then we have to compensate the height of the time ruler
            #     if self.posY < 1:
            #         height_delta_Lane0 = (
            #             utils_editors_dopesheet.getRulerHeight() - utils_editors_dopesheet.getLaneHeight()
            #         )

            # height_inValues = self.height * utils_editors_dopesheet.getLaneHeight() + height_delta_Lane0
            # height = region.view2d.view_to_region(0, posY_inView + height_inValues, clip=False)[1] - posY_inRegion

            # better way to compute the component height:
            # This way prevent rounding errors and ensure that there is not holes nor overlaps between components on
            # successive lanes
            numLanes = self.height
            if alignment_y in ("MID", "TOP"):
                height = utils_editors_dopesheet.getLaneToValue(
                    self.posY - numLanes + 1
                ) - utils_editors_dopesheet.getLaneToValue(self.posY + 1)
            else:
                height = utils_editors_dopesheet.getLaneToValue(
                    self.posY - numLanes
                ) - utils_editors_dopesheet.getLaneToValue(self.posY)

        # aligment to region ###############
        # horizontal
        if "RIGHT" == alignmentR_x:
            posX = region.width - posX
        elif "MID" == alignmentR_x:
            posX = posX + region.width / 2

        # vertical
        # vertical alignmentToRegion is ignored when posYIsInRegionCS is False (so linked to the view and channels, not to screen)
        if self.posYIsInRegionCS:

            if "TOP" == alignmentR_y:
                if self.posYIsInRegionCS:
                    # *** Warning: when Aligment to Region is TOP and posYIsInRegionCS is True then the Y axis points towards BOTTOM
                    # for the Y position (only, not for the height) (this avoid changing the sign of posY) ***
                    posY = region.height - posY
                else:
                    posY = posY  # + region.height
            elif "MID" == alignmentR_y:
                posY = posY + region.height / 2

        pivot_posX = posX
        pivot_posY = posY

        # aligment to pivot ###############
        # horizontal
        if "RIGHT" == alignment_x:
            posX = posX - width
        elif "MID" == alignment_x:
            posX = posX - width / 2

        # vertical
        if "TOP" == alignment_y:
            posY = posY - height
            # if self.posYIsInRegionCS:
            # else:
        elif "MID" == alignment_y:
            posY = posY - height / 2

        # posY = int(posY)
        # height = int(height)

        # if not self.heightIsInRegionCS and 1 == self.height:
        #     height = 1 * (
        #         utils_editors_dopesheet.getLaneToValue(self.posY - 1)
        #         - utils_editors_dopesheet.getLaneToValue(self.posY)
        #     )

        # posX and posY are the origin of the mesh, where the pivot is located
        # all those values are in pixels, in region CS
        # so far height and width can be negative
        vBotLeft = (min(posX, posX + width), min(posY, posY + height))
        vTopLeft = (min(posX, posX + width), max(posY, posY + height))
        vTopRight = (max(posX, posX + width), max(posY, posY + height))
        vBotRight = (max(posX, posX + width), min(posY, posY + height))
        transformed_vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)

        # clamp transform vertices: we get the intersection with the region
        # if the intersection is None then the current mesh is out of the region
        clamped_transformed_vertices = utils_editors_dopesheet.intersectionWithRegion(
            transformed_vertices, region, excludeRuler=not self.displayOverRuler
        )
        #  clamped_transformed_vertices = transformed_vertices

        # self._bBox = [vBotLeft[0], vBotLeft[1], vTopRight[0], vTopRight[1]]
        bBox = [
            transformed_vertices[0][0],
            transformed_vertices[0][1],
            transformed_vertices[2][0],
            transformed_vertices[2][1],
        ]

        # if clamped then the quad is not drawn
        if clamped_transformed_vertices is None:
            self.isFullyClamped = True
            self._bBox = bBox
            return

        self.isFullyClamped = False
        clamped_bBox = [
            clamped_transformed_vertices[0][0],
            clamped_transformed_vertices[0][1],
            clamped_transformed_vertices[2][0],
            clamped_transformed_vertices[2][1],
        ]
        self._bBox = clamped_bBox

        if self.hasFill:
            if shader is None:
                UNIFORM_SHADER_2D.bind()
                color = set_color_alpha(self.color, alpha_to_linear(self.color[3] * self.opacity))
                UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
                shader = UNIFORM_SHADER_2D

            self._drawMesh(shader, region, draw_types, cap_lines, clamped_transformed_vertices)

        if self.hasLine:
            UNIFORM_SHADER_2D.bind()
            color = set_color_alpha(self.colorLine, alpha_to_linear(self.colorLine[3] * self.opacity))
            UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
            shaderLine = UNIFORM_SHADER_2D
            draw_types = "LINES"

            edgeIndices = self.getEdgeIndices(bBox, clamped_bBox)

            self._drawMesh(shaderLine, region, draw_types, cap_lines, clamped_transformed_vertices, edgeIndices)

        # draw tripod
        if True:
            draw_tripod(pivot_posX, pivot_posY, 20)


class InteractiveObject2D:
    """Kind of abstract class or template to predefine the functions for interactions"""

    def __init__(
        self,
        targetArea,
    ):
        self.targetArea = targetArea

        self.isHighlighted = False
        self.isSelected = False

    def get_region_at_xy(self, context, x, y, area_type="VIEW_3D"):
        """Return the region and the area containing this region
        Does not support quadview right now
        Args:
            x:
            y:
        """
        for area in context.screen.areas:
            if area.type != area_type:
                continue
            # is_quadview = len ( area.spaces.active.region_quadviews ) == 0
            i = -1
            for region in area.regions:
                if region.type == "WINDOW":
                    i += 1
                    if region.x <= x < region.width + region.x and region.y <= y < region.height + region.y:

                        return region, area

        return None, None

    # to be overriden by inheriting classes
    def isInBBox(self, ptX, ptY):
        """Return True if the specified location is in the bbox of this InteractiveObject2D instance
        ptX and ptY are in screen coordinate system
        """
        # ptX_inRegion =
        return False

    # to override in classes inheriting from this class:
    def handle_event_custom(self, context, event, region):
        event_handled = False
        # if event.type == "G":
        mouseIsInBBox = self.isInBBox(event.mouse_x - region.x, event.mouse_y - region.y)

        # highlight ##############
        if mouseIsInBBox:
            if not self.isHighlighted:
                self.isHighlighted = True
                # _logger.debug_ext("component2D handle_events set highlighte true", col="PURPLE", tag="EVENT")
                config.gRedrawShotStack = True
        else:
            if self.isHighlighted:
                self.isHighlighted = False
                config.gRedrawShotStack = True

        # # selection ##############
        # if event.type == "LEFTMOUSE":
        #     if event.value == "PRESS":
        #         if mouseIsInBBox:
        #             if not self.isSelected:
        #                 self.isSelected = True
        #                 #_logger.debug_ext("component2D handle_events set selected true", col="PURPLE", tag="EVENT")
        #                 config.gRedrawShotStack = True

        #     if event.value == "RELEASE":

        return event_handled

    def handle_event(self, context, event):
        """handle event for InteractiveSpace operator"""
        _logger.debug_ext(" component2D handle_events", col="PURPLE", tag="EVENT")

        event_handled = False
        region, area = self.get_region_at_xy(context, event.mouse_x, event.mouse_y, "DOPESHEET_EDITOR")

        # get only events in the target area
        # wkip: mouse release out of the region have to be taken into account

        # events doing the action
        if not event_handled:
            if self.targetArea is not None and area == self.targetArea:
                if region:
                    # if ignoreWidget(bpy.context):
                    #     return False
                    # else:

                    # children
                    # for widget in self.widgets:
                    #     if widget.handle_event(context, event, region):
                    #         event_handled = True
                    #         break

                    # self
                    event_handled = self.handle_event_custom(context, event, region)

        return event_handled


# class Widget2D(InteractiveObject2D, Mesh2D):
class Component2D(InteractiveObject2D, QuadObject):
    """Interactive graphic 2D component"""

    def __init__(
        self,
        targetArea,
        posXIsInRegionCS=True,
        posX=30,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
    ):
        InteractiveObject2D.__init__(
            self,
            targetArea,
        )
        QuadObject.__init__(
            self,
            posXIsInRegionCS,
            posX,
            posYIsInRegionCS,
            posY,
            widthIsInRegionCS,
            width,
            heightIsInRegionCS,
            height,
            alignment,
            alignmentToRegion,
        )

        self.color = (0.2, 0.6, 0.0, 0.9)
        self.color_highlight = (0.6, 0.9, 0.6, 0.9)
        self.color_selected = (0.6, 0.9, 0.9, 0.9)
        self.color_selected_highlight = (0.6, 0.9, 0.9, 0.9)

    # override InteractiveObject2D
    # def handle_event_custom(self, context, event):
    #     event_handled = False
    #     if self.isInBBox(event.mouse_x, event.mouse_y):
    #         self.isHighlighted = True
    #     else:
    #         self.isHighlighted = False

    #     return event_handled

    # override InteractiveObject2D
    def isInBBox(self, ptX, ptY):
        """Return True if the specified location is in the bbox of this InteractiveObject2D instance
        ptX and ptY are in pixels, in region coordinate system
        """
        if not self.isFullyClamped:
            if self._bBox[0] <= ptX <= self._bBox[2] and self._bBox[1] <= ptY <= self._bBox[3]:
                return True
        return False

    # override Mesh2D
    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        # self.rebuild_rectangle_mesh(self.posX, self.posY, self.width, self.height)

        # if region:
        #     transformed_vertices = [
        #         region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
        #     ]

        if self.isSelected:
            if self.isHighlighted:
                widColor = self.color_selected_highlight
            else:
                widColor = self.color_selected
        else:
            if self.isHighlighted:
                widColor = self.color_highlight
            else:
                widColor = self.color

        # match (self.isHighlighted, self.isSelected):
        #     case (False, False):
        #         widColor = self.color
        #     case (True, False):
        #         widColor = self.color_highlight
        #     case (True, False):
        #         widColor = self.color_selected
        #     case (True, True):
        #         widColor = self.color_selected_highlight

        if shader is None:
            UNIFORM_SHADER_2D.bind()
            color = set_color_alpha(widColor, alpha_to_linear(widColor[3] * self.opacity))
            UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
            shader = UNIFORM_SHADER_2D

        QuadObject.draw(self, shader, region, draw_types, cap_lines)
