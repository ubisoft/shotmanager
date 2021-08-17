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

import os
from pathlib import Path
import subprocess

import json

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


###################
# UI
###################

# used as UI placeholder
class UAS_OT_EmptyOperator(Operator):
    bl_idname = "uas.empty_operator"
    bl_label = " "
    # bl_description = "Bla"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        pass

        return {"FINISHED"}


class UAS_Utils_RunScript(Operator):
    bl_idname = "uas_utils.run_script"
    bl_label = "Run Script"
    bl_description = "Open a script and run it"

    path: StringProperty()

    def execute(self, context):
        import pathlib

        myPath = str(pathlib.Path(__file__).parent.absolute()) + self.path  # \\api\\api_first_steps.py"
        print("\n*** UAS_Utils_RunScript Op is running: ", myPath)
        # bpy.ops.script.python_file_run(filepath=bpy.path.abspath(myPath))
        bpy.ops.script.python_file_run(filepath=myPath)
        return {"FINISHED"}




###################
# Scene control
###################


class UAS_Utils_GetCurrentFrameForTimeRange(Operator):
    bl_idname = "uas_utils.get_current_frame_for_time_range"
    bl_label = "Get/Set Current Frame"
    bl_description = "Click: Set time range with current frame value.\nShift + Click: Get value for current frame"
    bl_options = {"INTERNAL", "UNDO"}

    # opArgs is a dictionary containing this operator properties and dumped to a json string
    opArgs: StringProperty(default="")
    """ use the following entries for opArgs: "{'frame_start': value}", "{'frame_end': value}", "{'frame_preview_start': value}", "{'frame_preview_end': value}"
    """

    def execute(self, context):
        scene = context.scene
        self.opArgs = self.opArgs.replace("'", '"')
        print(f" self.opArgs: {self.opArgs}")
        if "" != self.opArgs:
            argsDict = json.loads(self.opArgs)
            firstItem = next(iter(argsDict))

            if hasattr(scene, firstItem):
                setattr(scene, firstItem, argsDict[firstItem])

        # bpy.ops.sequencer.view_all()
        # bpy.ops.time.view_all()

        return {"FINISHED"}


_classes = (
    UAS_OT_EmptyOperator,
    UAS_Utils_RunScript,
    UAS_Utils_GetCurrentFrameForTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
