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
About dialog box
"""

import bpy
from bpy.types import Operator

from shotmanager.ui.dependencies_ui import drawDependencies
from shotmanager.utils.utils import addonCategory
from shotmanager.config import config


class UAS_ShotManager_OT_About(Operator):
    bl_idname = "uas_shot_manager.about"
    bl_label = "About Ubisoft Shot Manager..."
    bl_description = "More information about Ubisoft Shot Manager..."
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        props = config.getAddonProps(context.scene)
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.scale_y = 0.9

        # Version
        ###############
        row = col.row()
        row.separator()
        row.label(text="Version: " + props.version()[0] + " - (" + "May 2022" + ")" + " -  Ubisoft")

        # Category
        ###############
        row = col.row()
        row.separator()
        row.label(text=f"Add-on Category: {addonCategory('Ubisoft Shot Manager')}")

        # Authors
        ###############
        row = col.row()
        row.separator()
        row.label(text="Designed and developed by Julien Blervaque (aka Werwack)")
        row = col.row()
        row.separator()
        row.label(text="Contributions from Romain Carriquiry Borchiari")

        # Purpose
        ###############
        row = box.row()
        row.label(text="Purpose:")
        col = box.column()
        col.scale_y = 0.9
        row = col.row()
        row.separator()
        row.label(text="Create a set of camera shots and edit them in the 3D View")
        row = col.row()
        row.separator()
        row.label(text=" as you would do with video clips.")

        # Documentation
        ###############
        row = box.row()
        row.label(text="Documentation:")
        row = box.row()
        row.separator()
        doc_op = row.operator("shotmanager.open_documentation_url", text="Online Doc", icon="HELP")
        doc_op.path = "https://ubisoft-shotmanager.readthedocs.io"
        doc_op.tooltip = "Open online documentation: " + doc_op.path

        doc_op = row.operator("shotmanager.open_documentation_url", text="Source Code", icon="SCRIPTPLUGINS")
        doc_op.path = "https://github.com/ubisoft/shotmanager"
        doc_op.tooltip = "Open GitHub project: " + doc_op.path

        doc_op = row.operator("shotmanager.open_documentation_url", text="Video Tutorials", icon="URL")
        doc_op.path = "https://www.youtube.com/channel/UCF6RsOpvCUGQozRlOO_-dDQ"
        doc_op.tooltip = "Watch video tutorials on Youtube: " + doc_op.path

        box.separator(factor=0.5)

        # Dependencies
        ###############
        drawDependencies(context, layout)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_ShotManager_OT_About,)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
