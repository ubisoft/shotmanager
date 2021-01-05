import bpy
from bpy.types import Panel, Operator, Menu
from bpy.props import StringProperty

from shotmanager.config import config
from shotmanager.utils import utils

from shotmanager.features.greasepencil import greasepencil_ui as gp

import logging

_logger = logging.getLogger(__name__)


class UAS_PT_ShotManager_ShotsGlobalSettings(Panel):
    bl_label = "Shots Global Control"  # "Current Shot Properties" # keep the space !!
    bl_idname = "UAS_PT_Shot_Manager_Shots_GlobalSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UAS Shot Man"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "UAS_PT_Shot_Manager"

    @classmethod
    def poll(cls, context):
        props = context.scene.UAS_shot_manager_props
        val = (
            (props.display_camerabgtools_in_properties or props.display_greasepencil_in_properties)
            and len(props.getTakes())
            and len(props.get_shots())
        )
        val = val and not props.dontRefreshUI()
        return val

    def draw(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        layout = self.layout
        box = layout.box()
        box.prop(props.shotsGlobalSettings, "alsoApplyToDisabledShots")

        # Camera background images
        ######################

        if props.display_camerabgtools_in_properties:

            # box.label(text="Camera Background Images:")

            subBox = box.box()
            subBox.use_property_decorate = False

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Camera BG Images:")
            grid_flow.operator("uas_shots_settings.use_background", text="Turn On").useBackground = True
            grid_flow.operator("uas_shots_settings.use_background", text="Turn Off").useBackground = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundAlpha", text="Alpha")
            c = row.column()
            c.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE")
            #  row.separator(factor=0.5)  # prevents stange look when panel is narrow

            if config.uasDebug:
                row = subBox.row()
                row.separator(factor=1.0)
                c = row.column()
                c.enabled = False
                c.prop(props.shotsGlobalSettings, "proxyRenderSize")

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Camera BG Sound:")
            grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn On").useBackgroundSound = True
            grid_flow.operator("uas_shots_settings.use_background_sound", text="Turn Off").useBackgroundSound = False
            grid_flow.prop(props.shotsGlobalSettings, "backgroundVolume", text="Volume")
            # row.separator(factor=0.5)  # prevents stange look when panel is narrow
            c.separator(factor=0.5)  # prevents stange look when panel is narrow

            # c = row.column()
            # grid_flow = c.grid_flow(align=False, columns=3, even_columns=False)
            # grid_flow.prop(props.shotsGlobalSettings, "proxyRenderSize")

            # grid_flow.operator("uas_shot_manager.remove_bg_images", text="", icon="PANEL_CLOSE", emboss=True)

        #  row.separator(factor=0.5)  # prevents stange look when panel is narrow

        # Shot grease pencil
        ######################

        if props.display_greasepencil_in_properties:

            # box.label(text="Camera Background Images:")

            subBox = box.box()
            subBox.use_property_decorate = False

            row = subBox.row()
            # row.separator(factor=1.0)
            c = row.column()
            grid_flow = c.grid_flow(align=False, columns=4, even_columns=False)
            grid_flow.label(text="Grease Pencil:")
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn On").useGreasepencil = True
            grid_flow.operator("uas_shots_settings.use_greasepencil", text="Turn Off").useGreasepencil = False
            grid_flow.prop(props.shotsGlobalSettings, "greasepencilAlpha", text="Alpha")
            c = row.column()
            c.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE")

            #  row.separator(factor=0.5)  # prevents stange look when panel is narrow


classes = (UAS_PT_ShotManager_ShotsGlobalSettings,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

