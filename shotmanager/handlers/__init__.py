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

from shotmanager.config import config
from shotmanager.utils import utils_handlers

from .sm_handlers import shotMngHandler_undo_pre, shotMngHandler_undo_post, shotMngHandler_load_pre

from .sm_check_data_handlers import shotMngHandler_load_post_checkDataVersion

from .sm_overlay_tools_handlers import shotMngHandler_frame_change_pre_jumpToShot

import logging

_logger = logging.getLogger(__name__)


def register():
    print("       - Registering Handlers Package")

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

    bpy.app.handlers.load_pre.append(shotMngHandler_load_pre)

    bpy.app.handlers.undo_pre.append(shotMngHandler_undo_pre)
    bpy.app.handlers.undo_pre.append(shotMngHandler_undo_post)

    if config.devDebug:
        utils_handlers.displayHandlers(handlerCategName="load_post")

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
    print("       - Unregistering Handlers Package")

    #    bpy.context.scene.UAS_shot_manager_props.display_shotname_in_3dviewport = False
    # if True:
    utils_handlers.removeAllHandlerOccurences(
        shotMngHandler_load_post_checkDataVersion, handlerCateg=bpy.app.handlers.load_post
    )

    if shotMngHandler_frame_change_pre_jumpToShot in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(shotMngHandler_frame_change_pre_jumpToShot)


#  sm_overlay_tools_handlers.unregister()

