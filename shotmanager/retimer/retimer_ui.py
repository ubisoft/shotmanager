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
Retimer UI
"""

import bpy
from bpy.types import Panel

# from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty, StringProperty

# from . import retimer
from shotmanager.config import config


class UAS_PT_ShotManagerRetimer(Panel):
    bl_idname = "UAS_PT_ShotManagerRetimerPanel"
    bl_label = "Retimer"
    bl_description = "Manage the global timing of the action in the scene and the shots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        prefs = config.getShotManagerPrefs()
        val = prefs.display_retimer_panel and not props.dontRefreshUI()
        return val

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)
        icon = config.icons_col["ShotManager_Retimer_32"]
        row.label(icon_value=icon.icon_id)

    def draw(self, context):
        def _get_retime_frames_as_range(start, end):
            if end < start:
                return "[ - ]"
            return f"[ {start} ]" if start == end else f"[ {start}  ..  {end} ]"

        retimerProps = context.scene.UAS_shot_manager_props.retimer
        layout = self.layout

        row = layout.row(align=False)
        row.prop(retimerProps, "mode")

        box = layout.box()
        row = box.row(align=True)

        if retimerProps.mode == "GLOBAL_OFFSET":
            leftRow = row.row(align=True)
            leftRow.separator(factor=1)
            leftRow.prop(retimerProps, "start_frame", text="Ref. Frame")
            leftRow.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"

            rightRow = row.row(align=False)
            rightRow.use_property_split = False
            rightRow.alignment = "RIGHT"
            rightRow.label(text="by ")
            rightRow.prop(retimerProps, "offset_duration", text="")

            simuRow = box.row(align=True)
            originStr = f"Origin: {0} \u2192 {0 + retimerProps.offset_duration}"
            newStart = retimerProps.start_frame + retimerProps.offset_duration
            newStartStr = f"Ref. Frame: {retimerProps.start_frame} \u2192 {newStart}"
            newEnd = retimerProps.start_frame + 1 + retimerProps.insert_duration
            newEndStr = f"Offset: {retimerProps.offset_duration}"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{originStr},      {newStartStr},      {newEndStr}")
            simuRow.separator(factor=1)

            applyText = "Offset Time"

        elif retimerProps.mode == "INSERT_BEFORE":
            row.separator(factor=1)
            row.prop(retimerProps, "end_frame", text="Insert Before")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"
            row.separator()
            row.prop(retimerProps, "insert_duration", text="Duration")

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimerProps.end_frame - 1
            newStartStr = f"Start: {newStart} \u2192 {newStart}"
            newEnd = retimerProps.end_frame + retimerProps.insert_duration
            newEndStr = f"End: {retimerProps.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {0} fr \u2192 {retimerProps.insert_duration} fr"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(text=f"New frames:  {_get_retime_frames_as_range(newStart + 1, newEnd - 1)}")
            simuRow.separator(factor=1)

            applyText = "Insert Time"

        elif retimerProps.mode == "INSERT_AFTER":
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Insert After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimerProps, "insert_duration", text="Duration")

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimerProps.start_frame
            newStartStr = f"Start: {retimerProps.start_frame} \u2192 {newStart}"
            newEnd = retimerProps.start_frame + 1 + retimerProps.insert_duration
            newEndStr = f"End: {retimerProps.start_frame + 1} \u2192 {newEnd}"
            newRangeStr = f"Duration: {0} fr \u2192 {retimerProps.insert_duration} fr"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")
            simuRow.separator(factor=1)

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(text=f"New frames:  {_get_retime_frames_as_range(newStart + 1, newEnd - 1)}")
            simuRow.separator(factor=1)

            applyText = "Insert Time"

        elif retimerProps.mode == "DELETE_RANGE":
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Delete After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimerProps, "end_frame", text="Up To (excluded)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"

            # row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            # row.separator()
            # quickH = row.operator("uas_utils.quickhelp", text="", icon="INFO")
            # quickH.descriptionText = quickHelpInfo[0]
            # quickH.title = quickHelpInfo[1]
            # quickH.text = quickHelpInfo[2]

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimerProps.start_frame
            newStartStr = f"Start: {retimerProps.start_frame} \u2192 {newStart}"
            newEnd = retimerProps.start_frame + 1
            newEndStr = f"End: {retimerProps.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {retimerProps.end_frame - retimerProps.start_frame - 1} fr. \u2192 {newEnd - retimerProps.start_frame - 1} fr."
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)

            simuRow.label(
                text=f"Deleted frames:  {_get_retime_frames_as_range(newStart + 1, retimerProps.end_frame - 1)}"
            )
            simuRow.separator(factor=1)

            applyText = "Delete Time"

        elif retimerProps.mode == "RESCALE":
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Rescale After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimerProps, "end_frame", text="Up To (excluded)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"

            # row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            # row.separator(factor=1)

            row2 = box.row(align=False)
            row2.label(text="")
            row2.prop(retimerProps, "factor", text="Scale Factor")
            row2.separator(factor=3)

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimerProps.start_frame
            newStartStr = f"Start: {retimerProps.start_frame} \u2192 {newStart}"

            # *** Warning: due to the nature of the time operation the duration is not computed as for Delete Time ***
            duration = retimerProps.end_frame - retimerProps.start_frame
            newDuration = round(duration * retimerProps.factor)

            # newEnd is excluded
            newEnd = retimerProps.start_frame + newDuration
            newEndStr = f"End: {retimerProps.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {duration} fr. \u2192 {newDuration} fr."
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")
            simuRow.separator(factor=1)

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(
                text=f"Rescale frames:  {_get_retime_frames_as_range(newStart, retimerProps.end_frame - 1)} \u2192 {_get_retime_frames_as_range(newStart, newEnd - 1)}"
            )
            simuRow.separator(factor=1)
            # row.prop(retimerProps, "pivot")

            applyText = "Rescale Time"

        elif retimerProps.mode == "CLEAR_ANIM":
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Clear After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()

            row.prop(retimerProps, "end_frame", text="Up To (excluded)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"

            # wkip animation inside a single frame should be clearable
            simuRow = box.row(align=True)
            newRangeStr = f"Duration: {retimerProps.end_frame - retimerProps.start_frame - 1} fr."
            simuRow.separator(factor=1)
            simuRow.label(
                text=f"Cleared frames:  {_get_retime_frames_as_range(retimerProps.start_frame + 1, retimerProps.end_frame - 1)},       {newRangeStr}"
            )
            simuRow.separator(factor=1)

            applyText = "Clear Animation"

        elif retimerProps.mode == "MOVE":
            row.separator(factor=1)
            row.prop(retimerProps, "start_frame", text="Move Frame")
            row.prop(retimerProps, "end_frame", text="To")

            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            applyText = "Move"

        else:
            applyText = "tototext"
            pass

        row.separator(factor=1)
        doc_op = row.operator("shotmanager.open_documentation_url", text="", icon="INFO", emboss=False)
        quickHelpInfo = retimerProps.getQuickHelp(retimerProps.mode)
        doc_op.path = quickHelpInfo[3]
        tooltipStr = quickHelpInfo[1]
        tooltipStr += f"\n{quickHelpInfo[2]}"
        tooltipStr += f"\n\nOpen Shot Manager Retimer online documentation:\n     {doc_op.path}"
        doc_op.tooltip = tooltipStr

        #### apply
        row = box.row()
        row.separator(factor=0.1)
        compo = layout.row()
        compo.separator(factor=2)
        compo.scale_y = 1.2
        compo.operator("uas_shot_manager.retimerapply", text=applyText)
        compo.separator(factor=2)


class UAS_PT_ShotManagerRetimer_Settings(Panel):
    bl_label = "Apply to..."
    bl_idname = "UAS_PT_ShotManagerRetimer_SettingsPanel"
    bl_description = "Manage the global timing of the action in the scene and the shots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shot Mng"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_ShotManagerRetimerPanel"

    def draw(self, context):
        retimerProps = context.scene.UAS_shot_manager_props.retimer
        prefs = config.getShotManagerPrefs()

        layout = self.layout

        split = layout.split(factor=0.326)
        row = split.row(align=True)
        row.separator(factor=0.7)
        row.prop(retimerProps, "onlyOnSelection", text="Selection Only")
        row = split.row(align=True)
        row.prop(retimerProps, "includeLockAnim", text="Include Locked Anim")

        box = layout.box()
        col = box.column()

        row = col.row(align=True)
        row.prop(retimerProps, "applyToObjects")
        row.prop(retimerProps, "applyToShapeKeys")
        row.prop(retimerProps, "applytToGreasePencil")

        row = col.row(align=True)
        row.scale_y = 0.3

        row = col.row(align=True)
        row.prop(retimerProps, "applyToShots")
        row.prop(retimerProps, "applyToVSE")
        row.label(text="")

        box = layout.box()
        col = box.column()

        row = col.row(align=True)
        row.prop(prefs, "applyToTimeCursor", text="Time Cursor")
        row.prop(prefs, "applyToSceneRange", text="Scene Range")
        # row.label(text="")


_classes = (
    UAS_PT_ShotManagerRetimer,
    UAS_PT_ShotManagerRetimer_Settings,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
