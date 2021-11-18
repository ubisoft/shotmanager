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
Operators for Shot Manager
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

from shotmanager.config import config
from shotmanager.operators.shots import convertMarkersFromCameraBindingToShots
from shotmanager.utils.utils import getSceneVSE, convertVersionIntToStr, clearMarkersFromCameraBinding


###################
# Properties accessible by operators for key mapping
###################


class UAS_ShotManager_OT_ShotsPlayMode(Operator):
    bl_idname = "uas_shot_manager.shots_play_mode"
    bl_label = "Toggle Shots Play Mode"
    # bl_description = "Bla"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        context.window_manager.UAS_shot_manager_shots_play_mode = (
            not context.window_manager.UAS_shot_manager_shots_play_mode
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_DisplayOverlayTools(Operator):
    bl_idname = "uas_shot_manager.display_overlay_tools"
    bl_label = "Toggle Overlay Tools Display"
    # bl_description = "Toggle Overlay Tools Display"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        context.window_manager.UAS_shot_manager_display_overlay_tools = (
            not context.window_manager.UAS_shot_manager_display_overlay_tools
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_DisplayDisabledShotsInOverlays(Operator):
    bl_idname = "uas_shot_manager.display_disabledshots_in_overlays"
    bl_label = "Display Disabled Shots in Overlay Tools"
    # bl_description = "Display Disabled Shots in Overlay Tools"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props

        val = not props.interactShotsStack_displayDisabledShots
        props.interactShotsStack_displayDisabledShots = val
        props.seqTimeline_displayDisabledShots = val

        return {"FINISHED"}


###################
# Various
###################


class UAS_ShotManager_OT_ClearMarkersFromCameraBinding(Operator):
    bl_idname = "uas_shot_manager.clear_markers_from_camera_binding"
    bl_label = "Clear Camera Binding"
    bl_description = "Remove the camera binding from the markers used in the timeline.\nMarkers are not deleted"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        clearMarkersFromCameraBinding(context.scene)
        return {"FINISHED"}


class UAS_ShotManager_OT_ConvertMarkersFromCameraBindingToShots(Operator):
    bl_idname = "uas_shot_manager.convert_markers_from_camera_binding_to_shots"
    bl_label = "Convert Camera Binding to Shots"
    bl_description = (
        "Convert the camera binding used by markers to shots and remove their binding.\nMarkers are not deleted"
    )
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        convertMarkersFromCameraBindingToShots(context.scene)
        clearMarkersFromCameraBinding(context.scene)
        return {"FINISHED"}


class UAS_ShotManager_OT_GoToVideoShotManager(Operator):
    bl_idname = "uas_shot_manager.go_to_video_tracks"
    bl_label = "Go to the VSE Edit"
    bl_description = (
        "Update the edit in the VSE and switch to this layout.\n !! Add-on Video Tracks has to be installed !!"
    )
    bl_options = {"INTERNAL"}

    vseSceneName: StringProperty(default="")

    def invoke(self, context, event):

        vsm_scene = None
        if "" == self.vseSceneName:
            self.vseSceneName = "VideoShotManager"
        vsm_scene = getSceneVSE(self.vseSceneName, createVseTab=True)

        # startup_blend = os.path.join(
        #     bpy.utils.resource_path("LOCAL"),
        #     "scripts",
        #     "startup",
        #     "bl_app_templates_system",
        #     "Video_Editing",
        #     "startup.blend",
        # )

        # bpy.context.window.scene = vsm_scene
        # if "Video Editing" not in bpy.data.workspaces:
        #     bpy.ops.workspace.append_activate(idname="Video Editing", filepath=startup_blend)
        bpy.context.window.workspace = bpy.data.workspaces["Video Editing"]

        return {"FINISHED"}


class UAS_ShotManager_OT_FileInfo(Operator):
    bl_idname = "uas_shot_manager.file_info"
    bl_label = "File Info"
    bl_description = "Display information about the current file content"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        layout = self.layout
        # box = layout.box()

        # Scene
        ###############
        row = layout.row()
        row.label(text=f"Current Scene:  {context.scene.name}")

        row = layout.row()
        box = row.box()

        subRow = box.row()
        subRow.separator()
        subRow.label(text="Fps:")
        subRow.label(text=f"{scene.render.fps}")

        if 1.0 != scene.render.fps_base:
            subRow = box.row()
            subRow.alert = True
            subRow.separator()
            subRow.label(text="FPS Base:")
            subRow.label(text=f"{scene.render.fps_base:0.3f}")

        subRow = box.row()
        subRow.separator()
        subRow.label(text="Resolution:")
        subRow.label(text=f"{scene.render.resolution_x} x {scene.render.resolution_y}")
        if 100 != scene.render.resolution_percentage:
            subRow = box.row()
            subRow.alert = True
            subRow.separator()
            subRow.label(text="Percentage:")
            subRow.label(text=f"{scene.render.resolution_percentage} %")

        # Project
        ###############
        layout.separator()
        layout.label(text=f"Project Used: {props.use_project_settings}")
        if props.use_project_settings:
            box = layout.box()

            subRow = box.row()
            subRow.separator()
            subRow.label(text="Fps:")
            subRow.label(text=f"{props.project_fps}")

            subRow = box.row()
            subRow.separator()
            subRow.label(text="Resolution:")
            subRow.label(text=f"{props.project_resolution_x} x {props.project_resolution_y}")

            subRow = box.row()
            subRow.separator()
            subRow.label(text="Framed Resolution:")
            subRow.label(text=f"{props.project_resolution_framed_x} x {props.project_resolution_framed_y}")

        # Version
        ###############
        layout.separator()
        box = layout.box()
        row = box.row()
        row.separator()
        row.label(text="Shot Manager Version: ")
        row.label(text=f"{props.version()[0]}")

        row = box.row()
        row.separator()
        row.label(text="Shot Manager Data Version: ")
        row.label(text=f"  {convertVersionIntToStr(props.dataVersion)}")

        row.separator()

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_OT_EnableDebug(Operator):
    bl_idname = "uas_shot_manager.enable_debug"
    bl_label = "Enable Debug Mode"
    bl_description = "Enable or disable debug mode"
    bl_options = {"INTERNAL"}

    enable_debug: BoolProperty(name="Enable Debug Mode", description="Enable or disable debug mode", default=False)

    def execute(self, context):
        config.devDebug = self.enable_debug
        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_ShotsPlayMode,
    UAS_ShotManager_OT_DisplayDisabledShotsInOverlays,
    UAS_ShotManager_OT_DisplayOverlayTools,
    UAS_ShotManager_OT_ClearMarkersFromCameraBinding,
    UAS_ShotManager_OT_ConvertMarkersFromCameraBindingToShots,
    UAS_ShotManager_OT_GoToVideoShotManager,
    UAS_ShotManager_OT_FileInfo,
    UAS_ShotManager_OT_EnableDebug,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
