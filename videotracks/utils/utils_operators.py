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


class UAS_ShotManager_OpenExplorer(Operator):
    bl_idname = "uas_shot_manager.open_explorer"
    bl_label = "Open Explorer"
    bl_description = "Open an Explorer window located at the render output directory.\nShift + Click: Copy the path into the clipboard"

    path: StringProperty()

    def invoke(self, context, event):
        absPathToOpen = bpy.path.abspath(self.path)
        head, tail = os.path.split(absPathToOpen)
        absPathToOpen = head + "\\"

        if event.shift:

            def _copy_to_clipboard(txt):
                cmd = "echo " + txt.strip() + "|clip"
                return subprocess.check_call(cmd, shell=True)

            _copy_to_clipboard(absPathToOpen)

        else:
            # wkipwkip
            if Path(absPathToOpen).exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen)}"')
            elif Path(absPathToOpen).parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent}"')
            elif Path(absPathToOpen).parent.parent.exists():
                subprocess.Popen(f'explorer "{Path(absPathToOpen).parent.parent}"')
            else:
                print(f"Open Explorer failed: Path not found: {Path(absPathToOpen)}")
                from ..utils.utils import ShowMessageBox

                ShowMessageBox(f"{absPathToOpen} not found", "Open Explorer - Directory not found", "ERROR")

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
    UAS_ShotManager_OpenExplorer,
    UAS_Utils_GetCurrentFrameForTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
