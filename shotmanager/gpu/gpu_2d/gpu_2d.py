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
        :param region: if region is specified this will transform the vertices into the region's view. This allow for pan and zoom support
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

        posXIsInViewCS:     If True the position on X axis is in the View coordinate system of the region, posX is then in pixels
                            The position X of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the position on X axis is in the Region coordinate system, in frames.
                            The position X of the object will change if the region scale on x is changed (eg: time zoom)

                            Use posXIsInViewCS = True to display a quad with a constant position on x on the screen
                            Use posXIsInViewCS = False to display a clip that has to stay as a specific frame (a key for eg)

        posX:               The position on the X axis of the object. Its unit is in pixels if posXIsInViewCS is True, in frames otherwise


        posYIsInViewCS:     If True the position on Y axis is in the View coordinate system of the region, posY is then in pixels
                            The position Y of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the position on X axis is in the Region coordinate system, in number of lines.
                            The position Y of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use posYIsInViewCS = True to display a static quad for example
                            Use posYIsInViewCS = False to display a clip that has to match a line position

        posY:               The position on the Y axis of the object. Its unit is in pixels if posYIsInViewCS is True, in lines otherwise


        widthIsInViewCS:    If True the width is in the View coordinate system of the region, width is then in pixels
                            Width of the object will NOT change even if the region scale on x is changed (eg: time zoom)

                            If False the width is in the Region coordinate system, in frames.
                            Width of the object will change if the region scale on x is changed (eg: time zoom)

                            Use widthIsInViewCS = True to display a quad with a constant width on screen
                            Use widthIsInViewCS = False to display a clip that has to match a given amount of frames width

        width:              The width of the object. Its unit is in pixels if widthIsInViewCS is True, in frames otherwise


        heightIsInViewCS:   If True the height is in the View coordinate system of the region, height is then in pixels
                            Height of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the height is in the Region coordinate system, in number of lines.
                            Height of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use heightIsInViewCS = True to display a static quad for example
                            Use heightIsInViewCS = False to display a clip that has to match a line height

        height:             The height of the object. Its unit is in pixels if heightIsInViewCS is True, in lines otherwise

    """

    def __init__(
        self,
        posXIsInViewCS,
        posX=30,
        posYIsInViewCS=True,
        posY=50,
        widthIsInViewCS=True,
        width=40,
        heightIsInViewCS=True,
        height=20,
    ):

        self.posXIsInViewCS = posXIsInViewCS
        self.posX = posX
        self.posYIsInViewCS = posYIsInViewCS
        self.posY = posY

        self.widthIsInViewCS = widthIsInViewCS
        self.width = width
        self.heightIsInViewCS = heightIsInViewCS
        self.height = height


class QuadObject(Object2D, Mesh2D):
    def __init__(
        self,
        posXIsInViewCS=True,
        posX=30,
        posYIsInViewCS=True,
        posY=50,
        widthIsInViewCS=True,
        width=40,
        heightIsInViewCS=True,
        height=20,
    ):
        Object2D.__init__(
            self, posXIsInViewCS, posX, posYIsInViewCS, posY, widthIsInViewCS, width, heightIsInViewCS, height
        )
        Mesh2D.__init__(self)

    # override Mesh2D
    def draw(self, shader, region=None, draw_types="TRIS", cap_lines=False):
        self.rebuild_rectangle_mesh(self.posX, self.posY, self.width, self.height)

        transformed_vertices = self._vertices
        # if region:
        #     transformed_vertices = [
        #         region.view2d.view_to_region(*clamp_to_region(x, y, region), clip=True) for x, y in transformed_vertices
        #     ]

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
