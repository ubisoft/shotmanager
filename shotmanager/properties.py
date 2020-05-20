import os
import json

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
    FloatVectorProperty,
)

from .operators import shots
from .operators import takes


class UAS_ShotManager_Shot(PropertyGroup):
    def getDuration(self):
        """ Returns the shot duration in frames
            in Blender - and in Shot Manager - the last frame of the shot is included in the rendered images
        """
        duration = self.end - self.start + 1
        return duration

    def getOutputFileName(self, frameIndex=-1, fullPath=False, fullPathOnly=False, rootFilePath=""):
        return bpy.context.scene.UAS_shot_manager_props.getShotOutputFileName(
            self, frameIndex=frameIndex, fullPath=fullPath, fullPathOnly=fullPathOnly, rootFilePath=rootFilePath
        )

    def getName_PathCompliant(self):
        shotName = self.name.replace(" ", "_")
        return shotName

    def _shot_name_changed(self, context):
        dup_name = False

        # wkip fix rename
        # ownerTakeInd = context.scene.UAS_shot_manager_props.getShotOwnerTake(self)  or ownertakeind?
        shots = context.scene.UAS_shot_manager_props.getShotsList(takeIndex=self.parentTakeIndex)

        for shot in shots:
            if shot != self and self.name == shot.name:
                dup_name = True

        if dup_name:
            self.name = f"{self.name}_1"

    def _start_frame_changed(self, context):
        if self.start > self.end:
            self.end = self.start

    def _end_frame_changed(self, context):
        if self.start > self.end:
            self.start = self.end

    def _enabled_changed(self, context):
        context.scene.UAS_shot_manager_props.selected_shot_index = context.scene.UAS_shot_manager_props.getShotIndex(
            self
        )

    parentTakeIndex: IntProperty(name="Parent Take Index", default=-1)
    name: StringProperty(name="Name", update=_shot_name_changed)
    start: IntProperty(name="Start", update=_start_frame_changed)
    end: IntProperty(name="End", update=_end_frame_changed)
    enabled: BoolProperty(
        name="Enabled", description="Use - or not - the shot in the edit", update=_enabled_changed, default=True
    )

    camera: PointerProperty(
        name="Camera",
        description="Select a Camera",
        type=bpy.types.Object,
        poll=lambda self, obj: True if obj.type == "CAMERA" else False,
    )

    color: FloatVectorProperty(subtype="COLOR", min=0.0, max=1.0, size=4, default=(1.0, 1.0, 1.0, 1.0), options=set())


class UAS_ShotManager_Take(PropertyGroup):
    def getName_PathCompliant(self):
        takeName = self.name.replace(" ", "_")
        return takeName

    name: StringProperty(name="Name")

    shots: CollectionProperty(type=UAS_ShotManager_Shot)


class UAS_ShotManager_RenderSettings(PropertyGroup):

    name: StringProperty(name="Name", default="Render Settings")

    renderMode: EnumProperty(
        name="Render Mode",
        description="Render Mode",
        items=(("STILL", "Still", ""), ("ANIMATION", "Animation", ""), ("PROJECT", "Project", "")),
        default="STILL",
    )

    renderAllTakes: BoolProperty(name="Render All Takes", default=False)

    renderAllShots: BoolProperty(name="Render All Shots", default=False)

    renderAlsoDisabled: BoolProperty(name="Render Also Disabled", default=False)

    renderWithHandles: BoolProperty(name="Render With Handles", default=False)

    writeToDisk: BoolProperty(name="Write to Disk", default=False)

    # file format
    # image_settings_file_format = 'FFMPEG'
    # scene.render.ffmpeg.format = 'MPEG4'


