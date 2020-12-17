import logging

import os
from pathlib import Path

import bpy
from bpy.app.handlers import persistent

from bpy.props import BoolProperty, IntProperty, FloatProperty


from .config import config

from .handlers import jump_to_shot

from . import otio

from .features import cameraBG
from .features import greasepencil

from .operators import takes
from .operators import shots
from .operators import shots_global_settings

from .operators import general
from .operators import playbar
from .operators import shots_toolbar

from .operators import prefs
from .operators import features
from .operators import about

from .properties import props
from .properties import addon_prefs

from .retimer import retimer_ui
from .retimer import retimer_props


from . import rendering
from .rendering import rendering_ui

# from .rrs_specific import rrs_vsm_tools

from .scripts import precut_tools

from .tools import vse_render
from .tools.markers_nav_bar import markers_nav_bar

# from .tools.markers_nav_bar import markers_nav_bar_addon_prefs

from .ui import sm_ui

from .utils import utils
from .utils import utils_render
from .utils import utils_handlers
from .utils import utils_operators
from .utils import utils_get_set_current_time

from . import videoshotmanager
from . import viewport_3d

from .scripts import rrs

# from .data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25
# from .data_patches.data_patch_to_v1_3_16 import data_patch_to_v1_3_16

# # from .data_patches.data_patch_to_v1_3_31 import data_patch_to_v1_3_31

from .debug import sm_debug

bl_info = {
    "name": "UAS Shot Manager",
    "author": "Julien Blervaque (aka Werwack), Romain Carriquiry Borchiari",
    "description": "Manage a sequence of shots and cameras in the 3D View - Ubisoft Animation Studio",
    "blender": (2, 90, 0),
    "version": (1, 3, 80),
    "location": "View3D > UAS Shot Manager",
    "wiki_url": "https://gitlab-ncsa.ubisoft.org/animation-studio/blender/shotmanager-addon/-/wikis/home",
    "warning": "BETA Version - Fais gaffe à tes données !!!",
    "category": "UAS",
}

__version__ = f"v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}"


###########
# Logging
###########

# https://docs.python.org/fr/3/howto/logging.html
_logger = logging.getLogger(__name__)
_logger.propagate = False
MODULE_PATH = Path(__file__).parent.parent
logging.basicConfig(level=logging.INFO)
_logger.setLevel(logging.INFO)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET


# _logger.info(f"Logger {str(256) + 'mon texte super long et tout'}")

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


###########
# Handlers
###########


def timeline_valueChanged(self, context):
    # print("  timeline_valueChanged:  self.UAS_shot_manager_display_timeline: ", self.UAS_shot_manager_display_timeline)
    if self.UAS_shot_manager_display_timeline:
        bpy.ops.uas_shot_manager.draw_timeline("INVOKE_DEFAULT")
        bpy.ops.uas_shot_manager.draw_montage_timeline("INVOKE_DEFAULT")
        # bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")


def install_shot_handler(self, context):
    if self.UAS_shot_manager_shots_play_mode and jump_to_shot not in bpy.app.handlers.frame_change_pre:
        scene = context.scene
        shots = scene.UAS_shot_manager_props.get_shots()
        for i, shot in enumerate(shots):
            if shot.start <= scene.frame_current <= shot.end:
                scene.UAS_shot_manager_props.current_shot_index = i
                break
        bpy.app.handlers.frame_change_pre.append(jump_to_shot)
    #     bpy.app.handlers.frame_change_post.append(jump_to_shot__frame_change_post)

    #    bpy.ops.uas_shot_manager.draw_timeline ( "INVOKE_DEFAULT" )
    elif not self.UAS_shot_manager_shots_play_mode and jump_to_shot in bpy.app.handlers.frame_change_pre:
        utils_handlers.removeAllHandlerOccurences(jump_to_shot, handlerCateg=bpy.app.handlers.frame_change_pre)
        # utils_handlers.removeAllHandlerOccurences(
        #     jump_to_shot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
        # )


