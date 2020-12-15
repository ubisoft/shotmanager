import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatVectorProperty, PointerProperty

from random import uniform
import json

from shotmanager.utils import utils


def list_cameras(self, context):
    res = list()
    for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        res.append((cam.name, cam.name, "", i))

    return res


########################
# for shot items
########################


class UAS_ShotManager_SetCurrentShot(Operator):
    """Set the specifed shot as current
    """

    bl_idname = "uas_shot_manager.set_current_shot"
    bl_label = "Set current Shot"
    bl_description = "Click: Set the shot as the current one.\nShift + Click: Toggle shot Disabled state.\nCtrl + Click: Select Shot Camera.\nAlt + Click: Set the shot as current one but do not change time"
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty()

    def adjust_dopesheet_view(self, context, shot):
        ctx = context.copy()
        for area in context.screen.areas:
            if area.type == "DOPESHEET_EDITOR":
                ctx["area"] = area
                for region in area.regions:
                    if region.type == "WINDOW":
                        ctx["region"] = region
                        bpy.ops.view2d.reset(ctx)
                        context.scene.frame_current = shot.start + (shot.end - shot.start) // 2
                        bpy.ops.action.view_frame(ctx)
                        bpy.ops.view2d.zoom(ctx, deltax=(region.width // 2 - (shot.end - shot.start) // 2) - 10)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        self.adjust_dopesheet_view(context, props.getShotByIndex(self.index))
        if event.shift and not event.ctrl and not event.alt:
            shot = props.getShotByIndex(self.index)
            shot.enabled = not shot.enabled
        elif event.ctrl and not event.shift and not event.alt:
            context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
            context.scene.UAS_shot_manager_props.selectCamera(self.index)
        elif event.alt and not event.shift and not event.ctrl:
            props.setCurrentShotByIndex(self.index, changeTime=False, area=context.area)
            props.setSelectedShotByIndex(self.index)
        else:
            props.setCurrentShotByIndex(self.index, area=context.area)
            props.setSelectedShotByIndex(self.index)

        return {"FINISHED"}


class UAS_ShotManager_ShotDuration(Operator):
    bl_idname = "uas_shot_manager.shot_duration"
    bl_label = "Shot Duration"
    bl_description = "Shot Duration, given by end - start + 1"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty(default=0)

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
        return {"FINISHED"}


class UAS_ShotManager_GetSetCurrentFrame(Operator):
    bl_idname = "uas_shot_manager.getsetcurrentframe"
    bl_label = "Get/Set Current Frame"
    bl_description = "Click: Set current frame with value.\nShift + Click: Get current frame for value"
    bl_options = {"INTERNAL"}

    # shotSource is an array [index of shot, 0 (for start) or 1 (for end)]
    shotSource: StringProperty(default="")

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
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


class UAS_ShotManager_ShotTimeInEdit(Operator):
    bl_idname = "uas_shot_manager.shottimeinedit"
    bl_label = "Toggle Edit Times"
    bl_description = "Display the timings of the shots in the edit reference time"
    bl_options = {"INTERNAL"}

    shotSource: StringProperty(default="")

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
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
    bl_label = "Show Shot notes"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shot = props.getShotByIndex(self.index)
        shot.selectShotInUI()
        return {"FINISHED"}


class UAS_ShotManager_ListCameraInstances(Operator):
    bl_idname = "uas_shot_manager.list_camera_instances"
    bl_label = "Shots Using This Camera "
    bl_description = "Number of shots using this camera in all the takes (this shot included)"
    bl_options = {"INTERNAL"}

    index: IntProperty(default=0)

    def invoke(self, context, event):
        wm = context.window_manager
        context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        props = context.scene.UAS_shot_manager_props
        layout = self.layout
        row = layout.row()
        shot = props.getShotByIndex(self.index)
        if shot.camera is not None:
            numSharedCam = props.getNumSharedCamera(shot.camera) - 1
            if 0 < numSharedCam:
                row.label(text=f"Camera shared with {numSharedCam} other shot(s)")
                row = layout.row()
                row.label(text=f"from this take or other ones")
                row = layout.row()
                row.operator("uas_shot_manager.make_shot_camera_unique").shotName = props.getShotByIndex(
                    self.index
                ).name
            else:
                row.label(text=f"Camera used only in this shot, only in this take")
        else:
            row.label(text=f"No camera defined")

    def execute(self, context):
        return {"FINISHED"}


class UAS_ShotManager_MakeShotCameraUnique(Operator):
    bl_idname = "uas_shot_manager.make_shot_camera_unique"
    bl_label = "Make Shot Camera Unique"
    bl_description = "If the camera is also used by another shot of the scene then it gets duplicated"
    bl_options = {"INTERNAL", "UNDO"}

    shotName: StringProperty(default="")

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props
        # selectedShot = props.getSelectedShot()
        # selectedShotInd = props.getSelectedShotIndex()

        shot = props.getShotByName(self.shotName)
        if shot is not None:
            shot.makeCameraUnique()
        return {"FINISHED"}


########################
# for shot manipulation
########################


def list_cameras_for_new_shot(self, context):
    res = list()
    res.append(("NEW_CAMERA", "New Camera", "Create new camera", 0))
    for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
        res.append(
            (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
        )

    return res


class UAS_ShotManager_ShotAdd_GetCurrentFrameFor(Operator):
    bl_idname = "uas_shot_manager.shotadd_getcurrentframefor"
    bl_label = "Get Current Frame"
    bl_description = "Use the current frame for the specifed component"
    bl_options = {"INTERNAL", "UNDO"}

    propertyToUpdate: StringProperty()

    def execute(self, context):
        scene = context.scene
        # props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences

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
    bl_label = "Add New Shot"
    bl_description = (
        "Add a new shot starting at the current frame and using the selected camera"
        "\nThe new shot is put after the selected shot"
    )
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name")
    cameraName: EnumProperty(items=list_cameras_for_new_shot, name="Camera", description="New Shot Camera")

    color: FloatVectorProperty(
        name="Shot Color",
        description="According to your preferences it can be a unique shot color\nor the color of the camera object (default)",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        precision=2,
        # default=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
        default=(1.0, 1.0, 1.0),
    )
    colorFromExistingCam: FloatVectorProperty(
        name="Shot Color",
        description="Color of the chosen camera",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        precision=2,
        default=(1.0, 1.0, 1.0),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        selectedShot = props.getSelectedShot()

        # self.name = f"{props.new_shot_prefix}{len ( props.getShotsList() ) + 1:02}" + "0"
        self.name = (props.project_shot_format.split("_")[2]).format((len(props.getShotsList()) + 1) * 10)

        # prefs.addShot_start = max(scene.frame_current, 10)

        # required otherwise start will be clamped to end value (cf prefs properties)
        prefs.addShot_end = 9999999

        if selectedShot is None:
            prefs.addShot_start = scene.frame_current
        else:
            prefs.addShot_start = selectedShot.end + 1

        prefs.addShot_end = prefs.addShot_start + prefs.new_shot_duration

        camName = props.getActiveCameraName()
        if "" != camName:
            self.cameraName = camName

        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        self.cameraName = "NEW_CAMERA"
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

        return wm.invoke_props_dialog(self)

    def draw(self, context):
        # scene = context.scene
        # props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences

        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Shot Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")

        col.separator(factor=1)
        col = grid_flow.column(align=False)
        col.label(text="Start:")
        col = grid_flow.column(align=False)
        row = col.row(align=True)
        row.prop(prefs, "addShot_start", text="")
        row.operator(
            "uas_shot_manager.shotadd_getcurrentframefor", text="", icon="TRIA_UP_BAR"
        ).propertyToUpdate = "addShot_start"

        col.separator(factor=1)
        col = grid_flow.column(align=False)
        col.label(text="End:")
        col = grid_flow.column(align=False)
        row = col.row(align=True)
        row.prop(prefs, "addShot_end", text="")
        row.operator(
            "uas_shot_manager.shotadd_getcurrentframefor", text="", icon="TRIA_UP_BAR"
        ).propertyToUpdate = "addShot_end"

        col.separator()
        col = grid_flow.column(align=False)
        col.label(text="Camera:")
        col = grid_flow.column(align=False)
        col.prop(self, "cameraName", text="")

        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        grid_flow.enabled = not context.scene.UAS_shot_manager_props.use_camera_color or "NEW_CAMERA" == self.cameraName
        col = grid_flow.column(align=False)
        col.label(text="Color:")
        col = grid_flow.column(align=True)
        if "NEW_CAMERA" == self.cameraName:
            col.prop(self, "color", text="")
        else:
            self.colorFromExistingCam = bpy.context.scene.objects[self.cameraName].color[0:3]
            col.prop(self, "colorFromExistingCam", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences
        selectedShotInd = props.getSelectedShotIndex()
        newShotInd = selectedShotInd + 1

        cam = None
        col = [self.color[0], self.color[1], self.color[2], 1]

        if "NEW_CAMERA" == self.cameraName:
            cam = utils.create_new_camera("Cam_" + self.name)
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

        newShot = props.addShot(
            atIndex=newShotInd,
            name=self.name,
            # name=props.getUniqueShotName(self.name),
            start=prefs.addShot_start,
            end=prefs.addShot_end,
            #            camera  = scene.objects[ self.camera ] if self.camera else None,
            camera=cam,
            color=col,
        )

        # make new camera name match possible changes in shot name
        if "NEW_CAMERA" == self.cameraName and newShot.name != self.name:
            cam.name = "Cam_" + newShot.name
            cam.data.name = cam.name

        utils.clear_selection()
        utils.add_to_selection(cam)

        if 0 < props.getNumShots() and props.display_shotname_in_3dviewport:
            bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")
            bpy.ops.uas_shot_manager.draw_hud("INVOKE_DEFAULT")

        # removed, now done in addShot
        # props.setCurrentShotByIndex(newShotInd)
        # props.setSelectedShotByIndex(newShotInd)

        return {"FINISHED"}


class UAS_ShotManager_ShotDuplicate(Operator):
    bl_idname = "uas_shot_manager.shot_duplicate"
    bl_label = "Duplicate Selected Shot"
    bl_description = "Duplicate the shot selected in the shot list." "\nThe new shot is put after the selected shot"
    bl_options = {"INTERNAL", "UNDO"}

    name: StringProperty(name="Name")
    startAtCurrentTime: BoolProperty(name="Start At Current Frame", default=True)
    addToEndOfList: BoolProperty(name="Add At The End Of The List")
    duplicateCam: BoolProperty(name="Duplicate Camera")
    camName: StringProperty(name="Camera Name")

    @classmethod
    def poll(cls, context):
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        #    currentShot = context.scene.UAS_shot_manager_props.getCurrentShot()
        selectedShot = context.scene.UAS_shot_manager_props.getSelectedShot()
        if selectedShot is None:
            return {"CANCELLED"}
        self.name = selectedShot.name + "_duplicate"
        if selectedShot.camera is not None:
            self.camName = selectedShot.camera.name + "_duplicate"
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        box = layout.box()
        box.separator(factor=0.2)
        row = box.row(align=True)
        row.label(text="New Shot Name:")
        row.scale_x = 1.6
        row.prop(self, "name", text="")

        box.separator(factor=0.1)
        row = box.row(align=True)
        row.separator(factor=2.5)
        subgrid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
        # subgrid_flow.separator( factor=0.5)
        # subgrid_flow.use_property_split = True
        subgrid_flow.prop(self, "startAtCurrentTime")
        subgrid_flow.prop(self, "addToEndOfList")
        subgrid_flow.separator(factor=1.0)
        subgrid_flow.prop(self, "duplicateCam")

        row = box.row()
        row.enabled = self.duplicateCam
        row.scale_x = 1.6
        row.separator(factor=2.0)
        row.label(text="New Camera Name:")
        row.scale_x = 2.4
        row.prop(self, "camName", text="")
        row.separator(factor=0.5)

        box.separator(factor=0.4)

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props
        selectedShot = props.getSelectedShot()
        selectedShotInd = props.getSelectedShotIndex()

        if selectedShot is None:
            return {"CANCELLED"}

        newShotInd = len(props.get_shots()) if self.addToEndOfList else selectedShotInd + 1
        newShot = props.copyShot(selectedShot, atIndex=newShotInd, copyCamera=self.duplicateCam)

        # newShot.name = props.getUniqueShotName(self.name)
        newShot.name = self.name
        if self.startAtCurrentTime:
            newShot.start = context.scene.frame_current
            newShot.end = newShot.start + selectedShot.end - selectedShot.start

        # if self.duplicateCam and newShot.camera is not None:
        #     newCam = utils.duplicateObject(newShot.camera)
        #     newCam.name = self.camName
        #     newShot.camera = newCam

        props.setCurrentShotByIndex(newShotInd)
        props.setSelectedShotByIndex(newShotInd)

        return {"FINISHED"}


class UAS_ShotManager_ShotRemove(Operator):
    bl_idname = "uas_shot_manager.shot_remove"
    bl_label = "Remove Selected Shot"
    bl_description = "Remove the shot selected in the shot list."
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        shots = props.get_shots()
        for s in shots:
            print(f"* Shot Name: {s.name}")
        selectedShotInd = props.getSelectedShotIndex()
        print(f"* selectedShotInd: {selectedShotInd}")

        props.removeShot(shots[selectedShotInd])

        return {"FINISHED"}


class UAS_ShotManager_ShotMove(Operator):
    """Move shots up and down in the take"""

    bl_idname = "uas_shot_manager.shot_move"
    bl_label = "Move Shot"
    bl_description = "Move selected shot up or down in the take, in other words before or after in the edit"
    bl_options = {"INTERNAL", "UNDO"}

    action: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

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
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    def invoke(self, context, event):

        scene = context.scene
        props = scene.UAS_shot_manager_props

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

        props.setCurrentShot(movedShot)
        props.setSelectedShot(movedShot)

        return {"FINISHED"}


########################
# for shot actions
########################


class UAS_ShotManager_CreateShotsFromEachCamera(Operator):
    bl_idname = "uas_shot_manager.create_shots_from_each_camera"
    bl_label = "Create Shots From Existing Cameras"
    bl_description = "Create a new shot for each camera in the scene.\nThe edit made with these shots will cover the current animation range."
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props
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
                shotName = props.new_shot_prefix + f"{(i + 1):02d}" + "0"
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
                # wkip pas parfait, on devrait conserver la sel currente

        return {"FINISHED"}


class UAS_ShotManager_CreateNShots(Operator):
    bl_idname = "uas_shot_manager.create_n_shots"
    bl_label = "Create Specifed Number of Shots..."
    bl_description = "Create a specified number of shots with the same camera"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")
    cameraName: EnumProperty(items=list_cameras, name="Camera", description="Select a Camera")
    start: IntProperty(name="Start")
    duration: IntProperty(name="Duration", min=1)
    offsetFromPrevious: IntProperty(
        name="Offset From previous Shot",
        description="Number of frames from which the start of a whot will be offset from the end of the one preceding it",
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
        props = context.scene.UAS_shot_manager_props
        prefs = context.preferences.addons["shotmanager"].preferences

        # self.name = f"{props.new_shot_prefix}{len ( props.getShotsList() ) + 1:02}" + "0"
        self.name = (props.project_shot_format.split("_")[2]).format((len(props.getShotsList()) + 1) * 10)
        self.start = max(context.scene.frame_current, 10)
        self.duration = prefs.new_shot_duration

        camName = props.getActiveCameraName()
        if "" != camName:
            self.cameraName = camName

        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

        return wm.invoke_props_dialog(self)

    def draw(self, context):
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
        col.label(text="New Shot Name:")
        col = grid_flow.column(align=False)
        col.prop(self, "name", text="")
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

        if not context.scene.UAS_shot_manager_props.use_camera_color:
            col = grid_flow.column(align=False)
            col.label(text="Color:")
            col = grid_flow.column(align=True)
            col.prop(self, "color", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        selectedShotInd = props.getSelectedShotIndex()
        newShotInd = selectedShotInd + 1

        cam = None
        col = [self.color[0], self.color[1], self.color[2], 1]

        if "" != self.cameraName:
            cam = bpy.context.scene.objects[self.cameraName]
            if props.use_camera_color:
                col[0] = cam.color[0]
                col[1] = cam.color[1]
                col[2] = cam.color[2]

        for i in range(1, self.count + 1):
            startFrame = self.start + (i - 1) * (self.duration - 1 + self.offsetFromPrevious)
            endFrame = startFrame + self.duration - 1

            props.addShot(
                atIndex=newShotInd,
                name=props.getUniqueShotName(props.project_shot_format.split("_")[2]).format(
                    (len(props.getShotsList()) + 1) * 10
                ),
                start=startFrame,
                end=endFrame,
                camera=cam,
                color=col,
            )
            newShotInd += 1

        props.setCurrentShotByIndex(newShotInd - 1)
        props.setSelectedShotByIndex(newShotInd - 1)
        bpy.ops.ed.undo_push()
        return {"FINISHED"}


def list_target_takes(self, context):
    props = context.scene.UAS_shot_manager_props
    takes = props.getTakes()
    currentTake = props.getCurrentTake()
    res = list()
    for i, t in enumerate(takes):
        if t != currentTake:
            # res.append((t.getName_PathCompliant(), t.name, "", i))
            res.append((t.name, t.name, "", i))
    return res


def list_target_take_shots(self, context):
    """ first index is -1 to define the take start
    """
    props = context.scene.UAS_shot_manager_props
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
    bl_options = {"INTERNAL", "UNDO"}

    mode: EnumProperty(
        name="Mode",
        description="Duplicate or Move shots",
        items=(("DUPLICATE", "Duplicate", ""), ("MOVE", "Move", "")),
        default="DUPLICATE",
    )

    targetTake: EnumProperty(
        name="Target Take", description="Take in which the shots will be duplicated", items=(list_target_takes),
    )

    insertAfterShot: EnumProperty(
        name="Insert After Shot",
        description="Shot in the target take after which the shots will be duplicated",
        items=(list_target_take_shots),
    )

    duplicateCam: BoolProperty(name="Duplicate Cameras", default=False)

    @classmethod
    def poll(cls, context):
        # shots = context.scene.UAS_shot_manager_props.get_shots()
        shots = context.scene.UAS_shot_manager_props.getShotsList(ignoreDisabled=True)
        takes = context.scene.UAS_shot_manager_props.getTakes()
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
        props = context.scene.UAS_shot_manager_props
        enabledShots = props.getShotsList(ignoreDisabled=True)
        targetTakeInd = props.getTakeIndexByName(self.targetTake)
        # print(f"targetTakeInd: {targetTakeInd}")
        # print(f"insertAfterShot: {self.insertAfterShot}")

        insertAfterShotInd = int(self.insertAfterShot) + 1
        insertAtInd = insertAfterShotInd
        copyCam = "DUPLICATE" == self.mode and self.duplicateCam
        for shot in enabledShots:
            # print(f"insertAtInd: {insertAtInd}")
            newShot = props.copyShot(
                shot, atIndex=insertAtInd, copyCamera=self.duplicateCam, targetTakeIndex=targetTakeInd
            )
            insertAtInd += 1

        # delete source shots
        if "DUPLICATE" == self.mode:
            props.setCurrentTakeByIndex(targetTakeInd)
            props.setCurrentShotByIndex(insertAfterShotInd)
            props.setSelectedShotByIndex(insertAfterShotInd)
        else:  # move
            for i, shot in enumerate(reversed(enabledShots)):
                print(f"shot to remove: {shot.name}, {shot.parentScene}, i:{i}")
                props.removeShot(shot)

        return {"FINISHED"}


class UAS_ShotManager_ShotRemoveMultiple(Operator):
    bl_idname = "uas_shot_manager.remove_multiple_shots"
    bl_label = "Remove Shots"
    bl_description = "Remove the specified shots from the current take"
    bl_options = {"INTERNAL", "UNDO"}

    action: EnumProperty(items=(("ALL", "ALL", ""), ("DISABLED", "DISABLED", "")), default="ALL")

    deleteCameras: BoolProperty(
        name="Delete Shots Cameras",
        description="When deleting a shot, also delete the associated camera, if not used by another shot",
        default=False,
    )

    @classmethod
    def description(self, context, properties):
        descr = "_"
        # print("properties: ", properties)
        # print("properties action: ", properties.action)
        if "ALL" == properties.action:
            descr = "Remove all shots from the current take"
        elif "DISABLED" == properties.action:
            descr = "Remove only disabled shots from the current take"
        return descr

    @classmethod
    def poll(cls, context):
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="Delete Associated Camera:")
        col = grid_flow.column(align=False)
        col.prop(self, "deleteCameras", text="")

        # row = box.row(align=True)
        # grid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
        # # grid_flow.separator( factor=0.5)
        # grid_flow.use_property_split = True
        # grid_flow.prop(self, "startAtCurrentTime")
        # grid_flow.prop(self, "addToEndOfList")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        shots = props.get_shots()
        currentShotInd = props.current_shot_index
        selectedShotInd = props.getSelectedShotIndex()

        props.setCurrentShotByIndex(-1)

        try:
            item = shots[selectedShotInd]
        except IndexError:
            pass
        else:
            if self.action == "ALL":
                props.setCurrentShotByIndex(-1)
                i = len(shots) - 1
                while i > -1:
                    if self.deleteCameras:
                        props.deleteShotCamera(shots[i])
                    shots.remove(i)
                    i -= 1
                props.setSelectedShotByIndex(-1)
            elif self.action == "DISABLED":
                i = len(shots) - 1
                while i > -1:
                    if not shots[i].enabled:
                        if currentShotInd == len(shots) - 1 and currentShotInd == selectedShotInd:
                            pass
                        if self.deleteCameras:
                            props.deleteShotCamera(shots[i])
                        shots.remove(i)
                    i -= 1
                if 0 < len(shots):  # wkip pas parfait, on devrait conserver la sel currente
                    props.setCurrentShotByIndex(0)
                    props.setSelectedShotByIndex(0)

        #  print(" ** removed shots, len(props.get_shots()): ", len(props.get_shots()))

        return {"FINISHED"}


class UAS_ShotManager_Shots_SelectCamera(Operator):
    bl_idname = "uas_shot_manager.shots_selectcamera"
    bl_label = "Select Camera"
    bl_description = "Deselect all and select specified camera"
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(default=0)

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
        if context.active_object is not None and context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        context.scene.UAS_shot_manager_props.selectCamera(self.index)
        return {"FINISHED"}


class UAS_ShotManager_Shots_RemoveCamera(Operator):
    bl_idname = "uas_shot_manager.shots_removecamera"
    bl_label = "Remove Camera From All Shots..."
    bl_description = "Remove the camera of the selected shot from all the shots."
    bl_options = {"INTERNAL", "UNDO"}

    removeFromOtherTakes: BoolProperty(name="Also Remove From Other Takes", default=False)

    @classmethod
    def poll(cls, context):
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    def invoke(self, context, event):
        selectedShot = context.scene.UAS_shot_manager_props.getSelectedShot()
        if selectedShot is None:
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "removeFromOtherTakes")

        layout.separator()

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props
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

        return {"FINISHED"}


class UAS_ShotManager_UniqueCameras(Operator):
    bl_idname = "uas_shot_manager.unique_cameras"
    bl_label = "Make All Cameras Unique"
    bl_description = "Make cameras unique per shot"
    bl_options = {"INTERNAL", "UNDO"}

    @classmethod
    def poll(cls, context):
        shots = context.scene.UAS_shot_manager_props.get_shots()
        return len(shots)

    @staticmethod
    def unique_cam_name(cam_name):
        i = 1
        objects = bpy.data.objects
        while cam_name in objects:
            cam_name = f"{cam_name}_{i}"
            i += 1
        return cam_name

    def execute(self, context):
        scene = context.scene
        takes = get_takes(context.scene)
        new_cam_from_shots = dict()
        objects = bpy.data.objects
        for take in takes:
            existing_cam = set()
            for shot in take.shots:
                if shot.camera is None:
                    continue
                cam = shot.camera.name

                if cam in existing_cam and cam in objects:
                    if shot.name in new_cam_from_shots:
                        shot.camera = new_cam_from_shots[shot.name]
                    else:
                        cam_obj = context.scene.objects[cam]
                        new_cam = cam_obj.copy()
                        new_cam.name = self.unique_cam_name(f"{cam}_{shot.name}")
                        scene.collection.objects.link(new_cam)
                        new_cam_from_shots[shot.name] = new_cam.name
                        shot.camera = new_cam

                new_cam_from_shots[shot.name] = shot.camera
                existing_cam.add(cam)

        return {"FINISHED"}


_classes = (
    # for shot items:
    UAS_ShotManager_SetCurrentShot,
    UAS_ShotManager_ShotDuration,
    UAS_ShotManager_GetSetCurrentFrame,
    UAS_ShotManager_NoLens,
    UAS_ShotManager_ShotTimeInEdit,
    UAS_ShotManager_ShowNotes,
    UAS_ShotManager_ListCameraInstances,
    UAS_ShotManager_MakeShotCameraUnique,
    # for shot manipulation:
    UAS_ShotManager_ShotAdd_GetCurrentFrameFor,
    UAS_ShotManager_ShotAdd,
    UAS_ShotManager_ShotDuplicate,
    UAS_ShotManager_ShotRemove,
    UAS_ShotManager_ShotMove,
    # for shot actions:
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
