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
Playbar operators
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)

#########
# Play bar
#########


class UAS_ShotManager_Playbar_GoToFirstShot(Operator):
    bl_idname = "uas_shot_manager.playbar_gotofirstshot"
    bl_label = "First Shot"
    bl_description = "Go to first enabled shot"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # currentFrameInd = context.scene.frame_current
        props = config.getAddonProps(context.scene)
        firstShot = props.getFirstShot(ignoreDisabled=True)
        newFrame = 0
        if firstShot is not None:
            newFrame = firstShot.start
            props.setCurrentShot(firstShot)
            props.setSelectedShot(firstShot)
            context.scene.frame_set(newFrame)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToLastShot(Operator):
    bl_idname = "uas_shot_manager.playbar_gotolastshot"
    bl_label = "Last Shot"
    bl_description = "Go to last enabled shot"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # currentFrameInd = context.scene.frame_current
        props = config.getAddonProps(context.scene)
        lastShot = props.getLastShot(ignoreDisabled=True)
        newFrame = 0
        if lastShot is not None:
            newFrame = lastShot.end
            props.setCurrentShot(lastShot)
            props.setSelectedShot(lastShot)
            context.scene.frame_set(newFrame)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToShotBoundary(Operator):
    bl_idname = "uas_shot_manager.playbar_gotoshotboundary"
    bl_label = "Ubisoft Shot Mng - Navigate on shots boundaries"
    bl_description = "Go from start to end of each shot"
    bl_options = {"INTERNAL", "UNDO"}

    eventsEnabled: BoolProperty(
        description="Enable keyboard events when the operator is called."
        "\nSet the value to True when the operator is called from a button"
        "\nand it needs to support alternative behaviors thanks to keyboard events",
        default=False,
    )

    # can be PREVIOUS or NEXT
    navigDirection: StringProperty(default="PREVIOUS")

    # can be START, END, ANY
    boundaryMode: StringProperty(default="ANY")

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "PREVIOUS" == properties.navigDirection:
            descr = (
                "Go to the start of the current shot or the end of the previous enabled one"
                "\n+ Ctrl: Jump forward from start to start"
                "\n+ Alt: Jump forward from end to end"
            )
        elif "NEXT" == properties.navigDirection:
            descr = (
                "Go to the end of the current shot or the start of the next enabled one"
                "\n+ Ctrl: Jump backward from start to start"
                "\n+ Alt: Jump backward from end to end"
            )
        descr += "\n\nShortcut: Ctrl / Alt Up and Down Arrows"
        return descr

    def invoke(self, context, event):
        # _logger.debug_ext(
        #     f"Op playbar_gotoshotboundary Invoke: dir: {self.navigDirection} - event.shift: {event.shift}",
        #     col="RED",
        # )

        if self.eventsEnabled:
            # if not event.ctrl and not event.shift and not event.alt:
            #     pass
            if event.ctrl and not event.shift and not event.alt:
                self.boundaryMode = "START"
            elif event.alt and not event.shift and not event.ctrl:
                self.boundaryMode = "END"
            else:
                self.boundaryMode = "ANY"
            # elif event.shift and not event.ctrl and not event.alt:
        return self.execute(context)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        currentFrameInd = context.scene.frame_current
        if "PREVIOUS" == self.navigDirection:
            props.goToPreviousShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode=self.boundaryMode)
        elif "NEXT" == self.navigDirection:
            props.goToNextShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode=self.boundaryMode)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToPreviousFrame(Operator):
    bl_idname = "uas_shot_manager.playbar_gotopreviousframe"
    bl_label = "Previous Frame"
    bl_description = "Go to previous frame" "\n\nShortcut: Left Arrow"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        currentFrameInd = context.scene.frame_current
        props.goToPreviousFrame(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToNextFrame(Operator):
    bl_idname = "uas_shot_manager.playbar_gotonextframe"
    bl_label = "Next Frame"
    bl_description = "Go to next frame" "\n\nShortcut: Right Arrow"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        currentFrameInd = context.scene.frame_current
        props.goToNextFrame(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


class UAS_ShotManager_UseAudio(Operator):
    bl_idname = "uas_shot_manager.use_audio"
    bl_label = "Use Audio"
    bl_description = "Toggle the audio in the scene"
    bl_options = {"INTERNAL"}
    """Blender scene property use_audio is the opposite of what it should be, should have been named audio_muted.
    This operator make it work as expected.
    """

    def execute(self, context):
        context.scene.use_audio = not context.scene.use_audio
        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Playbar_GoToFirstShot,
    UAS_ShotManager_Playbar_GoToLastShot,
    UAS_ShotManager_Playbar_GoToShotBoundary,
    UAS_ShotManager_Playbar_GoToPreviousFrame,
    UAS_ShotManager_Playbar_GoToNextFrame,
    UAS_ShotManager_UseAudio,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
