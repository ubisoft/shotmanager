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
Utils operators
"""

import json

# from tokenize import String

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from . import utils
from .utils_os import internet_on


###################
# UI
###################

# used as UI placeholder
class UAS_OT_EmptyOperator(Operator):
    bl_idname = "uas.empty_operator"
    bl_label = " "
    # bl_description = "Bla"
    bl_options = {"INTERNAL"}

    tooltip: StringProperty(default=" ")

    @classmethod
    def description(self, context, properties):
        return properties.tooltip

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


class UAS_Utils_QuickHelp(Operator):
    bl_idname = "uas_utils.quickhelp"
    bl_label = "Quick Help"
    bl_description = "Quick info and tips"
    bl_options = {"INTERNAL"}

    descriptionText: StringProperty(default="Tooltip")
    title: StringProperty(default="Info")
    text: StringProperty(default="My text\non 2 lines")
    icon: StringProperty(default="INFO")

    @classmethod
    def description(self, context, properties):
        return properties.descriptionText

    def invoke(self, context, event):
        # return context.window_manager.invoke_props_dialog(self, width=400)
        return self.execute(context)

    # def draw(self, context):
    #     layout = self.layout
    #     layout.separator(factor=0.2)
    #     row = layout.row()
    #     row.separator(factor=2)
    #     col = row.column(align=False)
    #     col.scale_y = 0.7
    #     messages = self.text.split("\n")
    #     for s in messages:
    #         col.label(text=s)
    #     layout.separator(factor=0.6)

    def execute(self, context):
        me = self

        def drawDialog(self, context):
            layout = self.layout
            layout.separator(factor=0.2)
            row = layout.row()
            row.separator(factor=2)
            col = row.column(align=False)
            col.scale_y = 0.7
            messages = me.text.split("\n")
            for s in messages:
                col.label(text=s)
            layout.separator(factor=0.6)

        bpy.context.window_manager.popup_menu(drawDialog, title=self.title, icon=self.icon)
        return {"FINISHED"}


class UAS_Utils_CheckInternetConnection(Operator):
    bl_idname = "uas_utils.ckeckinternetconnection"
    bl_label = "Check Internet Connection"
    bl_description = "Open a message box displaying the state of the connection of Blender to the Internet"
    bl_options = {"INTERNAL"}

    descriptionText: StringProperty(default="Tooltip")
    title: StringProperty(default="Info")
    text: StringProperty(default="My text\non 2 lines")
    icon: StringProperty(default="INFO")

    @classmethod
    def description(self, context, properties):
        return properties.descriptionText

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        return {"INTERFACE"}

    def draw(self, context):
        layout = self.layout
        layout.separator(factor=0.5)
        if internet_on(timeoutList=[2, 3]):
            row = layout.row()
            row.label(text="Internet is currently accessible from Blender")
        else:
            row = layout.row()
            row.alert = True
            row.label(text="Internet is currently NOT accessible from Blender")
            row = layout.row()
            row.alert = True
            row.label(text="Check your connection and your firewall")


###################
# Cameras
###################

# not used anymore since integrated in UAS_Utils_CameraToView


class UAS_Utils_CreateCameraFromView(Operator):
    """Create a camera from the current view (duplicate the current camera if needed) and set it
    in the viewport.
    """

    bl_idname = "uas_utils.create_camera_from_view"
    bl_label = "Cam From View"
    bl_description = (
        "Create a new camera from the current 3D view and put it in the viewport."
        "\nIf the view already contains a camera then its location and fov are used."
        "\nIf the viewport is not found then the new camera will be at the origin or at the cursor"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(" Creating new camera from view")

        # create new camera
        newCam = utils.create_new_camera("New_Camera")
        utils.makeCameraMatchViewport(context, newCam)

        return {"FINISHED"}


class UAS_Utils_CameraToView(Operator):
    bl_idname = "uas_utils.camera_to_view"
    bl_label = "Camera to View"
    bl_description = (
        "Make selected camera match the position and orientation of the 3D view"
        "\nor the current camera."
        "\n+ Ctrl: Make selected camera match the 3D view, LENS INCLUDED."
        "\n+ Shift: Create a new camera matching the 3D view"
    )
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if event.shift and not event.ctrl:
            # create a new camera
            newCam = utils.create_new_camera("New_Camera")
            utils.makeCameraMatchViewport(context, newCam, matchLens=True)
        elif event.ctrl and not event.shift:
            # align camera and change lens
            if 0 < len(context.selected_objects) and "CAMERA" == context.selected_objects[0].type:
                sel_cam = context.selected_objects[0]
                utils.makeCameraMatchViewport(context, sel_cam, matchLens=True)
        elif not event.ctrl and not event.shift:
            # align camera but do not change lens
            if 0 < len(context.selected_objects) and "CAMERA" == context.selected_objects[0].type:
                sel_cam = context.selected_objects[0]
                utils.makeCameraMatchViewport(context, sel_cam, matchLens=False)
        else:
            pass

        return {"FINISHED"}


###################
# Scene control
###################


class UAS_Utils_GetCurrentFrameForTimeRange(Operator):
    bl_idname = "uas_utils.get_current_frame_for_time_range"
    bl_label = "Get/Set Current Frame"
    bl_description = "Click: Set time range with current frame value." "\n+ Shift: Get value for current frame"
    bl_options = {"REGISTER", "UNDO"}

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
    UAS_Utils_QuickHelp,
    UAS_Utils_CheckInternetConnection,
    UAS_Utils_CreateCameraFromView,
    UAS_Utils_CameraToView,
    UAS_Utils_GetCurrentFrameForTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
