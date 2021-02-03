import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty

from shotmanager.config import config
from shotmanager.utils import utils

import logging

_logger = logging.getLogger(__name__)


class UAS_ShotManager_EnableDisableSoundBG(Operator):
    bl_idname = "uas_shot_manager.enabledisablesoundbg"
    bl_label = "Enable / Disable Camera Backgrounds"
    bl_description = "Alternatively enable or disable the background image of the cameras used by the shots"
    bl_options = {"INTERNAL", "UNDO"}

    # can be Image, Sound, All
    mode: StringProperty(default="All")

    def invoke(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences

        if "All" == self.mode or "Sound" == self.mode:
            bpy.ops.uas_shots_settings.use_background_sound(useBackgroundSound=prefs.toggleCamsSoundBG)
            prefs.toggleCamsSoundBG = not prefs.toggleCamsSoundBG

        return {"FINISHED"}


classes = (UAS_ShotManager_EnableDisableSoundBG,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

