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
Storyboard frame grid
"""

from . import storyboard_frame_grid_props
from . import storyboard_frame_grid_operators

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


# _classes = (UAS_ShotManager_OT_AddGreasePencil,)


def register():
    _logger.debug_ext("       - Registering Feature: Storyboard Package", form="REG")

    # frame grid props has to be initialized early to be used in greasepencil_frame_template
    storyboard_frame_grid_props.register()
    storyboard_frame_grid_operators.register()


#  greasepencil_toolbox_ui.register()
# rendering_ui.register()    # done in shotmanager.__init__ in order to display the panel in the right order


def unregister():
    _logger.debug_ext("       - Unregistering Feature: Storyboard Package", form="UNREG")

    # rendering_ui.unregister()   # done in shotmanager.__init__ in order to display the panel in the right order
    # greasepencil_toolbox_ui.unregister()

    storyboard_frame_grid_operators.unregister()
    storyboard_frame_grid_props.unregister()
