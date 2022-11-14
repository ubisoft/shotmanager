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
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty

from ..config import config

from .. import handlers
from ..handlers.sm_overlay_tools_handlers import install_handler_for_shot, toggle_overlay_tools_display
from ..overlay_tools.workspace_info.workspace_info import toggle_workspace_info_display

from ..features import cameraBG
from ..features import soundBG
from ..features import greasepencil
from ..feature_panels.greasepencil_25D import greasepencil_25D_ui
from ..features import storyboard

from ..operators import takes
from ..operators import shots
from ..operators import shots_global_settings_operators

from ..operators import general
from ..operators import playbar
from ..operators import shots_toolbar

from ..properties import props
from ..properties import shots_global_settings

from .. import prefs
from .. import retimer
from ..retimer import retimer_ui
from ..retimer.retimer_applyto_settings import UAS_Retimer_ApplyToSettings

from .. import rendering
from ..rendering import rendering_ui

from ..scripts import precut_tools
from ..scripts import rrs
from ..ui import sm_ui

from ..utils import utils
from ..utils import utils_render
from ..utils import utils_operators
from ..utils import utils_operators_overlays
from ..utils.utils_os import module_can_be_imported

from ..tools import frame_range
from ..tools import markers_nav_bar


from .. import debug as sm_debug

from ..config import sm_logging

_logger = sm_logging.getLogger(__name__)


import logging


