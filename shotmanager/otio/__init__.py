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
OTIO package and everything related to it
"""

import os
import importlib
import subprocess
import platform

import bpy

# from . import otio_wrapper
# from shotmanager.config import config

import sys
from pathlib import Path

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


# def importOpenTimelineIOLib():
# if (2, 93, 0) < bpy.app.version:
#     return False

# for versions of Blender after 2.93:
if (2, 93, 0) <= bpy.app.version:
    # forces an exception so that this package (otio) cannot be imported and then the function
    # used everywhere in ShotManager to see if the atio package is available fails
    # (namely module_can_be_imported("shotmanager.otio"))
    #
    # import opentimelineio

    if not platform.system() == "Windows":
        import opentimelineio
    else:

        try:
            import opentimelineio

            _logger.debug_ext("OTIO correctly imported", col="GREEN")

        except ModuleNotFoundError:
            _logger.error("*** Error - OpenTimelineIO import failed - Installing provided version")

            # # we use the provided wheel
            # pyExeFile = sys.executable
            # localPyDir = str(Path(pyExeFile).parent) + "\\lib\\site-packages\\"

            # try:
            #     print("  installing OpenTimelineIO 0.13 for Python 3.9 for Ubisoft Shot Manager...")
            #     subprocess.run(
            #         [
            #             pyExeFile,
            #             "-m",
            #             "pip",
            #             "install",
            #             os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.13.0_Ubi0.2-py3-none-any.whl"),
            #         ]
            #     )
            #     import opentimelineio as opentimelineio
            # except ModuleNotFoundError:
            #     _logger.error("*** Error - OpenTimelineIO instal from provided version 0.013 failed")


# for versions of Blender before 2.93:
else:
    print("OpentimelineIO not available for Blender before 2.93")

    # pyExeFile = sys.executable
    # localPyDir = str(Path(pyExeFile).parent) + "\\lib\\site-packages\\"

    # try:
    #     import opentimelineio

    #     # wkip type de comparaison qui ne marche pas tout le temps!!! ex: "2.12.1"<"11.12.1"  is False !!!
    #     if opentimelineio.__version__ < "0.12.1" and platform.system() == "Windows":
    #         print("Upgrading OpentimelineIO to 0.12.1")
    #         subprocess.run(
    #             [
    #                 pyExeFile,
    #                 "-m",
    #                 "pip",
    #                 "install",
    #                 os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
    #             ]
    #         )
    #         importlib.reload(opentimelineio)  # Need to be tested.
    # except ModuleNotFoundError:
    #     _logger.error("*** Error - OpenTimelineIO import failed - using provided version")
    #     if platform.system() == "Windows":
    #         _logger.error("Plateform: Windows")
    #         try:
    #             subprocess.run(
    #                 [
    #                     pyExeFile,
    #                     "-m",
    #                     "pip",
    #                     "install",
    #                     os.path.join(os.path.dirname(__file__), "OpenTimelineIO-0.12.1-cp37-cp37m-win_amd64.whl"),
    #                 ]
    #             )
    #             import opentimelineio as opentimelineio
    #         except ModuleNotFoundError:
    #             _logger.error("*** Error - OpenTimelineIO instal from provided version failed")
    #     else:
    #         subprocess.run([pyExeFile, "-m", "pip", "install", "opentimelineio"])
    #         import opentimelineio as opentimelineio
    # import opentimelineio as opentimelineio

# try:
#     import opentimelineio as opentimelineio

#     res = True
# except Exception:
#     res = False
# return res


def register():
    from . import blender

    # custom version used to track this package if used in several add-ons
    package_version = "1.0.1"
    package_last_update = "2022/01/19"

    try:
        import opentimelineio as otio

        otioVersion = otio.__version__
        otioVersionStr = f" - OpenTimelineIO V. {otioVersion}"
    except Exception:
        otioVersionStr = " - OpenTimelineIO not available"

    _logger.debug_ext(
        f"       - Registering OTIO Package (V. {package_version}, {package_last_update})" + otioVersionStr, form="REG"
    )

    blender.register()


def unregister():
    from . import blender

    _logger.debug_ext("       - Unregistering OTIO Package", form="UNREG")

    blender.unregister()
