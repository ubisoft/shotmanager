import bpy

from bpy.types import Panel, Menu, Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

from ..properties import vsm_props
from ..operators import tracks

import shotmanager.config as config

from .vsm_ui import UAS_PT_VideoShotManager


class UAS_VideoShotManager_SelectStrip(Operator):
    bl_idname = "uas_videoshotmanager.select_strip"
    bl_label = "Select"
    bl_description = "Select Strip"
    bl_options = {"INTERNAL"}

    # @classmethod
    # def poll(cls, context):
    #     props = context.scene.UAS_shot_manager_props
    #     val = len(props.getTakes()) and len(props.get_shots())
    #     return val

    # def invoke(self, context, event):
    #     props = context.scene.UAS_shot_manager_props

    #     return {"FINISHED"}
    # can be "SEL_SEQ", "ACTIVE"
    mode: StringProperty("SEL_SEQ")

    def execute(self, context):
        scene = context.scene

        if "SEL_SEQ" == self.mode:
            if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
                seq = bpy.context.selected_sequences[0]
                seq.select = False
                seq.select = True
        elif "ACTIVE" == self.mode:
            if scene.sequence_editor.active_strip is not None:
                seq = scene.sequence_editor.active_strip
                seq.select = False
                seq.select = True

        return {"FINISHED"}


class UAS_PT_VideoShotManagerSelectedStrip(Panel):
    bl_idname = "UAS_PT_VideoShotManagerSelectedStripPanel"
    bl_label = "Active Strip"
    bl_description = "Active Strip Options"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "UAS Video Shot Man"
    bl_parent_id = "UAS_PT_Video_Shot_Manager"
    # bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scene = context.scene
        prefs = context.preferences.addons["shotmanager"].preferences
        layout = self.layout

        row = layout.row()
        row.label(text="Active Strip:")
        subRow = row.row()
        # if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
        #     subRow.prop(bpy.context.selected_sequences[0], "name", text="")
        if scene.sequence_editor is not None and scene.sequence_editor.active_strip is not None:
            subRow.prop(scene.sequence_editor.active_strip, "name", text="")
        else:
            subRow.enabled = False
            subRow.prop(prefs, "emptyField", text="")
        subRow.operator(
            "uas_videoshotmanager.select_strip", text="", icon="RESTRICT_SELECT_OFF"
        ).mode = "ACTIVE"  # "SEL_SEQ"

        row = layout.row()
        row.label(text="Type:")
        if bpy.context.selected_sequences is not None and 1 == len(bpy.context.selected_sequences):
            row.label(text=str(type(bpy.context.selected_sequences[0]).__name__))

        # if config.uasDebug:
        #     box = layout.box()
        #     box.label(text="Tools:")
        #     row = box.row()
        #     #  row.operator("uas_video_shot_manager.selected_to_active")

        #     box = layout.box()

        #     row = box.row()
        #     row.separator(factor=0.1)


_classes = (
    UAS_PT_VideoShotManagerSelectedStrip,
    UAS_VideoShotManager_SelectStrip,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
