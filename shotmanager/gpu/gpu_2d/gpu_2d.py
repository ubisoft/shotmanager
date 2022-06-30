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
from shotmanager.utils import utils_editors


UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


def draw_tripod(xOrigin, yOrigin, scale=20, thickness=4):
    # tripod size in pixels
    tripodScale = scale
    linewidth = thickness

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
    UNIFORM_SHADER_2D.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
    shader = UNIFORM_SHADER_2D

    batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices}, indices=xAxisIndices)
    bgl.glLineWidth(linewidth)
    batch.draw(shader)

    # Y axis ####
    UNIFORM_SHADER_2D.bind()
    UNIFORM_SHADER_2D.uniform_float("color", (0.0, 1.0, 0.0, 1.0))
    shader = UNIFORM_SHADER_2D

    batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices}, indices=yAxisIndices)
    bgl.glLineWidth(linewidth)
    batch.draw(shader)
    # cap_lines = True
    # if cap_lines:
    #     batch = batch_for_shader(shader, "LINES", {"pos": transformed_vertices})
    #     bgl.glPointSize(linewidth * 2)
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

    def rebuild_rectangle_mesh(self, posX, posY, width, height, as_lines=False):
        """
        :param position:
        :param width:
        :param height:
        :return:
        """
        x1, y1 = posX, posY
        x2, y2 = posX + width, posY
        x3, y3 = posX, posY + height
        x4, y4 = posX + width, posY + height

        self._vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
        if as_lines:
            self._indices = ((0, 1), (0, 2), (2, 3), (1, 3))
        else:
            self._indices = ((0, 1, 2), (2, 1, 3))


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


class InteractiveObject2D(Object2D):
    """Use the pos and size of Object2D as a bbox for the interactive area"""

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

    def isInBBox(self, ptX, ptY):
        """Return True if the specified location is in the bbox of this InteractiveObject2D instance
        ptX and ptY are in screen coordinate system
        """
        # ptX_inRegion =
        return False

    # to override in classes inheriting from this class:
    def handle_event_custom(self, context, event):
        event_handled = False
        if self.isInBBox(event.mouse_x, event.mouse_y):
            self.isHighlighted = True
        else:
            self.isHighlighted = False

        return event_handled

    def handle_event(self, context, event):
        """handle event for InteractiveSpace operator"""
        # _logger.debug_ext(" handle_events", col="PURPLE", tag="EVENT")

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
                    event_handled = self.handle_event_custom(context, event)

        return event_handled


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
        height=100,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
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

        self.color = (0.9, 0.9, 0.0, 0.9)
        self.rebuild_rectangle_mesh(0, 0, 1, 1)

    # override Mesh2D
    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        #   self.rebuild_rectangle_mesh(self.posX, self.posY, self.width, self.height)

        # transformed_vertices = self._vertices
        # if region:
        #     transformed_vertices = [
        #         region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
        #     ]

        x1, y1 = 0, 0
        x2, y2 = 1, 0
        x3, y3 = 0, 1
        x4, y4 = 1, 1

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
            # height is in number of lanes
            height_delta_Lane0 = 0
            if self.posYIsInRegionCS:
                # this case may be buggy? Is it used?
                # not easy to fix since there is no vertical zoom on dopesheets
                posY_inView = region.view2d.region_to_view(0, self.posY)[1]
                posY_inRegion = self.posY
            else:
                # convert from lanes to y values
                posY_inValues = utils_editors.getLaneToValue(self.posY)
                posY_inView = posY_inValues
                posY_inRegion = region.view2d.view_to_region(0, posY_inValues, clip=False)[1]

                # if posY is 0 then we have to compensate the height of the time ruler
                if self.posY < 1:
                    height_delta_Lane0 = utils_editors.getRulerHeight() - utils_editors.getLaneHeight()

            height_inValues = self.height * utils_editors.getLaneHeight() + height_delta_Lane0

            height = region.view2d.view_to_region(0, posY_inView + height_inValues, clip=False)[1] - posY_inRegion

        # position ###############
        if self.posXIsInRegionCS:
            # in this case self.posX is in pixels, with origin at the LEFT, X axis rightward
            posX = self.posX
        else:
            # in this case self.posX is in frames, with origin at the LEFT, X axis still rightward

            #     # vertex[1] = region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True)
            #     vY = utils_editors.clampToRegion(0, vertex[1], region)[1]
            posX = region.view2d.view_to_region(self.posX, 0, clip=False)[0]

        if self.posYIsInRegionCS:
            # in this case self.posY is in pixels, with origin at the BOTTOM, Y axis upward
            posY = self.posY
        else:
            # in this case self.posY is in lanes, with origin at the TOP, Y axis DOWNWARD
            # the Y axis then has to be changed

            #     # vertex[1] = region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True)
            #     vY = utils_editors.clampToRegion(0, vertex[1], region)[1]
            posY_inValues = utils_editors.getLaneToValue(self.posY)
            posY = region.view2d.view_to_region(0, -posY_inValues, clip=False)[1]
            # height = -height

        # aligment to region ###############
        alignmentsR = self.alignmentToRegion.split("_")
        alignmentR_x = alignmentsR[1]
        alignmentR_y = alignmentsR[0]

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
        alignments = self.alignment.split("_")
        alignment_x = alignments[1]
        alignment_y = alignments[0]

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

        x1, y1 = posX, posY
        x2, y2 = posX + width, posY
        x3, y3 = posX, posY + height
        x4, y4 = posX + width, posY + height
        transformed_vertices = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

        # wkip to keep?
        bgl.glEnable(bgl.GL_BLEND)

        if shader is None:
            UNIFORM_SHADER_2D.bind()
            # UNIFORM_SHADER_2D.uniform_float("color", self.color)
            UNIFORM_SHADER_2D.uniform_float("color", self.color)
            shader = UNIFORM_SHADER_2D

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
        pass

        # draw tripod
        if True:
            draw_tripod(pivot_posX, pivot_posY, 20)


class Widget2D(InteractiveObject2D, Mesh2D):
    def __init__(
        self,
        targetArea,
        posXIsInRegionCS=True,
        posX=80,
        posYIsInRegionCS=True,
        posY=50,
        widthIsInRegionCS=True,
        width=40,
        heightIsInRegionCS=True,
        height=20,
    ):
        InteractiveObject2D.__init__(
            self,
            targetArea,
            posXIsInRegionCS,
            posX,
            posYIsInRegionCS,
            posY,
            widthIsInRegionCS,
            width,
            heightIsInRegionCS,
            height,
        )
        Mesh2D.__init__(self)

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

    # override Mesh2D
    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        self.rebuild_rectangle_mesh(self.posX, self.posY, self.width, self.height)

        transformed_vertices = self._vertices
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
            # UNIFORM_SHADER_2D.uniform_float("color", self.color)
            #    color = (0.9, 0.0, 0.0, 0.9)

            UNIFORM_SHADER_2D.uniform_float("color", widColor)
            shader = UNIFORM_SHADER_2D

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
        pass
