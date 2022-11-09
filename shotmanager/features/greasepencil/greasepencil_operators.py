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

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

from . import greasepencil as gp

from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


class UAS_ShotManager_OT_AddGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_grease_pencil"
    bl_label = "Add Grease Pencil"
    bl_description = "Add Grease Pencil to the specified shot"
    bl_options = {"INTERNAL", "UNDO"}

    shotName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
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

        gpProperties, gpObj = shot.addGreasePencil(mode="STORYBOARD")
        # gpProperties.initialize(shot)

        # gpName = shot.camera.name + "_GP"
        # gpObj = gp.createStoryboarFrameGP(gpName, parentCamera=shot.camera, location=[0, 0, -0.5])

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
#             gpObj = gp.createStoryboarFrameGP(gpName, parentCamera=cam, location=[0, 0, -0.5])

#             utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM", camera=cam)

#             utils.select_object(gpObj)

#         return {"FINISHED"}


class UAS_ShotManager_OT_SelectShotGreasePencil(Operator):
    bl_idname = "uas_shot_manager.select_shot_grease_pencil"
    bl_label = "Select Storyboard Frame"
    bl_description = "Select the storyboard frame of the current shot"
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty(default=-1)

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if -1 == properties.index:
            descr = "Select the storyboard frame of the current shot"
        else:
            descr = "Select the storyboard frame of the selected shot"
        return descr

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def invoke(self, context, event):
        scene = context.scene
        props = config.getAddonProps(scene)

        # select SELECTED shot
        # if event.shift and not event.ctrl and not event.alt:

        # NOTE: we use context.object here instead of context.active_object because
        # when the eye icon of the object is closed (meaning object.hide_get() == True)
        # then context.active_object is None
        # if context.active_object is not None and context.active_object.mode != "OBJECT":
        if context.object is not None and context.object.mode != "OBJECT":
            if not context.object.visible_get():
                context.object.hide_viewport = False
                bpy.ops.object.mode_set(mode="OBJECT")

        if -1 == self.index:
            shot = props.getShotByIndex(props.current_shot_index)
        else:
            props.setSelectedShotByIndex(self.index)
            shot = props.getShotByIndex(props.selected_shot_index)

        if shot is not None:
            if shot.isCameraValid() is not None:
                gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
                if gp_child is not None:
                    # bpy.ops.object.select_all(action="DESELECT")
                    # bpy.context.view_layer.objects.active = gp_child
                    # gp_child.select_set(True)
                    utils.select_object(gp_child)

        utils.setPropertyPanelContext(bpy.context, "DATA")

        # # select CURRENT shot
        # elif not event.ctrl and not event.shift and not event.alt:

        return {"FINISHED"}


class UAS_ShotManager_OT_SelectGreasePencilObject(Operator):
    bl_idname = "uas_shot_manager.select_grease_pencil_object"
    bl_label = "Select the grease pencil object being drawn"
    bl_description = "Select Grease Pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        # bpy.ops.outliner.item_activate(extend=True, deselect_all=True)

        gp = None
        if self.gpName in bpy.context.scene.objects:
            gp = bpy.context.scene.objects[self.gpName]

        # bpy.ops.object.select_all(action="DESELECT")
        if gp is None:
            bpy.ops.object.select_all(action="DESELECT")
        else:
            # bpy.data.objects["Cube"].select_get()
            for obj in context.selected_objects:
                obj.select_set(False)
            bpy.context.view_layer.objects.active = gp
            bpy.data.objects[gp.name].select_set(True)
            # utils.select_object(gp)

            utils.setPropertyPanelContext(bpy.context, "DATA")

        return {"FINISHED"}


class UAS_ShotManager_OT_AddCanvasToGreasePencil(Operator):
    bl_idname = "uas_shot_manager.add_canvas_to_grease_pencil"
    bl_label = "Add Canvas to Grease Pencil"
    bl_description = "Add a  canvas layer to the grease pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    # @classmethod
    # def poll(self, context):
    #     selectionIsPossible = context.active_object is None or context.active_object.mode == "OBJECT"
    #     return selectionIsPossible

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        gpObj = context.scene.objects[self.gpName]

        # get camera parent
        parentCam = gpObj.parent
        canvasPreset = props.stb_frameTemplate.getPresetByID("CANVAS")
        utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, canvasPreset, order="BOTTOM", camera=parentCam)

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
        props = config.getAddonProps(scene)

        props.setSelectedShotByIndex(self.shotIndex)

        # NOTE: we use context.object here instead of context.active_object because
        # when the eye icon of the object is closed (meaning object.hide_get() == True)
        # then context.active_object is None
        # if context.active_object is not None and context.active_object.mode != "OBJECT":
        if context.object is not None and context.object.mode != "OBJECT":
            if not context.object.visible_get():
                context.object.hide_viewport = False
            bpy.ops.object.mode_set(mode="OBJECT")

        shot = props.getShotByIndex(props.selected_shot_index)
        if shot is not None:
            shot.updateGreasePencils()

        return {"FINISHED"}


