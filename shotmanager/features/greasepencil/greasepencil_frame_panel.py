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
Shot Manager grease pencil frame panel
"""


import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

# from shotmanager.utils import utils
# from shotmanager.utils import utils_greasepencil

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_GpTemplatePanel(Operator):
    bl_idname = "uas_shot_manager.greasepencil_template_panel"
    bl_label = "Frame Template"
    bl_description = "Frame Template"
    bl_options = {"INTERNAL", "UNDO"}

    # rough #############
    use_layer_Rough: BoolProperty(default=True)
    layer_Rough_name: StringProperty(default="Rough")

    # FG #############
    use_layer_FG_Lines: BoolProperty(default=True)
    layer_FG_Lines_name: StringProperty(default="FG Lines")

    use_layer_FG_Fills: BoolProperty(default=True)
    layer_FG_Fills_name: StringProperty(default="FG Fills")

    # MG #############
    use_layer_MG_Lines: BoolProperty(default=True)
    layer_MG_Lines_name: StringProperty(default="MiddleG Lines")

    use_layer_MG_Fills: BoolProperty(default=True)
    layer_MG_Fills_name: StringProperty(default="MiddleG Fills")

    # BG #############
    use_layer_BG_Lines: BoolProperty(default=True)
    layer_BG_Lines_name: StringProperty(default="BG Lines")

    use_layer_BG_Fills: BoolProperty(default=True)
    layer_BG_Fills_name: StringProperty(default="BG Fills")

    # Canvas #########
    use_layer_Canvas: BoolProperty(default=True)
    layer_Canvas_name: StringProperty(default="_Canvas_")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout

        # rough
        layout.prop(self, "use_layer_Rough")
        layout.prop(self, "layer_Rough_name")

        layout.separator(factor=1)

        # FG #############
        layout.prop(self, "use_layer_FG_Lines")
        layout.prop(self, "layer_FG_Lines_name")

        layout.prop(self, "use_layer_FG_Fills")
        layout.prop(self, "layer_FG_Fills_name")

        layout.separator(factor=2)

        # MG #############
        layout.prop(self, "use_layer_MG_Lines")
        layout.prop(self, "layer_MG_Lines_name")

        layout.prop(self, "use_layer_MG_Fills")
        layout.prop(self, "layer_MG_Fills_name")

        layout.separator(factor=1)

        # BG #############
        layout.prop(self, "use_layer_BG_Lines")
        layout.prop(self, "layer_BG_Lines_name")

        layout.prop(self, "use_layer_BG_Fills")
        layout.prop(self, "layer_BG_Fills_name")

        # Canvas
        layout.prop(self, "use_layer_Canvas")
        layout.prop(self, "layer_Canvas_name")

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        # order of creation is important to have a relevant layer stack

        # wkipwkipwkip
        # Canvas
        props.stb_frameTemplate.addPreset("CANVAS", True, self.layer_Canvas_name)

        # BG #############
        props.stb_frameTemplate.addPreset("BG_FILLS", self.use_layer_BG_Fills, self.layer_BG_Fills_name)
        props.stb_frameTemplate.addPreset("BG_LINES", self.use_layer_BG_Lines, self.layer_BG_Lines_name)

        # MG #############
        props.stb_frameTemplate.addPreset("MG_FILLS", self.use_layer_MG_Fills, self.layer_MG_Fills_name)
        props.stb_frameTemplate.addPreset("MG_LINES", self.use_layer_MG_Lines, self.layer_MG_Lines_name)

        # FG #############
        props.stb_frameTemplate.addPreset("FG_FILLS", self.use_layer_FG_Fills, self.layer_FG_Fills_name)
        props.stb_frameTemplate.addPreset("FG_LINES", self.use_layer_FG_Lines, self.layer_FG_Lines_name)

        # Rough #############
        props.stb_frameTemplate.addPreset("ROUGH", self.use_layer_Rough, self.layer_Rough_name)

        return {"FINISHED"}


_classes = (UAS_ShotManager_GpTemplatePanel,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
