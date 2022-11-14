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
Handlers Init
"""

import bpy
from bpy.app.handlers import persistent

from shotmanager.utils import utils_handlers

from . import sm_handlers


# from . import sm_check_data_handlers
from .sm_check_data_handlers import shotMngHandler_load_post_checkDataVersion
from shotmanager.overlay_tools.viewport_camera_hud.camera_hud_handlers import shotMngHandler_load_post_cameraHUD

from .sm_overlay_tools_handlers import shotMngHandler_frame_change_pre_jumpToShot


from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def register():
    _logger.debug_ext("       - Registering Handlers Package", form="REG")

    # for cls in _classes:
    #     bpy.utils.register_class(cls)

    # from . import interact_shots_stack
    # from . import sequence_timeline

    # interact_shots_stack.register()
    # sequence_timeline.regitster()

    ###################
    # update data
    ###################

    # handler to check the data version at load
    ##################
    # print("       * Post Load handler added\n")

    # if config.devDebug:
    #     utils_handlers.displayHandlers(handlerCategName="load_post")

    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_load_post_checkDataVersion, handlerCateg=bpy.app.handlers.load_post
    )
    bpy.app.handlers.load_post.append(shotMngHandler_load_post_checkDataVersion)

    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_load_post_cameraHUD, handlerCateg=bpy.app.handlers.load_post
    )
    bpy.app.handlers.load_post.append(shotMngHandler_load_post_cameraHUD)

    # load
    bpy.app.handlers.load_pre.append(sm_handlers.shotMngHandler_load_pre)
    bpy.app.handlers.load_post.append(sm_handlers.shotMngHandler_load_post)

    # undo
    bpy.app.handlers.undo_pre.append(sm_handlers.shotMngHandler_undo_pre)
    bpy.app.handlers.undo_post.append(sm_handlers.shotMngHandler_undo_post)

    # redo
    bpy.app.handlers.redo_pre.append(sm_handlers.shotMngHandler_redo_pre)
    bpy.app.handlers.redo_post.append(sm_handlers.shotMngHandler_redo_post)

    # if config.devDebug:
    #     utils_handlers.displayHandlers(handlerCategName="load_post")

    # handler to write the data version at save
    ##################
    # print("       - Pre Save handler added")
    # if config.devDebug:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # utils_handlers.removeAllHandlerOccurences(checkDataVersion_save_pre_handler, handlerCateg=bpy.app.handlers.save_pre)
    # bpy.app.handlers.save_pre.append(checkDataVersion_save_pre_handler)

    # if config.devDebug:
    #     utils_handlers.displayHandlers(handlerCategName="save_pre")

    # initialization
    ##################

    # data version is written in the initialize function
    # bpy.types.WindowManager.UAS_shot_manager_isInitialized = BoolProperty(
    #     name="Shot Manager is initialized", description="", default=False
    # )

    # utils_handlers.displayHandlers()
    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_frame_change_pre_jumpToShot, handlerCateg=bpy.app.handlers.frame_change_pre
    )
    # utils_handlers.removeAllHandlerOccurences(
    #     shotMngHandler_frame_change_pre_jumpToShot__frame_change_post, handlerCateg=bpy.app.handlers.frame_change_post
    # )
    # utils_handlers.displayHandlers()


#  sm_overlay_tools_handlers.register()


def unregister():
    _logger.debug_ext("       - Unregistering Handlers Package", form="UNREG")

    # for cls in reversed(_classes):
    #     bpy.utils.unregister_class(cls)

    # from . import interact_shots_stack
    # from . import sequence_timeline

    # undo
    bpy.app.handlers.undo_pre.remove(sm_handlers.shotMngHandler_undo_pre)
    bpy.app.handlers.undo_post.remove(sm_handlers.shotMngHandler_undo_post)
    # redo
    bpy.app.handlers.redo_pre.remove(sm_handlers.shotMngHandler_redo_pre)
    bpy.app.handlers.redo_post.remove(sm_handlers.shotMngHandler_redo_post)

    # load
    bpy.app.handlers.load_pre.remove(sm_handlers.shotMngHandler_load_pre)
    bpy.app.handlers.load_post.remove(sm_handlers.shotMngHandler_load_post)

    # if True:
    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_load_post_checkDataVersion, handlerCateg=bpy.app.handlers.load_post
    )
    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_load_post_cameraHUD, handlerCateg=bpy.app.handlers.load_post
    )

    if shotMngHandler_frame_change_pre_jumpToShot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(shotMngHandler_frame_change_pre_jumpToShot)

    # sequence_timeline.unregitster()
    # interact_shots_stack.unregister()


#  sm_overlay_tools_handlers.unregister()
