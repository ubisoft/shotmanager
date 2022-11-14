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
Take operators
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, IntProperty

from shotmanager.config import config


class UAS_ShotManager_TakeAdd(Operator):
    bl_idname = "uas_shot_manager.take_add"
    bl_label = "Add New Take"
    bl_description = "Add a new take"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")

    resolution_x: IntProperty(name="Res. X", min=0, default=-1)
    resolution_y: IntProperty(name="Res. Y", min=0, default=-1)
    resolution_framed_x: IntProperty(name="Res. Framed X", min=0, default=1280)
    resolution_framed_y: IntProperty(name="Res. Framed Y", min=0, default=960)
    useStampInfoDuringRendering: BoolProperty(
        name="Stamp Info on Output",
        description="Stamp render information on rendered images thanks to Stamp Info add-on",
        default=True,
    )

    # @classmethod
    # def poll ( cls, context ):
    #     props = config.getAddonProps(context.scene)
    #     currentTakeInd = props.getCurrentTakeIndex()
    #     # take 0 (default, named Main Take) should not be removed !!
    #     if  len(props.getTakes()) <= 0 or currentTakeInd <= 0:
    #         return False
    #     return True

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        takes = props.getTakes()
        if len(takes) <= 0:
            self.name = "Main Take"
        else:
            self.name = f"Take_{len(props.getTakes()) - 1 + 1:02}"
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = config.getAddonProps(scene)

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)

        if len(props.getTakes()) <= 0:
            col = grid_flow.column(align=False)
            col.scale_x = 0.6
            col.label(text="Name (Base take):")
            col = grid_flow.column(align=False)
            col.enabled = False
            col.prop(self, "name", text="")
        else:
            col = grid_flow.column(align=False)
            col.scale_x = 0.6
            col.label(text="New Take Name:")
            col = grid_flow.column(align=True)
            col.prop(self, "name", text="")

        layout.separator()
        col.scale_x = 1.0

        # if not props.use_project_settings:
        #     subBox = box.box()
        #     row = subBox.row(align=False)
        #     row.use_property_split = False
        #     row.alignment = "RIGHT"
        #     row.label(text="Resolution")
        #     row.prop(self, "resolution_x", text="Width:")
        #     row.prop(self, "resolution_y", text="Height:")

        #     row = subBox.row(align=False)
        #     row.use_property_split = False
        #     row.alignment = "RIGHT"
        #     row.label(text="Frame Resolution")
        #     row.prop(self, "resolution_framed_x", text="Width:")
        #     row.prop(self, "resolution_framed_y", text="Height:")

        #     stampInfoStr = "Use Stamp Info Add-on"
        #     subBox.prop(self, "useStampInfoDuringRendering", text=stampInfoStr)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        newTake = props.addTake(name=self.name)

        props.current_take_name = newTake.name
        return {"INTERFACE"}


class UAS_ShotManager_TakeDuplicate(Operator):
    bl_idname = "uas_shot_manager.take_duplicate"
    bl_label = "Duplicate Current Take"
    bl_description = "Duplicate the current take"
    bl_options = {"REGISTER", "UNDO"}

    newTakeName: StringProperty(name="New Take Name")
    alsoDisabled: BoolProperty(name="Also Apply to Disabled Shots", default=True)
    duplicateCam: BoolProperty(name="Duplicate Cameras", default=False)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        takes = props.getTakes()
        if len(takes) <= 0:
            if props.use_project_settings:
                self.newTakeName = props.project_default_take_name
            else:
                self.newTakeName = "Main Take"
        else:
            currentTake = props.getCurrentTake()
            # name based on number of takes
            # self.newTakeName = f"Take_{len(props.getTakes()) - 1 + 1:02}"
            self.newTakeName = currentTake.name + "_duplicate"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        grid_flow = row.grid_flow(align=True, columns=2, even_columns=False)

        col = grid_flow.column(align=False)
        col.scale_x = 0.6
        col.label(text="New Take Name:")
        col = grid_flow.column(align=True)
        col.prop(self, "newTakeName", text="")

        row = box.row(align=True)
        row.separator(factor=2.5)
        subgrid_flow = row.grid_flow(align=True, row_major=True, columns=1, even_columns=False)
        subgrid_flow.prop(self, "alsoDisabled")
        subgrid_flow.prop(self, "duplicateCam")

        layout.separator()

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        currentShotIndex = props.getCurrentShotIndex()
        currentTake = props.getCurrentTake()
        currentTakeInd = props.getCurrentTakeIndex()

        if currentTake is not None:
            newTake = props.copyTake(
                currentTake,
                atIndex=currentTakeInd + 1,
                copyCamera=self.duplicateCam,
                ignoreDisabled=not self.alsoDisabled,
            )
            newTake.name = self.newTakeName
            props.current_take_name = newTake.name
            props.setCurrentShotByIndex(currentShotIndex)

        return {"INTERFACE"}


