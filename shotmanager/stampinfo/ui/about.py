# GPLv3 License
#
# Copyright (C) 2022 Ubisoft
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
This module defines the About menu of StampInfo
"""

import bpy
from bpy.types import Operator

from ..ui.dependencies_ui import drawDependencies
from ..utils.utils import addonCategory

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_StampInfo_OT_About(Operator):
    bl_idname = "uas_stamp_info.about"
    bl_label = "About Ubisoft Stamp Info..."
    bl_description = "More information about Ubisoft Stamp Info..."
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        props = context.scene.UAS_SM_StampInfo_Settings
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.scale_y = 0.9

        # Version
        ###############
        row = col.row()
        row.separator()
        row.label(text="Version:  " + props.version()[0] + " -  (" + "Oct. 2021" + ")" + " - Ubisoft")

        # Category
        ###############
        row = col.row()
        row.separator()
        row.label(text=f"Add-on Category: {addonCategory('Stamp Info')}")

        # Authors
        ###############
        row = col.row()
        row.separator()
        row.label(text="Written by Julien Blervaque (aka Werwack)")

        # Purpose
        ###############
        row = box.row()
        row.label(text="Purpose:")
        row = box.row()
        row.separator()
        row.label(text="Write scene information on the rendered images.")

        # Documentation
        ###############
        row = box.row()
        row.label(text="Documentation:")
        row = box.row()
        row.separator()
        doc_op = row.operator("stampinfo.open_documentation_url", text="Online Doc")
        doc_op.path = "https://ubisoft-stampinfo.readthedocs.io"
        doc_op.tooltip = "Open online documentation: " + doc_op.path

        doc_op = row.operator("stampinfo.open_documentation_url", text="Source Code")
        doc_op.path = "https://github.com/ubisoft/stampinfo"
        doc_op.tooltip = "Open GitHub project: " + doc_op.path

        doc_op = row.operator("stampinfo.open_documentation_url", text="Video Tutorials")
        doc_op.path = "https://www.youtube.com/channel/UCF6RsOpvCUGQozRlOO_-dDQ"
        doc_op.tooltip = "Watch video tutorials on Youtube: " + doc_op.path

        box.separator(factor=0.5)

        # Dependencies
        ###############
        drawDependencies(context, layout)

        layout.separator(factor=1)

    def execute(self, context):
        return {"FINISHED"}


_classes = (UAS_StampInfo_OT_About,)


def register():
    _logger.debug_ext("       - Registering About Package", form="REG")

    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _logger.debug_ext("       - Unregistering About Package", form="UNREG")

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
