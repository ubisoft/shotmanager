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
Utility functions for opengl overlay
"""

import gpu
from gpu_extras.batch import batch_for_shader

# Blender windows system utils
############################################


def get_region_at_xy(context, x, y, area_type="VIEW_3D"):
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


# Geometry utils functions
############################################


class Square:
    """Draw a rectangle filled with the specifed color, from bottom left corner and with
    width and height.
    Origin of the object is at the center.

    **** Warning: crappy implementation: not a square but a rect, and with MIDDLE_MIDDLE provided height and width are half the size
    of the expected result ! ***
    """

    UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def __init__(self, x, y, sx, sy, color=(1.0, 1.0, 1.0, 1.0), origin="MIDDLE_MIDDLE"):
        """
        origin can be: MIDDLE_MIDDLE, BOTTOM_LEFT
        """
        self._x = x
        self._y = y
        self._sx = sx
        self._sy = sy
        self._color = color
        self._origin = origin

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def sx(self):
        return self._sx

    @sx.setter
    def sx(self, value):
        self._sx = value

    @property
    def sy(self):
        return self._sy

    @sy.setter
    def sy(self, value):
        self.sy = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value

    def copy(self):
        return Square(self.x, self.y, self.sx, self.sy, self.color, self.origin)

    def draw(self, position=None):
        if "BOTTOM_LEFT" == self._origin:
            vertices = (
                (self._x, self._sy + self._y),
                (self._sx + self._x, self._sy + self._y),
                (self._x, self._y),
                (self._sx + self._x, self._y),
            )
        else:
            vertices = (
                (-self._sx + self._x, self._sy + self._y),
                (self._sx + self._x, self._sy + self._y),
                (-self._sx + self._x, -self._sy + self._y),
                (self._sx + self._x, -self._sy + self._y),
            )
        # vertices += [ pos_2d.x, pos_2d.y ]
        indices = ((0, 1, 2), (2, 1, 3))

        batch = batch_for_shader(self.UNIFORM_SHADER_2D, "TRIS", {"pos": vertices}, indices=indices)

        self.UNIFORM_SHADER_2D.bind()
        self.UNIFORM_SHADER_2D.uniform_float("color", self._color)
        batch.draw(self.UNIFORM_SHADER_2D)

    def bbox(self):
        return (-self._sx + self._x, -self.sy + self._y), (self._sx + self._x, self._sy + self._y)


class Rect:
    """Draw a rectangle filled with the specifed color, from bottom left corner and with
    width and height.
    Origin of the object is at the center.
    """

    UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def __init__(self, x, y, sx, sy, color=(1.0, 1.0, 1.0, 1.0), origin="MIDDLE_MIDDLE"):
        """
        origin can be: MIDDLE_MIDDLE, BOTTOM_LEFT
        """
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.color = color
        self.origin = origin

    def copy(self):
        return Rect(self.x, self.y, self.sx, self.sy, self.color, self.origin)

    def draw(self, position=None):
        if "BOTTOM_LEFT" == self.origin:
            vertices = (
                (self.x, self.y + self.sy),
                (self.x + self.sx, self.y + self.sy),
                (self.x, self.y),
                (self.x + self.sx, self.y),
            )
        else:
            vertices = (
                (self.x - 0.5 * self.sx, self.y + 0.5 * self.sy),
                (self.x + 0.5 * self.sx, self.y + 0.5 * self.sy),
                (self.x - 0.5 * self.sx, self.y - 0.5 * self.sy),
                (self.x + 0.5 * self.sx, self.y - 0.5 * self.sy),
            )
        # vertices += [ pos_2d.x, pos_2d.y ]
        indices = ((0, 1, 2), (2, 1, 3))

        batch = batch_for_shader(self.UNIFORM_SHADER_2D, "TRIS", {"pos": vertices}, indices=indices)

        self.UNIFORM_SHADER_2D.bind()
        self.UNIFORM_SHADER_2D.uniform_float("color", self.color)
        batch.draw(self.UNIFORM_SHADER_2D)

    # def bbox(self):
    #     return (-self.sx + self.x, -self.sy + self.y), (self.sx + self.x, self.sy + self.y)


class Quadrilater:
    """Draw a quadrilater filled with the specifed color, from bottom left corner and with
    width and height.
    Origin of the object is at the center.
    """

    UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def __init__(self, pt0, pt1, pt2, pt3, color=(1.0, 1.0, 1.0, 1.0)):
        self.pt0 = pt0
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3
        self.color = color

    def copy(self):
        return Quadrilater(self.pt0, self.pt1, self.pt2, self.pt3, self.color)

    def draw(self, position=None):
        # vertices = (
        #     (self.pt0),
        #     (self.pt1),
        #     (self.pt2),
        #     (self.pt3),
        # )
        # indices = ((0, 1, 2), (2, 3, 1))

        verticesLine = (
            (self.pt0),
            (self.pt1),
            (self.pt1),
            (self.pt2),
            (self.pt2),
            (self.pt3),
            (self.pt3),
            (self.pt0),
        )

        # batch = batch_for_shader(self.UNIFORM_SHADER_2D, "TRIS", {"pos": vertices}, indices=indices)
        fillMode = "LINES"  # "TRIS"
        batch = batch_for_shader(self.UNIFORM_SHADER_2D, fillMode, {"pos": verticesLine})
        # batch = batch_for_shader(shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR'), fillMode, {"pos": vertices}, indices=indices)

        self.UNIFORM_SHADER_2D.bind()
        self.UNIFORM_SHADER_2D.uniform_float("color", self.color)
        batch.draw(self.UNIFORM_SHADER_2D)

    # def bbox(self):
    #     return (-self.sx + self.x, -self.sy + self.y), (self.sx + self.x, self.sy + self.y)