class UAS_ShotManager_OT_RemoveGreasePencil(Operator):
    bl_idname = "uas_shot_manager.remove_grease_pencil"
    bl_label = "Remove Storyboard Frames"
    bl_description = (
        "Remove the storyboard frames of the selected shot(s)"
        "\nand delete the associated grease pencil and empty children objects"
    )
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)
    alsoApplyToDisabledShots: BoolProperty(default=True)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        shotList = []

        # print("Remove Grease Pencil: shotIndex: ", self.shotIndex)
        if self.shotIndex < 0:
            take = props.getCurrentTake()
            shotList = take.getShotsList(ignoreDisabled=not self.alsoApplyToDisabledShots)
        else:
            shot = props.getShotByIndex(self.shotIndex)
            if shot is not None:
                shotList.append(shot)

        for shot in shotList:
            # print("   del gp for shot ", shot.name)
            shot.removeGreasePencil()
            # if shot.isCameraValid():
            #     gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
            #     if gp_child is not None:
            #         bpy.data.objects.remove(gp_child, do_unlink=True)

        return {"FINISHED"}


class UAS_ShotManager_OT_ShowHideGreasePencil(Operator):
    bl_idname = "uas_shot_manager.showhidegreasepencil"
    bl_label = "Show / Hide Grease Pencil"
    bl_description = "Alternatively display or hide the grease pencil used by the camera of the shots"
    bl_options = {"INTERNAL", "UNDO"}

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)

        # prefs = config.getAddonPrefs()
        # bpy.ops.uas_shots_settings.use_greasepencil(useGreasepencil=prefs.enableGreasePencil)
        # prefs.enableGreasePencil = not prefs.enableGreasePencil

        props.enableGreasePencil(not props.use_greasepencil)

        return {"FINISHED"}


class UAS_ShotManager_OT_ShowHideCameras(Operator):
    bl_idname = "uas_shot_manager.showhidecameras"
    bl_label = "Show / Hide Cameras"
    bl_description = "Alternatively display or hide the cameras used by the storyboard frames"
    bl_options = {"INTERNAL", "UNDO"}

    visible: BoolProperty(default=True)

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        props.displayStoryboardFramesCameras(self.visible)
        return {"FINISHED"}


# class UAS_ShotManager_OT_ChangeGreasePencilOpacity(Operator):
#     bl_idname = "uas_shot_manager.change_grease_pencil_opacity"
#     bl_label = "Opacity"
#     bl_description = "Change Grease Pencil opacity"
#     bl_options = {"INTERNAL", "UNDO"}

# gpName: StringProperty(default="")


#     def execute(self, context):
#         scene = context.scene
#         props = config.getAddonProps(scene)

#         if self.gpName not in scene.objects or scene.objects[self.gpName] is None:
#             print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
#             return {"CANCELLED"}
#         else:
#             gp_child = scene.objects[self.gpName]

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
    bl_description = (
        "Delete all the strokes of the active key frame of the current layer."
        "\nNote that the keys themselves are NOT removed."
        "\n+ Shift: Delete strokes on keys at current time on EVERY layer"
    )
    bl_options = {"REGISTER", "UNDO"}

    gpName: StringProperty(default="")
    action: StringProperty(default="DO_NOTHING")

    def invoke(self, context, event):
        self.action = "DO_NOTHING"

        if not event.ctrl and not event.shift and not event.alt:
            self.action = "CURRENT"
        elif not event.ctrl and event.shift and not event.alt:
            self.action = "ALL"

        if "DO_NOTHING" == self.action:
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context):
        scene = context.scene

        gp = None
        if "" == self.gpName:
            gp = context.object
        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]

        # props = config.getAddonProps(scene)

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
                # gp = context.object
                # gpl = context.active_gpencil_layer

                for gpl in gp.data.layers:
                    # gpl = gp.data.layers.active
                    if "ALL" == self.action or gpl == gp.data.layers.active:
                        if gpl and gpl.info is not None and not gpl.lock:
                            layerFrameInd = utils_greasepencil.getLayerKeyFrameIndexAtFrame(
                                gp, scene.frame_current, "ACTIVE"
                            )
                            if -1 == layerFrameInd:
                                layerFrameTime = utils_greasepencil.getLayerPreviousFrame(
                                    gp, scene.frame_current, "ACTIVE"
                                )
                                layerFrameInd = utils_greasepencil.getLayerKeyFrameIndexAtFrame(
                                    gp, layerFrameTime, "ACTIVE"
                                )
                            if -1 < layerFrameInd < len(gpl.frames):
                                gpl.frames[layerFrameInd].clear()

                                # required for refresh
                                gpl.hide = not gpl.hide
                                gpl.hide = not gpl.hide

        return {"INTERFACE"}


class UAS_ShotManager_OT_PinGreasePencilObject(Operator):
    bl_idname = "uas_shot_manager.pin_grease_pencil_object"
    bl_label = "Pin the grease pencil object being drawn"
    # bl_description = "Select Grease Pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    pin: BoolProperty(default=False)
    pinnedObjName: StringProperty(default="")

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        _logger.debug_ext(f"pinnedObjName: {self.pinnedObjName}, pin: {self.pin}")

        if self.pin:
            if "" != self.pinnedObjName and self.pinnedObjName in context.scene.objects:
                props.stb_editedGPencilName = self.pinnedObjName

        props.stb_hasPinnedObject = self.pin

        # # bpy.ops.outliner.item_activate(extend=True, deselect_all=True)

        # # bpy.ops.object.select_all(action="DESELECT")
        # if context.object is None:
        #     bpy.ops.object.select_all(action="DESELECT")
        # else:
        #     # bpy.data.objects["Cube"].select_get()
        #     for obj in context.selected_objects:
        #         obj.select_set(False)
        #     bpy.context.view_layer.objects.active = context.object
        #     bpy.data.objects[context.object.name].select_set(True)

        #     utils.setPropertyPanelContext(bpy.context, "DATA")

        return {"FINISHED"}


