# -*- coding: utf-8 -*-

from random import uniform

import bpy
from bpy.types import Panel, Operator
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, PointerProperty, FloatVectorProperty

from ..operators import shots
from ..operators.shots import list_cameras


class UAS_ShotManager_PredecTools_CreateShotsFromSingleCamera(Operator):
    bl_idname = "uas_shot_manager.predec_shots_from_single_cam"
    bl_label = "Create Shots From Single Camera"
    bl_description = (
        "Precut Tool: Create a set of shots based on the specified camera."
        "\nNew shots are put after the selected shot"
    )
    bl_options = {"INTERNAL"}

    def _set_duration(self, value):
        print(" _set_duration: value: ", value)
        if value <= 1:
            self.duration = 1

    def _get_duration(self):
        return self.duration

    start: IntProperty(name="First Shot Start", description="")
    end: IntProperty(name="Last Shot Start", description="")
    duration: IntProperty(
        name="Duration",
        description="New shots duration in frames.\nUsually 1 for Precut production step",
        soft_min=1,
        default=1,
    )
    cameraName: EnumProperty(
        items=list_cameras, name="Camera", description="Camera that will be used for every new shot"
    )

    def invoke(self, context, event):
        wm = context.window_manager
        prefs = context.preferences.addons["shotmanager"].preferences

        self.start = context.scene.frame_current
        self.end = context.scene.frame_current + prefs.new_shot_duration

        camName = context.scene.UAS_shot_manager_props.getActiveCameraName()
        if "" != camName:
            self.cameraName = camName

        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, row_major=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.label(text="First Shot Start:")
        col = grid_flow.column(align=False)
        col.prop(self, "start", text="")
        col = grid_flow.column(align=False)
        col.label(text="Last Shot End:")
        col = grid_flow.column(align=False)
        col.prop(self, "end", text="")

        col = grid_flow.column(align=False)
        col.label(text="New Shots Duration:")
        col = grid_flow.column(align=False)
        col.prop(self, "duration", text="")

        col = grid_flow.column(align=False)
        col.label(text="Camera:")
        col = grid_flow.column(align=False)
        col.prop(self, "cameraName", text="")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        #       #  currentShotInd = props.getCurrentShotIndex()
        #         selectedShotInd = props.getSelectedShotIndex()

        shots = props.get_shots()
        currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()

        i = 0
        for shotNumber in range(self.start, self.end, self.duration):
            shotName = props.new_shot_prefix + f"{(shotNumber):03d}"
            props.addShot(
                atIndex=selectedShotInd + i + 1,
                camera=scene.objects[self.cameraName],
                name=shotName,
                start=shotNumber,
                end=shotNumber + self.duration - 1,
                color=(uniform(0, 1), uniform(0, 1), uniform(0, 1), 1),
            )

            i += 1

        if -1 == currentShotInd:
            props.setCurrentShotByIndex(0)
            props.setSelectedShotByIndex(0)
            # wkip pas parfait, on devrait conserver la sel currente

        return {"FINISHED"}


class UAS_ShotManager_OT_PredecTools_PrintMontageInfo(Operator):
    bl_idname = "uas_shot_manager.print_montage_info"
    bl_label = "Print Montage Info"
    bl_description = "Print montage information in the console"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # sm_montage = MontageShotManager()
        # sm_montage.initialize(scene, props.getCurrentTake())

        props.printInfo()

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_PredecTools_CreateShotsFromSingleCamera,
    UAS_ShotManager_OT_PredecTools_PrintMontageInfo,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
