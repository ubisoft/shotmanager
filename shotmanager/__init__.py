# -*- coding: utf-8 -*-
#
# This addon blabla
#
# Installation:
#
#
# Things to know:
#   - 1 shot manager instance per scene (= possible differences in preferences per scene)
#
#   - time on media (= output videos) starts at frame 0 (and then last frame index is equal to Durantion - 1)
#   - Shots:
#       - end frame is INCLUDED in the shot frames (and then rendered)
#
#
# Dev notes:
#  * Pb:
#   cleanner le patch dégueu des indices de takes lors de la suppression des shots disabled
#       - about à finir
#       - jog pas parfait
#       - script unique cam en rade
#       - getsion des viewports
#
#
#  * To do:
#   mettre des shot warnings et errors
#   faire un warning pour shot start - handle < 0!!!
#
#
#
#       - mettre des modifiers CTRL et Alt pour jogguer entre les débuts et fin seulement de plans
#       - ajouter un bouton Help
#       - prefix Name
#       - take verouille les cams
#
#       - mettre des vraies prefs utilisateurs
#
#
#   Refacto code:
#   - faire modules avec:
#       - otio (avec les bons imports)
#       - render
#   - ranger les explorers
#
#

import bpy
from bpy.app.handlers import persistent

from bpy.props import BoolProperty, IntProperty

from . import otio

from .config import config

from .handlers import jump_to_shot

# from .handlers import jump_to_shot__frame_change_post

from .operators import takes
from .operators import shots
from .operators import shots_global_settings

from .operators import general
from .operators import playbar
from .operators import renderProps

from .operators import prefs

from .properties import props

from .retimer import retimer_ui
from .retimer import retimer_props

from .scripts import precut_tools

from .tools import vse_render

from .ui import sm_ui

from .utils import utils_render
from .utils import utils
from .utils import utils_handlers

from . import videoshotmanager

from .scripts import rrs

from .data_patches.data_patch_to_v1_2_25 import data_patch_to_v1_2_25

from .debug import sm_debug

bl_info = {
    "name": "UAS Shot Manager",
    "author": "Romain Carriquiry Borchiari, Julien Blervaque (aka Werwack)",
    "description": "Manage a sequence of shots and cameras in the 3D View - Ubisoft Animation Studio",
    "blender": (2, 83, 1),
    "version": (1, 2, 21),
    "location": "View3D > UAS Shot Manager",
    "wiki_url": "https://mdc-web-tomcat17.ubisoft.org/confluence/display/UASTech/UAS+Shot+Manager",
    "warning": "",
    "category": "UAS",
}


###########
# Handlers
###########


def timeline_valueChanged(self, context):
    print("  timeline_valueChanged:  self.UAS_shot_manager_display_timeline: ", self.UAS_shot_manager_display_timeline)
    if self.UAS_shot_manager_display_timeline:
        bpy.ops.uas_shot_manager.draw_timeline("INVOKE_DEFAULT")
        bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")


def install_shot_handler(self, context):
    if self.UAS_shot_manager_handler_toggle and jump_to_shot not in bpy.app.handlers.frame_change_pre:
        scene = context.scene
        shots = scene.UAS_shot_manager_props.get_shots()
        for i, shot in enumerate(shots):
            if shot.start <= scene.frame_current <= shot.end:
                scene.UAS_shot_manager_props.current_shot_index = i
                break
        bpy.app.handlers.frame_change_pre.append(jump_to_shot)
    #     bpy.app.handlers.frame_change_post.append(jump_to_shot__frame_change_post)

    #    bpy.ops.uas_shot_manager.draw_timeline ( "INVOKE_DEFAULT" )
    elif not self.UAS_shot_manager_handler_toggle and jump_to_shot in bpy.app.handlers.frame_change_pre:
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
        print("  - Shot Manager is checking the version used to create the loaded scene data...")

        numScenesToUpgrade = 0
        for scn in bpy.data.scenes:
            if "UAS_shot_manager_props" in scn:
                #   print("\n   Shot Manager instance found in scene " + scn.name)
                props = scn.UAS_shot_manager_props
                #   print("     Data version: ", props.dataVersion)
                #   print("     Shot Manager version: ", bpy.context.window_manager.UAS_shot_manager_version)
                if props.dataVersion <= 0 or props.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
                    print("     *** Shot Manager Data Version is lower than the current Shot Manager version")
                    numScenesToUpgrade += 1
                #    props.dataVersion = -5

        if numScenesToUpgrade:
            # apply patch and apply new data version
            # wkip patch strategy to re-think. Collect the data versions and apply the respective patches?
            print("       Applying data patch to file")
            data_patch_to_v1_2_25()

            # set right data version
            # props.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
            # print("       Data upgraded to version V. ", props.dataVersion)


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


# def verbose_set(key: str, default: bool, override: str, verbose: bool = True) -> None:
#     default_value = str(default)
#     if key in os.environ.keys():
#         if override and os.environ[key] != default_value:
#             if verbose:
#                 print(f"Overrinding value for '{key}': {default}")
#             os.environ[key] = default_value
#         return  # already set

