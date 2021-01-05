import bpy
from bpy.types import Operator
from bpy.props import FloatProperty


class MyCustomMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_my_custom_menu"
    bl_label = "Wk My Custom Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile").copy = True

        layout.operator("object.shade_smooth")

        layout.label(text="Hello world!", icon="WORLD_DATA")

        # use an operator enum property to populate a sub-menu
        layout.operator_menu_enum(
            "object.select_by_type", property="type", text="Select All by Type...",
        )

        # call another menu
        layout.operator("wm.call_menu", text="Unwrap").name = "VIEW3D_MT_uv_map"


def draw_item(self, context):
    layout = self.layout
    layout.menu(MyCustomMenu.bl_idname)


class UAS_ShotManager_SetTimeRangeStart(Operator):
    bl_idname = "uas_shot_manager.set_time_range_start"
    bl_label = "Set Start Range"
    bl_description = "Set the end time range with the curent time value"
    bl_options = {"INTERNAL"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    # def invoke(self, context, event):
    #     props = context.scene.UAS_shot_manager_props

    #     return {"FINISHED"}

    def execute(self, context):
        scene = context.scene

        if scene.use_preview_range:
            scene.frame_preview_start = scene.frame_current
        else:
            scene.frame_start = scene.frame_current

        return {"FINISHED"}


class UAS_ShotManager_SetTimeRangeEnd(Operator):
    bl_idname = "uas_shot_manager.set_time_range_end"
    bl_label = "Set End Range"
    bl_description = "Set the end time range with the curent time value"
    bl_options = {"INTERNAL"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    # def invoke(self, context, event):
    #     props = context.scene.UAS_shot_manager_props

    #     return {"FINISHED"}

    def execute(self, context):
        scene = context.scene

        if scene.use_preview_range:
            scene.frame_preview_end = scene.frame_current
        else:
            scene.frame_end = scene.frame_current

        return {"FINISHED"}


class UAS_ShotManager_FrameTimeRange(Operator):
    bl_idname = "uas_shot_manager.frame_time_range"
    bl_label = "Frame Time Range"
    bl_description = "Change the VSE zoom value to fit the scene time range"
    bl_options = {"INTERNAL"}

    spacerPercent: FloatProperty(
        description="Range of time, in percentage, before and after the time range", min=0.0, max=40.0, default=5
    )

    # def invoke(self, context, event):
    #     props = context.scene.UAS_shot_manager_props

    #     return {"FINISHED"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        def _setTimeRange(time_start, time_end):
            ctx = context.copy()
            frameRange = int((time_end - time_start))
            for area in context.screen.areas:
                if area.type == "DOPESHEET_EDITOR":
                    ctx["area"] = area
                    for region in area.regions:
                        if region.type == "WINDOW":
                            ctx["region"] = region

                            #
                            # set one frame to one pixel
                            bpy.ops.view2d.reset(ctx)

                            context.scene.frame_current = time_start + frameRange // 2
                            bpy.ops.action.view_frame(ctx)
                            # viewWidthInPx = int(region.view2d.region_to_view(region.width, region.height)[0])
                            regionWidthInPx = int(region.width)
                            print(f"region.w: {region.width}, {regionWidthInPx}, frameRange: {frameRange}")
                            # zoom is based on a constant (why that value of 1.6??? ) and the ui scale
                            # https://devtalk.blender.org/t/proper-way-to-draw-viewport-text-when-using-hi-dpi-displays/6804/4
                            delta = int(
                                (regionWidthInPx - int(frameRange)) / (1.6 / bpy.context.preferences.view.ui_scale)
                            )
                            print(f"delta: {delta}")
                            print(f"delta 2: {region.width // 2 - (frameRange) // 2}")
                            bpy.ops.view2d.zoom(ctx, deltax=delta)
                            # bpy.ops.view2d.zoom(ctx, deltax=(region.width // 2 - (frameRange) // 2))

        if scene.use_preview_range:
            beforeStart = scene.frame_preview_start
            beforeEnd = scene.frame_preview_end

            framesToAdd = int((scene.frame_preview_end - scene.frame_preview_start + 1) * self.spacerPercent / 100.0)
            scene.frame_preview_start = beforeStart - framesToAdd
            scene.frame_preview_end = beforeEnd + framesToAdd

            _setTimeRange(scene.frame_preview_start, scene.frame_preview_end)

            scene.frame_preview_start = beforeStart
            scene.frame_preview_end = beforeEnd

        else:
            beforeStart = scene.frame_start
            beforeEnd = scene.frame_end

            framesToAdd = int((scene.frame_end - scene.frame_start + 1) * self.spacerPercent / 100.0)
            scene.frame_start = scene.frame_start - framesToAdd
            scene.frame_end = scene.frame_end + framesToAdd

            _setTimeRange(scene.frame_start, scene.frame_end)

            scene.frame_start = beforeStart
            scene.frame_end = beforeEnd

        return {"FINISHED"}


def draw_op_item(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.separator(factor=3)
    row.alignment = "RIGHT"
    # row.label(text="toto dsf trterte")
    # row.operator("bpy.ops.time.view_all")
    row.operator("uas_shot_manager.set_time_range_start", text="", icon="TRIA_UP_BAR")
    row.operator("uas_shot_manager.frame_time_range", text="", icon="CENTER_ONLY")
    row.operator("uas_shot_manager.set_time_range_end", text="", icon="TRIA_UP_BAR")


_classes = (
    UAS_ShotManager_SetTimeRangeStart,
    UAS_ShotManager_SetTimeRangeEnd,
    UAS_ShotManager_FrameTimeRange,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    # lets add ourselves to the main header
    # bpy.types.TIME_MT_editor_menus.prepend(draw_op_item)

    bpy.types.TIME_MT_editor_menus.append(draw_op_item)

    # vse
    # bpy.types.SEQUENCER_HT_header.append(draw_op_item)


#   bpy.types.TIME_HT_editor_buttons.append(draw_op_item)
# bpy.types.TIME_MT_editor_menus.append(draw_item)
# bpy.types.TIME_MT_view.append(draw_item)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TIME_MT_editor_menus.remove(draw_op_item)


# bpy.types.TIME_MT_editor_menus.remove(draw_op_item)


# if __name__ == "__main__":
#     register()

#     # The menu can also be called from scripts
#     bpy.ops.wm.call_menu(name=MyCustomMenu.bl_idname)
