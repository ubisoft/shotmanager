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
Grid operators to order storyboard frames in the 3D space
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty

from shotmanager.config import config


class UAS_ShotManager_StoryboardGridUpdate(Operator):
    bl_idname = "uas_shot_manager.storyboard_grid_update"
    bl_label = "Update Storyboard Grid"
    bl_description = "Update the position of the storyboard frames on the grid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        props.updateStoryboardGrid()

        return {"FINISHED"}


class UAS_ShotManager_StoryboardGridDisplaySettings(Operator):
    bl_idname = "uas_shot_manager.storyboard_grid_display_settings"
    bl_label = "Storyboard Grid Settings"
    bl_description = "Display the Storyboard Grid settings"
    bl_options = {"REGISTER", "UNDO"}

    # Can be SCENE or ADDON_PREFS
    mode: StringProperty(default="SCENE")

    origin: FloatVectorProperty(size=3, description="Top left corner of the grid", default=(10, 0, 10))

    offset_x: FloatProperty(default=1.5)
    offset_y: FloatProperty(default=-1.2)
    offset_z: FloatProperty(default=2.0)

    numShotsPerRow: IntProperty(default=5)

    orientTowardAxis: EnumProperty(
        name="Orient Toward Axis",
        description="Orient the Storyboard Shots in the direction of the specifed axis",
        items=(
            ("X_POSITIVE", "X", ""),
            ("X_NEGATIVE", "-X", ""),
            ("Y_POSITIVE", "Y", ""),
            ("Y_NEGATIVE", "-Y", ""),
        ),
        default="Y_POSITIVE",
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=360)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()
        layout = self.layout

        # layout.alert = True
        # layout.label(text="Any change is effective immediately")
        # layout.alert = False

        if "SCENE" == self.mode:
            grid = props.stb_frameTemplate.frameGrid
            draw_frame_grid_prefs(self.mode, grid, layout)
        else:
            draw_frame_grid_prefs(self.mode, self, layout)

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        if "SCENE" == self.mode:
            # modifs applied directly
            pass
            return {"INTERFACE"}
        else:
            # set prefs
            pass

        return {"FINISHED"}


def draw_frame_grid_prefs(mode, parentOperator, layout):

    box = layout.box()
    col = box.column()

    row = col.row()
    row.use_property_split = True
    row.use_property_decorate = False
    row.prop(parentOperator, "numShotsPerRow", text="Number of Shots per Row:")

    sepRow = col.row()
    sepRow.separator(factor=0.5)

    row = col.row()
    row.prop(parentOperator, "origin")

    sepRow = col.row()
    sepRow.separator(factor=0.5)

    row = col.row()
    splitFactor = 0.228
    split = row.split(factor=splitFactor)
    split.label(text="Offset:")
    split.prop(parentOperator, "offset_x", text="X")

    row = col.row()
    split = row.split(factor=splitFactor)
    split.label(text=" ")
    split.prop(parentOperator, "offset_y", text="Y")

    row = col.row()
    split = row.split(factor=splitFactor)
    split.label(text=" ")
    split.prop(parentOperator, "offset_z", text="Z")

    # reorient cameras
    ####################
    # The whole grid should be rotated

    # sepRow = col.row()
    # sepRow.separator(factor=2.0)

    # row = col.row()
    # splitFactor = 0.45
    # split = row.split(factor=splitFactor)
    # split.label(text="Orient Camera Toward:")
    # split.prop(parentOperator, "orientTowardAxis", text="")

    sepRow = col.row()
    sepRow.separator(factor=2.0)

    row = col.row()
    row.alignment = "CENTER"
    row.label(text="Update Scene: ")
    subRow = row.row()
    subRow.scale_x = 3.0
    subRow.operator("uas_shot_manager.storyboard_grid_update", text="", icon="LIGHTPROBE_GRID")

    sepRow = col.row()
    sepRow.separator(factor=2.0)


_classes = (
    UAS_ShotManager_StoryboardGridUpdate,
    UAS_ShotManager_StoryboardGridDisplaySettings,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
