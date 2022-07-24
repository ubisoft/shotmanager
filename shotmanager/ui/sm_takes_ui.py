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
UI for takes
"""

import bpy
from bpy.types import Menu

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


#############
# tools for Takes
#############


class UAS_MT_ShotManager_Takes_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_takes_toolsmenu"
    bl_label = "Take Tools"
    # bl_description = "Take Tools"

    def draw(self, context):

        # marker_list = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        #    row.label(text="Tools for Current Take:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_add", text="Add Take...", icon="ADD")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_duplicate", text="Duplicate Take...", icon="DUPLICATE")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_remove", text="Remove Take", icon="REMOVE")

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_move_up", icon="TRIA_UP", text="Move Up")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_move_down", icon="TRIA_DOWN", text="Move Down")

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_as_main", text="Set as Main Take")

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_rename", text="Rename...")  # , icon = "SYNTAX_ON"),

        layout.separator()

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.reset_takes_to_default", text="Reset to Default...")


classes = (UAS_MT_ShotManager_Takes_ToolsMenu,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
