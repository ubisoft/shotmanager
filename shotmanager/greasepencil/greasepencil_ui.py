import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty

from shotmanager.utils import utils


def draw_greasepencil_shot_properties(sm_ui, context, shot):
    layout = sm_ui.layout
    props = context.scene.UAS_shot_manager_props
    prefs = context.preferences.addons["shotmanager"].preferences
    scene = context.scene

    gp_child = None
    if shot is not None:
        shotIndex = props.getShotIndex(shot)
        if shot.camera is None:
            pass
        else:
            gp_child = utils.get_greasepencil_child(shot.camera)

    panelIcon = "TRIA_DOWN" if prefs.shot_greasepencil_extended and gp_child is not None else "TRIA_RIGHT"

    box = layout.box()
    box.use_property_decorate = False
    row = box.row()
    extendSubRow = row.row(align=True)
    extendSubRow.prop(prefs, "shot_greasepencil_extended", text="", icon=panelIcon, emboss=False)
    # row.separator(factor=1.0)

    subRow = row.row(align=False)
    # subRow.scale_x = 0.6
    subRow.label(text="Grease Pencil:")

    if gp_child is None:
        extendSubRow.enabled = False
        row.operator(
            "uas_shot_manager.add_grease_pencil", text="", icon="ADD", emboss=True
        ).cameraGpName = shot.camera.name

        # subSubRow.separator(factor=1.0)
        row.prop(props, "display_greasepencil_in_shotlist", text="")
        # subSubRow.separator(factor=0.5)  # prevents stange look when panel is narrow

    else:
        subRow.label(text=gp_child.name)
        subRow.operator("uas_shot_manager.select_grease_pencil", text="", icon="RESTRICT_SELECT_OFF").index = shotIndex
        subSubRow = subRow.row(align=True)
        subSubRow.prop(gp_child, "hide_select", text="")
        subSubRow.prop(gp_child, "hide_viewport", text="")
        subSubRow.prop(gp_child, "hide_render", text="")

        subRow = row.row(align=True)
        subRow.operator("uas_shot_manager.remove_grease_pencil", text="", icon="PANEL_CLOSE").shotIndex = shotIndex
        subRow.separator()
        subRow.prop(props, "display_greasepencil_in_shotlist", text="")

        if prefs.shot_greasepencil_extended:
            row = box.row()
            row.prop(gp_child, "location")

        # row = box.row()
        # row.operator("uas_shot_manager.change_grease_pencil_opacity").gpObjectName = gp_child