class UAS_ShotManager_OT_ToggleGreasePencilDrawMode(Operator):
    bl_idname = "uas_shot_manager.toggle_grease_pencil_draw_mode"
    bl_label = ""
    bl_description = "Toggle Grease Pencil Draw Mode"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    layerName: StringProperty(
        name="Layer Name",
        default="",
    )

    def execute(self, context):
        gp = None
        if "" == self.gpName:
            # NOTE: we use context.object here instead of context.active_object because
            # when the eye icon of the object is closed (meaning object.hide_get() == True)
            # then context.active_object is None
            gp = context.object
        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]

        if gp is not None:
            props = config.getAddonProps(context.scene)
            if "OBJECT" != gp.mode:
                # if context.active_object.mode == "PAINT_GPENCIL":
                # bpy.ops.object.mode_set(mode="OBJECT")
                utils_greasepencil.switchToObjectMode()
            else:
                utils_greasepencil.switchToDrawMode(context, gp)
                props.isEditingStoryboardFrame = True

                if props.shotsGlobalSettings.stb_camPOV_forFreeGP:
                    props.getCurrentShot().setCameraToViewport()
                    context.scene.tool_settings.gpencil_stroke_placement_view3d = (
                        props.shotsGlobalSettings.stb_strokePlacement_forFreeGP
                    )
                    context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"

                    if "" != self.layerName:
                        if props.shotsGlobalSettings.stb_changeCursorPlacement_forFreeGP:
                            layerName = self.layerName
                            utils_greasepencil.place3DCursor(gp, context.scene.frame_current, layerName)

        return {"FINISHED"}


# wkip toto 2022_10_14
# class UAS_ShotManager_OT_DrawOnGreasePencil(Operator):
#     bl_idname = "uas_shot_manager.draw_on_grease_pencil"
#     bl_label = "Draw on Grease Pencil"
#     bl_description = "Draw on the Grease Pencil of the specified shot"
#     bl_options = {"INTERNAL"}

#     def execute(self, context):
#         scene = context.scene
#         props = config.getAddonProps(scene)

#         shot = None
#         gp_child = None
#         if not ("SELECTED" == props.current_shot_properties_mode):
#             shot = props.getCurrentShot()
#         else:
#             shot = props.getShotByIndex(props.selected_shot_index)

#         if shot is not None:
#             gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)

#         props.setCurrentShotByIndex(props.selected_shot_index, changeTime=False)

#         if gp_child is None:
#             print("Grease Pencil Child is invalid for grease pencil parenting - Cancelling...")
#             return {"CANCELLED"}
#         elif not gp_child.visible_get():
#             print("Grease Pencil cannot be applied on hidden objects - Cancelling...")
#             return {"CANCELLED"}
#         else:
#             # if context.active_object.mode == "PAINT_GPENCIL":
#             #     if gp_child != context.active_object:
#             #         # we change the current object
#             #     bpy.ops.gpencil.paintmode_toggle()
#             #     return {"FINISHED"}

#             # if context.active_object is not None and context.active_object.mode != "OBJECT":
#             #     bpy.ops.object.mode_set(mode="OBJECT")
#             # bpy.ops.object.select_all(action="DESELECT")
#             # bpy.context.view_layer.objects.active = gp_child

#             # shot.updateGreasePencils()
#             # set ink layer, else topmost layer
#             gp.setInkLayerReadyToDraw(gp_child)

#             utils_greasepencil.switchToDrawMode(context, gp_child)
#             props.isEditingStoryboardFrame = True

#             # gp_child.select_set(True)
#             # gp_child.hide_select = False
#             # gp_child.hide_viewport = False
#             # gp_child.hide_render = False
#             # bpy.ops.gpencil.paintmode_toggle()

#             # context.scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
#             # context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"

#             utils.setPropertyPanelContext(context, "DATA")

#         return {"FINISHED"}


