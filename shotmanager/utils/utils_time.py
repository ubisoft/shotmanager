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
Time utils functions
"""

import bpy


def zoom_dopesheet_view_to_range(context, start, end, changeTime=True):
    """Change the zoom of the time range in the Timeline and Dopesheet editors to frame the 
    specified range.
    A given amount of frames is set before and after the range. This is not a percentage.
    """
    # number of frames before and after the specified range
    num_frames_around = 10

    ctx = context.copy()
    for area in context.screen.areas:
        if area.type == "DOPESHEET_EDITOR":
            ctx["area"] = area
            for region in area.regions:
                if region.type == "WINDOW":
                    ctx["region"] = region
                    bpy.ops.view2d.reset(ctx)
                    if not changeTime:
                        prevTime = context.scene.frame_current
                    context.scene.frame_current = start + (end - start) // 2
                    bpy.ops.action.view_frame(ctx)
                    bpy.ops.view2d.zoom(ctx, deltax=(region.width // 2 - (end - start) // 2) - num_frames_around)
                    if not changeTime:
                        context.scene.frame_current = prevTime