@persistent
def checkDataVersion_post_load_handler(self, context):
    loadedFileName = bpy.path.basename(bpy.context.blend_data.filepath)
    print("\n\n-------------------------------------------------------")
    if "" == loadedFileName:
        print("\nNew file loaded")
    else:
        print("\nExisting file loaded: ", bpy.path.basename(bpy.context.blend_data.filepath))
        _logger.info("  - Shot Manager is checking the version used to create the loaded scene data...")

        latestVersionToPatch = 1003061

        numScenesToUpgrade = 0
        lowerSceneVersion = -1
        for scn in bpy.data.scenes:

            # if "UAS_shot_manager_props" in scn:
            if getattr(bpy.context.scene, "UAS_shot_manager_props", None) is not None:
                #   print("\n   Shot Manager instance found in scene " + scn.name)
                props = scn.UAS_shot_manager_props

                # # Dirty hack to avoid accidental move of the cameras
                # try:
                #     print("ici")
                #     if bpy.context.space_data is not None:
                #         print("ici 02")
                #         if props.useLockCameraView:
                #             print("ici 03")
                #             bpy.context.space_data.lock_camera = False
                # except Exception as e:
                #     print("ici error")
                #     _logger.error("** bpy.context.space_data.lock_camera had an error **")
                #     pass

                #   print("     Data version: ", props.dataVersion)
                #   print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
                # if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
                # if props.dataVersion <= 0 or props.dataVersion < props.version()[1]:
                if props.dataVersion <= 0 or props.dataVersion < latestVersionToPatch:  # <= ???
                    _logger.info(
                        f"     *** Scene {scn.name}: Shot Manager Data Version is lower than the latest Shot Manager version to patch"
                    )
                    numScenesToUpgrade += 1
                    if -1 == lowerSceneVersion or props.dataVersion < lowerSceneVersion:
                        lowerSceneVersion = props.dataVersion
                else:
                    if props.dataVersion < props.version()[1]:
                        props.dataVersion = props.version()[1]
                    # set right data version
                    # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
                    # print("       Data upgraded to version V. ", props.dataVersion)

        if numScenesToUpgrade:
            print(
                f"Shot Manager Data Version is lower than the current Shot Manager version - Upgrading data with patches..."
            )
            # apply patch and apply new data version
            # wkip patch strategy to re-think. Collect the data versions and apply the respective patches?

            patchVersion = 1002026
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_2_25()
                lowerSceneVersion = patchVersion

            patchVersion = 1003016
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_3_16 import data_patch_to_v1_3_16

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_16()
                lowerSceneVersion = patchVersion

            patchVersion = 1003061
            if lowerSceneVersion < patchVersion:
                from .data_patches.data_patch_to_v1_3_61 import data_patch_to_v1_3_61

                print(f"       Applying data patch to file: upgrade to {patchVersion}")
                data_patch_to_v1_3_61()
                lowerSceneVersion = patchVersion

            # current version, no patch required but data version is updated
            if lowerSceneVersion < props.version()[1]:
                props.dataVersion = props.version()[1]

    props = bpy.context.scene.UAS_shot_manager_props
    if props is not None:
        if props.display_shotname_in_3dviewport:
            try:
                bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")
            except Exception as e:
                print("Paf in draw cameras ui  *")

        if props.display_hud_in_3dviewport:
            try:
                bpy.ops.uas_shot_manager.draw_hud("INVOKE_DEFAULT")
            except Exception as e:
                print("Paf in draw hud  *")


# wkip doesn t work!!! Property values changed right before the save are not saved in the file!
# @persistent
# def checkDataVersion_save_pre_handler(self, context):
#     print("\nFile saved - Shot Manager is writing its data version in the scene")
#     for scn in bpy.data.scenes:
#         if "UAS_shot_manager_props" in scn:
#             print("\n   Shot Manager instance found in scene, writing data version: " + scn.name)
#             props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
#             print("   props.dataVersion: ", props.dataVersion)


# classes = (
#
# )