class UAS_ShotManager_GreasePencilSelectAndDraw(Operator):
    bl_idname = "uas_shot_manager.greasepencil_select_and_draw"
    bl_label = " "
    bl_description = (
        "Select Storyboard Frame"
        "\n+ Shift: Select the storyboard frame and add it to the current selection"
        "\n+ Alt: Select the storyboard frame and switch to Draw mode"
    )
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty(default=0)

    # can be SELECT, DRAW
    mode: StringProperty(default="SELECT")

    # can be DO_NOTHING, SELECT, SELECT_AND_DRAW, ADD_TO_SELECTION
    action: StringProperty(default="DO_NOTHING")
    ignoreSetCurrentShot: BoolProperty(default=False)
    toggleDrawEditing: BoolProperty(default=False)

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "DRAW" == properties.mode:
            descr = (
                "Draw on Storyboard Frame"
                "\n+ Ctrl: Select the storyboard frame"
                "\n+ Shift: Select the storyboard frame and add it to the current selection"
            )
        # "SELECT"
        else:
            descr = (
                "Select Storyboard Frame"
                "\n+ Shift: Select the storyboard frame and add it to the current selection"
                "\n+ Alt: Select the storyboard frame and switch to Draw mode"
            )
        return descr

    def invoke(self, context, event):
        props = config.getAddonProps(context.scene)
        self.action = "DO_NOTHING"

        if "DRAW" == self.mode:
            if not event.ctrl and not event.shift:  # and not event.alt:
                self.action = "SELECT_AND_DRAW"
            elif event.ctrl and not event.shift and not event.alt:
                self.action = "SELECT"
            elif not event.ctrl and event.shift and not event.alt:
                self.action = "ADD_TO_SELECTION"
        # "SELECT"
        else:
            if not event.ctrl and not event.shift and not event.alt:
                self.action = "SELECT"
            elif not event.ctrl and event.shift and not event.alt:
                self.action = "ADD_TO_SELECTION"
            elif not event.ctrl and not event.shift and event.alt:
                self.action = "SELECT_AND_DRAW"

        props.setSelectedShotByIndex(self.index, callUpdateFunc=False)
        props.expand_storyboard_properties = True
        self.ignoreSetCurrentShot = False

        if "DO_NOTHING" == self.action:
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = config.getAddonProps(scene)
        framePreset = props.stb_frameTemplate
        # props.setSelectedShotByIndex(self.index)
        shot = props.getShotByIndex(self.index)
        gp_child = shot.getGreasePencilObject("STORYBOARD")

        # try:
        #     bpy.ops.object.select_all(action="DESELECT")
        # except Exception:
        #     pass

        if gp_child is None and "SELECT_AND_DRAW" == self.action:

            utils_greasepencil.switchToObjectMode()
            return {"FINISHED"}

            if shot.camera is None or shot.camera.name not in scene.objects or scene.objects[shot.camera.name] is None:
                print("Camera is invalid for grease pencil parenting - Cancelling...")
                return {"CANCELLED"}

            gp.createStoryboarFrameGP(
                shot.camera.name + "_GP", framePreset, parentCamera=shot.camera, location=[0, 0, 0]
            )
            gp_child = shot.getGreasePencilObject("STORYBOARD")

        if gp_child is not None:
            # if not event.shift or event.alt:
            if "SELECT" == self.action:
                # if context.active_object is not None and context.active_object.mode != "OBJECT":
                #     bpy.ops.object.mode_set(mode="OBJECT")
                if "OBJECT" != gp_child.mode:
                    utils_greasepencil.switchToObjectMode()
                utils.select_object(gp_child)

            # add to selection
            if "ADD_TO_SELECTION" == self.action:
                utils.add_to_selection(gp_child)

            # draw mode TOGGLE
            elif "SELECT_AND_DRAW" == self.action:

                # get out of GP Draw mode for the edited shot
                if self.toggleDrawEditing:
                    # if the current shot is being edited then we go back to OBJECT mode
                    # editedGP = props.getEditedStoryboardFrame()
                    # editedGP = props.getEditedGPShot(shotType="STORYBOARD")
                    editedGP = props.getEditedGPShot(shotType=None)
                    if editedGP == shot:
                        utils_greasepencil.switchToObjectMode()
                        utils.select_object(gp_child)
                        props.isEditingStoryboardFrame = False
                        return {"FINISHED"}

                # get out of GP Draw mode for the edited shot
                if utils_greasepencil.isAnotherObjectInSubMode(gp_child):
                    utils_greasepencil.switchToObjectMode()

                utils.select_object(gp_child)

                # quit draw mode
                # wkipwkipwkipwkip
                if "OBJECT" != gp_child.mode:
                    # get out of GP Draw mode for the edited shot
                    if self.toggleDrawEditing:
                        utils_greasepencil.switchToObjectMode()

                # enter draw mode
                else:
                    if not self.ignoreSetCurrentShot:
                        props.setCurrentShotByIndex(self.index)
                    shot.updateGreasePencils()
                    # set ink layer, else topmost layer
                    gp.setInkLayerReadyToDraw(gp_child)
                    utils_greasepencil.switchToDrawMode(context, gp_child)
                    props.isEditingStoryboardFrame = True

        # utils.setPropertyPanelContext(context, "DATA")

        return {"FINISHED"}


class UAS_ShotManager_DetachStoryboardFrame(Operator):
    bl_idname = "uas_shot_manager.detach_storyboard_frame"
    bl_label = "Detach Storyboard Frame"
    bl_description = "Unlink the Storyboard Frame from the shot and make it free in the scene"
    bl_options = {"INTERNAL", "UNDO"}

    shotIndex: IntProperty(default=-1)

    def execute(self, context):
        props = config.getAddonProps(context.scene)

        shot = props.getShotByIndex(self.shotIndex)
        if shot is not None:
            shot.detachGreasePencil()

        return {"FINISHED"}


