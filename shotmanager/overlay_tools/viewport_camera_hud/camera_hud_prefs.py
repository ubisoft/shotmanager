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
Settings panel for the camera HUD tool
"""

from shotmanager.utils.utils_ui import propertyColumn

from shotmanager.config import config


def draw_settings(context, layout):
    """Used in Shot Manager Feature Toggles panel"""
    props = config.getAddonProps(context.scene)
    prefs = config.getAddonPrefs()

    propCol = propertyColumn(layout)

    propCol.prop(props, "camera_hud_display_in_viewports", text="Display Shot name in 3D Viewport")
    propCol.prop(props, "camera_hud_display_in_pov", text="Display HUD in 3D Viewport")
    propCol.prop(prefs, "cameraHUD_shotNameSize", text="Size of the shot names")
