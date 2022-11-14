"""Add an interactive rectangle on the timeline

Eg:
    https://stackoverflow.com/questions/39596525/custom-end-a-modal-operator-blender-python

    https://docs.blender.org/api/current/bpy.types.Operator.html
    
"""


import bpy
import gpu
import bgl

UNIFORM_SHADER_2D = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

from mathutils import Vector

from shotmanager.config import config
from shotmanager.utils import utils
from shotmanager.overlay_tools.workspace_info.workspace_info import draw_typo_2d
from shotmanager.gpu.gpu_2d.class_Mesh2D import build_rectangle_mesh
from shotmanager.overlay_tools.interact_shots_stack.shots_stack_bgl import get_lane_origin_y


def drawAreaInfo(context, pos_y=90):
    """Draw the information about the area
    Calling area is given by context.area
    Args:

    See: https://blender.stackexchange.com/questions/55418/dopesheet-grapheditor-how-to-detect-change-with-api-displayed-frame-range

    """
    # # if not context.window_manager.UAS_shot_manager_identify_dopesheets:
    # #     return

    # dopesheets = utils.getDopesheets(context)

    # contextDopesheetsInd = -1
    # for i, screen_area in enumerate(dopesheets):
    #     if context.area == dopesheets[i]:
    #         contextDopesheetsInd = i
    #         break

    size = 20
    color = (0.95, 0.95, 0.95, 1.0)
    position = Vector([70, pos_y])
    position2 = Vector([70, pos_y - size - 5])
    position3 = Vector([70, pos_y - 2 * size - 5])
    # for i, area in enumerate(context.screen.areas):
    # if area.type == area_type:
    #     areasList.append(area)
    # draw_typo_2d(color, f"Area {i}: {area.type}", position, size)

    region = context.area.regions[-1]
    # print(f"SCREEN: {context.screen.name}")

    h = region.height  # screen
    w = region.width  #
    bl = region.view2d.region_to_view(0, 0)
    tr = region.view2d.region_to_view(w, h)
    # tr = region.view2d.region_to_view(1, 1)

    bl2 = region.view2d.view_to_region(0, 0)
    tr2 = region.view2d.view_to_region(1, 1)

    draw_typo_2d(color, f"Area {'x'}: width:{context.area.width}, region w: {region.width}", position, size)
    # draw_typo_2d(color, f"screen: {context.screen.name}", position2, size)
    draw_typo_2d(color, f"region top right: {tr}, bottom left: {bl}", position2, size)
    draw_typo_2d(color, f"Number of frames displayed: {tr[0]}", position3, size)


#  draw_typo_2d(color, f"region top right: {tr2}, bottom left: {bl2}", position3, size)

# if len(dopesheets):
# if targetDopesheetIndex == contextDopesheetsInd:
#     color = (0.1, 0.95, 0.1, 1.0)
# else:

# areaIndStr = "?" if -1 == contextDopesheetsInd else contextDopesheetsInd
# draw_typo_2d(color, f"Dopesheet: {areaIndStr}", position, size)


## !!! not in the class !!!
def draw_callback_modal_overlay(context, callingArea, targetAreaType="ALL", targetAreaIndex=-1, color=1):
    """Everything in this function should be accessible globally
    There can be only one registrer draw handler at at time
    Args:
        targetAreaType: can be DOPESHEET, VIEWPORT
        targetAreaIndex: index of the target in the list of the areas of the specified type
    """
    print("ogl")
    # if target_area is not None and context.area != target_area:
    #     return False

    # debug:
    targetAreaType = "ALL"

    okForDrawing = False
    if "ALL" == targetAreaType:
        okForDrawing = True

    elif "DOPESHEET" == targetAreaType:
        dopesheets = utils.getDopesheets(context)

        _contextDopesheetsInd = -1
        for i, screen_area in enumerate(dopesheets):
            if context.area == dopesheets[i]:
                _contextDopesheetsInd = i
                break

        if len(dopesheets):
            okForDrawing = targetAreaIndex == _contextDopesheetsInd

    if 1 == color:
        drawAreaInfo(context)
    else:
        drawAreaInfo(context, pos_y=60)
    # targetAreaType, targetAreaIndex

    if okForDrawing:
        print("ogl2")
        bgl.glEnable(bgl.GL_BLEND)
        UNIFORM_SHADER_2D.bind()
        color = (0.9, 0.0, 0.0, 0.9)
        UNIFORM_SHADER_2D.uniform_float("color", color)
        config.tmpTimelineModalRect.draw(UNIFORM_SHADER_2D, context.region)


