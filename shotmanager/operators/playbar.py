# -*- coding: utf-8 -*-
import bpy
from bpy.types import Panel, Operator
from bpy.props import CollectionProperty, StringProperty, BoolProperty


#########
# PLAY BAR
#########
class UAS_ShotManager_Playbar_GoToFirstShot(Operator):
    bl_idname = "uas_shot_manager.playbar_gotofirstshot"
    bl_label = "First Shot"
    bl_description = "Go to first enabled shot"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # currentFrameInd = context.scene.frame_current
        props = context.scene.UAS_shot_manager_props
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
        props = context.scene.UAS_shot_manager_props
        lastShot = props.getLastShot(ignoreDisabled=True)
        newFrame = 0
        if lastShot is not None:
            newFrame = lastShot.end
            props.setCurrentShot(lastShot)
            props.setSelectedShot(lastShot)
            context.scene.frame_set(newFrame)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToPreviousShotBoundary(Operator):
    bl_idname = "uas_shot_manager.playbar_gotopreviousshotboundary"
    bl_label = "Previous Shot"
    bl_description = "Go to the start of the current shot or the end of the previous enabled one"
    bl_options = {"INTERNAL"}

    ctrlPressed: BoolProperty(default=False)
    altPressed: BoolProperty(default=False)

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        self.ctrlPressed = not event.shift and event.ctrl and not event.alt
        self.altPressed = not event.shift and not event.ctrl and event.alt
        # print(f"Shit pressed: {self.shiftPressed}")

        currentFrameInd = scene.frame_current

        if self.ctrlPressed:
            props.goToPreviousShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="START")
        elif self.altPressed:
            props.goToPreviousShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="END")
        else:
            props.goToPreviousShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="ANY")

        return {"FINISHED"}

    # def execute(self, context):
    #     currentFrameInd = context.scene.frame_current
    #     context.scene.UAS_shot_manager_props.goToPreviousShotBoundary(currentFrameInd, ignoreDisabled=True)

    #     return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToNextShotBoundary(Operator):
    bl_idname = "uas_shot_manager.playbar_gotonextshotboundary"
    bl_label = "Next Shot"
    bl_description = "Go to the end of the current shot or the start of the previous enabled one"
    bl_options = {"INTERNAL"}

    ctrlPressed: BoolProperty(default=False)
    altPressed: BoolProperty(default=False)

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        self.ctrlPressed = not event.shift and event.ctrl and not event.alt
        self.altPressed = not event.shift and not event.ctrl and event.alt
        # print(f"Shit pressed: {self.shiftPressed}")

        currentFrameInd = scene.frame_current

        if self.ctrlPressed:
            props.goToNextShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="START")
        elif self.altPressed:
            props.goToNextShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="END")
        else:
            props.goToNextShotBoundary(currentFrameInd, ignoreDisabled=True, boundaryMode="ANY")

        return {"FINISHED"}

    # def execute(self, context):
    #     print("tititi")
    #     currentFrameInd = context.scene.frame_current
    #     context.scene.UAS_shot_manager_props.goToNextShotBoundary(currentFrameInd, ignoreDisabled=True)

    # return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToPreviousFrame(Operator):
    bl_idname = "uas_shot_manager.playbar_gotopreviousframe"
    bl_label = "Previous Frame"
    bl_description = "Go to previous frame"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        currentFrameInd = context.scene.frame_current
        context.scene.UAS_shot_manager_props.goToPreviousFrame(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToNextFrame(Operator):
    bl_idname = "uas_shot_manager.playbar_gotonextframe"
    bl_label = "Next Frame"
    bl_description = "Go to next frame"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        currentFrameInd = context.scene.frame_current
        context.scene.UAS_shot_manager_props.goToNextFrame(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_Playbar_GoToFirstShot,
    UAS_ShotManager_Playbar_GoToLastShot,
    UAS_ShotManager_Playbar_GoToPreviousShotBoundary,
    UAS_ShotManager_Playbar_GoToNextShotBoundary,
    UAS_ShotManager_Playbar_GoToPreviousFrame,
    UAS_ShotManager_Playbar_GoToNextFrame,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
