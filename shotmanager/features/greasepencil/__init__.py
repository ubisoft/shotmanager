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
Grease Pencil
"""

from shotmanager.config import config

# from .greasepencil_props import UAS_ShotManager_RenderGlobalContext, UAS_ShotManager_RenderSettings
from . import greasepencil_props
from . import greasepencil_operators
from . import greasepencil_tools
from . import greasepencil_frame_template
from . import greasepencil_frame_panel

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


# _classes = (UAS_ShotManager_OT_AddGreasePencil,)


def register():
    _logger.debug_ext("       - Registering Grease Pencil Package", form="REG")

    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    greasepencil_props.register()
    greasepencil_operators.register()
    greasepencil_tools.register()
    greasepencil_frame_template.register()
    greasepencil_frame_panel.register()


def unregister():
    _logger.debug_ext("       - Unregistering Grease Pencil Package", form="UNREG")

    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    # greasepencil_toolbox_ui.unregister()
    greasepencil_frame_panel.unregister()
    greasepencil_frame_template.unregister()
    greasepencil_tools.unregister()
    greasepencil_operators.unregister()
    greasepencil_props.unregister()