#############################################
# operator


class WkTimelineModalRect(bpy.types.Operator):
    bl_idname = "uas_debug.timeline_modal_rect"
    bl_label = "Simple Modal Operator"

    def __init__(self):
        self._handle_draw_onDopeSheet = None
        self.start_interaction_mesh = None
        # print("Start")

    def __del__(self):
        # print("End")
        pass

    def invoke(self, context, event):
        self.init_loc_x = context.object.location.x

        props = config.getAddonProps(context.scene)

        # height = 10
        # lane = 5
        # self.origin = Vector([2, get_lane_origin_y(lane)])
        # self.start_interaction_mesh = build_rectangle_mesh(self.origin, 20, height)

        targetDopesheetIndex = props.getTargetDopesheetIndex(context, only_valid=True)
        print(f"targetDopesheetIndex: {targetDopesheetIndex}")
        # targetDopesheetIndex = 0
        args = (self, context, context.area, targetDopesheetIndex)

        # self._handle_draw_onDopeSheet = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
        #     draw_callback__dopesheet_info, args, "WINDOW", "POST_PIXEL"
        # )

        if -1 < targetDopesheetIndex:
            valid_target = utils.getDopesheetFromIndex(context, targetDopesheetIndex)
        # targetDopesheetArea = props.getValidTargetDopesheet(context)
        # args = (context, context.area)

        # NOTE: There can be SEVERAL draw handlers added per type!!!
        args = (context, context.area, "DOPESHEET", targetDopesheetIndex)
        self.draw_handle = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
            draw_callback_modal_overlay, args, "WINDOW", "POST_PIXEL"
        )

        # NOTE: Turn on to see another display
        # args = (context, context.area, "DOPESHEET", targetDopesheetIndex, 2)
        # self.draw_handleB = bpy.types.SpaceDopeSheetEditor.draw_handler_add(
        #     draw_callback_modal_overlay, args, "WINDOW", "POST_PIXEL"
        # )

        self.draw_handle3D = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_modal_overlay, args, "WINDOW", "POST_PIXEL"
        )

        #  self.execute(context)

        context.window_manager.modal_handler_add(self)

        height = 20
        lane = 3
        startframe = 10
        self.origin = Vector([startframe, get_lane_origin_y(lane)])
        self.start_interaction_mesh = build_rectangle_mesh(self.origin, 2.5, height)
        config.tmpTimelineModalRect = self.start_interaction_mesh

        # redraw all
        for area in context.screen.areas:
            area.tag_redraw()

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # if event.type == "MOUSEMOVE":  # Apply
        #     self.value = event.mouse_x
        #     self.execute(context)
        # elif event.type == "LEFTMOUSE":  # Confirm
        #     return {"FINISHED"}
        print(f"Modal, event type: {event.type}")
        if event.type in {"RIGHTMOUSE", "ESC"}:  # Cancel
            print("Stop drawing")
            if self._handle_draw_onDopeSheet is not None:
                print("Stop drawing 02")
                bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self._handle_draw_onDopeSheet, "WINDOW")
            self._handle_draw_onDopeSheet = None

            if self.draw_handle is not None:
                bpy.types.SpaceDopeSheetEditor.draw_handler_remove(self.draw_handle, "WINDOW")
            self.draw_handle = None

            if self.draw_handle3D is not None:
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle3D, "WINDOW")
            self.draw_handle3D = None

            # redraw all
            for area in context.screen.areas:
                area.tag_redraw()
                # context.region.tag_redraw()
                context.scene.frame_current = context.scene.frame_current
                return {"CANCELLED"}

        # self.draw_ogl(context)

        return {"PASS_THROUGH"}
        return {"RUNNING_MODAL"}

    def execute(self, context):

        return {"FINISHED"}


# bpy.utils.register_class(ModalOperator)

# # Only needed if you want to add into a dynamic menu
# def menu_func(self, context):
#     self.layout.operator(ModalOperator.bl_idname, text="Modal Operator")


# # Register and add to the object menu (required to also use F3 search "Modal Operator" for quick access)
# bpy.utils.register_class(ModalOperator)
# bpy.types.VIEW3D_MT_object.append(menu_func)

# # test call
# bpy.ops.object.modal_operator("INVOKE_DEFAULT")


def register():
    bpy.utils.register_class(WkTimelineModalRect)


def unregister():
    bpy.utils.unregister_class(WkTimelineModalRect)
