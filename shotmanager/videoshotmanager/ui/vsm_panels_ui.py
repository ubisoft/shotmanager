import bpy

from bpy.types import Panel, Menu
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from ..properties import vsm_props
from ..operators import tracks

import shotmanager.config as config

from .vsm_ui import UAS_PT_VideoShotManager


######
# Video Shot Manager main panel #
######


class UAS_PT_VideoShotManagerSelectedStrip(Panel):
    bl_idname = "UAS_PT_VideoShotManagerSelectedStripPanel"
    bl_label = "Selected Strip"
    bl_description = "Selected Strip Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Shot_Manager"
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        return not props.dontRefreshUI()

    def draw(self, context):
        prefs = context.preferences.addons["shotmanager"].preferences

        layout = self.layout

        row = layout.row()
        row.label(text="Selected Strip:")
        subRow = row.row()
        if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
            subRow.prop(bpy.context.selected_sequences[0], "name", text="")
        else:
            subRow.enabled = False
            subRow.prop(prefs, "emptyField", text="")
        row = layout.row()
        row.label(text="Type:")
        if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
            row.label(text=str(type(bpy.context.selected_sequences[0]).__name__))

        if config.uasDebug:
            box = layout.box()
            box.label(text="Tools:")
            row = box.row()
            #  row.operator("uas_shot_manager.selected_to_active")

            box = layout.box()

            row = box.row()
            row.separator(factor=0.1)


_classes = (UAS_PT_VideoShotManagerSelectedStrip,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
