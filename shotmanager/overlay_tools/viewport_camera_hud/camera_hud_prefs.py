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


def draw_settings(context, layout):
    """Used in Shot Manager Feature Toggles panel"""
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences

    leftCol = layout.column()

    # empty spacer column
    row = leftCol.row()
    col = row.column()
    col.scale_x = 0.25
    col.label(text=" ")
    col = row.column(align=True)

    col.prop(props, "camera_hud_display_in_viewports", text="Display Shot name in 3D Viewport")
    col.prop(props, "camera_hud_display_in_pov", text="Display HUD in 3D Viewport")
    col.prop(prefs, "cameraHUD_shotNameSize", text="Size of the shot names")
