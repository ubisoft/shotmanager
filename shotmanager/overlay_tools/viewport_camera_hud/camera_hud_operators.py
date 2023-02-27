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

import bpy
from bpy.types import Operator

from shotmanager.config import config


class UAS_ShotManager_CameraHUD_ToggleDisplay(Operator):
    bl_idname = "uas_shot_manager.camerahud_toggle_display"
    bl_label = "Toggle Camera HUD Display"
    bl_description = "Toggle Camera HUD Display"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        val = not props.camera_hud_display_in_viewports or not props.camera_hud_display_in_pov
        props.camera_hud_display_in_viewports = val
        props.camera_hud_display_in_pov = val

        return {"FINISHED"}


_classes = (UAS_ShotManager_CameraHUD_ToggleDisplay,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
