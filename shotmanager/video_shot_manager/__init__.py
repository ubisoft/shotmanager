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

icons_col = None

# classes = (UAS_PT_VideoShotManager,)


def register():
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    tracks.register()
    vsm_props.register()
    vsm_ui.register()

    # declaration of properties that will not be saved in the scene

    # About button panel Quick Settings[ -----------------------------
    bpy.types.WindowManager.UAS_video_shot_manager_displayAbout = BoolProperty(
        name="About...", description="Display About Informations", default=False
    )

    pcoll = bpy.utils.previews.new()
    print("pcoll: ", pcoll)
    my_icons_dir = os.path.join(os.path.dirname(__file__), "..\\icons")
    print("my_icons_dir: ", my_icons_dir)
    for png in Path(my_icons_dir).rglob("*.png"):
        pcoll.load(png.stem, str(png), "IMAGE")

    global icons_col
    icons_col = pcoll


def unregister():
    vsm_ui.unregister()
    vsm_props.unregister()
    tracks.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.UAS_video_shot_manager_displayAbout

    global icons_col
    if icons_col is not None:
        bpy.utils.previews.remove(icons_col)
    icons_col = None
