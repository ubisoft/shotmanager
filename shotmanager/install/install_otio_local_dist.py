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
Install OTIO from the distribution provided with Shot Manager
"""

import bpy

import os
import subprocess
import platform
import sys

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def install_otio_local_dist():
    """Return True if OTIO is already installed or if the installation of the local distribution succeeded"""

    # for versions of Blender after 2.93:
    # if (2, 93, 0) <= bpy.app.version:

    if (3, 1, 0) <= bpy.app.version and platform.system() == "Windows":
        # forces an exception so that this package (otio) cannot be imported and then the function
        # used everywhere in ShotManager to see if the atio package is available fails
        # (namely module_can_be_imported("shotmanager.otio"))
        #
        # import opentimelineio

        # if not platform.system() == "Windows":
        #     import opentimelineio
        # else:

        try:
            import opentimelineio

            _logger.debug_ext(f"OTIO already installed: {opentimelineio.__version___}", col="GREEN")

            return True

        except ModuleNotFoundError:
            # we install the provided wheel

            pyExeFile = sys.executable
            # localPyDir = str(Path(pyExeFile).parent) + "\\lib\\site-packages\\"

            try:
                print(
                    "Installing provided distribution of OpenTimelineIO 0.15 for Python 3.10 for Ubisoft Shot Manager..."
                )
                package_path = os.path.join(
                    os.path.dirname(__file__), "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-win_amd64.whl"
                )
                subprocess.run(
                    [
                        pyExeFile,
                        "-m",
                        "pip",
                        "install",
                        package_path,
                    ]
                )
                import opentimelineio

                print("Provided distribution of OpenTimelineIO 0.15 for Python 3.10 installed successfully")

                return True

            except ModuleNotFoundError:
                _logger.error("*** Error - Installation of OpenTimelineIO from provided distribution failed ***")
                return False
