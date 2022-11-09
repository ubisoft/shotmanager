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
Render operators
"""

from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty

from .rendering import launchRender

from shotmanager.utils import utils

from shotmanager.config import config


# def get_media_path(out_path, take_name, shot_name):

#     if out_path.startswith("//"):
#         out_path = str(Path(bpy.data.filepath).parent.absolute()) + out_path[1:]
#     return f"{out_path}/{take_name}/{bpy.context.scene.UAS_shot_manager_props.getRenderShotPrefix()}_{shot_name}.mp4"


##########
# Render
##########


class UAS_OT_OpenPathBrowser(Operator):
    bl_idname = "uas_shot_manager.openpathbrowser"
    bl_label = "Open"
    bl_description = (
        "Open a path browser to define the directory to use to render the images\n"
        "Relative path must be set directly in the text field and must start with ''//''"
    )

    # https://docs.blender.org/api/current/bpy.props.html
    #  filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    directory: StringProperty(subtype="DIR_PATH")

    # filter_glob : StringProperty(
    #     default = '*',
    #     options = {'HIDDEN'} )

    def invoke(self, context, event):  # See comments at end  [1]
        #  self.filepath = bpy.context.scene.UAS_shot_manager_props.renderRootPath
        # https://docs.blender.org/api/current/bpy.types.WindowManager.html

        props = config.getAddonProps(context.scene)
        self.directory = props.renderRootPath

        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Open a path browser to define the directory to use to render the images"""
        props = config.getAddonProps(context.scene)
        props.renderRootPath = self.directory
        return {"FINISHED"}


class UAS_PT_ShotManager_Render(Operator):
    bl_idname = "uas_shot_manager.render"
    bl_label = "Render"
    bl_description = "Render."
    bl_options = {"INTERNAL"}

    renderMode: EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(
            ("STILL", "Still", ""),
            ("ANIMATION", "Animation", ""),
            ("ALL", "All Edits", ""),
            ("OTIO", "OTIO", ""),
            ("PLAYBLAST", "PLAYBLAST", ""),
        ),
        default="STILL",
    )

    @classmethod
    def description(self, context, properties):
        descr = "_"
        # print("properties: ", properties)
        # print("properties action: ", properties.action)
        if "STILL" == properties.renderMode:
            descr = "Render a still image, at current frame and with the current shot"
        elif "ANIMATION" == properties.renderMode:
            descr = "Render the current shot"
        elif "ALL" == properties.renderMode:
            descr = "Render all: shots, takes, edit file..."
        elif "OTIO" == properties.renderMode:
            descr = "Generate the edit file for the current take: .otio or .xml (Final Cut)"
        elif "PLAYBLAST" == properties.renderMode:
            descr = "Fast-render the enabled shots to a single video based on the current viewport settings."

        return descr

    # def invoke(self, context, event):
    #     # context.window_manager.modal_handler_add(self)
    #     return {"RUNNING_MODAL"}

    # def modal(self, context, event):
    #     # https://blender.stackexchange.com/questions/78069/modal-function-of-a-modal-operator-is-never-called
    #     if event.type == "SPACE":
    #         # wm = context.window_manager
    #         # wm.invoke_popup(self)
    #         # #wm.invoke_props_dialog(self)
    #         print("Space")

    #     if event.type in {"ESC"}:
    #         return {"CANCELLED"}

    #     return {"RUNNING_MODAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        prefs.renderMode = self.renderMode

        # update UI
        if "STILL" == prefs.renderMode:
            props.displayStillProps = True
        elif "ANIMATION" == prefs.renderMode:
            props.displayAnimationProps = True
        elif "ALL" == prefs.renderMode:
            props.displayAllEditsProps = True
        elif "OTIO" == prefs.renderMode:
            props.displayOtioProps = True
        elif "PLAYBLAST" == prefs.renderMode:
            props.displayPlayblastProps = True

        if not props.sceneIsReady(displayDialogMessage=True):
            return {"CANCELLED"}

        if "ANIMATION" == prefs.renderMode:
            currentShot = props.getCurrentShot()
            if currentShot is None:
                utils.ShowMessageBox("Current Shot not found - Rendering aborted", "Render aborted")
                return {"CANCELLED"}
            if not currentShot.enabled:
                utils.ShowMessageBox("Current Shot is not enabled - Rendering aborted", "Render aborted")
                return {"CANCELLED"}

        # renderWarnings = ""
        # if props.renderRootPath.startswith("//"):
        #     if "" == bpy.data.filepath:
        #         renderWarnings = "*** Save file first ***"
        # elif "" == props.renderRootPath:
        #     renderWarnings = "*** Invalid Output File Name ***"

        # if "" != renderWarnings:
        #     from ..utils.utils import ShowMessageBox

        #     ShowMessageBox(renderWarnings, "Render Aborted", "ERROR")
        #     print("Render aborted before start: " + renderWarnings)
        #     return {"CANCELLED"}

        if False and "OTIO" == prefs.renderMode:
            bpy.ops.uas_shot_manager.export_otio()
        else:
            renderRootPath = props.renderRootPath if "" != props.renderRootPath else "//"
            bpy.path.abspath(renderRootPath)
            if not (renderRootPath.endswith("/") or renderRootPath.endswith("\\")):
                renderRootPath += "\\"

            # if props.isRenderRootPathValid():
            launchRender(
                context,
                prefs.renderMode,
                renderRootPath,
                # useStampInfo=props.useStampInfoDuringRendering,
                area=context.area,
            )

        #   return {"RUNNING_MODAL"}
        return {"FINISHED"}


###########
# utils
###########


class UAS_ShotManager_Render_RestoreProjectSettings(Operator):
    bl_idname = "uas_shot_manager.render_restore_project_settings"
    bl_label = "Apply Project Settings"
    bl_description = "Apply Project Settings"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.applyProjectSettings()
        return {"FINISHED"}


class UAS_ShotManager_Render_OpenLastRenderResults(Operator):
    bl_idname = "uas_shot_manager.open_last_render_results"
    bl_label = "Last Render Results"
    bl_description = "Open last render results log file"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # to do
        return {"FINISHED"}


class UAS_ShotManager_Render_ClearLastRenderResults(Operator):
    bl_idname = "uas_shot_manager.clear_last_render_results"
    bl_label = "Clear Last Render Results"
    bl_description = "Clear last render results log file"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # to do
        return {"FINISHED"}


_classes = (
    UAS_PT_ShotManager_Render,
    UAS_OT_OpenPathBrowser,
    UAS_ShotManager_Render_RestoreProjectSettings,
    UAS_ShotManager_Render_OpenLastRenderResults,
    UAS_ShotManager_Render_ClearLastRenderResults,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
