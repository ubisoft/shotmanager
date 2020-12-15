import os
from stat import S_IMODE, S_IWRITE
from pathlib import Path
import re

import bpy
from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
)

# from shotmanager.operators import shots
from shotmanager.rrs_specific.montage.montage_interface import MontageInterface

# from .media import UAS_ShotManager_Media
from shotmanager.rendering.rendering_props import UAS_ShotManager_RenderSettings, UAS_ShotManager_RenderGlobalContext
from .shot import UAS_ShotManager_Shot
from .take import UAS_ShotManager_Take
from ..operators.shots_global_settings import UAS_ShotManager_ShotsGlobalSettings
from ..retimer.retimer_props import UAS_Retimer_Properties

from shotmanager.utils import utils

import logging

_logger = logging.getLogger(__name__)


class UAS_ShotManager_Props(MontageInterface, PropertyGroup):
    # marche pas
    # def __init__(self):
    #     self._characteristics = dict()
    #     print("\n\n */*/*/*/*/*/*/*/*/*/*/ Init shot manager !!! \n\n")

    def version(self):
        """ Return the add-on version in the form of a tupple made by: 
                - a string x.y.z (eg: "1.21.3")
                - an integer. x.y.z becomes xxyyyzzz (eg: "1.21.3" becomes 1021003)
            Return None if the addon has not been found
        """
        return utils.addonVersion("UAS Shot Manager")

    dataVersion: IntProperty(
        """ Data Version is of the form xxyyyzzz, integer generated from the string version "xx.yyy.zzz"
            Use functions convertVersionStrToInt and convertVersionIntToStr in the module utils.py to manipulate it.
        """,
        name="Data Version",
        description="Version of Shot Manager used to generate the data of the current scene.",
        default=-1,
    )

    def initialize_shot_manager(self):
        print(f"\nInitializing Shot Manager... Scene: {bpy.context.scene.name}")
        # self.parentScene = self.getParentScene()

        if self.parentScene is None:
            self.parentScene = self.findParentScene()
        # _logger.info(f"\n  self.parentScene : {self.parentScene}")

        self.initialize()
        self.dataVersion = bpy.context.window_manager.UAS_shot_manager_version
        self.createDefaultTake()
        self.createRenderSettings()
        self.isInitialized = True

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

    parentScene: PointerProperty(type=Scene)

    def findParentScene(self):
        for scn in bpy.data.scenes:
            if "UAS_shot_manager_props" in scn:
                props = scn.UAS_shot_manager_props
                if self == props:
                    #    print("findParentScene: Scene found")
                    return scn
        # print("findParentScene: Scene NOT found")
        return None

    def getParentScene(self):
        parentScn = None
        try:
            parentScn = self.parentScene
        except Exception:  # as e
            print("Error - parentScene property is None in props.getParentScene():", sys.exc_info()[0])

        # if parentScn is not None:
        #     return parentScn
        if parentScn is None:
            _logger.error("\n\n WkError: parentScn in None in Props !!! *** ")
            self.parentScene = self.findParentScene()
        else:
            self.parentScene = parentScn

        if self.parentScene is None:
            print("\n\n Re WkError: self.parentScene in still None in Props !!! *** ")
        # findParentScene is done in initialize function

        return self.parentScene

    retimer: PointerProperty(type=UAS_Retimer_Properties)

    def getWarnings(self, scene):
        """ Return an array with all the warnings
        """
        warningList = []

        # check if the current file is saved and not read only
        ###########
        currentFilePath = bpy.path.abspath(bpy.data.filepath)
        if "" == currentFilePath:
            warningList.append("Current file has to be saved")
        else:
            stat = Path(currentFilePath).stat()
            # print(f"Blender file Stats: {stat.st_mode}")
            if S_IMODE(stat.st_mode) & S_IWRITE == 0:
                warningList.append("Current file in Read-Only")

        # check if the current framerate is valid according to the project settings (wkip)
        ###########
        if self.use_project_settings:
            if scene.render.fps != self.project_fps:
                warningList.append("Current scene fps and project fps are different !!")

        # check if a negative render frame may be rendered
        ###########
        shotList = self.get_shots()
        hasNegativeFrame = False
        shotInd = 0
        while shotInd < len(shotList) and not hasNegativeFrame:
            hasNegativeFrame = shotList[shotInd].start - self.handles < 0
            shotInd += 1
        if hasNegativeFrame:
            warningList.append("Index of the output frame of a shot minus handle is negative !!")

        # check is the data version is compatible with the current version
        # wkip obsolete code due to post register data version check
        if self.dataVersion <= 0 or self.dataVersion < bpy.context.window_manager.UAS_shot_manager_version:
            # print("Warning: elf.dataVersion:", self.dataVersion)
            # print(
            #     "Warning: bpy.context.window_manager.UAS_shot_manager_version:",
            #     bpy.context.window_manager.UAS_shot_manager_version,
            # )

            warningList.append("Data version is lower than SM version !!")

        # wkip to do: check if some camera markers are used in the scene

        return warningList

    def sceneIsReady(self):
        renderWarnings = ""
        if self.renderRootPath.startswith("//"):
            if "" == bpy.data.filepath:
                renderWarnings = "*** Save file first ***"
        elif "" == self.renderRootPath:
            renderWarnings = "*** Invalid Output File Name ***"
        elif len(self.get_shots()) <= 0:
            renderWarnings = "*** No shots in the current take ***"

        if "" != renderWarnings:
            from shotmanager.utils.utils import ShowMessageBox

            utils.ShowMessageBox(renderWarnings, "Render Aborted", "ERROR")
            print("Render aborted before start: " + renderWarnings)
            return False

        return True

    def dontRefreshUI(self):
        res = not self.refreshUIDuringPlay and bpy.context.screen.is_animation_playing
        return res

    refreshUIDuringPlay: BoolProperty(
        name="Keep Refreshing UI During Play (Slower)",
        description="Refresh the information displayed in the Shot Manager UI during Shot Mode Play (slower)",
        default=True,
        options=set(),
    )

    # wkip rrs specific
    #############

    rrs_useRenderRoot: BoolProperty(name="Use Render Root", default=True)
    rrs_rerenderExistingShotVideos: BoolProperty(name="Force Re-render", default=True)
    rrs_fileListOnly: BoolProperty(name="File List Only", default=True)
    rrs_renderAlsoDisabled: BoolProperty(name="Render Also Disabled", default=False)

    # project settings
    #############

    use_project_settings: BoolProperty(name="Use Project Settings", default=False, options=set())

    # settings coming from production
    project_name: StringProperty(name="Project Name", default="My Project")
    project_fps: FloatProperty(name="Project Fps", min=0.5, max=200.0, default=25.0)
    project_resolution_x: IntProperty(name="Res. X", min=0, default=1280)
    project_resolution_y: IntProperty(name="Res. Y", min=0, default=720)
    project_resolution_framed_x: IntProperty(name="Res. Framed X", min=0, default=1280)
    project_resolution_framed_y: IntProperty(name="Res. Framed Y", min=0, default=720)
    project_shot_format: StringProperty(name="Shot Format", default=r"Act{:02}_Seq{:04}_Sh{:04}")

    project_use_shot_handles: BoolProperty(
        name="Use Handles",
        description="Use or not shot handles for the project.\nWhen not used, not reference to the handles will appear in Shot Manager user interface",
        default=True,
    )
    project_shot_handle_duration: IntProperty(
        name="Project Handles Duration",
        description="Duration of the handles used by the project, in number of frames",
        min=0,
        soft_max=50,
        default=10,
    )

    project_output_format: StringProperty(name="Output Format", default="")
    project_color_space: StringProperty(name="Color Space", default="")
    project_asset_name: StringProperty(name="Asset Name", default="")

    # built-in project settings
    project_images_output_format: StringProperty(name="Images Output Format", default="PNG")

    project_use_stampinfo: BoolProperty(
        name="Use Stamp Info Add-on",
        description="Use UAS Stamp Info add-on - if available - to write data on rendered images.\nNote: If Stamp Info is not installed then warnings will be displayed",
        default=False,
    )

    # built-in settings
    use_handles: BoolProperty(
        name="Use Handles",
        description="Use or not shot handles.\nWhen not used, not reference to the handles will appear in Shot Manager user interface",
        default=False,
    )
    handles: IntProperty(
        name="Handles Duration",
        description="Duration of the handles, in number of frames",
        default=10,
        min=0,
        options=set(),
    )

    new_shot_prefix: StringProperty(default="Sh")

    renderSingleFrameShotAsImage: BoolProperty(
        name="Render Single Frame Shot as Image",
        description="Render single frame shot as an image, not as a video",
        default=True,
    )

    # overriden by project settings
    render_shot_prefix: StringProperty(
        name="Render Shot Prefix", description="Prefix added to the shot names at render time", default=""
    )

    project_renderSingleFrameShotAsImage: BoolProperty(
        name="Project Render Single Frame Shot as Image",
        description="Render single frame shot as an image, not as a video",
        default=True,
    )

    # general
    #############

    def areShotHandlesUsed(self):
        """
            Returns the right handles use, either local or from the project.
        """
        return self.project_use_shot_handles if self.use_project_settings else self.use_handles

    def getHandlesDuration(self):
        """
            Returns the right handles duration, either local or from the project.
            Before calling this function check if the instance of Shto MAnager uses handles by calling 
        """
        handles = 0
        if self.areShotHandlesUsed():
            handles = self.project_shot_handle_duration if self.use_project_settings else self.handles
            handles = max(0, handles)
        return handles

    # playbar
    #############
    restartPlay: BoolProperty(default=False)

    # edit
    #############

    editStartFrame: IntProperty(
        name="Edit Start Frame",
        description="Index of the first frame of the edit.Default is 0.\nMost editing software start at 0, some at 1. \
            \nIt is possible to use a custom value when the current scene is not the first one of the edit in this file",
        default=0,
        options=set(),
    )

    # shots
    #############

    display_selectbut_in_shotlist: BoolProperty(
        name="Display Camera Selection Button in Shot List", default=True, options=set()
    )

    display_name_in_shotlist: BoolProperty(name="Display Name in Shot List", default=True, options=set())

    display_camera_in_shotlist: BoolProperty(name="Display Camera in Shot List", default=False, options=set())

    display_lens_in_shotlist: BoolProperty(name="Display Camera Lens in Shot List", default=False, options=set())

    display_duration_in_shotlist: BoolProperty(name="Display Shot Duration in Shot List", default=True, options=set())
    display_duration_after_time_range: BoolProperty(
        name="Display Shot Duration After Time Range", default=True, options=set()
    )

    display_color_in_shotlist: BoolProperty(name="Display Color in Shot List", default=True, options=set())

    display_enabled_in_shotlist: BoolProperty(name="Display Enabled State in Shot List", default=True, options=set())

    display_cameraBG_in_shotlist: BoolProperty(name="Display Camera BG in Shot List", default=False, options=set())
    display_greasepencil_in_shotlist: BoolProperty(
        name="Display Grease Pencil in Shot List", default=False, options=set()
    )

    display_getsetcurrentframe_in_shotlist: BoolProperty(
        name="Display Get/Set current Frame Buttons in Shot List", default=True, options=set()
    )

    display_edit_times_in_shotlist: BoolProperty(
        name="Display Edit Times in Shot List",
        description="Display start and end frames of the shots in the time of the edit",
        default=False,
        options=set(),
    )

    def _update_display_shotname_in_3dviewport(self, context):
        # print("\n*** Stamp Info updated. New state: ", self.stampInfoUsed)
        if self.display_shotname_in_3dviewport:
            bpy.ops.uas_shot_manager.draw_cameras_ui("INVOKE_DEFAULT")

    display_shotname_in_3dviewport: BoolProperty(
        name="Display Shot name in 3D Viewports",
        description="Display the name of the shots near the camera object or frame in the 3D viewport",
        default=True,
        update=_update_display_shotname_in_3dviewport,
        options=set(),
    )

    def _update_display_hud_in_3dviewport(self, context):
        # print("\n*** Stamp Info updated. New state: ", self.stampInfoUsed)
        if self.display_shotname_in_3dviewport:
            bpy.ops.uas_shot_manager.draw_hud("INVOKE_DEFAULT")

    display_hud_in_3dviewport: BoolProperty(
        name="Display HUD in 3D Viewports",
        description="Display global infos in the 3D viewport",
        default=True,
        update=_update_display_hud_in_3dviewport,
        options=set(),
    )

    # Features
    #############

    display_camerabgtools_in_properties: BoolProperty(
        name="Display Camera Background Image Tools in Shot Properties",
        description="Display the Camera Background Image Tools in the shot properties panels",
        default=False,
        options=set(),
    )

    display_notes_in_properties: BoolProperty(
        name="Display Shot Notes in Shot Properties",
        description="Display shot notes in the shot properties panels",
        default=False,
        options=set(),
    )

    display_greasepencil_in_properties: BoolProperty(
        name="Display Grease Pencil in Shot Properties",
        description="Display grease pencil in the shot properties panels",
        default=False,
        options=set(),
    )

    display_retimer_in_properties: BoolProperty(
        name="Display Retimer sub-Panel",
        description="Display Retimer sub-panel in the Shot Manager panel",
        default=True,
        options=set(),
    )

    display_notes_in_shotlist: BoolProperty(name="Display Color in Shot List", default=True, options=set())

    display_advanced_infos: BoolProperty(
        name="Display Advanced Infos",
        description="Display technical information and feedback in the UI",
        default=False,
        options=set(),
    )

    def _get_useLockCameraView(self):
        # Can also use area.spaces.active to get the space assoc. with the area
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        realVal = space.lock_camera

        # not used, normal it's the fake property
        self.get("useLockCameraView", realVal)

        return realVal

    def _set_useLockCameraView(self, value):
        self["useLockCameraView"] = value
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.lock_camera = value

    # fake property: value never used in itself, its purpose is to update ofher properties
    useLockCameraView: BoolProperty(
        name="Lock Cameras to View",
        description="Enable view navigation within the camera view",
        get=_get_useLockCameraView,
        set=_set_useLockCameraView,
        # update=_update_useLockCameraView,
        options=set(),
    )

    # shots global settings
    #############

    shotsGlobalSettings: PointerProperty(type=UAS_ShotManager_ShotsGlobalSettings)

    # prefs
    #############

    use_camera_color: BoolProperty(
        name="Use Camera Color",
        description="If True the color used by a shot is based on the color of its camera (default).\n"
        "Othewise the shot uses its own color",
        default=True,
        options=set(),
    )

    # bgImages_Alpha: FloatProperty(
    #     name="BG Image Alpha",
    #     description="Opacity of the camera background images",
    #     min=0.0,
    #     max=1.0,
    #     default=0.9,
    #     options=set(),
    # )

    # shots list
    #############

    current_shot_index: IntProperty(default=-1)

    selected_shot_index: IntProperty(name="Shot Name", default=-1)

    current_shot_properties_mode: bpy.props.EnumProperty(
        name="Display Shot Properties Mode",
        description="Update the content of the Shot Properties panel either on the current shot\nor on the shot seleted in the shots list",
        items=(("CURRENT", "Current Shot", ""), ("SELECTED", "Selected Shot", "")),
        default="SELECTED",
        options=set(),
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

    def _get_playSpeedGlobal(self):
        val = self.get("playSpeedGlobal", 1.0)
        val = 100.0 / bpy.context.scene.render.fps_base
        return val

    def _set_playSpeedGlobal(self, value):
        self["playSpeedGlobal"] = value

    def _update_playSpeedGlobal(self, context):
        bpy.context.scene.render.fps_base = 100.0 / self["playSpeedGlobal"]

    playSpeedGlobal: FloatProperty(
        name="Play Speed",
        description="Change the global play speed of the scene",
        subtype="PERCENTAGE",
        soft_min=10,
        soft_max=200,
        precision=0,
        get=_get_playSpeedGlobal,
        set=_set_playSpeedGlobal,
        update=_update_playSpeedGlobal,
        default=100.0,
        options=set(),
    )

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

    def _update_current_take_name(self, context):
        # print(f"_update_current_take_name: {self.getCurrentTakeIndex()}, {self.getCurrentTakeName()}")
        self.setCurrentShotByIndex(0)
        self.setSelectedShotByIndex(0)

    current_take_name: EnumProperty(
        name="Takes", description="Select a take", items=_list_takes, update=_update_current_take_name,
    )

    takes: CollectionProperty(type=UAS_ShotManager_Take)

    ####################
    # takes
    ####################

    # wkip deprecated
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

    def getNumTakes(self):
        return len(self.takes)

    def getTakeByIndex(self, takeIndex):
        """ Return the take corresponding to the specified index
        """
        takeInd = self.getCurrentTakeIndex() if -1 == takeIndex else (takeIndex if 0 < len(self.getTakes()) else -1)
        take = None
        if -1 == takeInd:
            return take
        return self.takes[takeInd]

    def getTakeByName(self, takeName):
        """ Return the first take with the specified name, None if not found
        """
        for t in self.takes:
            if t.name == takeName:
                return t
        return None

    def getTakeIndex(self, take):
        takeInd = -1

        if 0 < len(self.takes):
            takeInd = 0
            while takeInd < len(self.takes) and self.takes[takeInd] != take:
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1

        return takeInd

    def getTakeIndexByName(self, takeName):
        """ Return the index of the first take with the specified name, -1 if not found
        """
        if len(self.takes):
            for i in range(0, len(self.takes) + 1):
                if self.takes[i].name == takeName:
                    return i
        return -1

    def getCurrentTakeIndex(self):
        takeInd = -1
        if 0 < len(self.takes):
            takeInd = 0
            #      print(" self.takes[0]: " + str(self.takes[takeInd].name) + ", type: " + str(type(self.takes[takeInd])) )
            #     print(" self.current_take_name: " + str(self.current_take_name) + ", type: " + str(type(self.current_take_name)) )
            while takeInd < len(self.takes) and self.takes[takeInd].name != self.current_take_name:
                takeInd += 1
            if takeInd >= len(self.takes):
                takeInd = -1
        #    self.current_take_name = self.takes[takeInd].name

        return takeInd

    def setCurrentTakeByIndex(self, currentTakeIndex):
        currentTakeInd = min(currentTakeIndex, len(self.takes) - 1)
        if -1 < currentTakeInd:
            self.current_take_name = self.takes[currentTakeInd].name
            # already in current_take_name._update
            # self.setCurrentShotByIndex(0)
            # self.setSelectedShotByIndex(0)
        else:
            self.current_take_name = ""

        # print(f" ---- currentTakeByIndex: {currentTakeInd}, {self.getTakeByIndex(currentTakeInd)}")

    def getCurrentTake(self):
        currentTakeInd = self.getCurrentTakeIndex()
        if -1 == currentTakeInd:
            return None
        return self.getTakes()[currentTakeInd]

    def getCurrentTakeName(self):
        """ Return the name of the current take, 
        """
        #    print("getCurrentTakeName")
        #    currentTakeInd = self.getCurrentTakeIndex()
        #    if -1 == currentTakeInd: return None
        #    return (self.getTakes()[currentTakeInd].name)
        currentTakeName = self.current_take_name
        return currentTakeName

    # wkip deprecated
    def getTakeName_PathCompliant(self, takeIndex=-1):
        """ Return the name of the specified take with spaces replaced by "_"
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        takeName = ""
        if -1 == takeInd:
            return takeName

        takeName = self.takes[takeInd].getName_PathCompliant()

        return takeName

    def createDefaultTake(self):
        takes = self.getTakes()
        defaultTake = None
        if 0 >= len(takes):
            defaultTake = takes.add()
            defaultTake.getParentScene()
            defaultTake.name = "Main Take"
            self.setCurrentTakeByIndex(0)
            # self.setCurrentShotByIndex(-1)
            # self.setSelectedShotByIndex(-1)

        else:
            defaultTake = takes[0]
        return defaultTake

    def addTake(self, atIndex=-1, name="New Take"):
        """ Add a new take after the current take if possible or at the end of the take list otherwise
            Return the newly added take
        """
        takes = self.getTakes()
        newTake = None
        if len(takes) <= 0:
            newTake = self.createDefaultTake()
        else:
            newTakeName = self.getUniqueTakeName(name)

            #######
            # important note: newTake points to the slot in takes array, not to the take itself
            newTake = takes.add()
            newTake.parentScene = self.getParentScene()
            newTake.name = "" + newTakeName

        # self.current_take_name = newTake.name
        # print(f"new added take name: {newTake.name}")

        # move take at specified index
        # !!! warning: newTake has to be updated !!!
        if -1 != atIndex:
            atValidIndex = max(atIndex, 0)
            atValidIndex = min(atValidIndex, len(takes) - 1)
            takes.move(len(takes) - 1, atValidIndex)
            newTake = takes[atValidIndex]

        # after a move newTake is different!
        # print(f"new added take name02: {newTake.name}")

        return newTake

    def copyTake(self, take, atIndex=-1, copyCamera=False, ignoreDisabled=False):
        """ Copy a take after the current take if possible or at the end of the takes list otherwise
            Return the newly added take
        """

        def _copyString(str1):
            resStr = ""
            for c in str1:
                resStr += c
            return resStr

        newTake = self.addTake(atIndex=atIndex, name=take.name + "_copy")
        newTake.note01 = _copyString(take.note01)
        newTake.note02 = _copyString(take.note02)
        newTake.note03 = _copyString(take.note03)
        newTake.showNotes = take.showNotes

        newTakeInd = self.getTakeIndex(newTake)

        shots = take.getShotsList(ignoreDisabled=ignoreDisabled)
        for shot in shots:
            self.copyShot(shot, targetTakeIndex=newTakeInd, copyCamera=copyCamera)

        return newTake

    def moveTakeToIndex(self, take, newIndex, setAsMainTake=False):
        """Return the new take index if the move is done, -1 otherwise"""
        if take is None:
            return -1

        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = self.getTakeIndex(take)
        newInd = max(0, newIndex)
        newInd = min(newInd, len(self.takes) - 1)

        # Main Take cannot be moved by design
        if not setAsMainTake:
            if 0 == currentTakeInd or 0 == newInd:
                return -1

        self.takes.move(takeInd, newInd)
        self.setCurrentTakeByIndex(newInd)

        return newInd

    # render
    #############

    # can be overriden by the project settings
    # use ProjectRenderSettings: BoolProperty(
    #     name="Use Render Project Settings", description="Use Render Project Settings", default=True,
    # )

    def get_useStampInfoDuringRendering(self):
        #  return self.useStampInfoDuringRendering
        val = self.get("useStampInfoDuringRendering", True)
        # print("*** get_useStampInfoDuringRendering: value: ", val)
        return val

    def set_useStampInfoDuringRendering(self, value):
        print("*** set_useStampInfoDuringRendering: value: ", value)
        self["useStampInfoDuringRendering"] = value

        if getattr(bpy.context.scene, "UAS_StampInfo_Settings", None) is not None:
            # bpy.context.scene.UAS_StampInfo_Settings.activateStampInfo(value)
            bpy.context.scene.UAS_StampInfo_Settings.stampInfoUsed = value

    # def useStampInfoDuringRendering_StateChanged(self, context):
    #     print("\n*** useStampInfoDuringRendering updated. New state: ", self.useStampInfoDuringRendering)

    useStampInfoDuringRendering: BoolProperty(
        name="Stamp Info on Output",
        description="Stamp render information on rendered images thanks to Stamp Info add-on",
        default=True,
        get=get_useStampInfoDuringRendering,  # removed cause the use of Stamp Info in this add-on is independent from the one of Stamp Info add-on itself
        set=set_useStampInfoDuringRendering,
        # update = useStampInfoDuringRendering_StateChanged,
        options=set(),
    )

    ############
    # render properties for UI

    renderRootPath: StringProperty(
        name="Render Root Path",
        description="Directory where the rendered files will be placed.\n"
        "Relative path must be set directly in the text field and must start with ''//''",
        default="//",
    )

    def isRenderRootPathValid(self, renderRootFilePath=None):
        pathIsValid = False

        rootPath = self.renderRootPath if renderRootFilePath is None else renderRootFilePath
        if "" != rootPath:
            if os.path.exists(rootPath) or rootPath.startswith("//"):
                pathIsValid = True
        return pathIsValid

    def isStampInfoAvailable(self):
        """Return True if the add-on UAS Stamp Info is available, registred and ready to be used
        """
        readyToUse = getattr(bpy.context.scene, "UAS_StampInfo_Settings", None) is not None
        return readyToUse

    def isStampInfoAllowed(self):
        """Return True if the add-on UAS Stamp Info is available and allowed to be used
        """
        allowed = self.isStampInfoAvailable()
        # wkip temp while fixing stamp info...
        allowed = allowed and False
        return allowed

    def stampInfoUsed(self):
        """Return True if the add-on UAS Stamp Info is available and allowed to be used and checked for use,
        either from the UI or by the project settings
        """
        used = False
        if self.use_project_settings:
            used = self.project_use_stampinfo
        else:
            used = False  # self.useProjectRenderSettings

        used = used and self.isStampInfoAvailable()

        return used

    def addRenderSettings(self):
        newRenderSettings = self.renderSettingsList.add()
        return newRenderSettings

    renderContext: PointerProperty(type=UAS_ShotManager_RenderGlobalContext)

    # renderSettingsStill: CollectionProperty (
    #   type = UAS_ShotManager_RenderSettings )
    renderSettingsStill: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsAnim: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsAll: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsOtio: PointerProperty(type=UAS_ShotManager_RenderSettings)

    renderSettingsPlayblast: PointerProperty(type=UAS_ShotManager_RenderSettings)

    def get_displayStillProps(self):
        val = self.get("displayStillProps", True)
        return val

    def set_displayStillProps(self, value):
        print(" set_displayStillProps: value: ", value)
        self["displayStillProps"] = True
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayAnimationProps(self):
        val = self.get("displayAnimationProps", False)
        return val

    def set_displayAnimationProps(self, value):
        self["displayStillProps"] = False
        self["displayAnimationProps"] = True
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayProjectProps(self):
        val = self.get("displayAllEditsProps", False)
        return val

    def set_displayProjectProps(self, value):
        print(" set_displayProjectProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = True
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = False

    def get_displayOtioProps(self):
        val = self.get("displayOtioProps", False)
        return val

    def set_displayOtioProps(self, value):
        # print(" set_displayOtioProps: value: ", value)
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = True
        self["displayPlayblastProps"] = False

    def get_displayPlayblastProps(self):
        val = self.get("displayPlayblastProps", False)
        return val

    def set_displayPlayblastProps(self, value):
        _logger.debug(f" set_displayPlayblastProps: value: {value}")
        self["displayStillProps"] = False
        self["displayAnimationProps"] = False
        self["displayAllEditsProps"] = False
        self["displayOtioProps"] = False
        self["displayPlayblastProps"] = True

    displayStillProps: BoolProperty(
        name="Display Still Preset Properties", get=get_displayStillProps, set=set_displayStillProps, default=True
    )
    displayAnimationProps: BoolProperty(
        name="Display Animation Preset Properties",
        get=get_displayAnimationProps,
        set=set_displayAnimationProps,
        default=False,
    )
    displayAllEditsProps: BoolProperty(
        name="Display Project Preset Properties",
        get=get_displayProjectProps,
        set=set_displayProjectProps,
        default=False,
    )
    displayOtioProps: BoolProperty(
        name="Display OpenTimelineIO Export Preset Properties",
        get=get_displayOtioProps,
        set=set_displayOtioProps,
        default=False,
    )
    displayPlayblastProps: BoolProperty(
        name="Display Playblast Preset Properties",
        get=get_displayPlayblastProps,
        set=set_displayPlayblastProps,
        default=False,
    )

    ####################
    # editing
    ####################

    def getEditDuration(self, ignoreDisabled=True, takeIndex=-1):
        """ Return edit duration in frames
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        duration = -1
        if -1 == takeInd:
            return -1

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        if 0 < len(shotList):
            duration = 0
            for sh in shotList:
                duration += sh.getDuration()

        return duration

    def getEditTime(self, referenceShot, frameIndexIn3DTime, referenceLevel="TAKE"):
        """ Return edit current time in frames, -1 if no shots or if current shot is disabled
            Works on the take from which referenceShot is coming from.
            Disabled shots are always ignored and considered as not belonging to the edit.
            wkip negative times issues coming here... :/
            referenceLevel can be "TAKE" or "GLOBAL_EDIT"
        """
        frameIndInEdit = -1
        if referenceShot is None:
            return frameIndInEdit

        takeInd = referenceShot.getParentTakeIndex()
        ignoreDisabled = True

        # case where specified shot is disabled -- current shot may not be in the shot list if shotList is not the whole list
        if ignoreDisabled and not referenceShot.enabled:
            return -1

        # specified time must be in the range of the specifed shot!!!
        # get the whole shots list
        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)

        if 0 < len(shotList):
            if referenceShot.start <= frameIndexIn3DTime and frameIndexIn3DTime <= referenceShot.end:
                frameIndInEdit = 0
                shotInd = 0
                while shotInd < len(shotList) and referenceShot != shotList[shotInd]:
                    #         print("    While: shotInd: " + str(shotInd) + ", referenceShot: " + str(referenceShot) + ", shotList[shotInd]: " + str(shots[shotInd]))
                    #         print("    frameIndInEdit: ", frameIndInEdit)
                    if not ignoreDisabled or shotList[shotInd].enabled:
                        frameIndInEdit += shotList[shotInd].getDuration()
                    shotInd += 1

                frameIndInEdit += frameIndexIn3DTime - referenceShot.start

                if "GLOBAL_EDIT" == referenceLevel:
                    frameIndInEdit += referenceShot.getParentTake().startInGlobalEdit
                else:
                    # at take level
                    frameIndInEdit += self.editStartFrame  # at project level

        return frameIndInEdit

    def getEditCurrentTime(self, referenceLevel="TAKE", ignoreDisabled=True):
        """ Return edit current time in frames, -1 if no shots or if current shot is disabled
            works only on current take
            wkip negative times issues coming here... :/
        """
        # print(f"_update_current_take_name: {self.getCurrentTakeIndex()}, {self.getCurrentTakeName()}")
        # works only on current take
        takeInd = self.getCurrentTakeIndex()
        editCurrentTime = -1
        if -1 == takeInd:
            return editCurrentTime

        # current time must be in the range of the current shot!!!
        # get the whole shots list
        #        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)
        shot = self.getCurrentShot()

        return self.getEditTime(shot, bpy.context.scene.frame_current, referenceLevel=referenceLevel)

        # # works only on current take
        # takeInd = self.getCurrentTakeIndex()
        # editCurrentTime = -1
        # if -1 == takeInd:
        #     return editCurrentTime

        # # current time must be in the range of the current shot!!!
        # # get the whole shots list
        # shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeInd)

        # if 0 < len(shotList):
        #     # case where current shot is disabled -- current shot may not be in the shot list if shotList is not the whole list
        #     currentShot = self.getCurrentShot()

        #     if currentShot is not None:
        #         currentTime = bpy.context.scene.frame_current

        #         if currentShot.enabled and currentShot.start <= currentTime and currentTime <= currentShot.end:
        #             editCurrentTime = 0
        #             shotInd = 0
        #             while shotInd < len(shotList) and currentShot != shotList[shotInd]:
        #                 #         print("    While: shotInd: " + str(shotInd) + ", currentShot: " + str(currentShot) + ", shotList[shotInd]: " + str(shots[shotInd]))
        #                 #         print("    editCurrentTime: ", editCurrentTime)
        #                 if not ignoreDisabled or shotList[shotInd].enabled:
        #                     editCurrentTime += shotList[shotInd].getDuration()
        #                 shotInd += 1

        #             editCurrentTime += currentTime - currentShot.start
        #         # if shotInd == len(shotList): editCurrentTime = -1

        # return editCurrentTime

    def getEditCurrentTimeForSelectedShot(self, referenceLevel="TAKE", ignoreDisabled=True):
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
        #        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeInd)
        shot = self.getSelectedShot()

        return self.getEditTime(shot, bpy.context.scene.frame_current, referenceLevel=referenceLevel)

    def getEditShots(self, ignoreDisabled=True):
        return self.getShotsList(ignoreDisabled=ignoreDisabled)

    ####################
    # shots
    ####################

    def getUniqueShotName(self, nameToMakeUnique, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        uniqueName = nameToMakeUnique
        if -1 == takeInd:
            return uniqueName

        shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeIndex)

        dup_name = False
        for shot in shotList:
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
        durationLocked=False,
        camera=None,
        color=(0.2, 0.6, 0.8, 1),
        enabled=True,
    ):
        """ Add a new shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
            that is not the current one)
            Return the newly added shot
            Since this function works also with takes that are not the current one the current shot is not taken into account not modified
        """

        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = (
            currentTakeInd
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            print("AddShot: Failed")
            return None

        newShot = None
        shots = self.get_shots(takeIndex=takeInd)

        newShot = shots.add()  # shot is added at the end
        newShot.parentScene = self.getParentScene()
        # newShot.parentTakeIndex = takeInd
        newShot.initialize(self.getTakeByIndex(currentTakeInd))
        newShot.name = name
        newShot.enabled = enabled
        newShot.end = 9999999  # mandatory cause start is clamped by end
        newShot.start = start
        newShot.end = end
        newShot.durationLocked = durationLocked
        newShot.camera = camera
        newShot.color = color

        # move shot at specified index
        # !!! warning: newShot has to be updated !!!
        newShotInd = len(shots) - 1
        if -1 != atIndex:
            atValidIndex = max(atIndex, 0)
            atValidIndex = min(atValidIndex, len(shots) - 1)
            shots.move(len(shots) - 1, atValidIndex)
            newShot = shots[atValidIndex]
            newShotInd = atValidIndex

        # update the current take if needed
        if takeInd == currentTakeInd:
            self.setCurrentShotByIndex(newShotInd)
            self.setSelectedShotByIndex(newShotInd)

        # warning: by reordering the shots it looks like newShot is not pointing anymore on the new shot
        # we then get it again
        # newShot = self.getShotByIndex(newShotInd)

        return newShot

    def copyShot(self, shot, atIndex=-1, targetTakeIndex=-1, copyCamera=False):
        """ Copy a shot after the current shot if possible or at the end of the shot list otherwise (case of an add in a take
            that is not the current one)
            Return the newly added shot
            Since this function works also with takes that are not the current one the current shot is not taken into account not modified
            Specifying a value to targetTakeIndex allows the copy of a shot to another take
            When a shot is copied in the same take its name will be suffixed by "_copy". When copied to another take its name is not modified.
        """

        #  currentTakeInd = self.getCurrentTakeIndex()
        sourceTakeInd = shot.getParentTakeIndex()
        takeInd = (
            sourceTakeInd
            if -1 == targetTakeIndex
            else (targetTakeIndex if 0 <= targetTakeIndex and targetTakeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return None

        # newShot = None
        # shots = self.get_shots(takeIndex=takeInd)

        cam = shot.camera
        if copyCamera and shot.camera is not None:
            newCam = utils.duplicateObject(cam)
            if targetTakeIndex == sourceTakeInd:
                newCam.name = cam.name + "_copy"
            newCam.color = utils.sRGBColor(utils.slightlyRandomizeColor(utils.linearizeColor(cam.color)))
            cam = newCam

        nameSuffix = ""
        if targetTakeIndex == sourceTakeInd:
            nameSuffix = "_copy"

        newShot = self.addShot(
            atIndex=atIndex,
            takeIndex=targetTakeIndex,
            name=shot.name + nameSuffix,
            start=shot.start,
            end=shot.end,
            durationLocked=shot.durationLocked,
            camera=cam,
            color=cam.color,
            enabled=shot.enabled,
        )

        newShot.bgImages_offset = shot.bgImages_offset
        newShot.bgImages_linkToShotStart = shot.bgImages_linkToShotStart

        newShot.note01 = shot.note01
        newShot.note03 = shot.note02
        newShot.note03 = shot.note03

        # newShot = shots.add()  # shot is added at the end
        # newShot.parentScene = shot.parentScene
        # newShot.parentTakeIndex = takeInd
        # newShot.name = shot.name
        # newShot.enabled = shot.enabled
        # newShot.end = 9999999  # mandatory cause start is clamped by end
        # newShot.start = shot.start
        # newShot.end = shot.end
        # newShot.camera = shot.camera
        # newShot.color = shot.color

        # newShotInd = len(shots) - 1
        # if -1 != atIndex:  # move shot at specified index
        #     shots.move(newShotInd, atIndex)
        #     newShotInd = self.getShotIndex(newShot)

        # update the current take if needed
        # if takeInd == currentTakeInd:
        #     self.setCurrentShotByIndex(newShotInd)
        #     self.setSelectedShotByIndex(newShotInd)

        return newShot

    def removeShot(self, shot):
        currentTakeInd = self.getCurrentTakeIndex()
        takeInd = shot.getParentTakeIndex()
        shots = self.get_shots(takeIndex=takeInd)
        shotInd = self.getShotIndex(shot)

        # update the current take if needed
        if takeInd == currentTakeInd:
            print(f"Ici: takeInd == currentTakeInd : {currentTakeInd}, shotInd: {shotInd}")
            currentShotInd = self.current_shot_index
            #   currentShot = shots[currentShotInd]
            selectedShotInd = self.getSelectedShotIndex()
            previousSelectedShotInd = selectedShotInd
            #   selectedShot = shots[selectedShotInd]

            print(f"selectedShotInd 1 : {selectedShotInd}")
            if shotInd != selectedShotInd:
                self.setSelectedShotByIndex(shotInd)
                selectedShotInd = self.getSelectedShotIndex()
            print(f"selectedShotInd 2 : {selectedShotInd}")

            # case of the last shot
            if selectedShotInd == len(shots) - 1:
                if currentShotInd == selectedShotInd:
                    self.setCurrentShotByIndex(selectedShotInd - 1)

                shots.remove(selectedShotInd)
                self.setSelectedShotByIndex(selectedShotInd - 1)
            else:
                if currentShotInd >= selectedShotInd:
                    self.setCurrentShotByIndex(-1)
                shots.remove(selectedShotInd)

                if currentShotInd == selectedShotInd:
                    self.setCurrentShotByIndex(self.selected_shot_index)
                elif currentShotInd > selectedShotInd:
                    self.setCurrentShotByIndex(min(currentShotInd - 1, len(shots) - 1))

                if selectedShotInd < len(shots):
                    self.setSelectedShotByIndex(selectedShotInd)
                else:
                    self.setSelectedShotByIndex(selectedShotInd - 1)

            # restore selected item
            if shotInd != previousSelectedShotInd:
                if shotInd < previousSelectedShotInd:
                    self.setSelectedShotByIndex(previousSelectedShotInd - 1)
                else:
                    self.setSelectedShotByIndex(previousSelectedShotInd)
        else:
            print(f"La: takeInd: {takeInd}, currentTakeInd: {currentTakeInd}, shot Ind: {shotInd}")
            shots.remove(shotInd)

    def moveShotToIndex(self, shot, newIndex):
        """
            Move a shot to the specified index. The shot stays in the same take.
            Return the shot moved at the specified place.
            Once moved, the variable "shot" doesn't refer to the same shot anymore, hence:
                *** it is VERY IMPORTANT to get the returned shot back ***
        """
        # currentTakeInd = self.getCurrentTakeIndex()
        # takeInd = (
        #     currentTakeInd
        #     if -1 == takeIndex
        #     else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        # )
        # if -1 == takeInd:
        #     print("moveShotToIndex: Failed")
        #     return None

        if shot is None:
            return None

        takeInd = shot.getParentTakeIndex()
        shots = self.get_shots(takeIndex=takeInd)
        currentShotInd = self.getCurrentShotIndex()
        # selectedShotInd = self.getSelectedShotIndex()
        shotInd = self.getShotIndex(shot)
        newInd = max(0, newIndex)
        newInd = min(newInd, len(shots) - 1)

        shots.move(shotInd, newInd)

        # wkipwkipwkip test if shot and current shot are from the same take!!
        # if currentShotInd == shotInd:
        #     self.setCurrentShotByIndex(newInd)
        # self.setSelectedShotByIndex(newInd)

        return self.getShotByIndex(newInd, takeIndex=takeInd)

    def getShotParentTakeIndex(self, shot):
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return i
        return None

    def getShotParentTake(self, shot):
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return take
        return -1

    def getShotIndex(self, shot):
        """Return the shot index in its parent take
        """
        # takeInd = shot.getParentTakeIndex()
        # shotInd = -1

        # # wkip a optimiser
        # shotList = self.getShotsList(ignoreDisabled=False, takeIndex=takeInd)

        # shotInd = 0
        # while shotInd < len(shotList) and shot != shotList[shotInd]:  # wkip mettre shotList[shotInd].name?
        #     shotInd += 1
        # if shotInd == len(shotList):
        #     shotInd = -1

        # return shotInd
        for i, take in enumerate(self.takes):
            for j, sh in enumerate(take.shots):
                if sh == shot:
                    return j
        return -1

    def getShotByIndex(self, shotIndex, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shot = None
        if -1 == takeInd:
            return None

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        # if ignoreDisabled:
        #     if 0 < len(shotList) and shotIndex < len(shotList):
        #         shot = shotList[shotIndex]
        # else if 0 < shotNumber and shotIndex < shotNumber:
        #     shot = self.takes[takeIndex].shots[shotIndex]

        if 0 < len(shotList) and shotIndex < len(shotList):
            shot = shotList[shotIndex]

        return shot

    def getShotByName(self, shotName, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shot = None
        if -1 == takeInd:
            return None

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)

        for sh in shotList:
            if shotName == sh.name:
                return sh

        return shot

    def get_shots(self, takeIndex=-1):
        """ Return the actual shots array of the specified take
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        shotList = self.takes[takeInd].shots

        return shotList

    def getShotsList(self, ignoreDisabled=False, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        # for shot in self.takes[takeInd].shots:
        #     # if shot.enabled or self.context.scene.UAS_shot_manager_props.display_disabledshots_in_timeline:
        #     if not ignoreDisabled or shot.enabled:
        #         shotList.append(shot)

        return self.takes[takeInd].getShotsList(ignoreDisabled=ignoreDisabled)

    def getNumShots(self, ignoreDisabled=False, takeIndex=-1):
        """ Return the number of shots of the specified take
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return 0

        return self.takes[takeInd].getNumShots(ignoreDisabled=ignoreDisabled)

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

        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
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
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        currentShotInd = -1
        if -1 == takeInd:
            return currentShotInd

        currentShotInd = self.getCurrentShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print("getCurrentShot: currentShotInd: ", currentShotInd)
        currentShot = None
        if -1 != currentShotInd:
            currentShot = self.takes[takeInd].shots[currentShotInd]

        return currentShot

    def setCurrentShotByIndex(self, currentShotIndex, changeTime=None, area=None):
        """ Changing the current shot doesn't affect the selected one
        """
        scene = bpy.context.scene
        area = area if area is not None else bpy.context.area

        shotList = self.get_shots()
        self.current_shot_index = currentShotIndex

        if -1 < currentShotIndex and len(shotList) > currentShotIndex:
            prefs = bpy.context.preferences.addons["shotmanager"].preferences
            currentShot = shotList[currentShotIndex]

            if changeTime is None:
                if prefs.current_shot_changes_current_time:
                    scene.frame_current = currentShot.start
            elif changeTime:
                scene.frame_current = currentShot.start

            if prefs.current_shot_changes_time_range and scene.use_preview_range:
                bpy.ops.uas_shot_manager.scenerangefromshot()

            if currentShot.camera is not None and bpy.context.screen is not None:
                # set the current camera in the 3D view: [‘PERSP’, ‘ORTHO’, ‘CAMERA’]
                scene.camera = currentShot.camera
                utils.setCurrentCameraToViewport(bpy.context, area)
                # area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")

                # area.spaces[0].use_local_camera = False
                # area.spaces[0].region_3d.view_perspective = "CAMERA"

            # wkip use if
            # if prefs.toggleCamsSoundBG:
            # self.enableBGSoundForShot(prefs.toggleCamsSoundBG, currentShot)
            if self.useBGSounds:
                self.enableBGSoundForShot(True, currentShot)

        # bpy.context.scene.objects["Camera_Sapin"]

    def setCurrentShot(self, currentShot, changeTime=None, area=None):
        shotInd = self.getShotIndex(currentShot)
        # print("setCurrentShot: shotInd:", shotInd)
        self.setCurrentShotByIndex(shotInd, changeTime=changeTime, area=area)

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
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        firstShotInd = -1
        if -1 == takeInd:
            return firstShotInd

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        #   print(" getFirstShotIndex: shotList: ", shotList)

        #  not required cause shotList is already filtered!
        # if ignoreDisabled and 0 < len(shotList):
        #     firstShotInd = 0
        #     while firstShotInd < len(shotList) and not shotList[firstShotInd].enabled:
        #         firstShotInd += 1
        #     if firstShotInd >= len(shotList): firstShotInd = 0
        # else:
        if 0 < len(shotList):
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
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        lastShotInd = -1
        if -1 == takeInd:
            return lastShotInd

        shotList = self.getShotsList(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        print(" getLastShotIndex: shotList: ", shotList)

        if 0 < len(shotList):
            lastShotInd = len(shotList) - 1

        return lastShotInd

    def getFirstShot(self, ignoreDisabled=False, takeIndex=-1):
        firstShotInd = self.getFirstShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        # print(" getFirstShot: firstShotInd: ", firstShotInd)
        firstShot = (
            None
            if -1 == firstShotInd
            else self.getShotByIndex(firstShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return firstShot

    def getLastShot(self, ignoreDisabled=False, takeIndex=-1):
        lastShotInd = self.getLastShotIndex(ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        print(" getLastShot: lastShotInd: ", lastShotInd)
        lastShot = (
            None
            if -1 == lastShotInd
            else self.getShotByIndex(lastShotInd, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex)
        )

        return lastShot

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the previous enabled shot in the WHOLE list, -1 if none
    def getPreviousEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        previousShotInd = -1
        if -1 == takeInd:
            return previousShotInd

        shotList = self.getShotsList(takeIndex=takeIndex)

        previousShotInd = currentShotIndex - 1
        isPreviousFound = shotList[previousShotInd].enabled
        while 0 <= previousShotInd and not isPreviousFound:
            previousShotInd -= 1
            isPreviousFound = shotList[previousShotInd].enabled

        return previousShotInd

    # currentShotIndex is given in the WHOLE list of shots (including disabled)
    # returns the index of the next enabled shot in the WHOLE list, -1 if none
    def getNextEnabledShotIndex(self, currentShotIndex, takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        nextShotInd = -1
        if -1 == takeInd:
            return nextShotInd

        shotList = self.getShotsList(takeIndex=takeIndex)

        nextShotInd = currentShotIndex + 1
        if len(shotList) > nextShotInd:
            isNextFound = shotList[nextShotInd].enabled
            while len(shotList) > nextShotInd and not isNextFound:
                nextShotInd += 1
                if len(shotList) > nextShotInd:
                    isNextFound = shotList[nextShotInd].enabled

        if len(shotList) <= nextShotInd:
            nextShotInd = -1

        return nextShotInd

    def getShotsUsingCamera(self, cam, ignoreDisabled=False, takeIndex=-1):
        """ Return the list of all the shots used by the specified camera in the specified take
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        shotList = []
        if -1 == takeInd:
            return shotList

        return self.takes[takeInd].getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)

    def getShotsSharingCamera(self, cam, ignoreDisabled=False, takeIndex=-1, inAllTakes=True):
        """ Return a dictionary with all the shots using the specified camera in the specified takes
            The dictionary is made of "take name" / Shots array
        """
        shotsDict = dict()

        if cam is None:
            return shotsDict

        if not inAllTakes:
            takeInd = (
                self.getCurrentTakeIndex()
                if -1 == takeIndex
                else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
            )
            if -1 == takeInd:
                return shotsDict

            shotList = self.takes[takeInd].getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)
            if len(shotList):
                shotsDict[self.takes[takeInd].getName_PathCompliant()] = shotList

        else:
            if len(self.takes):
                for take in self.takes:
                    shotList = []
                    shotList = take.getShotsUsingCamera(cam, ignoreDisabled=ignoreDisabled)
                    if len(shotList):
                        shotsDict[take.getName_PathCompliant()] = shotList

        return shotsDict

    def getNumSharedCamera(self, cam, ignoreDisabled=False, takeIndex=-1, inAllTakes=True):
        """ Return the number of times the specified camera is used by the shots of the specified takes
            0 means the camera is not used at all, -1 that the specified take is not valid
        """
        if not inAllTakes:
            takeInd = (
                self.getCurrentTakeIndex()
                if -1 == takeIndex
                else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
            )
            if -1 == takeInd:
                return -1

        sharedCams = self.getShotsSharingCamera(
            cam, ignoreDisabled=ignoreDisabled, takeIndex=takeIndex, inAllTakes=inAllTakes
        )
        numSharedCams = 0
        for k in sharedCams:
            numSharedCams += len(sharedCams[k])

        return numSharedCams

    def deleteShotCamera(self, shot):
        """ Check in all takes if the camera is used by another shot and if not then delete it
        """
        deleteOk = False

        if shot.camera is None:
            return False

        for t in self.takes:
            for s in t.shots:
                if shot != s and s.camera is not None and shot.camera == s.camera:
                    return False

        bpy.ops.object.select_all(action="DESELECT")
        cam = shot.camera
        shot.camera = None

        # https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Scene_and_Object_API
        cam.select_set(True)
        bpy.ops.object.delete()

        return deleteOk

    ###############
    # sounds BG
    ###############

    useBGSounds: BoolProperty(default=False)
    meta_bgSoundsName01: StringProperty(default="")

    def getBGSoundsMetaContainingClip(self, clip):
        # wkip wkip wkip finir ici pour tester qu'on a le bon meta
        return self.getBGSoundsMeta()

    def getBGSoundsMeta(self):
        """ Get the first meta strip dedicated to the bg sounds and with some room in it (ie that has less than 32 tracks occupied)
            Meta strips for sounds are placed on tracks 30 to 32
        """
        scene = self.parentScene
        bgSoundsMeta = None
        newMetaTrackInd = 10  # 30

        # a stocker dans une propriété
        if "" != self.meta_bgSoundsName01:
            if self.meta_bgSoundsName01 not in scene.sequence_editor.sequences:
                self.meta_bgSoundsName01 = ""
            else:
                # bgSoundsMeta = bpy.context.sequences[self.meta_bgSoundsName01]
                bgSoundsMeta = bpy.context.scene.sequence_editor.sequences_all[self.meta_bgSoundsName01]

        if bgSoundsMeta is None:
            # close any meta opened:
            while len(scene.sequence_editor.meta_stack) > 0:
                bpy.ops.sequencer.meta_toggle()

            # create meta
            bpy.ops.sequencer.select_all(action="DESELECT")
            tmpClip = scene.sequence_editor.sequences.new_effect(
                "_tmp_clip-to_delete", "COLOR", newMetaTrackInd, frame_start=0, frame_end=45000
            )
            # tmpClip is selected so we can call meta_make()
            bpy.ops.sequencer.meta_make()
            # bpy.ops.sequencer.meta_toggle()  # close meta
            bgSoundsMeta = scene.sequence_editor.active_strip
            bgSoundsMeta.name = "ShotMan--BGSounds"

            # go back inside the meta to delete the temp strip
            bpy.ops.sequencer.meta_toggle()  # open meta
            # scene.sequence_editor.sequences_all[tmpClip.name]
            bpy.ops.sequencer.select_all(action="SELECT")
            bpy.ops.sequencer.delete()

            bpy.ops.sequencer.meta_toggle()  # close meta
            # scene.sequence_editor.sequences.remove(tmpClip)

            self.meta_bgSoundsName01 = bgSoundsMeta.name

        return bgSoundsMeta

    def openMetaStrip(self, context, metaClip):
        self.closeAllMetaStrips(context)

        bpy.ops.sequencer.select_all(action="DESELECT")
        context.scene.sequence_editor.sequences_all[metaClip.name].select = True
        bpy.ops.sequencer.meta_toggle()

    def closeAllMetaStrips(self, context):
        # close meta if one is opened:
        while len(context.scene.sequence_editor.meta_stack) > 0:
            bpy.ops.sequencer.meta_toggle()

    def getFirstEmptyTrack(self, context, bgSoundsMeta):
        """ Return the first empty track index of the specified meta strip
        """
        firstEmptyTrackInd = -1
        self.openMetaStrip(context, bgSoundsMeta)
        channelsList = list(range(1, 33))
        for seq in context.sequences:
            if seq.channel in channelsList:
                channelsList.remove(seq.channel)
        # print(f"channelsList: {channelsList}")
        if len(channelsList):
            firstEmptyTrackInd = channelsList[0]
        self.closeAllMetaStrips(context)
        return firstEmptyTrackInd

    def addBGSoundToShot(self, sound_path, shot):
        """ Add the sound of the specified media (sound or video) into one of the meta strips of the VSE reserved for shot Manager (from 30 to 32)
            Return the sound clip
        """
        context = bpy.context
        scene = self.parentScene
        newSoundClip = None

        bgSoundsMeta = self.getBGSoundsMeta()
        if bgSoundsMeta is None:
            print("Pb in addBGSoundToShot: no bgSoundsMeta strip")
        else:
            # # close meta if opened:
            # while len(scene.sequence_editor.meta_stack) > 0:
            #     bpy.ops.sequencer.meta_toggle()

            # bpy.ops.sequencer.select_all(action="DESELECT")
            # scene.sequence_editor.sequences_all[bgSoundsMeta.name].select = True

            targetTrackInd = self.getFirstEmptyTrack(bpy.context, bgSoundsMeta)

            if -1 < targetTrackInd:
                self.openMetaStrip(context, bgSoundsMeta)

                vse_render = context.window_manager.UAS_vse_render

                clipName = "myBGSound"
                newSoundClip = vse_render.createNewClip(
                    scene, str(sound_path), targetTrackInd, 0, importVideo=False, importAudio=True, clipName=clipName,
                )

                shot.bgSoundClipName = newSoundClip.name

        self.closeAllMetaStrips(context)

        return newSoundClip

    #################
    #################
    #################
    #################
    #################
    #################
    #################
    # to do:
    # fonction clear orphans in tracks
    # fonction enable seulement le clip actif
    # move clip doit bien mettre a jour le son
    #################
    #################
    #################
    #################
    #################
    #################
    #################
    #################
    #################

    def removeBGSoundFromShot(self, shot):
        context = bpy.context
        scene = self.parentScene
        metaSeq = self.getBGSoundsMetaContainingClip(shot.bgSoundClipName)
        if metaSeq is not None:
            self.openMetaStrip(context, metaSeq)
            bpy.ops.sequencer.select_all(action="DESELECT")
            print(f"removeBGSoundFromShot 01, shot.bgSoundClipName: {shot.bgSoundClipName} ")
            # for i, c in enumerate(context.scene.sequence_editor.sequences):
            for i, c in enumerate(context.sequences):
                print(f"   seq {i + 1}  {c.name}")
            # if shot.bgSoundClipName in context.scene.sequence_editor.sequences:

            for i in context.sequences:
                if shot.bgSoundClipName == i.name:
                    # if shot.bgSoundClipName in context.sequences:  # name and seq, marche pas
                    print("removeBGSoundFromShot 02")
                    # context.scene.sequence_editor.sequences[shot.bgSoundClipName].select = True
                    i.select = True
                    bpy.ops.sequencer.delete()
                    break
                #    self.closeAllMetaStrips(context)
            shot.bgSoundClipName = ""

    def disableAllShotsBGSounds(self):
        """ Turn off all the sounds of all the shots of all the takes
        """
        for clip in self.parentScene.sequence_editor.sequences:
            clip.mute = True

    def enableBGSoundForShot(self, useBgSound, shot):
        """ Turn off all the sounds of all the shots of all the takes and enable only the one of the specified shot
        """
        # print("----++++ enableBGSoundForShot")
        self.disableAllShotsBGSounds()

        if self.useBGSounds and shot is not None:
            bgSoundClip = shot.getSoundSequence()
            if bgSoundClip is not None:
                bgSoundClip.mute = not useBgSound

    ###############
    # functions working only on current take !!!
    ###############

    # wkip ignoreDisabled pas encore implémenté ici!!!!
    def goToPreviousShot(self, currentFrame, ignoreDisabled=False):
        """ 
            works only on current take
            behavior of this button:
            if current shot is enabled:
            - first click: put current time at the start of the current enabled shot
            else:
            - fisrt click: put current time at the end of the previous enabled shot
        """
        # print(" ** -- ** goToPreviousShot")

        if not len(self.get_shots()):
            return ()

        previousShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if True or bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
            else:
                print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShotByIndex(previousShotInd).end
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
        # print(" ** -- ** goToNextShot")
        if not len(self.get_shots()):
            return ()

        #   nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if True or bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
            else:
                print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShotByIndex(nextShotInd).start
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
        if not len(self.get_shots()):
            return ()

        #  previousShot = None
        previousShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #       print("    current Shot is disabled")
                previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                if -1 < previousShotInd:
                    #           print("    previous Shot ind is ", previousShotInd)
                    newFrame = self.getShotByIndex(previousShotInd).end
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.start:
                    #           print("      current frame is start")
                    previousShotInd = self.getPreviousEnabledShotIndex(currentShotInd)
                    if -1 < previousShotInd:
                        #              print("      previous Shot ind is ", previousShotInd)
                        newFrame = self.getShotByIndex(previousShotInd).end
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
        if not len(self.get_shots()):
            return ()

        #  nextShot = None
        nextShotInd = -1
        newFrame = currentFrame

        # in shot play mode the current frame is supposed to be in the current shot
        if bpy.context.window_manager.UAS_shot_manager_shots_play_mode:

            # get current shot in the WHOLE list (= even disabled)
            currentShotInd = self.getCurrentShotIndex()
            currentShot = self.getShotByIndex(currentShotInd)
            #    print("    current Shot: ", currentShotInd)
            if not currentShot.enabled:
                #        print("    current Shot is disabled")
                nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                if -1 < nextShotInd:
                    #            print("    next Shot ind is ", nextShotInd)
                    newFrame = self.getShotByIndex(nextShotInd).start
            else:
                #        print("    current Shot is ENabled")
                if currentFrame == currentShot.end:
                    #           print("      current frame is end")
                    nextShotInd = self.getNextEnabledShotIndex(currentShotInd)
                    if -1 < nextShotInd:
                        #              print("      next Shot ind is ", nextShotInd)
                        newFrame = self.getShotByIndex(nextShotInd).start
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

    # works only on current take
    def getFirstShotIndexContainingFrame(self, frameIndex, ignoreDisabled=False):
        """Return the first shot containing the specifed frame, -1 if not found
        """
        firstShotInd = -1

        shotList = self.get_shots()
        shotFound = False

        if len(shotList):
            firstShotInd = 0
            while firstShotInd < len(shotList) and not shotFound:
                if not ignoreDisabled or shotList[firstShotInd].enabled:
                    shotFound = shotList[firstShotInd].start <= frameIndex and frameIndex <= shotList[firstShotInd].end
                firstShotInd += 1

        if shotFound:
            firstShotInd = firstShotInd - 1
        else:
            firstShotInd = -1

        return firstShotInd

    # works only on current take
    def getFirstShotIndexAfterFrame(self, frameIndex, ignoreDisabled=False):
        """Return the first shot after the specifed frame (supposing thanks to getFirstShotIndexContainingFrame than 
            frameIndex is not in a shot), -1 if not found
        """
        firstShotInd = -1

        shotList = self.get_shots()
        shotFound = False

        if len(shotList):
            firstShotInd = 0
            while firstShotInd < len(shotList) and not shotFound:
                if not ignoreDisabled or shotList[firstShotInd].enabled:
                    shotFound = frameIndex < shotList[firstShotInd].start
                firstShotInd += 1

        if shotFound:
            firstShotInd = firstShotInd - 1
        else:
            firstShotInd = -1

        return firstShotInd

    ##############################

    def renderShotPrefix(self):
        shotPrefix = ""

        if self.use_project_settings:
            # wkip wkip wkip to improve with project_shot_format!!!
            # scene name is used but it may be weak. Replace by take name??
            # shotPrefix = self.getParentScene().name
            shotPrefix = self.parentScene.name
        else:
            shotPrefix = self.render_shot_prefix

        return shotPrefix

    def getOutputFileFormat(self, isVideo=True):
        #   _logger.debug(f"  /// isVideo: {isVideo}")
        outputFileFormat = ""
        if self.use_project_settings:
            if isVideo:
                # outputFileFormat = "mp4"  # wkipwkipwkipself.project_output_format.lower()
                outputFileFormat = self.project_output_format.lower()
                if "" == outputFileFormat:
                    print("\n---------------------------")
                    print(
                        "*** Shot Manager: Project video output file format not correctly set in the Preferences ***\n"
                    )
            #   _logger.debug(f"  /// outputFileFormat vid: {outputFileFormat}")
            else:
                outputFileFormat = self.project_images_output_format.lower()
                if "" == outputFileFormat:
                    print("\n---------------------------")
                    print(
                        "*** Shot Manager: Project image output file format not correctly set in the Preferences ***\n"
                    )
            #    _logger.debug(f"  /// outputFileFormat: {outputFileFormat}")
        else:
            if isVideo:
                outputFileFormat = "mp4"
            else:
                outputFileFormat = "png"
        return outputFileFormat

    def getTakeOutputFilePath(self, rootFilePath="", takeIndex=-1):
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        filePath = ""
        if -1 == takeInd:
            return filePath

        if "" == rootFilePath:
            #  head, tail = os.path.split(bpy.path.abspath(bpy.data.filepath))
            # wkip we assume renderRootPath is valid...
            head, tail = os.path.split(bpy.path.abspath(self.renderRootPath))
            filePath = head + "\\"
        else:
            # wkip tester le chemin
            filePath = rootFilePath
            if not filePath.endswith("\\"):
                filePath += "\\"

        filePath += f"{self.getTakeName_PathCompliant(takeIndex=takeInd)}" + "\\"

        return filePath

    # def getShotOutputFileNameFromIndex(
    #     self,
    #     shotIndex=-1,
    #     takeIndex=-1,
    #     rootFilePath="",
    #     fullPath=False,
    #     fullPathOnly=False,
    #     specificFrame=None,
    #     noExtension=False,
    # ):
    #     shot = self.getShotByIndex(shotIndex=shotIndex, takeIndex=takeIndex)

    #     fileName = ""
    #     if shot is None:
    #         return fileName

    #     fileName = self.getShotOutputFileName(
    #         shot,
    #         rootFilePath=rootFilePath,
    #         fullPath=fullPath,
    #         fullPathOnly=fullPathOnly,
    #         specificFrame=specificFrame,
    #         noExtension=False,
    #     )

    #     return fileName

    def getShotOutputMediaPath(
        # self, shot, rootFilePath=None, fullPath=False, fullPathOnly=False, specificFrame=None, noExtension=False
        self,
        shot,
        rootPath=None,
        insertTakeName=True,
        providePath=True,
        provideName=True,
        provideExtension=True,
        specificFrame=None,
        genericFrame=False,
    ):
        """
            Return the shot path. It is made of: <root path>/<shot take name>/<prefix>_<shot name>[_<specific frame index (if specified)].<extention>
            rootPath: start of the path, if specified. Otherwise the current file folder is used
            providePath: if True then the returned file name starts with the full path
            provideName: if True then the returned file name contains the name
            provideExtension: if True then the returned file name ends with the file extention
            
            if providePath is True:
                if rootPath is provided then the start of the path is the root, otherwise props.renderRootPath is used
                if insertTakeName is True then the name of the take is added to the path
            
            if genericFrame is True then #### is used instead of the specific frame index
        """

        # file path
        filePath = ""
        if providePath:
            if rootPath is not None:
                filePath += bpy.path.abspath(rootPath)
            else:
                #   filePath += bpy.path.abspath(bpy.data.filepath)     # current blender file path
                filePath += bpy.path.abspath(self.renderRootPath)

            if not (filePath.endswith("/") or filePath.endswith("\\")):
                filePath += "\\"

            if insertTakeName:
                takeName = shot.getParentTake().getName_PathCompliant()
                filePath += takeName + "\\"

        # file name
        fileName = ""
        if provideName:
            shotPrefix = self.renderShotPrefix()
            if "" != shotPrefix:
                fileName += shotPrefix + "_"
            fileName += shot.getName_PathCompliant()
            if genericFrame:
                fileName += "_" + "####"
            elif specificFrame is not None:
                fileName += "_" + f"{specificFrame:04d}"

        # file extension
        fileExtension = ""
        if provideExtension:
            fileExtension += "." + self.getOutputFileFormat(isVideo=specificFrame is None and not genericFrame)

        # result
        resultStr = filePath + fileName + fileExtension
        resultStr.replace("\\", "/")  # //

        #   _logger.debug(f" ** resultStr: {resultStr}")

        return resultStr

    def getShotOutputFileName(
        self, shot, rootFilePath="", fullPath=False, fullPathOnly=False, specificFrame=None, noExtension=False
    ):
        """
            Return the shot path
        """
        resultStr = ""

        # file
        fileName = shot.getName_PathCompliant()
        shotPrefix = self.renderShotPrefix()
        if "" != shotPrefix:
            fileName = shotPrefix + "_" + fileName

        # fileName + frame index + extension
        fileFullName = fileName
        if specificFrame is not None:
            fileFullName += "_" + f"{(specificFrame):04d}"

        filePath = ""
        if fullPath or fullPathOnly:

            if "" == rootFilePath:
                #  head, tail = os.path.split(bpy.path.abspath(bpy.data.filepath))
                # wkip we assume renderRootPath is valid...
                head, tail = os.path.split(bpy.path.abspath(self.renderRootPath))
                filePath = head + "\\"
            else:
                # wkip tester le chemin
                filePath = rootFilePath
                if not filePath.endswith("\\"):
                    filePath += "\\"

            filePath += f"{self.getTakeName_PathCompliant(takeIndex = shot.getParentTakeIndex())}" + "\\"
            filePath += f"{shot.getName_PathCompliant()}" + "\\"

        #   filePath += f"//{fileName}"

        # path is absolute and ends with a /
        if fullPathOnly:
            # _logger.debug(" ** fullPathOnly")
            resultStr = filePath
        elif fullPath:
            #            _logger.debug(" ** fullpath")
            resultStr = filePath + fileFullName
            if not noExtension:
                resultStr += "." + self.getOutputFileFormat(isVideo=specificFrame is None)
        else:
            #           _logger.debug(" ** else")
            resultStr = fileFullName
            #          _logger.debug(f" ** resultStr 1:  {resultStr}")
            if not noExtension:
                resultStr += "." + self.getOutputFileFormat(isVideo=specificFrame is None)
        #         _logger.debug(f" ** resultStr 2:  {resultStr}")

        _logger.debug(f" ** resultStr: {resultStr}")
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
        shot = self.getShotByIndex(shotIndex)
        if shot is not None:
            bpy.ops.object.select_all(action="DESELECT")
            if shot.camera is not None:
                if bpy.context.active_object is not None and bpy.context.active_object.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                    # if bpy.context.active_object is None or bpy.context.active_object.mode == "OBJECT":
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

    ##############################

    # Project ###

    ##############################

    def setProjectSettings(
        self,
        use_project_settings=None,
        project_name=None,
        project_fps=-1,
        project_resolution=None,
        project_resolution_framed=None,
        project_shot_format=None,
        project_use_shot_handles=None,
        project_shot_handle_duration=-1,
        project_output_format=None,
        project_color_space=None,
        project_asset_name=None,
    ):
        """ Set only the specified properties
            Shot format must use "_" as separators. It is of the template: Act{:02}_Seq{:04}_Sh{:04}
        """

        print("    * setProjectSettings *")

        if use_project_settings is not None:
            self.use_project_settings = use_project_settings

        if project_name is not None:
            self.project_name = project_name
        if -1 != project_fps:
            self.project_fps = project_fps
        if project_resolution is not None:
            self.project_resolution_x = project_resolution[0]
            self.project_resolution_y = project_resolution[1]
        if project_resolution_framed is not None:
            self.project_resolution_framed_x = project_resolution_framed[0]
            self.project_resolution_framed_y = project_resolution_framed[1]
        if project_shot_format is not None:
            self.project_shot_format = project_shot_format

        if project_use_shot_handles is not None:
            self.project_use_shot_handles = project_use_shot_handles
        if -1 != project_shot_handle_duration:
            self.project_shot_handle_duration = project_shot_handle_duration

        if project_output_format is not None:
            self.project_output_format = project_output_format
        if project_color_space is not None:
            self.project_color_space = project_color_space
        if project_asset_name is not None:
            self.project_asset_name = project_asset_name

        self.applyProjectSettings()

    def applyProjectSettings(self, settingsListOnly=False):

        settingsList = []

        settingsList.append(["Project Name", '"' + self.project_name + '"'])
        settingsList.append(["Project Framerate", str(self.project_fps) + " fps"])
        settingsList.append(["Resolution", str(self.project_resolution_x) + " x " + str(self.project_resolution_y)])
        settingsList.append(
            [
                "Resolution Framed",
                str(self.project_resolution_framed_x) + " x " + str(self.project_resolution_framed_y),
            ]
        )
        settingsList.append(["Shot Name Format", str(self.project_shot_format)])
        settingsList.append(["Use Shot Handles", str(self.project_use_shot_handles)])
        settingsList.append(["Shot Handle Duration", str(self.project_shot_handle_duration)])
        settingsList.append(["Project Output Format", str(self.project_output_format)])
        settingsList.append(["Project Color Space", str(self.project_color_space)])
        settingsList.append(["Project Asset Name", str(self.project_asset_name)])
        settingsList.append(["new_shot_prefix", str(self.new_shot_prefix)])
        # settingsList.append(["render_shot_prefix", str(self.render_shot_prefix)])

        #################
        # applying project settings to parent scene

        if self.use_project_settings and not settingsListOnly:

            parentScn = self.getParentScene()
            parentScn.render.fps = self.project_fps
            parentScn.render.fps_base = 1.0

            parentScn.render.resolution_x = self.project_resolution_x
            parentScn.render.resolution_y = self.project_resolution_y
            parentScn.render.resolution_percentage = 100.0

            # wkip both should not be there
            # self.use_handles = self.project_use_shot_handles
            # self.handles = self.project_shot_handle_duration

            s = self.project_shot_format.split("_")[2]
            s = s.format(0)
            s = s.replace("0", "")
            self.new_shot_prefix = s

            # path
            self.setProjectRenderFilePath()

        return settingsList

    def createRenderSettings(self):

        # Still
        self.renderSettingsStill.name = "Still Preset"
        self.renderSettingsStill.renderMode = "STILL"

        # Animation
        self.renderSettingsAnim.name = "Animation Preset"
        self.renderSettingsAnim.renderMode = "ANIMATION"

        # Project
        self.renderSettingsAll.name = "All Edits Preset"
        self.renderSettingsAll.renderMode = "ALL"

        self.renderSettingsAll.renderAllTakes = False
        self.renderSettingsAll.renderAllShots = False
        self.renderSettingsAll.renderAlsoDisabled = False
        self.renderSettingsAll.renderHandles = False
        self.renderSettingsAll.renderOtioFile = True
        self.renderSettingsAll.otioFileType = "XML"
        self.renderSettingsAll.generateEditVideo = True

        # Otio
        self.renderSettingsOtio.name = "Otio Preset"
        self.renderSettingsOtio.renderMode = "OTIO"
        self.renderSettingsOtio.renderOtioFile = True  # not used in this preset
        self.renderSettingsOtio.otioFileType = "XML"

        # Playblast
        self.renderSettingsPlayblast.name = "Playblast Preset"
        self.renderSettingsPlayblast.renderMode = "PLAYBLAST"
        self.renderSettingsPlayblast.useStampInfo = False

    def setProjectRenderFilePath(self):
        # if '' == bpy.data.filepath:

        bpy.context.scene.render.filepath = f"//{self.getTakeName_PathCompliant()}"

    ##############################
    # Montage ###
    ##############################

    # def rebuildMontage(self):
    #     self._montage = MontageShotManager()
    #     self._montage.initialize(context.scene, props.getCurrentTake())

    # def get_montage(self):
    #     return self._montage

    def __init__(self):
        super().__init__()

    # def initialize(self, scene, take):
    def initialize(self):
        # self.sequencesList =
        #        UAS_ShotManager_Props.montageType = property(lambda self: "SHOTMANAGER")

        pass

    def get_montage_type(self):
        return "SHOTMANAGER"

    def get_montage_characteristics(self):
        """
            Return a dictionary with the characterisitics of the montage.
            This is required to export it as xml EDL.
        """
        # dict cannot be set as a property for Props :S
        characteristics = dict()

        if self.use_project_settings:
            characteristics["resolution_x"] = self.project_resolution_framed_x  # width
            characteristics["resolution_y"] = self.project_resolution_framed_y  # height
        else:
            characteristics["resolution_x"] = self.parentScene.render.resolution_y  # width
            characteristics["resolution_y"] = self.parentScene.render.resolution_y  # height
        characteristics["framerate"] = self.get_fps()
        characteristics["duration"] = self.get_frame_duration()

        return characteristics

    def set_montage_characteristics(self, resolution_x=-1, resolution_y=-1, framerate=-1, duration=-1):
        """
        """
        # self._characteristics = dict()
        # # self._characteristics["framerate"] = framerate  # timebase
        # self._characteristics["resolution_x"] = resolution_x  # width
        # self._characteristics["resolution_y"] = resolution_y  # height
        # self._characteristics["framerate"] = self.get_fps()  # timebase
        # self._characteristics["duration"] = self.get_frame_duration()  # wkip may change afterwards...
        # # self._characteristics["duration"] = duration  # wkip may change afterwards...
        pass

    def getInfoAsDictionnary(self, dictMontage=None, shotsDetails=True):
        if dictMontage is None:
            dictMontage = dict()
            dictMontage["montage"] = self.get_name()

        for take in self.takes:
            dictMontage[take.get_name()] = take.getInfoAsDictionnary(shotsDetails=shotsDetails)
        return dictMontage

    def printChildrenInfo(self):
        self.getCurrentTake().printInfo()

    def get_name(self):
        return self.parentScene.name + "_" + self.takes[self.getCurrentTakeIndex()].get_name()

    def get_fps(self):
        return self.parentScene.render.fps

    def get_frame_start(self):
        return self.parentScene.UAS_shot_manager_props.editStartFrame

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
        # editShotsList = self.getShotsList(ignoreDisabled=True)
        # if len(self.takes) and len(editShotsList):
        #     return self.sequencesList[len(self.sequencesList) - 1].get_frame_end()
        # else:
        #     return -1
        return self.get_frame_start() + self.getEditDuration()

    def get_frame_duration(self):
        return self.getEditDuration()

    def get_num_sequences(self):
        return 1

    def get_sequences(self):
        return [self.getCurrentTake()]

    def newSequence(self):
        # if self.sequencesList is None:
        #     self.sequencesList = list()
        # newSeq = SequenceShotManager(self)
        # self.sequencesList.append(newSeq)
        # return newSeq
        return None

    ###########################

    def sortShotsVersions(self, takeIndex=-1):
        """ Sorts shots ending with '_a', '_b'...
            *** Only sort disabled shots by default ***
        """
        takeInd = (
            self.getCurrentTakeIndex()
            if -1 == takeIndex
            else (takeIndex if 0 <= takeIndex and takeIndex < len(self.getTakes()) else -1)
        )
        if -1 == takeInd:
            return ()

        # get the disabled shots
        shotList = self.takes[takeInd].shots

        disabledShotNames = list()
        for i in range(0, len(shotList)):
            if not shotList[i].enabled:
                disabledShotNames.append(shotList[i].name)

        # sort the list
        disabledShotNames.sort()

        # print("\nSorted list:")
        # for nam in disabledShotNames:
        #     print(f"  {nam}")

        # shot_re = re.compile(r"sh_?(\d+)", re.IGNORECASE)
        # shot_re = re.compile(r"Sh_?(\d+)")
        shot_re = re.compile(r"^Sh\d\d\d\d")

        def _baseName(name):
            """ We are based on teh name template Shxxxx
            """
            return name[:6]

        def _isValidShotName(name):
            res = False
            match = shot_re.search(name)
            if match:
                res = True
            return res

        #  print("\nTreated list:")
        for shName in disabledShotNames:
            # if it is a basename or a version name
            if _isValidShotName(shName):
                #         print(f"\n - {shName}, basename: {_baseName(shName)}")

                # check the shots list from begining and insert at first place where names are matching
                for i in range(0, len(shotList)):
                    # ignore self
                    shotFromName = self.getShotByName(shName)
                    shotFromNameInd = self.getShotIndex(shotFromName)

                    #       print(f"  i:{i} ")
                    if shotList[i].name == shName:
                        pass
                    elif (shotList[i].name).startswith(_baseName(shName)):
                        #  print(f"   ici:  shotList[i].name: {shotList[i].name}")

                        if shName < shotList[i].name:
                            #       print(f"     before, i:{i}, shotFromName:{shotFromName}")
                            #       self.takes[takeInd].debugDisplayShots()
                            if shotFromNameInd < i:
                                if 0 < i:
                                    self.moveShotToIndex(shotFromName, i - 1)
                            else:
                                self.moveShotToIndex(shotFromName, i)
                            #       self.takes[takeInd].debugDisplayShots()
                            break
                        else:
                            #    print(f"   lu")
                            if len(shotList) > i + 1:
                                #        print(f"   lulu")
                                if (shotList[i + 1].name).startswith(_baseName(shName)):
                                    if shName < shotList[i + 1].name:
                                        #                print(f"     lu")
                                        self.moveShotToIndex(shotFromName, i + 1)
                                        break
                                else:
                                    #            print("lo")
                                    self.moveShotToIndex(shotFromName, i + 1)
                                    break


###########################


_classes = (
    #    UAS_ShotManager_Media,
    UAS_ShotManager_Shot,
    UAS_ShotManager_Take,
    UAS_ShotManager_Props,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.UAS_shot_manager_props = PointerProperty(type=UAS_ShotManager_Props)


def unregister():
    del bpy.types.Scene.UAS_shot_manager_props
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
