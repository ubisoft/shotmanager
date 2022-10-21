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
Sound background
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_EnableDisableSoundBG(Operator):
    bl_idname = "uas_shot_manager.enabledisablesoundbg"
    bl_label = "Enable / Disable Camera Backgrounds"
    bl_description = "Alternatively enable or disable the background image of the cameras used by the shots"
    bl_options = {"INTERNAL", "UNDO"}

    # can be Image, Sound, All
    mode: StringProperty(default="All")

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()

        if "All" == self.mode or "Sound" == self.mode:
            bpy.ops.uas_shots_settings.use_background_sound(useBackgroundSound=prefs.toggleCamsSoundBG)
            prefs.toggleCamsSoundBG = not prefs.toggleCamsSoundBG

        return {"FINISHED"}


classes = (UAS_ShotManager_EnableDisableSoundBG,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
