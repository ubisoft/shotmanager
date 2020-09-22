import logging

_logger = logging.getLogger(__name__)

import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty

from shotmanager.config import config
from shotmanager.viewport_3d.ogl_ui import UAS_ShotManager_DrawTimeline

from shotmanager.utils import utils


#############
# tools for Takes
#############


class UAS_MT_ShotManager_Takes_ToolsMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_takes_toolsmenu"
    bl_label = "Take Tools"
    bl_description = "Take Tools"

    def draw(self, context):

        # marker_list = context.scene.timeline_markers
        # list_marked_cameras = [o.camera for o in marker_list if o != None]

        # Copy menu entries[ ---
        layout = self.layout
        row = layout.row(align=True)

        #    row.label(text="Tools for Current Take:")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_add", text="Add...", icon="ADD")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_duplicate", text="Duplicate...", icon="DUPLICATE")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.take_remove", text="Remove", icon="REMOVE")

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

