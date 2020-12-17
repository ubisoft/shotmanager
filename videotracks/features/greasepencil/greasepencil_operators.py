import bpy
from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty

from shotmanager.utils import utils


class UAS_ShotManager_OT_AddGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_grease_pencil"
    bl_label = "Add Grease Pencil"
    bl_description = "Add Grease Pencil to the camera of the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    cameraGpName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        if self.cameraGpName not in scene.objects or scene.objects[self.cameraGpName] is None:
            print("Camera is invalid for grease pencil parenting - Cancelling...")
            return {"CANCELLED"}
        else:
            cam = scene.objects[self.cameraGpName]
            utils.create_new_greasepencil(cam.name + "_GP", parent_object=cam, location=[0, 0, -0.2])

        return {"FINISHED"}


class UAS_ShotManager_OT_SelectGreasePencil(Operator):
    bl_idname = "uas_shot_manager.select_grease_pencil"
    bl_label = "Select Grease Pencil"
    bl_description = "Select Grease Pencil object from the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(default=0)

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        props.setSelectedShotByIndex(self.index)
        if context.active_object is not None and context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        shot = props.getShotByIndex(props.selected_shot_index)
        if shot is not None:
            print("toto")
            if shot.camera is not None:
                gp_child = utils.get_greasepencil_child(shot.camera)
                if gp_child is not None:
                    bpy.ops.object.select_all(action="DESELECT")
                    bpy.context.view_layer.objects.active = gp_child
                    gp_child.select_set(True)

        return {"FINISHED"}


# class UAS_ShotManager_OT_DrawOnGreasePencil(Operator):
#     bl_idname = "uas_shot_manager.draw_on_grease_pencil"
#     bl_label = "Select Grease Pencil"
#     bl_description = "Select Grease Pencil object from the specified shot"
#     bl_options = {"INTERNAL", "UNDO"}

#     gpObjectName: StringProperty(default="")

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         if self.gpObjectName not in scene.objects or scene.objects[self.gpObjectName] is None:
#             print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
#             return {"CANCELLED"}
#         else:
#             gp_child = scene.objects[self.gpObjectName]

#             # context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
#             if context.active_object is not None and context.active_object.mode != "OBJECT":
#                 bpy.ops.object.mode_set(mode="OBJECT")
#             bpy.ops.object.select_all(action="DESELECT")
#             bpy.context.view_layer.objects.active = gp_child
#             gp_child.select_set(True)
#             bpy.ops.gpencil.paintmode_toggle()

#         return {"FINISHED"}


class UAS_ShotManager_OT_DrawOnGreasePencil(Operator):
    bl_idname = "uas_shot_manager.draw_on_grease_pencil"
    bl_label = "Draw on Grease Pencil"
    bl_description = "Draw on the Grease Pencil of the specified shot"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        shot = None
        gp_child = None
        if not ("SELECTED" == props.current_shot_properties_mode):
            shot = props.getCurrentShot()
        else:
            shot = props.getShotByIndex(props.selected_shot_index)

        if shot is not None:
            if shot.camera is None:
                row = layout.row()
                row.enabled = False
                row.operator("uas_shot_manager.add_grease_pencil", text="", icon="OUTLINER_OB_GREASEPENCIL")
            else:
                gp_child = utils.get_greasepencil_child(shot.camera)

        props.setCurrentShotByIndex(props.selected_shot_index)

        if gp_child is None:
            print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
            return {"CANCELLED"}
        else:
            if context.active_object is not None and context.active_object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = gp_child
            gp_child.select_set(True)
            gp_child.hide_select = False
            gp_child.hide_viewport = False
            gp_child.hide_render = False

            bpy.ops.gpencil.paintmode_toggle()

        return {"FINISHED"}


class UAS_ShotManager_OT_RemoveGreasePencil(Operator):
    bl_idname = "uas_shot_manager.remove_grease_pencil"
    bl_label = "Remove Grease Pencil"
    bl_description = "Remove the camera grease pencil of the specified shots"
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shotList = []

        print("Remove Grease Pencil: shotIndex: ", self.shotIndex)
        if 0 > self.shotIndex:
            take = context.scene.UAS_shot_manager_props.getCurrentTake()
            shotList = take.getShotList(ignoreDisabled=props.shotsGlobalSettings.alsoApplyToDisabledShots)
        else:
            shot = props.getShotByIndex(self.shotIndex)
            if shot is not None:
                shotList.append(shot)

        for shot in shotList:
            #    print("   shot name: ", shot.name)
            if shot.camera is not None:
                gp_child = utils.get_greasepencil_child(shot.camera)
                if gp_child is not None:
                    bpy.data.objects.remove(gp_child, do_unlink=True)

        return {"FINISHED"}


class UAS_ShotManager_OT_EnableDisableGreasePencil(Operator):
    bl_idname = "uas_shot_manager.enabledisablegreasepencil"
    bl_label = "Enable / Disable Grease Pencil"
    bl_description = "Alternatively enable or disable the grease pencil used by camera the shots"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences
        bpy.ops.uas_shots_settings.use_greasepencil(useGreasepencil=prefs.toggleGreasePencil)
        prefs.toggleGreasePencil = not prefs.toggleGreasePencil

        return {"FINISHED"}


# class UAS_ShotManager_OT_ChangeGreasePencilOpacity(Operator):
#     bl_idname = "uas_shot_manager.change_grease_pencil_opacity"
#     bl_label = "Opacity"
#     bl_description = "Change Grease Pencil opacity"
#     bl_options = {"INTERNAL", "UNDO"}

#     gpObjectName: StringProperty(default="")

#     def execute(self, context):
#         scene = context.scene
#         props = scene.UAS_shot_manager_props

#         if self.gpObjectName not in scene.objects or scene.objects[self.gpObjectName] is None:
#             print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
#             return {"CANCELLED"}
#         else:
#             gp_child = scene.objects[self.gpObjectName]

#             # context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)
#             if context.active_object is not None and context.active_object.mode != "OBJECT":
#                 bpy.ops.object.mode_set(mode="OBJECT")
#             bpy.ops.object.select_all(action="DESELECT")
#             bpy.context.view_layer.objects.active = gp_child
#             gp_child.select_set(True)

#             bpy.context.object.data.layers["Lines"].opacity = 0.852564

#         return {"FINISHED"}


class UAS_ShotManager_GreasePencilItem(Operator):
    bl_idname = "uas_shot_manager.greasepencilitem"
    bl_label = " "
    bl_description = "Select shot"
    bl_options = {"INTERNAL"}

    index: bpy.props.IntProperty(default=0)

    def invoke(self, context, event):
        context.scene.UAS_shot_manager_props.setSelectedShotByIndex(self.index)

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_AddGreasePencil,
    UAS_ShotManager_OT_SelectGreasePencil,
    UAS_ShotManager_OT_DrawOnGreasePencil,
    UAS_ShotManager_OT_RemoveGreasePencil,
    UAS_ShotManager_OT_EnableDisableGreasePencil,
    UAS_ShotManager_GreasePencilItem,
    #   UAS_ShotManager_OT_ChangeGreasePencilOpacity,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
