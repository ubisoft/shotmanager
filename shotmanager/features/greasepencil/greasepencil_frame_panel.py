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
    use_layer_Rough: BoolProperty(name="Use Layer Rough", default=True)
    layer_Rough_name: StringProperty(default="Rough")
    layer_Rough_material: StringProperty(default="Lines")

    # FG #############
    use_layer_FG_Lines: BoolProperty(name="Use Foreground Lines Layer", default=True)
    layer_FG_Lines_name: StringProperty(default="FG Lines")
    layer_FG_Lines_material: StringProperty(default="Stb_Lines")

    use_layer_FG_Fills: BoolProperty(name="Use Foreground Fills Layer", default=True)
    layer_FG_Fills_name: StringProperty(default="FG Fills")
    layer_FG_Fills_material: StringProperty(default="Stb_Fills")

    # MG #############
    use_layer_MG_Lines: BoolProperty(name="Use Mid-ground Lines Layer", default=True)
    layer_MG_Lines_name: StringProperty(default="MiddleG Lines")
    layer_MG_Lines_material: StringProperty(default="Stb_Lines")

    use_layer_MG_Fills: BoolProperty(name="Use Mid-ground Lines Layer", default=True)
    layer_MG_Fills_name: StringProperty(default="MiddleG Fills")
    layer_MG_Fills_material: StringProperty(default="Stb_Fills")

    # BG #############
    use_layer_BG_Lines: BoolProperty(name="Use Background Lines Layer", default=True)
    layer_BG_Lines_name: StringProperty(default="BG Lines")
    layer_BG_Lines_material: StringProperty(default="Stb_Lines")

    use_layer_BG_Fills: BoolProperty(name="Use Background Fills Layer", default=True)
    layer_BG_Fills_name: StringProperty(default="BG Fills")
    layer_BG_Fills_material: StringProperty(default="Stb_Fills")

    # Canvas #########
    use_layer_Canvas: BoolProperty(name="Use Canvas Layer", default=True)
    layer_Canvas_name: StringProperty(default="_Canvas_")
    layer_Canvas_material: StringProperty(default="_Canvas_Mat")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        layout = layout.box()

        def _drawUsageProps(layout, useProp, layerNameProp, matNameProp=None):
            layout.prop(self, useProp)
            row = layout.row(align=True)
            row.separator(factor=4.0)
            #   row.enabled = getattr(self, useProp)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="Layer: ")
            split.prop(self, layerNameProp, text="")

            row.separator(factor=2.0)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="Material: ")
            split.prop(self, matNameProp, text="")

            row.separator(factor=1.0)

        # rough
        _drawUsageProps(layout, "use_layer_Rough", "layer_Rough_name", "layer_FG_Lines_material")

        layout.separator(factor=1)

        # FG #############
        _drawUsageProps(layout, "use_layer_FG_Lines", "layer_FG_Lines_name", "layer_FG_Lines_material")
        _drawUsageProps(layout, "use_layer_FG_Fills", "layer_FG_Fills_name", "layer_FG_Fills_material")

        layout.separator(factor=2)

        # MG #############
        _drawUsageProps(layout, "use_layer_MG_Lines", "layer_MG_Lines_name", "layer_MG_Lines_material")
        _drawUsageProps(layout, "use_layer_MG_Fills", "layer_MG_Fills_name", "layer_MG_Fills_material")

        layout.separator(factor=1)

        # BG #############
        _drawUsageProps(layout, "use_layer_BG_Lines", "layer_BG_Lines_name", "layer_BG_Lines_material")
        _drawUsageProps(layout, "use_layer_BG_Fills", "layer_BG_Fills_name", "layer_BG_Fills_material")

        # Canvas
        _drawUsageProps(layout, "use_layer_Canvas", "layer_Canvas_name", "layer_Canvas_material")

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

        # order of creation is important to have a relevant layer stack

        # wkipwkipwkip
        # Canvas
        props.stb_frameTemplate.addPreset("CANVAS", True, self.layer_Canvas_name, self.layer_Canvas_material)

        # BG #############
        props.stb_frameTemplate.addPreset(
            "BG_FILLS", self.use_layer_BG_Fills, self.layer_BG_Fills_name, self.layer_BG_Fills_material
        )
        props.stb_frameTemplate.addPreset(
            "BG_LINES", self.use_layer_BG_Lines, self.layer_BG_Lines_name, self.layer_BG_Lines_material
        )

        # MG #############
        props.stb_frameTemplate.addPreset(
            "MG_FILLS", self.use_layer_MG_Fills, self.layer_MG_Fills_name, self.layer_MG_Fills_material
        )
        props.stb_frameTemplate.addPreset(
            "MG_LINES", self.use_layer_MG_Lines, self.layer_MG_Lines_name, self.layer_MG_Lines_material
        )

        # FG #############
        props.stb_frameTemplate.addPreset(
            "FG_FILLS", self.use_layer_FG_Fills, self.layer_FG_Fills_name, self.layer_FG_Fills_material
        )
        props.stb_frameTemplate.addPreset(
            "FG_LINES", self.use_layer_FG_Lines, self.layer_FG_Lines_name, self.layer_FG_Lines_material
        )

        # Rough #############
        props.stb_frameTemplate.addPreset(
            "ROUGH", self.use_layer_Rough, self.layer_Rough_name, self.layer_Rough_material
        )

        return {"FINISHED"}


_classes = (UAS_ShotManager_GpTemplatePanel,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
