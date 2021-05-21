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
To do: module description here.
"""

import bpy
from bpy.types import Panel, Operator, Menu

from . import prefs_project

from ..config import config


#############
# Preferences
#############


class UAS_MT_ShotManager_Prefs_MainMenu(Menu):
    bl_idname = "UAS_MT_Shot_Manager_prefs_mainmenu"
    bl_label = "Settings for the Shot Manager instanced in this scene"
    # bl_description = "Display the settings for the Shot Manager instanced in the current scene"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("preferences.addon_show", text="Add-on Preferences...").module = "shotmanager"

        layout.separator()
        row = layout.row(align=True)
        row.operator("uas_shot_manager.general_prefs")
        row = layout.row(align=True)
        row.operator("uas_shot_manager.project_settings_prefs")

        layout.separator()
        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.playbar_prefs")  # , icon="SETTINGS")

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.shots_prefs")  # , icon="SETTINGS")

        if config.uasDebug:
            layout.separator()
            row = layout.row(align=True)
            row.label(text="Tools for Debug:")

            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            row.label(text="Add debug operator here")
            # row.operator("uas_shot_manager.predec_shots_from_single_cam")

        layout.separator()
        row = layout.row(align=True)

        row = layout.row(align=True)
        row.operator_context = "INVOKE_DEFAULT"
        row.operator("uas_shot_manager.file_info", text="File Info...")

        layout.separator()
        row = layout.row(align=True)

        row.operator("uas_shot_manager.about", text="About...")


class UAS_ShotManager_General_Prefs(Operator):
    bl_idname = "uas_shot_manager.general_prefs"
    bl_label = "Settings..."
    bl_description = "Display the Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        box = layout.box()
        box.use_property_decorate = False
        col = box.column()
        col.use_property_split = True
        # col.use_property_decorate = False

        col.prop(prefs, "new_shot_duration", text="Default Shot Length")

        ##################
        # Overriden by project settings
        ##################

        layout.separator()
        if props.use_project_settings:
            row = layout.row()
            row.alert = True
            row.label(text="Overriden by Project Settings:")
        else:
            # layout.label(text="Others")
            pass
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = not props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.prop(props, "new_shot_prefix", text="Default Shot Prefix")

        # row = layout.row()
        # row.label(text="Handles:")
        col.prop(props, "render_shot_prefix")
        col.prop(props, "renderSingleFrameShotAsImage")

        col.separator()
        row = col.row()
        row.prop(props, "use_handles", text="Use Handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "handles", text="Handles")
        col.separator()

        box = layout.box()
        box.use_property_decorate = False
        row = box.row()
        row.label(text="Debug Mode:")
        subrow = row.row()
        subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = True
        subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = False

        # col.use_property_split = True
        # col.o
        # col.use_property_decorate = False

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_PT_ShotManagerPref_General(Panel):
    bl_label = "General"
    bl_idname = "UAS_PT_Shot_Manager_Pref_General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager_Pref"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.use_property_split = True
        col.label(text="PlaceHolder")


class UAS_ShotManager_Playbar_Prefs(Operator):
    bl_idname = "uas_shot_manager.playbar_prefs"
    bl_label = "Playbar Settings..."
    bl_description = (
        "Display the Playbar, Timeline and Edit Settings panel\nfor the Shot Manager instanced in this scene"
    )
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Playbar ######
        # layout.label(text="Playbar:")
        # box = layout.box()
        # col = box.column()

        # col.use_property_split = True
        # col.separator(factor=1.7)
        # col.prop(props, "current_shot_properties_mode")
        # box.separator(factor=0.5)

        # Play ######
        # layout.separator(factor=1)
        layout.label(text="Shot Play Mode:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        col.prop(props, "refreshUIDuringPlay")

        # Timeline ######
        # layout.separator(factor=1)
        layout.label(text="Timeline:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        # col.use_property_decorate = False
        col.prop(
            props, "display_disabledshots_in_timeline", text="Display Disabled Shots",
        )

        # Edit ######
        layout.separator(factor=1)
        layout.label(text="Edit:")
        box = layout.box()
        box.use_property_decorate = False
        col = box.column()

        col.use_property_split = True
        col.prop(props, "editStartFrame", text="Index of the First Frame in the Edit:")
        # box.separator(factor=0.5)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_Shots_Prefs(Operator):
    bl_idname = "uas_shot_manager.shots_prefs"
    bl_label = "Shots Settings..."
    bl_description = "Display the Shots Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props

        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Shot List
        ##############
        layout.label(text="Shot List:")
        box = layout.box()
        box.use_property_decorate = False

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=0.5)
        col.use_property_split = False
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")
        col.prop(props, "display_edit_times_in_shotlist", text="Display Edit Times in Shot List")

        col.separator(factor=1.7)
        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")
        col.prop(props, "display_duration_after_time_range", text="Display Shot Duration After Time Range")

        col.separator(factor=1.0)
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.use_property_split = False
        col.separator(factor=1.7)
        col.prop(props, "current_shot_properties_mode")

        box.separator(factor=0.5)

        # User Prefs at addon level
        ###############
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        # empty spacer column
        row = box.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=2.0)
        #  col.label(text="User Preferenes (in Preference Add-on Window):")
        col.prop(
            prefs,
            "current_shot_changes_current_time",
            text="Set Current Frame To Shot Start When Current Shot Is Changed",
        )
        col.prop(
            prefs, "current_shot_changes_time_range", text="Set Time Range To Shot Range When Current Shot Is Changed"
        )

        # Shot infos displayed in viewport
        ###############
        layout.separator(factor=1)
        layout.label(text="Shot Info Displayed in 3D Viewport:")
        box = layout.box()
        col = box.column()

        col.use_property_split = True
        col.prop(props, "display_shotname_in_3dviewport", text="Display Shot name in 3D Viewport")
        col.prop(props, "display_hud_in_3dviewport", text="Display HUD in 3D Viewport")

        # col.prop(
        #     props, "display_selectbut_in_shotlist", text="Display Camera Select Button",
        # )
        # col.prop(
        #     props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time",
        # )

        # col.separator(factor=0.7)
        # col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        # col.separator(factor=0.7)
        # col.prop(props, "change_time", text="Set Current Frame To Shot Start When Current Shot Is Changed")

        # col.use_property_split = True
        # col.separator(factor=1.7)
        # col.prop(props, "current_shot_properties_mode")
        # box.separator(factor=0.5)

        layout.separator(factor=2)

    def execute(self, context):
        return {"FINISHED"}


# class UAS_PT_ShotManager_Render_StampInfoProperties(Panel):
#     bl_label = "Stamp Info Properties"
#     bl_idname = "UAS_PT_Shot_Manager_Pref_StampInfoPrefs"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Shot Mng"
#     bl_options = {"DEFAULT_CLOSED"}
#     bl_parent_id = "UAS_PT_Shot_Manager_Pref"

#     def draw_header_preset(self, context):
#         layout = self.layout
#         layout.emboss = "NONE"
#         row = layout.row(align=True)

#         if getattr(scene, "UAS_StampInfo_Settings", None) is not None:
#             # row.alert = True
#             row.label(text="Version not found")
#             row.alert = False
#         else:
#             try:
#                 versionStr = utils.addonVersion("UAS_StampInfo")
#                 row.label(text="Loaded - V." + versionStr)
#                 # row.label(text="Loaded - V." + context.scene.UAS_StampInfo_Settings.version())
#             except Exception as e:
#                 #    row.alert = True
#                 row.label(text="Not found")

#     def draw(self, context):
#         box = self.layout.box()
#         row = box.row()
#         row.prop(context.scene.UAS_shot_manager_props, "useStampInfoDuringRendering")


_classes = (
    UAS_MT_ShotManager_Prefs_MainMenu,
    UAS_ShotManager_General_Prefs,
    # UAS_PT_ShotManagerPref_General,
    UAS_ShotManager_Playbar_Prefs,
    UAS_ShotManager_Shots_Prefs,
    # UAS_PT_ShotManager_Render_StampInfoProperties,
)


def register():

    prefs_project.register()

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    prefs_project.unregister()
