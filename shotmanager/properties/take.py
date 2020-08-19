import bpy

from bpy.types import Scene
from bpy.types import PropertyGroup
from bpy.props import StringProperty, CollectionProperty, PointerProperty

from .shot import UAS_ShotManager_Shot

from shotmanager.utils.utils import findFirstUniqueName


class UAS_ShotManager_Take(PropertyGroup):
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
        takes = self.parentScene.UAS_shot_manager_props.getTakes()
        newName = findFirstUniqueName(self, value, takes)
        self["name"] = newName

    """ Take name is always unique in a scene
    """
    name: StringProperty(name="Name", get=_get_name, set=_set_name)

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