class UAS_ShotManager_ResetUsagePreset(Operator):
    bl_idname = "uas_shot_manager.resetusagepreset"
    bl_label = "Reset Usage Preset(s)"
    bl_description = "Reset Grease Pencil Usage Preset to default values"
    bl_options = {"INTERNAL", "UNDO"}

    # can be SCENE or ADDON_PREFS"
    mode: StringProperty(default="SCENE")

    # can be ALL to reset all the presets
    presetID: StringProperty(default="")

    def execute(self, context):
        prefs = config.getAddonPrefs()

        if "SCENE" == self.mode:
            props = config.getAddonProps(context.scene)
        else:
            props = prefs
        # props.stb_frameTemplate.updatePresets(mode="SCENE")

        if "ALL" == self.presetID:
            props.stb_frameTemplate.resetAllPresetsToDefault()
        elif "" != self.presetID:
            props.stb_frameTemplate.resetPresetToDefaultByID(self.presetID)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_UINavigationKeys(Operator):
    """This operator is to be used by the GUI only since it has
    different behaviors accorting to the key pressed when called,
    and then creating conflicts if used with operator key mapping
    """

    bl_idname = "uas_shot_manager.greasepencil_ui_navigation_keys"
    bl_label = ""
    bl_description = (
        "Jump between key frames of the specified layer of the grease pencil object" "\n+ Ctrl: Jump between shots"
    )
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    # can be GPKEYFRAME or SHOT
    mode: StringProperty(default="GPKEYFRAME")

    # can be PREVIOUS or NEXT
    navigDirection: StringProperty(default="PREVIOUS")

    @classmethod
    def description(self, context, properties):
        descr = "_"
        if "PREVIOUS" == properties.navigDirection:
            descr = (
                "Navigate to the previous key frame of the specified layer"
                "\n+ Ctrl: Jump to the start of the current shot, then to"
                "\nthe start of each previous shot"
            )
            descr += "\n\nShortcut: Ctrl Left Arrow"
        elif "NEXT" == properties.navigDirection:
            descr = (
                "Navigate to the next key frame of the specified layer" "\n+ Ctrl: Jump to the start of each next shot"
            )
            descr += "\n\nShortcut: Ctrl Right Arrow"
        return descr

    def invoke(self, context, event):
        _logger.debug_ext(
            f"Op greasepencil_ui_navigation_keys Invoke: name: {self.gpName}, dir: {self.navigDirection} - event.shift: {event.shift}",
            col="RED",
        )
        if not event.ctrl and not event.shift and not event.alt:
            self.mode = "GPKEYFRAME"
        elif event.ctrl and not event.shift and not event.alt:
            self.mode = "SHOT"
        # elif event.shift and not event.ctrl and not event.alt:
        # elif event.alt and not event.shift and not event.ctrl:
        return self.execute(context)

    def execute(self, context):
        if "GPKEYFRAME" == self.mode:
            bpy.ops.uas_shot_manager.greasepencil_navigateinkeyframes(
                navigDirection=self.navigDirection, gpName=self.gpName
            )
        elif "SHOT" == self.mode:
            bpy.ops.uas_shot_manager.playbar_gotoshotboundary(navigDirection=self.navigDirection, boundaryMode="START")
        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_NavigateInKeyFrames(Operator):
    bl_idname = "uas_shot_manager.greasepencil_navigateinkeyframes"
    bl_label = "Ubisoft Shot Mng - Navigate in grease pencil key frames"
    bl_description = "Jump from key frame to key frame on the specified grease pencil layer"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    # can be PREVIOUS or NEXT
    navigDirection: StringProperty(default="PREVIOUS")

    def invoke(self, context, event):
        # _logger.debug_ext(
        #     f"Op greasepencil_navigateinkeyframes Invoke: name: {self.gpName}, dir: {self.navigDirection} - event.shift: {event.shift}",
        #     col="RED",
        # )
        return self.execute(context)

    def execute(self, context):
        props = config.getAddonProps(context.scene)
        prefs = config.getAddonPrefs()

        gp = None
        gpIsStoryboardFrame = False

        if "" == self.gpName:
            # NOTE: Tricky situation when this operator is called from keyboard shortcut since it can refer to
            # the current storyboard frame or to the currently edited grease pencil object
            # we have to clearly define which is the referenced gp object between the current storyboard frame,
            # if there is one, the pinned gp object, if there is one, or the selected object in the 2.5D Grease Pencil panel
            # pinned gp object has the preseance over storyboard frame

            # currently edited gp object is used as a reference if:
            #   - the 2.5D panel is displayed (AND expanded: there is currently no way in the API to know if it is expanded)
            #   - and: either there is a pinned gp object or the edited gp object is valid (and not a storyboard frame)
            # otherwhise we check if there is a storyboard frame for the SELECTED shot
            # otherwhise we do nothing

            # edited 2.5D object
            if prefs.display_25D_greasepencil_panel:
                gpPinnedName = props.getPinnedGPObjectName()
                if "" != gpPinnedName:
                    gp = context.scene.objects[gpPinnedName]
                else:
                    if context.object is not None and "GPENCIL" == context.object.type:
                        gp = context.object

            # storyboard frame
            else:
                shot = props.getSelectedShot()
                if shot is not None:
                    gp_child = utils_greasepencil.get_greasepencil_child(shot.camera)
                    gpIsStoryboardFrame = gp_child is not None
                    if gpIsStoryboardFrame:
                        gp = gp_child

        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]
                gpIsStoryboardFrame = props.isStoryboardFrame(gp)

        if gp is not None:
            layerMode = "ACTIVE"
            if gpIsStoryboardFrame:
                if "" == props.greasePencil_layersMode:
                    if len(gp.data.layers):
                        props.greasePencil_layersMode = "ACTIVE"
                    else:
                        props.greasePencil_layersMode = "NOLAYER"

                if "NOLAYER" == props.greasePencil_layersMode:
                    return {"FINISHED"}
                # important to transform the layer ID in real layer name
                layerMode = props.getLayerModeFromID(props.greasePencil_layersMode)
            else:
                layerMode = props.greasePencil_layersModeB

            currentFrame = context.scene.frame_current
            if "PREVIOUS" == self.navigDirection:
                newFrame = utils_greasepencil.getLayerPreviousFrame(gp, currentFrame, layerMode)
            elif "NEXT" == self.navigDirection:
                newFrame = utils_greasepencil.getLayerNextFrame(gp, currentFrame, layerMode)
            context.scene.frame_current = newFrame

            if not gpIsStoryboardFrame and props.shotsGlobalSettings.stb_changeCursorPlacement_forFreeGP:
                layerName = "ACTIVE"  # self.layerName
                utils_greasepencil.place3DCursor(gp, context.scene.frame_current, layerName)

        return {"FINISHED"}


