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
Prefs dialog windows Init
"""


from . import about
from . import dialog_menu

# from . import general
from . import prefs_features
from . import prefs_overlay_tools
from . import prefs_project
from . import prefs_sequence
from . import prefs_shots_display
from . import prefs_tools
from . import prefs

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

# _classes = (UAS_ShotManager_OT_About,)


def register():
    _logger.debug_ext("       - Registering Prefs Package", form="REG")

    about.register()
    prefs_features.register()
    dialog_menu.register()
    #   general.register()
    prefs_overlay_tools.register()
    prefs_project.register()
    prefs_sequence.register()
    prefs_shots_display.register()
    prefs_tools.register()
    prefs.register()

    # for cls in _classes:
    #     bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering Prefs Package", form="UNREG")

    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    prefs.unregister()
    prefs_tools.unregister()
    prefs_shots_display.unregister()
    prefs_sequence.unregister()
    prefs_project.unregister()
    prefs_overlay_tools.unregister()
    #  general.unregister()
    dialog_menu.unregister()
    prefs_features.unregister()
    about.unregister()
