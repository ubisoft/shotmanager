# -*- coding: utf-8 -*-

import bpy
from bpy.types import Panel, Operator
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, PointerProperty, FloatVectorProperty


#############
## Preferences
#############


class UAS_PT_ShotManagerPrefPanel(Panel):
    bl_label = "Preferences"
    bl_idname = "UAS_PT_Shot_Manager_Pref"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

    # shots preferences
    # row = layout.row()
    # row.label ( text = "Shots:" )
    # box = layout.box()
    # col = box.column()
    # col.use_property_split = True
    # col.prop ( context.scene.UAS_shot_manager_props, "display_camera_in_shotlist", text = "Display Camera in Shot List" )
    # col.prop ( context.scene.UAS_shot_manager_props, "new_shot_duration", text = "Default Shot Length" )
    # col.prop ( context.scene.UAS_shot_manager_props, "new_shot_prefix", text = "Default Shot Prefix" )

    # timeline preferences
    # row = layout.row()
    # row.label ( text = "Timeline:" )
    # box = layout.box()
    # col = box.column()
    # col.use_property_split = True
    # col.prop ( context.scene.UAS_shot_manager_props, "change_time", text = "Set Current Frame On Shot Selection" )
    # col.prop ( context.scene.UAS_shot_manager_props, "display_disabledshots_in_timeline", text = "Display Disabled Shots in Timeline" )


class UAS_PT_ShotManagerPref_General(Panel):
    bl_label = "General"
    bl_idname = "UAS_PT_Shot_Manager_Pref_General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.use_property_split = True
        col.label(text="PlaceHolder")


class UAS_PT_ShotManagerPref_Timeline(Panel):
    bl_label = "Play Mode and Timeline"
    bl_idname = "UAS_PT_Shot_Manager_Pref_Timeline"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        # box = layout.box()
        # col = box.column ( )
        # or
        col = row.column()
        col.use_property_split = True
        col.prop(context.scene.UAS_shot_manager_props, "change_time", text="Set Current Frame On Shot Selection")
        col.prop(
            context.scene.UAS_shot_manager_props,
            "display_disabledshots_in_timeline",
            text="Display Disabled Shots in Timeline",
        )

    #    col.prop ( context.scene.UAS_shot_manager_props, "display_prev_next_buttons", text = "Display Previous and Next Frame buttons in the play bar" )


class UAS_PT_ShotManagerPref_Shots(Panel):
    bl_label = "Shots"
    bl_idname = "UAS_PT_Shot_Manager_Pref_Shots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        # box = layout.box()
        # col = box.column ( )
        # or
        col = row.column()

        col.use_property_split = True
        #    col.prop ( context.scene.UAS_shot_manager_props, "display_camera_in_shotlist", text = "Display Camera in Shot List" )
        #    col.prop ( context.scene.UAS_shot_manager_props, "display_color_in_shotlist", text = "Display Color in Shot List" )
        col.prop(
            context.scene.UAS_shot_manager_props,
            "display_selectbut_in_shotlist",
            text="Display Camera Select button in Shot List",
        )
        col.separator()
        col.prop(
            context.scene.UAS_shot_manager_props,
            "highlight_all_shot_frames",
            text="Highlight all framing values in Shot List",
        )
        col.prop(context.scene.UAS_shot_manager_props, "current_shot_properties_mode")
        col.separator()
        col.prop(context.scene.UAS_shot_manager_props, "new_shot_duration", text="Default Shot Length")
        col.prop(context.scene.UAS_shot_manager_props, "new_shot_prefix", text="Default Shot Prefix")

        layout.separator()


_classes = (
    UAS_PT_ShotManagerPrefPanel,
    UAS_PT_ShotManagerPref_Shots,
    # UAS_PT_ShotManagerPref_General,
    UAS_PT_ShotManagerPref_Timeline,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
