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
Display camera opengl hud in the viewports
"""
import bpy

from . import camera_hud
from . import camera_hud_operators

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Viewport Camera HUD Package", form="REG")

    camera_hud.register()
    camera_hud_operators.register()


def unregister():
    _logger.debug_ext("       - Unregistering Viewport Camera HUD Package", form="UNREG")

    camera_hud_operators.unregister()
    try:
        camera_hud.unregister()
    except Exception:
        print("Paf in Unregister viewport_camera_hud")