class UAS_ShotManager_TakeRemove(Operator):
    bl_idname = "uas_shot_manager.take_remove"
    bl_label = "Remove Current Take"
    bl_description = "Remove the current take.\nMain Take, as the base take, cannot be removed"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        currentTakeInd = props.getCurrentTakeIndex()
        # take 0 (default, named Main Take) should not be removed !!
        if len(props.getTakes()) <= 0 or currentTakeInd <= 0:
            return False
        return True

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        props.setCurrentShotByIndex(-1)

        currentTakeInd = props["current_take_name"]

        if props["current_take_name"] == 0:
            if 1 < len(props.takes):
                props.takes.remove(currentTakeInd)
                props["current_take_name"] = 0
            else:
                print("   About to remove the only take...")
        else:
            props["current_take_name"] = currentTakeInd - 1
            props.takes.remove(currentTakeInd)

        props.setCurrentShotByIndex(0)

        return {"INTERFACE"}


class UAS_ShotManager_TakeRename(Operator):
    bl_idname = "uas_shot_manager.take_rename"
    bl_label = "Rename Take"
    bl_description = "Rename the current take.\nMain Take, as the base take, cannot be renamed"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(name="Name")

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        currentTakeInd = props.getCurrentTakeIndex()
        # take 0 (default, named Main Take) should not be renamed !!
        if len(props.getTakes()) <= 0 or currentTakeInd <= 0:
            return False
        return True

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        self.name = props.getCurrentTake().name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        currentTake = props.getCurrentTake()

        if currentTake.name != self.name:
            self.name = props.getUniqueTakeName(self.name)
            currentTake.name = self.name

        return {"INTERFACE"}


class UAS_ShotManager_TakeMoveUp(Operator):
    """Move take up in the take list"""

    bl_idname = "uas_shot_manager.take_move_up"
    bl_label = "Move Take Up"
    bl_description = "Move current take up in the take list"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        takes = props.takes
        if len(takes) <= 1:
            return False

        currentTakeInd = props.getCurrentTakeIndex()
        return 1 < currentTakeInd

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        currentTakeInd = props.getCurrentTakeIndex()
        props.moveTakeToIndex(props.getCurrentTake(), currentTakeInd - 1)

        return {"INTERFACE"}


class UAS_ShotManager_TakeMoveDown(Operator):
    """Move take down in the take list"""

    bl_idname = "uas_shot_manager.take_move_down"
    bl_label = "Move Take Down"
    bl_description = "Move current take down in the take list"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        takes = props.takes
        if len(takes) <= 1:
            return False

        currentTakeInd = props.getCurrentTakeIndex()
        return len(takes) - 1 > currentTakeInd and currentTakeInd > 0

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        currentTakeInd = props.getCurrentTakeIndex()
        props.moveTakeToIndex(props.getCurrentTake(), currentTakeInd + 1)
        return {"INTERFACE"}


class UAS_ShotManager_TakeAsMain(Operator):
    """Set current take as the main one"""

    bl_idname = "uas_shot_manager.take_as_main"
    bl_label = "Set as Main Take"
    bl_description = "Set current take as the Main Take.\nPrevious Main Take is duplicated for backup"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = config.getAddonProps(context.scene)
        takes = props.takes
        if len(takes) <= 1:
            return False

        currentTakeInd = props.getCurrentTakeIndex()
        return 0 < currentTakeInd

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        # currentTakeInd = props.getCurrentTakeIndex()
        # currentShotIndex = props.getCurrentShotIndex()
        # currentTake = props.getCurrentTake()

        newInd = props.moveTakeToIndex(props.getCurrentTake(), 0, setAsMainTake=True)
        if 0 == newInd:
            previousMainTake = props.getTakeByIndex(1)
            previousMainTake.name = "Ex - " + previousMainTake.name
            newMainTake = props.getTakeByIndex(0)
            if props.use_project_settings:
                newMainTake.name = props.project_default_take_name
            else:
                newMainTake.name = "Main Take"

        return {"INTERFACE"}


class UAS_ShotManager_ResetTakesToDefault(Operator):
    bl_idname = "uas_shot_manager.reset_takes_to_default"
    bl_label = "Reset Takes to Default"
    bl_description = "Clear all exisiting takes"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.label(text="This will remove all the takes from the current scene.")
        layout.label(text="Please confirm:")
        layout.separator()

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        takes = props.getTakes()

        for i in range(len(takes), -1, -1):
            takes.remove(i)

        props.createDefaultTake()

        # https://docs.blender.org/api/current/bpy.props.html
        #         props.takes.objects_remove_all()
        # or c in bpy.data.collections:
        #     if not c.users:
        #         bpy.data.collections.remove(c)

        return {"INTERFACE"}


_classes = (
    UAS_ShotManager_TakeAdd,
    UAS_ShotManager_TakeDuplicate,
    UAS_ShotManager_TakeRemove,
    UAS_ShotManager_TakeRename,
    UAS_ShotManager_TakeMoveUp,
    UAS_ShotManager_TakeMoveDown,
    UAS_ShotManager_TakeAsMain,
    UAS_ShotManager_ResetTakesToDefault,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
