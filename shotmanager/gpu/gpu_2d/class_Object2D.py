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

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")


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


        heightIsInRegionCS: If True the height is in the View coordinate system of the region, height is then in pixels
                            Height of the object will NOT change even if the region scale on y is changed (eg: not dependent on lines scale)

                            If False the height is in the Region coordinate system, in number of lines.
                            Height of the object will change if the region scale on y is changed (eg: surface that has to mach a line height)

                            Note that the actual height of a line in pixels depends on the global UI scale factor.
                            Use heightIsInRegionCS = True to display a static quad for example
                            Use heightIsInRegionCS = False to display a clip that has to match a line height

        height:             The height of the object. Its unit is in pixels if heightIsInRegionCS is True, in lines otherwise

        alignment:          aligment of the object to its origin. It can be seen as being the placement of the pivot relatively
                            to the component bounding box.
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

        alignmentToRegion:  aligment of the object to the REGION in which it belongs to (and not to its parent component).
                            *** When this component has to be displayed in its parent component coordinate system then alignmentToRegion
                            must be ignored and let to default ***
                            can be TOP_LEFT, TOP_MID, TOP_RIGHT, MID_RIGHT, BOTTOM_RIGHT, BOTTOM_MID, BOTTOM_LEFT (default), MID_LEFT, MID_MID

    """

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
        parent=None,
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

        self.isVisible = True

        # children ########################
        self._children = list()
        self.parent = parent
        if self.parent:
            self.parent._children.append(self)
        self.inheritPosFromParent = True

        # children may be reorodered when their z order
        # z is a float that can be negative
        # the higher the value, the latest it is drawn (= will be drawn over the other, to the front)
        self.zOrder = 0.0

        # boundary box and clamping ########
        ####################################
        # NOTE: bBox is defined by [xMin, YMin, xMax, yMax], in pixels in region CS (so bottom left, compatible with mouse position)
        # In the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
        # Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)

        self._bBox = [0, 0, 1, 1]
        if self.widthIsInRegionCS:
            self._bBox[2] = self.width
        if self.heightIsInRegionCS:
            self._bBox[2] = self.height
        self._clamped_bBox = self._bBox.copy()
        self.isFullyClamped = False

        # if this object  has a parent then when enabled it can be offset in its parent bounding box to keep being displayed
        # in the region without being clamped
        self.avoidClamp_leftSide = False
        self.avoidClamp_leftSideOffset = 10
        self.avoidClamp_spacePreservedOnRight = 10

        # pivot ##################
        self._pivot_posX = 0
        self._pivot_posY = 0

    def getPositionInRegion(self):
        """Return the position of the object in pixels, in the region CS"""
        return (self._pivot_posX, self._pivot_posY)

    def getWidthInRegion(self, clamped=True):
        """Return the width of the object in pixels, in the region CS"""
        # NOTE: in the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
        # Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)
        if clamped:
            return 0 if self.isFullyClamped else self._clamped_bBox[2] - self._clamped_bBox[0]
        else:
            return self._bBox[2] - self._bBox[0]

    def getHeightInRegion(self, clamped=True):
        """Return the height of the object in pixels, in the region CS"""
        # NOTE: in the bounding boxes, the max values, corresponding to pixel coordinates, are NOT included in the component
        # Consequently the width of the rectangle, in pixels belonging to it, is given by xMax - xMin (and NOT xMax - xMin + 1 !)
        if clamped:
            return o if self.isFullyClamped else self._clamped_bBox[3] - self._clamped_bBox[1]
        else:
            return self._bBox[3] - self._bBox[1]

    def recomputePosToAvoidClamping(self, posX, posY, width, height):
        """Used to influence posX and posY (not self.posX not self.posY!!) after their computation to reposition
        this object inside the region without it being clamped"""
        # TODO: complete the code with top, right, bottom

        # NOTE: This works well because the component is aligned to the left. Haven't tried with aligned to right...
        newPosX = posX
        leftOffset = self.avoidClamp_leftSideOffset
        if self.parent._bBox[0] < self.parent._clamped_bBox[0]:
            if self.posX - leftOffset < self.parent._clamped_bBox[0] - self.parent._bBox[0]:
                parentClampedWidth = self.parent.getWidthInRegion()
                if width + leftOffset + self.avoidClamp_spacePreservedOnRight < parentClampedWidth:
                    # self.inheritPosFromParent = False
                    newPosX = leftOffset
                else:
                    newPosX = leftOffset - (
                        width + leftOffset + self.avoidClamp_spacePreservedOnRight - parentClampedWidth
                    )

        return [newPosX, posY]

    def getChildren(self, sortedByIncreasingZ=False, reverse=False):
        """Return a copy of the children list"""
        if sortedByIncreasingZ:
            children = sorted(self._children, key=lambda c: c.zOrder, reverse=reverse)
        else:
            children = reversed(self._children) if reverse else [c for c in self._children]
        return children