# wkip to delete
# class UAS_ShotManager_GreasePencil_NavigateInShots(Operator):
#     bl_idname = "uas_shot_manager.greasepencil_navigateinshots"
#     bl_label = ""
#     bl_description = (
#         "Jump to the previous key frame of the specified layer"
#         "\n+ Ctrl: Jump to the start of the current shot, then to"
#         "\nthe start of the previous shot"
#     )
#     bl_options = {"INTERNAL", "UNDO"}

#     gpName: StringProperty(default="")

#     # can be PREVIOUS or NEXT
#     navigDirection: StringProperty(default="PREVIOUS")

#     def invoke(self, context, event):
#         _logger.debug_ext(
#             f"Op greasepencil_navigateinshots Invoke: name: {self.gpName}, dir: {self.navigDirection} - event.shift: {event.shift}",
#             col="RED",
#         )
#         return self.execute(context)

#     def execute(self, context):
#         props = config.getAddonProps(context.scene)

#         currentFrame = context.scene.frame_current
#         if "PREVIOUS" == self.navigDirection:
#             props.goToPreviousShotBoundary(currentFrame, ignoreDisabled=True, boundaryMode="START")
#         elif "NEXT" == self.navigDirection:
#             props.goToNextShotBoundary(currentFrame, ignoreDisabled=True, boundaryMode="START")

#         return {"FINISHED"}


# https://blender.stackexchange.com/questions/142190/how-do-i-access-grease-pencil-data


