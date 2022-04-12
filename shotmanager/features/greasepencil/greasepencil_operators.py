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
To do: module description here.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


class UAS_ShotManager_OT_AddGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_grease_pencil"
    bl_label = "Add Grease Pencil"
    bl_description = "Add Grease Pencil to the camera of the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    cameraGpName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene

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
            if shot.camera is not None:
                gp_child = utils.get_greasepencil_child(shot.camera)
                if gp_child is not None:
                    bpy.ops.object.select_all(action="DESELECT")
                    bpy.context.view_layer.objects.active = gp_child
                    gp_child.select_set(True)

        return {"FINISHED"}


class UAS_ShotManager_OT_AddCanvasToGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_canvas_to_grease_pencil"
    bl_label = "Add Canvas to Grease Pencil"
    bl_description = "Add a  canvas layer to the grease pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: bpy.props.StringProperty(default="")

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        gpObj = context.scene.objects[self.gpName]

        utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM")

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


class UAS_ShotManager_OT_ToggleGreasePencilDrawMode(Operator):
    bl_idname = "uas_shot_manager.toggle_grease_pencil_draw_mode"
    bl_label = "Toggle Grease Pencil Draw Mode"
    bl_description = "Toggle Grease Pencil Draw Mode"
    bl_options = {"INTERNAL", "UNDO"}

    gpObjectName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        prefs = context.preferences.addons["shotmanager"].preferences
        props = scene.UAS_shot_manager_props

        if context.active_object is not None:
            if context.active_object.mode == "PAINT_GPENCIL":
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
                if prefs.stb_camPOV_forFreeGP:
                    props.getCurrentShot().setCameraToViewport()
                    scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
                    scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"
            # bpy.ops.object.select_all(action="DESELECT")
            # bpy.context.view_layer.objects.active = gp_child
            # gp_child.select_set(True)
            # bpy.ops.gpencil.paintmode_toggle()

        return {"FINISHED"}


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
        elif not gp_child.visible_get():
            print("Grease Pencil cannot be applied on hidden objects - Cancelling...")
            return {"CANCELLED"}
        else:
            if context.active_object.mode == "PAINT_GPENCIL":
                bpy.ops.gpencil.paintmode_toggle()
                return {"FINISHED"}

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
    alsoApplyToDisabledShots: BoolProperty(default=True)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shotList = []

        print("Remove Grease Pencil: shotIndex: ", self.shotIndex)
        if 0 > self.shotIndex:
            take = context.scene.UAS_shot_manager_props.getCurrentTake()
            shotList = take.getShotsList(ignoreDisabled=not self.alsoApplyToDisabledShots)
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
    bl_description = "Alternatively enable or disable the grease pencil used by the camera of the shots"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props

        # prefs = context.preferences.addons["shotmanager"].preferences
        # bpy.ops.uas_shots_settings.use_greasepencil(useGreasepencil=prefs.enableGreasePencil)
        # prefs.enableGreasePencil = not prefs.enableGreasePencil

        props.enableGreasePencil(not props.use_greasepencil)

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
    bl_description = (
        "Select Shot Grease Pencil"
        # "\n+ Ctrl: Disable all shots"
        # "\n+ Ctrl + Shift: Invert shots state"
        "\n+ Shift: Add Grease Pencil to the current selection"
        "\n+ Alt: Select Grease Pencil and switch to Draw mode"
    )
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(default=0)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        props.setSelectedShotByIndex(self.index)
        shot = props.getShotByIndex(self.index)
        gpChild = shot.getGreasePencil()
        if gpChild is not None:
            if not event.shift or event.alt:
                if context.active_object is not None and context.active_object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.select_all(action="DESELECT")
            gpChild.select_set(True)
            if event.alt:
                props.setCurrentShotByIndex(self.index)
                utils_greasepencil.switchToDrawMode(gpChild)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_PreviousKey(Operator):
    bl_idname = "uas_shot_manager.greasepencil_previouskey"
    bl_label = "Previous"
    bl_description = "Go to the previous key of the specified layer"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        gp = context.active_object
        if gp is not None:
            props = context.scene.UAS_shot_manager_props
            if "" == props.greasePencil_layersMode:
                if len(gp.data.layers):
                    props.greasePencil_layersMode = "ACTIVE"
                else:
                    props.greasePencil_layersMode = "NOLAYER"

            if "NOLAYER" == props.greasePencil_layersMode:
                return {"FINISHED"}

            currentFrame = context.scene.frame_current
            context.scene.frame_current = utils_greasepencil.getLayerPreviousFrame(
                gp, currentFrame, props.greasePencil_layersMode
            )

        return {"FINISHED"}


