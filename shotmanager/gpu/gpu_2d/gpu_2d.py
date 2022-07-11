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

from shotmanager.utils.utils import color_to_sRGB

# from shotmanager.config import config
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


def draw_bBox(bBox, thickness=1, color=(1.0, 1.0, 1.0, 1.0), drawDiagonal=True):
    lineThickness = thickness

    vBotLeft = (bBox[0], bBox[1])
    vTopLeft = (bBox[0], bBox[3])
    vTopRight = (bBox[2], bBox[3])
    vBotRight = (bBox[2], bBox[1])

    vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)
    indices = [(0, 3), (3, 2), (2, 1), (1, 0)]
    if drawDiagonal:
        indices.append((1, 3))

    bgl.glEnable(bgl.GL_BLEND)

    UNIFORM_SHADER_2D.bind()
    UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
    shader = UNIFORM_SHADER_2D

    batch = batch_for_shader(shader, "LINES", {"pos": vertices}, indices=indices)
    bgl.glLineWidth(lineThickness)
    batch.draw(shader)


# def loadImageAsTexture(img):
#     """Args:
#     img: a data Image type, got from utils.getDataImageFromPath for instance"""
#     texture = None
#     if img:
#         if img.gl_load():
#             _logger.error_ext(f"Error in loading image as a texture: {img}")
#             # raise Exception()
#             img = None
#     return texture
