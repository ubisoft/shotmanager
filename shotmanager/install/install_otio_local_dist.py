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

    try:
        # forces an exception so that this package (otio) cannot be imported and then the function
        # used everywhere in ShotManager to see if the atio package is available fails
        # (namely module_can_be_imported("shotmanager.otio"))
        import opentimelineio

        _logger.debug_ext(f"OTIO already installed: {opentimelineio.__version__}", col="GREEN")

        return True

    except ModuleNotFoundError:
        # for versions of Blender equal to or after 3.1 we install the provided wheel
        # for previous versions we follow the online check of the appropriate wheel (cf function install_dependencies()
        # alled in .init)
        if (3, 1, 0) <= bpy.app.version:
            pyExeFile = sys.executable
            # localPyDir = str(Path(pyExeFile).parent) + "\\lib\\site-packages\\"

            try:
                _logger.info_ext(
                    "Installing provided distribution of OpenTimelineIO 0.15 for Python 3.10 for Ubisoft Shot Manager...",
                    col="GREEN",
                )

                is_64bits = sys.maxsize > 2**32
                if "Windows" == platform.system():
                    if is_64bits:
                        package_path = os.path.join(
                            os.path.dirname(__file__), "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-win_amd64.whl"
                        )
                    else:
                        package_path = os.path.join(
                            os.path.dirname(__file__), "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-win32.whl"
                        )

                elif "Darwin" == platform.system():
                    package_path = os.path.join(
                        os.path.dirname(__file__),
                        "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-macosx_10_9_x86_64.whl",
                    )

                elif "Linux" == platform.system():
                    if is_64bits:
                        package_path = os.path.join(
                            os.path.dirname(__file__),
                            "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-manylinux_2_12_x86_64.manylinux2010_x86_64.whl",
                        )
                    else:
                        package_path = os.path.join(
                            os.path.dirname(__file__),
                            "..\\distr\\OpenTimelineIO-0.15.0.dev1-cp310-cp310-manylinux_2_12_i686.manylinux2010_i686.whl",
                        )

                subprocess.run(
                    [
                        pyExeFile,
                        "-m",
                        "pip",
                        "install",
                        # "--upgrade",
                        # "--force-reinstall",
                        package_path,
                    ]
                )
                import opentimelineio

                print("Provided distribution of OpenTimelineIO 0.15 for Python 3.10 installed successfully")

                return True

            except ModuleNotFoundError:
                _logger.error("*** Error - Installation of OpenTimelineIO from provided distribution failed ***")
                return False

    return False