# https://blender.stackexchange.com/questions/142190/how-do-i-access-grease-pencil-data


class UAS_ShotManager_GreasePencil_NextKey(Operator):
    bl_idname = "uas_shot_manager.greasepencil_nextkey"
    bl_label = "Next"
    bl_description = "Go to the next key of the specified layer"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        gp = context.active_object
        if gp is not None:
            props = context.scene.UAS_shot_manager_props
            if "" == props.greasePencil_layersMode:
                if len(gp.data.layers):
                    props.greasePencil_layersMode = "ACTIVE"
                else:
                    props.greasePencil_layersMode = "NOLAYER"

            if "NOLAYER" == props.greasePencil_layersMode:
                return {"FINISHED"}

            currentFrame = context.scene.frame_current
            context.scene.frame_current = utils_greasepencil.getLayerNextFrame(
                gp, currentFrame, props.greasePencil_layersMode
            )

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_NewKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_newkeyframe"
    bl_label = "New Drawing Frame"
    bl_description = "Add a new drawing frame to the specified Grease Pencil"
    bl_options = {"INTERNAL", "UNDO"}

    # layersMode: StringProperty(
    #     name="Layers Mode",
    #     default="",
    # )

    def invoke(self, context, event):
        gp = context.active_object
        if gp is not None:
            props = context.scene.UAS_shot_manager_props
            if "" == props.greasePencil_layersMode:
                if len(gp.data.layers):
                    props.greasePencil_layersMode = "ACTIVE"
                else:
                    props.greasePencil_layersMode = "NOLAYER"

        print(
            f"On a frame for mode {props.greasePencil_layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)}"
        )

        utils_greasepencil.addKeyFrameToLayer(gp, context.scene.frame_current, props.greasePencil_layersMode)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_DuplicateKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_duplicatekeyframe"
    bl_label = "Duplicate Drawing Frame"
    bl_description = "Duplicate the previous drawing frame of the specified Grease Pencil at current time"
    bl_options = {"INTERNAL", "UNDO"}

    # layersMode: StringProperty(
    #     name="Layers Mode",
    #     default="",
    # )

    def invoke(self, context, event):
        gp = context.active_object
        if gp is not None:
            props = context.scene.UAS_shot_manager_props
            if "" == props.greasePencil_layersMode:
                if len(gp.data.layers):
                    props.greasePencil_layersMode = "ACTIVE"
                else:
                    props.greasePencil_layersMode = "NOLAYER"

        print(
            f"On a frame for mode {props.greasePencil_layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)}"
        )

        utils_greasepencil.duplicateLayerKeyFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_DeleteKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_deletekeyframe"
    bl_label = "Delete Drawing Frame"
    bl_description = "Delete the drawing frame of the specified Grease Pencil at current time"
    bl_options = {"INTERNAL", "UNDO"}

    # layersMode: StringProperty(
    #     name="Layers Mode",
    #     default="",
    # )

    def invoke(self, context, event):
        gp = context.active_object
        if gp is not None:
            props = context.scene.UAS_shot_manager_props
            if "" == props.greasePencil_layersMode:
                if len(gp.data.layers):
                    props.greasePencil_layersMode = "ACTIVE"
                else:
                    props.greasePencil_layersMode = "NOLAYER"

        print(
            f"On a frame for mode {props.greasePencil_layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)}"
        )

        utils_greasepencil.deleteLayerKeyFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_ToggleOnionSkin(Operator):
    bl_idname = "uas_shot_manager.greasepencil_toggleonionskin"
    bl_label = "Onion Skin"
    bl_description = "Toggle Grease Pencil viewport overlay onion skin"
    bl_options = {"INTERNAL"}

    # https://blender.stackexchange.com/questions/162459/access-viewport-overlay-options-using-python-api
    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        if spaceDataViewport is not None:
            spaceDataViewport.overlay.use_gpencil_onion_skin = not spaceDataViewport.overlay.use_gpencil_onion_skin
        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_ToggleCanvas(Operator):
    bl_idname = "uas_shot_manager.greasepencil_togglecanvas"
    bl_label = "Canvas"
    bl_description = "Toggle Grease Pencil viewport overlay canvas"
    bl_options = {"INTERNAL"}

    # https://blender.stackexchange.com/questions/162459/access-viewport-overlay-options-using-python-api
    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        spaceDataViewport = props.getValidTargetViewportSpaceData(context)
        if spaceDataViewport is not None:
            spaceDataViewport.overlay.use_gpencil_grid = not spaceDataViewport.overlay.use_gpencil_grid
        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_SetLayerAndMat(Operator):
    bl_idname = "uas_shot_manager.greasepencil_setlayerandmat"
    bl_label = ""
    bl_description = "Set active layer and current material"
    bl_options = {"INTERNAL", "UNDO"}

    "layerID:    Can be CANVAS, BG_INK, BG_FILL"
    layerID: StringProperty(
        name="Layer ID",
        default="",
    )

    layerName: StringProperty(
        name="Layer Name",
        default="",
    )

    gpObjName: StringProperty(
        name="grease Pencil Object Name",
        default="",
    )

    @classmethod
    def description(self, context, properties):
        descr = "Set layer to active and pick the associated material"
        # print("properties: ", properties)

        warningStr = " - *** Layer not found ***" if "WARNING" in properties.layerID else ""

        if "CANVAS" in properties.layerID:
            descr = f"Canvas Layer{warningStr}\n{descr}"
        elif "BG_INK" in properties.layerID:
            descr = f"BG Ink Layer{warningStr}\n{descr}"
        elif "BG_FILL" in properties.layerID:
            descr = f"BG Fill Layer{warningStr}\n{descr}"

        return descr

    def invoke(self, context, event):
        prefs = context.preferences.addons["shotmanager"].preferences
        props = context.scene.UAS_shot_manager_props
        # print(f"Layer and mat - ID: {self.layerID}, name:{self.gpObjName}")

        utils_greasepencil.activeGpLayerAndMat(bpy.context.scene.objects[self.gpObjName], self.layerName)

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_AddGreasePencil,
    UAS_ShotManager_OT_SelectGreasePencil,
    UAS_ShotManager_OT_AddCanvasToGreasePencil,
    UAS_ShotManager_OT_DrawOnGreasePencil,
    UAS_ShotManager_OT_RemoveGreasePencil,
    UAS_ShotManager_OT_EnableDisableGreasePencil,
    UAS_ShotManager_GreasePencilItem,
    UAS_ShotManager_GreasePencil_NextKey,
    UAS_ShotManager_GreasePencil_PreviousKey,
    UAS_ShotManager_GreasePencil_NewKeyFrame,
    UAS_ShotManager_GreasePencil_DuplicateKeyFrame,
    UAS_ShotManager_GreasePencil_DeleteKeyFrame,
    UAS_ShotManager_GreasePencil_ToggleOnionSkin,
    UAS_ShotManager_GreasePencil_ToggleCanvas,
    UAS_ShotManager_GreasePencil_SetLayerAndMat,
    #   UAS_ShotManager_OT_ChangeGreasePencilOpacity,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
