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
Shot template list preferences
"""

import bpy
from bpy.types import Panel, Operator

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
        prefs = config.getAddonPrefs()
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

#         if getattr(scene, "UAS_SM_StampInfo_Settings", None) is not None:
#             # row.alert = True
#             row.label(text="Version not found")
#             row.alert = False
#         else:
#             try:
#                 versionStr = utils.addonVersion("UAS_StampInfo")
#                 row.label(text="Loaded - V." + versionStr)
#                 # row.label(text="Loaded - V." + context.scene.UAS_SM_StampInfo_Settings.version())
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
    # UAS_PT_ShotManager_Render_StampInfoProperties,
)


def register():

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