class UAS_ShotManager_Props(PropertyGroup):
    def get_isInitialized(self):
        #    print(" get_isInitialized")
        val = self.get("isInitialized", False)

        if not val:
            self.initialize_shot_manager()

        return val

    def set_isInitialized(self, value):
        #  print(" set_isInitialized: value: ", value)
        self["isInitialized"] = value

    isInitialized: BoolProperty(get=get_isInitialized, set=set_isInitialized, default=False)

    # render
    #############

    def addRenderSettings(self):
        newRenderSettings = self.renderSettingsList.add()
        return newRenderSettings

    # renderSettingsStill: CollectionProperty (
    #   type = UAS_ShotManager_RenderSettings )
    renderSettingsStill: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsAnim: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsProject: PointerProperty(type=UAS_ShotManager_RenderSettings)

    def get_displayStillProps(self):
        val = self.get("displayStillProps", True)
        return val

    def set_displayStillProps(self, value):
        print(" set_displayStillProps: value: ", value)
        self["displayStillProps"] = True
        self["displayAnimationProps"] = False
        self["displayProjectProps"] = False

    def get_displayAnimationProps(self):
        val = self.get("displayAnimationProps", False)
        return val

    def set_displayAnimationProps(self, value):
        print(" set_displayAnimationProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = True
        self["displayProjectProps"] = False

    def get_displayProjectProps(self):
        val = self.get("displayProjectProps", False)
        return val

    def set_displayProjectProps(self, value):
        print(" set_displayProjectProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayProjectProps"] = True

    displayStillProps: bpy.props.BoolProperty(
        name="Display Still Preset Properties", get=get_displayStillProps, set=set_displayStillProps, default=True
    )
    displayAnimationProps: bpy.props.BoolProperty(
        name="Display Animation Preset Properties",
        get=get_displayAnimationProps,
        set=set_displayAnimationProps,
        default=False,
    )
    displayProjectProps: bpy.props.BoolProperty(
        name="Display Project Preset Properties",
        get=get_displayProjectProps,
        set=set_displayProjectProps,
        default=False,
    )

    # shots
    #############

    display_name_in_shotlist: BoolProperty(name="Display Name in Shot List", default=True, options=set())

    display_camera_in_shotlist: BoolProperty(name="Display Camera in Shot List", default=False, options=set())

    display_lens_in_shotlist: BoolProperty(name="Display Camera Lens in Shot List", default=False, options=set())

    display_duration_in_shotlist: BoolProperty(name="Display Shot Duration in Shot List", default=False, options=set())

    display_color_in_shotlist: BoolProperty(name="Display Color in Shot List", default=False, options=set())

    display_selectbut_in_shotlist: BoolProperty(
        name="Display Camera Selection Button in Shot List", default=True, options=set()
    )

    new_shot_duration: IntProperty(default=50, options=set())

    new_shot_prefix: StringProperty(default="Sh")

    render_shot_prefix: StringProperty(
        name="Render Shot Prefix", description="Prefix added to the shot names at render time", default="Act01_Sq01_"
    )

    # shots list
    #############

    current_shot_index: IntProperty(default=-1)

    selected_shot_index: IntProperty(default=-1)

    current_shot_properties_mode: bpy.props.EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("CURRENT", "Current Shot", ""), ("SELECTED", "Selected Shot", "")),
        default="SELECTED",
    )

    highlight_all_shot_frames: BoolProperty(default=True, options=set())

    # timeline
    #############

    # def timeline_valueChanged( self, context ):
    #     if self.display_timeline:
    #         bpy.ops.uas_shot_manager.draw_timeline ( "INVOKE_DEFAULT" )

    # display_timeline: BoolProperty (    default = False,
    #                                     options = set ( ),
    #                                     update = timeline_valueChanged )

    change_time: BoolProperty(default=True, options=set())

    display_disabledshots_in_timeline: BoolProperty(default=False, options=set())

    # display_prev_next_buttons: BoolProperty (
    #     default = True,
    #     options = set ( ) )

    # takes
    #############

    def _list_takes(self, context):
        res = list()
        takes = self.takes
        for i, take in enumerate([t.name for t in takes]):
            res.append((take, take, "", i))

        return res

    def _current_take_changed(self, context):
        self.setCurrentShotByIndex(0)
        self.setSelectedShotByIndex(0)

    takes: CollectionProperty(type=UAS_ShotManager_Take)

    current_take_name: EnumProperty(
        items=_list_takes, name="Takes", description="Select a take", update=_current_take_changed
    )

    handles: IntProperty(default=10, min=0, options=set())

    ####################
    # takes
    ####################

    def fixShotsParent(self):
        """Recompute the value of parentTakeIndex for each shot - Debug
        """
        for i, t in enumerate(self.takes):
            for s in t.shots:
                s.parentTakeIndex = i

    def getUniqueTakeName(self, nameToMakeUnique):
        uniqueName = nameToMakeUnique
        takes = self.getTakes()

        dup_name = False
        for take in takes:
            if uniqueName == take.name:
                dup_name = True
        if dup_name:
            uniqueName = f"{uniqueName}_1"

        return uniqueName

    def getTakes(self):
        return self.takes

    def getTakeIndex(self, take):
        #  print("getCurrentTakeIndex")
        takeInd = -1
        if 0 < len(self.takes):
            takeInd = 0
            #   print(" self.takes[0]: ", self.takes[takeInd].name)
            #   print(" self.current_take_name: " + str(take) + ", type: " + str(type(take)) )
            while takeInd < len(self.takes) and self.takes[takeInd] != take:
                #        print("  toto02: takeInd: ", takeInd)
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1

        return takeInd

    def getCurrentTakeIndex(self):
        #   print("getCurrentTakeIndex")
        takeInd = -1
        if 0 < len(self.takes):
            takeInd = 0
            #      print(" self.takes[0]: " + str(self.takes[takeInd].name) + ", type: " + str(type(self.takes[takeInd])) )
            #     print(" self.current_take_name: " + str(self.current_take_name) + ", type: " + str(type(self.current_take_name)) )
            while takeInd < len(self.takes) and self.takes[takeInd].name != self.current_take_name:
                #         print("  toto06: takeInd: ", takeInd)
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1
        #    self.current_take_name = self.takes[takeInd].name

        return takeInd

    def setCurrentTakeIndex(self, currentTakeIndex):
        currentTakeInd = min(currentTakeIndex, len(self.takes))
        if -1 < currentTakeInd:
            self.current_take_name = self.takes[currentTakeInd].name
            self.setCurrentShotByIndex(0)
            self.setSelectedShotByIndex(0)
        else:
            self.current_take_name = ""

    def getCurrentTakeName(self):
        """ Return the name of the current take, 
        """
        #    print("getCurrentTakeName")
        #    currentTakeInd = self.getCurrentTakeIndex()
        #    if -1 == currentTakeInd: return None
        #    return (self.getTakes()[currentTakeInd].name)
        currentTakeName = self.current_take_name
        return currentTakeName

    def getTakeName_PathCompliant(self, takeIndex=-1):
        """ Return the name of the specified take with spaces replaced by "_"
        """
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        takeName = ""
        if -1 == takeInd:
            return takeName

        takeName = self.takes[takeInd].getName_PathCompliant()

        return takeName

    def getCurrentTake(self):
        #    print("getCurrentTake")
        currentTakeInd = self.getCurrentTakeIndex()
        if -1 == currentTakeInd:
            return None
        return self.getTakes()[currentTakeInd]

    # render
    #############

    useProjectRenderSettings: BoolProperty(
        name="Use Render Project Settings", description="Use Render Project Settings", default=True,
    )

    def get_useStampInfoDuringRendering(self):
        #  return self.useStampInfoDuringRendering
        val = self.get("useStampInfoDuringRendering", True)
        # print("*** get_useStampInfoDuringRendering: value: ", val)
        return val

    def set_useStampInfoDuringRendering(self, value):
        print("*** set_useStampInfoDuringRendering: value: ", value)
        self["useStampInfoDuringRendering"] = value

        if "UAS_StampInfo_Settings" in bpy.context.scene:
            # bpy.context.scene.UAS_StampInfo_Settings.activateStampInfo(value)
            bpy.context.scene.UAS_StampInfo_Settings.stampInfoUsed = value

    # def useStampInfoDuringRendering_StateChanged(self, context):
    #     print("\n*** useStampInfoDuringRendering updated. New state: ", self.useStampInfoDuringRendering)

    useStampInfoDuringRendering: BoolProperty(
        name="Stamp Render Info",
        description="Stamp render information on rendered images thanks to Stamp Info add-on",
        default=True,
        get=get_useStampInfoDuringRendering,  # removed cause the use of Stamp Info in this add-on is independent from the one of Stamp Info add-on itself
        set=set_useStampInfoDuringRendering,
        # update = useStampInfoDuringRendering_StateChanged,
        options=set(),
    )

    renderRootPath: StringProperty(name="Render Root Path", default="")

    def isRenderRootPathValid(self, renderRootFilePath=None):
        pathIsValid = False

        rootPath = self.renderRootPath if None == renderRootFilePath else renderRootFilePath
        if "" != rootPath and os.path.exists(rootPath):
            pathIsValid = True
        return pathIsValid

    ####################
    # editing
    ####################

    def getEditDuration(self, ignoreDisabled=False, takeIndex=-1):
        """ Return edit duration in frames
        """
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        duration = -1
        if -1 == takeInd:
            return -1

        shots = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        if 0 < len(shots):
            duration = 0
            for sh in shots:
                duration += sh.getDuration()

        return duration

    def getEditCurrentTime(self, ignoreDisabled=False):
        """ Return edit current time in frames, -1 if no shots or if current shot is disabled
            works only on current take
            wkip negative times issues coming here... :/
        """
        # works only on current take
        takeInd = self.getCurrentTakeIndex()
        editCurrentTime = -1
        if -1 == takeInd:
            return editCurrentTime

        # current time must be in the range of the current shot!!!
        # get the whole shots list
        shots = self.getShotsList(ignoreDisabled=False, takeIndex=takeInd)

        if 0 < len(shots):
            # case where current shot is disabled -- current shot may not be in the shot list if shots is not the whole list
            currentShot = self.getCurrentShot()

            if None != currentShot:
                currentTime = bpy.context.scene.frame_current

                if currentShot.enabled and currentShot.start <= currentTime and currentTime <= currentShot.end:
                    editCurrentTime = 0
                    shotInd = 0
                    while shotInd < len(shots) and currentShot != shots[shotInd]:
                        #         print("    While: shotInd: " + str(shotInd) + ", currentShot: " + str(currentShot) + ", shots[shotInd]: " + str(shots[shotInd]))
                        #         print("    editCurrentTime: ", editCurrentTime)
                        if not ignoreDisabled or shots[shotInd].enabled:
                            editCurrentTime += shots[shotInd].getDuration()
                        shotInd += 1

                    editCurrentTime += currentTime - currentShot.start
                # if shotInd == len(shots): editCurrentTime = -1

        return editCurrentTime

    ####################
    # shots
    ####################

    def getUniqueShotName(self, nameToMakeUnique, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        uniqueName = nameToMakeUnique
        if -1 == takeInd:
            return uniqueName

        shots = self.getShotsList(ignoreDisabled=False, takeIndex=takeIndex)

        dup_name = False
        for shot in shots:
            if uniqueName == shot.name:
                dup_name = True
        if dup_name:
            uniqueName = f"{uniqueName}_1"

        return uniqueName

    def addShot(
        self,
        atIndex=-1,
        takeIndex=-1,
        name="defaultShot",
        start=10,
        end=20,
        camera=None,
        color=(0.2, 0.6, 0.8, 1),
        enabled=True,
    ):
        """ Add a new shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
            that is not the current one)
            Return the newly added shot
            Since this function works also with takes that are not the current one the current shot is not taken into account not modified
        """
        # wkip wip fix for early backward compatibility - to remove
        self.fixShotsParent()
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        newShot = None
        if -1 == takeInd:
            return None

        shots = self.get_shots(takeInd)

        newShot = shots.add()  # shot is added at the end
        newShot.parentTakeIndex = takeInd
        newShot.name = name
        newShot.enabled = enabled
        newShot.start = start
        newShot.end = end
        newShot.camera = camera
        newShot.color = color

        if -1 != atIndex:  # move shot at specified index
            shots.move(len(shots) - 1, atIndex)

        return newShot

    def copyShot(self, shot, atIndex=-1, takeIndex=-1):
        """ Copy a shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
            that is not the current one)
            Return the newly added shot
            Since this function works also with takes that are not the current one the current shot is not taken into account not modified
        """
        # wkip wip fix for early backward compatibility - to remove
        self.fixShotsParent()
        takeInd = shot.parentTakeIndex if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        newShot = None
        if -1 == takeInd:
            return None

        shots = self.get_shots(takeInd)

        newShot = shots.add()  # shot is added at the end
        newShot.parentTakeIndex = takeInd
        newShot.name = shot.name
        newShot.enabled = shot.enabled
        newShot.start = shot.start
        newShot.end = shot.end
        newShot.camera = shot.camera
        newShot.color = shot.color

        if -1 != atIndex:  # move shot at specified index
            shots.move(len(shots) - 1, atIndex)
            newShot = shots[atIndex]

        return newShot

    def setCurrentShotByIndex(self, currentShotIndex):
        """ Changing the current shot doesn't affect the selected one
        """
        #  print(" setCurrentShotByIndex")
        scene = bpy.context.scene
        props = scene.UAS_shot_manager_props

        shots = self.get_shots()
        self.current_shot_index = currentShotIndex

        if -1 < currentShotIndex and len(shots) > currentShotIndex:
            if self.change_time:
                scene.frame_current = shots[currentShotIndex].start

            #    print(" Set Current Shot: new shot absolute index: ", currentShotIndex)

            #        self.selected_shot_index = currentShotIndex        # removed

            if shots[currentShotIndex].camera is not None:
                print("    new camera: ", shots[currentShotIndex].camera.name)

                # set the current camera in the 3D view
                # [‘PERSP’, ‘ORTHO’, ‘CAMERA’]
                area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
                #    area.spaces[0].region_3d.view_perspective = 'PERSP'

                # print("00000")
                scene.camera = shots[currentShotIndex].camera
                #    bpy.context.scene.camera =  bpy.context.scene.objects["Camera_Sapin"]
                #    bpy.data.scenes[ "SceneRace" ].camera = bpy.context.scene.objects["Camera_Sapin"]
                # scene.camera = shots[ currentShotIndex ].camera
                #   bpy.data.scenes[ scn.name ].camera = shots[ self.index ].camera

                #    print("    new scene camera: ", bpy.context.scene.camera.name)
                area.spaces[0].region_3d.view_perspective = "CAMERA"

            # bpy.context.scene.objects["Camera_Sapin"]

            #  context.space_data.region_3d.view_perspective = "CAMERA"

    def setCurrentShot(self, currentShot):
        shotInd = self.getShotIndex(currentShot)
        #    print("setCurrentShot: shotInd:", shotInd)
        self.setCurrentShotByIndex(shotInd)

    def getShotIndex(self, shot, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        shotInd = -1
        if -1 == takeInd:
            return shotInd

        shots = self.getShotsList(ignoreDisabled=False, takeIndex=takeIndex)

        shotInd = 0
        while shotInd < len(shots) and shot != shots[shotInd]:  # wkip mettre shots[shotInd].name?
            shotInd += 1
        if shotInd == len(shots):
            shotInd = -1

        return shotInd

    def getShot(self, shotIndex, ignoreDisabled=False, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        shot = None
        if -1 == takeInd:
            return None

        shots = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        # if ignoreDisabled:
        #     if 0 < len(shots) and shotIndex < len(shots):
        #         shot = shots[shotIndex]
        # else if 0 < shotNumber and shotIndex < shotNumber:
        #     shot = self.takes[takeIndex].shots[shotIndex]

        if 0 < len(shots) and shotIndex < len(shots):
            shot = shots[shotIndex]

        return shot

    def get_shots(self, takeIndex=-1):
        """ Return the actual shots array of the specified take
        """
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        shots = []
        if -1 == takeInd:
            return shots

        shots = self.takes[takeInd].shots

        return shots

    def getShotsList(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        shots = []
        if -1 == takeInd:
            return shots

        for shot in self.takes[takeInd].shots:
            # if shot.enabled or self.context.scene.UAS_shot_manager_props.display_disabledshots_in_timeline:
            if not ignoreDisabled or shot.enabled:
                shots.append(shot)

        return shots

    def getCurrentShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        """ Return the index of the current shot in the enabled shot list of the current take
            Use this function instead of a direct call to self.current_shot_index
            
            if ignoreDisabled is false (default) then the shot index is relative to the whole shot list,
               otherwise it is relative to the list of the enabled shots
            can return -1 if all the shots are disabled!!
            if takeIndex is different from the current take then it returns -1 because other takes than the current one are not supposed to
            have a current shot
        """
        #   print(" *** getCurrentShotIndex")

        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        currentShotInd = -1
        if -1 == takeInd:
            return currentShotInd

        # other takes than the current one are not supposed to have a current shot
        if self.current_take_name != self.takes[takeInd].name:
            return -1

        if ignoreDisabled and 0 < len(self.takes[takeInd].shots):
            # for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
            currentShotInd = self.current_shot_index
            for i in range(self.current_shot_index + 1):
                if not self.takes[takeInd].shots[i].enabled:
                    currentShotInd -= 1
        #      print("  in ignoreDisabled, currentShotInd: ", currentShotInd)
        else:
            if 0 < len(self.takes[takeInd].shots):

                if len(self.takes[takeInd].shots) > self.current_shot_index:
                    #          print("    in 01")
                    currentShotInd = self.current_shot_index
                else:
                    #          print("    in 02")
                    currentShotInd = len(self.takes[takeInd].shots) - 1
                    self.setCurrentShotByIndex(currentShotInd)

        # print("  NOT in ignoreDisabled, currentShotInd: ", currentShotInd)

        return currentShotInd

    def getCurrentShot(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        currentShotInd = -1
        if -1 == takeInd:
            return currentShotInd

        currentShotInd = self.getCurrentShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print("getCurrentShot: currentShotInd: ", currentShotInd)
        currentShot = None
        if -1 != currentShotInd:
            currentShot = self.takes[takeInd].shots[currentShotInd]

        return currentShot

    def getSelectedShotIndex(self):
        """ Return the index of the selected shot in the enabled shot list of the current take
            Use this function instead of a direct call to self.selected_shot_index
        """
        if 0 >= len(self.takes) or 0 >= len(self.get_shots()):
            self.selected_shot_index = -1

        return self.selected_shot_index

    def getSelectedShot(self):
        selectedShotInd = self.getSelectedShotIndex()
        selectedShot = None
        if -1 != selectedShotInd:
            selectedShot = (self.get_shots())[selectedShotInd]

        return selectedShot

    def setSelectedShotByIndex(self, selectedShotIndex):
        # print("setSelectedShotByIndex: selectedShotIndex:", selectedShotIndex)
        self.selected_shot_index = selectedShotIndex

    def setSelectedShot(self, selectedShot):
        shotInd = self.getShotIndex(selectedShot)
        self.setSelectedShotByIndex(shotInd)

    # # can return -1 if all the shots are disabled!!
    # def getCurrentShotIndexInEnabledList( self ):
    #     currentIndexInEnabledList = self.current_shot_index
    #     #for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
    #     for i in range(self.current_shot_index + 1):
    #         if not self.takes[self.current_take_name].shots[i].enabled:
    #             currentIndexInEnabledList -= 1

    #     return currentIndexInEnabledList

    def getFirstShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        """
        """
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        firstShotInd = -1
        if -1 == takeInd:
            return firstShotInd

        shots = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print(" getFirstShotIndex: shots: ", shots)

        #  not required cause shots is already filtered!
        # if ignoreDisabled and 0 < len(shots):
        #     firstShotInd = 0
        #     while firstShotInd < len(shots) and not shots[firstShotInd].enabled:
        #         firstShotInd += 1
        #     if firstShotInd >= len(shots): firstShotInd = 0
        # else:
        if 0 < len(shots):
            firstShotInd = 0

        return firstShotInd

    # # can return -1 if all the shots are disabled!!
    # def getCurrentShotIndexInEnabledList( self ):
    #     currentIndexInEnabledList = self.current_shot_index
    #     #for i, shot in enumerate ( self.context.scene.UAS_shot_manager_props.takes[self.context.scene.UAS_shot_manager_props.current_take_name].shots ):
    #     for i in range(self.current_shot_index + 1):
    #         if not self.takes[self.current_take_name].shots[i].enabled:
    #             currentIndexInEnabledList -= 1

    #     return currentIndexInEnabledList
    def getLastShotIndex(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        lastShotInd = -1
        if -1 == takeInd:
            return lastShotInd

        shots = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        print(" getLastShotIndex: shots: ", shots)

        if 0 < len(shots):
            lastShotInd = len(shots) - 1

        return lastShotInd

    def getFirstShot(self, ignoreDisabled=False, takeIndex=-1):
        firstShotInd = self.getFirstShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        # print(" getFirstShot: firstShotInd: ", firstShotInd)
        firstShot = (
            None
            if -1 == firstShotInd
            else self.getShot(firstShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return firstShot

    def getLastShot(self, ignoreDisabled=False, takeIndex=-1):
        lastShotInd = self.getLastShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        print(" getLastShot: lastShotInd: ", lastShotInd)
        lastShot = (
            None if -1 == lastShotInd else self.getShot(lastShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return lastShot

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the previous enabled shot in the WHOLE list, -1 if none
    def getPreviousEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        previousShotInd = -1
        if -1 == takeInd:
            return previousShotInd

        shots = self.getShotsList(takeIndex=takeIndex)

        previousShotInd = currentShotIndex - 1
        isPreviousFound = shots[previousShotInd].enabled
        while 0 <= previousShotInd and not isPreviousFound:
            previousShotInd -= 1
            isPreviousFound = shots[previousShotInd].enabled

        return previousShotInd

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the next enabled shot in the WHOLE list, -1 if none
    def getNextEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        nextShotInd = -1
        if -1 == takeInd:
            return nextShotInd

        shots = self.getShotsList(takeIndex=takeIndex)

        nextShotInd = currentShotIndex + 1
        if len(shots) > nextShotInd:
            isNextFound = shots[nextShotInd].enabled
            while len(shots) > nextShotInd and not isNextFound:
                nextShotInd += 1
                if len(shots) > nextShotInd:
                    isNextFound = shots[nextShotInd].enabled

        if len(shots) <= nextShotInd:
            nextShotInd = -1

        return nextShotInd

    # works only on current take
    # behavior of this button:
    #  if current shot is enabled:
    #   - first click: put current time at the start of the current enabled shot
    #  else:
    #   - fisrt click: put current time at the end of the previous enabled shot

    # wkip ignoreDisabled pas encore implémenté ici!!!!
    def goToPreviousShot(self, currentFrame, ignoreDisabled=False):
        """ ouici
        mon comment wkip
        """
        print(" ** -- ** goToPreviousShot")
        previousShot = None
        previousShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if True or bpy.context.window_manager.UAS_shot_manager_handler_toggle:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShot(currentShotInd)
            print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShot(previousShotInd).end
            else:
                print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShot(previousShotInd).end
                    else:  # case of the very first shot
                        previousShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    print("      current frame is middle or end")
                    previousShotInd = currentShotInd
                    newFrame = currentShot.start

        self.setCurrentShotByIndex(previousShotInd)
        self.setSelectedShotByIndex(previousShotInd)
        bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    def goToNextShot(self, currentFrame, ignoreDisabled=False):
        print(" ** -- ** goToNextShot")
        nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if True or bpy.context.window_manager.UAS_shot_manager_handler_toggle:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShot(currentShotInd)
            print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShot(nextShotInd).start
            else:
                print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShot(nextShotInd).start
                    else:  # case of the very last shot
                        nextShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    print("      current frame is middle or start")
                    nextShotInd = currentShotInd
                    newFrame = currentShot.end

        self.setCurrentShotByIndex(nextShotInd)
        self.setSelectedShotByIndex(nextShotInd)
        bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    # behavior of this button:
    #  if current shot is enabled:
    #   - first click: put current time at the start of the current enabled shot
    #  else:
    #   - fisrt click: put current time at the end of the previous enabled shot

    # wkip ignoreDisabled pas encore implémenté ici!!!!
    def goToPreviousFrame(self, currentFrame, ignoreDisabled=False):
        #  print(" ** -- ** goToPreviousFrame")
        previousShot = None
        previousShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_handler_toggle:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShot(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #       print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #           print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShot(previousShotInd).end
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    #           print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        #              print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShot(previousShotInd).end
                    else:  # case of the very first shot
                        previousShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    print("      current frame is middle or end")
                    previousShotInd = currentShotInd
                    newFrame = currentFrame - 1

            self.setCurrentShotByIndex(previousShotInd)
            self.setSelectedShotByIndex(previousShotInd)
            bpy.context.scene.frame_set(newFrame)

        # in standard play mode behavior is the classic one
        else:
            newFrame = currentFrame - 1
            bpy.context.scene.frame_set(newFrame)

        return newFrame

    # works only on current take
    def goToNextFrame(self, currentFrame, ignoreDisabled=False):
        #   print(" ** -- ** goToNextShot")
        nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_handler_toggle:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShot(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #        print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #            print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShot(nextShotInd).start
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    #           print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        #              print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShot(nextShotInd).start
                    else:  # case of the very last shot
                        nextShotInd = currentShotInd
                        newFrame = currentFrame
                #  elif currentFrame == currentShot.end:
                #      newFrame = currentShot.start
                else:
                    #         print("      current frame is middle or start")
                    nextShotInd = currentShotInd
                    newFrame = currentFrame + 1

            self.setCurrentShotByIndex(nextShotInd)
            self.setSelectedShotByIndex(nextShotInd)
            bpy.context.scene.frame_set(newFrame)

        # in standard play mode behavior is the classic one
        else:
            newFrame = currentFrame + 1
            bpy.context.scene.frame_set(newFrame)

        return newFrame

    def getShotOutputFileNameFromIndex(
        self, shotIndex=-1, takeIndex=-1, frameIndex=-1, fullPath=False, fullPathOnly=False, rootFilePath=""
    ):
        shot = self.getShot(shotIndex=shotIndex, takeIndex=takeIndex)

        fileName = ""
        if None == shot:
            return fileName

        fileName = self.getShotOutputFileName(
            shot, fullPath=fullPath, fullPathOnly=fullPathOnly, rootFilePath=rootFilePath
        )

        return fileName

    def getShotOutputFileName(self, shot, frameIndex=-1, fullPath=False, fullPathOnly=False, rootFilePath=""):
        props = bpy.context.scene.UAS_shot_manager_props
        resultStr = ""

        fileName = props.render_shot_prefix + shot.getName_PathCompliant()

        # fileName + frame index + extension
        fileFullName = fileName
        if -1 != frameIndex:
            fileFullName += "_" + f"{(frameIndex):04d}"
            fileFullName += ".png"
        else:
            fileFullName += ".mp4"

        filePath = ""
        if fullPath or fullPathOnly:

            if "" == rootFilePath:
                #  head, tail = os.path.split(bpy.path.abspath(bpy.data.filepath))
                # wkip we assume renderRootPath is valid...
                head, tail = os.path.split(bpy.path.abspath(props.renderRootPath))
                filePath = head + "\\"
            else:
                # wkip tester le chemin
                filePath = rootFilePath
                if not filePath.endswith("\\"):
                    filePath += "\\"

            filePath += f"{self.getTakeName_PathCompliant(takeIndex = shot.parentTakeIndex)}" + "\\"

        #   filePath += f"//{fileName}"

        # path is absolute and ends with a /
        if fullPathOnly:
            resultStr = filePath
        elif fullPath:
            resultStr = filePath + fileFullName
        else:
            resultStr = fileFullName

        return resultStr

    def getSceneCameras(self):
        """ Return the list of the cameras in the current scene
        """
        cameras = []
        for obj in bpy.context.scene.objects:
            # if str(type(bpy.context.view_layer.objects.active.data)) == "<class 'bpy.types.Camera'>"
            if str(type(obj.data)) == "<class 'bpy.types.Camera'>":
                cameras.append(obj)

        return cameras

    def selectCamera(self, shotIndex):
        bpy.ops.object.select_all(action="DESELECT")
        shot = self.getShot(shotIndex)
        if None != shot:
            if None != shot.camera:
                camObj = bpy.context.scene.objects[shot.camera.name]
                bpy.context.view_layer.objects.active = camObj
                camObj.select_set(True)

    def getActiveCameraName(self):
        cameras = self.getSceneCameras()
        # selectedObjs = []  #bpy.context.view_layer.objects.active    # wkip get the selection
        currentCam = None
        currentCamName = ""

        if bpy.context.view_layer.objects.active and (bpy.context.view_layer.objects.active).type == "CAMERA":
            # if len(selectedObjs) == 1 and selectedObjs.name == bpy.context.scene.objects[self.cameraName]:
            #    currentCam =  bpy.context.scene.objects[self.cameraName]
            currentCam = bpy.context.view_layer.objects.active
        if currentCam:
            currentCamName = currentCam.name
        elif 0 < len(cameras):
            currentCamName = cameras[0].name

        return currentCamName

    def setProjectRenderFilePath(self):
        # if '' == bpy.data.filepath:

        bpy.context.scene.render.filepath = f"//{self.getTakeName_PathCompliant()}"

    # wkip traiter cas quand aps de nom de fichier
    def getRenderFileName(self):
        #   print("\n getRenderFileName ")
        # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
        # the name of the file)
        filename = bpy.context.scene.render.filepath
        lastOccSeparator = filename.rfind("\\")
        if -1 != lastOccSeparator:
            filename = filename[lastOccSeparator + 1 :]

        #   print("    filename: " + filename)
        return filename

    # returns the path of the info image corresponding to the specified frame
    # path of temp info files is the same as the render output files
    #   def getInfoFileFullPath(self, renderFrameInd):
    #      pass
    # #    print("\n getInfoFileFullPath ")
    # #  filepath = bpy.data.filepath                               # get current .blend file path and name
    #     filepath = scene.render.filepath                               # get current .blend file path and name
    # #    print("    Temp Info Filepath: ", filepath)

    #     filePathIsValid = False

    #     # if path is relative then get the full path
    #     if '//' == filepath[0:2]:                        #and bpy.data.is_saved:
    #         # print("Rendering path is relative")
    #         filepath = bpy.path.abspath(filepath)

    #     filepath = bpy.path.abspath(filepath)
    # #    print("    Temp Info Filepath 02: ", filepath)

    #     # filename is parsed in order to remove the last block in case it doesn't finish with \ or / (otherwise it is
    #     # the name of the file)
    #     lastOccSeparator = filepath.rfind("\\")
    #     if -1 != lastOccSeparator:
    #         filepath = filepath[0:lastOccSeparator + 1]
    # #        print("    Temp Info Filepath 03: ", filepath)

    #     if os.path.exists(filepath):
    # #        print("  Rendering path is valid")
    #         filePathIsValid = True

    #     renderPath              = None
    #     renderedInfoFileName    = None
    #     if filePathIsValid:
    #         renderPath = os.path.dirname(filepath)               # get only .blend path

    #     #  renderPath = r"Z:\EvalSofts\Blender\DevPython_Data\UAS_StampInfo_Data\Outputs"
    # #        print("renderPath**: ", renderPath)
    #         renderedInfoFileName = "\\" + getRenderFileName(scene)
    #         renderedInfoFileName += r"_tmp_StampInfo." + '{:04d}'.format(renderFrameInd) + ".png"

    # #       renderedInfoFileName = r"\_tmp_StampInfo." + '{:04d}'.format(renderFrameInd) + ".png"

    #     return (renderPath, renderedInfoFileName)

    def restoreProjectSettings(self):
        scene = bpy.context.scene

        # verbose_set("UAS_PROJECT_NAME","RRSpecial",override_existing,verbose)
        # verbose_set("UAS_PROJECT_FRAMERATE","25.0",override_existing,verbose)
        # verbose_set("UAS_PROJECT_RESOLUTION","[1280,720]",override_existing,verbose)
        # verbose_set("UAS_PROJECT_RESOLUTIONFRAMED","[1280,960]",override_existing,verbose)
        # verbose_set("UAS_PROJECT_OUTPUTFORMAT","mp4",override_existing,verbose)
        # verbose_set("UAS_PROJECT_COLORSPACE","",override_existing,verbose)
        # verbose_set("UAS_PROJECT_ASSETNAME","",override_existing,verbose)

        if "UAS_RRS_PROJECTNAME" in os.environ.keys():
            projProp_Name = os.environ["UAS_RRS_PROJECTNAME"]

        if "UAS_PROJECT_RESOLUTION" in os.environ.keys():
            resolution = json.loads(os.environ["UAS_PROJECT_RESOLUTION"])
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]

        if "UAS_PROJECT_FRAMERATE" in os.environ.keys():
            scene.render.fps = float(os.environ["UAS_PROJECT_FRAMERATE"])

        # other settings
        scene.render.fps_base = 1.0
        scene.render.resolution_percentage = 100.0

        # path
        self.setProjectRenderFilePath()

    def createDefaultTake(self):
        takes = self.getTakes()
        defaultTake = None
        if 0 >= len(takes):
            defaultTake = takes.add()
            defaultTake.name = "Main Take"
            self.setCurrentTakeIndex(0)
            # self.setCurrentShotByIndex(-1)
            # self.setSelectedShotByIndex(-1)

        else:
            defaultTake = takes[0]
        return defaultTake

    def createRenderSettings(self):

        # Still
        self.renderSettingsStill.name = "Still Preset"
        self.renderSettingsStill.renderMode = "STILL"

        # Animation
        self.renderSettingsAnim.name = "Animation Preset"
        self.renderSettingsAnim.renderMode = "ANIMATION"

        # Project
        self.renderSettingsProject.name = "Project Preset"
        self.renderSettingsProject.renderMode = "PROJECT"

    def initialize_shot_manager(self):
        print("\nInitializing Shot Manager...\n")
        self.createDefaultTake()
        self.createRenderSettings()
        self.isInitialized = True


_classes = (UAS_ShotManager_Shot, UAS_ShotManager_Take, UAS_ShotManager_RenderSettings, UAS_ShotManager_Props)


def register():
    print("\n *** *** Resistering Shot Manager Addon *** *** \n")
    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.UAS_shot_manager_props = PointerProperty(type=UAS_ShotManager_Props)


def unregister():
    del bpy.types.Scene.UAS_shot_manager_props
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
