# -*- coding: utf-8 -*-
import bpy
from bpy.types import Panel, Operator
from bpy.props import CollectionProperty, StringProperty


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


class UAS_ShotManager_Playbar_GoToPreviousShot(Operator):
    bl_idname = "uas_shot_manager.playbar_gotopreviousshot"
    bl_label = "Previous Shot"
    bl_description = "Go to the start of the current shot or the end of the previous enabled one"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        currentFrameInd = context.scene.frame_current
        context.scene.UAS_shot_manager_props.goToPreviousShot(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


class UAS_ShotManager_Playbar_GoToNextShot(Operator):
    bl_idname = "uas_shot_manager.playbar_gotonextshot"
    bl_label = "Next Shot"
    bl_description = "Go to the end of the current shot or the start of the previous enabled one"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        currentFrameInd = context.scene.frame_current
        context.scene.UAS_shot_manager_props.goToNextShot(currentFrameInd, ignoreDisabled=True)

        return {"FINISHED"}


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
    UAS_ShotManager_Playbar_GoToPreviousShot,
    UAS_ShotManager_Playbar_GoToNextShot,
    UAS_ShotManager_Playbar_GoToPreviousFrame,
    UAS_ShotManager_Playbar_GoToNextFrame,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
