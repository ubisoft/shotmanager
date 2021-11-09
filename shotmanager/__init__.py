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

import logging

import os
from pathlib import Path

import bpy

from bpy.props import BoolProperty, IntProperty, FloatProperty

from .config import config

from . import handlers
from .handlers.sm_overlay_tools_handlers import install_handler_for_shot, timeline_valueChanged

from .features import cameraBG
from .features import soundBG
from .features import greasepencil

from .operators import takes
from .operators import shots
from .operators import shots_global_settings

from .operators import general
from .operators import playbar
from .operators import shots_toolbar

from .operators import prefs
from .operators import prefs_tools
from .operators import features
from .operators import about

from .properties import props

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

# from .data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25
# from .data_patches.data_patch_to_v1_3_16 import data_patch_to_v1_3_16
# from .data_patches.data_patch_to_v1_3_31 import data_patch_to_v1_3_31

from . import keymaps

from .debug import sm_debug

bl_info = {
    "name": "Shot Manager",
    "author": "Ubisoft - Julien Blervaque (aka Werwack), Romain Carriquiry Borchiari",
    "description": "Manage a sequence of shots and cameras in the 3D View - Ubisoft Animation Studio",
    "blender": (2, 92, 0),
    "version": (1, 6, 5),
    "location": "View3D > Shot Manager",
    "wiki_url": "https://ubisoft-shotmanager.readthedocs.io",
    # "warning": "BETA Version",
    "category": "Ubisoft",
}

__version__ = ".".join(str(i) for i in bl_info["version"])
display_version = __version__


###########
# Logging
###########

# https://docs.python.org/fr/3/howto/logging.html
_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.INFO)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

# _logger.info(f"Logger {str(256) + 'my long very long text'}")
# _logger.info(f"Logger {str(256)}")
# _logger.warning(f"logger {256}")
# _logger.error(f"error {256}")
# _logger.debug(f"debug {256}")


class Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord):
        """
        The role of this custom formatter is:
        - append filepath and lineno to logging format but shorten path to files, to make logs more clear
        - to append "./" at the begining to permit going to the line quickly with VS Code CTRL+click from terminal
        """
        s = super().format(record)
        pathname = Path(record.pathname).relative_to(MODULE_PATH)
        s += f"  [{os.curdir}{os.sep}{pathname}:{record.lineno}]"
        return s


# def get_logs_directory():
#     def _get_logs_directory():
#         import tempfile

#         if "MIXER_USER_LOGS_DIR" in os.environ:
#             username = os.getlogin()
#             base_shared_path = Path(os.environ["MIXER_USER_LOGS_DIR"])
#             if os.path.exists(base_shared_path):
#                 return os.path.join(os.fspath(base_shared_path), username)
#             logger.error(
#                 f"MIXER_USER_LOGS_DIR env var set to {base_shared_path}, but directory does not exists. Falling back to default location."
#             )
#         return os.path.join(os.fspath(tempfile.gettempdir()), "mixer")

#     dir = _get_logs_directory()
#     if not os.path.exists(dir):
#         os.makedirs(dir)
#     return dir


# def get_log_file():
#     from mixer.share_data import share_data

#     return os.path.join(get_logs_directory(), f"mixer_logs_{share_data.run_id}.log")


def register():

    from .utils import utils_ui

    utils_ui.register()
    versionTupple = utils.display_addon_registered_version("Shot Manager")
    config.initGlobalVariables()

    ###################
    # logging
    ###################

    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = None

        if config.devDebug_ignoreLoggerFormatting:
            ch = "~"  # "\u02EB"
            formatter = Formatter(ch + " {message:<140}", style="{")
        else:
            # formatter = Formatter("{asctime} {levelname[0]} {name:<30}  - {message:<80}", style="{")
            formatter = Formatter("SM " + " {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)

    if config.devDebug:
        _logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    # install dependencies and required Python libraries
    ###################
    # try to install dependencies and collect the errors in case of troubles
    # If some mandatory libraries cannot be loaded then an alternative Add-on Preferences panel
    # is used and provide some visibility to the user to solve the issue
    # Pillow lib is installed there

    if (2, 93, 0) <= bpy.app.version:
        # print("  installing OpenTimelineIO 0.13 for Python 3.9 for Ubisoft Shot Manager...")
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
    else:
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

    try:
        utils_vse_render.register()
    except Exception:
        print("*** Paf for utils_vse_render.register")

    utils_render.register()
    general.register()
    interact_shots_stack.register()
    sequence_timeline.register()
    viewport_camera_hud.register()
    prefs.register()
    prefs_tools.register()
    features.register()
    about.register()
    keymaps.register()
    handlers.register()

    # rrs specific
    # rrs_vsm_tools.register()

    # declaration of properties that will not be saved in the scene:
    ####################

    # call in the code by context.window_manager.UAS_shot_manager_shots_play_mode etc

    def _update_UAS_shot_manager_shots_play_mode(self, context):
        install_handler_for_shot(self, context)

    bpy.types.WindowManager.UAS_shot_manager_shots_play_mode = BoolProperty(
        name="Enable Shot Play Mode",
        description="Override the standard animation Play mode to play the enabled shots" "\nin the specified order",
        update=_update_UAS_shot_manager_shots_play_mode,
        default=False,
    )

    def _update_UAS_shot_manager_display_overlay_tool(self, context):
        timeline_valueChanged(self, context)

    bpy.types.WindowManager.UAS_shot_manager_display_overlay_tools = BoolProperty(
        name="Show Overlay Tools",
        description="Toggle the display of the overlay tools in the opened editors:"
        "\n  - Sequence Timeline in the 3D viewport"
        "\n  - Interactive Shots Stack in the Timeline editor",
        update=_update_UAS_shot_manager_display_overlay_tool,
        default=False,
    )

    bpy.types.WindowManager.UAS_shot_manager_toggle_montage_interaction = BoolProperty(
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
        print(f"\n ------ UAS debug: {config.devDebug} ------- ")
        print(f" ------ _Logger Level: {logging.getLevelName(_logger.level)} ------- \n")

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

    # bpy.utils.unregister_class(cls)
    #    bpy.ops.uas_shot_manager.draw_timeline.cancel(bpy.context)

    #  bpy.context.window_manager.event_timer_remove(bpy.ops.uas_shot_manager.draw_timeline.draw_event)
    # bpy.types.SpaceView3D.draw_handler_remove(bpy.ops.uas_shot_manager.draw_timeline.draw_handle, "WINDOW")

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
    about.unregister()
    features.unregister()
    prefs_tools.unregister()
    prefs.unregister()
    viewport_camera_hud.unregister()
    sequence_timeline.unregister()
    interact_shots_stack.unregister()
    general.unregister()
    utils_render.unregister()
    try:
        utils_vse_render.unregister()
    except Exception:
        print("*** Paf for utils_vse_render.unregister")

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

    utils_ui.unregister()
    config.releaseGlobalVariables()

    print("")
