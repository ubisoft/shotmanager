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
Panel to list the grease pencil materials
"""


######################################################################

# instanciation in the UI:
# see properties_paint_common.py in blender

# NOTE: This code comes from the toolbar of greasepencil when in draw mode


def brush_basic__draw_color_selector(context, layout, brush, gp_settings, props):
    tool_settings = context.scene.tool_settings
    settings = tool_settings.gpencil_paint
    ma = gp_settings.material

    row = layout.row(align=True)
    if not gp_settings.use_material_pin:
        ma = context.object.active_material
    icon_id = 0
    txt_ma = ""
    if ma:
        ma.id_data.preview_ensure()
        if ma.id_data.preview:
            icon_id = ma.id_data.preview.icon_id
            txt_ma = ma.name
            maxw = 25
            if len(txt_ma) > maxw:
                txt_ma = txt_ma[: maxw - 5] + ".." + txt_ma[-3:]

    sub = row.row(align=True)
    sub.enabled = not gp_settings.use_material_pin
    sub.ui_units_x = 8
    sub.popover(
        panel="TOPBAR_PT_gpencil_materials",
        text=txt_ma,
        icon_value=icon_id,
    )

    row.prop(gp_settings, "use_material_pin", text="")

    if brush.gpencil_tool in {"DRAW", "FILL"}:
        row.separator(factor=1.0)
        sub_row = row.row(align=True)
        sub_row.enabled = not gp_settings.pin_draw_mode
        if gp_settings.pin_draw_mode:
            sub_row.prop_enum(gp_settings, "brush_draw_mode", "MATERIAL", text="", icon="MATERIAL")
            sub_row.prop_enum(gp_settings, "brush_draw_mode", "VERTEXCOLOR", text="", icon="VPAINT_HLT")
        else:
            sub_row.prop_enum(settings, "color_mode", "MATERIAL", text="", icon="MATERIAL")
            sub_row.prop_enum(settings, "color_mode", "VERTEXCOLOR", text="", icon="VPAINT_HLT")

        sub_row = row.row(align=True)
        sub_row.enabled = settings.color_mode == "VERTEXCOLOR" or gp_settings.brush_draw_mode == "VERTEXCOLOR"
        sub_row.prop_with_popover(brush, "color", text="", panel="TOPBAR_PT_gpencil_vertexcolor")
        row.prop(gp_settings, "pin_draw_mode", text="")

    if props:
        row = layout.row(align=True)
        row.prop(props, "subdivision")


######################################################################

# Another example, taken from blender-3.2.1_SM02\3.2\scripts\startup\bl_ui\properties_material_gpencil.py


class MATERIAL_PT_gpencil_slots(GreasePencilMaterialsPanel, Panel):
    bl_label = "Grease Pencil Material Slots"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        ma = context.material

        return (ma and ma.grease_pencil) or (ob and ob.type == "GPENCIL")


######################################################################

# from blender-3.2.1_SM02\3.2\scripts\startup\bl_ui\space_view3d.py

from bl_ui.properties_grease_pencil_common import (
    AnnotationDataPanel,
    AnnotationOnionSkin,
    GreasePencilMaterialsPanel,
    GreasePencilVertexcolorPanel,
)


class TOPBAR_PT_gpencil_materials(GreasePencilMaterialsPanel, Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_label = "Materials"
    bl_ui_units_x = 14

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == "GPENCIL"


######################################################################

# taken from blender-3.2.1_SM02\3.2\scripts\startup\bl_ui\properties_grease_pencil_common.py

# for the UIList named GPENCIL_UL_matslots we can use class MATERIAL_UL_matslots_example(bpy.types.UIList) from the doc (https://docs.blender.org/api/current/bpy.types.UIList.html=)
# or GPENCIL_UL_matslots


class GreasePencilMaterialsPanel:
    # Mix-in, use for properties editor and top-bar.
    def draw(self, context):
        layout = self.layout
        show_full_ui = self.bl_space_type == "PROPERTIES"

        is_view3d = self.bl_space_type == "VIEW_3D"
        tool_settings = context.scene.tool_settings
        gpencil_paint = tool_settings.gpencil_paint
        brush = gpencil_paint.brush if gpencil_paint else None

        ob = context.object
        row = layout.row()

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 7

            row.template_list("GPENCIL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            # if topbar popover and brush pinned, disable
            if is_view3d and brush is not None:
                gp_settings = brush.gpencil_settings
                if gp_settings.use_material_pin:
                    row.enabled = False

            col = row.column(align=True)
            if show_full_ui:
                col.operator("object.material_slot_add", icon="ADD", text="")
                col.operator("object.material_slot_remove", icon="REMOVE", text="")

            col.separator()

            col.menu("GPENCIL_MT_material_context_menu", icon="DOWNARROW_HLT", text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon="TRIA_UP", text="").direction = "UP"
                col.operator("object.material_slot_move", icon="TRIA_DOWN", text="").direction = "DOWN"

                col.separator()

                sub = col.column(align=True)
                sub.operator("gpencil.material_isolate", icon="RESTRICT_VIEW_ON", text="").affect_visibility = True
                sub.operator("gpencil.material_isolate", icon="LOCKED", text="").affect_visibility = False

            if show_full_ui:
                row = layout.row()

                row.template_ID(ob, "active_material", new="material.new", live_icon=True)

                slot = context.material_slot
                if slot:
                    icon_link = "MESH_DATA" if slot.link == "DATA" else "OBJECT_DATA"
                    row.prop(slot, "link", icon=icon_link, icon_only=True)

                if ob.data.use_stroke_edit_mode:
                    row = layout.row(align=True)
                    row.operator("gpencil.stroke_change_color", text="Assign")
                    row.operator("gpencil.material_select", text="Select").deselect = False
                    row.operator("gpencil.material_select", text="Deselect").deselect = True
            # stroke color
            ma = None
            if is_view3d and brush is not None:
                gp_settings = brush.gpencil_settings
                if gp_settings.use_material_pin is False:
                    if len(ob.material_slots) > 0 and ob.active_material_index >= 0:
                        ma = ob.material_slots[ob.active_material_index].material
                else:
                    ma = gp_settings.material
            else:
                if len(ob.material_slots) > 0 and ob.active_material_index >= 0:
                    ma = ob.material_slots[ob.active_material_index].material

            if is_view3d and ma is not None and ma.grease_pencil is not None:
                gpcolor = ma.grease_pencil
                if gpcolor.stroke_style == "SOLID":
                    row = layout.row()
                    row.prop(gpcolor, "color", text="Stroke Color")

        else:
            space = context.space_data
            row.template_ID(space, "pin_id")
