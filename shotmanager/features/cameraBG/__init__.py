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

import bpy

from shotmanager.config import config

# from .greasepencil_props import UAS_ShotManager_RenderGlobalContext, UAS_ShotManager_RenderSettings
from . import cameraBG_operators

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    if config.devDebug:
        print("       - Registering Camera Background Package")

    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    cameraBG_operators.register()
    # rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    cameraBG_operators.unregister()
