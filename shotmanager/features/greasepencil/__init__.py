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


from . import greasepencil_props
from . import greasepencil_operators

from . import greasepencil_frame_panel
from . import greasepencil_tools_props

# from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Feature: Grease Pencil Package", form="REG")

    greasepencil_props.register()
    greasepencil_operators.register()

    # done in shot manager init
    # greasepencil_toolspanel_ui.register()

    # greasepencil_frame_template.register()
    greasepencil_frame_panel.register()
    greasepencil_tools_props.register()


#  greasepencil_toolbox_ui.register()
# rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    _logger.debug_ext("       - Unregistering Feature: Grease Pencil Package", form="UNREG")

    greasepencil_tools_props.unregister()
    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    # greasepencil_toolbox_ui.unregister()
    greasepencil_frame_panel.unregister()
    #  greasepencil_frame_template.unregister()

    # done in shot manager init
    #  greasepencil_toolspanel_ui.unregister()

    greasepencil_operators.unregister()
    greasepencil_props.unregister()