#     if verbose:
#         print(f"Key '{key}' not in the default environment, setting it to {default_value}")
#     os.environ[key] = default_value


# def setup_project_env(override_existing: bool, verbose: bool = True) -> None:

#     verbose_set("UAS_PROJECT_NAME", "RRSpecial", override_existing, verbose)
#     verbose_set("UAS_PROJECT_FRAMERATE", "25.0", override_existing, verbose)
#     verbose_set("UAS_PROJECT_RESOLUTION", "[1280,720]", override_existing, verbose)
#     verbose_set("UAS_PROJECT_RESOLUTIONFRAMED", "[1280,960]", override_existing, verbose)
#     verbose_set("UAS_PROJECT_OUTPUTFORMAT", "mp4", override_existing, verbose)
#     verbose_set("UAS_PROJECT_COLORSPACE", "", override_existing, verbose)
#     verbose_set("UAS_PROJECT_ASSETNAME", "", override_existing, verbose)


def register():
    # set RRS Environment variables for project
    #    setup_project_env(True, True)

    config.initGlobalVariables()
    verbose = config.uasDebug

    # update data
    versionTupple = utils.addonVersion("UAS Shot Manager")
    print(
        "\n *** *** Registering Shot Manager Add-on - version: "
        + versionTupple[0]
        + "  ("
        + str(versionTupple[1])
        + ") *** ***"
    )

    # bpy.context.window_manager.UAS_shot_manager_version
    bpy.types.WindowManager.UAS_shot_manager_version = IntProperty(
        name="Add-on Version Int", description="Add-on version as integer", default=versionTupple[1]
    )

    # handler to check the data version at load
    ##################
    print("       - Post Load handler added")

    if verbose:
        utils_handlers.displayHandlers(handlerCategName="load_post")

    utils_handlers.removeAllHandlerOccurences(
        checkDataVersion_post_load_handler, handlerCateg=bpy.app.handlers.load_post
    )
    bpy.app.handlers.load_post.append(checkDataVersion_post_load_handler)

    if verbose:
        utils_handlers.displayHandlers(handlerCategName="load_post")

    # handler to write the data version at save
    ##################
    # print("       - Pre Save handler added")
    # if verbose:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # utils_handlers.removeAllHandlerOccurences(checkDataVersion_save_pre_handler, handlerCateg=bpy.app.handlers.save_pre)
    # bpy.app.handlers.save_pre.append(checkDataVersion_save_pre_handler)

    # if verbose:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # initialization
    ##################

    # data version is written in the initialize function
    bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
        name="Shot Manager is initialized", description="", default=False
    )

    # utils_handlers.displayHandlers()
    utils_handlers.removeAllHandlerOccurences(jump_to_shot, handlerCateg=bpy.app.handlers.frame_change_pre)
    # utils_handlers.removeAllHandlerOccurences(
    #     jump_to_shot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
    # )
    # utils_handlers.displayHandlers()

    # for cls in classes:
    #     bpy.utils.register_class(cls)

    # operators
    takes.register()
    shots.register()
    shots_global_settings.register()
    precut_tools.register()
    playbar.register()
    retimer_props.register()
    props.register()

    # ui
    sm_ui.register()
    rrs.register()
    retimer_ui.register()
    renderProps.register()
    utils.register()

    otio.register()
    vse_render.register()
    utils_render.register()
    general.register()
    videoshotmanager.register()
    prefs.register()

    # debug tools
    if config.uasDebug:
        sm_debug.register()

    # declaration of properties that will not be saved in the scene:
    ####################

    # About button panel Quick Settings
    bpy.types.WindowManager.UAS_shot_manager_displayAbout = BoolProperty(
        name="About...", description="Display About Informations", default=False
    )

    bpy.types.WindowManager.UAS_shot_manager_handler_toggle = BoolProperty(
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


def unregister():

    # debug tools
    if config.uasDebug:
        sm_debug.unregister()

    # ui
    prefs.unregister()
    videoshotmanager.unregister()
    general.unregister()
    utils_render.unregister()
    vse_render.unregister()
    otio.unregister()

    utils.unregister()
    renderProps.unregister()
    retimer_ui.unregister()
    rrs.unregister()
    sm_ui.unregister()

    # operators
    props.unregister()
    retimer_props.unregister()
    playbar.unregister()
    precut_tools.unregister()
    shots_global_settings.unregister()
    shots.unregister()
    takes.unregister()

    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)

    if jump_to_shot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(jump_to_shot)

    del bpy.types.WindowManager.UAS_shot_manager_displayAbout
    del bpy.types.WindowManager.UAS_shot_manager_handler_toggle
    del bpy.types.WindowManager.UAS_shot_manager_display_timeline

    del bpy.types.WindowManager.UAS_shot_manager_isInitialized
    del bpy.types.WindowManager.UAS_shot_manager_version

    config.releaseGlobalVariables()