class UAS_ShotManager_GreasePencil_NewKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_newkeyframe"
    bl_label = "New Drawing Frame"
    bl_description = "Add a new drawing frame to the specified Grease Pencil"
    bl_options = {"INTERNAL", "UNDO"}

    layersMode: StringProperty(
        name="Layers Mode",
        default="",
    )

    gpName: StringProperty(default="")

    def execute(self, context):
        gp = None
        if "" == self.gpName:
            gp = context.object
        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]

        if gp is not None:
            props = config.getAddonProps(context.scene)
            if "" == self.layersMode:
                if gp is not None:
                    props = config.getAddonProps(context.scene)
                    if "" == props.greasePencil_layersMode:
                        if len(gp.data.layers):
                            props.greasePencil_layersMode = "ACTIVE"
                        else:
                            props.greasePencil_layersMode = "NOLAYER"
                        self.layersMode = props.greasePencil_layersMode
            _logger.debug_ext(
                f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
            )

            layerMode = props.getLayerModeFromID(self.layersMode)
            utils_greasepencil.addKeyFrameToLayer(gp, context.scene.frame_current, layerMode)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_DuplicateKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_duplicatekeyframe"
    bl_label = "Duplicate Drawing Frame"
    bl_description = "Duplicate the previous drawing frame of the specified Grease Pencil at current time"
    bl_options = {"INTERNAL", "UNDO"}

    layersMode: StringProperty(
        name="Layers Mode",
        default="",
    )

    gpName: StringProperty(default="")

    def execute(self, context):
        gp = None
        if "" == self.gpName:
            gp = context.object
        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]

        if gp is not None:
            props = config.getAddonProps(context.scene)
            if "" == self.layersMode:
                if gp is not None:
                    props = config.getAddonProps(context.scene)
                    if "" == props.greasePencil_layersMode:
                        if len(gp.data.layers):
                            props.greasePencil_layersMode = "ACTIVE"
                        else:
                            props.greasePencil_layersMode = "NOLAYER"
                    self.layersMode = props.greasePencil_layersMode
            _logger.debug_ext(
                f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
            )

            layerMode = props.getLayerModeFromID(self.layersMode)
            utils_greasepencil.duplicateLayerKeyFrame(gp, context.scene.frame_current, layerMode)

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_DeleteKeyFrame(Operator):
    bl_idname = "uas_shot_manager.greasepencil_deletekeyframe"
    bl_label = "Delete Drawing Frame"
    bl_description = "Delete the drawing frame of the specified Grease Pencil at current time"
    bl_options = {"INTERNAL", "UNDO"}

    layersMode: StringProperty(
        name="Layers Mode",
        default="",
    )

    gpName: StringProperty(default="")

    def execute(self, context):
        gp = None
        if "" == self.gpName:
            gp = context.object
        else:
            if self.gpName in context.scene.objects:
                gp = context.scene.objects[self.gpName]

        if gp is not None:
            props = config.getAddonProps(context.scene)
            if "" == self.layersMode:
                if "" == props.greasePencil_layersMode:
                    if len(gp.data.layers):
                        props.greasePencil_layersMode = "ACTIVE"
                    else:
                        props.greasePencil_layersMode = "NOLAYER"
                    self.layersMode = props.greasePencil_layersMode
                _logger.debug_ext(
                    f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
                )

            layerMode = props.getLayerModeFromID(self.layersMode)
            utils_greasepencil.deleteLayerKeyFrame(gp, context.scene.frame_current, layerMode)

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

    materialName: StringProperty(
        name="Material Name",
        default="",
    )

    gpObjName: StringProperty(
        name="grease Pencil Object Name",
        default="",
    )

    @classmethod
    def description(self, context, properties):
        warningStrInd = properties.layerID.find("_WARNING")
        if -1 != warningStrInd:
            currentLayerID = properties.layerID[:warningStrInd]
        else:
            currentLayerID = properties.layerID
        descr = ""
        descr += " *** Layer not found ***\n" if -1 != warningStrInd else ""
        descr += f"Activate the layer of the mode {currentLayerID} and pick the associated material"
        descr += "\n+ Ctrl: Add key frame" "\n+ Shift: Duplicate previous key frame" "\n+ Alt: Delete key frame"
        return descr

    def invoke(self, context, event):
        # prefs = config.getAddonPrefs()
        # props = config.getAddonProps(context.scene)
        # print(f"Layer and mat - ID: {self.layerID}, name:{self.gpObjName}")

        # if not event.ctrl and not event.shift and not event.alt:
        utils_greasepencil.activateGpLayerAndMat(
            bpy.context.scene.objects[self.gpObjName], self.layerName, self.materialName
        )
        if event.ctrl and not event.shift and not event.alt:
            bpy.ops.uas_shot_manager.greasepencil_newkeyframe(layersMode="ACTIVE")
        elif event.shift and not event.ctrl and not event.alt:
            bpy.ops.uas_shot_manager.greasepencil_duplicatekeyframe(layersMode="ACTIVE")
        elif event.alt and not event.shift and not event.ctrl:
            bpy.ops.uas_shot_manager.greasepencil_deletekeyframe(layersMode="ACTIVE")

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_SetLayerAndMatAndVisib(Operator):
    bl_idname = "uas_shot_manager.greasepencil_setlayerandmatandvisib"
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

    materialName: StringProperty(
        name="Material Name",
        default="",
    )

    gpObjName: StringProperty(
        name="grease Pencil Object Name",
        default="",
    )

    @classmethod
    def description(self, context, properties):
        warningStrInd = properties.layerID.find("_WARNING")
        if -1 != warningStrInd:
            currentLayerID = properties.layerID[:warningStrInd]
        else:
            currentLayerID = properties.layerID
        descr = ""
        descr += " *** Layer not found ***\n" if -1 != warningStrInd else ""
        descr += f"Activate the layer of the mode {currentLayerID} and pick the associated material"
        descr += "\n+ Ctrl: Toggle layer visibility"
        descr += "\n+ Alt: Toggle between Solo and All layer visibility"
        return descr

    def invoke(self, context, event):
        # prefs = config.getAddonPrefs()
        props = config.getAddonProps(context.scene)
        # print(f"Layer and mat - ID: {self.layerID}, name:{self.gpObjName}")

        if not event.ctrl and not event.shift and not event.alt:
            utils_greasepencil.activateGpLayerAndMat(
                bpy.context.scene.objects[self.gpObjName], self.layerName, self.materialName
            )
        elif event.ctrl and not event.shift and not event.alt:
            utils_greasepencil.toggleLayerVisibility(bpy.context.scene.objects[self.gpObjName], self.layerName)
        # elif event.shift and not event.ctrl and not event.alt:
        #     bpy.ops.uas_shot_manager.greasepencil_duplicatekeyframe(layersMode="ACTIVE")
        elif event.alt and not event.shift and not event.ctrl:
            props.stb_frameTemplate.toggleSoloLayersVisibility(
                bpy.context.scene.objects[self.gpObjName], self.layerName
            )

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_SetKeyframe(Operator):
    bl_idname = "uas_shot_manager.greasepencil_setkeyframe"
    bl_label = ""
    bl_description = "Set active layer and current material"
    bl_options = {"INTERNAL", "UNDO"}

    "Mode:    Can be ADD, DUPLICATE, REMOVE"
    mode: StringProperty(
        name="Mode",
        default="ADD",
    )

    "layerID:    Can be CANVAS, BG_INK, BG_FILL"
    layerID: StringProperty(
        name="Layer ID",
        default="",
    )

    gpName: StringProperty(
        name="grease Pencil Object Name",
        default="",
    )

    layerName: StringProperty(
        name="Layer Name",
        default="ACTIVE",
    )

    @classmethod
    def description(self, context, properties):

        warningStrInd = properties.layerID.find("_WARNING")
        if -1 != warningStrInd:
            currentLayerID = properties.layerID[:warningStrInd]
        else:
            currentLayerID = properties.layerID

        descr = ""
        descr += " *** Layer not found ***\n" if -1 != warningStrInd else ""

        if "ADD" == properties.mode:
            descr += "Insert blank keyframe to the active layer"
            descr += "\n+ Shift: Insert on EVERY layer"
        elif "DUPLICATE" == properties.mode:
            descr += "Duplicate active keyframe at the current time onto the specified layer"
            descr += "\n+ Shift: Duplicate for EVERY layer"
        elif "REMOVE" == properties.mode:
            descr += "Delete active keyframe from the specified layer"
            descr += "\n+ Shift: Delete on EVERY layer"

        return descr

    def invoke(self, context, event):
        # prefs = config.getAddonPrefs()
        # props = config.getAddonProps(context.scene)
        # print(f"Layer and mat - ID: {self.layerID}, name:{self.gpObjName}")

        # if not event.ctrl and not event.shift and not event.alt:

        layerMode = None
        if not event.ctrl and not event.shift and not event.alt:
            layerMode = self.layerName
        # elif event.ctrl and not event.shift and not event.alt:
        #     bpy.ops.uas_shot_manager.greasepencil_newkeyframe(layersMode="ACTIVE")
        elif event.shift and not event.ctrl and not event.alt:
            layerMode = "ALL"
        # elif event.alt and not event.shift and not event.ctrl:
        #     bpy.ops.uas_shot_manager.greasepencil_deletekeyframe(layersMode="ACTIVE")

        if layerMode is not None:
            if "ADD" == self.mode:
                bpy.ops.uas_shot_manager.greasepencil_newkeyframe(layersMode=layerMode, gpName=self.gpName)
            elif "DUPLICATE" == self.mode:
                bpy.ops.uas_shot_manager.greasepencil_duplicatekeyframe(layersMode=layerMode, gpName=self.gpName)
            elif "REMOVE" == self.mode:
                bpy.ops.uas_shot_manager.greasepencil_deletekeyframe(layersMode=layerMode, gpName=self.gpName)

        return {"FINISHED"}


