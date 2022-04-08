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
Shot Manager grease pencil operators
"""

from inspect import currentframe
import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, PointerProperty, CollectionProperty

from .greasepencil import setInkLayerReadyToDraw

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil


class UAS_ShotManager_OT_AddGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_grease_pencil"
    bl_label = "Add Grease Pencil"
    bl_description = "Add Grease Pencil to the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    shotName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        take = props.getCurrentTake()
        shotList = take.shots

        if self.shotName not in shotList or shotList[self.shotName] is None:
            print(f"Specified shot {self.shotName} not found in current take - Cancelling...")
            return {"CANCELLED"}

        shot = shotList[self.shotName]
        if not shot.isCameraValid():
            print("Camera is invalid for grease pencil parenting - Cancelling...")
            return {"CANCELLED"}

        # Monkey patch the shot property to avoid circular registration

        # from shotmanager.features.greasepencil.greasepencil_properties import GreasePencilProperties

        # from shotmanager.properties.shot import UAS_ShotManager_Shot

        # shot.gpStoryboard = bpy.props.PointerProperty(type=GreasePencilProperties)
        # UAS_ShotManager_Shot.gpStoryboard = PointerProperty(type=GreasePencilProperties)

        # shot["gpStoryboard"] = None
        # shot.gpStoryboard = None
        # shot.gpStoryboard = GreasePencilProperties()
        # print(f" gpStoryboard: {shot.gpStoryboard}")

        # if not hasattr(shot, "greasePencils"):
        #     UAS_ShotManager_Shot.gpList = CollectionProperty(type=GreasePencilProperties)
        # newShot = GreasePencilProperties()
        # newShot = GreasePencilProperties()

        gpProperties, gpObj = shot.addGreasePencil(type="STORYBOARD")
        # gpProperties.initialize(shot)

        # gpName = shot.camera.name + "_GP"
        # gpObj = utils_greasepencil.create_new_greasepencil(gpName, parentCamera=shot.camera, location=[0, 0, -0.5])

        # utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM", camera=shot.camera)

        gpProperties.updateGreasePencilToFrustum()

        utils.select_object(gpObj)

        return {"FINISHED"}


# class UAS_ShotManager_OT_AddGreasePencil(Operator):
#     bl_idname = "uas_shot_manager.add_grease_pencil"
#     bl_label = "Add Grease Pencil"
#     bl_description = "Add Grease Pencil to the camera of the specified shot"
#     bl_options = {"INTERNAL", "UNDO"}

#     cameraGpName: StringProperty(default="")

#     def execute(self, context):
#         scene = context.scene

#         if self.cameraGpName not in scene.objects or scene.objects[self.cameraGpName] is None:
#             print("Camera is invalid for grease pencil parenting - Cancelling...")
#             return {"CANCELLED"}
#         else:
#             cam = scene.objects[self.cameraGpName]
#             gpName = cam.name + "_GP"
#             gpObj = utils_greasepencil.create_new_greasepencil(gpName, parentCamera=cam, location=[0, 0, -0.5])

#             utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM", camera=cam)

#             utils.select_object(gpObj)

#         return {"FINISHED"}


class UAS_ShotManager_OT_SelectShotGreasePencil(Operator):
    bl_idname = "uas_shot_manager.select_shot_grease_pencil"
    bl_label = "Select Shot Storyboard Frame"
    bl_description = "Select the storyboard frame from the specified shot"
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
                gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
                if gp_child is not None:
                    bpy.ops.object.select_all(action="DESELECT")
                    bpy.context.view_layer.objects.active = gp_child
                    gp_child.select_set(True)

        utils.setPropertyPanelContext(bpy.context, "DATA")

        return {"FINISHED"}


class UAS_ShotManager_OT_SelectGreasePencilObject(Operator):
    bl_idname = "uas_shot_manager.select_grease_pencil_object"
    bl_label = "Select Grease Pencil"
    bl_description = "Select Grease Pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        # bpy.ops.outliner.item_activate(extend=True, deselect_all=True)

        # bpy.ops.object.select_all(action="DESELECT")
        if context.object is None:
            bpy.ops.object.select_all(action="DESELECT")
        else:
            # bpy.data.objects["Cube"].select_get()
            for obj in context.selected_objects:
                obj.select_set(False)
            bpy.context.view_layer.objects.active = context.object
            bpy.data.objects[context.object.name].select_set(True)

            utils.setPropertyPanelContext(bpy.context, "DATA")

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

        # get camera parent
        parentCam = gpObj.parent
        utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM", camera=parentCam)

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
        props = scene.UAS_shot_manager_props

        if context.active_object is not None:
            if context.active_object.mode == "PAINT_GPENCIL":
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
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
            gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)

        props.setCurrentShotByIndex(props.selected_shot_index, changeTime=False)

        if gp_child is None:
            print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
            return {"CANCELLED"}
        elif not gp_child.visible_get():
            print("Grease Pencil cannot be applied on hidden objects - Cancelling...")
            return {"CANCELLED"}
        else:
            # if context.active_object.mode == "PAINT_GPENCIL":
            #     if gp_child != context.active_object:
            #         # we change the current object
            #     bpy.ops.gpencil.paintmode_toggle()
            #     return {"FINISHED"}

            # if context.active_object is not None and context.active_object.mode != "OBJECT":
            #     bpy.ops.object.mode_set(mode="OBJECT")
            # bpy.ops.object.select_all(action="DESELECT")
            # bpy.context.view_layer.objects.active = gp_child

            # shot.updateGreasePencils()
            # set ink layer, else topmost layer
            setInkLayerReadyToDraw(gp_child)

            utils_greasepencil.switchToDrawMode(gp_child)
            # gp_child.select_set(True)
            # gp_child.hide_select = False
            # gp_child.hide_viewport = False
            # gp_child.hide_render = False
            # bpy.ops.gpencil.paintmode_toggle()

            # context.scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
            # context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"

        return {"FINISHED"}


class UAS_ShotManager_OT_UpdateGreasePencil(Operator):
    bl_idname = "uas_shot_manager.update_grease_pencil"
    bl_label = "Update Grease Pencil"
    bl_description = "Update the Grease Pencil of the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)

    # def invoke(self, context, event):
    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        props.setSelectedShotByIndex(self.shotIndex)
        if context.active_object is not None and context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        shot = props.getShotByIndex(props.selected_shot_index)
        if shot is not None:
            shot.updateGreasePencils()

        return {"FINISHED"}


class UAS_ShotManager_OT_RemoveGreasePencil(Operator):
    bl_idname = "uas_shot_manager.remove_grease_pencil"
    bl_label = "Remove Storyboard Frames"
    bl_description = "Remove the storyboard frames of the specified shots"
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)

    def invoke(self, context, event):
        props = context.scene.UAS_shot_manager_props
        shotList = []

        # print("Remove Grease Pencil: shotIndex: ", self.shotIndex)
        if self.shotIndex < 0:
            take = context.scene.UAS_shot_manager_props.getCurrentTake()
            shotList = take.getShotsList(ignoreDisabled=props.shotsGlobalSettings.alsoApplyToDisabledShots)
        else:
            shot = props.getShotByIndex(self.shotIndex)
            if shot is not None:
                shotList.append(shot)

        for shot in shotList:
            # print("   del gp for shot ", shot.name)
            shot.removeGreasePencil()
            # if shot.camera is not None:
            #     gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
            #     if gp_child is not None:
            #         bpy.data.objects.remove(gp_child, do_unlink=True)

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


class UAS_ShotManager_OT_ClearLayer(Operator):
    bl_idname = "uas_shot_manager.clear_layer"
    bl_label = "Clear Layer"
    bl_description = "Delete all the strokes of the current layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        if context.object is None:
            bpy.ops.object.select_all(action="DESELECT")
        else:
            # bpy.data.objects["Cube"].select_get()
            for obj in context.selected_objects:
                obj.select_set(False)
            bpy.context.view_layer.objects.active = context.object
            bpy.data.objects[context.object.name].select_set(True)

            objIsGP = "GPENCIL" == context.object.type
            if objIsGP:
                gp = context.object
                # gpl = context.active_gpencil_layer
                gpl = gp.data.layers.active
                if gpl and gpl.info is not None and not gpl.lock:
                    layerFrameInd = utils_greasepencil.getLayerFrameIndexAtFrame(gp, scene.frame_current, "ACTIVE")
                    if -1 == layerFrameInd:
                        layerFrameTime = utils_greasepencil.getLayerPreviousFrame(gp, scene.frame_current, "ACTIVE")
                        layerFrameInd = utils_greasepencil.getLayerFrameIndexAtFrame(gp, layerFrameTime, "ACTIVE")
                    if -1 != layerFrameInd:
                        gpl.frames[layerFrameInd].clear()

                        # required for refresh
                        gpl.hide = not gpl.hide
                        gpl.hide = not gpl.hide

        return {"FINISHED"}


class UAS_ShotManager_GreasePencilItem(Operator):
    bl_idname = "uas_shot_manager.greasepencilitem"
    bl_label = "Select Storyboard Frame"
    bl_description = (
        "+ Shift: Add a storyboard frame to the current selection"
        "\n+ Alt: Select storyboard frame and switch to Draw mode"
    )
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(default=0)

    def invoke(self, context, event):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        props.setSelectedShotByIndex(self.index)
        shot = props.getShotByIndex(self.index)
        gp_child = shot.getGreasePencilObject()

        try:
            bpy.ops.object.select_all(action="DESELECT")
        except Exception:
            pass

        if gp_child is None and event.alt and not event.ctrl and not event.shift:

            if shot.camera is None or shot.camera.name not in scene.objects or scene.objects[shot.camera.name] is None:
                print("Camera is invalid for grease pencil parenting - Cancelling...")
                return {"CANCELLED"}

            utils_greasepencil.create_new_greasepencil(
                shot.camera.name + "_GP", parentCamera=shot.camera, location=[0, 0, 0]
            )
            gp_child = shot.getGreasePencilObject()

        if gp_child is not None:
            if not event.shift or event.alt:
                if context.active_object is not None and context.active_object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="DESELECT")
            gp_child.select_set(True)
            context.view_layer.objects.active = gp_child

            # add to selection
            if event.shift and not event.ctrl and not event.alt:
                gp_child.select_set(True)
                context.view_layer.objects.active = gp_child

            # draw mode
            if event.alt and not event.ctrl and not event.shift:
                props.setCurrentShotByIndex(self.index)
                shot.updateGreasePencils()
                # set ink layer, else topmost layer
                setInkLayerReadyToDraw(gp_child)
                utils_greasepencil.switchToDrawMode(gp_child)

        utils.setPropertyPanelContext(bpy.context, "DATA")

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


class UAS_ShotManager_GreasePencil_FrameOperation(Operator):
    bl_idname = "uas_shot_manager.greasepencil_frameoperation"
    bl_label = "Frame Operation"
    bl_description = "Add, duplicate or delete drawing frame to the selected Grease Pencil"
    bl_options = {"INTERNAL", "UNDO"}

    layersMode: StringProperty(
        name="Layers Mode",
        default="",
    )

    # can be "NEW", "DUPLICATE", "DELETE"
    frameMode: StringProperty(
        name="Frame Mode",
        default="NEW",
    )

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
            f"On a frame for mode {props.greasePencil_layersMode}: {utils_greasepencil.isCurrentFrameOnLayerFrame(gp, context.scene.frame_current, props.greasePencil_layersMode)}"
        )

        if "NEW" == self.frameMode:
            utils_greasepencil.addFrameToLayer(gp, context.scene.frame_current, props.greasePencil_layersMode)
        elif "DUPLICATE" == self.frameMode:
            utils_greasepencil.duplicateFrameToLayer(gp, context.scene.frame_current, props.greasePencil_layersMode)
            pass
        elif "DELETE" == self.frameMode:
            pass

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


_classes = (
    UAS_ShotManager_OT_AddGreasePencil,
    UAS_ShotManager_OT_SelectShotGreasePencil,
    UAS_ShotManager_OT_SelectGreasePencilObject,
    UAS_ShotManager_OT_AddCanvasToGreasePencil,
    UAS_ShotManager_OT_ToggleGreasePencilDrawMode,
    UAS_ShotManager_OT_DrawOnGreasePencil,
    UAS_ShotManager_OT_UpdateGreasePencil,
    UAS_ShotManager_OT_RemoveGreasePencil,
    UAS_ShotManager_OT_EnableDisableGreasePencil,
    UAS_ShotManager_OT_ClearLayer,
    UAS_ShotManager_GreasePencilItem,
    UAS_ShotManager_GreasePencil_NextKey,
    UAS_ShotManager_GreasePencil_PreviousKey,
    UAS_ShotManager_GreasePencil_FrameOperation,
    UAS_ShotManager_GreasePencil_ToggleOnionSkin,
    UAS_ShotManager_GreasePencil_ToggleCanvas,
    #   UAS_ShotManager_OT_ChangeGreasePencilOpacity,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
