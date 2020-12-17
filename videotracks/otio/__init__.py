import os
import importlib
import subprocess
import platform

import bpy


try:
    import opentimelineio

    # wkip type de comparaison qui ne marche pas tout le temps!!! ex: "2.12.1"<"11.12.1"  is False !!!
    if opentimelineio.__version__ < "0.12.1" and platform.system() == "Windows":
        print("Upgrading OpentimelineIO to 0.12.1")
        subprocess.run(
            [
                bpy.app.binary_path_python,
                "-m",
                "pip",
                "install",
                os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
            ]
        )
        importlib.reload(opentimelineio)  # Need to be tested.
except ModuleNotFoundError:
    if platform.system() == platform.system() == "Windows":
        subprocess.run(
            [
                bpy.app.binary_path_python,
                "-m",
                "pip",
                "install",
                os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
            ]
        )
    else:
        subprocess.run([bpy.app.binary_path_python, "-m", "pip", "install", "opentimelineio"])
    import opentimelineio as opentimelineio

from . import operators

from . import otio_wrapper

from pathlib import Path


# classes = (
#     ,
# )


def register():
    print("       - Registering OTIO Package")
    # for cls in classes:
    #     bpy.utils.register_class(cls)

    operators.register()


def unregister():
    operators.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

