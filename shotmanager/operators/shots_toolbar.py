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
To do: module description here.
"""

import bpy
from bpy.types import Operator

#
# Removed and replaced by a property in props
#
# class UAS_ShotManager_LockCamToView(Operator):
#     bl_idname = "uas_shot_manager.lockcamtoview"
#     bl_label = "Lock Cameras to View"
#     bl_description = "Enable view navigation within the camera view"
#     bl_options = {"INTERNAL"}

#     @classmethod
#     def poll(cls, context):
#         props = context.scene.UAS_shot_manager_props
#         val = len(props.getTakes()) and len(props.get_shots())
#         return val

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         # Can also use area.spaces.active to get the space assoc. with the area
#         for area in context.screen.areas:
#             if area.type == "VIEW_3D":
#                 for space in area.spaces:
#                     if space.type == "VIEW_3D":
#                         space.lock_camera = True

#         return {"FINISHED"}


class UAS_ShotManager_EnableDisableAll(Operator):
    bl_idname = "uas_shot_manager.enabledisableall"
    bl_label = "Enable / Disable All Shots"
    bl_description = "Toggle shot enabled state.\nShift + Click: Enable all shots,\nCtrl + Click: Disable all shots,\nCtrl + Shift + Click: Invert shots state,\nAlt + Click: Isolate Selected Shot,"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences

        enableMode = "ENABLEALL"
        if event.shift and not event.ctrl and not event.alt:
            enableMode = "ENABLEALL"
        elif event.ctrl and not event.shift and not event.alt:
            enableMode = "DISABLEALL"
        elif event.shift and event.ctrl and not event.alt:
            enableMode = "INVERT"
        elif event.alt and not event.shift and not event.ctrl:
            enableMode = "ENABLEONLYCSELECTED"
        elif not event.alt and not event.shift and not event.ctrl:
            enableMode = "ENABLEALL" if prefs.toggleShotsEnabledState else "DISABLEALL"
            prefs.toggleShotsEnabledState = not prefs.toggleShotsEnabledState

        selectedShot = props.getSelectedShot()
        shotsList = props.getShotsList()
        for shot in shotsList:
            if "ENABLEALL" == enableMode:
                shot.enabled = True
            elif "DISABLEALL" == enableMode:
                shot.enabled = False
            elif "INVERT" == enableMode:
                shot.enabled = not shot.enabled
            elif "ENABLEONLYCSELECTED" == enableMode:
                shot.enabled = shot == selectedShot

        props.setSelectedShot(selectedShot)

        return {"FINISHED"}


class UAS_ShotManager_SceneRangeFromShots(Operator):
    bl_idname = "uas_shot_manager.scenerangefromshots"
    bl_label = "Scene Range From Shot"
    bl_description = (
        "Set scene time range with take range"
        #    "\nShift + Click: Create a new camera from the 3D view and put it in the viewport."
        "\nCtrl + Click: Set scene time range with current shot range"
        "\nUse Alt for the Preview time range"
    )
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        if event.shift:
            pass
        elif event.ctrl:
            currentShot = props.getCurrentShot()
            if event.alt:
                scene.use_preview_range = True
                scene.frame_preview_start = currentShot.start
                scene.frame_preview_end = currentShot.end
            else:
                scene.use_preview_range = False
                scene.frame_start = currentShot.start
                scene.frame_end = currentShot.end

        elif not event.ctrl:
            shotList = props.getShotsList(ignoreDisabled=True)
            if 0 < len(shotList):
                if event.alt:
                    scene.use_preview_range = True
                    scene.frame_preview_start = shotList[0].start
                    scene.frame_preview_end = shotList[len(shotList) - 1].end
                else:
                    scene.use_preview_range = False
                    scene.frame_start = shotList[0].start
                    scene.frame_end = shotList[len(shotList) - 1].end
        else:
            pass

        return {"FINISHED"}


# # operator here must be a duplicate of UAS_ShotManager_SceneRangeFromShot is order to use a different description
# class UAS_ShotManager_SceneRangeFromEnabledShots(Operator):
#     bl_idname = "uas_shot_manager.scenerangefromenabledshots"
#     bl_label = "Scene Range From Enabled Shot"
#     bl_description = "Set scene time range with enabled shots range"
#     bl_options = {"INTERNAL"}

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         shotList = props.getShotsList(ignoreDisabled=True)

#         if len(shotList):
#             scene.use_preview_range = True

#             scene.frame_preview_start = shotList[0].start
#             scene.frame_preview_end = shotList[len(shotList) - 1].end

#         return {"FINISHED"}


_classes = (
    UAS_ShotManager_EnableDisableAll,
    #   UAS_ShotManager_LockCamToView,
    UAS_ShotManager_SceneRangeFromShots,
    #    UAS_ShotManager_SceneRangeFromEnabledShots,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
