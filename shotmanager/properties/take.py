import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, PointerProperty, BoolProperty, IntProperty, EnumProperty

from .shot import UAS_ShotManager_Shot

from shotmanager.utils.utils import findFirstUniqueName
from shotmanager.rrs_specific.montage.montage_interface import SequenceInterface

from shotmanager.properties.output_params import UAS_ShotManager_OutputParams_Resolution

import logging

_logger = logging.getLogger(__name__)


class UAS_ShotManager_Take(SequenceInterface, PropertyGroup):
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

    # wkip for backward compatibility - before V1.2.21
    # used by data version patches.
    # For general purpose use the property self.parentScene
    def getParentScene(self):
        if self.parentScene is None:
            # matches = [
            #     s
            #     for s in bpy.data.scenes
            #     if "UAS_shot_manager_props" in s and self in s["UAS_shot_manager_props"].takes
            # ]
            # self.parentScene = matches[0] if len(matches) > 0 else None

            for scn in bpy.data.scenes:
                if "UAS_shot_manager_props" in scn:
                    # print("scn.UAS_shot_manager_props:", scn.UAS_shot_manager_props)
                    # takes = scn.UAS_shot_manager_props.getTakes()
                    # print("scn.UAS_shot_manager_props.takes:", scn.UAS_shot_manager_props.takes)
                    for t in scn.UAS_shot_manager_props.takes:
                        # print("t.name: ", t.name)
                        # print("self.name: ", self.name)
                        if self == t:
                            #    print("Found!")
                            self.parentScene = scn

        return self.parentScene

    # def shotManager(self):
    #     """Return the shot manager properties instance the take is belonging to.
    #     """
    #     parentShotManager = None
    #     parentScene = getParentScene()

    #     if parentScene is not None:
    #         parentShotManager = parentScene.UAS_shot_manager_props
    #     return parentShotManager

    def initialize(self, parentProps, name="New Take"):
        print("Initialising new take...")
        _logger.debug(f"\n  Initialising new take with the name: {name}")

        self.parentScene = parentProps.parentScene

        # wkip check for unique name
        self.name = name

        self.outputParams_Resolution.resolution_x = self.parentScene.render.resolution_x
        self.outputParams_Resolution.resolution_y = self.parentScene.render.resolution_y

    def copyPropertiesFrom(self, source):
        """
        Copy properties from the specified source to this one
        """
        from shotmanager.utils.utils_python import copyString as _copyString

        self.globalEditDirectory = _copyString(source.globalEditDirectory)
        self.globalEditVideo = _copyString(source.globalEditVideo)
        self.startInGlobalEdit = source.startInGlobalEdit

        self.renderMode = source.renderMode
        self.outputParams_Resolution.copyPropertiesFrom(source.outputParams_Resolution)

        self.note01 = _copyString(source.note01)
        self.note02 = _copyString(source.note02)
        self.note03 = _copyString(source.note03)
        self.showNotes = source.showNotes

    def getName_PathCompliant(self):
        takeName = self.name.replace(" ", "_")
        return takeName

    def getShotList(self, ignoreDisabled=False):
        """ Return a filtered copy of the shots associated to this take
        """
        shotList = []

        for shot in self.shots:
            if not ignoreDisabled or shot.enabled:
                shotList.append(shot)

        return shotList

    def _get_name(self):
        val = self.get("name", "Take 00")
        return val

    def _set_name(self, value):
        """ Set a unique name to the shot
        """
        takes = self.getParentScene().UAS_shot_manager_props.getTakes()
        newName = findFirstUniqueName(self, value, takes)
        self["name"] = newName

    """ Take name is always unique in a scene
    """
    name: StringProperty(name="Name", get=_get_name, set=_set_name)

    #############
    # shots #####
    #############

    shots: CollectionProperty(type=UAS_ShotManager_Shot)

    def getNumShots(self, ignoreDisabled=False):
        """ Return the number of shots of the take
        """
        numShots = 0
        if ignoreDisabled:
            for shot in self.shots:
                if shot.enabled:
                    numShots += 1
        else:
            if self.shots is None:
                numShots = 0
            else:
                numShots = len(self.shots)
        return numShots

    def getShotsUsingCamera(self, cam, ignoreDisabled=False):
        """ Return the list of all the shots used by the specified camera
        """
        shotList = []
        for shot in self.shots:
            if cam == shot.camera and (not ignoreDisabled or shot.enabled):
                shotList.append(shot)

        return shotList

    def getShotsList(self, ignoreDisabled=False):
        shotList = list()
        for shot in self.shots:
            if not ignoreDisabled or shot.enabled:
                shotList.append(shot)

        return shotList

    def getEditShots(self, ignoreDisabled=True):
        return self.getShotsList(ignoreDisabled=ignoreDisabled)

    #############
    # global edit infos #####
    #############
    globalEditDirectory: StringProperty(default="")
    globalEditVideo: StringProperty(default="")
    startInGlobalEdit: IntProperty(min=0, default=0)

    #############
    # render settings #####
    # Those properties are overriden by the project settings if use_project_settings is true
    #############

    renderMode: EnumProperty(
        name="Take Resolution Mode",
        description="Use the take resolution or adopt the project resolution\nif the project settings are activated",
        items=(("FROM_PROJECT", "From Project", ""), ("FROM_TAKE", "Override Project Resolution", ""),),
        default="FROM_TAKE",
    )

    outputParams_Resolution: PointerProperty(type=UAS_ShotManager_OutputParams_Resolution)

    def getResolution(self):
        """
            Return a tupple with the render resolution of the take. The resolution can be different if project settings are used or not
        """
        props = self.parentScene.UAS_shot_manager_props
        res = None
        if props.use_project_settings and "FROM_PROJECT" == self.renderMode:
            res = (props.project_resolution_x, props.project_resolution_y)
        else:
            res = (self.outputParams_Resolution.resolution_x, self.outputParams_Resolution.resolution_y)
        return res

    #############
    # notes #####
    #############

    showNotes: BoolProperty(
        name="Show Take Notes", description="Show or hide current take notes", default=False,
    )

    note01: StringProperty(name="Note 1", description="")
    note02: StringProperty(name="Note 2", description="")
    note03: StringProperty(name="Note 3", description="")

    def hasNotes(self):
        return "" != self.note01 or "" != self.note02 or "" != self.note03

    #############
    # interface for Montage #####
    # Note: Take inherits from SequenceInterface
    #############

    def __init__(self, parent):
        super().__init__(parent)
        self.shotsList = self.shots

        print("__Init__ from Take")
        pass

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def printInfo(self, printChildren=True):
        infoStr = f"\n    - Take: {self.get_name()}, Start: {self.get_frame_start()}, End(Incl.):{self.get_frame_end() - 1}, Duration: {self.get_frame_duration()}, Shots: {len(self.getEditShots())}"
        print(infoStr)
        if printChildren:
            for shot in self.getEditShots():
                print("")
                shot.printInfo()

    def debugDisplayShots(self):
        print("\nShots:")
        for sh in self.shots:
            offStr = "" if sh.enabled else "  Off"
            print(f"  {sh.name}{offStr}")

    def getInfoAsDictionnary(self, shotsDetails=True):
        dictSeq = dict()
        dictSeq["duration"] = self.get_frame_duration()
        dictSeq["shots"] = []
        for shot in self.getEditShots():
            dictSeq["shots"].append(shot.getInfoAsDictionnary(shotsDetails=shotsDetails))

        return dictSeq

    def newShot(self, shot):
        print("*** Take.newShot: To implement !! ***")
        return newShot

    def get_frame_start(self):
        return self.parentScene.UAS_shot_manager_props.editStartFrame

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips
        """
        return (
            self.parentScene.UAS_shot_manager_props.editStartFrame
            + self.parentScene.UAS_shot_manager_props.getEditDuration()
        )

    def get_frame_duration(self):
        """ Same as self.getEditDuration()
        """
        return self.get_frame_end() - self.get_frame_start()

