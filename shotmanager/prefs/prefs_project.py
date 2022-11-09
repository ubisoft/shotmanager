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
Preferences related to a project configuration
"""

import os
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty

# for file browser:
from bpy_extras.io_utils import ImportHelper

from ..utils import utils_ui
from ..config import config

#############
# Project references
#############


class UAS_ShotManager_ProjectSettings_Prefs(Operator):
    bl_idname = "uas_shot_manager.project_settings_prefs"
    bl_label = "Project Settings"
    bl_description = "Display the Project Settings panel\nfor the Shot Manager instanced in this scene"
    bl_options = {"INTERNAL"}

    uiImagesOutputFormat: EnumProperty(
        name="Image Output Format",
        description="File format for the rendered output images, BEFORE composition with the Stamp Info framing images"
        "\nExpected values: PNG, OPEN_EXR",
        items=(
            ("PNG", "PNG", ""),
            ("OPEN_EXR", "OPEN_EXR", ""),
        ),
        default="PNG",
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = config.getAddonProps(scene)

        sepLowerHeight = 1.0
        sepHigherHeight = 0.4
        sepPropsHeight = 0.7

        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        layout.prop(props, "use_project_settings")
        box = layout.box()
        box.use_property_decorate = False
        box.enabled = props.use_project_settings

        mainCol = box.column(align=False)

        mainCol.label(text="Project:")
        col = mainCol.column()
        col.use_property_split = True
        col.use_property_decorate = False

        # project name
        ############
        col.prop(props, "project_name")
        subrow = col.row(align=True)
        subrow.scale_x = 1.0

        # logo
        ############
        propRow = col.row(align=False)
        propRowSplit = propRow.split(factor=0.4)
        propRowLeft = propRowSplit.row()
        propRowLeft.alignment = "RIGHT"
        propRowLeft.label(text="Logo")
        propRowRight = propRowSplit.row(align=True)
        logoRow = propRowRight.row(align=True)
        if props.project_logo_path != "":
            logoRow.alert = not Path(props.project_logo_path).exists()
        logoRow.prop(props, "project_logo_path", text="")
        propRowRight.operator("shotmanager.set_project_logo", text="", icon="FILEBROWSER")

        ############
        # naming conventions
        ############
        utils_ui.separatorLine(mainCol, padding_bottom=sepLowerHeight, padding_top=sepHigherHeight)

        mainCol.label(text="Naming Conventions:")
        col = mainCol.column(align=False)
        col.use_property_split = True
        col.use_property_decorate = False

        namingRow = col.row(align=False)
        namingRowSplit = namingRow.split(factor=0.4)
        namingRowLeft = namingRowSplit.row()
        namingRowLeft.alignment = "RIGHT"
        namingRowLeft.label(text="Proj. / Seq. / Shot Identifiers")
        namingRowRight = namingRowSplit.row(align=True)
        namingRowRight.prop(props, "project_naming_project_format", text="")
        namingRowRight.prop(props, "project_naming_sequence_format", text="")
        namingRowRight.prop(props, "project_naming_shot_format", text="")

        col.prop(props, "project_naming_separator_char")

        namingRow = col.row(align=False)
        namingRowSplit = namingRow.split(factor=0.4)
        namingRowLeft = namingRowSplit.row()
        namingRowLeft.alignment = "RIGHT"
        shotNameEg = props.getProjectOutputMediaName(projInd=3, seqInd=20, shotInd=40)
        namingRowLeft.label(text="Eg. Resulting Shot Full Name")
        namingRowRight = namingRowSplit.row(align=True)
        namingRowRight.label(text=shotNameEg)

        col.separator()
        col.prop(props, "project_default_take_name")

        ############
        # settings
        ############
        utils_ui.separatorLine(mainCol, padding_bottom=sepLowerHeight, padding_top=sepHigherHeight)

        mainCol.label(text="Settings:")
        col = mainCol.column(align=False)
        col.use_property_split = True
        col.use_property_decorate = False

        # resolution
        ############
        # col.separator(factor=2)
        col.prop(props, "project_fps")

        col.separator(factor=sepPropsHeight)
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

        # handles
        ############
        col.separator(factor=sepPropsHeight)
        row = col.row()
        row.prop(props, "project_use_shot_handles")
        subrow = row.row()
        subrow.enabled = props.project_use_shot_handles
        subrow.prop(props, "project_shot_handle_duration", text="Handles")

        # color space
        ############
        if config.devDebug:
            col.separator(factor=0.5)
            col.prop(props, "project_color_space")

        ############
        # camera assets file
        ############
        utils_ui.separatorLine(mainCol, padding_bottom=sepLowerHeight, padding_top=sepHigherHeight)

        propRow = mainCol.row(align=False)
        propRowSplit = propRow.split(factor=0.4)
        propRowLeft = propRowSplit.row()
        propRowLeft.alignment = "RIGHT"
        propRowLeft.label(text="Camera Assets File")
        propRowRight = propRowSplit.row(align=True)
        logoRow = propRowRight.row(align=True)
        if props.project_cameraAssets_path != "":
            logoRow.alert = not Path(props.project_cameraAssets_path).exists()
        logoRow.prop(props, "project_cameraAssets_path", text="")
        propRowRight.operator("shotmanager.set_project_camera_assets_path", text="", icon="FILEBROWSER")

        ############
        # outputs
        ############
        utils_ui.separatorLine(mainCol, padding_bottom=sepLowerHeight, padding_top=sepHigherHeight)

        mainCol.label(text="Outputs:")
        col = mainCol.column(align=False)
        col.use_property_split = True
        col.use_property_decorate = False

        stampInfoStr = "Use Stamp Info Add-on"
        col.prop(props, "project_use_stampinfo", text=stampInfoStr)
        # row = col.row()
        # row.alignment = "RIGHT"
        # row.enabled = props.project_use_stampinfo

        col.separator(factor=sepPropsHeight)

        col.prop(props, "project_output_first_frame", text="Video First Frame Index")
        col.prop(props, "project_img_name_digits_padding", text="Frame Digits Padding")
        col.separator(factor=sepPropsHeight)
        col.prop(props, "project_output_format", text="Video Output Format")
        # col.prop(props, "project_images_output_format", text="Image Output Format")
        col.prop(self, "uiImagesOutputFormat", text="Image Output Format")
        col.prop(props, "project_sounds_output_format", text="Sound Output Format")

        if config.devDebug:
            # additional settings
            utils_ui.separatorLine(mainCol, padding_bottom=sepLowerHeight, padding_top=sepHigherHeight)

            mainCol.label(text="Additional Settings:")
            col = mainCol.column()
            col.enabled = props.use_project_settings
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(props, "project_asset_name")

        col.separator(factor=1)

        # project settings summary display
        if config.devDebug:
            settingsList = props.applyProjectSettings(settingsListOnly=True)
            box = layout.box()
            col = box.column()
            col.scale_y = 0.8
            for prop in settingsList:
                split = col.split(factor=0.4, align=True)
                row = split.row()
                row.alignment = "RIGHT"
                row.label(text=prop[0] + ":")
                split.label(text=str(prop[1]))

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        props.project_images_output_format = self.uiImagesOutputFormat

        context.scene.UAS_shot_manager_props.applyProjectSettings()
        return {"FINISHED"}

    def cancel(self, context):
        # since project properties are immediatly applied to Shot Manager properties then we also force the
        # application of the settings in the scene even if the user is not clicking on OK button
        scene = context.scene
        props = config.getAddonProps(scene)
        props.project_images_output_format = self.uiImagesOutputFormat

        context.scene.UAS_shot_manager_props.applyProjectSettings()
        # return {'CANCELLED'}
        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_SetProjectLogo(Operator, ImportHelper):
    bl_idname = "shotmanager.set_project_logo"
    bl_label = "Project Logo"
    bl_description = (
        "Open the file browser to define the image to stamp\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.tga,*.bmp", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file as a stamped logo"""

        props = config.getAddonProps(context.scene)

        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        props.project_logo_path = self.filepath

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_SetProjectCameraAssetsPath(Operator, ImportHelper):
    bl_idname = "shotmanager.set_project_camera_assets_path"
    bl_label = "Project Camera Assets"
    bl_description = (
        "Open the file browser to define the Blender file containing camera assets\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    filter_glob: StringProperty(default="*.blend;", options={"HIDDEN"})

    def execute(self, context):
        """Use the selected file to get the assets library"""

        props = config.getAddonProps(context.scene)

        filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        props.project_cameraAssets_path = self.filepath

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_ProjectSettings_Prefs,
    UAS_ShotManager_SetProjectLogo,
    UAS_ShotManager_SetProjectCameraAssetsPath,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
