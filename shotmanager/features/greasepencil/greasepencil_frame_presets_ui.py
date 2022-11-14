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
from bpy.props import StringProperty, BoolProperty, EnumProperty

# from shotmanager.utils import utils
# from shotmanager.utils import utils_greasepencil

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_GpTemplatePanel(Operator):
    bl_idname = "uas_shot_manager.greasepencil_template_panel"
    bl_label = "Frame Template"
    bl_description = "Define the name of the layers and materials supported on storyboard frames"
    bl_options = {"INTERNAL", "UNDO"}

    def listGreasepencilMaterialsInScene(self, context):
        res = list()

        #      res = [m.name for m in bpy.data.materials if m.is_grease_pencil]
        for i, mat in enumerate(bpy.data.materials):
            if mat.is_grease_pencil:
                res.append((mat.name, mat.name, "", i))

        # il
        # res = (("NOMAT", "No Material", "", 0),)
        return res

    # can be SCENE or ADDON_PREFS"
    mode: StringProperty(default="SCENE")

    # rough #############
    use_layer_Rough: BoolProperty(name="Use Layer Rough", default=True)
    layer_Rough_name: StringProperty(default="Rough")
    layer_Rough_material: StringProperty(default="Lines")

    def _get_layer_Rough_materialDrpdwn(self):
        return self.get("layer_Rough_materialDrpdwn", 0)

    def _set_layer_Rough_materialDrpdwn(self, value):
        self["layer_Rough_materialDrpdwn"] = value

    def _update_layer_Rough_materialDrpdwn(self, context):
        self.layer_Rough_material = self.layer_Rough_materialDrpdwn

    layer_Rough_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_Rough_materialDrpdwn,
        set=_set_layer_Rough_materialDrpdwn,
        update=_update_layer_Rough_materialDrpdwn,
        default=0,
    )

    # persp #############
    use_layer_Persp: BoolProperty(name="Use Layer Perspective", default=True)
    layer_Persp_name: StringProperty(default="Perspective")
    layer_Persp_material: StringProperty(default="Lines")

    def _get_layer_Persp_materialDrpdwn(self):
        return self.get("layer_Persp_materialDrpdwn", 0)

    def _set_layer_Persp_materialDrpdwn(self, value):
        self["layer_Persp_materialDrpdwn"] = value

    def _update_layer_Persp_materialDrpdwn(self, context):
        self.layer_Persp_material = self.layer_Persp_materialDrpdwn

    layer_Persp_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_Persp_materialDrpdwn,
        set=_set_layer_Persp_materialDrpdwn,
        update=_update_layer_Persp_materialDrpdwn,
        default=0,
    )

    # FG #############
    use_layer_FG_Lines: BoolProperty(name="Use Foreground Lines Layer", default=True)
    layer_FG_Lines_name: StringProperty(default="FG Lines")
    layer_FG_Lines_material: StringProperty(default="Stb_Lines")

    def _get_layer_FG_Lines_materialDrpdwn(self):
        return self.get("layer_FG_Lines_materialDrpdwn", 0)

    def _set_layer_FG_Lines_materialDrpdwn(self, value):
        self["layer_FG_Lines_materialDrpdwn"] = value

    def _update_layer_FG_Lines_materialDrpdwn(self, context):
        self.layer_FG_Lines_material = self.layer_FG_Lines_materialDrpdwn

    layer_FG_Lines_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_FG_Lines_materialDrpdwn,
        set=_set_layer_FG_Lines_materialDrpdwn,
        update=_update_layer_FG_Lines_materialDrpdwn,
        default=0,
    )

    use_layer_FG_Fills: BoolProperty(name="Use Foreground Fills Layer", default=True)
    layer_FG_Fills_name: StringProperty(default="FG Fills")
    layer_FG_Fills_material: StringProperty(default="Stb_Fills")

    def _get_layer_FG_Fills_materialDrpdwn(self):
        return self.get("layer_FG_Fills_materialDrpdwn", 0)

    def _set_layer_FG_Fills_materialDrpdwn(self, value):
        self["layer_FG_Fills_materialDrpdwn"] = value

    def _update_layer_FG_Fills_materialDrpdwn(self, context):
        self.layer_FG_Fills_material = self.layer_FG_Fills_materialDrpdwn

    layer_FG_Fills_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_FG_Fills_materialDrpdwn,
        set=_set_layer_FG_Fills_materialDrpdwn,
        update=_update_layer_FG_Fills_materialDrpdwn,
        default=0,
    )

    # MG #############
    use_layer_MG_Lines: BoolProperty(name="Use Mid-ground Lines Layer", default=True)
    layer_MG_Lines_name: StringProperty(default="MiddleG Lines")
    layer_MG_Lines_material: StringProperty(default="Stb_Lines")

    def _get_layer_MG_Lines_materialDrpdwn(self):
        return self.get("layer_MG_Lines_materialDrpdwn", 0)

    def _set_layer_MG_Lines_materialDrpdwn(self, value):
        self["layer_MG_Lines_materialDrpdwn"] = value

    def _update_layer_MG_Lines_materialDrpdwn(self, context):
        self.layer_MG_Lines_material = self.layer_MG_Lines_materialDrpdwn

    layer_MG_Lines_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_MG_Lines_materialDrpdwn,
        set=_set_layer_MG_Lines_materialDrpdwn,
        update=_update_layer_MG_Lines_materialDrpdwn,
        default=0,
    )

    use_layer_MG_Fills: BoolProperty(name="Use Mid-ground Lines Layer", default=True)
    layer_MG_Fills_name: StringProperty(default="MiddleG Fills")
    layer_MG_Fills_material: StringProperty(default="Stb_Fills")

    def _get_layer_MG_Fills_materialDrpdwn(self):
        return self.get("layer_MG_Fills_materialDrpdwn", 0)

    def _set_layer_MG_Fills_materialDrpdwn(self, value):
        self["layer_MG_Fills_materialDrpdwn"] = value

    def _update_layer_MG_Fills_materialDrpdwn(self, context):
        self.layer_MG_Fills_material = self.layer_MG_Fills_materialDrpdwn

    layer_MG_Fills_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_MG_Fills_materialDrpdwn,
        set=_set_layer_MG_Fills_materialDrpdwn,
        update=_update_layer_MG_Fills_materialDrpdwn,
        default=0,
    )

    # BG #############
    use_layer_BG_Lines: BoolProperty(name="Use Background Lines Layer", default=True)
    layer_BG_Lines_name: StringProperty(default="BG Lines")
    layer_BG_Lines_material: StringProperty(default="Stb_Lines")

    def _get_layer_BG_Lines_materialDrpdwn(self):
        return self.get("layer_BG_Lines_materialDrpdwn", 0)

    def _set_layer_BG_Lines_materialDrpdwn(self, value):
        self["layer_BG_Lines_materialDrpdwn"] = value

    def _update_layer_BG_Lines_materialDrpdwn(self, context):
        self.layer_BG_Lines_material = self.layer_BG_Lines_materialDrpdwn

    layer_BG_Lines_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_BG_Lines_materialDrpdwn,
        set=_set_layer_BG_Lines_materialDrpdwn,
        update=_update_layer_BG_Lines_materialDrpdwn,
        default=0,
    )

    use_layer_BG_Fills: BoolProperty(name="Use Background Fills Layer", default=True)
    layer_BG_Fills_name: StringProperty(default="BG Fills")
    layer_BG_Fills_material: StringProperty(default="Stb_Fills")

    def _get_layer_BG_Fills_materialDrpdwn(self):
        return self.get("layer_BG_Fills_materialDrpdwn", 0)

    def _set_layer_BG_Fills_materialDrpdwn(self, value):
        self["layer_BG_Fills_materialDrpdwn"] = value

    def _update_layer_BG_Fills_materialDrpdwn(self, context):
        self.layer_BG_Fills_material = self.layer_BG_Fills_materialDrpdwn

    layer_BG_Fills_materialDrpdwn: EnumProperty(
        items=(listGreasepencilMaterialsInScene),
        get=_get_layer_BG_Fills_materialDrpdwn,
        set=_set_layer_BG_Fills_materialDrpdwn,
        update=_update_layer_BG_Fills_materialDrpdwn,
        default=0,
    )

    # Canvas #########
    use_layer_Canvas: BoolProperty(name="Use Canvas Layer", default=True)
    layer_Canvas_name: StringProperty(default="_Canvas_")
    layer_Canvas_material: StringProperty(default="_Canvas_Mat")

    def invoke(self, context, event):
        prefs = config.getAddonPrefs()
        if "SCENE" == self.mode:
            props = config.getAddonProps(context.scene)
        else:
            props = prefs
        props.stb_frameTemplate.updatePresets(mode="SCENE")

        # rough #############
        preset = props.stb_frameTemplate.getPresetByID("ROUGH")
        self.use_layer_Rough = preset.used
        self.layer_Rough_name = preset.layerName
        self.layer_Rough_material = preset.materialName

        # persp #############
        preset = props.stb_frameTemplate.getPresetByID("PERSP")
        # if preset is None:
        #     # wkipwkipwkip dirty do a patch
        #     props.stb_frameTemplate.addPreset("PERSP", True, "Perspective", "Stb_Lines")
        #     preset = props.stb_frameTemplate.getPresetByID("PERSP")
        self.use_layer_Persp = preset.used
        self.layer_Persp_name = preset.layerName
        self.layer_Persp_material = preset.materialName

        # FG #############
        preset = props.stb_frameTemplate.getPresetByID("FG_LINES")
        self.use_layer_FG_Lines = preset.used
        self.layer_FG_Lines_name = preset.layerName
        self.layer_FG_Lines_material = preset.materialName

        preset = props.stb_frameTemplate.getPresetByID("FG_FILLS")
        self.use_layer_FG_Fills = preset.used
        self.layer_FG_Fills_name = preset.layerName
        self.layer_FG_Fills_material = preset.materialName

        # MG #############
        preset = props.stb_frameTemplate.getPresetByID("MG_LINES")
        self.use_layer_MG_Lines = preset.used
        self.layer_MG_Lines_name = preset.layerName
        self.layer_MG_Lines_material = preset.materialName

        preset = props.stb_frameTemplate.getPresetByID("MG_FILLS")
        self.use_layer_MG_Fills = preset.used
        self.layer_MG_Fills_name = preset.layerName
        self.layer_MG_Fills_material = preset.materialName

        # BG #############
        preset = props.stb_frameTemplate.getPresetByID("BG_LINES")
        self.use_layer_BG_Lines = preset.used
        self.layer_BG_Lines_name = preset.layerName
        self.layer_BG_Lines_material = preset.materialName

        preset = props.stb_frameTemplate.getPresetByID("BG_FILLS")
        self.use_layer_BG_Fills = preset.used
        self.layer_BG_Fills_name = preset.layerName
        self.layer_BG_Fills_material = preset.materialName

        # Canvas
        preset = props.stb_frameTemplate.getPresetByID("CANVAS")
        self.use_layer_Canvas = preset.used
        self.layer_Canvas_name = preset.layerName
        self.layer_Canvas_material = preset.materialName

        return context.window_manager.invoke_props_dialog(self, width=480)

    def draw(self, context):
        prefs = config.getAddonPrefs()
        if "SCENE" == self.mode:
            props = config.getAddonProps(context.scene)
        else:
            props = prefs
        #    props.stb_frameTemplate.updatePresets(mode="SCENE")

        sepBlocks = 1.8

        layout = self.layout

        layout = self.layout
        layout.alert = True
        layout.label(text="Any change is effective immediately")
        layout.alert = False

        box = layout.box()

        resetOp = box.operator("uas_shot_manager.resetusagepreset", text="Reset All", icon="LOOP_BACK")
        resetOp.mode = self.mode
        resetOp.presetID = "ALL"

        mainRow = box.row()

        mainRow.separator(factor=1.0)
        mainCol = mainRow.column()
        # mainCol.scale_y = 0.8

        def _drawUsageProps(layout, presetID, useProp, layerNameProp, matNameProp=None, enabled=True):

            # vertical separator
            layout.separator(factor=0.7)

            presetRow = layout.row()
            presetRow.enabled = enabled
            presetcol = presetRow.column()

            useRow = presetcol.row()
            useRowRight = useRow.row()
            useRowRight.prop(self, useProp)
            useRowRight.alignment = "LEFT"
            resetOp = useRowRight.operator("uas_shot_manager.resetusagepreset", text="", icon="LOOP_BACK")
            resetOp.mode = self.mode
            resetOp.presetID = presetID
            useRowRight.separator(factor=0.5)

            row = presetcol.row(align=True)
            row.separator(factor=3)
            #   row.enabled = getattr(self, useProp)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="*** Layer: ")
            split.prop(self, layerNameProp, text="")

            row.separator(factor=2.0)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="Material: ")
            split.prop(self, matNameProp, text="")

            row.separator(factor=2.0)

        def _drawUsagePresetFromActualProps(layout, props, presetID, matNameProp=None, matDrpdwn=None):

            preset = props.stb_frameTemplate.getPresetByID(presetID)

            # vertical separator
            layout.separator(factor=0.7)

            presetRow = layout.row()
            #   presetRow.enabled = enabled
            presetcol = presetRow.column()

            useRow = presetcol.row()
            useRowRight = useRow.row()
            useRowRight.prop(preset, "used", text=f"Use {preset.label} preset")
            useRowRight.alignment = "LEFT"
            resetOp = useRowRight.operator("uas_shot_manager.resetusagepreset", text="", icon="LOOP_BACK")
            resetOp.mode = self.mode
            resetOp.presetID = preset.id
            useRowRight.separator(factor=0.5)

            row = presetcol.row(align=True)
            row.separator(factor=3)
            #   row.enabled = getattr(self, useProp)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="Layer: ")
            split.prop(preset, "layerName", text="")

            row.separator(factor=2.0)
            subRow = row.row(align=True)
            split = subRow.split(factor=0.25)
            split.label(text="Material: ")
            if matNameProp:
                split.prop(self, matNameProp, text="")
            else:
                split.prop(preset, "materialName", text="")
            if matDrpdwn:
                # subRow.prop(self, "layer_Rough_materialDrpdwn", text="")
                matRow = subRow.row()
                matRow.ui_units_x = 1
                matRow.prop(self, matDrpdwn, text="")

            row.separator(factor=2.0)

        # rough #############
        preset = props.stb_frameTemplate.getPresetByID("ROUGH")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_Rough_material", "layer_Rough_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "ROUGH", "use_layer_Rough", "layer_Rough_name", "layer_FG_Lines_material")

        mainCol.separator(factor=sepBlocks)

        # persp #############
        preset = props.stb_frameTemplate.getPresetByID("PERSP")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_Persp_material", "layer_Persp_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "PERSP", "use_layer_Persp", "layer_Persp_name", "layer_FG_Lines_material")

        mainCol.separator(factor=sepBlocks)

        # FG #############
        preset = props.stb_frameTemplate.getPresetByID("FG_LINES")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_FG_Lines_material", "layer_FG_Lines_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "FG_LINES", "use_layer_FG_Lines", "layer_FG_Lines_name", "layer_FG_Lines_material")
        preset = props.stb_frameTemplate.getPresetByID("FG_FILLS")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_FG_Fills_material", "layer_FG_Fills_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "FG_FILLS", "use_layer_FG_Fills", "layer_FG_Fills_name", "layer_FG_Fills_material")

        mainCol.separator(factor=sepBlocks)

        # MG #############
        preset = props.stb_frameTemplate.getPresetByID("MG_LINES")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_MG_Lines_material", "layer_MG_Lines_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "MG_LINES", "use_layer_MG_Lines", "layer_MG_Lines_name", "layer_MG_Lines_material")
        preset = props.stb_frameTemplate.getPresetByID("MG_FILLS")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_MG_Fills_material", "layer_MG_Fills_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "MG_FILLS", "use_layer_MG_Fills", "layer_MG_Fills_name", "layer_MG_Fills_material")

        mainCol.separator(factor=sepBlocks)

        # BG #############
        preset = props.stb_frameTemplate.getPresetByID("BG_LINES")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_BG_Lines_material", "layer_BG_Lines_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "BG_LINES", "use_layer_BG_Lines", "layer_BG_Lines_name", "layer_BG_Lines_material")
        preset = props.stb_frameTemplate.getPresetByID("BG_FILLS")
        if preset is not None:
            _drawUsagePresetFromActualProps(
                mainCol, props, preset.id, "layer_BG_Fills_material", "layer_BG_Fills_materialDrpdwn"
            )
        else:
            _drawUsageProps(mainCol, "BG_FILLS", "use_layer_BG_Fills", "layer_BG_Fills_name", "layer_BG_Fills_material")

        mainCol.separator(factor=sepBlocks)

        # Canvas
        mainCol.label(text="System Layers:")
        preset = props.stb_frameTemplate.getPresetByID("CANVAS")
        if preset is not None:
            _drawUsagePresetFromActualProps(mainCol, props, preset.id)
        else:
            _drawUsageProps(
                mainCol, "CANVAS", "use_layer_Canvas", "layer_Canvas_name", "layer_Canvas_material", enabled=False
            )

        mainCol.separator()

    def execute(self, context):
        self.applySettings(context)
        return {"FINISHED"}

    def cancel(self, context):
        # since project properties are immediatly applied to Shot Manager properties then we also force the
        # application of the settings in the scene even if the user is not clicking on OK button
        self.applySettings(context)

    def applySettings(self, context):
        # Can be SCENE or ADDON_PREFS"
        prefs = config.getAddonPrefs()
        if "SCENE" == self.mode:
            props = config.getAddonProps(context.scene)
        else:
            props = prefs

        # rough #############
        preset = props.stb_frameTemplate.getPresetByID("ROUGH")
        preset.materialName = self.layer_Rough_material

        # persp #############
        preset = props.stb_frameTemplate.getPresetByID("PERSP")
        preset.materialName = self.layer_Persp_material

        # FG #############
        preset = props.stb_frameTemplate.getPresetByID("FG_LINES")
        preset.materialName = self.layer_FG_Lines_material

        preset = props.stb_frameTemplate.getPresetByID("FG_FILLS")
        preset.materialName = self.layer_FG_Fills_material

        # MG #############
        preset = props.stb_frameTemplate.getPresetByID("MG_LINES")
        preset.materialName = self.layer_MG_Lines_material

        preset = props.stb_frameTemplate.getPresetByID("MG_FILLS")
        preset.materialName = self.layer_MG_Fills_material

        # BG #############
        preset = props.stb_frameTemplate.getPresetByID("BG_LINES")
        preset.materialName = self.layer_BG_Lines_material

        preset = props.stb_frameTemplate.getPresetByID("BG_FILLS")
        preset.materialName = self.layer_BG_Fills_material

        # order of creation is important to have a relevant layer stack
        # wkipwkipwkip
        if False:
            # rough #############
            preset = props.stb_frameTemplate.getPresetByID("ROUGH")
            props.stb_frameTemplate.addPreset(
                "ROUGH", self.use_layer_Rough, self.layer_Rough_name, self.layer_Rough_material
            )

            # persp #############
            preset = props.stb_frameTemplate.getPresetByID("PERSP")
            if preset is None:
                props.stb_frameTemplate.addPreset(
                    "PERSP", self.use_layer_Persp, self.layer_Persp_name, self.layer_Persp_material
                )
            else:
                preset.used = preset.used
                preset.layerName = preset.layerName

            # Canvas
            preset = props.stb_frameTemplate.getPresetByID("CANVAS")
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


_classes = (UAS_ShotManager_GpTemplatePanel,)


def register():
    pass
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
