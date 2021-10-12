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
from bpy.types import Operator, PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty

# a function is used here so that the returned items tupple can also be called by the quick help components
def list_retime_modes(self, context):
    items=(
        (
            "GLOBAL_OFFSET",
            "Global Offset Time",
            "Offset all the animation by the specified number of frames.",
            0,
        ),
        (
            "INSERT_BEFORE",
            "Insert Time Before...",
            "Insert the given time, in number of frames, BEFORE the specified frame.\nKeyframes starting at the specified time are offset.",
            1,
        ),
        (
            "INSERT_AFTER",
            "Insert Time After...",
            "Insert the given time, in number of frames, AFTER the specified frame.\nKeyframes after the range are just offset.",
            2,
        ),
        (
            "DELETE_RANGE",
            "Delete in Between Time",
            "Remove the time located AFTER the start frame and BEFORE the end frame.\nStart and end frames are NOT removed."
            "\nKeyframes after the range are just offset.",
            3,
        ),
        (
            "RESCALE",
            "Rescale Time",
            "Change the scale of the specified time range, starting at the specified start frame.\nKeyframes after the end of the range are just offset.",
            4,
        ),
        (
            "CLEAR_ANIM",
            "Clear Animation",
            "Clear the animation on the specified time range.\nNo keyframes are offset.",
            5,
        ),
        # (
        #     "FREEZE",
        #     "Clear Animation",
        #     "Clear the animation on the specified time range.\nNo keyframes are offset.",
        # ),
    )

    return items

class UAS_Retimer_Properties(PropertyGroup):

    mode: EnumProperty(
        name="Time Mode",
        items = list_retime_modes,
        #default="GLOBAL_OFFSET",
    )


    def getQuickHelp(self, topic):
        items = list_retime_modes(self, bpy.context)
        modeItem = ([s for s in items if topic == s[0]])[0]
        #print(f"modeItem: {modeItem[1]}")

        docPath = "https://ubisoft-shotmanager.readthedocs.io/en/latest/features-advanced/retimer.html"
        title = modeItem[1]
        text = modeItem[2]

        if "GLOBAL_OFFSET" == topic:
            text += ""
            #TODO wkip add doc anchor to each path
            docPath += ""
        elif "INSERT_BEFORE" == topic:
            text += ""
        elif "INSERT_AFTER" == topic:
            text += ""
        elif "DELETE_RANGE" == topic:
            text += ""
        elif "RESCALE" == topic:
            text += ""
        elif "CLEAR_ANIM" == topic:
            text += ""
        else:
            title = "description"
            text = "text"

        tooltip = "Quick tips about " + title
        return (tooltip, title, text, docPath)

    def _get_start_frame(self):
        val = self.get("start_frame", True)
        return val

    def _set_start_frame(self, value):
        if value >= self.end_frame:
            self.end_frame = value + 1
        self["start_frame"] = value

    # def _update_start_frame(self, context):
    #     if self.start_frame >= self.end_frame:
    #         self.end_frame = self.start_frame + 1

    start_frame: IntProperty(
        name="Start Frame",
        description="The time operation will occur right AFTER this frame."
        "\nThis frame is then NOT MODIFIED",
        get=_get_start_frame,
        set=_set_start_frame,
        # update=_update_start_frame,
        default=1,
        options=set(),
    )

    def _get_end_frame(self):
        val = self.get("end_frame", True)
        return val

    def _set_end_frame(self, value):
        if value <= self.start_frame:
            self.start_frame = value - 1
        self["end_frame"] = value

    # def _update_end_frame(self, context):
    #     if self.start_frame >= self.end_frame:
    #         self.start_frame = self.end_frame - 1

    end_frame: IntProperty(
        name="End Frame",
        description="The time operation will occur right BEFORE this frame."
        "\nThis frame will then be modified",
        get=_get_end_frame,
        set=_set_end_frame,
        # update=_update_end_frame,
        default=10,
        options=set(),
    )

    move_current_frame: BoolProperty(
        "Move Current Frame", default=False, options=set(),
    )

    # Offset specific
    offset_duration: IntProperty(
        name="Offset Duration",
        description="Number of frames used to offset all the animation."
        "\nUse a negative value to make the animation start earlier in time",
        default=100,
        options=set(),
    )

    # Insert specific
    insert_duration: IntProperty(
        name="Insert Duration",
        description="Number of frames to insert after the specified one",
        default=10,
        soft_min=1,
        options=set(),
    )

    # Remove specific
    gap: BoolProperty(
        name="Remove Gap", default=True, options=set(),
    )

    # Rescale specific
    factor: FloatProperty(
        name="Factor",
        description="Scale factore used to change the duration of the specified time range",
        default=1,
        min=0.01,
        max=10,
        options=set(),
    )

    pivot: IntProperty(
        name="Pivot", options=set(),
    )

    onlyOnSelection: BoolProperty(
        name="Apply on Selection", default=False, options=set(),
    )

    applyToShots: BoolProperty(
        name="Shots", default=True, options=set(),
    )

    applyToObjects: BoolProperty(
        name="Objects", default=True, options=set(),
    )
    applyToShapeKeys: BoolProperty(
        name="Shape Keys", default=True, options=set(),
    )
    applytToGreasePencil: BoolProperty(
        name="Grease Pencil", default=True, options=set(),
    )
    applytToVSE: BoolProperty(
        name="VSE", default=True, options=set(),
    )


_classes = (UAS_Retimer_Properties,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

