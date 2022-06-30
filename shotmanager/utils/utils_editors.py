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
Functions specific to editors such as 3D Viewport, Dopesheet...
"""

import bpy

from shotmanager.utils.utils import clamp


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


def getRulerHeight():
    """Return the height in pixels of the time ruler of a dopesheet"""
    RULER_HEIGHT = 28
    return RULER_HEIGHT * getPrefsUIScale()


def getLaneHeight():
    """Return the height of a lane in pixels"""
    LANE_HEIGHT = 18.5
    LANE_HEIGHT = 22.5
    return LANE_HEIGHT * getPrefsUIScale()


# same as pixel to lane
def getLaneIndexUnderLocationY(region, rpY):
    """Get the lane index under the position rpY (in pixels, already in the specified region)"""

    # pY - region.height
    vrpY = -1.0 * region.view2d.region_to_view(0, rpY)[1]
    # vrpY = min(rpY, region.height)

    if vrpY < 0 or vrpY > region.height:
        return -1

    # vrpY = min(rpY, region.height)
    # inv_vrpY = region.height - vrpY

    if vrpY < getRulerHeight():
        return 0
    else:
        vrpY_inLanes = (vrpY - getRulerHeight()) // getLaneHeight() + 1
        return vrpY_inLanes


def getLaneToValue(laneVal):
    """Convert a lane (float) to a view value"""

    if laneVal < 0:
        return 0

    if laneVal <= 1:
        vrpY_inValues = laneVal * getRulerHeight()
        return vrpY_inValues
    else:
        vrpY_inValues = (laneVal - 1) * getLaneHeight() + getRulerHeight()
        return vrpY_inValues


def clampToRegion(x, y, region):
    l_x, l_y = region.view2d.region_to_view(0, 0)
    h_x, h_y = region.view2d.region_to_view(region.width - 1, region.height - 1)
    return clamp(x, l_x, h_x), clamp(y, l_y, h_y)
