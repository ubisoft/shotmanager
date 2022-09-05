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
Functions specific to 3D View editors
"""

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)



def displayOvelayInAllViewports(context, newState):
    """Turn viewports overlay on or off"""
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.overlay.show_overlays = newState
                    break


def getViewportOverlayState(targetArea):
    """Return the state of the overlay display for the specified viewport.
    Get the target area with props.getValidTargetViewport()"""
    # see aslo spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    # and props.getValidTargetViewport

    if targetArea is None:
        _logger.warning_ext("getViewportOverlayState: Specified target area is None getViewportOverlayState: Specified target area is None")
        return False

    if "VIEW_3D" != targetArea.type:
        _logger.warning_ext("getViewportOverlayState: Specified target area is not a 3D View")
        return False

    for space in targetArea.spaces:
        if space.type == "VIEW_3D":
            return space.overlay.show_overlays


def setViewportOverlayState(targetArea, newState):
    """Turn overlay on or off for the specified viewport.
    If targetArea is None then a warning message is displayed in the log.
    Get the target area with props.getValidTargetViewport()"""
    # see aslo spaceDataViewport = props.getValidTargetViewportSpaceData(context)
    # and props.getValidTargetViewport

    if targetArea is None:
        _logger.warning_ext("setViewportOverlayState: Specified target area is None")
        return

    if "VIEW_3D" != targetArea.type:
        _logger.warning_ext("setViewportOverlayState: Specified target area is not a 3D View")
        return

    for space in targetArea.spaces:
        if space.type == "VIEW_3D":
            space.overlay.show_overlays = newState
            break

    #     try:
    #         bpy.context.space_data.overlay.show_overlays = userRenderSettings["show_overlays"]
    #     except Exception as e:
    #         _logger.error_ext(f"Cannot restore Overlay mode: {e}")
