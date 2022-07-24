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
This module defines the Preference menu of StampInfo
"""

import bpy
from bpy.types import Menu

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


#############
# Preferences
#############


class UAS_MT_ShotManager_Prefs_StampInfoMainMenu(Menu):
    bl_idname = "UAS_MT_ShotManager_prefs_stampinfo_mainmenu"
    bl_label = "General Preferences"
    # bl_description = "General Preferences"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.separator(factor=5)
        resetOp = row.operator(
            "uas_sm_stamp_info.querybox", text="Reset Properties to Default Values...", icon="LOOP_BACK"
        )
        resetOp.width = 400
        resetOp.message = "Reset all the properties to their default value?"
        resetOp.function_name = "reset_all_properties"
        resetOp.descriptionText = "Set all the properties of the Stamp Info panel back to their default values"

        layout.separator()

        row = layout.row(align=True)
        row.operator("preferences.addon_show", text="Add-on Preferences...", icon="PREFERENCES").module = "shotmanager"

        layout.separator()
        row = layout.row(align=True)
        row.operator(
            "shotmanager.open_documentation_url", text="Documentation", icon="HELP"
        ).path = "https://ubisoft-stampinfo.readthedocs.io/"

        layout.separator()

        row = layout.row(align=True)
        row.operator("uas_stamp_info.about", text="About...")


_classes = (UAS_MT_ShotManager_Prefs_StampInfoMainMenu,)


def register():
    _logger.debug_ext("       - Registering Prefs Package", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Prefs Package", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