def register():

    #    config.initGlobalVariables()

    from ..utils import utils_ui

    utils_ui.register()

    sm_logging.initialize(addonName="Ubisoft Shot Manager", prefix="SM")
    if config.devDebug:
        _logger.setLevel("DEBUG")  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    _logger.tags = config.getLoggingTags()
    logger_level = f"Logger level: {sm_logging.getLevelName()}"
    sm_logging.loggerFormatTest(message="Logger test message")

    versionTupple = utils.display_addon_registered_version("Ubisoft Shot Manager", more_info=logger_level)

    from ..overlay_tools.workspace_info import workspace_info

    workspace_info.register()

    # install dependencies and required Python libraries
    ###################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there

    from ..install_and_register.install_otio_local_dist import install_otio_local_dist
    from ..install_and_register.install_dependencies import install_dependencies

    if not install_otio_local_dist():

        installErrorCode = install_dependencies([("opentimelineio", "opentimelineio")], retries=1, timeout=10)
        # installErrorCode = 0
        if 0 != installErrorCode:
            # utils_handlers.removeAllHandlerOccurences(shotMngHandler_frame_change_pre_jumpToShot, handlerCateg=bpy.app.handlers.frame_change_pre)
            # return installErrorCode
            _logger.error_ext("  *** OpenTimelineIO install failed for Ubisoft Shot Manager ***")
        else:
            _logger.info_ext("  OpenTimelineIO correctly installed for Ubisoft Shot Manager")

    # otio
    try:
        from .. import otio

        otio.register()

        # from shotmanager.otio import importOpenTimelineIOLib

        # if importOpenTimelineIOLib():
        #     otio.register()
        # else:
        #     print("       *** OTIO Package import failed ***")
    except ModuleNotFoundError:
        print("       *** OTIO Package import failed ****")

    # PIL library - for Stamp Info and image writing
    installErrorCode = install_dependencies([("PIL", "pillow")], retries=1, timeout=5)
    if 0 != installErrorCode:
        _logger.error_ext("  *** Pillow Imaging Library (PIL) install failed for Ubisoft Shot Manager ***")
    else:
        _logger.info_ext("  Pillow Imaging Library (PIL) correctly installed for Ubisoft Stamp Info")

    try:
        pil_logger = logging.getLogger("PIL")
        pil_logger.setLevel(logging.INFO)
    except Exception:
        pass

    # register other packages
    ###################

    # debug tools
    sm_debug.register()

    from ..features.storyboard import frame_grid
    from ..features.greasepencil import greasepencil_frame_usage_preset
    from ..features.greasepencil import greasepencil_frame_template

    from ..addon_prefs import addon_prefs
    from ..utils import utils_vse_render
    from ..overlay_tools import sequence_timeline
    from ..overlay_tools import interact_shots_stack
    from ..overlay_tools import viewport_camera_hud

    from .. import stampinfo

    from .. import keymaps

    ###################
    # update data
    ###################

    bpy.types.WindowManager.UAS_shot_manager_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    frame_grid.register()
    greasepencil_frame_usage_preset.register()
    greasepencil_frame_template.register()
    addon_prefs.register()

    utils_operators.register()
    utils_operators_overlays.register()

    # operators
    # markers_nav_bar_addon_prefs.register()
    cameraBG.register()
    soundBG.register()
    greasepencil.register()
    storyboard.register()
    frame_range.register()
    markers_nav_bar.register()
    rendering.register()
    takes.register()
    shots.register()
    shots_global_settings.register()
    shots_global_settings_operators.register()
    precut_tools.register()
    playbar.register()
    retimer.register()
    props.register()
    shots_toolbar.register()

    # ui
    sm_ui.register()
    greasepencil_25D_ui.register()
    retimer_ui.register()
    rendering_ui.register()
    rrs.register()

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
    stampinfo.register()

    # rrs specific
    # rrs_vsm_tools.register()

    # declaration of properties that will not be saved in the scene:
    ####################

    # call in the code by context.window_manager.UAS_shot_manager_shots_play_mode etc

    def _update_UAS_shot_manager_shots_play_mode(self, context):
        # if self.UAS_shot_manager_shots_play_mode:
        install_handler_for_shot(self, context)

    bpy.types.WindowManager.UAS_shot_manager_shots_play_mode = BoolProperty(
        name="Enable Shots Play Mode",
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
        default=False,
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

    bpy.types.WindowManager.UAS_shot_manager_shots_stack_retimerApplyTo = PointerProperty(
        type=UAS_Retimer_ApplyToSettings
    )

    if config.devDebug:
        print(f"\n ------ Ubisoft Shot Manager debug: {config.devDebug} ------- ")

    addon_prefs_inst = config.getAddonPrefs()
    addon_prefs_inst.displaySMDebugPanel = config.devDebug_displayDebugPanel

    # _props = config.getAddonProps(bpy.context.scene)
    # # currentLayout = props.getCurrentLayout()
    # if not _props.isInitialized:
    #     _props.initialize_shot_manager()

    # storyboard
    # prefs_properties = config.getAddonPrefs()
    # prefs_properties.stb_frameTemplate.initialize(fromPrefs=True)

    if not addon_prefs_inst.isPrefsVersionUpToDate():
        addon_prefs_inst.initialize_shot_manager_prefs()

    # not working...
    # try:
    #     bpy.ops.preferences.addon_show(module="shotmanager")
    # except Exception:
    #     print("Fail to update the Preferences panel...")

    print("")


def unregister():

    utils.display_addon_registered_version("Ubisoft Shot Manager", unregister=True)

    # marche pas
    _props = config.getAddonProps(bpy.context.scene)
    print(f"leaving current scene : {bpy.context.scene.name}")
    _props.isInitialized = False

    from ..utils import utils_ui
    from ..overlay_tools import sequence_timeline
    from ..overlay_tools import interact_shots_stack
    from ..overlay_tools import viewport_camera_hud

    # Unregister packages that may have been registered if the install had errors
    ###################
    from ..install_and_register.install_dependencies import unregister_from_failed_install

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

    from ..features.storyboard import frame_grid
    from ..features.greasepencil import greasepencil_frame_usage_preset
    from ..features.greasepencil import greasepencil_frame_template

    from ..addon_prefs import addon_prefs
    from ..utils import utils_vse_render

    from .. import keymaps

    from .. import stampinfo

    stampinfo.unregister()

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

    rrs.unregister()
    rendering_ui.unregister()
    retimer_ui.unregister()
    greasepencil_25D_ui.unregister()
    sm_ui.unregister()

    # operators
    rendering.unregister()
    shots_toolbar.unregister()
    props.unregister()
    retimer.unregister()
    playbar.unregister()
    precut_tools.unregister()
    shots_global_settings_operators.unregister()
    shots_global_settings.unregister()
    shots.unregister()
    takes.unregister()

    utils_operators_overlays.unregister()
    utils_operators.unregister()
    markers_nav_bar.unregister()
    frame_range.unregister()
    storyboard.unregister()
    greasepencil.unregister()
    soundBG.unregister()
    cameraBG.unregister()

    addon_prefs.unregister()
    greasepencil_frame_template.unregister()
    greasepencil_frame_usage_preset.unregister()
    frame_grid.unregister()

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
        from .. import otio

        otio.unregister()
    else:
        print("       *** No Otio found to unregister ***")

    from ..overlay_tools.workspace_info import workspace_info

    workspace_info.unregister()

    utils_ui.unregister()
    #   config.releaseGlobalVariables()

    print("")
