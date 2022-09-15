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
import blf

from .class_Object2D import Object2D

from .gpu_2d import draw_tripod, draw_bBox

from shotmanager.utils import utils_editors_dopesheet
from shotmanager.utils.utils import color_to_sRGB, set_color_alpha, alpha_to_linear, color_is_dark
from shotmanager.utils.utils_editors_dopesheet import getRulerHeight, getLaneHeight, getPrefsUIScale

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class Text2D(Object2D):
    def __init__(
        self,
        *,
        posXIsInRegionCS=True,
        posX=0,
        posYIsInRegionCS=True,
        posY=0,
        alignment="BOTTOM_LEFT",
        alignmentToRegion="BOTTOM_LEFT",
        displayOverRuler=False,
        text="Text2D",
        fontSize=12,
        parent=None,
    ):
        Object2D.__init__(
            self,
            posXIsInRegionCS=posXIsInRegionCS,
            posX=posX,
            posYIsInRegionCS=posYIsInRegionCS,
            posY=posY,
            widthIsInRegionCS=True,
            width=10,
            heightIsInRegionCS=True,
            height=20,
            alignment=alignment,
            alignmentToRegion=alignmentToRegion,
            parent=parent,
        )

        self.text = text
        self.fontSize = fontSize
        self.opacity = 1.0
        self.bold = False

        self.color = (0.9, 0.9, 0.0, 0.9)

        self.hasShadow = False
        # if not explicitely set then an automatic color is used
        self.colorShadow = None

        self.displayOverRuler = displayOverRuler

    #################################################################

    #################################################################

    def _getFontSizeForGlDraw(self):
        return round(self.fontSize * getPrefsUIScale())

    def _drawText(self, shader=None, region=None, pX=10, pY=10):
        # bgl.glDisable(bgl.GL_BLEND)
        blf.enable(0, blf.CLIPPING)
        # blf.clipping(0, *self._clamped_bBox)
        margin = 20
        blf.clipping(
            0,
            0 - margin,
            0 - margin,
            bpy.context.region.width + margin,
            bpy.context.region.height - getRulerHeight() - 0.8 * getLaneHeight(),
        )

        if self.hasShadow:
            blf.enable(0, blf.SHADOW)
            # The blur level, can be 3, 5 or 0
            blurLevel = 3
            if self.colorShadow:
                colShadow = self.colorShadow
            else:
                colShadow = (1, 1, 1, 0.5) if color_is_dark(self.color, 0.5) else (0, 0, 0, 0.5)

            blf.shadow(0, blurLevel, *colShadow)
            # blf.shadow_offset(0, 1, -1)

        blf.color(0, *self.color)
        blf.size(0, self._getFontSizeForGlDraw(), 72)
        blf.position(0, pX, pY, 0)

        blf.draw(0, self.text)
        if self.bold:
            #     # blf.position(0, pX + 1, pY, 0)
            blf.draw(0, self.text)

        blf.disable(0, blf.CLIPPING)
        blf.disable(0, blf.SHADOW)

    def draw(self, shader=None, region=None, preDrawOnly=False):
        # if not self.isVisible:
        #     return

        # aligment to region ###############
        alignmentsR = self.alignmentToRegion.split("_")
        alignmentR_x = alignmentsR[1]
        alignmentR_y = alignmentsR[0]

        # aligment to pivot ###############
        alignments = self.alignment.split("_")
        alignment_x = alignments[1]
        alignment_y = alignments[0]

        # position ###############
        parentPos = (0, 0)
        if self.inheritPosFromParent and self.parent:
            parentPos = self.parent.getPositionInRegion()

        if self.posXIsInRegionCS:
            # in this case self.posX is in pixels, with origin at the LEFT, X axis rightward
            posX = self.posX + parentPos[0]
        else:
            # in this case self.posX is in frames, with origin at the LEFT, X axis still rightward
            posX = region.view2d.view_to_region(self.posX, 0, clip=False)[0]

        if self.posYIsInRegionCS:
            # in this case self.posY is in pixels, with origin at the BOTTOM, Y axis upward
            posY = self.posY + parentPos[1]
        else:
            # in this case self.posY is in lanes, with origin at the TOP, Y axis DOWNWARD
            # the Y axis then has to be changed
            posY_inValues = -1.0 * utils_editors_dopesheet.getLaneToValue(self.posY)
            posY = region.view2d.view_to_region(0, -posY_inValues, clip=False)[1]

        # scale ##################
        # if self.widthIsInRegionCS:
        #     width = self.width
        # else:
        #     if self.posXIsInRegionCS:
        #         posX_inView = region.view2d.region_to_view(self.posX, 0)[0]
        #         posX_inRegion = self.posX
        #     else:
        #         posX_inView = self.posX
        #         posX_inRegion = region.view2d.view_to_region(self.posX, 0, clip=False)[0]

        #     width = region.view2d.view_to_region(posX_inView + self.width, 0, clip=False)[0] - posX_inRegion
        blf.size(0, self._getFontSizeForGlDraw(), 72)
        width = blf.dimensions(0, self.text)[0]
        height = blf.dimensions(0, self.text)[1]

        # if self.heightIsInRegionCS:
        #     height = self.height
        # else:
        #     # # height is in number of lanes
        #     # height_delta_Lane0 = 0
        #     # if self.posYIsInRegionCS:
        #     #     # this case may be buggy? Is it used?
        #     #     # not easy to fix since there is no vertical zoom on dopesheets
        #     #     posY_inView = region.view2d.region_to_view(0, self.posY)[1]
        #     #     posY_inRegion = self.posY
        #     # else:
        #     #     # convert from lanes to y values
        #     #     posY_inValues = -1.0 * utils_editors_dopesheet.getLaneToValue(self.posY)
        #     #     posY_inView = posY_inValues
        #     #     posY_inRegion = region.view2d.view_to_region(0, posY_inValues, clip=False)[1]

        #     #     # if posY is 0 then we have to compensate the height of the time ruler
        #     #     if self.posY < 1:
        #     #         height_delta_Lane0 = (
        #     #             utils_editors_dopesheet.getRulerHeight() - utils_editors_dopesheet.getLaneHeight()
        #     #         )

        #     # height_inValues = self.height * utils_editors_dopesheet.getLaneHeight() + height_delta_Lane0
        #     # height = region.view2d.view_to_region(0, posY_inView + height_inValues, clip=False)[1] - posY_inRegion

        #     # better way to compute the component height:
        #     # This way prevent rounding errors and ensure that there is not holes nor overlaps between components on
        #     # successive lanes
        #     numLanes = self.height
        #     if alignment_y in ("MID", "TOP"):
        #         height = utils_editors_dopesheet.getLaneToValue(
        #             self.posY - numLanes + 1
        #         ) - utils_editors_dopesheet.getLaneToValue(self.posY + 1)
        #     else:
        #         height = utils_editors_dopesheet.getLaneToValue(
        #             self.posY - numLanes
        #         ) - utils_editors_dopesheet.getLaneToValue(self.posY)

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
        elif "MID" == alignment_y:
            posY = posY - height / 2

        if self.avoidClamp_leftSide and self.parent:
            posX = self.recomputePosToAvoidClamping(posX, posY, width, height)[0]

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

        self._bBox = bBox
        # if clamped then the quad is not drawn
        if clamped_transformed_vertices is None:
            self.isFullyClamped = True
            self._clamped_bBox = bBox
            return

        self.isFullyClamped = False
        clamped_bBox = [
            clamped_transformed_vertices[0][0],
            clamped_transformed_vertices[0][1],
            clamped_transformed_vertices[2][0],
            clamped_transformed_vertices[2][1],
        ]
        self._clamped_bBox = clamped_bBox

        ########################################
        # effective draw
        ########################################

        if not self.isVisible:
            return

        if shader is None:
            UNIFORM_SHADER_2D.bind()
            color = set_color_alpha(self.color, alpha_to_linear(self.color[3] * self.opacity))
            UNIFORM_SHADER_2D.uniform_float("color", color_to_sRGB(color))
            shader = UNIFORM_SHADER_2D

        if False:
            #  draw_bBox(self._bBox)
            draw_bBox(self._clamped_bBox)

        if not preDrawOnly:
            self._drawText(shader, region, posX, posY)

        # draw tripod
        if False:
            draw_tripod(pivot_posX, pivot_posY, 20)

        # get sorted children and draw them. getChildren is inherited from Object2D
        sortedChildren = self.getChildren(sortedByIncreasingZ=True)
        for child in sortedChildren:
            child.draw(None, region)
