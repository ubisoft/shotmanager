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

from .retimer_applyto_ui import drawApplyTo

from shotmanager.utils.utils_ui import collapsable_panel, propertyColumn, separatorLine, labelBold

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
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        val = prefs.display_retimer_panel and not props.dontRefreshUI()
        return val

    def draw_header(self, context):
        layout = self.layout
        layout.emboss = "NONE"

        row = layout.row(align=True)
        icon = config.icons_col["ShotManager_Retimer_32"]
        row.label(icon_value=icon.icon_id)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        def _get_retime_frames_as_range(start, end):
            if end < start:
                return "[ - ]"
            return f"[ {start} ]" if start == end else f"[ {start}  ..  {end} ]"

        retimerProps = props.retimer
        retimeEngine = retimerProps.retimeEngine

        layout = self.layout
        drpdwnSplitFac = 0.3

        split = layout.split(factor=drpdwnSplitFac)
        # split.label(text="text")
        labelBold(split, text="Time Mode:")
        split.prop(retimeEngine, "mode", text="")

        box = layout.box()
        row = box.row(align=True)

        if retimeEngine.mode == "GLOBAL_OFFSET":
            leftRow = row.row(align=True)
            leftRow.separator(factor=1)
            leftRow.prop(retimeEngine, "start_frame", text="Ref. Frame")
            leftRow.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"

            rightRow = row.row(align=False)
            rightRow.use_property_split = False
            rightRow.alignment = "RIGHT"
            rightRow.label(text="by ")
            rightRow.prop(retimeEngine, "offset_duration", text="")

            simuRow = box.row(align=True)
            originStr = f"Origin: {0} \u2192 {0 + retimeEngine.offset_duration}"
            newStart = retimeEngine.start_frame + retimeEngine.offset_duration
            newStartStr = f"Ref. Frame: {retimeEngine.start_frame} \u2192 {newStart}"
            newEnd = retimeEngine.start_frame + 1 + retimeEngine.insert_duration
            newEndStr = f"Offset: {retimeEngine.offset_duration}"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{originStr},      {newStartStr},      {newEndStr}")
            simuRow.separator(factor=1)

            applyText = "Offset Time"

        elif retimeEngine.mode == "INSERT_BEFORE":
            row.separator(factor=1)
            row.prop(retimeEngine, "end_frame", text="Insert Before")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"
            row.separator()
            row.prop(retimeEngine, "insert_duration", text="Duration")

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimeEngine.end_frame - 1
            newStartStr = f"Start: {newStart} \u2192 {newStart}"
            newEnd = retimeEngine.end_frame + retimeEngine.insert_duration
            newEndStr = f"End: {retimeEngine.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {0} fr \u2192 {retimeEngine.insert_duration} fr"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(text=f"New frames:  {_get_retime_frames_as_range(newStart + 1, newEnd - 1)}")
            simuRow.separator(factor=1)

            applyText = "Insert Time"

        elif retimeEngine.mode == "INSERT_AFTER":
            row.separator(factor=1)
            row.prop(retimeEngine, "start_frame", text="Insert After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimeEngine, "insert_duration", text="Duration")

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimeEngine.start_frame
            newStartStr = f"Start: {retimeEngine.start_frame} \u2192 {newStart}"
            newEnd = retimeEngine.start_frame + 1 + retimeEngine.insert_duration
            newEndStr = f"End: {retimeEngine.start_frame + 1} \u2192 {newEnd}"
            newRangeStr = f"Duration: {0} fr \u2192 {retimeEngine.insert_duration} fr"
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")
            simuRow.separator(factor=1)

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(text=f"New frames:  {_get_retime_frames_as_range(newStart + 1, newEnd - 1)}")
            simuRow.separator(factor=1)

            applyText = "Insert Time"

        elif retimeEngine.mode == "DELETE_RANGE":
            row.separator(factor=1)
            row.prop(retimeEngine, "start_frame", text="Delete After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimeEngine, "end_frame", text="Up To (excluded)")
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
            newStart = retimeEngine.start_frame
            newStartStr = f"Start: {retimeEngine.start_frame} \u2192 {newStart}"
            newEnd = retimeEngine.start_frame + 1
            newEndStr = f"End: {retimeEngine.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {retimeEngine.end_frame - retimeEngine.start_frame - 1} fr. \u2192 {newEnd - retimeEngine.start_frame - 1} fr."
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)

            simuRow.label(
                text=f"Deleted frames:  {_get_retime_frames_as_range(newStart + 1, retimeEngine.end_frame - 1)}"
            )
            simuRow.separator(factor=1)

            applyText = "Delete Time"

        elif retimeEngine.mode == "RESCALE":
            row.separator(factor=1)
            row.prop(retimeEngine, "start_frame", text="Rescale After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()
            row.prop(retimeEngine, "end_frame", text="Up To (excluded)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"

            # row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            # row.separator(factor=1)

            row2 = box.row(align=False)
            row2.label(text="")
            row2.prop(retimeEngine, "factor", text="Scale Factor")
            row2.separator(factor=3)

            col = box.column()
            col.scale_y = 0.8
            simuRow = col.row(align=True)
            newStart = retimeEngine.start_frame
            newStartStr = f"Start: {retimeEngine.start_frame} \u2192 {newStart}"

            # *** Warning: due to the nature of the time operation the duration is not computed as for Delete Time ***
            duration = retimeEngine.end_frame - retimeEngine.start_frame
            newDuration = round(duration * retimeEngine.factor)

            # newEnd is excluded
            newEnd = retimeEngine.start_frame + newDuration
            newEndStr = f"End: {retimeEngine.end_frame} \u2192 {newEnd}"
            newRangeStr = f"Duration: {duration} fr. \u2192 {newDuration} fr."
            simuRow.separator(factor=1)
            simuRow.label(text=f"{newStartStr},      {newEndStr},      {newRangeStr}")
            simuRow.separator(factor=1)

            simuRow = col.row(align=True)
            simuRow.separator(factor=1)
            simuRow.label(
                text=f"Rescale frames:  {_get_retime_frames_as_range(newStart, retimeEngine.end_frame - 1)} \u2192 {_get_retime_frames_as_range(newStart, newEnd - 1)}"
            )
            simuRow.separator(factor=1)
            # row.prop(retimeEngine, "pivot")

            applyText = "Rescale Time"

        elif retimeEngine.mode == "CLEAR_ANIM":
            row.separator(factor=1)
            row.prop(retimeEngine, "start_frame", text="Clear After")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "start_frame"
            row.separator()

            row.prop(retimeEngine, "end_frame", text="Up To (excluded)")
            row.operator(
                "uas_shot_manager.getcurrentframefor", text="", icon="TRIA_UP_BAR"
            ).propertyToUpdate = "end_frame"

            # wkip animation inside a single frame should be clearable
            simuRow = box.row(align=True)
            newRangeStr = f"Duration: {retimeEngine.end_frame - retimeEngine.start_frame - 1} fr."
            simuRow.separator(factor=1)
            simuRow.label(
                text=f"Cleared frames:  {_get_retime_frames_as_range(retimeEngine.start_frame + 1, retimeEngine.end_frame - 1)},       {newRangeStr}"
            )
            simuRow.separator(factor=1)

            applyText = "Clear Animation"

        elif retimeEngine.mode == "MOVE":
            row.separator(factor=1)
            row.prop(retimeEngine, "start_frame", text="Move Frame")
            row.prop(retimeEngine, "end_frame", text="To")

            row.operator("uas_shot_manager.gettimerange", text="", icon="SEQ_STRIP_META")
            row.separator(factor=1)

            applyText = "Move"

        else:
            applyText = "tototext"
            pass

        row.separator(factor=1)
        doc_op = row.operator("shotmanager.open_documentation_url", text="", icon="INFO", emboss=False)
        quickHelpInfo = retimeEngine.getQuickHelp(retimeEngine.mode)
        doc_op.path = quickHelpInfo[3]
        tooltipStr = quickHelpInfo[1]
        tooltipStr += f"\n{quickHelpInfo[2]}"
        tooltipStr += f"\n\nOpen Shot Manager Retimer online documentation:\n     {doc_op.path}"
        doc_op.tooltip = tooltipStr

        # row = box.row()
        # row.separator(factor=0.1)

        # apply to settings ###########
        ###############################

        # layout.separator(factor=0.5)
        # separatorLine(layout, padding_top=0.5)

        box = layout.box()
        split = box.split(factor=drpdwnSplitFac)
        collapsable_panel(split, prefs, "retimer_applyTo_expanded", text="Apply To:")
        split.prop(retimerProps, "applyTo", text="")

        if prefs.retimer_applyTo_expanded:
            drawApplyTo(context, retimerProps, box)

        # apply button ################
        ###############################

        separatorLine(layout, padding_top=0.5, padding_bottom=1.5)

        compo = layout.row()
        compo.separator(factor=2)
        compo.scale_y = 1.2
        compo.operator("uas_shot_manager.retimerapply", text=applyText)
        compo.separator(factor=2)

        layout.separator(factor=0.6)


_classes = (UAS_PT_ShotManagerRetimer,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
