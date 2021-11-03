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

import bpy


#
# Blender windows system utils
#
def get_region_at_xy(context, x, y, area_type="VIEW_3D"):
    """
    Does not support quadview right now

    :param context:
    :param x:
    :param y:
    :return: the region and the area containing this region
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
