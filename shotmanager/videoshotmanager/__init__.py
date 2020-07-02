import os
import importlib
from pathlib import Path
import subprocess
import platform

import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

from .properties import vsm_props
from .operators import tracks

# from .ui.vsm_ui import UAS_PT_VideoShotManager
from .ui import vsm_ui


# classes = (
#     ,
# )


def register():

    print("\n         - Registering Video Shot Manager Package\n")

    # for cls in classes:
    #     bpy.utils.register_class(cls)

    vsm_props.register()
    tracks.register()
    vsm_ui.register()

    # declaration of properties that will not be saved in the scene

    # About button panel Quick Settings[ -----------------------------
    bpy.types.WindowManager.UAS_video_shot_manager_displayAbout = BoolProperty(
        name="About...", description="Display About Informations", default=False
    )


def unregister():
    vsm_ui.unregister()
    tracks.unregister()
    vsm_props.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_video_shot_manager_displayAbout
