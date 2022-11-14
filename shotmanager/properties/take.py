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
Definition of a take
"""

import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, PointerProperty, BoolProperty, IntProperty

from .shot import UAS_ShotManager_Shot
from .montage_interface import SequenceInterface

from shotmanager.utils.utils import findFirstUniqueName

from shotmanager.properties.output_params import UAS_ShotManager_OutputParams_Resolution

from shotmanager.config import config
from shotmanager.config import sm_logging

_logger = sm_logging.getLogger(__name__)


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
                    scn_props = config.getAddonProps(scn)
                    for t in scn_props.takes:
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
        print(f"\nInitializing new take with name {name}...")

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

        self.overrideRenderSettings = source.overrideRenderSettings
        self.outputParams_Resolution.copyPropertiesFrom(source.outputParams_Resolution)

        self.note01 = _copyString(source.note01)
        self.note02 = _copyString(source.note02)
        self.note03 = _copyString(source.note03)
        self.showNotes = source.showNotes

    def getName_PathCompliant(self, withPrefix=False):
        takeName = self.name.replace(" ", "_")
        if withPrefix:
            props = config.getAddonProps(self.parentScene)
            takeName = f"{props.getRenderShotPrefix()}{takeName}"
        return takeName

    def getShotList(self, ignoreDisabled=False):
        """Return a filtered copy of the shots associated to this take"""
        shotList = []

        for shot in self.shots:
            if not ignoreDisabled or shot.enabled:
                shotList.append(shot)

        return shotList

    def _get_name(self):
        val = self.get("name", "Take 00")
        return val

    def _set_name(self, value):
        """Set a unique name to the take"""
        props = config.getAddonProps(self.getParentScene())
        takes = props.getTakes()
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
        """Return the number of shots of the take"""
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

    def getShotsList(self, ignoreDisabled=False):
        """Return a filtered copy of the list of the shots associated to this take"""
        shotList = list()
        for shot in self.shots:
            if not ignoreDisabled or shot.enabled:
                shotList.append(shot)

        return shotList

    def getShotsUsingCamera(self, cam, ignoreDisabled=False):
        """Return the list of all the shots used by the specified camera"""
        shotList = []
        for shot in self.shots:
            if cam == shot.camera and (not ignoreDisabled or shot.enabled):
                shotList.append(shot)

        return shotList

    def getEditShots(self, ignoreDisabled=True):
        return self.getShotsList(ignoreDisabled=ignoreDisabled)

    def getMinFrame(self, ignoreDisabled=False):
        """Return the value of the lower frame found in the shots
        Return None if the take has no shots
        """
        minFrame = None
        for i, shot in enumerate(self.shots):
            if ignoreDisabled or shot.enabled:
                if minFrame is None:
                    minFrame = shot.start
                else:
                    minFrame = min(minFrame, shot.start)
        return minFrame

    def getMaxFrame(self, ignoreDisabled=False):
        """Return the value of the highest frame found in the shots
        Return None if the take has no shots
        """
        maxFrame = None
        for i, shot in enumerate(self.shots):
            if ignoreDisabled or shot.enabled:
                if maxFrame is None:
                    maxFrame = shot.end
                else:
                    maxFrame = max(maxFrame, shot.end)
        return maxFrame

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

    def _update_overrideRenderSettings(self, context):
        props = config.getAddonProps(self.parentScene)
        props.setResolutionToScene()

    overrideRenderSettings: BoolProperty(
        name="Override Render Settings",
        description="When checked, the take gets its own local render settings,\n"
        " overriding the render settings provided either by the project settings or the scene",
        update=_update_overrideRenderSettings,
        default=False,
    )

    outputParams_Resolution: PointerProperty(type=UAS_ShotManager_OutputParams_Resolution)

    def getRenderResolution(self):
        """Return the resolution used by Shot Manager in the current context.
        It is the resolution of the images resulting from the scene rendering, not the one resulting
        from these renderings composited with the Stamp Info frames, which can be bigger.

        This resolution is specified by:
            - the current take resolution if it overrides the scene or project render settings,
            - the project, if project settings are used,
            - or by the current scene if none of the specifications above

        The resolution can then be different if project settings are used or not.

        Returns:
            tupple with the render resolution x and y of the take
        """
        props = config.getAddonProps(bpy.context.scene)
        res = None
        if self.overrideRenderSettings:
            res = (self.outputParams_Resolution.resolution_x, self.outputParams_Resolution.resolution_y)
        else:
            if props.use_project_settings:
                res = (props.project_resolution_x, props.project_resolution_y)
            else:
                if props.parentScene is None:
                    props.getParentScene()
                res = (props.parentScene.render.resolution_x, props.parentScene.render.resolution_y)
        return res

    #############
    # notes #####
    #############

    showNotes: BoolProperty(
        name="Show Take Notes",
        description="Show or hide current take notes",
        default=False,
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
        # TODO
        print("*** Take.newShot: To implement !! ***")
        return None

    def get_frame_start(self):
        props = config.getAddonProps(self.parentScene)
        return props.editStartFrame

    def get_frame_end(self):
        """get_frame_end is exclusive in order to follow the Blender implementation of get_frame_end for its clips"""
        props = config.getAddonProps(self.parentScene)
        return props.editStartFrame + props.getEditDuration()

    def get_frame_duration(self):
        """Same as self.getEditDuration()"""
        return self.get_frame_end() - self.get_frame_start()
