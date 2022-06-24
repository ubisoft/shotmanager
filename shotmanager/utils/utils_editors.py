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
