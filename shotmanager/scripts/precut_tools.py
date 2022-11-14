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
Precut tools
"""

from random import uniform

from pathlib import Path

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, EnumProperty

from ..operators.shots import list_cameras
from shotmanager.config import config


class UAS_ShotManager_OT_PredecTools_SortVersionsShots(Operator):
    bl_idname = "uas_shot_manager.predec_sort_versions_shots"
    bl_label = "Sort Version Shots"
    bl_description = (
        "Sort the version shots (ie shorts with a name ending with '_a', '_b',...) so that they are placed altogheter in the edit."
        "\n*** Enabled shots are not moved since it would modify the edit ***"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.sortShotsVersions()

        return {"FINISHED"}


class UAS_ShotManager_PredecTools_CreateShotsFromSingleCamera(Operator):
    bl_idname = "uas_shot_manager.predec_shots_from_single_cam"
    bl_label = "Create Shots From Single Camera..."
    bl_description = (
        "Precut Tool: Create a set of shots based on the specified camera."
        "\nNew shots are put after the selected shot"
    )
    bl_options = {"REGISTER", "UNDO"}

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
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        self.start = context.scene.frame_current
        self.end = context.scene.frame_current + prefs.new_shot_duration

        camName = props.getActiveCameraName()
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
        props = config.getAddonProps(scene)
        #       #  currentShotInd = props.getCurrentShotIndex()
        #         selectedShotInd = props.getSelectedShotIndex()

        # shots = props.get_shots()
        currentShotInd = props.getCurrentShotIndex()
        selectedShotInd = props.getSelectedShotIndex()

        i = 0
        for shotNumber in range(self.start, self.end, self.duration):
            shotName = props.getShotPrefix(shotNumber)
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
        props = config.getAddonProps(scene)

        # sm_montage = MontageShotManager()
        # sm_montage.initialize(scene, props.getCurrentTake())

        props.printInfo()
        dictMontage = dict()
        dictMontage["sequence"] = context.scene.name
        props.getInfoAsDictionnary(dictMontage=dictMontage)

        import json

        print(json.dumps(dictMontage, indent=4))

        return {"FINISHED"}


class UAS_ShotManager_OT_PredecTools_MontageSequencesToJson(Operator):
    bl_idname = "uas_shot_manager.montage_sequences_to_json"
    bl_label = "Montage Sequences to Json"
    bl_description = "Print montage sequence information to Jason file"
    bl_options = {"INTERNAL"}

    filePath: StringProperty()

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)

        # sm_montage = MontageShotManager()
        # sm_montage.initialize(scene, props.getCurrentTake())

        # props.printInfo()
        dictMontage = dict()
        dictMontage["montage"] = config.gMontageOtio.get_name()
        dictMontage["montage_type"] = config.gMontageOtio.get_montage_type()
        dictMontage["montage_file"] = config.gMontageOtio.otioFile

        # props.getInfoAsDictionnary(dictMontage=dictMontage)
        config.gMontageOtio.getInfoAsDictionnary(dictMontage=dictMontage, shotsDetails=False)

        import json

        jsonFile = str(Path(config.gMontageOtio.otioFile).parent)
        if not jsonFile.endswith("\\"):
            jsonFile += "\\"
        jsonFile += Path(config.gMontageOtio.otioFile).stem + ".json"

        # with open(jsonFile, "w") as fp:
        #     json.dump(dictMontage, fp, indent=3)

        print("\nMontage dumped:")
        print(json.dumps(dictMontage, indent=3))

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_PredecTools_SortVersionsShots,
    UAS_ShotManager_PredecTools_CreateShotsFromSingleCamera,
    UAS_ShotManager_OT_PredecTools_PrintMontageInfo,
    UAS_ShotManager_OT_PredecTools_MontageSequencesToJson,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
