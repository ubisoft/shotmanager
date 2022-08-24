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
Rendering
"""

import bpy

from .rendering_settings_props import UAS_ShotManager_RenderSettings
from .rendering_global_props import UAS_ShotManager_RenderGlobalContext
from .rendering_prefs import UAS_ShotManager_Render_Prefs
from . import rendering_operators

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


_classes = (
    UAS_ShotManager_RenderGlobalContext,
    UAS_ShotManager_RenderSettings,
    UAS_ShotManager_Render_Prefs,
)


def register():
    _logger.debug_ext("       - Registering Rendering Package", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)

    rendering_operators.register()
    # rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    _logger.debug_ext("       - Unregistering Rendering Package", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    rendering_operators.unregister()
