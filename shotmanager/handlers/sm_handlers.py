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
Handler functions
"""

import bpy
from bpy.app.handlers import persistent

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


@persistent
def shotMngHandler_undo_pre(self, context):
    _logger.debug_ext("Handler: Undo Pre", col="GREEN_LIGHT", tag="HANDLER")

    config.gShotsStackInfos = None


#   bpy.context.window_manager.UAS_shot_manager_display_overlay_tools = False


@persistent
def shotMngHandler_undo_post(self, context):
    _logger.debug_ext("Handler: Undo Post", col="GREEN_LIGHT", tag="HANDLER")


@persistent
def shotMngHandler_redo_pre(self, context):
    _logger.debug_ext("Handler: Redo Pre", col="GREEN_LIGHT", tag="HANDLER")

    config.gShotsStackInfos = None


#   bpy.context.window_manager.UAS_shot_manager_display_overlay_tools = False


@persistent
def shotMngHandler_redo_post(self, context):
    _logger.debug_ext("Handler: Redo Post", col="GREEN_LIGHT", tag="HANDLER")


@persistent
def shotMngHandler_load_pre(self, context):
    _logger.debug_ext("Handler: Load Pre", col="GREEN_LIGHT", tag="HANDLER")
    bpy.context.window_manager.UAS_shot_manager_display_overlay_tools = False


@persistent
def shotMngHandler_load_post(self, context):
    _logger.debug_ext("Handler: Load Post", col="GREEN_LIGHT", tag="HANDLER")

    # bpy.ops.uas_shot_manager.sequence_timeline.cancel(bpy.context)

    # bpy.context.window_manager.event_timer_remove(bpy.ops.uas_shot_manager.sequence_timeline.draw_event)
    # bpy.types.SpaceView3D.draw_handler_remove(bpy.ops.uas_shot_manager.sequence_timeline.draw_handle, "WINDOW")

    # bpy.ops.uas_shot_manager.sequence_timeline.unregister_handlers(context)
    # bpy.context.window_manager.UAS_shot_manager_display_overlay_tools = False
