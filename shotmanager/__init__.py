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
Shot Manager initialization
"""

import bpy

from bpy.props import BoolProperty, IntProperty, FloatProperty

from .config import config

from . import handlers
from .handlers.sm_overlay_tools_handlers import install_handler_for_shot, toggle_overlay_tools_display
from .overlay_tools.workspace_info.workspace_info import toggle_workspace_info_display

from .features import cameraBG
from .features import soundBG
from .features import greasepencil

from .operators import takes
from .operators import shots
from .operators import shots_global_settings

from .operators import general
from .operators import playbar
from .operators import shots_toolbar

from .properties import props

from . import prefs

from . import retimer
from .retimer import retimer_ui


from . import rendering
from .rendering import rendering_ui

from .scripts import precut_tools

from .ui import sm_ui

from .utils import utils
from .utils import utils_render
from .utils import utils_operators
from .tools import frame_range
from .utils.utils_os import module_can_be_imported

from .scripts import rrs

from . import keymaps

from . import debug as sm_debug

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


bl_info = {
    "name": "Shot Manager",
    "author": "Ubisoft - Julien Blervaque (aka Werwack), Romain Carriquiry Borchiari",
    "description": "Easily manage shots and cameras in the 3D View and see the resulting edit in real-time",
    "blender": (2, 93, 0),
    "version": (1, 7, 15),
    "location": "View3D > Shot Manager",
    "doc_url": "https://ubisoft-shotmanager.readthedocs.io",
    # "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__


def register():

    config.initGlobalVariables()

    from .utils import utils_ui

    utils_ui.register()

    sm_logging.initialize()
    if config.devDebug:
        _logger.setLevel("DEBUG")  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    logger_level = f"Logger level: {sm_logging.getLevelName()}"
    versionTupple = utils.display_addon_registered_version("Shot Manager", more_info=logger_level)

    from .overlay_tools.workspace_info import workspace_info

    workspace_info.register()

    # install dependencies and required Python libraries
    ###################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there

    from .install.install_dependencies import install_dependencies

    installErrorCode = install_dependencies([("opentimelineio", "opentimelineio")], retries=1, timeout=20)
    # installErrorCode = 0
    if 0 != installErrorCode:
        # utils_handlers.removeAllHandlerOccurences(shotMngHandler_frame_change_pre_jumpToShot, handlerCateg=bpy.app.handlers.frame_change_pre)
        # return installErrorCode
        print("  *** OpenTimelineIO install failed for Ubisoft Shot Manager ***")
        pass
    else:
        print("  OpenTimelineIO correctly installed for Ubisoft Shot Manager")

        # otio
        try:
            from . import otio

            otio.register()

            # from shotmanager.otio import importOpenTimelineIOLib

            # if importOpenTimelineIOLib():
            #     otio.register()
            # else:
            #     print("       *** OTIO Package import failed ***")
        except ModuleNotFoundError:
            print("       *** OTIO Package import failed ****")

    # if install went right then register other packages
    ###################

    # debug tools
    sm_debug.register()

    from .addon_prefs import addon_prefs
    from .utils import utils_vse_render
    from .overlay_tools import sequence_timeline
    from .overlay_tools import interact_shots_stack
    from .overlay_tools import viewport_camera_hud

    ###################
    # update data
    ###################

    # bpy.context.window_manager.UAS_shot_manager_version
    bpy.types.WindowManager.UAS_shot_manager_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    addon_prefs.register()
    utils_operators.register()

    # operators
    # markers_nav_bar_addon_prefs.register()
    cameraBG.register()
    soundBG.register()
    greasepencil.register()
    frame_range.register()
    rendering.register()
    takes.register()
    shots.register()
    shots_global_settings.register()
    precut_tools.register()
    playbar.register()
    retimer.register()
    props.register()
    shots_toolbar.register()

    # ui
    sm_ui.register()
    rrs.register()
    retimer_ui.register()
    rendering_ui.register()

    # # otio
    # try:
    #     from . import otio

    #     otio.register()

    #     # from shotmanager.otio import importOpenTimelineIOLib

    #     # if importOpenTimelineIOLib():
    #     #     otio.register()
    #     # else:
    #     #     print("       *** OTIO Package import failed ***")
    # except ModuleNotFoundError:
    #     print("       *** OTIO Package import failed ****")

    utils_vse_render.register()
    # try:
    #     utils_vse_render.register()
    # except Exception:
    #     print("*** Paf for utils_vse_render.register")

    utils_render.register()
    general.register()
    interact_shots_stack.register()
    sequence_timeline.register()
    viewport_camera_hud.register()
    prefs.register()
    keymaps.register()
    handlers.register()

    # rrs specific
    # rrs_vsm_tools.register()

    # declaration of properties that will not be saved in the scene:
    ####################

    # call in the code by context.window_manager.UAS_shot_manager_shots_play_mode etc

    def _update_UAS_shot_manager_shots_play_mode(self, context):
        # if self.UAS_shot_manager_shots_play_mode:
        install_handler_for_shot(self, context)

    bpy.types.WindowManager.UAS_shot_manager_shots_play_mode = BoolProperty(
        name="Enable Shot Play Mode",
        description="Override the standard animation Play mode to play the enabled shots" "\nin the specified order",
        update=_update_UAS_shot_manager_shots_play_mode,
        default=False,
    )

    def _update_UAS_shot_manager_display_overlay_tool(self, context):
        toggle_overlay_tools_display(context)

    bpy.types.WindowManager.UAS_shot_manager_display_overlay_tools = BoolProperty(
        name="Show Overlay Tools",
        description="Toggle the display of the overlay tools in the opened editors:"
        "\n  - Sequence Timeline in the 3D viewport"
        "\n  - Interactive Shots Stack in the Timeline editor",
        update=_update_UAS_shot_manager_display_overlay_tool,
        default=False,
    )

    def _update_UAS_shot_manager_identify_3dViews(self, context):
        toggle_workspace_info_display(context)

    bpy.types.WindowManager.UAS_shot_manager_identify_3dViews = BoolProperty(
        name="Identify 3D Viewports",
        description="Display an index on each 3D viewport to clearly identify them."
        "\nThe Shot Manager target 3D viewport will appear in green",
        update=_update_UAS_shot_manager_identify_3dViews,
        default=False,
    )

    def _update_UAS_shot_manager_identify_dopesheets(self, context):
        toggle_workspace_info_display(context)

    bpy.types.WindowManager.UAS_shot_manager_identify_dopesheets = BoolProperty(
        name="Identify Dopesheet Editors",
        description="Display an index on each dopesheet editor to clearly identify them."
        "\nThe Shot Manager target dopesheet will appear in green",
        update=_update_UAS_shot_manager_identify_dopesheets,
        default=False,
    )

    bpy.types.WindowManager.UAS_shot_manager_toggle_shots_stack_interaction = BoolProperty(
        name="Enable Shots Manipulation",
        description="Enable the interactions with the shots in the Interactive Shots Stack,"
        "\nin the Timeline editor."
        "\nNote: When the manipulation mode is enabled it may become difficult to select underlying keyframes",
        default=True,
    )

    bpy.types.WindowManager.UAS_shot_manager_use_best_perfs = BoolProperty(
        name="Best Play Performance",
        description="Turn off overlay tools such as the viewport Sequence Timeline"
        "\nor the Interactive Shots Stack during animation play to improve performances."
        "\nConfigure the disabled tools in the Overlay Tools Settings panel",
        default=True,
    )

    bpy.types.WindowManager.UAS_shot_manager_progressbar = FloatProperty(
        name="Progress Bbar",
        description="Value of the progress bar",
        subtype="PERCENTAGE",
        min=0,
        max=100,
        precision=0,
        default=0,
        options=set(),
    )

    if config.devDebug:
        print(f"\n ------ Shot Manager debug: {config.devDebug} ------- ")

    print("")


def unregister():
    print("\n*** --- Unregistering Shot Manager Add-on --- ***")
    from .utils import utils_ui
    from .overlay_tools import sequence_timeline
    from .overlay_tools import interact_shots_stack
    from .overlay_tools import viewport_camera_hud

    # Unregister packages that may have been registered if the install had errors
    ###################
    from .install.install_dependencies import unregister_from_failed_install

    bpy.context.window_manager.UAS_shot_manager_display_overlay_tools = False
    bpy.context.window_manager.UAS_shot_manager_shots_play_mode = False

    # bpy.utils.unregister_class(cls)
    #    bpy.ops.uas_shot_manager.sequence_timeline.cancel(bpy.context)

    #  bpy.context.window_manager.event_timer_remove(bpy.ops.uas_shot_manager.sequence_timeline.draw_event)
    # bpy.types.SpaceView3D.draw_handler_remove(bpy.ops.uas_shot_manager.sequence_timeline.draw_handle, "WINDOW")

    if unregister_from_failed_install():
        utils_ui.unregister()
        config.releaseGlobalVariables()
        return ()

    # Unregister packages that were registered if the install went right
    ###################

    from .addon_prefs import addon_prefs
    from .utils import utils_vse_render

    # ui
    handlers.unregister()
    keymaps.unregister()
    prefs.unregister()
    viewport_camera_hud.unregister()
    sequence_timeline.unregister()
    interact_shots_stack.unregister()
    general.unregister()
    utils_render.unregister()
    utils_vse_render.unregister()
    # try:
    #     utils_vse_render.unregister()
    # except Exception:
    #     print("*** Paf for utils_vse_render.unregister")

    rendering_ui.unregister()
    retimer_ui.unregister()
    rrs.unregister()
    sm_ui.unregister()

    # operators
    rendering.unregister()
    shots_toolbar.unregister()
    props.unregister()
    retimer.unregister()
    playbar.unregister()
    precut_tools.unregister()
    shots_global_settings.unregister()
    shots.unregister()
    takes.unregister()
    utils_operators.unregister()
    frame_range.unregister()
    greasepencil.unregister()
    soundBG.unregister()
    cameraBG.unregister()

    addon_prefs.unregister()

    del bpy.types.WindowManager.UAS_shot_manager_shots_play_mode
    del bpy.types.WindowManager.UAS_shot_manager_display_overlay_tools

    #   del bpy.types.WindowManager.UAS_shot_manager_isInitialized
    del bpy.types.WindowManager.UAS_shot_manager_version

    # debug tools
    # if config.devDebug:
    try:
        sm_debug.unregister()
    except Exception as e:
        print(f"Trying to unregister sm-debug: {e}")

    # if module_can_be_imported("shotmanager.otio"):
    if module_can_be_imported("opentimelineio"):
        from . import otio

        otio.unregister()
    else:
        print("       *** No Otio found to unregister ***")

    from .overlay_tools.workspace_info import workspace_info

    workspace_info.unregister()

    utils_ui.unregister()
    config.releaseGlobalVariables()

    print("")
