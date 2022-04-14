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

from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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
    bl_label = "Select Storyboard Frame"
    bl_description = "Select the storyboard frame of the current shot"
    bl_options = {"INTERNAL", "UNDO"}

    index: bpy.props.IntProperty(default=-1)

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
        props = scene.UAS_shot_manager_props

        # select SELECTED shot
        # if event.shift and not event.ctrl and not event.alt:
        if context.active_object is not None and context.active_object.mode != "OBJECT":
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
                    bpy.ops.object.select_all(action="DESELECT")
                    bpy.context.view_layer.objects.active = gp_child
                    gp_child.select_set(True)

        utils.setPropertyPanelContext(bpy.context, "DATA")

        # # select CURRENT shot
        # elif not event.ctrl and not event.shift and not event.alt:

        return {"FINISHED"}


class UAS_ShotManager_OT_SelectGreasePencilObject(Operator):
    bl_idname = "uas_shot_manager.select_grease_pencil_object"
    bl_label = "Select the grease pencil object being drawn"
    # bl_description = "Select Grease Pencil object"
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

        utils_greasepencil.add_grease_pencil_canvas_layer(gpObj, "GP_Canvas", order="BOTTOM")

        return {"FINISHED"}


class UAS_ShotManager_OT_ToggleGreasePencilDrawMode(Operator):
    bl_idname = "uas_shot_manager.toggle_grease_pencil_draw_mode"
    bl_label = ""
    bl_description = "Toggle Grease Pencil Draw Mode"
    bl_options = {"INTERNAL", "UNDO"}

    gpObjectName: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props

        # NOTE: we use context.object here instead of context.active_object because
        # when the eye icon of the object is closed (meaning object.hide_get() == True)
        # then context.active_object is None
        if context.object is not None:
            if "OBJECT" != context.object.mode:
                # if context.active_object.mode == "PAINT_GPENCIL":
                # bpy.ops.object.mode_set(mode="OBJECT")
                utils_greasepencil.switchToObjectMode()
            else:
                # bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
                if self.gpObjectName in context.scene.objects:
                    gpencil = context.scene.objects[self.gpObjectName]
                else:
                    gpencil = context.object

                utils_greasepencil.switchToDrawMode(context, gpencil)
                if props.shotsGlobalSettings.stb_camPOV_forFreeGP:
                    props.getCurrentShot().setCameraToViewport()
                    scene.tool_settings.gpencil_stroke_placement_view3d = (
                        props.shotsGlobalSettings.stb_strokePlacement_forFreeGP
                    )
                    scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"

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

            utils_greasepencil.switchToDrawMode(context, gp_child)
            # gp_child.select_set(True)
            # gp_child.hide_select = False
            # gp_child.hide_viewport = False
            # gp_child.hide_render = False
            # bpy.ops.gpencil.paintmode_toggle()

            # context.scene.tool_settings.gpencil_stroke_placement_view3d = "ORIGIN"
            # context.scene.tool_settings.gpencil_sculpt.lock_axis = "VIEW"

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


class UAS_ShotManager_OT_ClearLayer(Operator):
    bl_idname = "uas_shot_manager.clear_layer"
    bl_label = "Clear Layer"
    bl_description = "Delete all the strokes of the active key frame of the current layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        # props = scene.UAS_shot_manager_props

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
                    layerFrameInd = utils_greasepencil.getLayerKeyFrameIndexAtFrame(gp, scene.frame_current, "ACTIVE")
                    if -1 == layerFrameInd:
                        layerFrameTime = utils_greasepencil.getLayerPreviousFrame(gp, scene.frame_current, "ACTIVE")
                        layerFrameInd = utils_greasepencil.getLayerKeyFrameIndexAtFrame(gp, layerFrameTime, "ACTIVE")
                    if -1 != layerFrameInd:
                        gpl.frames[layerFrameInd].clear()

                        # required for refresh
                        gpl.hide = not gpl.hide
                        gpl.hide = not gpl.hide

        return {"FINISHED"}


class UAS_ShotManager_OT_PinGreasePencilObject(Operator):
    bl_idname = "uas_shot_manager.pin_grease_pencil_object"
    bl_label = "Pin the grease pencil object being drawn"
    # bl_description = "Select Grease Pencil object"
    bl_options = {"INTERNAL", "UNDO"}

    pin: BoolProperty(default=False)
    pinnedObjName: StringProperty(default="")

    def execute(self, context):
        props = context.scene.UAS_shot_manager_props

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


