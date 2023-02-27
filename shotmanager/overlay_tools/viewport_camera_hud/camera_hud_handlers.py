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
Camera HUD
"""

import bpy
from bpy.app.handlers import persistent

from shotmanager.config import config


@persistent
def shotMngHandler_load_post_cameraHUD(self, context):
    # print("Activating Camera HUD Handlers")

    props = config.getAddonProps(bpy.context.scene)
    if props is not None:
        if props.camera_hud_display_in_viewports:
            try:
                bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports("INVOKE_DEFAULT")
            except Exception:
                print("******** Paf in draw cameras ui handler  *")

        if props.camera_hud_display_in_pov:
            # bpy.ops.uas_shot_manager.draw_camera_hud_in_pov("INVOKE_DEFAULT")
            try:
                bpy.ops.uas_shot_manager.draw_camera_hud_in_pov("INVOKE_DEFAULT")
            except Exception:
                print("****** Paf in draw hud on camera pov handler  *")
                # raise()
