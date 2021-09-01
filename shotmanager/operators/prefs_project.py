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
from bpy.types import Operator

from ..config import config

#############
# Project references
#############


class UAS_ShotManager_ProjectSettings_Prefs(Operator):
    bl_idname = "uas_shot_manager.project_settings_prefs"
    bl_label = "Project Settings"
    bl_description = "Display the Project Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        print("Invoke prefs")
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        layout.prop(props, "use_project_settings")
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = props.use_project_settings
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.separator(factor=1)

        ############
        # naming
        ############
        col.separator(factor=1)
        col.prop(props, "project_name")
        col.prop(props, "project_default_take_name")
        col.prop(props, "project_shot_format")

        ############
        # handles
        ############
        col.separator(factor=1)
        row = col.row()
        row.prop(props, "project_use_shot_handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "project_shot_handle_duration", text="Handles")

        stampInfoStr = "Use Stamp Info Add-on"
        if not props.isStampInfoAvailable():
            stampInfoStr += "  (Warning: Currently NOT installed)"
        col.prop(props, "project_use_stampinfo", text=stampInfoStr)
        row = col.row()
        row.alignment = "RIGHT"
        row.enabled = props.project_use_stampinfo
        row.label(text="Logo")
        # row.separator(factor=0)
        subrow = row.row()
        subrow.scale_x = 1.0
        subrow.prop(props, "project_logo_path", text="")

        ############
        # resolution
        ############
        col.separator(factor=2)
        col.prop(props, "project_fps")

        col.separator(factor=0.5)
        row = col.row(align=False)
        row.use_property_split = False
        row.alignment = "RIGHT"
        row.label(text="Resolution")
        row.prop(props, "project_resolution_x", text="Width:")
        row.prop(props, "project_resolution_y", text="Height:")

        row = col.row(align=False)
        row.use_property_split = False
        row.alignment = "RIGHT"
        row.label(text="Frame Resolution")
        row.prop(props, "project_resolution_framed_x", text="Width:")
        row.prop(props, "project_resolution_framed_y", text="Height:")

        ############
        # color space
        ############
        if config.uasDebug:
            col.separator(factor=0.5)
            col.prop(props, "project_color_space")

        ############
        # outputs
        ############

        col.separator(factor=2)
        col.prop(props, "project_output_format", text="Video Output Format")

        col.separator(factor=1)
        col.prop(props, "project_images_output_format", text="Image Output Format")

        col.separator(factor=1)
        col.prop(props, "project_sounds_output_format", text="Sound Output Format")

        if config.uasDebug:
            # additional settings
            box.separator()
            box.label(text="Additional Settings:")
            col = box.column()
            col.enabled = props.use_project_settings
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(props, "project_asset_name")

        col.separator(factor=1)

        # project settings summary display
        if config.uasDebug:
            settingsList = props.applyProjectSettings(settingsListOnly=True)
            box = layout.box()
            for prop in settingsList:
                row = box.row(align=True)
                row.label(text=prop[0] + ":")
                row.label(text=str(prop[1]))

    def execute(self, context):
        print("exec proj settings")
        context.scene.UAS_shot_manager_props.applyProjectSettings()
        return {"FINISHED"}

    def cancel(self, context):
        print("cancel proj settings")
        # since project properties are immediatly applied to Shot Manager properties then we also force the
        # application of the settings in the scene even if the user is not clicking on OK button
        context.scene.UAS_shot_manager_props.applyProjectSettings()


_classes = (UAS_ShotManager_ProjectSettings_Prefs,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