class UAS_ShotManager_GreasePencilItem(Operator):
    bl_idname = "uas_shot_manager.greasepencilitem"
    bl_label = " "
    bl_description = (
        "+ Shift: Select the storyboard frame and add it to the current selection"
        "\n+ Alt: Select the storyboard frame and switch to Draw mode"
    )
    bl_options = {"INTERNAL", "UNDO"}

    index: IntProperty(default=0)

    action: StringProperty(default="DO_NOTHING")

    def invoke(self, context, event):
        self.action = "DO_NOTHING"

        if not event.ctrl and not event.shift and not event.alt:
            self.action = "SELECT"
        elif not event.ctrl and event.shift and not event.alt:
            self.action = "ADD_TO_SELECTION"
        if not event.ctrl and not event.shift and event.alt:
            self.action = "SELECT_AND_DRAW"

        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.UAS_shot_manager_props
        props.setSelectedShotByIndex(self.index)
        shot = props.getShotByIndex(self.index)
        gp_child = shot.getGreasePencilObject()

        # try:
        #     bpy.ops.object.select_all(action="DESELECT")
        # except Exception:
        #     pass

        if gp_child is None and "SELECT_AND_DRAW" == self.action:

            if shot.camera is None or shot.camera.name not in scene.objects or scene.objects[shot.camera.name] is None:
                print("Camera is invalid for grease pencil parenting - Cancelling...")
                return {"CANCELLED"}

            utils_greasepencil.create_new_greasepencil(
                shot.camera.name + "_GP", parentCamera=shot.camera, location=[0, 0, 0]
            )
            gp_child = shot.getGreasePencilObject()

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
                if utils_greasepencil.isAnotherObjectInSubMode(gp_child):
                    utils_greasepencil.switchToObjectMode()

                utils.select_object(gp_child)

                # quit draw mode
                if "OBJECT" != gp_child.mode:
                    utils_greasepencil.switchToObjectMode()

                # enter draw mode
                else:
                    props.setCurrentShotByIndex(self.index)
                    shot.updateGreasePencils()
                    # set ink layer, else topmost layer
                    setInkLayerReadyToDraw(gp_child)
                    utils_greasepencil.switchToDrawMode(context, gp_child)

        utils.setPropertyPanelContext(context, "DATA")

        return {"FINISHED"}


class UAS_ShotManager_GreasePencil_PreviousKey(Operator):
    bl_idname = "uas_shot_manager.greasepencil_previouskey"
    bl_label = ""
    bl_description = (
        "Jump to the previous key frame of the specified layer"
        "\n+ Ctrl: Jump to the start of the current shot, then to"
        "\nthe start of the previous shot"
    )
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
    bl_label = ""
    bl_description = (
        "Jump to the next key frame of the specified layer" "\n+ Ctrl: Jump to the start of the current shot"
    )
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

    layersMode: StringProperty(
        name="Layers Mode",
        default="",
    )

    def execute(self, context):
        gp = context.active_object
        if "" == self.layersMode:
            if gp is not None:
                props = context.scene.UAS_shot_manager_props
                if "" == props.greasePencil_layersMode:
                    if len(gp.data.layers):
                        props.greasePencil_layersMode = "ACTIVE"
                    else:
                        props.greasePencil_layersMode = "NOLAYER"
                    self.layersMode = props.greasePencil_layersMode
        _logger.debug_ext(
            f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
        )
        utils_greasepencil.addKeyFrameToLayer(gp, context.scene.frame_current, self.layersMode)

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

    def execute(self, context):
        gp = context.active_object
        if "" == self.layersMode:
            if gp is not None:
                props = context.scene.UAS_shot_manager_props
                if "" == props.greasePencil_layersMode:
                    if len(gp.data.layers):
                        props.greasePencil_layersMode = "ACTIVE"
                    else:
                        props.greasePencil_layersMode = "NOLAYER"
                self.layersMode = props.greasePencil_layersMode
        _logger.debug_ext(
            f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
        )
        utils_greasepencil.duplicateLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)

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

    def execute(self, context):
        gp = context.active_object
        if "" == self.layersMode:
            if gp is not None:
                props = context.scene.UAS_shot_manager_props
                if "" == props.greasePencil_layersMode:
                    if len(gp.data.layers):
                        props.greasePencil_layersMode = "ACTIVE"
                    else:
                        props.greasePencil_layersMode = "NOLAYER"
                    self.layersMode = props.greasePencil_layersMode
        _logger.debug_ext(
            f"On a frame for mode {self.layersMode}: {utils_greasepencil.isCurrentFrameOnLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)}"
        )
        utils_greasepencil.deleteLayerKeyFrame(gp, context.scene.frame_current, self.layersMode)

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

        descr += (
            "\n+ Ctrl: Add key frame"
            # "\n+ Ctrl + Shift: Invert shots state"
            "\n+ Shift: Duplicate previous key frame"
            "\n+ Alt: Delete key frame"
        )

        return descr

    def invoke(self, context, event):
        # prefs = context.preferences.addons["shotmanager"].preferences
        # props = context.scene.UAS_shot_manager_props
        # print(f"Layer and mat - ID: {self.layerID}, name:{self.gpObjName}")

        # if not event.ctrl and not event.shift and not event.alt:
        utils_greasepencil.activeGpLayerAndMat(bpy.context.scene.objects[self.gpObjName], self.layerName)
        if event.ctrl and not event.shift and not event.alt:
            bpy.ops.uas_shot_manager.greasepencil_newkeyframe(layersMode="ACTIVE")
        elif event.shift and not event.ctrl and not event.alt:
            bpy.ops.uas_shot_manager.greasepencil_duplicatekeyframe(layersMode="ACTIVE")
        elif event.alt and not event.shift and not event.ctrl:
            bpy.ops.uas_shot_manager.greasepencil_deletekeyframe(layersMode="ACTIVE")

        return {"FINISHED"}


_classes = (
    UAS_ShotManager_OT_AddGreasePencil,
    UAS_ShotManager_OT_SelectGreasePencil,
    UAS_ShotManager_OT_AddCanvasToGreasePencil,
    UAS_ShotManager_OT_DrawOnGreasePencil,
    UAS_ShotManager_OT_RemoveGreasePencil,
    UAS_ShotManager_OT_EnableDisableGreasePencil,
    UAS_ShotManager_OT_ClearLayer,
    UAS_ShotManager_OT_PinGreasePencilObject,
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
