import os
import json

import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty, BoolProperty, IntProperty

from shotmanager.config import config
from shotmanager.utils import utils

import logging

_logger = logging.getLogger(__name__)


class UAS_ShotManager_OpenDialogForCamBG(Operator):
    bl_idname = "uas_shot_manager.opendialog_for_cam_bg"
    bl_label = "Add Camera Background"
    bl_description = "Add an image or video to the shot to use it as camera background"
    bl_options = {"INTERNAL", "UNDO"}

    filepath: StringProperty(name="Video File", subtype="FILE_PATH")

    filter_glob: StringProperty(default="*.mov;*.mp4", options={"HIDDEN"})

    importSoundFromVideo: BoolProperty(name="Import Sound", default=True)

    def invoke(self, context, event):  # See comments at end  [1]
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props

        wm.invoke_props_dialog(self, width=500)

        return {"RUNNING_MODAL"}

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        layout = self.layout
        box = layout.box()

        # box.label(text="otot")
        box.prop(self, "filepath")
        box.prop(self, "importSoundFromVideo")

    def execute(self, context):
        """Use the selected file as a stamped logo"""
        #  filename, extension = os.path.splitext(self.filepath)
        #   print('Selected file:', self.filepath)
        #   print('File name:', filename)
        #   print('File extension:', extension)
        props = context.scene.UAS_shot_manager_props
        shot = props.getCurrentShot()

        shot.removeBGImages()

        shot.addBGImages(
            str(self.filepath), frame_start=0, alpha=props.shotsGlobalSettings.backgroundAlpha, addSoundFromVideo=True
        )
        # # start frame of the background video is not set here since it will be linked to the shot start frame
        # utils.add_background_video_to_cam(
        #     shot.camera.data, str(self.filepath), 0, alpha=props.shotsGlobalSettings.backgroundAlpha
        # )

        # if self.importSoundFromVideo:
        #     props.addBGSoundToShot(self.filepath, shot)

        # refresh properties and their update function
        shot.bgImages_linkToShotStart = shot.bgImages_linkToShotStart
        shot.bgImages_offset = shot.bgImages_offset

        return {"FINISHED"}


# This operator requires   from bpy_extras.io_utils import ImportHelper
# See https://sinestesia.co/blog/tutorials/using-blenders-filebrowser-with-python/
class UAS_ShotManager_OpenFileBrowserForCamBG(Operator):  # from bpy_extras.io_utils import ImportHelper
    bl_idname = "uas_shot_manager.openfilebrowser_for_cam_bg"
    bl_label = "Camera Background"
    bl_description = "Open a file browser to define the image or video to use as camera background"
    bl_options = {"INTERNAL", "UNDO"}

    pathProp: StringProperty()

    filepath: StringProperty(subtype="FILE_PATH")

    filter_glob: StringProperty(default="*.mov;*.mp4", options={"HIDDEN"})

    def invoke(self, context, event):  # See comments at end  [1]

        context.window_manager.fileselect_add(self)

        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Open image or video file """
        filename, extension = os.path.splitext(self.filepath)
        print("ex Selected file:", self.filepath)
        # print("ex File name:", filename)
        # print("ex File extension:", extension)

        bpy.ops.uas_shot_manager.opendialog_for_cam_bg("INVOKE_DEFAULT", filepath=self.filepath)

        return {"FINISHED"}


class UAS_ShotManager_RemoveBGImages(Operator):
    bl_idname = "uas_shot_manager.remove_bg_images"
    bl_label = "Remove BG Images"
    bl_description = "Remove the camera background images of the specified shots"
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shotList = []

        print("Remove BG images: shotIndex: ", self.shotIndex)
        if 0 > self.shotIndex:
            take = context.scene.UAS_shot_manager_props.getCurrentTake()
            shotList = take.getShotList(ignoreDisabled=props.shotsGlobalSettings.alsoApplyToDisabledShots)
        else:
            shot = props.getShotByIndex(self.shotIndex)
            if shot is not None:
                shotList.append(shot)

        for shot in shotList:
            shot.removeBGImages()
            # #    print("   shot name: ", shot.name)
            # if shot.camera is not None and len(shot.camera.data.background_images):
            #     # if shot.camera.data.background_images[0].clip is not None:
            #     shot.camera.data.show_background_images = False
            #     # shot.camera.data.background_images[0].clip = None
            #     shot.camera.data.background_images.clear()
            #     # shot.camera.data.background_images[0].clip.filepath = ""
        return {"FINISHED"}


class UAS_ShotManager_EnableDisableCamsBG(Operator):
    bl_idname = "uas_shot_manager.enabledisablecamsbg"
    bl_label = "Enable / Disable Camera Backgrounds"
    bl_description = "Alternatively enable or disable the background image of the cameras used by the shots"
    bl_options = {"INTERNAL", "UNDO"}

    # can be Image, Sound, All
    mode: StringProperty(default="All")

    def invoke(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences

        if "All" == self.mode or "Image" == self.mode:
            bpy.ops.uas_shots_settings.use_background(useBackground=prefs.toggleCamsBG)
            prefs.toggleCamsBG = not prefs.toggleCamsBG
        if "All" == self.mode or "Sound" == self.mode:
            bpy.ops.uas_shots_settings.use_background_sound(useBackgroundSound=prefs.toggleCamsSoundBG)
            prefs.toggleCamsSoundBG = not prefs.toggleCamsSoundBG

        return {"FINISHED"}


class UAS_ShotManager_CamsBGItem(Operator):
    bl_idname = "uas_shot_manager.cambgitem"
    bl_label = " "
    bl_description = "Select shot"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty(default=0)

    def invoke(self, context, event):
        context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)

        return {"FINISHED"}


classes = (
    UAS_ShotManager_OpenDialogForCamBG,
    UAS_ShotManager_OpenFileBrowserForCamBG,
    UAS_ShotManager_RemoveBGImages,
    UAS_ShotManager_EnableDisableCamsBG,
    UAS_ShotManager_CamsBGItem,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

