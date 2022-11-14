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
Key mappings for all the operators of the add-on

Eg here: https://blender.stackexchange.com/questions/196483/create-keyboard-shortcut-for-an-operator-using-python
"""

from . import general_keymaps
from . import playbar_wrappers_operators
from . import playbar_keymaps
from . import storyboard_keymaps

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Keymaps Package", form="REG")
    playbar_wrappers_operators.register()
    general_keymaps.registerKeymaps()
    playbar_keymaps.registerKeymaps()
    storyboard_keymaps.registerKeymaps()


def unregister():
    _logger.debug_ext("       - Unregistering Keymaps Package", form="UNREG")

    # Remove the hotkeys
    # for km, kmi in config.gAddonKeymaps:
    #     km.keymap_items.remove(kmi)
    # config.gAddonKeymaps.clear()
    # general_wrappers_operators.unregister()

    storyboard_keymaps.unregisterKeymaps()
    playbar_keymaps.unregisterKeymaps()
    general_keymaps.unregisterKeymaps()
    playbar_wrappers_operators.unregister()
