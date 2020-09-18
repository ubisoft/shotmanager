import os
from pathlib import Path
import subprocess

import bpy
from bpy.types import Operator
from bpy.props import StringProperty


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
            if Path(absPathToOpen).exists():
                subprocess.Popen(f'explorer "{absPathToOpen}"')
            else:
                print('Open Explorer failed: Path not found: "' + absPathToOpen + '"')
                from ..utils.utils import ShowMessageBox

                ShowMessageBox(f"{absPathToOpen} not found", "Open Explorer - Directory not found", "ERROR")

        return {"FINISHED"}


_classes = (
    UAS_Utils_RunScript,
    UAS_ShotManager_OpenExplorer,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
