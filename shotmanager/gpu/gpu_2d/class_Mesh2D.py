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

import gpu
import bgl
from gpu_extras.batch import batch_for_shader

from shotmanager.utils.utils_ogl import clamp_to_region
from shotmanager.utils.utils import color_to_sRGB

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


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

    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False):
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
