# GPLv3 License
#
# Copyright (C) 2021 Ubisoft
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
Functions specific to Dopesheet editors such as the dopesheet, the timeline...

Several things to know for Dopesheets:

    - the openGL origin is at the BOTTOM LEFT corner of the region, pointing UPWARD
    - when converting from region to view we get a result in pixels but with an origin
      that is now at the TOP LEFT corner and moving up if the view is scrolled down. The
      Y axis is still pointing UPWARD, meaning the Y position of the mouse is always negative!
    - when converting in lanes, we start the count at lane 0, its origin at the TOP LEFT corner
      and counting negatively (ie the first lane has index -1, the second lane below has index -2...) 

"""

import math

import bpy

from shotmanager.utils.utils import clamp
from shotmanager.config import config


def getRegionFrameRange(context, targetArea, inViewUnits=True):
    """Return the region bottom left and top right of the target dopesheet area,
    with the x in frames and the y in something"""

    c = context.copy()
    for i, area in enumerate(context.screen.areas):
        if area != targetArea:
            continue
        region = area.regions[-1]
        # print("SCREEN:", context.screen.name, "[", i, "]")
        c["space_data"] = area.spaces.active
        c["area"] = area
        c["region"] = region

        # region size
        h = region.height  # screen
        w = region.width  #
        bl = region.view2d.region_to_view(0, 0)
        tr = region.view2d.region_to_view(w, h)
        # print(f"region bottom left: {(bl[0]):03.2f} fr, {(bl[1]):03.2f}")
        # print(f"region top right: {(tr[0]):03.2f} fr, {(tr[1]):03.2f}")

        # range = Vector(tr) - Vector(bl)

        # return (Vector(bl), Vector(tr))
        if inViewUnits:
            return (bl[0], bl[1], tr[0], tr[1])
        else:
            return (0.0, 0.0, w, h)

    return None


def getPrefsUIScale():
    # ui_scale has a very weird behavior, especially between 0.79 and 0.8. We try to compensate it as
    # much as possible
    factor = 0
    if bpy.context.preferences.view.ui_scale >= 1.1:
        factor = 0.2
    if bpy.context.preferences.view.ui_scale >= 1.0:
        factor = 0.0
    elif bpy.context.preferences.view.ui_scale >= 0.89:
        factor = 1.6
    elif bpy.context.preferences.view.ui_scale >= 0.79:
        factor = 0.0
    elif bpy.context.preferences.view.ui_scale >= 0.69:
        factor = 0.1
    else:
        factor = 0.15

    # return bpy.context.preferences.view.ui_scale + abs(bpy.context.preferences.view.ui_scale - 1) * factor
    return bpy.context.preferences.view.ui_scale


def getRulerHeight(firstLaneIndex=0):
    """Return the height in pixels of the time ruler of a dopesheet"""
    prefs = config.getAddonPrefs()
    RULER_HEIGHT = 23
    # RULER_HEIGHT = 28  # on laptop at display 125%
    rulerHeight = (
        RULER_HEIGHT * prefs.shtStack_screen_display_factor
    ) * getPrefsUIScale() + firstLaneIndex * getLaneHeight()
    # rulerHeight = rulerHeight * getPrefsUIScale()
    return rulerHeight


def getLaneHeight():
    """Return the height of a lane in pixels"""
    prefs = config.getAddonPrefs()
    LANE_HEIGHT = 18
    # LANE_HEIGHT = 22.5  # on laptop at display 125%
    laneHeight = LANE_HEIGHT * prefs.shtStack_screen_display_factor
    return laneHeight * getPrefsUIScale()


# same as pixel to lane
def getLaneIndexUnderLocationY(region, rpY):
    """Get the lane index under the position rpY (in pixels, already in the specified region)"""

    # pY - region.height
    # vrpY is negative !!
    vrpY = region.view2d.region_to_view(0, rpY)[1]
    # vrpY = min(rpY, region.height)

    # height range varies according to the vertical pan in the view
    rHeightRangeMinInView = region.view2d.region_to_view(0, 0)[1]
    rHeightRangeMaxInView = region.view2d.region_to_view(0, region.height)[1]

    # if 0 < vrpY or vrpY < -abs(rHeightInView):
    if rHeightRangeMaxInView < vrpY or vrpY < rHeightRangeMinInView:
        # if vrpY < 0 or vrpY > region.height:
        return -1

    # vrpY = min(rpY, region.height)
    # inv_vrpY = region.height - vrpY

    if vrpY < -1 * getRulerHeight():
        vrpY_inLanes = (-vrpY - getRulerHeight()) // getLaneHeight() + 1
        return vrpY_inLanes
    else:
        return 0


def getDisplayedLanesRange(region):
    """Return a tuple made of 3 floats, the first displayed lane index, the last displayed lane index and
    the number of FULLY displayed lanes (which will usually exclude the first and last lanes since they are
    only partly displayed)
    Note: the ruler is always excluded since it is not a lane"""

    # keep in mind y view is inverted:
    yValMin = abs(region.view2d.region_to_view(0, region.height - 1)[1])
    yValMax = abs(region.view2d.region_to_view(0, 0)[1])

    yLaneMin = yValMin / getLaneHeight() + 1
    yLaneMax = (yValMax - getRulerHeight()) / getLaneHeight() + 1

    numLanes = math.floor(yLaneMax) - math.ceil(yLaneMin)

    return (yLaneMin, yLaneMax, numLanes)


def getLaneToValue(laneVal):
    """Convert a lane (float) to a view value"""

    if laneVal < 0:
        vrpY_inValues = 0
    # elif 0 == laneVal:
    #     vrpY_inValues = -1.0 * laneVal * getRulerHeight()
    elif laneVal < 1:
        vrpY_inValues = -1.0 * laneVal * getRulerHeight()
    else:
        vrpY_inValues = -1.0 * laneVal * getLaneHeight() - getRulerHeight()

    return int(vrpY_inValues)


def clampToRegion(x, y, region):
    l_x, l_y = region.view2d.region_to_view(0, 0)
    h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)


def intersectionWithRegion(quadVertices, region, excludeRuler=False):
    """Return an array of vertices with x and y inside the region, None if the mesh defined by the
    vertices is fully out of the region
    Args:
        quadVertices:   array of peers (x, y) already in the region CS and defining a quad as follow:
        quadVertices = [vBotLeft, vTopLeft, vTopRight, vBotRight]
    """

    rOriginX = 0
    rOriginY = 0
    rWidth = region.width
    rHeight = region.height
    if excludeRuler:
        rHeight = rHeight - getRulerHeight()

    if (
        quadVertices[2][0] <= 0
        or quadVertices[0][0] >= rWidth
        or quadVertices[2][1] <= 0
        or quadVertices[0][1] >= rHeight
    ):
        return None

    # posX and posY are the origin of the mesh, where the pivot is located
    # all those values are in pixels, in region CS
    # so far height and width can be negative
    vBotLeft = (max(rOriginX, quadVertices[0][0]), max(rOriginY, quadVertices[0][1]))
    vTopLeft = (max(rOriginX, quadVertices[1][0]), min(rHeight, quadVertices[2][1]))
    vTopRight = (min(rWidth, quadVertices[2][0]), min(rHeight, quadVertices[2][1]))
    vBotRight = (min(rWidth, quadVertices[3][0]), max(rOriginY, quadVertices[3][1]))
    clamped_vertices = (vBotLeft, vTopLeft, vTopRight, vBotRight)

    return clamped_vertices
