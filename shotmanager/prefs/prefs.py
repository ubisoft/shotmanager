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

from shotmanager.config import config


#############
# Preferences
#############


class UAS_ShotManager_General_Prefs(Operator):
    bl_idname = "uas_shot_manager.general_prefs"
    bl_label = "Scene Settings"
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

        box = layout.box()
        box.use_property_decorate = False
        row = box.row()
        row.label(text="Debug Mode:")
        subrow = row.row()
        subrow.operator("uas_shot_manager.enable_debug", text="On").enable_debug = True
        subrow.operator("uas_shot_manager.enable_debug", text="Off").enable_debug = False

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


class UAS_ShotManager_Shots_Prefs(Operator):
    bl_idname = "uas_shot_manager.shots_prefs"
    bl_label = "Shots Display Settings"
    bl_description = "Display the Shots Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        prefs = bpy.context.preferences.addons["shotmanager"].preferences

        layout = self.layout

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        # Shot List
        ##############
        layout.label(text="Shot List:")
        box = layout.box()
        box.use_property_decorate = False

        # main column, to allow title offset
        maincol = box.column()
        row = maincol.row()
        row.separator(factor=2)
        row.label(text="Display:")

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.4
        col.label(text=" ")
        col = row.column()

        col.separator(factor=0.5)
        col.use_property_split = False
        col.prop(props, "display_selectbut_in_shotlist", text="Display Camera Select Button")
        col.prop(props, "display_enabled_in_shotlist", text="Display Enabled State")
        col.prop(props, "display_getsetcurrentframe_in_shotlist", text="Display Get/Set current Frame Buttons")

        col.prop(props, "display_cameraBG_in_shotlist")
        col.prop(props, "display_greasepencil_in_shotlist")

        col.separator(factor=1.7)
        col.prop(props, "highlight_all_shot_frames", text="Highlight Framing Values When Equal to Current Time")
        col.prop(props, "display_duration_after_time_range", text="Display Shot Duration After Time Range")
        col.prop(props, "use_camera_color", text="Use Camera Color for Shots ")

        col.use_property_split = False
        col.separator(factor=1.7)
        row = col.row()
        row.label(text="Display Shot Properties Mode:")
        row.prop(props, "current_shot_properties_mode", text="")
        row.separator()

        # User Prefs at addon level
        ###############

        box.separator(factor=0.5)
        # main column, to allow title offset
        maincol = box.column()
        row = maincol.row()
        row.separator(factor=2)
        row.label(text="When Current Shot Is Changed:  (Settings stored in the Add-on Preferences):")

        # empty spacer column
        row = maincol.row()
        col = row.column()
        col.scale_x = 0.28
        col.label(text=" ")
        col = row.column()

        # col.separator(factor=1.0)
        # col.label(text="Time Change:")
        #  col.label(text="User Preferenes (in Preference Add-on Window):")
        col.separator(factor=0.5)
        col.use_property_split = False
        col.prop(
            prefs,
            "current_shot_changes_current_time_to_start",
            text="Set Current Frame To Shot Start",
        )
        col.prop(
            prefs,
            "current_shot_changes_time_range",
            text="Set Scene Animation Range To Shot Range",
        )
        col.prop(
            prefs,
            "current_shot_changes_time_zoom",
            text="Zoom Timeline Content To Frame The Current Shot",
        )

        # on selected shot changed
        maincol.separator(factor=1.5)
        row = maincol.row()
        row.separator(factor=2)
        row.label(text="When Selected Shot Is Changed:  (Settings stored in the Add-on Preferences):")
        propsRow = maincol.row()
        propsRow.separator(factor=5)
        propsCol = propsRow.column()
        propsCol.prop(
            prefs,
            "selected_shot_changes_current_shot_in_stb",
            text="Storyboard Shots List: Set Selected Shot to Current One",
        )
        shotsStackRow = propsCol.row()
        shotsStackRow.separator(factor=5)
        shotsStackRow.prop(
            prefs,
            "selected_shot_in_shots_stack_changes_current_shot_in_stb",
            text="Shots Stack: Set Selected Shot to Current One",
        )

        propsCol.prop(
            prefs,
            "current_shot_changes_edited_frame_in_stb",
            text="Storyboard Shots List: Set Selected Shot to Edited One",
        )

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
    UAS_ShotManager_General_Prefs,
    # UAS_PT_ShotManagerPref_General,
    UAS_ShotManager_Shots_Prefs,
    # UAS_PT_ShotManager_Render_StampInfoProperties,
)


def register():

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
