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

from pathlib import Path

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

from shotmanager.utils.utils import getDataImageFromPath
from shotmanager.utils.utils import color_to_sRGB, set_color_alpha, alpha_to_linear

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class Mesh2D:
    def __init__(self, *, vertices=None, indices=None, texcoords=None):
        self._vertices = list() if vertices is None else vertices
        self._indices = list() if indices is None else indices
        self._indicesLine = list()

        self._texcoords = [(0, 0), (0, 1), (1, 1), (1, 0)] if texcoords is None else texcoords

        self.opacity = 1.0

        # fill #########
        self.hasFill = True
        self.color = (0.9, 0.9, 0.0, 0.5)

        # line #########
        self.hasLine = False
        self.colorLine = (0.9, 0.9, 0.9, 1.0)
        self.lineThickness = 1

        # texture ######
        self.hasTexture = False

        # Image data, gat be obtained from utils.getDataImageFromPath()
        self._image = None

        # offset in pixels of the edge line, in this order:
        #   left, top, right, bottom
        self.lineOffsetPerEdge = [0, -1, -1, 0]

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    def setImageFromFile(self, filename):
        imgPath = Path(filename).parent
        imgName = Path(filename).name
        self.image = getDataImageFromPath(imgPath, imgName)

    #################################################################

    # drawing ##########

    #################################################################

    def _getFillShader(self):
        shader = UNIFORM_SHADER_2D
        shader.bind()
        color = set_color_alpha(self.color, alpha_to_linear(self.color[3] * self.opacity))
        shader.uniform_float("color", color_to_sRGB(color))
        return shader

    def _getLineShader(self):
        shader = UNIFORM_SHADER_2D
        shader.bind()
        color = set_color_alpha(self.colorLine, alpha_to_linear(self.colorLine[3] * self.opacity))
        shader.uniform_float("color", color_to_sRGB(color))
        return shader

    def _getTextureShader(self):
        shader = gpu.shader.from_builtin("2D_IMAGE")
        shader.bind()
        # color = set_color_alpha(self.colorLine, alpha_to_linear(self.colorLine[3] * self.opacity))
        # shader.uniform_float("color", color_to_sRGB(color))
        return shader

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

            # attempt to z-sort but not compatible with 2D_IMAGE for the texture
            # if 0 != self.z:
            #     shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
            #     transformed_vertices = [(v[0], v[1], self.z) for v in transformed_vertices]

            batch = batch_for_shader(shader, draw_types, {"pos": transformed_vertices}, indices=v_indices)
            batch.draw(shader)

        elif "LINES" == draw_types:
            # draw lines and points fo the caps
            if vertex_indices is None:
                v_indices = self._indicesLine

            # fix line offset to stay inside the quad
            vertices_inner = []
            vertices_inner.append(
                (
                    transformed_vertices[0][0] + self.lineOffsetPerEdge[0],
                    transformed_vertices[0][1] + self.lineOffsetPerEdge[3],
                )
            )
            vertices_inner.append(
                (
                    transformed_vertices[1][0] + self.lineOffsetPerEdge[0],
                    transformed_vertices[1][1] + self.lineOffsetPerEdge[1],
                )
            )
            vertices_inner.append(
                (
                    transformed_vertices[2][0] + self.lineOffsetPerEdge[2],
                    transformed_vertices[2][1] + self.lineOffsetPerEdge[1],
                )
            )
            vertices_inner.append(
                (
                    transformed_vertices[3][0] + self.lineOffsetPerEdge[2],
                    transformed_vertices[3][1] + self.lineOffsetPerEdge[3],
                )
            )

            batch = batch_for_shader(shader, draw_types, {"pos": vertices_inner}, indices=v_indices)
            bgl.glLineWidth(self.lineThickness)
            batch.draw(shader)
            if cap_lines or True:
                batch = batch_for_shader(shader, "POINTS", {"pos": vertices_inner})
                bgl.glPointSize(self.lineThickness)
                batch.draw(shader)

        elif "POINTS" == draw_types:
            # wkip here draw points for rounded line caps
            batch = batch_for_shader(shader, "POINTS", {"pos": transformed_vertices})
            bgl.glPointSize(self.lineThickness)
            batch.draw(shader)

        elif "TRI_FAN" == draw_types:
            # https://docs.blender.org/api/current/bpy.types.Image.html?highlight=gl_load#bpy.types.Image.gl_load
            if self._image.gl_load():
                _logger.error_ext(f"Error in loading image texture: {self._image}")
                raise Exception()

            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._image.bindcode)

            # setting the texture filtering mode:
            # https://blenderartists.org/t/bind-custom-uniform-values-to-a-2d-filter-using-bgl-wrapper/645232/8
            # https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexParameter.xhtml
            # https://docs.blender.org/api/current/bgl.html?highlight=gltexparameteri

            # GL_NEAREST GL_LINEAR
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)

            textureShader = gpu.shader.from_builtin("2D_IMAGE")
            batch = batch_for_shader(
                textureShader,
                "TRI_FAN",
                {
                    "pos": transformed_vertices,
                    "texCoord": (self._texcoords),
                },
            )
            textureShader.bind()
            textureShader.uniform_int("image", 0)
            batch.draw(textureShader)

    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False, preDrawOnly=False):
        transformed_vertices = self._vertices

        # deprecated - use clampToRegion
        from shotmanager.utils.utils import clamp

        def _clamp_to_region(x, y, region):
            l_x, l_y = region.view2d.region_to_view(0, 0)
            h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
            return clamp(x, l_x, h_x), clamp(y, l_y, h_y)

        if region:
            transformed_vertices = [
                region.view2d.view_to_region(*_clamp_to_region(x, y, region), clip=True)
                for x, y in transformed_vertices
            ]

        if self.hasFill:
            fillShader = shader
            if not fillShader:
                fillShader = self._getFillShader()
            draw_types = "TRIS"
            if not preDrawOnly:
                self._drawMesh(fillShader, region, draw_types, cap_lines, transformed_vertices)

        if self.hasLine:
            lineShader = self._getLineShader()
            draw_types = "LINES"
            if not preDrawOnly:
                self._drawMesh(lineShader, region, draw_types, cap_lines, transformed_vertices, self._indicesLine)

        if self.hasTexture:
            textureShader = self._getTextureShader()
            draw_types = "TRI_FAN"
            if not preDrawOnly:
                self._drawMesh(textureShader, region, draw_types, cap_lines, transformed_vertices)

    def rebuild_rectangle_mesh(self, posX, posY, width, height):
        """All those values are in pixels, in region CS"""

        vBotLeft = (min(posX, posX + width), min(posY, posY + height))
        vTopLeft = (min(posX, posX + width), max(posY, posY + height))
        vTopRight = (max(posX, posX + width), max(posY, posY + height))
        vBotRight = (max(posX, posX + width), min(posY, posY + height))
        # transformed_vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)

        self._vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)
        self._indices = ((0, 3, 1), (1, 3, 2))

        # edges are in this order: left, top, right, bottom
        self._indicesLine = ((0, 1), (1, 2), (2, 3), (3, 0))


def build_rectangle_mesh(position, width, height, isLine=False):

    mesh = Mesh2D()
    mesh.rebuild_rectangle_mesh(position[0], position[1], width, height)
    if isLine:
        mesh.hasFill = False
        mesh.hasLine = True

    return mesh