class UAS_ShotManager_LockAnimChannel(Operator):
    bl_idname = "uas_shot_manager.lock_anim_channel"
    bl_label = "Lock Channel"
    bl_description = "Set active layer and current material"
    bl_options = {"INTERNAL", "UNDO"}

    gpName: StringProperty(default="")

    # Can be LOCK_LOCATION_X... but also ALL
    lockItem: StringProperty(default="")
    lockValue: BoolProperty(default=True)

    def invoke(self, context, event):
        if "LOCK_LOCATION_X" == self.lockItem:
            context.scene.objects[self.gpName].lock_location[0] = self.lockValue
        elif "LOCK_LOCATION_Y" == self.lockItem:
            context.scene.objects[self.gpName].lock_location[1] = self.lockValue
        elif "LOCK_LOCATION_Z" == self.lockItem:
            # has to be locked !!!
            context.scene.objects[self.gpName].lock_location[2] = self.lockValue

        elif "LOCK_ROTATION_X" == self.lockItem:
            # has to be locked !!!
            context.scene.objects[self.gpName].lock_rotation[0] = self.lockValue
        elif "LOCK_ROTATION_Y" == self.lockItem:
            # has to be locked !!!
            context.scene.objects[self.gpName].lock_rotation[1] = self.lockValue
        elif "LOCK_ROTATION_Z" == self.lockItem:
            context.scene.objects[self.gpName].lock_rotation[2] = self.lockValue

        elif "LOCK_SCALE_X" == self.lockItem:
            context.scene.objects[self.gpName].lock_scale[0] = self.lockValue
        elif "LOCK_SCALE_Y" == self.lockItem:
            context.scene.objects[self.gpName].lock_scale[1] = self.lockValue
        elif "LOCK_SCALE_Z" == self.lockItem:
            context.scene.objects[self.gpName].lock_scale[2] = self.lockValue

        elif "ALL" == self.lockItem:
            context.scene.objects[self.gpName].lock_location[0] = self.lockValue
            context.scene.objects[self.gpName].lock_location[1] = self.lockValue
            context.scene.objects[self.gpName].lock_location[2] = True
            context.scene.objects[self.gpName].lock_rotation[0] = True
            context.scene.objects[self.gpName].lock_rotation[1] = True
            context.scene.objects[self.gpName].lock_rotation[2] = self.lockValue
            context.scene.objects[self.gpName].lock_scale[0] = self.lockValue
            context.scene.objects[self.gpName].lock_scale[1] = self.lockValue
            context.scene.objects[self.gpName].lock_scale[2] = self.lockValue

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_AddGreasePencil,
    UAS_ShotManager_OT_SelectShotGreasePencil,
    UAS_ShotManager_OT_SelectGreasePencilObject,
    UAS_ShotManager_OT_AddCanvasToGreasePencil,
    UAS_ShotManager_OT_ToggleGreasePencilDrawMode,
    #   UAS_ShotManager_OT_DrawOnGreasePencil,
    UAS_ShotManager_OT_UpdateGreasePencil,
    UAS_ShotManager_OT_RemoveGreasePencil,
    UAS_ShotManager_OT_ShowHideGreasePencil,
    UAS_ShotManager_OT_ShowHideCameras,
    UAS_ShotManager_OT_ClearLayer,
    UAS_ShotManager_OT_PinGreasePencilObject,
    UAS_ShotManager_GreasePencilSelectAndDraw,
    UAS_ShotManager_DetachStoryboardFrame,
    UAS_ShotManager_ResetUsagePreset,
    UAS_ShotManager_GreasePencil_UINavigationKeys,
    UAS_ShotManager_GreasePencil_NavigateInKeyFrames,
    # UAS_ShotManager_GreasePencil_NavigateInShots,
    UAS_ShotManager_GreasePencil_NewKeyFrame,
    UAS_ShotManager_GreasePencil_DuplicateKeyFrame,
    UAS_ShotManager_GreasePencil_DeleteKeyFrame,
    UAS_ShotManager_GreasePencil_SetLayerAndMat,
    UAS_ShotManager_GreasePencil_SetLayerAndMatAndVisib,
    UAS_ShotManager_GreasePencil_SetKeyframe,
    #   UAS_ShotManager_OT_ChangeGreasePencilOpacity,
    UAS_ShotManager_LockAnimChannel,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
