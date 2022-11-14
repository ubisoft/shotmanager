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
from bpy.props import BoolProperty, StringProperty, IntProperty

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil
from shotmanager.operators.shots import convertMarkersFromCameraBindingToShots
from shotmanager.utils.utils import getSceneVSE, convertVersionIntToStr
from shotmanager.utils.utils_markers import clearMarkersFromCameraBinding

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

###################
# Properties accessible by operators for key mapping
###################


class UAS_ShotManager_OT_ShotsPlayMode(Operator):
    bl_idname = "uas_shot_manager.shots_play_mode"
    bl_label = "Ubisoft Shot Mng - Toggle Shots Play Mode"
    bl_description = "Enable / disable the Shots Play Mode"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        context.window_manager.UAS_shot_manager_shots_play_mode = (
            not context.window_manager.UAS_shot_manager_shots_play_mode
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_DisplayOverlayTools(Operator):
    bl_idname = "uas_shot_manager.display_overlay_tools"
    bl_label = "Ubisoft Shot Mng - Toggle Overlay Tools Display"
    bl_description = "Show or hide the Sequence Timeline, Interactive Shots Stack and some other tools"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        # _logger.debug_ext(f"uas_shot_manager.display_overlay_tools Poll", col="PURPLE")
        props = config.getAddonProps(context.scene)
        return len(props.get_shots())

    def execute(self, context):
        prefs = config.getAddonPrefs()
        # we force the update of the prefs display factor value
        prefs.shtStack_screen_display_factor_mode = prefs.shtStack_screen_display_factor_mode

        #  _logger.debug_ext(f"uas_shot_manager.display_overlay_tools Invoke", col="PURPLE")
        context.window_manager.UAS_shot_manager_display_overlay_tools = (
            not context.window_manager.UAS_shot_manager_display_overlay_tools
        )

        return {"FINISHED"}


class UAS_ShotManager_OT_DisplayDisabledShotsInOverlays(Operator):
    bl_idname = "uas_shot_manager.display_disabledshots_in_overlays"
    bl_label = "Display disabled shots in the Shots Stack and the Sequence Timeline"
    # bl_description = "Display Disabled Shots in Overlay Tools"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        val = not props.interactShotsStack_displayDisabledShots
        props.interactShotsStack_displayDisabledShots = val
        props.seqTimeline_displayDisabledShots = val

        return {"FINISHED"}


class UAS_ShotManager_OT_ChangeLayout(Operator):
    bl_idname = "uas_shot_manager.change_layout"
    bl_label = "Toggle layout between Storyboard and Previz"
    # bl_description = " "
    bl_options = {"INTERNAL"}

    @classmethod
    def description(self, context, properties):
        props = config.getAddonProps(context.scene)
        if "STORYBOARD" == props.currentLayoutMode():
            descr = "\nCurrent layout: Storyboard"
        else:
            descr = "\nCurrent layout: Previz"
        return descr

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        if "STORYBOARD" == props.currentLayoutMode():
            props.setCurrentLayout("PREVIZ")
        else:
            props.setCurrentLayout("STORYBOARD")

        return {"FINISHED"}


class UAS_ShotManager_OT_StbFrameDrawing(Operator):
    bl_idname = "uas_shot_manager.stb_frame_drawing"
    bl_label = "Ubisoft Shot Mng - Toggle Storyboard Frame Draw Mode"
    bl_description = "Enable / disable the Storyboard Frame Draw Mode"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        if props.getEditedGPShot() is not None:
            utils_greasepencil.switchToObjectMode()
        else:
            currentShotInd = props.getCurrentShotIndex()
            if -1 != currentShotInd and props.isContinuousGPEditingModeActive():
                # context.window_manager.UAS_shot_manager_shots_play_mode = (
                #     not context.window_manager.UAS_shot_manager_shots_play_mode
                # )
                bpy.ops.uas_shot_manager.greasepencil_select_and_draw(
                    action="SELECT_AND_DRAW", index=currentShotInd, toggleDrawEditing=True, mode="DRAW"
                )

        return {"FINISHED"}


###################
# Warning buttons
###################


class UAS_ShotManager_OT_TurnOffBurnIntoImage(Operator):
    bl_idname = "uas_shot_manager.turn_off_burn_into_image"
    bl_label = "Disable Metadata"
    bl_description = (
        "Turn off the use of Burn Into Image in the scene to prevent metadata" "\nto be written on output images"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.use_stamp = False
        return {"FINISHED"}


class UAS_ShotManager_OT_TurnOffPixelAspect(Operator):
    bl_idname = "uas_shot_manager.turn_off_pixel_aspect"
    bl_label = "Reset Pixel Aspect"
    bl_description = "Reset the render pixel aspects X and Y to 1.0"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.render.pixel_aspect_x = 1.0
        context.scene.render.pixel_aspect_y = 1.0
        return {"FINISHED"}


class UAS_ShotManager_OT_SetFpsAsProjectFps(Operator):
    bl_idname = "uas_shot_manager.set_render_fps_as_project_fps"
    bl_label = "Reset Fps"
    bl_description = "Change the scene render framerate to match the project settings framerate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = config.getAddonProps(bpy.context.scene)
        if props.use_project_settings:
            utils.setSceneFps(context.scene, props.project_fps)
        return {"FINISHED"}


class UAS_ShotManager_OT_SetRenderResAsProjectRes(Operator):
    bl_idname = "uas_shot_manager.set_render_res_as_project_res"
    bl_label = "Reset Render Resolution"
    bl_description = "Change the scene render resolution to match the project settings resolution"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = config.getAddonProps(bpy.context.scene)
        if props.use_project_settings:
            context.scene.render.resolution_x = props.project_resolution_x
            context.scene.render.resolution_y = props.project_resolution_y
        return {"FINISHED"}


###################
# Camera binding
###################


class UAS_ShotManager_OT_ClearMarkersFromCameraBinding(Operator):
    bl_idname = "uas_shot_manager.clear_markers_from_camera_binding"
    bl_label = "Clear Camera Binding"
    bl_description = "Remove the camera binding from the markers used in the timeline.\nMarkers are not deleted"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        clearMarkersFromCameraBinding(context.scene)
        return {"FINISHED"}


class UAS_ShotManager_OT_ConvertMarkersFromCamBindingToShots(Operator):
    bl_idname = "uas_shot_manager.convert_markers_from_cam_binding_to_shots"
    bl_label = "Convert Camera Binding to Shots"
    bl_description = (
        "Convert the camera binding used by markers to shots and remove their binding.\nMarkers are not deleted"
    )
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        convertMarkersFromCameraBindingToShots(context.scene)
        clearMarkersFromCameraBinding(context.scene)
        return {"FINISHED"}


class UAS_ShotManager_OT_SetProjectSequenceName(Operator):
    bl_idname = "uas_shot_manager.set_project_sequence_name"
    bl_label = "Project Sequence Name"
    bl_description = "Set the name of the sequence when project settings are used"
    bl_options = {"REGISTER", "UNDO"}

    naming_project_index: IntProperty(name="Project or Act Index", min=0, default=1)
    naming_sequence_index: IntProperty(name="Sequence Index", min=0, step=10, default=10)

    # naming_project_format: StringProperty(default="01")
    # naming_sequence_format: StringProperty(default="001")

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        # numHashes = len([n for n in props.project_naming_project_format if n == "#"])
        # if "" != props.project_naming_project_format or 0 < numHashes:

        if -1 != props.project_naming_project_index:
            self.naming_project_index = props.project_naming_project_index

        if -1 != props.project_naming_sequence_index:
            self.naming_sequence_index = props.project_naming_sequence_index

        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        layout = self.layout
        box = layout.box()

        col = box.column(align=False)
        col.use_property_split = True

        # seqNameTemplate = f"{props.project_naming_project_format}{props.project_naming_separator_char}{props.project_naming_sequence_format}"
        seqNameTemplate = props.getProjectOutputMediaName(projInd=None, seqInd=None)
        namingRow = col.row(align=True)
        namingRow.label(text="Sequence Template from Project Settings:")
        namingRow.label(text=seqNameTemplate)

        # namingRow = col.row(align=True)
        # namingRow.alignment = "CENTER"
        # namingRow.scale_x = 0.5

        # namingRowLeft = namingRow.row(align=True)
        # namingRowLeft.alignment = "RIGHT"
        # namingRowLeft.scale_x = 2.0
        # namingRowLeft.label(text="Actt")
        # namingRowLeft.prop(self, "naming_project_format", text="")
        # namingRowLeft.separator(factor=1.0)

        # namingRowRight = namingRow.row(align=True)
        # namingRowRight.alignment = "LEFT"
        # namingRowRight.scale_x = 2.0
        # namingRowRight.label(text="_Seqq")
        # namingRowRight.prop(self, "naming_sequence_format", text="")

        numHashes = len([n for n in props.project_naming_project_format if n == "#"])
        if "" != props.project_naming_project_format or 0 < numHashes:
            row = col.row(align=True)
            row.prop(self, "naming_project_index")

        row = col.row(align=True)
        row.prop(self, "naming_sequence_index")

        col.separator(factor=0.5)

        if "" != props.project_naming_project_format or 0 < numHashes:
            seqName = props.getProjectOutputMediaName(
                projInd=self.naming_project_index, seqInd=self.naming_sequence_index
            )
        else:
            seqName = props.getProjectOutputMediaName(seqInd=self.naming_sequence_index)

        namingRow = col.row(align=True)
        namingRow.label(text="Resulting Sequence Name:")
        namingRow.label(text=seqName)

        box.separator(factor=0.5)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        props.project_naming_project_index = self.naming_project_index
        props.project_naming_sequence_index = self.naming_sequence_index

        # update main ui
        prefs.projectSeqName = props.getSequenceName("FULL")

        return {"INTERFACE"}


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
        props = config.getAddonProps(scene)
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


class UAS_ShotManager_OT_RedrawUI(Operator):
    bl_idname = "uas_shot_manager.redrawui"
    bl_label = "Redraw ui"
    bl_description = "-"
    bl_options = {"INTERNAL"}

    def execute(self, context):

        # bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

        # redraw all
        # for area in context.screen.areas:
        #     area.tag_redraw()
        # # context.scene.frame_current = context.scene.frame_current

        config.gRedrawShotStack = True

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_ShotsPlayMode,
    UAS_ShotManager_OT_DisplayDisabledShotsInOverlays,
    UAS_ShotManager_OT_DisplayOverlayTools,
    UAS_ShotManager_OT_ChangeLayout,
    UAS_ShotManager_OT_StbFrameDrawing,
    UAS_ShotManager_OT_TurnOffBurnIntoImage,
    UAS_ShotManager_OT_TurnOffPixelAspect,
    UAS_ShotManager_OT_SetFpsAsProjectFps,
    UAS_ShotManager_OT_SetRenderResAsProjectRes,
    UAS_ShotManager_OT_ClearMarkersFromCameraBinding,
    UAS_ShotManager_OT_ConvertMarkersFromCamBindingToShots,
    UAS_ShotManager_OT_SetProjectSequenceName,
    UAS_ShotManager_OT_GoToVideoShotManager,
    UAS_ShotManager_OT_FileInfo,
    UAS_ShotManager_OT_EnableDebug,
    UAS_ShotManager_OT_RedrawUI,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
