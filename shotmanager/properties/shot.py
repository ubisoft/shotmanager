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
Definition of a shot
"""

import bpy

from bpy.types import Scene

# from bpy.types import SoundSequence
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,
    FloatVectorProperty,
    CollectionProperty,
)

from shotmanager.features.greasepencil.greasepencil_props import GreasePencilProperties

from shotmanager.features.greasepencil import greasepencil as gp
from shotmanager.utils import utils
from shotmanager.utils import utils_greasepencil
from .montage_interface import ShotInterface

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


def list_shot_types(self, context):
    # res = list()
    # res.append(("NEW_CAMERA", "Create New Camera", "Create new camera", 0))
    # for i, cam in enumerate([c for c in context.scene.objects if c.type == "CAMERA"]):
    #     res.append(
    #         (cam.name, cam.name, 'Use the exising scene camera named "' + cam.name + '"\nfor the new shot', i + 1)
    #     )
    # icon_previz = config.icons_col["ShotManager_CamGPShot_32"]
    icon_previz = config.icons_col["ShotManager_32"]
    # icon_stb = config.icons_col["ShotManager_CamGPStb_32"]  # no, that's the small stb frame icon
    icon_stb = config.icons_col["ShotMan_EnabledStb"]
    res = (
        ("PREVIZ", "Camera Shot", "Shot based on the record of a camera", icon_previz.icon_id, 0),
        ("STORYBOARD", "Storyboard Shot", "2D drawing used for storyboarding", icon_stb.icon_id, 1),
    )

    return res


class UAS_ShotManager_Shot(ShotInterface, PropertyGroup):
    # def _get_parentScene(self):
    #     val = self.get("parentScene", None)
    #     if val is None:
    #         matches = [
    #             s for s in bpy.data.scenes if "UAS_shot_manager_props" in s and self == s["UAS_shot_manager_props"]
    #         ]
    #         self["parentScene"] = matches[0] if len(matches) > 0 else None
    #     return self["parentScene"]

    # def _set_parentScene(self, value):
    #     self["parentScene"] = value

    # parentScene: PointerProperty(type=Scene, get=_get_parentScene, set=_set_parentScene)
    parentScene: PointerProperty(type=Scene)

    # parentTakeIndex: IntProperty(name="Parent Take Index", default=-1)

    def getParentTakeIndex(self):
        props = config.getAddonProps(self.parentScene)
        return props.getShotParentTakeIndex(self)

    def getParentTake(self):
        props = config.getAddonProps(self.parentScene)
        return props.getShotParentTake(self)

    # for backward compatibility - before V1.2.21
    # used by data version patches.
    # For general purpose use the property self.parentScene
    def getParentScene(self):
        if self.parentScene is not None:
            return self.parentScene

        for scene in bpy.data.scenes:
            if "UAS_shot_manager_props" in scene:
                props = config.getAddonProps(scene)
                for take in props.takes:
                    #    print("Take name: ", take.name)
                    for shot in take.shots:
                        #        print("  Shot name: ", shot.name)
                        if shot.name == self.name:
                            self.parentScene = scene
                            return scene
        return None

    # gpStoryboard: PointerProperty(type=GreasePencilStoryboard)

    tooltip: StringProperty(default="or change the name in the Properties panel below")

    def getOutputMediaPath(
        self,
        outputMedia,
        rootPath=None,
        insertSeqPrefix=False,
        providePath=True,
        provideName=True,
        provideExtension=True,
        specificFrame=None,
        genericFrame=False,
    ):
        props = config.getAddonProps(self.parentScene)
        return props.getOutputMediaPath(
            outputMedia,
            self,
            rootPath=rootPath,
            insertSeqPrefix=insertSeqPrefix,
            providePath=providePath,
            provideName=provideName,
            provideExtension=provideExtension,
            specificFrame=specificFrame,
            genericFrame=genericFrame,
        )

    def getName_PathCompliant(self, withPrefix=False):
        props = config.getAddonProps(self.parentScene)
        shotName = self.name.replace(" ", "_")
        if withPrefix:
            # shotName = f"{props.getRenderShotPrefix()}{shotName}"
            shotName = f"{props.getSequenceName('FULL', addSeparator=True)}{shotName}"
        return shotName

    def _get_name(self):
        val = self.get("name", "-")
        return val

    def _set_name(self, value):
        """Set a unique name to the shot"""
        props = config.getAddonProps(self.parentScene)
        shots = props.getShotsList(takeIndex=self.getParentTakeIndex())
        newName = utils.findFirstUniqueName(self, value, shots)
        self["name"] = newName

    name: StringProperty(name="Name", get=_get_name, set=_set_name)

    def _update_enabled(self, context):
        self.selectShotInUI()

    enabled: BoolProperty(
        name="Enable / Disable Shots",
        description="Use - or not - the shot in the edit",
        update=_update_enabled,
        default=True,
        options=set(),
    )

    def selectShotInUI(self):
        props = config.getAddonProps(self.parentScene)
        currentTakeInd = props.getCurrentTakeIndex()
        if currentTakeInd == self.getParentTakeIndex():
            props.setSelectedShot(self)

    shotType: EnumProperty(
        name="Type",
        description="Usage of the shot",
        items=list_shot_types,
        default=0,
    )

    #############
    # start #####
    #############

    def _get_start(self):
        val = self.get("start", 25)
        return val

    # *** behavior here must match the one of start and end of shot preferences ***
    def _set_start(self, value):
        duration = self.getDuration()
        self["start"] = value
        if self.durationLocked:
            self["end"] = self.start + duration - 1
        else:
            # increase end value if start is superior to end
            # if self.start > self.end:
            #     self["end"] = self.start

            # prevent start to go above end (more user error proof)
            if self.start > self.end:
                self["start"] = self.end

    def _update_start(self, context):
        self.selectShotInUI()
        self.updateClipLinkToShotStart()
        config.gRedrawShotStack = True

    start: IntProperty(
        name="Shot Start",
        description="Value of the first included frame of the shot.\nNote that start frame cannot exceed end frame",
        get=_get_start,
        set=_set_start,
        update=_update_start,
    )

    #############
    # end #####
    #############

    def _get_end(self):
        val = self.get("end", 30)
        return val

    # *** behavior here must match the one of start and end of shot preferences ***
    def _set_end(self, value):
        duration = self.getDuration()
        self["end"] = value
        if self.durationLocked:
            self["start"] = self.end - duration + 1
        else:
            # reduce start value if end is lowr than start
            # if self.start > self.end:
            #    self["start"] = self.end

            # prevent end to go below start (more user error proof)
            if self.start > self.end:
                self["end"] = self.start

    def _update_end(self, context):
        self.selectShotInUI()
        config.gRedrawShotStack = True

    end: IntProperty(
        name="Shot End",
        description="Value of the last included frame of the shot.\nNote that end frame cannot be lower than start frame",
        get=_get_end,
        set=_set_end,
        update=_update_end,
    )

    #############
    # duration #####
    #############

    def getDuration(self):
        """Returns the shot duration in frames
        In Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
        """
        duration = self.end - self.start + 1
        return duration

    def setDuration(self, duration, bypassLock=False):
        """Set the shot duration in frames
        In Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
        """
        newDuration = max(duration, 1)
        if not self.durationLocked:
            self.end = self.start + newDuration - 1
        elif bypassLock:
            self.durationLocked = False
            self.end = self.start + newDuration - 1
            self.durationLocked = True

    def _get_duration_fp(self):
        #   print("\n*** _get_duration_fp: New state: ", self.duration_fp)

        # not used, normal it's the fake property
        self.get("duration_fp", -1)

        realVal = self.getDuration()
        return realVal

    def _set_duration_fp(self, value):
        # print("\n*** _update_duration_fp: New state: ", self.duration_fp)
        if not self.durationLocked:
            self["duration_fp"] = value
            self.end = self.start + max(value, 1) - 1

    def _update_duration_fp(self, context):
        #  print("\n*** _update_duration_fp: New state: ", self.duration_fp)
        pass

    # fake property: value never used in itself, its purpose is to update ofher properties
    duration_fp: IntProperty(
        name="Shot Duration",
        description="Duration is a frame number given by end - start + 1.\nIf set in the Shots Settings panel, the duration is displayed in red\nwhen the current time is in the shot range",
        min=1,
        get=_get_duration_fp,
        set=_set_duration_fp,
        update=_update_duration_fp,
        options=set(),
    )

    def _update_durationLocked(self, context):
        self.selectShotInUI()

    durationLocked: BoolProperty(
        name="Lock Duration",
        description="Lock - or not - the shot duration.\nWhen locked, changing one boundary will also affect the other",
        default=False,
        update=_update_durationLocked,
        options=set(),
    )

    ##############
    # camera
    ##############

    def _filter_cameras(self, object):
        """Return true only for cameras from the same scene as the shot"""
        # print("self", str(self))  # this shot
        # print("object", str(object))  # all the objects of the property type

        if object.type == "CAMERA" and object.name in self.parentScene.objects:
            return True
        else:
            return False

    camera: PointerProperty(
        name="Camera",
        description="Select a Camera",
        type=bpy.types.Object,
        # poll=lambda self, obj: True if obj.type == "CAMERA" else False,
        poll=_filter_cameras,
    )

    def setCamera(self, newCamera):
        """Set the camera of the shot and update the shot so that if the camera has children and the shot has greasepencil they match again"""
        self.camera = newCamera
        # wkipwkipwkipwkip to finish

    def isCameraValid(self):
        """Sometimes a pointed camera can seem to work but the camera object doesn't exist anymore in the scene.
        Return True if the camera is really there, False otherwise
        Note: This doesn't change the camera attribute of the shot
        """
        cameraIsValid = self.camera is not None
        if self.camera is not None:
            try:
                if bpy.context.scene.objects[self.camera.name] is None:
                    self.camera = None
            except Exception:
                # item.camera = None     # not working, often invalid context to write in
                cameraIsValid = False
            # _logger.error(f"Error: Shot {self.name} uses a camera {self.camera.name} not found in the scene")

        return cameraIsValid

    def makeCameraUnique(self):
        if self.camera is not None:
            props = config.getAddonProps(self.parentScene)
            if 1 < props.getNumSharedCamera(self.camera):
                # self.camera = utils.duplicateObject(self.camera, newName="Cam_" + self.name)
                # wkip to do for each gp props
                gpProps = self.getGreasePencilProps("STORYBOARD")
                duplicateHierarchy = gpProps is not None
                props.copyCameraFromShot(self, targetShot=self, duplicateHierarchy=duplicateHierarchy)
        return self.camera

    def setCameraToViewport(self):
        if self.isCameraValid() and bpy.context.screen is not None:
            props = config.getAddonProps(self.parentScene)
            target_area_index = props.getTargetViewportIndex(bpy.context, only_valid=False)
            target_area = utils.getAreaFromIndex(bpy.context, target_area_index, "VIEW_3D")
            self.parentScene.camera = self.camera
            utils.setCurrentCameraToViewport2(bpy.context, target_area)

    ##############
    # color
    ##############

    def _get_color(self):
        defaultVal = [1.0, 1.0, 1.0, 1.0]
        print
        try:
            props = config.getAddonProps(self.parentScene)
        except Exception:
            print(f"_get_color: self: {self}, self.parentScene:{self.parentScene}")
            if self.parentScene is None:
                self.parentScene = self.getParentScene()
        props = config.getAddonProps(self.parentScene)

        if props.use_camera_color:
            if self.camera is not None:
                defaultVal[0] = self.camera.color[0]
                defaultVal[1] = self.camera.color[1]
                defaultVal[2] = self.camera.color[2]

        val = self.get("color", defaultVal)

        if props.use_camera_color:
            if self.camera is not None:
                val[0] = self.camera.color[0]
                val[1] = self.camera.color[1]
                val[2] = self.camera.color[2]
            else:
                val = [0.0, 0.0, 0.0, 1.0]

        return val

    def _set_color(self, value):
        self["color"] = value
        props = config.getAddonProps(self.parentScene)
        if props.use_camera_color and self.camera is not None:
            self.camera.color[0] = self["color"][0]
            self.camera.color[1] = self["color"][1]
            self.camera.color[2] = self["color"][2]
            self.camera.color[3] = self["color"][3]

    def _update_color(self, context):
        self.selectShotInUI()

    color: FloatVectorProperty(
        name="Set the Camera (or Shot) Color",
        description="Color of the camera used by the shot or, according to\nthe settings, color of the shot",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        get=_get_color,
        set=_set_color,
        update=_update_color,
        options=set(),
    )

    def getEditStart(self, referenceLevel="TAKE"):
        """
        referenceLevel can be "TAKE" or "GLOBAL_EDIT"
        """
        props = config.getAddonProps(self.parentScene)
        return props.getEditTime(self, self.start, referenceLevel=referenceLevel)

    def getEditEnd(self, referenceLevel="TAKE"):
        """
        referenceLevel can be "TAKE" or "GLOBAL_EDIT"
        """
        props = config.getAddonProps(self.parentScene)
        return props.getEditTime(self, self.end, referenceLevel=referenceLevel)

    ##############
    # background images
    ##############

    def hasBGImage(self):
        return self.camera is not None and len(self.camera.data.background_images)

    def updateClipLinkToShotStart(self):
        if self.camera is not None and len(self.camera.data.background_images):
            bgClip = self.camera.data.background_images[0].clip
            bgClip.use_proxy_custom_directory = True

            bgSoundSequence = self.getSoundSequence()

            if self.bgImages_linkToShotStart:
                if bgClip is not None:
                    bgClip.frame_start = self.start + self.bgImages_offset
                if bgSoundSequence is not None:
                    bgSoundSequence.frame_start = self.start + self.bgImages_offset
            else:
                if bgClip is not None:
                    bgClip.frame_start = self.bgImages_offset
                if bgSoundSequence is not None:
                    bgSoundSequence.frame_start = self.bgImages_offset

    def _get_bgImages_linkToShotStart(self):
        val = self.get("bgImages_linkToShotStart", True)
        return val

    def _set_bgImages_linkToShotStart(self, value):
        self["bgImages_linkToShotStart"] = value
        self.updateClipLinkToShotStart()

    # def _update_bgImages_linkToShotStart(self, context):
    #     if self.camera is not None and len(self.camera.data.background_images):
    #         bgClip = self.camera.data.background_images[0].clip
    #         if bgClip is not None:
    #             if self._update_bgImages_linkToShotStart:
    #                 bgClip.frame_start = self.start + self.bgImages_offset
    #             else:
    #                 bgClip.frame_start = self.bgImages_offset

    bgImages_linkToShotStart: BoolProperty(
        name="Link BG to Start",
        description="Link the background image clip to the shot start.\n"
        "If linked the background clip start frame is relative to the shot start.\n"
        "If not linked the clip starts at frame 0 + offset",
        default=True,
        get=_get_bgImages_linkToShotStart,
        set=_set_bgImages_linkToShotStart,
        # update=_update_bgImages_linkToShotStart,
        options=set(),
    )

    def _get_bgImages_offset(self):
        val = self.get("bgImages_offset", 0)
        return val

    def _set_bgImages_offset(self, value):
        self["bgImages_offset"] = value
        self.updateClipLinkToShotStart()
        # if self.camera is not None and len(self.camera.data.background_images):
        #     bgClip = self.camera.data.background_images[0].clip
        #     if bgClip is not None:
        #         if self.bgImages_linkToShotStart:
        #             bgClip.frame_start = self.start + self.bgImages_offset
        #         else:
        #             bgClip.frame_start = self.bgImages_offset

    bgImages_offset: IntProperty(
        name="BG Clip Offset",
        description="Time offset for the clip used as background for the camera",
        soft_min=-20,
        soft_max=20,
        get=_get_bgImages_offset,
        set=_set_bgImages_offset,
        default=0,
    )

    def addBGImages(self, mediaFile, frame_start=0, alpha=1.0, addSoundFromVideo=False):
        props = config.getAddonProps(self.parentScene)
        if self.camera is not None:
            if len(self.camera.data.background_images):
                self.removeBGImages()
            print("addBGImages 01")
            videoAdded = utils.add_background_video_to_cam(self.camera.data, str(mediaFile), frame_start, alpha=alpha)
            if not videoAdded:
                utils.ShowMessageBox(
                    message=f"The following video cannot be imported:\n   {mediaFile}",
                    title="Video Not Found",
                    icon="ERROR",
                )
            print(f"addBGImages 02 {self.camera.data.background_images[0].clip.name}")

        if addSoundFromVideo:
            soundClip = props.addBGSoundToShot(mediaFile, self)
            if soundClip is not None:
                soundClip.frame_start = frame_start

    def removeBGImages(self):
        props = config.getAddonProps(self.parentScene)
        if self.camera is not None and len(self.camera.data.background_images):
            # if shot.camera.data.background_images[0].clip is not None:
            self.camera.data.show_background_images = False
            # shot.camera.data.background_images[0].clip = None
            self.camera.data.background_images.clear()
            # shot.camera.data.background_images[0].clip.filepath = ""

        props.removeBGSoundFromShot(self)
        # if "" != self.bgSoundClipName:
        #     soundSeq = self.getSoundSequence()
        #     if soundSeq is not None:
        #         self.parentScene.sequence_editor.sequences.remove(soundSeq)
        #     self.bgSoundClipName = ""

    ##############
    # background sounds
    ##############

    bgImages_sound_trackIndex: IntProperty(name="Sound Track Index", min=-1, max=32, default=-1)
    # bgSoundClip: PointerProperty(type=SoundSequence)
    bgSoundClipName: StringProperty(default="")

    def enableBGSound(self, useBgSound):
        # if self.bgSoundClip is not None:
        #     self.bgSoundClip.mute = not useBgSound
        if "" != self.bgSoundClipName:
            soundClip = self.parentScene.sequence_editor.sequences[self.bgSoundClipName]
            if soundClip is not None:
                soundClip.mute = not useBgSound

    def isSoundSequenceValid(self):
        """Return true if there is no sound sequence -ie self.bgSoundClipName is "") or if a sequence with this name
        is found in the VSE, false otherwise
        """
        if "" == self.bgSoundClipName or self.bgSoundClipName in self.parentScene.sequence_editor.sequences:
            return True
        return False

    def getSoundSequence(self):
        soundClip = None
        if "" != self.bgSoundClipName and self.bgSoundClipName in self.parentScene.sequence_editor.sequences_all:
            soundClip = self.parentScene.sequence_editor.sequences_all[self.bgSoundClipName]
        if soundClip is not None:
            print(f"Sounclip: {soundClip.name}")

        return soundClip

    #############
    # grease pencil
    #############

    greasePencils: CollectionProperty(
        name="Properties of Grease Pencil Children",
        description="Set of Grease Pencil Properties",
        type=GreasePencilProperties,
    )

    def addGreasePencil(self, mode="STORYBOARD"):
        """Create a Grease Pencil object parented to the camera of the shot.
        Return a tupple with the grease pencil properties and the created object.
        """
        props = config.getAddonProps(self.parentScene)
        gpProps = self.getGreasePencilProps(mode)

        if gpProps is None:
            gpProps = self.greasePencils.add()
            gpProps.initialize(self, mode)

        gpObj = self.getGreasePencilObject(mode)

        if gpObj is None:
            framePreset = props.stb_frameTemplate

            gpName = self.camera.name + "_GP"

            if "STORYBOARD" == mode:
                gpObj = gp.createStoryboarFrameGP(gpName, framePreset, parentCamera=self.camera, location=[0, 0, -0.5])

                # No !!!
                # self.shotType = "STORYBOARD"

                gpProps.updateGreasePencil()

        return (gpProps, gpObj)

    def getGreasePencilProps(self, mode="STORYBOARD"):
        """Return the GreasePencilProperties instance of the specified mode, None otherwise
        Args:
            mode: "STORYBOARD"
        """
        # TODO: differenciate the modes of grease pencils to provide the right one
        #     if self.isCameraValid():
        # gp_child = utils_greasepencil.get_greasepencil_child(self.camera)
        # if gp_child is not None:
        #     gpProps = self.getGreasePencilProps(mode="STORYBOARD")

        gpProps = self.greasePencils[0] if len(self.greasePencils) else None
        return gpProps

    def removeGreasePencil(self, mode="STORYBOARD"):
        """Remove the Grease Pencil properties and the object parented to the camera of the shot."""
        if self.isCameraValid():
            gp_child = utils_greasepencil.get_greasepencil_child(self.camera, childType="GPENCIL")
            if gp_child is not None:
                bpy.data.objects.remove(gp_child, do_unlink=True)
            gp_child = utils_greasepencil.get_greasepencil_child(self.camera, childType="EMPTY")
            if gp_child is not None:
                bpy.data.objects.remove(gp_child, do_unlink=True)
        if len(self.greasePencils):
            self.greasePencils.remove(0)

    def hasGreasePencil(self):
        if self.isCameraValid():
            gp_child = utils_greasepencil.get_greasepencil_child(self.camera)
            return gp_child is not None
        else:
            return False

    # wkip to update with the gp list
    def getGreasePencilObject(self, mode="STORYBOARD"):
        """Set the grease pencil object of the specified mode associated to the camera.
        Return the created - or corresponding if one existed - grease pencil object, or None if the camera was invalid
        Args:
            mode: can be "STORYBOARD"
        """
        # TOFIX: At the moment there is only one child (or child hierarchy rather, since there is the empty and then the
        # grease pencil) for the camera, which is the storyboard frame. This may change in a future version to have other
        # grease pencil modes
        gp_child = None
        if self.isCameraValid():
            gp_child = utils_greasepencil.get_greasepencil_child(self.camera)
        return gp_child

    def updateGreasePencils(self):
        for gpProps in self.greasePencils:
            gpProps.updateGreasePencil()

    # wkip to update with the gp list
    def showGreasePencil(self, forceHide=False):
        """Display or hide the grease pencil object according to its visibility state
        and to the display state at the props level (props.use_greasepencil)
        Args:
            forceHide:  used by the renderer to avoid to see the gp of the other shots
        Called by props.updateStoryboardFramesDisplay()
        """
        #    def showGreasePencil(self, visible=None, mode="STORYBOARD"):
        def _showGreasePencil(gpencil, visible):
            gpencil.hide_viewport = not visible
            gpencil.hide_render = not visible

        if not self.isCameraValid():
            return

        gp_child = utils_greasepencil.get_greasepencil_child(self.camera)
        if gp_child is not None:
            gpProps = self.getGreasePencilProps(mode="STORYBOARD")

            if gpProps is None:
                return

            props = config.getAddonProps(self.parentScene)

            if forceHide:
                _showGreasePencil(gp_child, False)
                return

            if "ALWAYS_VISIBLE" == gpProps.visibility:
                _showGreasePencil(gp_child, props.use_greasepencil)
            elif "ALWAYS_HIDDEN" == gpProps.visibility:
                _showGreasePencil(gp_child, False)
            # AUTO
            else:
                if props.use_greasepencil:
                    currentTakeInd = props.getCurrentTakeIndex()
                    if self.getParentTakeIndex() == currentTakeInd:
                        if "STORYBOARD" == self.shotType:
                            _showGreasePencil(gp_child, True)

                        # PREVIZ
                        else:
                            if props.getCurrentShot() == self:
                                _showGreasePencil(gp_child, True)
                            else:
                                _showGreasePencil(gp_child, False)

                    # hide stb frames that are not belonging to shots from the current take
                    else:
                        _showGreasePencil(gp_child, False)
                else:
                    _showGreasePencil(gp_child, False)

    def detachGreasePencil(self):
        def _ClearParent(child):
            # Save the transform matrix before de-parenting
            matrixcopy = child.matrix_world.copy()
            # Clear the parent
            child.parent = None
            # Restore childs location / rotation / scale
            child.matrix_world = matrixcopy

        gp_child = utils_greasepencil.get_greasepencil_child(self.camera)
        if gp_child is not None:
            # unparent: bpy.ops.object.parent_clear(type='CLEAR')
            _ClearParent(gp_child)

            utils.lockTransforms(gp_child, lock=False)
            utils.clearTransformAnimation(gp_child)

            if 0 == gp_child.name.find("Cam_"):
                gp_child.name = gp_child.name[4:] + "_Free"

            self.shotType = "PREVIZ"

    #############
    # storyboard
    #############

    def addStoryboardFrame(self):
        """Add a grase pencil object to the shot as well as a Storyboard frame preset
        The type of the shot is NOT changed.
        Return a tupple with the grease pencil properties and the created object."""

        # the mode used here is to specify the kind of grease pencil object to create
        # it is not related to the shot type since any shot type can have a storyboard frame
        return self.addGreasePencil(mode="STORYBOARD")

    def isStoryboardType(self):
        return "S" == self.shotType[0]

    # TODO: wkip to update with the gp list
    def getStoryboardFrame(self):
        """Set the grease pencil object of the specified mode associated to the camera.
        Return the created - or corresponding if one existed - grease pencil object, or None if the camera was invalid
        Args:
            mode: can be "STORYBOARD"
        """
        return self.getGreasePencilObject(mode="STORYBOARD")

    def hasStoryboardFrame(self):
        return self.getGreasePencilObject("STORYBOARD") is not None

    # TODO: wkip check that the empty is the one of the storyboard frame
    def getStoryboardEmptyChild(self):
        """Return the Empty object used as the parent of the storyboard frame
        Note: This doesn't depend on the shot type since camera shots can also have a storyboard frame"""
        emptyChild = None
        if self.isCameraValid():
            emptyChild = utils_greasepencil.get_greasepencil_child(self.camera, childType="EMPTY")
        return emptyChild

    # wkip to update with the gp list
    def getStoryboardChildren(self):
        """If the shot has a valid camera: return the list of all the children of the camera associated
        to the Storyboard Frame. The camera is NOT included, but the empty object is.
        Return None otherwise
        Note: This doesn't depend on the shot type since camera shots can also have a storyboard frame"""
        stbChildren = None
        # if self.isStoryboardType():
        emptyChild = self.getStoryboardEmptyChild()
        if emptyChild is not None:
            stbChildren = utils.getChildrenHierarchy(emptyChild)
        return stbChildren

    #############
    # notes #####
    #############

    note01: StringProperty(name="Note 1", description="")
    note02: StringProperty(name="Note 2", description="")
    note03: StringProperty(name="Note 3", description="")

    def hasNotes(self):
        return "" != self.note01 or "" != self.note02 or "" != self.note03

    #############
    # interface for Montage #####
    # Note: Shot inherits from ShotInterface
    #############

    # def __init__(self, parent, shot):      # cannot use this constructor since new shots are added directly to the array of take
    def __init__(self):
        """
        parent: reference to the parent take
        """
        #  self.parent = None
        super().__init__()
        pass

    def initialize(self, parent):
        """Parent is the parent take"""
        # if "parent" not in self:
        # props = config.getAddonProps(self.parentScene)
        # #  print(" icicicic parent in shot")

        # UAS_ShotManager_Shot.parent = property(lambda self: parent)
        # self.parent = parent
        pass

    def get_index_in_parent(self):
        props = config.getAddonProps(self.parentScene)
        return props.getShotIndex(self)

    def get_name(self):
        # return self.parentScene.UAS_shot_manager_props.getRenderShotPrefix() + self.name
        return self.getName_PathCompliant(withPrefix=True)

    def printInfo(self, only_clip_info=False):
        super().printInfo(only_clip_info=True)

    #   infoStr = f"             - Media:"
    #   print(infoStr)

    ############
    # Note that all these interface functions are refering to timings in the EDIT, not in the 3D environment !!
    ############

    def get_frame_start(self):
        return self.getEditStart()

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips"""
        return self.getEditEnd() + 1

    def get_frame_duration(self):
        return self.getDuration()

    def get_frame_final_start(self):
        return self.get_frame_start()

    def get_frame_final_end(self):
        """get_frame_final_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips"""
        return self.get_frame_end()

    def get_frame_final_duration(self):
        return self.get_frame_duration()

    def get_frame_offset_start(self):
        return 0

    def get_frame_offset_end(self):
        return 0
