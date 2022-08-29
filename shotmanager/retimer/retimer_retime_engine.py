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
Retimer properties
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, EnumProperty, BoolProperty, FloatProperty


class UAS_Retimer_RetimeEngine(PropertyGroup):

    # a function is used here so that the returned items tupple can also be called by the quick help components
    def list_retime_modes(self, context):
        items = (
            (
                "GLOBAL_OFFSET",
                "Global Offset Time",
                "Offset all the animation by the specified number of frames."
                "\n\nUse tip: The 'Ref. Frame' spinner is just there to have a more contextual anticipation"
                "\nof what will happen, as written in the line below the spinners."
                "\nJust enter an offet value, positive or negative, in the right spinner to specify the offset"
                "\nthat will be applied to all the animated content of the scene."
                "\nThen press 'Offset Time'.",
                0,
            ),
            (
                "INSERT_BEFORE",
                "Insert Time Before...",
                "Insert the given time, in number of frames, BEFORE the specified frame."
                "\nKeyframes starting at the specified time are offset."
                "\n\nUse tip: To define the range of time to insert place the time cursor on the FIRST KEPT FRAME"
                "\nof the right part of the animation then press the Get button of the 'Insert Before' spinner."
                "\nThen specify the number of frames to add in the 'Duration' spinner."
                "\nThen press 'Insert Time'.",
                1,
            ),
            (
                "INSERT_AFTER",
                "Insert Time After...",
                "Insert the given time, in number of frames, AFTER the specified frame."
                "\nKeyframes after the range are just offset."
                "\n\nUse tip: To define the range of time to insert place the time cursor on the LAST KEPT FRAME"
                "\nof the first part of the animation then press the Get button of the 'Insert After' spinner."
                "\nThen specify the number of frames to add in the 'Duration' spinner."
                "\nThen press 'Insert Time'.",
                2,
            ),
            (
                "DELETE_RANGE",
                "Delete in Between Time",
                "Remove the time located AFTER the start frame and BEFORE the end frame."
                "\nStart and end frames are NOT removed."
                "\nKeyframes after the range are just offset."
                "\n\nUse tip: To define the range to delete first place the time cursor on the LAST KEPT FRAME"
                "\nof the first part of the animation then press the Get button of the 'Delete After' spinner."
                "\nThen move the time cursor to the FIRST KEPT FRAME of the second part of the animation"
                "\nand press the Get button of the 'Up To (excluded)' spinner."
                "\nThen press 'Delete Time'.",
                3,
            ),
            (
                "RESCALE",
                "Rescale Time",
                "Change the scale of the specified time range, starting at the specified start frame."
                "\nKeyframes after the end of the range are just offset."
                "\nStart and end frames are NOT removed."
                "\nKeyframes after the range are just offset."
                "\n\nUse tip: To define the range to rescale first place the time cursor on the LAST KEPT FRAME"
                "\nof the first part of the animation then press the Get button of the 'Rescale After' spinner."
                "\nThen move the time cursor to the FIRST KEPT FRAME of the second part of the animation"
                "\nand press the Get button of the 'Up To (excluded)' spinner."
                "\nSet the scale factor: values under 1 are speeding the animation, above 1 are making it slower."
                "\nScale factor can only be positive."
                "\nThe start frame is used as origin of the rescale and frames after are either pull or pushed."
                "\nFrames before are not modified."
                "\nThen press 'Rescale Time'.",
                4,
            ),
            (
                "CLEAR_ANIM",
                "Clear Animation",
                "Clear the animation on the specified time range. No keyframes are offset."
                "\n\nUse tip: To define the range to clear first place the time cursor on the LAST KEPT FRAME"
                "\nof the first part of the animation then press the Get button of the 'Clear After' spinner."
                "\nThen move the time cursor to the FIRST KEPT FRAME of the second part of the animation"
                "\nand press the Get button of the 'Up To (excluded)' spinner."
                "\nThen press 'Clear Animation'.",
                5,
            ),
            # (
            #     "FREEZE",
            #     "Clear Animation",
            #     "Clear the animation on the specified time range.\nNo keyframes are offset.",
            # ),
        )

        return items

    mode: EnumProperty(
        name="Time Mode",
        description="Can be GLOBAL_OFFSET, INSERT_BEFORE, INSERT_AFTER, DELETE_RANGE, RESCALE, CLEAR_ANIM",
        items=list_retime_modes,
        # default="GLOBAL_OFFSET",
        default=0,
        options=set(),
    )

    def getQuickHelp(self, topic):
        items = self.list_retime_modes(bpy.context)
        modeItem = ([s for s in items if topic == s[0]])[0]
        # print(f"modeItem: {modeItem[1]}")

        docPath = "https://ubisoft-shotmanager.readthedocs.io/en/latest/feature-toggles/retimer.html"
        title = modeItem[1]
        text = modeItem[2]

        if "GLOBAL_OFFSET" == topic:
            text += ""
            # TODO wkip add doc anchor to each path
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

    """Start of modified range (= created or deleted frames). Excluded from this range
    """
    start_frame: IntProperty(
        name="Start Frame",
        description=(
            "When labeled 'Ref. Frame' this value is used as an example for the computation text below."
            "\n\nOtherwise this value is used as the 'start frame'. The time operation then will occur right AFTER this frame."
            "\nThis frame is then NOT MODIFIED (except during a Time Rescale)"
        ),
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

    """End of modified range (= created or deleted frames). Excluded from this range
    """
    end_frame: IntProperty(
        name="End Frame",
        description="The time operation will occur right BEFORE this frame."
        "\nThis frame will then be the first one to be offset",
        get=_get_end_frame,
        set=_set_end_frame,
        # update=_update_end_frame,
        default=10,
        options=set(),
    )

    move_current_frame: BoolProperty(
        "Move Current Frame",
        default=False,
        options=set(),
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
    """Inclusive duration
    Duration of MODIFIED range (= created or deleted frames).
    It is then the duration of ] self.start_frame .. self.end_frame [
    Its value is: insert_duration = self.end_frame - self.start_frame - 1
    """
    insert_duration: IntProperty(
        name="Insert Duration",
        description="Number of frames to insert after the specified one",
        default=10,
        soft_min=1,
        min=1,
        options=set(),
    )

    # Remove specific
    gap: BoolProperty(
        name="Remove Gap",
        default=True,
        options=set(),
    )

    # Rescale specific
    factor: FloatProperty(
        name="Factor",
        description="Scale factor used to change the duration of the specified time range",
        default=1,
        min=0.01,
        max=10,
        options=set(),
    )

    pivot: IntProperty(
        name="Pivot",
    )


# _classes = (UAS_Retimer_RetimeProperties,)


# def register():
#     for cls in _classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     for cls in reversed(_classes):
#         bpy.utils.unregister_class(cls)
