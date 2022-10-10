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

from .class_Object2D import Object2D
from .class_Mesh2D import Mesh2D

from .gpu_2d import draw_tripod, draw_bBox

from shotmanager.utils import utils_editors_dopesheet
from shotmanager.utils.utils import color_to_sRGB, set_color_alpha, alpha_to_linear

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


class QuadObject(Object2D, Mesh2D):
    def __init__(
        self,
        *,
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
        parent=None,
    ):
        Object2D.__init__(
            self,
            posXIsInRegionCS=posXIsInRegionCS,
            posX=posX,
            posYIsInRegionCS=posYIsInRegionCS,
            posY=posY,
            widthIsInRegionCS=widthIsInRegionCS,
            width=width,
            heightIsInRegionCS=heightIsInRegionCS,
            height=height,
            alignment=alignment,
            alignmentToRegion=alignmentToRegion,
            parent=parent,
        )
        Mesh2D.__init__(self)

        # # attributes from MESH2D #########
        # self.color = (0.9, 0.9, 0.0, 0.9)
        # self.hasFill = True
        # # contour
        # self.hasLine = False
        # self.colorLine = (0.9, 0.9, 0.9, 1.0)

        self.displayOverRuler = displayOverRuler

        self.rebuild_rectangle_mesh(0, 0, 1, 1)

    # # override Object2D
    # def getPositionInRegion(self):
    #     return (0, 0)

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

    def updateTexCoords(self):
        # self._texcoords = [(0, 0), (0, 1), (1, 1), (1, 0)]
        texCoords = []

        width = self.getWidthInRegion(clamped=False)
        height = self.getHeightInRegion(clamped=False)

        # bottom left
        blX = (self._clamped_bBox[0] - self._bBox[0]) / width
        blY = (self._clamped_bBox[1] - self._bBox[1]) / height
        texCoords.append((blX, blY))
        # top left
        tlX = blX
        tlY = 1.0 - (self._bBox[3] - self._clamped_bBox[3]) / height
        texCoords.append((tlX, tlY))
        # top right
        trX = 1.0 - (self._bBox[2] - self._clamped_bBox[2]) / width
        trY = tlY
        texCoords.append((trX, trY))
        # bottom right
        brX = trX
        brY = blY
        texCoords.append((brX, brY))

        self._texcoords = texCoords

    #################################################################

    # drawing ##########

    #################################################################

    # override Mesh2D
    def draw(self, shader=None, region=None, draw_types="TRIS", cap_lines=False, preDrawOnly=False):
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
                if 0 == self.posY - numLanes:
                    height = utils_editors_dopesheet.getLaneHeight()
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

        self._pivot_posX = posX
        self._pivot_posY = posY

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

        # rebuilt the texture coordinates
        self.updateTexCoords()

        ########################################
        # effective draw
        ########################################

        if not self.isVisible:
            return

        if self.hasFill:
            fillShader = shader
            # fillShader = None
            if not fillShader:
                fillShader = self._getFillShader()
            draw_types = "TRIS"
            if not preDrawOnly:
                self._drawMesh(fillShader, region, draw_types, cap_lines, clamped_transformed_vertices)

        if self.hasLine:
            edgeIndices = self.getEdgeIndices(bBox, clamped_bBox)
            lineShader = self._getLineShader()
            draw_types = "LINES"
            if not preDrawOnly:
                self._drawMesh(lineShader, region, draw_types, cap_lines, clamped_transformed_vertices, edgeIndices)

        if self.hasTexture:
            textureShader = self._getTextureShader()
            draw_types = "TRI_FAN"
            if not preDrawOnly:
                self._drawMesh(textureShader, region, draw_types, cap_lines, clamped_transformed_vertices)

        if False:
            draw_bBox(self._bBox, color=(0, 1, 1, 1))
            draw_bBox(self._clamped_bBox)

        # draw tripod
        if False:
            draw_tripod(self._pivot_posX, self._pivot_posY, 20)

        # get sorted children and draw them. getChildren is inherited from Object2D
        sortedChildren = self.getChildren(sortedByIncreasingZ=True)
        for child in sortedChildren:
            child.draw(None, region)
