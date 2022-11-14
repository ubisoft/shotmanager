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
Shots functions and operators
"""

from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatVectorProperty

from random import uniform
import json

from shotmanager.utils import utils
from shotmanager.utils import utils_markers
from shotmanager.utils import utils_greasepencil
from shotmanager.utils.utils_time import zoom_dopesheet_view_to_range
from shotmanager.utils.utils_ui import propertyColumn
from shotmanager.utils.utils import slightlyRandomizeColor

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def list_cameras(self, context):
    res = list()
    for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        res.append((cam.name, cam.name, "", i))

    return res


def list_cameras_for_new_shot(self, context):
    res = list()
    res.append(("NEW_CAMERA", "Create New Camera", "Create new camera", 0))
    for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        res.append(
            (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
        )

    return res


def list_cameras_for_new_shots(self, context):
    res = list()
    res.append(("NEW_CAMERAS", "Create New Cameras", "Create a new camera for each shot", 0))
    for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        res.append(
            (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor all the new shots', i + 1)
        )

    return res


def list_cameras_assets_in_file(self, context):
    props = config.getAddonProps(context.scene)
    res = list()
    res.append(("DEFAULT_CAMERA", "Default Scene Camera", "Create a new camera from scene settings", 0))
    if Path(props.project_cameraAssets_path).exists() and Path(props.project_cameraAssets_path).is_file():

        # see https://docs.blender.org/api/current/bpy.types.BlendDataLibraries.html
        # https://blender.stackexchange.com/questions/251473/how-to-add-edit-tag-of-an-asset-from-another-asset-library-using-python-add-on
        cams = list()
        with bpy.data.libraries.load(props.project_cameraAssets_path, link=False, assets_only=False) as (
            data_from,
            data_to,
        ):
            for i, cam in enumerate(data_from.cameras):
                cams.append(cam)

        for i, camName in enumerate(cams):
            res.append(
                (
                    camName,
                    camName,
                    'Use the camera asset named "' + camName + '"\nas template for all the new shots',
                    i + 1,
                )
            )
    return res


########################
# for shot manipulation
########################


class UAS_ShotManager_SetShotStart(Operator):
    bl_idname = "uas_shot_manager.set_shot_start"
    bl_label = "Set Shot Start"
    bl_description = "Set the end time range with the curent time value"
    bl_options = {"INTERNAL", "UNDO_GROUPED"}

    # @classmethod
    # def poll(cls, context):
    #     return config.getAddonPrefs().display_frame_range_tool

    newStart: IntProperty(default=-99999)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        shot = props.getSelectedShot()
        # Manually add undo here
        if shot is not None:
            print(f"Shot Op: {self.newStart}, shot:{shot.name}")
            newValidStart = min(self.newStart, shot.end)
            #    bpy.ops.ed.undo_push(message=f"Set Shot Start to {newValidStart}")
            if shot.durationLocked:
                shot.durationLocked = False
                shot.start = newValidStart
                shot.durationLocked = True
            else:
                shot.start = newValidStart

        # if shot.durationLocked:
        #     if start_frame < shot.start:
        #         shot.start += offset
        #     elif start_frame < shot.end:
        #         shot.durationLocked = False
        #         shot.end += offset
        #         shot.durationLocked = True
        # else:
        #     # important to offset end first!!
        #     if start_frame < shot.end:
        #         shot.end += offset
        #     if start_frame < shot.start:
        #         shot.start += offset

        return {"FINISHED"}


########################
# for shot items
########################


class UAS_ShotManager_SetCurrentShot(Operator):
    """Set the specifed shot as current"""

    bl_idname = "uas_shot_manager.set_current_shot"
    bl_label = "Set Current Shot"
    bl_description = (
        "Click: Set the shot as current one"
        "\n+ Ctrl: Also frame shot in timeline"
        "\n+ Ctrl + Shft: Also frame whole edit in timeline"
        "\n+ Shft: No change to viewport"
        "\n+ Alt: No change to time"
        "\n+ Shft + Alt: No change to viewport nor time"
        # "\n+ Ctrl: Select Shot Camera"
        # "\n+ Shift: Toggle shot Disabled state"
    )

    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty(default=-1)

    # can be DO_NOTHING,
    action: StringProperty(default="DO_NOTHING")

    event_ctrl: BoolProperty(default=False)
    event_alt: BoolProperty(default=False)
    event_shift: BoolProperty(default=False)

    calledFromShotStack: BoolProperty(default=False)

    def invoke(self, context, event):
        _logger.debug_ext(f"Set Current Shot Operator invoke: event type: {event.type}", col="RED")

        if "DO_NOTHING" == self.action:

            self.event_ctrl = event.ctrl
            self.event_alt = event.alt
            self.event_shift = event.shift

            self.action = "SETCURRENT"

            if event.ctrl:
                if event.shift:
                    self.action += "_FRAMEEDIT"
                else:
                    self.action += "_FRAMESHOT"

            else:
                if event.shift:
                    if event.alt:
                        pass
                    else:
                        self.action += "_CHANGETIME"
                else:
                    if event.alt:
                        self.action += "_CHANGEVIEWPORT"
                    else:
                        self.action += "_CHANGEVIEWPORT"
                        self.action += "_CHANGETIME"

        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        # propsCurrentLayout = props.getCurrentLayout()
        prefs = config.getAddonPrefs()
        shot = props.getShotByIndex(self.index)

        if shot:
            _logger.debug_ext(f"Set Current Shot Op: {shot.name}")

        if not shot:
            _logger.error_ext(f"Set Current Shot Operator exec: shot is None. index: {self.index}")
        #     _logger.debug_ext("Set Current Shot Operator exec: ", col="RED")

        def _updateEditors(changeTime=True, zoom_mode=""):
            if shot is None:
                return

            # change time range to match shot range
            if prefs.current_shot_changes_time_range:
                if scene.use_preview_range:
                    scene.frame_preview_start = shot.start
                    scene.frame_preview_end = shot.end
                else:
                    scene.frame_start = shot.start
                    scene.frame_end = shot.end

            if prefs.current_shot_changes_current_time_to_start and changeTime:
                context.scene.frame_current = shot.start

            # zoom to frame shot or edit in anim range
            if "EDIT" == zoom_mode:
                shotList = props.getShotsList(ignoreDisabled=True)
                if 0 < len(shotList):
                    edit_start = shotList[0].start
                    edit_end = shotList[len(shotList) - 1].end
                    zoom_dopesheet_view_to_range(
                        context, edit_start, edit_end, changeTime=prefs.current_shot_changes_current_time_to_start
                    )
            # elif "SHOT" == zoom_mode:
            else:
                zoomView = False
                currentLayoutIsStb = "STORYBOARD" == props.currentLayoutMode()
                if currentLayoutIsStb:
                    if "STORYBOARD" == shot.shotType and prefs.stb_current_stb_shot_changes_time_zoom:
                        zoomView = True
                    elif "PREVIZ" == shot.shotType and prefs.stb_current_pvz_shot_changes_time_zoom:
                        zoomView = True
                else:
                    if "STORYBOARD" == shot.shotType and prefs.pvz_current_stb_shot_changes_time_zoom:
                        zoomView = True
                    elif "PREVIZ" == shot.shotType and prefs.pvz_current_pvz_shot_changes_time_zoom:
                        zoomView = True

                # shot zoom mode forced by use of key modifier
                if "SHOT" == zoom_mode:
                    zoomView = True

                if zoomView:
                    zoom_dopesheet_view_to_range(
                        context, shot.start, shot.end, changeTime=prefs.current_shot_changes_current_time_to_start
                    )

            if "STORYBOARD" == shot.shotType and prefs.current_stb_shot_select_stb_frame:
                gpChild = shot.getStoryboardFrame()
                if gpChild:
                    utils.select_object(gpChild)
            elif "PREVIZ" == shot.shotType and prefs.current_pvz_shot_select_stb_frame:
                gpChild = shot.getStoryboardFrame()
                if gpChild:
                    utils.select_object(gpChild)

        # change shot
        ###############################
        if "SETCURRENT" in self.action:

            props.setCurrentShotByIndex(
                self.index,
                source_area=context.area,
                changeTime="CHANGETIME" in self.action,
                setCamToViewport="CHANGEVIEWPORT" in self.action,
            )

            if self.index != props.selected_shot_index and not self.calledFromShotStack:
                props.setSelectedShotByIndex(self.index)

            zoomMode = ""
            if "FRAMESHOT" in self.action:
                zoomMode = "SHOT"
            elif "FRAMEEDIT" in self.action:
                zoomMode = "EDIT"

            _updateEditors(changeTime="CHANGETIME" in self.action, zoom_mode=zoomMode)

        # if not self.event_ctrl:
        #     props.setCurrentShotByIndex(
        #         self.index,
        #         changeTime=not self.event_alt,
        #         source_area=context.area,
        #         setCamToViewport=not self.event_shift,
        #     )
        #     if self.index != props.selected_shot_index and not self.calledFromShotStack:
        #         props.setSelectedShotByIndex(self.index)
        #     _updateEditors(changeTime=False)

        # # else:
        # #     props.setCurrentShotByIndex(self.index, source_area=context.area)
        # #     props.setSelectedShotByIndex(self.index)
        # #     _updateEditors(changeTime=True)

        # # disable shot
        # # elif event.shift and not event.ctrl and not event.alt:
        # #     shot.enabled = not shot.enabled

        # # frame shot range in timeline
        # ###############################
        # elif self.event_ctrl and not self.event_alt:
        #     # if event.alt:
        #     #     props.setCurrentShotByIndex(self.index, changeTime=False, source_area=context.area)
        #     # else:
        #     props.setCurrentShotByIndex(self.index, source_area=context.area)
        #     if self.index != props.selected_shot_index and not self.calledFromShotStack:
        #         props.setSelectedShotByIndex(self.index)
        #     if self.event_shift:
        #         _updateEditors(zoom_mode="EDIT")
        #     else:
        #         _updateEditors(zoom_mode="SHOT")

        # # select camera
        # # elif event.ctrl and not event.shift and not event.alt:
        # #     scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
        # #     scene.UAS_shot_manager_props.selectCamera(self.index)

        # # # already handled in first condition
        # # elif event.alt and not event.shift and not event.ctrl:
        # #     props.setCurrentShotByIndex(self.index, changeTime=False, source_area=context.area)
        # #     props.setSelectedShotByIndex(self.index)

        # else:
        #     pass

        return {"INTERFACE"}


class UAS_ShotManager_ToggleContinuousGPEditingMode(Operator):
    """Set the specifed shot as current"""

    bl_idname = "uas_shot_manager.toggle_continuous_gp_editing_mode"
    bl_label = "Continuous Draw Mode"
    bl_description = (
        "When used, the Storyboard Frame of each shot set to be the current"
        "\none will be automaticaly selected and switched to Draw mode."
        "\n+ Alt: Toggle the button between Draw and Select context for the Storyboard Frame"
    )
    bl_options = {"REGISTER"}

    # can be:
    #   - TOGGLE_USE_EDITING: will toggle the context between where the drawing state is available and the selection of the
    #     storyboard frame is available (basically the action button of each shot in the shot list will be changed).
    #     *** This does not activate the Drawing mode itself, but it can change it to Object mode in some cases ***
    #   - TOGGLE_ACTIVATE_EDITING_MODE: When the drawing context is available (one of the 2 states set by the mode above) then
    #     toggling between edit modes will alternate between Drawing mode activated (even if no stb frame is current)
    #     and Object mode activated.
    action: StringProperty(default="DO_NOTHING")

    def invoke(self, context, event):
        if event.alt:
            self.action = "TOGGLE_USE_EDITING"
        else:
            self.action = "TOGGLE_ACTIVATE_EDITING_MODE"

        return self.execute(context)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        # prefs = config.getAddonPrefs()

        if "TOGGLE_USE_EDITING" == self.action:
            props.useContinuousGPEditing = not props.useContinuousGPEditing
            if not props.useContinuousGPEditing:
                props.isEditingStoryboardFrame = False
                utils_greasepencil.switchToObjectMode()
        else:
            props.isEditingStoryboardFrame = not props.isEditingStoryboardFrame
            if props.isEditingStoryboardFrame:
                bpy.ops.uas_shot_manager.stb_frame_drawing()
            else:
                props.isEditingStoryboardFrame = False
                utils_greasepencil.switchToObjectMode()

        # NOTE: when the Continuous Editing mode is on then the selected and current shots are tied anyway
        # in the "change selection" code
        # if props.useContinuousGPEditing:
        #     prefs.stb_selected_shot_changes_current_shot = True
        # else:
        #     prefs.stb_selected_shot_changes_current_shot = False

        return {"FINISHED"}


class UAS_ShotManager_ShotDuration(Operator):
    bl_idname = "uas_shot_manager.shot_duration"
    bl_label = "Shot Duration"
    bl_description = "Shot Duration, given by end - start + 1"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.setSelectedShotByIndex(self.index)
        return {"FINISHED"}


class UAS_ShotManager_GetSetCurrentFrame(Operator):
    bl_idname = "uas_shot_manager.getsetcurrentframe"
    bl_label = "Get/Set Current Frame"
    bl_description = "Click: Set current frame with value." "\n+ Shift: Get current frame for value"
    bl_options = {"INTERNAL"}

    # shotSource is an array [index of shot, 0 (for start) or 1 (for end)]
    shotSource: StringProperty(default="")

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        argArr = json.loads(self.shotSource)

        shot = props.getShotByIndex(argArr[0])
        if event.shift:
            if 0 == argArr[1]:
                shot.start = context.scene.frame_current
            elif 1 == argArr[1]:
                shot.end = context.scene.frame_current
        else:
            if context.window_manager.UAS_shot_manager_shots_play_mode:
                props.setCurrentShotByIndex(argArr[0])
            else:
                props.setSelectedShotByIndex(argArr[0])
            if 0 == argArr[1]:
                context.scene.frame_current = shot.start
            elif 1 == argArr[1]:
                context.scene.frame_current = shot.end

        return {"FINISHED"}


class UAS_ShotManager_NoLens(Operator):
    bl_idname = "uas_shot_manager.nolens"
    bl_label = "No Lens"
    bl_description = "No Lens"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)


class UAS_ShotManager_NoDisplaySize(Operator):
    bl_idname = "uas_shot_manager.nodisplaysize"
    bl_label = "No Size"
    bl_description = "No Size"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)


class UAS_ShotManager_ShotTimeInEdit(Operator):
    bl_idname = "uas_shot_manager.shottimeinedit"
    bl_label = "Toggle Edit Times"
    bl_description = "Display the timings of the shots in the edit reference time"
    bl_options = {"INTERNAL"}

    shotSource: StringProperty(default="")

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        argArr = json.loads(self.shotSource)

        # print("shotSource: ", self.shotSource)
        # print("argArr: ", argArr)
        shot = props.getShotByIndex(argArr[0])

        if context.window_manager.UAS_shot_manager_shots_play_mode:
            props.setCurrentShotByIndex(argArr[0])
        else:
            props.setSelectedShotByIndex(argArr[0])

        if event.type == "LEFTMOUSE":
            if 0 == argArr[1]:
                context.scene.frame_current = shot.start
            elif 1 == argArr[1]:
                context.scene.frame_current = shot.end

        return {"FINISHED"}


class UAS_ShotManager_ShowNotes(Operator):
    bl_idname = "uas_shot_manager.shots_shownotes"
    bl_label = "Show Shot Notes"
    bl_description = "Display the notes associated to the shots"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        shot = props.getShotByIndex(self.index)
        shot.selectShotInUI()
        prefs.shot_notes_expanded = True
        props.expand_notes_properties = True
        return {"FINISHED"}


class UAS_ShotManager_ListCameraInstances(Operator):
    bl_idname = "uas_shot_manager.list_camera_instances"
    bl_label = "Shots Using This Camera "
    bl_description = "Number of shots using this camera in all the takes (this shot included)"
    # bl_options = {"REGISTER", "UNDO"}
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        wm = context.window_manager
        props.setSelectedShotByIndex(self.index)
        # return wm.invoke_props_dialog(self, width=300)
        return wm.invoke_popup(self, width=300)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        layout = self.layout
        row = layout.row()
        shot = props.getShotByIndex(self.index)
        if shot.camera is not None:
            numSharedCam = props.getNumSharedCamera(shot.camera) - 1
            if 0 < numSharedCam:
                row.label(text=f"Camera shared with {numSharedCam} other shot(s)")
                row = layout.row()
                row.label(text="from this take or other ones")
                row = layout.row()
                row.operator("uas_shot_manager.make_shot_camera_unique").shotName = props.getShotByIndex(
                    self.index
                ).name
            else:
                row.label(text="Camera used only in this shot, only in this take")
        else:
            row.label(text="No camera defined")

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_MakeShotCameraUnique(Operator):
    bl_idname = "uas_shot_manager.make_shot_camera_unique"
    bl_label = "Make Shot Camera Unique"
    bl_description = "If the camera is also used by another shot of the scene then it gets duplicated"
    bl_options = {"REGISTER", "UNDO"}

    shotName: StringProperty(default="")

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        # selectedShot = props.getSelectedShot()
        # selectedShotInd = props.getSelectedShotIndex()

        shot = props.getShotByName(self.shotName)
        if shot is not None:
            shot.makeCameraUnique()
        return {"INTERFACE"}


########################
# for shot manipulation
########################


class UAS_ShotManager_ShotAdd_GetCurrentFrameFor(Operator):
    bl_idname = "uas_shot_manager.shotadd_getcurrentframefor"
    bl_label = "Get Current Frame"
    bl_description = "Use the current frame for the specifed component"
    bl_options = {"REGISTER", "UNDO"}

    propertyToUpdate: StringProperty()

    def execute(self, context):
        scene = context.scene
        # props = config.getAddonProps(scene)
        prefs = config.getAddonPrefs()

        currentFrame = scene.frame_current

        if "addShot_start" == self.propertyToUpdate:
            prefs.addShot_start = min(prefs.addShot_end, currentFrame)
        elif "addShot_end" == self.propertyToUpdate:
            prefs.addShot_end = max(prefs.addShot_start, currentFrame)
        else:
            prefs[self.propertyToUpdate] = currentFrame

        return {"FINISHED"}


class UAS_ShotManager_ShotAdd(Operator):
    bl_idname = "uas_shot_manager.shot_add"
    bl_label = "Add New..."
    bl_description = (
        "Add a new shot starting at the current frame and using the selected camera"
        "\nThe new shot is put after the selected shot"
        "\n+ Shift: Skip the options dialog box"
    )
    bl_options = {"REGISTER", "UNDO"}

    layout_mode: StringProperty(name="Layout", default="PREVIZ")

    name: StringProperty(name="Name")
    cameraName: EnumProperty(items=list_cameras_for_new_shot, name="Camera", description="New Shot Camera")

    cameraAssetName: EnumProperty(
        items=list_cameras_assets_in_file,
        name="Camera Asset",
        description="Create a camera based on the specified asset",
    )

    atCurrentFrame: BoolProperty(
        name="At Current Frame:", description="Start the Storyboard Frame at the current time", default=False
    )

    color: FloatVectorProperty(
        name="Camera Color / Shot Color",
        description="Color of the chosen camera or color of the shot, according to the Shot Display settings",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        precision=2,
        # default=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
        default=(1.0, 1.0, 1.0),
    )
    colorFromExistingCam: FloatVectorProperty(
        name="Camera Color",
        description="Color of the chosen camera",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        precision=2,
        default=(1.0, 1.0, 1.0),
    )

    alignCamToView: BoolProperty(
        name="Align New Camera to Current View",
        description="If checked, the new camera is aligned to the current view."
        "\nIf not checked then the camera is placed at the cursor location",
        default=True,
    )

    addStoryboardGP: BoolProperty(
        name="Add Storyboard Grease Pencil",
        description="If checked, a grease pencil storyboard frame is created and parented to the specified camera",
        default=False,
    )

    @classmethod
    def description(self, context, properties):
        if "STORYBOARD" == properties.layout_mode:
            descr = "Add a new Storyboard Frame to the current take"
        else:
            descr = "Add a new shot as a Camera Shot"
        descr += "\nThe new shot is put after the selected shot"
        "\n+ Shift: Skip the options dialog box"
        return descr

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = config.getAddonProps(scene)
        prefs = config.getAddonPrefs()
        selectedShot = props.getSelectedShot()

        self.name = props.getShotPrefix((len(props.getShotsList()) + 1) * 10)

        # prefs.addShot_start = max(scene.frame_current, 10)

        # required otherwise start will be clamped to end value (cf prefs properties)
        prefs.addShot_end = 9999999

        if "STORYBOARD" == self.layout_mode:
            prefs.addShot_start = 100
            prefs.addShot_end = prefs.addShot_start + prefs.new_shot_duration
            self.addStoryboardGP = True
        else:
            if selectedShot is None:
                prefs.addShot_start = scene.frame_current
            else:
                prefs.addShot_start = selectedShot.end + 1

            prefs.addShot_end = prefs.addShot_start + prefs.new_shot_duration

            # self.addStoryboardGP = props.getCurrentLayout().display_storyboard_in_properties

        # self.cameraName = "NEW_CAMERA"
        # camName = props.getActiveCameraName()
        # if "" != camName:
        #     self.cameraName = camName

        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        self.cameraName = "NEW_CAMERA"
        self.cameraAssetName = "DEFAULT_CAMERA"

        #     cameras = props.getSceneCameras()
        #    # selectedObjs = []  #bpy.context.view_layer.objects.active    # wkip get the selection
        #     currentCam = None
        #     if context.view_layer.objects.active and (context.view_layer.objects.active).type == 'CAMERA':
        #     #if len(selectedObjs) == 1 and selectedObjs.name == bpy.context.scene.objects[self.cameraName]:
        #     #    currentCam =  bpy.context.scene.objects[self.cameraName]
        #         currentCam = context.view_layer.objects.active
        #     if currentCam:
        #         self.cameraName = currentCam.name
        #     elif 0 < len(cameras):
        #         self.cameraName = cameras[0].name

        # self.alignCamToView = not props.getCurrentLayout().display_storyboard_in_properties

        # self.addStoryboardGP = props.getCurrentLayout().display_storyboard_in_properties

        if event.shift and not event.ctrl and not event.alt:
            return self.execute(context)

        return wm.invoke_props_dialog(self, width=360)

    def draw(self, context):
        # scene = context.scene
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        isPrevizLayout = "PREVIZ" == self.layout_mode
        splitFactor = 0.3 if isPrevizLayout else 0.35
        layout = self.layout

        col = layout.box()
        # col = box.column(align=False)

        row = col.row()
        if isPrevizLayout:
            text = "Add a new shot to the current take:"
        else:
            text = "Add a new storyboard frame to the current take:"
        row.label(text=text)

        # row name #########################
        row = col.row()
        split = row.split(factor=splitFactor)
        subrow = split.row()
        subrow.alignment = "RIGHT"
        subrow.label(text="Shot Name:")
        split.prop(self, "name", text="")

        if isPrevizLayout:
            # doubleRow is used to reduce the size between rows #########
            col.separator(factor=0.1)
            doubleRow = col.column()
            # doubleRow.scale_y = 0.7

        # row start and end #########################
        if isPrevizLayout:
            row = doubleRow.row(align=True)
            mainRowSplit = row.split(factor=0.5)
            subSplitLeft = mainRowSplit.split(factor=0.26)
            subrow = subSplitLeft.row()
            # subrow.alignment = "RIGHT"
            subrow.label(text="Start:")
            row = subSplitLeft.row(align=True)
            row.prop(prefs, "addShot_start", text="")
            row.operator(
                "uas_shot_manager.shotadd_getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "addShot_start"

            subSplitRight = mainRowSplit.split(factor=0.26)
            subrow = subSplitRight.row()
            #  subrow.alignment = "RIGHT"
            subrow.separator(factor=0.5)
            subrow.label(text="End:")
            row = subSplitRight.row(align=True)
            row.prop(prefs, "addShot_end", text="")
            row.operator(
                "uas_shot_manager.shotadd_getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "addShot_end"
        else:
            row = col.row()
            split = row.split(factor=splitFactor)
            subrow = split.row()
            subrow.alignment = "RIGHT"
            subrow.label(text="At Current frame:")
            split.prop(self, "atCurrentFrame", text="")

        # row duration #########################
        if isPrevizLayout:
            row = doubleRow.row(align=False)
            mainRowSplit = row.split(factor=0.5)

            subSplitLeft = mainRowSplit.split(factor=0.4)
            subrow = subSplitLeft.row()
            # subrow.alignment = "RIGHT"
            subrow.label(text="Duration:")
            subrow = subSplitLeft.row()
            subrow.alignment = "RIGHT"
            duration = prefs.addShot_end - prefs.addShot_start + 1
            if duration <= 1:
                subrow.alert = True
            subrow.label(text=f"{duration} frame{'s' if duration > 1 else ''}")

        # row shot color #########################
        if not props.use_camera_color:
            subrow = mainRowSplit.row()
            subrow.separator(factor=0.5)
            subrow.label(text="Shot Color:")
            subrow.prop(self, "color", text="")

        if isPrevizLayout:
            # doubleRow is used to reduce the size between rows #########
            col.separator(factor=0.1)
            doubleRow = col.column()
            # doubleRow.scale_y = 0.7

            # row camera #########################
            row = doubleRow.row(align=True)
            mainRowSplit = row.split(factor=splitFactor)
            subrow = mainRowSplit.row()
            subrow.alignment = "RIGHT"
            subrow.label(text="Camera:")
            mainRowSplit.prop(self, "cameraName", text="")

            if props.use_project_settings and "" != props.project_cameraAssets_path:
                row = doubleRow.row()
                mainRowSplit = row.split(factor=splitFactor)
                subrow = mainRowSplit.row()
                subrow.alignment = "RIGHT"
                subrow.label(text="Camera Type:")
                mainRowSplit.prop(self, "cameraAssetName", text="")
                mainRowSplit.enabled = "NEW_CAMERA" == self.cameraName

            # row camera color ##########################################
            if props.use_camera_color:
                if "NEW_CAMERA" == self.cameraName:
                    row = doubleRow.row(align=False)
                    mainRowSplit = row.split(factor=splitFactor)
                    subrow = mainRowSplit.row()
                    subrow.alignment = "RIGHT"
                    subrow.label(text=" ")
                    subrow = mainRowSplit.row()
                    subrow.label(text="Camera Color:")
                    subrow.prop(self, "color", text="")
                else:
                    # row num shots using selected camera ###############
                    cam = context.scene.objects[self.cameraName]
                    row = doubleRow.row(align=False)
                    mainRowSplit = row.split(factor=splitFactor)
                    subrow = mainRowSplit.row()
                    subrow.alignment = "RIGHT"
                    subrow.label(text=" ")
                    subrow = mainRowSplit.row()
                    sharedCamsTupple = props.getShotsSharingCameraCount(cam, ignoreDisabled=False)
                    if 0 < sharedCamsTupple[0]:
                        usedStr = f"Also used by {sharedCamsTupple[0]} other shot"
                        if 1 < sharedCamsTupple[0]:
                            usedStr += "s"
                        usedStr += f"  in {sharedCamsTupple[1]} take"
                        if 1 < sharedCamsTupple[1]:
                            usedStr += "s"
                    else:
                        usedStr = "Not yet used by any shot"
                    subrow.label(text=usedStr)

                    # row camera color ##################################
                    row = doubleRow.row(align=False)
                    mainRowSplit = row.split(factor=splitFactor)
                    subrow = mainRowSplit.row()
                    subrow.enabled = False  # 0 == sharedCamsTupple[0]
                    subrow.alignment = "RIGHT"
                    subrow.label(text="Color:")
                    # idea was to prevent the modification of a camera color only for the used camera
                    # seems difficult to achieve so color change is not available
                    # self.colorFromExistingCam = bpy.context.scene.objects[self.cameraName].color[0:3] + (128, 128, 128)
                    # print(f" colc :{cam.color[0]}")
                    # lighten = 0.5
                    # disabledColor = (cam.color[0] + lighten, cam.color[1] + lighten, cam.color[2] + lighten)
                    # self.colorFromExistingCam = disabledColor
                    self.colorFromExistingCam = cam.color[0:3]
                    mainRowSplit.prop(self, "colorFromExistingCam", text="")

            # row camera position #######################################
            if "NEW_CAMERA" == self.cameraName:
                row = doubleRow.row(align=False)
                mainRowSplit = row.split(factor=splitFactor)
                subrow = mainRowSplit.row()
                subrow.alignment = "RIGHT"
                subrow.label(text=" ")
                mainRowSplit.prop(self, "alignCamToView", text="Align New Camera to View")

            if props.getCurrentLayout().display_storyboard_in_properties:
                col.separator(factor=0.1)
                row = col.row(align=True)
                mainRowSplit = row.split(factor=splitFactor)
                subrow = mainRowSplit.row()
                subrow.alignment = "RIGHT"
                subrow.label(text="Storyboard:")
                subrow = mainRowSplit.row()
                subrow.prop(self, "addStoryboardGP", text="Add Storyboard Frame")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        prefs = config.getAddonPrefs()
        selectedShotInd = props.getSelectedShotIndex()
        newShotInd = selectedShotInd + 1

        cam = None
        col = [self.color[0], self.color[1], self.color[2], 1]

        if "NEW_CAMERA" == self.cameraName:

            if props.use_project_settings and "" != props.project_cameraAssets_path:
                if "DEFAULT_CAMERA" == self.cameraAssetName:
                    cam = utils.create_new_camera("Cam_" + self.name)
                else:
                    # import from asset file
                    # if Path(props.project_cameraAssets_path).exists() and Path(props.project_cameraAssets_path).is_file():
                    # link all objects starting with 'A'
                    with bpy.data.libraries.load(props.project_cameraAssets_path, link=False, assets_only=False) as (
                        data_from,
                        data_to,
                    ):
                        for i, camName in enumerate(data_from.cameras):
                            if camName == self.cameraAssetName:
                                data_to.cameras = [data_from.cameras[i]]

                    camData = data_to.cameras[0]
                    cam = utils.create_new_camera("Cam_" + self.name, camData=camData)
            else:
                cam = utils.create_new_camera("Cam_" + self.name)

            if "PREVIZ" == self.layout_mode:
                if self.alignCamToView:
                    utils.makeCameraMatchViewport(context, cam)
            elif "STORYBOARD" == self.layout_mode:
                from math import radians

                cam.location = [0, 0, 0]
                cam.rotation_euler = (radians(90), 0.0, 0.0)
        else:
            cam = bpy.context.scene.objects[self.cameraName]
            if cam is None or "" == self.cameraName:
                utils.ShowMessageBox("Camera with specified name not found in scene", "New Shot Creation Canceled")
                return ()

            cam = bpy.context.scene.objects[self.cameraName]
            if props.use_camera_color:
                col[0] = cam.color[0]
                col[1] = cam.color[1]
                col[2] = cam.color[2]

        if "STORYBOARD" == self.layout_mode:
            startFr = scene.frame_current if self.atCurrentFrame else prefs.addShot_start
            endFr = startFr + prefs.addShot_start
        else:
            startFr = prefs.addShot_start
            endFr = prefs.addShot_end

        newShot = props.addShot(
            shotType=self.layout_mode,
            atIndex=newShotInd,
            name=self.name,
            # name=props.getUniqueShotName(self.name),
            start=startFr,
            end=endFr,
            #            camera  = scene.objects[ self.camera ] if self.camera else None,
            camera=cam,
            color=col,
            addGreasePencilStoryboard=self.addStoryboardGP,
        )

        # make new camera name match possible changes in shot name
        if "NEW_CAMERA" == self.cameraName and newShot.name != self.name:
            cam.name = "Cam_" + newShot.name
            cam.data.name = cam.name

        # update the frame grid
        if "STORYBOARD" == self.layout_mode:
            props.updateStoryboardGrid()

        utils.clear_selection()

        if props.getCurrentLayout().display_storyboard_in_properties:
            if self.addStoryboardGP:
                gp_child = newShot.getGreasePencilObject("STORYBOARD")
                utils.add_to_selection(gp_child)
                utils.setPropertyPanelContext(bpy.context, "DATA")
        else:
            utils.add_to_selection(cam)

        # removed, now done in camera HUD overlay tool
        # if 0 < props.getNumShots() and props.camera_hud_display_in_viewports:
        #     bpy.ops.uas_shot_manager.draw_camera_hud_in_viewports("INVOKE_DEFAULT")
        #     bpy.ops.uas_shot_manager.draw_camera_hud_in_pov("INVOKE_DEFAULT")

        # removed, now done in addShot
        # props.setCurrentShotByIndex(newShotInd)
        # props.setSelectedShotByIndex(newShotInd)

        return {"INTERFACE"}


class UAS_ShotManager_ShotDuplicate(Operator):
    bl_idname = "uas_shot_manager.shot_duplicate"
    bl_label = "Duplicate Selected Shot..."
    bl_description = "Duplicate the shot selected in the shot list."
    "\nThe new shot is put after the selected shot"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")
    startAtCurrentTime: BoolProperty(name="Start at Current Frame", default=False)
    addToEndOfList: BoolProperty(name="Add at the End of the List", default=False)

    duplicateCam: BoolProperty(name="Duplicate Camera", default=True)
    camName: StringProperty(name="Camera Name")
    useDifferentColor: BoolProperty(name="Slightly Different Color", default=True)
    duplicateStoryboardFrame: BoolProperty(name="Duplicate Storyboard Frame", default=True)

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        #    currentShot = props.getCurrentShot()
        selectedShot = props.getSelectedShot()
        if selectedShot is None:
            return {"CANCELLED"}
        self.name = selectedShot.name + "_duplicate"
        if selectedShot.camera is not None:
            self.camName = selectedShot.camera.name + "_duplicate"
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        selectedShot = props.getSelectedShot()
        shotIsStoryboard = selectedShot.isStoryboardType()

        layout = self.layout
        # scene = context.scene

        box = layout.box()

        mainCol = propertyColumn(box, padding_top=0.2, padding_left=0, padding_right=2)
        shType = "Storyboard" if shotIsStoryboard else "Camera"
        mainCol.label(text=f"New {shType} Shot:")

        propsCol = propertyColumn(mainCol, padding_top=0.8, padding_left=3)
        row = propsCol.row(align=True)
        row.label(text="Name:")
        row.scale_x = 1.6
        row.prop(self, "name", text="")

        #         propsCol = propertyColumn(mainCol, padding_top=0.2, padding_left=4)
        propsCol.separator(factor=1.0)

        # propsCol.prop(self, "useDifferentColor")
        if shotIsStoryboard:
            propsCol.prop(self, "startAtCurrentTime")
        propsCol.prop(self, "addToEndOfList")
        propsCol.separator(factor=1.0)
        propsCol.prop(self, "duplicateCam")

        camPropsCol = propertyColumn(propsCol, padding_left=3)
        row = camPropsCol.row()
        row.enabled = self.duplicateCam
        row.scale_x = 1.6
        row.label(text="New Camera Name:")
        row.scale_x = 2.4
        row.prop(self, "camName", text="")
        row.separator(factor=0.5)

        # propsCol.separator(factor=0.5)
        # camSubPropsCol = propertyColumn(camPropsCol, padding_left=3)
        if props.use_camera_color:
            camPropsCol.prop(self, "useDifferentColor", text="Slightly Change the Camera Identification Color")

        if selectedShot.hasStoryboardFrame():
            row = camPropsCol.row()
            row.enabled = self.duplicateCam
            row.prop(self, "duplicateStoryboardFrame")

        box.separator(factor=0.4)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        selectedShot = props.getSelectedShot()
        selectedShotInd = props.getSelectedShotIndex()

        if selectedShot is None:
            return {"CANCELLED"}

        newShotInd = len(props.get_shots()) if self.addToEndOfList else selectedShotInd + 1
        copyGreasePencil = self.duplicateCam and self.duplicateStoryboardFrame
        newShot = props.copyShot(
            selectedShot, atIndex=newShotInd, copyCamera=self.duplicateCam, copyGreasePencil=copyGreasePencil
        )

        # newShot.name = props.getUniqueShotName(self.name)
        newShot.name = self.name
        if self.startAtCurrentTime:
            newShot.start = context.scene.frame_current
            newShot.end = newShot.start + selectedShot.end - selectedShot.start

        if self.useDifferentColor:
            if props.use_camera_color:
                newShot.camera.color = slightlyRandomizeColor(selectedShot.camera.color, weight=0.55)

        # if self.duplicateCam and newShot.camera is not None:
        #     newCam = utils.duplicateObject(newShot.camera)
        #     newCam.name = self.camName
        #     newShot.camera = newCam

        props.setCurrentShotByIndex(newShotInd, setCamToViewport=False)
        props.setSelectedShotByIndex(newShotInd)

        return {"INTERFACE"}


# Not used anymore - Using UAS_ShotManager_ShotRemoveMultiple instead
class UAS_ShotManager_ShotRemove(Operator):
    bl_idname = "uas_shot_manager.shot_remove"
    bl_label = "Remove Selected Shot"
    bl_description = "Remove the shot selected in the shot list"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        scene = context.scene
        props = config.getAddonProps(scene)
        shots = props.get_shots()
        selectedShotInd = props.getSelectedShotIndex()
        props.removeShot_UIupdate(shots[selectedShotInd])

        return {"FINISHED"}


class UAS_ShotManager_ShotMove(Operator):
    """Move shots up and down in the take"""

    bl_idname = "uas_shot_manager.shot_move"
    bl_label = "Move Shot"
    bl_description = "Move selected shot up or down in the take, in other words before or after in the edit"
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "UP" == properties.action:
            descr = "Move shot up in the take list"
        elif "DOWN" == properties.action:
            descr = "Move shot down in the take list"
        return descr

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    def invoke(self, context, event):

        scene = context.scene
        props = config.getAddonProps(scene)

        shots = props.get_shots()
        # currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()

        movedShot = shots[selectedShotInd]
        if self.action == "UP":
            #    if 0 < selectedShotInd:
            movedShot = props.moveShotToIndex(movedShot, selectedShotInd - 1)
        elif self.action == "DOWN":
            #    if len(shots) - 1 > selectedShotInd:
            movedShot = props.moveShotToIndex(movedShot, selectedShotInd + 1)

        props.setCurrentShot(movedShot, setCamToViewport=False)
        props.setSelectedShot(movedShot)

        return {"FINISHED"}


########################
# for shot actions
########################


def convertMarkersFromCameraBindingToShots(scene):
    """Convert camera bindings to shots.
    New shots are added at the end of the shots list of the current take
    """
    props = config.getAddonProps(scene)
    prefs = config.getAddonPrefs()
    lastShotInd = props.getLastShotIndex()

    if len(scene.timeline_markers) <= 0:
        return

    # get the list of markers bound to cameras and sort them by time
    boundMarkers = []
    for m in scene.timeline_markers:
        #    _logger.debug_ext(f"Marker name: {m.name}, cam: {m.camera}", col="BLUE", form="BASIC")
        if m.camera is not None:
            boundMarkers.append(m)

    boundMarkers = utils_markers.sortMarkers(boundMarkers)

    # display sorted markers
    # for m in boundMarkers:
    #     _logger.debug_ext(f"Marker name: {m.name}, cam: {m.camera}", col="BLUE", form="BASIC")

    # create shot for each marker, even is some markers have the same camera
    for i, m in enumerate(boundMarkers):
        if i + 1 == len(boundMarkers):
            if m.frame <= scene.frame_end:
                duration = scene.frame_end - m.frame + 1
            else:
                duration = prefs.new_shot_duration
        else:
            duration = boundMarkers[i + 1].frame - boundMarkers[i].frame

        shotName = m.camera.name
        props.addShot(
            atIndex=lastShotInd + i + 1,
            camera=m.camera,
            name=shotName,
            start=boundMarkers[i].frame,
            end=boundMarkers[i].frame + duration - 1,
            color=(uniform(0, 1), uniform(0, 1), uniform(0, 1), 1),
        )

    currentShotInd = props.getCurrentShotIndex()
    if -1 == currentShotInd:
        props.setCurrentShotByIndex(0)
        props.setSelectedShotByIndex(0)


class UAS_ShotManager_CreateShotsFromEachCamera(Operator):
    bl_idname = "uas_shot_manager.create_shots_from_each_camera"
    bl_label = "Create Shots From Existing Cameras"
    bl_description = "Create a new shot for each camera in the scene.\nThe edit made with these shots will cover the current animation range"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        scene = context.scene
        props = config.getAddonProps(scene)
        currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()

        def _objectSortingFunc(obj):
            return obj.name

        cams = []
        for obj in scene.objects:
            if "CAMERA" == obj.type:
                cams.append(obj)
        cams = sorted(cams, key=_objectSortingFunc)

        if len(cams):
            duration = scene.frame_end - scene.frame_start + 1

            for i, cam in enumerate(cams):
                shotName = props.getShotPrefix((i + 1) * 10)
                props.addShot(
                    atIndex=selectedShotInd + i + 1,
                    camera=cam,
                    name=shotName,
                    start=scene.frame_start + i * int(duration / len(cams)),
                    end=scene.frame_start + (i + 1) * int(duration / len(cams)) - 1,
                    color=(uniform(0, 1), uniform(0, 1), uniform(0, 1), 1),
                )

            if -1 == currentShotInd:
                props.setCurrentShotByIndex(0)
                props.setSelectedShotByIndex(0)
                # wkipwkipwkip pas parfait, on devrait conserver la sel currente

        return {"FINISHED"}


class UAS_ShotManager_CreateNShots(Operator):
    bl_idname = "uas_shot_manager.create_n_shots"
    bl_label = "Create Specified Number of Shots..."
    bl_description = "Create a specified number of shots with new cameras or with the same one"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")
    cameraName: EnumProperty(items=list_cameras_for_new_shots, name="Camera", description="New Shot Camera")
    start: IntProperty(name="Start")
    duration: IntProperty(name="Duration", min=1)
    offsetFromPrevious: IntProperty(
        name="Offset From previous Shot",
        description="Number of frames from which the start of a shot will be offset from the end of the one preceding it",
        default=1,
    )
    count: IntProperty(name="Number of Shots to Create", min=1, default=4)

    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        description="Shot Color",
        min=0.0,
        max=1.0,
        precision=2,
        # default=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
        default=(1.0, 1.0, 1.0),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        self.name = props.project_naming_shot_format if props.use_project_settings else props.naming_shot_format

        self.start = max(context.scene.frame_current, 10)
        self.duration = prefs.new_shot_duration

        self.cameraName = "NEW_CAMERAS"
        # camName = props.getActiveCameraName()
        # if "" != camName:
        #     self.cameraName = camName

        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        return wm.invoke_props_dialog(self, width=360)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.label(text="Number of Shots:")
        col = grid_flow.column(align=False)
        col.prop(self, "count", text="")

        col.separator(factor=2)
        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Shot Identifier:")
        col = grid_flow.column(align=False)
        idRow = col.row()
        idRow.enabled = not props.use_project_settings
        idRow.prop(self, "name", text="")
        col = grid_flow.column(align=False)
        col.label(text="Camera:")
        col = grid_flow.column(align=False)
        col.prop(self, "cameraName", text="")

        col.separator(factor=1)
        col = grid_flow.column(align=False)
        col.label(text="Start:")
        col = grid_flow.column(align=False)
        col.prop(self, "start", text="")
        col = grid_flow.column(align=False)
        col.label(text="Duration:")
        col = grid_flow.column(align=False)
        col.prop(self, "duration", text="")
        col = grid_flow.column(align=False)
        col.label(text="Offset From Previous:")
        col = grid_flow.column(align=False)
        col.prop(self, "offsetFromPrevious", text="")

        if not props.use_camera_color:
            col = grid_flow.column(align=False)
            col.label(text="Color:")
            col = grid_flow.column(align=True)
            col.prop(self, "color", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        selectedShotInd = props.getSelectedShotIndex()
        newShotInd = selectedShotInd + 1

        cam = None
        col = [self.color[0], self.color[1], self.color[2], 1]

        if "" != self.cameraName and "NEW_CAMERAS" != self.cameraName:
            cam = bpy.context.scene.objects[self.cameraName]
            if props.use_camera_color:
                col[0] = cam.color[0]
                col[1] = cam.color[1]
                col[2] = cam.color[2]

        for i in range(1, self.count + 1):
            if props.use_project_settings:
                newShotName = props.getUniqueShotName(props.getShotPrefix((len(props.getShotsList()) + 1) * 10))
            else:
                newShotName = props.getUniqueShotName(props._replaceHashByNumber(self.name, (i + 1) * 10))
            startFrame = self.start + (i - 1) * (self.duration - 1 + self.offsetFromPrevious)
            endFrame = startFrame + self.duration - 1

            if "NEW_CAMERAS" == self.cameraName:
                cam = utils.create_new_camera("Cam_" + newShotName)

            props.addShot(
                atIndex=newShotInd,
                name=newShotName,
                start=startFrame,
                end=endFrame,
                camera=cam,
                color=cam.color,
            )
            newShotInd += 1

        props.setCurrentShotByIndex(newShotInd - 1)
        props.setSelectedShotByIndex(newShotInd - 1)
        bpy.ops.ed.undo_push()
        return {"INTERFACE"}


def list_target_takes(self, context):
    props = config.getAddonProps(context.scene)
    takes = props.getTakes()
    currentTake = props.getCurrentTake()
    res = list()
    for i, t in enumerate(takes):
        if t != currentTake:
            # res.append((t.getName_PathCompliant(), t.name, "", i))
            res.append((t.name, t.name, "", i))
    return res


def list_target_take_shots(self, context):
    """first index is -1 to define the take start"""
    props = config.getAddonProps(context.scene)
    take = props.getTakeByName(self.targetTake)
    res = list()
    if take is not None:
        res.append(("-1", "Edit Start", "Insert duplicated shots right after the start of the take", 0))
        for i, s in enumerate(take.shots):
            res.append((str(i), s.name, "", i + 1))

    # res = list()
    # res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
    return res


class UAS_ShotManager_DuplicateShotsToOtherTake(Operator):
    bl_idname = "uas_shot_manager.shot_duplicates_to_other_take"
    bl_label = "Duplicate / Move Enabled Shots to Another Take..."
    bl_description = "Duplicate or move enabled shots to the specified take"
    bl_options = {"REGISTER", "UNDO"}

    mode: EnumProperty(
        name="Mode",
        description="Duplicate or Move shots",
        items=(("DUPLICATE", "Duplicate", ""), ("MOVE", "Move", "")),
        default="DUPLICATE",
    )

    targetTake: EnumProperty(
        name="Target Take",
        description="Take in which the shots will be duplicated",
        items=(list_target_takes),
    )

    insertAfterShot: EnumProperty(
        name="Insert After Shot",
        description="Shot in the target take after which the shots will be duplicated",
        items=(list_target_take_shots),
    )

    duplicateCam: BoolProperty(name="Duplicate Cameras", default=False)

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        # shots = context.scene.UAS_shot_manager_props.get_shots()
        shots = props.getShotsList(ignoreDisabled=True)
        takes = props.getTakes()
        return len(shots) and len(takes) > 1

    def invoke(self, context, event):
        targetTakes = list_target_takes(self, context)
        self.targetTake = targetTakes[0][0]
        afterShots = list_target_take_shots(self, context)
        self.insertAfterShot = afterShots[0][0]

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Mode:")
        col = grid_flow.column(align=True)
        col.prop(self, "mode", text="")
        col.separator()

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Target Take:")
        col = grid_flow.column(align=True)
        col.prop(self, "targetTake", text="")

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)
        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Insert After Shot:")
        col = grid_flow.column(align=True)
        col.prop(self, "insertAfterShot", text="")

        if "DUPLICATE" == self.mode:
            row = box.row(align=True)
            row.separator(factor=2.5)
            subgrid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
            subgrid_flow.prop(self, "duplicateCam")

        layout.separator()

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        enabledShots = props.getShotsList(ignoreDisabled=True)
        targetTakeInd = props.getTakeIndexByName(self.targetTake)
        # print(f"targetTakeInd: {targetTakeInd}")
        # print(f"insertAfterShot: {self.insertAfterShot}")

        insertAfterShotInd = int(self.insertAfterShot) + 1
        insertAtInd = insertAfterShotInd
        for shot in enabledShots:
            # print(f"insertAtInd: {insertAtInd}")
            props.copyShot(shot, atIndex=insertAtInd, copyCamera=self.duplicateCam, targetTakeIndex=targetTakeInd)
            insertAtInd += 1

        # delete source shots
        if "DUPLICATE" == self.mode:
            props.setCurrentTakeByIndex(targetTakeInd)
            props.setCurrentShotByIndex(insertAfterShotInd)
            props.setSelectedShotByIndex(insertAfterShotInd)
        else:  # move
            for i, shot in enumerate(reversed(enabledShots)):
                print(f"shot to remove: {shot.name}, {shot.parentScene}, i:{i}")
                props.removeShot_UIupdate(shot)

        return {"INTERFACE"}


class UAS_ShotManager_ShotRemoveMultiple(Operator):
    bl_idname = "uas_shot_manager.remove_multiple_shots"
    bl_label = "Remove Shot(s)..."
    bl_description = "Remove the specified shot(s) from the current take" "\n+ Shift: Skip the confirmation dialog box"
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(
        items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", ""), ("SELECTED", "SELECTED", "")), default="ALL"
    )

    deleteCameras: BoolProperty(
        name="Delete Shots Cameras",
        description="When deleting a shot, also delete the associated camera, if not used by another shot"
        "\nand its storyboard frame, if any",
        default=False,
    )

    skipDialogBox: BoolProperty(default=False)

    @classmethod
    def description(self, context, properties):
        descr = "_"
        # print("properties: ", properties)
        # print("properties action: ", properties.action)
        if "ALL" == properties.action:
            descr = "Remove all shots from the current take"
        elif "DISABLED" == properties.action:
            descr = "Remove only disabled shots from the current take"
        elif "SELECTED" == properties.action:
            descr = "Remove the shot selected in the shot list"
        descr += "\n+ Shift: Skip the confirmation dialog box"
        return descr

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()
        self.deleteCameras = prefs.removeShot_deleteCameras
        if event.shift and not event.ctrl and not event.alt:
            self.skipDialogBox = True
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        txtS = "" if "SELECTED" == self.action else "s"
        col.label(text=f"Also Remove Associated Camera{txtS}:")
        col = grid_flow.column(align=False)
        col.prop(self, "deleteCameras", text="")

        row = box.row()
        row.separator(factor=2)
        col = row.column(align=True)
        col.enabled = False
        col.label(text="Only cameras that are not used by any other shots can be deleted.")
        col.label(text="Storyboard frames parented to the removed cameras will also be deleted.")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        prefs = config.getAddonPrefs()
        shots = props.get_shots()
        currentShotInd = props.current_shot_index
        selectedShotInd = props.getSelectedShotIndex()

        # props.setCurrentShotByIndex(-1, setCamToViewport=False)

        try:
            item = shots[selectedShotInd]
            item.name
        except IndexError:
            pass
        else:
            if "ALL" == self.action:
                props.setCurrentShotByIndex(-1, setCamToViewport=False)
                i = len(shots) - 1
                while i > -1:
                    # if self.deleteCameras:
                    #     props.deleteShotCamera(shots[i])
                    # shots.remove(i)
                    props.removeShotByIndex(i, deleteCamera=self.deleteCameras)
                    i -= 1
                props.setSelectedShotByIndex(-1)
            elif "DISABLED" == self.action:
                props.setCurrentShotByIndex(-1, setCamToViewport=False)
                i = len(shots) - 1
                while i > -1:
                    if not shots[i].enabled:
                        if currentShotInd == len(shots) - 1 and currentShotInd == selectedShotInd:
                            pass
                        # if self.deleteCameras:
                        #     props.deleteShotCamera(shots[i])
                        # shots.remove(i)
                        props.removeShotByIndex(i, deleteCamera=self.deleteCameras)
                    i -= 1
                if 0 < len(shots):  # wkip pas parfait, on devrait conserver la sel currente
                    props.setCurrentShotByIndex(0, setCamToViewport=False)
                    props.setSelectedShotByIndex(0)
            elif "SELECTED" == self.action:
                props.removeShot_UIupdate(shots[selectedShotInd], deleteCamera=self.deleteCameras)

            if not self.skipDialogBox:
                prefs.removeShot_deleteCameras = self.deleteCameras

        #  print(" ** removed shots, len(props.get_shots()): ", len(props.get_shots()))

        return {"INTERFACE"}


class UAS_ShotManager_Shots_SelectCamera(Operator):
    bl_idname = "uas_shot_manager.shots_selectcamera"
    bl_label = "Select Camera"
    bl_description = "Deselect all and select specified camera"
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty(default=0)

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.setSelectedShotByIndex(self.index)
        # NOTE: we use context.object here instead of context.active_object because
        # when the eye icon of the object is closed (meaning object.hide_get() == True)
        # then context.active_object is None
        # if context.active_object is not None and context.active_object.mode != "OBJECT":
        if context.object is not None and context.object.mode != "OBJECT":
            if not context.object.visible_get():
                context.object.hide_viewport = False
            bpy.ops.object.mode_set(mode="OBJECT")
        props.selectCamera(self.index)
        return {"INTERFACE"}


class UAS_ShotManager_Shots_RemoveCamera(Operator):
    bl_idname = "uas_shot_manager.shots_removecamera"
    bl_label = "Remove Camera From All Shots..."
    bl_description = "Remove the camera of the selected shot from all the shots."
    bl_options = {"REGISTER", "UNDO"}

    removeFromOtherTakes: BoolProperty(name="Also Remove From Other Takes", default=False)

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        selectedShot = props.getSelectedShot()
        if selectedShot is None:
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "removeFromOtherTakes")

        layout.separator()

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        selectedShot = props.getSelectedShot()

        if selectedShot is None:
            return {"CANCELLED"}

        cam = selectedShot.camera
        if self.removeFromOtherTakes:
            for t in props.takes:
                for s in t.shots:
                    if s.camera == cam:
                        s.camera = None
        else:
            currentTake = props.getCurrentTake()
            if currentTake is not None:
                for s in currentTake.shots:
                    if s.camera == cam:
                        s.camera = None

        return {"INTERFACE"}


class UAS_ShotManager_UniqueCameras(Operator):
    bl_idname = "uas_shot_manager.unique_cameras"
    bl_label = "Make All Cameras Unique"
    bl_description = "Make cameras unique per shot"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        shots = props.get_shots()
        return len(shots)

    @staticmethod
    def unique_cam_name(cam_name):
        return utils.unique_object_name(cam_name)

    def execute(self, context):
        # NOTE: brute force here - could be optimized
        scene = context.scene
        props = config.getAddonProps(scene)
        takes = props.getTakes()
        # new_cam_from_shots = dict()
        # objects = bpy.data.objects
        # existing_cameras = set()
        for take in takes:
            for shot in take.shots:
                shot.makeCameraUnique()

                # if shot.camera is None:
                #     continue
                # camName = shot.camera.name

                # if camName in existing_cameras and camName in objects:
                #     if shot.name in new_cam_from_shots:
                #         shot.camera = new_cam_from_shots[shot.name]
                #     else:
                #         # cam_obj = scene.objects[camName]
                #         # new_cam = utils.duplicateObject(cam_obj)
                #         # new_cam.name = self.unique_cam_name(f"{camName}_{shot.name}")
                #         # new_cam.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1)
                #         # # scene.collection.objects.link(new_cam)

                #         # shot.camera = new_cam
                #         new_cam = shot.makeCameraUnique()
                #         new_cam_from_shots[shot.name] = new_cam.name

                # new_cam_from_shots[shot.name] = shot.camera
                # existing_cameras.add(camName)

        return {"INTERFACE"}


_classes = (
    # # shot maniputlation
    UAS_ShotManager_SetShotStart,
    # # shot items
    UAS_ShotManager_SetCurrentShot,
    UAS_ShotManager_ToggleContinuousGPEditingMode,
    UAS_ShotManager_ShotDuration,
    UAS_ShotManager_GetSetCurrentFrame,
    UAS_ShotManager_NoLens,
    UAS_ShotManager_NoDisplaySize,
    UAS_ShotManager_ShotTimeInEdit,
    UAS_ShotManager_ShowNotes,
    UAS_ShotManager_ListCameraInstances,
    UAS_ShotManager_MakeShotCameraUnique,
    # # shot manipulation
    UAS_ShotManager_ShotAdd_GetCurrentFrameFor,
    UAS_ShotManager_ShotAdd,
    UAS_ShotManager_ShotDuplicate,
    UAS_ShotManager_ShotRemove,
    UAS_ShotManager_ShotMove,
    # # shot actions
    UAS_ShotManager_CreateShotsFromEachCamera,
    UAS_ShotManager_CreateNShots,
    UAS_ShotManager_DuplicateShotsToOtherTake,
    UAS_ShotManager_ShotRemoveMultiple,
    UAS_ShotManager_Shots_SelectCamera,
    UAS_ShotManager_Shots_RemoveCamera,
    UAS_ShotManager_UniqueCameras,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
