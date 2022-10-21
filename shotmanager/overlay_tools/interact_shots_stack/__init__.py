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
Interactive Shots Stack overlay tool
"""

import bpy
from . import shots_stack_operators

# from . import shots_stack_widgets
from . import shots_stack_prefs
from . import shots_stack_toolbar
from . import shots_stack

# from . import shots_stack_bgl

# debug
from shotmanager.gpu.gpu_2d.samples import dopesheet_gpu_sample

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Interactive Shots Stack Package", form="REG")

    # prefs = config.getAddonPrefs()
    prefs = config.getAddonPrefs()

    shots_stack_operators.register()
    shots_stack_prefs.register()
    shots_stack_toolbar.register()
    # shots_stack_widgets.register()
    shots_stack.register()
    # shots_stack_bgl.register()

    dopesheet_gpu_sample.register()

    # # # def _update_UAS_shot_manager__useInteracShotsStack(self, context):
    # # #     # toggle_overlay_tools_display(context)
    # # #     print(f"\nFrom Update fct: Toggle Interactive Shots Stack: {self.UAS_shot_manager__useInteracShotsStack}")
    # # #     from shotmanager.overlay_tools.interact_shots_stack.shots_stack_toolbar import display_state_changed_intShStack

    # # #     display_state_changed_intShStack(context)

    # # # bpy.types.WindowManager.UAS_shot_manager__useInteracShotsStack = BoolProperty(
    # # #     name="Use Sequence Timeline",
    # # #     description="Toggle the use of Shot Manager Sequence Timeline",
    # # #     update=_update_UAS_shot_manager__useInteracShotsStack,
    # # #     default=True,
    # # # )

    # shots_stack_toolbar.register()
    shots_stack_toolbar.display_shots_stack_toolbar_in_editor(prefs.display_shtStack_toolbar)


def unregister():
    _logger.debug_ext("       - Unregistering Interactive Shots Stack Package", form="UNREG")

    dopesheet_gpu_sample.unregister()

    # shots_stack_toolbar.unregister()
    shots_stack_toolbar.display_shots_stack_toolbar_in_editor(False)

    # shots_stack_bgl.unregister()
    shots_stack.unregister()
    # shots_stack_widgets.unregister()
    shots_stack_toolbar.unregister()
    shots_stack_prefs.unregister()
    shots_stack_operators.unregister()


### del bpy.types.WindowManager.UAS_shot_manager__useInteracShotsStack