def register():

    versionTupple = utils.display_addon_registered_version("UAS Shot Manager")

    config.initGlobalVariables()

    if config.uasDebug:
        _logger.setLevel(logging.DEBUG)  # CRITICAL ERROR WARNING INFO DEBUG NOTSET

    ###################
    # logging
    ###################

    if len(_logger.handlers) == 0:
        _logger.setLevel(logging.WARNING)
        formatter = None

        if config.uasDebug_ignoreLoggerFormatting:
            ch = "~"  # "\u02EB"
            formatter = Formatter(ch + " {message:<140}", style="{")
        else:
            formatter = Formatter("{asctime} {levelname[0]} {name:<30}  - {message:<80}", style="{")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        _logger.addHandler(handler)

        # handler = logging.FileHandler(get_log_file())
        # handler.setFormatter(formatter)
        # _logger.addHandler(handler)

    ###################
    # update data
    ###################

    # bpy.context.window_manager.UAS_shot_manager_version
    bpy.types.WindowManager.UAS_shot_manager_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    # handler to check the data version at load
    ##################
    # print("       * Post Load handler added\n")

    # if config.uasDebug:
    #     utils_handlers.displayHandlers(handlerCategName="load_post")

    utils_handlers.removeAllHandlerOccurences(
        checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    )
    bpy.app.handlers.load_post.append(checkDataVersion_post_load_handler)

    if config.uasDebug:
        utils_handlers.displayHandlers(handlerCategName="load_post")

    # handler to write the data version at save
    ##################
    # print("       - Pre Save handler added")
    # if config.uasDebug:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # utils_handlers.removeAllHandlerOccurences(checkDataVersion_save_pre_handler, handlerCateg=bpy.app.handlers.save_pre)
    # bpy.app.handlers.save_pre.append(checkDataVersion_save_pre_handler)

    # if config.uasDebug:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # initialization
    ##################

    # data version is written in the initialize function
    # bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
    #     name="Shot Manager is initialized", description="", default=False
    # )

    # utils_handlers.displayHandlers()
    utils_handlers.removeAllHandlerOccurences(jump_to_shot, handlerCateg=bpy.app.handlers.frame_change_pre)
    # utils_handlers.removeAllHandlerOccurences(
    #     jump_to_shot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
    # )
    # utils_handlers.displayHandlers()

    # for cls in classes:
    #     bpy.utils.register_class(cls)

    addon_prefs.register()

    utils_operators.register()

    # operators
    # markers_nav_bar_addon_prefs.register()
    cameraBG.register()
    greasepencil.register()
    markers_nav_bar.register()
    utils_get_set_current_time.register()
    rendering.register()
    takes.register()
    shots.register()
    shots_global_settings.register()
    precut_tools.register()
    playbar.register()
    retimer_props.register()
    props.register()
    shots_toolbar.register()

    # ui
    sm_ui.register()
    rrs.register()
    retimer_ui.register()
    rendering_ui.register()

    otio.register()
    vse_render.register()
    utils_render.register()
    general.register()
    viewport_3d.register()
    videoshotmanager.register()
    prefs.register()
    features.register()
    about.register()

    # rrs specific
    # rrs_vsm_tools.register()

    # debug tools
    if config.uasDebug:
        sm_debug.register()

    # declaration of properties that will not be saved in the scene:
    ####################

    # call in the code by context.window_manager.UAS_shot_manager_shots_play_mode etc

    bpy.types.WindowManager.UAS_shot_manager_shots_play_mode = BoolProperty(
        name="frame_handler",
        description="Override the standard animation Play mode to play the enabled shots\nin the specified order",
        default=False,
        update=install_shot_handler,
    )

    bpy.types.WindowManager.UAS_shot_manager_display_timeline = BoolProperty(
        name="display_timeline",
        description="Display a timeline in the 3D Viewport with the shots in the specified order",
        default=False,
        update=timeline_valueChanged,
    )

    bpy.types.WindowManager.UAS_shot_manager_toggle_montage_interaction = BoolProperty(
        name="montage_interaction", description="Disable or enable montage like timeline interaction", default=True,
    )

    bpy.types.WindowManager.UAS_shot_manager_progressbar = FloatProperty(
        name="progressbar",
        description="Value of the progress bar",
        subtype="PERCENTAGE",
        min=0,
        max=100,
        precision=0,
        default=0,
        options=set(),
    )

    if config.uasDebug:
        print(f"\n ------ UAS debug: {config.uasDebug} ------- ")
        print(f" ------ _Logger Level: {logging.getLevelName(_logger.level)} ------- \n")


def unregister():

    print("\n*** --- Unregistering UAS Shot Manager Add-on --- ***\n")

    #    bpy.context.scene.UAS_shot_manager_props.display_shotname_in_3dviewport = False

    utils_handlers.removeAllHandlerOccurences(
        checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    )

    # debug tools
    if config.uasDebug:
        sm_debug.unregister()

    # rrs specific
    #    rrs_vsm_tools.unregister()

    # ui
    about.unregister()
    features.unregister()
    prefs.unregister()
    videoshotmanager.unregister()
    viewport_3d.unregister()
    general.unregister()
    utils_render.unregister()
    vse_render.unregister()
    otio.unregister()

    rendering_ui.unregister()
    retimer_ui.unregister()
    rrs.unregister()
    sm_ui.unregister()

    # operators
    rendering.unregister()
    shots_toolbar.unregister()
    props.unregister()
    retimer_props.unregister()
    playbar.unregister()
    precut_tools.unregister()
    shots_global_settings.unregister()
    shots.unregister()
    takes.unregister()
    utils_operators.unregister()
    utils_get_set_current_time.unregister()
    markers_nav_bar.unregister()
    greasepencil.unregister()
    cameraBG.unregister()
    #   markers_nav_bar_addon_prefs.unregister()

    addon_prefs.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    if jump_to_shot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(jump_to_shot)

    del bpy.types.WindowManager.UAS_shot_manager_shots_play_mode
    del bpy.types.WindowManager.UAS_shot_manager_display_timeline

    #   del bpy.types.WindowManager.UAS_shot_manager_isInitialized
    del bpy.types.WindowManager.UAS_shot_manager_version

    config.releaseGlobalVariables()
