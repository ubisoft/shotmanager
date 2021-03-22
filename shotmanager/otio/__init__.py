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

