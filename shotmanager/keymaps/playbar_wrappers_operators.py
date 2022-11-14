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
Wrapper operators for the key mappings of the playbar.
There wrappers allow a clearer identification of the shortcuts in the Keymaps Preferences panel
"""

import bpy

from bpy.types import Operator
from bpy.props import StringProperty

# from shotmanager import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_Playbar_GoToShotBoundary_PreviousStart(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_previousstart"
    bl_label = "Ubisoft Shot Mng - Go to Previous Shot Start"
    bl_description = "Go to the start of previous shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the start of previous shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="PREVIOUS", boundaryMode="START")
        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary_PreviousEnd(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_previousend"
    bl_label = "Ubisoft Shot Mng - Go to Previous Shot End"
    bl_description = "Go to the end of previous shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the end of previous shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="PREVIOUS", boundaryMode="END")
        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary_PreviousAny(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_previousany"
    bl_label = "Ubisoft Shot Mng - Go to Previous Shot Boundary"
    bl_description = "Go to the previous boundary of previous shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the previous boundary of previous shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="PREVIOUS", boundaryMode="ANY")
        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary_NextStart(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_nextstart"
    bl_label = "Ubisoft Shot Mng - Go to Next Shot Start"
    bl_description = "Go to the start of next shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the start of next shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="NEXT", boundaryMode="START")
        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary_NextEnd(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_nextend"
    bl_label = "Ubisoft Shot Mng - Go to Next Shot End"
    bl_description = "Go to the end of next shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the end of next shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="NEXT", boundaryMode="END")
        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary_NextAny(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary_nextany"
    bl_label = "Ubisoft Shot Mng - Go to Next Shot Boundary"
    bl_description = "Go to the next boundary of next shot"
    bl_options = {"INTERNAL"}

    description: StringProperty(name="Description", default="Go to the next boundary of next shot")

    def execute(self, context):
        bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection="NEXT", boundaryMode="ANY")
        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Playbar_GoToShotBoundary_PreviousStart,
    UAS_ShotManager_Playbar_GoToShotBoundary_PreviousEnd,
    UAS_ShotManager_Playbar_GoToShotBoundary_PreviousAny,
    UAS_ShotManager_Playbar_GoToShotBoundary_NextStart,
    UAS_ShotManager_Playbar_GoToShotBoundary_NextEnd,
    UAS_ShotManager_Playbar_GoToShotBoundary_NextAny,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
